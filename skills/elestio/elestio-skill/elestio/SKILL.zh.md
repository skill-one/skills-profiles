---
name: elestio
description: 在 Elestio DevOps 平台上部署和管理服务。当用户希望在 Elestio 上部署应用程序、数据库或基础设施，管理项目、服务、集群、CI/CD 管道、备份、域名、防火墙、卷或计费时使用。涵盖 9 个云提供商的 400 多个开源模板，支持数据库集群，以及将目录软件部署为 CI/CD 管道。
---

# Elestio 技能

**版本:** 2.3
**目的:** 在 Elestio DevOps 平台上部署和管理服务
**状态:** 可用
**最后更新:** 2026-09-22

Elestio 是一个完全托管的 DevOps 平台。专用虚拟机（非共享 Kubernetes）。400 多个开源模板，9 个云服务提供商，100 多个区域。处理部署、安全、更新、备份、监控和支持。

此技能使用官方的 Elestio CLI（`elestio` 命令，通过 `npm install -g elestio` 安装）。
当 **Elestio MCP 连接器** 可用时（例如 `deploy_template`、`deploy_catalog_pipeline`、`list_clusters` 等工具），请使用其工具：以下规则同样适用。请参阅“使用 Elestio MCP 连接器”以获取与每个命令匹配的工具。

---

## 何时使用此技能

当用户：
- 想要部署 PostgreSQL、MySQL、Redis、MongoDB、Elasticsearch 等。
- 说“部署”、“启动”、“创建服务器”、“我需要数据库”。
- 提及任何开源软件（WordPress、Grafana、n8n、Metabase 等）。
- 想要通过 CI/CD 部署自定义代码。
- 需要管理备份、防火墙、SSL、SSH 访问。
- 询问服务状态、成本或凭证时。

**触发短语：**
- "部署 PostgreSQL" -> `elestio deploy postgresql`
- "我需要 Redis 缓存" -> `elestio deploy redis`
- "为自动化设置 n8n" -> `elestio deploy n8n`
- "从 GitHub 部署我的应用" -> CI/CD 工作流（第 4 步）
- "正在运行哪些服务？" -> `elestio services`
- "这个成本是多少？" -> `elestio billing`

## 何时不使用此技能

- **初始账户设置** - 注册、支付、审批必须由人工手动完成。
- **交互式 SSH 会话** - 使用直接 SSH。
- **复杂的 Docker Compose 编辑** - 直接 SSH 到服务器。

---

## 决策树：我应该部署什么？

有三种部署形状，而不是两种。选择错误是导致部署失败的最常见原因。

```
软件是否在 Elestio 目录中？  (elestio templates search <name>)
|
+-- 是
|   |
|   +-- 用户是否想要一个管理的、隔离的虚拟机？  (生产数据库、需要备份/监控/支持的内容)
|   |       -> 管理服务
|   |          elestio deploy <模板> --project <id>
|   |
|   +-- 用户是否想要复制/高可用性？
|   |       -> 集群   (仅 19 个模板：elestio clusters templates)
|   |          elestio deploy <模板> --cluster --nodes N --project <id>
|   |
|   +-- 用户是否想要便宜一点的，或者一个虚拟机上运行多个应用？
|           -> 目录模板的管道
|              elestio cicd deploy-template <软件> --target <vmID>
|
+-- 否，这是用户自己的代码
    |
    +-- 在 Git 仓库中？
    |       -> elestio cicd create --auto --target <vmID> --name X --repo owner/repo
    |
    +-- 只是一个 docker-compose 文件？
            -> elestio cicd create <pipeline.json>
```

### 关键：目录软件在管道中

要在 CI/CD 目标上运行目录软件（Vaultwarden、Redis、Metabase、...），您**必须**使用 `elestio cicd deploy-template`（MCP：`deploy_catalog_pipeline`）。您**不能**使用 `elestio cicd create`（MCP：`create_pipeline_docker` / `create_pipeline_auto`）。

`cicd create` 构建一个**空**的管道。它不知道软件的端口、环境变量或安装脚本，因此管道会部署但不会运行。这是最常报告的失败原因。

`deploy-template` 读取模板的 `elestio.yml`（来自 `github.com/elestio-examples/<软件>`），并从中配置管道。

```bash
# 正确
elestio cicd deploy-template vaultwarden --target <vmID>

# 错误 -- 生成一个空管道
elestio cicd create --auto --target <vmID> --name vaultwarden --repo elestio-examples/vaultwarden
```

目前，某些目录软件无法作为管道运行：n8n、Rybbit 和 WordPress 从其模板仓库挂载文件，这只有 Git 路径提供，而 Git 路径目前不可用。CLI 和 MCP 都会拒绝它们并报文件名。请提供管理服务（`elestio deploy <模板>`）。

要检查目录：
  elestio templates search <软件名>     # 所有内容
  elestio cicd templates <软件名>       # 可作为管道部署
  elestio clusters templates                   # 支持集群

---

## 使用 Elestio MCP 连接器

当 Elestio MCP 工具可用时（claude.ai 连接器、Claude Code MCP 服务器...），请使用它们而不是 CLI。它们涵盖相同的操作，此技能中的每条规则都适用于它们。破坏性工具需要 `"confirm": true`：先询问用户，就像在 `--force` 之前一样。

