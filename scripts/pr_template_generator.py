#!/usr/bin/env python3
"""
PR模板生成器

用于生成标准化的Pull Request描述模板，帮助贡献者更好地描述他们的更改。
"""

import os
from pathlib import Path
from typing import Dict, List


class PRTemplateGenerator:
    """PR模板生成器"""

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or Path(__file__).parent.parent

    def get_recent_changes(self) -> List[str]:
        """获取最近的更改"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')
        except:
            return []

    def get_changed_files(self) -> List[str]:
        """获取更改的文件"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')
        except:
            return []

    def categorize_changes(self, changed_files: List[str]) -> Dict[str, List[str]]:
        """对更改进行分类"""
        categories = {
            "frontend": [],
            "backend": [],
            "docs": [],
            "config": [],
            "tests": [],
            "scripts": []
        }

        for file in changed_files:
            if file.startswith("frontend/") or file.endswith((".html", ".css", ".js")):
                categories["frontend"].append(file)
            elif file.startswith("backend/") or file.endswith((".py", ".sql")):
                categories["backend"].append(file)
            elif file.endswith((".md", ".rst", ".txt")) or file in ["README.md", "CHANGELOG.md"]:
                categories["docs"].append(file)
            elif file.endswith((".yml", ".yaml", ".json", ".toml")) or "config" in file:
                categories["config"].append(file)
            elif "test" in file or file.startswith("tests/"):
                categories["tests"].append(file)
            elif file.startswith("scripts/"):
                categories["scripts"].append(file)

        return categories

    def generate_pr_template(self, pr_type: str = "feature") -> str:
        """生成PR模板"""
        template = f"""## 📝 描述

请简要描述这个PR做了什么。

## 🔗 相关问题

这个PR解决了哪些问题？请链接相关issues。

- 解决的问题: #

## ✨ 变更类型

请标记适用的变更类型：

- [ ] 🐛 Bug修复
- [ ] ✨ 新功能
- [ ] 💥 破坏性变更
- [ ] 📝 文档更新
- [ ] 🎨 代码样式更新
- [ ] ♻️ 重构
- [ ] ⚡ 性能优化
- [ ] ✅ 测试添加/更新
- [ ] 🔧 构建工具更新
- [ ] 🔒 安全更新

## 📋 检查清单

- [ ] 我的代码遵循项目的代码规范
- [ ] 我已经添加了必要的测试
- [ ] 所有测试都通过了
- [ ] 我已经更新了相关文档
- [ ] 这个变更不会破坏现有功能
- [ ] 我已经检查了我的代码，没有安全漏洞

## 🧪 测试

请描述如何测试这个变更：

1. 运行命令 `...`
2. 访问页面 `...`
3. 验证功能 `...`

## 📸 截图（如果适用）

添加截图来展示UI变更。

## 🔍 其他信息

在此添加任何其他相关信息或上下文。
"""

        return template

    def generate_issue_template(self, issue_type: str = "bug") -> str:
        """生成Issue模板"""
        if issue_type == "bug":
            template = """## 🐛 Bug描述

请清晰简洁地描述这个bug是什么。

## 🔄 重现步骤

请提供重现这个bug的步骤：

1. 转到 '...'
2. 点击 '....'
3. 向下滚动到 '....'
4. 看到错误

## 📸 截图

如果适用，请添加截图来帮助解释您的问题。

## 🖥️ 环境信息

- **操作系统**: [例如 Windows 10, macOS 12.1, Ubuntu 20.04]
- **浏览器**: [例如 Chrome 91, Firefox 89, Safari 14]
- **Python版本**: [例如 Python 3.9.7]
- **项目版本**: [例如 v1.0.0]

## 📋 期望行为

请描述您期望发生的事情。

## 📝 实际行为

请描述实际发生的事情。

## 📄 附加信息

在此添加关于这个问题的任何其他信息，如：
- 浏览器控制台错误信息
- 服务器日志错误
- 相关配置信息
- 可能的解决方案
"""
        elif issue_type == "feature":
            template = """## ✨ 功能描述

请清晰简洁地描述您想要的功能。

## 🎯 问题陈述

这个功能解决了什么问题？为什么需要这个功能？

## 💡 建议的解决方案

请描述您希望如何实现这个功能。

## 🔄 替代方案

您考虑过哪些替代方案？

## 📋 附加信息

在此添加关于这个功能请求的任何其他信息，如：
- 相关截图或mockups
- 参考资料或类似功能
- 技术实现考虑
- 用户影响评估

## ✅ 验收标准

这个功能何时算完成？请列出验收标准：

- [ ] 可以做这个
- [ ] 可以做那个
- [ ] 满足这些条件
"""
        else:
            template = "请选择正确的issue类型：bug 或 feature"

        return template

    def create_pr_description_helper(self) -> str:
        """创建PR描述助手"""
        changed_files = self.get_changed_files()
        categories = self.categorize_changes(changed_files)

        helper_text = "## 🤖 PR描述助手\n\n"
        helper_text += "根据您的更改，建议的PR类型和检查项目：\n\n"

        # 建议变更类型
        if categories["frontend"]:
            helper_text += "- [x] 🎨 前端UI变更\n"
        if categories["backend"]:
            helper_text += "- [x] ⚙️ 后端功能变更\n"
        if categories["tests"]:
            helper_text += "- [x] ✅ 测试添加/更新\n"
        if categories["docs"]:
            helper_text += "- [x] 📝 文档更新\n"
        if categories["config"]:
            helper_text += "- [x] 🔧 配置变更\n"

        # 建议检查项目
        helper_text += "\n### 建议检查项目：\n"
        if categories["backend"]:
            helper_text += "- [ ] 运行 `python -m pytest backend/test_*.py`\n"
        if categories["frontend"]:
            helper_text += "- [ ] 检查浏览器控制台无错误\n"
        if categories["docs"]:
            helper_text += "- [ ] 验证所有链接有效\n"

        helper_text += "\n### 更改的文件：\n"
        for category, files in categories.items():
            if files:
                helper_text += f"- **{category}**: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}\n"

        return helper_text


def main():
    """主函数"""
    generator = PRTemplateGenerator()

    print("🚀 PR模板生成器")
    print("=" * 50)

    # 生成PR描述助手
    helper = generator.create_pr_description_helper()
    print(helper)

    print("\n📋 标准PR模板:")
    print("-" * 30)
    pr_template = generator.generate_pr_template()
    print(pr_template)

    print("\n🐛 Bug Issue模板:")
    print("-" * 30)
    bug_template = generator.generate_issue_template("bug")
    print(bug_template)

    print("\n✨ 功能请求Issue模板:")
    print("-" * 30)
    feature_template = generator.generate_issue_template("feature")
    print(feature_template)


if __name__ == "__main__":
    main()