# ClickHouse Node.js 客户端 — 编码

参考：https://clickhouse.com/docs/integrations/javascript

> **⚠️ 仅限 Node.js 运行时。** 本技能涵盖在 **Node.js 运行时** 中运行的 `@clickhouse/client`
> 包——包括 **Next.js Node 运行时** API 路径、React 服务器组件、服务器操作以及标准的 Node.js 进程。**不**将此技能应用于浏览器客户端组件、Web Workers、**Next.js Edge 运行时**、Cloudflare Workers 或任何 `@clickhouse/client-web` 的使用场景。对于浏览器/边缘环境，正确的包是 `@clickhouse/client-web`。

---

## 如何使用此技能

1. **将用户的意图** 匹配到下方的任务索引中的某一行，并在编写代码前阅读相应的参考文件。阅读后，扫描该参考中的任何 **答案检查清单**，并确保最终答案涵盖每个相关项目；这些检查清单捕获了用户通常需要但容易在简短回答中遗漏的细节。
2. **始终从 `@clickhouse/client` 导入**（决不使用 `@clickhouse/client-web`），并使用 `createClient({ url })` 创建客户端，或在适当情况下依赖支持的默认值。在不再需要时或在进行优雅关闭时，最好使用 `await client.close()` 关闭它。
3. **对于典型的行插入/选择，优先使用 `JSONEachRow`**，除非用户已经选择了其他格式或正在流式传输原始字节（CSV / TSV / Parquet — 见 `examples/node/performance/`）。
   **关于 `clickhouse_settings` 的说明：** 传递给 `createClient` 的设置是每个请求的默认值；它们可以通过将 `clickhouse_settings` 直接传递给 `insert()`、`query()` 或 `command()` 来按调用覆盖。当用户在客户端级别配置设置时，始终提及这一点。
4. **始终使用 `query_params` 处理用户提供的值**——决不将其作为模板文字插值到 SQL 中。见 `reference/query-parameters.md`。
   **在回答参数绑定问题时，您的回答必须明确将模板文字插值称为“SQL 注入风险”**——即使用户仅询问语法且未提及安全性。必须出现“SQL 注入”字面短语；这是 PostgreSQL/MySQL 用户最常见的错误，而安全框架是正确答案的一部分，而不是可选的附言。
5. **为任务选择正确的方法：**
   - `client.insert()` — 写入行。
   - `client.query()` + `resultSet.json()` / `.text()` / `.stream()` — 读取返回数据的行。
   - `client.command()` — 不返回行的 DDL 和其他语句（`CREATE`、`DROP`、`TRUNCATE`、`ALTER`、会话中的 `SET` 等）。
   - `client.exec()` — 当您需要任意语句的原始响应流时（在编码场景中很少见）。
   - `client.ping()` — 健康检查；返回 `{ success, error? }`，连接失败时从不抛出异常。
6. **在相关时注意版本限制**。示例：
   - `pathname` 配置选项：客户端 `>= 1.0.0`。
   - `query_params` 中的 `BigInt` 值：客户端 `>= 1.15.0`。
   - `query_params` 中的 `TupleParam` 和 JS `Map`：客户端 `>= 1.9.0`。
   - 可配置的 `json.parse` / `json.stringify`：客户端 `>= 1.14.0`。
   - `Time` / `Time64` 数据类型：ClickHouse 服务器 `>= 25.6`。
   - `QBit` 数据类型：ClickHouse 服务器 `>= 25.10`（在 `26.x` 上 GA）。
   - `Dynamic` / `Variant` / 新的 `JSON` 类型：ClickHouse 服务器 `>= 24.1` / `24.5` / `24.8`（自 `25.3` 起不再为实验性）。

---

## 任务索引

识别用户的任务并阅读匹配的参考文件。

