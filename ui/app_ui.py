"""
PPE 檢測系統 UI 主控制器
"""
import streamlit as st
from ui.components.header import render_header
from ui.components.person_status import render_person_status
from ui.components.stages import render_stages
from ui.components.control_panel import render_control_panel
from ui.components.debug_info import render_debug_info

class AppUI:
    """應用程式UI主控制器"""
    
    @staticmethod
    def render():
        """渲染完整的應用程式介面"""
        # 渲染各個UI組件
        render_header()
        render_person_status()
        render_stages()
        render_control_panel()
        render_debug_info()
        
        # 頁腳
        st.markdown("---")
        st.markdown("*PPE自動檢測系統 v6.0 - 模組化架構 | 增強版日誌系統*")