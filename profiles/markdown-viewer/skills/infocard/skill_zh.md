# 信息卡片生成器

**快速入门：** 分析内容（密度 × 结构 × 情感）→ 自动感知基调以选择配色方案 → 选择布局骨架 → 将 HTML 直接嵌入 Markdown 中使用 `<style scoped>`。

## 关键规则

### 规则 1：直接 HTML 嵌入
**重要提示**：将信息卡片作为直接 HTML 写入 Markdown 中。**绝对不要**使用代码块（` ```html `）。HTML 应直接嵌入文档中，无需任何围栏。

### 规则 2：HTML 结构中无空行
**关键提示**：在 HTML 信息卡片结构中**不要**添加任何空行。保持整个 HTML 块连续，以防止解析错误。

### 规则 3：布局前的内容分析
**必须要求**：在设计之前，沿三个维度分析内容：

**密度**（决定呼吸节奏）：

| 密度 | 内容量 | 视觉处理 |
|------|--------|----------|
| 低 | ≤ 50 字核心内容 | "大字"构图。一个超大元素主导。留白充足。 |
| 中 | 50–200 字 | 主角 + 支持面板。2–3 个主要区块，有清晰的层级。 |
| 高 | 200+ 字 | 非对称多列网格。主要/次要/支持区块。从不使用等权重平铺。 |

**结构**（决定布局几何形状）：

| 结构 | 信号 | 布局模式 |
|------|------|----------|
| 单点 | 一个核心概念 | 一个锚定元素主导，其余元素退让 |
| 对比 | A 对 B，旧对新的对比 | 分割面板，两极分化 |
| 层级 | 层层递进 | 堆叠模块，金字塔形 |
| 流程 | 顺序步骤 | 垂直级联，编号项 |
| 放射状 | 核心 + 衍生 | 中心枢纽，周围面板 |
| 并列 | 多个平等概念 | 非对称网格（从不使用等宽列） |

**情感**（决定色调温度）：

| 情感 | 视觉感受 |
|------|----------|
| 反思 | 更多留白，衬线字体为主，对比度较低 |
| 锐利 | 强对比，粗体字，鲜艳的强调色 |
| 温暖 | 地球色系，圆润感，柔和节奏 |
| 技术 | 等宽字体强调，网格状密度 |

### 规则 4：基调感知
**必须要求**：根据内容主题自动选择配色方案。扫描内容关键词并匹配最接近的基调：

| 内容基调 | 背景 | 强调色 | 触发关键词 |
|----------|------|--------|------------|
| 哲学性 | `#FAF8F4` | `#7C6853` | 认知，思考，意义，哲学，本质 |
| 技术 | `#F5F7FA` | `#3D5A80` | 架构，算法，系统，API，代码 |
| 文学性 | `#FBF9F1` | `#6B4E3D` | 故事，叙事，写作，诗歌，人物 |
| 科学性 | `#F4F8F6` | `#2D6A4F` | 实验，数据，研究，论文，发现 |
| 商业性 | `#F4F3F0` | `#2D6A4F` | 市场，策略，增长，金融，投资 |
| 创意性 | `#F6F3F2` | `#B8432F` | 设计，艺术，美学，灵感，创造 |
| 默认 | `#FAFAF8` | `#4A4A4A` | 当没有明确匹配时——优先选择默认而非错误匹配 |

当明确选择样式模板时，其颜色优先于基调感知。在没有指定样式时，使用基调感知作为默认选项。

### 规则 5：标题保护
如果用户提供标题，则将其原样用作主标题。将编辑性解释放入副标题、摘要或侧边模块中。不要无声地重写用户的标题。

### 规则 6：字体层级
保持清晰的字体比例并始终如一地使用：
- 主标题：`32px–48px`，权重 700–900，紧密字间距（`-0.02em`）
- 副标题 / 摘要：`16px–20px`，权重 400–500
- 正文：`14px–16px`，权重 400，行高 `1.6–1.7`
- 元数据 / 标签 / 标题：`11px–13px`，权重 500–700，大写字母并加字间距
- 正文颜色：永远不要纯黑色——使用 `#1a1a1a`，`#333` 或 `#4a4a4a`

### 规则 7：视觉权重分配
至少一个模块应比其他模块在视觉上更重。避免使每个面板都使用完全相同的处理方式。通过规模、背景色调、字体权重或强调规则进行区分。

### 规则 8：品味规则（反 AI 检查清单）
在最终确定任何卡片之前，对照以下常见的 AI 生成的视觉模式进行检查：

