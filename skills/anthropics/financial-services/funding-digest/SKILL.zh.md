---
name: funding-digest
description: 生成一份精炼的单页PPT幻灯片，总结用户关注领域或公司近期融资轮次和资本市场活动的关键要点。当用户要求获取交易流摘要、每周回顾、融资摘要、交易汇总或资本市场简报时，使用此技能。触发条件包括："交易流摘要"、"每周融资回顾"、"交易汇总"、"本周交易总结"、"本周[领域]发生了什么"、"资本市场更新"，或任何要求将近期融资活动汇总成简报幻灯片的请求。生成一份专业的单页PPTX文件，包含关键要点、估值数据以及Capital IQ交易链接。
---

**AI免责声明（强制）：**
您必须在PowerPoint页脚中包含以下免责声明文本。这不是可选的——没有它，报告是不完整的：

> **“分析由AI生成——请确认所有输出”**

**页脚**——在生成的幻灯片底部，作为一个显眼的黄色横幅：“分析由AI生成——请确认所有输出”

---

# 每周交易流摘要

生成一个分析师质量的**单张幻灯片PowerPoint**，总结近期在关注的行业或公司中融资轮的关键要点，使用S&P Global Capital IQ数据。每个交易都链接到其Capital IQ资料，以便快速深入分析。

## 使用场景

在以下任何模式触发：
- “给我本周的交易流摘要”
- “[行业]每周融资回顾”
- “[行业/公司]最近有哪些交易？”
- “交易汇总”或“交易流汇总”
- “我的覆盖范围内的资本市场更新”
- “总结近期融资活动”
- 任何关于交易、融资或融资轮的定期简报请求

## 嵌套技能

此技能生成一个单张PPTX简报：
- **阅读** `/mnt/skills/public/pptx/SKILL.md` 在生成PowerPoint之前（及其子参考 `pptxgenjs.md` 用于从零开始创建）

## 实体解析与工具健壮性

S&P Global的标识符系统将公司名称解析为法律实体。这对于大多数公司都效果很好，但存在已知的故障模式，会导致空结果。**在整个工作流程中应用这些规则，以避免静默数据丢失。**

### 规则0：在查询融资之前预先验证所有标识符

**在**调用任何融资工具之前，通过 `get_info_from_identifiers` 运行每个标识符。这是最早发现问题最经济、最可靠的方法。在响应中检查两件事：

1. **它是否解析了？** 如果标识符返回空/错误，则该名称不存在于S&P Global。尝试从 `references/sector-seeds.md` 中的别名、法律实体名称或直接使用 `company_id`。
2. **`status` 字段是什么？**
   - `"Operating"` → 可以安全地查询融资轮。
   - `"Operating Subsidiary"` → 该公司存在，但由母公司拥有。它将返回**零融资轮**。在摘要中注明此信息（例如，“被 [母公司] 收购”），但不要查询融资。
   - 任何其他状态（例如，已关闭、非活跃）→ 该公司不再运营。可能存在历史数据，但没有新活动。

**这一单个预验证步骤可防止大多数空结果问题。** 将所有候选者批量到单个 `get_info_from_identifiers` 调用中（它处理大批量效果很好），并在继续之前进行分诊。

### 规则1：在没有回退的情况下永远不要信任空结果

如果 `get_rounds_of_funding_from_identifiers` 对于您预期有数据的公司返回空：
1. **尝试法律实体名称或公司_id。** 品牌名称通常有效，但有些无效。查看 `references/sector-seeds.md` 中的别名表以了解已知不匹配。常见模式："[品牌] AI" → "[法律名称], Inc."（例如，Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."）。
2. **验证该公司是否存在于S&P。** 如果您跳过了规则0，现在调用 `get_info_from_identifiers(identifiers=["Company"])`——如果这也返回空，该公司可能太早期或尚未索引。

### 规则2：子公司没有融资轮

作为较大公司部门或全资子公司的公司（例如，DeepMind在Alphabet下，GitHub在Microsoft下，BeReal在Voodoo下）将返回**零融资轮**。它们的资本事件在母公司层面进行跟踪。

