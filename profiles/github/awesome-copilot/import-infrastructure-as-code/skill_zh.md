# 导入基础设施即代码（Azure -> Terraform with AVM）

使用发现数据和使用 Azure 验证模块将现有的 Azure 基础设施转换为可维护的 Terraform 代码。

## 使用此技能的场景

当用户要求执行以下操作时，使用此技能：

- 将现有的 Azure 资源导入 Terraform
- 从运行中的 Azure 环境生成 IaC
- 处理 AVM 支持的任何 Azure 资源类型（并记录非 AVM 回退的合理性）
- 从订阅或资源组重新创建基础设施
- 映射发现 Azure 资源之间的依赖关系
- 使用 AVM 模块而不是手写的 `azurerm_*` 资源

## 前提条件

- 已安装并认证 Azure CLI (`az login`)
- 可以访问目标订阅或资源组
- 已安装 Terraform CLI
- 可以访问 Terraform Registry 和 AVM 索引源的网络

## 输入

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `subscription-id` | 否 | 活动的 CLI 上下文 | 用于订阅范围发现和上下文设置的 Azure 订阅 |
| `resource-group-name` | 否 | 无 | 用于资源组范围发现的 Azure 资源组 |
| `resource-id` | 否 | 无 | 一个或多个用于特定资源范围发现的 Azure ARM 资源 ID |

至少需要 `subscription-id`、`resource-group-name` 或 `resource-id` 中的一个。

## 分步工作流程

### 1) 收集所需范围（必填）

在运行发现命令之前，请求以下范围之一：

- 订阅范围：`<subscription-id>`
- 资源组范围：`<resource-group-name>`
- 特定资源范围：一个或多个 `<resource-id>` 值

范围处理规则：

- 将 Azure ARM 资源 ID（例如 `/subscriptions/.../providers/...`）视为云资源标识符，而不是本地文件系统路径。
- 仅使用 Azure CLI `--ids` 参数（例如 `az resource show --ids <resource-id>`）。
- 除非用户明确说明是本地文件路径，否则不要将资源 ID 传递给文件读取命令（`cat`、`ls`、`read_file`、glob 搜索）。
- 如果用户已经提供了一个有效的范围，除非命令失败需要，否则不要请求额外的范围输入。
- 不要询问可以从已提供的范围值中回答的后续问题。

如果范围缺失，请明确请求并停止。

### 2) 认证并设置上下文

仅运行与所选范围相关的命令。

对于订阅范围：

```bash
az login
az account set --subscription <subscription-id>
az account show --query "{subscriptionId:id, name:name, tenantId:tenantId}" -o json
```

预期输出：包含 `subscriptionId`、`name` 和 `tenantId` 的 JSON 对象。

对于资源组或特定资源范围，`az login` 仍然是必需的，但如果活动上下文已经正确，则可以省略 `az account set`。

在使用特定资源范围时，优先使用基于 `--ids` 的直接命令，并避免除非需要具体命令否则对订阅或资源组进行额外的发现提示。

### 3) 运行发现命令

使用所选范围发现资源，并确保获取所有必要信息以准确生成 Terraform。

```bash
# 订阅范围
az resource list --subscription <subscription-id> -o json

# 资源组范围
az resource list --resource-group <resource-group-name> -o json

# 特定资源范围
az resource show --ids <resource-id-1> <resource-id-2> ... -o json
```

预期输出：包含 Azure 资源元数据（`id`、`type`、`name`、`location`、`tags`、`properties`）的 JSON 对象或数组。

### 4) 在代码生成之前解析依赖关系

解析导出的 JSON 并映射：

- 父子关系（例如：NIC -> Subnet -> VNet）
- 资源属性中的跨资源引用
- Terraform 创建的顺序

**重要提示**：生成以下文档并保存到项目根目录下的 docs 文件夹中。
- `exported-resources.json`，包含所有发现的资源和它们的元数据，包括依赖关系和引用。
- `EXPORTED-ARCHITECTURE.MD` 文件，基于发现的资源和它们的关系，提供人类可读的架构概述。

### 5) 选择 Azure 验证模块（必填）

为每种资源类型使用最新的 AVM 版本。

### Terraform Registry

- 搜索 "avm" + 资源名称
- 通过 "Partner" 标签筛选以找到官方 AVM 模块
- 示例：搜索 "avm storage account" → 通过 Partner 筛选