**布局：**
- **无居中主角**——不要默认居中标题。优先选择左对齐或非对称
- **无等宽平铺**——三个等宽列并排是 AI 的首要特征。使用 `2fr 1fr`，非对称网格或交错布局
- **无统一面板**——至少一个面板必须在规模、权重或处理上有所不同

**字体：**
- **无纯黑色** `#000000`——使用偏黑色（`#1a1a1a`，`#2d2a26`）或暖色/冷色深色
- **无仅尺寸的层级**——通过权重和颜色建立层级，而不仅仅是字体大小缩放

**颜色：**
- **最多 1 个强调色**，饱和度 < 80%
- **无霓虹渐变**——无紫色-蓝色 AI 发光，无渐变填充标题
- **一致温度**——一个卡片中不要混合暖灰色和冷灰色

**内容：**
- **无填充数据**——避免 `99.99%`，`50%`，`1234567`。使用有机数字（`47.2%`，`3.8M`）
- **无 AI 语句**——避免 "赋能"，"无缝"，"释放"，"下一代"

**间距：**
- 内边距和边距必须精确计算，无尴尬的间隙
- 相邻元素必须视觉对齐

## 样式示例

首先选择视觉系列，然后在其中选择特定模板。这使库保持广泛，同时避免每次都强制进行 29 种样式的扫描。

### 样式系列

#### 温暖的编辑和叙事

当卡片应感觉反思、人性、叙事或文化纹理时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **编辑温暖** | [styles/editorial-warm.md](styles/editorial-warm.md) | 知识摘要，笔记，论文，分析报告 |
| **客户焦点** | [styles/customer-spotlight.md](styles/customer-spotlight.md) | 客户故事，案例研究，成功回顾，品牌叙事，采用故事 |
| **日落温暖** | [styles/sunset-warm.md](styles/sunset-warm.md) | 社区回顾，活动笔记，生活方式摘要，积极叙事 |
| **中世纪** | [styles/midcentury.md](styles/midcentury.md) | 品牌故事，复古现代活动，文化笔记，设计叙事 |

#### 柔和的生活方式和教学

当卡片应感觉平静、易接近、低压力时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **柔和中性** | [styles/soft-neutral.md](styles/soft-neutral.md) | 生活方式内容，健康，教育，温和品牌，创意工作坊 |
| **板岩粉笔** | [styles/slate-chalk.md](styles/slate-chalk.md) | 教学内容，课程，概念解释，工作坊笔记 |
| **教育工作室** | [styles/education-studio.md](styles/education-studio.md) | 教学笔记，课程模块，学习摘要，工作坊指南 |

#### 纸张、研究和治理

当卡片应像备忘录、报告、简报或证据摘要一样阅读时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **纸张极简** | [styles/paper-minimal.md](styles/paper-minimal.md) | 产品笔记，任务摘要，会议笔记，干净文档 |
| **实验室日记** | [styles/lab-journal.md](styles/lab-journal.md) | 研究摘要，科学解释，医疗内容，学术论文 |
| **学术论文** | [styles/academic-paper.md](styles/academic-paper.md) | 研究摘要，论文摘要，文献综述，证据密集型解释 |
| **政策论文** | [styles/policy-paper.md](styles/policy-paper.md) | 治理笔记，政策解释，法律相关摘要，内部规则 |
| **海军正式** | [styles/navy-formal.md](styles/navy-formal.md) | 投资者演示文稿，高管摘要，季度报告，企业提案 |
| **日本极简** | [styles/japanese-minimal.md](styles/japanese-minimal.md) | 品牌叙事，文化笔记，安静的产品论文，反思公告 |
| **临床简报** | [styles/clinical-brief.md](styles/clinical-brief.md) | 医疗摘要，医疗笔记，患者教育，临床快照 |

#### 商业、金融和信任

当卡片应看起来像运营、高管或商业可信时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **企业干净** | [styles/corporate-clean.md](styles/corporate-clean.md) | 产品发布，B2B 摘要，高管摘要，正式报告，面向投资者的材料 |
| **VC 演讲稿** | [styles/pitch-deck-vc.md](styles/pitch-deck-vc.md) | 融资卡片，市场机会快照，创业公司增长摘要 |
| **销售室** | [styles/sales-room.md](styles/sales-room.md) | 销售管道，账户快照，交易策略笔记，收入简报 |
| **信任中心** | [styles/trust-center.md](styles/trust-center.md) | 安全笔记，合规摘要，审计更新，面向信任的报告 |
| **合作伙伴渠道** | [styles/partner-channel.md](styles/partner-channel.md) | 合作伙伴摘要，联盟更新，渠道行动，共同销售摘要 |

