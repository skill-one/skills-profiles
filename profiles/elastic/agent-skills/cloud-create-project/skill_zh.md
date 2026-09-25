# 创建无服务器项目

使用 Serverless REST API 创建 Elastic Cloud 无服务器项目。使用 `cloud-manage-project` 技能进行日常操作，例如列出、更新或删除项目。

## 前置条件和权限

- 确保 `EC_API_KEY` 已配置。如果未配置，请先运行 `cloud-setup` 技能。
- 创建项目需要具有 **管理员** 或 **组织所有者** 角色的 Cloud API 密钥。
- 此技能不会执行单独的角色预检查。尝试请求的操作并让 API 执行授权。如果 API 返回授权错误（例如，`403 Forbidden`），请停止并要求用户验证提供的 API 密钥权限。

### 手动设置回退（当 `cloud-setup` 不可用时）

如果此技能独立安装且 `cloud-setup` 不可用，请指示用户在运行命令之前手动配置 Cloud 环境变量。切勿要求用户在聊天中粘贴 API 密钥。

| 变量      | 是否必需 | 描述                                                    |
| ------------- | -------- | -------------------------------------------------------------- |
| `EC_API_KEY`  | 是      | 用于项目创建操作的 Elastic Cloud API 密钥。    |
| `EC_BASE_URL` | 否       | Cloud API 基础 URL（默认：`https://api.elastic-cloud.com`）。 |

