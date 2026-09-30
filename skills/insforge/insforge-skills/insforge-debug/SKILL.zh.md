---
name: insforge-debug
description: 在InsForge项目中诊断问题时使用——反应性故障（SDK错误对象、HTTP 4xx/5xx、网关超时502/503/504、边缘函数失败或超时、登录/OAuth/认证错误、RLS拒绝、实时通道问题、单个端点的慢查询、边缘函数或Vercel部署失败）、主动审核（安全/RLS审查、性能/索引审查、系统健康检查、发布前准备就绪），或当用户遇到错误但不知道从何处开始时。
---

# InsForge 调试

通过结合后端的可观测性基础组件——日志、指标、数据库健康、顾问、策略、元数据、错误对象、部署状态和 AI 辅助，诊断 InsForge 项目中的问题。这项技能提供：

1. 每个 **调试基础组件** 的参考（每个可观测性表面都在 `references/` 下）
2. **症状配方**（见下文），用于命名已知反应性症状和主动审计的基础组件序列

**始终使用 `npx -y @insforge/cli`** —— 永远不要全局安装 CLI。

## 最快路径：AI 辅助的初步诊断

当用户给出具体的描述（错误消息、失败的 URL、HTTP 状态）时，将其交给 InsForge 调试代理。与其他基础组件不同，这个基础组件返回建议，而不仅仅是观察结果——在采取行动之前，请验证它引用的基础组件的诊断结果。

```bash
npx -y @insforge/cli diagnose --ai "<问题描述>"
```

有关何时使用此方法、何时跳过以及如何验证输出的信息，请参阅 [references/ai-assisted.md](references/ai-assisted.md)。

## 调试基础组件

每个基础组件都是一个独立可查询的可观测性表面，由不同的底层数据源支持。真实的诊断是基础组件的组合。

所有命令都通过 `npx -y @insforge/cli ...` 运行。每个基础组件旁边显示的 `(command)` 是实际的 CLI 命令——基础组件名称是概念标签，**不是** CLI 子命令名称（例如，“数据库健康”是 `diagnose db`，而不是 `diagnose db-health`；“策略”是 `db policies`，而不是 `diagnose policies`）。

| 基础组件 (command) | 您将看到的内容 | 参考 |
|---------------------|-------------|-----------|
| **日志** (`logs <source>`；`diagnose logs` 用于跨源聚合) | 来自 5 个后端源的 事件时间流 (`insforge.logs` / `postgREST.logs` / `postgres.logs` / `function.logs` / `function-deploy.logs`) | [references/logs.md](references/logs.md) |
| **指标** (`diagnose metrics`) | EC2 实例时间序列（CPU / 内存 / 磁盘 / 网络）在 `1h` / `6h` / `24h` / `7d` 内 | [references/metrics.md](references/metrics.md) |
| **数据库健康** (`diagnose db`) | 通过 7 个命名检查（`connections` / `slow-queries` / `bloat` / `size` / `index-usage` / `locks` / `cache-hit`）提供的当前 Postgres 状态 | [references/db-health.md](references/db-health.md) |
| **顾问** (`diagnose advisor --json`) | 跨 3 个类别（`security` / `performance` / `health`）的静态扫描问题，带有 `ruleId` / `affectedObject` / `recommendation` | [references/advisor.md](references/advisor.md) |
| **策略** (`db policies`) | 来自 `pg_policies` 的活动 RLS 规则（每个命令每个角色 `USING` / `WITH CHECK`）——返回所有策略的转储 | [references/policies.md](references/policies.md) |
| **元数据** (`metadata --json`) | 声明式后端状态转储（认证配置 / 表 / 存储桶 / 函数 / AI 模型 / 实时通道） | [references/metadata.md](references/metadata.md) |
| **错误对象**（无命令——读取 SDK / HTTP 响应） | SDK 错误包 + HTTP 状态——从客户端可见错误到正确日志源的路由表 | [references/error-objects.md](references/error-objects.md) |
| **部署状态** (`deployments list` + `deployments status <id> --json` + `logs function-deploy.logs`) | 前端（Vercel）部署历史记录 + 每个部署的元数据，以及边缘函数部署日志 | [references/deploy-state.md](references/deploy-state.md) |
| **AI 辅助** (`diagnose --ai "<description>"`) | 结合其他基础组件的 LLM 代理——返回带有建议的诊断 | [references/ai-assisted.md](references/ai-assisted.md) |

