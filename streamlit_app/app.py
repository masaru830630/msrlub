import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Msrlub v2.4", layout="wide")
st.title("🚀 Msrlub v2.4")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

def robust_read_rakuten(file):
    # ファイルをテキストとして全行読み込む
    content = file.read().decode("shift_jis")
    lines = content.splitlines()
    
    # 「銘柄」と「数量」の両方を含む行を探す
    target_idx = -1
    for i, line in enumerate(lines):
        if "銘柄" in line and "数量" in line:
            target_idx = i
            break
            
    if target_idx == -1:
        return None, "CSV内に銘柄情報が見つかりません"
    
    # 見つけた行から下を改めてCSVとして読み込む
    data_stream = io.StringIO("\n".join(lines[target_idx:]))
    df = pd.read_csv(data_stream)
    
    # カラム名の正規化
    df.columns = df.columns.str.normalize('NFKC').str.strip()
    return df, None

if uploaded_file:
    df, error = robust_read_rakuten(uploaded_file)
    
    if error:
        st.error(error)
    else:
        # 必要な列を特定
        name_c = [c for c in df.columns if '銘柄' in c or '商品' in c][0]
        qty_c = [c for c in df.columns if '数量' in c or '残高' in c][0]
        
        # 簡易抽出
        st.success("解析成功！")
        targets = {'JT': '日本たばこ', 'SB': 'ソフトバンク', 'IHI': 'ＩＨＩ', 'INPEX': 'ＩＮＰＥＸ'}
        
        cols = st.columns(3)
        for i, (k, name) in enumerate(targets.items()):
            match = df[df[name_c].astype(str).str.contains(name, na=False)]
            val = float(str(match[qty_c].iloc[0]).replace(',', '')) if not match.empty else 0
            if i < 3:
                cols[i].metric(k, f"{val:.0f}株")
