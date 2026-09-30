---
name: rover
description: 使用 Apollo Rover CLI 管理 GraphQL 模式和联合模式指南。在以下情况使用此技能：(1) 发布或获取子图/图模式，(2) 本地或通过 GraphOS 组合联合图模式，(3) 使用 rover dev 运行本地联合图开发，(4) 使用 check 和 lint 命令验证模式，(5) 配置 Rover 身份验证和环境，(6) 探索或搜索图的模式以进行代理驱动的发现（rover schema describe / rover schema search）。
---

# Apollo Rover CLI 使用指南

Rover 是 Apollo GraphOS 的官方命令行工具。它帮助您管理模式、本地运行组合、发布到 GraphOS，并在本地机器上开发超级图。

## 快速入门

### 第 1 步：安装

```bash
# macOS/Linux
curl -sSL https://rover.apollo.dev/nix/latest | sh

# npm (跨平台)
npm install -g @apollo/rover

# Windows PowerShell
iwr 'https://rover.apollo.dev/win/latest' | iex
```

### 第 2 步：认证

```bash
# 交互式认证（打开浏览器）
rover config auth

# 或者设置环境变量
export APOLLO_KEY=your-api-key
```

### 第 3 步：验证安装

```bash
rover --version
rover config whoami
```

## 探索图的模式（有模式问题时从这里开始）

要回答“这个图里有什么？”、查找一个字段或对 GraphOS 图编写查询，**获取 API 模式并将其传递给 `rover schema`** — 这将 SDL 从您的上下文中分离出来，并只返回您需要的内容：

```bash
# 我能查询什么？（简洁概览）
rover graph fetch <graph@variant> | rover schema describe -

# 通过概念/关键词查找字段（返回从根操作开始的路径）
rover graph fetch <graph@variant> | rover schema search - "<keyword>"

# 聚焦到一个类型或字段
rover graph fetch <graph@variant> | rover schema describe - --coord <Type.field> --depth 1
```

保持正确的三个规则：

- 使用 **`rover graph fetch`**（API 模式）— **不要**使用 `rover supergraph fetch`（那会返回包含联合内部结构如 `join__`/`link__` 的组合 SDL）。
- **传递**它 — 永远不要单独运行 `rover graph fetch` 并读取原始 SDL（一个大的模式会淹没您的上下文；这正是 `rover schema` 避免的）。
- `schema` 命令读取 **传递的 SDL，而不是图引用** — `rover schema describe <graph@variant>` 会失败；您必须先获取然后传递。

