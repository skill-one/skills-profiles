# pup (Datadog CLI)

Datadog API 操作的 Pup CLI。支持 OAuth2 和 API 密钥认证。

## 快速参考

| 任务 | 命令 |
|------|---------|
| 搜索错误日志 | `pup logs search --query "status:error" --from 1h` |
| 列出监控器 | `pup monitors list` |
| 比较监控器定义 | `pup monitors diff <monitor-id> monitor.json` |
| 安排监控器停机时间 | `pup downtime create --file downtime.json` |
| 在实时时间窗口中打开仪表板 | `pup dashboards url <dashboard-id> --from now-1h --to now --live true` |
| 查找服务最近的慢追踪（最后 1 小时） | `pup traces search --query "service:<service-name> @duration:>500ms" --from 1h` |
| 列出事件 | `pup incidents list --limit 50` |
| 导入事件负载 | `pup incidents import --file incident.json` |
| 查询指标 | `pup metrics query --query "avg:system.cpu.user{*}"` |
| 列出主机 | `pup infrastructure hosts list --count 50` |
| 检查 SLO | `pup slos list` |
| 当班团队 | `pup on-call teams list` |
| 分流开放的关键安全信号（最后 1 小时） | `pup security signals list --query "status:open severity:critical" --from 1h --limit 100` |
| 搜索审计日志 | `pup audit-logs search --query "@action:deleted" --from 24h` |
| 按用户审计活动 | `pup audit-logs search --query "@usr.email:user@example.com" --from 7d` |
| 调查 API 密钥 | `pup audit-logs search --query "@metadata.api_key.id:KEY_ID" --from 90d` |
| 检查认证 | `pup auth status` |
| 令牌过期（剩余时间） | `pup auth status` |
| 刷新令牌 | `pup auth refresh` |

## 前置条件

使用 [安装说明](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup) 安装 pup。

## 必需输入解析

对于需要特定作用域值（`<env>`、`<service-name>`、`<team-id>`、资源 ID）的命令，请按以下顺序使用：

1. 首先检查上下文（对话历史记录、先前的命令输出、保存的变量）。
2. 如果缺失，首先运行发现命令（列出/搜索）以获取有效值。
3. 如果仍然缺失或模糊不清，请要求用户确认确切值。
4. 然后运行目标命令。
5. 永远不要运行带有未解析占位符（如 `<env>` 或 `<monitor-id>`）的命令。

## 认证

```bash
pup auth login          # OAuth2 浏览器流程（推荐）
pup auth status         # 检查令牌有效性
pup auth refresh        # 刷新过期令牌（无需浏览器）
pup auth logout         # 清除凭证
```

**令牌过期（约 1 小时）。** 如果在对话中途命令失败并返回 401/403：

```bash
pup auth refresh        # 首先尝试刷新
pup auth login          # 如果刷新失败，则完整重新认证
```

如果 Chrome 打开了错误的配置文件/窗口，请使用 `pup auth login` 打印的一次性 OAuth URL（`If the browser doesn't open, visit: ...`）并手动在正确的账户会话中打开该链接。

### 无头/CI（无浏览器）

```bash
# 使用环境变量或：
export DD_API_KEY=your-api-key
export DD_APP_KEY=your-app-key
export DD_SITE=datadoghq.com    # 或 datadoghq.eu，等
```

## 命令参考

### 监控器
```bash
pup monitors list --limit 10
pup monitors list --tags "env:<env>"
pup monitors get <monitor-id>
pup monitors search --query "<monitor-name>"
pup monitors create --file monitor.json
pup monitors update <monitor-id> --file monitor.json
pup monitors diff <monitor-id> monitor.json
pup monitors delete <monitor-id>
# 没有 pup monitors mute/unmute 命令；请使用停机时间负载代替。
pup downtime create --file downtime.json
```

### 日志
```bash
pup logs search --query "status:error" --from 1h
pup logs search --query "service:<service-name>" --from 1h --limit 100
pup logs search --query "@http.status_code:5*" --from 24h
pup logs search --query "env:<env> level:error" --from 1h
pup logs aggregate --query "service:<service-name>" --compute count --from 1h
```

