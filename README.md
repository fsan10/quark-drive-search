# 云盘资源搜索系统 (CloudDrive Search System)

一个轻量级的网盘资源搜索系统，支持 AI 智能识别网盘分享链接并自动入库。

## ✨ 功能特性

### 用户端（前台）

- 🔍 **资源搜索**：极简风格搜索界面，支持模糊搜索、分类浏览、一键复制链接
- 👤 **用户注册登录**：弹窗式注册/登录，支持用户状态管理
- 📢 **公告系统**：椭圆标签展示公告，支持 Markdown 格式内容
- 🌟 **许愿池**：用户可提交资源许愿，查看回复状态，红点提示新消息
- ❤️ **打赏捐赠**：展示打赏信息，支持 Markdown 格式

### 管理端（后台）

- 📊 **仪表盘**：资源统计、搜索统计、快捷操作入口
- 📁 **资源管理**：完整的 CRUD 操作，支持筛选、分页
- 🤖 **AI 智能导入**：集成通义千问大模型，自动识别网盘分享链接
- 📥 **CSV 批量导入**：支持 CSV 文件批量导入资源
- 🏷️ **分类管理**：资源分类的增删改查
- 👥 **用户管理**：用户列表、状态管理
- 📢 **公告管理**：Markdown 编辑器，支持图片、排序、显示控制
- 🌟 **许愿池管理**：查看用户许愿、回复、一键同步到资源库
- ❤️ **打赏捐赠设置**：Markdown 编辑打赏内容

### 技术亮点

