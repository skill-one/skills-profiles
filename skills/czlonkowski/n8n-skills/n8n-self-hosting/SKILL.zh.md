---
name: n8n-self-hosting
description: 在新的 Linux 虚拟机 (VM) 上通过 SSH 部署生产环境的自托管 n8n，使用 Docker Compose 作为 Caddy 反向代理，并自动启用 HTTPS。当用户希望在自己的服务器/VPS（Hetzner、DigitalOcean、AWS EC2、裸金属服务器）上自行托管、安装、配置或部署 n8n（单线程/常规模式或队列模式带工作进程）时使用，或者用于更新、备份、恢复或加固此类实例，或让 Python 代码节点在其上运行（任务执行者）。针对自托管 n8n（Docker），而非 n8n 云服务，也不涉及工作流构建。该技能会先询问单线程与队列模式，收集域名/SSH/时区输入，在服务器上生成新的密钥，并使用 TLS 启动堆栈。触发条件包括："部署 n8n"、"自托管 n8n"、"n8n Docker Compose"、"n8n 队列模式/工作进程"、"n8n 反向代理/SSL"、"备份/更新我的 n8n"、"Python 执行者不可用" / "n8nio/runners 侧边容器"，或 "我们不想给每个用户都提供 OAuth 客户端密钥" / "启用 Google 登录"（凭证覆盖）。
---

# 部署自托管 n8n

此技能将一个**全新的 Linux 虚拟机**（Ubuntu/Debian，root 或 sudo SSH）通过 Docker Compose 在 **Caddy**（自动 Let's Encrypt TLS）后面部署为 **运行中、HTTPS、生产环境 n8n**。
它适用于 **Docker 上的自托管 n8n** — 不是 n8n 云，也不用于构建工作流（那是本套餐的其他部分）。

有两种部署模式。架构不同，所以 **在执行任何操作之前选择模式**。

你通过 SSH 驱动端到端：预检查 → 安装 Docker → 部署项目 → 生成密钥 → 启动 → 验证 TLS → 交接。模板文件位于 `assets/` 中；模式特定和安全深度位于下面命名的参考文件中。

## 规则 0 — 选择模式（询问用户）

不要猜测。询问后确定一个：

| | **单机 / 普通模式** | **队列模式** |
|---|---|---|
| 进程 | 一个 n8n | 主进程 + N 个工作进程 |
| 额外服务 | 无（使用 SQLite） | Redis（队列）+ Postgres（数据库） |
| 执行工作流 | 在主进程中 | 在工作进程中，并行执行 |
| 适用于 | 1 个用户、轻量/中等负载、最简单的操作 | 高容量、重/长执行、水平扩展 |
| Compose 文件 | `assets/docker-compose.single.yml` | `assets/docker-compose.queue.yml` |
| 深入了解 | **`SINGLE_MODE.md`** | **`QUEUE_MODE.md`** |

不确定的话，从 **单机模式** 开始 — 它是最简单正确的选择，并且涵盖了大多数需求。后期切换到队列模式意味着需要切换 Compose 文件和从 SQLite 迁移到 Postgres，所以如果用户已经预期到真实容量，从 **队列模式** 开始。

## 规则 1 — 密钥卫生（不可协商）

这里的一个失误会泄露客户端凭证。要谨慎：

1. **在目标机器上新鲜生成每个密钥。** 不要将另一个 n8n 实例的加密密钥、数据库密码或 `.env` 复制到这个实例中。有关 `openssl` 命令，请参阅 `SECURITY.md`。
2. **密钥仅存在于 `.env`**（模式 600），由 Compose 引用为 `${VAR}`。永远不要将密钥内联到 `docker-compose.yml`、Caddyfile 或任何你提交的内容中。
3. **`N8N_ENCRYPTION_KEY` 是神圣的。** 它加密每个存储的凭证。如果它丢失或更改，所有保存的凭证都变得无法解密。明确设置它，并告诉用户备份**离机**。不要将其回显到长时间运行的日志或聊天历史中（除了交接所需的部分）。
4. **永远不要暴露内部服务。** 只有 Caddy（80/443）是公有的。n8n（5678）、Postgres（5432）、Redis（6379）保留在私有的 Docker 网络上 — 模板文件已经省略了它们的宿主机端口映射。不要添加它们。
5. **`.env` 和 Caddy 的 `caddy_data` 卷（颁发的证书 + ACME 账户密钥）不是共享的工件。** 如果你正在 git 仓库内工作，请在任何提交之前确认 `.env` 被 git 忽略。

