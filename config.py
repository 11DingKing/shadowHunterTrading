"""
Shadow-Hunter v10.4 配置模块
定义游戏常量、妖怪映射和策略参数
"""

from dataclasses import dataclass, field
from typing import List

# ==================== 游戏常量 ====================

# 八妖位置映射
YAO_MAP = {
    1: "熊妖",
    2: "牛妖",
    3: "狐妖",
    4: "蛇妖",
    5: "蛛妖",
    6: "兔妖",
    7: "象妖",
    8: "猴妖",
}

# 八妖图标映射
YAO_ICONS = {
    1: "🐻",
    2: "🐂",
    3: "🦊",
    4: "🐍",
    5: "🕷️",
    6: "🐰",
    7: "🐘",
    8: "🐵",
}

# 基础概率 (1/8)
BASE_PROB = 0.125

# 状态常量
class Status:
    WARMUP = "WARMUP"   # 预热观测
    REAL = "REAL"       # 实盘投注
    SHADOW = "SHADOW"   # 影子防御


# ==================== 策略配置 ====================

@dataclass
class Config:
    """策略参数配置类"""
    
    # 投注序列 (单位: 矿石)
    sequence: List[int] = field(default_factory=lambda: [100, 600, 1300, 2700])
    
    # 滚雪球轮次上限
    snow_limit: int = 2
    
    # 影子模式解锁所需连胜数
    shadow_unlock_wins: int = 3
    
    # 影子模式解锁胜率阈值
    shadow_unlock_rate: float = 0.8
    
    # 是否开启软着陆 (解锁后首注减半)
    soft_landing: bool = True
    
    # 预热轮次
    warmup_rounds: int = 10
    
    # 初始余额
    initial_balance: int = 10000


# ==================== AI 人格配置 ====================

# 每个AI人格负责的算法ID
AI_ALGO_ASSIGNMENT = {
    "Deep": [1, 2, 3],      # 趋势类算法
    "Tongyi": [4, 5, 6],    # 模式类算法
    "Doubao": [7, 8, 9],    # 随机类算法
}

# 算法名称映射
ALGO_NAMES = {
    1: "趋势追踪",
    2: "冷门补位",
    3: "Z-Score",
    4: "镜像跟随",
    5: "反连击",
    6: "时间因子",
    7: "熵随机",
    8: "马尔可夫",
    9: "影子探针",
}


# ==================== 默认实例 ====================

# 全局默认配置
DEFAULT_CONFIG = Config()
