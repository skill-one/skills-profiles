# TanStack Start 最佳实践

全栈React应用程序中实现TanStack Start模式的全面指南。这些规则涵盖了服务器函数、中间件、SSR、认证和部署。

## 应用场景

- 创建用于数据变更的服务器函数
- 设置用于认证/日志记录的中间件
- 配置SSR和hydration
- 实现认证流程
- 处理客户端/服务器边界错误
- 组织全栈代码
- 部署到各种平台

## 按优先级分类的规则类别

| 优先级 | 类别 | 规则数量 | 影响 |
|--------|------|----------|------|
| CRITICAL | 服务器函数 | 5条规则 | 核心数据变更模式 |
| CRITICAL | 安全 | 4条规则 | 防止漏洞 |
| HIGH | 中间件 | 4条规则 | 请求/响应处理 |
| HIGH | 认证 | 4条规则 | 安全用户会话 |
| MEDIUM | API路由 | 1条规则 | 外部端点模式 |
| MEDIUM | SSR | 5条规则 | 服务器渲染模式 |
| MEDIUM | 错误处理 | 3条规则 | 优雅失败处理 |
| MEDIUM | 环境 | 1条规则 | 配置管理 |
| LOW | 文件组织 | 3条规则 | 可维护的代码结构 |
| LOW | 部署 | 2条规则 | 生产就绪 |

## 快速参考

### 服务器函数（前缀：`sf-`）

- `sf-create-server-fn` — 使用createServerFn进行服务器端逻辑
- `sf-input-validation` — 始终验证服务器函数输入
- `sf-method-selection` — 选择适当的HTTP方法
- `sf-error-handling` — 处理服务器函数中的错误
- `sf-response-headers` — 在需要时自定义响应头

### 安全（前缀：`sec-`）

- `sec-validate-inputs` — 使用模式验证所有用户输入
- `sec-auth-middleware` — 使用认证中间件保护路由
- `sec-sensitive-data` — 仅在服务器端保留密钥
- `sec-csrf-protection` — 为变更实现CSRF保护

### 中间件（前缀：`mw-`）

- `mw-request-middleware` — 使用请求中间件处理横切关注点
- `mw-function-middleware` — 使用函数中间件处理服务器函数
- `mw-context-flow` — 正确通过中间件传递上下文
- `mw-composability` — 有效地组合中间件

### 认证（前缀：`auth-`）

- `auth-session-management` — 实现安全的会话处理
- `auth-route-protection` — 使用beforeLoad保护路由
- `auth-server-functions` — 在服务器函数中验证认证
- `auth-cookie-security` — 配置安全的cookie设置

### API路由（前缀：`api-`）

- `api-routes` — 为外部消费者创建API路由

### SSR（前缀：`ssr-`）

- `ssr-data-loading` — 为SSR适当加载数据
- `ssr-hydration-safety` — 防止hydration不匹配
- `ssr-streaming` — 实现流式SSR以加快TTFB
- `ssr-selective` — 在有益时应用选择性SSR
- `ssr-prerender` — 配置静态预渲染和ISR

### 环境（前缀：`env-`）

- `env-functions` — 使用环境函数进行配置

### 错误处理（前缀：`err-`）

- `err-server-errors` — 处理服务器函数错误
- `err-redirects` — 适当使用重定向
- `err-not-found` — 处理未找到场景

### 文件组织（前缀：`file-`）

- `file-separation` — 分离服务器和客户端代码
- `file-functions-file` — 使用.functions.ts模式
- `file-shared-validation` — 共享验证模式

### 部署（前缀：`deploy-`）

- `deploy-env-config` — 配置环境变量
- `deploy-adapters` — 选择适当的部署适配器

## 如何使用

`rules/`目录中的每个规则文件包含：
1. **说明** — 为什么这个模式很重要
2. **不良示例** — 要避免的反模式
3. **良好示例** — 推荐的实现方式
4. **上下文** — 何时应用或跳过此规则

## 完整参考

有关详细指导和代码示例，请参阅`rules/`目录中的单个规则文件。
