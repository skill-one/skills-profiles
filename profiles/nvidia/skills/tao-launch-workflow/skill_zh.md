# TAO 工作流启动输入

> **是否为独立安装？** 如果此会话未由 TAO 技能库插件初始化，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

在启动任何 TAO 工作流或模型操作之前，请使用此技能。

## 快速入门

运行平台辅助工具，询问平台和监控偏好，然后运行所选平台的详细辅助工具，再询问凭证。

## 不可协商的启动门

此门与模型无关。在启动有副作用的操作之前，将其应用于每个 TAO 模型、数据操作和应用工作流。

在启动预检通过之前，**不要**创建运行者脚本、启动脚本、兼容性垫片、工作区文件夹、状态文件、日志或依赖安装的副作用。

预检仅在这些全部为真时通过：

1. 执行平台从打包的平台辅助工具中选择。
2. 平台凭证和必需的凭证组得到满足。
3. 模型特定凭证得到满足。
4. 默认容器镜像从打包的模型/操作元数据中解析，展示给用户，并由显式的 `image=<override>` 确认或替换。
5. 平台访问检查从启动主机成功。
6. 数据集输入从所选平台的视角映射到具体规范键并得到验证。
7. 模型/工作流技能所需的计算形状字段已知。
8. 所选数据/平台路径所需的本地工具存在，或用户批准安装最小的缺失依赖项并重新运行预检。
9. 已向用户展示并确认的启动审查，包括镜像、平台、数据集、计算形状、预期运行时间和任何生成的/默认配置更改。对于 AutoML，即使使用默认值，启动审查也必须明确说明推荐计数/预算、最大并发性、算法、指标、方向以及搜索参数/范围。

如果任何项缺失，请请求缺失的输入并在生成工件之前停止。这适用于 AutoML、正常训练/评估/推理/导出/TRT 和 DEFT/应用工作流。

当预检工作清除障碍时，请跟踪原始用户请求。修复后，重新运行相关预检并继续向该请求；不要在“障碍已修复”时停止，除非用户明确要求仅进行修复。

## 四动词执行契约

一旦启动门通过，并且产生模型/数据的技能已编写规范包（模式：`tao-artifacts`），执行就是精确的四个动词。每个平台技能在其原生 CLI 上实现它们——银行提供五个（`tao-run-on-docker`、`-slurm`、`-kubernetes`、`-brev`、`-virtualenv`），任何外部安装的平台技能加入相同的契约（§ 外部平台技能）；没有其他是平台特定的。
`$BANK` = `${TAO_SKILL_BANK_PATH}`。

- **submit(spec-bundle)** — 首先解决数据问题：如果输入可以从计算框架**读取**（本地路径、现有挂载——Tier A 已就位，通用本地和唯一的空气隔离情况），则无需阶段——记录 Tier A 并继续。仅在**框架不匹配**（远程 URI、跨主机路径、PTM 获取、Tier-C 结果上传）时调用 `tao-data-io`。然后使用 `redact_secrets.py lint` 检Lint 组装命令，并**按顺序打开记录和启动**：
  ```bash
  JOB_ID=$("$BANK/scripts/tao_job_record.py" open --platform <p> --image <img> \
    --network-arch <arch> --action <action> --storage-tier <A|B|C> --results-root <root>)
  # <原生启动，命名后端对象为 $JOB_ID>
  "$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state RUNNING --backend-ref <ref>
  ```
- **status(id)** — 轮询原生后端，映射到固定词汇 `PENDING RUNNING COMPLETE ERROR CANCELED UNKNOWN`；原生子状态（`ImagePullBackOff`、`PENDING`-资源、slurm `COMPLETING`）骑在转换 `message` 中。**不要**从记录中读取“正在运行”的内容——轮询后端。
- **logs(id, tail)** — 原生日志获取。
- **cancel(id)** — 原生取消+孤儿清理，然后 `mark <id> --state CANCELED`。

