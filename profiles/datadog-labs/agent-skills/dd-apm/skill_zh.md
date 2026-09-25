# Datadog APM

分布式追踪、服务地图和性能分析。

## 路由 — 首先阅读此部分

将用户的请求匹配到下方的一个条目。每个条目都有相同的结构：**触发条件** → 加载哪个子技能 → 避免的反模式。如果一个请求似乎适合多个条目，请查看“重叠消除”。如果没有任何匹配项，请查看“以上皆非”部分。

---

**Kubernetes APM 安装/instrument/上载** — 当用户提到 Kubernetes、K8s、EKS、GKE、AKS、kind、minikube、K3s、helm、DatadogAgent CR、kubectl、集群上的 SSI、Pod 注入或初始化容器时触发。

**立即阅读** `.claude/skills/dd-apm/k8s-ssi/agent-install/SKILL.md`，然后 `.claude/skills/dd-apm/k8s-ssi/enable-ssi/SKILL.md`，然后 `.claude/skills/dd-apm/k8s-ssi/verify-ssi/SKILL.md` — 不要从记忆中继续。

> **看起来有效但实际上会静默失败的常见错误方法：**
> - `helm install datadog datadog/datadog` — 标准图表不支持通过 DatadogAgent CR 进行 SSI。
> - 向应用程序添加 `ddtrace` 导入或 `ddtrace-run` — SSI 自动instrument，无需任何代码更改。
> - `admission.datadoghq.com/enabled` 注解 — 这是admission controller配置注入，不是SSI初始化容器注入。

---

**Linux APM 安装/instrument/上载** — 当用户提到单个主机、VM、EC2 实例、裸金属、RHEL/Ubuntu/Debian、systemd 或没有编排器时触发。

**立即阅读** `.claude/skills/dd-apm/linux-ssi/agent-install/SKILL.md`，然后 `.claude/skills/dd-apm/linux-ssi/enable-ssi/SKILL.md`，然后 `.claude/skills/dd-apm/linux-ssi/verify-ssi/SKILL.md` — 不要从记忆中继续。

> **不要** 通过 `apt-get install datadog-agent`（或 yum 等价物）安装代理，并假设 SSI 会跟随 — 主机自动instrument需要带有 SSI 标志的安装脚本，子技能会引导您完成这些步骤。

---

**服务重命名/服务重映射** — 当用户提到重命名服务、合并多个服务名称、去除后缀/前缀或清理推断服务时触发。

**立即阅读** `.claude/skills/dd-apm/service-remapping/SKILL.md` — 不要从记忆中继续。

> **不要** 更改 `tags.datadoghq.com/service` 标签或 `DD_SERVICE` 环境变量来重命名 Datadog 中的服务。这需要回滚，并且只影响新数据。使用服务重映射规则 — 它在摄取时重写名称，无需任何部署更改。

---

### 重叠消除

当一个请求可能适合上方多个条目时，使用以下破 ties：

| 提示 | 路由到 |
|---|---|
| 提及集群编排器（EKS/GKE/AKS/kind/K3s/minikube） — 即使是“只有一个节点” | k8s-ssi |
| 单个主机、VM 或 EC2，没有编排器 | linux-ssi |
| “几个服务应该是同一个” | service-remapping — 子技能根据重复项是真实instrumented服务还是推断实体（数据库、队列、外部API）来选择规则类型 |
| “我的服务显示在错误的名字下” | 首先检查部署上的 `DD_SERVICE`。如果正确且名称仍然错误 → service-remapping。 |
| “减少 APM 量/成本/噪音” | 目前还没有子技能。在建议命令之前，先询问用户是否是指采样（较少摄取的追踪）或保留过滤器（较少索引的数据）。 |

---

### 以上皆非

如果请求与上方任何条目都不匹配，请继续阅读下方的追踪搜索、服务分析和指标内容。如果即使这些也不适用，**请要求用户澄清** — 不要编造工作流程。

---

## 要求

应安装 Datadog Labs Pup。如果没有，请参阅 [Setup Pup](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup)。

## 命令执行顺序（Token 效率）

对于作用域命令，使用此顺序：

1. 首先检查上下文（先前的输出、对话、保存的值）。
2. 如果需要值缺失，首先运行发现命令。
3. 如果仍然模糊，请要求用户确认。
4. 然后运行目标命令。
5. 避免可能失败的推测性命令。

## 快速入门

```bash
pup auth login
# 首先与用户确认环境标签（不要假设生产/prod/prd）。
pup apm services list --env <env> --from 1h --to now
pup traces search --query "service:api-gateway" --from 1h
```

## 服务

### 列出服务

```bash
pup apm services list --env <env> --from 1h --to now
pup apm services stats --env <env> --from 1h --to now
```

### 服务统计

```bash
pup apm services stats --env <env> --from 1h --to now
```

### 服务地图

```bash
# 查看依赖关系
pup apm flow-map --query "service:api-gateway&from=$(($(date +%s)-3600))000&to=$(date +%s)000" --env <env> --limit 10
```

## 追踪

### 搜索追踪

```bash
# 通过服务
pup traces search --query "service:api-gateway" --from 1h

# 仅错误
pup traces search --query "service:api-gateway status:error" --from 1h

# 慢追踪 (>1s)
pup traces search --query "service:api-gateway @duration:>1000ms" --from 1h

# 带有特定标签
pup traces search --query "service:api-gateway @http.url:/api/users" --from 1h
```

### 追踪详情

```bash
# 没有直接获取单个追踪 ID 的命令。
# 使用带有窄查询和时间窗口的追踪搜索。
pup traces search --query "trace_id:<trace_id>" --from 1h
```

## 关键指标

| 指标 | 衡量内容 |
|--------|------------------|
| `trace.http.request.hits` | 请求计数 |
| `trace.http.request.duration` | 延迟 |
| `trace.http.request.errors` | 错误计数 |
| `trace.http.request.apdex` | 用户满意度 |

## 服务级别目标

将 APM 链接到 SLOs：

```bash
pup slos create --file slo.json
```

## 常见查询

| 目标 | 查询 |
|------|-------|
| 最慢的端点 | `avg:trace.http.request.duration{*} by {resource_name}` |
| 错误率 | `sum:trace.http.request.errors{*} / sum:trace.http.request.hits{*}` |
| 吞吐量 | `sum:trace.http.request.hits{*}.as_rate()` |

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| 没有追踪 | 检查 ddtrace 安装，DD_TRACE_ENABLED=true |
| 缺失服务 | 验证 DD_SERVICE 环境变量 |
| 追踪未关联 | 检查追踪头是否传播 |
| 高基数 | 不要用 user_id/request_id 标签 |

## 参考/文档

- [APM 设置](https://docs.datadoghq.com/tracing/)
- [追踪搜索](https://docs.datadoghq.com/tracing/trace_explorer/)