| 任务 | CLI | MCP 工具 |
|---|---|---|
| 查找软件 | `elestio templates search <name>` | `search_templates` |
| 部署管理服务 | `elestio deploy <template>` | `deploy_template` |
| 部署集群 | `elestio deploy <template> --cluster --nodes N` | `deploy_template` with `cluster_nodes` (and `cluster_mode`) |
| 支持集群的软件 | `elestio clusters templates` | `list_cluster_templates` |
| 等待部署完成 | `elestio wait <vmID>` | `wait_for_deployment` (对于集群，将逗号分隔的 `providerServerID` 原样传递) |
| CI/CD 目标 | `elestio deploy CI-CD-Target` | `deploy_cicd_target` |
| **在管道中部署目录软件** | `elestio cicd deploy-template <软件> --target <vmID>` | **`deploy_catalog_pipeline`** (支持 `dry_run`) |
| 您自己的仓库在管道中 | `elestio cicd create --auto ...` | `create_pipeline_auto` |
| 您自己的 compose 在管道中 | `elestio cicd create <pipeline.json>` | `create_pipeline_docker` |
| 目标上的管道 | `elestio cicd pipelines <vmID>` | `list_pipelines` |
| 项目中的集群 | `elestio clusters` | `list_clusters` |
| 集群及其节点 | `elestio clusters info <clusterID>` | `get_cluster` |
| 提升副本 | `elestio clusters promote <clusterID> <vmID> --force` | `promote_cluster_node` |
| 自动故障转移开关 | `elestio clusters failover <clusterID> on\|off` | `set_cluster_auto_failover` |
| 重建副本 | `elestio clusters resync <clusterID> --force` | `resync_cluster` |
| 锁定/解锁集群 | `elestio clusters lock\|unlock <clusterID>` | `lock_cluster` / `unlock_cluster` |
| 添加节点 | `elestio clusters add-node <clusterID> [--dry-run]` | `add_cluster_node` (支持 `dry_run`) |
| 删除节点 | `elestio clusters remove-node <clusterID> <vmID> --force` | `remove_cluster_node` |
| 集群防火墙 | `elestio clusters firewall\|firewall-restrict\|firewall-open <clusterID>` | `get_cluster_firewall` / `set_cluster_port_access` |
| 删除集群 | `elestio clusters delete <clusterID> --force` | `delete_cluster` |
| 管道构建历史记录 | `elestio cicd pipeline-history <vmID> <pipelineID>` | `get_pipeline_history` |
| 删除管道 | `elestio cicd pipeline-delete <vmID> <pipelineID> --force` | `delete_pipeline` |
| 服务实时日志 | `elestio logs <vmID>` | `get_service_logs` |
| 服务审计记录 | `elestio audits <vmID>` | `get_service_audits` |

MCP 没有 `deploy_template` 的 dry run：在集群之前，请自行声明虚拟机数量和月度成本（`list_providers_and_sizes` 提供每个虚拟机的价格）并获取用户的同意。

---

## 设置（一次性 -- 需要人工操作）

### 前提条件

1. **创建账户：** https://dash.elest.io/signup
2. **验证邮箱：** 检查收件箱，点击验证链接
3. **添加信用卡：** https://dash.elest.io/account/payment
4. **等待批准：** 通常即时，有时需要 24-48 小时
5. **创建 API 令牌：** https://dash.elest.io/account/security -> 管理 API 令牌 -> 创建令牌
6. **配置技能：** 向代理提供邮箱 + API 令牌

### 配置凭证

```bash
elestio login --email "user@domain.com" --token "xxx_..."
elestio auth test
```

### 验证设置

```bash
# 应显示：[SUCCESS] Authenticated as user@domain.com
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

# 2. 部署（使用默认值：netcup/nbg/MEDIUM-2C-4G）
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

### 部署集群（复制/高可用性）

```bash
# 1. 检查软件是否支持集群并查看其最小节点数
elestio clusters templates

# 2. **始终**先进行 dry-run：按虚拟机计费，--nodes 3 会计费 3 个虚拟机
elestio deploy postgresql --cluster --nodes 3 --project 112 --dry-run

# 3. 部署
elestio deploy postgresql --cluster --nodes 3 --project 112

# 4. 跟进
elestio clusters list --project 112
elestio clusters info <clusterID>
```

规则：
- `--nodes` 是**总数**，包括主节点。`--nodes 3` = 1 主节点 + 2 副本。
- ClickHouse、Vault、OpenSearch、RabbitMQ、rke2 和 Nats 至少需要 3 个节点。
- 其他软件从 2 个开始。最大为 15 个。
- `--cluster-mode multi-master` 仅适用于 MySQL；其他都是 `primary-replica`（默认）。

### 作为管道部署目录软件（Vaultwarden、Redis、Metabase...）

当用户希望在 CI/CD 目标上而不是专用虚拟机上部署目录软件时，请使用此路线。

```bash
# 1. 如果不存在，创建 CI/CD 目标（这是一个虚拟机；管道共享它）
elestio deploy CI-CD-Target --project 112 --name my-target
# -> 记下 vmID

# 2. 确认软件可用作管道模板
elestio cicd templates vaultwarden

# 3. **始终**先进行 dry-run：它会打印将要应用的端口、环境变量和生命周期钩子
#    并且不会创建任何内容
elestio cicd deploy-template vaultwarden --target <vmID> --dry-run

