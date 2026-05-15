import os
import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_upbit_usdt_price():
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": "KRW-USDT"}

    response = requests.get(url, params=params)
    data = response.json()

    return float(data[0]["trade_price"])


def get_usdkrw_rate():
    url = "https://finance.naver.com/marketindex/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    html = response.text

    start = html.find("미국 USD")
    sub_html = html[start:start + 1000]

    value_start = sub_html.find('<span class="value">') + len('<span class="value">')
    value_end = sub_html.find("</span>", value_start)

    rate_text = sub_html[value_start:value_end]
    rate_text = rate_text.replace(",", "")

    return float(rate_text)


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


def check_usdt():

    usdt_price = get_upbit_usdt_price()

    usdkrw = get_usdkrw_rate()

    gap = usdt_price - usdkrw

    premium_rate = (usdt_price / usdkrw - 1) * 100

    print("USDT:", usdt_price)
    print("환율:", usdkrw)
    print("괴리:", gap)
    print("역프율:", premium_rate)

    if premium_rate <= -0.9:

        message = f"""
🔥 강한 역프 발생

USDT: {usdt_price:,.2f}원
환율: {usdkrw:,.2f}원
괴리: {gap:,.2f}원
역프율: {premium_rate:.2f}%
"""

        send_telegram(message)


check_usdt()