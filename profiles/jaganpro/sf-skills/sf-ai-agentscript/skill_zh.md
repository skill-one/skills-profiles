# SF-AI-AgentScript 技能

Agent Script 是 **以代码优先** 的 Agentforce 代理路径。当用户正在编写 `.agent` 文件、构建有限状态主题流程，或需要重复控制路由、变量、操作和发布行为时，请使用此技能。

> 首先从最短的指南开始：[references/activation-checklist.md](references/activation-checklist.md)
>
> 从 Builder UI 迁移？使用 [references/migration-guide.md](references/migration-guide.md)

## 此技能拥有任务的条件

当工作涉及以下内容时，请使用 `sf-ai-agentscript`：

- 创建或编辑 `.agent` 文件
- 确定性主题路由、守卫和转换
- Agent Script CLI 工作流 (`sf agent generate authoring-bundle`, `sf agent validate authoring-bundle`, `sf agent preview`, `sf agent publish authoring-bundle`, `sf agent activate`)
- 插槽填充、指令解析、后操作循环或 FSM 设计

当用户处于以下情况时，请委派给其他技能：

- 维护 Builder 元数据代理 (`GenAiFunction`, `GenAiPlugin`, `GenAiPromptTemplate`, Models API, 自定义 Lightning 类型) → [sf-ai-agentforce](../sf-ai-agentforce/SKILL.md)
- 设计角色 / 语气 / 语音 → [sf-ai-agentforce-persona](../sf-ai-agentforce-persona/SKILL.md)
- 构建正式的测试计划或覆盖循环 → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)

如果用户处于 Builder Script / Canvas 视图，但结果是 `.agent` 作者捆绑包，请将工作保留在 `sf-ai-agentscript` 中。

---

## 确定性规模的调整

- 确定性是一个旋钮，而不是一个目的地。
- 当“大部分正确”不可接受时，请使用 Agent Script：门禁、强制顺序、显式状态转换、合规性或漂移控制。
- 如果工作流程是完全静态和线性的，请使用 Flow 或 Apex 而不是编写对话脚本。
- 优先选择确定性封装：确定性入口/门禁 → 灵活的中间部分 → 确定性收尾。
- 确定性越多并不一定更好。从最小化开始，然后仅硬化显示路由漂移、顺序失败或合规性风险的部分。

---

## 首先收集所需的上下文

请求或推断：

- 代理的目的以及 Agent Script 是否真正适合
- 服务代理与员工代理
- 目标组织和发布意图
- 预期操作 / 目标（Flow、Apex、PromptTemplate 等）
- 请求是作者、验证、预览还是发布故障排除

---

## 激活检查清单

在编写或修复任何 `.agent` 文件之前，请先验证以下内容：

1. **恰好一个 `start_agent` 块**
2. **没有混合制表符和空格**
3. **布尔值为 `True` / `False`**
4. **没有 `else if` 和嵌套 `if`**
5. **没有顶层 `actions:` 块**
6. **在 `set` 表达式中没有 `@inputs`**
7. **`linked` 变量没有默认值**
8. **`linked` 变量不使用 `object` / `list` 类型**
9. **使用显式的 `agent_type`**
10. **一致地使用 `@actions.` 前缀**
11. **仅当 `X` 是具有 `target:` 的主题级操作定义时，才使用 `run @actions.X`**
12. **不要直接基于原始 `@system_variables.user_input contains/startswith/endswith` 进行意图路由分支**
13. **在 prompt-template 输出中，优先使用 `is_displayable: False` + `is_used_by_planner: True`**
14. **不要假设 `@outputs.X` 是标量 —— 在分支或赋值之前检查输出模式**

对于扩展版本，请使用 [references/activation-checklist.md](references/activation-checklist.md)。

---

## 不可协商的规则

### 1) 服务代理与员工代理

| 代理类型 | 必须的 | 禁止 / 谨慎 |
|---|---|---|
| `AgentforceServiceAgent` | 合法的 `default_agent_user`、正确的权限、目标组织检查、优先使用 `sf org create agent-user` | 没有真实的 Einstein Agent User 就发布 |
| `AgentforceEmployeeAgent` | 显式的 `agent_type` | 提供 `default_agent_user` |

完整详细信息：[references/agent-user-setup.md](references/agent-user-setup.md)

### 2) 推荐的顶层块约定

使用此顺序在技能的示例和审核中保持一致性：

```yaml
config:
variables:
system:
connection:
knowledge:
language:
start_agent:
topic:
```

官方 Salesforce 材料以不同的顺序呈现顶层块，并且本地验证证据表明多个排序可以编译。将此视为一种样式约定，而不是独立的正确性或发布阻止器。

### 3) 关键配置字段