## 部署前收集的输入

- **SSH 目标** — `user@host` 以及如何进行身份验证（密钥路径或用户确认代理已经具有访问权限）。root 或 sudo 用户。
- **域名** — n8n 将要驻留的完整主机名，例如 `n8n.example.com`（→ `SUBDOMAIN=n8n`，`DOMAIN_NAME=example.com`）。用户必须控制其 DNS。
- **TLS 邮箱** — 用于 Let's Encrypt (`SSL_EMAIL`)。
- **时区** — IANA 名称用于 Schedule/Cron 节点（例如 `Europe/Warsaw`），否则 `Etc/UTC`。
- **模式** — 单机或队列（规则 0）。队列 → 确认机器有足够的 RAM（大致下限约为 4 GB；每个工作进程需要 1–2 GB）。
- **可选模块** — 一些功能（目前 **Agents**）是后端模块，除非列在 `N8N_ENABLED_MODULES` 中，否则它们会保留在离线状态。只有当用户引入一个时才询问；如果他们这样做，请在启用它之前阅读 `QUEUE_MODE.md` 中的模块部分，因为在队列模式下它必须到达工作进程。
- **Python 代码节点 / 谁编辑工作流** — 询问 *"工作流将使用 Python 代码节点，还是除了你之外的其他人将编辑工作流？* 对任何一个问题的肯定回答都意味着任务运行器在 **外部模式**：一个 `n8nio/runners` 侧车（在队列模式下每个工作进程一个）。标准的 `n8nio/n8n` 镜像没有 Python 3，所以在默认内部模式下，每个 Python 代码节点都会因 `Python runner unavailable: Python 3 is missing from this system` 而失败。在步骤 3 之前阅读 `TASK_RUNNERS.md`。

## 部署流程

按顺序处理这些步骤。`SINGLE_MODE.md` / `QUEUE_MODE.md` 提供模式特定命令的详细信息；`SECURITY.md` 涵盖密钥生成和加固；`DAY2.md` 涵盖更新/备份/恢复。

### 1. 预检查（这里捕获到的最便宜的失败是捕获到的失败）
- 通过 SSH 登录；确认操作系统是 Debian/Ubuntu 类似（`. /etc/os-release`）。
- **DNS 必须已经指向该机器。** 比较机器的公网 IP (`curl -s ifconfig.me`) 与 `dig +short <fqdn>`（从机器和理想情况下你的笔记本电脑上运行）。如果它们不匹配，**停止** — Caddy 的 ACME 挑战将失败。让用户创建 A 记录，等待它传播，然后继续。
- 端口 **80 和 443** 必须可以从互联网访问。检查主机防火墙和任何云安全组/网络防火墙（Hetzner Cloud、AWS SG 等）— 这些位于机器外部，并且是常见的静默阻塞因素。

### 2. 安装 Docker（如果不存在）
- 检查 `docker --version` 和 `docker compose version`。如果缺失，安装 Docker Engine + Compose 插件（在 Ubuntu/Debian 上使用 Docker 的官方 `get.docker.com` 脚本即可）。在继续之前重新检查 `docker compose version`。

