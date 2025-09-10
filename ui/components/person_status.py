"""
PPE 檢測系統人員狀態組件
"""
import streamlit as st
from datetime import datetime
from config.settings import Config
from core.database import Database

def render_person_status():
    """渲染人員狀態區域"""
    status = Database.get_status()
    if status:
        person_status = "🟢 檢測到人員" if status.has_person == "pass" else "🔴 無人員"
        st.markdown(f"### 👤 人員狀態: {person_status}")
        
        if st.session_state.last_person_seen:
            time_since = (datetime.now() - st.session_state.last_person_seen).total_seconds()
            if status.has_person == "fail" and time_since < Config.PERSON_TIMEOUT:
                remaining = Config.PERSON_TIMEOUT - time_since
                st.warning(f"⏰ 人員離開 {time_since:.0f}秒，{remaining:.0f}秒後重置系統")
    
    st.markdown("---")