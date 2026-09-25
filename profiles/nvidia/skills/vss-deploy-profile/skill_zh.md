# VSS 部署

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/normalize_resolved_yml.py` | 在部署前移除 `resolved.yml` 中过滤出的服务可选的 `depends_on` 条目。 | `resolved.yml` 的路径 |
| `scripts/probe_remote_models.sh` | 探测兼容 OpenAI 的远程 LLM/VLM 端点并验证所选模型 ID。 | 基础 URL，可选的预期模型 ID |

## 配置路由

将用户的请求匹配到配置文件，然后加载该配置文件的参考以进行尺寸调整、服务、环境配方和调试。

| 用户说 | 配置文件 | 参考 |
|---|---|---|
| "部署 vss" / "部署基础" | `base` | [`references/base.md`](references/base.md) |
| "部署警报" / "警报验证" / "实时警报" / "部署用于事件报告" | `alerts` | [`references/alerts.md`](references/alerts.md) |
| "部署 lvs" / "视频摘要" | `lvs` | [`references/lvs-profile.md`](references/lvs-profile.md) |
| "部署搜索" / "视频搜索" | `search` | [`references/search.md`](references/search.md) |
| "部署仓库" / "仓库蓝图" / "vss 仓库" | `warehouse` | [`references/warehouse.md`](references/warehouse.md) |
| "调试仓库" / "仓库无法工作" / "仓库 FPS 低" / "仓库 BEV 不同步" | `warehouse` (调试) | [`references/warehouse-debug.md`](references/warehouse-debug.md) |

**边缘硬件路由** (DGX Spark, AGX/IGX Thor): 查看 [`references/edge.md`](references/edge.md)。DGX Spark 使用 Spark Nano 9B 独立本地 LLM 在端口 `30081`；AGX/IGX Thor 使用 Edge 4B 独立 vLLM 备用。

**每个配置文件的参考拥有其尺寸表。** 不要从这个文件中选择部署形状 — 打开配置文件参考，检查主机硬件的最低 GPU 数量，并与那里的 (模式 × 平台) 矩阵进行对比。

## 说明

部署流程始终是：将 `.env` 复制到 `generated.env`，应用覆盖，将 compose 干运行到 `resolved.yml`，审查，规范化，部署，然后等待就绪。

```bash
# 1. cp dev-profile-<profile>/.env dev-profile-<profile>/generated.env  (干净复制)
# 2. 应用环境覆盖到 generated.env  (源 .env 保持不变)
# 3. docker compose --env-file generated.env config > resolved.yml      (干运行)
# 4. 审查 resolved.yml
# 5. docker compose --env-file generated.env -f resolved.yml up -d
```

`.env` 是只读的提交默认值；`generated.env` 是每个部署的工作副本。步骤 1c 涵盖了这一点。

## 前置条件

1. **仓库路径** — 在询问用户之前自动检测 `video-search-and-summarization/`。使用检测到的路径作为 `$REPO` 用于所有后续命令。
2. **凭证门** — 查看 [`references/credentials.md`](references/credentials.md)：`NGC_CLI_API_KEY` 用于本地/本地共享 NIM 拉取，`NVIDIA_API_KEY` 用于远程 NIM 端点，`HF_TOKEN` 用于使用受保护的 HF 模型的边缘配方。
3. **系统前置条件 (GPU 驱动程序、Docker、NVIDIA 容器工具包、内核 sysctls，以及如果 `ufw` 处于活动状态 — 则需要 [Docker-bridge→主机防火墙允许](references/prerequisites.md#firewall) 以便 bridge NIM 可以从主机模式 VST 获取片段)** — 完整检查在 [`references/prerequisites.md`](references/prerequisites.md)。标准的硬件/驱动程序矩阵是 [VSS 前置条件页面](https://docs.nvidia.com/vss/3.2.0/prerequisites.html)。

自动检测片段（git-root，然后一个常见路径探测，以 `deploy/docker/compose.yml` + `dev-profile.sh` + `skills/vss-deploy-profile` 为门控）位于 [`references/prerequisites.md`](references/prerequisites.md#repo-detect)。导出解析的 `$REPO`；如果检测失败，请询问用户 checkout 路径。

### 预飞行检查

在每次部署之前运行。完整的系统检查清单和修复步骤位于 [`references/prerequisites.md`](references/prerequisites.md#preflight)。对于 DGX Spark / IGX Thor / AGX Thor，还运行缓存清理检查，位于 [`references/edge.md`](references/edge.md#cache-cleaner-every-edge-deploy)。

**首先检测 sudo 模式。** 当前的预飞行修复和边缘缓存清理安装程序调用 `sudo`。如果主机需要 sudo 密码，这些步骤将在 `sudo -n` 下静默无操作，并将部署置于半准备状态。

```bash
if sudo -n true 2>/dev/null; then
  echo "无密码 sudo — 预飞行将自动安装缺失的组件"
