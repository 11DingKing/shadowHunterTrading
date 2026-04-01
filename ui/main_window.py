"""
Shadow-Hunter v10.4 主窗口模块
PyQt6 界面实现 (v2.0 优化版 - 无 Emoji)
"""

import os
from typing import Dict, Optional, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QProgressBar,
    QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QSizePolicy,
    QHeaderView, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import YAO_MAP, Status, Config

# 使用纯文字替代 emoji (Docker 容器字体兼容)
STATUS_ICONS = {
    Status.WARMUP: "[预热]",
    Status.REAL: "[实盘]",
    Status.SHADOW: "[防御]",
}

# 八妖显示名称 (无 emoji)
YAO_DISPLAY = {
    1: "熊", 2: "牛", 3: "狐", 4: "蛇",
    5: "蛛", 6: "兔", 7: "象", 8: "猴",
}


class AICard(QFrame):
    """AI 人格卡片组件"""
    
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.setMinimumSize(220, 130)
        self.setMaximumHeight(150)
        
        # 设置卡片样式
        self.setStyleSheet("""
            AICard {
                background-color: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
            }
            AICard:hover {
                border-color: #00bcd4;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 14, 16, 14)
        
        # 标题行
        title_layout = QHBoxLayout()
        self.title_label = QLabel(f"AI {name}")
        self.title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #00bcd4;
            background: transparent;
        """)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # 建议行
        self.vote_label = QLabel("建议: 等待中...")
        self.vote_label.setStyleSheet("""
            font-size: 14px; 
            color: #e0e0e0;
            background: transparent;
            padding: 4px 0;
        """)
        self.vote_label.setWordWrap(True)
        layout.addWidget(self.vote_label)
        
        # 置信度行
        conf_layout = QHBoxLayout()
        conf_layout.setSpacing(10)
        conf_label = QLabel("置信度:")
        conf_label.setStyleSheet("font-size: 12px; color: #888888; background: transparent;")
        conf_label.setFixedWidth(50)
        conf_layout.addWidget(conf_label)
        
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(67)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setFormat("%p%")
        self.confidence_bar.setFixedHeight(14)
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: none;
                border-radius: 4px;
                text-align: center;
                font-size: 10px;
                color: #aaaaaa;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00bcd4, stop:1 #4dd0e1);
                border-radius: 4px;
            }
        """)
        conf_layout.addWidget(self.confidence_bar)
        layout.addLayout(conf_layout)
        
        # EMA 权重行
        self.ema_label = QLabel("EMA权重: 10.00")
        self.ema_label.setStyleSheet("font-size: 12px; color: #666666; background: transparent;")
        layout.addWidget(self.ema_label)
    
    def update_data(self, vote: Optional[int], confidence: float, ema: float):
        """更新卡片数据"""
        if vote is None:
            self.vote_label.setText("建议: 弃权")
            self.vote_label.setStyleSheet("""
                font-size: 14px; 
                color: #888888;
                background: transparent;
                padding: 4px 0;
            """)
        else:
            yao_name = YAO_MAP.get(vote, "未知")
            self.vote_label.setText(f"建议躲避: {vote}号 {yao_name}")
            self.vote_label.setStyleSheet("""
                font-size: 14px; 
                color: #ff5722;
                font-weight: bold;
                background: transparent;
                padding: 4px 0;
            """)
        
        self.confidence_bar.setValue(int(confidence))
        self.ema_label.setText(f"EMA权重: {ema:.2f}")


class YaoButton(QPushButton):
    """八妖按钮组件"""
    
    def __init__(self, position: int, parent=None):
        super().__init__(parent)
        self.position = position
        self.name = YAO_MAP.get(position, "未知")
        self.short_name = YAO_DISPLAY.get(position, "?")
        
        self.setFixedSize(90, 75)
        self.reset_state()
    
    def reset_state(self):
        """重置按钮状态"""
        self.setText(f"{self.position}\n{self.name}")
        self.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 2px solid #404040;
                border-radius: 10px;
                color: #cccccc;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #353535;
                border-color: #505050;
            }
        """)
    
    def set_avoid(self):
        """设置为建议躲避状态"""
        self.setText(f"X {self.position}\n{self.name}")
        self.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                border: 2px solid #ff5252;
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
    
    def set_killer(self):
        """设置为神仙猿(杀手)状态"""
        self.setText(f"* {self.position}\n{self.name}")
        self.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                border: 3px solid #ffc107;
                border-radius: 10px;
                color: #ffc107;
                font-size: 14px;
                font-weight: bold;
            }
        """)


class MonitorPage(QWidget):
    """监控台页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== 状态栏 =====
        self.status_frame = QFrame()
        self.status_frame.setObjectName("statusBar")
        self.status_frame.setFixedHeight(70)
        self.update_status_style(Status.WARMUP)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(24, 0, 24, 0)
        
        self.status_label = QLabel("[预热] 预热模式")
        self.status_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #ffc107;
            background: transparent;
        """)
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.balance_label = QLabel("余额: 10,000")
        self.balance_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #4caf50;
            background: transparent;
        """)
        status_layout.addWidget(self.balance_label)
        
        layout.addWidget(self.status_frame)
        
        # ===== AI 卡片区 =====
        ai_frame = QFrame()
        ai_frame.setStyleSheet("background: transparent;")
        ai_layout = QHBoxLayout(ai_frame)
        ai_layout.setSpacing(16)
        ai_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ai_cards: Dict[str, AICard] = {}
        for name in ["Deep", "Tongyi", "Doubao"]:
            card = AICard(name)
            self.ai_cards[name] = card
            ai_layout.addWidget(card)
        
        layout.addWidget(ai_frame)
        
        # ===== 仲裁结果 =====
        self.arbiter_frame = QFrame()
        self.arbiter_frame.setFixedHeight(60)
        self.arbiter_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 10px;
            }
        """)
        arbiter_layout = QHBoxLayout(self.arbiter_frame)
        
        self.arbiter_label = QLabel(">> 最终建议: 等待中...")
        self.arbiter_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #00bcd4;
            background: transparent;
        """)
        self.arbiter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arbiter_layout.addWidget(self.arbiter_label)
        
        layout.addWidget(self.arbiter_frame)
        
        # ===== 八妖网格 =====
        yao_frame = QFrame()
        yao_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        yao_outer_layout = QVBoxLayout(yao_frame)
        yao_outer_layout.setContentsMargins(20, 16, 20, 16)
        
        # 网格标题
        grid_title = QLabel("八妖位置")
        grid_title.setStyleSheet("""
            font-size: 14px;
            color: #888888;
            font-weight: bold;
            background: transparent;
            margin-bottom: 8px;
        """)
        grid_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        yao_outer_layout.addWidget(grid_title)
        
        # 按钮网格
        yao_grid = QWidget()
        yao_grid.setStyleSheet("background: transparent;")
        yao_layout = QGridLayout(yao_grid)
        yao_layout.setSpacing(14)
        yao_layout.setContentsMargins(0, 0, 0, 0)
        
        self.yao_buttons: Dict[int, YaoButton] = {}
        for i in range(8):
            position = i + 1
            btn = YaoButton(position)
            self.yao_buttons[position] = btn
            row = i // 4
            col = i % 4
            yao_layout.addWidget(btn, row, col, Qt.AlignmentFlag.AlignCenter)
        
        yao_outer_layout.addWidget(yao_grid)
        layout.addWidget(yao_frame)
        
        # ===== 消息区 =====
        self.message_label = QLabel("系统就绪，等待开始...")
        self.message_label.setStyleSheet("""
            font-size: 13px;
            color: #888888;
            padding: 12px 16px;
            background-color: #151515;
            border-radius: 8px;
            border: 1px solid #2a2a2a;
        """)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumHeight(40)
        layout.addWidget(self.message_label)
        
        layout.addStretch()
    
    def update_status_style(self, status: str):
        """更新状态栏样式"""
        styles = {
            Status.WARMUP: "#2a2a2a",
            Status.REAL: "#1b3a1b",
            Status.SHADOW: "#3a2a1a",
        }
        bg = styles.get(status, "#2a2a2a")
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 12px;
            }}
        """)
    
    def update_status(self, status: str, balance: int):
        """更新状态栏"""
        config = {
            Status.WARMUP: ("[预热] 预热模式", "#ffc107"),
            Status.REAL: ("[实盘] 实盘模式", "#4caf50"),
            Status.SHADOW: ("[防御] 幽灵观测", "#ff9800"),
        }
        
        text, color = config.get(status, ("[--] 未知", "#888888"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            font-size: 20px; 
            font-weight: bold; 
            color: {color};
            background: transparent;
        """)
        self.update_status_style(status)
        self.balance_label.setText(f"余额: {balance:,}")
    
    def update_arbiter(self, position: Optional[int]):
        """更新仲裁结果"""
        if position is None:
            self.arbiter_label.setText(">> 最终建议: 全员弃权")
            self.arbiter_frame.setStyleSheet("""
                QFrame {
                    background-color: #1a1a1a;
                    border: 2px solid #444444;
                    border-radius: 10px;
                }
            """)
            self.arbiter_label.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #888888;
                background: transparent;
            """)
        else:
            yao_name = YAO_MAP.get(position, "未知")
            self.arbiter_label.setText(f">> 建议躲避: {position}号 {yao_name} [X]")
            self.arbiter_frame.setStyleSheet("""
                QFrame {
                    background-color: #2a1515;
                    border: 2px solid #d32f2f;
                    border-radius: 10px;
                }
            """)
            self.arbiter_label.setStyleSheet("""
                font-size: 18px; 
                font-weight: bold; 
                color: #ff5252;
                background: transparent;
            """)
    
    def update_yao_grid(self, avoid: Optional[int], killer: Optional[int]):
        """更新八妖网格"""
        for pos, btn in self.yao_buttons.items():
            btn.reset_state()
            if pos == avoid:
                btn.set_avoid()
            if pos == killer:
                btn.set_killer()


class ConfigPage(QWidget):
    """配置页面"""
    
    configChanged = pyqtSignal(object)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("策略配置")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #e0e0e0;
            padding-bottom: 10px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # ===== 资金配置组 =====
        money_group = QGroupBox("资金策略")
        money_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #00bcd4;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                margin-top: 14px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: #1e1e1e;
            }
        """)
        money_inner = QVBoxLayout(money_group)
        money_inner.setSpacing(16)
        money_inner.setContentsMargins(16, 24, 16, 16)
        
        # 投注序列
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        label1 = QLabel("投注序列:")
        label1.setFixedWidth(100)
        label1.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row1.addWidget(label1)
        self.sequence_input = QLineEdit(",".join(map(str, config.sequence)))
        self.sequence_input.setPlaceholderText("例: 100, 600, 1300, 2700")
        self.sequence_input.setFixedHeight(40)
        self.sequence_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #00bcd4; }
        """)
        row1.addWidget(self.sequence_input)
        money_inner.addLayout(row1)
        
        # 滚雪球轮次
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        label2 = QLabel("滚雪球轮次:")
        label2.setFixedWidth(100)
        label2.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row2.addWidget(label2)
        self.snow_limit_spin = QSpinBox()
        self.snow_limit_spin.setRange(1, 10)
        self.snow_limit_spin.setValue(config.snow_limit)
        self.snow_limit_spin.setFixedHeight(40)
        self.snow_limit_spin.setFixedWidth(120)
        self.snow_limit_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox:focus { border-color: #00bcd4; }
        """)
        row2.addWidget(self.snow_limit_spin)
        row2.addStretch()
        money_inner.addLayout(row2)
        
        layout.addWidget(money_group)
        
        # ===== 影子配置组 =====
        shadow_group = QGroupBox("影子防御")
        shadow_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #00bcd4;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                margin-top: 14px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: #1e1e1e;
            }
        """)
        shadow_inner = QVBoxLayout(shadow_group)
        shadow_inner.setSpacing(16)
        shadow_inner.setContentsMargins(16, 24, 16, 16)
        
        # 解锁连胜数
        row3 = QHBoxLayout()
        row3.setSpacing(16)
        label3 = QLabel("解锁连胜数:")
        label3.setFixedWidth(100)
        label3.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row3.addWidget(label3)
        self.unlock_wins_spin = QSpinBox()
        self.unlock_wins_spin.setRange(1, 10)
        self.unlock_wins_spin.setValue(config.shadow_unlock_wins)
        self.unlock_wins_spin.setFixedHeight(40)
        self.unlock_wins_spin.setFixedWidth(120)
        self.unlock_wins_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox:focus { border-color: #00bcd4; }
        """)
        row3.addWidget(self.unlock_wins_spin)
        row3.addStretch()
        shadow_inner.addLayout(row3)
        
        # 解锁胜率
        row4 = QHBoxLayout()
        row4.setSpacing(16)
        label4 = QLabel("解锁胜率:")
        label4.setFixedWidth(100)
        label4.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row4.addWidget(label4)
        self.unlock_rate_spin = QDoubleSpinBox()
        self.unlock_rate_spin.setRange(0.5, 1.0)
        self.unlock_rate_spin.setSingleStep(0.05)
        self.unlock_rate_spin.setValue(config.shadow_unlock_rate)
        self.unlock_rate_spin.setFixedHeight(40)
        self.unlock_rate_spin.setFixedWidth(120)
        self.unlock_rate_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QDoubleSpinBox:focus { border-color: #00bcd4; }
        """)
        row4.addWidget(self.unlock_rate_spin)
        row4.addStretch()
        shadow_inner.addLayout(row4)
        
        # 软着陆选项
        row5 = QHBoxLayout()
        row5.setSpacing(16)
        self.soft_landing_check = QCheckBox("启用软着陆 (解锁后首注减半)")
        self.soft_landing_check.setChecked(config.soft_landing)
        self.soft_landing_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #cccccc;
                spacing: 10px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #3a3a3a;
                border-radius: 4px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #00bcd4;
                border-color: #00bcd4;
            }
        """)
        row5.addWidget(self.soft_landing_check)
        row5.addStretch()
        shadow_inner.addLayout(row5)
        
        layout.addWidget(shadow_group)
        
        # ===== 预热配置组 =====
        warmup_group = QGroupBox("预热设置")
        warmup_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #00bcd4;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                margin-top: 14px;
                padding: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: #1e1e1e;
            }
        """)
        warmup_inner = QVBoxLayout(warmup_group)
        warmup_inner.setSpacing(16)
        warmup_inner.setContentsMargins(16, 24, 16, 16)
        
        # 预热轮次
        row6 = QHBoxLayout()
        row6.setSpacing(16)
        label6 = QLabel("预热轮次:")
        label6.setFixedWidth(100)
        label6.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row6.addWidget(label6)
        self.warmup_spin = QSpinBox()
        self.warmup_spin.setRange(0, 50)
        self.warmup_spin.setValue(config.warmup_rounds)
        self.warmup_spin.setFixedHeight(40)
        self.warmup_spin.setFixedWidth(120)
        self.warmup_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox:focus { border-color: #00bcd4; }
        """)
        row6.addWidget(self.warmup_spin)
        row6.addStretch()
        warmup_inner.addLayout(row6)
        
        # 初始余额
        row7 = QHBoxLayout()
        row7.setSpacing(16)
        label7 = QLabel("初始余额:")
        label7.setFixedWidth(100)
        label7.setStyleSheet("font-size: 14px; color: #cccccc; background: transparent;")
        row7.addWidget(label7)
        self.balance_spin = QSpinBox()
        self.balance_spin.setRange(100, 1000000)
        self.balance_spin.setSingleStep(1000)
        self.balance_spin.setValue(config.initial_balance)
        self.balance_spin.setFixedHeight(40)
        self.balance_spin.setFixedWidth(150)
        self.balance_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QSpinBox:focus { border-color: #00bcd4; }
        """)
        row7.addWidget(self.balance_spin)
        row7.addStretch()
        warmup_inner.addLayout(row7)
        
        layout.addWidget(warmup_group)
        
        # ===== 操作按钮 =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        
        self.apply_btn = QPushButton("应用配置")
        self.apply_btn.setFixedHeight(48)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4;
                color: #1a1a1a;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #26c6da; }
            QPushButton:pressed { background-color: #00acc1; }
        """)
        self.apply_btn.clicked.connect(self.apply_config)
        btn_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("重置默认")
        self.reset_btn.setFixedHeight(48)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #666666; }
        """)
        self.reset_btn.clicked.connect(self.reset_config)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def apply_config(self):
        """应用配置"""
        try:
            sequence = [int(x.strip()) for x in self.sequence_input.text().split(",")]
            self.config.sequence = sequence
        except ValueError:
            pass
        
        self.config.snow_limit = self.snow_limit_spin.value()
        self.config.shadow_unlock_wins = self.unlock_wins_spin.value()
        self.config.shadow_unlock_rate = self.unlock_rate_spin.value()
        self.config.soft_landing = self.soft_landing_check.isChecked()
        self.config.warmup_rounds = self.warmup_spin.value()
        self.config.initial_balance = self.balance_spin.value()
        
        self.configChanged.emit(self.config)
    
    def reset_config(self):
        """重置为默认配置"""
        default = Config()
        self.sequence_input.setText(",".join(map(str, default.sequence)))
        self.snow_limit_spin.setValue(default.snow_limit)
        self.unlock_wins_spin.setValue(default.shadow_unlock_wins)
        self.unlock_rate_spin.setValue(default.shadow_unlock_rate)
        self.soft_landing_check.setChecked(default.soft_landing)
        self.warmup_spin.setValue(default.warmup_rounds)
        self.balance_spin.setValue(default.initial_balance)


class DataPage(QWidget):
    """数据页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("历史数据")
        title.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            color: #e0e0e0;
        """)
        layout.addWidget(title)
        
        # 统计摘要
        self.stats_label = QLabel("总轮次: 0  |  胜: 0  |  负: 0  |  胜率: 0%")
        self.stats_label.setStyleSheet("""
            font-size: 15px; 
            color: #aaaaaa; 
            padding: 16px 20px;
            background-color: #252525;
            border-radius: 10px;
            border: 1px solid #333333;
        """)
        layout.addWidget(self.stats_label)
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["时间", "神仙猿", "躲避", "结果", "状态", "盈亏"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #222222;
                alternate-background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 8px;
                gridline-color: #333333;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #00697a;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #00bcd4;
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid #00bcd4;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.table)
        
        # 清除按钮
        self.clear_btn = QPushButton("清除数据")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_data)
        layout.addWidget(self.clear_btn)
    
    def add_record(self, time_str: str, ape: int, avoid: Optional[int], 
                   is_win: bool, status: str, profit: int):
        """添加一条记录"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        ape_name = f"{ape} {YAO_MAP.get(ape, '')}"
        avoid_name = f"{avoid} {YAO_MAP.get(avoid, '')}" if avoid else "-"
        result = "WIN" if is_win else "LOSE"
        profit_str = f"+{profit}" if profit > 0 else str(profit) if profit < 0 else "0"
        
        # 状态简写
        status_short = {"WARMUP": "预热", "REAL": "实盘", "SHADOW": "防御"}.get(status, status)
        
        items_data = [
            (time_str, None),
            (ape_name, None),
            (avoid_name, None),
            (result, "#4caf50" if is_win else "#f44336"),
            (status_short, None),
            (profit_str, "#4caf50" if profit > 0 else "#f44336" if profit < 0 else None),
        ]
        
        from PyQt6.QtGui import QColor
        for col, (text, color) in enumerate(items_data):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if color:
                item.setForeground(QColor(color))
            else:
                item.setForeground(QColor("#e0e0e0"))
            self.table.setItem(row, col, item)
        
        # 滚动到最新
        self.table.scrollToBottom()
    
    def update_stats(self, total: int, wins: int, losses: int):
        """更新统计"""
        rate = wins / max(1, wins + losses) * 100
        self.stats_label.setText(
            f"总轮次: {total}  |  胜: {wins}  |  负: {losses}  |  胜率: {rate:.1f}%"
        )
    
    def clear_data(self):
        """清除数据"""
        self.table.setRowCount(0)
        self.stats_label.setText("总轮次: 0  |  胜: 0  |  负: 0  |  胜率: 0%")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shadow-Hunter v10.4")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 780)
        
        # 加载样式表
        self.load_stylesheet()
        
        # 创建配置
        self.config = Config()
        
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== 侧边栏 =====
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #151515;
                border-right: 1px solid #2a2a2a;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(80)
        logo_frame.setStyleSheet("background-color: #101010;")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(16, 16, 16, 16)
        
        logo_title = QLabel("Shadow")
        logo_title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #ff5722;
            background: transparent;
        """)
        logo_layout.addWidget(logo_title)
        
        logo_sub = QLabel("Hunter v10.4")
        logo_sub.setStyleSheet("""
            font-size: 12px; 
            color: #888888;
            background: transparent;
        """)
        logo_layout.addWidget(logo_sub)
        
        sidebar_layout.addWidget(logo_frame)
        
        # 分隔线
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #2a2a2a;")
        sidebar_layout.addWidget(sep)
        
        # 导航按钮
        self.nav_buttons = []
        nav_items = [("监控台", 0), ("配置", 1), ("数据", 2)]
        
        for text, idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #888888;
                    border: none;
                    border-left: 3px solid transparent;
                    padding-left: 20px;
                    text-align: left;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                }
                QPushButton:checked {
                    background-color: #1e1e1e;
                    color: #00bcd4;
                    border-left: 3px solid #00bcd4;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        sidebar_layout.addStretch()
        
        # 版本信息
        version = QLabel("v10.4")
        version.setStyleSheet("""
            color: #555555; 
            padding: 16px;
            font-size: 12px;
            background: transparent;
        """)
        sidebar_layout.addWidget(version)
        
        main_layout.addWidget(sidebar)
        
        # ===== 内容区 =====
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #1e1e1e;")
        
        self.monitor_page = MonitorPage()
        self.config_page = ConfigPage(self.config)
        self.data_page = DataPage()
        
        self.stack.addWidget(self.monitor_page)
        self.stack.addWidget(self.config_page)
        self.stack.addWidget(self.data_page)
        
        main_layout.addWidget(self.stack)
        
        # 默认选中监控台
        self.nav_buttons[0].setChecked(True)
        
        # 连接配置变更信号
        self.config_page.configChanged.connect(self.on_config_changed)
    
    def load_stylesheet(self):
        """加载样式表"""
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
    
    def switch_page(self, index: int):
        """切换页面"""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    
    def on_config_changed(self, config: Config):
        """配置变更处理"""
        self.config = config
        self.monitor_page.message_label.setText("[OK] 配置已更新")
    
    # ==================== UI 更新接口 ====================
    
    def update_ui(self, data: dict):
        """统一的 UI 更新接口"""
        # 更新状态栏
        self.monitor_page.update_status(
            data.get('status', Status.WARMUP),
            data.get('balance', 0)
        )
        
        # 更新 AI 卡片
        ai_votes = data.get('ai_votes', {})
        for name, card in self.monitor_page.ai_cards.items():
            if name in ai_votes:
                v = ai_votes[name]
                card.update_data(v.get('vote'), v.get('confidence', 0), v.get('ema', 10))
        
        # 更新仲裁结果
        self.monitor_page.update_arbiter(data.get('arbiter_decision'))
        
        # 更新八妖网格
        self.monitor_page.update_yao_grid(
            data.get('avoid'),
            data.get('killer')
        )
        
        # 更新消息
        if 'message' in data:
            self.monitor_page.message_label.setText(data['message'])
        
        # 添加历史记录
        if 'record' in data:
            r = data['record']
            self.data_page.add_record(
                r.get('time', ''),
                r.get('ape', 0),
                r.get('avoid'),
                r.get('is_win', False),
                r.get('status', ''),
                r.get('profit', 0)
            )
        
        # 更新统计
        if 'stats' in data:
            s = data['stats']
            self.data_page.update_stats(
                s.get('total', 0),
                s.get('wins', 0),
                s.get('losses', 0)
            )
