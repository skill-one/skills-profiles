# /si:promote — 将经验转化为规则

将一个已被验证的模式从 Claude 的自动记忆中移动到项目的规则系统中，使其成为强制执行的指令，而不是背景注释。

## 使用方法

```
/si:promote <模式描述>                    # 自动检测最佳目标
/si:promote <模式> --target claude.md     # 提升至 CLAUDE.md
/si:promote <模式> --target rules/testing.md  # 提升至限定规则
/si:promote <模式> --target rules/api.md --paths "src/api/**/*.ts"  # 限定路径
```

## 工作流程

### 第一步：理解模式

解析用户的描述。如果描述模糊，问一个澄清问题：
- "Claude 应遵循的具体行为是什么？"
- "这是适用于所有文件还是特定路径？"

### 第二步：在自动记忆中查找模式

```bash
# 在 MEMORY.md 中搜索相关条目
MEMORY_DIR="$HOME/.claude/projects/$(pwd | sed 's|/|%2F|g; s|%2F|/|; s|^/||')/memory"
grep -ni "<keywords>" "$MEMORY_DIR/MEMORY.md"
```

显示匹配的条目并确认它们是用户想要的内容。

### 第三步：确定正确的目标

| 模式范围 | 目标 | 示例 |
|---|---|---|
| 适用于整个项目 | `./CLAUDE.md` | "使用 pnpm，而不是 npm" |
| 适用于特定文件类型 | `.claude/rules/<主题>.md` | "API 处理器需要验证" |
| 适用于所有您的项目 | `~/.claude/CLAUDE.md` | "优先使用显式的错误处理" |

如果用户没有指定目标，根据范围推荐一个。

### 第四步：提炼为简洁规则

将自动记忆中的笔记格式转化为 CLAUDE.md 的指令格式：

**之前** (MEMORY.md — 描述性):
> 项目使用 pnpm workspaces。当我尝试 npm install 时它失败了。锁文件是 pnpm-lock.yaml。必须使用 pnpm install 依赖项。

**之后** (CLAUDE.md — 规定性):
```markdown
## 构建与依赖项
- 包管理器：pnpm（不是 npm）。使用 `pnpm install`。
```

**提炼规则:**
- 尽可能每条规则占一行
- 使用祈使语气（"使用 X"，"始终 Y"，"从不 Z"）
- 包含命令或示例，而不仅仅是概念
- 没有背景故事——只需指令

### 第五步：写入目标

**对于 CLAUDE.md:**
1. 读取现有的 CLAUDE.md
2. 找到适当的部分（或创建一个）
3. 在正确的标题下追加新规则
4. 如果文件将超过 200 行，建议使用 `.claude/rules/` 代替

**对于 `.claude/rules/`:**
1. 如果文件不存在，则创建它
2. 如果限定范围，添加带有 `paths` 的 YAML 前置内容
3. 写入规则内容

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "tests/api/**/*"
---

# API 开发规则

- 所有端点必须使用 Zod 模式验证输入
- 使用 `ApiError` 类进行错误响应（而不是原始 Error）
- 在处理函数中包含 OpenAPI JSDoc 注释
```

### 第六步：清理自动记忆

提升后，删除或标记 MEMORY.md 中的原始条目：

```bash
# 显示将要删除的内容
grep -n "<pattern>" "$MEMORY_DIR/MEMORY.md"
```

询问用户确认删除。然后编辑 MEMORY.md 以删除提升的条目。这为新的学习腾出空间。

### 第七步：确认

```
✅ 提升至 {{target}}

规则： "{{提炼的规则}}"
来源：MEMORY.md 行 {{n}}（已删除）
MEMORY.md: {{lines}}/200 行剩余

该模式现在是一个强制执行的指令。Claude 将在所有未来的会话中遵循它。
```

## 提升决策指南

### 提升时：
- 模式在自动记忆中出现过 3 次或更多次
- 您多次纠正 Claude
- 这是一个任何贡献者都应该知道的 项目惯例
- 它可以防止重复错误

### 不提升时：
- 它是一个一次性调试笔记（保留在自动记忆中）
- 它是会话特定的上下文（会话记忆处理此问题）
- 它可能很快就会改变（例如，在迁移期间）
- 它已经被现有规则覆盖

### CLAUDE.md 与 .claude/rules/

| 用于 CLAUDE.md | 用于 .claude/rules/ |
|---|---|
| 全局项目规则 | 文件类型特定的模式 |
| 构建命令 | 测试惯例 |
| 架构决策 | API 设计规则 |
| 团队惯例 | 框架特定的陷阱 |

## 小贴士

- 保持 CLAUDE.md 在 200 行以内——使用 rules/ 处理溢出
- 每行一条规则比段落更容易维护
- 包含具体的命令，而不仅仅是概念
- 每季度审查提升的规则——删除不再相关的规则
