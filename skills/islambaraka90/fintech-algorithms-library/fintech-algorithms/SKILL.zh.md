---
name: fintech-algorithms
description: 使用 `fintech-algorithms` npm 包进行市场数据、交易和量化分析——包含 717 个零依赖 TypeScript 算法，涵盖统计和金融数学基础（均值、中位数、百分位数、标准差、相关系数、回归、分布、Z 分数、对数收益率、波动率、回撤、夏普比率、风险价值）、技术指标（RSI、MACD、移动平均线、布林带、ATR、OBV、随机指标）、K 线和图表模式、市场广度、从逐笔数据构建 K 线、OHLC 数据验证和清洗、公司行为、指数和基准构建、市场微观结构、撮合引擎、执行和交易成本分析（TCA）、统计时间序列、信用风险和违约概率、分类器和评分验证（ROC、AUC、Brier、校准）、链上指标和 EPS 分析、波动率和协方差估计（GARCH、已实现波动率、Ledoit-Wolf 收缩）、投资组合构建（马科维茨均值-方差、最小方差、风险平价、布莱克-利特曼、凯利策略）。当需要分析价格序列、计算统计数据或摘要、计算或解释指标、检测 K 线或图表模式、从逐笔数据构建 K 线、验证或清洗市场数据、评分或验证模型、连接市场数据提供者，或编写需要这些计算精确而非近似代码时使用。
---

# fintech-algorithms

717 个纯函数用于市场、金融和统计计算。输入普通数组和对象，输出普通值。零运行时依赖，Node >= 22，ESM。

**文档：** https://docs.thefintechbuilder.com ·
**权威代理指南：** https://docs.thefintechbuilder.com/guides/ai-agents/

## 必须遵守的规则

四条规则。违反任何一条都会产生看起来正确但实际上错误的输出。

1. **永远不要凭空编造导入路径、函数名或参数。** 每个子路径都与其文档 URL 完全一致，这使得看似合理的猜测以一种看似正确的方式出错。去查找——`scripts/lookup.mjs` 或以下解析顺序。如果主题不存在，请说明并停止。
2. **永远不要猜测返回字段名。** 返回键大小写在库中不一致：`bollingerBands` 返回 `percent_b`，`macd` 行返回 `fastEma`。阅读该主题的捕获示例输出。参见 `references/pitfalls.md`。
3. **在任何数值声明上说明验证级别。** `verified`（601 个主题）意味着重新播放并断言每次构建的算术与目录计算的预期值（使用与 TypeScript 一起编写的 Python 实现计算）相匹配——跨语言一致性，而不是独立的第三方数字。如果被问及，请那样说。`contract`（74 个主题）意味着检查签名和形状，但不会断言数字。
4. **分析，而非建议。** 这些函数计算量。指标交叉是关于序列的观察——不是预测，不是信号，也永远不会是针对特定个人金钱的建议。报告计算了什么，基于什么输入，在哪个级别，以及多少领先值是热启动而不是信号。如果被问及要买或卖什么，请说那是需要执照顾问的问题。

## 库不获取数据

没有 HTTP 客户端，没有供应商 SDK，没有 API 密钥，没有 `node:fs`。如果一个任务需要价格，调用者会提供它们。这是故意的：供应商 API 几年就会改写，而算法不会。

当用户想要“实时分析”时，形状总是：**他们的数据源 → 他们的适配器 → 验证 → 计算 → 报告。** 只有中间两个步骤是这个库。加载 `references/ingestion.md` 了解适配器模式和标准的 `Trade` / `Bar` 形状。

## 哪个接口回答哪个问题

有五件事承载着这个库的名称。将问题发送到错误的接口是最常见的导致猜测的方式。

