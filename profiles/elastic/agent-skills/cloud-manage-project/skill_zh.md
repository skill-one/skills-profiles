# 管理无服务器项目

使用无服务器 REST API 对 Elastic Cloud 无服务器项目执行日常运维操作。

## 前置条件和权限

- 确保 `EC_API_KEY` 已配置。如果未配置，请先运行 `cloud-setup` 技能。
- 更新项目设置需要目标项目上的 **管理员** 或 **编辑者** 角色。
- 此技能不执行单独的角色预检查。尝试请求的操作并由 API 强制执行授权。如果 API 返回授权错误（例如，`403 Forbidden`），停止并要求用户验证提供的 API 密钥权限。

### 手动设置回退（当 `cloud-setup` 不可用时）

如果此技能独立安装且 `cloud-setup` 不可用，请指示用户在运行命令之前手动配置 Cloud 环境变量。切勿要求用户在聊天中粘贴 API 密钥。

| 变量      | 是否必需 | 描述                                                    |
| --------- | -------- | ------------------------------------------------------- |
| `EC_API_KEY`  | 是      | 用于项目管理操作的 Elastic Cloud API 密钥。             |
| `EC_BASE_URL` | 否       | 云 API 基础 URL（默认：`https://api.elastic-cloud.com`）。 |

