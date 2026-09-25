# LaunchDarkly 标志目标与发布

您正在使用一个技能，它将指导您如何更改哪些用户可以看到某个功能标志。您的工作是了解标志的当前状态，确定用户想要的目标方法，安全地做出更改，并验证结果状态。

## 前置条件

此技能需要您的环境中配置了远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `get-flag`：在做出更改前了解当前状态
- `toggle-flag`：在环境中开启或关闭标志的目标
- `update-rollout`：更改默认规则（fallthrough）的变体或百分比发布
- `update-targeting-rules`：添加、删除或修改自定义目标规则
- `update-individual-targets`：添加或删除特定用户/上下文以进行单独目标

**可选的 MCP 工具：**
- `copy-flag-config`：将目标配置从一个环境复制到另一个环境
- `create-approval-request`：当直接更改被阻止时创建审批请求
- `list-approval-requests`：检查标志的待审批请求
- `apply-approval-request`：应用已批准的审批请求

## 核心概念：评估顺序

在做出任何目标更改之前，了解 LaunchDarkly 如何评估标志。这决定了您的更改实际上会做什么：

1. **标志是关闭的** -> 向所有人提供 `offVariation`。其他任何事都不重要。
2. **单独目标** -> 如果上下文匹配特定的目标列表，则提供该变体。最高优先级。
3. **自定义规则** -> 从上到下评估规则。第一个匹配的规则获胜。
4. **默认规则（fallthrough）** -> 如果其他任何事都不匹配，则提供此变体或发布。

这意味着：如果您添加了一个目标规则，但标志是关闭的，则没有人会看到更改。如果您在默认规则上设置了百分比发布，但有单独目标，则该目标用户会绕过发布。

## 工作流程

### 第 1 步：了解当前状态

在更改任何内容之前，检查已配置的内容。

1. **确认环境。** “开启它”而不指定环境是模糊的。始终确认用户指的是哪个环境。默认情况下，询问而不是假设。
2. **获取标志。** 使用 `get-flag` 并指定目标环境来查看：
   - `on`：目标是否当前启用？
   - `fallthrough`：默认规则是什么？（变体或百分比发布）
   - `offVariation`：标志关闭时提供什么？
   - `rules`：任何自定义目标规则？
   - `targets`：任何单独目标用户/上下文？
   - `prerequisites`：此标志依赖于任何其他标志？
3. **评估复杂性。** 没有规则和没有单独目标的标志很简单。具有多个规则、目标和先决条件的标志需要更多小心。

### 第 2 步：确定正确方法

根据用户想要什么以及您发现的内容，选择正确的工具和策略。请参阅 [目标模式](references/targeting-patterns.md) 获取完整参考。

**常见场景：**

| 用户想要 | 工具 | 备注 |
|-----------|------|-------|
| “开启它” | `toggle-flag` with `on: true` | 最简单的更改 |
| “关闭它” | `toggle-flag` with `on: false` | 向所有人提供 offVariation |
| “发布到 X%” | `update-rollout` with `rolloutType: "percentage"` | 权重必须总和为 100 |
| “为测试用户启用” | `update-targeting-rules`：添加一个具有子句的规则 | 规则在内部进行 AND 运算，在之间进行 OR 运算 |
| “添加特定用户” | `update-individual-targets` | 最高优先级，覆盖所有规则 |

**在编写规则、单独目标或百分比发布之前，确认上下文是否支持它。** 一个命名为标志评估不携带的上下文类型的规则会静默地不匹配；单独目标匹配上下文 **键**，而不是像电子邮件这样的属性；发布只能按标志读取时存在的类型进行分桶。请参阅 [上下文可用性](references/context-availability.md) 以选择一个实际会触发的上下文。
| “完全发布” | `update-rollout` with `rolloutType: "variation"` | 向所有人提供一个变体 |
| “从测试环境复制” | `copy-flag-config` | 将测试配置提升到生产环境 |

### 第 3 步：运行安全检查清单

在应用更改之前，尤其是在生产环境中，请运行 [安全检查清单](references/safety-checklist.md)。关键检查：