# 4. 部署
elestio cicd deploy-template vaultwarden --target <vmID>
```

成功后，CLI 会打印软件的 URL、登录名和生成的密码。

**两条路线：**

| | compose（默认） | git (`--owner <git-user>`) |
|---|---|---|
| 需要连接的 Git 账户 | 否 | 是 |
| 生命周期脚本（preInstall/postInstall） | 跳过 | 运行 |
| compose 挂载的仓库文件 | 不可用 | 可用 |
| 适用范围 | 需要仓库文件的模板 | 每个模板 |

**git 路线目前不可用**：它需要 `POST /api/cicd/createRepoByTemplate`，而 Elestio API 返回 404（控制器存在，但未在后台路由白名单中注册）。

**compose 路线不适用于所有模板。** 如果 compose 绑定挂载了来自仓库的文件，CLI 会拒绝并报文件名。不要传递 --force 来绕过它：Docker 会创建缺失的文件作为目录，容器启动失败。告诉用户该软件需要 git 路线，目前被阻塞，并提供管理服务（`elestio deploy <模板>`）。

验证：vaultwarden、redis 和 metabase 在 compose 路线上部署正常；n8n、rybbit 和 wordpress 需要 git 路线。

**始终验证部署，而不是假设它成功：**

```bash
elestio cicd pipelines <vmID>                          # Build 列必须显示 "success"
elestio cicd pipeline-history <vmID> <pipelineID>      # 状态、持续时间、日志文件
```

### 从 GitHub 部署自定义应用（用户自己的代码）

```bash
# 1. 部署 CI/CD 目标
elestio deploy CI-CD-Target --project 112 --name my-cicd

# 2. 自动创建管道
elestio cicd create --auto --target <vmID> --name my-app --repo owner/repo --mode github --auth-id <authID>
# -> 网站已上线：https://<name>-u<userID>.vm.elestio.app/
```

仅适用于用户自己的仓库。对于目录软件，请使用 `cicd deploy-template` 而不是——见上文。

### 手动部署自定义应用（Docker 模式）

```bash
# 1. 部署 CI/CD 目标
elestio deploy CI-CD-Target --project 112 --name my-cicd

# 2. 添加 SSH 密钥以供代理访问
elestio ssh-keys add <vmID> --name "agent-key" --key "ssh-ed25519 AAAA..."

# 3. 生成管道配置
elestio cicd template docker > pipeline.json
# 编辑 pipeline.json，填写正确的 CI/CD 目标信息（见 JSON 参考文档）

# 4. 创建管道
elestio cicd create pipeline.json

