# discover-event-surfaces

你处于分析工具化工作流程的第 2 步。读取一个 `change_brief` YAML 文件，并生成一份详尽的分析事件候选项列表——命名规范、按类别组织，并准备好供产品经理（PM）审查。

像一位既负责发布功能又关心功能是否成功的工程师一样思考。生成能够回答产品/业务问题的分析事件，而不是反映实现细节的事件。目标是**广度与质量**——下游的技能将缩小列表。

阅读 `taxonomy` 技能的 `../taxonomy/SKILL.md` 文件，了解核心分析理念和命名标准。

---

## 1. 解析 change_brief

- `classification.analytics_scope` — 如果为 `none`，则停止并告知用户没有需要工具化的内容。
- `summary` — 变更的一行描述。
- `user_facing_changes` — 主要信号。每个条目 = 用户现在可以不同地做或看到的事情。
- `surfaces.components` — 修改的 UI 组件；交互发生的地方。
- `file_summary_map` — 读取 `surfaces` 或触达用户界面逻辑的文件摘要。跳过测试/配置/工具。

## 2. 扫描代码库并映射用户流程

在生成任何事件之前，构建对用户如何通过该功能的清晰理解。变更简报提供了文件路径和摘要——现在读取实际代码以追踪完整旅程。

### 要读取的内容

- 列表在 `surfaces.components` 中的每个文件——完整读取它们。
- 来自 `file_summary_map` 且触达用户界面逻辑的文件（跳过测试、配置、工具）。
- 跟踪导入和引用的一级：如果一个组件调用钩子、API 函数或导航到另一个路由，也读取目标文件。这是你发现 diff 未触及但属于同一流程的步骤的方式。

### 要寻找的内容

追踪用户从入口到结果的路径：

- **入口点** — 用户如何到达？路由定义、导航调用、菜单项、链接、功能标志门。
- **交互序列** — 用户按步骤做什么？表单填写、选择、确认、上传。查看事件连接（`onClick`、`onSubmit`、`onChange`）及其改变的状态。
- **异步边界** — API 调用、变更、服务器操作。这些是“尝试”变为“成功”或“失败”的地方。
- **终端状态** — 成功确认、错误处理、重定向、完成屏幕。
- **分支路径** — 路由用户到不同结果的条件（例如，免费与付费、首次使用与再次使用）。

### 生成漏斗假设

将你的发现综合为一条或多条漏斗——从入口到结果的有序用户步骤序列。每个漏斗应有：

- 描述性名称（例如，“属性提取流程”、“引导向导”）
- 有序步骤，每个步骤都有发生文件的函数/处理程序
- 哪个步骤是**开始**，哪个是**结束**

并非每个变更都有漏斗。单操作功能（切换开关、一键导出）不需要——只需说明没有多步骤流程。但当流程存在时，在此处映射它允许你后来自信地分配漏斗开始/结束。

将假设基于你实际读取的代码。不要编造你没有证据支持的步骤。

## 3. 确定命名规范并获取现有事件

调用 `discover-analytics-patterns` 并使用其 `event_naming_convention` 和 `property_naming_convention` 输出。该技能拥有命名解析程序和优先级顺序。不要在此处重新定义它。

在生成候选项之前，拉取项目的现有事件分类法，以便避免重复并匹配已使用的命名规范。

### 解析项目

如果变更简报包含 Amplitude `projectId`，则直接使用它。否则，调用 `get_amplitude_context` 以解析项目名称或询问用户要针对哪个项目。你需要 `projectId` 进行下一步调用。

### 拉取现有事件

检查连接的目录并使用其当前分类法事件读取器与解析的 `projectId`。仅遵循其宣传的架构。当它支持调用者归因时，使用其 YAML 前面的 `name` 识别此技能。不需要游标——第一页就足够用于模式检测。当其架构支持字段选择时，请求事件名称、类别和描述字段，然后使用返回的字段名称。

### 构建命名参考和现有事件索引

