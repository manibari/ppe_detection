"""
PPE 檢測系統控制面板組件
"""
import streamlit as st
import os
from datetime import datetime
from models.stage_config import STAGE_NAMES
from core.database import Database
from core.detector import PPEDetector

def render_control_panel():
    """渲染控制面板"""
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎛️ 控制面板")
        
        # 當前階段信息
        current_stage_name = STAGE_NAMES[st.session_state.current_stage]
        st.info(f"當前階段: {current_stage_name}")
        
        # 手動控制
        st.markdown("### 🔧 手動控制")
        
        col_manual1, col_manual2 = st.columns(2)
        
        with col_manual1:
            if st.button("✅ 手動通過", use_container_width=True):
                if st.session_state.current_stage in [1, 2, 3]:
                    PPEDetector.manual_pass_stage()
                    st.rerun()
                else:
                    st.warning("當前無可通過的階段")
        
        with col_manual2:
            if st.button("🔄 重置系統", use_container_width=True):
                PPEDetector.reset_system("手動重置")
                st.rerun()
        
        # 系統信息
        st.markdown("### 📊 系統信息")
        status = Database.get_status()
        if status and status.last_updated:
            st.write(f"📅 最後更新: {status.last_updated}")
        
        # 計時器
        if st.session_state.stage_start_time:
            elapsed = (datetime.now() - st.session_state.stage_start_time).total_seconds()
            st.write(f"⏱️ 檢測時間: {elapsed:.0f}秒")
    
    with col2:
        # 加入標籤頁
        tab1, tab2 = st.tabs(["即時日誌", "歷史日誌"])
        
        with tab1:
            # 原有的即時日誌顯示
            st.subheader("📝 系統日誌")
            logs = st.session_state.get('logs', [])
            st.text_area("即時日誌", '\n'.join(logs[-30:]), height=300)
        
        with tab2:
            # 新增歷史日誌檢視
            st.subheader("📚 歷史日誌")
            
            log_files = []
            if os.path.exists("logs"):
                log_files = [f for f in os.listdir("logs") if f.endswith('.log')]
                log_files.sort(reverse=True)
            
            if log_files:
                selected_file = st.selectbox("選擇日誌檔案", log_files)
                
                if st.button("載入歷史日誌"):
                    try:
                        with open(f"logs/{selected_file}", 'r', encoding='utf-8') as f:
                            content = f.readlines()[-100:]  # 最後100行
                            st.text_area("歷史日誌", ''.join(content), height=300)
                    except Exception as e:
                        st.error(f"讀取失敗: {e}")
            else:
                st.info("暫無歷史日誌檔案")