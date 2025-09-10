"""
PPE 檢測系統配置模組
包含所有系統配置參數和常數
"""

class Config:
    """系統配置類"""
    DB_PATH = "ppe_detection.db"
    REFRESH_INTERVAL = 5.0
    PERSON_TIMEOUT = 30  # 人員離開30秒後重置
    COMPLETION_TIMEOUT = 30  # 完成檢查30秒後重置