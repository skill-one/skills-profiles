# Unslop

人性化AI生成的文本。先审核，用户要求重写时再进行重写。

每次审核或重写时，都必须阅读 [references/core-contract.md](references/core-contract.md)。
它是唯一的行为合约。命令文件定义路由和机制；预设提供可选的语音，但两者都不能覆盖核心合约。

## 路由

**当用户调用子命令（`/unslop teach ...`，`/unslop cleanup
...`）时，你必须先读取 `references/commands/<command>.md` 再执行。
强制要求 — 命令文件定义流程，跳过它会遗漏用户期望的步骤。一个不带命令词的 `/unslop <文本>` 默认为 `rewrite`。如果第一个词不匹配任何命令，但意图明显对应一个（例如 "标记AI说的内容，不要修改任何东西" → `cleanup` 报告式），加载该命令文件并按调用方式执行。

| 命令 | 目的 | 文件 |
|---------|---------|------|
| `rewrite` | 默认两遍去slop：诊断、在守卫下重建、验证。 | [references/commands/rewrite.md](references/commands/rewrite.md) |
| `cleanup` | 合作者：廉价检测、可审核的建议带合约门；包括报告式 "标记，不修改"。 | [references/commands/cleanup.md](references/commands/cleanup.md) |
| `teach` | 代理驱动的语音构建：收集、批准、分析、分层卡片、评分演示。 | [references/commands/teach.md](references/commands/teach.md) |
| `mimic` | 全门下带语音的起草或重写；当一遍不足时优化循环。 | [references/commands/mimic.md](references/commands/mimic.md) |
| _maintenance_ | 将一个狂野的AI用法变成一个评估行和一个PR（不是顶级动词）。 | [references/commands/contribute.md](references/commands/contribute.md) |

### 通过短语路由

子流程可以通过其自然名称访问，无需作为顶级动词。
当用户说任何这些时，加载命名的文件并跳转到流程：

| 用户说 | 跳转到 |
|---------------|-------|
| `audit` / "就标记它" / "不要修改任何东西" | [references/commands/cleanup.md](references/commands/cleanup.md#report-only) |
| `review` / "发布前再审查一下这个" | [references/commands/cleanup.md](references/commands/cleanup.md#report-only) |
| `harvest` / "你有什么我的写作？" | [references/commands/teach.md](references/commands/teach.md#1-gather-samples-harvest) |
| `calibrate` / "A/B游戏" / "考考我的语音" | [references/commands/teach.md](references/commands/teach.md#calibrate) |
| `refine` / "不断推进直到听起来像我" | [references/commands/mimic.md](references/commands/mimic.md#refine) |
| 语音检查 / "这个听起来像我吗？" | [references/commands/mimic.md](references/commands/mimic.md#voice-check) |
| "发现了一个新的AI-ism" / "添加这个特征" | [references/commands/contribute.md](references/commands/contribute.md) |

## 界面

| 参数 | 描述 | 默认 |
|----------|-------------|---------|
| `--preset` | 语音风格：`crisp`，`warm`，`expert`，`story` | `crisp` |
| `--strict` | 如果评分 < 32/40 则失败 | false |
| `--report` | 标记AI模式而不修改文本（cleanup） | false |
| 输入 | 要转换的文本（参数、文件路径或stdin） | 必填 |

在写入前从 `presets/` 读取一个预设。

| 预设 | 风格 | 适合 |
|--------|-------|----------|
| `crisp` | 简短、直接、无废话 | 技术写作、文档 |
| `warm` | 友好、对话式 | 邮件、博客文章 |
| `expert` | 权威、自信 | 思想领导力、文章 |
| `story` | 叙事流、展示而非讲述 | 案例研究、个人帖子 |

重写、保留、注册和验证行为仅存在于 `references/core-contract.md`；不要在这里重新创建或覆盖这些规则。

## 输出格式

对于快速重写，只返回清理后的文本。对于仅审核（cleanup `--report`）：

```markdown
## 发现的问题

- [引用问题，类别，严重性，为什么读起来像AI]

## 评估

- [哪些问题是明显的问题]
- [哪些问题是判断或依赖上下文的]
```

对于严格或请求的分析：

```markdown
## 转换后的文本

[人性化版本]

## 验证

- 约束：[X]/[Y] 保留
- AI模式：[N] 剩余（之前是 [M]）
- 结构：[通过/失败]
- 可读性：等级 [X]，句子差异 [Y]
- 变化：原始文本的 [X]%
- 评分：[X]/40
```

## 参考文件

| 文件 | 何时读取 |
|------|-------------|
| `references/commands/*.md` | 路由的命令流程（rewrite，cleanup，teach，mimic，contribute）。 |
| `references/pipeline.md` | 多代理 harness 的分层执行编排。 |
| `references/taboo-phrases.md` | 权威短语目录和扫描器类别。 |
| `references/fact-preservation.md` | 约束保留规则。 |
| `references/rewrite-examples.md` | 执行前/后的示例。 |
| `references/{mimic,harvest,calibrate}.md` | 由路由命令加载的语音工具内部。 |
| `references/{rubric,edit-library,maintenance}.md` | 严格评分、示例和贡献程序。 |
| `presets/*.md` | 语音特定增量。 |

## 维护

评估合约定义了产品。在 `evals/fixtures/contracts/scanner-examples.json` 中先评估添加扫描器示例；使用 `evals/adversarial-evals.json` 进行代理行为和路由。不要编辑遗留的 `evals/evals.json`。新模式需要一个假阴性示例和一个假阳性保护示例。代理行为变化需要一个 `skill` 行和一个重新生成的共享基准。对于具体程序（添加短语或结构，列出当前模式，与维基百科的AI写作标志页面同步），读取 `references/maintenance.md`。在野外发现了一个新的AI-ism？`references/commands/contribute.md` 将精确片段变成合约示例和结构化PR，保持用户确认门。
