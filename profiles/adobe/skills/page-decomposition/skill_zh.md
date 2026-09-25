# 页面分解

分析一个区域内的内容序列，并提供中性的描述，不分配区块名称。

## 使用此技能的场景

此技能由 **identify-page-structure** 对每个区域调用，以：
- 识别该区域内的内容序列
- 提供中性的描述（尚未命名区块）
- 识别序列之间的断点
- 允许后续的以作者为中心的决策

**重要提示：** 此技能一次分析一个区域，而不是整个页面。

## 所需输入

从调用技能（identify-page-structure），您需要：
- 区域的视觉描述和边界
- 显示该区域的截图
- 该区域的清理后的HTML内容

## 相关技能

- **page-import** - 顶层协调器
- **identify-page-structure** - 对每个区域调用此技能（步骤2b）
- **block-inventory** - 分解后提供可用区块
- **content-modeling** - 分解后做出作者决策
- **content-driven-development** - 在html-structure.md中引用区域结构

## 关键概念

**内容层次结构：**
```
DOCUMENT
├── SECTION (顶层，由identify-page-structure步骤2a分析)
│   ├── 内容序列1 ← 此技能识别这些
│   ├── 内容序列2 ← 此技能识别这些
│   └── ...
└── SECTION
    └── 内容序列1
```

**什么是“内容序列”？**
一个垂直排列的相关内容流，最终将成为：
- 默认内容（标题、段落、列表、内联图像），或
- 一个区块（结构化、重复或交互式组件）

**序列之间的断点：**
- 内容类型的视觉/语义转变
- 从散文转变为结构化模式
- 从一种模式转变为不同模式

**理念：**
- 描述你看到的内容，而不是它应该是什么
- “两个图像并排”而不是“列区块”
- “8个项目的网格，带有图标”而不是“卡片区块”
- 保持中立 - 作者决策稍后到来

## 分解工作流程

**背景：** identify-page-structure 已经识别了区域边界（步骤2a）。此技能被调用以分析一个区域的内部内容序列。

---

### 步骤1：检查区域

仅查看此区域的截图和HTML。

**需要观察：**
- 从上到下的内容垂直流
- 内容类型或模式何时改变
- 视觉分组或断点

**忽略：**
- 其他区域（超出范围）
- 区域样式（已由page-import识别）
- 区块名称（保持中立）

**输出：** 此区域内内容流的思维模型

---

### 步骤2：识别断点

找到内容从一个类型/模式转变为另一个类型/模式的地方。

**断点指示器：**
- 散文文本 → 结构化网格
- 标题/段落 → 并排的图像
- 一种重复模式 → 不同的重复模式
- 结构化内容 → 散文文本

**示例在一个区域内：**
```
内容从上到下流动：
- 大标题
- 段落
- 两个按钮
[BREAK] ← 视觉/语义转变
- 两个并排显示的图像
```

**输出：** 断点列表

---

### 步骤3：定义内容序列

每个断点之间是一个内容序列。

**对于每个序列，描述：**
- 它包含哪些元素（标题、段落、图像等）
- 它们如何排列（堆叠、并排、在网格中）
- 数量（一个标题、两个图像、8个项目的网格）

**使用中性语言：**
- ✅ "两个并排显示的图像"
- ❌ "带有两个图像的列区块"
- ✅ "8个项目的网格，每个项目带有图标和简短文本"
- ❌ "卡片区块"
- ✅ "居中大型标题、段落、两个垂直堆叠的按钮"
- ❌ "英雄区块"

**输出：** 每个序列的中性描述

---

### 步骤4：返回结构化输出

以结构化格式提供此区域的内容序列。

**输出格式：**
```javascript
{
  sectionNumber: 1,  // 来自identify-page-structure
  sequences: [
    {
      sequenceNumber: 1,
      description: "Large centered heading, paragraph, two buttons stacked vertically"
    },
    {
      sequenceNumber: 2,
      description: "Two images displayed side-by-side"
    }
  ]
}
```