# 5. SSH 并配置
ssh root@<ipv4>
cd /opt/app/<pipeline-name>
# 编辑 docker-compose.yml，添加代码，docker-compose up -d
```

#### 管道 JSON 参考文档（Docker 模式 -- `createCiCdExistServer` 负载）

**不要手动编写。** 使用 `elestio cicd template docker` 生成，并替换 `REPLACE` 值。端点会接收仪表板的整个表单状态，任何差异都会导致 500 错误或从未构建的管道。当前形状（CLI 1.1.0，已在线验证）：

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

`cluster.target` 值来自 `elestio cicd targets`：`id` 是目标的**serverID**（后端会读取它），`vmID` 是其 vmID。

**要避免的常见负载错误：**

| 字段 | 错误 | 正确 |
|-------|-------|---------|
| `CICDMode` | `"DOCKER"` | `"DockerCompose"` |
| `configData.runTime` | `runtime` (小写 t) | `runTime` (大写 T) |
| `configData.framework` | `""` | `"NoFramework"` |
| `imageData` | `{ imageName, imageTag, registryUrl }` | `{ isPrivate, compose, dockerExample, repoName }` |
| `gitData` (docker 模式) | `{ projectName, branch, ... }` | `{}` (空对象) |
| `authID` (docker 模式) | `"0"` | `null` |
| `isPublicGitRepo` | `"false"` (字符串) | `false` (布尔值) |
| `gitVolumeConfig` | `[]` | `[{}]` |
| `ports[]` | `{ targetPort, publishedPort, isDefault }` | `{ protocol, targetProtocol, listeningPort, targetPort, targetIP, public, path, isAuth, login, password, loginTitle }` |
| `exposedPorts` | 省略 | `[{ protocol, hostPort, containerPort, interface }]` |
| `cluster.target` | 仅 `vmID` | `id` (服务器ID), `vmID`, `vmProvider`, `vmRegion`, `levelName`, `projectID`, `displayName`, `serverName` |
| `nonRepoWorkSpaces` | 存在 | 删除 -- 使用 `monoRepoWorkSpaces` 代替 |
| `variables` | 省略或 `[]` (数组) | `""` 或 `"KEY=value\nKEY2=value2"` (字符串; 后端运行 `variables.trim()`) |
| `lifeCycleCommand` (compose, 无仓库) | 类似 `./scripts/preInstall.sh` 的钩子路径 | 所有 `""`: 代理在 docker compose 前会更改路径并失败构建 |

---

## 命令参考

### 身份验证 & 配置

```bash
elestio login --email X --token Y  # 设置凭证
elestio auth test                  # 验证身份验证
elestio whoami                     # 显示当前用户
elestio config                     # 显示当前配置
elestio config --set-default-project X  # 设置默认项目
```

### 目录 (无需身份验证)

```bash
elestio templates                  # 列出所有 400+ 模板
elestio templates search <query>   # 按名称搜索
elestio templates info <name>      # 模板详情
elestio categories                 # 列出分类
elestio sizes                      # 所有提供商/区域/大小组合
elestio sizes --provider netcup    # 按提供商过滤
```

### 项目

```bash
elestio projects                   # 列出所有项目
elestio projects create <name>     # 创建项目
elestio projects delete <id> --force  # 删除项目
elestio projects members <id>      # 列出成员
elestio projects add-member <id> <email>
elestio projects remove-member <id> <memberId>
```

### 服务

```bash
elestio services                   # 列出所有服务
elestio services --project 123     # 按项目过滤
elestio service <vmID>             # 服务详情
elestio deploy <template> --project X --name Y
elestio deploy <template> --cluster --nodes 3   # 集群 (见下文 Clusters)
elestio deploy CI-CD-Target --project X         # 部署 CI/CD 目标虚拟机
elestio delete-service <vmID> --force
elestio move-service <vmID> <targetProjectId>
elestio wait <vmID>                # 等待部署
```

### 电源管理

```bash
elestio reboot <vmID>              # 优雅重启
elestio reset <vmID>               # 强制重启
elestio shutdown <vmID>            # 优雅关机
elestio poweroff <vmID>            # 强制关机
elestio poweron <vmID>             # 开机
elestio restart-stack <vmID>       # 仅重启 Docker (最快)
elestio lock <vmID>                # 启用终止保护
elestio unlock <vmID>              # 禁用终止保护
elestio resize <vmID> --size LARGE-4C-8G  # 升级/降级虚拟机大小
```

### 防火墙

```bash
elestio firewall get <vmID>        # 列出规则
elestio firewall enable <vmID> --rules '[{"type":"INPUT","port":"22","protocol":"tcp","targets":["0.0.0.0/0"]}]'
elestio firewall update <vmID> --rules '[...]'
elestio firewall disable <vmID>
```

### SSL / 自定义域名

```bash
elestio ssl list <vmID>            # 列出域名
elestio ssl add <vmID> <domain>    # 添加并自动 SSL
elestio ssl remove <vmID> <domain>
```

### SSH 密钥

```bash
elestio ssh-keys list <vmID>       # 列出密钥
elestio ssh-keys add <vmID> --name "name" --key "ssh-ed25519 AAAA..."
elestio ssh-keys remove <vmID> --name "name"
```

**注意:** 添加 SSH 密钥时，仅提供密钥类型和密钥数据 (例如，`ssh-ed25519 AAAA...`)。不要在密钥末尾包含注释/电子邮件。

### 自动更新

```bash
elestio updates system-enable <vmID> --day 0 --hour 5 --security-only
elestio updates system-disable <vmID>
elestio updates system-now <vmID>  # 立即运行 OS 更新
elestio updates app-enable <vmID> --day 0 --hour 3
elestio updates app-disable <vmID>
elestio updates app-now <vmID>     # 立即运行应用更新
elestio change-version <vmID> <version>  # 例如，PostgreSQL 15
```

### 报警

```bash
elestio alerts get <vmID>          # 获取当前规则
elestio alerts enable <vmID> --rules '{...}' --cycle 60
elestio alerts disable <vmID>
```

### 备份

```bash
# 本地备份 (应用级)
elestio backups local-list <vmID>
elestio backups local-take <vmID>
elestio backups local-restore <vmID> /opt/app-backups/backup.zst
elestio backups local-delete <vmID> /opt/app-backups/backup.zst

# 远程备份 (Elestio 管理)
elestio backups remote-list <vmID>
elestio backups remote-take <vmID>
elestio backups remote-restore <vmID> <snapshot-name>
elestio backups auto-enable <vmID>
elestio backups auto-disable <vmID>

# S3 外部备份
elestio s3-backup verify <vmID> --key X --secret Y --bucket Z --endpoint S
elestio s3-backup enable <vmID> --key X --secret Y --bucket Z --endpoint S
elestio s3-backup disable <vmID>
elestio s3-backup take <vmID>
elestio s3-backup list <vmID>
elestio s3-backup restore <vmID> <backup-key>
elestio s3-backup delete <vmID> <backup-key>
```

### 快照 (提供商级)

```bash
elestio snapshots list <vmID>      # 列出所有快照
elestio snapshots take <vmID>      # 创建手动快照
elestio snapshots restore <vmID> <id>  # 恢复快照 (0 = 最新的)
elestio snapshots delete <vmID> <id>   # 删除快照
elestio snapshots auto-enable <vmID>   # 启用自动快照
elestio snapshots auto-disable <vmID>  # 禁用自动快照
```

### 访问 & 凭证

```bash
elestio credentials <vmID>         # 应用 URL + 登录
elestio ssh <vmID>                 # SSH 终端 URL
elestio ssh <vmID> --direct        # 直接 SSH 命令
elestio vscode <vmID>              # VSCode 网络 URL
elestio files <vmID>               # 文件浏览器 URL
elestio logs <vmID>                # 实时应用日志 (临时 URL); --mode install 用于安装日志
elestio audits <vmID> [--days 7]   # 谁在服务上做了什么
```

### 卷

**注意:** 卷支持取决于云提供商。Hetzner 支持完整的卷操作。一些提供商如 netcup 有限制或无卷支持。

```bash
elestio volumes                    # 列出项目中的所有卷
elestio volumes create --name X --size 10
elestio volumes service-list <vmID>    # 列出附加到服务
elestio volumes service-create <vmID> --name X --size 10
elestio volumes resize <vmID> <volumeID> --size 20
elestio volumes detach <vmID> <volumeID>
elestio volumes delete <vmID> <volumeID>
elestio volumes protect <vmID> <volumeID>
```

### 集群

```bash
elestio clusters templates                  # 支持集群的软件
elestio clusters                            # 列出项目中的集群
elestio clusters info <clusterID>           # 详情 + 节点
elestio clusters nodes <clusterID>          # 仅活动节点

