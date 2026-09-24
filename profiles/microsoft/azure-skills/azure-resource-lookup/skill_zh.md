# Azure Resource Lookup

列出、查找并发现跨订阅和资源组的所有类型 Azure 资源。当专用 MCP 工具无法涵盖某种资源类型时，使用 Azure Resource Graph (ARG) 进行快速、跨领域查询。

## 何时使用此技能

当用户需要以下情况时使用此技能：
- **列出任意类型的资源**（虚拟机、Web 应用、存储账户、容器应用、数据库等。）
- **在特定订阅或资源组中显示资源**
- 跨多个订阅或资源类型查询资源
- 查找**孤立资源**（未挂载磁盘、未使用的 NIC、闲置 IP）
- 发现**缺少必需标签或配置**的资源
- 获取跨多种类型的**资源清单**
- 查找处于**特定状态**的资源（不健康、配置失败、已停止）
- 回答"**我有哪些资源？**"或"**显示我的 Azure 资源**"
- **列出 Web 应用、网站或 App Service**

> ⚠️ **警告：** App Service / Web 应用没有专用的 MCP `list` 命令。像"list websites"、"list web apps"或"list app services"这类提示**必须**通过此技能路由，使用 Azure Resource Graph。

> 💡 **提示：** 对于单一资源类型的查询，首先检查是否有专用的 MCP 工具可以处理（参见下方的路由表）。如果不存在，则使用 Azure Resource Graph。

## 快速参考

| 属性 | 值 |
|------|-----|
| **查询语言** | KQL（Kusto 查询语言子集） |
| **CLI 命令** | `az graph query -q "<KQL>" -o table` |
| **扩展** | `az extension add --name resource-graph` |
| **MCP 工具** | `extension_cli_generate`，带有针对 `az graph query` 的意图 |
| **最佳适用场景** | 跨订阅查询、孤立资源、标签审计 |

## MCP 工具

| 工具 | 用途 | 何时使用 |
|------|------|-------------|
| `extension_cli_generate` | 生成 `az graph query` 命令 | 主要工具——根据用户意图生成 ARG 查询 |
| `mcp_azure_mcp_subscription_list` | 列出可用订阅 | 查询前发现订阅范围 |
| `mcp_azure_mcp_group_list` | 列出资源组 | 缩小查询范围 |

## 工作流程

### 步骤 1：检查是否有专用的 MCP 工具

对于单一资源类型的查询，检查是否有专用的 MCP 工具可以处理：

| 资源类型 | MCP 工具 | 覆盖情况 |
|---|---|---|
| 虚拟机 | `compute` | ✅ 完整——列出、详情、尺寸 |
| 存储账户 | `storage` | ✅ 完整——账户、Blob、表 |
| Cosmos DB | `cosmos` | ✅ 完整——账户、数据库、查询 |
| Key Vault | `keyvault` | ⚠️ 部分——仅限密钥，无保险库列表 |
| SQL 数据库 | `sql` | ⚠️ 部分——需要资源组名称 |
| 容器注册表 | `acr` | ✅ 完整——列出注册表 |
| Kubernetes (AKS) | `aks` | ✅ 完整——集群、节点池 |
| App Service / Web 应用 | `appservice` | ❌ 无列表命令——使用 ARG |
| 容器应用 | — | ❌ 无 MCP 工具——使用 ARG |
| Event Hubs | `eventhubs` | ✅ 完整——命名空间、枢纽 |
| Service Bus | `servicebus` | ✅ 完整——队列、主题 |

如果有专用的工具且具有完整覆盖，请使用它。否则继续执行步骤 2。

### 步骤 2：生成 ARG 查询

使用 `extension_cli_generate` 构建 `az graph query` 命令：

```yaml
mcp_azure_mcp_extension_cli_generate
  intent: "query Azure Resource Graph to <user's request>"
  cli-type: "az"
```

参见[Azure Resource Graph 查询模式](references/azure-resource-graph.md)了解常见的 KQL 模式。

### 步骤 3：执行并格式化结果

运行生成的命令。使用 `--query`（JMESPath）来塑形输出：

```bash
az graph query -q "<KQL>" --query "data[].{name:name, type:type, rg:resourceGroup}" -o table
```

使用 `--first N` 限制结果数量。使用 `--subscriptions` 进行范围限定。

## 错误处理

| 错误 | 原因 | 解决方案 |
|-------|-------|-----|
| **resource-graph extension not found** | 扩展未安装 | `az extension add --name resource-graph` |
| `AuthorizationFailed` | 没有订阅的读取访问权限 | 检查 RBAC——需要 Reader 角色 |
| 查询时出现 `BadRequest` | KQL 语法无效 | 验证表/列名；使用 `=~` 进行不区分大小写的类型匹配 |
| **结果为空** | 没有匹配的资源或范围错误 | 检查 `--subscriptions` 标志；验证资源类型拼写 |

## 约束

- ✅ **始终**使用 `=~` 进行不区分大小写的类型匹配（类型为小写）
- ✅ **始终**对于大型租户的查询使用 `--subscriptions` 或 `--first` 进行范围限定
- ✅ **优先**使用专用 MCP 工具进行单一资源类型查询
- ❌ **切勿**使用 ARG 进行实时监控（数据存在轻微延迟）
- ❌ **切勿**通过 ARG 尝试变更操作（仅只读）
