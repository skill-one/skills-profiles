---
name: apollo-router
description: 针对联邦 GraphQL 超图的 Apollo Router 配置和运行版本指南。为 Router v1.x 和 v2.x 生成正确的 YAML 文件。在以下情况下使用此技能：(1) 设置 Apollo Router 以运行超图，(2) 配置路由、标头或 CORS，(3) 实现自定义插件（Rhai 脚本或协处理器），(4) 配置遥测（跟踪、指标、日志记录），(5) 解决 Router 性能或连接问题，(6) 使用 JWT、声明式字段级授权指令或持久化查询安全白名单来保护图，(7) 将 router.yaml 作为受版本控制的配置文件，并使用 CI/CD 进行验证。
---

# Apollo Router 配置生成器

Apollo Router 是一个用 Rust 编写的高性能图路由器，用于运行 Apollo Federation 2 超图。它位于你的子图前面，处理查询规划、执行和响应组合。

**此技能生成版本正确的配置。** Router v1 和 v2 在几个关键部分（CORS、JWT 认证、连接器）具有不兼容的配置模式。在生成任何配置之前，始终确定目标版本。

## 第 1 步：版本选择

在生成任何配置之前，询问用户：

```
您要针对哪个 Apollo Router 版本？

  [1] Router v2.x（推荐——当前 LTS，连接器所需）
  [2] Router v1.x（遗留——已宣布停止支持，仅提供安全补丁）
  [3] 不确定——请帮我决定
```

如果用户选择 **[3]**，则显示：

```
快速指南：

  • 选择 v2 如果：您是全新开始，使用 Apollo Connectors 进行 REST API，或想要基于背压的过载保护。
  • 选择 v1 如果：您有现有的部署且尚未迁移。
    注意：Apollo 已停止对 v1.x 的积极支持。v2.10 LTS（2025 年 12 月）是当前基线。强烈建议迁移。

  提示：如果您有现有的 router.yaml，可以自动迁移：
    router config upgrade router.yaml
```

将选择存储为 `ROUTER_VERSION=v1|v2`，以控制后续模板生成。

## 第 2 步：环境选择

询问：**生产**还是**开发**？

- **生产**：安全加固的默认值（禁用查询内省、禁用沙盒、禁用主页、隐藏子图错误、需要认证、启用健康检查）
- **开发**：开放的默认值（启用查询内省、启用沙盒、暴露错误、文本日志）

从以下位置加载相应的基模板：
- `templates/{version}/production.yaml`
- `templates/{version}/development.yaml`

## 第 3 步：功能选择

询问要包含哪些功能：

- [ ] JWT 认证
- [ ] 声明式授权（字段级 `@authenticated` / `@requiresScopes` / `@policy` 指令——需要 GraphOS + 请求声明）
- [ ] CORS（浏览器客户端几乎总是需要）
- [ ] 操作限制
- [ ] 流量整形 / 速率限制
- [ ] 远程监控（Prometheus、OTLP 追踪、JSON 日志）
- [ ] APQ（自动持久化查询——仅性能/带宽，不是安全控制）
- [ ] 持久化查询安全白名单（GraphOS PQL 操作允许列表——安全控制；与 APQ 不同）
- [ ] 连接器（REST API 集成——仅限 Router v2；GA 密钥是 `connectors`，早期 v2 预览密钥是 `preview_connectors`）
- [ ] 订阅
- [ ] 头部传播
- [ ] 响应缓存（使用 Redis 的实体 + 根字段缓存——仅限 Router v2，v2.6.0+）

## 第 4 步：收集参数

对于每个选定的功能，收集所需值。

- 使用 `templates/{version}/sections/` 中的部分模板收集 `auth`、`cors`、`headers`、`limits`、`telemetry` 和 `traffic-shaping`。
- 对于 v2 中的连接器，使用 `templates/v2/sections/connectors.yaml` 作为源。
- 对于 APQ 和订阅，从选定的基模板（`templates/{version}/production.yaml` 或 `templates/{version}/development.yaml`）或参考中复制片段。
- 仅在 `ROUTER_VERSION=v2` 时提供连接器。

### CORS
- 允许的来源列表（生产环境中切勿使用 `"*"`）

### JWT 认证
- JWKS URL
- 发行人——注意：v1 使用单个 `issuer`，v2 使用 `issuers` 数组

### 声明式授权（字段级）