## 症状配方

每个配方是一个基础组件调用序列，每一步都有一个单行“查找 X”的说明。命令语法、标志和深度解释在上述每个基础组件的参考中。

### 配方：SDK 返回 `{ data: null, error: { code, message } }`

1. **error-objects** — 读取 code/message/details。如果 code 以 `PGRST*` 开头，请使用参考中的前缀进行路由。
2. **logs**（根据 error-objects 路由匹配的源）— 找到错误时间戳，获取完整的后端上下文。
3. **db-health** (`connections`, `locks`, `slow-queries`) — 仅当错误提示数据库问题时（PostgREST 超时、锁冲突）。

### 配方：特定请求上的 HTTP 4xx/5xx 响应

1. **error-objects** — 使用 HTTP 状态路由表选择日志源（每个状态都有不同的路径；429 是特殊的）。
2. **logs**（正确的源）— 找到失败的请求行和错误。
3. **metrics** — 仅用于跨多个端点的 5xx 模式，以确认系统范围的负载问题。

### 配方：RLS 访问问题（写入时 403，读取时为空结果）

> 同一个错误，两种表面。写入（INSERT / UPDATE / DELETE）会大声报 **403** 错误。读取（SELECT）会静默返回空数组——PostgREST 会过滤掉拒绝的行，而不是返回 403，因此请求看起来成功且没有行。诊断路径与步骤 1 仅适用于 403 变体的 403 变体相同。

1. **logs** (`postgREST.logs`) — *403 变体仅*：找到具有表和角色上下文的策略违规事件。*空结果变体*：跳过——没有记录静默过滤的行的错误。
2. **policies** — 列出该表的策略；根据实际请求和使用的 JWT 声明逐步检查 USING / WITH CHECK。
3. **metadata** — 验证认证配置（哪个声明提供 `auth.uid()` / `requesting_user_id()`；对于 Clerk/Auth0 等第三方认证，提供者是否注册为 JWT 发行者？）。
4. **db 查询** (`db query "<sql>"`) — *空结果变体仅*：通过作为服务角色（而不是用户）查询来确认应该可见的行确实存在：`npx -y @insforge/cli db query "SELECT id, user_id FROM <table>"`。区分“RLS 过滤了所有内容”和“没有匹配的数据存在”。

### 配方：登录失败 / OAuth 回调错误 / 令牌过期

1. **logs** (`insforge.logs`) — 找到带有时间戳和提供者上下文的认证错误。
2. **metadata** — 验证提供者已启用，重定向 URL 与回调 URL 完全匹配（协议 + 主机 + 路径）。

### 配方：边缘函数运行时错误 / 超时

1. **logs** (`function.logs`) — 获取错误堆栈和执行上下文。
2. **metadata** — 确认函数存在且 `status: "active"`。
3. （如果需要）`npx -y @insforge/cli functions code <slug>` — 检查源代码以查找明显问题。

### 配方：`functions deploy` 失败

1. **deploy-state** (`function-deploy.logs`) — 找到构建/推送错误。
2. **metadata** — 确认函数是否出现在活动列表中（部分部署检测）。

### 配方：`deployments deploy` 失败（Vercel）

1. **deploy-state** (`deployments list` + `status <id> --json`) — 读取 `status`、`metadata.webhookEventType` 和 `envVarKeys`。
2. **本地** `npm run build` — 在本地重现相同的错误以进行更快的迭代。

### 配方：单个慢查询 / 一个端点慢

