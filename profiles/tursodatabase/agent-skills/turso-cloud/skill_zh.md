# Turso Cloud 技能

这项技能整合了与 Turso Cloud 一起工作的文档，Turso Cloud 是一个完全托管的兼容 SQLite 的数据库平台。请选择下方的相关子技能。

## [turso-cloud-js](turso-cloud-js/overview.md)

使用 `@tursodatabase/serverless` TypeScript/JavaScript SDK 处理远程 Turso Cloud 数据库 — 查询、位置/命名参数、批处理和交互式事务 — 以及本地优先同步系列 (`@tursodatabase/sync`, `-wasm`, `-react-native`)。在从 Node.js、服务器less/边缘函数、浏览器或 React Native 连接到 Turso Cloud 时使用。

## [turso-cloud-py](turso-cloud-py/overview.md)

从 Python 使用 Turso Cloud：`pyturso` 用于与云端同步的本地优先数据库，以及 `libsql` 用于通过 libsql 协议进行远程仅访问。在将 Python 应用程序连接到 Turso Cloud 时使用。

## [turso-cloud-go](turso-cloud-go/overview.md)

从 Go 使用 Turso Cloud：`tursogo` 用于与云端同步的本地优先数据库，以及 `libsql-client-go` 用于通过 libsql 协议进行远程仅访问。在将 Go 应用程序连接到 Turso Cloud 时使用。

## [turso-cloud-rust](turso-cloud-rust/overview.md)

从 Rust 使用 Turso Cloud：`turso` crate (`sync` 功能) 用于与云端同步的本地优先数据库，以及 `libsql` crate 用于通过 libsql 协议进行远程仅访问。在将 Rust 应用程序连接到 Turso Cloud 时使用。

## [turso-cloud-auth](turso-cloud-auth/overview.md)

验证和授权对 Turso Cloud 数据库的访问：数据库 URL、通过 Turso CLI 的平台令牌、作用域（组/数据库/只读/有时间限制）、细粒度的每表权限、通过 JWKS 的外部认证提供程序（Clerk、Auth0）以及令牌失效。在签发凭证、限制客户端可以做什么或将要现有认证提供程序连接到 Turso 时使用。

## [turso-cloud-vercel](turso-cloud-vercel/overview.md)

使用和管理通过 Vercel Marketplace 提供的 Turso Cloud 数据库（集成 slug `tursocloud`）：注入的环境变量、使用 Vercel CLI 检查和配置资源、区域选择、凭证和破坏性操作的权限规则。在 Vercel 项目具有 — 或需要 — Turso 数据库时使用。

## Turso Cloud 功能

Turso Cloud 数据库开箱即用支持以下功能：

- **向量搜索** — 用于 AI/RAG 工作流的原生相似度搜索，无需扩展。支持使用 DiskANN 索引的余弦、L2 和 L1 距离函数。
- **全文搜索** — 通过内置 FTS 支持的 BM25 排名关键字搜索。
- **AI & 嵌入** — 用于存储和查询嵌入的原生向量类型。
- **分支** — 创建隔离的写时复制数据库分支用于测试/预发布。
- **时间点恢复** — 将数据库恢复到任何先前的时间点（保留取决于计划）。
- **嵌入式副本** — 与 Turso Cloud 同步的本地副本，用于快速读取和离线支持。
- **SQLite 扩展** — JSON、FTS5、R*Tree、SQLean、UUID、regexp。

## 深入阅读

**Turso 在线文档** — `https://docs.turso.tech` (Mintlify — 将 `.md` 添加到任何 URL 路径以获取原始 Markdown，例如 `https://docs.turso.tech/sdk/ts/quickstart.md`)。每个子技能都带有自己的文档链接；一般参考：

| 主题 | URL |
|------|-----|
| AI & 嵌入 | `https://docs.turso.tech/features/ai-and-embeddings.md` |
| 嵌入式副本 | `https://docs.turso.tech/features/embedded-replicas/introduction.md` |
| 云限制 | `https://docs.turso.tech/cloud/limitations.md` |
| SQLite 扩展 | `https://docs.turso.tech/features/sqlite-extensions.md` |
| 完整文档索引（用于 LLM） | `https://docs.turso.tech/llms.txt` |
