#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import subprocess


load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
TO_USER_ID = os.getenv("TO_USER_ID")

IFACE = "wlan0"


def get_ip(iface: str = IFACE) -> str:
    try:
        out = subprocess.check_output(
            ["ip", "-4", "addr", "show", iface], text=True
        ).split()
        return out[out.index("inet") + 1].split("/")[0]
    except Exception:
        return "N/A"


def main():
    print(CHANNEL_ACCESS_TOKEN)
    print(TO_USER_ID)

    if not CHANNEL_ACCESS_TOKEN or not TO_USER_ID:
        raise RuntimeError(
            "環境変数 CHANNEL_ACCESS_TOKEN または TO_USER_ID が設定されていません"
        )

    ip = get_ip()
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_text = f"Date: {now}\nIP: {ip}\nシステムが起動しました。"

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": message_text}],
    }

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()  # 失敗時は例外を投げて systemd 側にエラーを通知


if __name__ == "__main__":
    main()