1. **logs** (`postgres.logs`) — 找到查询文本和时间戳。
2. **db-health** (`slow-queries`, `index-usage`) — `slow-queries` 仅在运行时（>5s 快照）捕获；检查 `index-usage` 以查找缺失的索引。已经完成？**advisor** (`--category performance --json`) 有 `pg_stat_statements` 文本 + 平均时间；步骤 1 有时间戳。
3. **policies** — 如果它是 RLS 控制的表，请验证策略没有添加隐藏的连接。

### 配方：“内存约为 80%，但没有任何东西慢”

1. **预期——首先说明。** 专用 Postgres 实例将空闲 RAM 转换为共享缓冲区和页面缓存；稳定的内存高负载和低流量是其健康状态，而不是泄漏 ([references/metrics.md](references/metrics.md)，"内存：高是正常的")。
2. **metrics** (`--range 24h`) — 仅当 *上升* 趋势或 OOM 杀死/重启改变答案时。OOM 证据存在于 `postgres.logs` 中，作为崩溃恢复后的后果（“由于另一个服务器进程崩溃而终止连接” / “自动恢复正在进行中”）。
3. 有 OOM 证据时，修复方法是留出空间：升级到付费计划并选择更大的实例大小（仪表板 → 项目设置 → 计算 & 磁盘）。在真实负载下最小的实例上出现 OOM 是常见的和预期的——永远不要“重启以释放内存”。

### 配方：所有响应慢 / 高 CPU/内存（活跃事件）

1. **metrics** (`--range 1h`) — 确认系统范围的压力（CPU / 内存 / 磁盘）。
2. **db-health** — DB 是最常见的瓶颈；检查 `connections`、`locks`、`slow-queries`。
3. **logs** (`diagnose logs` 聚合) — 在峰值时间戳时跨源的错误模式。
4. **advisor** (`--severity critical`) — 可能解释退化预存的已知问题。

### 配方：实时通道无法连接 / 消息丢失

1. **logs** (`insforge.logs`) — WebSocket 错误和订阅失败。
2. **metadata** — 验证通道模式与客户端订阅的匹配，`enabled: true`。
3. **policies** — 基于表的 RLS（实时传递行更改；RLS 隔离订阅者看到的行）。

### 配方：429 速率限制

1. **error-objects** — 确认 429 状态。**没有记录 429 的日志；没有返回 `Retry-After` 标头。** 不要浪费时间搜索日志。
2. **metrics** (`--range 1h`) — 整个后端负载上下文。
3. **修复始终是客户端端**：防抖、批量处理、指数退避、消除重试循环。

### 配方：特定 URL 上的网关超时（502 / 503 / 504）

路由到 URL 子系统后再深入挖掘：

| URL 模式 | 深入挖掘 |
|-------------|-----------|
| `/api/database/records/...` | **logs** (`postgREST.logs` → `postgres.logs`) + **db-health** (`locks`, `slow-queries`) |
| `/functions/<slug>` | **logs** (`function.logs`) — 函数可能正在循环崩溃 |
| `/api/auth/...` | **logs** (`insforge.logs`) |
| 系统范围峰值期间的任何路径 | **metrics** (`--range 1h`) |

**504 跨 *无关* 路径在小型实例上：首先怀疑 OOM。** 系统范围峰值时同时击中数据库、认证和函数的间歇性网关超时是小型实例上内存不足的经典特征：内核杀死 Postgres，每个正在进行的请求在网关超时，同时运行崩溃恢复，然后在下一个负载峰值时重复。

**快速路径：`npx -y @insforge/cli diagnose incident`**（需要平台登录）。报告完全在云端构建——Prometheus 抓取历史记录、平台记录、外向数据库探测——因此即使在实例宕机或卡住时也能工作，正好是 `diagnose logs` 停止响应时。它返回一个判断（`oom_likely`、`platform_operation_in_progress`、`paused_or_suspended`、`metrics_stopped`、`down_unknown`、`no_incident_detected`）以及证据和建议的操作；`oom_likely` 已经意味着平台侧的重启/内存相关性检查已通过。