else
  echo "sudo 需要密码 — 预飞行将不会自动安装；手动命令给用户"
fi
```

当 sudo 需要密码时，技能**必须**自己不运行特权安装程序。向用户显示可复制粘贴的命令块，从 `references/prerequisites.md`，并使用 *"运行一次并确认"* 的手动交接，然后在用户回复后继续。

最低烟雾测试（必须成功）：

```bash
nvidia-smi --query-gpu=index,name --format=csv,noheader
docker info 2>/dev/null | grep -qi runtimes \
  && docker run --rm --gpus all ubuntu:22.04 nvidia-smi >/dev/null 2>&1 \
  && echo "nvidia 运行时 OK"
```

如果烟雾测试失败，请不要继续；打开 [`references/prerequisites.md`](references/prerequisites.md#preflight) 以获取修复树。

## 模型选择

- 如果用户要求远程，则 `$LLM_REMOTE_URL` / `$VLM_REMOTE_URL`
- `$NGC_CLI_API_KEY` (本地 NIMs) 或 `$NVIDIA_API_KEY` (远程)

**端点意图门。** 不要从零散的环境变量中推断远程位置（`LLM_ENDPOINT_URL`，`VLM_ENDPOINT_URL`，`LLM_BASE_URL`，`VLM_BASE_URL` 可能是遗留物）。仅在 (1) 用户要求/提供远程端点， (2) 本地尺寸无法适应所选模型且用户同意，或 (3) 边缘配方需要一个 VSS 视为 `remote` 的独立本地服务时使用远程 LLM/VLM。如果端点变量被设置但用户没有要求远程，请在步骤 1 中显示它并询问 — 永远不要因为变量恰好存在而静默部署远程。

如果此主机上没有任何组合满足配置文件的尺寸要求，**停止并报告阻止因素** — 不要静默选择另一个形状。

> **边缘共享模式是平台特定的。** 完整配方在 [`references/edge.md`](references/edge.md)。

## 部署流程

始终遵循此顺序。永远不要跳过干运行。

### 步骤 0 — 拆卸任何现有部署 + 清除数据卷

如果部署已存在，请先拆卸它，并清除过时的数据卷，然后再重新部署。

完整程序位于 [`references/teardown.md`](references/teardown.md)。

### 步骤 0a — 凭证门（在任何环境突变之前运行）

在将 `.env` 复制到 `generated.env` 之前，验证所选配置文件需要的每个凭证和远程端点。这里的 401 是 30 秒的失败；在 NIM 冷启动中的相同 401 是 10–20 分钟的失败。在 [`references/credentials.md`](references/credentials.md) 中运行发现和探测流程，包括对您计划写入 `generated.env` 的任何 LLM/VLM 端点的 `scripts/probe_remote_models.sh`。将结果与所选模式进行映射：缺少或无效的必要凭证/端点是阻止因素，可选凭证不是。

### 步骤 1 — 收集上下文

在构建环境覆盖之前，确认：

| 值 | 如何确定 |
|---|---|
| **配置文件** | 将用户意图与上文的路由表匹配。默认：`base` |
| **仓库路径** | 使用在前置条件中自动检测的 `$REPO` 值。如果自动检测失败，请在继续之前询问用户 checkout 路径。 |
| **硬件** | `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader` |
| **LLM/VLM 位置** | 明确决定本地 / 本地共享 / 远程。交叉参考可用 GPU 与所选配置文件的 **最低 GPU 数量** 表。如果端点环境变量存在但用户没有请求远程，请询问是否使用或忽略它们。 |
| **API 密钥** | `NGC_CLI_API_KEY` 用于本地 NIMs，`NVIDIA_API_KEY` 用于远程 |
| **`HOST_IP`** | 簇内拨号地址：`ip route get 1.1.1.1` src (像 `dev-profile.sh`；在局域网 + 云上正确)。如果该接口是 VPN/隧道，则回退到局域网 IP 并 **提示用户** — [网络寻址](references/prerequisites.md#addressing)。 |
| **`EXTERNAL_IP`** | 浏览器面向地址；默认为 `${HOST_IP}`。当浏览器路径不同时覆盖 — 云公共 IP，Brev 安全链接（步骤 1d），或隧道；如果不确定，**询问用户他们从哪里浏览**。 [网络寻址](references/prerequisites.md#addressing)。 |
| **`HAPROXY_PORT`** | 浏览器面向入口端口。默认 `7777`；确保它是空闲的。 |

在 `docker compose up` 之前，验证 `EXTERNAL_IP`，`HAPROXY_PORT`，`VSS_PUBLIC_HOST` 和 `VSS_PUBLIC_PORT` 是否填充了浏览器可访问的值。否则，堆栈可能看起来健康，而 UI/API/VST 链接 404 或通过 Cloudflare Access 循环。

### 步骤 1b — 准备数据目录

布局（资产路径、所有权、挂载点、配置文件特定子目录）在 [`references/data-directory.md`](references/data-directory.md) 中记录。在主机上首次部署配置文件或更改配置文件时，请先阅读该文件。

### 步骤 1c — 初始化 `generated.env`

技能的每个部署工作副本。始终从一个干净的源 `.env` 复制开始，永远不要修改源。

```bash
PROFILE=base
ENV_SRC=$REPO/deploy/docker/developer-profiles/dev-profile-$PROFILE/.env
ENV_GEN=$REPO/deploy/docker/developer-profiles/dev-profile-$PROFILE/generated.env

