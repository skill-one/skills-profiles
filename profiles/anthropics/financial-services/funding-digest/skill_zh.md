**AI 免责声明（强制）：**
您必须在 PPT 页脚中包含以下免责声明文本。这不是可选的——没有它，报告就不完整：

> **"分析内容由 AI 生成——请确认所有输出"**

**页脚** — 在生成的幻灯片底部，以醒目的黄色横幅显示："分析内容由 AI 生成——请确认所有输出"

---

# 每周交易流量摘要

使用 S&P Global Capital IQ 数据，生成一份**单页 PPT**，汇总所关注领域或公司近期融资轮次的关键要点。每笔交易均可链接到其 Capital IQ 档案，便于快速深入查看。

## 适用场景

匹配以下任何模式时触发：
- "给我一份本周的交易流量摘要"
- "[领域]的每周融资回顾"
- "[领域/公司]最近有哪些交易落地？"
- "交易汇总"或"融资汇总"
- "我覆盖范围内的资本市场动态"
- "总结近期融资动态"
- 任何关于交易、融资或轮次的定期简报请求

## 嵌套技能

此技能生成单页 PPTX 简报：
- **读取** `/mnt/skills/public/pptx/SKILL.md`（生成 PPT 之前），及其子引用文件 `pptxgenjs.md`（从零创建）

## 实体解析与工具健壮性

S&P Global 的标识符系统将公司名称解析为法律实体。这对大多数公司有效，但存在已知的失败模式，会导致空结果。**在工作流中全程应用以下规则，以避免静默数据丢失。**

### 规则 0：在查询融资之前预验证所有标识符

**在**调用任何融资工具之前，将每个标识符通过 `get_info_from_identifiers` 进行验证。这是最早、最可靠地发现问题方式。检查响应中的两项内容：

1. **是否成功解析？** 如果标识符返回空/错误，说明该名称在 S&P Global 中不存在。尝试 `references/sector-seeds.md` 中的别名、法律实体名称，或直接使用 `company_id`。
2. **`status` 字段是什么？**
   - `"Operating"` → 可以安全地查询融资轮次。
   - `"Operating Subsidiary"` → 公司存在但受母公司所有。它将返回**零条融资记录**。在摘要中作为背景注明（例如"已被 [母公司] 收购"），但不要查询其融资。
   - 其他任何状态（如已关闭、非活跃）→ 公司不再运营。可能仍有历史数据，但无新动态。

**这一步预验证可避免绝大多数的空结果问题。** 将所有候选标识符合并到一次 `get_info_from_identifiers` 调用中（该工具能很好地处理大批量），然后再进行后续处理。

### 规则 1：不要在没有回退方案的情况下信任空结果

如果 `get_rounds_of_funding_from_identifiers` 返回您预期有数据的公司的空结果：
1. **尝试法律实体名称或 company_id。** 品牌名称通常有效，但有些不行。参见 `references/sector-seeds.md` 中的别名表以了解已知不匹配。常见模式："[品牌] AI" → "[法律名称], Inc."（例如 Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."）。
2. **确认该公司在 S&P 中存在。** 如果跳过了规则 0，现在调用 `get_info_from_identifiers(identifiers=["Company"])` — 如果这也返回空，该公司可能过于早期或尚未被索引。

### 规则 2：子公司没有融资轮次

作为更大公司的部门或全资子公司（例如 DeepMind 隶属于 Alphabet、GitHub 隶属于 Microsoft、BeReal 隶属于 Voodoo）将返回**零条融资记录**。其资本事件在母公司层面追踪。

**如何检测：** `get_info_from_identifiers` 返回的 `status` 字段会显示 `"Operating Subsidiary"`。`references/sector-seeds.md` 文件也用 ⚠️ 标记了已知的子公司。对这些公司跳过融资查询。

### 规则 3：使用 `get_rounds_of_funding_from_identifiers` 作为主要工具，而非 `get_funding_summary_from_identifiers`

