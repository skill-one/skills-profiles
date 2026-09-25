# 使用 TypeSafe 构建

TypeSafe 将人工智能的智能单元转化为可像编程原语一样使用的对象：你可以将其组合成更大能力的小型判断。其 **System One 模型** 会返回快速、聚焦的判断，软件可直接消费。**Jev** 是 TypeSafe 的旗舰产品，也是首个 System One 模型。它能够理解自然语言，返回带类型的答案和概率，而非生成文本或推理解释。代码拥有工作流；当普通代码需要语义理解时，模型提供可编程的常识。

## 阅读实时文档

**TypeSafe 的实时文档为权威来源。阅读它们是本任务的一部分。**
本技能提供方向指引；文档则包含最新概念、提示词指南、API 契约、SDK 使用、模型、限制及示例。

- 从 [文档索引](https://docs.typesafe.ai/llms.txt) 开始，发现相关页面和菜谱。进行有针对性的阅读，而非加载整个站点。
- Mintlify 通过将 `.md` 附加到页面路径后提供 Markdown，例如
  [如何使用 TypeSafe 构建](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md)。
  跟随索引中的链接；在有用时，将无扩展名的文档页面链接转换为 `.md` 后缀。将相对链接以 `https://docs.typesafe.ai` 为基准解析。
- 在编写集成之前，阅读当前的 API 或所选 SDK 页面以及与设计相关的提问指导。对于新工作流，同时检查最近的菜谱：它通常比通用分类器展现出更优的分解方式。
- 如果索引不可用，使用下方的直接链接或站点的导航。若 Markdown 抓取失败，尝试常规页面。若无法实时访问，使用可用的本地文档或已安装的 SDK 类型，并说明该限制，避免编造依赖版本的细节。

| 任务 | 从这里开始；参考相关细节 |
| --- | --- |
| 理解编程模型 | [System One](https://docs.typesafe.ai/concepts/system-one.md)，[构建指南](https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md) |
| 探索要构建的内容 | [用例映射](https://docs.typesafe.ai/concepts/use-case-map.md)，然后从索引中查找相关菜谱 |
| 准备输入和提问 | [状态](https://docs.typesafe.ai/concepts/state.md)，[原语](https://docs.typesafe.ai/primitives.md)，然后阅读所选原语页面 |
| 决定如何处理不确定性 | [置信度](https://docs.typesafe.ai/confidence.md) |
| 编写 API 代码 | [HTTP API](https://docs.typesafe.ai/api.md)，[Python SDK](https://docs.typesafe.ai/sdk/python.md)，或 [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript.md) |
| 更新旧集成 | [迁移指南](https://docs.typesafe.ai/migrating-to-v1.md) 和已安装 SDK 的当前参考文档 |

## 找到合适的形态

从用户期望的行为开始：应用将展示、选择、更改或转交什么？反向推导所需的判断。将已知规则、计算、精确查找和执行保留在代码中。保留用户所选的技术栈和范围；在语义理解有所帮助的地方加入 TypeSafe。

在头脑风暴或选择架构时，不要只考虑分类。以下模式是起点：围绕用户的目标组合原语，包括不符合既有方案的想法。

- **路由并填充已知参数。** 请求可以选择一个处理器及其类型化的参数。预先提出有用的分支特定问题，仅消费相关答案。探索 [函数调用](https://docs.typesafe.ai/cookbooks/function_calling.md) 和 [推测性扇出](https://docs.typesafe.ai/patterns/fan-out.md)。
- **选择而非生成。** 在代码中查找候选值或源片段，使用判断选择预期的那个，然后复制或标准化。代码也可以将源文本组装为格式化的文档或阅读指南。探索 [值提取](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md) 和 [结构恢复](https://docs.typesafe.ai/cookbooks/autoformat.md)。
- **查找并判断证据。** 检索候选内容，将其与查询的关联性进行比较，并选择有用的上下文。探索 [重排序](https://docs.typesafe.ai/cookbooks/rerank_typesafe.md) 和 [层次分类](https://docs.typesafe.ai/cookbooks/hierarchical_classification.md)。
- **将判断转化为可复用数据。** 一次性对维度打分，然后让代码或用户控制权重、阈值、排序和视图的变化。在带标注的结果下，这些信号可转化为经典机器学习特征。探索 [综合评分](https://docs.typesafe.ai/patterns/composite-scoring.md) 和 [特征发现](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md)。
- **验证并升级。** 将具体声明或字段与其证据进行核对；将不确定或失败的情况转交人工或推理模型处理。探索 [引用校验](https://docs.typesafe.ai/cookbooks/citation_check.md) 和 [提取级联](https://docs.typesafe.ai/cookbooks/sde_cascade.md)。
- **响应变化的状态。** 代码可以保留目标和观察，同时让新鲜判断引导下一步的有界操作。将推断状态与观察到的事实区分开，并在将结果应用到变化的情况前检查新鲜度。

对于开放式请求，提供最能服务用户目标的几个方向，并推荐起点。对于具体请求，选择相关模式并构建；头脑风暴并非强制绕行。

## 设计判断

根据答案所表达的含义进行选择，然后阅读相关的原语页面：

| 需求 | 原语 | 重要区分 |
| --- | --- | --- |
| 属于定义中的集合之一 | [Choice](https://docs.typesafe.ai/primitives/choice.md) | 选择其中一个选项；其分布比较竞争选项 |
| 判断条件是否成立 | [Noul](https://docs.typesafe.ai/primitives/noul.md) | “是”的概率；不单独提供置信度；当多个标签可能适用时，每个标签使用一个 Noul |
| 描述维度上的程度 | [Score](https://docs.typesafe.ai/primitives/score.md) | 有序级别上的概率加权位置；对分级排序使用每个项目可比对的 Score |

为每个问题提供足够的**状态**以使其能够回答：源文本、身份、关系、策略和当前事实。当上下文包含多个部分时，优先使用命名的 JSON 字段。将判断放在 **instructions**（说明）中，在 **criteria**（标准）中定义其可能的答案。问题 ID 仅供代码使用，不会发送给模型；问题中应包含完整的含义。用带反引号的路径引用嵌套状态，例如 `ticket.messages[0].text`。

每个问题提出一个狭窄、连贯的判断。拆分相互独立、有用的维度，且不破坏正在判断的关系。有界的选择或上下文解释是有效的；原子并不意味着一定是字面事实提取或一句话的限制。字符串适用于简单问题。当定义、对比、排除或示例能够澄清说明或标准时，使用结构化对象或数组。评分等级必须描述具体情境，并能够独立成立。

保持所需答案可用。当没有内容可能符合时，包含无匹配结果；当独立有用时，使用单独的 presence 判断。对于源值选择，检查候选覆盖：模型不能选择被省略的值。

## 组合并验证

**针对同一状态一起提出独立问题**，包括有用的推测性问题。它们并行运行，无法看到彼此的回答。明确陈述每个推测性前提；代码消费适用的答案。当需要先前答案来获取证据、构建新状态或确定下一步选项时，需要发出第二次请求。额外问题仍会消耗令牌；测量实际的请求预算、成本和端到端延迟。

使用概率和置信度引导行为，阈值应在用户数据和后果上进行评估。Choice/Score 的置信度概括了分布的集中程度，而非整体工作流正确性或行动的许可。Noul 接近 0.5 表示“是”与“否”的概率相近，而非中等强度。多个可接受的备选方案也可能分散概率；低置信度并不意味着必须否定无害的偏好选择。忽略未使用分支的不确定性。

保持策略明确，原始判断可复用。加权评分适用于补偿偏好；“任何严重违规”这类规则需要单独的条件。当证据和问题的含义未改变时，更改权重或显示过滤条件无需重新运行推理。类型化输出保障的是接口，而非真相。System One 模型是为校准决策训练的；在目标领域验证其性能。

测试代表性案例及其应用产生的行为。对于失败，检查确切的状态、问题、候选内容、答案、组合方式和观察到的结果。区分缺失证据、模型错误、代码错误和服务故障。将菜谱中的阈值和演示结果视为需要评估的示例，而非普遍规则或永久的模型限制。在 Web 应用中，将 API 凭证保留在服务端。
