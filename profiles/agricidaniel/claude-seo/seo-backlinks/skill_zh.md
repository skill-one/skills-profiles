# 反向链接分析

## 源检测

在分析之前，检测可用数据源：

1. **DataForSEO MCP** (高级版)：检查 `backlinks_summary` 工具是否可用
2. **Moz API** (免费注册)：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run backlinks_auth.py --check moz --json`
3. **Bing Webmaster** (免费注册)：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run backlinks_auth.py --check bing --json`
4. **Keywords Everywhere** (免费注册；域名排名加引用域名数量)：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run backlinks_auth.py --check keywordseverywhere --json`
5. **Common Crawl** (始终可用)：域名级图与PageRank
6. **验证爬虫** (始终可用)：检查已知反向链接是否仍然存在

运行 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run backlinks_auth.py --check --json` 可一次性检测所有源。

如果配置的源仅限于始终可用的层级：

- 仍使用Common Crawl域名指标生成报告
- 建议："运行 `/seo backlinks setup` 添加免费的Moz和Bing API密钥以获取更丰富的数据"

## 快速参考

| 命令 | 目的 |
|------|------|
| `/seo backlinks <url>` | 全反向链接分析（使用所有可用源） |
| `/seo backlinks gap <url1> <url2>` | 竞争对手反向链接差距分析 |
| `/seo backlinks toxic <url>` | 有毒链接检测和拒绝建议 |
| `/seo backlinks new <url>` | 新增和丢失的链接（仅DataForSEO） |
| `/seo backlinks verify <url> --links <file>` | 验证已知反向链接是否仍然存在 |
| `/seo backlinks setup` | 显示免费反向链接API的设置说明 |

## 分析框架

生成以下7个部分。每个部分按优先级列出数据源。

### 1. 配置概述

**DataForSEO:** `backlinks_summary` → 总反向链接数、引用域名数、域名排名、遵循率、趋势。

**Moz API:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py metrics <url> --json` → 域名权威性、页面权威性、垃圾邮件评分、链接根域名、外部链接。

**Keywords Everywhere:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run keywordseverywhere_api.py rank <domain> --json` → 0-10 Open PageRank (`open_page_rank`)、一个全局 `rank` 和一个引用域名数量 (`referring_domains`)，根据当前API；无锚点或单个链接。当Moz未配置时作为备用；当两者都可用时，不要用Keywords Everywhere替代Moz。

**Common Crawl:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run commoncrawl_graph.py <domain> --json` → PageRank、调和中心性和低置信度排名/存在数据。

**评分：**

| 指标 | 良好 | 警告 | 严重 |
|------|------|------|------|
| 引用域名 | >100 | 20-100 | <20 |
| 遵循率 | >60% | 40-60% | <40% |
| 域名多样性 | 没有单个域名 >5% | 1个域名 >10% | 1个域名 >25% |
| 趋势 | 增长或稳定 | 缓慢下降 | 快速下降 (>20%/季度) |

### 2. 锚文本分布

**DataForSEO:** `backlinks_anchors`

**Moz API:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py anchors <url> --json`

**Bing Webmaster:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run bing_webmaster.py links <url> --json` (从链接详情中提取锚文本)

**健康分布基准：**

| 锚文本类型 | 目标范围 | 过度优化信号 |
|------------|----------|-------------|
| 品牌锚文本（公司/域名） | 30-50% | <15% |
| URL/裸链接 | 15-25% | N/A |
| 通用锚文本（"点击这里"、"了解更多"） | 10-20% | N/A |
| 精确匹配关键词 | 3-10% | >15% |
| 部分匹配关键词 | 5-15% | >25% |
| 长尾/自然锚文本 | 5-15% | N/A |

如果精确匹配锚文本超过15%，则作为审查启发式标记，这可能表明非自然或链接垃圾邮件模式。

### 3. 引用域名质量

**DataForSEO:** `backlinks_referring_domains`

**Moz API:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py domains <url> --json` → 域名DA评分

**Common Crawl:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run commoncrawl_graph.py <domain> --json` → 域名级排名/存在数据，无验证引用域名计数

分析：
- **顶级域名分布**：.edu、.gov、.org = 高权威。过多的.xyz、.info = 低质量
- **国家分布**：匹配目标市场。80%+来自无关国家 = PBN信号
- **域名排名分布**：健康配置包含来自所有权威层级的链接
- **每个域名的遵循/无遵循**：仅无遵循的网站 = 有限的SEO价值

### 4. 有毒链接检测

**DataForSEO:** `backlinks_bulk_spam_score` + 参考中的有毒模式

**Moz API:** 原始供应商垃圾邮件评分，来自 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py metrics <url> --json` (标记源值；仅当验证当前Moz文档时才应用阈值)

