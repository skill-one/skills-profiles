# 图表设计

将图表作为独立的HTML文件创建，包含内联SVG和编辑设计系统。

41种视觉类型。语义模式描述行为；类型参考描述布局。

---

## 0. 首次设置 — 样式指南门

在新的项目中生成第一个图表之前，请验证样式指南是否已定制。

不要在品牌项目中无声地发布默认样式的图表。

首先解决每个项目`.diagram-design`标记（[references/profiles.md](references/profiles.md)）；成功解析的标记选择其配置文件并绕过此门。该参考拥有失败、受保护的默认值和保存行为。

打开[`references/style-guide.md`](references/style-guide.md)并检查默认标记。如果它们仍然是默认的（纸张`#f5f5f5`，墨水`#2d3142`，强调`#eb6c36`），**暂停并询问用户**：

> *"这是您在此项目中的第一个图表，样式指南仍然是默认的。现在定制？选项：(a) 网站URL，(b) 已安装的技能，(c) 本地文件夹/设计系统，(d) 粘贴标记，(e) 保持默认，(f) 加载保存的配置文件。*

然后根据[`references/onboarding.md`](references/onboarding.md)的匹配部分分支；对于**(f)**，请遵循[`references/profiles.md`](references/profiles.md)。

**一旦样式指南已定制**（或用户明确选择了默认值），则在后续运行中跳过此门。领先的配置文件标题命名复制的活动配置文件。如果没有标题，任何语义角色值或排版家族与默认值不同都意味着**未保存的自定义**：跳过门并提供建议将其保存为配置文件。所有默认标记且无标记/标题触发门。在入门后，根据`references/profiles.md`保存为命名的客户端配置文件。

---

## 1. 哲学

**通常最高质量的操作是删除。**

应用于示意图：

- 每个节点代表一个独特的想法。总是一起旅行的两个节点是一个节点。
- 每个连接都携带信息。如果关系可以从布局中明显看出，请删除线条。
- Coral是**编辑性的，不是标志。** 每个图表最多1-2个焦点节点。在5个节点上使用它会抹去信号。
- 示意图完成时不是所有内容都已添加。当没有任何内容可以删除时，它才完成。

**目标密度：4/10。** 足够技术完整。不要太密集以至于需要指南。超过9个节点，它可能有两个图表。

---

## 2. 何时使用

当读者从视觉中比从文本、表格或项目符号列表中学习更多时，用于41种视觉类型中的任何一种（§3）。

**不要使用：**

- 快速的Unicode图表 → 使用**wiretext**。
- 物品列表 → 表格或项目符号。
- 简单的“之前/之后” → 表格。
- 单形状“图表” → 直接写句子。

绘制之前，请问：*读者会从这比从一篇写得好的段落中学到更多吗？* 如果不是，就不要绘制。

---

## 3. 选择：语义模式，然后视觉类型

当行为、状态、强制执行或风险携带意义时，首先加载[`references/semantic-patterns.md`](references/semantic-patterns.md)并选择一个主要模式。然后选择用于布局的最接近的视觉类型。如果没有匹配的模式，则直接选择类型。

| 行为触发器 | 语义模式 → 最近类型 |
|---|---|
| Fan-in、队列深度、有限容量、瓶颈 | **Fan-in queue / bottleneck** → 数据流 |
| 在各个阶段重复的问句/输入/治理/输出插槽 | **阶段框架与语义插槽** → 流程 |
| 对话或松散输入成为结构化的持久化工件 | **非结构化输入 → 结构化工件** → 数据流 |
| 两个规则跟踪需要通过/失败/跳过/未达到和第一次分歧 | **成对的政策评估跟踪** → 流程图 |
| 信任边界加上允许/禁止的入口或部署路径 | **安全的铺路** → 架构 |
| 按执行位置分组控制 | **治理 / 控制目录** → 层堆栈 |
| 防御措施弥补先前的差距和残余风险传播 | **补偿安全层** → 层堆栈 |
| 分层、ID地址able分解需要每个块的I/O、约束和代码链接 | **可追溯的块分解** → 树 |
| 一个主题通过阶段、等待、重试、取消和终端结果 | **生命周期阶段图** → 状态机 |

模式拥有语义原语及其更严格的预算；类型拥有布局语法。仅在请求运动或实质性澄清有序变化时使用[`references/animation.md`](references/animation.md)；静态是默认值。

### 视觉类型指南（41）

