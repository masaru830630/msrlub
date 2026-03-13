import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

# --- 1. 設定 & UI構成 ---
st.set_page_config(page_title="Msrlub - FIRE Engine", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub")
st.caption("2026年 セミリタイアへの航海日誌")

# --- 2. サイドバー：目標設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.divider()
    jt_target = st.number_input("JT目標株数", value=100)
    sb_target = st.number_input("ソフトバンク目標株数", value=10)

# --- 3. 楽天CSV解析ロジック (強化版) ---
def analyze_rakuten_csv(file):
    try:
        # 列数が合わない行（ヘッダーの重なり等）を無視して読み込む
        df = pd.read_csv(file, encoding="shift_jis", on_bad_lines='skip')
        
        portfolio = {}
        target_names = {
            'JT': '日本たばこ産業',
            'SB': 'ソフトバンク',
            'IHI': 'ＩＨＩ',
            'INPEX': 'ＩＮＰＥＸ'
        }

        # 銘柄名と数量が含まれる列を動的に特定
        name_col = None
        qty_col = None
        for col in df.columns:
            if any(k in col for k in ['銘柄', '商品']):
                name_col = col
            if any(k in col for k in ['数量', '残高']):
                qty_col = col

        if name_col and qty_col:
            df[name_col] = df[name_col].astype(str)
            for key, full_name in target_names.items():
                # 銘柄名が含まれる行を抽出
                target_row = df[df[name_col].str.contains(full_name, na=False)]
                if not target_row.empty:
                    # カンマを除去して数値化
                    val = target_row[qty_col].astype(str).str.replace(',', '').replace('nan', '0')
                    portfolio[key] = pd.to_numeric(val, errors='coerce').sum()
                else:
                    portfolio[key] = 0
        return portfolio
    except Exception as e:
        st.error(f"解析エラー: {e}")
        return None

# --- 4. メインコンテンツ ---
uploaded_file = st.file_uploader("楽天証券CSVをドロップして更新", type="csv")

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        st.subheader("🎯 目標達成状況")
        c1, c2, c3 = st.columns(3)
        
        # 目標値をサイドバーから取得
        jt_curr = data.get('JT', 0)
        sb_curr = data.get('SB', 0)
        ihi_curr = data.get('IHI', 0)

        with c1:
            st.metric("JT (2914)", f"{jt_curr:.0f} / {jt_target} 株", f"{jt_curr - jt_target:.0f} 株")
            st.progress(min(jt_curr / jt_target, 1.0) if jt_target > 0 else 0)
            
        with c2:
            st.metric("SB (9434)", f"{sb_curr:.0f} / {sb_target} 株", f"{sb_current - sb_target:.0f} 株" if 'sb_current' in locals() else "")
            st.progress(min(sb_curr / sb_target, 1.0) if sb_target > 0 else 0)

        with c3:
            st.metric("IHI (7013) 残高", f"{ihi_curr:.0f} 株", "利確検討" if ihi_curr > 100 else "ホールド")

# --- 5. AIデイトレ気づきエンジン ---
st.divider()
st.subheader("💡 今日の市場「熱量」と気づき")

if api_key:
    genai.configure(api_key=api_key)
    if st.button("AI分析を実行"):
        with st.spinner("Geminiが市場をスキャン中..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                # ここで最新の市場動向をGeminiに聞く
                prompt = "あなたはプロの株式トレーダーです。現在の日本市場（重工、資源、通信セクターなど）の動向を踏まえ、個人投資家が今日注目すべきデイトレードの視点を3行でアドバイスしてください。"
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"AI分析エラー: {e}")
else:
    st.warning("サイドバーでAPI Keyを設定すると、AI分析が有効になります。")

# --- 6. セクター・モメンタム (yfinance連携の準備) ---
st.write("📈 主要セクターのトレンド (参考値)")
# 将来的には yf.download を使ってリアルタイムチャート化
chart_data = pd.DataFrame(np.random.randn(10, 3).cumsum(axis=0), columns=['IHI系', '通信系', 'INPEX系'])
st.line_chart(chart_data)