摘要工具更快但可靠性较低——即使存在详细轮次数据，它也可能返回错误或不完全的数据。始终使用详细轮次工具作为主要数据源。摘要工具仅适用于快速汇总检查（总融资额、轮次数），如果结果偏低应与轮次工具交叉验证。

### 规则 4：小心批量处理并验证

处理大型公司库（50+ 家公司）时，每批 15–20 家。每批完成后，检查返回空结果的公司，并在继续之前对它们执行规则 1 中的回退步骤。

### 规则 5：`role` 参数至关重要

- `company_raising_funding` → "X 公司进行了哪些融资？"（公司视角）
- `company_investing_in_round_of_funding` → "投资人 Y 投资了什么？"（投资人视角）

使用错误的 role 会静默返回空结果。对于交易流量摘要，几乎总是需要 `company_raising_funding`。仅在专门分析某投资人的投资组合动态时才使用投资人视角。

### 规则 6：标识符解析不区分大小写但区分拼写

S&P Global 处理大小写变体（"openai" = "OpenAI"），但对拼写和标点很严格。"Character AI" 可能失败而 "Character.ai" 成功。不确定时，使用 `company_id`（例如 `C_1829047235`），它保证可解析。

## 工作流

### 步骤 1：确定覆盖范围与时间周期

确定摘要应覆盖的内容。有两种设置：

**回访用户（有关注列表）：**
如果用户之前已定义了要追踪的领域或公司，使用该列表。检查对话历史中是否有过往的关注列表。

**新用户：**
询问：

| 参数 | 默认值 | 备注 |
|-----------|---------|-------|
| **领域** | *（至少一个）* | 例如 "AI、金融科技、生物科技" |
| **具体公司** | 可选 | 补充领域级别的覆盖 |
| **时间周期** | 最近 7 天 | "本周"、"最近两周"、"本月" |

根据时间周期计算精确的 `start_date` 和 `end_date`。

### 步骤 2：构建公司库

对每个指定领域，使用经验证的引导方法构建公司库：

1. **种子公司**来自领域知识（参见 `references/sector-seeds.md`）
   - 注意种子文件中的 ⚠️ 警告和别名备注 — 一些知名公司是子公司、已被收购，或需要特定的法律名称才能解析。
   - 种子文件包含已知别名不匹配的 `company_id` 值。如果品牌名称失败，直接使用这些。

2. **立即预验证所有种子**（规则 0）：
   ```
   get_info_from_identifiers(identifiers=[all_seeds_for_this_sector])
   ```
   将结果分为两类：
   - ✅ **已解析且运营中**（`status` = "Operating"）→ 进入竞争对手扩展
   - ❌ **未解析或为子公司** → 使用种子文件中的别名/法律名称重试；子公司作为背景注明但排除在融资查询之外

3. **通过竞争对手扩展**（仅使用 ✅ 已解析的种子）：
   ```
   get_competitors_from_identifiers(identifiers=[resolved_seeds], competitor_source="all")
   ```

4. **验证扩展后的公司库：**
   ```
   get_info_from_identifiers(identifiers=[new_competitors])
   ```
   应用相同的分类。按 `simple_industry` 是否匹配目标领域进行过滤。丢弃未解析的名称或子公司。

如果用户提供了具体公司，直接添加但仍需通过预验证分类。切勿跳过验证 — 即使是知名品牌名称也可能静默失败。

保持公司库可控 — 每个领域目标 15–40 家**已解析、运营中**的公司。多领域摘要总计可能为 50–100+ 家。

### 步骤 3：获取融资轮次

对公司库中所有公司：

```
get_rounds_of_funding_from_identifiers(
    identifiers=[batch],
    role="company_raising_funding",
    start_date="YYYY-MM-DD",
    end_date="YYYY-MM-DD"
)
```

如果公司库较大，每批处理 15–20 家。

