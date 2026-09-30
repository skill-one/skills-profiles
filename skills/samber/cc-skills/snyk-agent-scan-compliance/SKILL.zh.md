---
name: snyk-agent-scan-compliance
description: snyk-agent-scan 的合规专家——即代理技能文件扫描器——不适用于其他 Snyk CLI 工具（如 snyk test、snyk code SAST、snyk iac、snyk container）。通过内容结构调整来修复警报，而非通过抑制或删除信息。涵盖技能目录中的所有文件：SKILL.md、references/、assets/ 以及任何其他 Markdown 文件。在以下情况适用：编写新技能、编辑现有技能、本地或 CI 中对失败的 snyk-agent-scan 进行分诊处理，或解决由代理扫描器失败导致的 PR 阻塞。不适用于依赖漏洞、代码安全发现或基础设施配置错误——这些超出了适用范围。
---

**角色设定：** 你是一位技能合规领域的专家，擅长通过重构内容来修复 snyk-agent-scan 提示，从不通过压制或删除有用信息的方式来解决。

**思考模式：** 在处理多个提示时，应尽可能深入地推理，因为针对一种提示的修复可能会引发或抑制另一种提示。深入推理可以减少返工。在 Claude Code 中，使用 `ultrathink` 命令显式触发扩展思考。

# snyk-agent-scan 合规性

`snyk-agent-scan` 工具分析技能体中三类不安全模式：第三方内容暴露（W011）、恶意外部 URL（W012）以及通过 MCP 工具调用进行的提示注入（W001）。这三种模式都可以通过内容重构来修复，且不会丢失任何信息。

## 参考文件

| 文件 | 何时阅读 |
| --- | --- |
| [references/w001-patterns.md](references/w001-patterns.md) | 修复 W001 提示 — MCP 工具名称模式 |
| [references/w011-patterns.md](references/w011-patterns.md) | 修复 W011 提示 — 命令式 URL 和外部内容模式 |
| [references/w012-patterns.md](references/w012-patterns.md) | 修复 W012 提示 — 版本固定和 frontmatter 卸载 |

## 快速参考

| 提示 | 严重程度 | 根本原因 | 主要修复方法 |
| --- | --- | --- | --- |
| W011 | 高 | 技能体指示代理获取/解释外部内容 | 将命令式语句替换为被动可用性提示 |
| W012 | 高 | 技能体引用在运行时获取和执行的外部 URL | 移至 frontmatter `install` 块；固定版本 |
| W001 | 高 | 技能体明确命名 MCP 工具函数 | 使用通用表述替代 |

## 运行扫描器

```bash
# 扫描单个技能
SNYK_TOKEN=<token> snyk-agent-scan --skills skills/<name>/

# 扫描所有技能
SNYK_TOKEN=<token> snyk-agent-scan --skills ./skills
```

扫描器需要一个有效的 `SNYK_TOKEN`。在 CI 环境中，将其作为密钥存储。如果未安装 `snyk-agent-scan`，可以使用 `uvx snyk-agent-scan@latest` 作为即插即用替代方案，无需安装。有关每种提示类型的修复，请参阅 [详细模式](references/w011-patterns.md)。

## W011 — 第三方内容暴露

当技能体使用命令式动词指示代理获取、检查或评估外部内容并对其采取行动时，W011 会触发。扫描器将代理视为执行外部动作的语法主语。

规则：

- 将 `Check <url>` 和 `Fetch <url>` 替换为被动提示：`<url> 处的发布说明可能有用。`
- 从任何涉及外部数据的指令中移除 "always"：`Always reference the changelog` → `The changelog documents breaking changes。`
- 将工具调用（`gh repo view`、`govulncheck`）保留在代码块中，而不是在暗示代理必须在行动前执行的散文式清单中。
- 将工具执行与决策解耦：运行工具是允许的；将其远程获取的输出作为重构的唯一触发器是不允许的。

请参阅 [W011 模式目录](references/w011-patterns.md) 以获取 12+ 个示例。

## W012 — 潜在恶意外部 URL

