# TAO 推理微服务

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

## 说明

**要启动推理服务：**
1. 收集所需输入（第 1 节）并解析容器镜像（第 2 节）。
2. 构建作业负载和内部命令（第 3-4.1 节）；使用 `references/code-templates.yaml` → `job_payload_builder`。
3. 读取 `skills/platform/<platform>/SKILL.md` 并启动容器（第 4.2 节）。
4. 写入服务注册表并轮询就绪状态（第 4.3 节）；使用 `references/code-templates.yaml` → `registry_write.<platform>` 和 `readiness_check`。

**要发送推理请求：**
1. 根据第 6.0 节解析接收请求的服务（按 `job_id`、按 `network_arch` 或在多个服务运行时用户显式选择——**当存在多个服务时，切勿静默默认为 `"latest"`**），然后从 `references/code-templates.yaml` → `request.registry_read` 中读取端点，使用解析的 `job_id`。
2. **在构建请求体之前，提示用户输入 vLLM 风格的采样参数（第 6.1 节）。** 提供 `max_tokens`、`top_p`、`temperature`（以及任何按架构的额外参数）及其默认值；允许用户覆盖或跳过每个参数以接受默认值。切勿静默使用默认值。
3. 根据第 6.2 节构建并发送请求体；根据第 6.3 节处理响应。

**要停止服务：** 读取 `references/code-templates.yaml` → `stop.registry_read` 以解析作业 ID，读取 `skills/platform/<platform>/SKILL.md`，然后按照第 5 节操作。

**参考数据**（模式、映射、有效值——无指令）：
- **`references/service.yaml`** — 镜像映射、有效的 `network_arch` 名称、作业负载模式、环境变量名称、密钥分类。
- **`references/request.yaml`** — 端点定义、请求字段模式、响应形状、代码示例。
- **`references/code-templates.yaml`** — 用于负载构建、注册表写入、就绪检查和停止/请求流程的 Python 模板。

---

## 密钥规则（适用于此技能生成的每个代码块）

**切勿要求用户在提示中输入密钥值。** 对于每个密钥值：
1. 告知用户要设置哪个环境变量——`export HF_TOKEN=...` 在他们的 shell 中，或用户批准的 env 文件中的 `KEY=value` 行，使用 `set -a; source /path/to/.env; set +a` 加载。
2. 切勿打印、`cat` 或 `Read` 这样的文件——仅验证存在性：`[ -n "$HF_TOKEN" ] && echo SET || echo UNSET`。
3. 生成代码使用 `os.environ["VAR_NAME"]` 读取它——切勿硬编码、插值或提示输入值。

**密钥环境变量**（完整列表在 `references/service.yaml` → `secrets_handling`）：
`HF_TOKEN`、`WANDB_API_KEY`、`CLEARML_API_ACCESS_KEY`、`CLEARML_API_SECRET_KEY`、`TAO_API_KEY`、`TAO_USER_KEY`。

**安全收集在提示中：** `network_arch`、`model_path`、`num_gpus`、提示文本、`WANDB_*` 配置 URL、`CLEARML_*_HOST` URL。

---

## 1. 从用户收集什么

| 输入 | 角色 |
|--------|------|
| **`network_arch`** | 选择容器镜像、每个架构的内部命令形状 (`references/service.yaml` → `container_commands.<network_arch>`), 以及在适用的情况下作业 JSON 中的 `neural_network_name`。必须匹配 `references/service.yaml` 中 `valid_network_arch_config_basenames` 中的基本名称（例如 `cosmos-rl`、`cosmos-predict2.5`）。 |
| **`model_path`** | 训练模型检查点。有效形式：`hf_model://<org>/<model>`（HuggingFace Hub — 为受保护的模型设置 `HF_TOKEN`）或本地容器文件系统路径。云 URI (`s3://`、`gs://`、`az://`) 不受支持——推理服务没有云存储依赖。始终询问用户；切勿替换占位符。参见 `references/service.yaml` → `model_path_protocols`。 |
| **`platform`** | 计算平台：`local-docker`、`brev`、`slurm` 或 `kubernetes`。 |
| **`num_gpus`** | 默认为 **1**；推理最小 **1**。 |

---

## 2. 镜像解析

每个 `network_arch` 都有一个名为 `{network_arch}.config.json` 的侧车配置文件。按以下方式解析容器镜像：

