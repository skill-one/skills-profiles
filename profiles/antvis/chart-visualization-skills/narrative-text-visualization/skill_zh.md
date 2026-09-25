# 叙事文本可视化技能

这项技能提供了一种将数据转换为结构化叙事文本可视化的工作流程，使用 **T8 语法**——一种声明式的类似 Markdown 的语言，用于创建带有语义实体标注的数据叙事。

## 什么是 T8

T8 是 AntV 技术栈下的一种文本可视化解决方案，专为基于洞察的叙事文本显示而设计。它不是手动构建 DOM 元素，而是您只需编写简单、人类可读的语法来描述您的数据叙事。

**主要特性：**
- **对大型语言模型友好**：语法直观，可被 AI 模型轻松生成
- **声明式与可读性**：写您想要的内容，而不是如何构建它
- **框架无关**：可与 React、Vue 或原生 JavaScript 一起使用
- **标准化样式**：默认专业外观
- **内置数据可视化**：迷你图表（饼图、折线图）是语法的原生特性
- **轻量级**：gzip 压缩前小于 20KB

## 工作流程

要生成叙事文本可视化，请按照以下步骤操作：

### 1. 理解需求

分析用户请求以确定：
- 要分析的主题或数据
- 需要的叙事类型（报告、摘要、文章）
- 需要强调的关键洞察
- 任何特定的数据源或指标

### 2. 生成 T8 语法内容

按照以下规范使用 T8 语法创建叙事文本。内容必须包括：
- 正确的文档结构（标题、段落、列表）
- 所有有意义的实体的实体标注
- 实体的适当元数据（来源、评估等）

### 3. 生成前端代码

创建 HTML、React 或 Vue 代码来渲染 T8 内容，基于用户的框架偏好。

### 4. 验证输出

确保：
- 所有数据来自真实来源
- 最小内容长度（800 字或等效内容）
- 全程正确的实体标注
- 清晰的结构和逻辑流程

---

## T8 语法规范

T8 语法是一种类似 Markdown 的语言，用于创建带有语义实体标注的叙事文本。它使数据分析报告更具表现力和视觉吸引力。

### 文档结构

#### 标题（6 级）

使用标准的 Markdown 标题语法：

```
# 一级标题（主标题）
## 二级标题（章节）
### 三级标题（子章节）
#### 四级标题
##### 五级标题
###### 六级标题
```

**规则：**
- 每个标题必须独占一行
- 在 `#` 符号后添加一个空格
- 标题在渲染输出中创建视觉层次结构

#### 段落

常规文本段落由空行分隔：

```
这是第一段文本，包含一些内容。

这是第二段文本，由一个空行分隔。
```

**规则：**
- 段落可以跨越多行
- 使用空行分隔不同的段落
- 段落内的文本自然流动

#### 列表

T8 语法支持无序列表和有序列表。

**无序列表：**
```
- 第一项
- 第二项
- 第三项
```

**有序列表：**
```
1. 第一步
2. 第二步
3. 第三步
```

**规则：**
- 每个列表项必须独占一行
- 在项目符号标记（-，*）或数字后添加一个空格
- 列表可以包含实体和文本格式化

### 文本格式化

T8 语法使用 Markdown 语法支持内联文本格式化：

**粗体文本**：`这是**粗体文本**，突出显示。`

**斜体文本**：`这是*斜体文本*，用于强调。`

**下划线文本**：`这是__下划线文本__，表示重要性。`

**链接**：`访问[我们的网站](https://example.com)获取更多信息。`

**规则：**
- 格式化标记必须平衡（开启和关闭）
- 格式化可以与实体结合使用
- 链接使用 `[文本](URL)` 语法，其中 URL 以 `http://`、`https://` 或 `/` 开头

### 实体标注语法

T8 语法的核心特性是**实体标注**——用语义含义和元数据标注特定数据点。

#### 基本实体语法

```
[显示文本](实体类型)
```

- `显示文本`：读者看到的文本
- `实体类型`：此实体的语义类型

**示例：**
```
销售额[收入](metric_name)达到[150 万](metric_value)元本季度。
```

#### 带元数据的实体

```
[显示文本](实体类型, key1=value1, key2=value2, key3="字符串值")
```

