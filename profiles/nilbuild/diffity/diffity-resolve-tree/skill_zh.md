# Diffity Resolve Tree 技能

您正在通过 `diffity tree` 浏览器阅读存储库文件中留下的公开评论，并通过执行请求的代码更改来解决问题。

## 参数

- `thread-id` (可选): 通过 ID 解决特定线程，而不是所有打开的线程。示例：`/diffity-resolve-tree abc123`

## 命令行参考

```
diffity agent list [--status open|resolved|dismissed] [--json]
diffity agent comment --file <路径> --line <n> [--end-line <n>] --body "<文本>"
diffity agent resolve <id> [--summary "<文本>"]
diffity agent dismiss <id> [--reason "<文本>"]
diffity agent reply <id> --body "<文本>"
```

- `--file`, `--line`, `--body` 是 `comment` 所必需的
- `--end-line` 默认为 `--line` (单行评论)
- `<id>` 接受完整的 UUID 或 8 字符前缀

## 前置条件

1. 检查 `diffity` 是否可用：运行 `which diffity`。如果未找到，请使用 `npm install -g diffity` 安装它。
2. 检查是否存在树会话：运行 `diffity agent list`。如果失败并显示 "No active review session"，请提示用户先启动 diffity tree (例如 `diffity tree`)。

## 操作步骤

1. 列出带有完整详细信息的打开评论线程：
   ```
   diffity agent list --status open --json
   ```
   如果提供了 `thread-id` 参数，则仅过滤该线程。JSON 输出包含每个线程的完整评论内容、文件路径、行号和侧边信息。
2. 如果没有打开的线程，告诉用户没有需要解决的问题。
3. 对于每个打开的线程：
   a. **跳过** 一般评论 (filePath `__general__`) — 这些是摘要，不是可执行的代码更改。
   b. **跳过** 最后一条评论是代理提问而用户尚未回复的线程 — 代理正在等待用户输入。
   c. **`[问题]` 评论** (来自用户) — 阅读问题，检查相关代码，并回复答案：
      ```
      diffity agent reply <thread-id> --body "您的答案在此处"
      ```
      然后用您的答案摘要解决线程。
   d. 没有明确 `[问题]` 标签的提问式评论 (例如 "我们应该添加 X 吗?" 或 "我们可以重命名这个吗?") 是建议 — 将其视为可执行的请求并执行更改。
   e. 从 JSON 输出中阅读评论内容并理解请求的更改。评论锚定到特定文件和行范围 — 阅读完整文件以了解上下文：
      - 如果评论建议代码更改、重构或改进，请执行更改。
      - 如果评论建议添加文档，请添加或更新相关文档。
      - 如果评论确实不明确，回复请求澄清：
        ```
        diffity agent reply <thread-id> --body "您能在这里澄清您想要的更改吗?"
        ```
   f. 执行更改后，用摘要解决线程：
      ```
      diffity agent resolve <thread-id> --summary "修复：简要描述所做的更改"
      ```
4. 解决所有适用线程后，运行 `diffity agent list` 确认状态。
5. 告诉用户检查浏览器 — 解决状态将在 2 秒内通过轮询显示。