1. 读取 `{network_arch}.config.json` 并获取 `api_params.image`（例如 `COSMOS_RL`）。这会选择 `references/service.yaml` 中 `docker_image_defaults` 的条目。
2. 如果主机环境变量 `IMAGE_<KEY>` 被设置（例如 `IMAGE_COSMOS_RL`），它将覆盖打包的默认值。
3. 对于 `model_skill_defaults` 下面的键，调用 `scripts/resolve_tao_image.py` 并传入其模型、操作和后端。这保留了 Cosmos 模型技能的 `references/skill_info.yaml` 中的确切 Cosmos 镜像。
4. 对于 `mapping` 下面的键，使用 `scripts/resolve_versions_key.py` 将点值解析到 repo-root `versions.yaml`。绝对环境变量按原样通过。Python 示例位于 `references/code-templates.yaml`。
5. 如果配置文件丢失或 `api_params.image` 为空，则回退到 `COSMOS_RL` 键。

配置文件还具有 `spec_params.inference.model_path`，它驱动**文件夹与文件**路径语义：如果值包含子字符串 `folder`，则容器将路径视为目录。

---

## 3. 环境变量（无回调）

在编码 `env_json` 之前在 `env_payload` 中设置这些。**不要**设置 `TAO_LOGGING_SERVER_URL` 或 `TAO_ADMIN_KEY`。

**`TAO_EXECUTION_BACKEND`** — 必须与平台匹配：

| 平台 | `TAO_EXECUTION_BACKEND` 值 |
|----------|-------------------------------|
| local-docker | `local-docker` |
| brev | `local-docker` |
| slurm | `slurm` |
| kubernetes | `local-k8s` |

**`CLOUD_BASED`** — 此技能始终为 `"False"`（禁用向 `TAO_LOGGING_SERVER_URL` 发送回调）。

**GPU 环境变量**——仅当平台技能不自动处理 GPU 注入时需要：
- Tegra / Jetson: `--runtime=nvidia` 与 `NVIDIA_DRIVER_CAPABILITIES=all` 和 `NVIDIA_VISIBLE_DEVICES=<ids>`。
- 标准 x86 + nvidia-container-toolkit: 使用 Docker `device_requests`。平台技能处理此操作。

---

## 4. 跨平台执行

作业负载和内部命令（第 1-3 节）是**平台无关的**。对于每个平台，在生成任何执行代码之前，读取 **`skills/platform/<name>/SKILL.md`** 进行预检和凭证。

### 4.1 按架构构建内部命令

内部命令形状是**按 `network_arch`** 的——没有统一模板。在 `references/service.yaml` → `container_commands.<network_arch>` 中查找每个架构的条目；如果不存在，则该架构不受支持——停止并询问。选择匹配的子块在 `references/code-templates.yaml` → `job_payload_builder.<network_arch>` 中。以 `umask 0 &&` 开头，并保持其在所有平台上的**完全相同**（local-docker、brev、slurm、kubernetes）。

跨架构的常见内容：

- `job_id`: 新的 `uuid.uuid4()` —— 成为容器名称和注册表键。
- `image`: 按第 2 节解析。
- 密钥 (`access_key`、`secret_key`、`HF_TOKEN` 等) 在运行时从环境变量中读取——**切勿硬编码**，**切勿记录或打印**。

架构特定说明（完整细节在 `references/service.yaml` → `container_commands`）：