> **注意：** 如果 `EC_API_KEY` 缺失，或者用户还没有 Cloud API 密钥，请直接引导用户在 [Elastic Cloud API 密钥](https://cloud.elastic.co/account/keys) 处生成一个，然后使用以下步骤本地配置。

推荐方法（对代理友好）：在项目根目录创建一个 `.env` 文件：

```bash
EC_API_KEY=your-api-key
EC_BASE_URL=https://api.elastic-cloud.com
```

所有 `cloud/*` 脚本会自动加载工作目录中的 `.env`。

替代方法：在终端中直接导出：

```bash
export EC_API_KEY="<your-cloud-api-key>"
export EC_BASE_URL="https://api.elastic-cloud.com"
```

终端导出可能不会在单独的 shell 会话中运行的沙盒代理中可见，因此在使用代理时请优先使用 `.env`。

## 关键原则

- **切勿在聊天中显示密钥。** 不要在对话消息或代理思考中回显、记录或重复 API 密钥、密码或凭证。请引导用户到 `.elastic-credentials` 文件。管理员密码必须 **绝对** 不会出现在聊天历史记录、思考痕迹或代理输出中——即使在使用它来创建 API 密钥时，也请直接通过 shell 变量替换而不回显。
- **在破坏性操作前确认。** 在删除项目或重置凭证之前，始终要求用户确认。
- **凭证保存到文件。** 在凭证重置后，脚本会自动将新密码写入 `.elastic-credentials`。密码会从标准输出中删除。切勿在聊天中读取或显示 `.elastic-credentials` 的内容。
- **管理员凭证仅用于 API 密钥创建。** `create-project` 和 `reset-credentials` 保存的 `admin` 密码仅用于引导范围 API 密钥——切勿用它直接执行 Elasticsearch 操作。`load-credentials` 默认排除管理员凭证；仅当创建密钥时才传递 `--include-admin`。
- **始终优先使用 API 密钥。** 在设置 `ELASTICSEARCH_API_KEY` 之前不要进行 Elasticsearch 操作。如果只有管理员凭证可用，请通过 `elasticsearch-authn` 创建范围 API 密钥。如果该技能未安装，请要求用户安装它或在 **Kibana > Stack Management > API keys** 中手动创建密钥。请为密钥设置范围，仅授予用户需要的权限。
- **通过类型和 ID 识别项目。** 每个命令都需要 `--type` 和 `--id`（`list` 命令除外，它只需要 `--type`）。
- **两种 API 密钥。** 此技能使用 **Cloud API 密钥** (`EC_API_KEY`) 进行项目管理操作（列出、获取、更新、删除）。Elasticsearch 操作需要一个单独的 **Elasticsearch API 密钥** (`ELASTICSEARCH_API_KEY`)，它针对项目的 Elasticsearch 端点进行身份验证。不要混淆两者。

## 工作流：连接到现有项目

当用户要求查询或管理当前会话中代理未创建的项目时，请使用此工作流。它会解析项目、保存其端点，并在继续之前确保工作 Elasticsearch 凭证。

此工作流仅适用于 **Elastic Cloud 无服务器项目**。如果用户的 Elasticsearch 实例是自管理的或 Elastic Cloud Hosted，此技能不适用——直接跳过它并继续执行相关技能。如有疑问，请询问用户：**“您的 Elasticsearch 实例是 Elastic Cloud 无服务器项目吗？”**

```text
连接到现有项目：
- [ ] 第 1 步：解析项目
- [ ] 第 2 步：获取项目详细信息并加载凭证
- [ ] 第 3 步：获取 Elasticsearch 凭证
```

### 第 1 步：解析项目

如果尚未提供，请要求用户提供 **项目名称**。根据用户请求推断项目类型：

| 用户说                                                   | `--type`        |
| ------------------------------------------------------- | --------------- |
| "search project", "elasticsearch project", vector search    | `elasticsearch` |
| "observability project", "o11y", logs, metrics, traces, APM | `observability` |
| "security project", "SIEM", detections, endpoint protection | `security`      |

如果类型不明确，请列出所有三种类型以找到项目。

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py list \
  --type elasticsearch
```

将用户的引用（名称、部分名称或别名）与列表结果进行匹配。如果匹配多个项目或没有匹配，请提供候选项目并要求用户选择。

### 第 2 步：获取项目详细信息并加载凭证

一旦确定单个项目，请检查 `.elastic-credentials` 是否已为此项目（从先前会话）包含条目。如果是，请使用 `load-credentials` 加载它们：

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --name "<project-name>")
```

这将使用单个命令为项目设置所有保存的环境变量——端点和之前创建的任何 Elasticsearch API 密钥。故意排除了管理员凭证 (`ELASTICSEARCH_USERNAME`/`ELASTICSEARCH_PASSWORD`)。同一项目的后续部分会自动覆盖先前的值，因此最新的凭证始终有效。

如果 `load-credentials` 报告没有匹配的条目，请从 API 获取项目详细信息并手动导出端点：

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py get \
  --type elasticsearch \
  --id <project-id>
```

然后从响应中导出端点 URL。可用的端点取决于项目类型。

**所有项目类型：**

```bash
export ELASTICSEARCH_URL="<elasticsearch_endpoint>"
export KIBANA_URL="<kibana_endpoint>"
```

**Observability 项目**（附加）：

```bash
export APM_URL="<apm_endpoint>"
export INGEST_URL="<ingest_endpoint>"
```

**Security 项目**（附加）：

```bash
export INGEST_URL="<ingest_endpoint>"
```

### 第 3 步：获取 Elasticsearch 凭证

如果 `load-credentials` 设置了 `ELASTICSEARCH_API_KEY`，请验证凭证是否有效：

```bash
curl -H "Authorization: ApiKey ${ELASTICSEARCH_API_KEY}" \
  "${ELASTICSEARCH_URL}/_security/_authenticate"
```

在继续之前，请确认响应包含有效的 `username` 和 `"authentication_type": "api_key"`。如果验证成功，请跳过此步骤的其余部分。

如果没有加载凭证，或验证失败，请要求用户：**“您是否为此项目有现有的 Elasticsearch API 密钥？”**

**如果有的话**——请要求用户将其添加到 `.elastic-credentials`（见“凭证文件格式”）。不要在聊天中接受密钥。重新加载并验证：

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --name "<project-name>")
curl -H "Authorization: ApiKey ${ELASTICSEARCH_API_KEY}" \
  "${ELASTICSEARCH_URL}/_security/_authenticate"
```

**如果没有**——请遵循此恢复路径：

1. 确认后，重置管理员引导凭证：

   ```bash
   python3 skills/cloud/manage-project/scripts/manage-project.py reset-credentials \
     --type elasticsearch \
     --id <project-id>
   ```

   新密码会自动保存到 `.elastic-credentials`，并在头部包含项目名称。请引导用户查看该文件——不要显示其内容。

2. 使用 `--include-admin` 加载凭证，以便管理员密码可用于 API 密钥创建：

   ```bash
   eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
     --name "<project-name>" --include-admin)
   ```

   如果 `elasticsearch-authn` 可用，请使用管理员凭证通过它创建范围 Elasticsearch API 密钥。如果该技能未安装，请要求用户安装它或在 **Kibana > Stack Management > API keys** 中手动创建密钥。请为密钥设置范围，仅授予用户需要的权限。

3. 创建 API 密钥后，使用项目特定头部格式（见下文“凭证文件格式”）将其保存到 `.elastic-credentials`。然后重新加载 **不带 `--include-admin`** 以从环境中删除管理员凭证并验证：

   ```bash
   eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
     --name "<project-name>")
   curl -H "Authorization: ApiKey ${ELASTICSEARCH_API_KEY}" \
     "${ELASTICSEARCH_URL}/_security/_authenticate"
   ```

   确认响应显示有效的 `username` 和 `"authentication_type": "api_key"` 后再继续。

## 凭证文件格式

有关完整格式规范，请参阅 [references/credential-file-format.md](references/credential-file-format.md)。

## 工作流：加载项目凭证

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --name "<project-name>")
```

或通过项目 ID：

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --id <project-id>)
```