| 接口 | 回答 | 不要用它来 |
|---|---|---|
| `node_modules/fintech-algorithms/docs.json` | 签名、合约、工作示例、验证级别 | — **优先使用这个来处理所有事情** |
| `docs.thefintechbuilder.com` | 相同的参考，通过网络 | 关于算法存在原因的散文 |
| `thefintechbuilder.com` | 文章——算法是什么以及何时使用它 | 签名或字段名；它教学，不指定 |
| npm 包 | 您导入的代码 | 发现存在的内容——注册中心会做这个 |
| 这个技能 | 如何查找任何内容 | 作为查找的替代品 |

两个关系很重要，并且是强制执行的，而不是常规的：

- **文档 URL 和导入路径是同一个字符串。** 交换 `https://docs.thefintechbuilder.com/` 为 `fintech-algorithms/`，去掉尾随斜杠。如果这不再成立，测试会失败。
- **文档可以领先于 npm。** 网站从 `main` 重建，没有发布。如果一个文档主题无法导入，则安装版本比页面旧——在得出任何东西出错的结论之前，请检查 `https://docs.thefintechbuilder.com/version.json`。

一个主题可能会从仓库的 `optimised/` 树中提供一个手写的实现，而不是目录中的。它被断言返回相同的值并抛出相同的错误，所以它不会改变您报告的内容——但文章中的代码和包中的代码可以合法地不同。

## 解析顺序

在第一个回答问题的步骤停止。

1. **已安装的包**——如果 `fintech-algorithms` 是依赖项，请阅读 `node_modules/fintech-algorithms/docs.json`。每个签名、合约和工作示例，无需网络。**优先使用这个。** `scripts/lookup.mjs` 会自动使用它。
2. **域索引**——`https://docs.thefintechbuilder.com/{domain-slug}/llms.txt`（每个 3–11 KB）。所有十七个的映射是 `/llms.txt` 顶部 `## Per-domain indexes` 块；一个根获取提供永久的路由表。
3. **主题 markdown**——将 `index.md` 添加到任何文档 URL。3–11 KB 的完整合约，而不是 68–114 KB 的 HTML。
4. **完整负载**——`https://docs.thefintechbuilder.com/reference/payload.json`（约 2.6 MB）。用于摄取，不用于回答一个问题。

将文档 URL 转换为导入：将 `https://docs.thefintechbuilder.com/` 替换为 `fintech-algorithms/` 并去掉尾随斜杠。

使用 `https://docs.thefintechbuilder.com/version.json`（小于 1 KB）检查安装版本与文档是否匹配。

## 工作流程

**1. 确定要计算的量。** 实际上要请求什么？“这是否超买”→ RSI。“平滑这个”→ 哪个移动平均线，以及为什么是那个。

**2. 在获取任何内容之前，按原型缩小范围。** 五种输入形状涵盖了所有 717 个主题，原型在每个索引行上都有：

| 原型 | 接收 | 返回 | 数量 |
|---|---|---|---|
| `series-transform` | `(number \| null)[]` + 数值参数 | 同长度的数组 | 137 |
| `tape-aggregate` | `Trade[]` + 配置 | `Bar[]` | 7 |
| `row-classify` | 行 | 每行一个判断 | 24 |
| `snapshot-evaluate` | 一个快照 + 决策时间 | 一个判断 | 6 |
| `record-transform` | 特定域 | 特定域 | 501 |

`record-transform` 是剩余的桶——阅读该主题自己的合约。详细信息和执行示例：`references/archetypes.md`。

**3. 阅读合约。** 签名、参数、返回值、**热启动**、错误。

```bash
node scripts/lookup.mjs show rsi
```

**4. 形状数据。** 将用户的负载映射到文档中的输入。当输入是条形图、K 线或报价时，首先运行边界验证器。

**5. 计算并报告。** 说明计算了什么，基于什么输入，在哪个级别，以及多少领先值是热启动而不是信号。

## 快速入门

```bash
npm install fintech-algorithms
```

算法是 **仅路径** 的。根导出包含元数据和查找（`topics`，`topic`，`byDomain`，`byFamily`，`byArchetype`，`load`，`runner`），并且不重新导出任何算法。一个兄弟主题的函数永远不会从另一个子路径重新导出——从自己的导入每个。