完整参考、排名规则和一次性保存模式：[模式探索](#agent的schema探索) 和 [参考资料/schema.md](references/schema.md)。

## 核心命令概览

| 命令 | 描述 | 用例 |
|------|------|------|
| `rover subgraph publish` | 将子图模式发布到 GraphOS | CI/CD、模式更新 |
| `rover subgraph check` | 验证模式更改 | PR 检查、预部署 |
| `rover subgraph fetch` | 下载子图模式 | 本地开发 |
| `rover supergraph compose` | 本地组合超级图 | 本地测试 |
| `rover dev` | 本地超级图开发 | 开发工作流 |
| `rover graph publish` | 发布单图模式 | 非联合图 |
| `rover schema describe` | 通过坐标探索模式；**通过 stdin/文件获取 SDL，而不是图引用** — 从 `rover graph fetch` 传递 | 代理模式发现 |
| `rover schema search` | 通过关键词搜索模式；**通过 stdin/文件获取 SDL，而不是图引用** — 从 `rover graph fetch` 传递 | 代理模式发现 |

## 图引用格式

大多数命令需要一个图引用，格式为：

```
<GRAPH_ID>@<VARIANT>
```

示例：
- `my-graph@production`
- `my-graph@staging`
- `my-graph@current`（默认变体）

设置为环境变量：
```bash
export APOLLO_GRAPH_REF=my-graph@production
```

## 子图工作流

### 发布子图

```bash
# 从模式文件
rover subgraph publish my-graph@production \
  --name products \
  --schema ./schema.graphql \
  --routing-url https://products.example.com/graphql

# 从运行的服务器（检视）
rover subgraph publish my-graph@production \
  --name products \
  --schema <(rover subgraph introspect http://localhost:4001/graphql) \
  --routing-url https://products.example.com/graphql
```

### 检查模式更改

```bash
# 与生产流量对比
rover subgraph check my-graph@production \
  --name products \
  --schema ./schema.graphql
```

### 获取模式

```bash
# 从 GraphOS 获取
rover subgraph fetch my-graph@production --name products

# 检视运行的服务器
rover subgraph introspect http://localhost:4001/graphql
```

## 超级图组合

### 本地组合

创建 `supergraph.yaml`：

```yaml
federation_version: =2.9.0
subgraphs:
  products:
    routing_url: http://localhost:4001/graphql
    schema:
      file: ./products/schema.graphql
  reviews:
    routing_url: http://localhost:4002/graphql
    schema:
      subgraph_url: http://localhost:4002/graphql
```

这里的 `federation_version` 是**组合版本** — 它只需要 ≥ 每个子图的 `@link` 地板，因此固定到较低版本的子图可以正常组合。如果一个子图服务器在启动时抛出 `UNKNOWN_FEDERATION_LINK_VERSION`，那是一个客户端库延迟，而不是组合问题。有关 apollo-federation 技能的 [组合版本](../apollo-federation/references/composition.md#federation-versions-floor-vs-composition)。

组合：
```bash
rover supergraph compose --config supergraph.yaml > supergraph.graphql
```

### 获取组合的超级图

```bash
rover supergraph fetch my-graph@production
```

> 这返回**超级图 SDL**（联合指令 + `join__`/`link__` 内部结构）— 用于组合/路由器工作。要**探索可以查询什么**或编写操作，请使用 `rover graph fetch`（API 模式）而不是 — 见 [探索图的模式](#explore-a-graphs-schema-start-here-for-schema-questions)。

## 使用 `rover dev` 进行本地开发

启动自动模式组合的本地路由器：

```bash
# 使用超级图配置启动
rover dev --supergraph-config supergraph.yaml

# 以 GraphOS 变体为基础启动
rover dev --graph-ref my-graph@staging --supergraph-config local.yaml
```

### 与 MCP 集成

```bash
# 启用 MCP 服务器
rover dev --supergraph-config supergraph.yaml --mcp
```

## 模式探索（针对代理）

`rover schema describe` 和 `rover schema search` 允许代理**在不将完整 SDL 加载到上下文的情况下探索模式** — 这正是这些命令的要点。

> ⚠️ **永远不要将原始 SDL 读取到上下文中。** 单独运行 `rover graph fetch <ref>`（或 `rover graph introspect <url>`）会直接将整个模式（数百到数万行）打印到您的上下文中，这违背了这些命令的用途。**始终将 `rover graph fetch`/`introspect` 的输出传递给 `rover schema describe`/`search`**：SDL 通过 stdin 流动，只有紧凑概览/结果会到达您这里。（将获取到文件中是当用户实际需要 SDL 时可以的。）
>
> 这些命令还接受在 **stdin 或文件上的 SDL，而不是图引用** — 您不能将 `graph@variant` 传递给它们。先获取，然后传递：
>
> ```bash
> ❌ rover schema describe my-graph@current             # 错误：查找以该名称命名的文件
> ❌ rover graph fetch my-graph@current                 # 将完整的 SDL 打印到您的上下文中
> ✅ rover graph fetch my-graph@current | rover schema describe -
> ```

要探索 GraphOS 中的图，获取其模式并传递。**使用 `rover graph fetch`（API 模式）进行“我可以查询什么？”的探索** — 它会省略联合内部结构。仅在需要组合细节（`join__`/`link__` 类型、子图结构）时使用 `rover supergraph fetch`：

```bash
# GraphOS 图的概览
rover graph fetch my-graph@current | rover schema describe -

# 通过关键词查找字段（结果包括从根操作开始的路径）
rover graph fetch my-graph@current | rover schema search - "playback"

# 聚焦到坐标，展开引用的类型一级
rover graph fetch my-graph@current | rover schema describe - --coord <Type.field> --depth 1
```

**坐标形式：** `--coord` 接受类型（`User`）、字段（`User.posts`）、字段参数（`Type.field(arg:)`）或指令（`@deprecated`）— 不指定它将显示概览。

**`search` vs `describe`：** 当您匹配概念或关键词但尚未知道字段名时，首先使用 `rover schema search` — 它会找到**嵌套**字段并显示从根操作开始的路径。`describe` 概览只列出根字段，因此 `search` 是如何定位更深层次字段的方法。使用 `describe` 进行概览或一旦您知道类型/字段坐标。

这启用了闭环工作流 — 搜索 → 描述 → 编写查询 — 而无需设置 MCP 服务器。有关完整命令参考、排名规则和大型模式的保存一次模式，请参阅 [模式探索](references/schema.md)。

**运行生成的操作：** Rover **不**执行查询 — 它只管理和检视模式。要实际运行生成的查询，您需要图的端点：

- **单子图图：** `rover subgraph list <graph@variant>` 会打印**路由 URL** — 使用 `curl` 将查询发送到那里。
- **多子图/联合：** 客户端端点是**路由器** URL（在 GraphOS Studio 中找到；对于 GraphOS 云路由器，`rover cloud config fetch <graph@variant>`），而不是每个子图的路由 URL。
- 不要尝试通过 GraphOS 平台 API 发现端点 — Rover 将 API 密钥保存在其配置文件/密钥链中，而不是 `$APOLLO_KEY`，因此临时 API 调用将返回未认证的响应。

## 参考资料

特定主题的详细文档：

- [子图](references/subgraphs.md) - 获取、发布、检查、格式化、检视、删除
- [图](references/graphs.md) - 单图命令（非联合）
- [超级图](references/supergraphs.md) - 组合、获取、配置格式
- [开发](references/dev.md) - `rover dev` 用于本地开发
- [模式探索](references/schema.md) - 描述、搜索、代理模式发现工作流
- [配置](references/configuration.md) - 安装、认证、环境变量、配置文件

## 常见模式

### CI/CD 管道

```bash
# 1. 检查模式更改
rover subgraph check $APOLLO_GRAPH_REF \
  --name $SUBGRAPH_NAME \
  --schema ./schema.graphql

# 2. 如果检查通过，发布
rover subgraph publish $APOLLO_GRAPH_REF \
  --name $SUBGRAPH_NAME \
  --schema ./schema.graphql \
  --routing-url $ROUTING_URL
```

### 模式格式化

```bash
# 根据 GraphOS 规则格式化
rover subgraph lint --name products ./schema.graphql

# 单图格式化
rover graph lint my-graph@production ./schema.graphql
```

### 输出格式

```bash
# 脚本用的 JSON 输出
rover subgraph fetch my-graph@production --name products --format json

# 普通输出（默认）
rover subgraph fetch my-graph@production --name products --format plain
```

## 基本规则

- 在使用 GraphOS 命令之前**始终认证**（`rover config auth` 或 `APOLLO_KEY`）
- **始终**使用正确的图引用格式：`graph@variant`
- 在 CI/CD 中**优先**使用 `rover subgraph check` 而不是 `rover subgraph publish`
- 使用 `rover dev` 进行本地超级图开发，而不是手动运行路由器
- **永远不要**将 `APOLLO_KEY` 提交到版本控制；使用环境变量
- 解析输出时**使用** `--format json`
- 在 `supergraph.yaml` 中明确指定 `federation_version` 以确保可重复性
- 使用 `rover subgraph introspect` 从运行的服务器中提取模式
- 使用 `rover schema search` / `rover schema describe`（从 `fetch` 传递）探索大型模式，而不是将完整 SDL 加载到上下文中
- **永远不要**为了探索而获取完整模式 — 将 `rover graph fetch`/`introspect` 传递给 `rover schema describe`/`search`（裸 `fetch` 仅在用户需要 SDL 文件时使用）