**如何检测：** 来自 `get_info_from_identifiers` 的 `status` 字段将显示 `"Operating Subsidiary"`。`references/sector-seeds.md` 文件也用 ⚠️ 警告标记了已知的子公司。跳过这些融资查询。

### 规则3：使用 `get_rounds_of_funding_from_identifiers` 作为主要工具，而不是 `get_funding_summary_from_identifiers`

摘要工具更快，但不太可靠——即使存在详细的轮次，它也可能返回错误或不完整的数据。始终使用详细的轮次工具作为主要数据源。摘要工具仅在快速汇总检查（总融资额、轮次数量）时才可接受，如果结果似乎较低，应将其与轮次工具进行验证。

### 规则4：小心批量处理并验证

在处理大型公司宇宙（50多家公司）时，批量处理15-20家公司。每次批量处理后，检查返回空结果的公司，并在继续之前通过规则1中的回退步骤运行它们。

### 规则5：`role` 参数至关重要

- `company_raising_funds` → “X公司融资了哪些轮？”（公司角度）
- `company_investing_in_round_of_funding` → “投资者Y投资了什么？”（投资者角度）

使用错误的角色将静默返回空结果。对于交易流摘要，您几乎总是需要 `company_raising_funds`。仅在分析投资者的投资组合活动时才使用投资者角色。

### 规则6：标识符解析不区分大小写，但区分拼写

S&P Global处理大小写变化（"openai" = "OpenAI"），但对拼写和标点符号很严格。"Character AI" 可能失败，而 "Character.ai" 可能成功。不确定时，使用 `company_id`（例如，`C_1829047235`），它保证可以解析。

## 工作流程

### 第1步：确定覆盖范围和时间段

确定摘要应涵盖的内容。有两种设置：

**返回用户（有监控列表）：**
如果用户之前定义了要跟踪的行业或公司，请使用该列表。检查对话历史记录以获取先前的监控列表。

**新用户：**
询问：

| 参数 | 默认值 | 备注 |
|------|--------|------|
| **行业** | *(至少一个)* | 例如，“AI、金融科技、生物技术” |
| **特定公司** | 可选 | 补充行业级覆盖 |
| **时间段** | 最后7天 | “本周”、“过去2周”、“本月” |

根据时间段计算确切的 `start_date` 和 `end_date`。

### 第2步：构建公司宇宙

针对每个指定的行业，使用经过验证的引导方法构建公司宇宙：

1. **从领域知识中获取种子公司**（参见 `references/sector-seeds.md`）
   - 注意种子文件中的 ⚠️ 警告和别名说明——一些知名公司是子公司、已被收购或需要特定的法律名称才能解析。
   - 种子文件包括已知别名不匹配的 `company_id` 值。如果品牌名称失败，请直接使用这些值。

2. **立即对所有种子进行预验证**（规则0）：
   ```
   get_info_from_identifiers(identifiers=[本行业所有种子])
   ```
   将结果分诊到两个桶中：
   - ✅ **已解析且运营** (`status` = "Operating") → 继续进行竞争对手扩展
   - ❌ **未解析或子公司** → 尝试从种子文件中获取别名/法律名称；子公司仅用于上下文说明，但排除融资查询

3. **通过竞争对手扩展**（仅使用 ✅ 解析的种子）：
   ```
   get_competitors_from_identifiers(identifiers=[resolved_seeds], competitor_source="all")
   ```

4. **验证扩展宇宙：**
   ```
   get_info_from_identifiers(identifiers=[new_competitors])
   ```
   应用相同的分诊。按 `simple_industry` 匹配目标行业进行过滤。删除任何未解析的名称或子公司。

如果用户提供特定公司，请直接添加，但仍然通过规则1中的预验证分诊运行。永远不要跳过验证——即使知名品牌也可能静默失败。

保持宇宙可控——每个行业目标为15-40 **已解析、运营** 的公司。对于多行业摘要，这可能总计为50-100+家公司。

### 第3步：提取融资轮

针对宇宙中的所有公司：

