#!/usr/bin/env python3
"""
社区建设工作流工具

用于自动化社区管理任务，包括：
- 贡献者统计和报告
- Issue和PR管理
- 社区活动组织
- 文档维护
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class CommunityWorkflow:
    """社区建设工作流管理器"""

    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or Path(__file__).parent.parent

    def run_contribution_analysis(self) -> Dict[str, Any]:
        """运行贡献分析"""
        print("📊 分析项目贡献情况...")

        try:
            # 获取Git统计
            result = subprocess.run(
                ["git", "log", "--pretty=format:'%an,%ae,%ad'", "--date=short", "--since='2026-01-01'"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = result.stdout.strip().split('\n')
            contributors = {}

            for commit in commits:
                if commit.strip():
                    parts = commit.strip("'").split(',')
                    if len(parts) >= 2:
                        name = parts[0]
                        email = parts[1] if len(parts) > 1 else ""
                        date = parts[2] if len(parts) > 2 else ""

                        if name not in contributors:
                            contributors[name] = {
                                "name": name,
                                "email": email,
                                "commits": 0,
                                "first_commit": date,
                                "last_commit": date
                            }

                        contributors[name]["commits"] += 1
                        if date < contributors[name]["first_commit"]:
                            contributors[name]["first_commit"] = date
                        if date > contributors[name]["last_commit"]:
                            contributors[name]["last_commit"] = date

            return {
                "total_contributors": len(contributors),
                "total_commits": len(commits),
                "contributors": list(contributors.values()),
                "analysis_date": datetime.now().isoformat()
            }

        except subprocess.CalledProcessError:
            return {"error": "无法获取Git统计信息"}

    def check_community_health(self) -> Dict[str, Any]:
        """检查社区健康状况"""
        print("🏥 检查社区健康状况...")

        health_score = 0
        checks = {}

        # 检查文档完整性
        docs_exist = [
            "README.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "COMMUNITY.md",
            "SECURITY.md"
        ]

        docs_score = 0
        for doc in docs_exist:
            if (self.repo_path / doc).exists():
                docs_score += 20
                checks[f"文档_{doc}"] = "✅ 存在"
            else:
                checks[f"文档_{doc}"] = "❌ 缺失"

        health_score += docs_score * 0.3

        # 检查国际化支持
        i18n_score = 0
        translations_dir = self.repo_path / "backend" / "translations"
        if translations_dir.exists():
            lang_dirs = [d for d in translations_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
            i18n_score = min(len(lang_dirs) * 25, 100)
            checks["国际化支持"] = f"✅ 支持 {len(lang_dirs)} 种语言"
        else:
            checks["国际化支持"] = "❌ 无国际化支持"

        health_score += i18n_score * 0.2

        # 检查测试覆盖
        test_files = list(self.repo_path.glob("**/test_*.py"))
        if test_files:
            checks["测试覆盖"] = f"✅ 发现 {len(test_files)} 个测试文件"
            health_score += 80 * 0.2
        else:
            checks["测试覆盖"] = "❌ 无测试文件"
            health_score += 0

        # 检查CI/CD
        ci_files = list(self.repo_path.glob(".github/workflows/*.yml"))
        if ci_files:
            checks["CI/CD"] = f"✅ 配置了 {len(ci_files)} 个工作流"
            health_score += 100 * 0.15
        else:
            checks["CI/CD"] = "❌ 无CI/CD配置"
            health_score += 0

        # 检查问题模板
        issue_templates = list(self.repo_path.glob(".github/ISSUE_TEMPLATES/*.md"))
        if issue_templates:
            checks["问题模板"] = f"✅ 配置了 {len(issue_templates)} 个模板"
            health_score += 100 * 0.15
        else:
            checks["问题模板"] = "❌ 无问题模板"
            health_score += 0

        return {
            "health_score": round(health_score, 1),
            "checks": checks,
            "recommendations": self.generate_recommendations(checks)
        }

    def generate_recommendations(self, checks: Dict[str, str]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if "❌" in checks.get("文档_README.md", ""):
            recommendations.append("📝 创建项目README.md文件")

        if "❌" in checks.get("文档_CONTRIBUTING.md", ""):
            recommendations.append("🤝 创建CONTRIBUTING.md贡献指南")

        if "❌" in checks.get("国际化支持", ""):
            recommendations.append("🌐 添加多语言支持")

        if "❌" in checks.get("测试覆盖", ""):
            recommendations.append("🧪 添加单元测试")

        if "❌" in checks.get("CI/CD", ""):
            recommendations.append("⚙️ 配置GitHub Actions CI/CD")

        if "❌" in checks.get("问题模板", ""):
            recommendations.append("📋 创建Issue和PR模板")

        return recommendations

    def organize_community_event(self, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """组织社区活动"""
        print(f"🎉 组织社区活动: {event_type}")

        events = {
            "code_quality_week": {
                "title": "代码质量改善周",
                "duration": "7天",
                "goals": ["代码重构", "测试覆盖提升", "性能优化"],
                "participants": "所有贡献者"
            },
            "documentation_month": {
                "title": "文档完善月",
                "duration": "30天",
                "goals": ["文档更新", "教程编写", "国际化"],
                "participants": "文档贡献者"
            },
            "feature_development_season": {
                "title": "功能开发季",
                "duration": "90天",
                "goals": ["新功能开发", "用户体验改进", "技术债务清理"],
                "participants": "开发者"
            }
        }

        if event_type in events:
            event = events[event_type].copy()
            event.update(details)
            event["created_at"] = datetime.now().isoformat()
            event["status"] = "planned"

            return event
        else:
            return {"error": f"未知活动类型: {event_type}"}

    def generate_monthly_report(self) -> Dict[str, Any]:
        """生成月度社区报告"""
        print("📈 生成月度社区报告...")

        contribution_data = self.run_contribution_analysis()
        health_data = self.check_community_health()

        report = {
            "report_type": "monthly_community_report",
            "generated_at": datetime.now().isoformat(),
            "period": f"{datetime.now().strftime('%Y-%m')}",
            "contribution_stats": contribution_data,
            "community_health": health_data,
            "achievements": [],
            "challenges": [],
            "next_month_goals": []
        }

        # 分析成就
        if contribution_data.get("total_contributors", 0) > 0:
            report["achievements"].append(f"社区有 {contribution_data['total_contributors']} 位活跃贡献者")

        if health_data.get("health_score", 0) > 80:
            report["achievements"].append("社区健康度良好")

        # 分析挑战
        recommendations = health_data.get("recommendations", [])
        report["challenges"].extend(recommendations)

        return report

    def print_report(self, report: Dict[str, Any]) -> None:
        """打印报告"""
        print("\n" + "="*60)
        print("📊 社区建设工作流报告")
        print("="*60)

        if "contribution_stats" in report:
            stats = report["contribution_stats"]
            print(f"👥 贡献者数量: {stats.get('total_contributors', 0)}")
            print(f"📝 总提交数: {stats.get('total_commits', 0)}")

        if "community_health" in report:
            health = report["community_health"]
            print(f"🏥 社区健康度: {health.get('health_score', 0)}/100")

            print("\n🔍 健康检查结果:")
            for check, status in health.get("checks", {}).items():
                print(f"  {status}")

        if report.get("recommendations"):
            print("\n💡 改进建议:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")

        print("="*60)


def main():
    """主函数"""
    workflow = CommunityWorkflow()

    print("🚀 社区建设工作流工具")
    print("=" * 50)

    # 运行贡献分析
    contribution_data = workflow.run_contribution_analysis()
    print(f"📊 贡献分析完成: {contribution_data.get('total_contributors', 0)} 位贡献者")

    # 检查社区健康
    health_data = workflow.check_community_health()
    print(f"🏥 健康检查完成: {health_data.get('health_score', 0)} 分")

    # 生成月度报告
    monthly_report = workflow.generate_monthly_report()

    # 打印综合报告
    workflow.print_report(monthly_report)

    # 保存报告
    report_file = workflow.repo_path / "COMMUNITY_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(monthly_report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 报告已保存到: {report_file}")


if __name__ == "__main__":
    main()