### 官方 AVM 索引

> **注意**：以下链接始终指向主分支上最新版本的 CSV 文件。按预期，这意味着文件可能会随时间变化。如果您需要某个时间点的版本，请考虑在 URL 中使用特定的发布标签。

- **Terraform 资源模块**：`https://raw.githubusercontent.com/Azure/Azure-Verified-Modules/refs/heads/main/docs/static/module-indexes/TerraformResourceModules.csv`
- **Terraform 模式模块**：`https://raw.githubusercontent.com/Azure/Azure-Verified-Modules/refs/heads/main/docs/static/module-indexes/TerraformPatternModules.csv`
- **Terraform 工具模块**：`https://raw.githubusercontent.com/Azure/Azure-Verified-Modules/refs/heads/main/docs/static/module-indexes/TerraformUtilityModules.csv`

### 单个模块信息

如果本地 `.terraform` 文件夹中不可用，使用 `web` 工具或其他合适的 MCP 方法获取模块信息。

使用 AVM 源：

- Registry: `https://registry.terraform.io/modules/Azure/<module>/azurerm/latest`
- GitHub: `https://github.com/Azure/terraform-azurerm-avm-res-<service>-<resource>`

当存在 AVM 模块时，优先使用 AVM 模块而不是手写的 `azurerm_*` 资源。

当从 GitHub 存储库获取模块信息时，存储库根目录中的 `README.md` 文件通常包含有关模块的所有详细信息，例如：https://raw.githubusercontent.com/Azure/terraform-azurerm-avm-res-<service>-<resource>/refs/heads/main/README.md

### 5a) 在编写任何代码之前阅读模块 README（必填）

**此步骤不是可选的。** 在为模块编写任何 HCL 之前，获取并阅读该模块的完整 README。不要依赖对原始 `azurerm` 提供者的了解或与其他 AVM 模块的先前经验。

对于每个选定的 AVM 模块，获取其 README：

```text
https://raw.githubusercontent.com/Azure/terraform-azurerm-avm-res-<service>-<resource>/refs/heads/main/README.md
```

或者如果模块在 `terraform init` 后已下载：

```bash
cat .terraform/modules/<module_key>/README.md
```

从 README 中提取并记录**在编写代码之前**：

1. **必需输入** — 模块要求的所有输入。此处列出的任何子资源（NIC、扩展、子网、公共 IP）都由模块**内部**管理。不要为这些资源创建独立的模块块。
2. **可选输入** — Terraform 变量名称及其声明的 `type`。
3. **使用示例** — 检查使用的资源组标识符（`parent_id` vs `resource_group_name`）、子资源表示方式（内联映射 vs 独立模块）以及每个输入的语法。

#### 将模块规则作为模式，而不是假设

使用以下示例作为经常导致导入失败的类型不匹配的示例。不要假设这些确切名称适用于每个 AVM 模块。始终验证每个选定模块的 README 和 `variables.tf`。

**`avm-res-compute-virtualmachine`（任何版本）**

- `network_interfaces` 是一个**必需输入**。NIC 由 VM 模块拥有。永远不要在 VM 模块旁边创建独立的 `avm-res-network-networkinterface` 模块 — 在 `network_interfaces` 下内联定义每个 NIC。
- TrustedLaunch 通过顶层布尔值 `secure_boot_enabled = true` 和 `vtpm_enabled = true` 表示。`security_type` 参数仅在 `os_disk` 下用于机密 VM 磁盘加密，并且不能用于 TrustedLaunch。
- `boot_diagnostics` 是一个 `bool`，而不是对象。使用 `boot_diagnostics = true`；如果需要存储 URI，请使用单独的 `boot_diagnostics_storage_account_uri` 变量。
- 扩展通过 `extensions` 映射在模块内部管理。不要创建独立的扩展资源。

**`avm-res-network-virtualnetwork`（任何版本）**

- 此模块由 AzAPI 提供者支持，而不是 `azurerm`。使用 `parent_id`（完整的资源组资源 ID 字符串）指定资源组，而不是 `resource_group_name`。
- README 中的每个示例都显示 `parent_id`；没有一个显示 `resource_group_name`。

所有 AVM 模块的通用经验：

- 从**必需输入**中确定子资源所有权，然后再创建兄弟模块。
- 从**可选输入**和 `variables.tf` 中确定接受的变量名称和类型。
- 从 README 使用示例中确定标识符样式和输入形状。
- 不要从原始 `azurerm_*` 资源推断参数名称。

