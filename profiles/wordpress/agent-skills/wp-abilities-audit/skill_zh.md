# WP 能力审计

为 WordPress 插件的 REST 接口生成标准化的审计文档，按语义意图分组提出一组能力 API 注册。审计文档是实施者的规划工件——无论是人类、代理还是两者——它以结构化形式捕获控制器清单、能力门禁和拟议的能力形状。阅读文档的审阅者可以无需重新推导调查范围即可规划工作。

此技能适用于任何暴露 REST 接口的插件。插件分类（用于可选的 `plugin_family` 注释）由用户决定；工作流程本身与插件无关。

## 使用场景

- 任务是“为 WP 插件注册能力 API 能力”，且尚未存在审计文档。
- 规划参与多插件能力推广，需要一个可共享、标准化的审计工件。
- 在实现能力之前，预先检查插件的代理就绪情况。
- 产品经理或非实施者希望在工程人员接手之前规划工作。

## 所需输入

1. **插件检出路径** — 审计插件的 working tree。
2. **分诊输出** — 如果尚未完成，请先运行 `wp-project-triage`。审计文档消耗报告中的 `signals.usesAbilitiesApi`、`versions.wordpress` 和 `project.kind`。
3. **审计员身份** — 名称和团队或上下文，记录在审计文档的 `auditor` 字段中。
4. **输出路径** — 审计文档应存放的位置。默认显式优先于隐式；如果未提供，则询问而不是写入插件工作树。

## 前置条件

- `wp-project-triage` 已成功运行并对插件进行了分类。
- 插件至少有一个 REST 控制器。如果枚举发现零个控制器，则不适用审计——见下文“失败模式”。

## 程序

### 1. 枚举 REST 控制器

现在阅读 `references/controller-enumeration.md`——它涵盖了两种观察到的枚举路径（标准布局的 glob、作为通用回退的 grep）以及何时使用每种路径。

将每个控制器类 + 文件 + REST 基础 + 路由记录在“控制器清单”表中。清单是详尽的，即使只有一部分成为拟议的能力。

### 2. 对每个控制器提取支撑字段

对于每个找到的控制器，提取审计模式所需的字段：类、文件、HTTP 方法、路由、路由注册行号、回调名称、回调行号、权限回调、回调是否接受 `WP_REST_Request` 参数或为零参数，以及返回类型。

现在阅读 `references/audit-schema.md`——了解确切字段列表和 `proposed_abilities` 条目的形状。行号字段对于继承的回调可能是 `null`——模式允许这种情况，并与其可选的 `inherited_from` 字段配对。

### 3. 确认能力门禁

跟踪每个控制器的 `permission_callback` 到其 `current_user_can()` 调用（或到扩展了基于帖子类型的基类的控制器的帖子类型能力机制）。

现在阅读 `references/capability-gate-tracing.md`——它记录了两种常见机制（直接 `check_permission()` 与基于帖子类型的 `wc_rest_check_post_permissions()`）以及如何在模式中表示每种机制。明确注明读和写门禁是否不同：复合门禁表示为 `{read, write}` 对象，而不是单个字符串。

### 4. 使用语义意图分组提出能力

不要为每个 HTTP 方法原子化一个能力。应用语义意图分组启发式算法——这是此技能使用的唯一分组规则。

现在阅读 `../wp-abilities-api/references/grouping-heuristic.md`——不要在此重新推导规则。简而言之：每个真实世界的问题或状态转换一个能力，`input_schema` 中的过滤参数将 N 个变体合并为 1。

**在填充任何候选之前应用用例合理性检查**。根据 `../wp-abilities-api/references/domain-vs-projection.md` 的用例合同测试：人类或代理是否会通过受支持的插件工作流程有意执行此行为？如果是，候选者是真实的能力——继续填写字段。如果不是，路由是内部传输管道（缓存失效、调度器滴答、账本端点、调试内省）——将其保留在控制器清单部分以保持完整性，但不要将其提升到 `proposed_abilities`。路由可能对清单有用；拟议的能力必须代表一个真实的用户/操作员问题或操作。

对于通过合理性检查的每个拟议能力，填写 `proposed_abilities` 模式中的每个字段：`name`、`intent`、`backing`、`permission`、`return_type`、`effort`（S/M/L）、`annotations`（只读/破坏性/幂等）、`notes`、`risks`、`use_case_fit`、`side_effects`、`seed_data_needs`。

