import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# 1. 頁面基礎設定
st.set_page_config(page_title="大戶資產雲端導航", layout="centered")
st.title("💎 資產全自動體檢儀表板")
st.caption("智慧功能：輸入代碼數字（如 00878）即可，系統會自動處理後綴")

# 2. 初始數據
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00713", "00937B", "00982A", "00981A", "00896", "2330"],
        "張數": [168.0, 78.0, 35.0, 100.0, 43.0, 32.0, 15.0, 5.0],
        "Beta": [0.81, 0.92, 0.72, 0.12, 0.95, 1.05, 0.92, 1.25],
        "預估Alpha%": [1.5, 2.0, 3.5, 0.2, 5.5, 6.2, 2.5, 4.0],
        "現價": [0.0] * 8
    }
    st.session_state.df = pd.DataFrame(initial_data)

# 💡 智慧補完邏輯函數
def auto_complete_ticker(symbol):
    symbol = str(symbol).strip().upper()
    if "." in symbol: return symbol # 如果已經有手打後綴，就不動它
    
    # 判斷是否為數字（台灣標的）
    if symbol.isdigit() or (len(symbol) > 4 and symbol[:5].isdigit()):
        # 簡易邏輯：通常 009 開頭或 B 結尾的債券多在櫃買 (.TWO)，其餘在上市 (.TW)
        # 這裡用 yfinance 嘗試抓取，若 TW 抓不到就換 TWO
        return f"{symbol}.TW"
    return symbol

# 3. 雲端同步功能
if st.button("🔄 同步最新雲端行情"):
    with st.spinner('智慧搜尋行情中...'):
        for index, row in st.session_state.df.iterrows():
            raw_symbol = row["標的"]
            # 優先嘗試 .TW，如果失敗再嘗試 .TWO
            tickers_to_try = [f"{raw_symbol}.TW", f"{raw_symbol}.TWO", raw_symbol]
            
            success = False
            for t in tickers_to_try:
                try:
                    data = yf.Ticker(t).history(period="1d")
                    if not data.empty:
                        st.session_state.df.at[index, "現價"] = round(data['Close'].iloc[-1], 2)
                        success = True
                        break
                except:
                    continue
            if not success:
                st.warning(f"⚠️ 找不到標的: {raw_symbol}")
    st.success("行情同步完成！")

# 4. 互動編輯表格
st.subheader("📝 持股配置即時修正")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

# 5. 指標計算 (與前版本相同，確保資產健康度監控)
if edited_df["現價"].sum() > 0:
    edited_df["市值"] = edited_df["張數"] * 1000 * edited_df["現價"]
    total_value = edited_df["市值"].sum()
    weights = edited_df["市值"] / total_value
    p_beta = (edited_df["Beta"] * weights).sum()
    p_alpha = (edited_df["預估Alpha%"] * weights).sum()
    
    # 夏普值計算
    rf, market_ret = 0.015, 0.05
    vol = p_beta * 0.15
    sharpe = ((market_ret + p_alpha/100) - rf) / vol if vol != 0 else 0

    st.divider()
    st.subheader(f"💰 總資產估值：${total_value/10000:,.1f} 萬")
    c1, c2, c3 = st.columns(3)
    c1.metric("加權 Beta", f"{p_beta:.2f}")
    c2.metric("預期 Alpha", f"+{p_alpha:.1f}%")
    c3.metric("夏普值", f"{sharpe:.2f}")
