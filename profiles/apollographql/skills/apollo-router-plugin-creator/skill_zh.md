# Apollo Router 插件创建器

为 Apollo Router 创建原生 Rust 插件。

## 请求生命周期

```
┌────────┐             ┌────────────────┐                                   ┌────────────────────┐               ┌───────────────────┐       ┌─────────────────────┐
│ 客户端 │             │ 路由服务      │                                   │ 超图服务          │               │ 执行服务        │       │ 子图服务(们)      │
└────┬───┘             └────────┬───────┘                                   └──────────┬─────────┘               └─────────┬─────────┘       └──────────┬──────────┘
     │                          │                                                      │                                   │                            │
     │      发送请求           │                                                      │                                   │                            │
     │──────────────────────────▶                                                      │                                   │                            │
     │                          │                                                      │                                   │                            │
     │                          │  将原始 HTTP 请求转换为 GraphQL/JSON 请求   │                                   │                            │
     │                          │──────────────────────────────────────────────────────▶                                   │                            │
     │                          │                                                      │                                   │                            │
     │                          │                                                      │  启动查询计划执行           │                            │
     │                          │                                                      │──────────────────────────────────▶                            │
     │                          │                                                      │                                   │                            │
     │                          │                                                      │                               ┌par [启动子操作]───────┐
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               │   │  启动子操作           │   │
     │                          │                                                      │                               │   │────────────────────────────▶   │
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               ├[启动子操作]╌╌╌╌╌╌╌╌╌╌╌┤
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               │   │  启动子操作           │   │
     │                          │                                                      │                               │   │────────────────────────────▶   │
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               ├[启动子操作]╌╌╌╌╌╌╌╌╌╌╌┤
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               │   │  启动子操作           │   │
     │                          │                                                      │                               │   │────────────────────────────▶   │
     │                          │                                                      │                               │   │                            │   │
     │                          │                                                      │                               └────────────────────────────────────┘
     │                          │                                                      │                                   │                            │
     │                          │                                                      │  组装并返回响应           │                            │
     │                          │                                                      ◀╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│                            │
     │                          │                                                      │                                   │                            │
     │                          │            返回 GraphQL/JSON 响应             │                                   │                            │
     │                          ◀╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│                                   │                            │
     │                          │                                                      │                                   │                            │
     │  返回 HTTP 响应         │                                                      │                                   │                            │
     ◀╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│                                                      │                                   │                            │
     │                          │                                                      │                                   │                            │
┌────┴───┐             ┌────────┴───────┐                                   ┌──────────┴─────────┐               ┌─────────┴─────────┐       ┌──────────┴──────────┐
│ 客户端 │             │ 路由服务      │                                   │ 超图服务          │               │ 执行服务        │       │ 子图服务(们)      │
└────────┘             └────────────────┘                                   └────────────────────┘               └───────────────────┘       └─────────────────────┘
```

## 服务钩子

### 服务概述

| 服务              | 描述                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `router_service`     | 在 HTTP 请求生命周期的最开始和最末尾运行。例如，JWT 认证在 RouterService 内部执行。如果您的自定义需求需要与 HTTP 上下文和头部交互，请定义 router_service。它不支持访问 body 属性                                                                                                                                                               |
| `supergraph_service` | 在 GraphQL 请求生命周期的最开始和最末尾运行。如果您的自定义需求需要与 GraphQL 请求或 GraphQL 响应交互，请定义 supergraph_service。例如，您可以添加对匿名查询的检查。                                                                                                                                                                                                  |
| `execution_service`  | 处理在生成查询计划后启动其执行。如果您的自定义需求包括控制执行的逻辑（例如，如果您想根据策略决策阻止特定的查询），请定义 execution_service。                                                                                                                                                                                                       |
| `subgraph_service`   | 处理路由与您的子图之间的通信。定义 subgraph_service 以配置此通信（例如，动态地向子图传递 HTTP 头部）。其他服务是针对每个客户端请求调用一次，而此服务是针对解析客户端请求所需的每个子图请求调用一次。每次调用都会传递一个子图参数，该参数指示相应子图的名称。 |

**签名：**
```rust
fn router_service(&self, service: router::BoxService) -> router::BoxService
fn supergraph_service(&self, service: supergraph::BoxService) -> supergraph::BoxService
fn execution_service(&self, service: execution::BoxService) -> execution::BoxService
fn subgraph_service(&self, name: &str, service: subgraph::BoxService) -> subgraph::BoxService
```

### 单个钩子（Tower Layers）

使用 `ServiceBuilder` 在任何服务内组合这些钩子：

| 钩子                      | 目的                                      | 同步/异步 |
|---------------------------|----------------------------------------------|------------|
| `map_request(fn)`         | 在继续之前转换请求                          | 同步       |
| `map_response(fn)`        | 在返回之前转换响应                          | 同步       |
| `checkpoint(fn)`          | 验证/过滤，可以短路                        | 同步       |
| `checkpoint_async(fn)`    | 异步验证，可以短路                        | 异步      |
| `buffered()`              | 启用服务克隆（异步所需）                  | -          |
| `instrument(span)`        | 在服务周围添加跟踪跨度                      | -          |
| `rate_limit(num, period)` | 控制请求吞吐量                           | -          |
| `timeout(duration)`       | 设置操作时间限制                         | -          |

