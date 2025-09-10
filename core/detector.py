"""
PPE 檢測邏輯模組
"""
import streamlit as st
from datetime import datetime
from models.ppe_status import PPEStatus
from config.settings import Config
from core.database import Database
from core.logger import Logger

class PPEDetector:
    """PPE檢測邏輯類"""
    
    @staticmethod
    def check_stage_completion(stage: int, status: PPEStatus) -> bool:
        """
        檢查指定階段是否完成
        
        Args:
            stage: 階段編號 (1, 2, 3)
            status: PPE狀態物件
            
        Returns:
            bool: 階段是否完成
        """
        if stage == 1:
            return status.helmet == "pass" and status.goggles == "pass"
        elif stage == 2:
            return status.gloves == "pass" and status.boots == "pass"
        elif stage == 3:
            return status.suit == "pass" and status.mask == "pass"
        return False
    
    @staticmethod
    def check_stage_failure(stage: int, status: PPEStatus) -> bool:
        """
        檢查指定階段是否失敗
        
        Args:
            stage: 階段編號 (1, 2, 3)
            status: PPE狀態物件
            
        Returns:
            bool: 階段是否失敗
        """
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
        """
        重置系統到初始狀態
        
        Args:
            reason: 重置原因
        """
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