# 公司研究

发现并深入研究可销售的公司。使用 Browserbase 搜索 API 进行发现，并采用 Plan→Research→Synthesize 模式进行深度丰富——输出评分研究报告和 CSV 文件。

**必需**：`BROWSERBASE_API_KEY` 环境变量和 `browse` CLI 安装。

**首次运行设置**：首次运行时，系统会提示您批准 `browse cloud fetch`、`browse cloud search`、`cat`、`mkdir`、`sed` 等。为每个选择 **"是，并且不再询问：browse cloud fetch:\*"**（或等效选项）以自动批准本次会话。要永久批准，请将这些内容添加到您的 `~/.claude/settings.json` 中的 `permissions.allow` 下：
```json
"Bash(browse:*)", "Bash(bunx:*)", "Bash(bun:*)", "Bash(node:*)",
"Bash(cat:*)", "Bash(mkdir:*)", "Bash(sed:*)", "Bash(head:*)", "Bash(tr:*)", "Bash(rm:*)"
```

**路径规则**：在所有 Bash 命令中始终使用完整字面路径——**不要**使用 `~` 或 `$HOME`（两者都会触发“shell 扩展语法”批准提示）。一次性解析家目录并到处使用。在构建子代理提示时，将 `{SKILL_DIR}` 替换为完整字面路径。

**输出目录**：所有研究输出都到 `~/Desktop/{company_slug}_research_{YYYY-MM-DD}/`。此目录包含每个研究公司的 `.md` 文件和一个最终 `.csv` 文件。用户将获得评分电子表格和完整研究文件。

**关键——工具限制（适用于主代理和所有子代理）**：
- 所有网络搜索：使用 `browse cloud search`。**绝对不要**使用 WebSearch。
- 所有页面内容提取：使用 `node {SKILL_DIR}/scripts/extract_page.mjs "<url>"`。此脚本通过 `browse cloud fetch --output` 获取，解析标题 + 元标签 + 可见正文文本，并在获取失败或返回瘦 JS 渲染内容时自动回退到 `browse get markdown`。**绝对不要**手动编写 `browse cloud fetch | sed` 管道——它会删除元标签并且不会解析 stdout JSON 封装。**绝对不要**使用 WebFetch。
- 所有研究输出：子代理使用 bash heredoc 将**每个公司写入一个 markdown 文件**到 `{OUTPUT_DIR}/{company-slug}.md`。**绝对不要**使用 Write 工具或 `python3 -c`。有关文件格式，请参阅 `references/example-research.md`。
- 报告 + CSV 编译：使用 `node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open`——一步生成 HTML 报告和 CSV，并在浏览器中打开概览。
- URL 去重：在发现后使用 `node {SKILL_DIR}/scripts/list_urls.mjs /tmp`。
- **子代理必须仅使用 Bash 工具。不允许其他工具。**
- **主代理****绝对不要**读取原始发现 JSON 批处理文件。使用 `list_urls.mjs` 进行去重。

**关键——防止幻觉规则（适用于主代理和所有子代理）**：
- **绝对不要**从网站的字体、框架（Framer/Next.js/React）、设计系统或排版中推断 `product_description`、`industry` 或 `target_audience`。这些是装饰性的，并不能说明公司销售什么。
- **绝对不要**让用户的 ICP 泄露到目标的描述中。如果您不知道目标做什么，请写 `Unknown`——不要将它们与 ICP 进行模式匹配。
- `product_description` 必须引用或释义 `extract_page.mjs` 输出中的特定短语（TITLE、META_DESCRIPTION、OG_DESCRIPTION、HEADINGS 或 BODY）。如果这些字段没有产生可识别的产品声明，请写 `Unknown — homepage content not accessible`。
- 如果 `product_description` 是 `Unknown`，将 `icp_fit_score` 限制在 3，并将 `icp_fit_reasoning` 设置为 `Insufficient evidence — homepage returned no readable content`。

**关键——最小化权限提示**：
- 子代理必须将所有文件写入批处理到单个 Bash 调用中，使用链接的 heredoc。一个 Bash 调用 = 一个权限提示。
- 将所有搜索和所有获取批处理到单个 Bash 调用中，使用 `&&` 链接。

