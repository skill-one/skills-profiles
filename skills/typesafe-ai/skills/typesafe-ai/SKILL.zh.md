---
name: typesafe-ai
description: 使用 TypeSafe 构建人工智能软件：将人工智能智能拆分为可像编程原语一样使用的微小单元。其 System One 模型（包括 Jev）将自然语言和应用状态转化为代码可组合的类型化判断和概率。当需要可编程的常识功能、构思人工智能在应用中可能实现的可能性，或当 LLM 的提示与解析步骤可转化为结构化决策时，即可使用。应用场景包括路由、排序、提取、验证和交互式体验；这些只是起点，而非终点。查阅实时文档和食谱，以发现实用模式并探索新的组合方式。
---

# 使用 TypeSafe 构建

TypeSafe 将 AI 智能单元像编程原语一样使用：你可以将小的判断组合成更大的能力。它的 **System One 模型** 返回快速、专注的判断，软件可以直接消费。**Jev** 是 TypeSafe 的旗舰产品，也是第一个 System One 模型。它理解自然语言，并返回带类型的答案和概率，而不是生成文本或推理解释。代码拥有工作流程；模型在普通代码需要语义理解的地方提供可编程的常识。

## 阅读实时文档

**TypeSafe 实时文档是权威来源。将其作为任务的一部分来阅读。** 这项技能提供方向；文档包含当前概念、提示指导、API 合约、SDK 使用方法、模型、限制和示例。

- 从 [文档索引](https://docs.typesafe.ai/llms.txt) 开始，发现相关页面和食谱。使用有针对性的阅读，而不是加载整个网站。
- Mintlify 通过在页面路径后附加 `.md` 来提供 Markdown，例如 [如何使用 TypeSafe 构建](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)。从索引中跟随链接；在需要时将无扩展名的文档页面链接转换为 `.md`。相对于 `https://docs.typesafe.ai` 解析相对链接。
- 在编写集成之前，阅读当前的 API 或选择的 SDK 页面以及与设计相关的提问指导。对于新的工作流程，还要检查最接近的食谱：它通常比通用分类器显示更好的分解方式。
- 如果索引不可用，使用下方的直接链接或网站的导航。如果 Markdown 获取失败，尝试正常页面。如果实时访问不可用，使用可用的本地文档或安装的 SDK 类型，说明该限制，并避免编造与版本相关的细节。

| 任务 | 从这里开始；遵循相关细节 |
| --- | --- |
| 理解编程模型 | [System One](https://docs.typesafe.ai/concepts/system-one.md)，[构建指南](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md) |
| 探索要构建的内容 | [用例地图](https://docs.typesafe.ai/concepts/use-case-map.md)，然后从索引中选择相关的食谱 |
| 准备输入和问题 | [状态](https://docs.typesafe.ai/concepts/state.md)，[原语](https://docs.typesafe.ai/primitives.md)，然后选择的原语页面 |
| 决定如何处理不确定性 | [置信度](https://docs.typesafe.ai/confidence.md) |
| 编写 API 代码 | [HTTP API](https://docs.typesafe.ai/api.md)，[Python SDK](https://docs.typesafe.ai/sdk/python.md)，或 [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript.md) |
| 更新旧的集成 | [迁移指南](https://docs.typesafe.ai/migrating-to-v1.md) 和安装的 SDK 的当前参考 |

## 找到有用的形状

从用户期望的行为开始：应用程序将显示、选择、更改或移交什么？逆向工作到它需要的判断。将已知规则、计算、精确查找和执行保留在代码中。保留用户选择的技术栈和范围；在语义理解有助于的地方添加 TypeSafe。

在构思或选择架构时，考虑的不仅仅是分类。以下模式是起点：围绕用户的目标组合原语，包括那些不符合既定食谱的想法。

- **路由并填充已知参数。** 请求可以选择处理程序及其类型参数。提前提出有用的分支特定问题，并只消费相关的答案。探索 [函数调用](https://docs.typesafe.ai/cookbooks/function_calling.md) 和 [推测性发散](https://docs.typesafe.ai/patterns/fan-out.md)。
- **选择而不是生成。** 在代码中找到候选值或源跨度，使用判断选择预期的值，然后复制或规范化它。代码还可以将源文本组装成格式化文档或阅读指南。探索 [值提取](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) 和 [结构恢复](https://docs.typesafe.ai/cookbooks/autoformat.md)。
- **查找和判断证据。** 检索候选值，比较它们与查询的相关性，并选择有用的上下文。探索 [重新排序](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) 和 [分层分类](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md)。
- **将判断转换为可重用的数据。** 一次评分维度，然后让代码或用户控件更改权重、阈值、排名和视图。对于标记的结果，这些信号可以成为经典的 ML 特征。探索 [组合评分](https://docs.typesafe.ai/patterns/composite-scoring.md) 和 [特征发现](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md)。
- **验证和升级。** 检查特定声明或字段与其证据；将不确定或失败的案例发送给人员或推理模型。探索 [引用检查](https://docs.typesafe.ai/cookbooks/citation_check.md) 和 [提取级联](https://docs.typesafe.ai/cookbooks/sde_cascade.md)。
- **响应变化的状态。** 代码可以保留目标和观察结果，同时新的判断指导下一个有界步骤。将推断状态与观察事实区分开来，并在将结果应用于变化的情况之前检查新鲜度。

对于开放式请求，提供最能服务于用户目标的几个方向，并推荐一个起点。对于具体请求，选择相关模式并构建；头脑风暴不是强制性的绕道。

## 设计判断

根据答案的含义来选择，然后阅读相关的原语页面：

| 需求 | 原语 | 重要区别 |
| --- | --- | --- |
| 定义集合中的一个 | [选择](https://docs.typesafe.ai/primitives/choice.md) | 选择一个选项；其分布比较竞争选项 |
| 条件是否成立 | [Noul](https://docs.typesafe.ai/primitives/noul.md) | 是的概率；没有单独的置信度；当多个可能适用时，每个标签使用一个 |
| 描述的维度上的程度 | [评分](https://docs.typesafe.ai/primitives/score.md) | 概率加权的有序级别上的位置；为分级排名使用可比较的每个项评分 |

给每个问题足够的**状态**来回答：源文本、身份、关系、策略和当前事实。当上下文有多个部分时，优先使用命名的 JSON 字段。将判断放在**指令**中，并在**标准**中定义其可能的答案。问题 ID 用于代码，不会发送到模型；在问题中包含完整含义。使用反引号路径引用嵌套状态，例如 `ticket.messages[0].text`。

每个问题只问一个狭窄、连贯的判断。将独立有用的维度分开，而不破坏正在判断的关系。有界动作选择或上下文解释是有效的；原子不代表字面事实提取或一句话限制。字符串适用于简单问题。当定义、对比、排除或示例澄清指令或标准时，使用结构化对象或数组。评分级别必须描述具体情况并独立存在。

保留所需的答案。当没有任何可能匹配时，包括一个不匹配的结果；当它独立有用时，使用一个单独的存在判断。对于源值选择，检查候选覆盖范围：模型不能选择遗漏的值。

## 组合和验证

**对同一状态一起提出独立的问题**，包括有用的推测性问题。它们并行运行，并且无法看到彼此的答案。明确说明每个推测前提；代码消费适用的答案。当需要早期答案来获取证据、构建新状态或确定下一个选项时，才需要第二个请求。额外的问
