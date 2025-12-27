# Echo Tutor - AI 语言学习助手

一个基于多智能体架构的智能语言学习系统，支持文档/图片读取、发音练习和智能问答。

## 🌟 功能特性

- 📄 **文档/图片上传** - 支持文本文件和图片OCR识别
- 🔊 **智能发音** - 使用ModelScope TTS生成标准发音
- 🤖 **AI问答** - 基于Qwen大模型生成学习问题
- ✅ **智能评估** - 自动评估答案并提供反馈
- 📚 **分段学习** - 智能分段，循序渐进

## 🏗️ 技术栈

### 后端
- **FastAPI** - 现代化的Python Web框架
- **LangGraph** - 多智能体编排框架
- **ModelScope** - OCR、TTS和Qwen LLM API
- **Pydantic** - 数据验证

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - 优雅的UI组件库
- **Vite** - 快速的构建工具
- **Axios** - HTTP客户端

## 📁 项目结构

```
echo_tutor/
├── pyproject.toml             # 项目配置和依赖管理（uv）
├── README.md                  # 项目说明文档
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
│
├── echo_tutor/                # 主Python包
│   ├── __init__.py            # 包初始化
│   ├── main.py                # FastAPI应用入口
│   ├── config.py              # 配置管理
│   │
│   ├── agents/                # LangGraph智能体
│   │   ├── __init__.py
│   │   ├── graph.py           # 工作流定义
│   │   ├── reader_agent.py   # 文档读取Agent
│   │   └── tutor_agent.py    # 发音辅导Agent
│   │
│   ├── api/                   # API路由
│   │   ├── __init__.py
│   │   └── routes.py          # API端点定义
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic模型
│   │
│   └── services/              # 服务层
│       ├── __init__.py
│       └── modelscope_client.py  # ModelScope API客户端
│
├── tests/                     # 测试目录
│   ├── __init__.py
│   └── test_config.py         # 配置测试
│
├── data/                      # 数据目录
│   └── uploads/               # 上传文件存储
│
└── frontend/                  # 前端代码
    ├── src/
    │   ├── components/        # Vue组件
    │   ├── views/             # 页面视图
    │   ├── services/          # API服务
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) - 快速的Python包管理器
- Node.js 18+
- ModelScope API Key

### 安装 uv

如果还没有安装 uv，可以通过以下命令安装：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env
```

编辑 `.env` 文件，填入你的 ModelScope API Key：

```env
MODELSCOPE_API_KEY=your_api_key_here
QWEN_MODEL=qwen-turbo
```

### 2. 启动后端

```bash
# 进入项目根目录