#### 技术和运营

当精确性、系统语言或实施细节需要主导时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **技术蓝图** | [styles/tech-blueprint.md](styles/tech-blueprint.md) | 技术规格，系统设计文档，架构摘要，工程计划 |
| **工程白蓝图** | [styles/engineering-whiteprint.md](styles/engineering-whiteprint.md) | 架构笔记，API 摘要，实施计划，技术白皮书 |
| **终端绿色** | [styles/terminal-green.md](styles/terminal-green.md) | 基础设施状态卡片，CLI 指南，事件笔记，复古计算主题 |

#### 广播、声明和高对比度

当卡片应宣布、发出紧急信号或留下强烈的视觉冲击时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **强烈对比** | [styles/bold-contrast.md](styles/bold-contrast.md) | 数据高亮，KPI 仪表板，活动公告 |
| **新闻广播** | [styles/news-broadcast.md](styles/news-broadcast.md) | 快速更新，摘要卡片，状态公告，媒体风格回顾 |
| **事件台** | [styles/incident-desk.md](styles/incident-desk.md) | 事件回顾，停机笔记，事后分析，可靠性更新 |
| **新原始 brutalism** | [styles/neo-brutalism.md](styles/neo-brutalism.md) | 勇敢的活动卡片，宣言式摘要，创业公司发布，有力的声明 |
| **瑞士网格** | [styles/swiss-grid.md](styles/swiss-grid.md) | 结构化编辑布局，设计导向报告，字体声明 |

#### 签名视觉身份

当视觉身份本身是信息的一部分时使用。

| 样式 | 文件 | 适合 |
|------|------|------|
| **深夜** | [styles/deep-night.md](styles/deep-night.md) | 娱乐，创意展示，产品揭晓，游戏内容 |
| **玻璃形态** | [styles/glassmorphism.md](styles/glassmorphism.md) | 高端产品揭晓，功能聚焦，活动邀请，面向未来的展示 |

## 布局骨架

首先选择内容结构系列，然后选择该系列内的特定线框。布局保持样式无关。

### 布局系列

#### 核心单主题卡片

当一个主题应主导，而支持内容应保持次要时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **英雄卡片** | [layouts/hero-card.md](layouts/hero-card.md) | 单主题，标题 + 摘要 + 一个支持面板 |
| **引用卡片** | [layouts/quote-card.md](layouts/quote-card.md) | 提引，使命声明，演讲稿引用（附归属） |
| **分割面板** | [layouts/split-panel.md](layouts/split-panel.md) | 两列布局：主要内容 + 侧边栏或左右对比 |
| **堆叠模块** | [layouts/stacked-modules.md](layouts/stacked-modules.md) | 多节垂直流，混合权重区块 |

#### 指标和运营读数

当数字、状态或操作信号需要快速扫描时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **指标板** | [layouts/metric-board.md](layouts/metric-board.md) | KPI 卡片，绩效仪表板，季度回顾，健康检查，指标驱动公告 |
| **财务快照** | [layouts/financial-snapshot.md](layouts/financial-snapshot.md) | 收入摘要，现金视图，绩效快照，单位经济 |
| **销售简报** | [layouts/sales-brief.md](layouts/sales-brief.md) | 销售管道，交易策略，区域销售更新，收入运营 |
| **终端窗口** | [layouts/terminal-window.md](layouts/terminal-window.md) | 状态快照，命令演练，事件更新，运营摘要 |

#### 顺序、路线图和进展

当读者需要阶段、步骤或方向性移动时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **时间线流** | [layouts/timeline-flow.md](layouts/timeline-flow.md) | 顺序步骤，里程碑，过程阶段，垂直时间线 |
| **站点工作流** | [layouts/station-workflow.md](layouts/station-workflow.md) | 详细工作流分解，每个步骤都带有结构化属性（输入/过程/输出/门/持续时间） |
| **路线图板** | [layouts/roadmap-board.md](layouts/roadmap-board.md) | 现在 / 下一步 / 后来规划，战略排序，分阶段推出 |
| **阶梯进展** | [layouts/staircase-progression.md](layouts/staircase-progression.md) | 成熟曲线，分阶段范围累积，逐步构建故事 |
| **漏斗堆叠** | [layouts/funnel-stack.md](layouts/funnel-stack.md) | 销售漏斗，转化流，招聘管道，决策收窄 |
| **事件回顾** | [layouts/incident-review.md](layouts/incident-review.md) | 事后分析，停机回顾，可靠性事件，补救快照 |

