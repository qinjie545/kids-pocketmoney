#!/usr/bin/env python3
"""
版本管理脚本

用于自动更新项目版本号，支持以下格式：
- patch: 修复bug (1.0.0 -> 1.0.1)
- minor: 新功能，向后兼容 (1.0.0 -> 1.1.0)
- major: 破坏性变更 (1.0.0 -> 2.0.0)

使用方法:
python scripts/bump_version.py patch
python scripts/bump_version.py minor
python scripts/bump_version.py major
"""

import re
import sys
from pathlib import Path


def read_version():
    """从pyproject.toml读取当前版本"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        raise ValueError("无法在pyproject.toml中找到版本号")


def write_version(new_version):
    """更新pyproject.toml中的版本号"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新version字段
    content = re.sub(
        r'^(version\s*=\s*)"[^"]*"',
        rf'\1"{new_version}"',
        content,
        flags=re.MULTILINE
    )

    with open(pyproject_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 更新pyproject.toml版本为: {new_version}")


def update_setup_py(new_version):
    """更新setup.py中的版本号"""
    setup_path = Path(__file__).parent.parent / "setup.py"
    if not setup_path.exists():
        return

    with open(setup_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新version字段
    content = re.sub(
        r'^(    version=)"[^"]*"',
        rf'\1"{new_version}"',
        content,
        flags=re.MULTILINE
    )

    with open(setup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 更新setup.py版本为: {new_version}")


def update_changelog(new_version):
    """在CHANGELOG.md中添加新版本条目"""
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找第一个版本标题
    match = re.search(r'^## \[([^\]]+)\]', content, re.MULTILINE)
    if match:
        current_version = match.group(1)
        today = Path(__file__).parent.parent.joinpath('.git').exists()
        if today:
            # 如果在git仓库中，尝试获取当前日期
            import subprocess
            try:
                date_str = subprocess.check_output(
                    ['git', 'log', '-1', '--format=%cd', '--date=short'],
                    cwd=Path(__file__).parent.parent
                ).decode().strip()
            except:
                from datetime import datetime
                date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y-%m-%d')

        # 插入新版本条目
        new_entry = f"""## [{new_version}] - {date_str}

### ✨ 新增功能

### 🐛 修复

### 📝 文档

### 🔧 技术改进

"""
        # 在第一个版本条目前插入新条目
        insert_pos = content.find(f'## [{current_version}]')
        content = content[:insert_pos] + new_entry + '\n' + content[insert_pos:]

        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 在CHANGELOG.md中添加新版本条目: {new_version}")


def bump_version(version_type):
    """执行版本递增"""
    current_version = read_version()
    print(f"📋 当前版本: {current_version}")

    # 解析版本号
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', current_version)
    if not match:
        raise ValueError(f"无效的版本号格式: {current_version}")

    major, minor, patch = map(int, match.groups())

    # 根据类型递增版本
    if version_type == 'patch':
        patch += 1
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"无效的版本类型: {version_type}。必须是 'patch', 'minor' 或 'major'")

    new_version = f"{major}.{minor}.{patch}"
    print(f"🔄 新版本: {new_version}")

    # 更新文件
    write_version(new_version)
    update_setup_py(new_version)
    update_changelog(new_version)

    print("
🎉 版本更新完成！"    print(f"📝 请手动更新CHANGELOG.md中的新版本条目内容")
    print(f"🏷️  创建Git标签: git tag -a v{new_version} -m 'Release version {new_version}'")
    print(f"📤 推送标签: git push origin v{new_version}")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python scripts/bump_version.py <patch|minor|major>")
        print("示例:")
        print("  python scripts/bump_version.py patch  # 1.0.0 -> 1.0.1")
        print("  python scripts/bump_version.py minor  # 1.0.0 -> 1.1.0")
        print("  python scripts/bump_version.py major  # 1.0.0 -> 2.0.0")
        sys.exit(1)

    version_type = sys.argv[1].lower()
    if version_type not in ['patch', 'minor', 'major']:
        print(f"❌ 无效的版本类型: {version_type}")
        print("必须是 'patch', 'minor' 或 'major'")
        sys.exit(1)

    try:
        bump_version(version_type)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()