# Upstash 技能

此技能整合了所有 Upstash SDK 的文档。请选择下方的相关子技能。

如果此会话中提供 Upstash MCP 工具，请优先使用它们进行账户和数据操作——创建和检查数据库、索引和 Blob 存储桶，运行 Redis 命令，读取统计信息、日志和死信队列 (DLQ)，以及在 Box（shell、浏览器、git、预览 URL、PR、上传到 Blob 的截图；参见 `upstash-box-remote-work`）。下方的子技能用于编写应用程序代码；仅在不存在 MCP 或工作本质上为 shell 工作时才使用 `upstash-cli`。

## [upstash-blob-js](upstash-blob-js/overview.md)

使用 @upstash/blob TypeScript/JavaScript SDK 进行兼容 S3 的对象存储，支持直接浏览器上传、预签名 URL、分片上传和签名读取。在存储文件或 Blob、上传头像、图像、视频、附件或用户文档、允许浏览器直接上传到存储而不通过服务器代理字节、生成公共或定时限制的签名 URL、提供私有文件、流式传输大文件（支持暂停和恢复）、为存储对象设置缓存头，或从 AWS SDK 访问兼容 S3 的存储桶时使用。

## [upstash-box-cli](upstash-box-cli/overview.md)

使用 `box` CLI 从终端驱动 Upstash Box（一个远程隔离的工作区）。在需要运行命令、编辑文件、克隆仓库、运行构建或测试、发布公共 URL、浏览或截图页面、附带截图打开 PR 或问题、安排定期工作、运行 AI 代理，或在 Box 内而不是此机器上执行任何工作时使用。

## [upstash-box-js](upstash-box-js/overview.md)

使用 @upstash/box TypeScript/JavaScript SDK 进行隔离云容器，支持 AI 代理、shell、文件系统、git、cron 计划、快照和无头浏览器。在构建 Upstash Box、创建沙盒或隔离环境以运行不受信任或代理生成的代码、在容器中运行 AI 编码代理、为代理提供带 shell 和仓库的云开发环境、从 Box 自动化浏览器、在 Box 内安排定期工作、保存和恢复快照，或编排并行 Box 时使用。

## [upstash-box-py](upstash-box-py/overview.md)

使用 upstash-box Python SDK 进行隔离云容器，支持 AI 代理、shell、文件系统、git、cron 计划、快照和无头浏览器。在 Python 中使用 Upstash Box 构建时、创建沙盒或隔离环境以运行不受信任或代理生成的代码、在容器中运行 AI 编码代理、为代理提供带 shell 和仓库的云开发环境、从 Box 自动化浏览器、在 Box 内安排定期工作、保存和恢复快照，或编排并行 Box 时使用。

## [upstash-box-remote-work](upstash-box-remote-work/overview.md)

在 Upstash Box（通过远程 Upstash MCP 服务器 mcp.upstash.com 驱动的隔离云容器）中工作，而不是在本地机器上。在用户要求远程、在沙盒、在云端或在 Box 中运行、构建、测试、克隆或编辑某物时使用；当交付成果是 PR、公共预览 URL 或运行应用程序的截图时；当本地机器无法交付（gh 没有 GitHub 登录、无法暴露端口、本地检出脏或慢）；当多个独立任务应在不同机器上并行运行；一个将任务列表转换为 PR 列表的代码工厂；或当交付成果是视频、屏幕录制、演示或浏览器、Web 应用程序、终端程序或代理运行的快照时。只要会话具有 box_* 和 blob_* MCP 工具，即使未提及 Upstash 也适用。

## [upstash-cli](upstash-cli/overview.md)

从终端、shell 脚本或 CI 任务中运行 Upstash CLI (`upstash`)，当会话中没有 Upstash MCP 工具时。当 Upstash MCP 工具可用时（Upstash 插件注册了 mcp.upstash.com）不要加载此技能——它们已经涵盖创建、列出、重命名和删除 Redis 数据库、运行 Redis 命令、使用统计信息、备份、Vector 和 Search 索引、QStash 计划和消息、Blob 存储桶和 Box，因此直接调用它们。使用此技能进行 MCP 不执行的操作——需要 `upstash` 命令并输出 JSON 的 CI 步骤或配置脚本、将结果管道到其他命令、`upstash auth login` 和 API 密钥设置、团队和成员管理、更改计划、区域、TLS、驱逐、自动升级或预算、为 Blob 存储桶生成临时 S3 凭据，或当用户明确要求使用 CLI 或在不使用控制台的情况下管理 Upstash 时。

## [upstash-qstash-js](upstash-qstash-js/overview.md)

使用 @upstash/qstash TypeScript/JavaScript SDK，这是一个基于 HTTP 的消息队列、任务调度器和后台作业系统，适用于无服务器和边缘运行时（Next.js、Vercel、Cloudflare Workers、Deno、Node.js）。在发布消息到 HTTP 端点或 URL 组、运行后台作业而不需要长时间运行的 worker 进程、使用 cron 表达式进行调度、延迟消息、构建具有并行和流控制的 FIFO 队列、配置重试和回调、处理死信队列 (DLQ)、消息去重、扩展到多个端点、验证 QStash webhook 签名（Next.js App Router、Pages Router 和 Edge Runtime）、运行本地 QStash 开发服务器或迁移区域时使用。当用户要求无服务器 cron 作业、异步任务队列、作业调度器、延迟交付、带重试的 webhook 交付或服务之间的事件驱动消息时也使用。

