用户希望继续工作。可选的 cwd 覆盖：$ARGUMENTS

## 快速入门

```json
memory_sessions { "limit": 20 }
```

选择最接近的会话，其 `cwd` 与此项目匹配，然后：
`memory_recall { "query": "<会话顶部概念>", "limit": 10 }`。

预期输出：

```text
继续 7f3a9c2 "Auth refresh rework"。
开放问题：注销是否应撤销所有设备令牌还是仅当前一个？
下一步：确定撤销范围，然后更新 auth/logout.ts。
```

## 原因

按目录边界匹配会话，而不是原始前缀，因此兄弟仓库永远不会被误认为是这个。永远不会为空会话编造观察结果。

## 工作流程

1. 解析项目路径：如果 `$ARGUMENTS` 被提供，将其规范化为绝对路径 (`path.resolve(process.cwd(), $ARGUMENTS)`)；否则使用 cwd。
2. 调用 `memory_sessions`。选择最接近的会话，其规范化 `cwd` 按目录边界匹配：相等性，OR `cwd.startsWith(projectPath + sep)`，OR `projectPath.startsWith(cwd + sep)`。优先选择 `completed` 而不是 `abandoned`。没有匹配：回退到总体上最接近的会话。
3. 如果会话在未回答的用户界面问题上结束，首先显示它。在 `summary` 或最近的 `conversation` 观察结果中查找 `narrative` 以 `?` 结尾的。
4. 总结：标题/摘要，关键文件，关键决策或错误，使用 `memory_recall` 对顶部概念进行总结，限制为 10。
5. 以一个具体的 "下一步?" 指针结束。

## 反模式

错误：`session.cwd.startsWith(projectPath)` 在项目是 `/repo-a` 时匹配 `/repo-a-staging`，继续错误的仓库的会话。

正确：`session.cwd === projectPath || session.cwd.startsWith(projectPath + sep)`，一个不能跨越兄弟仓库的目录边界检查。

## 检查清单

- cwd 覆盖解析为一个绝对、规范化的路径。
- 匹配使用了一个目录边界检查，而不是原始前缀。
- 未回答的问题（如果有）引导响应。
- 空会话被平铺报告，并提供重新开始的提议。

## 参见

- `recap`, `session-history`, `recall`：相同的会话数据，更广泛的视图。

## 故障排除

如果 `memory_sessions` 或 `memory_recall` 不可用，请参阅 ../_shared/TROUBLESHOOTING.md。
