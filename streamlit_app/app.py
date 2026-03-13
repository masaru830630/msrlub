import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

st.set_page_config(page_title="Msrlub v2.3", layout="wide")

st.title("🚀 Msrlub v2.3")
uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

def analyze_rakuten_csv(file):
    try:
        # 1. 全行を一旦読み込む（ヘッダー指定なしで全行テキストとして）
        df_raw = pd.read_csv(file, encoding="shift_jis", header=None)
        
        # 2. 銘柄名と数量の列を探す（全セルを検索）
        # 銘柄が含まれる行番号を探す
        header_row_idx = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains('銘柄').any(), axis=1)].index[0]
        
        # 3. その行をヘッダーとして再読み込み
        file.seek(0)
        df = pd.read_csv(file, encoding="shift_jis", skiprows=header_row_idx)
        df.columns = df.columns.str.normalize('NFKC').str.strip()
        
        # 4. 必要な列を特定
        name_c = [c for c in df.columns if '銘柄' in c or '商品' in c][0]
        qty_c = [c for c in df.columns if '数量' in c or '残高' in c][0]
        
        # 5. データ抽出
        res = {}
        targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
        for k, name in targets.items():
            # 文字列型に強制変換してから検索
            match = df[df[name_c].astype(str).str.contains(name, na=False)]
            res[k] = float(str(match[qty_c].iloc[0]).replace(',', '')) if not match.empty else 0
        return res
    except Exception as e:
        st.error(f"解析失敗: {e}")
        return None

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        st.success("解析成功！")
        # 簡易株価取得
        prices = {'JT': 3800, 'IHI': 8000, 'SB': 2000} # yfinanceのエラー回避のため一旦固定値も用意
        
        c1, c2, c3 = st.columns(3)
        c1.metric("JT", f"{data['JT']:.0f}株")
        c2.metric("IHI", f"{data['IHI']:.0f}株")
        c3.metric("SB", f"{data['SB']:.0f}株")
    else:
        st.error("データが見つかりません。")
