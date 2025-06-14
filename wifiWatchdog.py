#!/usr/bin/env python3
"""
Wi-Fi 監視デーモン
- 10分ごとに ping で疎通を確認
- 障害: 1回目→Wi-Fi リセット, 2回目→Wi-Fi リセット, 3回目→本体再起動
- リセットで復旧したら LINE 通知
"""

import os
import time
import subprocess
from datetime import datetime
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
TO_USER_ID = os.getenv("TO_USER_ID")

CHECK_INTERVAL_SEC = 600  # 10分
PING_TARGET = "8.8.8.8"
IFACE = "wlan0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def check_connectivity() -> bool:
    result = subprocess.run(
        ["ping", "-I", IFACE, "-c", "1", "-w", "2", PING_TARGET],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def wifi_reset():
    logging.warning("Wi-Fiリセット")
    cmds = [
        ["ip", "link", "set", IFACE, "down"],
        ["ip", "link", "set", IFACE, "up"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, check=False)
    # dhcpcd を使っていれば IP 取得を待つ
    time.sleep(15)


def send_line(text: str):
    if not (CHANNEL_ACCESS_TOKEN and TO_USER_ID):
        logging.error("LINE トークン未設定、送信スキップ")
        return
    payload = {"to": TO_USER_ID, "messages": [{"type": "text", "text": text}]}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    try:
        r = requests.post(
            "https://api.line.me/v2/bot/message/push",
            json=payload,
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        logging.info("LINE 送信成功")
    except Exception as e:
        logging.error(f"LINE 送信失敗: {e}")


def get_ip(iface: str = IFACE) -> str:
    try:
        out = subprocess.check_output(
            ["ip", "-4", "addr", "show", iface], text=True
        ).split()
        return out[out.index("inet") + 1].split("/")[0]
    except Exception:
        return "N/A"


# ---------------------- メイン ------------------------
def main():
    fail_count = 0

    while True:
        if check_connectivity():
            if fail_count:
                logging.info("回復を確認、カウンタリセット")
            fail_count = 0
        else:
            fail_count += 1
            logging.error(f"接続失敗 #{fail_count}")

            if fail_count in (1, 2):
                wifi_reset()
                if check_connectivity():
                    ip = get_ip()
                    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    message_text = f"Date: {now}\nIP: {ip}ResetCount: {fail_count}\nWi-Fiをリセットしました。"
                    send_line(message_text)
                    fail_count = 0  # 復旧

            else:  # 3回連続失敗
                logging.critical("本体再起動")
                subprocess.run(["/usr/bin/systemctl", "reboot"])

        time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
