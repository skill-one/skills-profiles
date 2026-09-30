---
name: visual-pr
description: 仅在用户明确调用此技能时使用。
---

# 描述一个拉取请求

为当前任务创建或更新拉取请求，使用简洁的描述帮助审查者理解变更的原因以及实现的概要。

## 工作流程

1. 读取描述模板：

   `Read({SKILLBASE}/references/pr_description_template.md)`

2. 识别或创建拉取请求：
   - 使用 `gh pr view --json url,number,title,state,baseRefName,headRefName 2>/dev/null` 检查当前分支是否存在拉取请求。
   - 如果不存在拉取请求，检查 `git status --short --branch` 以及当前分支上的提交记录。
   - 当需要时提交与任务相关的变更，推送带有上游的分支，并为其创建拉取请求。遵循仓库的 git 安全协议。
   - 只有在当前分支没有相关工作且无法创建安全的当前分支拉取请求时，才要求用户选择拉取请求。

3. 收集解释变更所需的上下文：
   - 读取工单以及任何相关的任务工件。
   - 读取完整的拉取请求差异以及足够的周边代码以理解行为和所有权。
   - 使用 `gh pr view` 收集拉取请求元数据和已更改文件。
   - 读取 `{SKILLBASE}/references/show-me.md` 了解拉取请求正文中使用的视觉轮廓约定。

4. 使用模板编写拉取请求描述：
   - 将 **变更原因** 保持为一句。
   - 将 **需要特别注意的事项** 保持为 1-3 个要点。优先考虑审查者警告、迁移、兼容性限制、故意省略或令人惊讶的决策。当没有特殊考虑时，写 `- None.`。
   - 将 **变更概要** 制作为一个紧凑的、受 `/show-me` 启发的结构化视图，而不是散文或按文件记录的变更日志。
   - 仅包含有助于解释此拉取请求的视图：
     - SQL 表和端点契约变更，以及业务逻辑的伪代码。
     - 关键数据结构/类型变更
     - 显示变更责任关系的浅层文件树。
     - React 组件树变更，包括重要的钩子、状态和包边界。
     - 调用树、调用栈、控制流或数据流变更。
   - 当显示对现有结构的变更时，优先使用 `diff` 块。当大部分内容是新的或差异表示会掩盖所有权或顺序时，显示完整的目标形状。
   - 保持每个视图专注于审查者需要的内容。省略未变更的类别。
   - 可选：如果你知道工单 ID/URL、humanlayer 任务 URL 或相关计划/文档 URL 或其他相关链接，请在标题中包含它们，否则省略标题。

5. 保存并发布描述：
   - 当任务目录存在时，使用 `.humanlayer/tasks/{task-slug}/pr-description.md`；否则使用 `.humanlayer/tasks/pr-{number}/description.md`。
   - 使用 `gh pr edit {number} --body-file {output-path}` 更新拉取请求。
   - 确认更新成功。

6. 报告完成：
   - 读取 `{SKILLBASE}/references/describe_pr_final_answer.md`。
   - 使用该最终答案模板并以拉取请求 URL、保存的描述 URL 以及变更文件列表的简洁形式进行响应。

始终读取并遵循 `{SKILLBASE}/references/pr_description_template.md`。不要扩展拉取请求正文超出该模板。

像人类对人类说话一样写：避免行话和俚语，使用简单、连贯、简洁的语言。
