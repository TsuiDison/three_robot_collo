# 多智能体协作配送仿真系统 (Multi-Agent Collaborative Delivery Simulation)

![Simulation Screenshot](https://user-images.githubusercontent.com/your-username/your-repo/assets/simulation_demo.gif)  
*(在这里替换为您自己的仿真截图或 GIF 动图)*

这是一个基于 Python 的多智能体系统（MAS）仿真平台，旨在模拟一个复杂的无人机、无人车和机器狗协同工作的城市物流配送场景。系统能够动态生成复杂的随机地图，处理一系列配送任务，并实时可视化整个过程。

---

## ✨ 功能亮点

- **异构智能体协同**:
  - **三种智能体**: 无人机、无人车、机器狗，每种都有独特的速度、载重、地形适应性。
  - **智能决策**: 系统能根据任务重量、目的地地形、智能体实时位置和状态，动态决策采用**直达**或**中转**策略。
  - **动态任务分配**: 能够为中转任务的每一段独立寻找最优的执行者，实现高效的资源利用。

- **动态复杂的仿真环境**:
  - **程序化地图生成**: 每次运行都会通过 Perlin 噪声生成包含山脉、河流、湖泊、道路和建筑的独一无二的 100x100 地图。
  - **战争迷雾**: 智能体拥有有限的视野，需要在探索中逐步构建共享的知识地图。
  - **A\* 路径规划**: 所有智能体都基于共享的、不完整的知识地图进行鲁棒的路径规划。

- **高性能实时可视化**:
  - **Matplotlib 动画**: 使用 `blit=True` 模式和 Artist 池化技术，实现流畅、高效的实时动画渲染。
  - **信息丰富的UI**: 包含动态更新的系统状态面板和清晰的分组图例，直观展示所有关键信息。
  - **任务路径可视化**: 每个任务的配送路径都会以独特的颜色进行高亮显示。

- **灵活的任务与日志系统**:
  - **YAML 任务配置**: 可通过简单的 `tasks.yaml` 文件轻松定义包含重量和紧急度的复杂任务队列。
  - **优先级处理**: 系统能够优先处理紧急度更高的任务。
  - **详细日志输出**: 仿真结束后，会自动生成 `delivery_log.json` 文件，记录每个任务（包括中转分段）的详细执行数据，便于分析和复盘。

---

## 🛠️ 技术栈

- **核心语言**: Python 3.x
- **核心库**:
  - `numpy`: 用于高效的地图数据处理和计算。
  - `matplotlib`: 用于实现强大的数据可视化和动画。
  - `PyYAML`: 用于解析任务配置文件。
  - `noise`: 用于生成 Perlin 噪声以创建程序化地图。

---

## 🚀 如何运行

### 1. 环境配置

首先，确保您已安装 Python 3。然后，克隆本仓库并安装所需的依赖库。

```bash
# 克隆仓库
git clone https://github.com/TsuiDison/three_robot_collo.git
cd three_robot_collo

# 安装依赖
pip install -r requirements.txt
```

*(注意: 您需要创建一个 `requirements.txt` 文件，内容如下:)*

**`requirements.txt`**:
```
numpy
matplotlib
PyYAML
noise
```

### 2. 定义任务

您可以编辑 `tasks.yaml` 文件来设计您自己的配送任务。每个任务可以定义 `id`, `goal_pos`, `weight`, 和 `urgency`。

```yaml
- id: T01_EXAMPLE
  goal_pos: [80, 80]
  weight: 15.0      # 重量 (kg)
  urgency: 5        # 紧急度 (越高越优先)
```

### 3. 启动仿真

直接运行主程序即可启动仿真。

```bash
python main.py
```

仿真窗口将会弹出，您可以实时观察智能体的决策和行动。关闭窗口后，程序会自动停止并生成日志文件。

---

## 📁 代码结构

项目代码结构清晰，各模块职责分明：

```
.
├── 📂assets/                  # (建议) 存放截图、GIF等媒体资源
├── 📜main.py                  # 程序主入口，负责初始化和启动
├── 📜config.py                # 存放所有配置参数 (地图大小、智能体数量、颜色等)
├── 📜map_system.py            # 负责生成和管理真实地图
├── 📜knowledge_base.py         # 定义了智能体共享的知识地图
├── 📜path_planning.py          # A* 路径规划算法实现
├── 📜delivery_task.py          # DeliveryTask 类定义
├── 📜agent.py                  # 定义了 Agent 基类和具体的智能体子类 (Drone, Car, Dog)
├── 📜vehicle.py                # 定义了智能体搭载的载具，处理移动逻辑
├── 📜multi_agent_coordination.py # 系统的核心！负责决策、任务分配和智能体协调
├── 📜visualization.py          # Matplotlib 可视化和动画实现
├── 📜log_entry.py              # 定义了日志条目的数据结构
├── 📜tasks.yaml                # 任务定义文件
├── 📜delivery_log.json         # (自动生成) 仿真日志输出
└── 📜README.md                 # 就是你正在看的这个文件
```

---

## 🔭 未来展望

这个项目为更复杂的研究和功能提供了坚实的基础。未来的可能方向包括：

- [ ] **更复杂的决策模型**: 引入强化学习或更高级的启发式算法来优化任务分配和路径选择。
- [ ] **动态事件**: 增加随机事件，如道路拥堵、天气变化（影响无人机）、智能体故障等。
- [ ] **能源/电量约束**: 为智能体增加电池限制，需要规划返回充电的路径。
- [ ] **更丰富的交互**: 允许智能体之间进行通信和协商，而不仅仅依赖中央协调器。
- [ ] **Web 前端**: 使用 Flask/Django 和 Three.js/D3.js 将仿真结果在网页上进行 3D 或交互式展示。

---

## 🤝 贡献

欢迎任何形式的贡献！如果您有任何想法、建议或发现了 bug，请随时提交一个 [Issue](https://github.com/TsuiDison/three_robot_collo/issues) 或 [Pull Request](https://github.com/TsuiDison/three_robot_collo/pulls)。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 授权。
*(您可以在项目中添加一个 `LICENSE` 文件)*