```
get_rounds_of_funding_from_identifiers(
    identifiers=[batch],
    role="company_raising_funds",
    start_date="YYYY-MM-DD",
    end_date="YYYY-MM-DD"
)
```

如果宇宙较大，则分批处理15-20家公司。

**每次批量处理后，识别空结果的公司。** 对于预期有活动的任何公司：
1. 尝试法律实体名称或备用标识符（见实体解析规则）。
2. 仅在穷尽回退后，将公司记录为“无数据”。

收集所有 `transaction_id` 值，然后使用详细信息丰富轮次：

```
get_rounds_of_funding_info_from_transaction_ids(
    transaction_ids=[all_funding_ids]
)
```

将所有交易ID一次性（或少量调用）传递，而不是每个交易一个——该工具高效处理批量。

**从每个轮次中提取以下信息（对幻灯片至关重要）：**
- `transaction_id` — 需要Capital IQ交易链接
- **公告日期** — 融资轮何时公开宣布
- **关闭日期** — 融资轮何时正式关闭
- 融资金额
- **预融资估值**（如果披露）
- **后融资估值**（如果披露）
- 主要投资者
- 轮次类型（A轮、B轮、C轮等）
- 证券条款
- 顾问
- 定价趋势（上涨轮/下跌轮/持平）

> **日期是必需的。** 公告和关闭日期必须始终出现在最终幻灯片的交易表中。如果只有一个日期可用，请显示它，并将另一个标记为“—”。

### 第4步：为重大交易提取公司背景

对于参与重大交易（大额轮次、显著估值变化）的任何公司，获取简要描述：

```
get_company_summary_from_identifiers(identifiers=[notable_companies])
```

这为叙述添加了背景（例如，“该公司是一家成立于2021年的AI基础设施初创公司，正在扩展……”）。

### 第5步：识别亮点和趋势

在设计幻灯片之前，分析数据以揭示故事：

**标记为“重大”：**
- 超过$10亿美元的轮次
- 下跌轮次（定价趋势=下跌）
- 新独角兽（后融资估值超过$10亿）
- 显著的估值跳跃（后融资估值≥上次已知估值的2倍）
- 重复融资者（同一公司在6个月内再次融资）
- 异常大的投资者联盟

**识别趋势：**
- 本期部署的总资本与典型值相比（如果可用历史数据）
- 哪些子行业最热（最多轮次、最多资本）
- 轮次阶段分布（早期阶段还是后期阶段占主导地位？）
- 摘要中最活跃的投资者
- 地理集中度
- 估值趋势（预融资估值是收缩还是扩张？）

**选择关键要点（3-5）：**
将最重要的信号提炼为3-5条简洁的要点式要点。这些是幻灯片的核心。每个要点应为一句话，简洁有力，有数据支持。

示例：
- “AI行业在8轮中筹集了$2.4B——是上一周的3倍，由[公司]以$12B的后融资估值进行的$8亿美元超级轮领导。”
- “[公司]以$3.5B的预融资估值完成了$2亿美元的D轮，高于其C轮的$1.8B——表明对AI开发者工具的需求强劲。”
- “下跌轮次活动有所上升：6次后期轮次中有2次定价低于先前估值。”

### 第6步：生成公司标志

对于在关键要点或重大交易中出现的每个公司，使用两级本地管道生成标志。**不要使用Clearbit** (`logo.clearbit.com`)——它已弃用且始终失败。外部标志CDN（Brandfetch、logo.dev、Google Favicons）需要API密钥或被网络限制阻止。相反，请使用以下方法：

#### 级别1：`simple-icons` npm包（3,300多个品牌SVG，无需网络）

`simple-icons` 包捆绑了数千个知名品牌的SVG图标。它完全离线工作——无需API密钥，无需网络调用。安装它以与 `sharp` 一起进行SVG→PNG转换：

```bash
npm install simple-icons sharp
```

**查找策略：**