**记录后启动是顺序不变量。** `open` 在任何启动之前铸造 id 并绑定 `results_dir`，它返回的 id 是启动唯一可用的句柄——跳过门的提交或 `open` 没有id，所以无法启动。这是保持运行跨上下文中断可恢复的原因：`results_dir` 在后端对象（K8s TTL 或 docker `--rm` 可能稍后删除）之前记录。

当产生规范包声明 `execution` 时，将其保留为模型拥有的操作语义，跨所有重用该模型技能的应用程序。所选平台消耗生命周期；应用程序不得将其命令复制到私有启动器。平台无关的预/后命令、运行时认证、辅助依赖项、分布式意图和完成证据属于生产者的规范包。调度器语法、挂载、密钥、超时、排名和子进程退出保留为平台所有。

### 外部平台技能

无注册表，无接口文件：平台技能**通过文档记录四个动词来声明契约，并在首次使用前进行验证**。只有原生原语技能可能被使用，通过**推断**映射（银行不变量仍然绑定；映射放入启动审查；持久化有效内容）。规则和不可替代的硬底线：`references/external-platforms.md`。

### 失败分析 & 重试

当 `status` 达到 `ERROR` 时，读取日志尾部并在**任何重试之前进行分类**——基础设施故障可重试（新记录、`--retry-of`、最多 10 次），程序故障永不重试。完整标准、两个判断（设备端断言、下游跟踪）、以及后轮轮询规则：`references/failure-analysis-retry.md`。

## 初始问题

在用户确认他们要做什么之后，询问应使用哪个**执行平台**运行。从**此会话中安装的平台技能**发现选择——你已经通过名称和描述看到它们（`tao-run-on-docker`、`-slurm`、`-kubernetes`、`-brev`、`-virtualenv`，以及任何外部安装的，如官方 `brev-cli` 技能）。没有中央平台注册表可读取。如果你的运行时仅显示核心路由技能（例如 Codex），则通过读取 `${TAO_SKILL_BANK_PATH}` 下 `skills/platform/tao-run-on-*/SKILL.md` 前置（名称+单行描述）列出银行的平台技能。

然后询问：

- 哪个支持的平台应运行此工作流？
- 我是否应在聊天中监控运行？监控意味着我在启动后持续轮询后端/作业日志并报告进度，直到作业完成、失败或你要求我停止，即使作业保持排队数小时或数天。如果禁用，我启动作业，给你作业 id/日志路径，并停止轮询。默认：在聊天中监控。
- 我应多久报告一次状态？默认：每 5 分钟。对于烟雾测试，使用 1-2 分钟；对于正常训练，使用 5 分钟；对于长运行，使用 10-15 分钟。

当用户接受默认值时，使用 `long_running_enabled=true` 和 `status_interval_minutes=5`。

当监控启用时，不要因为几个轮询已过或作业仍为 `PENDING` 而发送最终摘要。保持回合连接，并每 `status_interval_minutes` 发出状态，直到达到终止状态或用户明确要求停止/分离。如果运行时环境无法保持聊天回合打开，请明确说明并留下持久的监视器/日志路径；不要暗示回合结束后聊天更新将继续。

最终答案规则：`final` 响应结束聊天侧监控。在 `long_running_enabled=true` 和任何已启动的作业非终止时，状态消息必须作为进行中更新发送，代理必须继续轮询。仅在以下情况下发送最终响应：工作流达到终止状态、用户明确要求分离/停止监控，或运行时确实无法保持回合打开；在后一种情况下，说明这是运行时限制并提供确切的持久状态命令/日志路径。

## 缺失输入提示形状

当输入缺失时，使用 `references/intake-prompts.md` 中的确切提示形状（一个整合的询问、具体示例、不发明默认值）。

## 实现后端解析