### 指标
```bash
pup metrics query --query "avg:system.cpu.user{*}" --from 1h --to now
pup metrics query --query "sum:trace.express.request.hits{service:<service-name>}" --from 1h --to now
pup metrics list --filter "system.*"
```

### APM / 追踪
```bash
# 首先向用户确认环境标签（不要假设生产/prod/prd）。
pup apm services list --env <env> --from 1h --to now
pup traces search --query "service:<service-name>" --from 1h
pup traces search --query "service:<service-name> @duration:>500ms" --from 1h
pup traces search --query "service:<service-name> status:error" --from 1h
```

### 事件
```bash
pup incidents list --limit 50
pup incidents get <incident-id>
pup incidents import --file incident.json
```

### 仪表板
```bash
pup dashboards list
pup dashboards get <dashboard-id> --read-only
pup dashboards url <dashboard-id> --from now-1h --to now --live true
pup dashboards create --file dashboard.json
pup dashboards update <dashboard-id> --file dashboard.json
pup dashboards delete <dashboard-id>
```

#### 安全的仪表板创建、克隆和更新工作流

目标是可恢复的源和一个经过验证的目标。仅 API 响应成功并不能证明小部件内容或位置已保留。

1. 使用 `--read-only` 获取源或更新目标，并将确切响应保存为不可变的快照。切勿用转换后的 JSON 覆盖此文件。
   ```bash
   pup dashboards get <dashboard-id> --read-only -o json > dashboard-source.json
   ```
2. 构建一个单独的突变负载。在创建/更新之前删除响应字段：`author_handle`、`author_name`、`created_at`、`id`、`modified_at` 和 `url`。
   ```bash
   jq 'del(.author_handle, .author_name, .created_at, .id, .modified_at, .url)' \
     dashboard-source.json > dashboard-payload.json
   ```
3. 对于备份或克隆，保持源仪表板不变，仅更改明确请求的字段，通常是 `title` 或 `description`。保留 `layout_type`、`reflow_type`、小部件顺序和每个递归小部件 `layout` 对象（`x`、`y`、`width`、`height` 和 `is_column_break`）。重新打包或压缩坐标会创建派生布局，而不是精确克隆。
4. 使用 `dashboard-payload.json` 创建或更新，然后将目标获取到新文件中。
   ```bash
   pup dashboards create --file dashboard-payload.json
   pup dashboards get <destination-id> --read-only -o json > dashboard-destination.json
   ```
5. 移除响应字段并比较完整定义。唯一差异应该是故意更改的字段。
6. 还应单独比较布局投影，以便放置回归不会隐藏在大型小部件差异中：
   ```bash
   jq '{layout_type, reflow_type, layouts: [.. | objects | .layout? // empty]}' dashboard-source.json
   jq '{layout_type, reflow_type, layouts: [.. | objects | .layout? // empty]}' dashboard-destination.json
   ```

Pup 1.6.3 暂不暴露仪表板版本历史记录。如果需要精确的历史版本且不存在不可变的快照，请在更改仪表板之前在 Datadog UI 中检查版本历史记录。

### SLO
```bash
pup slos list
pup slos get <slo-id>
pup slos status <slo-id> --from 30d --to now
pup slos create --file slo.json
```

### 合成
```bash
pup synthetics tests list
pup synthetics tests get <test-id>
pup synthetics tests search --text "login"
pup synthetics locations list
```

### 当班
```bash
pup on-call teams list
# 从 `pup on-call teams list` 输出中选择一个真实的团队 ID。
pup on-call teams get <team-id>
pup on-call teams memberships list <team-id>
```

### 主机 / 基础设施
```bash
pup infrastructure hosts list --count 50
pup infrastructure hosts list --filter "env:<env>"
pup infrastructure hosts get <host-name>
```

### 事件
```bash
pup events list --from 24h
pup events list --tags "source:deploy"
pup events search --query "deploy" --from 24h --limit 50
pup events get <event-id>
```

### 停机时间
```bash
pup downtime list
pup downtime create --file downtime.json
pup downtime cancel <downtime-id>
```

### 用户 / 团队
```bash
pup users list
pup users get <user-id>
```

### 安全
```bash
pup security signals list --query "*" --from 1h --limit 100
pup security signals list --query "status:open severity:critical" --from 1h --limit 100
# 更长的时间回溯用于历史分流
pup security signals list --query "severity:critical" --from 24h --limit 100
```

