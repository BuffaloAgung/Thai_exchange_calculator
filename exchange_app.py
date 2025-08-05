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
@st.cache_data(ttl=300)  # 快取5分鐘
def get_twd_usd():
    try:
        url = "https://www.findrate.tw/USD/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        table = soup.find("table")
        if not table:
            return "資料來源", 31.5  # 預設值
            
        trs = table.find_all("tr")
        if len(trs) < 2:
            return "資料來源", 31.5
            
        cols = trs[1].find_all("td")
        if len(cols) < 3:
            return "資料來源", 31.5
            
        bank = cols[1].get_text(strip=True)
        exchange_text = cols[2].get_text(strip=True)
        exchange = float(exchange_text)
        return bank, exchange
    except Exception as e:
        st.error(f"取得 TWD/USD 匯率失敗: {e}")
        return "資料來源", 31.5

@st.cache_data(ttl=300)  # 快取5分鐘
def get_twd_thb():
    try:
        url = "https://www.findrate.tw/THB/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        table = soup.find("table")
        if not table:
            return "資料來源", 0.9  # 預設值
            
        trs = table.find_all("tr")
        if len(trs) < 2:
            return "資料來源", 0.9
            
        cols = trs[1].find_all("td")
        if len(cols) < 3:
            return "資料來源", 0.9
            
        bank = cols[1].get_text(strip=True)
        exchange_text = cols[2].get_text(strip=True)
        exchange = float(exchange_text)
        return bank, exchange
    except Exception as e:
        st.error(f"取得 TWD/THB 匯率失敗: {e}")
        return "資料來源", 0.9

# 輔助函數
def safe_float(val):
    try:
        return float(val) if val else 0.0
    except:
        return 0.0

def safe_int(val):
    try:
        return int(float(val)) if val else 0
    except:
        return 0

# 標題
st.title("台幣 ➡️ 泰銖")

# 取得匯率
with st.spinner("正在取得最新匯率..."):
    twd_usd_bank, twd_usd = get_twd_usd()
    twd_thb_bank, twd_thb = get_twd_thb()

# 顯示當前匯率
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"**目前 TWD/USD 匯率：** {twd_usd}（{twd_usd_bank}）")
st.write(f"**目前 TWD/THB 匯率：** {twd_thb}（{twd_thb_bank}）")
st.write(f"**更新時間：** {current_time}")

st.divider()

# 輸入欄
col1, col2 = st.columns(2)

with col1:
    twd_thb_superrich = safe_float(st.text_input("SuperRich TWD/THB 匯率", value="0.97"))
    fee = safe_int(st.text_input("手續費（NTD）", value="15"))

with col2:
    usd_thb_superrich = safe_float(st.text_input("SuperRich USD/THB 匯率", value="34.5"))
    spend = safe_int(st.text_input("預計換多少台幣", value="10000"))

# 計算按鈕
if st.button("💰 開始計算", type="primary"):
    if spend <= 0:
        st.error("請輸入有效的台幣金額")
    elif fee >= spend:
        st.error("手續費不能大於或等於兌換金額")
    elif twd_thb_superrich <= 0 or usd_thb_superrich <= 0:
        st.error("請輸入有效的 SuperRich 匯率")
    else:
        # 計算
        # 方法1：直接在台灣換泰銖
        exchange_in_Taiwan = twd_thb * (spend - fee)
        
        # 方法2：在泰國用台幣換泰銖
        exchange_in_Thai = twd_thb_superrich * spend
        
        # 方法3：在台灣換美元，再在泰國換泰銖
        usd_amount = (spend - fee) / twd_usd
        exchange_twice = usd_amount * usd_thb_superrich
        
        # 差額計算
        diff_thai_vs_taiwan = exchange_in_Thai - exchange_in_Taiwan
        diff_usd_vs_taiwan = exchange_twice - exchange_in_Taiwan
        diff_usd_vs_thai = exchange_twice - exchange_in_Thai
        
        # 結果顯示
        st.subheader("📊 計算結果")
        
        # 建立三欄顯示
        result_col1, result_col2, result_col3 = st.columns(3)
        
        with result_col1:
            st.metric(
                label="方法1：台灣直接換",
                value=f"{exchange_in_Taiwan:.2f} THB",
                help="在台灣直接兌換泰銖"
            )
        
        with result_col2:
            st.metric(
                label="方法2：泰國換泰銖",
                value=f"{exchange_in_Thai:.2f} THB",
                delta=f"+{diff_thai_vs_taiwan:.2f} THB",
                help="帶台幣到泰國兌換"
            )
        
        with result_col3:
            st.metric(
                label="方法3：台灣換美元再換泰銖",
                value=f"{exchange_twice:.2f} THB",
                delta=f"+{diff_usd_vs_taiwan:.2f} THB",
                help="先在台灣換美元，再到泰國換泰銖"
            )
        
        st.divider()
        
        # 最佳建議
        best_method = max(
            [("台灣直接換", exchange_in_Taiwan),
             ("泰國換泰銖", exchange_in_Thai),
             ("台灣換美元再換泰銖", exchange_twice)],
            key=lambda x: x[1]
        )
        
        st.subheader("💡 建議")
        if best_method[0] == "台灣直接換":
            st.success(f"建議：**{best_method[0]}** 最划算！可得到 **{best_method[1]:.2f} THB**")
        elif best_method[0] == "泰國換泰銖":
            st.success(f"建議：**{best_method[0]}** 最划算！比台灣直接換多得到 **{diff_thai_vs_taiwan:.2f} THB**")
        else:
            st.success(f"建議：**{best_method[0]}** 最划算！比台灣直接換多得到 **{diff_usd_vs_taiwan:.2f} THB**")
        
        # 詳細比較
        with st.expander("詳細比較"):
            st.write("**方法比較：**")
            st.write(f"• 方法2 比方法1 多：**{diff_thai_vs_taiwan:.2f} THB**")
            st.write(f"• 方法3 比方法1 多：**{diff_usd_vs_taiwan:.2f} THB**")
            st.write(f"• 方法3 比方法2 多：**{diff_usd_vs_thai:.2f} THB**")

# 說明
with st.expander("使用說明"):
    st.write("""
    **三種兌換方式：**
    1. **台灣直接換**：在台灣銀行直接兌換泰銖（需扣手續費）
    2. **泰國換泰銖**：帶台幣到泰國的兌換點換泰銖
    3. **台灣換美元再換泰銖**：先在台灣換美元（扣手續費），再到泰國換泰銖
    
    **注意事項：**
    - SuperRich 是泰國知名的兌換點，匯率通常較好
    - 實際匯率可能因時間和地點而異
    - 建議出發前再次確認最新匯率
    """)