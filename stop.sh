#!/bin/bash

# 云盘资源搜索系统 - 停止服务脚本
# 停止所有本地运行的服务

set -e

echo "================================"
echo "  网盘资源搜索系统 - 停止服务"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 停止后端服务
echo -e "${YELLOW}正在停止后端服务...${NC}"
if [ -f ".pids" ]; then
    BACKEND_PID=$(grep "BACKEND_PID=" .pids | cut -d'=' -f2)
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo "后端服务未运行"
    fi
else
    # 尝试通过端口查找并停止
    BACKEND_PID=$(lsof -ti:8000 2>/dev/null || echo "")
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 后端服务已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo "后端服务未运行"
    fi
fi

# 停止前端服务
echo -e "${YELLOW}正在停止前端服务...${NC}"
if [ -f ".pids" ]; then
    FRONTEND_PID=$(grep "FRONTEND_PID=" .pids | cut -d'=' -f2)
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo "前端服务未运行"
    fi
else
    FRONTEND_PID=$(lsof -ti:3000 2>/dev/null || echo "")
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 前端服务已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo "前端服务未运行"
    fi
fi

# 停止管理后台服务
echo -e "${YELLOW}正在停止管理后台服务...${NC}"
if [ -f ".pids" ]; then
    ADMIN_PID=$(grep "ADMIN_PID=" .pids | cut -d'=' -f2)
    if [ -n "$ADMIN_PID" ] && kill -0 "$ADMIN_PID" 2>/dev/null; then
        kill "$ADMIN_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 管理后台服务已停止 (PID: $ADMIN_PID)${NC}"
    else
        echo "管理后台服务未运行"
    fi
else
    ADMIN_PID=$(lsof -ti:3001 2>/dev/null || echo "")
    if [ -n "$ADMIN_PID" ]; then
        kill "$ADMIN_PID" 2>/dev/null || true
        echo -e "${GREEN}✓ 管理后台服务已停止 (PID: $ADMIN_PID)${NC}"
    else
        echo "管理后台服务未运行"
    fi
fi

# 删除PID文件
if [ -f ".pids" ]; then
    rm -f .pids
    echo -e "${GREEN}✓ 已清理PID文件${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}  所有本地服务已停止${NC}"
echo "================================"
echo ""
echo "注意：Docker 数据库仍在运行"
echo "如需停止数据库，请运行:"
echo "  docker-compose down"
echo ""
