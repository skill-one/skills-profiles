# Elestio 技能

**版本:** 2.3
**目的:** 在 Elestio DevOps 平台上部署和管理服务
**状态:** 即将使用
**最后更新:** 2026-09-22

Elestio 是一个完全托管的 DevOps 平台。专用虚拟机（非共享 Kubernetes）。400 多个开源模板，9 个云提供商，100 多个地区。处理部署、安全、更新、备份、监控、支持。

此技能使用 **官方 Elestio CLI** (`elestio` 命令，通过 `npm install -g elestio` 安装)。
当 **Elestio MCP 连接器** 可用时（例如 `deploy_template`、`deploy_catalog_pipeline`、`list_clusters` 等工具），请使用其工具：以下规则同样适用。请参阅“使用 Elestio MCP 连接器”以匹配每个命令的工具。

---

## 何时使用此技能

当以下情况使用此技能时：
- 用户想要部署 PostgreSQL、MySQL、Redis、MongoDB、Elasticsearch 等。
- 用户说“部署”、“启动”、“创建服务器”、“我需要数据库”
- 用户提到任何开源软件（WordPress、Grafana、n8n、Metabase 等）
- 用户想要通过 CI/CD 部署自定义代码
- 用户需要管理备份、防火墙、SSL、SSH 访问
- 用户询问服务状态、成本或凭证

**触发短语:**
- "Deploy PostgreSQL" -> `elestio deploy postgresql`
- "I need a Redis cache" -> `elestio deploy redis`
- "Set up n8n for automation" -> `elestio deploy n8n`
- "Deploy my app from GitHub" -> CI/CD 工作流（阶段 4）
- "What services are running?" -> `elestio services`
- "How much is this costing?" -> `elestio billing`

## 不应使用此技能的情况

- **初始账户设置** - 注册、支付、审批必须由人工手动完成
- **交互式 SSH 会话** - 使用直接 SSH
- **复杂的 Docker Compose 编辑** - 直接 SSH 到服务器

---

## 决策树：我应该部署什么？

有三个部署形状，而不是两个。选择错误是最常见的导致部署失败的原因。

```
软件是否在 Elestio 目录中？ (elestio templates search <name>)
|
+-- 是
|   |
|   +-- 用户想要管理的独立 VM 吗？ (生产数据库，任何需要备份 / 监控 / 支持)
|   |       -> 管理服务
|   |          elestio deploy <template> --project <id>
|   |
|   +-- 用户想要复制 / 高可用性吗？
|   |       -> 集群   (19 个模板仅限: elestio clusters templates)
|   |          elestio deploy <template> --cluster --nodes <n> --project <id>
|   |
|   +-- 用户想要便宜的还是一个 VM 上运行多个应用？
|           -> 目录模板的管道
|              elestio cicd deploy-template <software> --target <vmID>
|
+-- 否，它是用户自己的代码
    |
    +-- 在 Git 仓库中？
    |       -> elestio cicd create --auto --target <vmID> --name X --repo owner/repo
    |
    +-- 只是一个 docker-compose 文件？
            -> elestio cicd create <pipeline.json>
```

### 关键：目录中的软件在管道中

要在 CI/CD 目标上运行目录软件（Vaultwarden、Redis、Metabase 等），您 **必须** 使用 `elestio cicd deploy-template` (MCP: `deploy_catalog_pipeline`)。您 **不能** 使用 `elestio cicd create` (MCP: `create_pipeline_docker` / `create_pipeline_auto`)。

`cicd create` 构建一个空的管道。它不知道软件的端口、环境变量或安装脚本，因此管道部署后什么都不会运行。这是最常报告的失败原因。

`deploy-template` 读取模板的 `elestio.yml`（来自 `github.com/elestio-examples/<software>）并从中配置管道。

```bash
# 正确的
elestio cicd deploy-template vaultwarden --target <vmID>

