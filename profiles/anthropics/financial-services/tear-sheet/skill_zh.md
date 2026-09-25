# 财务摘要生成器

通过 S&P Capital IQ 的 S&P Global MCP 工具获取实时数据，并格式化为专业的 Word 文档，生成针对不同受众的公司摘要。

## 样式配置

这些都是合理的默认值。要针对贵公司的品牌进行自定义，请修改此部分——常见的更改包括更换调色板、更改字体（Calibri 是许多银行的行业标准）以及更新免责声明文本。

**颜色：**
- 主要（页眉横幅背景、章节标题文本）：#1F3864
- 强调（签名部分高亮）：#2E75B6
- 表格标题行填充：#D6E4F0
- 表格交替行填充：#F2F2F2
- 表格边框：#CCCCCC
- 页眉横幅文本：#FFFFFF

**排版（docx-js 的半点大小）：**
- 字体：Arial
- 公司名称：18pt 加粗（大小：36）
- 章节标题：11pt 加粗（大小：22），主要颜色
- 正文：9pt（大小：18）
- 表格文本：8.5pt（大小：17）
- 页脚/免责声明：7pt 斜体（大小：14）
- 每个模板的覆盖设置在各自的参考文件的格式说明中指定。

**公司页眉横幅：**
- 页眉是一个跨越整个页面宽度的海军色 (#1F3864) 横幅，公司名称为白色。
- **横幅下方，键值对必须以跨越整个页面宽度的无边框两列表格形式呈现。** 左列：公司标识符（股票代码、总部、成立时间、员工人数、行业）。右列：财务标识符（市值、企业价值、股价、流通股数）。每个单元格包含加粗标签和常规权重值（例如，“**市值** $124.7B”）。不要将所有字段在单列中左对齐——这浪费水平空间并显得不专业。两列布局是区分专业摘要和默认文档的最重要视觉信号。
  - **实现：** 创建一个无边框和无边色的两列表格。将列宽设置为各占 50%。将左列字段（股票代码、总部、成立时间、员工人数）作为左单元格中的单独段落放置。将右列字段（市值、企业价值、股价、流通股数）放在右单元格中。每个字段是一个单独的段落：标签使用加粗运行，值使用常规运行。
  - 每列中的具体字段因受众而异——请参阅参考文件的页眉规范。原则始终是跨页面分布，而不是左簇拥。
- **不要使用带边框的表格来呈现页眉键值块。** 带边框的表格仅用于财务数据。
- 页眉中的关键指标（市值、企业价值、股价）应显示为内联键值对，而不是在单独的带边框的表格中。

**章节标题：**
- 每个章节标题下方都应有一条水平规则（细线，#CCCCCC，0.5pt），以在章节之间创建干净的视觉分隔。
- **将规则作为标题段落的底部边框呈现**——不要插入单独的段落元素。单独的段落会添加自己的前后间距，并在章节标题下方导致过多的空白。
- **实现：** 在 docx-js 中，通过 `paragraph.borders.bottom = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }` 将底部边框应用于章节标题段落。不要使用 `doc.addParagraph()` 与单独的水平规则元素。不要使用 `thematicBreak`。边框必须位于标题段落本身，且段落之后没有间距，以便规则紧贴标题文本。
- 间距：标题段落之前 12pt，标题段落之后 0pt，下一个内容元素之前 4pt。

**项目符号格式：**
- 对所有类型的摘要中的所有项目符号内容使用单个项目符号字符（•）。不要在或跨摘要中混合 •、-、▸ 或编号列表。
- **综合/分析项目符号**（盈利亮点、战略契合度、整合考虑、对话起点）：缩进块状格式，左缩进 360 DXA（0.25"），项目符号字符使用悬挂缩进。这些应与正文文本在视觉上有所区分——它们是解释性内容，应看起来与数据表格和段落不同。
- **关系部分中的信息性项目符号**：标准正文缩进（180 DXA），无悬挂缩进。
- **不要对任何项目符号部分应用左边界装饰。** 左边界样式在 docx-js 中渲染不一致，并会产生视觉伪影。使用缩进和文本大小区分签名部分。

**表格（仅限财务数据）：**
- 标题行：表格标题填充 (#D6E4F0) 与加粗深色文本
- 正文行：交替白色 / 表格交替填充 (#F2F2F2)
- 边框：表格边框颜色 (#CCCCCC)，细线（BorderStyle.SINGLE，大小 1）
- 单元格填充：顶部/底部 40 DXA，左/右 80 DXA
- 所有数字列右对齐
- 始终使用 ShadingType.CLEAR（永远不会 SOLID——SOLID 会导致黑色背景）

**布局：**
- 美国信纸横向，页边距 0.75"（所有边 1080 DXA）

**数字格式：**
- 货币：美元。如果公司收入 > $50B，则使用十亿（一位小数）。在列标题中标记单位（例如，“收入 ($M)”），而不是在单个单元格中。
- **表格单元格：纯数字，带逗号，不带美元符号。** 示例：收入单元格显示“4,916”，而不是“$4,916”。单位在列标题中。
- 财政年度：实际年份（FY2022、FY2023、FY2024），永远不会使用相对标签（FY-2、FY-1）。
- 负数：括号，例如，(2.3%)
- 百分比：一位小数
- 大数字：逗号作为千位分隔符

**页脚（文档页脚，不是内联）：**
在文档页脚（每页重复）中放置来源归因和免责声明，而不是作为底部的内联正文。页脚在每页上都是两行，居中，格式如下：
- 行 1：“数据：S&P Capital IQ via Kensho | 分析：AI 生成 | [月份 日期，年份]”
- 行 2：“仅供参考。不构成投资建议。”
- 样式：7pt 斜体，居中，#666666 文本颜色
- 此页脚文本必须对同一公司的所有摘要类型完全相同。不要根据受众更改措辞。
- **此页脚在每份摘要的每个页面上都是必需的。** 不要省略它。

## 组件功能

**你必须使用这些确切的功能来创建文档元素。** **不要**编写自定义的 docx-js 样式代码。将以下功能复制到生成的 Node.js 脚本中并调用它们。上面的样式配置说明仍然是文档；这些功能是执行机制。

```javascript
const docx = require("docx");
const {
  Document, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType,
  Header, Footer, PageNumber, HeadingLevel, TableLayoutType,
  convertInchesToTwip
} = docx;

// ── 颜色常量 ──
const COLORS = {
  PRIMARY: "1F3864",
  ACCENT: "2E75B6",
  TABLE_HEADER_FILL: "D6E4F0",
  TABLE_ALT_ROW: "F2F2F2",
  TABLE_BORDER: "CCCCCC",
  HEADER_TEXT: "FFFFFF",
  FOOTER_TEXT: "666666",
};

const FONT = "Arial";

// ── 1. createHeaderBanner ──
// 返回一个 docx 元素数组：[横幅段落，键值表]
function createHeaderBanner(companyName, leftFields, rightFields) {
  // leftFields / rightFields: { label: string, value: string } 数组
  const banner = new Paragraph({
    children: [
      new TextRun({
        text: companyName,
        bold: true,
        size: 36, // 18pt
        color: COLORS.HEADER_TEXT,
        font: FONT,
      }),
    ],
    shading: { type: ShadingType.CLEAR, color: "auto", fill: COLORS.PRIMARY },
    spacing: { after: 0 },
    alignment: AlignmentType.LEFT,
  });

  function buildCellParagraphs(fields) {
    return fields.map(
      (f) =>
        new Paragraph({
          children: [
            new TextRun({ text: f.label + "  ", bold: true, size: 18, font: FONT }),
            new TextRun({ text: f.value, size: 18, font: FONT }),
          ],
          spacing: { after: 40 },
        })
    );
  }

  const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
  const noShading = { type: ShadingType.CLEAR, color: "auto", fill: "FFFFFF" };

  const kvTable = new Table({
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: buildCellParagraphs(leftFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
          new TableCell({
            children: buildCellParagraphs(rightFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
        ],
      }),
    ],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });

  return [banner, kvTable];
}

// ── 2. createSectionHeader ──
// 返回一个 Paragraph，带有底部边框规则
function createSectionHeader(text) {
  return new Paragraph({
    children: [
      new TextRun({
        text: text,
        bold: true,
        size: 22, // 11pt
        color: COLORS.PRIMARY,
        font: FONT,
      }),
    ],
    spacing: { before: 240, after: 0 }, // 12pt before, 0pt after
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    },
  });
}

// ── 3. createTable ──
// headers: string[], rows: string[][], options: { accentHeader?, fontSize? }
function createTable(headers, rows, options = {}) {
  const fontSize = options.fontSize || 17; // 8.5pt 默认
  const headerFill = options.accentHeader ? COLORS.ACCENT : COLORS.TABLE_HEADER_FILL;
  const headerTextColor = options.accentHeader ? COLORS.HEADER_TEXT : "000000";

  const cellBorders = {
    top: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    left: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    right: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
  };

  const cellMargins = { top: 40, bottom: 40, left: 80, right: 80 };

  function isNumeric(val) {
    if (typeof val !== "string") return false;
    const cleaned = val.replace(/[,$%()]/g, "").trim();
    return cleaned !== "" && !isNaN(cleaned);
  }

  // 标题行
  const headerRow = new TableRow({
    children: headers.map(
      (h) =>
        new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: h,
                  bold: true,
                  size: fontSize,
                  color: headerTextColor,
                  font: FONT,
                }),
              ],
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: headerFill },
          borders: cellBorders,
          margins: cellMargins,
        })
    ),
  });

  // 数据行，交替填充
  const dataRows = rows.map((row, rowIdx) => {
    const fill = rowIdx % 2 === 1 ? COLORS.TABLE_ALT_ROW : "FFFFFF";
    return new TableRow({
      children: row.map((cell, colIdx) => {
        const align = colIdx > 0 && isNumeric(cell)
          ? AlignmentType.RIGHT
          : AlignmentType.LEFT;
        return new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: cell, size: fontSize, font: FONT }),
              ],
              alignment: align,
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: fill },
          borders: cellBorders,
          margins: cellMargins,
        });
      }),
    });
  });

  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}

// ── 4. createBulletList ──
// items: string[], style: "synthesis" | "informational"
function createBulletList(items, style = "synthesis") {
  const indent =
    style === "synthesis"
      ? { left: 360, hanging: 180 }   // 360 DXA left, 悬挂缩进用于项目符号
      : { left: 180 };                 // 180 DXA, 无悬挂缩进
  return items.map(
    (item) =>
      new Paragraph({
        children: [
          new TextRun({ text: "•  ", font: FONT, size: 18 }),
          new TextRun({ text: item, font: FONT, size: 18 }),
        ],
        indent: indent,
        spacing: { after: 60 },
      })
  );
}

// ── 5. createFooter ──
// date: string (e.g., "February 23, 2026")
function createFooter(date) {
  return new Footer({
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: `Data: S&P Capital IQ via Kensho | Analysis: AI-generated | ${date}`,
            italics: true,
            size: 14, // 7pt
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
      new Paragraph({
        children: [
          new TextRun({
            text: "For informational purposes only. Not investment advice.",
            italics: true,
            size: 14,
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
    ],
  });
}
```

**在生成的脚本中使用：**
1. 将上述所有函数和常量复制到生成的 Node.js 脚本中
2. 使用 `createHeaderBanner(...)` 而不是手动构建横幅段落和表格
3. 使用 `createSectionHeader(...)` 为每个章节标题——绝不要手动设置段落边框
4. 使用 `createTable(...)` 为**所有**表格数据——财务摘要、交易比较、并购活动、关系表格、融资历史等。传递 `{ accentHeader: true }` 用于并购活动表格（IB/M&A 模板）。对于非数字表格（例如，关系、所有权），该函数仍然可以正确工作——它仅对包含数字值的单元格进行右对齐。
5. 使用 `createBulletList(items, "synthesis")` 用于盈利亮点、战略契合度、整合考虑和对话起点
6. 使用 `createBulletList(items, "informational")` 用于关系条目
7. 将 `createFooter(date)` 传递给 Document 构造函数的 `footers.default` 属性

**这些函数消除的内容：**
- 黑色背景表格（强制 `ShadingType.CLEAR` 处处）
- 章节标题下方的单独水平规则段落（强制将边框应用于段落本身）
- 页眉中的带边框键值表（强制 `borders: none`）
- 不一致的项目符号样式（强制仅使用 • 字符）
- 缺少页脚（提供确切的页脚结构）

## 工作流程

### 第 1 步：确定输入

在进行下一步之前，收集最多四样东西：

1. **公司**——名称或股票代码。如果只有股票代码，请先进行初始查询以解析完整公司名称（例如，使用公司信息工具）。
2. **受众**——四种类型之一：
   - **股票研究**——用于买方/卖方分析师评估投资
   - **投行 / 并购**——用于银行在交易背景下对公司进行 profiling
   - **公司发展**——用于内部战略团队评估收购目标
   - **销售 / 商务发展**——用于商业团队为即将进行的客户会议做准备
3. **可比公司**（可选）——如果用户有特定的可比公司，请记录它们。否则，该技能将使用 S&P Global 数据识别同行。这对股票研究、投行/并购和公司发展摘要很重要。
4. **页面长度偏好**（可选）——默认值因受众而异（见下文），但用户可以覆盖。

如果用户未指定受众，请询问。

### 第 2 步：读取针对特定受众的参考文件

从该技能的目录中读取相应的参考文件：

- 股票研究 → `references/equity-research.md`
- 投行 / 并购 → `references/ib-ma.md`
- 公司发展 → `references/corp-dev.md`
- 销售 / 商务发展 → `references/sales-bd.md`

每个参考文件定义了章节、查询计划、格式指导以及页面长度默认值。

### 第 3 步：通过 S&P Global MCP 拉取数据

**首先：** 创建中间文件目录：
```bash
mkdir -p /tmp/tear-sheet/
```

使用 **S&P Global** MCP 工具（也称为 Kensho LLM-ready API）。Claude 将可以访问结构化工具以获取财务数据、公司信息、市场数据、共识估计、盈利记录、并购交易和业务关系。每个参考文件中的查询计划描述了每个章节应检索的数据——将这些映射到对话中可用的适当 S&P Global 工具。

**每次查询步骤后，立即将检索到的数据写入参考文件查询计划中指定的中间文件。** 不要延迟写入——写入磁盘的数据受长对话中上下文退化的保护。

**查询策略：**
每个参考文件都包含一个包含 4-6 个数据检索步骤的查询计划。这些是起点，不是严格的限制。优先考虑数据完整性而不是最小化调用：

- **始终拉取 4 个财政年度的财务数据**，即使只显示 3 年。第四年（最早年份）是计算第一年显示年份的年收入增长率所需的。没有它，最早年份的增长率将显示为“N/A”——这看起来像缺失数据，而不是设计选择。
- 执行查询计划，使用与所需数据匹配的 S&P Global 工具。
- 如果工具调用返回不完整的结果，尝试替代工具或更窄的查询。例如，如果公司摘要不包含细分详情，则直接尝试细分工具。
- 如果在目标重试后某个数据点未返回，请继续前进——标记为“N/A”或“未披露”。
- 从不编造数据。如果工具未返回一个数字，则不要从训练知识中填充空白——它可能过时或错误。

**用户指定的可比公司：** 如果用户提供了可比公司，请明确查询每个可比公司的财务数据和乘数。如果没有提供可比公司，则使用工具返回的任何同行数据，或使用竞争对手工具从公司的行业识别同行。

**用户提供的可选上下文：** 倾听用户自然提供的任何额外上下文。如果他们提到收购方（“我们正在评估这个平台”），他们销售的产品（“我们向银行销售数据分析服务”），或可能的买家（“Salesforce 或 Microsoft 会感兴趣”），请将这些上下文纳入相关的综合部分（战略契合度、整合考虑、对话起点、业务概述段落）。这些部分需要分析推理，将数据点串联成故事——没有上下文地列出公司名称不是综合分析。
- **私有公司处理：**
  CIQ 包括私有公司数据，因此查询方式相同。但是，预期结果较少。在为私有公司生成摘要时：
  - 跳过：股价、52 周区间、贝塔、股价表现、共识估计、交易可比
  - 侧重于：业务概述、关系、所有权结构，以及可用的财务数据
  - 突出显示“私有公司”在页眉中

### 第 3b 步：计算派生指标

在所有数据收集完成后，在单独的专用步骤中计算所有派生指标。这是一个计算步骤——不进行任何 MCP 查询。

**读取所有中间文件** 回到上下文中，然后计算：

- **利润率：** 毛利率 %、EBITDA 利润率 %、FCF 利润率 %、营业利润率 %
- **增长率：** 年收入增长率、细分收入增长率、每股收益增长率
- **效率比率：** FCF 转换（FCF/EBITDA）、研发占收入的百分比、资本支出占收入的百分比
- **资本结构：** 净债务（总债务减去现金及等价物）、净债务 / EBITDA
- **细分组合：** 每个细分收入占合并总收入（使用合并收入作为分母，符合数据完整性规则 8）的百分比

**验证（从算术验证移动到 Step 3b）：** 在此计算步骤中，强制执行所有算术检查：

- **利润率计算：** 验证 EBITDA 利润率 = EBITDA / 收入，毛利率 = 毛利润 / 收入等。如果计算出的利润率与原始数字不匹配，请使用从原始组件计算的结果。
- **增长率：** 验证 YoY 增长率 = (当前 - 先前) / 先前。不要依赖预计算的增长率，如果你有底层值。
- **细分总计：** 如果显示按细分收入，请验证细分总计与总收入（在舍入容差内）。如果它们不匹配，请省略总计行，而不是发布不一致的数学。
- **百分比列：** 验证 “% of Total” 列的总和约为 100%。
- **估值交叉检查：** 如果你显示 EV 和 EV/收入，请验证 EV / 收入 ≈ 声明的乘数

如果验证失败：尝试从原始数据中重新计算。如果仍然不一致，请将指标标记为“N/A”而不是发布不正确的数字。在摘要中静默的数学错误会破坏可信度。

**将结果** 写入 `/tmp/tear-sheet/calculations.csv`，列：`metric,value,formula,components`

示例行：
```
metric,value,formula,components
gross_margin_fy2024,72.4%,gross_profit/revenue,"9524/13159"
revenue_growth_fy2024,12.3%,(current-prior)/prior,"13159/11716"
net_debt_fy2024,2150,total_debt-cash,"4200-2050"
```

### 第 3c 步：验证中间文件

在生成文档之前，验证所有预期的中间文件是否存在并已填充。

**读取每个中间文件** 通过单独的读取操作，并打印验证摘要：

```
=== 摘要数据验证 ===
company-profile.txt: ✓ (12 个字段)
financials.csv:      ✓ (36 行)
segments.csv:        ✓ (8 行)
valuation.csv:       ✓ (5 行)
calculations.csv:    ✓ (18 行)
earnings.txt:        ✓ (已填充)
relationships.txt:   ⚠ 缺失
peer-comps.csv:      ✓ (12 行)
================
```

**软门禁：** 如果任何预期用于当前受众类型的文件缺失或为空，请打印警告但继续。摘要会优雅地处理缺失数据，并跳过部分。但是，警告确保了可见性，了解丢失了哪些数据。

**关键规则：文件——而不是你对你之前对话的记忆——是文档中每个数字的唯一来源。** 在生成 DOCX 的第 4 步中，从中间文件中读取值。不要依赖对话上下文中的财务数据。

### 第 4 步：格式化为 DOCX

读取 `/mnt/skills/public/docx/SKILL.md` 以获取 docx 创建机制（docx-js 通过 Node）。应用上面的样式配置，以及参考文件中的章节特定格式。

**页面长度默认值（用户可以覆盖）：**
- 股票研究：1 页（密度是惯例）
- 投行 / 并购：1-2 页
- 公司发展：1-2 页
- 销售 / 商务发展：1-2 页

如果内容超过目标长度，每个参考文件指定了默认页面长度和编号的剪切顺序。如果渲染的文档超过目标长度，则按指定的顺序应用剪切——不要尝试缩小字体大小或页边距低于模板最小值。剪切顺序是一个严格的优先级堆栈：在触摸第 1 个部分之前，不要触摸第 2 个部分。

**输出文件名：** `[CompanyName]_TearSheet_[Audience]_[YYYYMMDD].docx`
示例：`Nvidia_TearSheet_CorpDev_20260220.docx`

保存到 `/mnt/user-data/outputs/` 并呈现给用户。

## 数据完整性规则

11. **为每个受众重写每个叙述部分。** CIQ 公司摘要是一个输入，不是一个输出。每个受众类型都需要不同的描述：简洁且以论点为导向的股票研究，投行演示文稿文本，产品导向的公司发展，以及销售/商务发展的平实语言。永远不要将 CIQ 摘要原封不动地粘贴到任何摘要中。
12. **根据受众区分盈利亮点。** 同一个盈利电话会产生不同类型的见解。股票研究想要细分级别的表现和共识超预期/不及预期。投行想要利润率轨迹和战略评论。销售/商务发展想要能够创造对话起点的战略主题。不要在跨摘要类型中重复相同的要点。
13. **综合部分是区分的关键。** 战略契合度分析、整合考虑、对话起点和业务概述段落是摘要获得其价值的地方。这些部分需要分析推理，将数据点串联成故事——没有上下文地列出公司名称不是综合分析。
14. **在细分表格中标记待剥离的细分。** 如果一家公司宣布了剥离某个细分或业务单元的计划，请在细分表格中添加脚注或括号，注明待进行的交易（例如，“Mobility* — *预计 2026 年中期剥离”）。对于公司发展和投行/并购摘要，在细分表格下方添加一行，显示排除剥离细分后的预期收入和收入组合。这有助于读者评估“未来”业务，而无需他们自己做数学计算。

### 算术验证

**→ 算术验证现在在 Step 3b（计算派生指标）中强制执行。** 所有利润率计算、增长率、细分总计、百分比列和估值交叉检查都在专门的计算步骤中验证，在文档生成开始之前。请参阅 Step 3b 中的完整验证清单。
