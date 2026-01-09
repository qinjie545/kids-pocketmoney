# 使用官方Python运行时作为基础镜像
FROM python:3.14-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=19754

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/database /app/logs

# 暴露端口
EXPOSE 19754

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:19754/login || exit 1

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
echo "正在初始化数据库..."\n\
python database/init_db.py || echo "数据库已存在或初始化失败，继续启动..."\n\
echo "启动应用服务..."\n\
exec python app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]