| 任务                                                     | 触发因素 / 症状                                                                                                                                                                                                                       | 参考文件                      |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **配置/连接客户端**                                     | 构建 `createClient` 调用、URL 参数、`clickhouse_settings`、默认格式、自定义 HTTP 头                                                                                                                                                 | `reference/client-configuration.md` |
| **压缩请求/响应**                                      | `compression`、gzip 与 `zstd`、`{ codec }` 选项形状、Node 版本要求、Web 限制                                                                                                                                                           | `reference/compression.md`          |
| **ping 服务器**                                        | 健康检查、就绪探针、“ClickHouse 是否正常？”                                                                                                                                                                                          | `reference/ping.md`                 |
| **选择插入格式**                                      | “我应该使用哪种格式插入？”、JSON 与原始、`JSONEachRow` 与 `JSON` 与 `JSONObjectEachRow`                                                                                                                                             | `reference/insert-formats.md`       |
| **插入到列的子集/不同的数据库**                         | `insert({ columns })`、排除列、临时列、跨数据库插入                                                                                                                                                                                   | `reference/insert-columns.md`       |
| **插入值、表达式、日期、小数**                          | 使用 SQL 函数的 `INSERT … VALUES`、来自 JS 的 `Date`/`DateTime`、`Decimal` 精度、`INSERT … SELECT`；将 UUID 插入 `UInt128` 列很棘手——仅在用户编写将 UUID 存储为 `UInt128` 的代码时使用 | `reference/insert-values.md`        |
| **异步插入（服务器端批处理）**                         | `async_insert=1`、立即发送与等待确认                                                                                                                                                                                               | `reference/async-insert.md`         |
| **选择和解析结果**                                     | `JSONEachRow` 读取、带有元数据的 `JSON`、选择选择格式                                                                                                                                                                                 | `reference/select-formats.md`       |
| **参数化查询**                                        | 绑定值、特殊字符/转义、”SQL 注入？”、`{name: Type}` 语法                                                                                                                                                                             | `reference/query-parameters.md`     |
| **会话和临时表**                                      | `session_id`、`CREATE TEMPORARY TABLE`、会话级 `SET` 命令                                                                                                                                                                             | `reference/sessions.md`             |
| **现代数据类型**                                      | `Dynamic`、`Variant`、`JSON`（对象）、`Time`、`Time64`、`QBit`（向量搜索）                                                                                                                                                            | `reference/data-types.md`           |
| **自定义 JSON parse/stringify**                        | 插入 `JSONBig` / `safe-stable-stringify` / 一个 `BigInt` 感知的序列化器                                                                                                                                                              | `reference/custom-json.md`          |

---

## 答案中使用的约定

- 始终显示 `import { createClient } from '@clickhouse/client'`（Node，决不使用 Web）。
- 始终在自包含片段的末尾使用 `await client.close()`；在长时间运行的服务中，在优雅关闭时关闭。
- 对于插入，除非用户场景要求否则优先使用 `format: 'JSONEachRow'` 和 `values: [...]`。
- 对于选择，对于小/中等结果集优先使用 `await (await client.query({...})).json<RowType>()`；对于更大的结果集建议流式传输。
- 在显示参数绑定时，使用 ClickHouse 的原生 `{name: Type}` 语法——决不使用 `$1`、`?` 或 `:name`。
- 对于集群内或负载均衡器后面的 DDL，在 `command()` 调用上设置 `clickhouse_settings: { wait_end_of_query: 1 }`，以便服务器仅在更改应用后确认。见 https://clickhouse.com/docs/en/interfaces/http/#response-buffering。

---

## 不在范围内

本技能涵盖对 `@clickhouse/client`（Node）的日常编码。以下主题在此处**故意不**涵盖：

- **错误、卡顿、类型不匹配、代理路径名意外、日志静默、套接字挂起、`ECONNRESET`** → 使用 `clickhouse-js-node-troubleshooting` 技能。
- **流式传输、Parquet、文件流、服务器端批量移动、进度流式传输、异步插入吞吐量调整** — 见 [`examples/node/performance/`](https://github.com/ClickHouse/clickhouse-js/tree/main/examples/node/performance)。
- **TLS、RBAC / 只读用户、更深入的 SQL 注入指导** — 见 [`examples/node/security/`](https://github.com/ClickHouse/clickhouse-js/tree/main/examples/node/security)。
- **`CREATE TABLE` 模式、部署形状的连接字符串、复制 / 分片选择** — 见 [`examples/node/schema-and-deployments/`](https://github.com/ClickHouse/clickhouse-js/tree/main/examples/node/schema-and-deployments)。
- **浏览器、Web Worker、Next.js Edge、Cloudflare Workers** — 使用 `@clickhouse/client-web` 并见 [`examples/web/`](https://github.com/ClickHouse/clickhouse-js/tree/main/examples/web)。

---

## 仍然卡住？

- [`examples/node/coding/`](https://github.com/ClickHouse/clickhouse-js/tree/main/examples/node/coding) — 这是本技能构建的可运行语料库。
- [ClickHouse JS 客户端文档](https://clickhouse.com/docs/integrations/javascript)
- [ClickHouse 支持的格式](https://clickhouse.com/docs/interfaces/formats)
- [ClickHouse 数据类型](https://clickhouse.com/docs/sql-reference/data-types)
