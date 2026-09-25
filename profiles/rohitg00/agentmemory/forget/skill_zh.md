用户想要从 agentmemory 中删除数据：$ARGUMENTS

## 快速入门

```json
memory_smart_search { "query": "配置中的旧 API 密钥", "limit": 20 }
```

显示匹配项，得到确认后：

```json
memory_governance_delete { "memoryIds": ["abc12345", "def67890"], "reason": "用户隐私请求" }
```

预期输出：

```text
找到 2 个匹配的记忆。已确认。删除了 2 个记忆。
```

## 原因

这是破坏性的且不可逆的。在调用删除之前，必须明确显示将要删除的内容并获取明确的确认。通过记忆 ID 删除，而不是直接删除会话。

## 工作流程

1. 使用 `memory_smart_search` 搜索，用户的文本作为 `query`，`limit: 20`。
2. 显示匹配项：会话 ID、记忆 ID、标题。请求明确确认。在沉默或模糊的“行，随便”的情况下不要继续。
3. 确认后，调用 `memory_governance_delete`，使用 `memoryIds`（数组或逗号分隔的字符串）和可选的 `reason`（默认 `插件技能请求`）。
4. 要删除整个会话，从搜索结果中收集该会话中的所有记忆 ID 并将它们全部传递。MCP 不接受裸 `sessionId`。
5. 课程是分开的：使用 `memory_lesson_delete` 和其 `lessonId` 删除一个；`memory_governance_delete` 不会触及课程。
6. 报告删除数量。数量为 0 表示 ID 不存在；如实说明，而不是声称删除。

## 反模式

错误：搜索返回匹配项，你立即调用 `memory_governance_delete` 而不显示它们或等待确认。

正确：列出匹配项，询问“删除这些 2 个？(是/否)”，并在明确确认后删除。

## 检查清单

- 在任何删除之前，匹配项都已显示给用户。
- 收到了明确的“是”，而不是假设。
- `memoryIds` 包含来自搜索的真实 ID，而不是裸 `sessionId`。
- 最终消息说明了实际删除的数量。

## 参见

- `remember`：写入端；忘记是其撤销操作。
- `recall`：在删除前找到确切的记忆 ID。

## 故障排除

如果 `memory_smart_search` 或 `memory_governance_delete` 不可用，请参阅 ../_shared/TROUBLESHOOTING.md。
