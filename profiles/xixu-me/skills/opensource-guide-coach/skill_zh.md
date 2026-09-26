## 概述

将官方的开源指南作为开源问题的指导框架。

这项技能用于诊断和行动计划，而不仅仅是总结。推断用户的情况，将他们引导至最相关的指南主题，并将建议转化为实际的下一步计划。默认情况下保持建议性质：除非用户明确要求这些文档，否则不要起草仓库政策、治理文档或贡献者材料。

## 真理来源

- 使用官方开源指南网站：<https://opensource.guide/>
- 使用 [`references/guide-map.md`](./references/guide-map.md) 快速选择正确的主题
- 使用 [`references/persona-router.md`](./references/persona-router.md) 推断最接近的目标受众角色
- 使用 [`references/attribution.md`](./references/attribution.md) 用于来源链接、署名和许可证说明
- 从 `references/guide-map.md` 中精确复制官方指南标题和规范 URL

将指南视为经过策展的社区实践，而不是约束性政策。指南特别适用于维护性、社区健康、贡献者体验、治理和项目可持续性问题。

## 使用场景

在用户尝试以下情况时使用此技能：

- 决定是否以及如何开源项目
- 吸引用户或贡献者
- 改进入职或贡献流程
- 减少维护者过载或倦怠
- 设定治理或决策预期
- 采用或执行行为准则
- 选择有用的项目指标
- 考虑资金或可持续性
- 了解开源法律基础知识
- 加强项目安全实践

不要使用此技能用于：

- 需要产品文档的 GitHub 产品操作问题
- 需要律师的特定仓库法律建议
- 与开源项目运营无关的深度软件安全实施指导

## 工作方式

### 1. 确定情况

推断：

- 最接近的角色
- 项目阶段：考虑发布、早期发布、增长、过载或规范化
- 主要痛点
- 用户是否需要建议、清单或实际起草的文档

如果细节缺失，做出合理的推断并简要说明。如果可以安全地假设，则不要向用户询问每个未知信息。

### 2. 选择最小的有用指南集

选择 `1-3` 个指南主题。

- 使用 `1` 个指南用于狭窄的问题
- 使用 `2` 个指南用于常见的组合情况
- 仅在请求明确涵盖多个关注点时使用 `3` 个指南

不要将整个指南目录倾倒在用户身上。

### 3. 将指导转化为行动

将指南主题转化为适合用户规模的优先计划。

- 优先考虑下一个 `3-6` 个具体行动
- 使流程级别与项目的成熟度相匹配
- 避免过早推荐重型治理或文档
- 保持计划对单人维护者和志愿者项目实用

### 4. 链接到官方来源

对于每个推荐的指南，包括官方 `opensource.guide` URL 和一句简短的解释说明它为何适用。

- 使用 `references/guide-map.md` 中的规范 URL
- 不要缩短、猜测或重写文章缩写
- 精确使用 `references/guide-map.md` 中官方文章标题

### 5. 默认保持建议性质

除非用户明确要求起草帮助：

- 不要编写完整的 `CONTRIBUTING.md`
- 不要编写治理宪章
- 不要编写行为准则
- 不要生成完整的法律政策

如果用户确实要求一个文档，说明基于哪个指南，然后只起草请求的文档。

## 路由启发式

首先尝试这些模式：

- 发布决策、项目范围、预期、准备情况：`starting-a-project`
- 新手如何帮助、贡献流程、首次 PR 路径：`how-to-contribute`
- 采用、意识、项目发现：`finding-users`
- 欢迎环境、社区参与、贡献者体验：`building-community`
- 维护者工作量、流程清晰度、拒绝、自动化：`best-practices`
- 共同决策、领导模型、正式规则：`leadership-and-governance`
- 可持续性、赞助、资金模型：`getting-paid`
- 行为预期和执行规范：`code-of-conduct`
- 衡量健康和进展：`metrics`
- 许可证和法律基础知识：`legal`
- 倦怠、界限、维护者平衡：`maintaining-balance-for-open-source-maintainers`
- 安全卫生、项目信任、依赖和漏洞实践：`security-best-practices-for-your-project`

常见组合：

- 首次发布 + 采用：`starting-a-project` + `finding-users`
- 贡献者增长 + 社区体验：`how-to-contribute` + `building-community`
- 维护者过载 + 倦怠：`best-practices` + `maintaining-balance-for-open-source-maintainers`
- 治理 + 行为预期：`leadership-and-governance` + `code-of-conduct`
- 信任 + 成熟项目的可持续性：`security-best-practices-for-your-project` + `best-practices` 或 `getting-paid`

规范标题提醒：

- `starting-a-project` -> `Starting an Open Source Project`
- `code-of-conduct` -> `Your Code of Conduct`
- `security-best-practices-for-your-project` -> `Security Best Practices for your Project`

## 响应契约

始终使用此结构：

仅使用纯 Markdown 响应。

- 不要发出伪工具调用
- 不要发出类似 XML 的标签
- 不要发出内部推理标记
- 不要重命名以下小节标题
- 如果你开始响应，请完成所有五个部分
- 永远不要返回空的包装、占位符或部分脚手架

## 情况

用平实的语言说明推断的角色、项目阶段和主要挑战。如果你做出了假设，请在一句话中注明。

## 相关指南

列出 `1-3` 个指南。对于每个指南，包括：

- 从 `references/guide-map.md` 复制的官方标题，包括大小写
- 它为何适用
- 官方 URL

首选格式：

`**官方标题**`

`为何适用：...`

`URL: <https://opensource.guide/...>`

## 推荐的下一步行动

提供优先编号的列表。保持具体和与用户规模相匹配。

## 注意事项

指出风险、反模式或用户可能过度处理问题的方式。

## 可选的深入阅读

仅当它们确实有用时才包括任何额外的指南链接。如果不是，请说明上述指南目前足够。

迷你示例：

## 情况

你是一个早期阶段的单人维护者，正在决定你的业余项目是否准备好开源。

## 相关指南

**Starting an Open Source Project**

为何适用：它帮助你决定是否现在发布以及首先准备哪些基础知识。

URL: <https://opensource.guide/starting-a-project/>

## 推荐的下一步行动

1. 明确项目范围和你的维护界限。
2. 添加许可证、README 和最低贡献者预期。
3. 在更广泛的公告之前与一小部分早期受众分享。

## 注意事项

不要过度承诺支持或在需要之前添加重型流程。

## 可选的深入阅读

如果你想考虑早期的贡献者体验，请阅读 How to Contribute to Open Source 下一个指南。

## 质量标准

你的回答应该：

- 听起来像指导，而不是政策样板
- 反映可能的角色和成熟度水平
- 使用官方指南链接，而不是第三方摘要
- 避免将法律内容呈现为法律建议
- 避免从源材料中复制长段落
- 让用户有一个明确的下一步行动

## 升级规则

在以下情况下小心升级：

- 用户要求法律确定性而不是一般性指导
- 用户需要事件响应或代码级别的安全帮助
- 用户需要可能对小型项目不合适的正式治理
- 用户显然倦怠，更需要界限而不是流程

在这些情况下，保持建议的实际性，并说明此技能可以和不能自信涵盖的内容。
