#!/usr/bin/env python3
"""
贡献者跟踪工具

用于跟踪和管理项目贡献者信息，包括：
- 贡献者统计
- 贡献类型分析
- 贡献者排名
- 贡献历史记录
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


class ContributionTracker:
    """贡献者跟踪器"""

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or Path(__file__).parent.parent
        self.contributors_file = self.repo_path / "CONTRIBUTORS.json"

    def get_git_contributors(self) -> List[Dict]:
        """获取Git贡献者信息"""
        try:
            # 获取贡献者统计
            result = subprocess.run(
                ["git", "shortlog", "-sn", "--no-merges"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            contributors = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        commits = int(parts[0])
                        name = parts[1]
                        contributors.append({
                            "name": name,
                            "commits": commits,
                            "type": "core_contributor"
                        })

            return contributors

        except subprocess.CalledProcessError:
            return []

    def get_issue_contributors(self) -> List[Dict]:
        """获取Issues贡献者（手动维护）"""
        # 这里可以集成GitHub API来获取issues贡献者
        # 目前返回空列表，需要手动维护
        return []

    def get_translation_contributors(self) -> List[Dict]:
        """获取翻译贡献者"""
        translation_contributors = []

        # 检查翻译文件
        translations_dir = self.repo_path / "backend" / "translations"
        if translations_dir.exists():
            for lang_dir in translations_dir.iterdir():
                if lang_dir.is_dir() and lang_dir.name != "__pycache__":
                    po_file = lang_dir / "LC_MESSAGES" / "messages.po"
                    if po_file.exists():
                        try:
                            with open(po_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # 查找翻译者信息
                                if "Last-Translator:" in content:
                                    # 这里可以解析翻译者信息
                                    pass
                        except:
                            pass

        return translation_contributors

    def generate_contributors_report(self) -> Dict:
        """生成贡献者报告"""
        git_contributors = self.get_git_contributors()
        issue_contributors = self.get_issue_contributors()
        translation_contributors = self.get_translation_contributors()

        # 合并所有贡献者
        all_contributors = git_contributors + issue_contributors + translation_contributors

        # 去重和合并
        contributors_dict = {}
        for contributor in all_contributors:
            name = contributor["name"]
            if name not in contributors_dict:
                contributors_dict[name] = contributor.copy()
            else:
                # 合并贡献
                existing = contributors_dict[name]
                existing["commits"] = existing.get("commits", 0) + contributor.get("commits", 0)
                # 合并类型
                types = set(existing.get("types", [existing.get("type", "contributor")]))
                types.add(contributor.get("type", "contributor"))
                existing["types"] = list(types)

        contributors = list(contributors_dict.values())

        # 按提交数排序
        contributors.sort(key=lambda x: x.get("commits", 0), reverse=True)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_contributors": len(contributors),
            "contributors": contributors,
            "stats": {
                "core_contributors": len([c for c in contributors if c.get("type") == "core_contributor"]),
                "total_commits": sum(c.get("commits", 0) for c in contributors)
            }
        }

        return report

    def save_contributors_report(self, report: Dict = None) -> None:
        """保存贡献者报告"""
        if report is None:
            report = self.generate_contributors_report()

        with open(self.contributors_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def load_contributors_report(self) -> Dict:
        """加载贡献者报告"""
        if self.contributors_file.exists():
            with open(self.contributors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def print_report(self, report: Dict = None) -> None:
        """打印贡献者报告"""
        if report is None:
            report = self.generate_contributors_report()

        print("🚀 零钱管理系统 - 贡献者报告")
        print("=" * 50)
        print(f"📊 生成时间: {report['generated_at']}")
        print(f"👥 总贡献者: {report['total_contributors']}")
        print(f"📝 总提交数: {report['stats']['total_commits']}")
        print(f"⭐ 核心贡献者: {report['stats']['core_contributors']}")
        print()

        print("🏆 贡献者排名:")
        print("-" * 30)
        for i, contributor in enumerate(report['contributors'][:10], 1):
            name = contributor['name']
            commits = contributor.get('commits', 0)
            types = contributor.get('types', [contributor.get('type', 'contributor')])
            type_str = ', '.join(types)
            print("2d"
        if len(report['contributors']) > 10:
            print(f"  ... 还有 {len(report['contributors']) - 10} 位贡献者")


def main():
    """主函数"""
    tracker = ContributionTracker()

    # 生成报告
    report = tracker.generate_contributors_report()

    # 保存报告
    tracker.save_contributors_report(report)

    # 打印报告
    tracker.print_report(report)


if __name__ == "__main__":
    main()