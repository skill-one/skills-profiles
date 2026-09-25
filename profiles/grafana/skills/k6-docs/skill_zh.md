# k6 文档

在三个仓库中编写或审查 k6 功能：k6-DefinitelyTyped（TypeScript 类型）、k6-docs（用户文档）和 k6（发布说明）。

## 工作流

选择与用户意图匹配的工作流：

- **编写文档**：遵循 [references/workflows/write.md](references/workflows/write.md)
- **审查文档**：遵循 [references/workflows/review.md](references/workflows/review.md)

## 快速参考

- [仓库结构 & 功能类型识别](references/repository-structure.md)
- [TypeScript 模式 & 故障排除](references/typescript-patterns.md)
- [使用并行子代理的测试工作流](references/testing-workflow.md)
- [agent-browser 命令参考](references/agent-browser-reference.md)
- [故障排除指南](references/troubleshooting.md)

## 严格规则

- **禁止自动推送** - 始终先询问
- **禁止使用 `&&` 或 `;` 链接命令** - 分别运行每个命令（防止失败）
- **仅记录面向用户的功能** - 不记录内部实现
- **编号列表项使用 `1.`**（不使用 `1.`, `2.`, `3.`）
- **在提交前对 k6@master 的每个代码示例进行测试**
- **提交中不得包含 `Co-Authored-By: Claude` 或 AI 归因**

## 验证示例（提交前始终运行）

k6 文档**和发布说明**中的每个代码示例都必须在 `k6@master` 上干净地执行。最小循环：

```bash
# 1. 进入 k6 仓库（不是 k6-docs 或 k6-DefinitelyTyped）
cd ~/path/to/k6

# 2. 确保你在最新的 master 提交上（合同是 k6@master）
git checkout master
git pull

# 3. 将每个示例作为单独的命令运行（无 &&）
go run . run /path/to/script.js
```

如果运行失败：阅读错误信息，在源代码（文档或发布说明）中修复示例，重新运行。不要提交示例在当前 `master` 上无法干净运行的更改。有关完整的多示例工作流（使用并行子代理），请参阅 [references/testing-workflow.md](references/testing-workflow.md)。
