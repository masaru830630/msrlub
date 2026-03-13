import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Msrlub v2.8", layout="wide")
st.title("🚀 Msrlub v2.8")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file is not None:
    content = uploaded_file.read().decode("shift_jis")
    lines = content.splitlines()
    
    # 全データを抽出してテーブル化
    # 銘柄と数値のペアを探す
    data = []
    for line in lines:
        parts = [p.replace('"', '').strip() for p in line.split(',')]
        # 銘柄名と思われる文字列と、数量と思われる数値を探す
        for i, p in enumerate(parts):
            if len(p) > 2 and not p.isdigit() and i+1 < len(parts) and parts[i+1].replace(',','').isdigit():
                data.append({"銘柄": p, "数量": int(parts[i+1].replace(',',''))})
    
    df = pd.DataFrame(data)
    
    # 銘柄を選択できるようにする
    st.subheader("✅ 銘柄の紐付け")
    with st.sidebar:
        st.write("### CSV内の全銘柄")
        all_stocks = df['銘柄'].unique().tolist()
        sb_name = st.selectbox("ソフトバンクの表記を選んでください", all_stocks, index=0 if not all_stocks else 0)

    # 抽出処理
    results = {
        'SB': df[df['銘柄'] == sb_name]['数量'].sum() if sb_name in df['銘柄'].values else 0
    }
    
    st.metric("ソフトバンク", f"{results['SB']:,}株")
    
    with st.expander("詳細抽出データ"):
        st.write(df)
