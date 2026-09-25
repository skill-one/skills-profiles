# 信息图可视化工具

> **⚠️ 检查模板：** 错误的模板名称会导致渲染失败。

## 使用场景及可用模板

**✅ 使用信息图当：**
- **功能列表 / 复选清单**：`list-grid-badge-card`, `list-grid-candy-card-lite`, `list-grid-ribbon-card`, `list-column-done-list`, `list-column-vertical-icon-arrow`, `list-column-simple-vertical-arrow`, `list-row-horizontal-icon-arrow`, `list-row-simple-illus`, `list-sector-plain-text`, `list-zigzag-down-compact-card`, `list-zigzag-down-simple`, `list-zigzag-up-compact-card`, `list-zigzag-up-simple`
- **时间线 / 里程碑**：`sequence-timeline-simple`, `sequence-timeline-rounded-rect-node`, `sequence-timeline-simple-illus`
- **分步流程**：`sequence-snake-steps-simple`, `sequence-snake-steps-compact-card`, `sequence-snake-steps-underline-text`, `sequence-stairs-front-compact-card`, `sequence-stairs-front-pill-badge`, `sequence-ascending-steps`, `sequence-ascending-stairs-3d-underline-text`, `sequence-circular-simple`, `sequence-pyramid-simple`, `sequence-mountain-underline-text`, `sequence-cylinders-3d-simple`, `sequence-zigzag-steps-underline-text`, `sequence-zigzag-pucks-3d-simple`, `sequence-horizontal-zigzag-underline-text`, `sequence-horizontal-zigzag-simple-illus`, `sequence-color-snake-steps-horizontal-icon-line`
- **产品路线图**：`sequence-roadmap-vertical-simple`, `sequence-roadmap-vertical-plain-text`
- **漏斗 / 转化**：`sequence-filter-mesh-simple`, `sequence-funnel-simple`
- **A 与 B 对比**：`compare-binary-horizontal-underline-text-vs`, `compare-binary-horizontal-simple-fold`, `compare-binary-horizontal-badge-card-arrow`, `compare-hierarchy-left-right-circle-node-pill-badge`
- **SWOT 分析**：`compare-swot`
- **优先级矩阵 2×2**：`quadrant-quarter-simple-card`, `quadrant-quarter-circular`, `quadrant-simple-illus`
- **组织树 / 层级**：`hierarchy-tree-tech-style-capsule-item`, `hierarchy-tree-curved-line-rounded-rect-node`, `hierarchy-tree-tech-style-badge-card`, `hierarchy-structure`
- **饼图 / 环形图**：`chart-pie-plain-text`, `chart-pie-compact-card`, `chart-pie-donut-plain-text`, `chart-pie-donut-pill-badge`
- **柱状图 / 条形图**：`chart-bar-plain-text`, `chart-column-simple`, `chart-line-plain-text`
- **词云**：`chart-wordcloud`
- **关系 / 圆形**：`relation-circle-icon-badge`, `relation-circle-circular-progress`

## 语法结构

```plain
infographic <template-name>
data
  title 标题
  desc 描述
  items
    - label 标签
      value 12.5
      desc 说明
      icon mdi/rocket-launch
theme
  palette #3b82f6 #8b5cf6 #f97316
```

**规则：** 第一行 `infographic <template-name>`（必须匹配模板列表） | 2 空格缩进 | `key value` 对（空格分隔，**不是** `key: value`） | `-` 前缀用于数组 | 对比模板需要恰好 2 个根项带有 `children` | SWOT 需要 4 个项（Strengths/Weaknesses/Opportunities/Threats 英文） | 四象限需要 4 个项带有 `children` | 列表模板使用 `desc` 而不是 `value` | `hierarchy-structure` 最大 3 级 | 使用 `desc` 而不是 `description` | 使用 `items` 而不是 `steps`

### ⚠️ 常见错误（会导致渲染失败）

```plain
❌ 错误 — 不要使用 YAML 冒号语法：
template: list-grid-badge-card     ← 错误！没有 "template:" 键
title: My Title                    ← 错误！不允许冒号
items:                             ← 错误！`items` 后面没有冒号
  - label: Item One                ← 错误！`label` 后面没有冒号
    description: Some text         ← 错误！字段是 "desc" 不是 "description"
    value: "100"                   ← 错误！没有冒号，值必须是数字
steps:                             ← 错误！字段是 "items" 不是 "steps"
left:                              ← 错误！对比使用 2 个根项 + `children`
  label: Option A                  ← 错误！对比结构是扁平项
quadrants:                         ← 错误！四象限使用 4 个项 + `children`

✅ 正确 — 空格分隔的 key-value，2 空格缩进：
infographic list-grid-badge-card
data
  title My Title
  items
    - label Item One
      desc Some text
      value 100
```

## 数据字段

