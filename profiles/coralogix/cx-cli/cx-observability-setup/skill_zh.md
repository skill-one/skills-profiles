# 可观测性设置技能

在设置或配置可观测性堆栈时使用此技能 - 保存的视图、webhook 集成、通知渠道和外部集成。这是为新服务上线或重新配置通知管道的“第一天设置”技能。

---

## CLI 命令

### 视图

| 命令 | 目的 |
|---|---|
| `cx views list` | 列出所有保存的视图 |
| `cx views get <id>` | 获取视图定义 |
| `cx views create --from-file` | 创建保存的视图 |
| `cx views update <id> --from-file` | 更新保存的视图 |
| `cx views delete <id>` | 删除保存的视图 |
| `cx views folders list` | 列出视图文件夹 |
| `cx views folders get <id>` | 获取文件夹 |
| `cx views folders create --from-file` | 创建文件夹 |
| `cx views folders update <id> --from-file` | 更新文件夹 |
| `cx views folders delete <id>` | 删除文件夹 |

### Webhooks

| 命令 | 目的 |
|---|---|
| `cx webhooks list` | 列出所有外发 webhook |
| `cx webhooks get <id>` | 获取 webhook 详情 |
| `cx webhooks create --from-file` | 创建 webhook |
| `cx webhooks update <id> --from-file` | 更新 webhook |
| `cx webhooks delete <id>` | 删除 webhook |
| `cx webhooks test <id>` | 测试 webhook |
| `cx webhooks types` | 列出可用的 webhook 类型 |
| `cx webhooks actions list` | 列出自动化操作 |
| `cx webhooks actions get <id>` | 获取操作详情 |
| `cx webhooks actions create --from-file` | 创建操作 |
| `cx webhooks actions update --from-file` | 更新操作 |
| `cx webhooks actions delete <id>` | 删除操作 |
| `cx webhooks actions batch --from-file` | 批量执行操作 |
| `cx webhooks actions reorder --from-file` | 重新排序操作 |

### 通知

| 命令 | 目的 |
|---|---|
| `cx notifications connectors list` | 列出通知连接器 |
| `cx notifications connectors get <id>` | 获取连接器详情 |
| `cx notifications connectors create --from-file` | 创建连接器 |
| `cx notifications connectors update --from-file` | 更新连接器 |
| `cx notifications connectors delete <id>` | 删除连接器 |
| `cx notifications connectors types` | 列出连接器类型 |
| `cx notifications connectors entity-types` | 列出实体类型 |
| `cx notifications connectors entity-subtypes --type <type>` | 列出实体子类型 |
| `cx notifications routers list` | 列出通知路由器 |
| `cx notifications routers get <id>` | 获取路由器详情 |
| `cx notifications routers create --from-file` | 创建路由器 |
| `cx notifications routers update --from-file` | 更新路由器 |
| `cx notifications routers delete <id>` | 删除路由器 |
| `cx notifications routers validate-matcher --from-file` | 测试实体标签匹配器 |
| `cx notifications presets list` | 列出通知预设 |
| `cx notifications presets get <id>` | 获取预设详情 |
| `cx notifications presets create --from-file` | 创建自定义预设 |
| `cx notifications presets update --from-file` | 更新自定义预设 |
| `cx notifications presets delete <id>` | 删除自定义预设 |
| `cx notifications presets set-default <id>` | 设置默认预设 |
| `cx notifications test connector --from-file` | 测试连接器配置 |
| `cx notifications test destination --from-file` | 测试目标 |
| `cx notifications test preset --from-file` | 测试预设配置 |
| `cx notifications test routing-condition --from-file` | 测试路由条件 |
| `cx notifications test template-render --from-file` | 测试模板渲染 |

### 集成