## 管道概述

按顺序执行以下 5 步。不要跳过步骤或重新排序。

1. **公司研究**——深入理解用户的公司、产品和销售对象
2. **深度模式选择**——根据目标公司数量选择研究深度
3. **发现**——使用多样化的搜索查询找到目标公司
4. **深度研究 & 评分**——研究每个公司，评分 ICP 匹配度
5. **报告 & CSV**——展示结果，编译评分 CSV

---

## 第 0 步：设置输出目录

在开始之前，在用户的桌面上创建输出目录：

```bash
OUTPUT_DIR=~/Desktop/{company_slug}_research_{YYYY-MM-DD}
mkdir -p "$OUTPUT_DIR"
```

将 `{company_slug}` 替换为用户的公司名称（小写，连字符），将 `{YYYY-MM-DD}` 替换为今天的日期。将 `{OUTPUT_DIR}`（作为完整字面路径，不要使用 `~`）传递给所有子代理提示，以便它们在那里写入研究文件。

还清理先前的运行中的发现批处理文件：
```bash
rm -f /tmp/company_discovery_batch_*.json
```

## 第 1 步：深度公司研究

这是最重要的步骤。下游所有步骤的质量都取决于对用户公司的深入理解。

1. 向用户询问其公司名称或 URL

2. **检查现有配置文件**：
   - 列出 `{SKILL_DIR}/profiles/` 中的文件（忽略 `example.json`）
   - 如果存在匹配的配置文件 → 加载它，向用户展示："我拥有您来自 {researched_at} 的配置文件。仍然准确吗？如果确定 → 跳到第 2 步。
   - 如果没有配置文件存在 → 继续执行下面的深度研究。

3. **对用户的公司运行完整深度研究**，使用 Plan→Research→Synthesize 模式。
   参考 `references/research-patterns.md` 获取子问题模板和研究方法。

   **关键研究步骤**：
   - 搜索：`browse cloud search "{company name}" --num-results 10`
   - 获取主页：`node {SKILL_DIR}/scripts/extract_page.mjs "{company website}"`
   - **通过站点地图发现站点页面**（**不要**硬编码路径，如 `/about` 或 `/customers`）：
     1. `browse cloud fetch --allow-redirects "{company website}/sitemap.xml"` — 站点地图很小，原始 `browse cloud fetch` 即可
     2. 扫描包含关键词的 URL：`customer`、`case-stud`、`pricing`、`about`、`use-case`、`industry`、`solution`
     3. 可选地也获取 `/llms.txt` 以获取页面描述
     4. 选择 3-5 个最相关的 URL 并使用 `extract_page.mjs` 提取（**不要**使用原始 `browse cloud fetch`）
   - 搜索外部背景和竞争对手
   - 积累具有置信级别的发现

   **合成配置文件**：
   公司、产品、现有客户、竞争对手、用例。
   **不要**包括 ICP 或子垂直——这些是每次运行的决定。

4. 向用户展示配置文件以供确认。在确认之前不要继续。

5. **保存确认的配置文件**到 `{SKILL_DIR}/profiles/{company-slug}.json`

6. **使用 `AskUserQuestion` 提问**，使用复选框：
   - "您正在瞄准哪些细分市场？" 选项来自公司研究
   - "公司阶段？" — 初创公司、中型市场、企业、全部
   - "多少公司 / 深度？" — 快速 (~100)、深度 (~50)、更深 (~25)
   - 这是**唯一**的用户交互。在此之后，直到结果准备好之前，执行静默。

## 第 2 步：深度模式选择

| 模式 | 每个公司的研究 | 适用于 |
|------|---------------------|----------|
| `quick` | 主页 + 1-2 搜索 | ~100 公司，广泛扫描 |
| `deep` | 2-3 子问题，5-8 工具调用 | ~50 公司，扎实研究 |
| `deeper` | 4-5 子问题，10-15 工具调用 | ~25 公司，全面情报 |

## 第 3 步：发现

