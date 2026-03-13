import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

# --- 1. 設定 & UI構成 ---
st.set_page_config(page_title="Msrlub - FIRE Engine", layout="wide", initial_sidebar_state="collapsed")

# 背景と文字色のコントラストを修正
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #464b5d;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricLabel"] { color: #808495 !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub")
st.caption("2026年 セミリタイアへの航海日誌")

# --- 2. サイドバー ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    jt_target = st.number_input("JT目標", value=100)
    sb_target = st.number_input("SB目標", value=10)

# --- 3. 楽天CSV解析 (表記ゆれ対応強化) ---
def analyze_rakuten_csv(file):
    try:
        content = file.read().decode("shift_jis").splitlines()
        file.seek(0)
        
        header_index = 0
        for i, line in enumerate(content):
            if any(k in line for k in ["銘柄", "商品", "名称"]) and any(k in line for k in ["数量", "残高"]):
                header_index = i
                break
        
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_index, on_bad_lines='skip')
        portfolio = {}
        # 銘柄名を部分一致かつ正規化して判定
        target_map = {
            'JT': ['日本たばこ', 'ＪＴ', '2914'],
            'SB': ['ソフトバンク', '9434'],
            'IHI': ['ＩＨＩ', 'IHI', '7013'],
            'INPEX': ['ＩＮＰＥＸ', 'INPEX', '1605']
        }

        name_col = next((c for c in df.columns if any(k in str(c) for k in ['銘柄', '商品', '名称'])), None)
        qty_col = next((c for c in df.columns if any(k in str(c) for k in ['数量', '残高', '保有数量'])), None)

        if name_col and qty_col:
            df[name_col] = df[name_col].astype(str).str.normalize('NFKC') # 全角半角を正規化
            for key, keywords in target_map.items():
                # いずれかのキーワードが含まれる行を探す
                mask = df[name_col].apply(lambda x: any(k in x for k in keywords))
                target_row = df[mask]
                if not target_row.empty:
                    val = str(target_row[qty_col].iloc[0]).replace(',', '').replace(' ', '')
                    portfolio[key] = float(val) if val != 'nan' else 0
                else:
                    portfolio[key] = 0
        return portfolio
    except Exception as e:
        st.error(f"解析エラー: {e}")
        return None

# --- 4. メイン ---
uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        st.subheader("🎯 目標達成状況")
        # スマホで見やすいよう、1列ずつ並べる（columnsを使わずそのまま並べる）
        jt_curr = data.get('JT', 0)
        sb_curr = data.get('SB', 0)
        ihi_curr = data.get('IHI', 0)

        st.metric("JT (2914)", f"{jt_curr:.0f} / {jt_target} 株", f"{jt_curr - jt_target:.0f} 株")
        st.progress(min(jt_curr / jt_target, 1.0) if jt_target > 0 else 0)
        st.write("") # スペース空け

        st.metric("ソフトバンク (9434)", f"{sb_curr:.0f} / {sb_target} 株", f"{sb_curr - sb_target:.0f} 株")
        st.progress(min(sb_curr / sb_target, 1.0) if sb_target > 0 else 0)
        st.write("")

        st.metric("IHI (7013) 残高", f"{ihi_curr:.0f} 株", "利確準備" if ihi_curr > 100 else "ホールド中")

# --- 5. AI分析 ---
st.divider()
if api_key:
    genai.configure(api_key=api_key)
    if st.button("AI市場分析を実行"):
        with st.spinner("スキャン中..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content("日本市場の重工・通信・高配当株について、今日のデイトレード戦略を3行で。")
            st.info(res.text)
