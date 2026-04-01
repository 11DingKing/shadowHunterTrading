# Shadow-Hunter v10.4

基于"方块兽"游戏地狱板块的自动化博弈辅助系统

## 1. How to Run

```bash
docker compose up --build -d
```

## 2. Services

| 服务 | 访问地址 |
|------|----------|
| 主应用 (noVNC) | http://localhost:8081/vnc.html |

## 3. 测试账号

本系统为单机模拟软件，无需登录账号。启动后自动进入预热模式，10轮后切换至实盘模式。

## 4. 题目内容

```
🛠️ Shadow-Hunter v10.4 AI 辅助开发执行方案 

零、 项目基础设定 (Project Setup) 
首先，你需要告诉 AI 项目的 世界观 和 基本结构。这就像给 AI 设定"系统人设"。 

📂 推荐文件结构: 
ShadowHunter/ 
├── main.py                # 程序入口 
├── config.py              # 常量与配置定义 
├── core/ 
│   ├── algorithms.py      # 9种数学算法 
│   ├── agents.py          # 3大AI人格 
│   ├── arbiter.py         # 仲裁系统 
│   └── strategy.py        # 资金与风控引擎 
└── ui/ 
    ├── styles.qss         # 界面样式表 
    └── main_window.py     # PyQt6 界面逻辑 

第一步：定义数据结构与常量 (Config) 
🎯 目标: 确立 8 妖、神仙猿、矿石等术语，防止 AI 混淆。
定义 8 个位置的映射字典 YAO_MAP：1:熊妖, 2:牛妖, 3:狐妖, 4:蛇妖, 5:蛛妖, 6:兔妖, 7:象妖, 8:猴妖。 
基础概率常量 BASE_PROB = 0.125。 
一个 Config 类，用于存储策略参数。

第二步：构建底层数学探针 (Algorithms) 
🎯 目标: 实现 Layer 1 的 9 种算法。
需要一个 AlgorithmLab 类，包含 9 个静态方法，对应 9 种针对伪随机的探针。

第三步：构建 AI 人格与仲裁 (AI & Arbiter) 
🎯 目标: 实现 Deep/Tongyi/Doubao 的人设逻辑和 EMA 加权仲裁。

第四步：构建策略引擎 (Strategy - 核心难点) 
🎯 目标: 实现"序列+滚雪球"混合资金链和"影子防御"状态机。

第五步：构建 UI 界面 (UI) 
🎯 目标: 实现深色地狱风格界面，分为 3 个页面。
背景色 #1e1e1e，高亮色 #00bcd4 (青色) 和 #ff3d00 (熔岩红)。

第六步：整合主程序 (Main Integration) 
🎯 目标: 将所有模块串联起来，加入反侦察逻辑。
```

---

## 项目简介

Shadow-Hunter v10.4 (影子猎手) 是一款基于多层算法探针与 AI 人格投票机制的博弈辅助系统。系统通过 9 种数学算法分析历史数据，由 3 个 AI 人格 (Deep/Tongyi/Doubao) 进行投票，经 EMA 加权仲裁后给出躲避建议。

### 核心功能

- **9 种探针算法**: 趋势追踪、冷门补位、Z-Score、镜像跟随、反连击、时间因子、熵随机、马尔可夫、影子探针
- **3 大 AI 人格**: Deep (趋势派)、Tongyi (模式派)、Doubao (随机派)
- **EMA 加权仲裁**: 根据历史表现动态调整各人格权重
- **策略状态机**: WARMUP (预热) → REAL (实盘) ⇄ SHADOW (影子防御)
- **资金管理**: 序列投注 + 滚雪球 + 软着陆机制

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| GUI 框架 | PyQt6 |
| 容器化 | Docker + noVNC |
| 基础镜像 | python:3.11-slim |

---

## 项目结构

```
ShadowHunter/
├── main.py                 # 程序入口
├── config.py               # 常量与配置定义
├── requirements.txt        # Python 依赖
├── Dockerfile              # 容器构建文件
├── docker-compose.yml      # 容器编排
├── core/
│   ├── __init__.py
│   ├── algorithms.py       # 9种数学算法
│   ├── agents.py           # 3大AI人格
│   ├── arbiter.py          # 仲裁系统
│   └── strategy.py         # 资金与风控引擎
├── ui/
│   ├── __init__.py
│   ├── styles.qss          # 界面样式表
│   └── main_window.py      # PyQt6 界面逻辑
└── docs/
    ├── Requirements.md     # 需求文档
    ├── Roadmap.md          # 开发路线图
    ├── DesignSpec.md       # 设计规范
    └── SelfTestReport.md   # 自测报告
```

---

## 冲突解决记录

| 冲突点 | AI 分析 | 最终决策 |
|--------|---------|----------|
| PyQt6 是桌面应用，不满足 Web 访问要求 | Docker 交付标准要求通过 localhost 访问 | 采用 noVNC 方案，将桌面应用通过 Web 浏览器访问 |

---

## 使用说明

### 界面操作

1. **监控台**: 查看当前状态、AI 建议和八妖位置
2. **配置**: 调整投注序列、滚雪球轮次、影子解锁参数
3. **数据**: 查看历史记录和胜率统计

### 状态说明

| 状态 | 含义 |
|------|------|
| [预热] | 观测模式，不进行投注 |
| [实盘] | 实际投注模式 |
| [防御] | 影子模式，虚拟观测中 |

---

## 许可证

MIT License
