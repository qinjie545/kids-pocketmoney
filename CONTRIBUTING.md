# 贡献指南

感谢您对零钱管理系统项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎨 改进用户界面
- 🧪 添加测试用例

## 开发环境设置

### 1. 环境要求

- Python 3.8+
- pip (Python包管理器)

### 2. 克隆项目

```bash
git clone https://github.com/your-username/cash-manager.git
cd cash-manager
```

### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 初始化数据库

```bash
python database/init_db.py
```

### 6. 运行应用程序

```bash
python app.py
```

访问 `http://localhost:19754` 查看应用运行情况。

## 代码规范

### Python代码规范

我们遵循 [PEP 8](https://pep8.org/) Python代码规范。请确保您的代码：

- 使用4个空格进行缩进
- 行长度不超过88个字符
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

### 提交信息规范

提交信息应该清晰描述所做的更改：

```
类型: 简要描述

详细描述（如果需要）
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或工具配置更新

示例：
```
feat: 添加定时发放功能

- 支持每天/每周/每月发放
- 添加发放记录到数据库
- 更新用户界面
```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 编写测试

在修改代码之前，请先为您的功能编写测试用例：

```bash
# 运行现有测试
python -m pytest test_transactions.py -v

# 或使用unittest
python test_transactions.py
```

### 3. 实现功能

确保您的代码：
- 通过所有现有测试
- 添加新的测试用例
- 更新相关文档
- 遵循代码规范

### 4. 提交更改

```bash
# 添加文件
git add .

# 提交更改
git commit -m "feat: 您的功能描述"

# 推送到远程
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

1. 在GitHub上访问项目仓库
2. 点击 "New pull request"
3. 选择您的功能分支
4. 填写PR描述，包括：
   - 功能概述
   - 实现细节
   - 测试说明
   - 相关的issue链接

## 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest test_*.py -v

# 运行特定测试文件
python test_transactions.py

# 生成测试覆盖率报告
python -m pytest --cov=. --cov-report=html
```

### 编写测试

测试应该放在 `test_*.py` 文件中，使用 `unittest` 框架：

```python
import unittest
from your_module import your_function

class TestYourFunction(unittest.TestCase):
    def test_something(self):
        # 测试代码
        result = your_function(input_data)
        self.assertEqual(result, expected_output)
```

## 数据库更改

如果您的更改涉及数据库结构修改：

1. 更新 `database/schema.sql`
2. 创建相应的迁移脚本（如 `database/migrate_v1_to_v2.py`）
3. 测试迁移脚本
4. 更新文档

## 前端开发

### HTML/CSS/JavaScript

- 保持界面简洁，适合6-12岁儿童使用
- 避免使用外部CDN，使用原生JavaScript
- 确保响应式设计
- 使用年龄适宜的配色方案

### 图标和配色

- 收入：绿色 (#10b981)
- 支出：红色 (#ef4444)
- 余额：紫色 (#667eea)

## 报告问题

### Bug报告

请使用 [GitHub Issues](https://github.com/your-username/cash-manager/issues) 报告bug，并包含：

- 详细的错误描述
- 重现步骤
- 期望的行为
- 实际的行为
- 环境信息（操作系统、Python版本等）

### 功能请求

对于新功能请求，请描述：

- 功能的具体需求
- 为什么需要这个功能
- 可能的实现方式

## 行为准则

请阅读我们的 [行为准则](CODE_OF_CONDUCT.md)，确保您的贡献符合社区标准。

## 许可证

通过贡献代码，您同意您的贡献将根据项目的 [MIT许可证](LICENSE) 进行许可。

## 获取帮助

如果您在贡献过程中遇到问题：

1. 查看 [README.md](README.md) 获取基本信息
2. 查看 [CLAUDE.md](CLAUDE.md) 了解Agent工作规范
3. 在GitHub Issues中提问
4. 联系项目维护者

感谢您的贡献！🎉