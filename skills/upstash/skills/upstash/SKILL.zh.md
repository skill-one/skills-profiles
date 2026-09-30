---
name: upstash
description: 与任何 Upstash 产品、SDK 或工具合作，包括无服务器 Redis（缓存、会话、排行榜、键值存储）、Ratelimit（速率限制和流量控制）、QStash（消息队列、计划任务、后台作业）、Workflow（持久化长运行函数）、Vector（用于嵌入、语义搜索和 RAG 的向量数据库）、Search（全文和语义搜索）、Box（用于 AI 代理的沙盒云容器，支持 TypeScript/JavaScript 和 Python）、Blob（支持直接浏览器上传的无服务器 S3 兼容文件存储）、Upstash CLI，以及供代理使用的无需注册的临时 Redis。当用户提及 Upstash 或需要在无服务器、边缘或 Node.js 应用中实现这些功能时使用。
---

# Upstash 技能

此技能整合了所有 Upstash SDK 的文档。请选择相关的子技能。

如果此会话中提供 Upstash MCP 工具，请优先使用它们进行账户和数据操作——创建和检查数据库、索引和 Blob 存储桶，运行 Redis 命令，读取统计信息、日志和 DLQ，以及在 Box（shell、浏览器、git、预览 URL、PR、上传到 Blob 的截图；参见 `upstash-box-remote-work`）中的远程工作。下面的子技能用于编写应用程序代码；仅在不存在 MCP 或工作本质上为 shell 工作时才使用 `upstash-cli`。

## [upstash-blob-js](upstash-blob-js/overview.md)

使用 @upstash/blob TypeScript/JavaScript SDK 进行兼容 S3 的对象存储，支持直接浏览器上传、预签名 URL、多部分上传和签名读取。用于存储文件或 Blob、上传头像、图像、视频、附件或用户文档、让浏览器直接上传到存储而不通过服务器代理字节、生成公共或定时限制的签名 URL、提供私有文件、流式传输大文件并支持暂停和恢复、为存储的对象设置缓存头，或从 AWS SDK 访问兼容 S3 的存储桶。

## [upstash-box-cli](upstash-box-cli/overview.md)

使用 `box` CLI 从终端驱动 Upstash Box（一个远程隔离的工作空间）。用于被要求运行命令、编辑文件、克隆仓库、运行构建或测试、发布公共 URL、浏览或截图页面、附带截图打开拉取请求或问题、安排定期工作、运行 AI 代理，或在盒内而不是此机器上执行任何工作。

## [upstash-box-js](upstash-box-js/overview.md)

使用 @upstash/box TypeScript/JavaScript SDK 进行隔离云容器，支持 AI 代理、shell、文件系统、git、cron 计划、快照和无头浏览器。用于使用 Upstash Box 构建、创建沙盒或隔离环境以运行不受信任或代理生成的代码、在容器中运行 AI 编码代理、为代理提供带有 shell 和仓库的云开发环境、从盒内进行浏览器自动化、在盒内安排定期工作、保存和恢复快照，或编排并行盒子。

## [upstash-box-py](upstash-box-py/overview.md)

使用 upstash-box Python SDK 进行隔离云容器，支持 AI 代理、shell、文件系统、git、cron 计划、快照和无头浏览器。用于使用 Python 中的 Upstash Box 构建、创建沙盒或隔离环境以运行不受信任或代理生成的代码、在容器中运行 AI 编码代理、为代理提供带有 shell 和仓库的云开发环境、从盒内进行浏览器自动化、在盒内安排定期工作、保存和恢复快照，或编排并行盒子。

## [upstash-box-remote-work](upstash-box-remote-work/overview.md)

