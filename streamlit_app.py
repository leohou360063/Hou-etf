import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# 1. 頁面基礎設定
st.set_page_config(page_title="資產智慧導航", layout="centered")

# 2. 初始數據
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00713", "00937B", "00982A", "00981A", "00929", "00888"],
        "張數": [168.0, 78.0, 35.0, 100.0, 43.0, 32.0, 78.0, 83.0],
        "Beta": [0.81, 0.92, 0.72, 0.12, 0.95, 1.05, 0.98, 0.88],
        "預估Alpha%": [1.5, 2.0, 3.5, 0.2, 5.5, 6.2, 0.5, 1.2],
        "現價": [22.8, 26.1, 57.5, 15.9, 11.5, 12.8, 19.5, 14.2] 
    }
    st.session_state.df = pd.DataFrame(initial_data)

# 3. 核心計算邏輯 (先計算，後顯示，確保即時聯動)
df = st.session_state.df
# 計算權重與指標
valid_df = df[df["現價"] > 0].copy()
if not valid_df.empty:
    valid_df["市值"] = valid_df["張數"] * 1000 * valid_df["現價"]
    total_val = valid_df["市值"].sum()
    weights = valid_df["市值"] / total_val
    p_beta = (valid_df["Beta"] * weights).sum()
    p_alpha = (valid_df["預估Alpha%"] * weights).sum()
    
    # 夏普值模型 (Rf=1.5%, Market=6%)
    rf, mkt = 0.015, 0.06
    vol = p_beta * 0.15 # 波動隨 Beta 連動
    expected_ret = rf + p_beta*(mkt-rf) + (p_alpha/100)
    sharpe = (expected_ret - rf) / vol if vol > 0 else 0
else:
    total_val, p_beta, p_alpha, sharpe = 0, 0, 0, 0

# --- 📱 手機版抬頭顯示器 (置頂顯示) ---
st.title("💎 資產全自動體檢")

# 用大字卡直接顯示最重要的三個數字
st.markdown(f"""
<div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 8px solid #FFD700; color:white;">
    <p style="margin:0; font-size:16px;">組合總市值</p>
    <h1 style="margin:0; color:#FFD700;">${total_val/10000:,.1f} 萬</h1>
    <hr style="opacity:0.3">
    <div style="display: flex; justify-content: space-between;">
        <div><p style="margin:0; font-size:12px;">加權 Beta</p><b>{p_beta:.2f}</b></div>
        <div><p style="margin:0; font-size:12px;">預期 Alpha</p><b>+{p_alpha:.1f}%</b></div>
        <div><p style="margin:0; font-size:12px;">夏普值</p><b>{sharpe:.2f}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# 4. 同步與編輯區 (放到下面，不遮擋數據)
if st.button("🚀 點我同步最新行情"):
    with st.spinner('同步中...'):
        for index, row in df.iterrows():
            sym = str(row["標的"]).strip()
            for ext in [".TW", ".TWO", ""]:
                try:
                    p = yf.Ticker(sym+ext).history(period="1d")['Close'].iloc[-1]
                    st.session_state.df.at[index, "現價"] = round(p, 2)
                    break
                except: continue
    st.rerun()

st.subheader("📝 調整持股/參數")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

if sharpe > 0.8: st.balloons()