**验证爬虫：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run verify_backlinks.py --target <url> --links <file> --json` (验证可疑链接是否仍然存在)

**高风险指标（立即标记）：**
- 来自已知PBN（私有博客网络）域名的链接
- 非自然锚文本模式（100%精确匹配来自一个域名）
- 来自受罚或已删除域名的链接
- 大量目录提交（50+目录链接）
- 链接农场（每页有10K+出站链接的网站）
- 付费链接模式（整个域名的页脚/侧边栏链接）

**中等风险指标（手动审查）：**
- 来自无关细分市场的链接
- 互惠链接模式
- 来自内容页面的链接（<100字）
- 来自单个域名的过多链接（1个域名>50个反向链接）

加载 `../seo/references/backlink-quality.md` 获取完整的30种有毒模式和拒绝标准。

### 5. 按反向链接排名的页面

**DataForSEO:** `backlinks_backlinks`，目标类型为"页面"

**Moz API:** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py pages <domain> --json`

查找：
- 哪些页面吸引最多的反向链接
- 高权威链接的页面（链接磁铁）
- 无反向链接的页面（内部链接机会）
- 有反向链接的404页面（重定向机会以收回链接权益）

### 6. 竞争对手差距分析

**DataForSEO:** `backlinks_referring_domains` 对两个域名，然后比较

**Bing Webmaster：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run bing_webmaster.py compare <url1> <url2> --json`
仅当两个属性都注册并可访问相同的Bing API帐户时。对于任意竞争对手，使用DataForSEO、Moz或Common Crawl。

**Moz API：** 通过 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run moz_api.py metrics <url> --json` 对每个域名比较DA/PA

输出：
- 链接到竞争对手但未链接到目标的域名 = 链接建设机会
- 链接到两者之间的域名 = 验证现有关系
- 仅链接到目标的域名 = 竞争优势
- 前二十大链接建设机会，域名权威性

### 7. 新增和丢失的链接

**DataForSEO仅限：** `backlinks_backlinks`，使用30/60/90天日期过滤器进行变化

**验证爬虫：** 对于已知链接，使用 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run verify_backlinks.py --target <url> --links <file> --json` 验证当前状态

**注意：** 免费源无法跟踪随时间变化的新增/丢失链接。如果请求此部分而没有DataForSEO，通知用户："链接速度跟踪需要DataForSEO扩展。免费源仅提供瞬时的快照。"

**红旗：**
- 新增链接突然激增（可能的负面SEO攻击）
- 突然丢失许多链接（网站受罚或内容删除）
- 3个月以上速度下降（内容不再吸引链接）

## 反向链接健康评分

计算0-100分。当混合源时，应用置信度加权：

| 因素 | 权重 | 源（优先级顺序） | 置信度 |
|------|------|------------------|--------|
| 引用域名数量 | 20% | DataForSEO > Moz | 1.0 / 0.85 |
| 域名质量分布 | 20% | DataForSEO > Moz DA分布 | 1.0 / 0.85 |
| 锚文本自然性 | 15% | DataForSEO > Moz > Bing锚点 | 1.0 / 0.85 / 0.70 |
| 有毒链接比率 | 20% | DataForSEO > Moz垃圾邮件评分 | 1.0 / 0.85 |
| 链接速度趋势 | 10% | DataForSEO仅限 | 1.0 |
| 遵循/无遵循比率 | 5% | DataForSEO > Bing详情 | 1.0 / 0.70 |
| 地理相关性 | 10% | DataForSEO > Bing国家 | 1.0 / 0.70 |

**数据充足性门控：** 计算有多少个7个因素至少有一个可用数据源。
- **4+因素有数据：** 生成0-100的数值分数（按比例重新分配缺失权重）
- **少于4个因素：** 不要生成数值分数。相反，显示：
  ```
  反向链接健康评分：数据不足 (X/7因素评分)
  ```
  显示可用的单个因素分数及其源和置信度。
  建议："配置Moz API（免费）以获取可评分配置文件。运行 `/seo backlinks setup`"

### 不得：对未测量的内容进行评分

**当Common Crawl是唯一可用源时，你不得生成任何类型的数值分数** —— 不是健康分数，不是每个因素分数，也不是"近似"或"估计"数字。Common Crawl仅提供排名和存在信号。报告低置信度排名/存在数据，并在每个数字处使用字面字符串 `Not Assessed`。

**使用 `source: not-assessed` 书写的发现不得带有数值分数。**

少于4个数据源的数值分数是**误导性**的：它暗示健康状况不佳，而实际情况是我们缺乏数据。

### 验证门控（必需，非可选）

此规则之前已在此技能中声明，但仍然违反，因此现在可以检查。**在编写任何反向链接输出之前，运行验证器：**

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run validate_backlink_report.py --report <report>.json --json
```

传递你实际收集的源 (`cc_data`，`moz_data`，`bing_data`，`dataforseo_data`，`scoring_factors` 和你的 `findings` 列表)。当 `source_score_consistency` 检查失败时，报告状态为 `status: FAIL`，当：

