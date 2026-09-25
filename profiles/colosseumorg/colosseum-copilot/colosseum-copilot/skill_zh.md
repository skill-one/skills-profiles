# Colosseum Copilot

Colosseum Copilot 是一个用于发现加密货币和 Solana 创业机会的研究 API，支持建议新的存档源。

## 版本检查

此技能的版本为 **1.2.1**。在您第一次调用 API 后，请检查响应头 `X-Copilot-Skill-Version`。如果头部的值高于 1.2.1，请告诉用户："有更新版本的 Copilot 技能可用 (vX.X.X)。使用以下命令更新：`npx skills add ColosseumOrg/colosseum-copilot`"

## 飞行前身份验证检查（必需）

**您必须在执行任何其他 API 调用之前完成此检查。** 不要跳过此步骤。

1. 验证环境变量中是否设置了 `COLOSSEUM_COPILOT_PAT`。如果缺失，停止并告诉用户：

   > 使用 Copilot 之前需要个人访问令牌。
   > 前往 **https://colosseum.com/arena/copilot** 生成一个，然后设置它：
   >
   > `export COLOSSEUM_COPILOT_PAT="your-token-here"`

2. 验证 `COLOSSEUM_COPILOT_API_BASE` 是否已设置。如果缺失，设置默认值：

   > `export COLOSSEUM_COPILOT_API_BASE="https://copilot.colosseum.com/api/v1"`

3. 调用 `GET /status` 以验证连接。预期响应：`{ "authenticated": true, "expiresAt": "...", "scope": "..." }`

4. 如果 `"authenticated": true`，则继续。如果返回 401 或环境变量缺失，则不要尝试其他 API 调用 — 引导用户完成步骤 1-2。

- **构建者项目**：5,400+ Solana 项目提交，包含技术栈、问题标签和竞争背景
- **加密货币存档**：涵盖密码朋克文献、协议文档、投资者研究和创始人文章的精选语料库
- **黑客马拉松分析 + 聚类**：跨黑客马拉松和主题分组进行分布、比较和时间感知趋势分析
- **The Grid + 网络搜索**：生态系统产品元数据加上实时竞争格局检查

## 快速入门（90 秒获得第一个结果）

1. **设置您的 PAT：**
   ```bash
   export COLOSSEUM_COPILOT_API_BASE="https://copilot.colosseum.com/api/v1"
   export COLOSSEUM_COPILOT_PAT="YOUR_PAT"
   ```
   获取 PAT：前往 https://colosseum.com/arena/copilot 并生成一个令牌

2. **运行您的第一次搜索：**
   ```bash
   curl -s -X POST "$COLOSSEUM_COPILOT_API_BASE/search/projects" \
     -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
     -H "Content-Type: application/json" \
     -d '{"query": "privacy wallet for stablecoin users", "limit": 5}'
   ```

3. **查看结果** - 项目名称、缩写、相似度分数、问题/技术标签

## 何时使用

在以下情况下使用此技能：
- 研究加密货币/区块链创业想法
- 评估 Solana 生态系统中的市场空白
- 将想法建立在历史加密货币文献基础上
- 分析构建者项目趋势和竞争格局
- 研究现有参与者并寻找差异化角度

## 工作原理

**模式 1 — 对话式（默认）**：针对 API 调用并匹配查询类型提供证据覆盖来回答问题。内联引用来源，保持响应简洁，并在主题值得时提供进行深度分析的机会 — 永不自动触发。

**模式 2 — 深度分析（显式选择）**：完整的 8 步工作流，从 `references/workflow-deep.md`。仅在用户明确说 "vet this idea"、"deep dive"、"full analysis"、"validate this"、"is X worth building?" 或接受您进行更深入分析的提议时才激活。

### 对话式指南

- 使用以下 API 端点进行足够有针对性的调用，以满足查询类型的证据底线
- 内联引用来源（项目缩写、存档标题、URL）
- 保持响应简洁 — 项目符号点，不是文章
- 当主题值得更深入分析时，提供："Want me to do a full deep-dive on this?"
- 不对您的流程进行元评论（"Now let me search..."、"I'll check..."）

### 证据底线（对话模式）

