"""
PPE 檢測系統會話狀態管理模組
"""
import streamlit as st

def init_session_state():
    """初始化 Streamlit session state"""
    defaults = {
        'current_stage': 0,  # 0=等待, 1=第一階段, 2=第二階段, 3=第三階段, 4=完成
        'stage_start_time': None,
        'last_person_seen': None,
        'completion_time': None,
        'logs': [],
        'manual_override': False,
        'system_started': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value