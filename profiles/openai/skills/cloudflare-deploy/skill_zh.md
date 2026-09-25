# Cloudflare 部署

在 Cloudflare 平台上构建的综合技能。使用下方的决策树找到合适的产品，然后加载详细参考。

## 前置条件

- 当沙盒阻止部署网络调用时，使用 `sandbox_permissions=require_escalated` 重新运行。
- 部署可能需要几分钟。使用适当的超时值。

## 认证（部署前必须）

在 `wrangler deploy`、`wrangler pages deploy` 或 `npm run deploy` 之前验证认证：

```bash
npx wrangler whoami    # 如果认证成功，显示账号信息
```

未认证？→ `references/wrangler/auth.md`
- 交互式/本地：`wrangler login`（一次性 OAuth）
- CI/CD：设置 `CLOUDFLARE_API_TOKEN` 环境变量

## 快速决策树

### "我需要运行代码"

```
需要运行代码？
├─ 边缘服务器less函数 → workers/
├─ 带Git部署的全栈Web应用 → pages/
├─ 状态管理/实时 → durable-objects/
├─ 长运行多步骤任务 → workflows/
├─ 运行容器 → containers/
├─ 多租户（客户部署代码）→ workers-for-platforms/
├─ 定时任务（cron）→ cron-triggers/
├─ 轻量级边缘逻辑（修改HTTP）→ snippets/
├─ 处理Worker执行事件（日志/可观测性）→ tail-workers/
└─ 优化到后端基础设施的延迟 → smart-placement/
```

### "我需要存储数据"

```
需要存储？
├─ 键值（配置、会话、缓存）→ kv/
├─ 关系型SQL → d1/ (SQLite) 或 hyperdrive/ (现有Postgres/MySQL)
├─ 对象/文件存储（S3兼容）→ r2/
├─ 消息队列（异步处理）→ queues/
├─ 向量嵌入（AI/语义搜索）→ vectorize/
├─ 每个实体的强一致性状态 → durable-objects/ (DO存储)
├─ 密钥管理 → secrets-store/
├─ 流式ETL到R2 → pipelines/
└─ 持久化缓存（长期保留）→ cache-reserve/
```

### "我需要AI/ML"

```
需要AI？
├─ 运行推理（LLMs、嵌入、图像）→ workers-ai/
├─ 向量数据库用于RAG/搜索 → vectorize/
├─ 构建状态AI代理 → agents-sdk/
├─ 任何AI提供商的网关（缓存、路由）→ ai-gateway/
└─ AI驱动的搜索组件 → ai-search/
```

### "我需要网络/连接"

```
需要网络？
├─ 将本地服务暴露到互联网 → tunnel/
├─ TCP/UDP代理（非HTTP）→ spectrum/
├─ WebRTC TURN服务器 → turn/
├─ 私有网络连接 → network-interconnect/
├─ 优化路由 → argo-smart-routing/
├─ 优化到后端（非用户）的延迟 → smart-placement/
└─ 实时音视频 → realtimekit/ 或 realtime-sfu/
```

### "我需要安全"

```
需要安全？
├─ Web应用防火墙 → waf/
├─ DDoS防护 → ddos/
├─ 机器人检测/管理 → bot-management/
├─ API防护 → api-shield/
├─ CAPTCHA替代方案 → turnstile/
└─ 凭证泄露检测 → waf/ (管理规则集)
```

### "我需要媒体/内容"

```
需要媒体？
├─ 图像优化/转换 → images/
├─ 视频流/编码 → stream/
├─ 浏览器自动化/截图 → browser-rendering/
└─ 第三方脚本管理 → zaraz/
```

### "我需要基础设施即代码"

```
需要IaC? → pulumi/ (Pulumi), terraform/ (Terraform), 或 api/ (REST API)
```

## 产品索引

### 计算 & 运行时

| 产品 | 参考 |
|-------|-----------|
| Workers | `references/workers/` |
| Pages | `references/pages/` |
| Pages Functions | `references/pages-functions/` |
| Durable Objects | `references/durable-objects/` |
| Workflows | `references/workflows/` |
| Containers | `references/containers/` |
| Workers for Platforms | `references/workers-for-platforms/` |
| Cron Triggers | `references/cron-triggers/` |
| Tail Workers | `references/tail-workers/` |
| Snippets | `references/snippets/` |
| Smart Placement | `references/smart-placement/` |

### 存储 & 数据

| 产品 | 参考 |
|---------|-----------|
| KV | `references/kv/` |
| D1 | `references/d1/` |
| R2 | `references/r2/` |
| Queues | `references/queues/` |
| Hyperdrive | `references/hyperdrive/` |
| DO Storage | `references/do-storage/` |
| Secrets Store | `references/secrets-store/` |
| Pipelines | `references/pipelines/` |
| R2 Data Catalog | `references/r2-data-catalog/` |
| R2 SQL | `references/r2-sql/` |

### AI & 机器学习

| 产品 | 参考 |
|---------|-----------|
| Workers AI | `references/workers-ai/` |
| Vectorize | `references/vectorize/` |
| Agents SDK | `references/agents-sdk/` |
| AI Gateway | `references/ai-gateway/` |
| AI Search | `references/ai-search/` |

### 网络 & 连接

| 产品 | 参考 |
|---------|-----------|
| Tunnel | `references/tunnel/` |
| Spectrum | `references/spectrum/` |
| TURN | `references/turn/` |
| Network Interconnect | `references/network-interconnect/` |
| Argo Smart Routing | `references/argo-smart-routing/` |
| Workers VPC | `references/workers-vpc/` |

### 安全

| 产品 | 参考 |
|---------|-----------|
| WAF | `references/waf/` |
| DDoS Protection | `references/ddos/` |
| Bot Management | `references/bot-management/` |
| API Shield | `references/api-shield/` |
| Turnstile | `references/turnstile/` |

### 媒体 & 内容

| 产品 | 参考 |
|---------|-----------|
| Images | `references/images/` |
| Stream | `references/stream/` |
| Browser Rendering | `references/browser-rendering/` |
| Zaraz | `references/zaraz/` |

### 实时通信

| 产品 | 参考 |
|---------|-----------|
| RealtimeKit | `references/realtimekit/` |
| Realtime SFU | `references/realtime-sfu/` |

### 开发者工具

| 产品 | 参考 |
|---------|-----------|
| Wrangler | `references/wrangler/` |
| Miniflare | `references/miniflare/` |
| C3 | `references/c3/` |
| Observability | `references/observability/` |
| Analytics Engine | `references/analytics-engine/` |
| Web Analytics | `references/web-analytics/` |
| Sandbox | `references/sandbox/` |
| Workerd | `references/workerd/` |
| Workers Playground | `references/workers-playground/` |

### 基础设施即代码

| 产品 | 参考 |
|---------|-----------|
| Pulumi | `references/pulumi/` |
| Terraform | `references/terraform/` |
| API | `references/api/` |

### 其他服务

| 产品 | 参考 |
|---------|-----------|
| Email Routing | `references/email-routing/` |
| Email Workers | `references/email-workers/` |
| Static Assets | `references/static-assets/` |
| Bindings | `references/bindings/` |
| Cache Reserve | `references/cache-reserve/` |

## 故障排除

### 升级网络访问

如果由于网络问题（超时、DNS错误、连接重置）导致部署失败，使用升级权限重新运行部署（使用 `sandbox_permissions=require_escalated`）。当沙盒网络阻止出站请求时，部署需要升级网络访问权限。

用户指导示例：

```
部署需要升级网络访问权限才能部署到Cloudflare。我可以使用升级权限重新运行命令——要继续吗？
```
