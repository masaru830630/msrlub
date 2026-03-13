import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# --- 1. 設定 & スタイル ---
st.set_page_config(page_title="Msrlub v2.0", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2129; border: 1px solid #3e4149; padding: 15px; border-radius: 12px; }
    .stProgress > div > div > div > div { background-color: #1c83e1; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub v2.0")
st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- 2. 銘柄マスター設定 ---
TICKERS = {
    'JT': '2914.T',
    'SB': '9434.T',
    'IHI': '7013.T',
    'INPEX': '1605.T'
}
DIV_MONTHS = {
    'JT': [3, 9],    # 決算期ベースの入金目安
    'SB': [6, 12],
    'IHI': [6, 12],
    'INPEX': [3, 9]
}

# --- 3. サイドバー ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    jt_target = st.number_input("JT目標", value=100)
    ihi_alert_pct = st.slider("IHI利確アラート (高値からの下落%)", 0, 20, 5)

# --- 4. 関数群 ---
@st.cache_data(ttl=3600)
def get_stock_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return data.history(period="1d")['Close'].iloc[-1]
    except:
        return 0

def analyze_rakuten_csv(file):
    try:
        content = file.read().decode("shift_jis").splitlines()
        file.seek(0)
        header_index = next(i for i, line in enumerate(content) if "銘柄" in line and "数量" in line)
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_index, on_bad_lines='skip')
        portfolio = {}
        df.columns = df.columns.str.normalize('NFKC').str.strip()
        name_col = next(c for c in df.columns if any(k in c for k in ['銘柄', '商品']))
        qty_col = next(c for c in df.columns if any(k in c for k in ['数量', '残高']))
        
        target_map = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
        for key, name in target_map.items():
            row = df[df[name_col].str.contains(name, na=False)]
            portfolio[key] = float(str(row[qty_col].iloc[0]).replace(',', '')) if not row.empty else 0
        return portfolio
    except: return None

# --- 5. メイン処理 ---
uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        st.subheader("📊 リアルタイム評価 & 進捗")
        prices = {k: get_stock_price(v) for k, v in TICKERS.items()}
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("JT (2914)", f"{data['JT']:.0f} / {jt_target} 株", f"時価: ¥{prices['JT']*data['JT']:,.0f}")
            st.progress(min(data['JT']/jt_target, 1.0))
        with c2:
            st.metric("IHI (7013)", f"{data['IHI']:.0f} 株", f"評価額: ¥{prices['IHI']*data['IHI']:,.0f}")
        with c3:
            st.metric("SB (9434)", f"{data['SB']:.0f} 株", f"時価: ¥{prices['SB']*data['SB']:,.0f}")

        # --- 6. 配当カレンダーの視覚化 ---
        st.divider()
        st.subheader("🗓️ 配当受取予定カレンダー")
        cal_data = pd.DataFrame(0, index=["配当"], columns=[f"{i}月" for i in range(1, 13)])
        for key, months in DIV_MONTHS.items():
            for m in months:
                cal_data.at["配当", f"{m}月"] += 1 # 簡易的に銘柄数をカウント
        
        st.bar_chart(cal_data.T)
        st.caption("⚠️ 7月・8月が空白です。この期間の権利確定銘柄（積水ハウス等）の検討を推奨します。")

        # --- 7. IHI 収穫アラート ---
        st.divider()
        st.subheader("🔔 収穫（利確）アラート")
        ihi_price = prices['IHI']
        if ihi_price > 0:
            st.info(f"現在のIHI株価: ¥{ihi_price:,.0f}")
            if ihi_price > 8000: # 仮のターゲット価格
                st.warning("🎯 IHIがターゲット価格を超えています！JTへの資金移動を検討してください。")
            else:
                st.success("IHIは現在ホールド圏内です。")

# --- 8. AIアシスタント ---
st.divider()
if api_key:
    genai.configure(api_key=api_key)
    if st.button("🤖 AIに戦略を相談する"):
        with st.spinner("ポートフォリオを分析中..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            context = f"現在、JTを{data['JT']}株、IHIを{data['IHI']}株保有。セミリタイアを目指しています。今の市場での次の一手は？" if uploaded_file else "市場環境についてアドバイスを。"
            res = model.generate_content(context + " 3行で簡潔に。")
            st.chat_message("assistant").write(res.text)