| 如果你正在展示… | 使用 | 参考 |
|---|---|---|
| 系统中的组件 + 连接 | **架构** | [type-architecture.md](references/type-architecture.md) |
| 阶段或部门按阶段划分的遗留IT景观；显示*之前*状态 | **IT当前状态** | [type-it-state.md](references/type-it-state.md) |
| 带分支的决策逻辑 | **流程图** | [type-flowchart.md](references/type-flowchart.md) |
| 按时间顺序在参与者之间传递消息 | **序列** | [type-sequence.md](references/type-sequence.md) |
| 状态 + 转换 + 守卫 | **状态机** | [type-state.md](references/type-state.md) |
| 实体 + 字段 + 关系 | **ER / 数据模型** | [type-er.md](references/type-er.md) |
| 事件在时间中的位置 | **时间线** | [type-timeline.md](references/type-timeline.md) |
| 跨职能流程中的交接 | **泳道** | [type-swimlane.md](references/type-swimlane.md) |
| 双轴定位 / 优先级 | **象限** | [type-quadrant.md](references/type-quadrant.md) |
| 多个实体在3-5个定量标准上得分 | **雷达 / 蜘蛛** | [type-radar.md](references/type-radar.md) |
| 一个定量系列在循环类别中；角度=类别，半径=幅度 | **极坐标图** | [type-polar.md](references/type-polar.md) |
| 强化循环；最后一步为第一步提供输入，中心节点积累状态 | **循环** | [type-loop.md](references/type-loop.md) |
| 通过包含 / 范围实现层次结构 | **嵌套** | [type-nested.md](references/type-nested.md) |
| 父 → 子关系 | **树** | [type-tree.md](references/type-tree.md) |
| 人员/代理/团队所有权、报告、路由、升级 | **组织结构图** | [type-org-chart.md](references/type-org-chart.md) |
| 堆叠的抽象级别 | **层堆栈** | [type-layers.md](references/type-layers.md) |
| 集合之间的重叠 | **维恩图** | [type-venn.md](references/type-venn.md) |
| 排名层次结构或转换掉落 | **金字塔 / 漏斗** | [type-pyramid.md](references/type-pyramid.md) |
| 定量比较 across 类别 | **条形图** | [type-bar.md](references/type-bar.md) |
| 一个开始总数通过有符号贡献（预算桥接、人员数量差异）桥接到一个结束总数 | **瀑布图** | [type-waterfall.md](references/type-waterfall.md) |
| 部分整体，相对大小是故事 | **树状图** | [type-treemap.md](references/type-treemap.md) |
| 交叉分类数据；填充编码每个单元格的值 | **热图** | [type-heatmap.md](references/type-heatmap.md) |
| 随时间变化的连续趋势，两个状态之间的变化（斜率图），每个系列的一个分布（等高线），跨多个快照的排名移动（颠簸） | **线图** | [type-line.md](references/type-line.md) |
| 时间线上的任务和阶段 | **甘特图** | [type-gantt.md](references/type-gantt.md) |
| 两个变量的相关性或分布；气泡（三个变量）和蜜蜂群（一个变量，每个项目一个点）变体 | **散点图** | [type-scatter.md](references/type-scatter.md) |
| 容器集群上的端到端数据堆栈 | **高级** | [type-high-level.md](references/type-high-level.md) |
| 多参与者顺序流程中的数据交接 | **流程** | [type-process.md](references/type-process.md) |
| 多层数据存储具有质量级别和访问策略 | **冠冕** | [type-medallion.md](references/type-medallion.md) |
| 按角色范围的数据流：每个管道步骤中谁做什么 | **数据流** | [type-data-flow.md](references/type-data-flow.md) |
| 数据平台的集成拓扑 — 来源 → 核心 → 消费者 | **DP集成** | [type-dp-integration.md](references/type-dp-integration.md) |
| 按角色/按组件访问权限矩阵 | **DP安全矩阵** | [type-dp-security-matrix.md](references/type-dp-security-matrix.md) |
| 阶段之间分割和合并的数量，带宽=数量 | **Sankey** | [type-sankey.md](references/type-sankey.md) |
| 一个观察到的效果的原因，按类别分组（根本原因分析） | **鱼骨图** | [type-fishbone.md](references/type-fishbone.md) |
| 价值链与演变 — 什么要构建，购买，什么在移动 | **沃德利地图** | [type-wardley.md](references/type-wardley.md) |
| 进行中的工作按状态，有WIP限制和阻塞项 | **看板** | [type-kanban.md](references/type-kanban.md) |
| 一个人在体验的各个阶段做什么，以及感觉如何 | **用户旅程** | [type-journey.md](references/type-journey.md) |
| 软件运行的位置 — 区域、主机、工件、副本、端口 | **部署** | [type-deployment.md](references/type-deployment.md) |
| 什么依赖于什么，有fan-in和循环一个树无法表达 | **依赖关系图** | [type-dependency.md](references/type-dependency.md) |
| 类别具有操作、继承、组合（其他UML路由在其他地方） | **UML类** | [type-uml-class.md](references/type-uml-class.md) |
| 叙事骨干按发布切片，并带有切线 | **故事地图** | [type-story-map.md](references/type-story-map.md) |
| 物理表：SQL类型、约束、索引、列级FK | **数据库模式** | [type-db-schema.md](references/type-db-schema.md) |