### 审计日志
```bash
# 列出最近的事件
pup audit-logs list --from 1h --limit 100

# 使用查询（Lucene 语法，与日志探索器相同）
pup audit-logs search --query "@action:deleted" --from 24h
pup audit-logs search --query "@usr.email:user@example.com" --from 7d
pup audit-logs search --query "@evt.name:Authentication @action:login" --from 7d
pup audit-logs search --query "@metadata.api_key.id:KEY_ID" --from 90d --limit 200

# JSON 输出用于管道到 jq
pup audit-logs search --query "@action:deleted" --from 24h -o json | jq '.data[].attributes'

# audit-logs 是长形式（两者都有效）
pup audit-logs search --query "@evt.name:Monitor @action:modified" --from 7d
```

### 服务目录
```bash
pup service-catalog list
pup service-catalog get <service-name>
```

### 笔记本
```bash
pup notebooks list
pup notebooks get <notebook-id>
```

### 工作流
```bash
pup workflows get <workflow-id>
pup workflows run <workflow-id> --payload '{"key":"value"}'
pup workflows instances list <workflow-id>
```

### 可观察性管道
```bash
pup obs-pipelines list --limit 50
pup obs-pipelines get <pipeline-id>
pup obs-pipelines create --file pipeline.json
pup obs-pipelines update <pipeline-id> --file pipeline.json
pup obs-pipelines delete <pipeline-id>
pup obs-pipelines validate --file pipeline.json
```

### LLM 可观察性
```bash
pup llm-obs projects list
pup llm-obs projects create --file project.json
pup llm-obs experiments list
pup llm-obs experiments list --filter-project-id <project-id>
pup llm-obs experiments list --filter-dataset-id <dataset-id>
pup llm-obs experiments create --file experiment.json
pup llm-obs experiments update <experiment-id> --file experiment.json
pup llm-obs experiments delete --file delete-request.json
pup llm-obs datasets list --project-id <project-id>
pup llm-obs datasets create --project-id <project-id> --file dataset.json
pup llm-obs spans search --ml-app <ml-app-name> --from 1h --limit 20
```

### 参考表格
```bash
pup reference-tables list --limit 50
pup reference-tables get <table-id>
pup reference-tables create --file table.json
pup reference-tables batch-query --file query.json
```

### 成本云配置
```bash
# AWS CUR 配置
pup cost aws-config list
pup cost aws-config get <account-id>
pup cost aws-config create --file config.json
pup cost aws-config delete <account-id>

# Azure UC 配置
pup cost azure-config list
pup cost azure-config get <account-id>
pup cost azure-config create --file config.json
pup cost azure-config delete <account-id>

# GCP 使用成本配置
pup cost gcp-config list
pup cost gcp-config get <account-id>
pup cost gcp-config create --file config.json
pup cost gcp-config delete <account-id>
```

## 子命令发现

```bash
pup --version           # 在记录解决方案之前确认安装版本
pup --help              # 列出所有命令
pup <command> --help    # 命令特定帮助
pup dashboards get <dashboard-id> --jq '{title, layout_type}'  # 在格式化之前过滤输出
```

如果本地帮助与此技能不同，请比较 `pup --version` 与最新稳定版本，然后再发明解决方案。

## 错误处理

| 错误 | 原因 | 修复 |
|-------|-------|-----|
| 401 未授权 | 令牌过期 | `pup auth refresh` |
| 403 禁止 | 缺少作用域 | 检查应用密钥权限 |
| 404 未找到 | 错误的 ID/资源 | 验证资源是否存在 |
| 速率限制 | 请求过多 | 在调用之间添加延迟 |

## 安装

参见 [设置 Pup](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup) 获取安装说明。

### 验证安装

```bash
which pup
pup --version
```

## 网站

| 网站 | `DD_SITE` 值 |
|------|-----------------|
| US1 (默认) | `datadoghq.com` |
| US3 | `us3.datadoghq.com` |
| US5 | `us5.datadoghq.com` |
| EU1 | `datadoghq.eu` |
| AP1 | `ap1.datadoghq.com` |
| AP2 | `ap2.datadoghq.com` |
| US1-FED | `ddog-gov.com` |
