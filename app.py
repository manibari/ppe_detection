import streamlit as st
import sqlite3
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import logging
import os

# 設定頁面
st.set_page_config(
    page_title="PPE檢測系統",
    page_icon="🦺",
    layout="wide"
)

# 系統配置
class Config:
    DB_PATH = "ppe_detection.db"
    REFRESH_INTERVAL = 5.0
    PERSON_TIMEOUT = 30  # 人員離開30秒後重置
    COMPLETION_TIMEOUT = 30  # 完成檢查30秒後重置

# 資料結構
@dataclass
class PPEStatus:
    has_person: str = "fail"
    helmet: str = "fail"
    goggles: str = "fail"
    gloves: str = "fail"
    boots: str = "fail"
    suit: str = "fail"
    mask: str = "fail"
    last_updated: str = ""

# 初始化 session state
def init_session_state():
    defaults = {
        'current_stage': 0,  # 0=等待, 1=第一階段, 2=第二階段, 3=第三階段, 4=完成
        'stage_start_time': None,
        'last_person_seen': None,
        'completion_time': None,
        'logs': [],
        'manual_override': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 資料庫操作
class Database:
    @staticmethod
    def get_status() -> Optional[PPEStatus]:
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
            Logger.add_log(f"讀取資料庫失敗: {str(e)}", "ERROR")
            return None

# 日誌系統
class Logger:
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
        """添加日誌 - 同時存檔和記憶體"""
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
            

# PPE檢測邏輯
class PPEDetector:
    @staticmethod
    def check_stage_completion(stage: int, status: PPEStatus) -> bool:
        """檢查指定階段是否完成"""
        if stage == 1:
            return status.helmet == "pass" and status.goggles == "pass"
        elif stage == 2:
            return status.gloves == "pass" and status.boots == "pass"
        elif stage == 3:
            return status.suit == "pass" and status.mask == "pass"
        return False
    
    @staticmethod
    def check_stage_failure(stage: int, status: PPEStatus) -> bool:
        """檢查指定階段是否失敗"""
        if stage == 1:
            return status.helmet == "fail" or status.goggles == "fail"
        elif stage == 2:
            return status.gloves == "fail" or status.boots == "fail"
        elif stage == 3:
            return status.suit == "fail" or status.mask == "fail"
        return False
    
    @staticmethod
    def update_detection_state():
        """更新檢測狀態的主邏輯"""
        status = Database.get_status()
        if not status:
            return
        
        current_time = datetime.now()
        
        # 檢查是否有人
        if status.has_person == "pass":
            st.session_state.last_person_seen = current_time
        
        # 檢查人員離開超時
        if (st.session_state.last_person_seen and 
            (current_time - st.session_state.last_person_seen).total_seconds() > Config.PERSON_TIMEOUT):
            PPEDetector.reset_system("人員離開超過30秒，系統重置")
            return
        
        # 檢查完成超時
        if (st.session_state.completion_time and 
            (current_time - st.session_state.completion_time).total_seconds() > Config.COMPLETION_TIMEOUT):
            PPEDetector.reset_system("完成檢查30秒後，系統重置")
            return
        
        # 狀態機邏輯
        if st.session_state.current_stage == 0:  # 等待階段
            if status.has_person == "pass":
                st.session_state.current_stage = 1
                st.session_state.stage_start_time = current_time
                Logger.add_log("檢測到人員，進入第一階段", "INFO")
        
        elif st.session_state.current_stage == 1:  # 第一階段
            if PPEDetector.check_stage_completion(1, status):
                st.session_state.current_stage = 2
                Logger.add_log("第一階段通過 - 安全帽和護目鏡", "SUCCESS")
            elif PPEDetector.check_stage_failure(1, status):
                Logger.add_log("第一階段失敗 - 請檢查安全帽和護目鏡", "ERROR")
        
        elif st.session_state.current_stage == 2:  # 第二階段
            if PPEDetector.check_stage_completion(2, status):
                st.session_state.current_stage = 3
                Logger.add_log("第二階段通過 - 手套和安全靴", "SUCCESS")
            elif PPEDetector.check_stage_failure(2, status):
                Logger.add_log("第二階段失敗 - 請檢查手套和安全靴", "ERROR")
        
        elif st.session_state.current_stage == 3:  # 第三階段
            if PPEDetector.check_stage_completion(3, status):
                st.session_state.current_stage = 4
                st.session_state.completion_time = current_time
                Logger.add_log("第三階段通過 - 防護衣和防護面罩", "SUCCESS")
                Logger.add_log("🎉 所有PPE檢測完成！可以進入工作區域", "SUCCESS")
            elif PPEDetector.check_stage_failure(3, status):
                Logger.add_log("第三階段失敗 - 請檢查防護衣和防護面罩", "ERROR")
    
    @staticmethod
    def reset_system(reason: str = "手動重置"):
        """重置系統到初始狀態"""
        st.session_state.current_stage = 0
        st.session_state.stage_start_time = None
        st.session_state.last_person_seen = None
        st.session_state.completion_time = None
        Logger.add_log(f"系統重置: {reason}", "INFO")
    
    @staticmethod
    def manual_pass_stage():
        """手動通過當前階段"""
        if st.session_state.current_stage in [1, 2, 3]:
            st.session_state.current_stage += 1
            if st.session_state.current_stage == 4:
                st.session_state.completion_time = datetime.now()
                Logger.add_log("🎉 手動通過所有檢測！", "SUCCESS")
            else:
                Logger.add_log(f"手動通過階段{st.session_state.current_stage-1}", "INFO")

# UI組件
class UI:
    @staticmethod
    def render_header():
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
    
    

    @staticmethod
    def render_person_status():
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
    
    @staticmethod
    def render_stages():
        st.subheader("🔍 PPE檢測階段")
        
        # 獲取當前狀態
        status = Database.get_status()
        
        # 定義階段信息
        stages = [
            {
                "id": 1,
                "name": "頭部防護",
                "items": [("👷‍♂️ 安全帽", "helmet"), ("🥽 護目鏡", "goggles")]
            },
            {
                "id": 2, 
                "name": "手足防護",
                "items": [("🧤 手套", "gloves"), ("👢 安全靴", "boots")]
            },
            {
                "id": 3,
                "name": "身體防護", 
                "items": [("🦺 防護衣", "suit"), ("😷 防護面罩", "mask")]
            }
        ]
        
        cols = st.columns(3)
        
        for i, stage in enumerate(stages):
            with cols[i]:
                # 決定階段狀態
                stage_active = st.session_state.current_stage == stage["id"]
                stage_completed = st.session_state.current_stage > stage["id"]
                
                # 容器樣式
                #if stage_completed:
                #    container_style = "border: 3px solid #28a745; background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);"
                #elif stage_active:
                #    container_style = "border: 3px solid #ffc107; background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);"
                #else:
                #    container_style = "border: 3px solid #ddd; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);"
                
                #st.markdown(f'<div style="{container_style} border-radius: 15px; padding: 20px; margin: 10px; text-align: center; min-height: 300px;">', unsafe_allow_html=True)
                
                # 階段標題
                st.markdown(f"### 階段 {stage['id']}: {stage['name']}")
                
                # 狀態燈
                if stage_completed:
                    st.markdown("## 🟢")
                elif stage_active:
                    st.markdown("## 🟡")
                else:
                    st.markdown("## ⚪")
                
                # 設備檢測狀態
                for item_name, item_key in stage["items"]:
                    if status:
                        item_status = getattr(status, item_key, "fail")
                        status_icon = "✅" if item_status == "pass" else "❌"
                        st.markdown(f"**{item_name}** {status_icon}")
                    else:
                        st.markdown(f"**{item_name}** ❓")
                
                # 階段狀態文字
                if stage_completed:
                    st.success("✅ 已完成")
                elif stage_active:
                    st.warning("🟡 檢測中...")
                else:
                    st.info("⏳ 等待中")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_control_panel():
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🎛️ 控制面板")
            
            # 當前階段信息
            stage_names = ["等待人員", "頭部防護", "手足防護", "身體防護", "檢測完成"]
            current_stage_name = stage_names[st.session_state.current_stage]
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
# ...existing code...
            
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
    
    @staticmethod
    def render_debug_info():
        """調試信息（可選顯示）"""
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
            


# 主程式
def main():
    # 初始化
    init_session_state()
    
    # 初始化日誌系統
    logger = Logger()
    
    # 檢查資料庫是否存在
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
    
    # 系統啟動日誌 (只在第一次運行時記錄)
    if 'system_started' not in st.session_state:
        Logger.add_log("PPE檢測系統啟動", "INFO")
        st.session_state.system_started = True
    
    # 更新檢測狀態
    PPEDetector.update_detection_state()
    
    # 渲染UI
    UI.render_header()
    UI.render_person_status()
    UI.render_stages()
    UI.render_control_panel()
    UI.render_debug_info()
    
    # 頁腳
    st.markdown("---")
    st.markdown("*PPE自動檢測系統 v5.1 - 增強版日誌系統 | 檔案儲存 + 歷史查詢 + 管理工具*")
    
    # 自動刷新
    time.sleep(Config.REFRESH_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    main()