# 错误的 -- 生成一个空的管道
elestio cicd create --auto --target <vmID> --name vaultwarden --repo elestio-examples/vaultwarden
```

一些目录软件目前无法作为管道运行：n8n、Rybbit 和 WordPress 从其模板仓库挂载文件，而只有 Git 路径提供此功能，Git 路径目前不可用。CLI 和 MCP 都拒绝使用文件名。提供管理服务（`elestio deploy <template>`）。

要检查目录：
  elestio templates search <software-name>     # 所有内容
  elestio cicd templates <software-name>       # 可作为管道部署
  elestio clusters templates                   # 支持集群

---

## 使用 Elestio MCP 连接器

当 Elestio MCP 工具可用时（claude.ai 连接器，Claude Code MCP 服务器...），请使用它们而不是 CLI。它们涵盖相同的操作，此技能中的每条规则都适用于它们。破坏性工具需要 `"confirm": true`：先询问用户，就像你在 `--force` 之前一样。

| 任务 | CLI | MCP 工具 |
|---|---|---|
| 查找软件 | `elestio templates search <name>` | `search_templates` |
| 部署管理服务 | `elestio deploy <template>` | `deploy_template` |
| 部署集群 | `elestio deploy <template> --cluster --nodes N` | `deploy_template` with `cluster_nodes` (and `cluster_mode`) |
| 可以集群 | `elestio clusters templates` | `list_cluster_templates` |
| 等待部署 | `elestio wait <vmID>` | `wait_for_deployment` (对于集群，将逗号分隔的 `providerServerID` 原样传递) |
| CI/CD 目标 | `elestio deploy CI-CD-Target` | `deploy_cicd_target` |
| **目录软件在管道中** | `elestio cicd deploy-template <software> --target <vmID>` | **`deploy_catalog_pipeline`** (支持 `dry_run`) |
| 您自己的仓库在管道中 | `elestio cicd create --auto ...` | `create_pipeline_auto` |
| 您自己的 compose 在管道中 | `elestio cicd create <pipeline.json>` | `create_pipeline_docker` |
| 管道上的目标 | `elestio cicd pipelines <vmID>` | `list_pipelines` |
| 项目中的集群 | `elestio clusters` | `list_clusters` |
| 集群及其节点 | `elestio clusters info <clusterID>` | `get_cluster` |
| 提升副本 | `elestio clusters promote <clusterID> <vmID> --force` | `promote_cluster_node` |
| 自动故障转移开启/关闭 | `elestio clusters failover <clusterID> on\|off` | `set_cluster_auto_failover` |
| 重建副本 | `elestio clusters resync <clusterID> --force` | `resync_cluster` |
| 锁定/解锁集群 | `elestio clusters lock\|unlock <clusterID>` | `lock_cluster` / `unlock_cluster` |
| 添加节点 | `elestio clusters add-node <clusterID> [--dry-run]` | `add_cluster_node` (支持 `dry_run`) |
| 删除节点 | `elestio clusters remove-node <clusterID> <vmID> --force` | `remove_cluster_node` |
| 集群防火墙 | `elestio clusters firewall\|firewall-restrict\|firewall-open <clusterID>` | `get_cluster_firewall` / `set_cluster_port_access` |
| 删除集群 | `elestio clusters delete <clusterID> --force` | `delete_cluster` |
| 管道构建历史记录 | `elestio cicd pipeline-history <vmID> <pipelineID>` | `get_pipeline_history` |
| 删除管道 | `elestio cicd pipeline-delete <vmID> <pipelineID> --force` | `delete_pipeline` |
| 服务的实时日志 | `elestio logs <vmID>` | `get_service_logs` |
| 服务的审计跟踪 | `elestio audits <vmID>` | `get_service_audits` |

MCP 没有针对 `deploy_template` 的 dry run：在集群之前，您需要自己声明 VM 数量和月度成本（使用 `list_providers_and_sizes` 获取每台 VM 的价格）并获取用户的许可。

---

## 设置（一次性 -- 需要人工操作）

### 前提条件

1. **创建账户：** https://dash.elest.io/signup
2. **验证邮箱：** 检查收件箱，点击验证链接
3. **添加信用卡：** https://dash.elest.io/account/payment
4. **等待批准：** 通常即时，有时 24-48 小时
5. **创建 API 令牌：** https://dash.elest.io/account/security -> 管理 API 令牌 -> 创建令牌
6. **配置技能：** 给电子邮件 + API 令牌给代理

### 配置凭证

```bash
elestio login --email "user@domain.com" --token "xxx_..."
elestio auth test
```

### 验证设置

```bash
# 应显示：[成功] 已认证为 user@domain.com
elestio auth test

# 列出项目（应至少显示一个）
elestio projects
```

---

## 快速入门示例

### 部署 PostgreSQL（2 个命令）

```bash
# 1. 查找模板 ID
elestio templates search postgresql
# -> ID: 11, PostgreSQL

