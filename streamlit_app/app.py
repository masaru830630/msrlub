import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

# --- 1. 設定 & UI構成 ---
st.set_page_config(page_title="Msrlub - FIRE Engine", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSSでスマホ対応を強化
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub")
st.caption("22026年 セミリタイアへの航海日誌")

# --- 2. サイドバー：目標とAPI設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.divider()
    jt_target = st.number_input("JT目標株数", value=100)
    sb_target = st.number_input("ソフトバンク目標株数", value=10)

# --- 3. CSV解析ロジック ---
def analyze_rakuten_csv(file):
    try:
        # 楽天証券のCSVはShift-JISが多い
        df = pd.read_csv(file, encoding="shift_jis")
        
        # 簡易的な銘柄抽出ロジック（実際のCSV列名「銘柄名」「保有数量」を想定）
        # ※お使いのCSVに合わせてカラム名は微調整してください
        portfolio = {}
        if '銘柄' in df.columns or '銘柄名' in df.columns:
            name_col = '銘柄' if '銘柄' in df.columns else '銘柄名'
            qty_col = '保有数量' if '保有数量' in df.columns else '残高'
            
            portfolio['JT'] = df[df[name_col].str.contains('日本たばこ', na=False)][qty_col].sum()
            portfolio['SB'] = df[df[name_col].str.contains('ソフトバンク', na=False)][qty_col].sum()
            portfolio['IHI'] = df[df[name_col].str.contains('ＩＨＩ', na=False)][qty_col].sum()
            portfolio['INPEX'] = df[df[name_col].str.contains('ＩＮＰＥＸ', na=False)][qty_col].sum()
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
        
        with c1:
            jt_current = data.get('JT', 0)
            st.metric("JT (2914)", f"{jt_current:.0f} / {jt_target} 株", f"{jt_current - jt_target} 株")
            st.progress(min(jt_current / jt_target, 1.0))
            
        with c2:
            sb_current = data.get('SB', 0)
            st.metric("ソフトバンク (9434)", f"{sb_current:.0f} / {sb_target} 株", f"{sb_current - sb_target} 株")
            st.progress(min(sb_current / sb_target, 1.0))

        with c3:
            ihi_current = data.get('IHI', 0)
            st.metric("IHI (7013) 残高", f"{ihi_current:.0f} 株", "利確余力あり" if ihi_current > 100 else "ホールド")

# --- 5. AIデイトレ気づきエンジン ---
st.divider()
st.subheader("💡 今日の市場「熱量」と気づき")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if st.button("AI分析を実行"):
        with st.spinner("市場の歪みを検知中..."):
            # 本来はここでyfinance等のデータをプロンプトに渡す
            prompt = "現在の日本市場でボラティリティが高まっているセクターを3つ挙げ、デイトレードの観点から簡潔にアドバイスして。"
            response = model.generate_content(prompt)
            st.write(response.text)
else:
    st.warning("サイドバーでAPI Keyを設定すると、AI分析が有効になります。")

# --- 6. 市場センチメント（簡易版） ---
st.write("📈 セクター別モメンタム")
# ダミーデータでトレンドを表示（後ほどyfinanceと連携可能）
chart_data = pd.DataFrame(np.random.randn(10, 3).cumsum(axis=0), columns=['重工', '通信', '資源'])
st.line_chart(chart_data)