在模型所有权解析后，检查所选模型的 `references/skill_info.yaml`。如果它声明了 `backend_contracts`，则在选择镜像或编写规范之前解析实现。当显式后端支持模型/操作时，它将获胜；否则应用打包的 `backend_selection` 策略并展示其理由。在 `skill_info.yaml` 中选择的后端元数据拥有其镜像。引用的后端契约拥有入口点、配置模式、数据映射、拓扑、检查点格式、输出布局和状态行为。**不要**为多后端前端使用遗留顶层镜像回退，也**不要**将一个后端视为另一个版本的回退。

将操作、后端和工作负载提示传递给模型解析器。当元数据声明后端规划器时，使用它。例如，共享的 Cosmos 前端使用 `scripts/cosmos_workflow.py plan` 生成后端原生 TOML 和启动序列。

## 容器镜像确认

在创建规范、运行者脚本、工作区、日志、状态文件或提交作业之前，解析所选模型/操作的镜像：

```bash
${TAO_SKILL_BANK_PATH:-~/tao-skill-bank}/scripts/resolve_tao_image.py \
  --skill-bank ${TAO_SKILL_BANK_PATH:-~/tao-skill-bank} \
  --model <network> --action <action> --backend <auto-or-explicit> \
  --workload <workload-hint> --format text
```

如果辅助工具不可用，直接读取 `skills/models/<network>/config.json`。按顺序解析镜像字段：

1. `backend_contracts.<selected-backend>.container_image`，当存在时
2. `actions.<action>.container_image`
3. `actions.<action>.image`
4. 顶层 `container_image`
5. 顶层 `image`

展示确切镜像并询问：

```text
<网络>/<操作> 的容器镜像：
默认=<解析的镜像>

使用此镜像，或提供 image=<override>？
```

如果用户接受，将解析的镜像作为作业 `image` 传递。如果用户覆盖，要求非空的镜像引用并传递该值。不要在默认镜像上无声启动。此确认适用于训练、AutoML 推荐、评估、推理、导出、TensorRT 引擎生成和应用工作流提交 TAO 容器。

## 凭证过滤

在用户选择平台后，从所选技能本身获取**仅该平台**的凭证列表——其 `## 凭证` 部分和，如果存在，`references/skill_info.yaml`（`required_credentials`、`credential_groups`、`optional_credentials`）。启动预检（`check_tao_launch_preflight.py`）读取相同的每个技能 `skill_info.yaml` 来执行凭证门；无凭证的平台（例如 Docker）可能仅提供文本，在这种情况下依赖其预检部分。

仅请求平台实际需要的凭证，以及从所选模型技能获取的模型特定凭证。不要在 SLURM、Kubernetes 或 Docker 上请求 Brev 凭证。不要在 Brev、Kubernetes 或 Docker 上请求 SLURM 凭证。仅在所选平台和数据集/结果 URI 需要 `s3://` 访问时才请求 S3 凭证。
凭证可能已存在于进程环境或用户批准的密钥环境文件中，例如 `~/.tao/secrets.env` 或 `~/.config/tao/.env`；仅在需要时源化这些文件，并**永远不要**打印、grep、cat、粘贴或记录其内容。仅验证变量存在。

对于初始启动输入，仅请求必需凭证和必需凭证组。将辅助工具的可选凭证/设置部分视为参考材料；除非其 `only_when` 条件适用、所选工作流无法在没有它们的情况下进行，或用户要求自定义该设置，否则**不要**请求这些值。

当辅助工具输出包括“必需凭证组”部分时，在继续之前从每个组满足一个凭证。使用辅助工具的描述和“如何获取它”文本解释每个请求的值。

对于 SLURM，面向用户的提示应首先请求 `SSH_KEY_PATH`。仅在用户表示他们已使用 SSH 代理时才提及 `SSH_AUTH_SOCK`。

## 依赖修复

如果必需的 CLI/库缺失，明确说明缺失的内容及其原因，然后在安装前询问。示例：

- S3 数据集或结果路径 -> 需要一个 S3 能力客户端，例如 `aws`。
- 本地 Docker 路径 -> 需要 Docker CLI 和配置的 Docker 网络。

