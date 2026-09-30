---
name: authoring-analysis
description: 在页面导入流程需要确定抓取内容的创作方式（默认内容与块）以生成 AEM Edge Delivery Services 的导入 HTML 之前，请使用此功能。涵盖验证导入/迁移的块选择和区域样式。不要直接调用——作为页面导入流程中的一个步骤被调用。
---

# 内容创作分析

确定每个内容序列的创作方式：默认内容还是特定模块。

## 使用此技能的场景

在以下情况下使用此技能：
- 您拥有页面结构，其中包含内容序列（来自identify-page-structure技能）
- 您拥有模块清单（本地 + Block Collection）
- 准备按照David的模型进行创作决策

**由以下技能触发：** page-import技能（第3步）

## 前置条件

从identify-page-structure技能中，您需要：
- ✅ 带有样式说明的段落边界
- ✅ 每个段落的（中性描述）内容序列
- ✅ 模块清单（本地 + 带有用途的Block Collection）
- ✅ screenshot.png用于视觉参考

## 相关技能

- **page-import** - 触发此技能的协调器
- **identify-page-structure** - 提供段落结构和模块清单
- **content-modeling** - 当模块选择不明确时，此技能会触发它
- **block-collection-and-party** - 此技能触发它以验证模块
- **generate-import-html** - 使用此技能的输出来创建HTML

## **重要提示：第3步e执行触发条件**

完成第3步（分析所有序列）后，如果满足以下条件，您**必须**执行第3步e：
- ✅ 至少有一个段落包含恰好一个序列，该序列变成了一个模块
- ✅ 该段落具有与identify-page-structure不同的背景样式

如果没有段落满足这些条件 → 跳过第3步e
如果有任何段落满足这些条件 → 为每个符合条件的段落执行第3步e

## 内容创作分析工作流

**背景：** 现在您拥有：
- 段落边界和样式
- 每个段落的（中性描述）内容序列
- 可用的模块调色板

**对于每个内容序列，请按照以下强制流程操作：**

---

### 第3步a：强制执行 - 默认内容检查（首先！）

**问题：** "作者能否在Word/Google Docs中正常输入来创建此内容？"

**默认内容意味着：**
- ✅ 标题、段落、列表
- ✅ 文本内的内联图片
- ✅ 简单引号
- ✅ 只是...输入内容

**不是默认内容意味着：**
- ❌ 重复结构化模式（卡片网格、功能列表）
- ❌ 交互式组件（手风琴、选项卡、轮播）
- ❌ 复杂布局（并排列、分割内容）
- ❌ 需要特定结构进行装饰

**决策：**
- 如果是（可以正常输入）→ **标记为默认内容，完成** ✅
- 如果不是（需要结构）→ **继续执行第3步b**

**示例：**
```
"居中大型标题、段落、两个按钮"
→ 作者能否正常输入标题、段落、链接？是
→ 决策：默认内容 ✅

"居中两个按钮"
→ 作者能否正常输入两个链接？是
→ 决策：默认内容 ✅

"网格中的四个项目，每个项目带有图片、标题、描述"
→ 作者能否正常输入？不是 - 需要网格结构
→ 决策：继续执行第3步b ➡️

"可展开的问题和答案"
→ 作者能否正常输入？不是 - 需要交互/装饰
→ 决策：继续执行第3步b ➡️
```

---

### 第3步b：模块选择（仅当不是默认内容时）

**在模块清单上下文中询问：** "作者会选择哪个可用模块来创建此内容？"

**决策树：何时触发content-modeling**

**明显匹配（不要触发content-modeling）：**

模式与模块用途1:1匹配：
- "带图片/文本的项目网格" + 看到"cards"模块 → 使用它 ✅
- "可展开的问题" + 看到"accordion"模块 → 使用它 ✅
- "选项卡内容面板" + 看到"tabs"模块 → 使用它 ✅
- "并排内容" + 看到"columns"模块 → 使用它 ✅
- "轮播图片" + 看到"carousel"模块 → 使用它 ✅

**明显匹配的标准：**
- 内容描述与模块用途完全匹配
- 结构没有歧义
- 模块存在于清单中

**不明确匹配（触发content-modeling）：**