**这可以实现：**
- 清晰理解区域的内部结构
- 中性基础用于作者决策
- 描述与实现的分离

---

## 区域元数据格式

**表格格式：**
```markdown
+------------------------------+
| 区域元数据             |
+------------------+-----------+
| style            | light     |
+------------------+-----------+
```

**位置：** 每个区域的开始处，内容之前

**用途：** 由generate-import-html技能在生成最终HTML时应用

---

## 示例

### 示例1：英雄区域

**输入：** "区域1（浅色背景）：页面顶部的大突出内容"

**视觉观察：**
- 居中大型标题
- 标题下方的段落文本
- 两个行动号召按钮
[BREAK - 视觉转变]
- 两个并排显示的大图像

**输出：**
```javascript
{
  sectionNumber: 1,
  sequences: [
    {
      sequenceNumber: 1,
      description: "Large centered heading, paragraph, two call-to-action buttons stacked vertically"
    },
    {
      sequenceNumber: 2,
      description: "Two large images displayed side-by-side"
    }
  ]
}
```

---

### 示例2：功能区域

**输入：** "区域2（浅色背景）：功能项目网格"

**视觉观察：**
- 居中标题
[BREAK - 转变为结构化模式]
- 8个项目网格
- 每个项目包含：小图标、简短文本描述
[BREAK - 转变回简单元素]
- 两个居中按钮

**输出：**
```javascript
{
  sectionNumber: 2,
  sequences: [
    {
      sequenceNumber: 1,
      description: "Single centered heading"
    },
    {
      sequenceNumber: 2,
      description: "Grid of 8 items, each with small icon and short text description"
    },
    {
      sequenceNumber: 3,
      description: "Two centered buttons"
    }
  ]
}
```

---

### 示例3：文章卡片区域

**输入：** "区域3（灰色背景）：博客文章"

**视觉观察：**
- 眉毛文本“最新文章”
- 大标题
- 段落描述
- 浏览按钮
[BREAK - 转变为重复模式]
- 网格中的4个项目
- 每个项目：图像、分类标签、标题、简短描述、阅读链接

**输出：**
```javascript
{
  sectionNumber: 3,
  sequences: [
    {
      sequenceNumber: 1,
      description: "Eyebrow text, large heading, paragraph description, browse button - all stacked vertically"
    },
    {
      sequenceNumber: 2,
      description: "Grid of 4 items, each with image, category tag, heading, description, and read link"
    }
  ]
}
```

---

### 示例4：简单内容区域

**输入：** "区域4（浅色背景）：正文内容"

**视觉观察：**
- 多个段落文本
- 文本中的内联图像
- 交错出现的标题（H2、H3）
- 没有明确的断点 - 内容自然流动

**输出：**
```javascript
{
  sectionNumber: 4,
  sequences: [
    {
      sequenceNumber: 1,
      description: "流动的散文内容：多个段落带有内联图像和标题（H2、H3）"
    }
  ]
}
```

**注意：** 由于内容自然流动而没有结构化断点，整个区域是一个序列。

---

## 应避免的常见错误

**在描述中使用区块名称：**
❌ "带有标题和按钮的英雄区块"
✓ "居中大型标题、段落、两个垂直堆叠的按钮"

**未识别断点：**
❌ 将整个区域描述为一个序列，尽管有明确的转变
✓ 识别内容类型何时改变并分解为序列

**过于细致：**
❌ 每个元素作为单独序列：“标题”、“段落”、“按钮”
✓ 相关元素组合在一起：“标题、段落、两个垂直堆叠的按钮”

**混合分析级别：**
❌ 同时分析多个区域
✓ 一次专注于一个区域（每次调用）

**做出作者决策：**
❌ “这应该是一个卡片区块，因为..."
✓ "带有图像和文本的4个项目网格"（中性描述）
