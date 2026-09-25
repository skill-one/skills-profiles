# TAO 执行 SDK

> **是否需要独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

该 SDK 是用户需要作业句柄、S3 I/O 封装或平台特定功能（SLURM/Lustre 队列、Kubernetes 作业、本地 Docker 调试、Brev 实例重用）时的**可选** Python 层。大多数 TAO 技能仅使用 `docker run` 即可运行，无需该 SDK。当您需要以下功能时，请使用该 SDK：

- 您需要一个 `Job` 句柄来轮询状态并随时间流式传输日志。
- 您需要在入口点中嵌入 S3 感知的输入下载/输出上传。
- 您正在链接多个作业并希望持久化状态。

## 预检

在使用此平台之前，请安装 `nvidia-tao-sdk[all]` — `[all]` 附加项会拉取所有平台特定依赖项（Brev、S3 工具等）。如果缺失，请在活动的 Python 环境中默认安装它并重新运行导入检查：

```bash
python -c "import tao_sdk" 2>/dev/null || {
  echo "安装缺失的 Python 依赖项：nvidia-tao-sdk[all]"
  python -m pip install "nvidia-tao-sdk[all]"
}
python -c "import tao_sdk"
```

包索引是环境特定的 — 预置程序/容器应具有工作的 `pip` 配置（例如 `~/.pip/pip.conf`、`PIP_INDEX_URL`、`PIP_EXTRA_INDEX_URL` 或代理）。如果由于索引/网络原因安装失败，那是预置程序设置问题；此技能对注册表保持中立。

缺失的 pip 依赖项默认自动安装并报告在运行日志中。非 pip/系统先决条件仍然需要正常的预检失败和用户可见的修复措施。

## 设置

凭证来自**环境变量** — 从会话环境读取（在启动之前在您的 shell 中导出它们）。

```python
from tao_sdk.platforms.brev   import BrevSDK     # Brev GPU 实例

sdk = BrevSDK()      # 读取 BREV_API_TOKEN（可选 — 回退到 brev 登录）
```

SDK 在首次使用时惰性验证凭证，如果缺少必需的环境变量，则会引发 `CredentialError` 并附带清晰的错误消息。必需的环境变量：

| 平台 | 必需 | 可选 |
|---|---|---|
| Brev | — (手动 `brev login` 可工作) | `BREV_API_TOKEN` |
| S3 I/O（任何平台） | `S3_BUCKET_NAME`、`ACCESS_KEY`、`SECRET_KEY` | `S3_ENDPOINT_URL`、`CLOUD_REGION` |
| 容器环境 | `NGC_KEY` | `HF_TOKEN` |

代理永远不会读取凭证值 — 它仅使用 `[ -n "$VAR_NAME" ]` 检查存在性。

## 工作流启动输入

对于任何 TAO 工作流或操作启动，首先确认用户目标。然后在凭证或启动详细信息之前，询问平台和监控偏好。
从打包的辅助工具生成支持的平台选择，而不是扫描平台文档或文件夹：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/list_tao_platforms.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skills-external} --format text
```

询问：

1. 哪个支持的平台应运行此工作流？
2. 长时间运行的监控是否保持启用？默认：启用。这意味着代理保持连接并发布状态，直到终端状态，包括长时间的 `PENDING` 队列等待。
3. 状态更新之间的分钟数是多少？默认：5 分钟。

在工作流/操作已知后，从打包的元数据解析默认容器镜像，并询问用户确认或提供 `image=<override>`，然后再创建运行者文件：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/resolve_tao_image.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skills-external} \
  --model <network_arch> --action <action> --format text
```

对于可训练模型工作流，在创建普通训练作业之前，检查模型级别的 AutoML 元数据：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/list_tao_models.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skills-external} \
  --scope automl --format json
```

如果选定的模型具有 `automl_enabled: true` 且有效的训练模式，默认通过 `skills/applications/tao-run-automl` 路由训练，并使用 `automl_policy: on`。工作流应仅在运行设置包括 `automl_policy: off`、用户明确要求普通运行或模型元数据说明 AutoML 已启用但训练模式尚未打包时绕过 AutoML。

平台选定后，获取凭证过滤器：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skills-external}/scripts/list_tao_platforms.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skills-external} \
  --platform <platform> --format text
```

仅询问选定平台的凭证。例如，SLURM 需要 `SLURM_USER` 和 `SLURM_HOSTNAME`；它不需要 Brev 凭证。Kubernetes 和本地 Docker 不需要 Brev 或 SLURM 凭证。仅在选定的平台和数据/结果 URI 需要它们时，才询问存储凭证，例如 S3 密钥。

## 核心 API

所有平台 SDK 实现相同的核心结构：