| 字段 | 规则 |
|---|---|
| `developer_name` | 必须与文件夹 / 捆绑包名称匹配 |
| `description` | 公共文档/示例应使用此配置字段 |
| `agent_type` | 每次都显式设置 |
| `default_agent_user` | 服务代理仅限 |

本地工具也接受 `agent_description:` 以兼容性，但此技能的公共文档和示例应优先使用 `description:`。

### 4) 应视为立即失败的语法阻止器

- `else if`
- 嵌套 `if`
- 仅注释的 `if` 正文
- 顶层 `actions:`
- 调用级 `inputs:` / `outputs:` 块
- 保留变量/字段名称，如 `description` 和 `label`

规范规则集：[references/syntax-reference.md](references/syntax-reference.md) 和 [references/validator-rule-catalog.md](references/validator-rule-catalog.md)

---

## 推荐的工作流程

## 推荐的作者工作流程

### 第一阶段 — 设计代理
- 确定问题是否足够确定性以使用 Agent Script
- 将主题建模为状态，将转换建模为边
- 仅定义您真正需要的变量

### 第二阶段 — 编写 `.agent`
- 首先创建 `config`、`system`、`start_agent` 和主题
- 添加具有完整 `inputs:` 和 `outputs:` 的目标支持操作
- 使用 `available when` 进行确定性工具可见性
- 在分支之前将原始意图/验证信号归一化为布尔值或枚举；避免对原始用户话语进行直接子字符串检查以进行关键控制流
- 将后操作检查保持在 `instructions:` 的**顶部**

### 默认作者立场

- 默认直接 `.agent` 作者和源代码控制中的编辑。
- 仅当用户需要本地捆绑包脚手架时，才使用 `sf agent generate authoring-bundle --no-spec`。
- 将 `sf agent generate agent-spec` 视为可选的构思 / 主题引导，而不是默认工作流程。
- 不要将 Agent Script 用户引导至 `sf agent create` 或 `sf agent generate template`。

### 第三阶段 — 持续验证
验证已在写入/编辑时自动运行。在发布之前使用 CLI：

```bash
sf agent validate authoring-bundle --api-name MyAgent -o TARGET_ORG --json
```

验证器涵盖结构、运行时陷阱、目标就绪和与组织相关的服务代理检查。规则 ID 位于 [references/validator-rule-catalog.md](references/validator-rule-catalog.md)。

### 第四阶段 — 预览冒烟测试
在发布之前使用预览循环：
- 推导 3–5 个冒烟话语
- 使用 `start` / `send` / `end` 子命令启动预览，而不是裸 `sf agent preview`
- 如果您使用 `--authoring-bundle`，请始终明确选择模式：`--simulate-actions` 或 `--use-live-actions`
- 检查主题路由 / 操作调用 / 安全性 / 根基
- 最多重试 3 次

完整循环：[references/preview-test-loop.md](references/preview-test-loop.md)

### 第五阶段 — 发布和激活
```bash
sf agent publish authoring-bundle --api-name MyAgent -o TARGET_ORG --json

# 手动激活
sf agent activate --api-name MyAgent -o TARGET_ORG

# CI / 确定性激活已知 BotVersion
sf agent activate --api-name MyAgent --version <n> -o TARGET_ORG --json
```

发布**不会**激活代理。
对于自动化，请优先使用 `--version <n> --json`，以便激活是确定性的且机器可读的。

---

## 确定性构建块

这些作为代码执行，而不是建议：
- 条件语句
- `available when` 守卫
- 变量检查
- 直接 `set` / `transition to`
- `run @actions.X` **仅当 `X` 是具有 `target:` 的主题级目标支持定义时**
- 变量注入到面向 LLM 的文本

重要区别：
- **确定性**：`set`、`transition to` 和 `run @actions.X` 用于目标支持的主题操作
- **LLM 指向**：`reasoning.actions:` 便利 / 委托，如 `@utils.setVariables`、`@utils.transition` 和 `{!@actions.X}` 指令引用

如果您需要确定性行为，而当前将其建模为推理级便利，则：
- 重新编写它为直接 `set` / `transition to`，或
- 将其提升为主题级目标支持操作并 `run` 该操作

参见 [references/instruction-resolution.md](references/instruction-resolution.md) 和 [references/architecture-patterns.md](references/architecture-patterns.md)。

---

## 跨技能集成

## 跨技能编排

| 任务 | 委托给 | 原因 |
|---|---|---|
| 构建 `flow://` 目标 | [sf-flow](../sf-flow/SKILL.md) | Flow 创建 / 验证 |
| 构建 Apex 操作目标 | [sf-apex](../sf-apex/SKILL.md) | `@InvocableMethod` 和业务逻辑 |
| 测试主题路由 / 操作 | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md) | 正式测试规范和修复循环 |
| 部署 / 发布 | [sf-deploy](../sf-deploy/SKILL.md) | 部署编排 |

