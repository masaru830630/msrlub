import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

st.set_page_config(page_title="Msrlub v2.2", layout="wide")

st.title("🚀 Msrlub v2.2")
uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

# --- 共通の関数 ---
def analyze_rakuten_csv(file):
    try:
        content = file.read().decode("shift_jis").splitlines()
        file.seek(0)
        # 「銘柄」と「数量」が含まれる行を探す
        header_idx = next(i for i, l in enumerate(content) if "銘柄" in l and "数量" in l)
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_idx, on_bad_lines='skip')
        df.columns = df.columns.str.normalize('NFKC').str.strip()
        
        res = {}
        name_c = next(c for c in df.columns if any(k in c for k in ['銘柄', '商品']))
        qty_c = next(c for c in df.columns if any(k in c for k in ['数量', '残高']))
        
        target_map = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
        for k, name in target_map.items():
            row = df[df[name_c].str.contains(name, na=False)]
            res[k] = float(str(row[qty_c].iloc[0]).replace(',', '')) if not row.empty else 0
        return res
    except Exception as e:
        st.error(f"解析エラー: {e}")
        return None

# --- メイン処理 ---
if uploaded_file is not None:
    data = analyze_rakuten_csv(uploaded_file)
    
    if data:
        st.success("解析完了！")
        # 株価取得
        prices = {k: yf.Ticker(v).fast_info['last_price'] for k, v in {'JT': '2914.T', 'SB': '9434.T', 'IHI': '7013.T'}.items()}
        
        # 1. 進捗表示
        st.subheader("🎯 目標達成状況")
        c1, c2, c3 = st.columns(3)
        c1.metric("JT", f"{data['JT']:.0f}株", f"¥{data['JT']*prices['JT']:,.0f}")
        c2.metric("IHI", f"{data['IHI']:.0f}株", f"¥{data['IHI']*prices['IHI']:,.0f}")
        c3.metric("SB", f"{data['SB']:.0f}株", f"¥{data['SB']*prices['SB']:,.0f}")
        
        # 2. 配当グラフ
        st.subheader("🗓️ 配当カレンダー")
        st.bar_chart(pd.DataFrame({'銘柄数': [0,0,1,0,0,1,0,0,1,0,0,1]}, index=[f"{i}月" for i in range(1,13)]))

        # 3. 利確アラート
        if prices['IHI'] > 8500:
            st.warning("⚠️ IHI利確推奨ライン超え")
        else:
            st.info("IHIホールド中")
            
    else:
        st.error("データが取得できませんでした。CSVの中身を確認してください。")
else:
    st.info("CSVをアップロードしてください。")