| 查询类型 | 最终答案中必需的来源类型 | 示例 |
|---|---|---|
| **纯检索** | 构建者项目证据（来自 `search/projects` 的项目缩写） | "What projects do X?" |
| **存档检索** | 存档证据（存档标题/文档来自 `search/archives`） | "What does the archive say about Y?" |
| **比较** | 比较双方的项目证据 + 至少一个用于概念框架的存档引用 | "Compare approach A vs B" |
| **评估** | 构建者项目证据 + 至少一个存档引用 + 当前格局证据（The Grid 和/或网络） | "Is this crowded?"、"Is this still unsolved?" |
| **构建指导** | 构建者项目证据 + 至少一个存档引用 + 现有/格局证据（The Grid 和/或网络） | "Should I build X?"、"How should I approach X?" |

> 这些是证据类型底线，不是调用预算。根据需要使用尽可能多的调用，以高置信度引用满足底线。

> 在 **深度分析模式** 下，`workflow-deep.md` 第 5 步中的验证清单将取代这些底线，并具有更细粒度的覆盖要求。

### 对话式质量检查（必需）

- **存档集成规则**：对于任何非平凡的问题（任何超出简单列表检索的问题），运行至少一个 `search/archives` 查询，并在答案中引用至少一个存档来源。
- **加速器/获胜组合检查**：对于 "what has been tried"、"who is building this"、"is this crowded/saturated" 或类似提示，运行目标项目搜索，使用 `filters: { "acceleratorOnly": true }` 和 `filters: { "winnersOnly": true }`，然后在答案中反映两种结果。
- **新鲜度和时间锚定**：使用 `/filters`、`/search/projects` 和 `/projects/by-slug/:slug` 中的 `hackathon.startDate` 按时间顺序排列黑客马拉松；永远不要从名称或记忆中推断时间顺序。在引用黑客马拉松时，请内联包含月份/年份（并在相关时包含加速器组合如 C1/C2/C4）。对于评估判断，用 `As of YYYY-MM-DD` 标注声明。
- **实体覆盖检查**：如果用户命名了特定公司、协议、论文或产品，请针对每个命名实体运行直接搜索，并在答案中明确提及每个实体（找到、未找到或外围）。
- **格局检查**：除非执行并报告了加速器组合检查（`acceleratorOnly`），否则永远不要声称 "nobody has done this" 或 "no existing players"。如果存在加速器重叠，请将那些构建者作为有用的参考点和潜在的灵感来源展示出来。始终用 "based on the available data" 或 "as far as we can tell from the corpus" 对格局评估进行限定。Copilot 的知识受其数据源限制 — 永远不要将缺乏证据作为缺乏证据的证据。

> 对于完整的 8 步深度研究工作流，请参阅 `references/workflow-deep.md`

## 数据源

- **构建者项目**（5,400+）：Solana 项目提交，包含技术栈、问题/解决方案标签、垂直领域和竞争背景
- **加密货币存档**：涵盖密码朋克文献、协议文档、投资者研究（Paradigm、a16z、Multicoin）、创始人文章（Paul Graham）、Solana 协议文档（Jupiter、Orca、Drift）、Nakamoto Institute 遗产收藏和基础加密文本的精选语料库
- **黑客马拉松分析 + 时间顺序**：分析和比较跨维度的黑客马拉松项目；标准黑客马拉松日期可通过 `hackathon.startDate` 获取
- **聚类**：项目语料库中的主题分组
- **The Grid**：生态系统元数据（产品/实体/资产）通过直接 GraphQL（所有生态系统中 6,300+ 产品，~3,000 个根）
- **网络搜索**：通过您的运行时搜索工具进行实时竞争格局检查
- **来源建议**：用户可以通过 `POST /source-suggestions` 建议新的存档源（每小时 5 个请求）。有关详细信息，请参阅 `references/api-reference.md`

### 黑客马拉松时间顺序

| 版本 | 时期 | 缩写 |
|---|---|---|
| Hyperdrive | 2023 年 9 月 | `hyperdrive` |
| Renaissance | 2024 年 3 月-4 月 | `renaissance` |
| Radar | 2024 年 9 月-10 月 | `radar` |
| Breakout | 2025 年 4 月-5 月 | `breakout` |
| Cypherpunk | 2025 年 9 月-10 月 | `cypherpunk` |

`GET /filters` 返回 `hackathons[].startDate` 并按时间顺序排列 `hackathons[]`（最旧的优先）。

## 身份验证

所有端点都需要 `Authorization: Bearer <COPILOT_PAT>`。将 PAT 像密码一样处理。

