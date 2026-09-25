# 云网络安全

管理 Elastic Cloud Serverless 项目的网络安全策略：IP 过滤器用于允许特定 IP 或 CIDR 列表，以及 VPC 过滤器（AWS PrivateLink）用于限制流量到特定 VPC 端点。

> **前提条件：** 此技能假定 **cloud-setup** 技能已经运行——`EC_API_KEY` 已设置在环境中，组织上下文已建立。如果缺少 `EC_API_KEY`，请指示代理先调用 **cloud-setup**。**不要**直接提示用户输入 API 密钥。

有关项目创建和日常操作（包括将过滤器与项目关联），请参阅 **cloud-create-project** 和 **cloud-manage-project**。有关身份和访问管理（用户、角色、API 密钥），请参阅 **cloud-access-management**。

有关详细的 API 端点和请求模式，请参阅 [references/api-reference.md](references/api-reference.md)。

## 术语

此技能使用 **网络安全** 作为总称，与 Elastic Cloud UI 方向一致。底层 API 使用 **流量过滤器**——你会在端点路径中看到 `traffic-filters`，在 JSON 字段中看到 `traffic_filters`。当用户或代理说“流量过滤器”时，他们指的是与“网络安全策略”相同的东西。这两种过滤器类型是 **IP 过滤器**（类型 `ip`）和 **VPC 过滤器**（类型 `vpce`）。

## 需要完成的任务

- 创建 IP 过滤器以限制特定 IP 或 CIDR 块的入站流量
- 创建 VPC 过滤器（AWS PrivateLink）以限制流量到特定 VPC 端点 ID
- 列出、检查、更新和删除网络安全策略
- 查询 PrivateLink 区域元数据（服务名称、域名、可用区）
- 将过滤器与 Serverless 项目关联或取消关联（委托给 **cloud-manage-project**）
- 审计组织的当前网络安全态势

## 前提条件和权限

| 项目            | 描述                                                                                       |
| --------------- | ------------------------------------------------------------------------------------------- |
| **EC_API_KEY**  | 云 API 密钥（由 **cloud-setup** 设置）。所有操作都需要。                                    |
| **Region**      | 过滤器是区域范围的。创建过滤器时，用户必须指定目标区域。                                   |
| **Project IDs** | 仅在将过滤器与项目关联时需要（由 **cloud-manage-project** 处理）。                         |

在执行任何操作之前，运行 `python3 skills/cloud/network-security/scripts/cloud_network_security.py list-filters` 以验证 `EC_API_KEY` 是否有效。

### 操作级权限

在 Elastic Cloud Serverless 中执行常见的网络安全操作需要以下权限。

| 操作                        | 需要的权限                       |
| -------------------------- | -------------------------------- |
| 列出过滤器 / 获取元数据      | 任何组织成员                   |
| 创建 / 更新 / 删除过滤器    | 组织所有者 (`organization-admin`) |
| 将过滤器与项目关联          | 组织所有者或项目管理员       |

此技能不会执行单独的角色预检查。尝试请求的操作并让 API 执行授权。如果 API 返回授权错误（例如，`403 Forbidden`），停止并要求用户验证提供的 API 密钥权限。

### 手动设置回退（当 cloud-setup 不可用时）

如果此技能独立安装且 `cloud-setup` 不可用，请指示用户在运行命令之前手动配置云环境变量。**永远不要**要求用户在聊天中粘贴 API 密钥。

| 变量      | 需要 | 描述                                                                          |
| --------- | ---- | -------------------------------------------------------------------------------- |
| `EC_API_KEY`  | 是   | Elastic Cloud API 密钥（有关操作所需的权限，请参阅权限表）。                     |
| `EC_BASE_URL` | 否   | 云 API 基础 URL（默认：`https://api.elastic-cloud.com`）。                       |

