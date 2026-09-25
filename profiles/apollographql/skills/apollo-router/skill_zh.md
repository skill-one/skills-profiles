# Apollo Router 配置生成器

Apollo Router 是一个用 Rust 编写的高性能图路由器，用于运行 Apollo Federation 2 超图。它位于你的子图前面，处理查询规划、执行和响应组合。

**此技能生成与版本匹配的配置。** Router v1 和 v2 在几个关键部分（CORS、JWT 认证、连接器）具有不兼容的配置模式。在生成任何配置之前，请始终确定目标版本。

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

  • 选择 v2 如果：您是全新开始、使用 Apollo Connectors 进行 REST API，或需要基于背压的过载保护。
  • 选择 v1 如果：您有现有的部署且尚未迁移。
    注意：Apollo 已停止对 v1.x 的积极支持。v2.10 LTS（2025 年 12 月）是当前基线。强烈建议迁移。

  提示：如果您有现有的 router.yaml，可以自动迁移：
    router config upgrade router.yaml
```

将选择存储为 `ROUTER_VERSION=v1|v2`，以控制后续模板生成。

## 第 2 步：环境选择

询问：**生产**还是**开发**？

- **生产**：安全加固的默认值（关闭内省、关闭沙盒、关闭主页、隐藏子图错误、需要认证、开启健康检查）
- **开发**：开放的默认值（开启内省、开启沙盒、暴露错误、文本日志）

从以下位置加载相应的基模板：
- `templates/{version}/production.yaml`
- `templates/{version}/development.yaml`

## 第 3 步：功能选择

询问要包含哪些功能：

- [ ] JWT 认证
- [ ] 声明式授权（字段级别的 `@authenticated` / `@requiresScopes` / `@policy` 指令——需要 GraphOS + 请求声明）
- [ ] CORS（几乎总是对浏览器客户端是肯定的）
- [ ] 操作限制
- [ ] 流量整形 / 速率限制
- [ ] 远程监控（Prometheus、OTLP 追踪、JSON 日志）
- [ ] APQ（自动持久化查询——仅性能/带宽，不是安全控制）
- [ ] 持久化查询安全列表（GraphOS PQL 操作允许列表——安全控制；与 APQ 不同）
- [ ] 连接器（REST API 集成——仅限 Router v2；GA 密钥是 `connectors`，早期 v2 预览密钥是 `preview_connectors`）
- [ ] 订阅
- [ ] 头部传播
- [ ] 响应缓存（使用 Redis 的实体 + 根字段缓存——仅限 Router v2，v2.6.0+）

## 第 4 步：收集参数

对于每个选定的功能，收集所需值。

- 使用 `templates/{version}/sections/` 中的部分模板来收集 `auth`、`cors`、`headers`、`limits`、`telemetry` 和 `traffic-shaping` 的值。
- 对于 v2 中的连接器，使用 `templates/v2/sections/connectors.yaml` 作为源。
- 对于 APQ 和订阅，从选定的基模板（`templates/{version}/production.yaml` 或 `templates/{version}/development.yaml`）或参考中复制片段。
- 仅在 `ROUTER_VERSION=v2` 时提供连接器。

### CORS
- 允许的来源列表（生产环境中绝对不要使用 `"*"`）

### JWT 认证
- JWKS URL
- 发行人——注意：v1 使用单个 `issuer`，v2 使用 `issuers` 数组

### 声明式授权（字段级别）

> 字段和类型级别的访问控制在 **路由器** 中强制执行，通过在子图模式中应用的 `@authenticated`、`@requiresScopes` 和 `@policy` 指令。这是全局 `authorization.require_authentication` 门无法表达的层。这是一个 **GraphOS 功能**（企业版；开发者/标准计划需要 Router v2.6.0+），并且需要一个连接到 GraphOS 的路由器。指令默认启用——配置仅用于关闭它们。

在推荐这些之前，确认先决条件：

- **路由器连接到 GraphOS**（Router v1.29.1+；开发者/标准计划需要 v2.6.0+）。
- **一个声明源。** 指令在 `apollo::authentication::jwt_claims` 上下文键中评估声明。通过 JWT 认证（配置该功能）**或** 注入声明的协处理器来填充它。
- **`@policy` 需要一个超图插件**（Rhai 脚本或协处理器）来评估每个策略——路由器将所需的策略提取到 `apollo::authorization::required_policies` 中，但不会自行决定它们。

询问：
- **哪些字段/类型需要保护，以及保护级别？**（`@authenticated` = 任何有效身份；`@requiresScopes` = 特定范围；`@policy` = 自定义逻辑。）
- **范围/声明来自哪里？**（JWT 声明 vs. 协处理器注入。）

指令位于 **子图模式** 中，而不是在 `router.yaml` 中。路由器配置仅启用/禁用该功能，并且（对于 `@policy`）连接评估插件。参见 `references/configuration.md` → 授权。

### 持久化查询安全列表（GraphOS PQL）

> **与 APQ 不同。** APQ (`apq`) 是一个运行时带宽优化，它缓存客户端发送的任何操作——它提供**没有**安全功能。安全列表使用 GraphOS 管理的 **持久化查询列表 (PQL)**，客户端在构建时注册；然后路由器会**拒绝不在列表中的操作**。这是“持久化查询安全列表”安全控制。这是一个 **GraphOS 功能**，需要一个连接到 GraphOS 的路由器（`APOLLO_KEY` + `APOLLO_GRAPH_REF`）。

选择一个 **安全级别**（限制性递增）：

| 级别 | 配置 | 行为 |
|------|------|------|
| 审计（推荐首先） | `persisted_queries.log_unknown: true` | 记录未注册的操作；拒绝任何操作。用于确认所有客户端都已注册后再强制执行。 |
| 安全列表 | `safelist.enabled: true` | 拒绝不在 PQL 中的操作。如果注册，ID 和完整字符串都接受。 |
| 安全列表，仅 ID | `safelist.enabled: true` + `require_id: true` | 拒绝未注册的操作**和**任何自由形式的操作字符串，即使字符串已注册。 |

然后收集：
- **路由器是否 GraphOS 连接？** 安全列表需要从 GraphOS 获取 PQL（或 `local_manifests` 用于离线许可证）。
- **客户端是否已将其操作发布到 PQL**（通过 `rover persisted-queries publish` 在其 CI/CD 中）？如果没有，请从审计模式开始。
- 启用 `safelist` 时，**APQ 必须禁用** (`apq.enabled: false`)——它们是互斥的。

配置键历史：GA `persisted_queries` 自 v1.32.0（v1.25.0–v1.32.0 中为 `preview_persisted_queries`）；所有 v2 中 GA。参见 `references/configuration.md` → 持久化查询安全列表。

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
  较高值（75–100）对兼容性更安全，但提供较少的保护以防止基于深度的滥用。

  提示：首先以 `warn_only` 模式运行路由器，以查看实际流量实际使用的深度，然后收紧：
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

> **安全：数据泄露风险。** 在生成任何响应缓存配置之前，您**必须**询问用户哪些类型和字段返回用户特定数据。缓存的默认数据是共享的——没有 `Cache-Control: private` 的子图响应对所有用户可见。用户特定的子图必须返回 `Cache-Control: private`，并在路由器上配置 `private_id`。

- 询问：**哪些子图提供用户特定数据？**（例如，账户、个人资料、购物车）
- 询问：**如何识别用户？**（JWT `sub` 声明、会话令牌、API 密钥）
- Redis URL（默认：`redis://localhost:6379`）
- 默认 TTL（默认：`5m`）
- 启用主动失效？如果是的：失效监听地址和共享密钥
- 使用部分模板：`templates/v2/sections/response-caching.yaml`
- 对于安全要求、模式指令和高级配置：`references/response-caching.md`（从安全部分开始）

