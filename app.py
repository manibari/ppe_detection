"""
PPE 個人防護設備檢測系統
模組化架構重構版本

主要功能：
- 三階段PPE檢測流程
- 自動狀態機控制
- 即時和歷史日誌系統
- 手動控制功能
"""
import streamlit as st
import time
from core.session_manager import init_session_state
from core.logger import Logger
from core.database import Database
from core.detector import PPEDetector
from ui.app_ui import AppUI
from config.settings import Config

# 設定頁面
st.set_page_config(
    page_title="PPE檢測系統",
    page_icon="🦺",
    layout="wide"
)

def main():
    """主程式入口點"""
    # 初始化會話狀態
    init_session_state()
    
    # 初始化日誌系統
    logger = Logger()
    
    # 檢查資料庫連接
    try:
        status = Database.get_status()
        if status is None:
            st.error("❌ 無法連接到資料庫，請確認 ppe_detection.db 存在")
            st.info("💡 請先執行 ppe_simulator.py 創建資料庫")
            Logger.add_log("資料庫連接失敗", "ERROR")
            return
    except Exception as e:
        st.error(f"❌ 資料庫錯誤: {str(e)}")
        Logger.add_log(f"資料庫錯誤: {str(e)}", "ERROR")
        return
    
    # 系統啟動日誌（只在第一次運行時記錄）
    if not st.session_state.system_started:
        Logger.add_log("PPE檢測系統啟動（模組化架構）", "INFO")
        st.session_state.system_started = True
    
    # 更新檢測狀態
    PPEDetector.update_detection_state()
    
    # 渲染UI
    AppUI.render()
    
    # 自動刷新
    time.sleep(Config.REFRESH_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    main()