# 创建通过 deploy，不是通过 clusters
elestio deploy <template> --cluster --nodes <n> [--cluster-mode multi-master]

# 操作 -- 所有破坏性操作都需要 --force
elestio clusters promote <clusterID> <vmID> --force   # 提升副本
elestio clusters failover <clusterID> on|off          # 自动故障转移开关，不会立即切换
elestio clusters resync <clusterID> --force           # 删除副本数据
elestio clusters lock <clusterID>                     # 终止保护
elestio clusters unlock <clusterID>
elestio clusters delete <clusterID> --force           # 删除所有节点 (不是 delete-service)

# 节点 -- 首先使用 add-node 进行 dry-run: 作为额外 VM 计费
elestio clusters add-node <clusterID> --dry-run       # 复制主节点: 提供商、区域、大小、版本
elestio clusters add-node <clusterID> [--size X] [--region Y]
elestio clusters remove-node <clusterID> <vmID> --force   # 副本仅

# 防火墙 -- 适用于每个节点; 集群的节点保持允许
elestio clusters firewall <clusterID>
elestio clusters firewall-restrict <clusterID> --port 25432 --ips 203.0.113.7,198.51.100.0/24
elestio clusters firewall-open <clusterID> --port 25432
```

**约束 (CLI 在调用 API 前强制执行这些规则):**

| 规则 | 值 |
|---|---|
| `--nodes` 计数 | 总节点数，主节点包括在内 |
| 最小值，大多数软件 | 2 |
| 最小值：ClickHouse, Vault, OpenSearch, RabbitMQ, rke2, Nats | 3 (多数) |
| 最大值 | 15 |
| `--cluster-mode multi-master` | MySQL 仅 |
| 计费 | 按 VM. `--nodes 5` 计费 5 个 VM。 |
| 手动切换主节点 | `promote`，不是 `failover` (后者仅切换自动故障转移) |
| 副本 | 只读，无 SSL: `sslmode=require` 在副本上失败 |
| `add-node` 前提条件 | 主节点上的远程备份 (`elestio backups auto-enable <vmID>`)，主副本模式 |
| `add-node` 后 | VM 部署，然后 Elestio 花几分钟将其设置为副本。集群此时读取 `running`；在执行其他节点或防火墙更改前等待 (CLI 拒绝它们) |
| 删除主节点 | 不可能：首先提升一个副本，或删除集群 |
| 限制访问 | `clusters firewall-restrict`，永远不在单个节点上使用 `elestio firewall`：它会与其它节点不一致 |

部署集群前，永远先运行 `--dry-run` 并告知用户 VM 数量和成本。

### CI/CD 管道

```bash
# CATALOG SOFTWARE -> 总是使用 deploy-template (读取 elestio.yml 模板)
elestio cicd templates [query]     # 目录中可部署为管道的软件
elestio cicd deploy-template <software> --target <vmID>
elestio cicd deploy-template <software> --target <vmID> --dry-run
elestio cicd deploy-template <software> --target <vmID> --owner <git-user>  # git 路由 (目前 404)
# 选项：--name, --branch, --private, --non-org, --auth-id, --git-type,
#       --repo-name, --build-cmd, --run-cmd, --install-cmd, --build-dir

elestio cicd targets               # 列出 CI/CD 目标
elestio cicd pipelines <vmID>      # 列出管道
elestio cicd pipeline-info <vmID> <pipelineID>

# 用户自己的仓库 -> 创建 --auto。永远不要用这个来部署目录软件。
elestio cicd create --auto --target <vmID> --name my-app --repo owner/repo --mode github
elestio cicd create --auto --target <vmID> --name my-app --repo owner/repo --mode github --auth-id <id>
# 模式：github, github-fullstack, gitlab, gitlab-fullstack, docker
# 可选：--branch, --build-cmd, --run-cmd, --install-cmd, --build-dir, --framework, --node-version

# 手动管道创建 (从 JSON 模板)
elestio cicd template docker       # Docker Compose (自定义，无 Git)
elestio cicd template github       # GitHub 静态 SPA (Vite/React)
elestio cicd template github-fullstack  # GitHub 全栈 (Node.js)
elestio cicd template gitlab       # GitLab 静态 SPA (Vite/React)
elestio cicd template gitlab-fullstack  # GitLab 全栈 (Node.js)
elestio cicd create <config.json>

# 管道操作
elestio cicd pipeline-restart <vmID> <pipelineID>
elestio cicd pipeline-stop <vmID> <pipelineID>
elestio cicd pipeline-logs <vmID> <pipelineID>
elestio cicd pipeline-history <vmID> <pipelineID>
elestio cicd pipeline-delete <vmID> <pipelineID> --force

