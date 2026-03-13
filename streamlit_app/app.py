import streamlit as st
import pandas as pd

st.set_page_config(page_title="Msrlub Final", layout="wide")
st.title("🚀 Msrlub Final")

# 1. シンプルなファイルアップローダー
uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

if uploaded_file is not None:
    # 2. ファイルをテキストとして全行読み込み、エラーを回避
    content = uploaded_file.read().decode("shift_jis")
    lines = content.splitlines()
    
    # 3. 必要な情報を手動で抽出するロジック
    # 行ごとに、「JT」「ソフトバンク」などのキーワードがあるかを探す
    targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
    results = {k: 0 for k in targets}
    
    for line in lines:
        for key, keyword in targets.items():
            if keyword in line:
                # 行をカンマで分割
                parts = line.split(',')
                # カンマ区切りのどこかに数字（数量）が含まれているか探す
                for p in parts:
                    clean_p = p.replace('"', '').replace(',', '').strip()
                    if clean_p.isdigit():
                        results[key] = float(clean_p)
    
    # 4. 結果を表示
    st.success("解析完了！")
    cols = st.columns(3)
    cols[0].metric("JT", f"{results['JT']:.0f}株")
    cols[1].metric("IHI", f"{results['IHI']:.0f}株")
    cols[2].metric("SB", f"{results['SB']:.0f}株")
    
    # デバッグ用に全行を表示
    with st.expander("詳細データ確認"):
        st.write(results)
else:
    st.info("CSVをアップロードしてください")