```javascript
const si = require('simple-icons');
const sharp = require('sharp');

// 通过精确标题匹配查找图标（不区分大小写）
function findSimpleIcon(companyName) {
    // 首先尝试精确匹配
    for (const [key, val] of Object.entries(si)) {
        if (!key.startsWith('si') || !val || !val.title) continue;
        if (val.title.toLowerCase() === companyName.toLowerCase()) return val;
    }
    // 尝试去除常见后缀（AI、Inc.？、Corp.？、Ltd.？）
    const stripped = companyName.replace(/\s*(AI|Inc\.?|Corp\.?|Ltd\.?)$/i, '').trim();
    if (stripped !== companyName) {
        for (const [key, val] of Object.entries(si)) {
            if (!key.startsWith('si') || !val || !val.title) continue;
            if (val.title.toLowerCase() === stripped.toLowerCase()) return val;
        }
    }
    return null;
}

// 将SVG转换为带品牌官方颜色的PNG
async function simpleIconToPng(icon, outputPath) {
    const coloredSvg = icon.svg.replace('<svg', `<svg fill="#${icon.hex}"`);
    await sharp(Buffer.from(coloredSvg))
        .resize(128, 128, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
        .png()
        .toFile(outputPath);
}
```

**覆盖率：** 典型交易流公司中约43%（对于主要科技品牌如Stripe、Anthropic、Databricks、Snowflake、Discord、Shopify、SpaceX、Mistral AI、Hugging Face效果良好；对于利基金融科技、生物技术或早期阶段公司较弱）。

#### 级别2：基于初始的回退通过 `sharp`

对于在 `simple-icons` 中找不到的公司，生成一个干净的初始基于标志作为PNG：

```javascript
async function generateInitialLogo(companyName, outputPath) {
    const initial = companyName.charAt(0).toUpperCase();
    const svg = `
    <svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
        <circle cx="64" cy="64" r="64" fill="#BDBDBD"/>
        <text x="64" y="64" font-family="Arial, Helvetica, sans-serif"
              font-size="56" font-weight="bold" fill="#FFFFFF"
              text-anchor="middle" dominant-baseline="central">${initial}</text>
    </svg>`;
    await sharp(Buffer.from(svg)).png().toFile(outputPath);
}
```

#### 完整管道

```javascript
async function fetchLogo(companyName, outputDir) {
    const fileName = companyName.toLowerCase().replace(/[\s.]+/g, '-') + '.png';
    const outPath = path.join(outputDir, fileName);

    // 级别1：尝试simple-icons
    const icon = findSimpleIcon(companyName);
    if (icon) {
        await simpleIconToPng(icon, outPath);
        return { path: outPath, source: 'simple-icons' };
    }

    // 级别2：生成基于初始的回退
    await generateInitialLogo(companyName, outPath);
    return { path: outPath, source: 'initial-fallback' };
}
```

**标志指南：**
- 将所有标志保存到 `/home/claude/logos/[company-name].png`
- 所有标志都是128×128 PNG，带透明背景
- 在幻灯片中以0.35"-0.5"高显示标志——它们是点缀，不是焦点
- 初始回退圆圈使用灰色（`BDBDBD`）填充和白色文本——与单色调调色板一致
- 永远不要随机混合标志样式——如果大多数公司解析为品牌图标，则少数回退应自然融入

### 第7步：生成单页PPTX

阅读 `/mnt/skills/public/pptx/SKILL.md` 和 `/mnt/skills/public/pptx/pptxgenjs.md` 在创建幻灯片之前。

使用 `pptxgenjs` 创建**单张幻灯片**PowerPoint。幻灯片应信息密集但视觉干净——想想“执行仪表板”，而不是“文字墙”。

#### 幻灯片布局