# 管道域名
elestio cicd domains <vmID> <pipelineID>
elestio cicd domain-add <vmID> --pipeline <id> --domain myapp.example.com
elestio cicd domain-remove <vmID> --pipeline <id> --domain myapp.example.com

# Docker 注册表
elestio cicd registries
elestio cicd registry-add --name X --username U --password P --url URL
```

**自动创建管道流程:** CLI 查找连接的 Git 账户 (或使用 `--auth-id`)，解析仓库和 CI/CD 目标，通过 API 创建管道。Elestio 然后克隆、构建并启动它；使用 `elestio cicd pipelines <vmID>` 和 `elestio cicd pipeline-history <vmID> <pipelineID>` 跟踪构建。

### 计费

```bash
elestio billing                    # 总成本
elestio billing project <id>       # 按服务分解
```

---

## 强制：交互式部署流程

**关键:** 部署任何服务时，你必须使用 `AskUserQuestion` 逐个询问每个必需参数。永远不要使用默认值而未经明确用户确认部署。

### 必需参数 (按此顺序询问):

**1. 提供商** -- 使用 `AskUserQuestion` 询问：
- Netcup (推荐) -- 最佳性价比，基于欧洲，可靠
- Hetzner -- 最佳功能：完整卷、快照和电源管理支持
- AWS -- 亚马逊云服务，全球覆盖
- Azure -- 微软云

**2. 区域** -- 使用 `AskUserQuestion`，基于选择的提供商：
- Netcup: nbg (欧洲 - 德国，纽伦堡) | mns (北美 - 美国，马纳萨斯)
- Hetzner: fsn1 (福尔肯斯坦，DE), nbg1 (纽伦堡，DE), hel1 (赫尔辛基，FI), ash (阿什本，US)
- AWS: us-east-1, eu-west-1, ap-southeast-1, 等
- Azure: germanywestcentral, eastus, westeurope, 等

如果需要，使用 `elestio sizes --provider <provider>` 获取确切可用区域。

**3. 服务计划 (大小)** -- 使用 `AskUserQuestion`，提供可用大小和价格：
- SMALL-1C-1G -- 1 核心，1GB RAM (~$11/月，Linode)
- MEDIUM-2C-4G -- 2 核心，4GB RAM (~$16/月，Netcup DE)
- LARGE-4C-8G -- 4 核心，8GB RAM (~$30/月，Netcup DE)
- XL-8C-16G -- 8 核心，16GB RAM (~$55/月，Netcup DE)

使用 `elestio sizes --provider <provider>` 获取选择的提供商的确切大小/价格。

**4. 服务名称** -- 不要使用 `AskUserQuestion`。直接以纯文本询问用户提供名称，建议基于服务类型 (例如，"prod-postgres", "staging-redis")。等待用户文本输入。

**5. 管理员邮箱** -- 使用 `AskUserQuestion` 询问，建议使用雇主的邮箱作为默认值。让用户确认或更改。

### 示例流程：

```
用户: "部署 PostgreSQL"
代理: [AskUserQuestion] 选择云提供商? (推荐 Netcup, Hetzner, AWS, Azure)
用户: "Netcup"
代理: [AskUserQuestion] 选择区域? (nbg 欧洲-德国, mns 北美-美国)
用户: "nbg"
代理: [AskUserQuestion] 选择服务计划? (SMALL ~$11/月, MEDIUM ~$16/月, LARGE ~$30/月, XL ~$55/月)
用户: "MEDIUM"
代理: "您想给这个服务起什么名字? 建议: prod-postgresql"
用户: "demo-postgres"
代理: [AskUserQuestion] 管理员邮箱? (建议: user@company.com)
用户: 确认
代理: 使用所有确认的参数部署
```

---

## 黄金法则

1. **始终先进行身份验证** -- 每个会话都以有效的 JWT 开始
2. **vmID != serverID** -- 大多数端点使用 `vmID`，备份/笔记使用 `serverID`（两者均来自 `elestio services`）
3. **检查部署状态** -- 部署后，等待 `deploymentStatus = "Deployed"` 再访问
4. **未经确认切勿删除** -- 始终需要 `--force` 标志
5. **尽可能使用目录** -- 第三阶段（目录）比第四阶段（CI/CD）更简单
5b. **在管道中目录化软件 -> `cicd deploy-template` (MCP: `deploy_catalog_pipeline`)，绝不使用 `cicd create` (MCP: `create_pipeline_docker` / `create_pipeline_auto`)** -- 这些无法知道软件的端口、环境变量或安装脚本，因此它们生成的管道既不部署也不运行任何内容
6. **验证组合** -- 提供商 + 数据中心 + 服务器类型必须匹配 `elestio sizes`
7. **账户必须已批准** -- 新账户需要信用卡 + 批准才能部署
8. **始终遵循上述交互式部署流程** -- 切勿跳过参数问题
9. **设置默认项目** -- 使用 `elestio config --set-default-project <id>` 以避免每次传递 `--project`
10. **服务属于项目** -- 使用 `elestio service <vmID>` 时，确保 vmID 属于当前默认项目或指定 `--project`
11. **对任何增加 VM 数量的操作进行干运行** -- 部署集群前始终运行 `--dry-run` 并告知用户 VM 数量和月度成本；集群按 VM 收费
12. **`--nodes` 是总数** -- `--nodes 3` 是 1 个主节点 + 2 个副本，计费 3 个 VM，不是 4 个

---

## 默认值

| 设置 | 默认值 | 覆盖 |
|------|--------|------|
| 提供商 | netcup | `--provider hetzner` |
| 数据中心 | nbg (德国) | `--region fsn1` |
| 服务器大小 | MEDIUM-2C-4G | `--size LARGE-4C-8G` |
| 支持 | level1 | `--support level2` |

**为什么选择 netcup？** 性价比最佳。EU 区域。可靠。

---

## 提供商限制

并非所有云提供商都支持所有功能。使用 `--provider` 切换。

| 功能 | netcup | Hetzner | AWS | GCP | Azure | Scaleway |
|------|--------|---------|-----|-----|-------|----------|
| 目录部署 | 是 | 是 | 是 | 是 | 是 | 是 |
| CI/CD 部署 | 是 | 是 | 是 | 是 | 是 | 是 |
| **卷** | 否 | 是 | 是 | 是 | 是 | 是 |
| **快照** | 有限制 | 是 | 是 | 是 | 是 | 是 |
| 电源操作 | 有限制 | 是 | 是 | 是 | 是 | 是 |
| 防火墙 | 是 | 是 | 是 | 是 | 是 | 是 |
| SSL/域名 | 是 | 是 | 是 | 是 | 是 | 是 |
| **大小降级** | 是 | 否 | 是 | 否 | 是 | 是 |

**大小降级支持：** 仅 **Netcup、AWS、Azure 和 Scaleway** 支持降级实例大小。其他提供商（Hetzner、GCP 等）仅支持升级。在不支持的提供商上尝试降级可能会阻止服务并需要 Elestio 支持干预。CLI 将自动阻止在不支持的提供商上的降级尝试。

**建议：** 如果需要卷、快照或完整电源管理，请使用 **Hetzner**。当基本功能足够时，使用 **netcup** 获取最佳性价比。如果需要降级实例大小的灵活性，请使用 **netcup、AWS、Azure 或 Scaleway**。

---

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|-------|----------|
| "未配置" | 缺少凭证 | `elestio login --email X --token Y` |
| "身份验证失败" | 错误的凭证或过期的令牌 | 在仪表板中重新创建 API 令牌 |
| "账户未批准" | 未获批准的新账户 | 等待批准或联系 support@elest.io |
| "模板未找到" | 错误的名称/ID | 使用 `elestio templates search <name>` |
| "无效的服务器类型" | 提供商/区域/大小组合不存在 | 检查 `elestio sizes --provider X` |
| "服务未找到" | 错误的 vmID 或项目 | 检查 `elestio services --project X` |
| "部署超时" | 耗时过长 | 检查仪表板，如果超过 10 分钟请联系支持 |
| "项目未找到" | 错误的 projectId | 检查 `elestio projects` |

---

## 可组合性：部署后该做什么

### 部署服务后

1. **获取凭证：** `elestio credentials <vmID>`
2. **验证运行状态：** 打开 URL，确认服务正常工作
3. **启用备份：** `elestio backups auto-enable <vmID>`
4. **添加自定义域名：** `elestio ssl add <vmID> myapp.example.com`
5. **配置防火墙：** `elestio firewall enable <vmID> --rules [...]`
6. **启用自动更新：** `elestio updates system-enable <vmID> --security-only`

### 创建 CI/CD 目标后

**目录化软件（Vaultwarden、Redis、Metabase 等）——使用这个：**
1. **检查是否可用：** `elestio cicd templates <software>`
2. **预览：** `elestio cicd deploy-template <software> --target <vmID> --no-git --dry-run`
3. **部署：** `elestio cicd deploy-template <software> --target <vmID>`
4. **告知用户打印的 URL、登录名和密码**
5. **添加域名：** `elestio cicd domain-add <vmID> --pipeline <pipelineID> --domain myapp.example.com`

**用户的私有仓库：**
1. **自动创建管道：** `elestio cicd create --auto --target <vmID> --name my-app --repo owner/repo --mode github --auth-id <id>`
2. 跟踪构建：`elestio cicd pipelines <vmID>`（构建列必须显示 "success"）

**手动 docker-compose：**
1. **添加 SSH 密钥：** `elestio ssh-keys add <vmID> --name "name" --key "key"`
2. **创建管道：** `elestio cicd create pipeline.json`
3. **SSH 并配置：** `ssh root@<ipv4>`
4. **添加域名：** `elestio cicd domain-add <vmID> --pipeline <pipelineID> --domain myapp.example.com`

### 出错后

1. **重新身份验证：** `elestio auth test`
2. **检查状态：** `elestio service <vmID>`
3. **查看日志：** `elestio logs <vmID>`（服务）或 `elestio cicd pipeline-logs <vmID> <pipelineID>`（管道）
3b. **查看变更：** `elestio audits <vmID>`
4. **重启堆栈：** `elestio restart-stack <vmID>`

---

## 故障排除

### "身份验证失败" 重复出现

```bash
# 1. 验证当前配置
elestio config