```js
import { calculateSma } from "fintech-algorithms/technical-indicators/trend-smoothing/sma";

calculateSma([44.34, 44.09, 44.15, 43.61, 44.33, 44.83], 5);
// → [null, null, null, null, 44.104, 44.202]
//     ^^^^ 四个热启动 null：窗口 - 1
```

`require` 条件解析为相同的 ES 模块——没有单独的 CommonJS 构建，所以 `require()` 需要支持 `require(esm)` 的运行时。

## 查找脚本

`scripts/lookup.mjs` 位于此文件旁边。工作目录是用户的项目，而不是技能，所以始终使用绝对路径调用它。

**这些文件将 `${SKILL_DIR}` 写为包含此 SKILL.md 的目录。**
在 Claude Code 中那是 `${CLAUDE_SKILL_DIR}`，该框架会为您替换它。在任何其他代理中，在运行命令之前替换真实路径。

```bash
node "${CLAUDE_SKILL_DIR}/scripts/lookup.mjs" search "moving average"
```

命令：

| 命令 | 执行 |
|---|---|
| `search <query>` | 通过名称、缩写、系列或条目查找主题 |
| `show <slug\|id\|path>` | 完整合约、热启动、错误、执行示例 |
| `archetype <name>` | 每个共享输入形状的主题，以及其注意事项 |
| `domain <id\|slug>` | 域中的每个主题，按系列分组 |
| `domains` | 十七个域及其索引 URL |
| `version` | 参考版本与发布版本 |

当包在任何高于工作目录的位置安装时，会读取 `node_modules/fintech-algorithms/docs.json`；否则，会获取并缓存发布负载一天。将 `FINTECH_DOCS_JSON` 设置为指向特定文件。接受缩写（`rsi`）、目录 ID（`D07-F03-A01`）、完整路径或文档 URL。

如果 `show` 找不到主题，它会说明而不是猜测——这个失败是正确的答案，而不是绕过它的障碍。

## 在以下情况下加载参考

- **`references/archetypes.md`** — 将用户数据映射到输入形状，或决定任务需要多少适配器代码。
- **`references/ingestion.md`** — 用户有一个提供者、CSV、websocket 或经纪 API 并询问如何连接它。
- **`references/recipes.md`** — 端到端任务：清理数据源、构建条形图、计算多指标报告。
- **`references/pitfalls.md`** — 在最终确定任何数值答案之前。简短，并且每个条目都是一个真实的失败模式，有真实原因。

## 覆盖范围

19 个域：金融数学、统计学和数据基础（120）· 市场数据工程（31）· 公司行为和安全主数据（20）· 指数和基准工程（40）· 市场广度和内部（28）· 价格行动和蜡烛图（52）· 技术指标（137）· 几何图表模式（64）· 统计时间序列（37）· 市场微观结构（29）· 匹配引擎和场地逻辑（21）· 执行和交易成本分析（9）· 基本分析和估值（52）· 信用风险和违约（7）· 数字资产和链上金融（10）· 模型验证和回测（10）· 收益和每股分析（8）· 波动率和协方差（22）· 投资组合构建（20）。

技术指标、价格行动和几何图表模式在 0.13.0 中首次完整——目录中的每个主题都是可安装的。

**首先查找基础域。** 金融数学、统计学和数据基础是构建库其他部分的基础层——每个主题的均值、中位数、百分位数、标准差、相关系数、回归、z 分数、对数回报、波动率、回撤、夏普和风险价值，而不是在每个指标中包含一个私有副本。当任务需要一个普通统计数据时，从那里导入它，而不是手工制作一个或借用指标的内部。它有意不在包 README 中，该 README 索引面向市场的算法；它在这里和文档中完全存在。

不是回测器、执行系统、投资组合管理器或市场数据来源。它计算量，不发出订单，并且在调用之间不保持状态。