| 字段 | 描述 | 示例 |
|-------|-------------|---------|
| `label` | 项标题/名称（必填） | `label Q1 销售额` |
| `desc` | 描述文本 | `desc $1.28B \| +20%` |
| `value` | 数值（仅用于图表/漏斗） | `value 128` |
| `time` | 时间标签（仅用于时间线模板） | `time Q1 2024` |
| `icon` | 图标：`mdi/icon-name` ([Iconify](https://icon-sets.iconify.design/)) | `icon mdi/star` |
| `illus` | 插图名称 ([unDraw](https://undraw.co/illustrations)) | `illus coding` |
| `children` | 嵌套项（用于层级/对比） | 查看示例 |
| `done` | 完成状态（用于复选清单） | `done true` |

## 核心示例

### 功能网格 (list-grid-badge-card)
```infographic
infographic list-grid-badge-card
data
  title 关键指标
  desc 年度表现概览
  items
    - label 总收入
      desc $1.28B | 同比增长 23.5%
    - label 新客户
      desc 3280 | 同比增长 45%
    - label 满意度
      desc 94.6% | 行业领先
    - label 市场份额
      desc 18.5% | 排名 #2
```

### 时间线 (sequence-timeline-simple)
时间线项使用 `time` 作为时间标签，`label` 作为里程碑名称。
```infographic
infographic sequence-timeline-simple
data
  title 产品路线图
  items
    - label 研究
      time Q1 2024
      desc 研究阶段
    - label 设计
      time Q2 2024
      desc 设计阶段
    - label 开发
      time Q3 2024
      desc 开发
    - label 发布
      time Q4 2024
      desc 发布
```

### 漏斗图 (sequence-filter-mesh-simple)
```infographic
infographic sequence-filter-mesh-simple
data
  title 销售漏斗
  items
    - label 潜在客户
      value 10000
      desc 市场潜在客户
    - label 合格客户
      value 2500
      desc 转化率 25%
    - label 提案
      value 800
      desc 转化率 32%
    - label 已成交
      value 328
      desc 转化率 41%
```

### 复查清单 (list-column-done-list)
```infographic
infographic list-column-done-list
data
  title 发布复查清单
  items
    - label 代码审查完成
      done true
    - label 测试通过
      done true
    - label 文档更新
      done false
    - label 部署到生产环境
      done false
```

### A 与 B 对比 (compare-binary-horizontal-underline-text-vs)
```infographic
infographic compare-binary-horizontal-underline-text-vs
data
  title 云服务与本地部署
  items
    - label 云服务
      children
        - label 按需扩展
        - label 按量付费
    - label 本地部署
      children
        - label 完全控制
        - label 一次性成本
```

### SWOT 分析 (compare-swot)
必须恰好 4 个项，带有英文标签：Strengths（优势）、Weaknesses（劣势）、Opportunities（机会）、Threats（威胁）
```infographic
infographic compare-swot
data
  title 战略分析
  items
    - label 优势
      children
        - label 强大的研发
        - label 完整的供应链
    - label 劣势
      children
        - label 品牌知名度有限
        - label 成本高
    - label 机会
      children
        - label 数字化转型
        - label 新兴市场
    - label 威胁
      children
        - label 激烈竞争
        - label 市场变化
```

### 饼图/环形图 (chart-pie-donut-plain-text)
```infographic
infographic chart-pie-donut-plain-text
data
  title 按产品划分的收入
  items
    - label 企业软件
      value 42
    - label 云服务
      value 28
    - label 硬件
      value 18
    - label 服务
      value 12
```

### 组织树 (hierarchy-tree-tech-style-capsule-item)
```infographic
infographic hierarchy-tree-tech-style-capsule-item
data
  title 组织结构
  items
    - label CEO
      children
        - label 工程副总裁
          children
            - label 前端团队
            - label 后端团队
        - label 产品副总裁
          children
            - label 设计
            - label 研究
```

### 优先级矩阵 (quadrant-quarter-simple-card)
四象限模板需要恰好 4 个根项，每个带有 `children`。4 个项代表四个象限。
```infographic
infographic quadrant-quarter-simple-card
data
  title 优先级矩阵
  items
    - label 首先执行
      desc 紧急且重要
      children
        - label 严重 Bug
        - label 客户截止日期
    - label 安排
      desc 不紧急但重要
      children
        - label 规划
        - label 培训
    - label 分配
      desc 紧急但不重要
      children
        - label 会议
        - label 一些邮件
    - label 消除
      desc 不紧急且不重要
      children
        - label 浪费时间的事情
        - label 忙碌的工作
```

## 输出格式

````markdown
```infographic
infographic <template-name>
data
  title 您的标题
  items
    - label 项目 1
      desc 描述在此
```
````

### 主题（可选）

将 `theme` 块作为 `data` 的**同级元素**添加（不要嵌套在 `data` 内）：

```plain
# 预设主题（单行）
theme dark

# 自定义调色板
infographic list-grid-badge-card
theme
  palette #3b82f6 #8b5cf6 #f97316
data
  title 我的标题
  items
    - label 项目 1
```

可用预设：`dark`, `hand-drawn`

## 相关文件

> 关于详细语法、模板和示例，请参考以下参考资料：

- [syntax.md](references/syntax.md) — 完整语法规范和规则
- [templates.md](references/templates.md) — 所有可用模板及其描述
- [examples.md](references/examples.md) — 每个模板类别的完整示例

## 资源

- [AntV 信息图画廊](https://infographic.antv.vision/examples)
- [Iconify 图标](https://icon-sets.iconify.design/)
- [unDraw 插图](https://undraw.co/illustrations)
