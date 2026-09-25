# Azure 资源查询

列出、查找和发现跨订阅和资源组的任何类型 Azure 资源。使用 Azure 资源图 (ARG) 进行快速、跨领域的查询，当专用 MCP 工具不涵盖资源类型时。

## 使用此技能的场景

当用户想要时，使用此技能：
- **列出**任何类型的资源（虚拟机、Web 应用、存储账户、容器应用、数据库等）
- **显示**特定订阅或资源组中的资源
- 查询跨多个订阅或资源类型的资源
- 查找**遗弃资源**（未附加的磁盘、未使用的 NIC、空闲 IP）
- 发现**缺少必需标签**或配置的资源
- 获取**跨多种类型的资源清单**
- 查找处于**特定状态**的资源（不健康、部署失败、已停止）
- 回答“**我有哪些资源？**”或“**显示我的 Azure 资源**”
- **列出 Web 应用、网站或 App Services**

> ⚠️ **警告**：App Service / Web Apps 没有专用的 MCP `list` 命令。像“list websites”、“list web apps”或“list app services”这样的提示**必须**通过此技能使用 Azure 资源图。

> 💡 **提示**：对于单类型资源查询，首先检查是否有专用的 MCP 工具可以处理（见下方的路由表）。如果没有，请使用 Azure 资源图。

## 快速参考

| 属性 | 值 |
|----------|-------|
| **查询语言** | KQL（Kusto 查询语言子集） |
| **CLI 命令** | `az graph query -q "<KQL>" -o table` |
| **扩展** | `az extension add --name resource-graph` |
| **MCP 工具** | `extension_cli_generate`，意图为 `az graph query` |
| **适用场景** | 跨订阅查询、遗弃资源、标签审计 |

## MCP 工具

| 工具 | 目的 | 使用场景 |
|------|---------|-------------|
| `extension_cli_generate` | 生成 `az graph query` 命令 | 主要工具——根据用户意图生成 ARG 查询 |
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 | 查询前发现订阅范围 |
| `mcp_azure_mcp_group_list` | 列出资源组 | 缩小查询范围 |

## 工作流程

### 第 1 步：检查是否有专用 MCP 工具

对于单类型资源查询，检查是否有专用的 MCP 工具可以处理：

| 资源类型 | MCP 工具 | 覆盖范围 |
|---|---|---|
| 虚拟机 | `compute` | ✅ 全部——列出、详情、规格 |
| 存储账户 | `storage` | ✅ 全部——账户、Blob、表 |
| Cosmos DB | `cosmos` | ✅ 全部——账户、数据库、查询 |
| 密钥保管库 | `keyvault` | ⚠️ 部分支持——仅限密钥/密钥，无保管库列表 |
| SQL 数据库 | `sql` | ⚠️ 部分支持——需要资源组名称 |
| 容器注册中心 | `acr` | ✅ 全部——列出注册中心 |
| Kubernetes (AKS) | `aks` | ✅ 全部——集群、节点池 |
| App Service / Web Apps | `appservice` | ❌ 无列表命令——使用 ARG |
| 容器应用 | — | ❌ 无 MCP 工具——使用 ARG |
| 事件中心 | `eventhubs` | ✅ 全部——命名空间、中心 |
| 服务总线 | `servicebus` | ✅ 全部——队列、主题 |

如果存在全覆盖的专用工具，请使用它。否则，继续第 2 步。

### 第 2 步：生成 ARG 查询

使用 `extension_cli_generate` 构建的 `az graph query` 命令：

```yaml
mcp_azure_mcp_extension_cli_generate
  intent: "query Azure Resource Graph to <user's request>"
  cli-type: "az"
```

见 [Azure 资源图查询模式](references/azure-resource-graph.md) 以获取常见 KQL 模式。

### 第 3 步：执行和格式化结果

运行生成的命令。使用 `--query`（JMESPath）来调整输出：

```bash
az graph query -q "<KQL>" --query "data[].{name:name, type:type, rg:resourceGroup}" -o table
```

使用 `--first N` 限制结果。使用 `--subscriptions` 来限定范围。

## 错误处理

| 错误 | 原因 | 解决方法 |
|-------|-------|-----|
| `resource-graph extension not found` | 扩展未安装 | `az extension add --name resource-graph` |
| `AuthorizationFailed` | 没有订阅的读取权限 | 检查 RBAC——需要 Reader 角色 |
| 查询时 `BadRequest` | 无效的 KQL 语法 | 验证表/列名称；使用 `=~` 进行不区分大小写的类型匹配 |
| 空结果 | 没有匹配的资源或范围错误 | 检查 `--subscriptions` 标志；验证资源类型拼写 |

## 限制

- ✅ **始终**使用 `=~` 进行不区分大小写的类型匹配（类型为小写）
- ✅ **始终**使用 `--subscriptions` 或 `--first` 为大型租户限定查询
- ✅ **优先**使用专用 MCP 工具进行单类型资源查询
- ❌ **永不**使用 ARG 进行实时监控（数据有轻微延迟）
- ❌ **永不**尝试通过 ARG 进行变更（只读）
