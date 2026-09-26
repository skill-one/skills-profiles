# AI中心技能

**这是用于AI/GenAI应用的工具**——既包括关于其行为的问题（提示/响应、质量、幻觉、护栏、安全、成本/令牌、错误、延迟——所有AI应用通过GenAI跨度/标签暴露的内容），也包括管理它们的操作（应用、评估/策略、策略↔应用链接、模型定价）。如果请求涉及AI应用或其GenAI遥测数据，请使用此技能。

Coralogix **AI中心**观察、评估和保护GenAI/LLM应用。此技能从两个来源回答关于AI应用的问题：

- **配置**（此技能的`cx ai-center`命令）：AI应用清单、配置的评估/策略、覆盖范围、自定义评估和模型定价——这些都不存在于跨度遥测数据中。
- **遥测数据**（GenAI跨度）：用户询问的内容、模型如何回答、成本、令牌、延迟、错误、工具调用以及评估/护栏判定结果——使用**`cx spans '<DataPrime>'`**查询。有关完整、可运行的查询库、跨度架构和剧本，请参阅[references/ai-center-queries.md](references/ai-center-queries.md)。

根据问题匹配来源：*"哪些应用缺少护栏"* → 配置（`cx ai-center applications list`）；*"我的聊天机器人用户在问什么"* → 遥测数据（`cx spans '…'`，从GenAI跨度中读取对话）。某些问题需要**两者**——例如*"我的聊天机器人的PII策略是否真的捕获了PII?"*将配置（策略是否启用）与遥测数据（PII判定结果+消息）结合起来。

---

## 破坏性操作安全

所有写操作（`create`、`update`、`delete`、`add`、`remove`、`set`）都需要交互式确认。`ai-center`是一个**有风险**的命令，因此写操作也受`~/.cx/config.toml`中`allow_risky_commands`的约束。要在脚本中跳过提示，请传递`--yes`。

**重要提示：未经明确用户批准，切勿传递`--yes`。**在执行任何写操作之前：
1. 向用户描述确切的操作（将要创建/修改/删除/链接的内容）。
2. 等待用户确认。
3. 然后才使用`--yes`执行。

读操作（`list`、`get`、`coverage`、`list-for-application`、`model-pricing get`）不需要确认，可以自由运行。

### 只读模式
使用`--read-only`（或`CX_READ_ONLY=1`）在CLI级别阻止所有写操作——适用于探索。

### 代理模式
在AI代理（Claude Code、Cursor、Codex等）中运行时，cx会检测到这一点，并立即停止（而不是显示一个会挂起的确认提示（没有人在那里输入y/n）），并显示一个错误，提示您获取用户批准，然后使用`--yes`重新运行。

### 无删除命令（设计如此）
CLI有意不暴露自定义评估策略、AI应用或模型定价的**删除**功能——尽管AI v3 API有这些删除端点，但`cx ai-center`不会显示它们。
- **自定义评估策略**：无法删除；要从应用中移除它，使用`custom-evaluations remove`（策略对象仍然存在，可以重新附加）。
- **模型定价**：无删除命令。它是**团队范围的**（不是按应用），因此要更改或清除它，请运行`model-pricing set`并使用新的映射（空映射`{}`清除所有覆盖）——`set`替换整个集合。

---

## 金科玉律

对于**内容**问题（质量、幻觉、情感、主题），请阅读实际对话并引用`traceID`——不要仅依赖判定标签。对话记录存储在两种约定之一中（`gen_ai.input.messages`/`output.messages`，或较旧的索引`gen_ai.prompt.<n>`/`completion.<n>`标签）；使用库中的**读取对话（内容问题）**查询来读取它，这些查询处理两者并排除系统提示和工具流量。完整指南：
[references/ai-center-queries.md](references/ai-center-queries.md)。

---

## CLI命令

**向用户显示名称；仅在内部使用UUID。**在显示结果时，请按其人类名称（应用/子系统、评估名称）引用应用和评估，而不是原始UUID。UUID仅在调用按ID或写命令时需要——从匹配的`list`命令自行解析它（切勿猜测或让用户粘贴UUID）。

### 应用（清单+受保护状态）

| 命令 | 目的 |
|------|------|
| `cx ai-center applications list` | 列出AI应用，包括`guardrailsIntegrated`（受保护）状态 |
| `cx ai-center applications list --evaluation-type <TYPE>` | 按评估类型过滤应用（可重复） |
| `cx ai-center applications list --page-size <N> --page-offset <N>` | 分页 |
| `cx ai-center applications get <application-id>` | 通过UUID获取一个应用 |

### 评估（应用的配置策略）

