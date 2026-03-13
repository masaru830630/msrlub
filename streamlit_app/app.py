import streamlit as st
import pandas as pd

st.set_page_config(page_title="Msrlub v2.5", layout="wide")
st.title("🚀 Msrlub v2.5")

uploaded_file = st.file_uploader("楽天証券CSVをアップロード", type="csv")

def robust_read_rakuten(file):
    content = file.read().decode("shift_jis")
    lines = content.splitlines()
    target_idx = next((i for i, line in enumerate(lines) if "銘柄" in line and "数量" in line), -1)
    if target_idx == -1: return None, "銘柄/数量のヘッダーが見つかりません"
    
    # データを読み込み
    import io
    df = pd.read_csv(io.StringIO("\n".join(lines[target_idx:])))
    df.columns = df.columns.str.normalize('NFKC').str.strip()
    return df, None

if uploaded_file:
    df, error = robust_read_rakuten(uploaded_file)
    if error:
        st.error(error)
    else:
        name_c = [c for c in df.columns if '銘柄' in c or '商品' in c][0]
        qty_c = [c for c in df.columns if '数量' in c or '残高' in c][0]
        
        # --- デバッグ機能：CSV内の銘柄リストを表示 ---
        with st.expander("🔍 CSV内の銘柄リストを確認"):
            st.write(df[name_c].unique().tolist())
        
        # --- 検索ロジックの強化 ---
        targets = {'JT': 'JT', 'SB': 'ソフトバンク', 'IHI': 'IHI', 'INPEX': 'INPEX'}
        
        cols = st.columns(3)
        for i, (k, key_word) in enumerate(targets.items()):
            # 全角/半角、大文字/小文字を無視して検索
            match = df[df[name_c].astype(str).str.contains(key_word, na=False, case=False)]
            
            # 数値抽出（カンマ除去）
            val = 0
            if not match.empty:
                raw_val = str(match[qty_c].iloc[0]).replace(',', '')
                # 数字のみを抽出
                import re
                nums = re.findall(r'\d+', raw_val)
                val = float(nums[0]) if nums else 0
            
            if i < 3:
                cols[i].metric(k, f"{val:.0f}株")
