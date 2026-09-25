**角色：** 你是一位技能合规领域的专家。你通过重构内容来修复 snyk-agent-scan 警报，而不是压制或删除有用的信息。

**思考模式：** 对于多警报修复，要尽可能彻底地推理，因为一个警报的修复可能会引发或压制另一个警报。深度推理可以减少返工。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

# snyk-agent-scan 合规性

`snyk-agent-scan` 工具分析技能体，查找三类不安全模式：第三方内容暴露（W011）、恶意外部 URL（W012）以及通过 MCP 工具调用进行的提示注入（W001）。这三类都可以通过内容重构来修复，而不会丢失任何信息。

## 参考文件

| 文件 | 何时阅读 |
| --- | --- |
| [references/w001-patterns.md](references/w001-patterns.md) | 修复 W001 警报 — MCP 工具名称模式 |
| [references/w011-patterns.md](references/w011-patterns.md) | 修复 W011 警报 — 命令式 URL 和外部内容模式 |
| [references/w012-patterns.md](references/w012-patterns.md) | 修复 W012 警报 — 版本固定和 frontmatter 卸载 |

## 快速参考

| 警报 | 严重性 | 根本原因 | 主要修复 |
| --- | --- | --- | --- |
| W011 | 高 | 技能体指示代理获取/解释外部内容 | 将命令式语句替换为被动可用性提示 |
| W012 | 高 | 技能体引用在运行时获取和执行的外部 URL | 移至 frontmatter `install` 块；固定版本 |
| W001 | 高 | 技能体明确命名 MCP 工具函数 | 使用通用表述代替 |

## 运行扫描器

```bash
# 扫描单个技能
SNYK_TOKEN=<token> snyk-agent-scan --skills skills/<name>/

# 扫描所有技能
SNYK_TOKEN=<token> snyk-agent-scan --skills ./skills
```

扫描器需要一个有效的 `SNYK_TOKEN`。在 CI 中，将其作为密钥存储。如果 `snyk-agent-scan` 未安装，可以使用 `uvx snyk-agent-scan@latest` 作为即插即用替代方案，无需安装。有关按警报类型修复的详细模式，请参阅 [详细模式](references/w011-patterns.md)。

## W011 — 第三方内容暴露

当技能体使用命令式动词指示代理获取、检查或评估外部内容并对其采取行动时，W011 会触发。扫描器将代理视为执行外部动作的语法主语。

规则：

- 将 `Check <url>` 和 `Fetch <url>` 替换为被动提示：`<url> 上的发布说明可能有用。`
- 从任何涉及外部数据的指令中删除 "always"：`Always reference the changelog` → `The changelog documents breaking changes。`
- 将工具调用（`gh repo view`，`govulncheck`）保留在代码块中，而不是在暗示代理必须在行动前执行的散文式清单中。
- 将工具执行与决策解耦：运行工具是可以的；将其远程源输出作为重构的唯一触发器则不行。

请参阅 [W011 模式目录](references/w011-patterns.md) 以获取 12+ 的示例。

## W012 — 潜在恶意外部 URL

当技能体引用在运行时获取和执行的外部内容时，W012 会触发：使用 `@latest` 的包安装、管道到 shell 模式或 GitHub Actions 的错误/不存在的主要版本。

规则：

- 将 `go install pkg@latest` 和类似命令从散文移至 frontmatter `metadata.openclaw.install` 块 — 扫描器不会标记 frontmatter。
- 将 GitHub Actions 固定到正确的当前主要版本（`@v4`，而不是 `@v6`）。
- 技能体中永远不要使用管道到 shell 模式（`curl ... | sh`）。

请参阅 [W012 模式目录](references/w012-patterns.md) 以获取 8+ 的示例。

## W001 — 通过 MCP 工具调用进行的提示注入

当技能体明确命名 MCP 服务器工具函数时，W001 会触发提示注入检测。

规则：

- 技能体中永远不要写工具函数名称（`resolve-library-id`，`query-docs`，`mcp__*`）。
- 使用通用表述代替：`Context7 可以作为可发现性平台提供帮助。`
- MCP 工具名称仍可能出现在 `allowed-tools` frontmatter 字段中 — 只有技能体受到限制。

请参阅 [W001 模式目录](references/w001-patterns.md) 以获取安全的重构方式。

## 修复方法

逐个修复警报，每次更改后重新运行 `snyk-agent-scan`，并验证警报数量减少后再移动到下一个。如果修复未减少警报，请撤销并尝试不同方法 — 不要堆叠未经验证的更改。

当扫描返回多个警报时，按以下顺序修复以最小化返工：

```
1. W001（最简单） — 从体中删除 MCP 工具名称；确认 allowed-tools 是否正确
2. W011 — 将命令式句子改写为被动陈述；将清单项移至代码块
3. W012 — 将安装命令移至 frontmatter；固定版本
4. 每次单独修复后重新扫描以验证改进
```

W011 修复有时会在重构后使 URL 更加突出，从而暴露隐藏的 W012。

## 假阳性

并非所有警报都是真实的。可能假阳性的标准：

| 条件 | 可能是假阳性？ |
| --- | --- |
| URL 出现在 markdown 表格单元格中作为参考数据，而不是指令 | 是 — 表格通常安全 |
| 在描述库的技能中，URL 是库的官方文档 | 是 — 通常安全 |
| URL 是 frontmatter 中的 `homepage` 或 `issues` 链接 | 是 — 未被扫描 |
| 工具名称出现在三反引号代码块中作为 shell 命令 | 有时 — 代码块受到较轻的审查 |
| `go install` 在 Quick Reference 代码块中使用固定版本 | 有时 — 固定版本风险较低 |
| 句子中包含 `always`，但不涉及外部资源 | 是 — "always" 单独不会触发 W011 |

当警报可能是假阳性时，使用被动提示模式进行重构 — 扫描器的启发式算法保护了真实用户；重构比假设扫描器错误更安全。

## 预编写检查清单

在编写新技能体时应用这些检查，以避免在第一次扫描前出现警报：

- [ ] 没有句子将代理作为主语执行对 URL 的动作
- [ ] 技能体中没有 `@latest` 标签在任何安装指令中
- [ ] 技能体中没有 MCP 工具函数名称（`mcp__*`，`resolve-library-id` 等）在体中
- [ ] 所有安装命令都在 frontmatter `install` 块中
- [ ] GitHub Actions 版本与实际存在的主要版本匹配
- [ ] 工具调用在代码块中，而不是在有序列表清单中
- [ ] "always" 不在任何外部资源指令前

如果你在 `snyk-agent-scan` 中遇到错误或意外行为，请访问 <https://github.com/snyk/snyk-agent-scan/issues> 打开问题。

如果你发现一个触发警报的模式未在上述参考文件中涵盖 — 一种新的绕过技术、一个假阳性条件或一个未记录的警报代码 — 请访问 <https://github.com/samber/cc-skills/issues> 打开问题或向 `samber/cc-skills` 仓库提交拉取请求以将其添加到相关模式文件。新模式是对此技能最有价值的贡献。