### 6) 生成 Terraform 文件

### 在编写导入块之前 — 检查模块源（必填）

在 `terraform init` 下载模块后，检查每个模块的源文件以确定 Terraform 资源地址，然后再编写任何 `import {}` 块。永远不要从记忆中编写导入地址。

#### 步骤 A — 确定提供者和资源标签

```bash
grep "^resource" .terraform/modules/<module_key>/main*.tf
```

这揭示了模块是否使用 `azurerm_*` 或 `azapi_resource` 标签。例如，`avm-res-network-virtualnetwork` 暴露 `azapi_resource "vnet"`，而不是 `azurerm_virtual_network "this"`。

#### 步骤 B — 确定子模块和嵌套路径

```bash
grep "^module" .terraform/modules/<module_key>/main*.tf
```

如果子资源在子模块中管理（子网、扩展等），导入地址必须包括所有中间模块标签：

```text
module.<root_module_key>.module.<child_module_key>["<map_key>"].<resource_type>.<label>[<index>]
```

#### 步骤 C — 检查 `count` vs `for_each`

```bash
grep -n "count\|for_each" .terraform/modules/<module_key>/main*.tf
```

使用 `count` 的资源需要在导入地址中包含索引。当 `count = 1`（例如，条件 Linux vs Windows 选择）时，地址必须以 `[0]` 结尾。使用 `for_each` 的资源使用字符串键，而不是数字索引。

#### 已知的导入地址模式（从经验教训中获取的示例）

这些只是示例。使用它们作为推理模板，然后从当前导入的模块的下载源代码中推导出确切地址。

| 资源 | 正确的导入 `to` 地址模式 |
|---|---|
| AzAPI 支持的 VNet | `module.<vnet_key>.azapi_resource.vnet` |
| 子网（嵌套，基于 count） | `module.<vnet_key>.module.subnet["<subnet_name>"].azapi_resource.subnet[0]` |
| Linux VM（基于 count） | `module.<vm_key>.azurerm_linux_virtual_machine.this[0]` |
| VM NIC | `module.<vm_key>.azurerm_network_interface.virtualmachine_network_interfaces["<nic_key>"]` |
| VM 扩展（默认 deploy_sequence=5） | `module.<vm_key>.module.extension["<ext_name>"].azurerm_virtual_machine_extension.this` |
| VM 扩展（deploy_sequence=1–4） | `module.<vm_key>.module.extension_<n>["<ext_name>"].azurerm_virtual_machine_extension.this` |
| NSG-NIC 关联 | `module.<vm_key>.azurerm_network_interface_security_group_association.this["<nic_key>-<nsg_key>"]` |

生成：

- `providers.tf`，包含 `azurerm` 提供者和所需版本约束
- `main.tf`，包含 AVM 模块块和显式依赖关系
- `variables.tf`，用于环境特定值
- `outputs.tf`，用于关键 ID 和端点
- `terraform.tfvars.example`，包含占位符值

### 将实时属性与模块默认值进行比较（必填）

在编写初始配置后，将每个发现的实时资源的非零属性与相应 AVM 模块的 `variables.tf` 中声明的默认值进行比较。任何实时值与模块默认值不同的属性都必须在 Terraform 配置中显式设置。

特别关注以下属性类别，它们是配置漂移的常见来源：

- **超时值**（例如，公共 IP `idle_timeout_in_minutes` 默认为 `4`；实时部署通常使用 `30`）
- **网络策略标志**（例如，子网 `private_endpoint_network_policies` 默认为 `"Enabled"`；现有子网通常为 `"Disabled"`）
- **SKU 和分配**（例如，公共 IP `sku`、`allocation_method`）
- **可用区**（例如，VM 区、公共 IP 区）
- 存储和数据库资源上的**冗余和复制**设置

使用显式 `az` 命令获取完整实时属性，例如：

```bash
az network public-ip show --ids <resource_id> --query "{idleTimeout:idleTimeoutInMinutes, sku:sku.name, zones:zones}" -o json
az network vnet subnet show --ids <resource_id> --query "{privateEndpointPolicies:privateEndpointNetworkPolicies, delegation:delegations}" -o json
```

不要仅依赖 `az resource list` 输出，它可能省略嵌套或计算属性。

显式固定模块版本：

