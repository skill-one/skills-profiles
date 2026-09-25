# /si:remember — 显式保存知识

当某件事重要到你不希望依赖 Claude 自动发现它时，向自动记忆写入一个显式条目。

## 使用方法

```
/si:remember <要记住的内容>
/si:remember "这个项目的 CI 需要 Node 20 LTS — v22 会破坏构建"
/si:remember "The /api/auth 端点使用自定义的 JWT 库，而不是 passport"
/si:remember "Reza 更倾向于显式错误处理而不是 try-catch-all 模式"
```

## 何时使用

| 情况 | 示例 |
|------|------|
| 艰难获得的调试见解 | "CORS 错误发生在 /api/upload 是由 CDN 引起的，而不是后端" |
| 项目约定不在 CLAUDE.md 中 | "我们在 src/components/ 中使用模块导出" |
| 工具特定的陷阱 | "Jest 需要 `--forceExit` 标志，否则它在 DB 测试中挂起" |
| 架构决策 | "我们选择 Drizzle 而不是 Prisma 用于类型安全的 SQL" |
| 你希望 Claude 学习的偏好 | "不要添加解释明显代码的注释" |

## 工作流程

### 第一步：解析知识

从用户输入中提取：
- **内容**：具体的事实或模式
- **重要性原因**：上下文（如果提供）
- **范围**：项目特定还是全局？

### 第二步：检查重复

```bash
MEMORY_DIR="$HOME/.claude/projects/$(pwd | sed 's|/|%2F|g; s|%2F|/|; s|^/||')/memory"
grep -ni "<keywords>" "$MEMORY_DIR/MEMORY.md" 2>/dev/null
```

如果存在相似的条目：
- 向用户显示它
- 询问："更新现有条目还是添加新条目？"

### 第三步：写入 MEMORY.md

追加到 `MEMORY.md` 的末尾：

```markdown
- {{简洁的事实或模式}}
```

保持条目简洁——尽可能一行。自动记忆条目不需要时间戳、ID 或元数据。它们是笔记，不是数据库记录。

如果 MEMORY.md 超过 180 行，警告用户：

```
⚠️ MEMORY.md 是 {{n}}/200 行。考虑运行 /si:memory-review 来释放空间。
```

### 第四步：建议提升

如果知识听起来像一条规则（祈使句、总是/从不、约定）：

```
💡 这听起来可能更适合作为 CLAUDE.md 规则而不是记忆条目。
   规则具有更高的优先级。想 /si:promote 它吗？
```

### 第五步：确认

```
✅ 已保存到自动记忆

  "{{条目}}"

  MEMORY.md: {{n}}/200 行
  Claude 将在每个项目会话开始时看到此内容。
```

## /si:remember 不应用于什么

- **临时上下文**：使用会话记忆或在对话中直接告诉 Claude
- **强制规则**：使用 `/si:promote` 直接写入 CLAUDE.md
- **跨项目知识**：使用 `~/.claude/CLAUDE.md` 用于全局规则
- **敏感数据**：永远不要在记忆文件中存储凭证、令牌或密钥

## 小贴士

- 保持简洁——一行胜过一整段
- 包含具体的命令或值，而不仅仅是概念
  - ✅ "使用 `pnpm build` 构建项目，使用 `pnpm test:e2e` 运行测试"
  - ❌ "项目使用 pnpm 进行构建和测试"
- 如果你两次记住同一件事，将其提升到 CLAUDE.md