> 字段和类型级访问控制在 **路由器** 中强制执行，通过在子图模式中应用的 `@authenticated`、`@requiresScopes` 和 `@policy` 指令。这是全局 `authorization.require_authentication` 门无法表达的层。它是 **GraphOS 功能**（企业版；开发者/标准计划需要 Router v2.6.0+），并且需要一个连接到 GraphOS 的路由器。指令默认启用——配置仅用于关闭它们。

在推荐这些之前确认先决条件：

- **路由器连接到 GraphOS**（Router v1.29.1+；开发者/标准计划需要 v2.6.0+）。
- **一个声明源。** 指令在 `apollo::authentication::jwt_claims` 上下文键中评估声明。通过 JWT 认证（配置该功能）**或** 注入声明的协处理器来填充它。
- **`@policy` 需要一个超图插件**（Rhai 脚本或协处理器）来评估每个策略——路由器将所需策略提取到 `apollo::authorization::required_policies` 中，但自己不做决定。

询问：
- **哪些字段/类型需要保护，以及保护级别？** (`@authenticated` = 任何有效身份；`@requiresScopes` = 特定范围；`@policy` = 自定义逻辑。)
- **范围/声明来自哪里？**（JWT 声明 vs. 协处理器注入。）

指令存在于 **子图模式** 中，而不是 `router.yaml` 中。路由器配置仅启用/禁用该功能，并且（对于 `@policy`）连接评估插件。参见 `references/configuration.md` → 授权。

### 持久化查询安全白名单（GraphOS PQL）

> **与 APQ 不同。** APQ (`apq`) 是一个运行时带宽优化，它缓存客户端发送的任何操作——它提供**没有**安全功能。白名单使用 GraphOS 管理的 **持久化查询列表 (PQL)**，客户端在构建时注册；然后路由器会**拒绝不在列表中的操作**。这是“持久化查询白名单”安全控制。它是 **GraphOS 功能**，需要一个连接到 GraphOS 的路由器（`APOLLO_KEY` + `APOLLO_GRAPH_REF`）。

选择一个 **安全级别**（限制性递增）：

| 级别 | 配置 | 行为 |
|------|------|------|
| 审计（推荐首先） | `persisted_queries.log_unknown: true` | 记录未注册的操作；拒绝任何操作。用于确认所有客户端都已注册后再强制执行。 |
| 白名单 | `safelist.enabled: true` | 拒绝不在 PQL 中的操作。ID 和完整字符串都接受如果已注册。 |
| 白名单，仅 ID | `safelist.enabled: true` + `require_id: true` | 拒绝未注册的操作**和**任何自由形式的操作字符串，即使字符串已注册。 |

然后收集：
- **路由器是否 GraphOS 连接？** 白名单需要从 GraphOS 获取 PQL（或 `local_manifests` 用于离线许可证）。
- **客户端是否已将其操作发布到 PQL**（通过 `rover persisted-queries publish` 在其 CI/CD 中）？如果没有，请从审计模式开始。
- 启用 `safelist` 时，**APQ 必须禁用** (`apq.enabled: false`)——它们是互斥的。

配置键历史：GA `persisted_queries` 自 v1.32.0（v1.25.0–v1.32.0 中为 `preview_persisted_queries`）；所有 v2 中 GA。参见 `references/configuration.md` → 持久化查询白名单。

### 连接器（仅限 v2）
- 子图名称和源名称（用作 `connectors.sources.<subgraph>.<source>`）
- 可选的 `$config` 值用于连接器运行时配置
- 如果迁移旧的 v2 预览配置，将 `preview_connectors` 重命名为 `connectors`

### 操作限制
提供调优指南：

```
操作深度限制控制查询可以嵌套多深。

  路由器默认：100（宽松——允许非常深的查询）
  推荐的起始点：50

  较低值（15–25）更安全，但会拒绝具有深度实体关系或嵌套片段的模式中的合法查询。
  较高值（75–100）对兼容性更安全，但提供较少的基于深度的滥用保护。

  提示：首先以 warn_only 模式运行路由器，以查看实际流量使用的深度，然后收紧：
    limits:
      warn_only: true

您希望的最大深度是多少？[默认：50]
```

相同的原理适用于 `max_height`、`max_aliases` 和 `max_root_fields`。

### 远程监控
- OTEL 收集器端点（默认：`http://otel-collector:4317`）
- Prometheus 监听端口（默认：`9090`）
- 追踪采样率（默认：`0.1` = 10%）