## [upstash-ratelimit-js](upstash-ratelimit-js/overview.md)

使用 @upstash/ratelimit TypeScript/JavaScript SDK 进行无服务器和边缘应用程序的速率限制，由 Upstash Redis 支持。在向 API 路由、Next.js 中间件、Vercel Edge、Cloudflare Workers 或任何 HTTP 端点添加速率限制或节流；返回 429 Too Many Requests；选择固定窗口、滑动窗口和令牌桶算法；使用前缀和自定义键限制每个用户、IP、API 密钥或租户；保护登录、注册、表单或 AI 端点免受滥用、机器人和暴力破解；使用拒绝列表、临时缓存、分析、超时和多区域速率限制；或估计速率限制的 Redis 命令成本时使用。当用户提到速率限制、速率限制、节流、配额、请求限制或流量保护时也使用。

## [upstash-redis-js](upstash-redis-js/overview.md)

使用 @upstash/redis TypeScript/JavaScript SDK，这是一个适用于 Next.js、Vercel、Cloudflare Workers、边缘运行时和 Node.js 的无服务器 HTTP-based Redis 客户端。在添加缓存（缓存旁路、写穿、TTL 和过期策略）、会话存储和用户会话、键值存储、使用有序集合的排行榜和排名、计数器、分布式锁、使用列表的队列、流和消费者组、稀疏索引寻址的数组和环形缓冲区（ARSET、ARINSERT、ARRING、ARGREP、AROP）、存储在 Redis 中的嵌入和最近邻向量搜索（通过 redis.vector 的 VECTOR 命令，与 @upstash/vector 分开）、JSON 文档、管道和 MULTI/EXEC 事务、Lua 脚本、读取副本、全文搜索、容错搜索、分组、聚合和搜索 Redis 流条目（与普通 FT.SEARCH 不同；也适用于通过 @upstash/search-redis 和 @upstash/search-ioredis 的 TCP 客户端）时使用。在从 ioredis 或 node-redis 迁移时、从无连接池的服务器less 函数中需要 Redis 连接时、集成 @upstash/ratelimit，或当用户提到 Redis 缓存、键值存储、会话存储、无服务器 Redis 或 Upstash Redis 时也使用。支持 JavaScript 类型的自动序列化/反序列化。

## [upstash-redis-start](upstash-redis-start/overview.md)

通过向 https://upstash.com/start-redis 发送单个 POST 请求，为 AI 代理配置零配置、无需注册的临时 Upstash Redis 数据库，无需账户、API 密钥或 SDK 设置。当代理需要立即的 Redis 临时存储且用户未提供凭据时、用于跨工具调用的短期记忆、对话历史、子代理工作队列、排名召回或快速原型或演示时使用。涵盖幂等创建和重新获取凭据、通过请求体风格的 REST API 或官方 SDK 调用数据库，以及告诉用户如何认领它。数据库在用户认领前存在 3 天；不适用于生产数据、PII 或密钥。

## [upstash-search-js](upstash-search-js/overview.md)

使用 @upstash/search TypeScript/JavaScript SDK，这是一个带内置重新排序的无服务器全文和语义搜索数据库。在向应用程序或网站添加搜索、创建搜索索引、使用可搜索内容和非结构化元数据插入文档、运行关键字、语义或混合搜索查询、重新排序结果、使用类似 SQL 或结构化过滤语法进行过滤、分页、获取或删除文档、重置索引或检查索引信息时使用。当用户要求网站搜索、产品、文档或知识库搜索，或需要无集群即可运行的管理搜索服务时也使用。

## [upstash-vector-js](upstash-vector-js/overview.md)

使用 @upstash/vector TypeScript/JavaScript SDK，这是一个用于嵌入、相似性搜索、语义搜索和 RAG（检索增强生成）的无服务器向量数据库。在插入、查询、获取、范围或删除向量、使用内置嵌入模型对索引插入原始文本、选择密集、稀疏或混合索引、按元数据过滤、使用命名空间组织数据、运行可恢复查询，或连接 Upstash Vector 到 AI 或 LLM 应用程序时使用。当用户要求向量存储、向量搜索、最近邻或 kNN 搜索、嵌入存储、语义缓存、推荐或相似性功能，或需要无基础设施的托管向量索引时也使用。

## [upstash-workflow-js](upstash-workflow-js/overview.md)

使用 @upstash/workflow TypeScript/JavaScript SDK，用于无服务器函数中的持久、长时间运行的 workflows，是 QStash 的多步骤过程，可存活超时、重试和重启。在定义使用 serve() 的工作流端点、使用 context.run 运行步骤、暂停几分钟到几天而不保持函数打开、使用 context.call 调用外部 API、等待外部事件或 webhook、调用其他 workflows、配置重试、失败回调和 DLQ、控制并发、速率和并行性、使用 Workflow 客户端触发、取消或检查运行、构建 AI 代理和编排器、人工参与批准、实时更新、使用 QStash 开发服务器进行本地开发、添加中间件，或安全迁移 workflows 时使用。当用户要求持久执行、步骤函数、Saga 或编排模式、带检查点的后台作业，或 Vercel、Next.js、Cloudflare Workers 或其他无服务器平台上的长时间运行任务时也使用。