不确定使用哪个模块：
- "三个带图片的项目" - 可以是cards？可以是columns？→ 触发
- "带图标的特性列表" - cards？自定义列表模块？→ 触发
- "带照片的客户引言" - 引言模块？cards？证言模块？→ 触发

清单中缺失：
- 内容需要结构，但没有匹配的模块 → 触发
- content-modeling可以推荐规范模型或建议创建自定义模块

复杂的创作考虑：
- "英雄式内容，但位于页面中间" → 触发
- "卡片式项目，但只有2个" → 触发
- 需要作者心智模型的验证 → 触发

**不明确匹配的标准：**
- 多个模块可能适用
- 没有明显的模块匹配
- 需要创作视角验证
- 可能需要创建自定义模块

---

### 第3步c：验证模块是否存在（如果需要）

**仅当模块不在Block Collection公共集中时：**

触发**block-collection-and-party**技能以：
- 确认模块存在
- 获取实时示例URL
- 审查内容模型

---

### 第3步d：获取模块HTML结构（生成HTML之前）

**关键：** 在下一个技能中生成任何HTML之前，获取所有将要使用的模块的预装饰HTML结构。

```bash
# 获取每个模块的结构示例
node .claude/skills/block-collection-and-party/scripts/get-block-structure.js cards
node .claude/skills/block-collection-and-party/scripts/get-block-structure.js tabs
node .claude/skills/block-collection-and-party/scripts/get-block-structure.js accordion
node .claude/skills/block-collection-and-party/scripts/get-block-structure.js columns
```

**为什么这可以防止错误：**
- 显示确切的行/列结构（例如，cards：每个卡片=1行，2列）
- 揭示所有变体（例如，“Cards” vs “Cards (no images)”）
- 显示干净的HTML，没有装饰
- 防止第1个HTML生成错误：结构错误

**使用输出来：**
1. 了解每行应有多少列
2. 看图片与内容的位置
3. 将您的内容与正确的变体匹配
4. 生成与预期结构完全匹配的HTML

---

### 第3步输出格式

**所有序列的完整分析：**

```
Section 1 (light):
  - Sequence 1: "Large centered heading, paragraph, two call-to-action buttons"
    → 决策：默认内容
    → 原因：作者可以正常输入标题、段落、链接
    → 备注：突出样式是CSS问题

  - Sequence 2: "Two images side-by-side"
    → 决策：columns模块（2列）
    → 原因：并排布局需要结构
    → 明显匹配，清单中有"columns"模块

Section 2 (light):
  - Sequence 1: "Centered heading"
    → 决策：默认内容
    → 原因：只是一个标题 - 作者输入它

  - Sequence 2: "Grid of 8 items, each with icon and short text"
    → 决策：cards模块
    → 原因：重复结构化模式，需要模块
    → 明显匹配，清单中有"cards"模块

  - Sequence 3: "Two centered buttons"
    → 决策：默认内容
    → 原因：只是两个链接 - 作者输入它们

Section 3 (grey):
  - Sequence 1: "Eyebrow text, heading, paragraph, button stacked vertically"
    → 决策：默认内容
    → 原因：作者正常输入文本和链接

  - Sequence 2: "Four items in grid, each with image, category tag, heading, description"
    → 决策：cards模块
    → 原因：重复结构化模式
    → 明显匹配，清单中有"cards"模块

Section 4 (dark):
  - Sequence 1: "Tab navigation with three switchable content panels"
    → 决策：tabs模块
    → 原因：交互式组件，需要装饰
    → 明显匹配，清单中有"tabs"模块
```

---

### 第3步e：验证段落样式（仅限单模块段落）

**⚠️ 执行触发条件：** 此步骤在完成第3步后执行。如果且仅当满足以下条件时执行此步骤：
- ✅ 您已完成第3步（识别了哪些序列变成了模块）
- ✅ 至少有一个段落包含恰好一个序列，该序列变成了一个模块
- ✅ 该段落具有与identify-page-structure不同的背景样式

**如果没有段落满足这些条件 → 完全跳过第3步e，并继续下一个技能**

**如果有任何段落满足这些条件 → 您必须为每个符合条件的段落执行以下所有子步骤**

---

**为什么此验证很重要：**