**元数据规则：**
- 用逗号分隔多个元数据字段
- 数字和布尔值：直接写入（例如，`origin=1500000`，`active=true`）
- 字符串：用双引号括起来（例如，`unit="元"`，`region="亚洲"`）

**示例：**
```
收入增长了[15.3%](ratio_value, origin=0.153, assessment="positive")，与去年相比。
```

### 实体类型参考

使用这些实体类型来标注不同类型的数据：

| 实体类型          | 描述                          | 使用场景                                    | 示例                                                         |
| ---------------- | ----------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| `metric_name`        | 指标或 KPI 的名称              | 当提到您正在衡量什么时                      | "收入", "用户数量", "市场份额"                              |
| `metric_value`       | 主要指标值                     | 报告的主要数字/值                           | "150 万", "50,000 用户", "250 个单位"                      |
| `other_metric_value` | 次要或支持性指标值             | 提供背景的其他指标                          | "平均订单价值：$120"                                        |
| `delta_value`        | 绝对变化/差异                 | 当显示两个时期之间的数字变化时              | "+1,200 个单位", "-$50K", "增加了 500"                    |
| `ratio_value`        | 百分比变化/比率               | 当显示百分比变化时                         | "+15.3%", "-5.2%", "增长了 23%"                            |
| `contribute_ratio`   | 贡献百分比                    | 当显示某事物贡献了百分之多少                | "占 45%"，"代表总量的 30%"                                |
| `trend_desc`         | 趋势描述                      | 描述变化的方向/模式                        | "稳步上升"，"下降趋势"，"稳定"                             |
| `dim_value`          | 维度值/分类                   | 地理、分类或细分数据                        | "北美洲"，"企业细分"，"2024 年第三季度"                    |
| `time_desc`          | 时间段或时间戳                 | 当指定某事何时发生时                        | "2024 年第三季度"，"1 月至 3 月"，"财政年度 2023"           |
| `proportion`         | 比例或比率                    | 当表达整体的一部分时                        | "5 个中的 3 个"，"60% 的客户"                             |
| `rank`               | 排名或位置                    | 当指示列表中的顺序或位置时                  | "排名第一"，"前 3 名"，"第 5 名"                           |
| `difference`         | 比较差异                      | 当突出显示两个项目之间的差异时              | "差异为 50K"，"差距为 200 个单位"                         |
| `anomaly`            | 异常或意外值                  | 当指出离群值或异常时                        | "异常激增"，"意外下降"                                     |
| `association`        | 关系或相关性                  | 当描述指标之间的联系时                      | "强相关性"，"与...相关"，"关联"                            |
| `distribution`       | 数据分布模式                  | 当描述数据如何分布时                        | "均匀分布"，"集中在"，"分布在"                             |
| `seasonality`        | 季节性模式或趋势              | 当描述周期性季节性模式时                    | "第四季度高峰"，"假日期间"，"第四季度激增"                  |

### 常见元数据字段

添加这些可选字段以提供更丰富的数据上下文：

#### `origin` (数字)

显示文本背后的原始数值。

**示例：**
- `[150 万](metric_value, origin=1500000)`
- `[23.7%](ratio_value, origin=0.237)`
- `[5.2K 用户](metric_value, origin=5200)`
- `[3 个中的 4 个](proportion, origin=0.75)`

**为什么使用它：** 启用数据可视化、排序和计算

#### `assessment` (字符串)

评估变化是积极的、消极的还是中性的。

**有效值：** `"positive"`，`"negative"`，`"equal"`，`"neutral"`

**示例：**
- `[增长了 15%](ratio_value, assessment="positive")`
- `[下降了 8%](ratio_value, assessment="negative")`
- `[保持不变](trend_desc, assessment="equal")`

**为什么使用它：** 启用视觉指示器（颜色、图标）来表示好/坏的趋势

#### `unit` (字符串)

值的计量单位。

**示例：**
- `[150 万](metric_value, origin=1500000, unit="元")`
- `[150](metric_value, unit="单位")`

#### `detail` (任何)

用于图表渲染的附加上下文或细分数据。某些实体类型需要此字段。

**需要此字段的实体类型：**
- `rank`：表示排名数据的数字数组
  - 示例：`[顶尖表现者](rank, detail=[5, 8, 12, 15, 20])`
- `difference`：显示比较值的数字数组
  - 示例：`[差距收窄](difference, detail=[100, 80, 60, 40])`
