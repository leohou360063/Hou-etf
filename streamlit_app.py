import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="大戶資產雲端導航", layout="centered")
st.title("💎 全自動數據同步儀表板")

# 1. 初始化數據 (確保有基本的標的資料)
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00713", "00937B", "00982A", "00981A", "00929", "00888"],
        "張數": [168.0, 78.0, 35.0, 100.0, 43.0, 32.0, 78.0, 83.0],
        "Beta": [0.81, 0.92, 0.72, 0.12, 0.95, 1.05, 0.98, 0.88],
        "預估Alpha%": [1.5, 2.0, 3.5, 0.2, 5.5, 6.2, 0.5, 1.2],
        "現價": [0.0] * 8
    }
    st.session_state.df = pd.DataFrame(initial_data)

# 2. 核心功能：強化版一鍵同步
if st.button("🚀 一鍵同步最新市場數據"):
    with st.spinner('正在連線交易所 (嘗試多重後綴)...'):
        for index, row in st.session_state.df.iterrows():
            symbol = str(row["標的"]).strip()
            # 智慧嘗試清單：原名 -> 上市後綴 -> 上櫃後綴
            trial_list = [symbol, f"{symbol}.TW", f"{symbol}.TWO"]
            
            success = False
            for t in trial_list:
                try:
                    tk = yf.Ticker(t)
                    hist = tk.history(period="1d")
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                        st.session_state.df.at[index, "現價"] = round(price, 2)
                        
                        # 嘗試同步 Beta
                        market_beta = tk.info.get('beta')
                        if market_beta:
                            st.session_state.df.at[index, "Beta"] = round(market_beta, 2)
                        
                        success = True
                        break # 抓到就跳出試錯迴圈
                except:
                    continue
            
            if not success:
                st.toast(f"無法同步 {symbol}，建議手動輸入現價")

    st.success("同步嘗試完成！")
    st.rerun()

# 3. 互動編輯表格 (修正 None 顯示問題)
st.subheader("📝 資產配置清單")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

# 4. 指標計算邏輯 (確保即便現價為 0 也不報錯)
if not edited_df.empty:
    # 填補現價為 0 的部分避免計算錯誤，若為 0 則以 1 代替計算市值比重
    valid_prices = edited_df["現價"].apply(lambda x: x if x > 0 else 1.0)
    edited_df["市值"] = edited_df["張數"] * 1000 * valid_prices
    total_value = edited_df["市值"].sum()
    weights = edited_df["市值"] / total_value
    
    p_beta = (edited_df["Beta"] * weights).sum()
    p_alpha = (edited_df["預估Alpha%"] * weights).sum()
    
    # 夏普值模型
    rf, market_ret = 0.015, 0.06
    vol = p_beta * 0.15
    sharpe = (((rf + p_beta*(market_ret-rf) + p_alpha/100)) - rf) / vol if vol > 0 else 0

    st.divider()
    if edited_df["現價"].sum() > 0:
        st.subheader(f"💰 總資產規模：${total_value/10000:,.1f} 萬")
    else:
        st.warning("⚠️ 請點擊上方同步按鈕以載入最新行情與資產估值")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("加權 Beta", f"{p_beta:.2f}")
    c2.metric("加權 Alpha", f"+{p_alpha:.1f}%")
    c3.metric("夏普值 (Sharpe)", f"{sharpe:.2f}")