解析 `.elastic-credentials`，合并匹配项目的所有部分，并打印 `export` 语句。默认情况下排除管理员凭证 (`ELASTICSEARCH_USERNAME`/`ELASTICSEARCH_PASSWORD`)——仅导出端点和 API 密钥。当您需要管理员凭证以创建 API 密钥时，请添加 `--include-admin`。

## 工作流：列出项目

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py list \
  --type elasticsearch
```

使用 `--type observability` 或 `--type security` 列出其他项目类型。

## 工作流：获取项目详细信息

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py get \
  --type elasticsearch \
  --id <project-id>
```

## 工作流：更新项目

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type elasticsearch \
  --id <project-id> \
  --name "new-project-name"
```

仅更新提供的字段（PATCH 语义）。支持的字段：`--name`、`--alias`、`--tag`、`--search-power`、`--boost-window`、`--max-retention-days`、`--default-retention-days`。

### 别名

别名是一个 RFC-1035 域标签（小写字母数字和连字符，最大 50 个字符），它将成为项目端点 URL 的一部分。**更改别名会更改所有端点 URL**，这会中断指向旧 URL 的现有客户端。在应用之前警告用户。

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type elasticsearch \
  --id <project-id> \
  --alias "prod-search"
```

### 标签

标签是用于团队跟踪、成本归因和组织的键值元数据对。为每个标签传递 `--tag KEY:VALUE`。可以一次性设置多个标签。

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type elasticsearch \
  --id <project-id> \
  --tag env:prod \
  --tag team:search
```

标签作为 `metadata.tags` 发送到 API 请求。设置标签会替换项目上的所有现有标签——首先使用 `get` 获取当前标签，并包含用户希望保留的任何标签。

### Elasticsearch Search Lake 设置

对于 Elasticsearch 项目，两个字段控制查询性能和 Search AI Lake 中的数据缓存。已导入的数据存储在成本效益高的通用存储中。顶部的缓存层提供了对最近和频繁查询数据的更快搜索速度——这些缓存的被认为是 **搜索就绪** 的。

| 标志             | 范围   | 描述                                                                  |
| ---------------- | ------ | -------------------------------------------------------------------- |
| `--search-power` | 28–3000 | 查询性能级别。较高的值可以提高性能，但会增加成本 |
| `--boost-window` | 1–180   | 有资格进行增强缓存的日期数（默认：7）                       |

#### Search Power

Search Power 通过分配更多或更少的查询资源来控制搜索速度。常见的预设（与 Cloud UI 匹配）：

| 值   | 预设            | 行为                                                                       |
| ---- | --------------- | ---------------------------------------------------------------------------- |
| 28   | On-demand         | 自动扩展具有较低的基线。延迟更可变，最大吞吐量降低                      |
| 100  | Performant        | 始终如一的低延迟，自动扩展以适应中等高吞吐量                          |
| 250  | High availability | 优化用于高吞吐量场景，在高卷量下保持低延迟 |

当用户通过名称请求预设时，请将其映射到相应的值。28–3000 范围内的自定义值也是有效的。

**在更新 `search_power` 之前警告用户成本影响。** 较高的值会增加 VCU 消耗，并可能导致账单增加。在应用之前与用户确认新值。

#### Search Boost Window

非时间序列数据始终是搜索就绪的。增强窗口确定多少时间序列数据（具有 `@timestamp` 字段的文档）也保留在快速缓存层中。增加窗口意味着更多的时间序列数据成为搜索就绪的，这可以提高对最近数据的查询速度，但会增加搜索就绪数据的量。

### Security 数据保留设置

对于 Security 项目，两个字段控制数据在 Search AI Lake 中保留的时间。保留按数据流配置，但这两个项目级设置会强制执行全局边界。

| 标志                       | 单位 | 描述                                                    |
| -------------------------- | ---- | ------------------------------------------------------- |
| `--max-retention-days`     | 天   | 项目中任何数据流的最大保留期                           |
| `--default-retention-days` | 天   | 应用于没有自定义保留期的数据流的默认保留期             |

- **最大保留** — 在所有数据流上执行上限。降低时，它会替换当前具有较长保留期的流。新最大值之前的旧数据会 **永久删除**。
- **默认保留** — 自动应用于没有设置自定义保留期的数据流。不会影响具有现有自定义保留期的流。

**在减少 `max-retention-days` 之前警告用户。** 降低最大值会永久删除新限制之前的旧数据。在应用之前与用户确认新值。

## 工作流：重置项目凭证

**在重置之前始终与用户确认。**

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py reset-credentials \
  --type elasticsearch \
  --id <project-id>
```