- `anomaly`：突出显示离群值的数字数组
  - 示例：`[异常激增](anomaly, detail=[10, 12, 11, 45, 13])`
- `association`：表示相关性数据的 {x, y} 对象数组
  - 示例：`[强相关性](association, detail=[{"x":1,"y":2},{"x":2,"y":4},{"x":3,"y":6}])`
- `distribution`：显示数据分布的数字数组
  - 示例：`[分布不均](distribution, detail=[5, 15, 45, 25, 10])`
- `seasonality`：带有数据数组和可选范围的对象
  - 示例：`[第四季度高峰](seasonality, detail={"data":[10,12,15,30],"range":[0,40]})`

**其他类型的可选示例：**
- `[稳定增长](trend_desc, detail=[100, 120, 145, 180, 210])`

---

## 数据要求

**关键**：所有数据必须来自公开的真实来源：
- 官方公告/财务报告
- 权威媒体（路透社、彭博、TechCrunch 等）
- 行业研究机构（IDC、Canalys、Counterpoint Research 等）
- **绝不使用虚构、AI 猜测或模拟数据**
- 使用具体数字（例如，"146 百万单位"，"7058 个单位"），而不是模糊的近似值

---

## 完整的 T8 语法示例

```
# 2024 智能手机市场分析

## 市场概述

全球 [智能手机出货量](metric_name) 在 2024 年达到 [12 亿台](metric_value, origin=1200000000) 单位，同比 [温和下降 2.1%](ratio_value, origin=-0.021, assessment="negative")。

**高端市场**（设备价格超过 800 元）显示出 *显著的韧性* (trend_desc, assessment="positive")，增长了 [5.8%](ratio_value, origin=0.058, assessment="positive")。[平均销售价格](other_metric_value) 为 [$420](metric_value, origin=420, unit="USD")。

## 关键发现

1. [亚太地区](dim_value) 仍然是最大的市场
2. [高端设备](dim_value) 显示出 **强劲增长**
3. 入门级市场面临 *挑战*

## 区域细分

### 亚太地区

[亚太地区](dim_value) 仍然是最大的市场，出货量为 [6.8 亿台](metric_value, origin=680000000) 单位，尽管这代表从上一年下降了 [1.8 亿台](delta_value, origin=-180000000, assessment="negative")。

主要市场：
- [中国](dim_value)：[3.2 亿台](metric_value, origin=320000000) - 下降 [8.5%](ratio_value, origin=-0.085, assessment="negative")，全球 [排名第一](rank, detail=[320, 180, 90, 65, 45])，占区域销售的 [47%](contribute_ratio, origin=0.47, assessment="positive")
- [印度](dim_value)：[1.8 亿台](metric_value, origin=180000000) - 增长 [12.3%](ratio_value, origin=0.123, assessment="positive")，全球 [排名第二](rank, detail=[320, 180, 90, 65, 45])
- [东南亚](dim_value)：[1.8 亿台](metric_value, origin=180000000) - [稳定](trend_desc, assessment="equal")

有关详细方法，请访问 [我们的研究页面](https://example.com/methodology)。
```

---

## 在 HTML、React 和 Vue 中使用 T8

### 通过 CDN 在 HTML 中使用

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>T8 叙事文本</title>
</head>
<body>
  <div id="container"></div>

  <!-- 从 unpkg CDN 导入 T8 -->
  <script src="https://unpkg.com/@antv/t8/dist/t8.min.js"></script>
  
  <script>
    // T8 作为全局变量可用
    const { Text } = window.T8;

    // 初始化 T8 实例
    const text = new Text(document.getElementById('container'));

    // 使用 T8 语法渲染叙事文本
    const narrativeText = `
# 销售报告

本季度，[订单](metric_name) 高于正常水平。它们是 [34.8 万](metric_value, origin=348.12)。

[订单](metric_name) 相对于去年同期的增长为 [18.03 万](delta_value, assessment="positive")。
    `;

    text.theme('light').render(narrativeText);
  </script>
</body>
</html>
```

**安装：**
```bash
npm install @antv/t8
# 或
yarn add @antv/t8
```

### 在 React 中使用

```tsx
import { Text } from '@antv/t8';
import { useEffect, useRef } from 'react';