当技能体引用在运行时获取和执行的外部内容时，W012 会触发：使用 `@latest` 的包安装、管道到 shell 模式或 GitHub Actions 的错误/不存在的主版本。

规则：

- 将 `go install pkg@latest` 和类似命令从散文中移至 frontmatter `metadata.openclaw.install` 块 — 扫描器不会标记 frontmatter。
- 将 GitHub Actions 固定到正确的主版本（`@v4`，而不是 `@v6`）。
- 技能体中永远不要使用管道到 shell 模式（`curl ... | sh`）。

请参阅 [W012 模式目录](references/w012-patterns.md) 以获取 8+ 个示例。

## W001 — 通过 MCP 工具调用进行的提示注入

当技能体明确命名 MCP 服务器工具函数时，W001 会触发提示注入检测。

规则：

- 技能体中永远不要写工具函数名称（`resolve-library-id`、`query-docs`、`mcp__*`）。
- 使用通用表述替代：`Context7 可以作为发现性平台提供帮助。`
- MCP 工具名称仍可能出现在 `allowed-tools` frontmatter 字段中 — 只有技能体受到限制。

请参阅 [W001 模式目录](references/w001-patterns.md) 以获取安全的重构方法。

## 修复方法

逐个修复提示，每次更改后重新运行 `snyk-agent-scan`，并验证提示数量是否减少后再移动到下一个。如果修复未减少提示，请撤销并尝试不同方法 — 不要堆叠未经验证的更改。

当扫描返回多个提示时，按以下顺序修复以最小化返工：

```
1. W001（最简单） — 从体中移除 MCP 工具名称；确认 allowed-tools 是否正确
2. W011 — 将命令式句子改写为被动陈述；将清单项移至代码块
3. W012 — 将安装命令移至 frontmatter；固定版本
4. 每次单独修复后重新扫描以验证改进
```

W011 修复有时会在重构后使 URL 更加突出，从而暴露隐藏的 W012。

## 假阳性

并非所有提示都是真实的。可能假阳性的标准：

| 条件 | 可能是假阳性？ |
| --- | --- |
| URL 出现在 markdown 表格单元格中作为参考数据，而不是指令 | 是 — 表格通常安全 |
| 在描述库的技能中，URL 是库的官方文档 | 是 — 通常安全 |
| URL 是 frontmatter 中的 `homepage` 或 `issues` 链接 | 是 — 不被扫描 |
| 工具名称出现在三反引号代码块中作为 shell 命令 | 有时 — 代码块受到较宽松的审查 |
| `go install` 在快速参考代码块中使用固定版本 | 有时 — 固定版本风险较低 |
| 句子中 "always" 出现，但不涉及外部资源 | 是 — "always" 单独不会触发 W011 |

当提示可能是假阳性时，使用被动提示模式进行重构 — 扫描器的启发式算法保护真实用户；重构比假设扫描器错误更安全。

## 预编写检查清单

在编写新技能体时应用这些检查，以避免在第一次扫描前出现提示：

- [ ] 没有句子让代理作为主语对 URL 执行动作
- [ ] 技能体中任何安装指令都没有 `@latest` 标签
- [ ] 技能体中散文部分没有 MCP 工具函数名称（`mcp__*`、`resolve-library-id` 等）
- [ ] 所有安装命令都在 frontmatter `install` 块中
- [ ] GitHub Actions 版本与实际存在的主版本匹配
- [ ] 工具调用在代码块中，而不是在有序列表清单中
- [ ] "always" 不在任何外部资源指令前出现

如果你在 `snyk-agent-scan` 中遇到错误或意外行为，请访问 <https://github.com/snyk/snyk-agent-scan/issues> 打开问题。

如果你发现一个触发提示但未在上述参考文件中涵盖的模式 — 一种新的绕过技术、假阳性条件或未记录的提示代码 — 请访问 <https://github.com/samber/cc-skills/issues> 打开问题或向 `samber/cc-skills` 仓库提交拉取请求以将其添加到相关模式文件。新模式是对此技能最有价值的贡献。