## 第 5 步：生成配置

1. 从 `templates/{version}/` 加载正确的版本模板。
2. 组装支持的分段功能的部分模板，然后根据需要合并基模板片段以用于 APQ/订阅。
3. 注入用户提供的参数。
4. 在顶部添加一个注释块，声明目标版本。

## 第 6 步：验证

运行 [生成后清单](validation/checklist.md)：

- [ ] 配置中引用的所有环境变量都有文档记录
- [ ] CORS 来源不包括通配符（生产）
- [ ] 速率限制应用于 `router:`（客户端面），而不仅仅是 `all:`（子图）
- [ ] JWT 使用 `issuers`（v2）而不是 `issuer`（v1），反之亦然
- [ ] 如果是生产：`introspection=false`，`sandbox=false`，`subgraph_errors=false`
- [ ] 健康检查已启用
- [ ] 主页已禁用（生产）
- [ ] 如果路由器二进制文件可用，运行：`router config validate <file>`

## 必要的验证门（始终运行）

生成或编辑任何 `router.yaml` 后，您**必须**：

1. 运行 `validation/checklist.md` 并报告每个清单项的通过/失败。
2. 如果路由器 CLI 可用，运行 `router config validate <path-to-router.yaml>`。
3. 如果路由器 CLI 不可用，明确说明并仍然完成清单。
4. 验证完成之前，不要将配置呈现为最终配置。

## 配置即代码（git + CI/CD）

`router.yaml` 是路由器与每个请求的合同——将其视为应用程序代码，而不是运维的后续思考。无论何时生成或编辑配置，引导用户使用此工作流程：