| 命令 | 目的 |
|---|---|
| `cx integrations list` | 列出所有集成 |
| `cx integrations get <id>` | 获取集成详情 |
| `cx integrations create --from-file` | 创建集成 |
| `cx integrations update <id> --from-file` | 更新集成 |
| `cx integrations delete <id>` | 删除集成 |
| `cx integrations test --from-file` | 测试集成配置 |
| `cx integrations template` | 获取集成模板 |
| `cx integrations definition <id>` | 获取集成定义 |
| `cx integrations deployed <id>` | 获取已部署集成 |
| `cx integrations extensions list` | 列出可用扩展 |
| `cx integrations extensions get <id>` | 获取扩展详情 |
| `cx integrations extensions deployed` | 列出已部署扩展 |
| `cx integrations extensions deploy --from-file` | 部署扩展 |
| `cx integrations extensions update --from-file` | 更新已部署扩展 |
| `cx integrations extensions undeploy --from-file` | 卸载扩展 |
| `cx integrations contextual-data list` | 列出上下文数据集成 |
| `cx integrations contextual-data get <id>` | 获取上下文数据详情 |
| `cx integrations contextual-data create --from-file` | 创建上下文数据集成 |
| `cx integrations contextual-data update <id> --from-file` | 更新上下文数据集成 |
| `cx integrations contextual-data delete <id>` | 删除上下文数据集成 |
| `cx integrations contextual-data definition <id>` | 获取上下文数据定义 |
| `cx integrations contextual-data test <id>` | 测试上下文数据集成 |

所有命令支持 `-o json` 用于结构化输出和 `-p <profile>` 用于配置文件选择。

---

## 新服务设置工作流

在为新服务上线时，请遵循以下清单：

### 1. 创建保存的视图

为服务的关键日志查询设置视图：

```bash
cx views folders create --from-file folder.json
cx views create --from-file view.json
```

### 2. 设置通知连接器

配置渠道（Slack、PagerDuty、邮件）：

```bash
cx notifications connectors types -o json
cx notifications connectors create --from-file slack-connector.json
```

### 3. 配置通知路由

将警报路由到正确的渠道：

```bash
cx notifications routers create --from-file router.json
```

### 4. 设置 Webhooks

为外部集成配置外发 webhook：

```bash
cx webhooks types -o json
cx webhooks create --from-file webhook.json
cx webhooks test <webhook-id>
```

### 5. 安装集成

部署相关的集成和扩展：

```bash
cx integrations list -o json
cx integrations create --from-file integration.json
cx integrations extensions deploy --from-file extension.json
```

### 6. 创建仪表盘

使用 `cx-dashboards` 技能进行完整的仪表盘创建工作流。

### 7. 创建 SLO

使用 `cx-slos` 技能进行 SLO 创建和监控。

---

## 通知设置工作流

详细的通道配置：

### 1. 列出可用的连接器类型

```bash
cx notifications connectors types -o json
```

### 2. 创建连接器

```bash
cx notifications connectors create --from-file connector.json
```

### 3. 创建路由器

```bash
cx notifications routers create --from-file router.json
```

### 4. 分配或创建预设

```bash
cx notifications presets list -o json
cx notifications presets create --from-file preset.json
cx notifications presets set-default <preset-id>
```

### 5. 端到端测试

```bash
cx notifications test connector --from-file test-connector.json
cx notifications test destination --from-file test-destination.json
cx notifications test routing-condition --from-file test-condition.json
```

---

## Webhook 设置

### 1. 列出 Webhook 类型

```bash
cx webhooks types -o json
```

### 2. 创建 Webhook

如果可能，从现有的 webhook 获取模板：

```bash
cx webhooks get <existing-id> -o json > webhook-template.json
cx webhooks create --from-file webhook.json
```

### 3. 测试 Webhook

```bash
cx webhooks test <webhook-id>
```

### 4. 创建自动化操作（可选）

```bash
cx webhooks actions create --from-file action.json
cx webhooks actions reorder --from-file order.json
```

---

## 关键原则

- **设置后始终测试** - 使用 `cx notifications test`、`cx webhooks test`、`cx integrations test`
- **使用 `--from-file`** 用于复杂的 JSON 负载 - 从 stdin 管道或使用文件
- **从现有创建模板** - `cx <command> get <id> -o json > template.json` 在创建前
- **首先检查连接器类型** - `cx notifications connectors types` 和 `cx webhooks types` 在创建前

---

## 相关技能

- **`cx-dashboards`** - 仪表盘创建和替换工作流
- **`cx-slos`** - SLO 创建和错误预算监控
- **`cx-cases`** - 在警报触发时处理案例
- **`cx-alerts`** - 触发通知的警报定义
- **`cx-telemetry-querying`** - 设置后验证数据流
