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

# --- 3. 楽天CSV解析ロジック (行スキップ対応版) ---
def analyze_rakuten_csv(file):
    try:
        # 一旦テキストとして読み込み、実際のヘッダーがどこにあるか探す
        content = file.read().decode("shift_jis").splitlines()
        file.seek(0) # ポインタを戻す

        skip_rows = 0
        header_index = 0
        for i, line in enumerate(content):
            if any(k in line for k in ["銘柄", "商品", "名称"]) and any(k in line for k in ["数量", "残高"]):
                header_index = i
                break
        
        # 特定したヘッダー行から読み込み開始
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_index, on_bad_lines='skip')
        
        portfolio = {}
        target_names = {'JT': '日本たばこ産業', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}

        # カラムの再特定
        name_col = next((c for c in df.columns if any(k in str(c) for k in ['銘柄', '商品', '名称'])), None)
        qty_col = next((c for c in df.columns if any(k in str(c) for k in ['数量', '残高', '保有数量'])), None)

        if not name_col or not qty_col:
            st.warning("銘柄データが見つかりませんでした。資産内訳の表までスクロールしてください。")
            return None

        df[name_col] = df[name_col].astype(str)
        for key, full_name in target_names.items():
            target_row = df[df[name_col].str.contains(full_name, na=False, case=False)]
            if not target_row.empty:
                val_str = str(target_row[qty_col].iloc[0]).replace(',', '').replace(' ', '')
                portfolio[key] = float(val_str) if val_str != 'nan' else 0
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
        
        jt_curr = data.get('JT', 0)
        sb_curr = data.get('SB', 0)
        ihi_curr = data.get('IHI', 0)

        with c1:
            st.metric("JT (2914)", f"{jt_curr:.0f} / {jt_target} 株", f"{jt_curr - jt_target:.0f} 株")
            st.progress(min(jt_curr / jt_target, 1.0) if jt_target > 0 else 0)
            
        with c2:
            st.metric("SB (9434)", f"{sb_curr:.0f} / {sb_target} 株", f"{sb_curr - sb_target:.0f} 株")
            st.progress(min(sb_curr / sb_target, 1.0) if sb_target > 0 else 0)

        with c3:
            st.metric("IHI (7013) 残高", f"{ihi_curr:.0f} 株", "利確検討" if ihi_curr > 100 else "ホールド")

# --- 5. AI分析 ---
st.divider()
st.subheader("💡 今日の市場「熱量」と気づき")
if api_key:
    genai.configure(api_key=api_key)
    if st.button("AI分析を実行"):
        with st.spinner("Geminiが分析中..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("現在の日本市場、特に重工、資源、通信株の動向からデイトレのヒントを3行で。")
            st.info(response.text)
else:
    st.warning("サイドバーでAPI Keyを設定してください。")

st.write("📈 セクター推移（参考）")
st.line_chart(pd.DataFrame(np.random.randn(10, 3).cumsum(axis=0), columns=['重工', '通信', '資源']))
