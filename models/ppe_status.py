"""
PPE 狀態資料模型
"""
from dataclasses import dataclass

@dataclass
class PPEStatus:
    """PPE 檢測狀態資料結構"""
    has_person: str = "fail"
    helmet: str = "fail"
    goggles: str = "fail"
    gloves: str = "fail"
    boots: str = "fail"
    suit: str = "fail"
    mask: str = "fail"
    last_updated: str = ""