#!/bin/bash

# 零钱管理系统 Docker 启动脚本

echo "=========================================="
echo "  零钱管理系统 Docker 部署"
echo "=========================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker，请先安装 Docker"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: 未安装 docker-compose，请先安装 docker-compose"
    exit 1
fi

# 创建必要的目录
mkdir -p database logs

# 检查是否使用生产配置
if [ "$1" == "prod" ]; then
    echo "📦 使用生产环境配置启动..."
    docker-compose -f docker-compose.prod.yml up -d --build
else
    echo "📦 使用开发环境配置启动..."
    docker-compose up -d --build
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🌐 访问地址: http://localhost:19754"
    echo "👤 默认账号: admin / admin123"
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
else
    echo "❌ 服务启动失败，请查看日志: docker-compose logs"
    exit 1
fi
