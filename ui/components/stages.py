"""
PPE 檢測系統階段組件
"""
import streamlit as st
from core.database import Database
from models.stage_config import STAGE_CONFIG

def render_stages():
    """渲染PPE檢測階段"""
    st.subheader("🔍 PPE檢測階段")
    
    # 獲取當前狀態
    status = Database.get_status()
    
    cols = st.columns(3)
    
    for i, stage in enumerate(STAGE_CONFIG):
        with cols[i]:
            # 決定階段狀態
            stage_active = st.session_state.current_stage == stage["id"]
            stage_completed = st.session_state.current_stage > stage["id"]
            
            # 階段標題
            st.markdown(f"### 階段 {stage['id']}: {stage['name']}")
            
            # 狀態燈
            if stage_completed:
                st.markdown("## 🟢")
            elif stage_active:
                st.markdown("## 🟡")
            else:
                st.markdown("## ⚪")
            
            # 設備檢測狀態
            for item_name, item_key in stage["items"]:
                if status:
                    item_status = getattr(status, item_key, "fail")
                    status_icon = "✅" if item_status == "pass" else "❌"
                    st.markdown(f"**{item_name}** {status_icon}")
                else:
                    st.markdown(f"**{item_name}** ❓")
            
            # 階段狀態文字
            if stage_completed:
                st.success("✅ 已完成")
            elif stage_active:
                st.warning("🟡 檢測中...")
            else:
                st.info("⏳ 等待中")
            
            st.markdown('</div>', unsafe_allow_html=True)