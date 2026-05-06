#!/bin/bash

# 云盘资源搜索系统 - 一键启动脚本
# Docker 运行 PostgreSQL 数据库，本地运行后端和前端

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  云盘资源搜索系统 - 一键启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查依赖
echo -e "${YELLOW}[1/5] 检查依赖...${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3 未安装${NC}"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: Node.js 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 所有依赖已安装${NC}"
echo ""

# 启动数据库
echo -e "${YELLOW}[2/5] 启动 PostgreSQL 数据库 (Docker)...${NC}"

# 使用 docker-compose 启动数据库
if docker-compose version &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# 等待数据库就绪
echo "等待数据库就绪..."
for i in {1..30}; do
    if docker exec clouddrive-db pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
echo -e "${GREEN}✓ 数据库已就绪${NC}"
echo ""

# 安装后端依赖
echo -e "${YELLOW}[3/5] 安装后端依赖...${NC}"
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 检查是否需要安装依赖
if ! pip show fastapi > /dev/null 2>&1; then
    echo "安装 Python 依赖..."
    pip install -q -r requirements.txt
fi

echo -e "${GREEN}✓ 后端依赖已就绪${NC}"
echo ""

# 安装前端依赖
echo -e "${YELLOW}[4/5] 安装前端依赖...${NC}"

# 前台
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "安装前台依赖..."
    npm install > /dev/null 2>&1
fi
echo -e "${GREEN}✓ 前台依赖已就绪${NC}"

# 管理后台
cd "$SCRIPT_DIR/admin"
if [ ! -d "node_modules" ]; then
    echo "安装管理后台依赖..."
    npm install > /dev/null 2>&1
fi
echo -e "${GREEN}✓ 管理后台依赖已就绪${NC}"
echo ""

# 启动服务
echo -e "${YELLOW}[5/5] 启动服务...${NC}"
echo ""

# 启动后端
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/clouddrive"

# 初始化数据库
python init_db.py > /dev/null 2>&1 || true

# 后台启动后端
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "  日志: $SCRIPT_DIR/backend.log"
echo "  地址: http://localhost:8000"
echo ""

# 启动前台
cd "$SCRIPT_DIR/frontend"
nohup npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ 前台服务已启动 (PID: $FRONTEND_PID)${NC}"
echo "  日志: $SCRIPT_DIR/frontend.log"
echo "  地址: http://localhost:3000"
echo ""

# 启动管理后台
cd "$SCRIPT_DIR/admin"
nohup npm run dev > "$SCRIPT_DIR/admin.log" 2>&1 &
ADMIN_PID=$!
echo -e "${GREEN}✓ 管理后台已启动 (PID: $ADMIN_PID)${NC}"
echo "  日志: $SCRIPT_DIR/admin.log"
echo "  地址: http://localhost:3001"
echo ""

# 保存 PID 到文件
cat > "$SCRIPT_DIR/.pids" << EOF
BACKEND_PID=$BACKEND_PID
FRONTEND_PID=$FRONTEND_PID
ADMIN_PID=$ADMIN_PID
EOF

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  所有服务已启动！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "访问地址:"
echo "  • 搜索前台: http://localhost:3000"
echo "  • 管理后台: http://localhost:3001"
echo "  • API 文档: http://localhost:8000/docs"
echo ""
echo "默认账号:"
echo "  • 用户名: admin"
echo "  • 密码: admin123"
echo ""
echo "管理命令:"
echo "  • 查看日志: tail -f backend.log frontend.log admin.log"
echo "  • 停止服务: ./stop.sh"
echo ""
