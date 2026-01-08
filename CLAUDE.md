# Cash Manager Agent 指引规范

## 项目概述
这是一个为6-12岁儿童设计的零钱管理系统，采用BS（Browser-Server）架构，使用Flask后端和SQLite3数据库。

## 项目结构
```
cash_manager/
├── app.py                    # Flask主应用程序
├── scheduler.py              # 定时任务调度器
├── generate_test_data.py     # 测试数据生成器
├── database/
│   ├── schema.sql           # 数据库表结构定义
│   ├── init_db.py           # 数据库初始化脚本
│   ├── migrate_db.py        # 数据库迁移脚本
│   └── cash_manager.db      # SQLite数据库文件
├── templates/
│   ├── login.html           # 登录页面
│   └── dashboard.html       # 主控制面板
└── venv/                     # Python虚拟环境
```

## Agent 工作规范

### 1. 代码修改后自动重启服务
**重要：每次修改以下文件后，必须自动重启Flask服务：**
- `app.py` - Flask主应用程序
- `scheduler.py` - 定时任务调度器
- `templates/` 目录下的任何HTML模板文件
- `database/` 目录下影响数据库结构的文件

**重启服务流程：**
```bash
# 1. 停止当前运行的服务（在端口5001）
lsof -ti:5001 | xargs kill -9

# 2. 重新启动服务
source venv/bin/activate && python app.py
```

### 2. 数据库修改规范
当修改数据库表结构时：
1. 先更新 `database/schema.sql` 文件
2. 创建相应的迁移脚本（如 `database/migrate_db.py`）
3. 运行迁移脚本更新现有数据库
4. 重启服务以使更改生效

### 3. 前端开发规范
- 避免使用外部CDN（如Chart.js），使用原生JavaScript实现功能
- 保持界面简洁，适合6-12岁儿童使用
- 使用年龄适宜的配色方案和交互设计
- 确保响应式设计，支持不同屏幕尺寸

### 4. 测试和验证
- 每次修改后验证功能是否正常工作
- 检查浏览器控制台是否有JavaScript错误
- 检查服务器日志是否有错误信息
- 对于涉及数据库的操作，验证数据是否正确存储和检索

### 5. 分类体系
系统使用不同的收入和支出分类：

**收入分类：**
- 零花钱
- 奖励
- 帮忙家务
- 红包
- 礼物
- 压岁钱
- 其他

**支出分类：**
- 零食
- 文具
- 玩具
- 游戏
- 书籍
- 娱乐
- 交通
- 礼物
- 捐款
- 其他

### 6. 定时发放功能
系统支持三种发放周期：
- 每天发放
- 每周发放（可选择星期一至星期日）
- 每月发放（可选择1号至28号）

### 7. 趋势图表
- 支持三种视图：余额变化、收入趋势、支出趋势
- 使用柱状图显示数据
- 不同数据类型使用不同颜色：
  - 余额：紫色 (#667eea)
  - 收入：绿色 (#10b981)
  - 支出：红色 (#ef4444)

### 8. 错误处理
- 前端错误：显示用户友好的错误消息
- 后端错误：记录到服务器日志，返回适当的HTTP状态码
- 数据库错误：回滚事务，显示错误消息

## 服务管理
- 默认端口：5001
- 访问地址：http://127.0.0.1:5001
- 默认用户：admin/admin123
- 调试模式：已启用

## 常用命令
```bash
# 启动服务
source venv/bin/activate && python app.py

# 停止服务
lsof -ti:5001 | xargs kill -9

# 生成测试数据
python generate_test_data.py

# 初始化数据库
python database/init_db.py

# 运行数据库迁移
python database/migrate_db.py
```

## 开发注意事项
1. 修改后总是记得重启服务
2. 测试所有受影响的功能
3. 检查浏览器和服务器日志
4. 保持代码简洁和可维护性
5. 遵循现有的代码风格和结构