| 命令 | 目的 |
|------|------|
| `cx ai-center evaluations list` | 所有配置的评估 |
| `cx ai-center evaluations list --application <app> --subsystem <sub>` | 限制为一个应用（成对） |
| `cx ai-center evaluations list --evaluation-type <TYPE>` | 按类型过滤——`<TYPE>`是API枚举（例如`PII`、`TOXICITY`、`PROMPT_INJECTION`；来自`coverage`的键），**不是**小写形式 |
| `cx ai-center evaluations get <evaluation-id>` | 通过UUID获取一个评估 |
| `cx ai-center evaluations create --from-file eval.json` | 创建/启用一个评估 *(写)* |
| `cx ai-center evaluations update <evaluation-id> --from-file patch.json` | 部分更新 *(写)* |
| `cx ai-center evaluations delete <evaluation-id>` | 从其应用中移除一个评估 *(写)* |

### 自定义评估（策略）与应用链接

| 命令 | 目的 |
|------|------|
| `cx ai-center custom-evaluations list` | 所有自定义评估策略 |
| `cx ai-center custom-evaluations list-for-application <application-id>` | 链接到一个应用的策略 |
| `cx ai-center custom-evaluations create --from-file policy.json` | 创建一个自定义策略 *(写)* |
| `cx ai-center custom-evaluations update <id> --from-file patch.json` | 部分更新 *(写)* |
| `cx ai-center custom-evaluations add <evaluation-id> <application-id>` | 将策略附加到应用 *(写)* |
| `cx ai-center custom-evaluations remove <evaluation-id> <application-id>` | 分离（可逆） *(写)* |

> **按ID仅限预构建。** `evaluations get <id>`获取一个**预构建/配置**的评估。自定义策略**没有**按ID获取——通过`custom-evaluations list` / `list-for-application`查找，并按`id`/名称匹配。

### 覆盖范围与模型定价

| 命令 | 目的 |
|------|------|
| `cx ai-center coverage` | 每个评估类型→使用它的应用数量（覆盖范围/差距分析） |
| `cx ai-center model-pricing get` | 团队的自定义按模型定价覆盖 |
| `cx ai-center model-pricing set --from-file prices.json` | 设置团队定价（团队范围，新数据仅） *(写)* |

`evaluations`和`custom-evaluations`的`--from-file`正文与AI v3 API形状逐字匹配；使用`-`从stdin读取JSON。对于`evaluations create`，`target`是**必需**的，必须是大写（`PROMPT`或`RESPONSE`）；对于`custom-evaluations create`，`name`、`instructions`和`policyType`是必需的。**例外**：`model-pricing set`只需原始`model→price`映射——cx会为您将其包装为`{"prices": …}`，因此**不要**包含外部的`prices`包。每个模型映射到一个价格对象；所有四个字段都是可选的双精度浮点数（每**一百万**令牌的美元），省略不应用的字段：

```json
{
  "gpt-4o": {
    "inputPricePerMillionTokens": 2.5,
    "outputPricePerMillionTokens": 10,
    "cacheReadPricePerMillionTokens": 1.25,
    "cacheWritePricePerMillionTokens": 3.75
  }
}
```

空映射`{}`清除所有覆盖（设置替换整个集合——它是团队范围的，新数据仅）。`model-pricing get`返回包装`{ "pricing": { "id", "companyId", "prices": { … } } }`——每个模型的覆盖位于`prices`下（未设置时为空）。

---

## 常见工作流

### 清单与护栏差距
```bash
# 哪些应用没有被保护？
cx ai-center applications list -o json | jq '[.[] | select(.guardrailsIntegrated==false)]'
```

### 在应用上启用策略（写——先确认！）
```bash
# 1. 向用户描述；2. 获取批准；3. 然后执行：
cx ai-center evaluations create --from-file eval.json --yes
# eval.json: { "application": "...", "subsystem": "...", "target": "PROMPT", "config": { "<type>": {...} }, "isEnabled": true }
# `target`是必需的，必须是UPPERCASE——"PROMPT"或"RESPONSE"（API拒绝小写/缺失target）。
```

### 读取实际对话（遥测数据，不是配置）
使用`cx spans`和[references/ai-center-queries.md](references/ai-center-queries.md)中的查询库——读取消息、成本、延迟、错误、工具调用和按用户分析。

---

## 关键原则

- **配置与遥测数据**：清单 / 评估 / 策略 / 覆盖范围 / 定价 → `cx ai-center`；内容 / 成本 / 延迟 / 错误 / 判定结果 → 通过`cx spans`的GenAI跨度。不要用另一个来源回答一个问题。
- **写操作前确认。** 描述操作，获取批准，然后使用`--yes`运行。

---

## 相关技能

- `cx-telemetry-querying` — 通用日志/跨度/指标/DataPrime查询（这里是`cx spans`查询背后的引擎）。
- `cx-olly` — 对话式AI助手（`cx olly ask`）。
