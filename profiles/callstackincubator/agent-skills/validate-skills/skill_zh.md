# 验证技能

验证 `skills/` 目录下的所有技能是否符合 agentskills.io 规范和 Claude Code 最佳实践。

## 验证清单

对于每个技能目录，请验证：

### 规范符合性 (agentskills.io)

| 检查项 | 规则 |
|-------|------|
| `name` 格式 | 1-64 个字符，小写字母数字和连字符，不能有首尾连字符或连续连字符 |
| `name` 与目录匹配 | 目录名必须等于 `name` 字段 |
| `description` 长度 | 1-1024 个字符，非空 |
| 可选字段有效 | 如果存在 `license`、`metadata`、`compatibility` 字段 |

### 最佳实践 (Claude Code)

| 检查项 | 规则 |
|-------|------|
| 描述格式 | 第三人称，描述用途和适用场景 |
| 主体长度 | 少于 500 行 |
| 加载为单级深度 | `SKILL.md` 是唯一的渐进式披露入口点：每个引用文件都必须能从 `SKILL.md` 中访问到。引用文件可以互相交叉链接用于导航（见下注）。 |
| 链接使用 markdown | 使用 `[文本](路径)` 而不是裸文件名 |
| 无冗余 | 不要在主体中重复描述 |
| 简洁 | 只添加 Claude 已知的上下文之外的信息 |

> **单级深度与交叉链接。** 单级深度规则针对 *渐进式披露加载链* — 一个只能通过先加载另一个引用文件才能发现的引用（`SKILL.md` → `a.md` → `b.md`，其中 `b.md` 未从 `SKILL.md` 链接）。这是一种缺陷：它隐藏了加载器的内容。
>
> 它**不**禁止 *导航* 交叉链接。根据 [AGENTS.md](../../../AGENTS.md)，引用文件以“相关技能”页脚结尾，链接到同级引用文件，这是必需的。只要两个端点都可直接从 `SKILL.md` 访问，交叉链接就是允许的。只有当引用文件*仅*通过另一个引用文件才能访问时，才应标记该引用。

## 如何执行

1. 查找所有技能目录：
   ```bash
   fd -t d -d 1 . skills/
   ```

2. 对于每个技能，读取 `SKILL.md` 并对照上述规则进行检查

3. 以以下格式报告问题：
   ```
   ## 验证结果

   ### skills/example-skill
   - [PASS] name 格式有效
   - [FAIL] name "example" 与目录 "example-skill" 不匹配
   - [PASS] 描述长度正常 (156 个字符)
   ```

## 参考资料

- [agentskills.io 规范](https://agentskills.io/specification)
- [Claude Code 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