> **注意：** 如果 `EC_API_KEY` 缺失，或者用户还没有 Cloud API 密钥，请首先检查用户是否拥有 Elastic Cloud 账户。如果没有，建议用户在
> [Elastic Cloud 免费试用](https://cloud.elastic.co/registration) 开始免费试用——14 天完全访问权限，无需信用卡。注册后，请指示用户在
> [Elastic Cloud API 密钥](https://cloud.elastic.co/account/keys) 生成密钥，然后使用以下步骤本地配置。

首选方法（对代理友好）：在项目根目录创建一个 `.env` 文件：

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

终端导出可能不会对在单独 shell 会话中运行的沙盒代理可见，因此在使用代理时请优先使用 `.env`。

## 关键原则

- **切勿在聊天中显示密钥。** 不要在对话消息或代理思考中回显、记录或重复 API 密钥、密码或凭证。请指示用户查看 `.elastic-credentials` 文件。管理员密码必须
  **绝对不能** 出现在聊天历史记录、思考痕迹或代理输出中。
- **创建前确认。** 始终向用户展示项目配置，并在运行创建脚本之前请求确认。
- **管理员凭证仅用于 API 密钥创建。** 脚本将 `admin` 密码保存到 `.elastic-credentials` 以便引导创建范围的 API 密钥。`admin` 用户具有完全权限，并且在无服务器项目中无法修改。切勿使用管理员凭证进行直接 Elasticsearch 操作（查询、索引等）——始终先创建范围的 API 密钥（见步骤 8）。`load-credentials` 命令默认排除管理员凭证——仅在步骤 7/8 使用 `--include-admin`，创建 API 密钥后重新加载时不使用它。切勿在聊天中读取或显示 `.elastic-credentials` 的内容。
- **恢复丢失的凭证。** 如果脚本无法写入 `.elastic-credentials`（磁盘满、权限等），保存可能不完整。首先检查 `.elastic-credentials` 中的密码。如果缺失，请使用
  `cloud-manage-project` 技能的 `reset-credentials` 命令生成新密码。
- **区域是永久的。** 创建项目后无法更改项目区域。
- **优先自动就绪检查。** 将 `--wait` 传递给创建脚本，以便它轮询直到阶段从 `initializing` 变更为 `initialized`。仅在 `--wait` 不可用时才回退到手动轮询状态端点。

## 项目类型

| 类型            | 描述                               | 关键端点                    |
| --------------- | ----------------------------------------- | -------------------------------- |
| `elasticsearch` | 搜索、分析和向量工作负载   | Elasticsearch, Kibana            |
| `observability` | 日志、指标、跟踪和 APM            | Elasticsearch, Kibana, APM, OTLP |
| `security`      | SIEM、端点保护、云安全 | Elasticsearch, Kibana, OTLP      |

### 项目类型推断

将用户的请求映射到正确的 `--type` 值：

| 用户说                                                   | `--type`        |
| ----------------------------------------------------------- | --------------- |
| "search project", "elasticsearch project", vector search    | `elasticsearch` |
| "observability project", "o11y", logs, metrics, traces, APM | `observability` |
| "security project", "SIEM", detections, endpoint protection | `security`      |

**不要** 默默默认为任何类型。如果用户未指定类型，请从对话上下文中推断它（例如，讨论日志摄取建议 `observability`，讨论检测或 SIEM 建议为 `security`，讨论搜索或向量工作负载建议为 `elasticsearch`）。始终向用户展示推断的类型，并在继续之前请求确认。如果上下文不足以推断类型，请要求用户选择。

### 产品层级

Observability 和 security 项目支持 `--product-tier` 标志。默认为 `complete`，除非用户明确请求其他层级。

| 项目类型    | 层级              | 描述                                           |
| --------------- | ----------------- | ----------------------------------------------------- |
| `observability` | `complete`        | 完整的 observability 套件（日志、指标、跟踪、APM） |
| `observability` | `logs_essentials` | 仅日志管理                                   |
| `security`      | `complete`        | 完整的安全套件（SIEM、云、端点）           |
| `security`      | `essentials`      | 仅核心 SIEM                                    |

Elasticsearch 项目没有产品层级——使用 `--optimized-for` 代替。

## 合理的默认值

在创建之前向用户展示这些默认值。询问他们是否要使用或更改它们：

| 设置 | 默认           |
| ------- | ----------------- |
| Region  | `gcp-us-central1` |

项目类型必须与用户确认——不要假设默认值。见“项目类型推断”部分。

始终使用 `--optimized-for general_purpose`，除非用户明确请求 `vector`。不要主动提供 `vector` 选项。

如果用户未指定名称，请要求一个——它是必需的。

## 工作流程：创建项目

```text
项目创建:
- [ ] 步骤 1：验证 API 密钥已设置
- [ ] 步骤 2：向用户展示默认值并确认
- [ ] 步骤 3：列出可用区域（可选）
- [ ] 步骤 4：创建项目
- [ ] 步骤 5：保存凭证和端点
- [ ] 步骤 6：等待项目初始化
- [ ] 步骤 7：设置环境变量
- [ ] 步骤 8：建议创建范围的 API 密钥
```

### 步骤 1：验证 API 密钥已设置

```bash
echo "${EC_API_KEY:?Not set}"
```

如果 `EC_API_KEY` 未设置，请先运行 `cloud-setup` 技能以配置身份验证和默认值。

### 步骤 2：向用户展示摘要并确认

在展示摘要之前，请确保项目类型已由用户明确确认。如果未指定类型，请从对话上下文中推断它并建议它。如果上下文不明确，请要求用户从 `elasticsearch`、`observability` 或 `security` 中选择。

始终在创建之前展示确认摘要。根据项目类型显示不同的字段：

**Elasticsearch 项目:**

```text
项目摘要:
  类型:          elasticsearch
  名称:          my-project
  区域:        gcp-us-central1
```

**Observability 项目:**

```text
项目摘要:
  类型:          observability
  名称:          my-project
  区域:        gcp-us-central1
  产品层级:  complete
```

**Security 项目:**

```text
项目摘要:
  类型:          security
  名称:          my-project
  区域:        gcp-us-central1
  产品层级:  complete
```

在继续之前，询问用户是否确认或覆盖任何值。

### 步骤 3：列出可用区域（可选）

```bash
python3 skills/cloud/create-project/scripts/create-project.py list-regions
```

输出按云提供商（AWS、Azure、GCP）分组并按字母顺序排序。标有 `*` 的区域不支持项目创建。

### 步骤 4：创建项目

```bash
python3 skills/cloud/create-project/scripts/create-project.py create \
  --type elasticsearch \
  --name "my-project" \
  --region gcp-us-central1 \
  --optimized-for general_purpose \
  --wait
```

始终传递 `--optimized-for general_purpose` 用于 Elasticsearch 项目。仅在用户明确请求时使用 `vector`。

对于 observability 和 security 项目，传递 `--product-tier complete`，除非用户明确请求其他层级。

始终传递 `--wait`，以便脚本自动轮询直到项目就绪。

### 步骤 5：保存凭证和端点

脚本会自动将凭证写入工作目录中的 `.elastic-credentials`。密码会从标准输出上的 JSON 输出中省略。

**如果保存成功**，告诉用户：

```text
凭证已保存到 .elastic-credentials — 打开该文件以检索您的密码。
```

**不要** 在聊天中读取、cat 或展示 `.elastic-credentials` 的内容。

**如果保存失败**，脚本会向标准错误输出打印错误。检查 `.elastic-credentials` 是否存在并包含密码（可能部分写入）。如果密码缺失或文件不存在，请立即运行 `cloud-manage-project` 技能的 `reset-credentials` 命令以生成新密码。

创建响应还包含：

- **项目 ID** — 用于所有后续操作
- **云 ID** — 用于客户端库
- **Elasticsearch 和 Kibana 端点** — 可以在聊天中安全显示

管理员凭证仅用于初始引导。建议创建范围的 API 密钥以供持续访问（步骤 8）。

### 步骤 6：等待项目初始化

当传递 `--wait`（推荐）时，脚本会自动轮询直到项目阶段变为 `initialized`。无需手动轮询。

如果代理未使用 `--wait` 运行，请手动轮询：

```bash
python3 skills/cloud/create-project/scripts/create-project.py status \
  --type elasticsearch \
  --id <project-id>
```

重复轮询，直到 `phase` 从 `initializing` 变更为 `initialized`。

### 步骤 7：设置环境变量

创建脚本将凭证和端点保存到带有项目名称标题的 `.elastic-credentials`。使用 `--include-admin` 将它们加载到当前 shell 中，以便在步骤 8 中创建 API 密钥时提供管理员凭证：

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --name "<project-name>" --include-admin)
```

这将设置 `ELASTICSEARCH_URL`、`KIBANA_URL`、任何特定于项目类型的端点（`APM_URL`、`INGEST_URL`），以及引导 API 密钥所需的 `admin` `ELASTICSEARCH_USERNAME`/`ELASTICSEARCH_PASSWORD`。

### 步骤 8：创建范围的 API 密钥

`admin` 用户具有完全权限，并且在无服务器项目中无法修改。**不要** 使用管理员凭证进行 Elasticsearch 操作。创建仅具有用户所需权限的范围 Elasticsearch API 密钥。

如果 `elasticsearch-authn` 技能可用，请使用它创建 API 密钥——它涵盖完整生命周期（创建、授权、使无效、查询）并正确处理范围权限。如果技能未安装，请要求用户要么安装它，要么通过 **Kibana > Stack Management > API keys** 手动创建 API 密钥。创建后，使用项目特定标题格式（见 `manage-project` 技能的“凭证文件格式”部分）将 API 密钥保存到 `.elastic-credentials`，然后重新加载**不使用 `--include-admin**** 以从环境中删除管理员凭证：

```bash
eval $(python3 skills/cloud/manage-project/scripts/manage-project.py load-credentials \
  --name "<project-name>")
```

## 示例

### 使用默认值创建 Elasticsearch 项目

```bash
python3 skills/cloud/create-project/scripts/create-project.py create \
  --type elasticsearch \
  --name "my-search-project" \
  --region gcp-us-central1 \
  --optimized-for general_purpose \
  --wait
```

### 创建 observability 项目

```bash
python3 skills/cloud/create-project/scripts/create-project.py create \
  --type observability \
  --name "prod-o11y" \
  --region aws-eu-west-1 \
  --product-tier complete \
  --wait
```

### 创建 security 项目

```bash
python3 skills/cloud/create-project/scripts/create-project.py create \
  --type security \
  --name "siem-prod" \
  --region gcp-us-central1 \
  --product-tier complete \
  --wait
```

## 指南

- 如果 `EC_API_KEY` 未设置，请先运行 `cloud-setup` 技能。
- 始终在创建之前与用户确认项目配置。
- **切勿在聊天中显示密码或 API 密钥。** 请指示用户查看 `.elastic-credentials`。
- **切勿** 默默默认为项目类型。从上下文中推断并确认与用户。
- 默认为 `general_purpose` 优化。仅在用户明确请求时使用 `vector`。
- 默认为 observability 和 security 项目的 `complete` 产品层级。仅在用户明确请求时使用 `logs_essentials` 或 `essentials`。
- 始终传递 `--wait`，以便脚本轮询直到项目就绪。
- 如果凭证保存失败，请立即使用 `cloud-manage-project` 技能重置凭证。
- 创建后，建议创建范围的 API 密钥，而不是依赖管理员凭证。
- 区域创建后无法更改——在继续之前确认选择。

## 脚本参考

| 命令        | 描述                       |
| -------------- | --------------------------------- |
| `create`       | 创建新的无服务器项目   |
| `status`       | 获取项目初始化状态 |
| `list-regions` | 列出可用区域            |

| 标志              | 命令       | 描述                                                |
| ----------------- | -------------- | ---------------------------------------------------------- |
| `--type`          | create, status | 项目类型: `elasticsearch`, `observability`, `security` |
| `--name`          | create         | 项目名称 (必需)                                    |
| `--region`        | create         | 区域 ID (默认: `gcp-us-central1`)                     |
| `--id`            | status         | 项目 ID                                                 |
| `--optimized-for` | create         | Elasticsearch 子类型: `general_purpose` 或 `vector`       |
| `--product-tier`  | create         | Observability/security 层级 (见“产品层级”部分)  |
| `--wait`          | create         | 轮询直到项目就绪前退出           |

## 环境变量

| 变量                | 是否必需 | 描述                                                              |
| ----------------------- | -------- | ------------------------------------------------------------------------ |
| `EC_API_KEY`            | 是      | Elastic Cloud API 密钥                                                    |
| `EC_BASE_URL`           | 否       | Cloud API 基础 URL (默认: `https://api.elastic-cloud.com`)            |
| `ELASTICSEARCH_URL`     | 输出   | Elasticsearch URL (创建后通过 `load-credentials` 加载)         |
| `KIBANA_URL`            | 输出   | Kibana URL (创建后通过 `load-credentials` 加载)                |
| `APM_URL`               | 输出   | APM 端点 (observability 项目仅限)                               |
| `INGEST_URL`            | 输出   | OTLP 摄取端点 (observability 和 security 项目)               |
| `ELASTICSEARCH_API_KEY` | 输出   | Elasticsearch API 密钥 (步骤 8 创建，通过 `load-credentials` 加载) |

## 额外资源

- 有关完整 API 详细信息、请求/响应模式以及项目类型选项，请参阅
  [references/api-reference.md](references/api-reference.md)