### 3. 部署项目
- 选择 `DATA_FOLDER` — 一个 **绝对路径**，例如 `/opt/n8n`。`.env` 中的 `DATA_FOLDER` 值 **必须等于这个确切目录**（Compose 挂载 `${DATA_FOLDER}/caddy_config/Caddyfile`，`init-data.sh` 通过相对 `./` 路径挂载），所以始终从这里运行 `docker compose`。创建它，并在其中创建 `caddy_config/` 和 `local_files/`。
- **将模板文件放到机器上。** 它们位于你机器上此技能的 `assets/` 中，而不是服务器上 — 将每个文件传输上去。要么使用 `scp` 将它们上传，要么（不需要本地副本）通过 SSH 写入每个文件的内容，例如：
  `ssh <target> 'cat > <DATA_FOLDER>/docker-compose.yml' < assets/docker-compose.single.yml`。
  使用确切名称放置它们：
  - 选择的 Compose → `<DATA_FOLDER>/docker-compose.yml`（将其重命名为确切名称）
  - `Caddyfile` → `<DATA_FOLDER>/caddy_config/Caddyfile`
  - **仅限队列模式：** `init-data.sh` → `<DATA_FOLDER>/init-data.sh`，然后 `chmod +x` 它
  - 匹配的 `.env.*.example` → `<DATA_FOLDER>/.env`
- **外部任务运行器（Python）：** 现在将运行器环境变量和 `task-runners` 侧车添加到 Compose 中（`TASK_RUNNERS.md` 包含每个模式的代码片段）。与其他密钥一起在步骤 4 中生成 `N8N_RUNNERS_AUTH_TOKEN`。

### 4. 填充 `.env` + 生成密钥
- 设置 `DATA_FOLDER`、`DOMAIN_NAME`、`SUBDOMAIN`、`SSL_EMAIL`、`GENERIC_TIMEZONE`。
- 使用 `openssl`（`SECURITY.md` 包含命令）在机器上生成每个密钥，并将其写入 `.env`，替换匹配的 `REPLACE_WITH_…` 占位符：`N8N_ENCRYPTION_KEY`；队列还生成 `POSTGRES_PASSWORD` + `POSTGRES_NON_ROOT_PASSWORD`。
- **在启动之前，确认没有未设置的：** `grep REPLACE_WITH_ .env` 必须返回空 — 一个剩余的占位符会变成字面密码，Postgres/n8n 无法连接。
- `chmod 600 .env`。记录加密密钥，以便用户可以安全地离机备份。

### 5. 防火墙
- `ufw`：允许 OpenSSH + 80 + 443，然后启用。**不要**打开 5678/5432/6379。

### 6. 启动
- `cd <DATA_FOLDER> && docker compose up -d`。
- 队列模式会启动 Redis + Postgres + 主进程 + 工作进程（工作进程通过 `replicas`）。要增加容量：`docker compose up -d --scale n8n-worker=N`。

### 7. 验证（没有这个不要宣布成功）
- `docker compose ps` — 每个服务 `Up`/健康（队列：postgres & redis `healthy` 首先出现）。
- **n8n 本身启动（内部）：** `docker compose exec n8n wget -qO- http://localhost:5678/healthz` → `{"status":"ok"}`。这区分了“n8n 正在运行”和“TLS 还未准备好”。
- **证书已颁发：** `docker compose logs caddy | grep -i 'certificate obtained'`。首次启动 ACME 可能需要一分钟左右；直到它完成，公共 `https://` 请求会因 TLS 失败 — 这意味着证书仍在等待中，**不是** n8n 已停止。
- **公网可访问性（带重试）：** `curl -fsS --retry 5 --retry-delay 10 https://<fqdn>/healthz` → `{"status":"ok"}`。（`/healthz` 仅证明进程可访问；`/healthz/readiness` 额外确认数据库已连接并迁移 — 在调试启动循环时使用。）
- **队列模式 — 主进程和工作进程必须一致。** 比较它们的环境：
  `diff <(docker compose exec -T n8n env | sort) <(docker compose exec -T --index 1 n8n-worker env | sort)`。
  只有公网 URL/proxy 变量应该不同。否则意味着行为设置到达了主进程但没有到达工作进程 — 而工作进程是执行工作流的，所以它在运行时在一个节点上失败，而不是在启动时。`QUEUE_MODE.md` 解释了该规则。
- **外部任务运行器：** `docker compose logs n8n | grep 'Registered runner'` 必须显示 `launcher-javascript` 和 `launcher-python`（队列：检查每个工作进程）。然后对 Python 代码节点进行冒烟测试（`TASK_RUNNERS.md` → 验证）。
- 打开 `https://<fqdn>` → **所有者设置**屏幕。**第一个完成注册表单的人将声称该实例** — 一个未拥有的暴露实例是一个竞赛，所以立即创建所有者账户，在分享 URL 之前。启用 2FA。（自动部署可以预先通过环境变量配置所有者 — 请参阅 `SECURITY.md` 中的所有者行。）

