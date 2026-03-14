import streamlit as st
import pandas as pd
import config

st.set_page_config(page_title="Msrlub FIRE Dashboard", layout="wide")
st.title("🚀 Msrlub: Road to 10万円/月")

# --- データ入力エリア ---
st.sidebar.header("データアップロード")
uploaded_file = st.sidebar.file_uploader("楽天証券CSVを選択", type="csv")

# 資産の計算ロジック
def calculate_metrics(rakuten_div_annual):
    monthly_div = rakuten_div_annual / 12
    current_passive = monthly_div + config.FIXED_INCOME_MONTHLY
    progress = (current_passive / config.GOAL_MONTHLY_INCOME) * 100
    return current_passive, progress

# --- メインコンテンツ ---
if uploaded_file is not None:
    # 簡易的な配当計算（本来はCSVの銘柄名から計算するロジックが入る場所）
    # 一旦、テスト用に現在の推定配当を入れています
    rakuten_div_annual = 120000 # 仮の年間配当（後でCSV解析ロジックと結合）
    
    current_total, progress_rate = calculate_metrics(rakuten_div_annual)
    
    # メトリクス表示
    col1, col2, col3 = st.columns(3)
    col1.metric("現在の不労所得/月", f"¥{int(current_total):,}")
    col2.metric("目標達成率", f"{progress_rate:.1f}%")
    col3.metric("目標まであと", f"¥{int(config.GOAL_MONTHLY_INCOME - current_total):,}")

    st.progress(min(progress_rate/100, 1.0))
    
    # 未来予測グラフ
    st.subheader("📈 24ヶ月後の未来予測")
    months = list(range(25))
    future_data = [current_total + (config.MONTHLY_INVESTMENT * config.EXPECTED_YIELD / 12 * m) for m in months]
    st.line_chart(pd.DataFrame({"月数": months, "不労所得予測": future_data}).set_index("月数"))

else:
    st.info("左のサイドバーから楽天証券のCSVをアップロードしてください。")
    st.write("※現在は『固定収入 5.5万円』の状態からスタートします。")
