用户希望回忆关于：$ARGUMENTS 的过去上下文

## 快速入门

```json
memory_smart_search { "query": "jwt 刷新令牌旋转", "limit": 10 }
```

预期输出：

```text
2 个结果跨越 2 个会话。
[重要性 8] 决策 · "每次使用时旋转刷新令牌" (会话 7f3a9c21)
[重要性 5] 代码 · "limit.ts 计数每个 IP" (会话 b21d004e)
```

## 原因

仅展示工具返回的内容。不要编造观察结果、会话 ID 或重要性分数。如果没有任何结果，请说明。

## 工作流程

1. 使用用户的文本作为 `query` 并设置 `limit: 10` 来调用 `memory_smart_search`。当用户针对特定仓库进行范围限制时，请传递 `project`。
2. 按会话分组结果。记录包含来源渠道 (`user`, `agent`, `tool`, `import`, `shared`)；当结果冲突时，优先考虑 `user` 的推断，并将 `shared` 记录标记为另一位队友的写入。
3. 对于每个观察结果，显示其类型、标题和叙述。
4. 优先展示高信号观察结果（重要性 >= 7）。
5. 如果没有结果，建议 2-3 个替代搜索词并停止。不要猜测。

## 反模式

错误：结果为空，因此你从假设中写出 "我们上周可能讨论过令牌过期"。

正确："没有匹配该查询的记忆。尝试 `refresh token`、`session expiry` 或 `auth rotation`。"

## 检查清单

- 每个展示的观察结果都来自工具响应。
- 结果按会话分组，高重要性优先。
- 空结果触发替代词建议，而不是编造。
- 没有会话 ID 或分数被释义或四舍五入。

## 参见

- `remember`：写入端；回忆检索它存储的内容。
- `recap`、`handoff`、`session-history`：相同数据的会话范围视图。
- `memory-discipline`：何时无需提示运行此搜索。

## 故障排除

如果 `memory_smart_search` 不可用，请参阅 ../_shared/TROUBLESHOOTING.md。