最后三个是实施者和使用验证模式工具都需要的实施就绪事实：此能力服务于哪个人类/代理工作流程 (`use_case_fit`)、支撑路径在每次调用时发出什么 (`side_effects`——空数组是一个事实，而不是缺失值)、测试环境中必须存在哪些代表性数据才能使能力通过公共边界执行 (`seed_data_needs`)。

### 5. 揭示差距和延迟项

三个桶：

- **`excluded_from_mvp`** — 因风险原因有意延迟的候选者（真实金钱写入、不可逆状态更改或先决设计工作）。每个条目都应有一个一句话的理由。
- **`surfaced_gaps`** — 没有支撑端点的 MVP 候选者（能力 `backing: null`），以及枚举期间发现的具有高价值端点，但不在 MVP 列表中但将是轻松的未来胜利。
- 每个能力的风险——支撑端点的任何内容都必须由实施者处理（没有幂等键、两阶段行为、状态转换注意事项、使用 `permission_callback => '__return_true'` 注册的零参数端点必须不复制该值到能力注册中）。

### 6. 编写审计文档

写入在“所需输入”中收集的显式输出路径。文档结构必须与 `references/audit-schema.md` 完全匹配：

1. `最后更新：YYYY-MM-DD HH:MM` 标头。
2. 包含所有必需的顶层元数据 + `proposed_abilities`、`excluded_from_mvp`、`surfaced_gaps` 的 YAML 块。
3. “控制器清单”表。
4. “注释和惊喜”散文部分。

一个可复制粘贴的最小示例，显示完整的形状，位于 `references/audit-schema.md` 的“最小有效示例”下——在编写新的审计时从那里开始。

### 7. （可选）指定一个参考实现能力

在第一个实施者应着陆的能力上设置 `reference_ability: true`——通常是最小、最安全、最高杠杆的读。这为下游工作流程提供了一个确定性起点。

## 验证

- 审计符合 `references/audit-schema.md`（所有必需的顶层字段存在，至少有一个 `proposed_abilities` 条目，每个能力上的注释完整）。
- `capability_gate` 对于单能力插件是字符串，对于基于帖子类型的插件是 `{read, write}` 对象。
- 每个具有 `backing: null` 的能力也出现在 `surfaced_gaps` 中。
- 文档通过 `audit-schema.md` 中的“已知限制”中的验证器而不会出错。

## 失败模式 / 调试

- **插件没有 REST 控制器**——不适用审计。考虑基于钩子/过滤器的能力（此技能当前版本的范围之外）或跳过此插件的能能力采用。
- **插件从另一个存储库继承控制器**（对于扩展核心基于帖子类型的控制器如 `WP_REST_Posts_Controller` 的插件，或基于父 REST 类构建的扩展插件常见）——使用 `backing.inherited_from: "<parent FQCN>"` 捕获。根据模式，行号字段可以是 `null`。
- **复合能力门禁（不同的读/写能力）**——使用 `references/capability-gate-tracing.md` 中记录的结构化 `{read, write}` 形式。不要将 `/` 分隔的字符串混入作为单个能力类型的字段。
- **模糊分组**——路由到 `../wp-abilities-api/references/grouping-heuristic.md`。不要在审计文档中发明替代分组规则。
- **具有 `permission_callback => '__return_true'` 的零参数端点**——在 REST 层合法，但能力的 `permission_callback` 必须与插件的商家门禁匹配。永远不要将 `'__return_true'` 提升到能力注册中。在能力的 `risks` 中注明这一点。
- **输出路径默认为插件工作树**——始终询问用户一个显式的输出目录（例如他们的保险库 `plans/`）。将审计写入插件自己的 git 历史会污染工作树并隐藏工件。

## 升级

- 如果插件使用的枚举约定未在 `references/controller-enumeration.md` 中涵盖（标准的 glob 和 grep 回退都没有产生完整的清单），请更新该参考文件以包含新的约定，并打开一个 PR，以便未来的审计可以确定性地涵盖它。
- 如果能力跟踪遇到 `references/capability-gate-tracing.md` 未涵盖的机制，请扩展该文件，而不是仅在审计的“注释和惊喜”中编码新情况。