新密码会自动保存到 `.elastic-credentials`。请告诉用户打开该文件——不要在聊天中显示其内容。

## 工作流：删除项目

**在删除之前始终与用户确认。**

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py delete \
  --type elasticsearch \
  --id <project-id>
```

## 工作流：恢复已暂停的项目

项目在试用期结束后可以自动暂停。使用以下方式恢复：

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py resume \
  --type elasticsearch \
  --id <project-id>
```

恢复后，轮询项目状态，直到阶段从 `initializing` 变更为 `initialized`。

## 示例

### 列出所有 Security 项目

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py list --type security
```

### 在 Elasticsearch 项目上更新搜索功率

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type elasticsearch \
  --id abc123def456abc123def456abc12345 \
  --search-power 500
```

### 在 Security 项目上设置数据保留

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type security \
  --id abc123def456abc123def456abc12345 \
  --max-retention-days 396 \
  --default-retention-days 396
```

### 更改项目别名

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type elasticsearch \
  --id abc123def456abc123def456abc12345 \
  --alias "prod-search"
```

### 为成本跟踪标记项目

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type observability \
  --id abc123def456abc123def456abc12345 \
  --tag env:prod \
  --tag team:platform
```

### 重命名一个 Observability 项目

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py update \
  --type observability \
  --id abc123def456abc123def456abc12345 \
  --name "production-logs"
```

### 连接到现有项目（凭证在文件中）

```text
用户：我想对我的搜索项目 "prod-search" 运行查询
代理：让我找到那个项目。
       [运行：list --type elasticsearch]
       我找到了 "prod-search"（ID: abc123...）。加载保存的凭证...
       [运行：eval $(load-credentials --name prod-search)]
       凭证加载完成。验证...
       [运行：curl -H "Authorization: ApiKey ..." "${ELASTICSEARCH_URL}/_security/_authenticate"]
       验证通过——通过 API 密钥以 "my-service" 用户身份进行身份验证。您已准备就绪。
```

### 连接到项目（没有保存的凭证）

```text
用户：让我们将日志导入我的 o11y 项目 "siem-prod"
代理：让我找到那个项目。
       [运行：list --type observability]
       找到 "siem-prod"（ID: def456...）。未找到此项目的保存凭证。
       [运行：get --type observability --id def456...]
       端点设置。由于文件中没有 Elasticsearch 凭证，我可以重置管理员引导密码以获取初始访问权限。要继续吗？
用户：是
代理：[运行：reset-credentials --type observability --id def456...]
       凭证保存到 .elastic-credentials — 打开那个文件以检索密码。
       [运行：eval $(load-credentials --name siem-prod --include-admin)]
       为 API 密钥创建加载了管理员凭证。现在正在使用管理员凭证通过 elasticsearch-authn 创建范围 Elasticsearch API 密钥——它需要什么访问权限？
用户：对 "logs-*" 的只读访问
代理：[使用管理员凭证通过 elasticsearch-authn 创建范围 API 密钥]
       [使用项目头部将 API 密钥追加到 .elastic-credentials]
       [运行：eval $(load-credentials --name siem-prod)]
       [针对 ELASTICSEARCH_URL 进行验证]
       API 密钥创建并验证。从环境中删除了管理员凭证。
```

