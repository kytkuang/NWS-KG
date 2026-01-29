#!/bin/bash

# 启动网站脚本
# 用于同时启动后端和前端服务

echo "=========================================="
echo "启动网络安全知识图谱学习系统"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend/my_vue_app"

# 检查目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    echo "错误: 后端目录不存在: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "错误: 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# 启动后端服务
echo ""
echo "正在启动后端服务..."
cd "$BACKEND_DIR"
python app.py &


# 等待后端启动
sleep 3

# 启动前端服务
echo ""
echo "正在启动前端服务..."
cd "$FRONTEND_DIR"

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "检测到未安装前端依赖，正在安装..."
    npm install
fi

npm run dev &


# 等待用户中断
wait
