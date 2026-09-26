# sf-ai-agentforce：标准 Agentforce 平台开发

使用此技能用于 **Setup UI / Agent Builder** 路径：声明式主题、Builder 管理的操作、`GenAiFunction` / `GenAiPlugin` 元数据、**存储为 `GenAiPromptTemplate` 元数据的 Prompt Builder 模板**、从 Apex 使用模型 API，以及自定义 Lightning 类型。

> 对于新的代码优先代理开发，请优先使用 [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)。
>
> 如果工作生成或编辑 `.agent` 文件——包括 Builder Script / Canvas 工作生成的作者捆绑包——请使用 [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)。

## 此技能拥有任务的条件

当用户是以下情况时，使用 `sf-ai-agentforce`：
- 维护现有的基于 Builder 的代理
- 在 Setup → Agentforce → Agents 中工作
- 创建或修复 `GenAiFunction`、`GenAiPlugin` 或 `GenAiPromptTemplate` 元数据
- 将 Builder 主题连接到 Flow / Apex / Prompt Builder 操作
- 在基于 Builder 的代理上下文中使用模型 API 或 LightningTypeBundle

**不要**用于：
- `.agent` 文件或确定性 FSM 设计 → [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- 代理测试套件和覆盖循环 → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- persona / 语音设计 → [sf-ai-agentforce-persona](../sf-ai-agentforce-persona/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 这是否是基于 Builder / Setup UI 的项目还是代码优先的 Agent Script 项目
- 用户是否正在编辑 Builder 元数据还是 `.agent` 作者捆绑包
- 代理类型：服务代理还是员工代理
- 工作是否针对主题、操作、Prompt Builder 模板、模型 API 或自定义 Lightning 类型
- 已经存在的支持性 Flow / Apex / 元数据依赖项
- 用户是否需要作者帮助、发布帮助或故障排除

---

## 两条 Agentforce 路径

| 路径 | 技能 | 最佳匹配 |
|---|---|---|
| Builder 元数据路径 | `sf-ai-agentforce` | 声明式维护、现有的 Builder 代理、元数据驱动的操作注册 |
| Agent Script 作者捆绑包路径 | `sf-ai-agentscript` | 代码优先的 `.agent` 作者、确定性路由、版本控制的代理逻辑 |

如果用户从零开始并希望对流程/状态有强控制，请路由到 Agent Script。

---

## Builder 工作流摘要

1. 确认这是一个 **Builder / Setup UI** 项目
2. 选择服务代理还是员工代理
3. 对于服务代理，配置运行用户（优先使用 `sf org create agent-user`）
4. 对于员工代理，规划权限集 `<agentAccesses>` 中的可见性
5. 定义具有强描述、范围和说明的主题
6. 准备支持性操作（Flow、Apex、Prompt Builder 模板）
7. 小心配置输入 / 输出
8. 验证依赖项和模板状态
9. 发布，然后激活

扩展工作流：[references/builder-workflow.md](references/builder-workflow.md)

---

## 关键平台规则

### 主题质量很重要
主题描述是规划器的路由指令。它们必须：
- 具体
- 基于场景
- 与兄弟主题不重叠

### 操作是围绕真实目标的包装
| 目标类型 | 典型用途 | 注册方式 |
|---|---|---|
| Flow | Builder 操作的最安全默认值 | `GenAiFunction` |
| Apex | 通过 `@InvocableMethod` 的复杂业务逻辑 | `GenAiFunction` |
| Prompt Builder 模板 | 生成的摘要 / 草稿 / 建议 | `GenAiFunction` |

### Prompt Template 与 GenAiPromptTemplate
- **Prompt Template** 是在 Prompt Builder 中使用的英文 / UI 术语。
- **`GenAiPromptTemplate`** 是当前元数据 API 类型，用于源驱动的模板工作。
- 优先使用当前源格式：`genAiPromptTemplates/*.genAiPromptTemplate-meta.xml`。
- 对于灵活的 Prompt Builder 模板，请围绕 **5 个输入的最大值** 进行规划，并在需要时合并输入。
- Prompt 内容应使用当前的合并字段形状引用输入，例如 `{!$Input:TargetRecord}` 或 `{!$Input:AdditionalContext}`。

### 支持性元数据首先部署
在发布代理本身之前，部署支持性堆栈：
1. 如果需要，元数据 / 字段
2. 如果需要，Apex
3. 如果需要，Flow
4. `GenAiPromptTemplate` / `GenAiFunction` / `GenAiPlugin`
5. 然后发布代理

### 服务代理运行用户
对于服务代理，优先使用原生 GA 命令：
`sf org create agent-user --target-org <alias> --json`
使用返回的用户名在运行用户配置中。

### 员工代理可见性
对于员工代理，确保最终用户收到包含 `<agentAccesses>` 的权限集。如果没有，代理可以处于活动状态，但在 Lightning Experience 中仍然不可见。
参见 [../sf-permissions/references/agent-access-guide.md](../sf-permissions/references/agent-access-guide.md)。

### 发布不会激活
发布后，单独运行 `sf agent activate`。
对于自动化，请优先使用 `sf agent activate --api-name <AgentName> --version <n> --target-org <alias> --json`，以便发布是确定性的和机器可读的。

---

## 元数据指南

### GenAiFunction
在注册单个可调用操作时使用。验证：
- 目标存在
- 目标处于活动状态 / 可部署
- 输入名称与目标合约匹配
- 输出名称与目标合约匹配
- 能力文本清楚地说明何时应使用该操作

### GenAiPlugin
在将相关函数分组到一个逻辑包中使用。

### GenAiPromptTemplate
用于生成内容，而不是确定性业务规则。

优先使用当前的元数据形状：
- 元数据类型：`GenAiPromptTemplate`
- 文件夹：`genAiPromptTemplates/`
- 文件后缀：`.genAiPromptTemplate-meta.xml`
- 内容位于 `templateVersions` 下
- 在连接依赖它们的操作之前使用已发布的模板版本

### Models API
当解决方案属于 Apex 驱动的 AI 管理而不是 Builder 仅操作时使用。

### 自定义 Lightning 类型
当操作需要更丰富的结构化输入或输出表示时使用。

扩展参考：
- [references/metadata-reference.md](references/metadata-reference.md)
- [references/genaiprompttemplate.md](references/genaiprompttemplate.md)

---

## 跨技能集成

### 推荐的编排顺序

```text
sf-metadata → sf-apex → sf-flow → sf-ai-agentforce → sf-deploy
```

### 必需的委托
| 需求 | 委托给 | 原因 |
|---|---|---|
| 创建 / 修复 Flow | [sf-flow](../sf-flow/SKILL.md) | 操作目标创建和 Flow 验证 |
| 创建 / 修复 Apex 操作 | [sf-apex](../sf-apex/SKILL.md) | `@InvocableMethod` 和 Apex 正确性 |
| 部署 / 发布 | [sf-deploy](../sf-deploy/SKILL.md) | 部署编排 |
| 测试代理 | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md) | 正式测试执行和断言 |
| 员工代理可见性 / 访问 | [sf-permissions](../sf-permissions/SKILL.md) | 权限集 `<agentAccesses>` 设置 |

---

## 高信号失败模式

| 症状 | 可能的原因 | 读取下一项 |
|---|---|---|
| 操作在 Builder 中不可用 | 目标元数据缺失或未部署 | [references/metadata-reference.md](references/metadata-reference.md) |
| Prompt 操作在发布或激活期间失败 | 模板是草稿、缺少输入或使用旧的元数据形状 | [references/genaiprompttemplate.md](references/genaiprompttemplate.md) |
| 需要超过 5 个模板输入 | 灵活模板输入限制被触发 | [references/genaiprompttemplate.md](references/genaiprompttemplate.md) |
| Apex AI 逻辑超时 | 模型 API 工作放置在错误的上下文中 | [references/models-api.md](references/models-api.md) |
| 丰富的输入/输出 UI 未渲染 | Lightning 类型配置或先决条件不完整 | [references/custom-lightning-types.md](references/custom-lightning-types.md) |
| 代理发布但不可用 | 忘记显式激活 | [references/cli-commands.md](references/cli-commands.md) |
| 服务代理发布/运行时失败 | 缺失或无效的运行用户 | [../sf-ai-agentscript/references/agent-user-setup.md](../sf-ai-agentscript/references/agent-user-setup.md) |
| 员工代理处于活动状态但对用户不可见 | 缺失 `<agentAccesses>` 权限集 | [../sf-permissions/references/agent-access-guide.md](../sf-permissions/references/agent-access-guide.md) |

---

## 参考地图

### 从这里开始
- [references/builder-workflow.md](references/builder-workflow.md)
- [references/metadata-reference.md](references/metadata-reference.md)
- [references/genaiprompttemplate.md](references/genaiprompttemplate.md)
- [references/cli-commands.md](references/cli-commands.md)

### 术语和模板规划
- [references/prompt-templates.md](references/prompt-templates.md)
- [references/models-api.md](references/models-api.md)
- [references/custom-lightning-types.md](references/custom-lightning-types.md)

### 评分标准
- [references/scoring-rubric.md](references/scoring-rubric.md)

### 跨技能阅读
- [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)
- [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- [sf-flow](../sf-flow/SKILL.md)
- [sf-apex](../sf-apex/SKILL.md)
- [sf-permissions](../sf-permissions/SKILL.md)
- [sf-deploy](../sf-deploy/SKILL.md)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 准备部署 |
| 80–89 | 强大，只需少量清理 |
| 70–79 | 部署前审查 |
| 60–69 | 需要工作 |
| < 60 | 阻止部署 |

完整评分标准：[references/scoring-rubric.md](references/scoring-rubric.md)