**每批完成后，识别返回空结果的公司。** 对于预期有动态的公司：
1. 使用法律实体名称或备用标识符重试（参见上述实体解析规则）。
2. 只有在穷尽所有回退方案后，才将该公司标记为"无数据"。

收集所有成功结果中的 `transaction_id` 值，然后获取详细轮次信息：

```
get_rounds_of_funding_info_from_transaction_ids(
    transaction_ids=[all_funding_ids]
)
```

将所有交易 ID 放在一次调用中（或少数几次调用），而非每笔交易一次 — 该工具能高效处理批量。

**从每个轮次中提取以下内容（对幻灯片至关重要）：**
- `transaction_id` — Capital IQ 交易链接所需
- **公告日期** — 轮次对外公告的时间
- **交割日期** — 轮次正式完成的时间
- 融资金额
- **投前估值**（如已披露）
- **投后估值**（如已披露）
- 领投投资人
- 轮次类型（A 轮、B 轮、C 轮等）
- 证券条款
- 顾问
- 定价趋势（溢价 / 折价 / 持平）

> **日期为必填项。** 公告日期和交割日期必须始终出现在最终幻灯片的交易表中。如果只有一个日期可用，显示它并将另一个标记为"—"。

### 步骤 4：获取重要交易的公司的背景信息

对于涉及重要交易的公司（大额轮次、估值显著变化），获取简要描述：

```
get_company_summary_from_identifiers(identifiers=[notable_companies])
```

这为叙述增添了背景（例如"该公司是一家 2021 年成立的 AI 基础设施初创企业，正在扩展至……"）。

### 步骤 5：识别亮点与趋势

在设计幻灯片之前，分析数据以提炼故事线：

**标记为"重要"：**
- 金额 ≥ 1 亿美元的轮次
- 折价轮次（定价趋势 = 折价）
- 新晋独角兽（投后估值突破 10 亿美元）
- 估值显著跃升（投后估值 ≥ 上次已知估值的 2 倍）
- 重复融资者（同一公司在 6 个月内再次融资）
- 异常大的投资人辛迪加

**识别趋势：**
- 本周期总部署资本 vs. 正常水平（如有历史数据）
- 哪些子领域最热门（轮次最多、资本最多）
- 轮次阶段分布（早期还是后期占主导？）
- 整个摘要中最活跃的投资人
- 地域集中度
- 估值趋势（投前估值在压缩还是扩张？）

**选择关键要点（3–5 条）：**
将最重要的信号提炼为 3–5 条简洁的要点式摘要。这些是幻灯片的核心。每条要点应为一句话，有力且基于数据。

示例：
- "AI 领域共完成 8 轮融资，总额 24 亿美元 — 是上周的 3 倍，由 [公司] 以 120 亿美元投后估值的 8 亿美元超级轮次领衔。"
- "[公司] 以 35 亿美元投前估值完成 2 亿美元 D 轮融资，较 C 轮的 18 亿美元大幅上调 — 表明 AI 开发者工具需求强劲。"
- "折价轮次活动增加：6 个后期轮次中有 2 个定价低于前次估值。"

### 步骤 6：生成公司 Logo

对每个出现在关键要点或重要交易中的公司，使用两级本地管道生成 logo。**不要使用 Clearbit**（`logo.clearbit.com`）— 它已弃用且持续失败。外部 logo CDN（Brandfetch、logo.dev、Google Favicons）需要 API 密钥或受网络限制阻断。改用以下方法：

#### 第一级：`simple-icons` npm 包（3,300+ 品牌 SVG，无需网络）

`simple-icons` 包内置了数千个知名品牌的高质量 SVG 图标。它完全离线工作 — 无需 API 密钥，无需网络调用。安装时搭配 `sharp` 用于 SVG → PNG 转换：

```bash
npm install simple-icons sharp
```

**查找策略：**