经验法则：

- 如果一个3列表格传达相同的信息，请选择表格。
- 如果两种类型似乎都有用，请选择主导轴；语义模式可能会添加行为特定的原语，而不是第二个布局语法。
- 如果您超过了复杂性预算（§7），请将其拆分为一个概述 + 详细内容。

**始终在绘制之前加载指南中链接的所选类型参考。** 当路由到上面时，也加载`semantic-patterns.md`；当选择动画时，加载`animation.md`。

### 绘制前确认

在渲染之前，用一条简短的信息陈述计划：所选视觉类型（和语义模式，如果路由到上面），大小预设，以及复杂性预算（§7）将强制删除的内容。如果用户可以访问，让他们在绘制之前重定向；如果不能，请继续并注意假设旁边的交付物。仅在请求已经固定类型、大小和内容确切时才暂停。

---

## 4. 通用反模式

这些标记任何类型的“AI杂乱”图表：

| 反模式 | 失败原因 |
|---|---|
| 暗模式 + 蓝色/紫色辉光 | 看起来“技术性”而没有设计决策 |
| JetBrains Mono作为通用的“开发人员”字体 | 单体字用于*技术*内容 — 端口、命令、URL。名称使用Geist sans。 |
| 每个节点使用相同的框 | 消除层次结构 |
| 图表浮动在图表区域内部 | 与节点冲突 |
| 箭头标签没有遮罩矩形 | 透过线条 |
| 箭头上的垂直`writing-mode`文本 | 难以阅读 |
| 3个等宽摘要卡片作为默认值 | 通用网格 — 变更宽度 |
| 任何元素上的阴影 | 阴影是禁止的。边框是允许的。 |
| `rounded-2xl`在框上 | 最大半径6-10px或无 |
| 每个重要节点都使用珊瑚 | 珊瑚用于1-2个编辑性强调，不是信号系统 |
| 重新创建Mermaid的渲染器布局 | 导入自动间距和路由，而不是制作编辑性布局 |
| 任何违反§6连接器规则的六个规则 | 斜线倾斜，标签接触它们的笔画，遮罩被后续节点剪裁，重叠路径，共享连接点，在非端点框后面 transit — 每个都是自动失败；§6详细说明它们 |

特定类型的反模式存在于指南中链接的每个类型参考。

---

## 5. 设计系统

**设计系统是可定制的。** 所有颜色、排版和标记都存在于一个单一的真实来源 — [`references/style-guide.md`](references/style-guide.md)。该文件描述语义角色（`paper`，`ink`，`muted`，`accent`，`link`，…）。默认皮肤是一个凉爽的编辑性调色板（白色烟雾纸张，黑色墨水，原子橙强调色，蓝灰中性色，银色发丝线）；要应用自己的品牌，请直接编辑`style-guide.md`，或者运行[`references/onboarding.md`](references/onboarding.md)中描述的基于URL的流程。

> 当规范低于或位于类型参考中提到“ink”，“accent”，“muted”等时，请在`style-guide.md`中查找当前的十六进制值。

### 语义角色（一览）

| 角色 | 目的 |
|---|---|
| `paper`，`paper-2` | 页面背景和容器背景 |
| `ink` | 主要文本 / 笔画 |
| `muted`，`soft` | 次要文本，默认箭头，子标签 |
| `rule`，`rule-solid` | 发丝线边框 |
| `accent`，`accent-tint` | 每个图表最多1-2个焦点元素 |
| `link` | HTTP/API调用，外部箭头 |

**焦点规则：`accent`最多用于1-2个元素。其他所有内容都是`ink` / `muted` / `soft`。如果您想强调4件事，您还没有决定什么是焦点的。