当一个段落包含单个模块时，背景样式可能是：
- **模块特定设计**（例如，带有深色背景图片的英雄）→ 不要添加section-metadata
- **段落容器样式**（例如，深色段落带有tabs模块）→ 添加section-metadata

如果没有验证，我们可能会添加不必要的section-metadata，这与模块样式冲突或使创作更复杂。

**包含多个序列的段落：** 始终保留section-metadata（样式适用于所有内容，第3步未验证）

---

**对于每个恰好包含一个模块的段落，执行所有这些子步骤：**

**子步骤1：识别候选段落**

查看您的第3步输出。找到以下条件的段落：
- 段落包含恰好1个内容序列
- 该序列变成了一个模块（不是默认内容）
- 段落具有与identify-page-structure不同的背景样式

**示例：**
```
Section 1 (dark blue):
  - Sequence 1: Large centered heading, paragraph, two buttons
    → 决策：Hero模块

Section 3 (grey):
  - Sequence 1: Tab navigation with three switchable panels
    → 决策：Tabs模块
```

---

**子步骤2：对于每个候选段落，检查screenshot.png**

打开screenshot.png并检查段落视觉上。

**问这些问题：**

**Q1：背景是图片（照片、渐变、插图）吗？**
- 如果是 → 可能是模块特定设计
- 如果不是（纯色）→ 继续问Q2

**Q2：内容是否填充了彩色区域边缘到边缘，或者有可见的段落填充？**
- 边缘到边缘（全出血）→ 可能是模块特定设计
- 内容周围有可见填充 → 可能是段落容器样式

**Q3：该模块类型通常具有自己的背景样式吗？**
- Hero、横幅、全宽CTAs → 通常有自己的背景
- Tabs、accordion、cards、columns → 通常使用段落背景

---

**子步骤3：做出决策**

根据您的分析，为每个单模块段落决定：

**跳过section-metadata如果：**
- 背景是图片/渐变（模块特定）
- 内容是全出血/边缘到边缘（没有可见段落填充）
- 模块类型通常具有内在背景（hero、banner）

**保留section-metadata如果：**
- 背景是纯色，有可见段落填充
- 模块类型通常继承段落样式（tabs、cards、accordion）
- 样式明显提供容器上下文（不是模块设计）

---

**子步骤4：记录您的决策**

对于每个验证的段落，记录：
- 段落编号
- 模块类型
- 背景分析（图片 vs 纯色，全出血 vs 填充）
- 决策（保留或跳过section-metadata）
- 原因

**示例输出：**
```
已验证段落：

Section 1 (dark blue):
  - 模块：Hero
  - 背景：全宽深蓝色渐变图片
  - 布局：边缘到边缘，没有可见段落填充
  - 决策：跳过section-metadata
  - 原因：背景是hero的设计，不是段落样式

Section 3 (grey):
  - 模块：Tabs
  - 背景：纯灰色（#f5f5f5）
  - 布局：内容居中，两侧有可见填充（约80px）
  - 决策：保留section-metadata style="grey"
  - 原因：段落为tabs模块提供容器样式
```

---

**不确定时：**

如果您不确定背景是模块特定还是段落范围：
- **默认保留section-metadata**（更安全，作者删除比添加更容易）
- **在您的文档中添加注释**解释模糊之处
- 考虑向用户寻求指导

---

**第3步e完成检查清单：**

在继续下一个技能之前，验证您已完成：
- ✅ 识别了所有单模块段落与背景样式
- ✅ 检查了每个候选段落的screenshot.png
- ✅ 对每个候选段落回答了Q1、Q2、Q3
- ✅ 为每个候选段落做出了跳过/保留决策
- ✅ 记录了每个决策的原因
- ✅ 更新了段落样式说明，包含验证决策
- ✅

---

## 最终输出

此技能提供完整的内容创作分析：

**1. 所有序列的创作决策：**
- 每个序列标记为DEFAULT CONTENT或特定模块名称
- 记录了原因

**2. 获取模块结构：**
- 所有将使用的模块的HTML结构示例

**3. 段落样式验证（如果适用）：**
- 更新段落列表，包含验证的样式决策
- 某些段落可能标记为"无section-metadata"

**下一步：** 将这些输出传递给generate-import-html技能