# 2. 部署 (使用默认值: netcup/nbg/MEDIUM-2C-4G)
elestio deploy postgresql --project 112 --name my-db
# -> 等待部署，准备好时显示凭证
```

### 部署 Redis 缓存

```bash
elestio deploy redis --project 112
```

### 部署 WordPress

```bash
elestio deploy wordpress --project 112
```

### 部署集群（复制 / 高可用性）

```bash
# 1. 检查软件是否支持集群并查看其最小节点数
elestio clusters templates

# 2. **始终先进行 dry-run：** 计费按 VM 计算，`--nodes 3` 将计费 3 个 VM
elestio deploy postgresql --cluster --nodes 3 --project 112 --dry-run

# 3. 部署
elestio deploy postgresql --cluster --nodes 3 --project 112

# 4. 跟踪
elestio clusters list --project 112
elestio clusters info <clusterID>
```

规则：
- `--nodes` 是总数，包括主节点。`--nodes 3` 是 1 个主节点 + 2 个副本，计费 3 个 VM。
- ClickHouse、Vault、OpenSearch、RabbitMQ、rke2 和 Nats 至少需要 3 个节点。
- 其他软件从 2 开始。最大值为 15。
- `--cluster-mode multi-master` 仅适用于 MySQL；所有其他软件都是 `primary-replica`（默认值）。

### 将目录软件作为管道部署（Vaultwarden、Redis、Metabase...）

当用户想要在 CI/CD 目标上而不是专用 VM 上运行目录软件时，请使用此方法。

```bash
# 1. 如果不存在 CI/CD 目标，则创建一个（这是一个 VM；管道共享它）
elestio deploy CI-CD-Target --project 112 --name my-target
# -> 记下 vmID

# 2. 确认软件可用为管道模板
elestio cicd templates vaultwarden

# 3. **始终先进行 dry-run：** 它将打印将要应用的端口、环境变量和生命周期挂钩，并且不会创建任何内容
elestio cicd deploy-template vaultwarden --target <vmID> --no-git --dry-run

# 4. 部署
elestio cicd deploy-template vaultwarden --target <vmID>
```

成功后，CLI 将打印软件的 URL、登录名和生成的密码。

**两种路线:**

| | compose (默认) | git (`--owner <git-user>`)
|---|---|---|
| 需要连接的 Git 账户 | 否 | 是 |
| 生命周期脚本 (preInstall/postInstall) | 跳过 | 运行 |
| compose 挂载的仓库文件 | 不可用 | 可用 |
| 适用 | 模板不需要仓库文件 | 每个模板 |

**git 路径当前不可用：** 它需要 `POST /api/cicd/createRepoByTemplate`，Elestio API 返回 404（控制器存在，但未在后台路由白名单中注册）。

**compose 路径不适用于每个模板。** 如果 compose 绑定挂载来自仓库的文件，CLI 将使用文件名拒绝。不要传递 `--force` 来绕过它：Docker 会创建一个缺失的文件作为目录，容器将无法启动。告诉用户软件需要 git 路径，它目前被阻止，并提供管理服务（`elestio deploy <template>`）。

始终验证部署而不是假设它工作：

```bash
elestio cicd pipelines <vmID>                          # 构建列必须为 "success"
elestio cicd pipeline-history <vmID> <pipelineID>      # 状态、持续时间、日志文件
```

### 从 GitHub 部署自定义应用（用户自己的代码）

```bash
# 1. 部署 CI/CD 目标
elestio deploy CI-CD-Target --project 112 --name my-cicd

# 2. 自动创建管道
elestio cicd create --auto --target <vmID> --name my-app --repo owner/repo --mode github --auth-id <authID>
# -> 网站位于 https://<name>-u<userID>.vm.elestio.app/
```

仅用于用户的自己的仓库。对于目录软件，请使用 `cicd deploy-template` 而不是 -- 见上。

### 手动部署自定义应用（手动 -- Docker 模式）

```bash
# 1. 部署 CI/CD 目标
elestio deploy CI-CD-Target --project 112 --name my-cicd

# 2. 添加 SSH 密钥以供代理访问
elestio ssh-keys add <vmID> --name "agent-key" --key "ssh-ed25519 AAAA..."

# 3. 生成管道配置
elestio cicd template docker > pipeline.json
# 使用正确的 CI/CD 目标信息编辑 pipeline.json（见下面的 JSON 参考）

# 4. 创建管道
elestio cicd create pipeline.json