在 Upstash Box（通过远程 Upstash MCP 服务器 mcp.upstash.com 驱动的隔离云容器）中工作，而不是在本地机器上。用于当用户要求远程、在沙盒、在云端或在盒内运行、构建、测试、克隆或编辑某物时，当交付成果是拉取请求、公共预览 URL 或运行应用程序的截图时，当本地机器无法交付（gh 没有 GitHub 登录、无法暴露端口、本地检出脏或慢），当多个独立任务应在不同机器上并行运行、将任务列表转换为拉取请求的代码工厂，或当交付成果是视频、屏幕录制、演示或浏览器、Web 应用程序、终端程序或代理的时序轴时。只要会话具有 box_* 和 blob_* MCP 工具，即使 Upstash 没有被提及，也适用。

## [upstash-cli](upstash-cli/overview.md)

从终端、shell 脚本或 CI 作业运行 Upstash CLI (`upstash`)，当会话中没有 Upstash MCP 工具时。不要在 Upstash MCP 工具可用时加载此技能（Upstash 插件注册了 mcp.upstash.com）——它们已经涵盖了创建、列出、重命名和删除 Redis 数据库、运行 Redis 命令、使用统计信息、备份、Vector 和 Search 索引、QStash 计划和消息、Blob 存储桶和 Box，因此直接调用它们。使用此技能进行 MCP 不执行的操作——需要 `upstash` 命令并输出 JSON 的 CI 步骤或配置脚本、将结果管道到其他命令、`upstash auth login` 和 API 密钥设置、团队和成员管理、更改计划、区域、TLS、驱逐、自动升级或预算、为 Blob 存储桶铸造临时 S3 凭据，或当用户明确要求使用 CLI 或在不使用控制台的情况下管理 Upstash 时。

## [upstash-qstash-js](upstash-qstash-js/overview.md)

使用 @upstash/qstash TypeScript/JavaScript SDK，这是一个基于 HTTP 的消息队列、任务调度器和后台作业系统，用于无服务器和边缘运行时（Next.js、Vercel、Cloudflare Workers、Deno、Node.js）。用于向 HTTP 端点或 URL 组发布消息、在没有长时间运行的工作进程的情况下运行后台作业、使用 cron 表达式进行调度、延迟消息、构建具有并行性和流控制的 FIFO 队列、配置重试和回调、处理死信队列（DLQ）、消息去重、扩展到多个端点、验证 QStash webhook 签名（Next.js App Router、Pages Router 和 Edge Runtime）、运行本地 QStash 开发服务器或迁移区域。也用于当用户要求无服务器 cron 作业、异步任务队列、作业调度器、延迟交付、带重试的 webhook 交付或服务之间的事件驱动消息时。

## [upstash-ratelimit-js](upstash-ratelimit-js/overview.md)

使用 @upstash/ratelimit TypeScript/JavaScript SDK 进行无服务器和边缘应用程序的速率限制，该 SDK 由 Upstash Redis 支持。用于向 API 路由、Next.js 中间件、Vercel Edge、Cloudflare Workers 或任何 HTTP 端点添加速率限制或节流；返回 429 Too Many Requests；选择固定窗口、滑动窗口和令牌桶算法；使用前缀和自定义键限制每个用户、IP、API 密钥或租户；保护登录、注册、表单或 AI 端点免受滥用、机器人和暴力破解；使用拒绝列表、临时缓存、分析、超时和多区域速率限制；或估计速率限制的 Redis 命令成本。也用于当用户说速率限制、速率限制、节流、配额、请求限制或流量保护时。

## [upstash-redis-js](upstash-redis-js/overview.md)