> **注意：** 如果缺少 `EC_API_KEY`，或者用户还没有 Cloud API 密钥，请直接引导用户在 [Elastic Cloud API 密钥](https://cloud.elastic.co/account/keys) 生成一个，然后按照以下步骤在本地配置。

首选方法（代理友好）：在项目根目录创建一个 `.env` 文件：

```bash
EC_API_KEY=your-api-key
EC_BASE_URL=https://api.elastic-cloud.com
```

所有 `cloud/*` 脚本自动加载工作目录中的 `.env`。

替代方法：在终端中直接导出：

```bash
export EC_API_KEY="<your-cloud-api-key>"
export EC_BASE_URL="https://api.elastic-cloud.com"
```

终端导出可能对在单独 shell 会话中运行的沙盒代理不可见，因此在使用代理时优先使用 `.env`。

## 分解网络安全请求

当用户用自然语言描述网络安全需求（例如，“将我的搜索项目限制到我们的办公 IP”）时，在执行之前将请求分解为独立的任务。

### 第 1 步 — 确定组件

| 组件       | 需要回答的问题                                                     |
| ---------- | ------------------------------------------------------------------ |
| **Filter type** | IP 过滤器（公共 IP/CIDR）还是 VPC 过滤器（AWS PrivateLink 端点）？ |
| **Region**      | 目标项目位于哪个 AWS 区域？                           |
| **Rules**       | 应该允许哪些源 IP、CIDR 或 VPC 端点 ID？         |
| **Scope**       | 默认应用于所有新项目，还是仅特定项目？       |
| **Projects**    | 哪些现有项目应与此过滤器关联？         |

### 第 2 步 — 检查现有状态

在创建新过滤器之前，检查已存在的内容：

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py list-filters --region us-east-1
```

**过滤器卫生：** 如果现有过滤器已经涵盖了相同的目的地规则，则重用它而不是创建重复的过滤器。过滤器是区域范围的，可以与多个项目关联，因此一个具有正确规则的过滤器可以服务于多个项目。当两个过滤器具有相同的源规则但服务于不同的目的时（例如，不同团队管理自己的策略），这是合法的，但为相同的目的创建第二个过滤器是不必要的。

### 第 3 步 — 创建过滤器

从 `skills/cloud/network-security/scripts/cloud_network_security.py` 运行适当的命令。

### 第 4 步 — 与项目关联

过滤器关联使用项目 PATCH 端点管理。使用 **cloud-manage-project** 关联或取消关联过滤器：

```text
PATCH /api/v1/serverless/projects/{type}/{id}
Body: { "traffic_filters": [{ "id": "filter-id-1" }, { "id": "filter-id-2" }] }
```

在更新关联时，提供 **完整的过滤器 ID 列表**。列表中未包含的任何过滤器都将与项目取消关联。

### 第 5 步 — 验证

执行后，再次列出过滤器或获取项目以确认更改已生效。

## IP 过滤器与 VPC 过滤器

| 方面            | IP 过滤器 (`ip`)                                   | VPC 过滤器 (`vpce`)                                      |
| -------------- | -------------------------------------------------- | -------------------------------------------------------- |
| **目的**       | 允许公共 IP 地址或 CIDR 列表                       | 限制流量到特定的 AWS VPC 端点 ID                      |
| **用例**      | 办公室 IP、CI/CD 运行器、合作伙伴访问          | 私有连接而不暴露公共互联网                           |
| **源格式**     | IP 地址或 CIDR（例如，`203.0.113.0/24`）            | AWS VPC 端点 ID（例如，`vpce-0abc123def456`）          |
| **网络路径**   | 公共互联网                                        | AWS PrivateLink（私有，永远不会离开 AWS 网络）          |
| **前提条件**  | 无                                               | 首先在 AWS 控制台创建 VPC 端点和 DNS 记录             |

> **关键概念：** AWS 中的私有连接在 Elastic Cloud 中默认接受。创建 VPC 过滤器仅用于**限制**流量到特定的 VPC 端点 ID。如果你只需要私有连接（无需过滤），请在 AWS 中创建 VPC 端点和 DNS 记录——Elastic Cloud 端无需过滤器。

## 示例

### 允许办公 IP 范围

**提示：** “仅允许来自我们办公网络的流量 203.0.113.0/24 到 us-east-1 中的项目。”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py create-filter \
  --name "Office IP allowlist" \
  --type ip \
  --region us-east-1 \
  --rules '[{"source": "203.0.113.0/24", "description": "Office network"}]'
```

然后使用 **cloud-manage-project** 将过滤器与特定项目关联。

### 限制流量到 VPC 端点

**提示：** “将我的可观察性项目锁定，仅接受来自我们 VPC 端点的流量。”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py create-filter \
  --name "Production VPC" \
  --type vpce \
  --region us-east-1 \
  --rules '[{"source": "vpce-0abc123def456", "description": "Production VPC endpoint"}]'
```

### 列出区域中的所有过滤器

**提示：** “显示 eu-west-1 中的所有网络安全策略。”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py list-filters --region eu-west-1
```

### 更新过滤器以添加新的 IP

**提示：** “将 VPN IP 198.51.100.5 添加到我们现有的办公过滤器。”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py get-filter --filter-id tf-12345
# 查看当前规则，然后使用完整的规则集更新：
python3 skills/cloud/network-security/scripts/cloud_network_security.py update-filter \
  --filter-id tf-12345 \
  --body '{"rules": [{"source": "203.0.113.0/24", "description": "Office network"}, {"source": "198.51.100.5", "description": "VPN"}]}'
```

### 查询区域的 PrivateLink 元数据

**提示：** “我需要 us-east-1 的 PrivateLink 服务名称是什么？”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py get-metadata --region us-east-1
```

### 删除未使用的过滤器

**提示：** “删除旧的测试 IP 过滤器。”

```bash
python3 skills/cloud/network-security/scripts/cloud_network_security.py delete-filter --filter-id tf-67890 --dry-run
# 查看将要删除的内容，然后确认：
python3 skills/cloud/network-security/scripts/cloud_network_security.py delete-filter --filter-id tf-67890
```

## 指南

- 如果 `EC_API_KEY` 未设置，不要提示用户——指示代理先调用 **cloud-setup**。
- 在执行破坏性操作（删除过滤器）之前，始终与用户确认。
- 过滤器是 **区域范围的**：在 `us-east-1` 中创建的过滤器只能与该区域中的项目关联。
- **过滤器卫生——重用、范围和清理：**
  - 在创建过滤器之前，始终运行 `list-filters` 并检查是否已存在**相同目的**的过滤器且具有所需的源规则。过滤器可以与多个项目关联，因此一个具有正确规则的过滤器比重复的过滤器更好。
  - 重复的过滤器意味着具有相同目的且源规则相同的过滤器——不仅仅是重叠的 IP。使用相同 CIDR 覆盖不同项目组的两个过滤器是合法的。
  - 定期检查未使用的过滤器。如果过滤器不再与任何项目关联，提示用户删除它以减少杂乱。
- **更新规则将替换整个规则集。** 使用 PATCH 添加规则时，请包含所有现有规则和新的规则。省略现有规则将删除它。
- **删除过滤器如果它仍然与项目关联将失败。** 首先使用 **cloud-manage-project** 分离（使用 PATCH 更新项目，从 `traffic_filters` 列表中删除过滤器），然后删除。
- `include_by_default` 自动将过滤器与区域中的所有新项目关联。谨慎使用——它会影响每个未来的项目。
- 对于项目关联和取消关联，委托给 **cloud-manage-project** 技能。此技能仅管理过滤器定义。
- 有关身份和访问管理（用户、角色、API 密钥），请参阅 **cloud-access-management**。
- 有关 Elasticsearch 级别的安全（原生用户、角色映射、DLS/FLS），请参阅 **elasticsearch-authz**。
