import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="大戶資產全自動導航", layout="centered")
st.title("💎 全自動數據同步儀表板")

# 1. 初始數據
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00713", "00937B", "00982A", "00981A", "2330"],
        "張數": [168.0, 78.0, 35.0, 100.0, 43.0, 32.0, 5.0],
        "Beta": [0.81, 0.92, 0.72, 0.12, 0.95, 1.05, 1.25],
        "預估Alpha%": [1.5, 2.0, 3.5, 0.2, 5.5, 6.2, 4.0],
        "現價": [0.0] * 7
    }
    st.session_state.df = pd.DataFrame(initial_data)

# 2. 核心功能：一鍵同步所有數據 (股價 + Beta)
if st.button("🚀 一鍵同步最新市場數據 (股價 & Beta)"):
    with st.spinner('正在連線交易所與分析中心...'):
        for index, row in st.session_state.df.iterrows():
            symbol = str(row["標的"]).strip()
            for suffix in [".TW", ".TWO", ""]:
                try:
                    tk = yf.Ticker(symbol + suffix)
                    # 抓取股價
                    hist = tk.history(period="1d")
                    if not hist.empty:
                        st.session_state.df.at[index, "現價"] = round(hist['Close'].iloc[-1], 2)
                        
                        # 嘗試抓取 Beta (Yahoo Finance 提供之數據)
                        # 注意：並非所有 ETF 都有 Beta 數據，若無則保留原值
                        info = tk.info
                        market_beta = info.get('beta')
                        if market_beta:
                            st.session_state.df.at[index, "Beta"] = round(market_beta, 2)
                        break
                except: continue
    st.success("同步完成！(部分 ETF 若無公開 Beta 則保留手動設定值)")
    st.rerun()

# 3. 互動編輯表格
st.subheader("📝 資產配置清單")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

# 4. 即時聯動計算
if not edited_df.empty and edited_df["現價"].sum() > 0:
    # 權重計算
    edited_df["市值"] = edited_df["張數"] * 1000 * edited_df["現價"]
    total_value = edited_df["市值"].sum()
    weights = edited_df["市值"] / total_value
    
    # 指標計算
    p_beta = (edited_df["Beta"] * weights).sum()
    p_alpha = (edited_df["預估Alpha%"] * weights).sum()
    
    # 夏普值模型 (Rf=1.5%, 市場預期回報=6%)
    rf, market_ret = 0.015, 0.06
    # 組合回報 = Rf + Beta*(Market_Ret - Rf) + Alpha
    expected_portfolio_return = rf + p_beta * (market_ret - rf) + (p_alpha / 100)
    # 波動率預算：假設市場標準差 15%
    vol = p_beta * 0.15
    sharpe = (expected_portfolio_return - rf) / vol if vol > 0 else 0

    st.divider()
    st.subheader(f"💰 總資產規模：${total_value/10000:,.1f} 萬")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("加權 Beta (風險)", f"{p_beta:.2f}")
    c2.metric("加權 Alpha (超額)", f"+{p_alpha:.1f}%")
    c3.metric("夏普值 (Sharpe)", f"{sharpe:.2f}")
    
    # 健康診斷
    if p_beta < 0.8 and sharpe > 0.7:
        st.balloons()
        st.success("🏆 完美的防禦型高回報組合！")