### 8. 交接
- 给用户：URL、项目位置、加密密钥以安全存储，以及来自 **`DAY2.md`** 的日常维护基础知识（更新 / 备份 / 恢复）。

## 不要做的事情

- **不要跳过 DNS/端口预检查。** 错误的 A 记录或关闭的云防火墙是 Caddy 无法获取证书并且 n8n 看起来“已损坏”的 #1 原因。
- **不要将 5678/5432/6379** 发布到主机。Caddy 通过私有网络到达 n8n。
- **不要重用另一个实例的加密密钥或 `.env`。** 每个机器的新鲜密钥。
- **不要在 SQLite 上运行队列模式。** 队列需要 Postgres（模板文件已经连接了它）。
- **不要将密钥放在 `docker-compose.yml` 或 Caddyfile 中。** 只有 `.env`。
- **不要将行为环境变量仅添加到主进程（队列模式）。** 模块、数据库、队列、二进制数据和加密设置属于共享的 `x-n8n-env` 锚点，以便工作进程也能获取它们；只有公网 URL/proxy 变量是主进程专用的。参见 `QUEUE_MODE.md`。
- **不要盲目使用 `:latest`。** 固定 `N8N_IMAGE_TAG`；故意更新（`DAY2.md`）。
- **不要在标准镜像的内部模式下承诺 Python 代码节点。** 它们需要 `n8nio/runners` 侧车，在确切版本的 n8n 上，并且需要在启动器配置中允许导入。默认情况下即使 `import json` 也会被拒绝。参见 `TASK_RUNNERS.md`。
- **不要在启用外部运行器后 `--scale` 队列工作进程。** 一个侧车服务于恰好一个工作进程。相反地添加工作进程 + 运行器对（`TASK_RUNNERS.md`）。

## 参考文件

- **`SINGLE_MODE.md`** — 单实例特定内容，SQLite 与 Postgres，何时升级到队列。
- **`QUEUE_MODE.md`** — 队列架构，工作进程/并发/扩展，共享加密密钥，主进程与工作进程的 **环境一致性规则**，可选后端模块（`N8N_ENABLED_MODULES`，例如 Agents），二进制数据（`database` 模式 — 队列模式下不支持文件系统；S3/Azure = 企业），webhook 处理器，多主许可。
- **`SECURITY.md`** — 生成密钥，加密密钥规则，完整的加固清单（关闭遥测、环境访问阻止、公共 API、防火墙、安全 Cookie）。
- **`CREDENTIAL_OVERWRITES.md`** — 管理OAuth：注册一个全局范围的 OAuth 应用实例，以便用户永远不会看到客户端 ID/密钥（自托管上的“使用 Google 登录”）。端点与环境的选项，**必须**的端点认证令牌，父类型继承，持久化和工作进程重新加载。
- **`TASK_RUNNERS.md`** — 外部模式下的任务运行器：为什么 Python 代码节点需要 `n8nio/runners` 侧车，单机模式和队列模式（每个工作进程一个侧车）的 Compose 代码片段，通过 `/etc/n8n-task-runners.json` 允许 Python/JS 模块，内置拒绝列表，验证，失败签名，以及一起升级 n8n 和运行器。
- **`DAY2.md`** — 安全地更改设置（环境变量），更新镜像，备份（加密密钥 + 卷 + Postgres），和恢复。
- **`assets/`** — 模板：`docker-compose.single.yml`，`docker-compose.queue.yml`，`Caddyfile`，`.env.single.example`，`.env.queue.example`，`init-data.sh`。

权威上游参考：官方托管文档位于
<https://docs.n8n.io/deploy/host-n8n>（2026 年中期重构自旧的 `/hosting/` 路径 — 优先使用这些 URL）。环境变量参考索引位于
<https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables>。
当此技能和实时文档不一致时，信任文档并告知用户。