```python
sdk.create_job(image, command, gpu_count=1, env_vars=None, inputs=None, outputs=None, **kwargs) -> Job
sdk.get_job_status(job_id) -> JobStatus
sdk.get_job_logs(job_id, tail=None) -> str
sdk.cancel_job(job_id) -> bool
sdk.get_failure_analysis(job_id) -> dict | None
sdk.get_job_results_dir(job_id) -> str
sdk.check_path(remote_path) -> bool
sdk.list_path(remote_path) -> list[str]
```

仅 Brev：
- `sdk.delete_instance(instance_id)` — 清理临时实例。
- `sdk.list_instances()` — 列出活动实例。

## 提交作业

代理始终**通过 `build_entrypoint` 构建容器命令**，然后再调用 `create_job`。代理从 `skill_info.yaml` 读取操作的架构（`command`、`mode`、`config_format`、`inputs`、`outputs`、`upload_excludes`），并将这些字段作为 kwargs 传递。`build_entrypoint` 然后封装：

1. 容器内的 `script_runner` 运行时（作为 base64 套接文档内联 — 无需在容器中安装 `tao_sdk`）。
2. 在容器运行时将调用的 CLI 语句：下载声明的输入（S3 / HF-Hub / NGC）、在 `{config_path}` 写入规范文件并将远程 URI 重写为本地路径、运行用户命令，并上传输出。

输出目的地在运行时从 SDK 注入的环境变量解析（见下文“输出去向”）。平台 SDK 的 `create_job` 运行生成的命令**原样** — 无输入/输出 kwargs，无隐式封装。数据流在代理的代码中可见。

### 输出去向（运行时解析 — 代理不管理）

SDK 将 `TAO_JOB_ID`（匹配 `Job.id`）和在附加持久挂载时 `TAO_RESULTS_ROOT` 注入容器环境。在容器内，`script_runner` 解析输出目的地：

| 容器环境 | 结果 |
|---|---|
| `TAO_RESULTS_ROOT` 设置（Lustre / PVC / 绑定 / NFS） | 输出在 `{TAO_RESULTS_ROOT}/<job_id>/<key>/`；无需上传 |
| `S3_BUCKET_NAME` 设置（云，无挂载） | 输出在 `s3://{bucket}/results/<job_id>/<key>/`；在运行结束时上传 |
| 都未设置 | 输出在 `/results/<job_id>/<key>/`（容器临时）带运行结束时的响亮警告 |

按平台策略：

| SDK | 注入的内容 |
|---|---|
| `SlurmSDK` | `TAO_RESULTS_ROOT={SLURM_BASE_RESULTS_DIR}/results`（始终 — Lustre，永不 S3，避免 GPU-idle 调度器杀死） |
| `KubernetesSDK` / `DockerSDK` / `BrevSDK` | 如果挂载目标为 `/results`，则 `TAO_RESULTS_ROOT=/results`；否则 S3 回退 |

希望自定义目的地的代理可以将 `s3://...` URI 或绝对路径直接放在输出规范键处 — 显式值会覆盖自动填充。否则，模型自然默认值（如 cosmos-rl 的 `output_dir: "output"` 或 DINO 的空 `results_dir`）会由 `script_runner` 自动重写。

### 规范是嵌套字典，不是扁平点键

构建规范时最常见的错误。`skill_info.yaml` 中 `inputs:` / `outputs:` 块中出现的点符号（例如 `section.subsection.key`）是**嵌套规范中的路径** — `script_runner` 在该路径处查找值。它不是规范自身的形状。规范镜像模型容器期望的形状（通常是嵌套的 TOML/YAML）。

```python
# ✓ 正确 — 嵌套字典
specs = {
    "section": {
        "subsection": {"key": "value"},
    },
}

# ✗ 错误 — 扁平顶层键带点。TOML/YAML 发出此作为引用的裸字符串键，模型看到空的 `section` 表，任何在 "section.subsection.key" 声明的输入将因 `_get_nested(specs, "section.subsection.key") → None` 而静默失败。
specs = {
    "section.subsection.key": "value",
}
```

这两种形状看起来表面相似，但含义不同。如有疑问，请打开模型的 `references/` 目录（例如默认规范的 TOML 或 YAML）— 那是规范字典需要镜像的原始嵌套结构。`skill_info.yaml` 中的 `inputs:` / `outputs:` 声明是嵌套规范的路径，不是键名。

### 构建规范/参数

技能在其 `skill_info.yaml` 的 `actions.<action>.mode` 字段中声明其配置机制。将缺失的 `mode` 视为无效元数据并修复技能，而不是推断默认值。首先读取 `actions.<action>.mode`，然后传递匹配的参数形状给 `build_entrypoint`：

| 声明模式 | 代理传递的内容 |
|---|---|
| `config` | `specs=...` 带规范键的 `inputs` / `outputs`；辅助工具写入规范文件、重写 URI 并运行命令 |
| `args` | `args=...` 带可选规范键的 `inputs` / `outputs`；辅助工具将 CLI 参数替换到命令模板 |
| `passthrough` | 路径键的 `inputs=...` 和/或 `outputs=...`；辅助工具下载到列表路径，运行命令，并上传列表输出 |