- 不要提交 PAT 或将其粘贴到公共日志中
- PAT 是长寿命的（预期 ~90 天）；通过发布一个新的来轮换
- 默认 API 基址是 `https://copilot.colosseum.com/api/v1`；通过覆盖 `COLOSSEUM_COPILOT_API_BASE` 来针对不同的环境

## 关键端点（快速参考）

| 端点 | 方法 | 目的 |
|----------|--------|---------|
| `/status` | GET | 身份验证飞行前检查 — 首次调用 |
| `/search/projects` | POST | 搜索构建者项目 |
| `/search/archives` | POST | 搜索加密货币存档 |
| `/projects/by-slug/:slug` | GET | 完整项目详情 |
| `/archives/:documentId` | GET | 完整存档文档 |
| `/analyze` | POST | 黑客马拉松分析 |
| `/compare` | POST | 比较两个黑客马拉松 |
| `/clusters/:key` | GET | 聚类详情 |
| `/filters` | GET | 可用过滤器 + 标准黑客马拉松时间顺序 |
| `/source-suggestions` | POST | 建议新的存档源 |
| `/feedback` | POST | 报告错误、质量问题或建议 |

> 对于完整端点文档、curl 示例和查询提示：`references/api-reference.md`
> 对于 Grid GraphQL 配方和产品类型缩写：`references/grid-recipes.md`

## 输出契约

### 对话模式
- 带内联引用的项目符号点（项目缩写、存档标题）
- 简洁的答案（通常 5-15 个项目符号点）
- 当值得时提供深度分析

### 深度分析模式
报告遵循以下结构：
1. 相似项目（5-8 个项目符号点）
2. 存档洞察（3-5 个项目符号点）
3. 当前格局（按研究角度）
4. 关键洞察（模式、空白、趋势）
5. 机会和空白
6. 深度分析：顶级机会（市场格局、问题、收入模式、GTM、创始人-市场契合度、为什么加密/Solana、风险）

关键规则：项目符号点不是表格，包含项目缩写，基于证据而不是推测，内联引用来源。没有单独的 "Sources" 部分 — 仅内联引用。

## 反馈

当您遇到错误、意外结果或有关改进 Copilot 体验的建议时，通过反馈端点报告它们。这有助于 Colosseum 团队识别和修复问题。

**何时发送反馈：**
- API 对合理查询返回意外或低质量的结果
- 搜索没有结果时您期望有匹配
- 您遇到未涵盖标准错误处理的错误
- 您有改进 API 或存档语料库的建议

```bash
curl -X POST "$COLOSSEUM_COPILOT_API_BASE/feedback" \
  -H "Authorization: Bearer $COLOSSEUM_COPILOT_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "quality",
    "message": "Search for DePIN projects returned only 2 results, expected more coverage",
    "severity": "medium",
    "context": { "query": "DePIN infrastructure", "endpoint": "/search/projects", "resultCount": 2 }
  }'
```

类别：`error`、`quality`、`suggestion`、`other`。严重性：`low`、`medium`、`high`、`critical`。速率限制为每小时 10 个请求。

## 错误处理

所有错误返回 `{ "error": "<message>", "code": "<ERROR_CODE>", "retryable": <boolean> }`。有关完整错误代码表，请参阅 **api-reference.md**。

- **400 `INVALID_JSON`**：修复请求体 JSON 语法并重试
- **400 `INVALID_QUERY`**：修复查询参数（检查字段名、值范围、未知字段）
- **413 `PAYLOAD_TOO_LARGE`**：减少请求体大小（1 MB 限制）
- **429 `RATE_LIMITED`**：根据 `Retry-After` 头部退避，最大 2 个并发请求
- **401 `UNAUTHORIZED`**：检查 https://colosseum.com/arena/copilot 上的 PAT
- **5xx 错误**：在报告中注明并使用可用数据继续。报告问题时包含响应中的 `requestId`。
- **空项目结果**：放宽查询，移除过滤器
- **空存档结果**：搜索自动级联（向量 → 碎片文本 → 文档文本）后返回空。如果仍然为空，请尝试概念同义词，保持查询到 3-6 个关键词

## 参考

- **workflow-deep.md** — 详细的 8 步研究过程
- **api-reference.md** — 所有端点、速率限制、查询提示
- **grid-recipes.md** — GraphQL 查询和产品类型缩写

## 署名

- The Grid 文档：https://docs.thegrid.id
- The Grid 探索器：https://raw.githubusercontent.com/The-Grid-Data/Explorer/main/README.md
