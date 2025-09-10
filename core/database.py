"""
PPE 檢測系統資料庫操作模組
"""
import sqlite3
from typing import Optional
from models.ppe_status import PPEStatus
from config.settings import Config

class Database:
    """資料庫操作類"""
    
    @staticmethod
    def get_status() -> Optional[PPEStatus]:
        """
        從資料庫讀取PPE檢測狀態
        
        Returns:
            PPEStatus: 檢測狀態物件，如果讀取失敗返回None
        """
        try:
            conn = sqlite3.connect(Config.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT has_person, helmet, goggles, gloves, boots, suit, mask, last_updated
                FROM ppe_detection WHERE id = 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return PPEStatus(
                    has_person=result[0] or "fail",
                    helmet=result[1] or "fail",
                    goggles=result[2] or "fail",
                    gloves=result[3] or "fail",
                    boots=result[4] or "fail",
                    suit=result[5] or "fail",
                    mask=result[6] or "fail",
                    last_updated=result[7] or ""
                )
            return None
        except Exception as e:
            # 避免循環導入，使用基本的錯誤處理
            import sys
            print(f"讀取資料庫失敗: {str(e)}", file=sys.stderr)
            return None