### 选择服务钩子

**按所需数据：**
- 仅 HTTP 头部 → `router_service`
- GraphQL 查询/变量 → `supergraph_service`
- 查询计划 → `execution_service`
- 每个子图控制 → `subgraph_service`

**按时间：**
- 在 GraphQL 解析之前 → `router_service` 请求
- 解析之后、规划之前 → `supergraph_service` 请求
- 规划之后、执行之前 → `execution_service` 请求
- 每个子图调用之前/之后 → `subgraph_service`
- 最终返回给客户端的响应 → `router_service` 响应

参见 [references/service-hooks.md](references/service-hooks.md) 了解实现模式。

## 快速入门

### 第 1 步：创建插件文件

创建一个新文件 `src/plugins/my_plugin.rs` 并包含必要的导入：

```rust
use std::ops::ControlFlow;
use apollo_router::plugin::{Plugin, PluginInit};
use apollo_router::register_plugin;
use apollo_router::services::{router, subgraph, supergraph};
use schemars::JsonSchema;
use serde::Deserialize;
use tower::{BoxError, ServiceBuilder, ServiceExt};

const PLUGIN_NAME: &str = "my_plugin";
```

### 第 2 步：定义配置结构体

每个插件都需要一个具有 `Deserialize` 和 `JsonSchema` 派生的配置结构体。`JsonSchema` 可以在编辑器中启用配置验证：

```rust
#[derive(Debug, Clone, Default, Deserialize, JsonSchema)]
struct MyPluginConfig {
  /// 启用插件
  enabled: bool,
  // 根据需要添加其他配置字段
}
```

### 第 3 步：定义插件结构体

```rust
#[derive(Debug)]
struct MyPlugin {
  configuration: MyPluginConfig,
}
```

### 第 4 步：实现插件特质

实现 `Plugin` 质别，包含所需的 `Config` 类型和新构造函数：

```rust
#[async_trait::async_trait]
impl Plugin for MyPlugin {
  type Config = MyPluginConfig;

  async fn new(init: PluginInit<Self::Config>) -> Result<Self, BoxError> {
    Ok(MyPlugin { configuration: init.config })
  }

  // 根据您的需求添加服务钩子（参见“选择服务钩子”部分）
}
```

### 第 5 步：添加服务钩子

根据您的需求选择要钩子的服务（详情参见 [服务概述](#service-overview)）。

示例服务钩子：
```rust
fn supergraph_service(&self, service: supergraph::BoxService) -> supergraph::BoxService {
  if !self.configuration.enabled {
    return service;
  }

  ServiceBuilder::new()
    .map_request(|req| { /* 转换请求 */ req })
    .map_response(|res| { /* 转换响应 */ res })
    .service(service)
    .boxed()
}
```

### 第 6 步：注册插件

在您的插件文件底部，使用路由器注册它：

```rust
register_plugin!("acme", "my_plugin", MyPlugin);
```

### 第 7 步：添加模块到 mod.rs

在 `src/plugins/mod.rs` 中，添加您的模块：

```rust
pub mod my_plugin;
```

### 第 8 步：在 YAML 中配置

在路由器配置中启用您的插件：

```yaml
plugins:
  acme.my_plugin:
    enabled: true
```

## 常见模式

有关实现模式和代码示例，参见 [references/service-hooks.md](references/service-hooks.md)：
- 启用/禁用模式
- 请求/响应转换 (`map_request`, `map_response`)
- Checkpoint（提前返回/短路）
- 钩子之间传递上下文
- 异步操作 (`checkpoint_async`, `buffered`)
- 错误响应构建器

## 示例

### Apollo Router 示例

位于 [Apollo Router 插件目录](https://github.com/apollographql/router/tree/dev/apollo-router/src/plugins) 中：

| 插件                 | 服务钩子           | 模式           | 描述                 |
|------------------------|------------------------|-------------------|-----------------------------|
| `forbid_mutations.rs`  | `execution_service`    | checkpoint        | 简单查询计划门禁   |
| `expose_query_plan.rs` | execution + supergraph | 上下文传递   | 多服务协调  |
| `cors.rs`              | `router_service`       | HTTP 层        | HTTP 层的 CORS 处理 |
| `headers/`             | `subgraph_service`     | 层级组合        | 复杂头部操作 |

有关完整的代码示例和测试模式，参见 [references/examples.md](references/examples.md)。

## 前置条件

建议安装 [rust-best-practices](https://skills.sh/apollographql/skills/rust-best-practices) 技能，以便在开发路由器插件时编写符合 Rust 习惯的代码。如果已安装，则在生成或修改插件代码时遵循这些最佳实践。

## 资源

- [references/service-hooks.md](references/service-hooks.md) - 详细服务钩子实现
- [references/existing-plugins.md](references/existing-plugins.md) - 现有插件索引
- [references/examples.md](references/examples.md) - 完整代码示例和测试模式
- Apollo Router 插件：https://github.com/apollographql/router/tree/dev/apollo-router/src/plugins
