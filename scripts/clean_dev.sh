#!/bin/bash

# 零钱管理系统开发环境清理脚本

echo "🧹 开始清理开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 清理Python缓存文件
echo "🐍 清理Python缓存文件..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# 清理测试覆盖率文件
echo "📊 清理测试覆盖率文件..."
rm -rf htmlcov/ .coverage .coverage.* 2>/dev/null || true

# 清理数据库文件（仅开发环境）
if [ "$1" = "--clean-db" ]; then
    echo "💾 清理数据库文件..."
    rm -f backend/database/cash_manager.db 2>/dev/null || true
    rm -f backend/database/test_*.db 2>/dev/null || true
fi

# 清理日志文件
echo "📝 清理日志文件..."
rm -f *.log 2>/dev/null || true
rm -rf logs/ 2>/dev/null || true

# 清理Docker临时文件
echo "🐳 清理Docker临时文件..."
docker system prune -f >/dev/null 2>&1 || true

echo -e "${GREEN}✅ 开发环境清理完成！${NC}"

if [ "$1" != "--clean-db" ]; then
    echo -e "${YELLOW}💡 提示: 如需清理数据库文件，请运行: $0 --clean-db${NC}"
fi

echo ""
echo "📋 常用开发命令:"
echo "  🚀 启动应用: python run.py"
echo "  🧪 运行测试: python -m pytest backend/test_*.py"
echo "  🔧 初始化数据库: python backend/database/init_db.py"
echo "  🐳 Docker启动: docker-compose up -d"