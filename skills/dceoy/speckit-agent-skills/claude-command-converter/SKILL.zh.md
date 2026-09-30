---
name: claude-command-converter
description: 将 Claude 代码命令（.claude/commands/*.md）转换为标准代理技能（skills/*/SKILL.md）。用于将斜杠命令迁移到便携式技能格式、从现有命令创建技能或跨 AI 运行时标准化命令定义。
---

# Claude 命令转换器

将 Claude Code 命令转换为标准 Agent Skills 格式，以实现跨 AI 编码助手的应用。

## 使用场景

- 将现有的 `.claude/commands/*.md` 文件迁移到 `skills/*/SKILL.md` 格式。
- 从 Claude Code 特定命令创建可移植技能。
- 为使用 Claude Code、Codex CLI、GitHub Copilot 等运行时环境标准化命令定义。

## 输入

- 源命令文件路径（例如：`.claude/commands/my-command.md`）。
- 可选：目标技能名称（默认为不带扩展名的命令文件名）。

如果输入缺失，请询问源命令文件路径。

## 格式差异

### Claude Code 命令格式

位置：`.claude/commands/<command-name>.md`

```yaml
---
description: 命令的简短描述
handoffs:
  - label: 下一步操作
    agent: other.command
    prompt: 触发提示
    send: true
---
## 用户输入

\`\`\`text
$ARGUMENTS
\`\`\`

[命令说明...]
```

### 标准Agent技能格式

位置：`skills/<skill-name>/SKILL.md`

```yaml
---
name: skill-name
description: 完整描述，包括技能的作用和使用场景。
---

# 技能标题

## 使用场景

- 场景1
- 场景2

## 输入

- 必需输入1
- 可选输入2

## 工作流

1. 步骤1
2. 步骤2
...

## 输出

- 输出文件1
- 输出文件2
```

## 转换工作流

1. **从 `.claude/commands/` 读取源命令**。

2. **提取元数据**：
   - 从 YAML 前置内容中提取 `description`。
   - 提取 `handoffs` 用于相关技能/下一步操作。
   - 处理 `$ARGUMENTS` 作为输入。

3. **确定技能名称**：
   - 将 `command.name.md` 转换为 `command-name`（用连字符替换点）。
   - 多词名称使用连字符命名法（kebab-case）。

4. **创建技能目录**：`skills/<skill-name>/`

5. **转换内容为 SKILL.md 格式**：
   - **前置内容**：仅保留 `name` 和 `description`。
   - **增强描述**：扩展以包含技能的使用场景。
   - **转换 `$ARGUMENTS`**：作为输入部分进行文档化。
   - **结构化工作流**：提取步骤到编号的 Workflow 部分。
   - **添加“使用场景”**：根据命令上下文和描述推导。
   - **添加“输出”**：列出生成的文件/工件。
   - **转换 handoffs**：添加“下一步操作”部分引用相关技能。

6. **移除运行时特定内容**：
   - 移除 `## 用户输入` 部分和 `$ARGUMENTS` 块。
   - 从前置内容中移除 `handoffs`（移至文本部分）。
   - 移除 `/command.name` 引用（使用技能名称替代）。

7. **验证技能结构**：
   - 前置内容仅包含 `name` 和 `description`。
   - 正文有清晰的章节（使用场景、输入、工作流、输出）。
   - 无 TODO 占位符残留。
   - 无运行时特定变量（如 `$ARGUMENTS`）。

8. **报告转换结果**：
   - 源命令路径。
   - 生成的技能路径。
   - 应用的主要转换。
   - 手动审核建议。

## 转换规则

| Claude Command                | Agent Skill                                   |
| ----------------------------- | --------------------------------------------- |
| `$ARGUMENTS`                  | 输入部分描述预期用户输入                     |
| `handoffs:`                   | 下一步操作部分包含技能引用                   |
| `/command.name`               | `skill-name`（连字符命名法）                 |
| `agent: foo.bar`              | `foo-bar` 技能引用                           |
| `description:` in frontmatter | `description:` 扩展包含触发条件             |
| Inline `## User Input`        | 移除；输入部分文档化                         |

## 示例转换

**输入**：`.claude/commands/speckit.specify.md`

```yaml
---
description: 从自然语言创建功能规范。
handoffs:
  - label: 制定技术计划
    agent: speckit.plan
---
## 用户输入

\`\`\`text
$ARGUMENTS
\`\`\`

用户在 `/speckit.specify` 后输入的文本...
```

**输出**：`skills/speckit-specify/SKILL.md`

```yaml
---
name: speckit-specify
description: 从自然语言功能描述创建或更新功能规范。
---

# Spec Kit Specify 技能

## 使用场景

- 用户需要从自然语言描述获取新或更新的功能规范。

## 输入

- 用户的特征描述。
- 包含 `.specify/` 脚本和模板的仓库上下文。

如果描述缺失或不清晰，在继续之前询问针对性问题。

## 工作流

...

## 输出

- `specs/<feature>/spec.md`
- `specs/<feature>/checklists/requirements.md`

## 下一步操作

生成 spec.md 后：

- **使用 speckit-plan 制定** 技术实施计划。
- **使用 speckit-clarify 明确** 规范需求。
```

## 关键规则

- 保留所有工作流逻辑和指令。
- 移除运行时特定结构（`$ARGUMENTS`、`handoffs`、`/slash-commands`）。
- 将简短描述扩展为包含使用触发条件。
- 工作流步骤使用祈使语气。
- 保持技能自包含和可移植。
- 不要添加不必要的文档文件（README、CHANGELOG 等）。

## 下一步操作

转换后：

- 审核生成的 SKILL.md 的完整性。
- 删除 `scripts/`、`references/`、`assets/` 中的未使用示例文件。
- 如适用，更新 AGENTS.md/CLAUDE.md 技能清单。
- 如需运行时集成，创建符号链接。
