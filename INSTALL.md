# 旅行规划仿真系统 - 安装和运行指南

## 🚀 一键安装启动（推荐）

### Windows用户
```bash
# 方法1: 双击运行
start.bat

# 方法2: 命令行运行
python install_and_run.py
```

### Linux/Mac用户
```bash
# 方法1: Shell脚本
chmod +x start.sh
./start.sh

# 方法2: 直接运行
python3 install_and_run.py
```

## 📋 安装流程说明

### 自动安装程序特性
- ✅ **环境检查** - 自动检查Python版本和pip
- ✅ **镜像选择** - 支持国内镜像加速下载
- ✅ **依赖管理** - 智能安装必需和可选依赖
- ✅ **启动模式** - 根据环境自动选择最佳启动方式
- ✅ **错误处理** - 安装失败时提供降级方案

### 依赖层次
1. **必需依赖**: gradio (Web界面)
2. **可选依赖**: plotly (图表), psutil (性能监控), python-dateutil (日期处理)

## 🔧 手动安装选项

### 基础安装
```bash
# 只安装核心功能
pip install gradio
python main_browser_use.py
```

### 完整安装
```bash
# 安装所有功能
pip install gradio plotly psutil python-dateutil
python main_browser_use.py
```

### 使用国内镜像
```bash
# 清华镜像（推荐）
pip install gradio plotly psutil python-dateutil -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 阿里镜像
pip install gradio plotly psutil python-dateutil -i https://mirrors.aliyun.com/pypi/simple/

# 中科大镜像
pip install gradio plotly psutil python-dateutil -i https://pypi.mirrors.ustc.edu.cn/simple/
```

## 🎯 启动方式选择

### 1. Browser-Use风格 Web界面（推荐）
```bash
python main_browser_use.py
```
- ✅ 现代化界面设计
- ✅ 实时监控面板
- ✅ 完整功能支持
- 🌐 访问: http://127.0.0.1:7899

### 2. 经典Web界面
```bash
python main.py
```
- ✅ 传统界面风格
- ✅ 基础功能完整
- 🌐 访问: http://127.0.0.1:7899

### 3. 控制台模式（无依赖）
```bash
python simple_run.py
```
- ✅ 无需任何外部依赖
- ✅ 快速启动体验
- 💻 纯命令行交互

## 🛠️ 故障排除

### 常见问题

#### 1. Python版本问题
```
❌ Python版本过低: 2.7
解决方案: 安装Python 3.8+
下载地址: https://www.python.org/downloads/
```

#### 2. pip不可用
```
❌ pip不可用
解决方案: 
- Windows: python -m ensurepip --upgrade
- Linux: sudo apt install python3-pip
- Mac: python3 -m ensurepip --upgrade
```

#### 3. 网络问题
```
❌ 依赖下载失败
解决方案:
1. 使用国内镜像源
2. 增加超时时间: pip install --timeout 1000 gradio
3. 离线安装: 下载whl文件后本地安装
```

#### 4. 权限问题
```
❌ 权限不足
解决方案:
- Windows: 以管理员运行命令行
- Linux/Mac: 使用sudo或虚拟环境
- 或使用: pip install --user gradio
```

### 系统检查工具
```bash
# 运行系统检查
python check_system.py
```

## 📊 系统要求

### 最低要求
- Python 3.8+
- 100MB 可用内存
- 50MB 磁盘空间

### 推荐配置
- Python 3.9+
- 500MB 可用内存
- 200MB 磁盘空间
- 现代浏览器（Chrome/Firefox/Safari/Edge）

## 🌐 网络要求

### 在线安装
- 需要访问PyPI或镜像站
- 下载大小约20-50MB

### 离线使用
- 安装完成后可离线运行
- 所有数据本地存储

## 🔍 验证安装

### 快速测试
```bash
# 1. 检查系统状态
python check_system.py

# 2. 测试核心功能
python -c "from src.agent.travel_agent import TravelAgent; print('✅ 核心模块正常')"

# 3. 启动系统
python simple_run.py
```

### 功能验证
1. **代理创建** - 确保可以创建智能代理
2. **环境模拟** - 验证环境状态更新
3. **仿真执行** - 测试仿真引擎运行
4. **界面访问** - 确认Web界面可访问

## 💡 性能优化建议

### 提升安装速度
```bash
# 使用多线程安装
pip install --upgrade pip setuptools wheel

# 禁用缓存（节省空间）
pip install --no-cache-dir gradio

# 并行安装
pip install gradio plotly psutil python-dateutil --process-dependency-links
```

### 系统优化
```bash
# 清理pip缓存
pip cache purge

# 升级pip
python -m pip install --upgrade pip
```

## 🚀 快速开始检查清单

- [ ] Python 3.8+ 已安装
- [ ] pip 可正常使用
- [ ] 网络连接正常
- [ ] 运行 `python install_and_run.py`
- [ ] 选择镜像源
- [ ] 等待依赖安装完成
- [ ] 选择启动模式
- [ ] 访问 Web 界面或使用控制台

## 📞 获取帮助

如果遇到问题：
1. 运行 `python check_system.py` 诊断
2. 查看错误日志
3. 尝试控制台模式 `python simple_run.py`
4. 提交Issue或寻求帮助