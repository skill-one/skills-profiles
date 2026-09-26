# 归档技能

跨会话捕获、索引和重用项目知识。

## 何时归档

- 完成重要任务后（部署、迁移、主要功能）
- 解决棘手的调试会话后
- 当用户说“归档这个”时
- 任何包含值得保留的学习成果的多步骤流程后

## 何时查阅归档

- 调试基础设施、部署或 CI 问题前
- 重复过去会话中执行过的流程前
- 遇到可能之前已解决的问题的错误时

**搜索**：`grep -ri "关键词" .archive/`
**索引**：`.archive/MEMORY.md`

## 归档工作流程

1. 阅读 `.archive/MEMORY.md` — 检查相关现有归档
2. 如有需要，创建 `.archive/年-月-日/` 目录
3. 使用 YAML 前置文本（参考 `references/TEMPLATE.md`）编写 Markdown 文件
4. **更新 `.archive/MEMORY.md`**：在正确分类下添加一行条目
5. 如存在相关归档，在前置文本中添加 `related` 字段

## 查阅工作流程

1. 阅读 `.archive/MEMORY.md` 找到相关条目
2. 阅读特定归档文件获取详细上下文
3. 将学习成果应用于当前任务

## 分类

- **基础设施** — AWS、ECS、IAM、网络、密钥、CloudWatch
- **发布** — TestFlight、版本控制、Git Flow、CHANGELOG
- **调试** — Bug 修复、错误解决、注意事项
- **功能** — 功能设计、实现笔记
- **设计** — UI/UX、图标、视觉设计

## 规则

- `.archive/` 必须在 `.gitignore` 中 — 仅本地笔记
- 保持条目简洁但可复现
- 聚焦于 **问题、解决方案和精确命令**
- 创建归档后始终更新 MEMORY.md
- 使用描述性文件名（例如 `cloudwatch-logging.md` 而不是 `session.md`）
- 包含带有 `tags`、`category` 和可选 `related` 的 YAML 前置文本