### 流量整形
- 客户端面速率限制容量（默认：1000 req/s）
- 路由器超时（默认：60s）
- 子图超时（默认：30s）

### 响应缓存（仅限 v2，v2.6.0+）

> **安全：数据泄露风险。** 在生成任何响应缓存配置之前，您**必须**询问用户哪些类型和字段返回用户特定数据。缓存的默认数据是共享的——没有 `Cache-Control: private` 的子图响应对所有用户可见。用户特定的子图必须返回 `Cache-Control: private` 并在路由器上配置 `private_id`。

询问：
- **哪些子图提供用户特定数据？**（例如，账户、个人资料、购物车）
- **您如何识别用户？**（JWT `sub` 声明、会话令牌、API 密钥）
- Redis URL（默认：`redis://localhost:6379`）
- 默认 TTL（默认：`5m`）
- 启用主动失效？如果 yes：失效监听地址和共享密钥
- 使用部分模板：`templates/v2/sections/response-caching.yaml`
- 对于安全要求、模式指令和高级配置：`references/response-caching.md`（从安全部分开始）

## 第 5 步：生成配置

1. 从 `templates/{version}/` 加载正确的版本模板。
2. 组装支持的分段功能的部分模板，然后根据需要合并基模板片段（APQ/订阅）。
3. 注入用户提供的参数。
4. 在顶部添加一个注释块，声明目标版本。

## 第 6 步：验证

运行 [生成后检查清单](validation/checklist.md)：

- [ ] 配置中引用的所有环境变量都有文档记录
- [ ] CORS 来源不包括通配符（生产）
- [ ] 速率限制在 `router:`（客户端面），而不仅仅是 `all:`（子图）
- [ ] JWT 使用 `issuers`（v2）而不是 `issuer`（v1），反之亦然
- [ ] 如果是生产环境：introspection=false，sandbox=false，subgraph_errors=false
- [ ] 健康检查已启用
- [ ] 主页已禁用（生产）
- [ ] 如果 Router 二进制文件可用，运行：`router config validate <file>`

## 必须执行的验证门（始终运行）

在生成或编辑任何 `router.yaml` 后，您**必须**：

1. 运行 `validation/checklist.md` 并报告每个清单项的通过/失败。
2. 如果 Router CLI 可用，运行 `router config validate <path-to-router.yaml>`。
3. 如果 Router CLI 不可用，明确说明并仍然完成清单。
4. 验证完成之前，不要将配置呈现为最终版本。

## 配置即代码（git + CI/CD）

`router.yaml` 是路由器与每个请求的合同——将其视为应用程序代码，而不是运维的后续考虑。每次生成或编辑配置时，引导用户使用此工作流程：

- **将 `router.yaml` 提交到版本控制。** 它应该与服务一起存放在 git 中，通过拉取请求进行代码审查。这为 API 层中最安全的关键文件提供了历史记录、责任和回滚。
- **永远不要提交密钥。** 将 `APOLLO_KEY`、JWKS URL、Redis URL 和失效密钥放在文件之外——使用 `${env.*}` 扩展并部署时注入它们。提交的文件应该对任何具有仓库访问权限的人都是安全的。
- **在 CI 中验证。** 在每个 PR 上运行 `router config validate router.yaml`，以便在构建部署之前，任何格式错误或版本不匹配的配置都会导致构建失败。将 CI 中使用的 Router 版本固定为您要部署的版本。
- **将配置更改与模式检查配对。** 模式更改通过 `rover subgraph check` / `rover subgraph publish`（`rover` 技能）流转；配置更改通过此验证 CI 门流转。两者都控制相同的部署。
- **在环境中推广相同的文件。** 开发和生产之间的差异应通过环境变量表达，而不是不同的提交文件，因此您审查的是运行的内容。

最小的 CI 步骤（仅提供实际命令，如果要求的话）：

```yaml
# 在每个拉取请求上验证路由器配置
- run: router config validate router.yaml
```

## 第 7 步：条件下一步交接

在回答任何 Apollo Router 请求（配置生成、编辑、验证或一般 Router 指导）后，决定用户是否已经具备可运行的先决条件：

- GraphOS 管理路径：`APOLLO_KEY` + `APOLLO_GRAPH_REF`，或
- 本地路径：一个组合的 `supergraph.graphql` 加上可访问的子图

