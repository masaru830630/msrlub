亀梨、おおくら

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Msrlub v2.9", layout="wide")
st.title("🚀 Msrlub v2.9")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file is not None:
    content = uploaded_file.read().decode("shift_jis")
    lines = content.splitlines()
    
    # 探索対象のキーワード
    targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'IHI', 'INPEX': 'INPEX'}
    results = {k: 0 for k in targets}
    
    # 行ごとにループ
    for line in lines:
        for key, keyword in targets.items():
            if keyword in line:
                # 行をカンマで分解
                parts = line.split(',')
                # この行の中で、キーワードが含まれるインデックスを探す
                for i, p in enumerate(parts):
                    if keyword in p:
                        # 銘柄名の隣や、一定範囲内にある数字を探す（楽天CSVの構造）
                        # 銘柄名(i)の直後から、数ステップ以内の数字を探す
                        for j in range(i + 1, min(i + 5, len(parts))):
                            val_str = parts[j].replace('"', '').replace(',', '').strip()
                            # それが数字かつ、明らかに株数（資産合計の桁数でない）か判定
                            if val_str.isdigit() and 0 < int(val_str) < 100000:
                                results[key] = int(val_str)
                                break
    
    st.success("解析完了！")
    cols = st.columns(3)
    cols[0].metric("JT", f"{results['JT']:,}株")
    cols[1].metric("IHI", f"{results['IHI']:,}株")
    cols[2].metric("SB", f"{results['SB']:,}株")
