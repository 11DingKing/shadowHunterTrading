"""
Shadow-Hunter v10.4 算法探针模块
实现 9 种针对伪随机的数学探针
"""

import random
import time
from collections import Counter
from typing import List, Dict, Optional


class AlgorithmLab:
    """算法实验室 - 包含9种探针算法"""
    
    @staticmethod
    def _safe_random() -> int:
        """安全随机返回 1-8"""
        return random.randint(1, 8)
    
    @staticmethod
    def algo_trend(history: List[int]) -> int:
        """
        算法1: 趋势追踪 (追热)
        统计最近50期出现最多的数字
        """
        if len(history) < 5:
            return AlgorithmLab._safe_random()
        
        recent = history[:50]
        counter = Counter(recent)
        most_common = counter.most_common(1)
        return most_common[0][0] if most_common else AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_gap(history: List[int]) -> int:
        """
        算法2: 冷门补位 (补冷)
        统计最近80期出现最少的数字
        """
        if len(history) < 10:
            return AlgorithmLab._safe_random()
        
        recent = history[:80]
        counter = Counter(recent)
        
        # 找出所有1-8中出现最少的
        min_count = float('inf')
        coldest = []
        for num in range(1, 9):
            count = counter.get(num, 0)
            if count < min_count:
                min_count = count
                coldest = [num]
            elif count == min_count:
                coldest.append(num)
        
        return random.choice(coldest) if coldest else AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_zscore(history: List[int]) -> int:
        """
        算法3: Z-Score 简化版
        返回最近20期出现频率最高的
        """
        if len(history) < 5:
            return AlgorithmLab._safe_random()
        
        recent = history[:20]
        counter = Counter(recent)
        most_common = counter.most_common(1)
        return most_common[0][0] if most_common else AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_mirror(history: List[int]) -> int:
        """
        算法4: 镜像跟随
        返回上一期结果
        """
        if len(history) < 1:
            return AlgorithmLab._safe_random()
        return history[0]
    
    @staticmethod
    def algo_anti_double(history: List[int]) -> int:
        """
        算法5: 反连击
        如果上一期和上上期相同，返回该数字
        """
        if len(history) < 2:
            return AlgorithmLab._safe_random()
        
        if history[0] == history[1]:
            return history[0]
        return AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_time(history: List[int]) -> int:
        """
        算法6: 时间因子
        返回 (当前时间戳秒数 % 8) + 1
        """
        return (int(time.time()) % 8) + 1
    
    @staticmethod
    def algo_entropy(history: List[int]) -> int:
        """
        算法7: 熵随机
        纯随机返回 1-8
        """
        return AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_markov(history: List[int]) -> int:
        """
        算法8: 马尔可夫 (简化)
        基于转移概率的随机 (当前简化为随机)
        """
        return AlgorithmLab._safe_random()
    
    @staticmethod
    def algo_shadow(history: List[int]) -> int:
        """
        算法9: 影子探针
        随机返回 1-8
        """
        return AlgorithmLab._safe_random()
    
    @classmethod
    def calculate_all(cls, history: List[int]) -> Dict[int, int]:
        """
        调用所有算法，返回结果字典
        
        Args:
            history: 历史开奖列表 (最新在前)
            
        Returns:
            {算法ID: 建议躲避位置}
        """
        algorithms = [
            (1, cls.algo_trend),
            (2, cls.algo_gap),
            (3, cls.algo_zscore),
            (4, cls.algo_mirror),
            (5, cls.algo_anti_double),
            (6, cls.algo_time),
            (7, cls.algo_entropy),
            (8, cls.algo_markov),
            (9, cls.algo_shadow),
        ]
        
        results = {}
        for algo_id, algo_func in algorithms:
            try:
                result = algo_func(history)
                # 确保结果在有效范围内
                if not (1 <= result <= 8):
                    result = cls._safe_random()
                results[algo_id] = result
            except Exception:
                results[algo_id] = cls._safe_random()
        
        return results


# 便捷函数
def run_all_algorithms(history: List[int]) -> Dict[int, int]:
    """运行所有算法的便捷函数"""
    return AlgorithmLab.calculate_all(history)