**公式**：`ceil(requested_companies / 35)` 搜索查询需要。由于过滤通常会减少 50-70%，因此需要多发现 2-3 倍。

使用这些模式生成搜索查询：
- 行业 + 公司阶段 + 地理区域 ("fintech 初创公司 A 轮 旧金山")
- 技术栈 + 用例 ("使用 Selenium 进行网络抓取的公司")
- 竞争对手邻近 ("已知 ICP 公司的替代品")
- 买家画像 + 痛点 ("在浏览器自动化方面遇到困难的工程团队")

**流程**：
1. **同时启动所有发现子代理**（每条消息最多 ~6 个）。每个在单个 Bash 调用中运行其查询：
   ```bash
   browse cloud search "{query}" --num-results 25 --output /tmp/company_discovery_batch_{N}.json
   ```
2. 所有波次完成后，去重：`node {SKILL_DIR}/scripts/list_urls.mjs /tmp`
3. **过滤 URL 列表**——删除：
   - 博客文章、新闻文章（globenewswire.com、techcrunch.com 等）
   - 目录/聚合器（tracxn.com、crunchbase.com、g2.com）
   - 用户的竞争对手和现有客户（来自配置文件）
   仅保留公司主页。

参考 `references/workflow.md` 获取子代理提示模板和波次管理。

## 第 4 步：深度研究 & 评分

并行启动子代理以研究公司。参考 `references/workflow.md` 获取丰富子代理提示模板。参考 `references/research-patterns.md` 获取完整研究方法。

**流程**：
1. 将过滤后的 URL 分组到每个子代理（快速：~10，深度：~5，更深：~2-3）
2. **同时启动所有丰富子代理**（每条消息最多 ~6 个）
3. 每个子代理仅使用 Bash——对于每个公司：

   **阶段 A — 计划**（快速模式下跳过）：
   根据ICP和丰富字段分解为 2-5 个子问题。

   **阶段 B — 研究循环**：
   搜索和获取页面，提取发现。尊重步骤预算（快速：2-3，深度：5-8，更深：10-15）。

   **阶段 C — 合成**：
   评分 1-10 的 ICP 匹配度，并从发现中填充丰富字段。

4. 子代理使用单个 Bash 调用和链接的 heredoc 将所有 markdown 文件写入 `{OUTPUT_DIR}/`
5. 所有子代理完成后，继续第 5 步

**关键**：在每个子代理提示中包含确认的 ICP 描述。将完整字面 `{OUTPUT_DIR}` 路径传递给每个子代理。

## 第 5 步：报告 & CSV

1. **生成 HTML 报告 + CSV**（自动在浏览器中打开概览）：
   ```bash
   node {SKILL_DIR}/scripts/compile_report.mjs {OUTPUT_DIR} --open
   ```
   这将生成：
   - `{OUTPUT_DIR}/index.html` — 带有评分表格的概览页面（在浏览器中打开）
   - `{OUTPUT_DIR}/companies/*.html` — 单个公司页面（从概览链接）
   - `{OUTPUT_DIR}/results.csv` — 可导入电子表格/CRM 的评分电子表格

2. **在聊天中展示摘要**：

```
## 公司研究完成

- **研究公司总数**：{count}
- **深度模式**：{mode}
- **评分分布**：
  - 强匹配 (8-10)：{count}
  - 部分匹配 (5-7)：{count}
  - 弱匹配 (1-4)：{count}
- **浏览器中打开报告**：~/Desktop/{company_slug}_research_{date}/index.html
```

3. 在表格中展示**顶级公司**按 ICP 评分排序：

```
| 公司 | 评分 | 产品 | 行业 | 匹配原因 |
|---------|-------|---------|----------|---------------|
| Acme | 9 | AI 库存管理 | 电子商务 SaaS | A 轮，使用 Selenium，扩展到欧盟 |
```

4. 对于前 3-5 家公司，展示简要研究摘要——关键发现、为什么它们是好的匹配，以及与它们接触的具体角度。

提供深入挖掘特定公司、调整评分标准或使用不同查询重新运行发现的选项。