- **将 `router.yaml` 提交到版本控制。** 它应与服务一起存放在 git 中，通过拉取请求进行更改审查。这为您最安全的关键文件提供了历史记录、责任和回滚。
- **永远不要提交密钥。** 将 `APOLLO_KEY`、JWKS URL、Redis URL 和失效密钥放在文件之外——使用 `${env.*}` 扩展并在部署时注入。提交的文件应该是任何人都可以读取的。
- **在 CI 中验证。** 在每个 PR 上运行 `router config validate router.yaml`，以便在配置有误或版本不匹配的情况下，在发货前失败构建。将 CI 中使用的路由器版本固定到您部署的版本。
- **将配置更改与模式检查配对。** 模式更改通过 `rover subgraph check` / `rover subgraph publish`（`rover` 技能）流经；配置更改通过此 CI 验证门流经。两者都控制相同的部署。
- **在环境中推广相同的文件。** 开发与生产之间的差异应通过环境变量表达，而不是不同的提交文件，因此您审查的是运行的内容。

最小的 CI 步骤（仅提供实际命令，如果需要的话）：

```yaml
# 在每个拉取请求上验证路由器配置
- run: router config validate router.yaml
```

## 第 7 步：条件下一步交接

回答任何 Apollo Router 请求（配置生成、编辑、验证或一般路由器指导）后，决定用户是否已经具有可运行的先决条件：

- GraphOS 管理路径：`APOLLO_KEY` + `APOLLO_GRAPH_REF`，或
- 本地路径：一个组合的 `supergraph.graphql` 加上可访问的子图

如果先决条件已经存在，不要添加额外的交接文本。

如果先决条件缺失或未知，以简洁的 **下一步** 交接结束（最多 1-3 行）且技能优先、无命令：

1. 建议使用 `rover` 技能来组合或获取超图模式。
2. 建议在超图准备好后，使用生成的配置继续 `apollo-router`。
3. 如果子图缺失，建议使用 `apollo-server`、`graphql-schema` 和 `graphql-operations` 技能来构建和测试。

除非用户明确要求命令，否则**不要**在此交接中包含原始 shell 命令。

## 快速入门（技能优先）

1. 使用此 `apollo-router` 技能生成或完善适用于您环境的 `router.yaml`。
2. 选择运行时路径：
   - GraphOS 管理路径：提供 `APOLLO_KEY` 和 `APOLLO_GRAPH_REF`（无需本地超图组合）。
   - 本地超图路径：使用 `graphql-schema` + `apollo-server` 定义/运行子图，然后使用 `graphql-operations` 进行烟雾测试，然后使用 `rover` 技能组合或获取 `supergraph.graphql`。
3. 使用此 `apollo-router` 技能验证就绪状态 (`validation/checklist.md`) 并逐步引导运行时启动输入。

使用标准路由器监听默认值时，默认端点仍然是 `http://localhost:4000`。

如果用户要求可执行的 shell 命令，请按需提供。否则保持快速入门指导为技能导向。

## 运行模式

| 模式 | 命令 | 用例 |
|------|------|------|
| 本地模式 | `router --supergraph ./schema.graphql` | 开发、CI/CD |
| GraphOS 管理 | `APOLLO_KEY=... APOLLO_GRAPH_REF=my-graph@prod router` | 带自动更新的生产 |
| 开发 | `router --dev --supergraph ./schema.graphql` | 本地开发 |
| 热重载 | `router --hot-reload --supergraph ./schema.graphql` | 无需重启的模式更改 |

## 环境变量

| 变量 | 描述 |
|------|------|
| `APOLLO_KEY` | GraphOS 的 API 密钥 |
| `APOLLO_GRAPH_REF` | 图引用 (`graph-id@variant`) |
| `APOLLO_ROUTER_CONFIG_PATH` | `router.yaml` 路径 |
| `APOLLO_ROUTER_SUPERGRAPH_PATH` | 超图模式路径 |
| `APOLLO_ROUTER_LOG` | 日志级别（关闭、错误、警告、信息、调试、追踪） |
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
- [验证清单](validation/checklist.md) — 生成后检查

## CLI 参考

```
router [OPTIONS]

选项:
  -s, --supergraph <PATH>    超图模式文件路径
  -c, --config <PATH>        路由器.yaml 配置路径
      --dev                  启用开发模式
      --hot-reload           监听模式更改
      --log <LEVEL>          日志级别（默认：info）
      --listen <ADDRESS>     覆盖监听地址
  -V, --version              打印版本
  -h, --help                 打印帮助
```

## 行为准则