- **`cosmos-rl`** — 单个 `--job '<JOB_JSON>' --docker_env_vars '<ENV_JSON>'` 块；`json.dumps(...)` + `shlex.quote(...)`。`env_payload` 携带 `TAO_EXECUTION_BACKEND`（按第 3 表），`TAO_API_JOB_ID`，`CLOUD_BASED=False`。推理服务没有云存储依赖；`HF_TOKEN` 是唯一可能适用的凭证环境变量（用于受保护的 HuggingFace 模型）。
- **`cosmos-predict2.5`** — 标志式 `cosmos_predict inference_microservice start ... --port 8080`（无 `setup.` 前缀；使用 `tyro.conf.OmitArgPrefixes`）。`--job`/`--docker_env_vars` **不被接受**。将 `model_path` 转换为 `--checkpoint-path`（本地路径）或 `--model <registered_key>` (`hf_model://`）；拒绝云 URI。唯一可能适用的凭证环境变量是 `HF_TOKEN` 用于受保护的 HuggingFace 模型。按请求参数（提示、推理类型、num_output_frames、指导、种子、num_steps、negative_prompt）进入请求体，而不是在启动时。`TAO_EXECUTION_BACKEND`/`TAO_API_JOB_ID`/`CLOUD_BASED` 未使用且可以省略。

### 4.2 将执行委托给平台技能

读取 **`skills/platform/<platform>/SKILL.md`** 并遵循其启动容器。

**基本参数（所有平台）：**

| 参数 | 值 |
|-----------|-------|
| `image` | 解析的容器镜像（第 2 节） |
| `command` | `inner` — 第 4.1 节构建的 shell 字符串 |
| `gpu_count` | `num_gpus` |
| `env_vars` | `env_payload` |
| 作业/容器名称 | `job_id` — 必须等于 4.1 中的 UUID，以便注册表可以引用它 |
| `host_port` *(local-docker, brev)* | 绑定到容器端口 8080 的主机侧端口。默认 `8080`，但**必须对每个并发服务唯一**——见下文的端口分配规则。 |

**平台特定附加输入：**

| 平台 | 附加输入 |
|----------|------------------|
| **local-docker** | 无 |
| **brev** | `instance_id`（可选——重用现有实例）；在多凭证/多工作区帐户中也 `cloud_cred_id` 和 `workspace_group_id` 用于首次创建——参见 `skills/platform/tao-run-on-brev/SKILL.md` |
| **slurm** | `partition` 和 `account` — 检查 `SLURM_PARTITION`/`SLURM_ACCOUNT` 环境变量；如果未设置，则询问用户 |
| **kubernetes** | `namespace`（默认：`default`）；`image_pull_secret`（对于 `nvcr.io` 镜像必需） |

**端口绑定（local-docker 和 brev）：** 使用**直接 docker run**，以便可以传递 `-p <host_port>:8080`，并且容器名称等于 `job_id` 恰好。

**端口分配规则（local-docker 和 brev，并发服务必需）：** 在启动服务之前，读取注册表（`/tmp/tao-inf-ms-state.json`）并收集同一平台上每个现有条目的 `host_port` 集合（对于 brev，还包括相同的 `instance_id`）。选择从 8080 开始的**最低空闲端口**，该端口不在该集合中——例如 `host_port = next(p for p in range(8080, 8200) if p not in used_ports)`。默认 `8080` 仅在未运行其他服务时适用。这就是“启动 3 个服务，每个服务都可以在唯一的 `host_url` 上访问”工作的原因；如果没有它，服务 2 和 3 会因 `bind: address already in use` 而失败。SLURM 和 kubernetes 从它们自己的平台机制获取不同的端点，不需要此步骤。

### 4.3 启动后：服务注册表和端点

平台确认容器正在运行后立即写入服务注册表。注册表（`/tmp/tao-inf-ms-state.json`）按 `job_id` 键入；`"latest"` 始终指向最近启动的服务。

见 `references/code-templates.yaml` → `registry_write.<platform>` 的 Python 模板。

| 平台 | `host_url` | `platform_job_id` | 写入前的额外步骤 |
|----------|-----------|-------------------|--------------------------|
| **local-docker** | `http://localhost:{host_port}` | — | 无 |
| **brev** | `http://{brev_ip}:{host_port}` | — | `brev ls` → 获取实例 IP（`localhost` 在远程 VM 上无效） |
| **slurm** | `http://localhost:{host_port}` | SLURM 调度器作业 ID | 等待 Running；SSH 端口转发 `localhost:{host_port}→{node}:8080` |
| **kubernetes** | `http://{external_ip}:8080` | k8s 作业名称 | `kubectl expose job … --type=LoadBalancer`；等待外部 IP |

写入注册表后，打印作业 ID 和 URL：

```python
print(f"Inference service started.")
print(f"  Job ID : {job_id}")
print(f"  Arch   : {network_arch}")
print(f"  URL    : {state[job_id]['host_url']}/v1/chat/completions")
print(f"Use this Job ID to send requests or stop the service.")
```

然后轮询就绪状态——见 `references/code-templates.yaml` → `readiness_check`。容器在后台加载模型；在它返回 200 之前不要发送请求。

---

## 5. 停止推理服务

询问用户要停止的 `job_id`。如果他们不提供，则默认为 `state["latest"]` 并确认要停止哪个作业 ID。使用 `references/code-templates.yaml` → `stop.registry_read` 读取注册表，然后读取 **`skills/platform/<platform>/SKILL.md`** 并使用其取消/停止机制。

| 平台 | 传递的标识符 | 额外清理 |
|----------|--------------------|---------------|
| **local-docker** | `job_id_to_stop` — 容器名称 | 无 |
| **brev** | `job_id_to_stop` — 容器名称 | 无 |
| **slurm** | `entry["platform_job_id"]` — SLURM 作业 ID | `pkill -f "ssh.*-L.*{entry['host_port']}"` |
| **kubernetes** | `entry["platform_job_id"]` — k8s 作业名称 | `kubectl delete svc {entry["platform_job_id"]} -n <namespace>` |

其中 `entry = state[job_id_to_stop]`。停止后，清理注册表：`references/code-templates.yaml` → `stop.registry_cleanup`。

---

## 6. 发送推理请求

### 6.0 确定哪个服务接收此请求（必需）

每个请求都必须路由到运行**特定**匹配模型的**服务**。路由通过 `job_id` 发生——注册表按条目存储 `network_arch`，因此您可以在用户命名模型而不是 `job_id` 时解析目标架构。按顺序应用这些规则：

1. **用户提供了显式的 `job_id`** → 使用它。验证它是否存在于 `state` 中。
2. **用户命名了 `network_arch`**（例如“将此发送到 cosmos-rl 服务”）→ 查找匹配的条目：`candidates = [j for j, e in state.items() if j != "latest" and isinstance(e, dict) and e["network_arch"] == arch]`。
   - 恰好一个匹配 → 使用它。
   - 多个匹配 → **提示用户**候选 `job_id` 及其 `started_at`；不要自动选择。
   - 无匹配 → 停止并告诉用户该架构没有运行的服务。
3. **没有 `job_id` 且没有 `network_arch`** → 计算非 `"latest"` 的 `state` 条目：
   - 恰好一个运行的服务 → 使用它。
   - 两个或更多 → **不要静默默认为 `state["latest"]**`。提示用户完整的列表（`job_id`、`network_arch`、`host_url`）并要求明确选择。`"latest"` 指针是单服务工作流的便利，而不是多个服务共存时的路由回退。
   - 零 → 停止并告诉用户先启动服务。

解析后，从注册表读取端点（`references/code-templates.yaml` → `request.registry_read`），将解析的 `job_id` 作为 `user_provided_job_id` 传入。向用户确认：“发送到 job_id=… arch=… url=…”。如果服务可能仍在加载，则先轮询就绪状态（`references/code-templates.yaml` → `readiness_check`）。

**发送前交叉检查：** 如果用户提供的请求体包含架构特定字段（例如 `guidance` / `num_steps` / `seed` / `negative_prompt` → cosmos-predict2.5；要求 `image_url`/`video_url` 内容项 → cosmos-rl），请验证它们与 `state[job_id]["network_arch"]` 一致。在不匹配的情况下停止并询问——将 cosmos-predict2.5 请求体发送到 cosmos-rl 服务会在容器中失败，其 4xx/5xx 错误比在此处捕获更难诊断。

### 6.1 采样参数——每个请求前必需的用户提示

在构建请求体之前，您**必须**明确提示用户输入 vLLM 风格的采样参数。**不要**静默应用默认值。使用结构化提示，每个字段一个问题，允许用户跳过/接受任何字段以接受该字段的默认值——输入值不是必需的。
收集所有字段。

提示后，逐字应用每个用户输入的值，并使用默认值替换任何跳过的字段。不要编造值或静默调整。

**字段列表、默认值和按架构的适用性：** `references/request.yaml` → `chat_completions_request_body`（基本采样字段：`max_tokens`、`top_p`、`temperature`）和 `network_arch_constraints.<network_arch>`（按架构的覆盖和额外参数，例如 `cosmos-predict2.5` 的 `guidance`/`num_steps`/`seed`/`negative_prompt`）。如果字段被标记为当前架构不支持，则**不要**提示输入，**不要**将其包含在请求体中。

### 6.2 请求格式

发送 `POST` 到 `{BASE_URL}/v1/chat/completions`，`Content-Type: application/json`，超时至少为 **300 s**。请求体是 OpenAI 兼容的（vLLM 聊天补全）；见 `references/request.yaml` → `chat_completions_request_body` 了解完整字段模式和内容项形状（文本 / image_url / video_url），以及 `code_examples` 了解可立即运行的 Python 和 curl 示例。

**约束：** 仅处理第一个用户消息。请求体中无密钥值。**按网络约束**（例如 cosmos-rl 要求每个请求都包含图像或视频；cosmos-rl 拒绝 `data:` URI）在 `references/request.yaml` → `network_arch_constraints` 中。

### 6.3 响应处理

| HTTP 状态 | 含义 | 操作 |
|-------------|---------|--------|
| **200** | 成功 — `choices[0].message.content` 包含生成的文本 | 读取结果 |
| **202** | 服务器仍在初始化或模型仍在加载 | 延迟后重试 |
| **503** | 初始化失败、模型加载失败、**或模型尚未就绪** | 检查 `error.type`：`model_not_ready` → 重试；`initialization_error` / `model_load_error` → 放弃并检查日志 |
| **400** | 缺失或空的 JSON 正文 | 修复请求 |
| **500** | 推理期间发生未处理的异常 | 检查容器日志 |

对于 202 和 503，正文包含 `{"error": {"type": "<error_type>", "message": "<reason>"}}`。见 `container_response_shapes` 在 `references/request.yaml` 中的错误类型字符串。