#### 比较和决策

当卡片需要明确的权衡、优先级或并排框架时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **优缺点** | [layouts/pros-cons.md](layouts/pros-cons.md) | 权衡分析，决策框架，风险与收益，平衡评估 |
| **象限矩阵** | [layouts/quadrant-matrix.md](layouts/quadrant-matrix.md) | 优先级映射，风险回报框架，投资组合视图，2x2 分类 |
| **矩阵表** | [layouts/matrix-table.md](layouts/matrix-table.md) | MxN 分类网格，两个有意义的轴和原型标记单元格 |
| **比较** | [layouts/comparison.md](layouts/comparison.md) | 并列对比，选项框架，前后对比或 A/B 对比 |
| **原则网格** | [layouts/principle-grid.md](layouts/principle-grid.md) | 编号原则与反模式和应用对比 |

#### 网格和清单

当卡片需要重复模块、混合大小平铺或扫描友好的清单时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **便当网格** | [layouts/bento-grid.md](layouts/bento-grid.md) | 多主题概览，功能展示，混合大小网格单元 |
| **徽章网格** | [layouts/badge-grid.md](layouts/badge-grid.md) | 功能列表，能力目录，技能清单，利益展示 |
| **清单板** | [layouts/checklist-board.md](layouts/checklist-board.md) | 执行跟踪，发布准备，QA 门槛，运营清单 |

#### 系统和关系映射

当结构、相邻关系或网络关系比顺序更重要时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **架构图** | [layouts/architecture-map.md](layouts/architecture-map.md) | 层次系统，平台概述，服务边界，技术蓝图 |
| **分层侧边栏图** | [layouts/layered-sidebar-map.md](layouts/layered-sidebar-map.md) | 层次堆栈由承载交叉线索的上下文轨道包围，KPI 或价值链锚点 |
| **径向中心** | [layouts/radial-hub.md](layouts/radial-hub.md) | 生态系统概述，核心+功能，中心辐射关系 |

#### 文档和备忘录逻辑

当卡片应像结构化简报一样阅读时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **研究摘要** | [layouts/research-abstract.md](layouts/research-abstract.md) | 摘要摘要卡片，研究结果，证据综合，论文快照 |
| **会议备忘录** | [layouts/board-memo.md](layouts/board-memo.md) | 高管更新，决策备忘录，季度会议笔记，领导摘要 |
| **政策备忘录** | [layouts/policy-memo.md](layouts/policy-memo.md) | 内部政策变更，治理决定，流程规则，指导笔记 |
| **教育模块** | [layouts/education-module.md](layouts/education-module.md) | 课程总结，学习路径，工作坊模块，教学卡片 |
| **医疗保健摘要** | [layouts/healthcare-summary.md](layouts/healthcare-summary.md) | 临床概述，患者摘要，护理快照，健康教育 |

#### 治理、风险和审计

当所有权、控制状态和缓解细节必须明确时使用。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **风险登记册** | [layouts/risk-register.md](layouts/risk-register.md) | 风险跟踪，缓解规划，合规审查，项目治理 |
| **合规审计** | [layouts/compliance-audit.md](layouts/compliance-audit.md) | 审计摘要，控制审查，安全态势检查，合规跟踪 |

#### 叙事和利益相关者更新

当内容是关于人员、团队、客户或合作伙伴行动时使用。

原始笔记：`org-update`，`customer-story` 和 `partner-brief` 现在共享一个轻量级的 `card-brief-*` 外部节奏。除非结构实际上是关于关系或利益相关者行动而不是标题节奏，否则保留 `news-bulletin` 分开。

| 布局 | 文件 | 最佳用途 |
|------|------|----------|
| **新闻公告** | [layouts/news-bulletin.md](layouts/news-bulletin.md) | 紧急更新，摘要卡片，状态公告，新闻风格回顾 |
| **组织更新** | [layouts/org-update.md](layouts/org-update.md) | 团队变更，招聘更新，所有权转移，领导沟通 |
| **客户故事** | [layouts/customer-story.md](layouts/customer-story.md) | 案例研究，前后结果，客户胜利，采用叙事 |
| **合作伙伴简报** | [layouts/partner-brief.md](layouts/partner-brief.md) | 联盟更新，共同销售笔记，合作伙伴摘要，渠道回顾 |

### 家庭对齐说明