不要从缺失的元数据推断模式。缺失的 `mode` 表示技能契约已过时。

有关每种模式的构建策略、推荐决策顺序和规范驱动作业（配置文件）和路径键作业（无配置文件）的 `build_entrypoint` 示例，请参阅 [`references/spec-construction.md`](references/spec-construction.md)。

## 解析容器镜像

技能通过键（`tao_toolkit.pyt`）或绝对 URI（`nvcr.io/...`）声明镜像。使用 `resolve_container_image()` 处理两者：

```python
from tao_sdk.versions import resolve_container_image
image = resolve_container_image(skill_info["container_image"])
```

在后台，它遍历 `versions.yaml` 以键；绝对 URI 原样返回。

## 监控

```python
status = sdk.get_job_status(job.id)
print(status.status)   # Pending, Running, Complete, Error, Canceled
print(status.message)  # 平台特定详细信息

logs = sdk.get_job_logs(job.id, tail=200)
print(logs)
```

失败时，`get_failure_analysis()` 对根本原因进行分类：

```python
analysis = sdk.get_failure_analysis(job.id)
if analysis:
    print(analysis["err_class"])   # ERR_PROGRAM, ERR_INFRA, 等。
    print(analysis["suggestion"])  # 人类可读的修复措施
    for event in analysis.get("job_failure_by_node_event", []):
        print(event["node_event_name"], event["message"])  # OOM, GPU 错误，等。
```

## 轮询模式

对于用户希望观看的交互式运行：

```python
import time
status_interval_minutes = status_interval_minutes or 5
while True:
    status = sdk.get_job_status(job.id)
    if status.status in ("Complete", "Error", "Canceled"):
        break
    print(f"  {status.status}")
    time.sleep(status_interval_minutes * 60)

if status.status == "Error":
    print(sdk.get_job_logs(job.id, tail=100))
    print(sdk.get_failure_analysis(job.id))
```

启用长时间运行监控时，不要在 30 分钟或几次未更改的轮询后停止。保持每 `status_interval_minutes` 发送更新，直到作业完成、失败、被取消，或用户要求分离/停止。如果聊天/运行时无法保持那么长时间，请明确说明并提供可持久的工作流/日志路径以手动刷新状态。

不要使用最终响应来监控非终端作业。最终化回合会分离聊天监视器。保持非终端状态消息在进度更新中，继续轮询；仅在终端状态、显式用户分离/停止或无法进一步轮询的真实运行时限制下最终化。

对于后台运行，持久化 `job.id` 和 `state_file` 路径，稍后通过构建相同的 SDK 并调用 `get_job_status(job_id)` 重新连接 — 作业状态从磁盘存储读取。

## 编排模式

多步骤工作流、并行扫描和通过 `ActionWorkflow` 实现的运行文件夹持久化位于 [`references/orchestration-patterns.md`](references/orchestration-patterns.md)。在链接 `create_job` 调用、扫描参数或跨上下文中断持久化运行状态之前，请先阅读它。

## 数据集工具

当技能的文档文件名与用户的布局不匹配时，请列出数据集以确认：

```python
assert sdk.check_path("s3://my-bucket/coco/")
files = sdk.list_path("s3://my-bucket/coco/train/")
# 使用实际路径设置规范字段。
```

对于 S3 路径，在连接时删除尾随斜杠以避免 `//`：

```python
base = dataset_uri.rstrip("/")
specs["dataset"]["train_csv"] = f"{base}/train.csv"   # 嵌套 — 见“规范是嵌套字典”
```

## 平台特定说明

有关每个平台的特定行为、kwargs 和凭证作用域，请参阅 [`references/platform-notes.md`](references/platform-notes.md)：Brev（`instance_id`/`gpu_type`/`cloud_cred_id`/`workspace_group_id`、就绪等待超时）、SLURM（SSH 上 sbatch、Lustre 路径、队列默认值）、Kubernetes（kubeconfig、GPU Operator），以及本地 Docker（单主机、多 GPU）。

## 错误模式

SDK 错误→根本原因→修复映射位于 [`references/error-patterns.md`](references/error-patterns.md)。当您遇到 `CredentialError`、镜像拉取失败、卡在 `Pending` 的作业或类似情况时，请阅读 — 条目将异常文本映射到根本原因。

## SDK 不做什么

SDK 不会读取/解释技能、自行运行 AutoML、决定规范内容、选择平台或编排多步骤工作流 — 这些仍然是代理的责任。有关完整范围护栏，请参阅 [`references/scope.md`](references/scope.md)，包括模型级别的 AutoML 政策（`automl_enabled: true` → `skills/applications/tao-run-automl`，除非 `automl_policy: off` 或用户要求普通单次运行）。