- 存在数值分数但未提供可评分源（Moz、Bing或DataForSEO）的数据 —— 即Common-Crawl仅用的情况，以及
- 任何标记为 `source: not-assessed` 的发现带有数值 `score`，`value` 或 `health_score`。

**如果验证器返回 `status: FAIL`，不要展示报告。** 修复发现 —— 将有害数字替换为 `Not Assessed` —— 并重新运行，直到通过。

## 输出格式

### 反向链接健康评分：XX/100（或数据不足）

| 部分 | 状态 | 分数 | 数据源 |
|------|------|------|--------|
| 配置概述 | 通过/警告/失败 | XX/100 | Moz (0.85) |
| 锚文本分布 | 通过/警告/失败 | XX/100 | Moz (0.85) |
| 引用域名质量 | 通过/警告/失败 | XX/100 | CC (0.50) |
| 有毒链接 | 通过/警告/失败 | XX/100 | Moz垃圾邮件 (0.85) |
| 顶级页面 | 信息 | N/A | Moz (0.85) |
| 链接速度 | 通过/警告/失败 | XX/100 | DataForSEO仅限 |

### 严重问题（立即修复）
### 高优先级（1个月内修复）
### 中优先级（持续改进）
### 链接建设机会（前10名）

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 未配置源 | 无API密钥，无DataForSEO | 运行 `/seo backlinks setup` |
| Moz速率限制 | 免费版：1请求/10秒 | 等待10秒，重试。脚本内置。 |
| Bing网站未验证 | 网站未在Bing中验证 | 在 https://www.bing.com/webmasters 中验证 |
| CC下载超时 | 大型图文件，连接慢 | 使用 `--timeout 180` 标志 |
| DataForSEO不可用 | 扩展未安装 | 运行 `./extensions/dataforseo/install.sh` |
| 无反向链接数据返回 | 域名太新或非常小 | 注意：小网站可能有<10个反向链接 |

**后备级联：**
1. DataForSEO可用？ → 使用为首选（置信度：1.0）
2. Moz配置？ → 使用DA/PA/垃圾邮件/锚点（置信度：0.85）
3. Bing配置？ → 仅在两个属性都可访问时使用注册属性链接和比较（置信度：0.70）
4. Moz未配置但Keywords Everywhere可用？ → 使用Profile Overview排名仅后备（置信度：0.60；单一指标，无链接计数/锚点）
5. 始终：Common Crawl用于域名级指标（置信度：0.50）
6. 始终：验证爬虫用于已知链接检查（置信度：0.95）
7. 什么也不行？ → "运行 `/seo backlinks setup` 配置免费API"

## 交付前审查（强制）

在向用户展示任何反向链接分析之前，内部运行此清单。不要跳过此步骤。修复发现的任何问题，然后再显示报告。

### 每个声明核实事实
- [ ] **模式声明**：`parse_html` 返回每个块 `@type` 吗？如果任何 `@type` 缺失，重新检查，它可能使用 `@graph` 包装器（有效的JSON-LD，不是格式错误）。
- [ ] **"link_removed"发现**：页面是JS渲染的吗？如果 `unverifiable_js`，请说明，永远不要将JS渲染页面报告为"链接已移除"（那是假阴性）。
- [ ] **H1发现**：`h1_suspicious` 列表中有任何H1吗？如果是，请注意它们可能是计数器/统计数据，而不是语义标题。
- [ ] **互惠链接**：如果网站A链接到网站B，并且B也链接回A，将其标记为互惠链接模式。检查出站链接与验证的入站源进行对比。
- [ ] **健康评分**：7个因素中有4个以上被评分吗？如果不是，报告 `INSUFFICIENT DATA`，永远不要显示误导性的数值分数。

### 核实数据源标签
- [ ] 报告中的每个指标都有源标签（例如，"Parsed (0.95)"，"CC (0.50)）
- [ ] 每个"未找到"结果都区分"未抓取"与"低于阈值"与"错误"
- [ ] 标记为 `unverifiable_js` 的社交媒体页面（不是 `link_removed`）

### 交叉检查一致性
- [ ] 平台检测匹配实际信号（检查wp-content、shopify CDN等）
- [ ] 摘要中的引用域名数量与实际验证的链接列表匹配
- [ ] 没有声明没有数据源支持

如果任何检查失败，修复发现后再展示。永远不要将推断数据作为事实展示。

## 分析后

完成任何反向链接分析命令后，始终提供：
"生成专业PDF报告？使用 `/seo google report`"

## 参考文档

按需加载（不要在启动时加载）：
- `${CLAUDE_PLUGIN_ROOT}/skills/seo/references/backlink-quality.md` -- 详细的毒性链接模式和评分方法（共享参考，分析有毒链接或垃圾邮件评分时加载）
- `${CLAUDE_PLUGIN_ROOT}/skills/seo/references/free-backlink-sources.md` -- 源比较、置信度加权、设置指南（共享参考，配置免费反向链接API时加载）