cp "$ENV_SRC" "$ENV_GEN"
```

所有后续写入（Brev `EXTERNAL_IP`，来自步骤 2 的 `env_overrides` 字典）都写入 `$ENV_GEN`。`$ENV_SRC` 从此起是只读的。

### 步骤 1d — Brev 仅：首先检测，然后设置 `EXTERNAL_IP` 为安全链接域

**在所有其他事情之前检测 Brev** — 一个 Brev 提供的实例在 `/etc/environment` 中设置 `BREV_ENV_ID`；其他任何东西都不会： 

```bash
grep -qE '^BREV_ENV_ID=' /etc/environment && echo "on Brev" || echo "not Brev"
```

- **不是 Brev** → 跳过此步骤的其余部分，**不要阅读 [`references/brev.md`](references/brev.md)**；保持正常的 `${HOST_IP}`-基于 `EXTERNAL_IP`。
- **是 Brev** → 将 [`references/brev.md` § 设置流程](references/brev.md#setup-flow) 中的 Brev 安全链接覆盖应用到 `generated.env`（不是 `.env`）。这些设置 `EXTERNAL_IP` / `VSS_PUBLIC_HOST` 为安全链接域 **并且** `VSS_PUBLIC_HTTP_PROTOCOL=https` / `VSS_PUBLIC_WS_PROTOCOL=wss` / `VSS_PUBLIC_PORT=443` — 仅设置 `EXTERNAL_IP` 会留下 `http://…:7777` UI/API/WS 链接，浏览器会将其作为混合内容阻止。

### 步骤 2 — 构建 `env_overrides`

根据用户请求和收集的上下文生成 `env_overrides` 字典：明确选择远程/本地 LLM/VLM，设置凭证，指向端点，设置平台特定标志。不要让现有的 shell 环境变量静默选择位置；将选定的 `LLM_MODE` / `VLM_MODE` 和匹配的端点/模型字段写入 `generated.env`。完整的映射（每个覆盖键，何时适用，默认值，配置文件特定差异）位于 [`references/env-overrides.md`](references/env-overrides.md)。每个配置文件参考都有该配置文件常见场景的工作示例。

### 步骤 3 — 应用覆盖 + 干运行

**工作环境文件：** `<repo>/deploy/docker/developer-profiles/dev-profile-<profile>/generated.env`（在步骤 1c 创建）。

> **提醒（见步骤 1c）：** 将所有覆盖（步骤 2 字典 + Brev `EXTERNAL_IP`）应用到 `generated.env`；`--env-file` 始终指向它，并且部署后验证器读取它以获取实际部署的值。

