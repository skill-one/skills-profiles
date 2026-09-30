---
name: tear-sheet
description: 通过Kensho LLM-ready API MCP服务器，使用S&P Capital IQ数据生成专业的公司传单。当用户要求获取公司传单、公司单页、公司简介、事实清单、公司快照或公司概览文件时，使用此技能——尤其是在用户提及特定公司名称或股票代码时。此外，当用户要求获取股票研究报告摘要、并购公司简介、企业发展战略目标简介、销售/BD会议准备文件或任何简洁的单公司财务摘要时，也会触发此技能。该技能支持四种受众类型：股票研究、投资银行/并购、企业发展和销售/业务发展。如果用户未指定受众类型，系统会询问。适用于上市公司和私营公司。
---

# 财务摘要生成器

通过从 S&P Capital IQ 经 S&P Global MCP 工具获取实时数据，并格式化为专业的 Word 文档，生成针对不同受众的公司摘要。

## 样式配置

这些都是合理的默认值。要针对贵公司的品牌进行自定义，请修改此部分——常见的更改包括更换调色板、更改字体（许多银行的标准字体是 Calibri）以及更新免责声明文本。

**颜色：**
- 主要（页眉横幅背景、章节标题文本）：#1F3864
- 强调（签名部分高亮）：#2E75B6
- 表格标题行填充：#D6E4F0
- 表格交替行填充：#F2F2F2
- 表格边框：#CCCCCC
- 页眉横幅文本：#FFFFFF

**排版（docx-js 使用的半点大小）：**
- 字体：Arial
- 公司名称：18pt 加粗（大小：36）
- 章节标题：11pt 加粗（大小：22），主要颜色
- 正文：9pt（大小：18）
- 表格文本：8.5pt（大小：17）
- 页脚/免责声明：7pt 斜体（大小：14）
- 每个模板的覆盖设置在每个参考文件的格式说明中指定。

