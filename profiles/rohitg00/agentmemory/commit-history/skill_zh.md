用户想要一个与代理关联的提交列表。过滤参数：$ARGUMENTS

## 快速入门

```json
memory_commits { "branch": "main", "limit": 20 }
```

预期输出：

```text
9a1b2c3 main 2026-06-07 "rotate refresh tokens" · session 7f3a9c2 (14 obs)
b21d004 main 2026-06-05 "rate limiter audit"    · session b21d004 (9 obs)
```

## 原因

仅渲染工具返回的提交，按最新排序。空结果表示过滤器没有匹配任何内容，而不是工作缺失。

## 工作流程

1. 解析 `$ARGUMENTS` 以获取 `branch=<name>`、`repo=<url-or-fragment>`、`limit=<n>`。纯数字标记是限制值。默认值：无分支、无仓库、限制 100、最大 500。
2. 使用解析的过滤器调用 `memory_commits`。
3. 逆时间顺序渲染：短哈希值、分支、创建时间戳、消息的第一行、链接的会话 ID（前 8 个）以及观察计数，如果存在 `files` 则显示文件计数。
4. 空结果：告诉用户过滤器没有匹配任何内容，并建议删除分支或仓库过滤器。

## 反模式

错误（REST 回退）：连接 `?branch=` + 原始分支名，因此包含 `?`、`&` 或 `#` 的名称会损坏查询字符串。

正确：在追加到 `GET /agentmemory/commits` 之前，使用 `URLSearchParams`/`encodeURIComponent` 对每个值进行 URL 编码。

## 检查清单

- 过滤器已解析；纯数字被视为限制值；限制值上限为 500。
- 输出按逆时间顺序排列。
- 会话 ID 和观察计数直接来自响应。
- REST 回退 URL 编码分支、仓库和限制值。

## 参见

- `commit-context`：深入查看单个提交的会话。
- `recall`：搜索链接会话背后的观察记录。

## 故障排除

如果 `memory_commits` 不可用，请参阅 ../_shared/TROUBLESHOOTING.md。
