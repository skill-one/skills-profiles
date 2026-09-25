# 为 Managed ClickStack 设置 OpenTelemetry collector

这项技能将 OpenTelemetry collector 集成到在 ClickHouse Cloud 上运行的 Managed ClickStack 服务中，通过它发送丰富的合成遥测数据，并确认数据实际上在 ClickStack 中可见。它使用 [`clickhousectl`](https://clickhouse.com/docs/interfaces/cli) 执行所有云和 SQL 操作。

**范围。** 此技能支持两种路径，在步骤 0 中选择：

1. **在本地部署一个新的 collector**。你可以通过两种方式来做：单独的 `docker` 命令，或者 `docker compose` 文件（推荐，命令更少，一个文件用于启动/停止）。提前让用户了解这两种方式，并在步骤 0 中让他们选择；不要假设普通的 `docker`。无论哪种方式，都运行 Managed ClickStack 的 collector 分发版本，预先配置为 Managed ClickStack。
2. **通过添加 ClickHouse 出口配置来配置你自己的现有 collector**。我们提供确切的配置，你可以直接复制；你重新加载你的 collector。如果你已经在网关角色中运行 collector，请使用此方法。

完整的 Kubernetes 部署（Helm，K8s Secrets 中的密钥）不在此范围内；我们在步骤 2 中生成的配置可以应用于任何运行的 collector。

最终状态是：

- 在目标服务上有一个专用的 `hyperdx_ingest` SQL 用户，具有 collector 所需的确切权限（它在第一次写入时创建 `otel.*` 模板）。
- collector 将日志、跟踪和指标转发到服务上的 `otel` 数据库，无论是新的本地 ClickStack collector 还是你的现有 collector。
- 跨多个服务、严重性、跨度状态和指标类型发送丰富的合成遥测数据，以便 ClickStack 的搜索、服务地图和仪表板有真实的数据可以显示。
- 服务确认 **已唤醒**，并且用户在 Cloud 控制台中完成了 ClickStack 的入职流程，以便他们实际上 *可以看到*他们的数据。

密钥（OTLP 认证令牌和 SQL 密码）在本地生成，写入 **一次** 到一个 `0600` 环境文件，并通过 `--env-file` 传递给 Docker。它们永远不会粘贴到聊天中，永远不会与 `docker run -e` 一起传递，也永远不会在创建后回显。

按顺序执行这些步骤。每一步都依赖于前一个步骤建立的状态。

---

## 步骤 0：选择你的路径

在执行任何操作之前，先向用户提出两个简短的问题，因为它们决定了后续步骤的运行。

**问题 1：你已经在网关角色中运行 OpenTelemetry collector 吗？**

- **没有，为我设置一个。** -> **新 collector** 路径。继续到问题 2。
- **有。** -> **现有 collector** 路径。跳过问题 2（它不适用），并在步骤 6 中你将配置他们的 collector 而不是部署一个新的。

**问题 2（仅限新 collector 路径）：使用单独的 Docker 命令运行 collector，还是使用 Docker Compose 文件？**

- **Docker Compose（推荐）。** 命令更少，一个文件用于启动和停止，最容易重新运行。如果 `docker compose` 可用，这是最佳选择。
- **单独的 Docker 命令。** 如果 Compose 没有安装或者你更喜欢明确的命令，请使用此方式。

将答案记录为 `COLLECTOR_PATH`（`新` 或 `现有`），对于新路径，记录 `DEPLOY_MODE`（`compose` 或 `run`）。在步骤 6 和步骤 7 中参考它们。

---

## 步骤 1：提前批量权限

编码代理在看到每个 shell 命令时第一次提示批准。为了避免每隔几步就打断用户，请提前一次，在前面允许列出以下命令前缀（他们代理中的“始终允许此项目/会话”选项）。没有破坏性操作，并且没有任何操作针对此项目或他们的 ClickHouse Cloud 服务之外的内容。

| 命令前缀 | 用于 | 需要时 |
| --- | --- | --- |
| `openssl rand …` | 生成 OTLP 令牌和 SQL 密码 | 总是 |
| `clickhousectl cloud …` | 认证、解析服务、通过查询 API 运行 SQL | 总是 |
| `jq …` | 解析来自 `clickhousectl` 的 JSON | 总是 |
| `docker …` / `docker compose …` | 运行/检查 collector 和遥测生成器 | 新 collector 路径，以及可选的遥测检查 |
| `curl …` | 对 `localhost:13133` 进行本地健康检查（如果缺少则安装 `clickhousectl`） | 新 collector 路径 |

用你自己的话告诉用户：*"如果你的代理支持，第一次请求时选择“始终允许”每个。整个运行对你的机器是只读的，除了 collector 容器；对 ClickHouse 的写入操作仅限于创建摄取用户和 `otel` 模板。**

如果用户选择现有 collector 路径并且不想运行可选的遥测检查，你可以从列表中删除 `docker` 和 `curl`。

**两个批准是语义上的，而不是基于前缀的，所以允许列表不会预先清除它们。** 警告用户要期待这些，并在它们出现时明确批准它们：

- 步骤 3 中的 `clickhousectl` 安装使用 `curl … | sh`，许多代理沙盒将其标记为“下载和运行不受信任的代码”，无论任何 `curl` 允许列表规则如何。
- 步骤 5 中的 `CREATE USER` / `GRANT` 可能被标记为“修改共享生产基础设施”，再次独立于 `clickhousectl` 前缀规则。

以上都没有解决；它们是一次性、故意的，并且可以安全地批准。

然后继续。

---

## 步骤 2：创建工作目录和密钥文件

用户的提示包含一个服务标识符，无论是服务 ID（UUID）还是服务名称。将此值视为 `SERVICE_REF`。

创建一个工作目录和一个 **`0600` 环境文件**，其中将包含此运行的所有配置和密钥。密钥名称与 collector 图像读取的内容完全匹配，因此此文件可以直接传递到 `docker run --env-file`（或由 Compose 引用）在步骤 6 中。在严格的 `umask` 下写入它，以便密钥永远不会短暂地对世界可读：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"
mkdir -p "$WORKDIR" && chmod 700 "$WORKDIR"
ENV_FILE="$WORKDIR/collector.env"

# 生成密钥，不要打印；直接写入一个私有的文件。
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

有两个关于这些值需要注意的地方，而且很容易出错：

- **密钥名称是确切的。** Collector 读取 `CLICKHOUSE_USER`、`CLICKHOUSE_PASSWORD`、`CLICKHOUSE_ENDPOINT` 和 `HYPERDX_OTEL_EXPORTER_CLICKHOUSE_DATABASE`。将 SQL 密码存储在 `CLICKHOUSE_PASSWORD` 下（不是自定义名称）；如果它丢失，collector 会以 **空** 密码启动，并以 `code: 516, Authentication failed` 错误退出。
- **密码字符集从三个方向同时受到限制。** ClickHouse Cloud 拒绝没有至少一个大写字母和至少一个特殊字符的密码，因此纯十六进制字符串在 `CREATE USER` 失败。同时，collector 的迁移工具将密码嵌入连接 URL 中，因此 `@`、`:`、`/`、`?`、`#` 和 `%` 会损坏它（症状：`code: 516` 在启动时即使密码“正确”也会出现）。上面的配方是随机十六进制（小写字母 + 数字），加上后缀 `Aa1-`，它添加了所需的大写字母、数字和一个 **URL 保留** 特殊字符（`-`）。OTLP 令牌没有这样的规则（它只是一个持有令牌），因此纯十六进制是合适的。

环境文件使用 **裸 `KEY=VALUE` 行，没有引号**：Docker 的 `--env-file` 不执行 shell 解析，因此你添加的任何引号都会成为值的一部分。

在 **现有 collector 路径** 中，`OTLP_AUTH_TOKEN` 对你的 collector 不使用（你的接收器上的认证是你自己的设置）；它仅生成，以便如果你稍后切换到本地 collector，此文件仍然适用。`CLICKHOUSE_*` 值仍然使用：它们进入你添加到现有 collector 的出口配置中，步骤 6 中。

**每个后续步骤都在一个新的 shell 中运行，所以 `WORKDIR`、`ENV_FILE` 和任何导出的凭证都不会持久化，并且 `WORKDIR`/`ENV_FILE` 不会存储在环境文件中，所以 sourcing 它们无法恢复它们。** 在每个后续步骤的 shell 中以这个 **标准前缀** 开头，它从确定性默认值中重新导出路径，加载保存的凭证（步骤 3），并加载配置：

```bash
WORKDIR="${WORKDIR:-$HOME/clickstack-otel-collector}"; ENV_FILE="$WORKDIR/collector.env"
[ -f "$WORKDIR/creds.env" ] && . "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
```

如果选择了非默认的 `WORKDIR`，请在每一步的顶部显式设置它（`${WORKDIR:-…}` 默认仅覆盖标准位置）。后续步骤将此称为“标准前缀”。

**与用户确认** `SERVICE_REF` 是正确的。告诉他们工作目录，并且 `collector.env`（模式 `0600`）现在包含 OTLP 令牌和 SQL 密码。不要打印任何密钥。如果他们想查看值，请指向文件 (`grep OTLP_AUTH_TOKEN "$ENV_FILE"`).

如果用户提供了自己的令牌或密码，请将它们写入文件而不是生成的值，但保持相同的 `0600` 纪律，并确保任何自定义密码仍然满足上面的字符集规则。

---

## 步骤 3：认证 `clickhousectl`（默认情况下使用单独的终端）

检查 `clickhousectl` 是否在 `PATH` 中。运行此存在检查 **单独地**，不要将其链接到安装程序：`|| curl … | sh` 形式的无害检查被拖入一个复合命令中，沙盒拒绝将其作为不受信任代码下载。

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

此技能需要 **API 密钥认证**：OAuth 是只读的，无法创建用户或运行写入查询。如果 `API key` 行不是 `Active`，用户必须进行认证。

**不要要求用户将他们的 API 密钥和密钥粘贴到聊天中。** 任何粘贴到对话中的内容都存在于转录中，必须旋转。相反，请要求他们在 **单独的终端** 中进行认证，然后告诉您他们完成：

> 我需要一个 ClickHouse Cloud **管理员** API 密钥来创建摄取用户并验证数据。请不要将其粘贴到聊天中。相反：
>
> 1. 在 [Cloud console](https://console.clickhouse.cloud) 中，打开 **组织 → API 密钥 → 新 API 密钥**，并给它 **管理员** 角色。（开发者范围的密钥无法配置服务查询 API 端点，`cloud service query` 使用它。)
> 2. 在 **单独的终端** 中，运行：
>
>    ```bash
>    clickhousectl cloud auth login --api-key <key-id> --api-secret <key-secret>
>    ```
>
> 3. 告诉我当它完成时，我会重新检查认证状态。

轮询，直到 API 密钥行报告 `Active`，然后通过一个真正的特权调用而不是单独信任状态表来确认，而不是单独信任状态表：

```bash
clickhousectl cloud auth status
clickhousectl cloud service list --json | jq -r '.[].name'
```

使用一个 **无参考** 的调用：`SERVICE_REF` 可能是一个名称，而 `cloud service get` 只接受 UUID，因此使用 `get` 确认会因与认证无关的原因在名称上失败。`cloud service list` 不需要参考，并且可以证明 API 密钥有效：

```bash
clickhousectl cloud service query --id "$SERVICE_ID" --query "SELECT version()"
```

如果列表返回你的服务，你已认证；继续。实际名称或 UUID 的解析发生在步骤 4 中。

**预期需要环境变量凭证（常见，不是边缘情况）。** 许多 `clickhousectl` 构建（例如）保存凭证文件，但一个新的 spawned shell（例如你工具调用的那个）不会读取它，因此 `auth status` 显示 `Active`，而下一个 `clickhousectl` 调用报告 `No credentials found`。而不是将此视为罕见的回退，而是编写一个小型 **可 source** 凭证文件一次，然后在每个后续 shell 中加载它。这使每个后续 shell 保持为单个 `.` 行而不是两个 `jq` 重导，并将秘密保持在聊天之外：

```bash
# 在 collector.env 旁边写入一个私有的、可 source 的凭证文件。
( umask 177
  { echo "export CLICKHOUSE_CLOUD_API_KEY=$(jq -r .api_key "$HOME/.clickhouse/credentials.json")"
    echo "export CLICKHOUSE_CLOUD_API_SECRET=$(jq -r .api_secret "$HOME/.clickhouse/credentials.json")"
  } > "$WORKDIR/creds.env"
)
chmod 600 "$WORKDIR/creds.env"
```

**从现在开始，打开每个调用 `clickhousectl` 的 shell 时都需要这两个加载**，因为环境变量不会跨 shell 持久化：

```bash
. "$WORKDIR/creds.env"; set -a; . "$ENV_FILE"; set +a
```

重新运行上面的 `service list` 检查，加载凭证；它现在应该成功。不要继续，直到一个真实的调用工作。如果 `clickhousectl auth status` 已经显示 `API key … Active` 并且调用成功，你可以跳过此步骤；但大多数代理 shell 需要它。