在用户批准和安装后，重新运行相同的预检。在失败的检查和重新运行之间，**不要**创建运行者文件或启动作业。

## 数据集输入

以任何模式接受数据集输入：

- **数据集根模式**：用户提供训练/评估/校准根，模型技能按约定映射所需文件。Cosmos-RL 训练示例：`custom.train_dataset.annotation_path=<root>/annotations.json` 和 `custom.train_dataset.media_path=<root>`。
- **直接规范模式**：当注释、媒体存档、视频或图像文件夹位于不同位置时，用户在注释、媒体存档、视频或图像文件夹位于不同位置时提供确切规范键路径。直接保留这些键，例如
  `custom.train_dataset.annotation_path=<TRAIN_ANNOTATION_PATH>`
  和 `custom.train_dataset.media_path=<TRAIN_MEDIA_PATH>`。

询问与所选平台匹配的数据集示例：

- SLURM：用户提供的明确共享集群路径，并从分配的计算节点验证；技能没有特定站点的存储默认值。
- Brev、Kubernetes：通常 `s3://bucket/path/train` 和 `s3://bucket/path/eval`，除非平台配置挂载共享存储。
- 本地 Docker：Docker 主机可见的本地路径，例如 `/data/tao/<model>/train`，或计划容器挂载内可见的直接规范路径。
- 远程 Docker：在 `DOCKER_HOST` 命名的远程 Docker 主机上可见的绝对路径，而不是本地代理机器上的路径。

不要假设“数据集根”是唯一可接受的输入。当提供直接规范路径时，验证确切的规范路径，而不是追加默认文件名。

## 平台预检

在创建任何启动工件之前，运行所选平台的预检检查——优先使用打包的辅助工具 `scripts/check_tao_launch_preflight.py`（`--platform <p> --container-image <img> --path <label>=<path> ...`）。它验证凭证、客户端工具、平台/集群/对象存储访问、计算框架中的数据集路径、GPU/运行时健康和镜像架构匹配；将任何失败视为阻塞。**不要**为真实启动使用 `--skip-platform-access`。

有关每个平台的详细信息，请参阅 `references/platform-preflight.md`（SLURM SSH/密钥设置+资源默认值、docker/远程-docker GPU+绑定挂载检查、Brev/Kubernetes API+对象存储检查、注释内容字段检查和数据阶段）。

## 运行时和配置审查

在执行任何有副作用的启动之前，显示简洁的审查：

- 所选平台和确切容器镜像
- GPU id/数量和节点，包括因已占用而避免的任何 GPU
- 数据集根或直接规范路径，以及可用时的样本计数
- 与模板默认值不同的重要模型/工作流覆盖
- 预计运行时间和其背后的假设
- 监控间隔和聊天侧监控是否将保持连接
- 实现后端和选择理由，当模型暴露多个后端时

对于 AutoML，还显示算法、指标/方向、推荐预算、搜索参数、范围和生成的/默认推荐详细信息，如 `skills/applications/tao-run-automl/SKILL.md` 中所述。在启动前，如果用户提供了时间限制，标记任何超出限制的计划并提供具体的减少建议。

**永远不要**以“未启动任何内容”结束成功的启动审查。以一个直接的行动提示结束：`Ready to materialize the sealed plan and submit the job. Reply "launch", "go ahead", or "yes" to proceed.` 下一个明确的肯定聊天消息授权材料化、作业记录创建、提交和之前审查的监控模式；立即执行，无需另一个输入或确认回合。

## 结构化训练指标

当模型契约声明结构化状态路径或指标提取器时，与原生后端一起轮询它。调度器/容器完成本身不是成功的训练结果：需要模型的终止结构化成功记录，收集具体的检查点事件，并返回最终训练损失加上每个 epoch 验证完成损失。不要将验证心跳/批次指标或训练损失线提升为 epoch 验证损失。如果进程在其原生记录器存在之前失败，请调用打包的状态最终izer或报告真实的进程退出失败；仅将原始日志解析作为回退使用。
