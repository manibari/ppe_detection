"""
PPE 檢測階段配置資料
"""

STAGE_CONFIG = [
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

STAGE_NAMES = ["等待人員", "頭部防護", "手足防護", "身體防護", "檢測完成"]