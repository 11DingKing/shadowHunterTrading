"""
Shadow-Hunter v10.4 策略引擎
实现序列+滚雪球混合资金链和影子防御状态机
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

import sys
sys.path.insert(0, '..')
from config import Config, Status, DEFAULT_CONFIG


@dataclass
class Decision:
    """决策结果数据类"""
    action: str          # "BET" 或 "OBSERVE"
    amount: int          # 投注金额 (观测时为0)
    status: str          # 当前状态
    message: str         # 状态描述
    soft_landing: bool   # 是否软着陆


class StrategyEngine:
    """策略引擎 - 管理资金链和状态机"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化策略引擎
        
        Args:
            config: 策略配置，默认使用全局配置
        """
        self.config = config or DEFAULT_CONFIG
        
        # 状态变量
        self.status: str = Status.WARMUP
        self.warmup_counter: int = self.config.warmup_rounds
        
        # 资金变量
        self.seq_idx: int = 0           # 序列指针
        self.snow_step: int = 0          # 滚雪球步数
        self.current_money: int = 0      # 滚存金额
        self.balance: int = self.config.initial_balance  # 当前余额
        
        # 影子变量
        self.virt_combo: int = 0         # 虚拟连胜
        self.virt_history: list = []     # 虚拟胜负记录
        
        # 软着陆标记
        self._soft_landing: bool = False
        
        # 统计变量
        self.total_rounds: int = 0
        self.real_rounds: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.total_profit: int = 0
    
    def get_decision(self) -> Decision:
        """
        获取当前轮次的决策
        
        Returns:
            Decision 对象，包含动作、金额、状态等信息
        """
        self.total_rounds += 1
        
        # 预热模式
        if self.status == Status.WARMUP:
            self.warmup_counter -= 1
            if self.warmup_counter <= 0:
                self.status = Status.REAL
                return Decision(
                    action="OBSERVE",
                    amount=0,
                    status=Status.WARMUP,
                    message=f"预热完成，即将进入实盘",
                    soft_landing=False
                )
            return Decision(
                action="OBSERVE",
                amount=0,
                status=Status.WARMUP,
                message=f"预热观测中... 剩余 {self.warmup_counter} 轮",
                soft_landing=False
            )
        
        # 影子模式
        if self.status == Status.SHADOW:
            return Decision(
                action="OBSERVE",
                amount=0,
                status=Status.SHADOW,
                message=f"幽灵观测中... 连胜 {self.virt_combo}/{self.config.shadow_unlock_wins}",
                soft_landing=False
            )
        
        # 实盘模式
        if self.status == Status.REAL:
            self.real_rounds += 1
            
            # 计算投注金额
            if self.snow_step == 0:
                # 序列投注
                if self.seq_idx >= len(self.config.sequence):
                    self.seq_idx = len(self.config.sequence) - 1
                amount = self.config.sequence[self.seq_idx]
            else:
                # 滚雪球
                amount = self.current_money
            
            # 软着陆减半
            is_soft = self._soft_landing
            if self._soft_landing:
                amount = amount // 2
                self._soft_landing = False  # 只生效一次
            
            return Decision(
                action="BET",
                amount=amount,
                status=Status.REAL,
                message=f"实盘投注 | 序列[{self.seq_idx}] 雪球[{self.snow_step}]",
                soft_landing=is_soft
            )
        
        # 兜底
        return Decision(
            action="OBSERVE",
            amount=0,
            status=self.status,
            message="未知状态",
            soft_landing=False
        )
    
    def update_result(self, is_win: bool, bet_amount: int = 0) -> Tuple[str, int]:
        """
        更新结果，处理状态转换
        
        Args:
            is_win: 是否胜利 (躲避成功)
            bet_amount: 本轮投注金额
            
        Returns:
            (状态变化描述, 盈亏金额)
        """
        profit = 0
        message = ""
        
        # 预热模式 - 只记录不处理
        if self.status == Status.WARMUP:
            return ("预热观测", 0)
        
        # 影子模式
        if self.status == Status.SHADOW:
            self.virt_history.append(is_win)
            
            if is_win:
                self.virt_combo += 1
                
                # 检查解锁条件
                if self.virt_combo >= self.config.shadow_unlock_wins:
                    # 计算虚拟胜率
                    recent = self.virt_history[-10:] if len(self.virt_history) >= 10 else self.virt_history
                    win_rate = sum(recent) / len(recent)
                    
                    if win_rate >= self.config.shadow_unlock_rate:
                        self.status = Status.REAL
                        self._soft_landing = self.config.soft_landing
                        self.virt_combo = 0
                        self.virt_history = []
                        message = f"🔓 影子解锁! 连胜{self.config.shadow_unlock_wins}达成"
                    else:
                        message = f"虚拟连胜 {self.virt_combo}，胜率不足"
                else:
                    message = f"虚拟连胜 {self.virt_combo}/{self.config.shadow_unlock_wins}"
            else:
                self.virt_combo = 0
                message = "虚拟失败，连胜重置"
            
            return (message, 0)
        
        # 实盘模式
        if self.status == Status.REAL:
            if is_win:
                self.wins += 1
                # 计算盈利 (简化: 赔率1:1)
                profit = bet_amount
                self.balance += profit
                self.total_profit += profit
                
                # 滚雪球逻辑
                self.snow_step += 1
                self.current_money = bet_amount + profit  # 本金+盈利
                
                # 检查止盈
                if self.snow_step >= self.config.snow_limit:
                    message = f"✅ 止盈! 雪球{self.snow_step}轮完成"
                    self.seq_idx = 0
                    self.snow_step = 0
                    self.current_money = 0
                else:
                    message = f"✅ 赢! 雪球累积 {self.snow_step}/{self.config.snow_limit}"
            else:
                self.losses += 1
                profit = -bet_amount
                self.balance += profit
                self.total_profit += profit
                
                # 触发影子防御
                self.status = Status.SHADOW
                self.seq_idx = min(self.seq_idx + 1, len(self.config.sequence) - 1)
                self.snow_step = 0
                self.current_money = 0
                self.virt_combo = 0
                self.virt_history = []
                
                message = f"❌ 输! 触发影子防御，序列升至[{self.seq_idx}]"
            
            return (message, profit)
        
        return ("", 0)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "status": self.status,
            "balance": self.balance,
            "total_rounds": self.total_rounds,
            "real_rounds": self.real_rounds,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": self.wins / max(1, self.wins + self.losses),
            "total_profit": self.total_profit,
            "seq_idx": self.seq_idx,
            "snow_step": self.snow_step,
            "virt_combo": self.virt_combo,
        }
    
    def reset(self) -> None:
        """重置引擎状态"""
        self.__init__(self.config)