```bash
# (步骤 1c 已经运行：cp $ENV_SRC $ENV_GEN)

# 将步骤 2 中的 env_overrides 字典应用到 generated.env
# (读取行，更新匹配的键，追加新键，写入)
# 示例：
#   sed -i "s|^LLM_MODE=.*|LLM_MODE=remote|" "$ENV_GEN"
#   sed -i "s|^LLM_BASE_URL=.*|LLM_BASE_URL=http://localhost:30081|" "$ENV_GEN"

# 解析 compose
cd $REPO/deploy/docker
docker compose --env-file $ENV_GEN config > resolved.yml
```

解析的 YAML 保存到 `<repo>/deploy/docker/resolved.yml`。

### 步骤 3b — 验证 `resolved.yml` 没有未展开的 ${...} 标记

`resolved.yml` 中的未展开的 `${VAR}` 标记意味着 compose 没有看到这些环境值。诊断程序和常见原因位于 [`references/troubleshooting.md`](references/troubleshooting.md)。

### 步骤 3c — 验证对所选 NGC 资产的访问权限

在 `resolved.yml` 存在之后和 `docker compose up` 之前执行此操作。步骤 0a 中的 NGC 令牌探测只证明密钥可以验证；它不证明密钥所属的组织/团队可以访问所选的镜像或模型存储库。

从实际选择的部署构建资产列表：

- `resolved.yml`：Compose 将拉取的每个 `image:` 在 `nvcr.io/...` 下。
- `$ENV_GEN`：NGC 支持的模型/资源路径，例如
  `RTVI_VLM_MODEL_PATH=ngc:nim/nvidia/cosmos3-nano-reasoner:bf16-final`。跳过 `none`，`git:...`，本地路径和远程端点 URL。
- 配置文件预置步骤：配置文件参考中记录的任何 NGC 模型/资源下载，例如警报/搜索感知模型预置。

在继续之前，使用规范化后的 NGC 密钥探测每个选定的资产：

- 容器镜像：`docker manifest inspect <nvcr.io/...>` 在 `docker login nvcr.io` 之后 — 对于受保护的 `nvcr.io` 仓库，这里的 `401`/`403` 是一个明确的没有授权信号（读取清单需要与层拉取相同的组织/团队授权）；或者当资产干净映射到 NGC 镜像路径时，匹配的 `ngc registry image info ...`。
- NGC 模型/资源路径（例如运行时下载的宇宙检查点 RT-VLM）：运行匹配的 `ngc registry model info ...` 或 `ngc registry resource info ...` 对于配置文件将加载或下载的确切仓库/标签；这些使用 NGC 的范围授权。**不要用 `docker manifest inspect` 探测模型**（返回“没有这样的清单”，因为模型不是 OCI 镜像）或原始 `Authorization: Bearer <key>` REST 调用（返回 `403`，因为这不是 NGC 的授权流程）；两者都是预期的假阴性，不是授权失败。如果 `ngc` CLI 不可用，将容器镜像探测视为授权信号，因为 NGC 授权组织/团队跨图像和模型一起访问。
- 配置文件预置的 TAO/感知模型：在预置块下载文件之前，为每个仓库/标签运行相应的 `ngc registry model info ...` / `resource info ...`。

如果任何探测返回 `401`，`403`，`权限`，`不是所属仓库组织的成员`，缺少组织/仓库，或类似的访问错误，停止并提示用户提供来自有权访问这些资产的 NGC 密钥的组织/团队的 NGC 密钥。不要开始 Compose 并在 NIM 冷启动期间发现失败。

### 步骤 3d — 从 `resolved.yml` 中移除悬空的可选 `depends_on`

**必须在步骤 3 之后，步骤 5 之前运行。** 跳过此步骤将中止部署：

规范化 - 移除从 `resolved.yml` 中过滤出的服务的可选依赖

```bash
# 从仓库根目录
uv run skills/vss-deploy-profile/scripts/normalize_resolved_yml.py "$REPO/deploy/docker/resolved.yml"
```
如果 `uv` 不在主机上，使用 `curl -LsSf https://astral.sh/uv/install.sh | sh` 一次性安装它（不需要 root）。**重新验证** 在 `up -d` 之前：

```bash
docker compose -f "$REPO/deploy/docker/resolved.yml" config --quiet && echo "resolved.yml OK"
```

在正常化器运行后，如果验证仍然失败，捕获错误并检查 — 那是一个不同的错误（一个不是可选的依赖项，或另一个模式违规），而不是悬空依赖项的情况。