# 5. SSH 并配置
ssh root@<ipv4>
cd /opt/app/<pipeline-name>
# 编辑 docker-compose.yml，添加代码，docker-compose up -d
```

#### 管道 JSON 参考（Docker 模式 -- `createCiCdExistServer` 负载）

**不要手动编写。** 使用 `elestio cicd template docker` 生成，并将 `REPLACE` 值替换。端点接收仪表板的整个表单状态，任何偏差都会导致 500 或无法构建的管道。当前形状（CLI 1.1.0，已验证为实时）：

```json
{
  "cluster": {
    "isCluster": false,
    "createNew": false,
    "target": {
      "displayName": "REPLACE",
      "id": "REPLACE",
      "serverName": "REPLACE",
      "vmID": "REPLACE",
      "vmProvider": "REPLACE",
      "vmRegion": "REPLACE",
      "levelName": "Elestio-services",
      "projectID": "REPLACE"
    }
  },
  "gitData": {},
  "imageData": {
    "isPrivate": false,
    "compose": "services:\n  nginx:\n    image: nginx:alpine\n    ports:\n      - \"172.17.0.1:3000:80\"\n    volumes:\n      - ./html:/usr/share/nginx/html:ro",
    "dockerExample": "",
    "repoName": "CustomDocker"
  },
  "configData": {
    "buildDir": "/",
    "rootDir": "/",
    "runTime": "NodeJs",
    "buildCmd": "",
    "runCmd": "",
    "installCmd": "",
    "framework": "NoFramework",
    "version": "20"
  },
  "ports": [
    {
      "protocol": "HTTPS",
      "targetProtocol": "HTTP",
      "listeningPort": "443",
      "targetPort": 3001,
      "public": true,
      "targetIP": "172.17.0.1",
      "path": "/",
      "isAuth": false,
      "login": "",
      "password": "",
      "loginTitle": ""
    }
  ],
  "variables": "",
  "isPublicGitRepo": false,
  "exposedPorts": [
    {
      "protocol": "HTTP",
      "hostPort": "3000",
      "containerPort": "3000",
      "interface": "172.17.0.1"
    }
  ],
  "gitVolumeConfig": [
    {}
  ],
  "isNeedToCreateRepo": false,
  "gitUserFormData": {
    "selectedUser": "",
    "searchGitUser": "",
    "gitOrgsFilteredList": {
      "GITHUB": [],
      "GITLAB": []
    },
    "gitOrgsList": [],
    "selectedRepo": {},
    "thirdPartyRepoInput": "",
    "gitScopesUsers": [],
    "thirdPartyRepoScopeName": "",
    "getGitScopeUser": {
      "GITHUB": [],
      "GITLAB": []
    },
    "thirdPartyRepoName": "",
    "thirdPartyRepoPrivate": false,
    "loadSearch": false
  },
  "lifeCycleCommand": {
    "preInstallCommand": "",
    "postInstallCommand": "",
    "preBackupCommand": "",
    "postBackupCommand": "",
    "preRestoreCommand": "",
    "postRestoreCommand": "",
    "preUpdateCommand": "",
    "postUpdateCommand": "",
    "preDeployCommand": "",
    "postDeployCommand": ""
  },
  "monoRepoWorkSpaces": [
    ""
  ],
  "copyCommandConfig": [],
  "CICDMode": "DockerCompose",
  "projectID": "REPLACE",
  "pipelineName": "REPLACE",
  "isMovePipeline": false,
  "authID": null
}
```

`cluster.target` 值来自 `elestio cicd targets`：`id` 是目标的 **serverID**（后端读取它），`vmID` 是其 vmID。

**常见错误：** 使用 `serverID` 而不是 `vmID`（或反之）。它们是同一服务的不同数字。

---

## VM 架构

每个 Elestio 服务都在一个专用的 VM 上运行：

```
/opt/elestio/nginx/          <- 反向代理（自动配置，不要修改）
/opt/app/                    <- 您的应用
    +-- docker-compose.yml   <- 对于目录服务
    +-- <pipeline_name>/     <- 对于 CI/CD 管道
```

- 反向代理自动处理 HTTPS 终止
- SSL 证书通过 Let's Encrypt 自动生成
- 端口 `172.17.0.1:XXXX` 是内部 Docker 网络接口

---

## 支持级别

| 计划 | 价格 | 响应时间 |
|---|-------|---------------|
| level1 | 包含 | 48 小时（电子邮件） |
| level2 | +$50/服务/月 | 24 小时（优先） |
| level3 | +$200/服务/月 | 4 小时（专属工程师） |

---

## 链接

- **仪表板：** https://dash.elest.io
- **API 文档：** https://api-doc.elest.io
- **支持：** support@elest.io
- **模板：** 400 多个在 https://elest.io/open-source
- **CLI：** `npm install -g elestio`
