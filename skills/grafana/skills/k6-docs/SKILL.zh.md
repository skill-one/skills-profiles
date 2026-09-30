---
name: k6-docs
description: 编写或审阅 k6 文档，覆盖三个 k6 仓库：k6-DefinitelyTyped（TypeScript 类型）、k6-docs（用户文档）和 k6（版本说明/变更日志）。应用 k6 文档风格规范，生成 TypeScript 类型定义，起草版本说明，并通过在 k6@master 上运行来验证示例。在处理 k6 文档、k6 变更日志、k6 版本说明、k6 API 参考、k6 TypeScript 类型、负载测试文档，或用户要求编写、编辑或审阅 k6、k6-docs 或 k6-DefinitelyTyped 仓库中的任何内容时使用（即使他们没有明确说明“文档”）。
---

# k6 文档

跨三个仓库（k6-DefinitelyTyped（TypeScript类型）、k6-docs（用户文档）和k6（发布说明））编写或审查k6功能。

## 工作流

选择与用户意图匹配的工作流：

- **编写文档**：遵循 [references/workflows/write.md](references/workflows/write.md)
- **审查文档**：遵循 [references/workflows/review.md](references/workflows/review.md)

## 快速参考

- [仓库结构 & 功能类型识别](references/repository-structure.md)
- [TypeScript模式 & 故障排除](references/typescript-patterns.md)
- [使用并行子代理的测试工作流](references/testing-workflow.md)
- [agent-browser命令参考](references/agent-browser-reference.md)
- [故障排除指南](references/troubleshooting.md)

## 严格规则

- **禁止自动推送** - 始终先询问
- **禁止使用`&&`或`;`链式命令** - 分别运行每个命令（防止失败）
- **仅记录面向用户的功能** - 不记录内部实现
- **编号列表项使用`1.`（不使用`1.`, `2.`, `3.`）**
- **在提交前，使用k6@master测试每个代码示例**
- **提交中禁止包含`Co-Authored-By: Claude`或AI署名**

## 验证示例（提交前必须运行）

k6文档**和**发布说明中的每个代码示例都必须在`k6@master`上干净执行。最小循环：

```bash
# 1. 进入k6仓库（不是k6-docs或k6-DefinitelyTyped）
cd ~/path/to/k6

# 2. 确保你在最新的master提交上（契约是k6@master）
git checkout master
git pull

# 3. 将每个示例作为单独命令运行（不使用&&）
go run . run /path/to/script.js
```

如果运行失败：阅读错误信息，在源代码（文档或发布说明）中修复示例，重新运行。不要提交示例在当前`master`上无法干净运行的更改。有关使用并行子代理的完整多示例工作流，请参阅 [references/testing-workflow.md](references/testing-workflow.md)。
