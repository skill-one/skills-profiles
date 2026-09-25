用户希望将此内容保存到长期记忆中：$ARGUMENTS

## 快速入门

```json
memory_save {
  "content": "我们每次使用 JWT 刷新令牌时都会进行轮换；旧令牌在 auth/refresh.ts 中由服务器端吊销。",
  "concepts": "jwt-refresh-rotation, token-revocation, auth-flow",
  "files": "src/auth/refresh.ts"
}
```

预期输出：

```text
已保存记忆 abc12345，包含 3 个概念：jwt-refresh-rotation, token-revocation, auth-flow。
```

## 原因

记忆的实用性取决于检索它的术语。使用具体概念进行标记，以便未来的 `recall` 能够找到它，并保留用户自己的措辞。

## 工作流程

1. 从 `$ARGUMENTS` 中提取核心见解、决策或事实。
2. 提取 2-5 个小写概念短语。优先选择具体的而不是通用的（`jwt-refresh-rotation` 比 `auth` 更好）。
3. 提取引用的文件路径（绝对或仓库相对路径）。如果没有，则为空。
4. 调用 `memory_save`，使用 `content`、`concepts`（逗号分隔的字符串）和 `files`（逗号分隔的字符串）。在多代理设置中传递 `agentId`，以便记忆保存在正确的代理范围内。
5. 确认保存并回显概念，以便用户知道检索术语。
6. 要更新事实，直接保存更正后的版本：近重复内容会覆盖旧记录，旧记录会保留在版本链中。

## 反模式

错误：`concepts: "stuff, code, notes"`（通用标签，无法在以后找到）。

正确：`concepts: "jwt-refresh-rotation, token-revocation"`（具体、可检索）。

## 检查清单

- 内容保留用户的措辞，而不是释义。
- 概念是具体的、小写的、2-5 项。
- 文件路径是真实引用，而不是猜测。
- 确认回显了标记的确切概念。

## 参见

- `recall`：在此处检索保存的内容（与此技能成对的技能）。
- `forget`：删除错误保存的记忆。
- `lesson`：来自更正的行为规则；记忆用于事实。
- `memory-discipline`：何时无需提示保存。

## 故障排除

如果 `memory_save` 不可用，请参阅 ../_shared/TROUBLESHOOTING.md。