```javascript
const si = require('simple-icons');
const sharp = require('sharp');

// 按精确标题匹配查找图标（不区分大小写）
function findSimpleIcon(companyName) {
    // 先尝试精确匹配
    for (const [key, val] of Object.entries(si)) {
        if (!key.startsWith('si') || !val || !val.title) continue;
        if (val.title.toLowerCase() === companyName.toLowerCase()) return val;
    }
    // 去掉常见后缀（AI, Inc., Corp.）再试
    const stripped = companyName.replace(/\s*(AI|Inc\.?|Corp\.?|Ltd\.?)$/i, '').trim();
    if (stripped !== companyName) {
        for (const [key, val] of Object.entries(si)) {
            if (!key.startsWith('si') || !val || !val.title) continue;
            if (val.title.toLowerCase() === stripped.toLowerCase()) return val;
        }
    }
    return null;
}

// 使用品牌官方颜色将 SVG 转换为 PNG
async function simpleIconToPng(icon, outputPath) {
    const coloredSvg = icon.svg.replace('<svg', `<svg fill="#${icon.hex}"`);
    await sharp(Buffer.from(coloredSvg))
        .resize(128, 128, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
        .png()
        .toFile(outputPath);
}
```

**覆盖率：** 约 43% 的典型交易流量公司（对 Stripe、Anthropic、Databricks、Snowflake、Discord、Shopify、SpaceX、Mistral AI、Hugging Face 等主要科技品牌效果很好；对小众金融科技、生物科技或早期公司效果较弱）。

#### 第二级：基于首字母的回退方案（通过 `sharp` 实现，100% 覆盖）