```
┌─────────────────────────────────────────────────────────────┐
│  交易流程摘要                                           │
│  [期间] · [行业]                           [日期]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  $X.XB  │  │  N      │  │  $X.XB  │  │  $X.XB  │       │
│  │  筹集    │  │  轮次    │  │  平均预 │  │  最大    │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  关键要点                                              │
│  ─────────────────────────────────────────────────          │
│  [Logo] 要点 1 文本放在这里...                        │
│  [Logo] 要点 2 文本放在这里...                        │
│  [Logo] 要点 3 文本放在这里...                        │
│  [Logo] 要点 4 文本放在这里...                        │
│                                                             │
│  主要交易                                                  │
│  ┌──────────────────────────────────────────────────────────┐│
│  │公司│类型 │宣布│关闭│金额│预-$│后-$│领投│🔗││
│  │────│─────│─────│────│────│─────│────│────│──││
│  │ ... │ ... │  ...│ ...│ ...│ ... │ ...│... │🔗││
│  └──────────────────────────────────────────────────────────┘│
│                                                             │
│  [页脚：交易流程摘要 · 来源：S&P Global Capital IQ]│
│  [页脚：AI免责声明]                                    │
└─────────────────────────────────────────────────────────────┘
```

#### 设计规范

**色彩理念：极简，首选单色。** 幻灯片应像高端金融简报一样——黑色、白色和灰色主导。仅在以下情况下使用颜色：它传达意义（例如，用于降轮的红色指示器，用于突出显示指标的绿色指示器）或读者自然会期望它（公司标志）。绝不要出于纯装饰目的使用颜色，如背景填充、强调条或渐变效果。

**色彩面板——单色高管：**
- 主要背景：`FFFFFF`（白色）—— 干净、开阔的幻灯片背景
- 标题栏：`1A1A1A`（近黑色）—— 标题区域的强对比度
- 主要文本：`1A1A1A`（近黑色）—— 所有正文、统计数据、要点
- 次要文本：`6B6B6B`（中灰色）—— 标签、说明、页脚、日期戳
- 边框和分隔符：`D0D0D0`（浅灰色）—— 微妙的结构线、卡片轮廓、表格边框
- 卡片背景：`F5F5F5`（浅白色/非常浅的灰色）—— 统计卡片填充、交替表格行
- 链接文本：`2B5797`（柔和的蓝色）—— Capital IQ 交易链接（幻灯片上唯一的蓝色）
- **语义颜色（有节制地）：**
  - 降轮或负面信号：`C0392B`（柔和的红色）—— 仅用作小点、标签或单个词突出显示，绝不能用作填充或背景
  - 突出显示的积极指标（新独角兽、超额轮次）：`2E7D32`（柔和的绿色）—— 同样的最小化使用：点、小标签或单个突出显示的数字
  - 如果没有数据点值得颜色指示，**则根本不使用颜色**。完全单色的幻灯片是完全正确的。

**字体：**
- 标题：28–32pt，粗体，白色在近黑色标题栏上
- 统计数字：36–44pt，粗体，近黑色
- 统计标签：10–12pt，中灰色 (`6B6B6B`)
- 要点文本：12–14pt，近黑色，左对齐
- 表格文本：9–11pt，近黑色，次要列使用灰色 (`6B6B6B`)
- 链接文本：9–10pt，柔和的蓝色 (`2B5797`)
- 页脚：8pt，中灰色

**统计卡片（顶行）：**
- 4个关键指标作为大数字调用：总筹集资金、轮次数量、平均预资金估值、最大轮次
- 每个指标在一个卡片中，`F5F5F5` 填充和细 `D0D0D0` 边框——无阴影，无颜色填充
- 如果指标令人惊讶或极端（例如，3倍正常量，记录交易），可以在该单个数字旁边放置一个小颜色点或下划线——否则保持完全单色
- 如果预资金估值大多未披露，用其他指标替代（例如，中位数轮次规模、新独角兽数量）

**关键要点（中间部分）：**
- 3–5行要点，每行前缀相关公司标志（小，~0.35"高）
- 如果没有标志可用，使用**灰色圆圈**，白色公司首字母——不是彩色圆圈
- 左对齐，留有足够的间距
- 降轮或负面要点可能使用红色小点前缀；否则无颜色
- 在可能的情况下包含估值背景（例如，“在50亿美元的投后估值下”）