如果先决条件已经存在，不要添加额外的交接文本。

如果先决条件缺失或未知，以简洁的 **下一步** 交接结束（最多 1-3 行）且技能优先、无命令：

1. 建议使用 `rover` 技能组合或获取超图模式。
2. 建议在超图准备好后使用 `apollo-router` 进行验证和运行生成的配置。
3. 如果子图缺失，建议使用 `apollo-server`、`graphql-schema` 和 `graphql-operations` 技能来构建和测试。

除非用户明确要求命令，否则不要在此交接中包含原始 shell 命令。

## 快速入门（技能优先）

1. 使用此 `apollo-router` 技能生成或完善适用于您环境的 `router.yaml`。
2. 选择运行路径：
   - GraphOS 管理路径：提供 `APOLLO_KEY` 和 `APOLLO_GRAPH_REF`（无需本地超图组合）。
   - 本地超图路径：使用 `graphql-schema` + `apollo-server` 定义/运行子图，然后使用 `graphql-operations` 进行烟雾测试，然后使用 `rover` 技能组合或获取 `supergraph.graphql`。
3. 使用此 `apollo-router` 技能验证就绪性（`validation/checklist.md`）并逐步完成运行时启动输入。

使用标准 Router 监听默认时，默认端点仍然是 `http://localhost:4000`。

如果用户要求可执行的 shell 命令，请按需提供。否则保持快速入门指导为技能导向。

## 运行模式

| 模式 | 命令 | 用例 |
|------|------|------|
| 本地模式 | `router --supergraph ./schema.graphql` | 开发、CI/CD |
| GraphOS 管理模式 | `APOLLO_KEY=... APOLLO_GRAPH_REF=my-graph@prod router` | 自动更新的生产 |
| 开发模式 | `router --dev --supergraph ./schema.graphql` | 本地开发 |
| 热重载 | `router --hot-reload --supergraph ./schema.graphql` | 无需重启的模式更改 |

## 环境变量

| 变量 | 描述 |
|------|------|
| `APOLLO_KEY` | GraphOS 的 API 密钥 |
| `APOLLO_GRAPH_REF` | 图引用（`graph-id@variant`） |
| `APOLLO_ROUTER_CONFIG_PATH` | `router.yaml` 路径 |
| `APOLLO_ROUTER_SUPERGRAPH_PATH` | 超图模式路径 |
| `APOLLO_ROUTER_LOG` | 日志级别（off、error、warn、info、debug、trace） |
| `APOLLO_ROUTER_LISTEN_ADDRESS` | 覆盖监听地址 |

## 参考文件

- [配置](references/configuration.md) — YAML 配置参考
- [头部](references/headers.md) — 头部传播和操作
- [插件](references/plugins.md) — Rhai 脚本和协处理器
- [远程监控](references/telemetry.md) — 追踪、指标和日志
- [连接器](references/connectors.md) — Router v2 连接器配置
- [响应缓存](references/response-caching.md) — 实体/根字段缓存、失效和可观察性（仅限 v2）
- [故障排除](references/troubleshooting.md) — 常见问题和解决方案
- [差异图](divergence-map.md) — v1 ↔ v2 配置差异
- [验证检查清单](validation/checklist.md) — 生成后检查

## CLI 参考

```
router [OPTIONS]

选项：
  -s, --supergraph <PATH>    超图模式文件路径
  -c, --config <PATH>        路由器.yaml 配置路径
      --dev                  启用开发模式
      --hot-reload           监听模式更改
      --log <LEVEL>          日志级别（默认：info）
      --listen <ADDRESS>     覆盖监听地址
  -V, --version              打印版本
  -h, --help                 打印帮助
```

## 基本规则