1. **现有事件索引** — 将所有 `eventType` 值收集到一个集合中。你将在第 4 步中检查候选项以避免提议已跟踪的事件。如果事件的语义意义与现有 `eventType` 匹配，则它是重复的，而不仅仅是字符串完全匹配——例如，如果 `Subscription Upgraded` 存在，则不要为同一操作提议 `Plan Upgraded`。

## 4. 生成候选项事件

从漏斗假设开始。如果你在第 2 步中识别了漏斗，首先为漏斗开始和结束生成事件——这些是你的锚点。然后填充中间步骤和非漏斗表面的候选项。

对于每个 `user_facing_change`，问：“如果用户这样做——PM 想要了解哪些结果？”

从四个类别生成（按优先级排序）：

| 类别             | 它捕获的内容                                                                                              | 包括何时                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **business_outcome** | 收入、留存、增长操作（购买、订阅变更、转换门）                                                              | 变更触达变现或留存表面                                                                 |
| **user_journey**     | 有意义的状态转换（工作流完成、功能激活、引导完成）                                                             | 变更引入或改变用户旅程步骤                                                                 |
| **feature_success**  | “它起作用了”的时刻——确认结果，而不是按钮点击（创建文档、生成报告）                                                 | 任何新或实质性变更的功能                                                                |
| **friction_failure** | 用户失败、卡住或放弃的地方（错误、空状态、放弃）                                                               | 复杂的多步骤交互或易出错的流程                                                              |

### 与现有事件去重

生成候选项后，检查每个候选项与第 3 步中你构建的**现有事件索引**。对于每个候选项：

- **完全匹配** — `eventType` 已存在。丢弃候选项。
- **语义匹配** — 不同名称跟踪相同的用户操作或结果（例如，你提议了 `Plan Upgraded`，但 `Subscription Upgraded` 已存在以跟踪同一操作）。丢弃候选项。
- **部分重叠** — 现有事件覆盖更广泛的操作，该操作包含你的候选项（例如，`Checkout Completed` 已存在，而你的候选项 `Payment Submitted` 在同一时刻触发）。除非候选项捕获有意义不同的信息，否则丢弃。

如果你因为已存在而丢弃候选项，请在输出中的 `already_tracked` 列表中注明，以便用户知道哪些内容已覆盖。

## 5. 质量过滤

每个候选项必须通过所有三个：

1. **决策有用** — PM 可以仅凭此信息做出产品决策，无需其他五个事件提供背景。
2. **结果导向** — 捕获的是发生了什么，而不是用户尝试了什么。`Property Extracted` > `Extract Button Clicked`。优先考虑确认结果；当没有服务器确认时，表单提交是可接受的。
3. **跨重新设计稳定** — 围绕业务/产品概念命名，而不是 UI 元素。如果重命名模态会导致事件名称过时，则它耦合过紧。

**丢弃：** 没有结果的原始点击/悬停、内部技术操作（API 回调、状态更新）、UI 版本化的名称（`modal_v2_submit`）、子步骤级粒度。

## 6. 命名事件

使用 `discover-analytics-patterns` 返回的命名规范。新事件应看起来像它们属于其余的仪器化：相同的 casing、相同的词序、相同的分隔符、相同的前缀模式，以及相同的特定程度。

如果你后来需要在理由或仪器化提示中建议属性名称，请使用 `discover-analytics-patterns` 返回的 `property_naming_convention`。

在所有情况下，使用产品领域主语（属性、用户、文档），而不是代码名称（属性项、操作存储）。

| 良好（标题大小写约定） | 坏                        |
| ---------------------------- | -------------------------- |
| `Property Extracted`         | `extract_property_clicked` |
| `Extract Type Configured`    | `type_dropdown_changed`    |
| `Property Creation Failed`   | `500_error_new_property`   |

## 7. 确定文件和仪器化点

对于每个候选项，使用 `file_summary_map` 和 `surfaces.components` 来识别：

- **`file`** — 跟踪调用所属的源文件。优先选择最接近结果确认的文件（而不是用户启动操作的文件）。通常是来自 `surfaces.components` 的组件文件或异步操作解析的钩子。
- **`instrumentation`** — 1-2 句话：*何时*触发（在什么条件/回调/状态转换后）以及*如何*连接（放在哪个函数/处理程序中）。引用实际函数名称，以便工程师可以找到正确的行。