function T8Component() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 初始化 T8 实例
    const text = new Text(containerRef.current);

    // 使用 T8 语法渲染叙事文本
    const narrativeText = `
# 销售报告

本季度，[订单](metric_name) 高于正常水平。它们是 [34.8 万](metric_value, origin=348.12)。

[订单](metric_name) 相对于去年同期的增长为 [18.03 万](delta_value, assessment="positive")。
    `;

    text.theme('light').render(narrativeText);

    // 卸载时清理
    return () => {
      text.unmount();
    };
  }, []);

  return <div ref={containerRef} />;
}

export default T8Component;
```

### 在 Vue 3 中使用

```vue
<template>
  <div ref="containerRef"></div>
</template>

<script setup lang="ts">
import { Text } from '@antv/t8';
import { ref, onMounted, onBeforeUnmount } from 'vue';

const containerRef = ref<HTMLDivElement>();
let textInstance: Text | null = null;

onMounted(() => {
  if (!containerRef.value) return;

  // 初始化 T8 实例
  textInstance = new Text(containerRef.value);

  // 使用 T8 语法渲染叙事文本
  const narrativeText = `
# 销售报告

本季度，[订单](metric_name) 高于正常水平。它们是 [34.8 万](metric_value, origin=348.12)。

[订单](metric_name) 相对于去年同期的增长为 [18.03 万](delta_value, assessment="positive")。
  `;

  textInstance.theme('light').render(narrativeText);
});

onBeforeUnmount(() => {
  if (textInstance) {
    textInstance.unmount();
  }
});
</script>
```

### 在 Vue 2 中使用

```vue
<template>
  <div ref="container"></div>
</template>

<script>
import { Text } from '@antv/t8';

export default {
  name: 'T8Component',
  data() {
    return {
      textInstance: null,
    };
  },
  mounted() {
    // 初始化 T8 实例
    this.textInstance = new Text(this.$refs.container);

    // 使用 T8 语法渲染叙事文本
    const narrativeText = `
# 销售报告

本季度，[订单](metric_name) 高于正常水平。它们是 [34.8 万](metric_value, origin=348.12)。

[订单](metric_name) 相对于去年同期的增长为 [18.03 万](delta_value, assessment="positive")。
    `;

    this.textInstance.theme('light').render(narrativeText);
  },
  beforeDestroy() {
    if (this.textInstance) {
      this.textInstance.unmount();
    }
  },
};
</script>
```

---

## 写作指南和最佳实践

### 内容要求

1. **最小长度**：不少于 800 字（根据数据复杂性调整）
2. **结构**：清晰的层次结构，各章节之间有逻辑流程
3. **分析**：不要只列数字——解释其重要性和上下文
4. **语气**：自然、流畅、客观、专业
5. **实体使用**：标注所有有意义的数字——指标、值、趋势、时间、变化、百分比

### 实体标注最佳实践

1. **全面性**：标注所有定量数据，而不仅仅是主要数字
2. **使用适当的类型**：选择最能描述语义含义的实体类型
3. **添加元数据**：在适用时添加 `origin`、`assessment` 和其他相关字段
4. **自然流动**：实体应与可读的散文无缝融合

### 需要标注的内容

✅ **要标注：**
- 所有数值（收入、数量、测量值）
- 所有百分比（变化、贡献、比例）
- 指标名称和 KPI
- 时间段
- 地理区域和类别
- 趋势描述
- 比较和变化

❌ **不要标注：**
- 没有特定数据含义的通用文本
- 连接短语和过渡
- 不代表可测量概念的上下文

---

## 输出格式

为用户生成 T8 语法内容时：
1. 直接输出 T8 语法内容，不要用代码块包裹
2. 根据用户偏好提供前端代码（HTML/React/Vue）
3. 确保所有实体都带有适当的元数据标注
4. 验证内容是否满足最小长度和质量要求

渲染输出提供：
- 丰富的语义标记数据实体
- 交互式实体高亮
- 清晰的视觉层次结构
- 专业报告式格式
- 响应式设计，适用于所有设备

---

## 参考链接

- T8 GitHub 仓库：https://github.com/antvis/T8
- T8 文档：https://github.com/antvis/T8/blob/main/site/zh-CN/tutorial/quick-start.md
- T8 语法参考：https://github.com/antvis/T8/blob/main/prompt.md
