"""
Shadow-Hunter v10.4 AI 人格模块
实现三大 AI 人格及其投票机制
"""

from typing import Dict, List, Optional
from collections import Counter


class AIPersona:
    """AI 人格类"""
    
    def __init__(self, name: str, algo_ids: List[int]):
        """
        初始化 AI 人格
        
        Args:
            name: 人格名称 (Deep/Tongyi/Doubao)
            algo_ids: 负责的算法 ID 列表 (3个)
        """
        self.name = name
        self.algo_ids = algo_ids
        self.ema_score: float = 10.0  # EMA 权重分数
        self.vote_history: List[bool] = []  # 投票历史 (用于统计)
        self.total_votes: int = 0
        self.correct_votes: int = 0
    
    def get_vote(self, algo_results: Dict[int, int]) -> Optional[int]:
        """
        获取该人格的投票
        
        规则: 如果负责的3个算法中至少2个结果相同，返回该结果
        否则弃权返回 None
        
        Args:
            algo_results: {算法ID: 建议躲避位置}
            
        Returns:
            投票结果 (1-8) 或 None (弃权)
        """
        # 获取自己负责的算法结果
        my_results = [algo_results.get(aid) for aid in self.algo_ids if aid in algo_results]
        
        if len(my_results) < 2:
            return None
        
        # 统计结果
        counter = Counter(my_results)
        most_common = counter.most_common(1)
        
        if most_common and most_common[0][1] >= 2:
            # 至少有2个算法结果一致
            return most_common[0][0]
        
        return None  # 弃权
    
    def update_score(self, is_win: bool) -> None:
        """
        更新 EMA 权重分数
        
        公式: new_score = old_score * 0.8 + (1 if win else -1) * 0.2
        
        Args:
            is_win: 本轮是否胜利
        """
        adjustment = 1.0 if is_win else -1.0
        self.ema_score = self.ema_score * 0.8 + adjustment * 0.2
        
        # 限制分数范围
        self.ema_score = max(0.1, min(20.0, self.ema_score))
        
        # 更新统计
        self.vote_history.append(is_win)
        self.total_votes += 1
        if is_win:
            self.correct_votes += 1
    
    @property
    def win_rate(self) -> float:
        """计算胜率"""
        if self.total_votes == 0:
            return 0.0
        return self.correct_votes / self.total_votes
    
    @property
    def confidence(self) -> float:
        """计算置信度 (基于 EMA 分数归一化)"""
        # 将 EMA 分数映射到 0-100%
        return min(100.0, max(0.0, (self.ema_score / 15.0) * 100))
    
    def reset(self) -> None:
        """重置状态"""
        self.ema_score = 10.0
        self.vote_history = []
        self.total_votes = 0
        self.correct_votes = 0
    
    def __repr__(self) -> str:
        return f"AIPersona({self.name}, EMA={self.ema_score:.2f}, WinRate={self.win_rate:.1%})"


def create_default_personas() -> Dict[str, AIPersona]:
    """创建默认的三个 AI 人格"""
    return {
        "Deep": AIPersona("Deep", [1, 2, 3]),
        "Tongyi": AIPersona("Tongyi", [4, 5, 6]),
        "Doubao": AIPersona("Doubao", [7, 8, 9]),
    }