### 步骤 4 — 审查

向用户显示将要部署的摘要：

- 配置文件名称和硬件
- LLM/VLM 模型和模式（本地/远程/本地共享）
- 将启动的服务
- GPU 设备分配
- 关键端点（UI 端口，代理端口）

询问：**“看起来不错 — 现在部署？”** 并在步骤 5 之前等待确认。

**例外 — 自动模式。** 如果用户的请求已经要求您运行自动模式（例如，"自动部署 X"，"无需确认运行"，"非交互式"），请跳过确认提示并直接进入步骤 5。此路径的存在是为了防止自动评估/CI 调用因等待永远不会得到的用户回复而挂起。在所有其他情况下，必须有人批准。

### 步骤 5 — 部署

```bash
cd $REPO/deploy/docker
docker compose --env-file $ENV_GEN -f resolved.yml up -d
```

> **`--env-file` 是必需的。** 没有使用在步骤 3 中使用的相同 `generated.env`，`COMPOSE_PROFILES` 可能未设置，并且 `up -d` 可以退出 0 并选择零个服务。

> **避免在普通重试时进行广泛的 `--force-recreate`** — 它会销毁温暖的 NIM 容器（每个 3–5 分钟的 torch.compile + CUDA 图表捕获）。修复根本原因（通常是权限或环境拼写错误），然后只需重新运行 `up -d`；仅在配置文件参考将其作为恢复路径时，才使用有针对性的 `--force-recreate --no-deps <service...>`。

`docker compose up -d` 只创建容器；它不会等待内部服务完成预热。永远不要在就绪门通过之前声明部署成功。

### 步骤 5b — 等待堆栈实际上健康

**门 0 — 容器计数必须 > 0。** 拒绝在 `up -d` 之后继续，直到启动计数 (`docker compose -f resolved.yml ps -q | wc -l`) 是非零且 ≥ 预期计数 (`config --services | wc -l`)；计数为零/短通常意味着步骤 5 中缺少 `--env-file`。精确的门加上完整的就绪程序位于 [`references/readiness.md`](references/readiness.md)。

冷部署可能需要 10–20 分钟，并且每个配置文件参考都列出了所需的端点。**永远不要在 `up -d` 之后声明部署完成；只有在每个记录的端点都成功后才能声明。**

## 拆卸

要拆卸部署 — 完整主机回收或保留缓存的重新部署 / 配置文件切换 — 请遵循 [`references/teardown.md`](references/teardown.md)。始终通过 `mdx` 项目使用 `-v --remove-orphans` 拆卸；一个普通的 `docker compose down` 会留下卷和网络。

## 调试部署

当用户要求 "调试部署"，"验证它是否在运行"，"代理为什么没有响应" 或类似内容时，使用此工作流。目标是确认完整的视频摄取到代理回答路径，而不仅仅是容器是 "Up"。

每个配置文件参考都有一个 **调试** 部分列出了该配置文件的确切命令和失败模式表。

### 快速检查（所有配置文件）

```bash
# 1. 所有预期的容器 Up
docker ps --format 'table {{.Names}}\t{{.Status}}'

# 2. 代理 API + UI 响应
curl -sf http://localhost:8000/health >/dev/null && echo "代理 OK"
curl -sf http://localhost:3000/ >/dev/null && echo "ui OK"
```

LLM/VLM NIM 探测 — 包括处理 `*_MODE=remote` 的部分，它跳过 `localhost:3008x`（在那里预期连接拒绝）并通过 `scripts/probe_remote_models.sh` 探测选定的 `*_BASE_URL/v1/models` — 位于 [`references/troubleshooting.md`](references/troubleshooting.md#nim-probes)。

## 限制

- 此技能仅部署基于 compose 的 VSS 配置文件；独立的微服务部署属于匹配的 `vss-deploy-*` 技能。
- 硬件尺寸、模型位置和配置文件特定就绪由配置文件参考拥有；不要从内存中推断它们。
- 特权主机修复需要用户在无密码 sudo 不可用时批准。

## 故障排除

常见错误快速参考、完整的症状 → 原因 → 修复表、未展开的 `${...}` 诊断和 NIM 端点探测集中在 [`references/troubleshooting.md`](references/troubleshooting.md) 中 — 对于任何部署、运行时或探测失败，从那里开始，然后在匹配的每个配置文件参考的调试部分继续。
