import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import google.generativeai as genai

# --- 1. 設定 & UI構成 ---
st.set_page_config(page_title="Msrlub - FIRE Engine", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Msrlub")
st.caption("2026年 セミリタイアへの航海日誌")

# --- 2. サイドバー：目標設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.divider()
    jt_target = st.number_input("JT目標株数", value=100)
    sb_target = st.number_input("ソフトバンク目標株数", value=10)

# --- 3. 楽天CSV解析ロジック (超柔軟版) ---
def analyze_rakuten_csv(file):
    try:
        # 楽天CSVはShift-JIS、エラー行は飛ばす
        df = pd.read_csv(file, encoding="shift_jis", on_bad_lines='skip')
        
        portfolio = {}
        target_names = {
            'JT': '日本たばこ産業',
            'SB': 'ソフトバンク',
            'IHI': 'ＩＨＩ',
            'INPEX': 'ＩＮＰＥＸ'
        }

        # --- 賢いカラム特定ロジック ---
        # 銘柄名が入っていそうな列を探す
        name_col = next((c for c in df.columns if any(k in str(c) for k in ['銘柄', '商品', '名称'])), None)
        # 数量が入っていそうな列を探す
        qty_col = next((c for c in df.columns if any(k in str(c) for k in ['数量', '残高', '保有数量'])), None)

        # デバッグ用：カラムが見つからない場合に情報を出す
        if not name_col or not qty_col:
            st.warning(f"CSVの項目を自動判定できませんでした。")
            st.write("CSVに含まれる項目名:", list(df.columns))
            return None

        # データクレンジング
        df[name_col] = df[name_col].astype(str)
        
        for key, full_name in target_names.items():
            # 銘柄名が含まれる行を抽出
            target_row = df[df[name_col].str.contains(full_name, na=False, case=False)]
            
            if not target_row.empty:
                # 数量列の値を数値化（カンマ除去など）
                val_str = str(target_row[qty_col].iloc[0]).replace(',', '').replace(' ', '')
                try:
                    portfolio[key] = float(val_str)
                except ValueError:
                    portfolio[key] = 0
            else:
                portfolio[key] = 0
        
        return portfolio
    except Exception as e:
        st.error(f"解析エラー: {e}")
        return None

# --- 4. メインコンテンツ ---
uploaded_file = st.file_uploader("楽天証券CSVをドロップして更新", type="csv")

if uploaded_file:
    data = analyze_rakuten_csv(uploaded_file)
    if data:
        st.subheader("🎯 目標達成状況")
        c1, c2, c3 = st.columns(3)
        
        # データの取得（辞書から取得）
        jt_curr = data.get('JT', 0)
        sb_curr = data.get('SB', 0)
        ihi_curr = data.get('IHI', 0)

        with c1:
            diff = jt_curr - jt_target
            st.metric("JT (2914)", f"{jt_curr:.0f} / {jt_target} 株", f"{diff:.0f} 株")
            st.progress(min(jt_curr / jt_target, 1.0) if jt_target > 0 else 0)
            
        with c2:
            diff_sb = sb_curr - sb_target
            st.metric("SB (9434)", f"{sb_curr:.0f} / {sb_target} 株", f"{diff_sb:.0f} 株")
            st.progress(min(sb_curr / sb_target, 1.0) if sb_target > 0 else 0)

        with c3:
            st.metric("IHI (7013) 残高", f"{ihi_curr:.0f} 株", "利確検討" if ihi_curr > 100 else "ホールド")

# --- 5. AIデイトレ気づきエンジン ---
st.divider()
st.subheader("💡 今日の市場「熱量」と気づき")

if api_key:
    genai.configure(api_key=api_key)
    if st.button("AI分析を実行"):
        with st.spinner("Geminiが市場をスキャン中..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "あなたはプロの投資家です。現在の日本市場、特に重工、資源、高配当通信株の動向を踏まえ、個人投資家に向けた今日のアドバイスを3行でください。"
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"AI分析エラー: {e}")
else:
    st.warning("サイドバーでAPI Keyを設定すると、AI分析が有効になります。")

st.write("📈 主要セクターのトレンド (参考値)")
chart_data = pd.DataFrame(np.random.randn(10, 3).cumsum(axis=0), columns=['重工', '通信', '資源'])
st.line_chart(chart_data)