**公司页眉横幅：**
- 页眉是一个跨越整个页面宽度的海军色 (#1F3864) 横幅，公司名称为白色。
- **横幅下方，键值对必须以跨越整个页面宽度的无边框两列表格形式呈现。** 左列：公司标识符（股票代码、总部、成立时间、员工人数、行业）。右列：财务标识符（市值、企业价值、股价、流通股数）。每个单元格包含加粗标签和常规加粗值在同一行上（例如，“**市值** $124.7B”）。不要将所有字段左对齐在一个列中——这浪费水平空间，看起来不专业。两列布局是区分专业摘要和默认文档的最重要视觉信号。
  - **实现：** 创建一个两列表格，`borders: none` 和 `shading: none` 在所有单元格上。将列宽设置为各占 50%。将左列字段（股票代码、总部、成立时间、员工人数）作为左单元格中的单独段落放置。将右列字段（市值、企业价值、股价、流通股数）放在右单元格中。每个字段是一个单独的段落：加粗运行用于标签，常规运行用于值。
  - 每列中的具体字段因受众而异——请参阅参考文件的页眉规范。原则始终是：跨越整个页面，而不是左对齐。
- **不要使用带边框的表格来呈现页眉键值块。** 带边框的表格仅用于财务数据。
- 页眉中的关键指标（市值、企业价值、股价）应显示为内联键值对，而不是在单独的带边框的表格中。

**章节标题：**
- 每个章节标题下方都应有一条水平规则（细线，#CCCCCC，0.5pt），以在章节之间创建干净的视觉分隔。
- **将规则作为标题段落的底部边框呈现**——不要插入单独的段落元素。单独的段落会添加自己的前后间距，导致章节标题下方出现过多的空白。
- **实现：** 在 docx-js 中，通过 `paragraph.borders.bottom = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }` 将底部边框应用于章节标题段落。不要使用 `doc.addParagraph()` 与单独的水平规则元素。不要使用 `thematicBreak`。边框必须在标题段落本身上，且后间距为 0pt，以便规则紧贴标题文本。
- 间距：标题段落前 12pt，标题段落后 0pt，下一个内容元素前 4pt。

**项目符号格式：**
- 在所有类型的摘要中，使用单个项目符号字符（•）进行所有项目符号内容。不要在或跨摘要中混合 •、-、▸ 或编号列表。
- **综合/分析项目符号**（盈利亮点、战略契合度、整合考虑、对话起点）：缩进块式格式，左缩进 360 DXA（0.25"），项目符号字符使用悬挂缩进。这些应与正文文本在视觉上偏移——它们是解释性内容，应与数据表格和段落文本区分开来。
- **关系部分中的信息性项目符号**：标准正文缩进（180 DXA），无悬挂缩进。
- **不要对任何项目符号部分应用左边框装饰。** 左边框样式在 docx-js 中渲染不一致，并会创建视觉伪影。使用缩进和文本大小差异来区分签名部分。

**表格（仅限财务数据）：**
- 标题行：表格标题填充 (#D6E4F0) 与加粗深色文本
- 正文行：交替白色 / 表格交替填充 (#F2F2F2)
- 边框：表格边框颜色 (#CCCCCC)，细线（BorderStyle.SINGLE，大小 1）
- 单元格填充：顶部/底部 40 DXA，左/右 80 DXA
- 所有数字列右对齐
- 始终使用 ShadingType.CLEAR（永远不会 SOLID——SOLID 会导致黑色背景）

**布局：**
- 美国信纸纵向，页边距 0.75"（所有边 1080 DXA）

**数字格式：**
- 货币：美元。如果公司收入 > $50B，则使用十亿（一位小数），否则使用百万，并在列标题中标注单位（例如，“收入 ($M)”），而不是在单个单元格中。
- **表格单元格：纯数字，带逗号，不带美元符号。** 示例：收入单元格显示“4,916”，而不是“$4,916”。列标题包含单位。
- 财政年度：实际年份（FY2022、FY2023、FY2024），永远不使用相对标签（FY-2、FY-1）。
- 负数：括号，例如 (2.3%)
- 百分比：一位小数
- 大数字：逗号作为千位分隔符

**页脚（文档页脚，非内联）：**
将来源归因和免责声明放在实际文档页脚（每页重复），而不是作为底部内联正文。页脚在每页上都是两行，居中，文本颜色 #666666：
- 行 1：“数据：S&P Capital IQ via Kensho | 分析：AI 生成 | [月份 日期，年份]”
- 行 2：“仅供参考。不构成投资建议。”
- 样式：7pt 斜体，居中，文本颜色 #666666
- 此页脚文本必须对所有类型的公司摘要保持一致。不要根据受众更改措辞。
- **此页脚必须在每个摘要、每种受众类型、每页上。** 不要省略它。

## 组件功能

**你必须使用这些确切的函数来创建文档元素。** **不要编写自定义的 docx-js 样式代码。** 将这些函数复制到生成的 Node.js 脚本中并调用它们。上面的样式配置说明仍然是文档；这些函数是执行机制。

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
// 返回一个 Paragraph 带底部边框规则
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
    spacing: { before: 240, after: 0 }, // 12pt 前，0pt 后
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

  // 数据行带交替填充
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
      ? { left: 360, hanging: 180 }   // 360 DXA 左，悬挂缩进用于项目符号
      : { left: 180 };                 // 180 DXA，无悬挂

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
// date: string (例如，"February 23, 2026")
function createFooter(date) {
  return new Footer({
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: `数据：S&P Capital IQ via Kensho | 分析：AI 生成 | ${date}`,
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
            text: "仅供参考。不构成投资建议。",
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

**在生成脚本中的使用：**
1. 将上面的所有函数和常量复制到生成的 Node.js 脚本中
2. 调用 `createHeaderBanner(...)` 而不是手动构建横幅段落和表格
3. 调用 `createSectionHeader(...)` 用于每个章节标题——永远不要手动设置段落边框
4. 调用 `createTable(...)` 用于**所有**表格数据——财务摘要、交易比较、并购活动、关系表、融资历史等。传递 `{ accentHeader: true }` 用于并购活动表格（IB/M&A 模板）。对于非数字表格（例如，关系、所有权），该函数仍然可以正确工作——它仅将包含数字值的单元格右对齐。
5. 调用 `createBulletList(items, "synthesis")` 用于盈利亮点、战略契合度、整合考虑和对话起点
6. 调用 `createBulletList(items, "informational")` 用于关系条目
7. 将 `createFooter(date)` 传递给 Document 构造函数的 `footers.default` 属性

**这些函数消除的内容：**
- 黑色背景表格（强制 `ShadingType.CLEAR` 处处使用）
- 章节标题下方的单独水平规则段落（强制 `border.bottom` 在段落本身上）
- 页眉中的带边框键值表（强制 `borders: none`）
- 不一致的项目符号样式（强制使用 `•` 字符）
- 缺少页脚（提供确切的页脚结构）

## 工作流程

### 第 1 步：确定输入

在进行下一步之前，收集最多四样东西：

1. **公司**——名称或股票代码。如果只有股票代码，则使用初始查询解决完整公司名称（例如，使用公司信息工具）。
2. **受众**——四种类型之一：
   - **股权研究**——用于买方/卖方分析师评估投资
   - **投行 / 并购**——用于银行在交易背景下对公司进行介绍
   - **公司发展**——用于内部战略团队评估收购目标
   - **销售 / 业务发展**——用于商业团队准备客户会议
3. **可比公司**（可选）——如果用户有特定的比较公司，请记录。否则，该技能将从 S&P Global 数据中识别同行。这对于股权研究、投行 / 并购和公司发展摘要很重要。
4. **页面长度偏好**（可选）——默认值因受众而异（见下文），但用户可以覆盖。

如果用户没有指定受众，请询问。

### 第 2 步：读取受众特定参考

从该技能的目录中读取相应的参考文件：

- 股权研究 → `references/equity-research.md`
- 投行 / 并购 → `references/ib-ma.md`
- 公司发展 → `references/corp-dev.md`
- 销售 / 业务发展 → `references/sales-bd.md`

每个参考文件定义了章节、查询计划、格式指南和页面长度默认值。

### 第 3 步：通过 S&P Global MCP 拉取数据

**首先：** 创建中间文件目录：
```bash
mkdir -p /tmp/tear-sheet/
```

使用 **S&P Global** MCP 工具（也称为 Kensho LLM-ready API）。Claude 将可以访问用于金融数据、公司信息、市场数据、一致预期、盈利记录、并购交易和业务关系的结构化工具。每个参考文件中的查询计划描述了要为每个部分检索哪些数据——将这些映射到对话中可用的适当 S&P Global 工具。

**在每次查询步骤后，立即将检索到的数据写入参考文件查询计划中指定的中间文件。** 不要延迟写入——写入磁盘的数据可以防止在长对话中上下文退化。

**查询策略：**
每个参考文件包含一个包含 4-6 个数据检索步骤的查询计划。这些是起点，不是严格的约束。优先考虑数据完整性而不是最小化调用：

- **始终拉取 4 个财政年度的财务数据**，即使只显示 3 年。第四年（最早）是计算第一年显示年份的年增长率所必需的。没有它，最早年份的增长率将显示为“N/A”——这看起来像是缺失数据，而不是设计选择。
- 按照编写的方式执行查询计划，使用匹配所需数据的 S&P Global 工具。
- 如果工具调用返回不完整的结果，请尝试替代工具或更窄的查询。例如，如果公司摘要不包括细分详情，请直接使用细分工具。
- 如果在目标重试后未返回数据点，请继续前进——将其标记为“N/A”或“未披露”。
- 永远不要编造数据。如果工具未返回数字，请不要根据训练知识进行估算。

**用户指定的可比公司：** 如果用户提供了可比公司，请明确查询每个可比公司的财务数据和乘数。如果未提供可比公司，请使用工具返回的任何同行数据，或使用竞争对手工具从公司的行业识别同行。

**用户提供的可选上下文：** 聆听用户自然提供的任何附加上下文。如果他们提到收购方（“我们正在为我们的平台查看这个”），他们销售的产品（“我们向银行销售数据分析”），或可能的买家（“这会对 Salesforce 或 Microsoft 感兴趣”），请将此上下文纳入相关的综合部分（战略契合度、对话起点、交易角度）。不要提示此信息——如果提供，请使用它。

**私营公司处理：**
CIQ 包括私营公司数据，因此查询方式相同。但是，请预期结果较少。为私营公司生成数据时：
- 跳过：股票价格、52 周区间、贝塔系数、股票表现、一致预期、交易可比公司
- 侧重：业务概述、关系、所有权结构、可用的任何财务数据
- 在标题中突出显示“私营公司”

### 第 3 步 b：计算派生指标

在所有数据收集完成并将中间文件写入后，在单个专用传递中计算所有派生指标。这是一个仅计算步骤——不进行新的 MCP 查询。

**将所有中间文件重新读入上下文**，然后计算：

- **利润率：** 毛利率%、EBITDA 利润率%、FCF 利润率%、营业利润率%
- **增长率：** 同比收入增长率、同比细分收入增长率、同比 EPS 增长率
- **效率比率：** FCF 转化率（FCF/EBITDA）、研发占收入的百分比、资本支出占收入的百分比
- **资本结构：** 净债务（总债务 - 现金及等价物）、净债务 / EBITDA
- **细分组合：** 每个细分的收入占合并总收入百分比（根据数据完整性规则 8，使用合并收入作为分母）

**验证（从算术验证移动）：** 在此计算传递期间，执行所有算术检查：

- **利润率计算：** 验证 EBITDA 利润率 = EBITDA / 收入，毛利率 = 毛利润 / 收入，等等。如果计算出的利润率与原始数字不匹配，请使用从原始组件计算的结果。
- **增长率：** 验证同比增长率 = (当前 - 以前) / 以前。如果具有底层值，则不要依赖预计算的增长率。
- **细分总计：** 如果按细分显示收入，请验证细分总计等于总收入（在舍入容差范围内）。如果它们不匹配，请省略总计行，而不是发布不一致的数学。
- **百分比列：** 验证“占总计的百分比”列总和约为 100%。
- **估值交叉检查：** 如果您同时显示 EV 和 EV/收入，请验证 EV / 收入 ≈ 声明的乘数。

如果验证失败：尝试从原始数据重新计算。如果仍然不一致，请将指标标记为“N/A”，而不是发布不正确的数字。在拆页中静默的数学错误会破坏可信度。

**将结果**写入 `/tmp/tear-sheet/calculations.csv`，列：`metric,value,formula,components`

示例行：
```
metric,value,formula,components
gross_margin_fy2024,72.4%,gross_profit/revenue,"9524/13159"
revenue_growth_fy2024,12.3%,(current-prior)/prior,"13159/11716"
net_debt_fy2024,2150,total_debt-cash,"4200-2050"
```

### 第 3 步 c：验证数据文件

在生成文档之前，验证所有中间文件是否存在且已填充。

**通过单独的读取操作读取每个中间文件**并打印验证摘要：

```
=== 拆页数据验证 ===
company-profile.txt: ✓ (12 个字段)
financials.csv:      ✓ (36 行)
segments.csv:        ✓ (8 行)
valuation.csv:       ✓ (5 行)
calculations.csv:    ✓ (18 行)
earnings.txt:        ✓ (已填充)
relationships.txt:   ⚠ 缺失
peer-comps.csv:      ✓ (12 行)
=====================
```

**软门：** 如果任何当前受众类型预期的文件缺失或为空，请打印警告但继续。拆页可以优雅地处理缺失数据并跳过部分。但是，警告确保可以了解丢失了哪些数据。

**关键规则：文件——而不是您对先前对话的记忆——是文档中每个数字的单一来源。** 在第 4 步生成 DOCX 时，请从中间文件读取值。不要依赖对话上下文来获取财务数据。

### 第 4 步：格式化为 DOCX

读取 `/mnt/skills/public/docx/SKILL.md` 以获取 DOCX 创建机制（docx-js 通过 Node）。应用上述样式配置以及参考文件中的部分特定格式。

**页面长度默认值（用户可以覆盖）：**
- 股票研究：1 页（密度是惯例）
- IB / 并购：1-2 页
- 企业发展：1-2 页
- 销售 / BD：1-2 页

如果内容超过目标，每个参考文件指定要首先裁剪哪些部分。

**输出文件名：** `[CompanyName]_TearSheet_[Audience]_[YYYYMMDD].docx`
示例：`Nvidia_TearSheet_CorpDev_20260220.docx`

保存到 `/mnt/user-data/outputs/` 并向用户展示。

## 数据完整性规则

这些优先于所有其他规则：
1. **S&P Global 工具是财务数据的唯一来源。** 不要用训练知识填充空白——它可能过时或错误。
2. **标记您找不到的内容。** 使用“N/A”或“未披露”而不是无声地省略一行。
3. **日期很重要。** 注明财政年度末或报告期间。不要假设日历年度 = 财政年度。市场数据（股票价格、市值）应包括“截至”日期。
4. **不要混合报告期间。** 如果您有 FY2023 收入和 LTM EBITDA，请明确标记它们。
5. **优先使用 MCP 返回的字段而不是手动计算。** 如果 S&P Global 工具返回预计算字段（例如，净债务、EBITDA、FCF），请直接使用该值，而不是从组件计算。只有在工具未返回字段时，才手动计算派生指标。这减少了差异。
6. **确保拆页类型之间的一致性。** 如果在同一会话中为同一公司生成多个拆页（例如，股票研究和 IB/M&A），相同的底层数据点必须在所有输出中产生相同的值。净债务、收入、EBITDA、利润率和增长率必须完全匹配。不要独立于每个报告重新查询或重新计算——重用相同的检索值。
7. **永远不要降低已知的交易价值。** 如果 M&A 工具返回交易的交易价值，该价值必须出现在输出中。不要用“未披露”替换已知的交易价值。只有在工具确实未为交易返回值时，才使用“未披露”。
8. **使用合并收入作为细分百分比的分母。** 在计算细分表的“占总计的百分比”时，请将每个细分的收入除以合并总收入（在损益表上报告），而不是细分收入的总和。细分总和通常由于内部消除而超过合并收入。使用合并收入可确保百分比与文档中其他地方显示的总收入数字一致。
9. **始终包含前瞻性（NTM）乘数（当可用时）。** 如果工具返回 trailing 和 forward 估值乘数，两者都必须出现在输出中。前瞻性乘数是股票研究、IB/M&A 和企业发展受众的主要估值参考。当有 forward 数据时，永远不要只显示 trailing 乘数。
10. **没有 S&P Global 工具返回高管或管理层数据。** 不要从训练数据中填充管理层姓名、头衔或传记细节——这违反了规则 1，并会产生过时的信息。如果模板中显示管理层部分，请完全省略它。只有当工具返回时，才可能包括所有权结构（机构持有人、内部人士百分比、PE 赞助商）——以“数据允许”为门。

## 中间文件规则

从 MCP 工具检索的所有数据都必须在文档生成之前持久化到结构化的中间文件中。这些文件——而不是对话上下文——是文档中每个数字的单一来源。

**设置：** 在第 3 步开始时创建工作目录：
```
mkdir -p /tmp/tear-sheet/
```

**写入查询后命令：** 在每个 MCP 查询步骤完成后，立即将检索到的数据写入适当的中间文件。不要等到所有查询完成。每个参考文件的查询计划指定了在每个步骤后要写入哪个文件。

**文件架构：**

| 文件 | 格式 | 列 / 结构 | 使用 |
|---|---|---|---|
| `/tmp/tear-sheet/company-profile.txt` | 文本键值 | name, ticker, exchange, HQ, sector, industry, founded, employees, market_cap, enterprise_value, stock_price, 52wk_high, 52wk_low, shares_outstanding, beta, ownership | 所有 |
| `/tmp/tear-sheet/financials.csv` | CSV | `period,line_item,value,source` | 所有 |
| `/tmp/tear-sheet/segments.csv` | CSV | `period,segment_name,revenue,source` | ER, IB, CD |
| `/tmp/tear-sheet/valuation.csv` | CSV | `metric,trailing,forward,source` | ER, IB, CD |
| `/tmp/tear-sheet/consensus.csv` | CSV | `metric,fy_year,value,source` | ER |
| `/tmp/tear-sheet/earnings.txt` | 结构化文本 | Quarter, date, key quotes, guidance, key drivers | ER, IB, Sales |
| `/tmp/tear-sheet/relationships.txt` | 结构化文本 | Customers, suppliers, partners, competitors — 每个都有描述符 | IB, CD, Sales |
| `/tmp/tear-sheet/peer-comps.csv` | CSV | `ticker,metric,value,source` | ER, IB, CD |
| `/tmp/tear-sheet/ma-activity.csv` | CSV | `date,target,deal_value,type,rationale,source` | IB, CD |
| `/tmp/tear-sheet/calculations.csv` | CSV | `metric,value,formula,components` | 所有（在第 3 步 b 中写入） |

**缩写：** ER = 股票研究，IB = IB/并购，CD = 企业发展，Sales = 销售/BD。

并非每个受众类型都使用每个文件——参考文件定义了哪些查询步骤适用。与当前受众类型不相关的文件无需创建。

**仅原始值。** 中间文件存储工具返回的原始值。不要在这些文件中预先计算利润率、增长率或其他派生指标——那发生在第 3 步 b。

**页面预算执行：** 每个参考文件指定默认页面长度和编号的裁剪顺序。如果渲染的文档超过目标，请按指定顺序应用裁剪——不要尝试将字体大小或边距缩小到模板最小值以下。裁剪顺序是一个严格的优先级堆栈：在触摸第 2 部分之前，完全裁剪第 1 部分。

## 内容质量规则

11. **为受众重写每个叙述部分。** CIQ 公司摘要是一个输入，不是一个输出。每种受众类型都需要不同的描述：简洁且以论点为导向的股票研究，用于 IB 的演示文稿文本，用于企业发展的产品导向，用于销售/BD 的平实语言。永远不要将 CIQ 摘要逐字粘贴到任何拆页中。
12. **根据受众区分盈利亮点。** 同一个盈利电话为不同的读者产生不同的见解。股票研究想要细分级别的表现和一致预期的高低。IB 想要利润率轨迹和战略评论。销售/BD 想要创造对话角度的战略主题。不要在拆页类型之间重复相同的要点。
13. **综合部分是区分点。** 战略契合度分析、整合考虑、对话起点和业务概述段落是拆页获得其价值的地方。这些部分需要分析推理，将数据点连接成一个故事——没有上下文地列出公司名称不是综合。
14. **在细分表中标记待处理的剥离。** 如果公司宣布了待处理的细分或业务单位的剥离，请在细分表中添加脚注或括号，注明待处理的交易（例如，“Mobility* — *待剥离，预计 2026 年中期”）。对于企业发展和 IB/并购拆页，请在细分表下方添加一行笔记，显示排除剥离细分后的预测收入和收入组合。这有助于读者评估“向前”业务，而无需他们自己做数学。

### 算术验证

**→ 算术验证现在在第 3 步 b（计算派生指标）中执行。** 所有利润率计算、增长率、细分总计、百分比列和估值交叉检查都在专用的计算传递期间执行，在文档生成开始之前。有关完整的验证清单，请参阅第 3 步 b。
