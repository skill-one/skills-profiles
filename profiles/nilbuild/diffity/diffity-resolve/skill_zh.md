# Diffity Resolve Skill

您正在阅读公开的评审评论，并通过执行请求的代码更改来解决问题。

## 参数

- `thread-id` (可选): 通过 ID 解决特定线程，而不是所有打开的线程。示例：`/diffity-resolve abc123`

## 命令行参考

```
diffity agent diff
diffity agent list [--status open|resolved|dismissed] [--json]
diffity agent comment --file <路径> --line <n> [--end-line <n>] [--side new|old] --body "<文本>"
diffity agent general-comment --body "<文本>"
diffity agent resolve <id> [--summary "<文本>"]
diffity agent dismiss <id> [--reason "<文本>"]
diffity agent reply <id> --body "<文本>"
```

- `--file`, `--line`, `--body` 是 `comment` 命令必需的
- `--end-line` 默认为 `--line` (单行评论)
- `--side` 默认为 `new`
- `general-comment` 创建一个不与任何文件或行绑定的 diff 级评论
- `<id>` 接受完整的 UUID 或 8 字符前缀

## 前置条件

1. 检查 `diffity` 是否可用：运行 `which diffity`。如果未找到，请使用 `npm install -g diffity` 安装它。
2. 检查是否存在评审会话：运行 `diffity agent list`。如果失败并显示 "No active review session"，请提示用户先启动 diffity (例如 `diffity` 或 **/diffity-diff**)。

## 操作步骤

1. 列出所有打开的评论线程并显示完整详细信息：
   ```
   diffity agent list --status open --json
   ```
   如果提供了 `thread-id` 参数，则仅过滤该线程。JSON 输出包含每个线程的完整评论内容、文件路径、行号和侧边信息。
2. 如果没有打开的线程，请告知用户没有需要解决的问题。
3. 对于每个打开的线程，检查 `comments` 数组和每个评论上的 `author.type` 字段 (`"user"` 或 `"agent"`):
   a. **跳过** 一般评论 (filePath `__general__`) — 这些是摘要，不是可执行的代码更改。
   b. **跳过** 最后一条评论是代理回复用户问题的线程 (例如 "Could you clarify...?") 且用户尚未回复的线程 — 代理正在等待用户输入。仍然处理代理留下原始评论的线程 (代码建议、评审反馈等) — 这些是可执行的。
   c. **`[nit]` 评论** — 这些是轻微建议但仍可执行。像处理其他评论一样解决它们。
   d. **`[question]` 评论** (来自用户) — 阅读问题，检查相关代码，并使用您的答案作为摘要解决线程：
      ```
      diffity agent resolve <thread-id> --summary "您的答案"
      ```
   e. 没有明确 `[question]` 标签的提问式评论 (例如 "should we add X?" 或 "can we rename this?") 是建议 — 将其视为可执行请求并执行更改。
   f. 从 JSON 输出中读取评论内容并理解请求的更改。解释意图：
      - 如果评论建议代码更改，请执行更改。
      - 如果评论建议添加文档，请添加或更新相关文档。
      - 如果评论提出的问题暗示了行动 (例如 "should we add X?")，将其视为执行该行动的请求。
      - 如果评论确实不明确且无法确定要采取的行动，请回复请求澄清而不是静默跳过：
        ```
        diffity agent reply <thread-id> --body "Could you clarify what change you'd like here?"
        ```
   g. 读取相关源文件以了解评论行周围的完整上下文，然后使用编辑工具执行请求的更改。
   h. 执行更改后，使用摘要解决线程：
      ```
      diffity agent resolve <thread-id> --summary "修复：简要描述更改内容"
      ```
4. 解决所有适用线程后，运行 `diffity agent list` 确认状态。
5. 告知用户检查浏览器 — 解决状态将在 2 秒内通过轮询显示。