- 优先选择现有家庭原始元素，而不是发明新的类名。当前对齐的布局系列包括 `card-doc-*`，`card-kpi-*`，`card-sequence-*`，`card-tile-*`，`card-map-*`，`card-compare-*`，`card-review-*`，`card-topic-*` 和 `card-brief-*`。
- 当一个新布局明显属于其中之一时，首先变化几何形状和修饰符。不要为相同角色创建平行的原始词汇表。
- 明确的特殊情况故意分开：`quote-card`，`terminal-window`，`news-bulletin`，以及最强的身份驱动样式主题，如 `deep-night` 和 `glassmorphism`。
- 如果布局或样式仅共享情感而非结构，请在文本中记录家庭关系，而不是强制额外的原始合并。

## 设计原则

### 空间和呼吸空间

- 卡片边缘填充：`32px–48px`
- 模块间隙：`16px–24px`
- 标题区域必须有充足的行高（`1.1–1.3`）和与正文清晰的分隔
- 永远不要将内容挤向卡片边缘

### 视觉强调

- 使用 `4px–6px` 厚的规则作为区域分隔符或强调边框
- 使用微妙的着色背景（`rgba(0,0,0,0.03)` 或样式特定色调）为次要面板
- 强调色应克制：一个高亮颜色用于规则、标签或关键数字
- 可选：`4%` 噪声覆盖（见样式模板）用于纸张纹理

### 内容节奏

- 高密度卡片：分组为概览 → 核心判断 → 支持模块 → 结论
- 排名内容：非对称英雄 + 结构化列表（避免等宽平铺）
- 教学分析内容：概览 → 核心见解 → 详细区块 → 边界/注意事项 → 总结

## 样式参考

### 常见类（跨所有样式共享）

- `.card-frame` — 外部容器具有最大宽度和填充
- `.card` — 主卡片表面具有背景、填充和可选的噪声覆盖
- `.card-meta` — 元数据行（类别、日期、版本）使用小写大写字母
- `.card-title` — 主标题
- `.card-subtitle` — 副标题或摘要
- `.card-bar` — 厚强调规则分隔符
- `.card-body` — 正文段落
- `.card-body.dropcap` — 第一段带有下沉首字母（编辑开场）
- `.card-highlight` — 独立短句（< 25 字符）带有左侧强调边框，用于关键见解
- `.card-grid` — 网格容器；`.card-grid-2` 用于两列
- `.card-panel` — 内容面板带有边框顶部强调
- `.card-panel.heavy` — 更重的面板，更多填充
- `.card-panel.light` — 较轻的面板，更薄的边框
- `.card-panel-title` — 面板标题使用小写大写字母
- `.card-panel-text` — 面板正文
- `.card-item` — 带有标签的标题内容块（标签 + 描述对）
- `.card-item-label` — 项目标题/标签
- `.card-tag` — 内联标签/徽章
- `.card-stat` — 超大数字/指标显示
- `.card-stat-label` — 统计标签下方
- `.card-divider` — 两个部分之间的细水平规则
- `.card-footer` — 底部条用于来源、归属或笔记
- `.card-endmark` — 内容结束标记（∎）用于编辑结束

### 富文本元素

**下沉首字母**（仅第一段——创建编辑开场仪式）：
```html
<p class="card-body dropcap">First paragraph text...</p>
```

**高亮引用**（独立见解，< 25 字符，带有左侧强调边框）：
```html
<p class="card-highlight">Key insight phrase</p>
```

**带标题的项目**（标签 + 描述对，用于结构化列表）：
```html
<div class="card-item">
  <p class="card-item-label">Item Title</p>
  <p class="card-panel-text">Item description text.</p>
</div>
```

**区域分隔符**：
```html
<div class="card-divider"></div>
```

**结束标记**（编辑结束，放置在内容末尾）：
```html
<span class="card-endmark">∎</span>
```

## 最佳实践

### 内容指南
1. **仅直接嵌入** — 始终将 HTML 直接嵌入 Markdown 中，绝不要使用 ` ```html ` 代码块
2. **结构中无空行** — 保持整个 HTML 块连续
3. **首先判断密度** — 在选择布局之前决定低/中/高
4. **保护用户标题** — 绝不要无声地重写提供的标题
5. **平衡视觉权重** — 至少一个较重的模块，一个中等，一个较轻
6. **一致使用字体比例** — 遵循上面定义的大小层级
7. **克制使用强调** — 一个强调色，谨慎使用于规则和高亮
8. **有意填充空间** — 如果一个部分看起来为空，则先重构层级，然后再添加填充内容