**主要交易表格（底部部分）：**
- 紧凑表格显示4–6个最显著交易
- 列：公司、类型（轮次X）、宣布（日期）、关闭（日期）、金额（$M）、预资金（$M）、投后（$M）、领投机构、交易链接
- **宣布**和**关闭**列显示 `MMM DD` 格式的日期（例如，“Jan 15”）。这些列是必需的，必须始终存在。如果日期不可用，显示“—”。
- **交易链接**列包含指向 Capital IQ 的可点击“查看→”文本：
  ```
  https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=<transaction_id>
  ```
  其中 `<transaction_id>` 是 `get_rounds_of_funding_from_identifiers` 中的 `transaction_id`。
- 如果预资金或投后估值未披露，在该单元格显示“—”
- 头行使用近黑色 (`1A1A1A`) 填充和白色文本；交替行在 `F5F5F5` 和 `FFFFFF`
- **水平居中表格**在幻灯片上。计算表格的总宽度，然后设置 `x` 使其在幻灯片宽度内居中：`x = (slideWidth - tableWidth) / 2`。对于16:9布局（13.33"宽），如果表格是12"宽，使用 `x = 0.67`。永远不要将表格左对齐到幻灯片边缘。
- 保持紧凑——这是一个参考，不是焦点
- 表格单元格中无颜色填充。如果交易是降轮，金额旁边可能会出现一个小红色文本标签“(↓降)”——那是表格中唯一允许的颜色。

**交易链接实现（pptxgenjs）：**
在 pptxgenjs 中，使用单元格对象的 `options.hyperlink` 属性将超链接添加到表格单元格：
```javascript
// 表格单元格带有 Capital IQ 交易链接
{
  text: "查看→",
  options: {
    hyperlink: {
      url: `https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=${transactionId}`
    },
    color: "2B5797",
    fontSize: 9,
    fontFace: "Arial"
  }
}
```

**表格居中（pptxgenjs）：**
始终将交易表格居中。动态计算 `x` 位置：
```javascript
const SLIDE_W = 13.33; // 16:9 幻灯片宽度（英寸）
const TABLE_W = 12.5;  // 表格总宽度（所有列宽之和）
const TABLE_X = (SLIDE_W - TABLE_W) / 2; // ≈ 0.42"

slide.addTable(tableRows, {
  x: TABLE_X,
  y: tableY,
  w: TABLE_W,
  colW: [1.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.2, 1.6, 0.7], // 公司、类型、宣布、关闭、金额、预-$、投后、领投、链接
  // ... 其他选项
});
```
根据需要调整 `colW` 值，但始终重新计算 `TABLE_X` 从 `(SLIDE_W - sum(colW)) / 2` 以保持表格居中。

**页脚：**
- 小号文本，中灰色：“交易流程摘要 · [期间] · 来源：S&P Global Capital IQ · 生成 [日期]”

**一般颜色规则（严格执行）：**
- 公司标志是幻灯片上唯一的“全色”元素——它们按源文件原样显示。
- 交易链接使用柔和的蓝色 (`2B5797`)——这是幻灯片上唯一的非单色文本颜色，除了语义红/绿。
- 除了标志和链接外，幻灯片应能在黑白打印机上正确打印。
- 绝不要将颜色应用于背景、强调条、装饰形状或部分分隔符。
- 疑虑时，留灰。

#### 代码结构

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "交易流程摘要";

const slide = pres.addSlide();
const SLIDE_W = 13.33; // 16:9 幻灯片宽度（英寸）

// 1. 深色标题栏，带有标题和期间
// 2. 统计卡片行（4张卡片：总筹集资金、轮次数量、平均预资金、最大轮次）
// 3. 关键要点部分，带有标志（包括估值背景）
// 4. 主要交易表格，带有宣布、关闭、预资金、投后列和 Capital IQ 交易链接
//    - 居中表格：x = (SLIDE_W - tableWidth) / 2
// 5. 页脚

