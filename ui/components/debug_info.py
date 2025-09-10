"""
PPE 檢測系統調試信息組件
"""
import streamlit as st
from core.database import Database

def render_debug_info():
    """渲染調試信息（可選顯示）"""
    with st.expander("🔍 調試信息"):
        status = Database.get_status()
        if status:
            st.json({
                "current_stage": st.session_state.current_stage,
                "has_person": status.has_person,
                "helmet": status.helmet,
                "goggles": status.goggles,
                "gloves": status.gloves,
                "boots": status.boots,
                "suit": status.suit,
                "mask": status.mask,
                "last_person_seen": str(st.session_state.last_person_seen),
                "completion_time": str(st.session_state.completion_time)
            })