- **始终在生成配置之前确定目标 Router 版本（v1 或 v2）**
- **对于新项目默认使用 v2**
- **始终在生成的配置顶部添加一个注释块，声明目标版本**
- **始终使用 `--dev` 模式进行本地开发（启用内省和沙盒）**
- **始终在生产中禁用内省、沙盒和主页**
- **优先使用 GraphOS 管理模式进行生产（自动更新、指标）**
- **使用 `--hot-reload` 进行基于文件的模式的本地开发**
- **永远不要在生产中暴露 `APOLLO_KEY` 在日志或版本控制中**
- **使用环境变量 (`${env.VAR}`) 用于所有密钥和敏感配置**
- **优先使用 YAML 配置而不是命令行参数进行复杂设置**
- **在生产部署之前在本地测试配置更改**
- **如果用户在生产中启用 `allow_any_origin` 或通配符 CORS，请警告**
- **建议使用 `router config upgrade router.yaml` 进行 v1 → v2 迁移，而不是从零开始重新生成**
- **生成或编辑路由器配置后，必须运行 `validation/checklist.md`**
- **当 Router CLI 可用时，必须运行 `router config validate <file>`**
- **必须报告 CLI 验证无法运行的情况（例如，路由器二进制文件缺失）**
- **当运行时先决条件缺失或未知时，必须附加一个简短的条件交接**
- **必须使此交接技能优先，并避免除非用户明确要求命令，否则不包含原始 shell 命令**
- **必须保持快速入门指导为技能优先，除非用户明确要求命令**
- **必须说明 Rover 仅用于本地超图路径；GraphOS 管理的运行时不需要本地 Rover 组合**
- **使用 `max_depth: 50` 作为默认起始点，而不是 15（过于激进）或 100（过于宽松）**
- **建议 `warn_only: true` 用于初始限制推广，以在强制执行之前观察实际流量**
- **仅当 `ROUTER_VERSION=v2` 时才提供响应缓存（需要 v2.6.0+）**
- **始终使用 `${env.*}` 用于 Redis URL、密码和失效共享密钥**
- **永远不要在生产配置中启用 `response_cache.debug: true`**
- **建议将 Cache-Control 标头（被动 TTL）与 @cacheTag（主动失效）结合用于生产**
- **始终在生成响应缓存配置之前询问哪些字段返回用户特定数据——永远不要假设所有数据都可以作为共享缓存**
- **始终为提供用户特定数据的子图配置 `private_id`，并确保这些子图返回 `Cache-Control: private`（通过 Apollo Server 中的 `@cacheControl(scope: PRIVATE)`，或在其他框架中直接设置该标头）**
- **永远不要在没有解决私有数据的情况下生成响应缓存配置——如果用户说“没有用户特定数据”，请在继续之前明确确认**
- **始终将失效端点绑定到 `127.0.0.1`，永远不要在生产中使用 `0.0.0.0`**
- **永远不要将 APQ 与持久化查询安全列表混淆——APQ (`apq`) 是带宽优化，没有安全价值；安全列表 (`persisted_queries.safelist`) 是操作允许列表。如果用户要求“锁定可以运行的查询”，请引导他们使用安全列表，而不是 APQ**
- **始终在启用 `persisted_queries.safelist` 时禁用 APQ (`apq.enabled: false`)——它们是互斥的**
- **建议从审计模式 (`log_unknown: true`) 开始持久化查询，以确认所有客户端都已注册后再启用 `safelist.enabled`**
- **说明持久化查询安全列表需要一个 GraphOS 连接的路由器（通过 `APOLLO_KEY` + `APOLLO_GRAPH_REF` 获取 PQL，或 `local_manifests` 用于离线许可证）**
- **使用 `persisted_queries`（GA，v1.32.0+ 和所有 v2），而不是 `preview_persisted_queries`（v1.25.0–v1.32.0）**
- **将全局 `authorization.require_authentication` 和声明式指令视为不同层：前者控制整个请求，后者 (`@authenticated` / `@requiresScopes` / `@policy`) 执行字段和类型级别的过滤**
- **说明声明式授权指令需要一个 GraphOS 连接的路由器（v1.29.1+；开发者/标准计划需要 v2.6.0+）和一个声明源（JWT 认证或填充 `apollo::authentication::jwt_claims` 的协处理器）**
- **注意授权指令默认启用——`authorization.directives.enabled: false` 仅用于关闭它们；永远不要暗示配置是必需的以“打开”它们**
- **说明 `@policy` 需要在超图阶段需要一个 Rhai 脚本或协处理器来评估 `apollo::authorization::required_policies`**
- **将授权指令放在子图模式中，永远不要放在 `router.yaml` 中——路由器配置仅启用/禁用该功能**
- **建议将 `router.yaml` 提交到版本控制，并在每个 PR 上在 CI 中运行 `router config validate`，所有密钥都通过 `${env.*}` 引用，并在部署时注入**
- **永远不要将密钥（`APOLLO_KEY`、JWKS/Redis URL、失效密钥）提交到配置文件；提交的 `router.yaml` 必须安全，任何人都可以持有仓库访问权限**