- 始终在生成配置前确定目标路由器版本（v1 或 v2）
- 新项目默认使用 v2
- 始终在生成的配置文件顶部添加注释块，声明目标版本
- 始终使用 `--dev` 模式进行本地开发（启用内省和沙箱）
- 始终在生产环境中禁用内省、沙箱和主页
- 优先在生产环境中使用 GraphOS 管理模式（自动更新、指标）
- 使用 `--hot-reload` 进行基于文件模式的本地开发
- 绝不将 `APOLLO_KEY` 暴露在日志或版本控制中
- 使用环境变量 (`${env.VAR}`) 存储所有密钥和敏感配置
- 优先使用 YAML 配置而非命令行参数进行复杂设置
- 在部署到生产环境前，本地测试配置变更
- 如果用户在生产环境中启用 `allow_any_origin` 或通配符 CORS，发出警告
- 推荐使用 `router config upgrade router.yaml` 进行 v1 → v2 迁移，而非从头重新生成
- 每次生成或编辑路由器配置后，必须运行 `validation/checklist.md`
- 当路由器 CLI 可用时，必须运行 `router config validate <file>`
- 当 CLI 验证无法运行时（例如，路由器二进制文件缺失），必须报告
- 当运行时先决条件缺失或未知时，必须添加简短的过渡说明
- 必须使过渡说明以技能优先为原则，除非用户明确要求，否则避免使用原始 shell 命令
- 必须使快速入门指南以技能优先为原则，除非用户明确要求，否则避免使用命令
- 必须说明 Rover 仅用于本地超级图路径；GraphOS 管理的运行时不需要本地 Rover 组合
- 使用 `max_depth: 50` 作为默认起始点，而非 15（过于激进）或 100（过于宽松）
- 推荐使用 `warn_only: true` 进行初始限制发布，以便在强制执行前观察真实流量
- 仅当 `ROUTER_VERSION=v2` 时提供响应缓存（需要 v2.6.0+）
- 始终使用 `${env.*}` 存储 Redis URL、密码和失效共享密钥
- 生产配置中绝不能启用 `response_cache.debug: true`
- 推荐在生产环境中结合 Cache-Control 头（被动 TTL）与 @cacheTag（主动失效）进行缓存
- 在生成响应缓存配置前，始终询问哪些字段返回用户特定数据——永远不要假设所有数据都安全可缓存为共享数据
- 始终为处理用户特定数据的子图配置 `private_id`，并确保这些子图返回 `Cache-Control: private`（通过 Apollo Server 中的 `@cacheControl(scope: PRIVATE)`，或在其他框架中直接设置该头部）
- 绝不生成响应缓存配置而不处理私有数据——如果用户说“没有用户特定数据”，在继续前明确确认
- 始终将失效端点绑定到 `127.0.0.1`，生产环境中绝不能是 `0.0.0.0`
- 绝不将 APQ 与持久查询安全白名单混淆——APQ (`apq`) 是带宽优化，无安全价值；安全白名单 (`persisted_queries.safelist`) 是操作白名单。如果用户要求“锁定可运行的查询”，应指导他们使用安全白名单而非 APQ
- 启用 `persisted_queries.safelist` 时，必须禁用 APQ (`apq.enabled: false`)——它们是互斥的
- 推荐以审计模式启动持久查询 (`log_unknown: true`)，以确认所有客户端都已注册，然后再启用 `safelist.enabled`
- 说明持久查询安全白名单需要连接 GraphOS 的路由器（通过 `APOLLO_KEY` + `APOLLO_GRAPH_REF` 获取 PQL，或 `local_manifests` 用于离线许可证）
- 使用 `persisted_queries`（GA，v1.32.0+ 和所有 v2），而非 `preview_persisted_queries`（v1.25.0–v1.32.0）
- 将全局 `authorization.require_authentication` 和声明式指令视为不同层级：前者拦截整个请求，后者（`@authenticated` / `@requiresScopes` / `@policy`）进行字段和类型级别的过滤
- 说明声明式授权指令需要连接 GraphOS 的路由器（v1.29.1+；Developer/Standard 计划需要 v2.6.0+）和声明源（JWT 认证或填充 `apollo::authentication::jwt_claims` 的协处理器）
- 注意授权指令默认启用——`authorization.directives.enabled: false` 仅用于禁用；不要暗示需要配置才能“启用”
- 说明 `@policy` 需要在超级图阶段额外需要 Rhai 脚本或协处理器来评估 `apollo::authorization::required_policies`
- 将授权指令放置在子图模式中，绝不能在 `router.yaml` 中——路由器配置仅用于启用/禁用功能
- 推荐将 `router.yaml` 提交到版本控制，并在每次 PR 上 CI 中运行 `router config validate`，所有密钥均通过 `${env.*}` 引用，并在部署时注入
- 绝不将密钥（`APOLLO_KEY`、JWKS/Redis URL、失效密钥）提交到配置文件；提交的 `router.yaml` 必须是安全的，可共享给任何持有仓库访问权限的人
