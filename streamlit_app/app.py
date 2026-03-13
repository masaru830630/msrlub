import streamlit as st
import pandas as pd

st.set_page_config(page_title="Msrlub v2.7", layout="wide")
st.title("🚀 Msrlub v2.7")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file is not None:
    content = uploaded_file.read().decode("shift_jis")
    lines = content.splitlines()
    
    # 銘柄名とターゲットリスト
    targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
    results = {k: 0 for k in targets}
    
    # 全行をループして「銘柄名」が含まれる行を探し、その行の「数量」にあたる箇所を抽出
    # 楽天のCSVは「銘柄名,コード,市場,数量,...」の順になっていることが多いです
    for line in lines:
        for key, keyword in targets.items():
            if keyword in line:
                parts = line.split(',')
                # カンマ区切りのリストから、数字っぽい部分を探す
                # 数量列の位置を特定するための安全策
                for p in parts:
                    clean_p = p.replace('"', '').replace(',', '').strip()
                    # 50株以上などの現実的な数値を判定
                    if clean_p.isdigit() and int(clean_p) > 0:
                        results[key] = int(clean_p)
    
    # 表示
    st.success("解析成功！")
    cols = st.columns(3)
    cols[0].metric("JT", f"{results['JT']:,}株")
    cols[1].metric("IHI", f"{results['IHI']:,}株")
    cols[2].metric("SB", f"{results['SB']:,}株")
    
    with st.expander("詳細抽出データ"):
        st.write(results)