pres.writeFile({ fileName: "/home/claude/交易流程摘要.pptx" });
```

使用工厂函数（而不是共享对象），根据 pptxgenjs 潜在问题指南为阴影和重复样式设置样式。

### 第 8 步：验证幻灯片

遵循 PPTX 技能的验证过程：

1. **内容验证：** `python -m markitdown 交易流程摘要.pptx` — 验证所有文本、数字、公司名称、估值数字和交易链接是否正确
2. **视觉验证：** 转换为图像并检查：
   ```bash
   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf 交易流程摘要.pptx
   pdftoppm -jpeg -r 200 交易流程摘要.pdf slide
   ```
   检查重叠元素、文本溢出、对齐问题、低对比度文本、标志尺寸问题，以及交易链接文本是否可见。
3. **链接验证：** 验证表格中的 Capital IQ URL 是否正确格式化并包含正确的交易 ID。
4. **修复并重新验证** — 至少一个修复和验证循环，完成前完成。

### 第 9 步：展示结果

1. 将最终 `.pptx` 复制到 `/mnt/user-data/outputs/`
2. 使用 `present_files` 共享幻灯片
3. 提供一个 2–3 句话的口头总结：
   - “您的摘要涵盖了 X 轮，总计筹集资金 $Y，涉及 [行业]。”
   - 调用最显著交易及其估值
   - 标记任何令人担忧的趋势（降轮、估值压缩等）

## 错误处理

### 实体解析失败
- **已知公司为空结果：** 首先检查 `get_info_from_identifiers` — 如果失败，尝试 `references/sector-seeds.md` 中的别名或 `company_id` 直接。常见的品牌→法律不匹配：Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."。
- **子公司公司：** DeepMind、GitHub、Instagram、WhatsApp、YouTube、BeReal、等都是子公司——它们没有独立的融资轮次。在上下文中标记为“收购/子公司”，但不要报告为“无活动。”
- **已注销公司：** 像Convoy（2023年10月关闭）这样的公司仍会在 S&P Global 中解析，但永远不会有新活动。检查 `references/sector-seeds.md` 文件以确认是否包含公司。
- **`get_funding_summary_from_identifiers` 错误或返回零：** 回退到 `get_rounds_of_funding_from_identifiers` — 摘要工具不太可靠。永远不要将摘要工具作为唯一数据源依赖。
- **错误的 `role` 参数：** 如果投资者视角查询返回为空，请验证您使用的是 `company_investing_in_round_of_funding`，而不是 `company_raising_funds`（反之亦然）。

### 数据质量问题
- **期间内无活动：** 如果一个行业在期间内没有融资轮次，请在幻灯片上明确注明（“在 [行业] 期间未记录交易”）——缺乏活动本身就是信息。
- **估值数据稀疏：** 如果大多数交易未披露预资金和投后估值，请在页脚注释中注明数据限制，并在表格中使用“—”。调整统计卡片以显示其他指标（例如，中位数轮次规模）而不是平均预资金。
- **标志检索失败：** `simple-icons` npm 包对典型交易流公司的覆盖率约为 43%。对于其余部分，使用 `sharp` 生成的基于首字母的备用方案。保持一致的图标样式——不要混合随机方法。如果 `simple-icons` 或 `sharp` 安装失败，回退到 pptxgenjs 形状首字母（灰色椭圆+白色文本叠加），这不需要外部依赖。
- **一张幻灯片上的交易过多：** 如果有 6 个以上显著交易，请在表格中显示前 6 个，并添加脚注：“+N 个其他交易未显示。” 优先考虑交易规模。
- **大型宇宙：** 对于包含 100 多家公司的多行业摘要，将所有 API 调用分组为 15–20 组。优先考虑显著交易的深度，而不是对次要交易的完整性。
- **陈旧的种子：** 如果竞争对手扩展返回非常少的行业结果，种子公司可能过于狭窄。通过添加 2–3 个知名名称来扩展，并重新扩展。
- **无效的交易 ID：** 如果来自融资工具的交易 ID 不会产生有效的 Capital IQ URL，请省略该行的链接单元格，而不是包含损坏的链接。

## 示例提示

- “给我一份 AI 和金融科技每周交易流摘要”
- “总结本周生物技术的融资”
- “我的覆盖范围交易摘要——网络安全、云基础设施和开发工具——过去两周”
- “本周所有行业我关注的创业投资发生了什么？”
- “本月气候技术快速交易流幻灯片”
