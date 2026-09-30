---
name: clickstack-otel-collector
description: 当用户希望将 OpenTelemetry collector 部署到 ClickHouse Cloud 上的 Managed ClickStack 服务中时，可以使用此方法。用户可以通过部署新的本地 collector（使用 Docker run 或 Docker Compose）或配置他们自己的现有 collector 来实现，然后将丰富的合成遥测数据发送出去，并验证这些数据是否在 ClickStack 中可见。
---

# 为托管 ClickStack 设置 OpenTelemetry 收集器

这项技能将 OpenTelemetry 收集器连接到在 ClickHouse Cloud 上运行的托管 ClickStack 服务，通过它发送丰富的合成遥测数据，并确认数据实际上在 ClickStack 中可见。它使用 [`clickhousectl`](https://clickhouse.com/docs/interfaces/cli) 执行所有云和 SQL 操作。

**范围。** 此技能支持两条路径，在步骤 0 中选择：

1. **本地部署新的收集器**。你可以通过两种方式完成：单独的 `docker` 命令，或 `docker compose` 文件（推荐，命令更少，一个文件用于启动/停止）。提前让用户了解这两种方式，并在步骤 0 中让他们选择；不要假设纯 `docker`。无论哪种方式，都运行 ClickStack 分发的收集器，预先配置为托管 ClickStack。
2. **通过添加 ClickHouse 导出器配置来配置你自己的现有收集器**。我们为你提供确切的配置，你可以直接复制；然后重新加载你的收集器。如果你已经在网关角色中运行收集器，请使用此方法。

完整的 Kubernetes 部署（Helm、K8s Secrets 中的密钥）在此范围内之外；我们在路径 2 中生成的配置可以应用于任何运行的收集器。

最终状态是：

- 在目标服务上创建一个专用的 `hyperdx_ingest` SQL 用户，具有收集器所需的精确权限（它在第一次写入时创建 `otel.*` 模式）。
- 收集器将日志、跟踪和指标转发到服务的 `otel` 数据库中，无论是新的本地 ClickStack 收集器还是你现有的收集器。
- 跨多个服务、严重性、跟踪状态和指标类型发送丰富的合成遥测数据，以便 ClickStack 的搜索、服务映射和仪表板有真实内容可以显示。
- 确认服务**已唤醒**，并且用户在云控制台中完成了 ClickStack 引导，以便他们实际上可以看到他们的数据。

密钥（OTLP 认证令牌和 SQL 密码）在本地生成，**一次**写入到 `0600` 环境文件中，并通过 `--env-file` 传递给 Docker。它们永远不会粘贴到聊天中，永远不会与 `docker run -e` 一起传递，创建后也永远不会回显。

按顺序执行以下步骤。每个步骤都依赖于前一个步骤建立的状态。

---

## 步骤 0：选择你的路径

在执行任何操作之前，向用户提出两个简短的问题，因为它们决定了后续步骤的运行。

**问题 1：你已经在网关角色中运行 OpenTelemetry 收集器吗？**

- **没有，为我设置一个。** -> **新收集器**路径。继续到问题 2。
- **有。** -> **现有收集器**路径。跳过问题 2（它不适用），并在步骤 6 中配置他们的收集器，而不是部署新的收集器。

**问题 2（仅限新收集器路径）：使用单独的 Docker 命令，还是 Docker Compose 文件运行收集器？**

- **Docker Compose（推荐）。** 命令更少，一个文件用于启动和停止，最容易重新运行。如果 `docker compose` 可用，这是最佳选择。
- **单独的 Docker 命令。** 如果 Compose 未安装或你更喜欢明确的命令，请使用此方式。

将答案记录为 `COLLECTOR_PATH`（`new` 或 `existing`），对于新路径，记录 `DEPLOY_MODE`（`compose` 或 `run`）。在步骤 6 和步骤 7 中引用它们。

---

## 步骤 1：提前批量权限

编码代理在看到每个 shell 命令时第一次提示批准。为了避免每隔几步就中断用户，请提前一次，在前面允许列出以下命令前缀（他们代理中的“始终为此项目/会话允许”选项）。没有破坏性操作，并且没有任何操作针对此项目或他们的 ClickHouse Cloud 服务之外的内容。

| 命令前缀       | 用于                     | 需要时                 |
| -------------- | ------------------------ | ---------------------- |
| `openssl rand …` | 生成 OTLP 令牌和 SQL 密码 | 总是                   |
| `clickhousectl cloud …` | 认证、解析服务、通过查询 API 运行 SQL | 总是                   |
| `jq …`         | 解析来自 `clickhousectl` 的 JSON | 总是                   |
| `docker …` / `docker compose …` | 运行/检查收集器和遥测生成器 | 新收集器路径，以及可选的遥测检查 |
| `curl …`       | 对 `localhost:13133` 进行本地健康检查（如果缺少则安装 `clickhousectl`） | 新收集器路径         |

用你自己的话告诉用户：*"如果你的代理支持，请在每个中第一次询问时选择“始终允许”。整个运行对你的机器是只读的，除了收集器容器；对 ClickHouse 的写入操作仅限于创建摄取用户和 `otel` 模式。*"

如果用户选择现有收集器路径并且不想运行可选的遥测检查，你可以从列表中删除 `docker` 和 `curl`。

**两个批准是语义上的，而不是基于前缀的，因此允许列表不会预先清除它们。** 警告用户要期待这些并明确批准它们：

- 步骤 3 中的 `clickhousectl` 安装使用 `curl … | sh`，许多代理沙盒将其标记为“下载和运行不受信任的代码”，无论任何 `curl` 允许列表规则如何。
- 步骤 5 中的 `CREATE USER` / `GRANT` 可能被标记为“修改共享生产基础设施”，再次独立于 `clickhousectl` 前缀规则。

以上都不是通过上面的表格解决的；它们是一次性的、故意的，并且可以安全地批准。

然后继续。

---

## 步骤 2：确认目标服务并创建密钥文件

用户的提示中包含一个服务标识符，无论是服务 ID（UUID）还是服务名称。将此值视为 `SERVICE_REF`。

创建一个工作目录和一个 **`0600` 环境文件**，其中将包含此运行的所有配置和密钥。键名与收集器镜像读取的完全匹配，因此这个文件可以直接传递给 `docker run --env-file`（或在 Compose 中引用）在步骤 6 中。在严格的 `umask` 下写入它，以便密钥永远不会短暂地对世界可读：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"
mkdir -p "$WORKDIR" && chmod 700 "$WORKDIR"
ENV_FILE="$WORKDIR/collector.env"

# 生成密钥而不打印它们；直接写入一个私有文件。
( umask 177
  {
    echo "SERVICE_REF=$SERVICE_REF"
    echo "OTLP_AUTH_TOKEN=$(openssl rand -hex 32)"
    echo "CLICKHOUSE_USER=hyperdx_ingest"
    echo "CLICKHOUSE_PASSWORD=$(openssl rand -hex 24)Aa1-"
    echo "HYPERDX_OTEL_EXPORTER_CLICKHOUSE_DATABASE=otel"
  } > "$ENV_FILE"
)
chmod 600 "$ENV_FILE"
ls -l "$ENV_FILE"
```

这两个值很重要，而且很容易出错：

- **键名是精确的。** 收集器读取 `CLICKHOUSE_USER`、`CLICKHOUSE_PASSWORD`、`CLICKHOUSE_ENDPOINT` 和 `HYPERDX_OTEL_EXPORTER_CLICKHOUSE_DATABASE`。将 SQL 密码存储在 `CLICKHOUSE_PASSWORD` 下（不要使用自定义名称）；如果它丢失，收集器将以**空**密码启动并因 `code: 516, Authentication failed` 而死亡。
- **密码字符集从三个方向同时受到限制。** ClickHouse Cloud 拒绝没有至少一个大写字母和至少一个特殊字符的密码，因此纯十六进制字符串在 `CREATE USER` 时失败。同时，收集器的迁移工具将密码嵌入连接 URL 中，因此 `@`、`:`、`/`、`?`、`#` 和 `%` 会损坏它（症状：`code: 516` 在启动时即使密码“正确”也会失败）。上面的配方是随机十六进制（小写字母加数字）加上后缀 `Aa1-`，它添加了所需的大写字母、数字和**URL 未保留**的特殊字符（`-`）。OTLP 令牌没有这样的规则（它只是一个凭证令牌），因此纯十六进制对它来说是安全的。

环境文件使用**不带引号的 `KEY=VALUE` 行**：Docker 的 `--env-file` 不做 shell 解析，因此你添加的任何引号都会成为值的一部分。

在**现有收集器路径**上，`OTLP_AUTH_TOKEN` 不会被你的收集器使用（你的接收器上的认证是你自己的设置）；它仅生成，以便如果你后来切换到本地收集器，同一个文件也能工作。`CLICKHOUSE_*` 值仍然使用：它们进入导出器配置，你将在步骤 6 中将其添加到你的收集器中。

**每个后续步骤都在一个新鲜 shell 中运行，因此 `WORKDIR`、`ENV_FILE` 和任何导出的凭证都不会持久化，并且 `WORKDIR`/`ENV_FILE` 不会存储在环境文件中，因此 sourcing 它们无法恢复它们。** 从每个后续步骤的 shell 开始，使用这个**标准前缀**，它从确定性默认值重新派生路径，加载保存的凭证（步骤 3），并加载配置：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"; ENV_FILE="$WORKDIR/collector.env"
[ -f "$WORKDIR/creds.env" ] && . "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
```

如果你选择了一个非默认的 `WORKDIR`，请在每个步骤的顶部显式设置它（`${WORKDIR:-…}` 默认仅覆盖标准位置）。后续步骤将其称为“标准前缀”。

**与用户确认** `SERVICE_REF` 是否正确。告诉他们工作目录，并且 `collector.env`（模式 `0600`）现在包含 OTLP 令牌和 SQL 密码。**不要**打印任何密钥。如果他们想查看值，请指向该文件 (`grep OTLP_AUTH_TOKEN "$ENV_FILE"`).

如果用户提供了自己的令牌或密码，请将这些值写入文件，而不是生成的值，但请保持相同的 `0600` 纪律，并确保任何自定义密码仍然满足上面的字符集规则。

---

## 步骤 3：认证 `clickhousectl`（默认情况下使用单独的终端）

检查 `clickhousectl` 是否在 `PATH` 上。运行此存在检查**单独地**，不要将其链接到安装程序：`|| curl … | sh` 形式的无害检查会被沙盒作为“下载和运行不受信任的代码”整体拒绝。

```bash
which clickhousectl
```

只有当它打印为空时，才安装它（用户可能需要明确批准此操作，见步骤 1）：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

检查认证：

```bash
clickhousectl cloud auth status
```

此技能需要**API 密钥认证**：OAuth 是只读的，无法创建用户或运行写入查询。如果 `API key` 行不是 `Active`，用户必须进行认证。

**不要**要求用户将他们的 API 密钥和密钥粘贴到聊天中。任何粘贴到对话中的内容都存在于转录中，并且必须旋转。相反，请他们在一个**单独的终端**中进行认证，然后告诉您何时完成：

> 我需要一个 ClickHouse Cloud **管理员** API 密钥来创建摄取用户并验证数据。
> 请不要在这里粘贴它。相反：
>
> 1. 在 [云控制台](https://console.clickhouse.cloud) 中，打开 **组织 → API 密钥 → 新 API 密钥**，并给它 **管理员** 角色。（开发者范围的密钥无法配置服务查询 API 端点，该端点 `cloud service query` 使用。)
> 2. 在一个 **单独的终端** 中，运行：
>
>    ```bash
>    clickhousectl cloud auth login --api-key <key-id> --api-secret <key-secret>
>    ```
>
> 3. 告诉我何时完成，我将重新检查认证状态。

轮询，直到 API 密钥行报告 `Active`，然后使用一个**无参考**的真实特权调用来确认，而不是单独信任状态表。在这里使用一个**无参考**的调用：`SERVICE_REF` 可能是一个名称，而 `cloud service get` 只接受 UUID，因此使用 `get` 会在名称上失败，原因与认证无关。`cloud service list` 不需要参考，并证明 API 密钥有效：

```bash
clickhousectl cloud auth status
clickhousectl cloud service list --json | jq -r '.[].name'
```

如果列表返回你的服务，你已认证；继续。`SERVICE_REF` 的实际名称或 UUID 解析发生在步骤 4 中。

**预期需要环境变量凭证（常见，不是边缘情况）。** 许多 `clickhousectl` 构建**保存凭证文件**，但一个新生成的 shell（例如你工具调用的那个）不会读取它，因此 `auth status` 显示 `Active`，而下一个 `clickhousectl` 调用报告 `No credentials found`。与其将此视为罕见的回退，不如编写一个小的**可源文件**，然后在每个后续 shell 中加载它。这使每个后续 shell 保持在单个 `.` 行而不是两个 `jq` 重新派生，并将密钥保持在聊天之外：

```bash
# 在收集器.env 旁边写入一个私有的、可源文件。
( umask 177
  { echo "export CLICKHOUSE_CLOUD_API_KEY=$(jq -r .api_key    "$HOME/.clickhouse/credentials.json")"
    echo "export CLICKHOUSE_CLOUD_API_SECRET=$(jq -r .api_secret "$HOME/.clickhouse/credentials.json")"
  } > "$WORKDIR/creds.env"
)
chmod 600 "$WORKDIR/creds.env"
```

**从现在开始，打开每个调用 `clickhousectl` 的 shell，并加载这两个**，因为环境变量不会跨 shell 持久化：

```bash
. "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
```

重新运行上面的 `service list` 检查，现在应该成功。不要继续，直到一个真实调用工作。（如果 `clickhousectl auth status` 已经显示 `API key … Active` 并且调用成功，而无需 `creds.env`，你可以跳过此步骤；但大多数代理 shell 需要它。）

---

## 步骤 4：解析服务并捕获 HTTPS 端点

运行标准前缀（步骤 2），以便此 shell 中的路径、凭证和配置都加载完毕，然后解析服务。如果 `SERVICE_REF` 是 UUID，直接使用它；否则通过名称查找：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"; ENV_FILE="$WORKDIR/collector.env"
[ -f "$WORKDIR/creds.env" ] && . "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
```

```bash
# UUID 形式
clickhousectl cloud service get "$SERVICE_REF" --json > "$WORKDIR/svc.json"

# 名称形式（注意双引号：服务名称可以包含空格或撇号，例如 "Alex's test")
clickhousectl cloud service list --json \
  | jq --arg n "$SERVICE_REF" '.[] | select(.name==$n)' > "$WORKDIR/svc.json"
```

提取你需要的信息，将端口强制转换为整数。端口作为浮点数序列化（`8443.0`）；如果 `:8443.0` 泄露到端点，收集器的 ClickHouse 导出器无法拨号它：

```bash
SERVICE_ID=$(jq -r '.id' "$WORKDIR/svc.json")
SERVICE_NAME=$(jq -r '.name' "$WORKDIR/svc.json")
STATE=$(jq -r '.state' "$WORKDIR/svc.json")
CLICKHOUSE_ENDPOINT=$(jq -r '.endpoints[] | select(.protocol=="https")
  | "https://\(.host):\(.port | tonumber | floor)"' "$WORKDIR/svc.json")

# 将解析的值持久化回环境文件，供后续步骤和 docker --env-file 使用。
# 仅当键不存在时才追加，以便第二次运行不会重复行。
grep -q '^SERVICE_ID=' "$ENV_FILE" || echo "SERVICE_ID=$SERVICE_ID" >> "$ENV_FILE"
grep -q '^CLICKHOUSE_ENDPOINT=' "$ENV_FILE" || echo "CLICKHOUSE_ENDPOINT=$CLICKHOUSE_ENDPOINT" >> "$ENV_FILE"
printf 'service=%q state=%s endpoint=%s\n' "$SERVICE_NAME" "$STATE" "$CLICKHOUSE_ENDPOINT"
```

`STATE` 必须是 `running`。如果它是 `stopped` 或 `starting`，请要求用户启动服务（或等待），然后不要继续。ClickHouse Cloud 服务**空闲挂起**，因此即使服务“正在运行”，它也可能处于休眠状态；下一个查询既检查可达性，也唤醒它：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query "SELECT version()"
```

成功的响应确认服务已唤醒，并且为每个服务配置了查询 API 密钥。在第一次调用时，`clickhousectl` 会打印 `Provisioning Query API endpoint + key for service '<name>'...`，这是预期的。

> **此处应出现审批提示。** 下面的 `CREATE USER` / `GRANT` 语句是针对云服务的 DDL，即使 `clickhousectl` 被允许，一些代理沙盒也会将其标记为“修改共享生产基础设施”。这是预期的；操作范围仅限于单个专用的摄取用户和 `otel` 模式，当提示时用户应明确批准它们。

**永远不要将明文密码放在 SQL 中。在本地哈希并使用 `sha256_hash`。** 两个问题排除了 `IDENTIFIED WITH sha256_password BY '$CLICKHOUSE_PASSWORD'`：密钥会出现在进程参数列表（在 `ps` 中可见）和 shell 历史记录中，更重要的是，**查询 API 在其错误 JSON 中逐字回显失败语句**，因此任何错误（瞬态故障、字符集错误）都会将密码泄露到代理可能显示的输出中。通过标准输入传递它没有帮助，错误回显仍然包含它。相反，在本地计算密码的 SHA-256 哈希（`sha256_hash` 存储的内容与 `sha256_password` 完全相同，因此收集器仍然使用来自环境文件的明文登录）并将**哈希值**放入语句中。哈希值是不可逆的，因此即使回显错误也无法泄露密码：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"; ENV_FILE="$WORKDIR/collector.env"
[ -f "$WORKDIR/creds.env" ] && . "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a

# 密码的 SHA-256 哈希。openssl 已经是依赖项；这是可移植的（macOS + Linux）。
# 只有这个哈希值会到达 SQL、输出或 `ps`；明文保留在环境文件中。
PW_HASH=$(printf %s "$CLICKHOUSE_PASSWORD" | openssl dgst -sha256 | awk '{print $NF}')

# 逐条发送语句：查询 API 通过 HTTP 运行并拒绝多语句输入（“不允许多语句”），因此单个 ; 分隔的批处理会失败。
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "CREATE USER IF NOT EXISTS hyperdx_ingest IDENTIFIED WITH sha256_hash BY '$PW_HASH'"
# 安全重新运行：如果用户已存在，强制将密码设置为本次运行值。
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "ALTER USER hyperdx_ingest IDENTIFIED WITH sha256_hash BY '$PW_HASH'"
```

授予收集器创建和写入 `otel.*` 模式的最低权限。在当前镜像中，模式迁移及其版本表也位于 `otel` 中，因此 `otel.*` 足够（此语句不包含密钥）：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "GRANT SELECT, INSERT, CREATE DATABASE, CREATE TABLE, CREATE VIEW ON otel.* TO hyperdx_ingest"
```

> **旧镜像构建：** 一些早期的收集器版本将其 goose 迁移运行在 `default` 数据库中的版本表中，因此启动会在 `ACCESS_DENIED` 循环直到 `default.*` 也被授予权限。如果在收集器日志（步骤 6）中看到引用 `default` 的 `ACCESS_DENIED`，请添加此内容并重启容器：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "GRANT SELECT, INSERT, CREATE TABLE ON default.* TO hyperdx_ingest"
```

验证：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query "SHOW GRANTS FOR hyperdx_ingest"
```

您应该看到 `GRANT SELECT, INSERT, CREATE DATABASE, CREATE TABLE, CREATE VIEW ON otel.* TO hyperdx_ingest`。

---

## 步骤 6：设置收集器

遵循与步骤 0 中选择的路径和模式匹配的子部分。所有三个最终都会达到相同的状态：一个接受 OTLP 并写入服务上 `otel` 数据库的收集器。本步骤中的所有代码块都假设您已运行**标准前导程序**（步骤 2），因此 `$WORKDIR`、`$ENV_FILE`、`$SERVICE_ID` 和密钥都在 shell 中设置。

确保 Docker 正在运行（仅新收集器路径）：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"; ENV_FILE="$WORKDIR/collector.env"
[ -f "$WORKDIR/creds.env" ] && . "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
docker info > /dev/null
```

### 步骤 6a：使用 Docker Compose 的新收集器 (`DEPLOY_MODE=compose`)

在工作目录中编写一个 Compose 文件。它读取相同的 `collector.env` 获取密钥，发布 OTLP 和健康端口，并固定一个命名网络，以便步骤 7 中的遥测生成器可以通过容器名称访问收集器：

```bash
cat > "$WORKDIR/docker-compose.yaml" <<'EOF'
name: clickstack
services:
  otel-collector:
    image: clickhouse/clickstack-otel-collector:latest
    container_name: clickstack-otel-collector
    env_file: ./collector.env
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "13133:13133" # health
    restart: unless-stopped
    networks: [clickstack-net]
networks:
  clickstack-net:
    name: clickstack-net
EOF

# Compose 拒绝采用它未创建的 clickstack-net（来自 docker run 路径的遗留、先前的失败 Compose 运行或 DEPLOY_MODE 切换），失败时显示“网络 clickstack-net 被找到但标签不正确”。如果存在没有容器连接的孤儿，请删除它，以便 Compose 可以使用自己的标签重新创建它。
if docker network inspect clickstack-net >/dev/null 2>&1 \
   && [ -z "$(docker network inspect clickstack-net -f '{{range .Containers}}{{.Name}} {{end}}')" ]; then
  docker network rm clickstack-net
fi

( cd "$WORKDIR" && docker compose up -d )
```

Compose 会为您创建 `clickstack-net` 网络（上面的保护措施会首先清除先前的运行中的孤儿）。跳到 **步骤 6d** 以确认健康状态。

### 步骤 6b：使用单独的 Docker 命令的新收集器 (`DEPLOY_MODE=run`)

创建一个用户定义的网络，以便步骤 7 中的遥测生成器可以通过容器名称访问收集器：

```bash
docker network create clickstack-net 2>/dev/null || true
```

启动收集器，通过 `--env-file` 传递**所有密钥**（永远不要 `-e`，这会将密钥放在命令行、shell 历史记录和 `ps` 中）。首先使用 `docker rm -f` 使步骤安全可重运行：

```bash
docker rm -f clickstack-otel-collector 2>/dev/null || true
docker run -d \
  --name clickstack-otel-collector \
  --network clickstack-net \
  --env-file "$ENV_FILE" \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 13133:13133 \
  clickhouse/clickstack-otel-collector:latest
```

镜像从 `env` 文件中读取 `OTLP_AUTH_TOKEN`、`CLICKHOUSE_ENDPOINT`、`CLICKHOUSE_USER`、`CLICKHOUSE_PASSWORD` 和 `HYPERDX_OTEL_EXPORTER_CLICKHOUSE_DATABASE`。它在 OTLP 接收器上启用基于令牌的认证，使用空方案，因此调用者将原始令牌作为 `authorization` 标头发送（没有 `Bearer ` 前缀）。继续到 **步骤 6d**。

### 步骤 6c：配置现有的收集器 (`COLLECTOR_PATH=existing`)

将 ClickHouse 导出器添加到您的现有收集器配置中。以下配置与 ClickStack 发行版的行為匹配，包括会话重放（`rrweb`）路由路径，并将数据写入 ClickStack UI 期望的 `otel` 数据库。

**将端点和密码作为环境变量引用（`${env:…}`），不要将其硬编码到配置文件中。** 贡献收集器在加载时扩展 `${env:VAR}`，因此将明文密码从配置文件中移除既更安全也符合本技能的其余部分。使用 `--env-file` 启动收集器，使其可用，这是本地收集器使用的相同 `--env-file` 的最简单方式：

```bash
# 当在 Docker 中运行贡献收集器时，传递 collector.env 以使 ${env:CLICKHOUSE_*} 解析：
#   docker run -d --env-file "$ENV_FILE" -p 4317:4317 -p 4318:4318 \
#     -v "$WORKDIR/your-config.yaml:/etc/otelcol-contrib/config.yaml:ro" \
#     otel/opentelemetry-collector-contrib:latest
# 对于非 Docker 收集器，在它启动之前将其 CLICKHOUSE_ENDPOINT 和 CLICKHOUSE_PASSWORD 导出到其环境（例如 systemd unit 中的 EnvironmentFile=）。
```

将以下内容添加到您的收集器配置并重新加载它：

```yaml
receivers:
  otlp/hyperdx:
    protocols:
      grpc:
        include_metadata: true
        endpoint: "0.0.0.0:4317"
      http:
        cors:
          allowed_origins: ["*"]
          allowed_headers: ["*"]
        include_metadata: true
        endpoint: "0.0.0.0:4318"

processors:
  batch:
  memory_limiter:
    limit_mib: 1500
    spike_limit_mib: 512
    check_interval: 5s

connectors:
  routing/logs:
    default_pipelines: [logs/out-default]
    error_mode: ignore
    table:
      - context: log
        statement: route() where IsMatch(attributes["rr-web.event"], ".*")
        pipelines: [logs/out-rrweb]

exporters:
  clickhouse:
    database: otel
    endpoint: ${env:CLICKHOUSE_ENDPOINT}
    username: hyperdx_ingest
    password: ${env:CLICKHOUSE_PASSWORD}
    ttl: 720h
    timeout: 5s
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s
  clickhouse/rrweb:
    database: otel
    endpoint: ${env:CLICKHOUSE_ENDPOINT}
    username: hyperdx_ingest
    password: ${env:CLICKHOUSE_PASSWORD}
    ttl: 720h
    logs_table_name: hyperdx_sessions
    timeout: 5s
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s

service:
  pipelines:
    traces:
      receivers: [otlp/hyperdx]
      processors: [memory_limiter, batch]
      exporters: [clickhouse]
    metrics:
      receivers: [otlp/hyperdx]
      processors: [memory_limiter, batch]
      exporters: [clickhouse]
    logs/in:
      receivers: [otlp/hyperdx]
      exporters: [routing/logs]
    logs/out-default:
      receivers: [routing/logs]
      processors: [memory_limiter, batch]
      exporters: [clickhouse]
    logs/out-rrweb:
      receivers: [routing/logs]
      processors: [memory_limiter, batch]
      exporters: [clickhouse/rrweb]
```

此路径的注意事项：

- 如果您使用自己的发行版，请确保它包含 ClickHouse 导出器。上游的 [贡献镜像](https://github.com/open-telemetry/opentelemetry-collector-contrib) 已经这样做了。
- OTLP 接收器上的认证是您的现有设置。步骤 2 中生成的 `OTLP_AUTH_TOKEN` 除非您将其连接到自己的认证（例如 `bearertokenauth`）否则不在此处使用。
- 重新加载后，跳过以下健康检查（它仅针对本地容器特定），直接进入 **步骤 7** 以发送验证突发（将生成器指向您自己的收集器的 OTLP 端点）。

### 步骤 6d：确认本地收集器是否健康（新收集器路径）

```bash
docker ps --filter name=clickstack-otel-collector --format '{{.Status}}'
curl -fsS http://localhost:13133/ && echo
docker logs --tail 40 clickstack-otel-collector 2>&1 | tail -40
```

健康的启动显示种子迁移运行完成（以 `[seed] OK ...` 行结束，以 `goose: up to current file version: N` 结尾），然后是 `Everything is ready. Begin running and processing data.`（或等效内容），`docker ps` 报告 `Up ... (healthy)`，并且健康检查返回 HTTP 200。在较旧的服务器版本上出现类似 `ClickHouse 25.12 < 26.2, falling back to compatibility logs and traces schemas` 的种子行是**预期且无害的**，不是错误；不要在它上面暂停。如果相反容器退出，原因几乎总是种子步骤：

- `code: 516, Authentication failed: password is incorrect` -> `CLICKHOUSE_PASSWORD` 在环境文件中为空或错误。最常见的错误是存储密码在不同的键名下（它**必须**是 `CLICKHOUSE_PASSWORD`），或者使用包含 `@ : / ? # %` 的密码，这会损坏迁移工具的连接 URL。
- `[HTTP 403]` / `data size should be 0 < <huge number>` 在“server hello”时 -> 相同的根本原因：对 HTTPS 端点的空/错误密码。
- TLS / dial 错误 -> `CLICKHOUSE_ENDPOINT` 格式错误（它必须是 `https://<host>:8443`，端口上没有 `.0`）。
- `ACCESS_DENIED` 引用 `default` -> 仅在旧镜像构建上；应用步骤 5 注释中的 `default.*` 授权并重启。

---

## 步骤 7：发送丰富的合成遥测并验证摄取

使用 `telemetrygen`（OpenTelemetry 收集器贡献生成器）的**Docker 镜像**，因此不会在主机上安装任何内容。与其发送一条平坦的突发，不如通过多个**服务**、**严重性**、**跨度状态**和**指标类型**发送遥测，以便 ClickStack 的搜索、服务地图和仪表板具有现实、多样化的数据，而不是单一统一的流。

加载环境文件以使令牌可用，然后引用 `$OTLP_AUTH_TOKEN`。下面的 `tg` 帮助程序**将所有生成器输出重定向到日志文件**，并且只打印退出代码，因为 `telemetrygen` 将其完整配置（包括 `authorization` 标头（您的 OTLP 令牌））回显到 stdout。永远不要在聊天中显示原始输出。`telemetrygen` 的标题语法要求值是一个引号字符串：`key="value"`。

两个服务上的日志，具有不同的严重性和正文，包括一个错误行：

```bash
tg logs --service checkout --severity-text Info  --severity-number 9 \
  --body "checkout completed" \
  --otlp-attributes 'deployment.environment="production"' \
  --telemetry-attributes 'http.method="POST"'
tg logs --service payment  --severity-text Error --severity-number 17 \
  --body "payment gateway timeout" \
  --otlp-attributes 'deployment.environment="production"' \
  --telemetry-attributes 'http.status_code="500"'
```

带有子跨度、一个健康服务和一个出错服务的跟踪（这是填充服务地图和错误视图的内容）：

```bash
tg traces --service checkout --service-name checkout --child-spans 4 --span-duration 120ms --status-code Ok \
  --otlp-attributes 'deployment.environment="production"' \
  --telemetry-attributes 'http.route="/cart"'
tg traces --service payment  --service-name payment --child-spans 3 --span-duration 400ms --status-code Error \
  --otlp-attributes 'deployment.environment="production"' \
  --telemetry-attributes 'http.route="/charge"'
```

跨三种常见类型收集指标，以便仪表板具有仪表、计数器和分布：

```bash
tg metrics --service checkout --metric-type Sum
tg metrics --service checkout --metric-type Gauge
tg metrics --service payment  --metric-type Histogram
```

(`--metric-type` 接受 `Gauge`、`Sum`、`Histogram` 或 `ExponentialHistogram`。添加 `--otlp-http`
并使用 `--otlp-endpoint clickstack-otel-collector:4318` 来使用 HTTP 路径而不是 gRPC。)

等待约 15 秒，让收集器刷新其批次，然后确认表是否存在：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "SELECT name FROM system.tables WHERE database='otel' ORDER BY name"
```

然后确认行是否已到达。按 `parts.rows` 计数，它是信号无关的，避免了为每个信号硬编码列名：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query \
  "SELECT table, sum(rows) AS rows
   FROM system.parts
   WHERE database='otel' AND active
     AND table IN ('otel_logs','otel_traces',
                   'otel_metrics_sum','otel_metrics_gauge',
                   'otel_metrics_histogram','otel_metrics_exponential_histogram',
                   'otel_metrics_summary')
   GROUP BY table ORDER BY table"
```

您应该看到 `otel_logs`、`otel_traces`、`otel_metrics_sum`、
`otel_metrics_gauge` 和 `otel_metrics_histogram` 的 `rows` 非零。如果某个信号缺失：

1. 尾部收集器日志 (`docker logs --tail 50 clickstack-otel-collector`) 查找导出错误。
2. 确认 `authorization` 头匹配 `$OTLP_AUTH_TOKEN`：`grep -c Unauthenticated
   "$TG_LOG"`（非零计数表示不匹配，完整消息是 `code = Unauthenticated desc =
   provided authorization does not match expected scheme or token`）。使用 `grep` 而不是打印日志，因为其中包含令牌。
3. 重新检查 `CLICKHOUSE_ENDPOINT` 具有正确的 `https://` 方案和 `:8443` 端口。
4. 某些指标类型刷新缓慢。在宣布失败之前，再运行一次计数，等待另外 30 秒。

在所有预期信号都显示非零行之前，不要继续。

---

## 第 8 步：确认服务已启动，然后在 ClickStack 中完成引导

ClickHouse 中的行与用户在 ClickStack 中看到的遥测数据**不同**。ClickStack UI 需要一次性引导步骤来自动检测数据源，如果 ClickHouse 服务在此期间处于空闲挂起状态，该步骤会失败。

**首先，确认服务已启动。** 不要跳过这一步；这是引导显示没有源的最常见原因。运行一个实际查询并要求其成功：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query "SELECT 1"
```

如果返回 `1`，服务已启动；立即继续下面的控制台步骤，同时保持服务热。如果它出错或超时，服务处于空闲状态，此调用正在唤醒它：等待几秒钟并重新运行，直到它返回 `1`。只有在成功后才能继续。

**然后明确引导用户。** 不要只说“完成”；详细说明每个点击，因为源只有在完成此流程后才会出现：

1. 前往 [ClickHouse Cloud 控制台](https://console.clickhouse.cloud) 并打开目标服务。
2. 在 **左侧菜单中选择 ClickStack**。
3. 点击进入 **入门指南** 并遵循引导流程。
4. **忽略任何提示要求您设置或配置收集器 / 开始摄取的提示。** 您已经在上述步骤中完成了这些。直接跳过这些屏幕（点击通过 / “下一步”）到源检测。重新运行控制台的收集器设置是不必要的，并且只会造成混乱。
5. 数据源**自动检测**：`otel` 数据库的日志、跟踪和指标会自动捕获，您的数据会出现在搜索和仪表板视图中。

直接链接是 `https://console.clickhouse.cloud/services/<SERVICE_ID>/clickstack`（替换 `$SERVICE_ID`）。

**如果源检测显示为空**，服务几乎肯定在数据发送和控制台步骤之间空闲挂起。重新运行上面的 `SELECT 1` 唤醒查询，然后让用户重新运行检测，而不是让他们调试一个不透明的失败。

---

## 第 9 步：总结并交接（不回显密钥）

以大致此格式打印摘要。注意令牌是**引用，而不是打印**，SQL 密码完全未显示，收集器会一直运行，直到用户停止它。调整“如何停止”行以匹配他们选择的部署模式。

```
✅ ClickStack 已设置并正在为服务 <SERVICE_NAME> (<SERVICE_ID>) 摄取遥测数据。
   在控制台（第 8 步）中完成引导，以自动检测源并查看您的数据。

收集器
  ▸ 新本地收集器通过 <Docker Compose | docker run>  （或：配置了您现有的收集器）
  ▸ 发送 OTLP gRPC 到：localhost:4317
  ▸ 发送 OTLP HTTP 到：localhost:4318
  ▸ 健康检查：      http://localhost:13133/   （仅限本地收集器）
  ▸ 必要头：       authorization: <OTLP 令牌>
       （获取方式：  grep OTLP_AUTH_TOKEN <WORKDIR>/collector.env）

ClickHouse 目标
  ▸ 端点： <CLICKHOUSE_ENDPOINT>
  ▸ SQL 用户：hyperdx_ingest   （密码在 <WORKDIR>/collector.env，模式 0600）
  ▸ 数据库：otel

在 ClickHouse Cloud 控制台中完成：
  ▸ 打开服务，在左侧菜单中选择 ClickStack，然后入门指南，
    并完成引导以自动检测源。
  ▸ https://console.clickhouse.cloud/services/<SERVICE_ID>/clickstack
```

然后用您自己的话告诉用户：

1. 所有密钥都在 `<WORKDIR>/collector.env`（模式 `0600`）中。没有敏感信息被粘贴到这个聊天中或传递到 `docker run` 命令行。
2. 收集器会一直运行，直到他们停止它。对于 Compose：
   `cd <WORKDIR> && docker compose down` 停止它，`docker compose up -d` 重新启动它。对于单个 Docker：`docker stop clickstack-otel-collector` 和 `docker start
   clickstack-otel-collector`。
3. 此主机上的任何应用程序、SDK 或代理现在都可以使用来自环境文件的 `authorization` 头将 OTLP 发送到 `localhost:4317`（gRPC）或 `localhost:4318`（HTTP）。
4. ClickHouse Cloud 服务空闲挂起。如果 ClickStack 后来显示没有最近的数据，服务可能只是处于空闲状态；发送新的遥测数据或运行任何查询都会唤醒它。

---

## 清理（只有在用户明确要求时）

```bash
# Docker Compose 部署：
( cd "$WORKDIR" && docker compose down )

# 单独 Docker 部署：
docker rm -f clickstack-otel-collector
docker network rm clickstack-net 2>/dev/null || true

# 任何部署，删除摄取用户：
clickhousectl cloud service query --id "$SERVICE_ID" --query "DROP USER IF EXISTS hyperdx_ingest"

# 可选地，在不再需要时删除本地文件：
# rm -f "$WORKDIR/collector.env" "$WORKDIR/svc.json" "$WORKDIR/docker-compose.yaml"
```

**不要**删除 `otel` 数据库：它包含用户可能希望保留的遥测数据。
