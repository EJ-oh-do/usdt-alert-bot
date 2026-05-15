import os
import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def get_upbit_usdt_price():
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": "KRW-USDT"}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return float(data[0]["trade_price"])


def get_usdkrw_rate():
    url = "https://finance.naver.com/marketindex/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

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

    response = requests.post(url, data=payload, timeout=10)
    response.raise_for_status()


def check_usdt():
    usdt_price = get_upbit_usdt_price()
    usdkrw = get_usdkrw_rate()

    gap = usdt_price - usdkrw
    premium_rate = (usdt_price / usdkrw - 1) * 100

    print("USDT:", usdt_price)
    print("환율:", usdkrw)
    print("괴리:", gap)
    print("역프율:", premium_rate)

    if premium_rate <= -1.6:
        level = "🚨 초강한 역프"
        action = "역프가 매우 큰 구간입니다. 무리한 풀매수보다 분할매수 기준으로 검토하세요."

    elif premium_rate <= -1.2:
        level = "🔥 강한 역프"
        action = "좋은 역프 구간입니다. 분할매수 적극 검토 구간입니다."

    elif premium_rate <= -0.9:
        level = "🟠 좋은 역프"
        action = "분할매수 검토 구간입니다."

    elif premium_rate <= -0.6:
        level = "🟡 역프 알림"
        action = "매수 관심 구간입니다."

    else:
        print("알림 조건 아님")
        return

    message = f"""
{level}

업비트 USDT: {usdt_price:,.2f}원
원달러 환율: {usdkrw:,.2f}원
괴리 금액: {gap:,.2f}원
역프율: {premium_rate:.2f}%

{action}
"""

    send_telegram(message)


if __name__ == "__main__":
    try:
        check_usdt()
    except Exception as e:
        print("에러 발생:", e)