如果命令不可用（较旧的 CLI/后端，`--api-key` 链接模式），请手动在 **logs** (`postgres.logs`) 中确认——通过崩溃恢复后的后果（“由于另一个服务器进程崩溃而终止连接” / “自动恢复正在进行中”）**与 5xx 爆发时间相关**：仅凭恢复证据只能证明不干净的 Postgres 重启，因此时间戳必须对齐，OOM 才会成为首要诊断
([references/metrics.md](references/metrics.md))。有证据时，修复方法是留出空间，而不是重试循环：

1. **升级实例** — `npx -y @insforge/cli projects upgrade-instance <type>`
   (`nano` → `micro` → `small` → `medium` → `large` → `xl`)，或仪表板 → 项目设置 → 计算 & 磁盘。在免费计划上，首先升级到付费计划，然后选择大小。调整大小会改变账单，CLI 会要求交互式确认——首先获得用户的许可，然后使用 CLI 级别的 `--yes`（`npx -y` 中的 `-y` 是 npm 的安装标志，不是确认跳过）。调整大小是异步的——轮询 `projects get` 直到 `operation_status` 清除，然后宣布事件已解决。
2. 调整大小**作为更改的一部分重启项目**，这也清除了卡住的状态——没有单独的用户界面重启，并且裸重启只会买几分钟，然后下一个峰值 OOM 会再次发生。在真实负载下最小的实例上出现 OOM 是常见的和预期的，不是错误。

### 配方：发布前 / 主动审计

> 需要 Platform 登录 (`npx -y @insforge/cli login`)。**当项目通过 `--api-key` 链接时不可用**——在这种情况下，回退到 `db-health` + `policies` + `metadata` 进行手动审计。

1. **advisor** — 全扫描，然后 `--severity critical` 优先，然后警告。
2. **advisor** (`--category security`) — 专注于安全问题；与 **policies** (RLS 覆盖) 和 **metadata**（认证配置、公共存储桶、秘密存在）交叉验证。
3. **advisor** (`--category performance`) — 与 **db-health** (`slow-queries`, `index-usage`, `bloat`) 交叉验证。
4. **advisor** (`--category health`) — 与 **metrics**（资源趋势 `7d` 内）交叉验证。
5. 修复后，重新运行 **advisor** 并确认每个解决的 `ruleId` 的 `isResolved: true`。

### 配方：不知道从哪里开始

1. **ai-assisted** (`diagnose --ai "<错误或 URL>"`) — 获取起始假设。
2. **验证** 通过重新检查诊断引用的基础组件。信任基础组件的观察结果而不是建议。

## 当根本原因是 InsForge 本身

一些诊断在 InsForge 端的缺陷处结束，而不是项目配置错误：平台错误或回归、行为异常的 SDK 调用、与观察到的行为矛盾的文档或技能，或缺失的功能。调试会话正是确认这些的地方——在证据在手时报告它们：

```bash
npx -y @insforge/cli feedback --json \
  --type bug --component backend --area db \
  --title "<一句话摘要>" \
  --detail "<发生了什么与预期不符，最小重放>" \
  --command "<失败的调用>" \
  --error "<日志中的逐字错误>" \
  --workaround "<你做了什么替代方案>"
```

不需要登录；常见的 PII 模式（电子邮件、凭证/密钥格式、公共 IP、主目录用户名）在本地被过滤——基于模式，因此仍然保持用户数据。使用 `--component sdk --language <lang>` 用于 SDK 缺陷；`--component docs` 或 `--component skills` 与 `--doc` 和 `--expected` 当文档与现实矛盾时；`--type feature-request` 当发现是“不支持”时。然后继续用户的任务，使用替代方案——永远不要因为报告而阻塞，也永远不要为用户自己的应用代码或配置中的问题提交反馈。完整标志参考：**insforge-cli** 技能的 Feedback 部分。
