"""
PPE 檢測系統日誌模組
"""
import streamlit as st
import logging
import os
from datetime import datetime

class Logger:
    """日誌系統類 - 單例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.setup_logging()
        return cls._instance
    
    def setup_logging(self):
        """設定日誌系統"""
        # 創建logs目錄
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # 按日期命名日誌檔案
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"logs/ppe_detection_{today}.log"
        
        # 設定logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
        
        self.file_logger = logging.getLogger('PPE_Detection')
    
    @staticmethod
    def add_log(message: str, level: str = "INFO"):
        """
        添加日誌 - 同時存檔和記憶體
        
        Args:
            message: 日誌訊息
            level: 日誌等級 (INFO, SUCCESS, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # 記憶體儲存 (供Streamlit顯示)
        if 'logs' not in st.session_state:
            st.session_state.logs = []
        
        st.session_state.logs.append(log_entry)
        if len(st.session_state.logs) > 30:
            st.session_state.logs.pop(0)
        
        # 檔案儲存
        logger_instance = Logger()
        if level == "ERROR":
            logger_instance.file_logger.error(message)
        elif level == "SUCCESS":
            logger_instance.file_logger.info(f"✅ {message}")
        elif level == "WARNING":
            logger_instance.file_logger.warning(message)
        else:
            logger_instance.file_logger.info(message)