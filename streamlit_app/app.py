import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Msrlub v2.6", layout="wide")
st.title("🚀 Msrlub v2.6")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file:
    # 1. どんな区切り文字でも強引に読むための設定
    # engine='python' は区切り文字を自動推論してくれるので強力です
    df = pd.read_csv(uploaded_file, encoding="shift_jis", sep=None, engine='python', on_bad_lines='skip')
    
    # 2. 全列の列名を正規化
    df.columns = df.columns.astype(str).str.normalize('NFKC').str.strip()
    
    # 3. デバッグ表示（中身を見れば全て解決する）
    with st.expander("🔍 CSVの中身を全公開"):
        st.write(df)
        st.write("カラム一覧:", df.columns.tolist())

    # 4. ここは変えず、上記で読み込んだdfから抽出
    # 実際のカラム名に合わせて調整してください
    try:
        # 名前が含まれる列を探す
        name_col = [c for c in df.columns if '銘柄' in c or '商品' in c][0]
        # 数量が含まれる列を探す
        qty_col = [c for c in df.columns if '数量' in c or '残高' in c][0]
        
        targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'IHI', 'INPEX': 'INPEX'}
        cols = st.columns(3)
        for i, (k, key_word) in enumerate(targets.items()):
            match = df[df[name_col].astype(str).str.contains(key_word, na=False, case=False)]
            val = float(str(match[qty_col].iloc[0]).replace(',', '')) if not match.empty else 0
            if i < 3:
                cols[i].metric(k, f"{val:.0f}株")
    except Exception as e:
        st.error(f"抽出エラー: {e}")