```hcl
module "example" {
	source  = "Azure/<module>/azurerm"
	version = "<latest-compatible-version>"
}
```

### 7) 验证生成的代码

运行：

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
```

预期输出：没有语法错误，没有验证错误，并且计划与发现的基础设施意图匹配。

## 故障排除

| 问题 | 可能的原因 | 操作 |
|---|---|---|
| `az` 命令因授权错误而失败 | 错误的租户/订阅或缺少 RBAC 角色 | 重新运行 `az login`，验证订阅上下文，确认所需权限 |
| 发现输出为空 | 范围不正确或范围内没有资源 | 重新检查范围输入并再次运行范围列表/显示命令 |
| 未找到资源类型的 AVM 模块 | 资源类型尚未由 AVM 覆盖 | 使用原生 `azurerm_*` 资源并记录该差距 |
| `terraform validate` 失败 | 缺少变量或未解决的依赖关系 | 添加所需变量和显式依赖关系，然后重新运行验证 |
| 模块中未找到未知参数或变量 | AVM 变量名称与 `azurerm` 提供者参数名称不同 | 阅读 README 的 `variables.tf` 或可选输入部分以获取正确名称 |
| 导入块失败 — 资源在地址中找不到 | 提供者标签错误（`azurerm_` vs `azapi_`）、缺少子模块路径或缺少 `[0]` 索引 | 运行 `grep "^resource" .terraform/modules/<key>/main*.tf` 和 `grep "^module"` 以找到确切地址 |
| `terraform plan` 显示导入资源意外的 `~ update` | 实时值与 AVM 模块默认值不同 | 使用 `az <resource> show` 获取实时属性，与模块默认值比较，在 Terraform 配置中显式设置 |
| 子模块给出 "提供者配置不存在" | 子资源作为独立模块声明，尽管父模块拥有它们 | 检查 README 中的必需输入，删除不正确的独立模块，并使用父模块记录的输入结构建模子资源 |
| 嵌套子资源导入失败，显示 "资源找不到" | 缺少中间模块路径、错误的映射键或缺少索引 | 检查模块块和源中的 `count`/`for_each`；构建包括所有模块段和所需键/索引的完整嵌套导入地址 |
| 工具尝试将 ARM 资源 ID 作为文件路径或询问重复的范围问题 | 资源 ID 未作为 `--ids` 输入处理，或代理未信任已提供的范围 | 严格将 ARM ID 视为云标识符，使用 `az ... --ids ...`，并在提供有效范围后停止重新提示 |

## 响应合同

返回结果时，提供：

1. 使用的范围（订阅、资源组或资源 ID）
2. 创建的发现文件
3. 检测到的资源类型
4. 选择的 AVM 模块及其版本
5. 生成的或更新的 Terraform 文件
6. 验证命令结果
7. 需要用户输入的开放差距（如果有）

## 代理的执行规则

- 如果范围缺失，不要继续。
- 不要在没有列出发现的文件和验证输出的情况下声称成功导入。
- 在生成 Terraform 之前不要跳过依赖关系映射。
- 优先使用 AVM 模块；明确为每个非 AVM 回退提供理由。
- **在编写代码之前阅读每个 AVM 模块的 README。** 必需输入标识模块拥有的子资源。可选输入记录确切的变量名称和类型。使用示例显示提供者特定约定（`parent_id` vs `resource_group_name`）。跳过 README 是基于 AVM 导入的代码错误最常见的原因。
- **永远不要从记忆中编写导入地址。** 在 `terraform init` 后，通过 grep 下载的模块源来发现实际的提供者（`azurerm` vs `azapi`）、资源标签、子模块嵌套和 `count` vs `for_each` 使用情况，然后再编写任何 `import {}` 块。
- **永远不要将 ARM 资源 ID 视为文件路径。** 资源 ID 属于 Azure CLI `--ids` 参数和 API 查询，而不是文件 IO 工具。仅在提供真实工作区路径时才读取本地文件。
- **当范围已知时最小化提示。** 如果订阅、资源组或特定资源 ID 已提供，请直接执行命令，并且仅在命令因缺少所需上下文而失败时才询问后续问题。
- **不要在 `terraform plan` 显示 0 销毁和 0 不需要的更改之前声明导入完成。** Telemetry `+ create` 资源是可以接受的。任何对真实基础设施资源的 `~ update` 或 `- destroy` 都必须解决。