1. **正确的环境？** 再次确认您正在针对预期的环境。
2. **需要审批吗？** 某些环境需要审批工作流。如果任何变异工具返回 `requiresApproval: true`：
   - 告知用户此环境需要审批。
   - 如果提供了 `approvalUrl`，请共享。
   - 提供使用 `create-approval-request` 创建审批请求的选项，使用被阻止响应中的 `instructions` 字段（在响应中返回）。
   - 不要尝试绕过审批或自动批准。
   - 请参阅 [审批工作流](references/approval-workflows.md) 获取完整过程。
3. **先决条件标志？** 如果此标志有先决条件，则必须在目标按预期工作之前满足它们。
4. **规则顺序影响？** 如果添加规则，请考虑它们在评估顺序中的位置。规则从上到下评估，第一个匹配的规则获胜。
5. **添加评论。** 始终添加审计跟踪评论，尤其是对于生产环境的更改。

### 第 4 步：应用更改

使用适当的工具进行更改。关键注意事项：

- **`toggle-flag`**：指定 `on: true` 或 `on: false`、`env` 和一个 `comment`。
- **`update-rollout`**：使用 `rolloutType: "percentage"` 和人类友好的权重（例如，80 表示 80%）总和为 100，或 `rolloutType: "variation"` 和一个 `variationIndex`。
- **`update-targeting-rules`**：说明支持 `addRule`、`removeRule`、`updateRuleVariationOrRollout`、`addClauses`、`removeClauses`、`reorderRules`。
- **`update-individual-targets`**：说明支持 `addTargets`、`removeTargets`、`addContextTargets`、`removeContextTargets`、`replaceTargets`。

请参阅 [目标模式](references/targeting-patterns.md) 获取详细的说明示例。

### 第 5 步：验证

应用更改后，确认结果：

1. **再次获取更新后的标志。** 使用 `get-flag` 再次验证新状态。
2. **确认用户期望的结果。** 用 plain language 描述结果目标：
   - “标志现在在生产环境中开启，向 25% 的用户提供 `true`，向 75% 的用户提供 `false`。”
   - “测试用户现在看到变体 A。其他人获得默认（变体 B）。”
3. **检查副作用。** 如果有规则或单独目标，请确保更改与它们正确交互。

### 处理需要审批的环境

当任何变异工具返回 `requiresApproval: true` 时，直接更改被阻止，因为环境需要审批。请遵循 [审批工作流](references/approval-workflows.md) 参考：

1. **使用 `create-approval-request` 创建审批请求**，使用被阻止响应中的 `instructions`。
2. **告知用户** 关于待审批的情况并共享审批请求详情。
3. **如果需要**，稍后使用 `list-approval-requests` 检查审批状态。
4. **一旦审查者批准**，使用 `apply-approval-request` 应用请求（`reviewStatus` 是 "approved"）。
5. **应用后** 使用 `get-flag` 验证结果。

## 重要上下文

- **`update-rollout` 使用人类友好的百分比。** 传递 80 表示 80%，而不是 80000。该工具处理内部权重转换。
- **权重必须总和为 100。** 对于百分比发布，所有变体的权重必须正好总和为 100。
- **规则顺序很重要。** 规则从上到下评估。重新排序规则可能会改变行为，而不会改变任何单个规则。
- **单独目标是最高优先级的。** 它们覆盖所有规则和默认值。将某人添加为单独目标意味着规则不适用于他们。
- **“已发布”的标志仍然是开启的。** 状态为 "launched" 的标志正在向所有人提供单个变体。如果您想移除标志，请使用 [清理技能](../launchdarkly-flag-cleanup/SKILL.md)，而不是目标更改。

## 参考

- [目标模式](references/targeting-patterns.md)：发布策略、规则构建、单独目标以及跨环境复制
- [上下文可用性](references/context-availability.md)：规则、目标或发布可以使用哪些上下文类型/属性 — 匹配标志读取的表面类型，键与属性，以及发布分桶
- [安全检查清单](references/safety-checklist.md)：更改前的验证、审批工作流、环境意识
- [审批工作流](references/approval-workflows.md)：创建、检查和应用审批请求
