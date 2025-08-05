# exchange_app.py
import requests
from bs4 import BeautifulSoup
import streamlit as st

# 找 TWD/USD
def get_twd_usd():
    url = "https://www.findrate.tw/USD/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    trs = soup.find("table").find_all("tr")
    cols = trs[1].find_all("td")
    bank = cols[1].get_text(strip=True)
    exchange = float(cols[2].get_text(strip=True))
    return bank, exchange

# 找 TWD/THB
def get_twd_thb():
    url = "https://www.findrate.tw/THB/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    trs = soup.find("table").find_all("tr")
    cols = trs[1].find_all("td")
    bank = cols[1].get_text(strip=True)
    exchange = float(cols[2].get_text(strip=True))
    return bank, exchange

# Streamlit 設定
st.set_page_config(page_title="台幣換泰銖計算器", layout="centered")
st.title("💱 台幣換泰銖比較工具")

# 匯率資料
twd_usd_bank, twd_usd = get_twd_usd()
twd_thb_bank, twd_thb = get_twd_thb()

st.write(f"**目前 TWD/USD 匯率：** {twd_usd}（{twd_usd_bank}）")
st.write(f"**目前 TWD/THB 匯率：** {twd_thb}（{twd_thb_bank}）")

# 使用者輸入
twd_thb_superrich = st.number_input("SuperRich TWD/THB 匯率", min_value=0.0, value=1.0, step=0.001)
usd_thb_superrich = st.number_input("SuperRich USD/THB 匯率", min_value=0.0, value=1.0, step=0.001)
fee = st.number_input("手續費（NTD）", min_value=0.0, value=15.0, step=1.0)
spend = st.number_input("預計換多少台幣（NTD）", min_value=0.0, value=10000.0, step=100.0)

# 計算
exchange_in_Taiwan = twd_thb * (spend - fee)
exchange_in_Thai = twd_thb_superrich * spend
exchange_twice = (1 / twd_usd) * usd_thb_superrich * (spend - fee)
output3 = exchange_in_Thai - exchange_in_Taiwan
output4 = exchange_twice - exchange_in_Taiwan
difference = exchange_twice - exchange_in_Thai

# 結果
st.subheader("📊 計算結果")
st.write(f"方法1 - 在泰國換泰銖：**{exchange_in_Thai:.3f} THB**")
st.write(f"方法2 - 在台灣換美元再換泰銖：**{exchange_twice:.3f} THB**")
st.write(f"方法1 比在台灣換多：**{output3:.3f} THB**")
st.write(f"方法2 比在台灣換多：**{output4:.3f} THB**")
st.write(f"方法2 比方法1 多賺：**{difference:.3f} THB**")
