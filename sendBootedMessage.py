#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# .env を読み込む（スクリプトと同じディレクトリに置く想定）
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
TO_USER_ID = os.getenv("TO_USER_ID")


def main():
    print(CHANNEL_ACCESS_TOKEN)
    print(TO_USER_ID)

    if not CHANNEL_ACCESS_TOKEN or not TO_USER_ID:
        raise RuntimeError(
            "環境変数 CHANNEL_ACCESS_TOKEN または TO_USER_ID が設定されていません"
        )

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_text = f"{now}\nシステムが起動しました。"

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