## 8. 深化理解，然后优先级排序

对于每个候选项，首先处理这两个字段——它们迫使你具体思考事件的价值，然后再评分它：

- **`analysis_recipe`** — 描述分析师将使用此事件构建的具体图表、漏斗或查询。具体说明：提及可视化类型、细分维度以及与其他事件组合的任何其他事件。例如，*"每周漏斗：Panel Opened → Extract Type Selected → Property Extracted，按 extractType 分段。如果完成率低于 50%，则发出警报。"**
- **`stakeholder_narrative`** — 写一句 PM 可以放入季度回顾或董事会演示文稿中的话，使用此事件的数据。想象指标已存在并写出它讲述的故事。例如，*"68% 的尝试提取的用户在第一次尝试中完成，较上一季度的 45% 有所提高。"* 如果你想不出一个引人入胜的幻灯片句子，该事件可能不值得仪器化。

现在，带着这个背景，分配一个**优先级**：

| 优先级         | 含义                                                                                                            | 指导                                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **3** (关键) | 如果缺少此事件，你会阻止发布。它回答了团队将在第一周内提出的问题。                                                                 | 保留用于直接衡量功能是否成功或失败的事件。大多数变更只产生 1-2 个关键事件。                                                   |
| **2** (有用)   | 添加了真正的分析价值，但功能可以在没有它的情况下发布。如果仪器化成本较低，则值得添加。                                                                 | 分段维度、次要工作流、配置选择。                                                                                             |
| **1** (可选) | 可选的。只有当团队有带宽并有一个特定的假设要测试时，才仪器化。                                                                 | 边缘案例失败、探索性参与信号、可发现性指标。                                                                                 |

**漏斗事件值得特别关注。** 当变更引入或修改多步骤流程（结账流程、引导向导、数据导入管道）时，PM 的第一个问题是“用户在哪里放弃？” 漏斗开始和漏斗结束之间的差距，在中间没有可见性，是一个盲点，可能隐藏严重的产品问题——如果参与在第 5 步的 5 步中的第 2 步崩溃，团队需要知道，而不是猜测。

**漏斗开始和漏斗结束事件始终是关键的（优先级 3）。** 没有书签，你无法衡量转化率——任何漏斗最重要的指标。这两个事件是不可协商的，无论漏斗的长度或复杂性如何。

要决定标记多少个*中间*漏斗事件为关键，根据漏斗的长度和复杂性进行评估：

- **短流程（2-3 步，单页）**：开始和结束事件就足够了。不要在简单流程中仪器化每个微步骤。
- **中等流程（3-5 步，可能跨越多页）**：在最有可能的放弃点添加一个中间事件——通常是在用户投入努力时（填写表单、做出关键选择、上传文件）。
- **长流程（5+ 步，多页或向导式）**：2-3 个中间事件在自然阶段边界。思考“开始 → 配置 → 提交 → 确认”，而不是跟踪每个字段交互。

谨慎选择中间事件。每个你标记为关键的漏斗事件都是工程师必须实现和 PM 必须监控的一件事。如果你不确定一个中间步骤是否值得跟踪，它可能不值得——开始和结束事件将揭示是否存在问题，团队可以在看到高放弃点后随时添加粒度。

少即是多。一个专注的关键事件集，实际上会被仪表板使用，比一个无人关注的庞杂列表更好。当不确定时，降级——添加一个事件比删除一个已存在于仪表板中的事件更容易。

## 9. 发射 YAML 输出

仅输出 YAML 块——没有周围的文字。

