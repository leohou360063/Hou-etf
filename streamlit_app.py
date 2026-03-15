import streamlit as st
import pandas as pd
import numpy as np

# 1. 手機版基礎設定
st.set_page_config(page_title="大戶資產導航系統", layout="centered")

# 自定義 CSS 讓手機閱讀更舒適
st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 大戶資產體檢儀表板")
st.caption("數據基準：2026/03/15 | 3,500萬級距專屬")

# 2. 核心資產數據 (已根據您的 1,104 張持股配置)
data = {
    "標的": ["00878", "00919", "00888", "00713", "00882", "0056", "00929", "00937B", "00982A", "00981A", "00896", "合庫金", "兆豐金", "元大金", "元大龍頭基金"],
    "張數": [168, 78, 82, 35, 125, 32, 78, 100, 43, 32, 15, 72, 6, 6, 15],
    "Beta": [0.81, 0.92, 0.88, 0.72, 0.95, 0.87, 0.98, 0.12, 0.95, 1.05, 0.92, 0.65, 0.62, 0.68, 1.02],
    "預估Alpha%": [1.5, 2.0, 1.2, 3.5, -0.5, 1.0, 0.5, 0.2, 5.5, 6.2, 2.5, 0.8, 1.0, 1.2, 4.8],
    "年配息預估": [2.2, 3.2, 2.0, 3.1, 1.2, 3.5, 1.8, 0.86, 1.51, 1.64, 2.8, 1.2, 1.8, 1.3, 1.4]
}

df = pd.DataFrame(data)

# 3. 核心指標計算邏輯 (智慧引擎)
total_value = (df["張數"] * 25).sum() # 假設平均市價 25 元計算權重
df["權重"] = (df["張數"] * 25) / total_value

# 加權計算組合指標
portfolio_beta = (df["Beta"] * df["權重"]).sum()
portfolio_alpha = (df["預估Alpha%"] * df["權重"]).sum()
total_div = (df["張數"] * df["年配息預估"] * 1000).sum()

# 夏普值估算 (R_f = 1.5%, 預期年化 11%, 波動 11%)
rf = 0.015
exp_return = 0.11
volatility = 0.11
sharpe_ratio = (exp_return - rf) / volatility

# 4. 頂部核心指標看板
st.subheader("📊 組合健康指標")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("貝塔值 (Beta)", f"{portfolio_beta:.2f}", help="越低代表越抗跌。建議維持在 0.8 以下。")
with c2:
    st.metric("阿法值 (Alpha)", f"+{portfolio_alpha:.1f}%", help="代表經理人幫您多賺的部分。")
with c3:
    st.metric("夏普值 (Sharpe)", f"{sharpe_ratio:.2f}", delta="優秀", help="數值高於 0.8 代表風險調整後報酬極佳。")

st.divider()

# 5. 50/25/25 投入導航
st.subheader("💰 股息再投入指令")
income = st.number_input("請輸入預計入帳金額 (TWD):", value=114000)

sc1, sc2, sc3 = st.columns(3)
sc1.success(f"**主動加碼 (Alpha)**\n\n$ {income*0.5:,.0f}")
sc2.warning(f"**債券防禦 (Beta)**\n\n$ {income*0.25:,.0f}")
sc3.info(f"**生活消費 (Enjoy)**\n\n$ {income*0.25:,.0f}")

# 6. 資產健康檢查建議
st.divider()
st.subheader("💡 智慧導航建議")
if portfolio_beta < 0.8 and sharpe_ratio > 0.8:
    st.balloons()
    st.success("✨ 目前組合處於「最適化」狀態！您的資產具備高 Alpha 與低 Beta 特性。")
else:
    st.warning("⚠️ 建議透過下個月股息增加債券(00937B)配置以壓低 Beta 值。")

# 7. 數據明細
with st.expander("查看各標的詳細指標"):
    st.dataframe(df[["標的", "張數", "Beta", "預估Alpha%"]], use_container_width=True)
