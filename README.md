# 夸克网盘资源分享管理系统

一个简洁高效的网盘资源共享系统，支持 AI 智能识别网盘分享链接并自动入库，适合资源博主和个人分享者管理、分享网盘资源。

## 核心功能

### 用户端（前台）
- 泤嵌 **资源搜索**：极简风格搜索界面，支持分类浏览、一键复制链接
- 泤嵌 **用户注册登录**：弹窗式注册/登录，支持用户状态管理
- 泤嵌 **公告系统**：横幅展示公告，支持 Markdown 格式内容
- 泤嵌 **许愿池**：用户可提交资源许愿，查看回复状态，红点提示新回复
- 泤嵌 **打赏通道**：展示打赏信息，支持 Markdown 格式

### 管理端（后台）
- 泤嵌 **仪表盘**：资源统计、搜索统计、快搜操作入口
- 泤嵌 **资源管理**：完整的 CRUD 操作，支持筛选、分类
- 泤嵌 **AI 智能导入**：集成百宝箱大模型，自动识别网盘分享链接
- 泤嵌 **CSV 批量导入**：支持 CSV 文件批量导入资源
- 泤嵌 **分类管理**：资源分类的增删改查
- 泤嵌 **用户管理**：用户列表、状态管理
- 泤嵌 **公告管理**：Markdown 编辑器，支持图片、排序、显示控制
- 泤嵌 **许愿池管理**：查看用户许愿、回复、删除、一键同步到资源库
- 泤嵌 **打赏通道设置**：Markdown 编辑打赏内容

### 技术亮点
- 泤嵌 **一键启动**：本地开发只需一条命令启动所有服务
- 泤嵌 **Markdown 支持**：公告、打赏内容支持 Markdown 格式，集成 md-editor-v3 编辑器
- 泤嵌 **消息提醒**：许愿回复红点提醒，实时更新

## 技术栈

| 层级 | 技术 |
|------|------|
| 用户前端 | Vue 3 + Vite + TailwindCSS + Pinia |
| 管理后台 | Vue 3 + Vite + Element Plus + md-editor-v3 |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL 16 (Docker) |
| AI | 百宝箱大模型 (OpenAI 兼容接口) |

## 快速开始

### 环境要求

- Docker 24+（仅用于运行数据库）
- Docker Compose 2.24+
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 一键启动
`ash
git clone https://github.com/your-username/cloud-drive-search.git
cd cloud-drive-search

# 配置环境变量（可选，默认配置可直接运行）
cp .env.example backend/.env
# 编辑 backend/.env，修改 AI_API_KEY

# 一键启动所有服务
./start.sh
`

启动后访问：
- 用户端前台：http://localhost:8080
- 管理后台：http://localhost:8081
