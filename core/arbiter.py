"""
Shadow-Hunter v10.4 仲裁系统
实现 EMA 加权投票仲裁
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from .agents import AIPersona


class Arbiter:
    """仲裁者 - 综合所有 AI 人格的投票做出最终决策"""
    
    def __init__(self):
        self.last_decision: Optional[int] = None
        self.last_votes: Dict[str, Optional[int]] = {}
        self.decision_history: List[Tuple[int, bool]] = []  # (决策, 是否正确)
    
    def decide(
        self, 
        personas: Dict[str, AIPersona], 
        algo_results: Dict[int, int]
    ) -> Optional[int]:
        """
        做出最终决策
        
        逻辑:
        1. 收集所有 AI 人格的有效投票
        2. 按 EMA 权重加权统计每个位置的得分
        3. 返回得分最高的位置
        4. 如果全部弃权，返回 None
        
        Args:
            personas: AI 人格字典
            algo_results: 算法结果字典
            
        Returns:
            最终建议躲避的位置 (1-8) 或 None
        """
        # 收集投票
        votes: Dict[str, Optional[int]] = {}
        position_scores: Dict[int, float] = defaultdict(float)
        
        for name, persona in personas.items():
            vote = persona.get_vote(algo_results)
            votes[name] = vote
            
            if vote is not None:
                # 加权累加
                position_scores[vote] += persona.ema_score
        
        self.last_votes = votes
        
        # 如果没有有效投票
        if not position_scores:
            self.last_decision = None
            return None
        
        # 找出得分最高的位置
        best_position = max(position_scores.keys(), key=lambda p: position_scores[p])
        self.last_decision = best_position
        
        return best_position
    
    def get_vote_summary(self) -> Dict[str, str]:
        """
        获取投票摘要
        
        Returns:
            {人格名: "位置X" 或 "弃权"}
        """
        summary = {}
        for name, vote in self.last_votes.items():
            if vote is None:
                summary[name] = "弃权"
            else:
                summary[name] = f"位置{vote}"
        return summary
    
    def record_result(self, is_correct: bool) -> None:
        """记录决策结果"""
        if self.last_decision is not None:
            self.decision_history.append((self.last_decision, is_correct))
    
    @property
    def accuracy(self) -> float:
        """计算仲裁准确率"""
        if not self.decision_history:
            return 0.0
        correct = sum(1 for _, is_correct in self.decision_history if is_correct)
        return correct / len(self.decision_history)
    
    def reset(self) -> None:
        """重置状态"""
        self.last_decision = None
        self.last_votes = {}
        self.decision_history = []
