"""
Shadow-Hunter v10.4 主程序入口
整合所有模块，实现模拟游戏循环
"""

import sys
import random
import time
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

from config import Config, Status, YAO_MAP, DEFAULT_CONFIG
from core.algorithms import AlgorithmLab
from core.agents import AIPersona, create_default_personas
from core.arbiter import Arbiter
from core.strategy import StrategyEngine
from ui.main_window import MainWindow


class SimulationThread(QThread):
    """模拟游戏循环线程"""
    
    # 信号定义
    update_signal = pyqtSignal(dict)  # UI 更新信号
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.running = True
        
        # 初始化组件
        self.engine = StrategyEngine(config)
        self.arbiter = Arbiter()
        self.personas = create_default_personas()
        self.history: list = []  # 历史开奖记录
    
    def run(self):
        """主循环"""
        print("\n" + "=" * 50)
        print("  Shadow-Hunter v10.4 模拟循环启动")
        print("=" * 50 + "\n")
        
        round_num = 0
        
        while self.running:
            round_num += 1
            
            # ===== 反侦察延迟 =====
            delay = random.uniform(1.5, 4.0)
            time.sleep(delay)
            
            if not self.running:
                break
            
            # ===== 模拟获取数据: 神仙猿 (开奖结果) =====
            current_ape = random.randint(1, 8)
            
            # ===== 算法计算 =====
            algo_results = AlgorithmLab.calculate_all(self.history)
            
            # ===== AI 投票 =====
            for persona in self.personas.values():
                persona.get_vote(algo_results)
            
            # ===== 仲裁决策 =====
            final_prediction = self.arbiter.decide(self.personas, algo_results)
            
            # ===== 策略决策 =====
            decision = self.engine.get_decision()
            
            # ===== 结算 =====
            # 判断是否躲避成功 (预测位置 != 神仙猿位置)
            is_win = (final_prediction is not None and final_prediction != current_ape)
            
            # 更新策略引擎
            message, profit = self.engine.update_result(is_win, decision.amount)
            
            # 更新 AI 权重 (只有在有有效预测时)
            if final_prediction is not None:
                for persona in self.personas.values():
                    if persona.get_vote(algo_results) == final_prediction:
                        persona.update_score(is_win)
            
            # 记录历史
            self.history.insert(0, current_ape)
            if len(self.history) > 200:
                self.history = self.history[:200]
            
            # ===== 构建 UI 更新数据 =====
            stats = self.engine.get_stats()
            
            ui_data = {
                'status': stats['status'],
                'balance': stats['balance'],
                'ai_votes': {
                    name: {
                        'vote': persona.get_vote(algo_results),
                        'confidence': persona.confidence,
                        'ema': persona.ema_score
                    }
                    for name, persona in self.personas.items()
                },
                'arbiter_decision': final_prediction,
                'avoid': final_prediction,
                'killer': current_ape,
                'message': f"[第{round_num}轮] {decision.message} | {message}",
                'record': {
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'ape': current_ape,
                    'avoid': final_prediction,
                    'is_win': is_win,
                    'status': stats['status'],
                    'profit': profit
                },
                'stats': {
                    'total': stats['total_rounds'],
                    'wins': stats['wins'],
                    'losses': stats['losses']
                }
            }
            
            # 发送更新信号
            self.update_signal.emit(ui_data)
            
            # 日志输出
            result_icon = "✅" if is_win else "❌"
            ape_name = YAO_MAP.get(current_ape, "未知")
            avoid_name = YAO_MAP.get(final_prediction, "无") if final_prediction else "弃权"
            print(f"[{round_num:03d}] {result_icon} 神仙猿:{current_ape}{ape_name} | "
                  f"躲避:{avoid_name} | {decision.status} | 余额:{stats['balance']:,}")
    
    def stop(self):
        """停止循环"""
        self.running = False
    
    def reset(self, config: Config):
        """重置引擎"""
        self.config = config
        self.engine = StrategyEngine(config)
        self.arbiter.reset()
        for persona in self.personas.values():
            persona.reset()
        self.history = []


class Application:
    """应用程序主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.simulation: Optional[SimulationThread] = None
    
    def start_simulation(self):
        """启动模拟"""
        if self.simulation is not None:
            self.simulation.stop()
            self.simulation.wait()
        
        self.simulation = SimulationThread(self.window.config)
        self.simulation.update_signal.connect(self.window.update_ui)
        self.simulation.start()
    
    def stop_simulation(self):
        """停止模拟"""
        if self.simulation is not None:
            self.simulation.stop()
            self.simulation.wait()
    
    def run(self):
        """运行应用"""
        print("\n" + "=" * 50)
        print("  Shadow-Hunter v10.4")
        print("  地狱板块 - 方块兽博弈辅助系统")
        print("=" * 50)
        print("\n  Startup Success!")
        print("  Access URL: http://localhost:8081")
        print("\n" + "=" * 50 + "\n")
        
        self.window.show()
        
        # 延迟启动模拟线程
        QTimer.singleShot(1000, self.start_simulation)
        
        # 连接配置变更
        self.window.config_page.configChanged.connect(self.on_config_changed)
        
        # 运行事件循环
        exit_code = self.app.exec()
        
        # 清理
        self.stop_simulation()
        
        return exit_code
    
    def on_config_changed(self, config: Config):
        """配置变更处理"""
        if self.simulation is not None:
            self.simulation.reset(config)


def main():
    """主入口"""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
