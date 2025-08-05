import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime

# 頁面設定
st.set_page_config(
    page_title="台幣換泰銖計算器",
    page_icon="💸",
    layout="centered"
)

# 爬蟲函數
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

# 取得匯率 & 更新時間
update_time = datetime.now()
twd_usd_bank, twd_usd = get_twd_usd()
twd_thb_bank, twd_thb = get_twd_thb()

# 標題
st.title("台幣 ➡️ 泰銖")
st.write(f"**目前 TWD/USD 匯率：** {twd_usd}（{twd_usd_bank}） — 更新於 { (datetime.now() - update_time).seconds } 秒前")
st.write(f"**目前 TWD/THB 匯率：** {twd_thb}（{twd_thb_bank}） — 更新於 { (datetime.now() - update_time).seconds } 秒前")

# 輸入欄（用文字輸入，避免 + / - 按鈕）
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def safe_int(val):
    try:
        return int(float(val))  # 小數自動捨去
    except:
        return 0

twd_thb_superrich = safe_float(st.text_input("SuperRich TWD/THB 匯率", ""))
usd_thb_superrich = safe_float(st.text_input("SuperRich USD/THB 匯率", ""))
fee = safe_int(st.text_input("手續費（NTD）", "15"))
spend = safe_int(st.text_input("預計換多少台幣", "10000"))

# 計算按鈕
if st.button("計算"):
    # 計算
    exchange_in_Taiwan = twd_thb * (spend - fee)
    exchange_in_Thai = twd_thb_superrich * spend
    exchange_twice = (1 / twd_usd) * usd_thb_superrich * (spend - fee)
    output3 = exchange_in_Thai - exchange_in_Taiwan
    output4 = exchange_twice - exchange_in_Taiwan
    difference = exchange_twice - exchange_in_Thai

    # 結果
    st.subheader("📊 計算結果")
    st.write(f"方法1 - 在泰國換泰銖：           **{exchange_in_Thai:.2f} THB**")
    st.write(f"方法2 - 在台灣換美元再換泰銖：    **{exchange_twice:.2f} THB**")
    st.write(f"-----------------------------------------------------------")
    st.write(f"方法1 比在台灣換多：**{output3:.2f} THB**")
    st.write(f"方法2 比在台灣換多：**{output4:.2f} THB**")
    st.write(f"-----------------------------------------------------------")
    st.markdown(f"<h3>方法2 比 方法1 多賺：<b>{difference:.2f} THB</b></h3>", unsafe_allow_html=True)
