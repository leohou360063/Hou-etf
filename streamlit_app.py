import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

# 1. 頁面基礎設定
st.set_page_config(page_title="資產與現金流導航", layout="centered")

# 2. 初始數據 (已加入 0056 與 元大龍頭)
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00713", "00937B", "00982A", "00981A", "0056", "元大龍頭"],
        "張數": [168.0, 78.0, 35.0, 100.0, 43.0, 32.0, 32.0, 15.0],
        "Beta": [0.81, 0.92, 0.72, 0.12, 0.95, 1.05, 0.85, 1.02],
        "預估Alpha%": [1.5, 2.0, 3.5, 0.2, 5.5, 6.2, 1.2, 4.5],
        "現價": [22.8, 26.1, 57.5, 15.9, 11.5, 12.8, 38.5, 15.2],
        "年配息金額": [2.2, 2.8, 3.6, 1.0, 0.6, 0.8, 2.5, 0.8],
        "配息月份": ["2,5,8,11", "3,6,9,12", "3,6,9,12", "每月", "每月", "每月", "1,4,7,10", "每月"]
    }
    st.session_state.df = pd.DataFrame(initial_data)

df = st.session_state.df

# --- 核心計算：12 個月現金流 (含防錯機制) ---
monthly_dividends = np.zeros(12)
for _, row in df.iterrows():
    try:
        annual_div = row["張數"] * 1000 * row["年配息金額"]
        months_str = str(row["配息月份"]).strip()
        
        if "月" in months_str or "every" in months_str.lower():
            monthly_dividends += (annual_div / 12)
        else:
            # 防錯解析：只取出數字並過濾掉符號
            import re
            month_list = [int(m) for m in re.findall(r'\d+', months_str)]
            if month_list:
                per_div = annual_div / len(month_list)
                for m in month_list:
                    if 1 <= m <= 12:
                        monthly_dividends[m-1] += per_div
    except:
        continue # 若該列輸入錯誤，跳過不計算，避免 App 崩潰

# --- 核心計算：Alpha/Beta/Sharpe ---
valid_df = df[df["現價"] > 0].copy()
if not valid_df.empty:
    valid_df["市值"] = valid_df["張數"] * 1000 * valid_df["現價"]
    total_val = valid_df["市值"].sum()
    weights = valid_df["市值"] / total_val
    p_beta = (valid_df["Beta"] * weights).sum()
    p_alpha = (valid_df["預估Alpha%"] * weights).sum()
    rf, mkt = 0.015, 0.06
    vol = p_beta * 0.15
    expected_ret = rf + p_beta*(mkt-rf) + (p_alpha/100)
    sharpe = (expected_ret - rf) / vol if vol > 0 else 0
else:
    total_val, p_beta, p_alpha, sharpe = 0, 0, 0, 0

# --- 📱 HUD 置頂顯示 ---
st.title("💎 資產與配息日曆")
st.markdown(f"""
<div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 8px solid #FFD700; color:white; margin-bottom:20px;">
    <p style="margin:0; font-size:14px; opacity:0.8;">預估年領股息</p>
    <h1 style="margin:0; color:#FFD700;">${monthly_dividends.sum()/10000:,.1f} 萬</h1>
    <div style="display: flex; justify-content: space-between; margin-top:10px;">
        <div style="text-align:center;"><p style="margin:0; font-size:10px; opacity:0.6;">Beta</p><b>{p_beta:.2f}</b></div>
        <div style="text-align:center;"><p style="margin:0; font-size:10px; opacity:0.6;">Alpha</p><b>+{p_alpha:.1f}%</b></div>
        <div style="text-align:center;"><p style="margin:0; font-size:10px; opacity:0.6;">Sharpe</p><b>{sharpe:.2f}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 📊 12 個月現金流圖表 ---
st.subheader("🗓️ 12個月預估現金流 (萬元)")
fig = go.Figure(data=[go.Bar(
    x=[f"{i}月" for i in range(1, 13)],
    y=monthly_dividends / 10000,
    marker_color='#FFD700',
    text=[f"${v/10000:.1f}" for v in monthly_dividends],
    textposition='auto',
)])
fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
st.plotly_chart(fig, use_container_width=True)

# --- 📝 數據編輯 ---
st.subheader("📝 調整配置 (請輸入代碼數字)")
if st.button("🚀 同步最新雲端行情"):
    for index, row in df.iterrows():
        sym = str(row["標的"]).strip()
        for ext in [".TW", ".TWO", ""]:
            try:
                p = yf.Ticker(sym+ext).history(period="1d")['Close'].iloc[-1]
                st.session_state.df.at[index, "現價"] = round(p, 2)
                break
            except: continue
    st.rerun()

edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df