- 🚀 **一键启动**：本地开发只需一条命令启动所有服务
- 📝 **Markdown 支持**：公告、打赏内容支持 Markdown 格式，集成 [md-editor-v3](https://github.com/imzbf/md-editor-v3) 编辑器
- 🔔 **消息提醒**：许愿回复红点提示，实时更新

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TailwindCSS + Pinia |
| 管理后台 | Vue 3 + Vite + Element Plus + md-editor-v3 |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL 16 (Docker) |
| AI | 通义千问 (OpenAI 兼容接口) |

## 📦 快速开始

### 环境要求

- Docker 24+ (仅用于运行数据库)
- Docker Compose 2.24+
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/your-username/cloud-drive-search.git
cd cloud-drive-search

# 2. 配置环境变量（可选，默认配置可直接运行）
cp .env.example backend/.env
# 编辑 backend/.env，修改 AI_API_KEY

# 3. 一键启动所有服务
./start.sh
```

启动后访问：
- 搜索前台：http://localhost:3000
- 管理后台：http://localhost:3001
- API 文档：http://localhost:8000/docs
- 默认管理员账号：`admin` / `admin123`

### 停止服务

```bash
# 停止所有本地服务（保留数据库）
./stop.sh

# 停止数据库
docker-compose down
```

## 📁 项目结构

```
cloud-drive-search/
├── start.sh                # 一键启动脚本
├── stop.sh                 # 停止服务脚本
├── docker-compose.yml      # Docker 数据库配置
├── .env.example            # 环境变量模板
├── docs/                   # 项目文档
│   └── design-v2.md        # 功能设计文档
│
├── backend/                # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   ├── models/         # 数据模型
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── resource.py
│   │   │   ├── search_log.py
│   │   │   ├── announcement.py  # 公告模型
│   │   │   ├── wish.py          # 许愿模型
│   │   │   ├── wish_reply.py    # 许愿回复模型
│   │   │   └── site_setting.py  # 系统配置模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── api/            # API 路由
│   │   │   ├── auth.py
│   │   │   ├── search.py
│   │   │   ├── announcement.py  # 公告API
│   │   │   ├── wish.py          # 许愿池API
│   │   │   ├── site_setting.py  # 系统配置API
│   │   │   └── admin/           # 管理后台API
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt
│
├── frontend/               # 搜索前台
│   └── src/
│       ├── views/          # 页面组件
│       ├── components/     # 公共组件
│       │   ├── AuthDialog.vue       # 注册/登录弹窗
│       │   ├── AnnouncementBar.vue  # 公告展示
│       │   ├── DonationButton.vue   # 打赏捐赠
│       │   ├── WishDialog.vue       # 许愿提交
│       │   └── MyWishes.vue         # 我的许愿
│       ├── stores/         # Pinia 状态管理
│       ├── api/            # API 封装
│       └── router/         # 路由配置
│
└── admin/                  # 管理后台
    └── src/
        ├── views/          # 页面组件
        │   ├── AnnouncementView.vue  # 公告管理
        │   ├── WishPoolView.vue      # 许愿池管理
        │   └── DonationView.vue      # 打赏捐赠设置
        ├── api/            # API 封装
        └── router/         # 路由配置
```

## 🌐 支持的网盘

| 网盘 | 域名 | 说明 |
|------|------|------|
| 夸克网盘 | pan.quark.cn | 默认支持 |
| 百度网盘 | pan.baidu.com | 默认支持 |
| 阿里云盘 | aliyundrive.com | 默认支持 |
| 迅雷云盘 | pan.xunlei.com | 默认支持 |
| 123云盘 | 123pan.com | 默认支持 |
| 蓝奏云 | lanzou*.com | 默认支持 |

## 🤖 AI 模型配置

系统默认使用阿里百炼平台的免费模型，支持以下模型：

| 模型 | 说明 |
|------|------|
| Qwen 3.6 Plus | 默认模型，效果好 |
| Qwen 3.5 122B | 大参数模型 |
| Qwen 3.6 Flash | 速度快 |
| MiniMax M2.5 | MiniMax 模型 |
| DeepSeek V4 Pro | DeepSeek 模型 |

在管理后台的 AI 导入页面可以自由切换模型。

### 配置 AI API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 创建 API Key
3. 编辑 `backend/.env` 文件：
   ```
   AI_API_KEY=your-api-key-here
   ```

## 📝 Markdown 编辑器

管理后台的公告管理和打赏捐赠设置页面集成了 [md-editor-v3](https://github.com/imzbf/md-editor-v3) 开源 Markdown 编辑器：

- ✅ Vue 3 原生支持
- ✅ 支持图片上传
- ✅ 实时预览
- ✅ 轻量、中文友好
- ✅ MIT 开源协议

## ⚙️ 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接串 | postgresql+psycopg2://postgres:postgres@localhost:5432/clouddrive |
| SECRET_KEY | JWT 密钥 | dev-secret-key-change-in-production |
| AI_API_KEY | AI 模型 API Key | (必填) |
| AI_API_BASE | AI API 地址 | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| AI_MODEL | 默认 AI 模型 | qwen3.6-plus |
| ADMIN_USERNAME | 初始管理员用户名 | admin |
| ADMIN_PASSWORD | 初始管理员密码 | admin123 |

## 📖 API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。

### 主要 API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/login` | 用户登录 |
| 认证 | `POST /api/auth/register` | 用户注册 |
| 搜索 | `GET /api/search` | 搜索资源 |
| 公告 | `GET /api/announcements` | 获取公告列表 |
| 许愿池 | `POST /api/wishes` | 提交许愿 |
| 许愿池 | `GET /api/wishes/mine` | 我的许愿 |
| 打赏 | `GET /api/site-settings/donation` | 获取打赏内容 |

## ❓ 常见问题

### 端口被占用

如果 3000、3001 或 8000 端口被占用，可以修改启动命令：

```bash
# 前端使用其他端口
cd frontend
npm run dev -- --port 3002

# 管理后台使用其他端口
cd admin
npm run dev -- --port 3003

# 后端使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 数据库连接失败

确保 Docker 数据库已启动：

```bash
docker-compose ps
# 如果没有运行
docker-compose up -d
```

### 前端依赖安装失败

尝试使用淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

## 📄 License

[MIT](LICENSE)

## 🙏 致谢

- [md-editor-v3](https://github.com/imzbf/md-editor-v3) - Vue 3 Markdown 编辑器
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [TailwindCSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