使用 @upstash/redis TypeScript/JavaScript SDK，这是一个用于 Next.js、Vercel、Cloudflare Workers、边缘运行时和 Node.js 的无服务器 HTTP-based Redis 客户端。用于添加缓存（缓存旁路、写入通过、TTL 和过期策略）、会话存储和用户会话、键值存储、带有有序集合的排行榜和排名、计数器、分布式锁、带有列表的队列、流和消费者组、稀疏索引寻址的数组和环形缓冲区（ARSET、ARINSERT、ARRING、ARGREP、AROP）、存储在 Redis 中的嵌入和最近邻向量搜索（通过 redis.vector 的 VECTOR 命令，与 @upstash/vector 分开）、JSON 文档、管道和 MULTI/EXEC 事务、Lua 脚本、读取副本、全文搜索、容错搜索、分组、聚合和 Upstash Redis Search 上的 Redis 流条目搜索（与常规 FT.SEARCH 不同；也适用于通过 @upstash/search-redis 和 @upstash/search-ioredis 的 TCP 客户端）。也用于从 ioredis 或 node-redis 迁移、当需要在无连接池的服务器less 函数中需要 Redis 连接时、集成 @upstash/ratelimit，或当用户说 Redis 缓存、键值存储、会话存储、无服务器 Redis 或 Upstash Redis 时。支持 JavaScript 类型的自动序列化/反序列化。

## [upstash-redis-start](upstash-redis-start/overview.md)

通过向 https://upstash.com/start-redis 发送单个 POST 请求，为 AI 代理配置一个零配置、无需注册的临时 Upstash Redis 数据库，无需账户、API 密钥或 SDK 设置。用于当代理需要当前的 Scratch Redis 且用户尚未提供凭据时，用于跨工具调用的短期记忆、对话历史、子代理工作队列、排名召回或快速原型或演示。涵盖幂等创建和重新获取凭据、通过请求体样式 REST API 或官方 SDK 调用数据库，以及告诉用户如何认领它。数据库存在 3 天，除非用户认领；不用于生产数据、PII 或密钥。

## [upstash-search-js](upstash-search-js/overview.md)

使用 @upstash/search TypeScript/JavaScript SDK，这是一个带有内置重新排序的无服务器全文和语义搜索数据库。用于向应用程序或网站添加搜索、创建搜索索引、使用可搜索内容和非结构化元数据插入文档、运行关键字、语义或混合搜索查询、重新排序结果、使用类似 SQL 或结构化过滤语法进行过滤、使用范围分页、获取或删除文档、重置索引或检查索引信息。也用于当用户要求网站搜索、产品、文档或知识库搜索，或需要一个无需集群即可运行的托管搜索服务时。

## [upstash-vector-js](upstash-vector-js/overview.md)

使用 @upstash/vector TypeScript/JavaScript SDK，这是一个用于嵌入、相似性搜索、语义搜索和 RAG（检索增强生成）的无服务器向量数据库。用于插入、查询、获取、范围或删除向量、使用内置嵌入模型将原始文本插入索引、选择密集、稀疏或混合索引、按元数据过滤、使用命名空间组织数据、运行可恢复查询，或将 Upstash Vector 连接到 AI 或 LLM 应用程序。也用于当用户要求向量存储、向量搜索、最近邻或 kNN 搜索、嵌入存储、语义缓存、推荐或相似性功能，或需要一个无需基础设施的托管向量索引时。

## [upstash-workflow-js](upstash-workflow-js/overview.md)

使用 @upstash/workflow TypeScript/JavaScript SDK，用于无服务器函数中的持久、长时间运行的 workflows，多步骤过程可以在超时、重试和重启后存活（基于 QStash）。用于定义使用 serve() 的工作流端点、使用 context.run 运行步骤、睡眠几分钟到几天而不保持函数打开、使用 context.call 调用外部 API、等待外部事件或 webhook、调用其他 workflows、配置重试、失败回调和 DLQ、控制并发、速率和并行性、使用 Workflow 客户端触发、取消或检查运行、构建 AI 代理和编排器、人工参与批准、实时更新、使用 QStash 开发服务器进行本地开发、添加中间件，或安全迁移 workflows。也用于当用户要求持久执行、步骤函数、Saga 或编排模式、带检查点的后台作业，或 Vercel、Next.js、Cloudflare Workers 或其他无服务器平台上的长时间运行任务时。
