"""
PPE 檢測系統標題組件
"""
import streamlit as st
from datetime import datetime
from config.settings import Config

def render_header():
    """渲染頁面標題"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🦺 PPE 個人防護設備檢測系統")
    
    with col2:
        if st.session_state.current_stage == 4:
            st.success("✅ 已完成檢查")
            if st.session_state.completion_time:
                remaining = Config.COMPLETION_TIMEOUT - (datetime.now() - st.session_state.completion_time).total_seconds()
                if remaining > 0:
                    st.write(f"⏰ {remaining:.0f}秒後重置")
    
    st.markdown("---")