### 确认后删除项目

```text
用户：删除我的 Elasticsearch 项目 abc123...
代理：您确定要删除项目 abc123... 吗？此操作不可撤销。
用户：是
```

```bash
python3 skills/cloud/manage-project/scripts/manage-project.py delete \
  --type elasticsearch \
  --id abc123def456abc123def456abc12345
```

## 指南

- 如果 `EC_API_KEY` 未设置，请先运行 `cloud-setup` 技能。
- 使用 `cloud-create-project` 技能创建新项目——此技能仅处理现有项目。
- 当用户提到代理未创建的项目时，请遵循“连接到现有项目”工作流。
- 删除是永久性的。在继续之前始终与用户确认。
- 重置凭证后，提醒用户更新任何存储的密码或环境变量。
- 在增加 `search_power` 之前警告用户成本影响。在应用之前先与用户确认新值。
- 在减少 `max-retention-days` 之前警告用户数据丢失。新最大值之前的旧数据会永久删除。
- 警告用户更改项目别名会更改所有端点 URL，这会中断指向旧 URL 的现有客户端。
- 设置标签会替换所有现有标签。首先使用 `get` 获取当前标签，然后包含用户希望保留的任何标签。

## 脚本参考

| 命令             | 描述                                                    |
| ---------------- | ------------------------------------------------------- |
| `list`            | 按类型列出项目                                          |
| `get`             | 通过 ID 获取项目详细信息                                  |
| `update`          | 更新项目名称、别名、标签或 Search Lake 设置              |
| `reset-credentials` | 重置项目凭证（新密码）                                   |
| `delete`          | 删除项目                                               |
| `resume`          | 恢复已暂停的项目                                         |
| `load-credentials`  | 从 `.elastic-credentials` 加载项目的保存凭证             |

| 标志                       | 命令                                                         | 描述                                                  |
| -------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------ |
| `--type`                   | list, get, update, reset-credentials, delete, resume             | 项目类型：`elasticsearch`, `observability`, `security`   |
| `--id`                     | get, update, reset-credentials, delete, resume, load-credentials | 项目 ID                                                   |
| `--name`                   | update, load-credentials                                         | 项目名称（update: 新名称；load-credentials: 查找）    |
| `--alias`                  | update                                                           | 新项目别名                                            |
| `--tag`                    | update                                                           | 标签作为 KEY:VALUE (可重复，替换所有标签)             |
| `--search-power`           | update                                                           | 搜索功率 28–3000 (仅限 Elasticsearch)                    |
| `--boost-window`           | update                                                           | 增强窗口 1–180 天 (仅限 Elasticsearch)                 |
| `--max-retention-days`     | update                                                           | 最大数据保留天数 (仅限 Security)                       |
| `--default-retention-days` | update                                                           | 默认数据保留天数 (仅限 Security)                       |
| `--include-admin`          | load-credentials                                                 | 包含管理员用户名/密码 (仅用于 API 密钥引导)            |
| `--wait-seconds`           | reset-credentials                                                | 等待凭证传播的秒数 (0 跳过)                           |

## 环境变量

| 变量                | 是否必需 | 描述                                                             |
| ------------------- | -------- | ----------------------------------------------------------------- |
| `EC_API_KEY`            | 是      | Elastic Cloud API 密钥 (项目管理操作)                           |
| `EC_BASE_URL`           | 否       | 云 API 基础 URL（默认：`https://api.elastic-cloud.com`）           |
| `ELASTICSEARCH_URL`     | 输出   | Elasticsearch URL (解析项目后为下游技能设置)                    |
| `KIBANA_URL`            | 输出   | Kibana URL (解析项目后为下游技能设置)                            |
| `APM_URL`               | 输出   | APM 端点 (仅限 Observability 项目)                              |
| `INGEST_URL`            | 输出   | OTLP 导入端点 (仅限 Observability 和 Security 项目)              |
| `ELASTICSEARCH_API_KEY` | 输出   | Elasticsearch API 密钥 (用于堆栈级操作)                      |

## 其他资源

- 有关完整 API 详细信息、请求/响应模式和项目类型选项，请参阅
  [无服务器项目 API](https://www.elastic.co/docs/api/doc/elastic-cloud-serverless)
- 有关 Search AI Lake 设置、数据保留和项目功能的官方文档，请参阅
  [项目设置](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/project-settings)
