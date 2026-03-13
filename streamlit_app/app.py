import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# --- 1. 基本設定 ---
st.set_page_config(page_title="Msrlub v2.1", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #1e2129; border: 1px solid #3e4149; padding: 15px; border-radius: 12px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub v2.1")

# --- 2. 銘柄データ設定 ---
TICKERS = {'JT': '2914.T', 'SB': '9434.T', 'IHI': '7013.T', 'INPEX': '1605.T'}
DIV_MONTHS = {'JT': [3, 9], 'SB': [6, 12], 'IHI': [6, 12], 'INPEX': [3, 9]}

# --- 3. サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    jt_target = st.number_input("JT目標株数", value=100)
    st.divider()
    st.caption("v2.1: 時価・配当・AI統合版")

# --- 4. 解析・データ取得ロジック ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return data.fast_info['last_price']
    except:
        return 0

def analyze_rakuten_csv(file):
    try:
        lines = file.read().decode("shift_jis").splitlines()
        file.seek(0)
        header_idx = next(i for i, l in enumerate(lines) if "銘柄" in l and "数量" in l)
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_idx, on_bad_lines='skip')
        df.columns = df.columns.str.normalize('NFKC').str.strip()
        
        res = {}
        name_c = next(c for c in df.columns if any(k in c for k in ['銘柄', '商品']))
        qty_c = next(c for c in df.columns if any(k in c for k in ['数量', '残高']))
        
        target_map = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
        for key, name in target_map.items():
            row = df[df[name_c].str.contains(name, na=False)]
            res[key] = float(str(row[qty_c].iloc[0]).replace(',', '')) if not row.empty else 0
        return res
    except: return None

# --- 5. メイン表示部 ---
uploaded_file = st.file_uploader("楽天証券CSVをアップロードして起動", type="csv")

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        # 株価取得
        with st.spinner("最新株価を取得中..."):
            prices = {k: get_live_price(v) for k, v in TICKERS.items()}
        
        # A. リアルタイム時価・進捗
        st.subheader("🎯 セミリタイア進捗 & 時価評価")
        
        # JT表示
        jt_val = prices['JT'] * data['JT']
        st.metric("JT (2914)", f"{data['JT']:.0f} / {jt_target} 株", f"時価: ¥{jt_val:,.0f}")
        st.progress(min(data['JT']/jt_target, 1.0))
        
        # IHI & SB表示
        c1, c2 = st.columns(2)
        with c1:
            ihi_val = prices['IHI'] * data['IHI']
            st.metric("IHI (7013)", f"{data['IHI']:.0f} 株", f"時価: ¥{ihi_val:,.0f}")
        with c2:
            sb_val = prices['SB'] * data['SB']
            st.metric("ソフトバンク (9434)", f"{data['SB']:.0f} 株", f"時価: ¥{sb_val:,.0f}")

        # B. 配当カレンダー
        st.divider()
        st.subheader("🗓️ 年間配当受取スケジュール")
        months = [f"{i}月" for i in range(1, 13)]
        cal_counts = [0] * 12
        for k, ms in DIV_MONTHS.items():
            if data.get(k, 0) > 0:
                for m in ms:
                    cal_counts[m-1] += 1
        
        chart_df = pd.DataFrame({'銘柄数': cal_counts}, index=months)
        st.bar_chart(chart_df)
        st.caption("💡 7月・8月の空白を埋める銘柄（積水ハウス、J-REIT等）が次の狙い目です。")

        # C. 収穫アラート
        st.divider()
        st.subheader("🔔 収穫・銘柄入替サイン")
        if prices['IHI'] > 0:
            current_ihi = prices['IHI']
            # 仮の判断：8000円を超えたら強気利確圏
            if current_ihi > 8500:
                st.warning(f"🚀 IHI (¥{current_ihi:,.0f}) は利確検討ゾーンです。JTへの資金移動を推奨。")
            else:
                st.info(f"IHIは現在 ¥{current_ihi:,.0f}。目標の¥8,500まで継続ホールド。")

        # D. AIアシスタント
        st.divider()
        if api_key:
            genai.configure(api_key=api_key)
            if st.button("🤖 AIに本日の戦略を聞く"):
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"保有:JT {data['JT']}株, IHI {data['IHI']}株。IHIは現在 ¥{prices['IHI']}です。セミリタイアに向けて今すべきことを100文字以内で。"
                res = model.generate_content(prompt)
                st.chat_message("assistant").write(res.text)
else:
    st.info("👆 スマホで楽天証券から保存したCSVをここにドロップしてください。")
