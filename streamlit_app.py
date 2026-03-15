import streamlit as st
import pandas as pd

# 1. 頁面設定
st.set_page_config(page_title="大戶資產智慧導航", layout="centered")

st.title("💎 大戶資產動態管理系統")
st.caption("您可以直接在下方表格修改張數，或在最底端新增 ETF 標的")

# 2. 初始數據 (作為預設值)
if 'df' not in st.session_state:
    initial_data = {
        "標的": ["00878", "00919", "00888", "00713", "00937B", "00982A", "00981A", "元大龍頭基金"],
        "張數": [168.0, 78.0, 82.0, 35.0, 100.0, 43.0, 32.0, 15.0],
        "Beta": [0.81, 0.92, 0.88, 0.72, 0.12, 0.95, 1.05, 1.02],
        "預估Alpha%": [1.5, 2.0, 1.2, 3.5, 0.2, 5.5, 6.2, 4.8],
        "年配息(元)": [2.2, 3.2, 2.0, 3.1, 0.86, 1.51, 1.64, 1.4]
    }
    st.session_state.df = pd.DataFrame(initial_data)

# 3. 【核心功能】動態編輯表格
st.subheader("📝 持股清單即時修正")
edited_df = st.data_editor(
    st.session_state.df, 
    num_rows="dynamic", # 允許新增/刪除行
    use_container_width=True,
    key="portfolio_editor"
)

# 更新數據狀態
st.session_state.df = edited_df

# 4. 智慧計算引擎
total_value_factor = (edited_df["張數"] * 25).sum() # 權重計算基數
weights = (edited_df["張數"] * 25) / total_value_factor

portfolio_beta = (edited_df["Beta"] * weights).sum()
portfolio_alpha = (edited_df["預估Alpha%"] * weights).sum()
total_dividend = (edited_df["張數"] * edited_df["年配息(元)"] * 1000).sum()

# 5. 儀表板顯示
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("加權 Beta", f"{portfolio_beta:.2f}")
c2.metric("平均 Alpha", f"+{portfolio_alpha:.1f}%")
c3.metric("預估年息", f"${total_dividend/10000:.1f}萬")

# 6. 50/25/25 投入計算器
st.divider()
st.subheader("💰 股息分流策略")
income = st.number_input("輸入本次入帳股息 (TWD):", value=100000)
col1, col2, col3 = st.columns(3)
col1.success(f"**再投入**\n${income*0.5:,.0f}")
col2.warning(f"**避險**\n${income*0.25:,.0f}")
col3.info(f"**生活**\n${income*0.25:,.0f}")

st.info("💡 提示：在手機上長按表格內容即可進行修改。若要新增標的，請點擊表格最下方的 '+' 號。")