# 2. 使用仪表板中的新令牌重新配置
elestio login --email "..." --token "..."

# 3. 测试
elestio auth test
```

### 服务卡在 "部署中"

1. 正常部署耗时 2-5 分钟
2. 如果超过 10 分钟，检查 Elestio 仪表板是否有错误
3. 如果仍然卡住，请联系 support@elest.io

### "服务未找到" 但存在

- 确保使用 `vmID` 而不是 `serverID`
- 检查正确项目：`elestio services --project X`
- vmID 格式：`12345678`（数字）

### 管道部署但软件未运行（最常见）

几乎总是：管道使用 `cicd create` 而不是 `cicd deploy-template` 创建，因此没有端口、没有环境变量和没有安装脚本。

```bash
# 确认：正确构建的管道有环境变量
elestio cicd pipeline-info <vmID> <pipelineID>

# 修复：删除它并通过 deploy-template 重新部署
elestio cicd pipeline-delete <vmID> <pipelineID> --force
elestio cicd deploy-template <software> --target <vmID>
```

使用 MCP 连接器的原因是相同的：管道使用 `create_pipeline_docker` 或 `create_pipeline_auto` 创建。使用 `deploy_catalog_pipeline` 重新部署它。

### 软件启动后立即退出

模板声明了 `preInstall`/`postInstall` 脚本，而 compose 路径没有仓库来运行它们。

```bash
# 查看模板需要的钩子
elestio cicd deploy-template <software> --target <vmID> --dry-run
```

如果出现 "Lifecycle:" 行，该软件需要这些脚本。git 路径运行它们但目前不可用（API 返回 404 for `createRepoByTemplate`）。向用户报告此问题而不是重试。

### "在 ... 未找到 elestio.yml"

该软件没有管道模板，无法作为管道部署。改为作为托管服务部署：`elestio deploy <template>`。

### 管道不工作（一般）

1. SSH 到 CI/CD 目标：`ssh root@<ipv4>`
2. 检查日志：`cd /opt/app/<pipeline-name> && docker-compose logs`
3. 验证 docker-compose.yml 语法
4. 检查端口映射：`172.17.0.1:XXXX`（内部网络）

### 集群错误

| 消息 | 原因 |
|---|---|
| `does not support clustering` | 不是可集群的模板之一 -- 运行 `elestio clusters templates` |
| `needs at least 3 nodes` | 共识软件（ClickHouse、Vault、OpenSearch、RabbitMQ、rke2、Nats） |
| `does not support multi-master` | `--cluster-mode multi-master` 仅适用于 MySQL |
| `cannot exceed 15 nodes` | 平台硬限制 |
| `remote backups are off` (add-node) | 新节点从主节点的远程备份中获取：`elestio backups auto-enable <primary vmID>` |
| `is busy (add-node)` | 节点仍在配置中；等待几分钟 |
| `is the primary` (remove-node) | 首先提升一个副本，或删除整个集群 |

### "variables.trim is not a function" (500 Pipeline.CreateFailed)

管道负载中的 `variables` 字段必须是 **字符串**，不能是数组或省略。后端对它运行 `variables.trim()`，因此任何其他类型都会在读取构建/运行/框架设置之前抛出错误（即使是最小参数也会失败）。

- 正确：`"variables": ""`（无环境变量）或 `"variables": "KEY=value\nKEY2=value2"`。
- 错误：`"variables": []` 或完全省略该字段。

CLI 从 1.1.0 开始强制执行此规则，MCP 连接器正确发送。如果使用 CLI 遇到此问题，请升级：`npm install -g elestio@latest`。

---

## ID 参考（关键）

| 术语 | 在哪里查找 | 在哪里使用 |
|------|------------|--------|
| `vmID` | `elestio services` -> `.vmID` | 大多数端点（操作、防火墙、ssl 等） |
| `serverID` | `elestio services` -> `.id` | 备份端点、笔记 |
| `projectID` | `elestio projects` -> `.projectID` | 几乎所有内容 |
| `templateID` | `elestio templates` -> `.id` | `elestio deploy` |
| `pipelineID` | `elestio cicd pipelines` -> `.pipelineID` | CI/CD 操作 |
| `volumeID` | `elestio volumes` -> `.id` | 卷操作 |

**常见错误：** 在预期 `vmID` 处使用 `serverID`（反之亦然）。它们是相同服务的不同数字。

---

## VM 架构

每个 Elestio 服务都在专用 VM 上运行：

```
/opt/elestio/nginx/          <- 反向代理（自动配置，不要修改）
/opt/app/                    <- 你的应用程序
    +-- docker-compose.yml   <- 用于目录化服务
    +-- <pipeline_name>/     <- 用于 CI/CD 管道
```

- 反向代理自动处理 HTTPS 终止
- SSL 证书通过 Let's Encrypt 自动生成
- 端口 `172.17.0.1:XXXX` 是内部 Docker 网络接口

---

## 支持层级

| 计划 | 价格 | 响应时间 |
|------|-------|---------------|
| level1 | 包含 | 48h (邮件) |
| level2 | +$50/svc/mo | 24h (优先) |
| level3 | +$200/svc/mo | 4h (专属工程师) |

---

## 链接

- **仪表板：** https://dash.elest.io
- **API 文档：** https://api-doc.elest.io
- **支持：** support@elest.io
- **模板：** 400+ 个开源模板在 https://elest.io/open-source
- **CLI：** `npm install -g elestio`