```yaml
event_candidates:
  source_summary: "<from change_brief.summary>"
  analytics_scope: "<from change_brief.classification.analytics_scope>"
  event_naming_convention: "<from MCP if clear, otherwise codebase instrumentation, otherwise taxonomy skill>"
  property_naming_convention: "<from MCP if clear, otherwise codebase instrumentation, otherwise taxonomy skill>"

  already_tracked:                         # omit if no duplicates found
    - existing_event: "Subscription Upgraded"
      candidate_dropped: "Plan Upgraded"
      reason: "Same action — existing event already tracks plan/subscription upgrades."

  funnels:                                 # omit if no multi-step flows found
    - name: "Descriptive funnel name"
      steps:
        - step: "Step description"
          file: "src/components/Foo.tsx"
          function: "handleOpen"
          role: start                      # start | intermediate | end
        - step: "Next step"
          file: "src/components/Bar.tsx"
          function: "onSubmit"
          role: intermediate
        - step: "Final step"
          file: "src/hooks/useSave.ts"
          function: "onSuccess"
          role: end

  candidates:
    - name: "Event Name Here"
      category: feature_success          # business_outcome | user_journey | feature_success | friction_failure
      rationale: "What PM question this answers."
      analysis_recipe: "Weekly trend of completions; funnel from Panel Opened → Extract Type Selected → Event Name, segmented by extract type."
      stakeholder_narrative: "Feature X adoption reached 40% of active users within two weeks of launch, exceeding our 25% target."
      priority: 3                        # 3 = critical, 2 = useful, 1 = optional
      funnel: "Funnel name"             # which funnel this belongs to, if any
      funnel_role: start                 # start | intermediate | end — omit if not part of a funnel
      surface: "ComponentName"           # from surfaces.components
      file: "src/components/Foo/Bar.tsx"
      instrumentation: "Fire after the async save resolves, inside onSuccess of useExtract(). Pass result status."

    - name: "Another Event"
      category: user_journey
      rationale: "..."
      analysis_recipe: "..."
      stakeholder_narrative: "..."
      priority: 2
      surface: "..."
      file: "..."
      instrumentation: "..."
```

排序：高级类别优先，每个类别中最有影响力的优先。

---

## 示例

**输入摘录：**
```yaml
user_facing_changes:
  - "Users can now select Extract Type (Text or Attribute) in the PropertyItem panel"
surfaces:
  components:
    - name: PropertyItem
      change: modified
```

**好的候选项：**
```yaml
- name: "Property Extracted"
  category: feature_success
  rationale: "Core adoption signal — tells PMs whether the extract workflow completes."
  analysis_recipe: "Weekly funnel: Panel Opened → Extract Type Selected → Property Extracted, segmented by extractType. Alert if completion rate drops below 50%."
  stakeholder_narrative: "72% of users who open a property panel complete an extraction, up from 0% before this release — validating the new extract workflow."
  priority: 3
  surface: "PropertyItem"
  file: "src/components/PropertiesPanel/PropertyItem.tsx"
  instrumentation: "Fire after extract resolves successfully in onSuccess handler. Include extractType (TEXT or ATTRIBUTE)."

- name: "Extract Type Selected"
  category: feature_success
  rationale: "Shows which mode users prefer — informs investment in Attribute mode."
  analysis_recipe: "Pie chart of Text vs Attribute selections over 30 days. Combine with Property Extracted to get per-mode completion rate."
  stakeholder_narrative: "85% of extractions use Text mode vs 15% Attribute — we should double down on Text UX before expanding Attribute capabilities."
  priority: 2
  surface: "PropertyItem"
  file: "src/components/PropertiesPanel/PropertyItem.tsx"
  instrumentation: "Fire in onChange of Extract Type select, passing new value."

- name: "Property Extraction Failed"
  category: friction_failure
  rationale: "Surfaces where the extract workflow breaks for reliability prioritization."
  analysis_recipe: "Error rate chart: Property Extraction Failed / (Property Extracted + Property Extraction Failed), grouped by error reason. Alert on spikes."
  stakeholder_narrative: "Extraction failure rate dropped from 12% to 3% after the v2 error-handling patch — users are hitting fewer dead ends."
  priority: 2
  surface: "PropertyItem"
  file: "src/components/PropertiesPanel/PropertyItem.tsx"
  instrumentation: "Fire in catch/onError of extract call. Include error reason if available."
```

**不要包括：** `Extract Type Dropdown Opened`（点击，无结果）、`PropertyItem State Updated`（内部）、`Attribute Input Focused`（太细粒度）。