对于在 `simple-icons` 中未找到的公司，使用 PNG 生成简洁的首字母 logo：

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

    // 第一级：尝试 simple-icons
    const icon = findSimpleIcon(companyName);
    if (icon) {
        await simpleIconToPng(icon, outPath);
        return { path: outPath, source: 'simple-icons' };
    }

    // 第二级：生成首字母回退方案
    await generateInitialLogo(companyName, outPath);
    return { path: outPath, source: 'initial-fallback' };
}
```

**Logo 规范：**
- 所有 logo 保存至 `/home/claude/logos/[company-name].png`
- 所有 logo 为 128×128 PNG，透明背景
- 在幻灯片上，logo 显示高度为 0.35"–0.5" — 它们是点缀而非焦点
- 首字母回退圆圈使用灰色（`BDBDBD`）填充配白色文字 — 与单色配色方案一致
- 不要随机混用 logo 风格 — 如果大多数公司解析为品牌图标，少数回退方案应自然融入

### 步骤 7：生成单页 PPTX

创建幻灯片前，读取 `/mnt/skills/public/pptx/SKILL.md` 和 `/mnt/skills/public/pptx/pptxgenjs.md`。

使用 `pptxgenjs` 创建**单页** PowerPoint。幻灯片应信息密集但视觉清爽 — 想象"高管仪表盘"而非"文字墙"。

#### 幻灯片布局

```
┌─────────────────────────────────────────────────────────────┐
│  DEAL FLOW DIGEST                                           │
│  [Period] · [Sectors]                           [Date]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  $X.XB  │  │  N      │  │  $X.XB  │  │  $X.XB  │       │
│  │ Raised  │  │ Rounds  │  │ Avg Pre │  │ Largest │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  KEY TAKEAWAYS                                              │
│  ─────────────────────────────────────────────────          │
│  [Logo] Takeaway 1 text goes here...                        │
│  [Logo] Takeaway 2 text goes here...                        │
│  [Logo] Takeaway 3 text goes here...                        │
│  [Logo] Takeaway 4 text goes here...                        │
│                                                             │
│  TOP DEALS                                                  │
│  ┌──────────────────────────────────────────────────────────┐│
│  │Company│Type │Announced│Closed│Amount│Pre-$│Post-$│Lead│🔗││
│  │───────│─────│─────────│──────│──────│─────│──────│────│──││
│  │ ...   │ ... │  ...    │ ...  │ ...  │ ... │ ...  │... │🔗││
│  └──────────────────────────────────────────────────────────┘│
│                                                             │
│  [Footer: Deal Flow Digest · Sources: S&P Global Capital IQ]│
│  [Footer: AI Disclaimer]                                    │
└─────────────────────────────────────────────────────────────┘
```

#### 设计规范

**色彩理念：极简、单色优先。** 幻灯片应给人高端金融简报的感觉 — 黑、白、灰为主。颜色**仅**在承载含义时使用（例如折价轮次的红色指示器、突出指标的绿色指示器），或在读者自然期望颜色的地方使用（公司 logo）。切勿将颜色用于纯装饰目的，如背景填充、强调条或渐变效果。

**色板 — 单色高管风：**
- 主背景：`FFFFFF`（白色）— 干净、开阔的幻灯片背景
- 标题栏：`1A1A1A`（近黑色）— 标题区域强对比
- 主文本：`1A1A1A`（近黑色）— 所有正文、统计数字、要点
- 次文本：`6B6B6B`（中灰）— 标签、说明文字、页脚、日期戳
- 边框与分隔线：`D0D0D0`（浅灰）— 微妙的结构线、卡片轮廓、表格边框
- 卡片背景：`F5F5F5`（灰白 / 极浅灰）— 统计卡片填充、表格交替行
- 链接文字：`2B5797`（暗蓝）— 表格中的 Capital IQ 交易链接（幻灯片上唯一的蓝色）
- **语义色（少量使用）：**
  - 折价轮次或负面信号：`C0392B`（暗红）— 仅用作小圆点、标签或单词高亮，绝不作为填充或背景
  - 突出的正面指标（新独角兽、超大规模轮次）：`2E7D32`（暗绿）— 同样的最小化使用：圆点、小标签或单个高亮数字
  - 如果没有数据点需要颜色指示器，**完全不用颜色**。全单色幻灯片完全正确。

**字体：**
- 标题：28–32pt，粗体，近黑色标题栏上的白色
- 统计数字：36–44pt，粗体，近黑色
- 统计标签：10–12pt，中灰（`6B6B6B`）
- 要点文字：12–14pt，近黑色，左对齐
- 表格文字：9–11pt，近黑色，次要列用灰色（`6B6B6B`）
- 链接文字：9–10pt，暗蓝（`2B5797`）
- 页脚：8pt，中灰

**统计卡片（顶部行）：**
- 4 个关键指标以大数字呈现：总融资额、轮次数、平均投前估值、最大轮次
- 每个卡片使用 `F5F5F5` 填充和细 `D0D0D0` 边框 — 无阴影，无彩色填充
- 如果某项统计数据令人惊讶或极端（例如正常量的 3 倍、创纪录交易），可在该数字旁放置一个小彩色圆点或下划线 — 否则保持全单色
- 如果投前估值大多未披露，替换为其他指标（例如中位轮次金额、新独角兽数量）

**关键要点（中间区域）：**
- 3–5 条单行要点，每条前缀相关公司 logo（小尺寸，约 0.35" 高）
- 如果无 logo 可用，使用**灰色圆圈**配白色公司首字母 — 而非彩色圆圈
- 左对齐，间距充足
- 折价或负面要点可使用小红圆点前缀；否则不用颜色
- 在可用时包含估值背景（例如"投后估值 50 亿美元"）

**交易表格（底部区域）：**
- 紧凑表格，展示 4–6 笔最引人注目的交易
- 列：公司、类型（X 轮）、公告日期、交割日期、金额（$M）、投前（$M）、投后（$M）、领投、交易链接
- **公告日期**和**交割日期**列以 `MMM DD` 格式显示日期（例如 "Jan 15"）。这些列是必需的，必须始终存在。如果日期不可用，显示"—"。
- **交易链接**列包含可点击的 "View →" 文本，链接到 Capital IQ：
  ```
  https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=<transaction_id>
  ```
  其中 `<transaction_id>` 是 `get_rounds_of_funding_from_identifiers` 中的 `transaction_id`。
- 如果投前或投后估值未披露，在该单元格中显示"—"
- 表头行使用近黑色（`1A1A1A`）填充配白色文字；交替行使用 `F5F5F5` 和 `FFFFFF`
- **将表格在幻灯片上水平居中。** 计算表格总宽度，然后设置 `x` 使其在幻灯片宽度内居中：`x = (slideWidth - tableWidth) / 2`。对于 16:9 布局（13.33" 宽），如果表格宽 12"，使用 `x = 0.67`。切勿将表格左对齐到幻灯片边缘。
- 保持紧凑 — 这是参考信息，不是焦点
- 表格单元格不使用彩色填充。如果交易为折价轮次，可在金额旁显示小号红色文字标签 "(↓ down)" — 这是表格中唯一允许的颜色。

**交易链接实现（pptxgenjs）：**
在 pptxgenjs 中，超链接通过单元格对象的 `options.hyperlink` 属性添加到表格单元格：
```javascript
// 带 Capital IQ 交易链接的表格单元格
{
  text: "View →",
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
始终将交易表格在幻灯片上居中。动态计算 x 位置：
```javascript
const SLIDE_W = 13.33; // 16:9 幻灯片宽度
const TABLE_W = 12.5;  // 表格总宽度（所有列宽之和）
const TABLE_X = (SLIDE_W - TABLE_W) / 2; // ≈ 0.42"

slide.addTable(tableRows, {
  x: TABLE_X,
  y: tableY,
  w: TABLE_W,
  colW: [1.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.2, 1.6, 0.7], // Company, Type, Announced, Closed, Amount, Pre-$, Post-$, Lead, Link
  // ... 其他选项
});
```
根据需要调整 `colW` 值，但始终从 `(SLIDE_W - sum(colW)) / 2` 重新计算 `TABLE_X` 以保持表格居中。

**页脚：**
- 中灰小字："Deal Flow Digest · [Period] · Sources: S&P Global Capital IQ · Generated [Date]"

**通用色彩规则（严格执行）：**
- 公司 logo 是幻灯片上唯一的"全彩"元素 — 按源文件原样显示。
- 交易链接使用暗蓝（`2B5797`）— 这是除语义红/绿外唯一的非单色文字颜色。
- 除 logo 和链接外，幻灯片在黑白打印机上打印应看起来正确。
- 切勿将颜色应用于背景、强调条、装饰形状或区域分隔线。
- 不确定时，保持灰色。

#### 代码结构

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Deal Flow Digest";

const slide = pres.addSlide();
const SLIDE_W = 13.33; // 16:9 幻灯片宽度（英寸）

// 1. 深色标题栏，含标题和时间周期
// 2. 统计卡片行（4 个卡片：总融资额、轮次数、平均投前估值、最大轮次）
// 3. 带 logo 的关键要点区域（包含估值背景）
// 4. 交易表格，含公告日期、交割日期、投前、投后列和 Capital IQ 交易链接
//    - 表格居中：x = (SLIDE_W - tableWidth) / 2
// 5. 页脚

pres.writeFile({ fileName: "/home/claude/deal-flow-digest.pptx" });
```

按照 pptxgenjs 陷阱指南，对阴影和重复样式使用工厂函数（而非共享对象）。

### 步骤 8：幻灯片 QA

按照 PPTX 技能的 QA 流程执行：

1. **内容 QA：** `python -m markitdown deal-flow-digest.pptx` — 验证所有文本、数字、公司名称、估值数据和交易链接正确
2. **视觉 QA：** 转换为图片并检查：
   ```bash
   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf deal-flow-digest.pptx
   pdftoppm -jpeg -r 200 deal-flow-digest.pdf slide
   ```
   检查元素重叠、文字溢出、对齐问题、低对比度文字、logo 尺寸问题，以及交易链接文字是否可见。
3. **链接 QA：** 验证表格中 Capital IQ URL 格式正确且交易 ID 无误。
4. **修复并重新验证** — 宣布完成前至少完成一轮修复-验证循环。

### 步骤 9：呈现结果

1. 将最终 `.pptx` 复制到 `/mnt/user-data/outputs/`
2. 使用 `present_files` 分享幻灯片
3. 提供 2–3 句话的口头总结：
   - "您的摘要涵盖 [领域] 共 X 轮、总融资 $Y。"
   - 指出单笔最引人注目的交易及其估值
   - 标记任何令人担忧的趋势（折价轮次、估值压缩等）

## 错误处理

### 实体解析失败
- **已知公司返回空结果：** 首先检查 `get_info_from_identifiers` — 如果失败，尝试 `references/sector-seeds.md` 中的别名或 `company_id`。常见品牌→法律名称不匹配：Together AI → "Together Computer, Inc."，Character.ai → "Character Technologies, Inc."，Runway ML → "Runway AI, Inc."。
- **子公司：** DeepMind、GitHub、Instagram、WhatsApp、YouTube、BeReal 等是子公司 — 它们没有独立的融资轮次。在背景中注明"已收购/子公司"，但不要报告为"无活动"。
- **已停业公司：** 如 Convoy（2023 年 10 月关停）在 S&P Global 中仍可解析，但绝不会有新活动。`references/sector-seeds.md` 文件标记了这些 — 包含公司前先检查。
- **`get_funding_summary_from_identifiers` 报错或返回零：** 回退到 `get_rounds_of_funding_from_identifiers` — 摘要工具可靠性较低。切勿将摘要工具作为唯一数据源。
- **错误的 `role` 参数：** 如果投资人视角查询返回空，确认使用的是 `company_investing_in_round_of_funding` 而非 `company_raising_funding`（反之亦然）。

### 数据质量问题
- **周期内无活动：** 如果某领域融资轮次为零，在幻灯片上明确注明（"[领域]在周期内无交易记录"）— 无活动本身也有信息价值。
- **估值数据稀疏：** 如果大多数交易的投前和投后估值未披露，在页脚注释中说明数据限制，表格中使用"—"。统计卡片替换为不同指标（例如中位轮次金额）而非平均投前估值。
- **Logo 获取失败：** `simple-icons` npm 包对典型交易流量公司覆盖率约 43%。其余使用 `sharp` 生成的首字母回退方案。保持图标风格一致 — 不要混用随机方法。如果 `simple-icons` 或 `sharp` 安装失败，回退到 pptxgenjs 基于形状的首字母（灰色椭圆 + 白色文字叠加），无需外部依赖。
- **单页交易过多：** 如果重要交易超过 6 笔，表格显示前 6 笔并添加脚注："+N 笔额外交易未显示。" 按交易金额排序。
- **大型公司库：** 对于 100+ 家公司的多领域摘要，所有 API 调用按 15–20 家分批。优先深度覆盖重要交易而非次要交易的完整性。
- **过期种子：** 如果竞争对手扩展对某领域返回结果极少，种子公司可能过于小众。增加 2–3 个更知名的名称并重新扩展。
- **链接的交易 ID 无效：** 如果融资工具返回的 `transaction_id` 无法生成有效的 Capital IQ URL，省略该行的链接单元格，而非包含一个坏链接。

## 示例提示

- "给我一份 AI 和金融科技的每周交易流量摘要"
- "总结本周生物科技的融资情况"
- "我覆盖范围的交易汇总 — 网络安全、云基础设施和开发工具 — 最近两周"
- "本周我关注的所有领域风险投资有什么动态？"
- "本月气候科技快速交易流量幻灯片"
