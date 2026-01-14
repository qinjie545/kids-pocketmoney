# 发布前检查清单

在发布新版本之前，请确保以下所有项目都已完成：

## 📋 代码质量检查

- [ ] 所有测试通过 (`python -m pytest`)
- [ ] 代码格式正确 (`black --check .` && `isort --check-only .`)
- [ ] 代码质量检查通过 (`flake8`)
- [ ] 测试覆盖率达标 (>80%)
- [ ] 没有安全漏洞 (`bandit` 或手动检查)

## 📝 文档更新

- [ ] 更新CHANGELOG.md中的新版本条目
- [ ] 更新README.md中的版本信息（如适用）
- [ ] 确认所有文档链接有效
- [ ] 更新API文档（如适用）

## 🔧 配置检查

- [ ] pyproject.toml中的版本号已更新
- [ ] setup.py中的版本号已同步（如适用）
- [ ] Docker镜像标签正确
- [ ] CI/CD配置正确

## 🧪 集成测试

- [ ] Docker构建成功
- [ ] Docker容器运行正常
- [ ] 数据库迁移测试通过
- [ ] 端到端测试通过

## 🔒 安全检查

- [ ] 没有硬编码的敏感信息
- [ ] 依赖版本安全（无已知漏洞）
- [ ] 默认配置安全
- [ ] 密码处理安全

## 🚀 发布准备

- [ ] 创建Git标签 (`git tag -a v1.0.0 -m "Release version 1.0.0"`)
- [ ] 推送到主分支 (`git push origin main`)
- [ ] 推送标签 (`git push origin v1.0.0`)
- [ ] 验证GitHub Actions工作流运行成功

## 📦 包发布

- [ ] PyPI发布成功
- [ ] Docker镜像推送成功
- [ ] GitHub Release创建成功

## 📢 发布后

- [ ] 在项目Issues中关闭相关milestone
- [ ] 通知社区（如论坛、社交媒体）
- [ ] 监控发布后的问题报告
- [ ] 准备下一个开发周期

---

## 快速发布命令

```bash
# 1. 运行完整测试套件
python -m pytest --cov=. --cov-report=html

# 2. 代码质量检查
black --check .
isort --check-only .
flake8

# 3. 更新版本号
python scripts/bump_version.py patch  # 或 minor/major

# 4. 手动更新CHANGELOG.md

# 5. 提交更改
git add .
git commit -m "chore: release version x.y.z"

# 6. 创建标签并推送
git tag -a vx.y.z -m "Release version x.y.z"
git push origin main
git push origin vx.y.z

# 7. 验证发布
# 检查GitHub Actions状态
# 验证PyPI发布
# 验证Docker镜像
```

## 🔄 回滚计划

如果发布出现问题：

1. **PyPI回滚**: 删除有问题的版本（如果可能）
2. **Git回滚**: 删除错误的标签 `git tag -d vx.y.z && git push origin :refs/tags/vx.y.z`
3. **Docker回滚**: 使用之前的镜像标签
4. **用户通知**: 通知用户避免使用有问题的版本

## 📞 紧急联系人

- 项目维护者: [维护者邮箱]
- 安全问题: [安全邮箱]
- 基础设施: [基础设施联系人]