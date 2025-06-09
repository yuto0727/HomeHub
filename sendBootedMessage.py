import requests
from datetime import datetime

CHANNEL_ACCESS_TOKEN = "T4/fajd38McCUoA+UrUqbFkIquN5yp8jhszymK+O+DSmMM6ebyuGMqSSLihHl+fMtA1kFla6zAEIuQezEuT9ZJrlHVXqReVqNRheS/5kGGzgJFxRh4m7DMr5lIAOn64DZLEawzcSWt5EeSqolDI+6gdB04t89/1O/w1cDnyilFU="
TO_USER_ID = "U5a2991011c7a349ab5c5bebc4347cfb6"


def send_line_message(token, to_user_id):
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message = f"{now}\nシステムが起動しました。"

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"to": to_user_id, "messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)


if __name__ == "__main__":
    send_line_message(CHANNEL_ACCESS_TOKEN, TO_USER_ID)
