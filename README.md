# Echo Tutor - AI 语言学习助手

一个基于多智能体架构的**云原生**智能语言学习系统，支持文档/图片读取、标准发音辅导及智能交互问答。

## 🌟 功能特性

- 📄 **多模态内容识别** - 使用 `qwen-vl-ocr` 云端大模型，精准识别图片与文档内容。
- 🔊 **旗舰级语音合成** - 集成 DashScope `qwen3-tts-flash` 模型，提供极速、自然的语音辅导。
- 🤖 **多智能体教学** - 基于 LangGraph 编排多智能体工作流，实现文档阅读、问题生成与评估。
- ✅ **智能互动评估** - 实时纠正发音与回答，提供建设性的学习反馈。
- ⚡ **极致启动速度** - 全面迁移至云端 API，告别 GB 级模型下载，实现后端秒级启动。

## 🏗️ 技术栈

### 后端
- **FastAPI** - 异步高性能 Web 框架
- **LangGraph** - 多智能体工作流引擎
- **DashScope (阿里云)** - Qwen-VL (OCR), Qwen3-TTS (语音), Qwen-Turbo (大模型)
- **uv** - 现代 Python 包管理工具

### 前端
- **Vue 3 + Vite** - 响应式前端开发环境
- **Element Plus** - 高质量 UI 组件库
- **Axios** - 异步数据交互

## 📁 项目结构

```
echo_tutor/
├── pyproject.toml             # 项目配置和依赖管理 (uv)
├── README.md                  # 项目说明文档
├── .env                       # 环境变量 (根目录)
├── .gitignore                 # Git 忽略文件
│
├── echo_tutor/                # 主 Python 包
│   ├── main.py                # FastAPI 入口 & 静态文件挂载
│   ├── config.py              # 集中配置管理
│   ├── agents/                # LangGraph 智能体逻辑
│   ├── api/                   # RESTful API 路由
│   ├── models/                # Pydantic 核心数据模型
│   └── services/              # 云端 API 客户端 (DashScope)
│
├── scripts/                   # 实用工具脚本
│   └── diagnose_api.py        # API 权限诊断工具
│
├── data/                      # 存储目录
│   └── uploads/               # 本地保存的上传文件与生成的语音 (.wav)
│
└── frontend/                  # Vue 前端项目
    ├── package.json
    └── src/
```

## 🚀 快速开始

### 1. 准备工作
- **Python 3.9+** 建议安装 [uv](https://github.com/astral-sh/uv) 提升效率。
- **Node.js 18+** 用于前端运行。
- **DashScope API Key**: 请访问 [阿里云官网](https://dashscope.console.aliyun.com/apiKey) 领取。

### 2. 环境配置
在根目录创建 `.env` 文件：
```env
MODELSCOPE_API_KEY=sk-xxxx...  # 填入你的真实 sk- 前缀的 Key
QWEN_MODEL=qwen-turbo
```

### 3. 启动项目

#### 后端启动 (根目录执行)
```bash
# 同步依赖并启动
uv sync
uv run uvicorn echo_tutor.main:app --reload
```
后端运行在: `http://localhost:8000`

#### 前端启动 (进入 frontend 目录)
```bash
cd frontend
npm install
npm run dev
```
前端预览: `http://localhost:5173`

## 🛠️ 诊断工具
如果您遇到 401 (未授权) 或 400 (参数错误)，请运行诊断脚本：
```bash
uv run python scripts/diagnose_api.py
```

## 📄 开源协议
[MIT License](LICENSE)