---

## 高信号失败模式

| 症状 | 可能的原因 | 阅读下一项 |
|---|---|---|
| 发布期间出现 `Internal Error` | 无效的服务代理用户或缺少操作 I/O | [references/agent-user-setup.md](references/agent-user-setup.md), [references/actions-reference.md](references/actions-reference.md) |
| prompt template 操作出现 `invalid input/output parameters` | **目标模板处于草稿状态** — 首先激活它 | [references/action-prompt-templates.md](references/action-prompt-templates.md#draft-template-publish-errors) |
| 解析器拒绝条件语句 | `else if`、嵌套 `if`、空的 `if` 正文 | [references/syntax-reference.md](references/syntax-reference.md) |
| 操作目标问题 | 缺少 Flow / Apex 目标、Flow 无效、坏模式 | [references/actions-reference.md](references/actions-reference.md) |
| prompt template 运行但用户看到空白响应 | prompt 输出标记 `is_displayable: True` | [references/production-gotchas.md](references/production-gotchas.md), [references/action-prompt-templates.md](references/action-prompt-templates.md) |
| prompt 操作运行但规划器行为像输出缺失 | 输出对直接显示隐藏但规划器可见 | [references/production-gotchas.md](references/production-gotchas.md), [references/actions-reference.md](references/actions-reference.md) |
| `ACTION_NOT_IN_SCOPE` 在 `run @actions.X` 上 | `run` 指向工具 / 委托 / 未解析的操作，而不是主题级目标支持定义 | [references/syntax-reference.md](references/syntax-reference.md), [references/instruction-resolution.md](references/instruction-resolution.md) |
| 确定性取消 / 修订 / URL 检查行为不一致 | 原始 `@system_variables.user_input` 匹配或字符串方法守卫被用作关键控制流验证 | [references/syntax-reference.md](references/syntax-reference.md), [references/production-gotchas.md](references/production-gotchas.md) |
| `@outputs.X` 比较或赋值行为异常 | 操作输出是结构化的/包装的，而不是纯标量 | [references/actions-reference.md](references/actions-reference.md), [references/syntax-reference.md](references/syntax-reference.md) |
| 预览和运行时不一致 | 链接变量 / 上下文 / 已知平台问题 | [references/known-issues.md](references/known-issues.md) |
| 验证通过但发布失败 | 组织特定的用户 / 权限 / 检索后问题 | [references/production-gotchas.md](references/production-gotchas.md), [references/cli-guide.md](references/cli-guide.md) |

---

## 参考地图

### 从这里开始
- [references/activation-checklist.md](references/activation-checklist.md)
- [references/syntax-reference.md](references/syntax-reference.md)
- [references/actions-reference.md](references/actions-reference.md)

### 发布 / 运行时安全
- [references/agent-user-setup.md](references/agent-user-setup.md)
- [references/production-gotchas.md](references/production-gotchas.md)
- [references/customer-web-client.md](references/customer-web-client.md)
- [references/known-issues.md](references/known-issues.md)

### 架构 / 推理
- [references/architecture-patterns.md](references/architecture-patterns.md)
- [references/instruction-resolution.md](references/instruction-resolution.md)
- [references/fsm-architecture.md](references/fsm-architecture.md)
- [references/patterns-quick-ref.md](references/patterns-quick-ref.md)

### 验证 / 测试 / 调试
- [references/preview-test-loop.md](references/preview-test-loop.md)
- [references/testing-guide.md](references/testing-guide.md)
- [references/debugging-guide.md](references/debugging-guide.md)
- [references/validator-rule-catalog.md](references/validator-rule-catalog.md)

### 示例 / 脚手架
- [references/minimal-examples.md](references/minimal-examples.md)
- [references/migration-guide.md](references/migration-guide.md)
- [assets/](assets/)
- [assets/agents/](assets/agents/)
- [assets/patterns/](assets/patterns/)

### 项目文档
- [references/version-history.md](references/version-history.md)
- [references/sources.md](references/sources.md)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 放心部署 |
| 75–89 | 良好，审核警告 |
| 60–74 | 需要集中修订 |
| < 60 | 阻止发布 |

完整标准：[references/scoring-rubric.md](references/scoring-rubric.md)

---

## 官方资源

- [Agent Script 文档](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-script.html)
- [Agent Script 配方](https://github.com/trailheadapps/agent-script-recipes)
- [Agentforce DX 指南](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx.html)
- [references/official-sources.md](references/official-sources.md)
