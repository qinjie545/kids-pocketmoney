# Docker 部署指南

## 快速开始

### 1. 使用 docker-compose 启动服务

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 使用生产环境配置

```bash
# 设置环境变量（可选）
export SECRET_KEY=your-production-secret-key

# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d
```

## 常用命令

### 启动服务
```bash
docker-compose up -d
```

### 停止服务
```bash
docker-compose down
```

### 查看日志
```bash
docker-compose logs -f cash-manager
```

### 重启服务
```bash
docker-compose restart
```

### 查看服务状态
```bash
docker-compose ps
```

### 进入容器
```bash
docker-compose exec cash-manager bash
```

### 重建镜像
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 数据持久化

数据库文件存储在 `./backend/database` 目录中，通过 Docker volume 持久化。

## 环境变量

可以通过环境变量或 `.env` 文件配置：

- `SECRET_KEY`: Flask session密钥（生产环境必须修改）
- `PORT`: 服务端口（默认19754）
- `FLASK_ENV`: Flask环境（production/development）

## 健康检查

服务包含健康检查，可以通过以下命令查看：

```bash
docker-compose ps
```

## 访问服务

启动后访问：`http://localhost:19754`

默认用户：`admin` / `admin123`（首次启动自动创建）

## 注意事项

1. 生产环境请务必修改 `SECRET_KEY`
2. 数据库文件会自动持久化到 `./database` 目录
3. 定时任务调度器会在容器启动时自动启动
4. 建议使用 `docker-compose.prod.yml` 进行生产部署
