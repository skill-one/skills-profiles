---
name: google-cloud-solution-guided-gke-ai-migration
description: 指导将现有的 AI 工作负载（Cloud Run、Gemini API、Gemini Enterprise Agent Platform）迁移到使用 gcloud 和 kubectl 的自托管 GKE 推理。当用户已有现有的 AI 推理工作负载（在 Cloud Run、Gemini API、Gemini Enterprise Agent Platform 或自定义 VM 上）并希望将其迁移到 GKE 的自托管推理，或在迁移过程中提出后续问题时使用（硬件规模调整、模型预置、清单生成、验证、流量切换）。不适用于没有现有工作负载需要迁移的新建 GKE 推理部署（请使用 gke-inference）。如果用户打算通过 Gemini Cloud Assist MCP 服务器自动化迁移，则不适用。
---

# 将 AI 工作负载迁移到 GKE Inference

本技能指导代理完成将现有 AI 推理工作负载（例如，从 Cloud Run、Gemini API、Gemini Enterprise Agent Platform 等平台）迁移到 Google Kubernetes Engine (GKE) 自托管推理的全流程。代理将扮演交互式架构师的角色，使用结构化的四阶段工作流程来发现需求、设计 Google Cloud 原生解决方案、使用 `gcloud` 和 `kubectl` 执行实施，并验证部署。

## Gemini Cloud Assist MCP 下行通道

本技能仅涵盖手动、架构师指导的迁移。自动化迁移是 Gemini Cloud Assist MCP 服务器的任务。按以下方式路由它们：

- **用户要求使用 Gemini Cloud Assist 或 MCP 自动化进行此迁移**（例如，“使用 Cloud Assist MCP 服务器来做这个”）：停止手动工作流程，并回复以下四个要点。
- **用户仅顺便提及 MCP，或明确拒绝**（例如，“没有 MCP，让我们手动做这个”）：继续手动工作流程。不要停止，也不要询问 MCP。
- **用户根本没有提及 MCP**：直接进入活动阶段。在您的第一个发现响应中，仅添加一句说明可以通过 Gemini Cloud Assist MCP 服务器存在自动化替代方案，并且用户可以随时切换。不要等待答案再开始发现。

**当为 MCP 请求停止时，您的响应必须包含这四个要点：**

1. **停止手动工作流程并明确范围**：说明 `google-cloud-solution-guided-gke-ai-migration` 严格用于手动、架构师指导的迁移，使用原生 CLI（`gcloud` 和 `kubectl`），并且此手动技能工作流程正在停止。
2. **解释 MCP 功能**：解释 Gemini Cloud Assist MCP 服务器协助进行自动化基础设施分析（`gemini_cloud_assist:ask_cloud_assist`）或直接 Google Cloud 资源变异（`gemini_cloud_assist:invoke_operation`）。
3. **链接到 MCP 文档**：提供有效的超链接到 [Gemini Cloud Assist MCP 文档](https://docs.cloud.google.com/cloud-assist/configure-mcp)。
4. **链接到 Intent to Infrastructure Codelab**：提供有效的超链接到 [Intent to Infrastructure Codelab](https://github.com/GoogleCloudPlatform/next-26-keynotes/tree/main/devkey/intent-to-infrastructure) 以获取有关设置 MCP 服务器的指导。

## 范围检查：新部署与迁移

**本技能专门用于将现有的 AI 工作负载（来自 Cloud Run、Gemini API、Agent Platform 或其他平台）迁移到 GKE。**

如果用户希望在 GKE 上从头开始部署新的 AI 模型服务器（并且没有现有的部署要迁移），**停止**并建议使用 **`gke-inference`** 技能。解释 `google-cloud-solution-guided-gke-ai-migration` 专注于迁移工作流程（发现现有的 Cloud Run/Agent Platform 配置、流量切换等），而 `gke-inference` 专门用于使用 AI Profiles 和黄金路径模板在 GKE 上部署新的 AI 模型服务器。

## 核心架构原则（“黄金路径”）
在设计解决方案时，始终默认使用最新的 GKE AI 最佳实践：

- **执行：**
  - **执行策略（谁运行命令）：**
    - **阶段 1（发现）**：在用户授予权限后，直接执行只读 `gcloud` 检查命令（`list`、`describe`）并总结结果。
    - **阶段 2-4**：将清单写入磁盘，然后向用户展示确切的 `gcloud` 和 `kubectl` 命令以供用户运行。除非用户明确要求您运行它们，否则不要执行变异命令（`apply`、`create`、`delete`、集群或 IAM 变更）；如果用户这样做，请执行它们并报告每个命令的实际输出。
    - **信息性和故障排除问题**：仅用 markdown 指导、清单和建议命令回答；不要执行任何操作。
  - 倾向于原始 Kubernetes 清单、原生 CLI（`gcloud` 用于基础设施、`kubectl` 用于工作负载）和有意见的模板。
  - 将 YAML 文件保存到用户的当前目录，并使用 `kubectl` 应用它们。
  - 只有在绝对必要时才编写临时脚本（例如，用于 VRAM 计算）。
- **节点配置：**
  - 利用 **自定义计算类（CCC）** 以最大化加速器可获取性（例如，动态选择 Spot 与按需或特定 GPU 配置）。
  - 使用 GKE 的托管 GPU 驱动程序安装。
  - 选择适当的节点拓扑：对于简单任务，使用静态池中的单个节点；对于较大任务，使用具有 LWS/CCC 的多个节点。
- **推理堆栈与版本控制：**
  - 默认使用 **vLLM**（`vllm/vllm-openai`）作为标准 LLM 服务引擎。如果从 Vertex AI 迁移，用户可以选择保留 Vertex AI Model Garden 图像（例如，`pytorch-vllm-serve`），这是允许的。
  - **显式入口点覆盖**：无论选择哪个图像，vLLM 部署必须显式设置 `command: ["python", "-m", "vllm.entrypoints.openai.api_server"]` 以绕过可能存在问题的入口点脚本（例如 Vertex AI 图像中的 `gcs_download_launcher.sh`），这些脚本在传递标准 vLLM 参数时崩溃。
  - 始终固定显式、稳定的 vLLM 图像标签，绝不使用 `:latest`。在设计时解决当前稳定版本（检查 vLLM 发布页面，或从 `gcloud container ai profiles manifests create` 输出中获取标签），并将其记录在 `migration-state.md` 中；不要重复使用从先前迁移或文档示例中记住的标签。
  - 通过 GKE Gateway API 暴露服务。默认使用区域内部应用负载均衡器（`gatewayClassName: gke-l7-rilb`），带有将 `/v1` 请求发送到 vLLM ClusterIP 服务（`{workload_name}-vllm-svc`）在端口 8000 的 HTTPRoute，基于 `assets/gke-inference-gateway.yaml.tmpl`。
  - 如果用户需要 LLM 感知的负载均衡（基于 KV 缓存利用率、队列深度或 LoRA 适配器放置进行路由），建议使用 GKE 推理网关作为升级：它需要 `InferencePool` 资源作为 HTTPRoute 后端而不是服务，并且仅在 `gke-l7-rilb` 和 `gke-l7-regional-external-managed` GatewayClasses 上受支持。在生成 InferencePool 清单之前，请获取 [关于 GKE 推理网关](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/about-gke-inference-gateway.md.txt) 的信息；不要从记忆中临时创建它们。
  - 对于多节点模型，使用 **LeaderWorkerSet (LWS)** 与 vLLM。
- **安全性与访问：**
  - 始终使用 **GKE Workload Identity** 进行 Google Cloud API 访问。
  - **受控模型密钥安全**：对于受控模型（例如 Llama 3、Gemma）需要 Hugging Face 令牌（`HF_TOKEN`）：
    - 绝不将字面令牌值写入 Deployment 或 Pod 规范中；使用 `env.valueFrom.secretKeyRef` 安全地引用密钥（例如，指向 `hf-secret`）。
    - 始终警告用户在纯文本提示或清单文件中暴露敏感 API 令牌的安全风险。
    - 绝不写入 Kubernetes `Secret` 清单到磁盘，也不要将其包含在模板中。相反，明确指示用户在应用任何其他清单之前通过 CLI 直接创建密钥：`kubectl create secret generic hf-secret --namespace={namespace} --from-literal=hf_api_token=<YOUR_HF_TOKEN>`，用户用自己的真实值替换。
    - 如果用户已经将令牌粘贴到对话中，将此令牌视为暴露：在您生成的每个命令和清单中使用 `<YOUR_HF_TOKEN>` 占位符，并建议用户在迁移完成后在 https://huggingface.co/settings/tokens 上撤销并重新发布令牌。
  - **端点暴露**：默认 Gateway 为内部类（`gke-l7-rilb`）。vLLM OpenAI 兼容端点没有内置认证；如果用户需要外部暴露，明确警告他们未经身份验证的外部监听器是 GPU 账单上的开放推理 API，并在生成外部暴露的 Gateway 清单之前要求明确的决定加上前端控制（IAP、认证 API 网关或严格的客户端允许列表）。
- **模型存储与冷启动：**
  - 将所选模型暂存到 Cloud Storage 桶中以节省重复下载成本。
  - **通过集群上的 Job 执行暂存**：向用户解释通过集群 Job 暂存权重可以避免将重型权重下载到他们的本地工作站，并避免每次容器重启时重新下载。始终将暂存清单保存为 `model-staging-job.yaml`，并指示用户运行 `kubectl apply -f model-staging-job.yaml`。
  - **基于源/目标的暂存逻辑：**
    - **源是 Hugging Face（gCS FUSE 或 Lustre 目标）**：使用暂存 Job 直接将权重下载到 PVC。
    - **源是 GCS（GCS FUSE 目标）**：暂存 Job 是 **可选的**。如果 PVC 通过 FUSE 直接挂载 GCS 桶，权重已经可访问，则不需要暂存步骤。
    - **源是 GCS（Lustre 目标）**：使用暂存 Job 将权重从源 GCS 桶复制到 Lustre PVC（例如，使用 `gcloud storage cp`）。
  - 倾向于大多数工作负载的 Cloud Storage 暂存通过 **Cloud Storage FUSE**，或对于超低延迟、PiB 规模需求使用 **Managed Lustre**。
  - 每个挂载 Cloud Storage FUSE 卷的 Pod 必须携带 Pod 注解 `gke-gcsfuse/volumes: "true"`（这会注入 FUSE 侧车），并且必须以绑定到具有模型桶 `roles/storage.objectUser` 的 Google 服务账户的 Kubernetes ServiceAccount 运行。缺少任何一个都会导致挂载失败或读取失败；在解决任何其他存储相关问题时，请检查这两个条件。
- **可观察性：**
  - 默认使用 **Google Cloud Managed Service for Prometheus** 并使用 DCGM 指标以获得深度 GPU 可见性。
- **自动扩展：**
  - 不要假设用户想要水平 Pod 自动扩展（HPA）；您必须在工作负载发现期间询问他们。
  - 如果拒绝 HPA，则省略所有自动扩展清单。
  - 如果需要 HPA，警告用户关于 **LLM 自动扩展陷阱**：标准的 CPU、内存和 GPU 内存利用率指标不可靠，因为 vLLM 为 KV 缓存预分配 VRAM，导致它们持续高度利用率。
  - 建议基于反映实际并发或队列深度（例如 `vllm:num_requests_waiting` 或批处理大小）的自定义服务器指标进行扩展。
  - 除非用户明确提到不同的指标，否则在清单中包含一个合理的默认值，即 **队列大小**。
  - 实现可以使用 GKE 自定义指标（Stackdriver 适配器）或 KEDA。

## 工作流程

解决方案设计和实施工作流程包括以下四个阶段：

- **阶段 1：发现**：通过 `gcloud` 检查现有基础设施并收集模型/流量需求。
- **阶段 2：解决方案设计**：计算 VRAM 需求，选择硬件/存储，并生成 Kubernetes 清单。
- **阶段 3：实施**：配置资源，通过临时 Pod 暂存模型权重，并使用 `kubectl` 应用工作负载清单。
- **阶段 4：验证和流量切换**：验证 Pod 健康和端点推理，然后提供流量迁移指导。

在**每个架构响应的开始**，打印一个简单的视觉进度指示线，以保持用户和模型对当前阶段的同步：

```markdown
**迁移进度**：[● 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]
```

*(更新 `●` 以标记当前活动阶段，例如，在阶段 2 时为 `[● 解决方案设计]`）。*

### 阶段路由规则
根据用户的提示上下文确定活动阶段：

如果当前目录中存在 `migration-state.md`，则在任何其他操作之前读取它，并从记录的阶段和记录的值继续；如果文件中缺少发现问题的值或被用户的提示矛盾，则仅重新询问发现问题。

- **阶段 1（发现）**：用于没有先前发现的新迁移请求。
- **阶段 2（解决方案设计）**：当提示表示发现已完成或要求架构设计 / YAML 清单生成时使用。
- **阶段 3（实施）**：当提示表示模型权重已暂存或直接要求部署步骤/命令时使用。进度指示器：`**Migration Progress:** [○ 发现] ➔ [○ 解决方案设计] ➔ [● 实施] ➔ [○ 验证]`。
- **阶段 4（验证）**：当提示表示工作负载正在运行或要求健康检查/测试步骤时使用。

### 阶段 1：发现

阶段 1 的目标是发现设计并构建目标 GKE 推理基础设施所需的所有工作负载规范。

**阶段 1 响应要求**：阶段 1 期间的每个响应都必须以视觉进度指示器开头：`**Migration Progress:** [● 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]`。

#### 发现清单（要识别的属性）
代理必须发现或确认以下 6 个核心属性类别：

- **源平台和服务配置：**
  - 源平台（Cloud Run、Gemini API、Gemini Enterprise Agent Platform、自定义 VM）。
  - 容器图像标签、环境变量、CPU/RAM 分配和密钥绑定。
- **模型规范：**
  - 模型名称和参数大小（例如 Gemma 2 9B、Llama 3 70B）。
  - 目标精度和量化容差（FP16/BF16 与 INT8/INT4 AWQ）。*必须在发现期间询问量化容差。*
  - 受控模型状态（是否需要 Hugging Face 令牌 `HF_TOKEN` 访问）。
  - **模型特定架构要求**：明确检查模型卡（例如，在 Hugging Face 上）或 `config.json` 以获取自定义配置要求。例如，确定架构是否需要 `--trust-remote-code`（如 Qwen 模型）、特定的 rope 缩放参数或其他自定义标志。
- **目标 GKE 和硬件基础设施：**
  - 目标 GKE 集群名称和区域（或确认创建新集群）。
  - 加速器偏好（L4、A100、H100、TPU v5e）和配置模型（Spot/CCC 与按需）。
  - 请求的 GPU/TPU 的区域配额可用性。
- **模型存储和暂存：**
  - 模型权重的当前位置（GCS 桶、Hugging Face Hub、外部 URL）。
  - 偏好的存储集成（Cloud Storage FUSE 与 Managed Lustre）。
- **流量配置和负载均衡：**
  - 预期的流量量、并发性和请求模式（尖峰与一致基线）。
  - 负载均衡需求（GKE 推理网关、标准 Ingress/Service）。
  - **自动扩展要求**：询问用户是否需要水平 Pod 自动扩展（HPA）。不要假设他们需要。如果他们需要，请确定目标指标（默认为队列大小）并讨论 LLM 自动扩展陷阱。

- **模型等效性（仅限 Gemini API / Agent Platform 源）：**
  - 使用哪些 Gemini 模型和 API 功能（函数调用、系统指令、上下文长度、多模态输入）。
  - 将其替换为哪个开源权重模型，以及用户计划如何在切换前将输出质量与当前系统进行评估。
  - 客户端影响：vLLM 端点是 OpenAI 兼容的，不是 Gemini-API 兼容的；识别必须更改的客户端代码和 SDK 调用。

#### 发现执行（自动化和交互式）

- **先请求基础设施访问权限和许可：** 在执行任何发现命令之前，您必须通过 CLI 命令（例如 `gcloud run services list` 或 `gcloud run services describe`）明确请求用户许可，以检查现有的环境资源。
- **经批准后进行检查：** 一旦用户授予许可，执行 `gcloud` CLI 命令，检查环境变量，并审查本地工作区文件以自动填充清单项目：
  - **Cloud Run 工作负载：** 运行 `gcloud run services list --format="table(metadata.name,status.url,status.latestReadyRevisionName)"` 来枚举服务，然后运行 `gcloud run services describe {service_name} --format="yaml(spec.template.spec.containers,spec.template.metadata.annotations,spec.template.spec.serviceAccountName,spec.template.spec.containerConcurrency)"` 来仅提取容器镜像、环境变量、资源限制、并发和密钥绑定。在所有发现命令中优先使用 `--format` 过滤器；切勿将未过滤的完整资源描述拉入对话中。
  - **现有的 GKE 集群：** 运行 `gcloud container clusters list` 和 `gcloud container clusters describe {cluster_name}` 来检查活动集群配置、Workload Identity 设置和可用的加速器池。
  - **Vertex AI / 存储：** 运行 `gcloud ai endpoints list` 或 `gcloud storage buckets list` 来定位模型工件和存储桶。
  - **工作区与环境：** 检查活动工作区目录中的本地配置文件或环境变量。
- **总结、查询缺失项并确认：** 呈现所有发现配置数据的综合摘要，并提示用户任何剩余缺失的属性。如果任何清单项目未解决或含糊不清，请在进入阶段 2 之前获得明确的用户确认。如果每个清单项目都无含糊地解决，您可以在同一响应中呈现发现摘要和阶段 2 的解决方案设计，在单个合并的批准门下；设计批准然后涵盖两者。
- **持久化发现状态：** 在用户确认发现摘要后，将其写入当前目录中的 `migration-state.md`：每个清单类别一个部分，包含确认的值，以及最后一行 `Current phase: <phase name>`。每次工作流推进阶段时，更新 `Current phase:` 行。

### 阶段 2：解决方案设计

根据发现阶段，设计完成迁移所需的架构和清单。

**阶段 2 响应要求：** 阶段 2 期间的每个响应都必须以视觉进度指示器开头：`**迁移进度：** [○ 发现] ➔ [● 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]`。

**即时上下文加载：** 在评估以下特定架构选择时（例如，存储选项、负载均衡或自动扩展），按需获取并阅读 **支持链接** 部分的相关参考文档链接。

1. **映射组件和替代方案：** 对于每个主要组件（例如，负载均衡、自动扩展、单节点与多节点），呈现您推荐的“黄金路径”选项以及替代方案。如果用户请求 HPA，请确保设计解决 LLM 自动扩展陷阱，并建议自定义指标（默认为队列大小）。
2. **加速器选择：** 参考
    [GPU 平台](https://docs.cloud.google.com/compute/docs/gpus.md.txt) 或
    [在 GKE 中规划 TPU 配置](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/plan-tpus.md.txt) 来推荐最适合目标模型的加速器。
    *(注意：`assets/` 中的清单模板仅支持 GPU。如果用户选择 Cloud TPU，请明确说明，并基于 GKE TPU 服务文档而不是此技能中的模板来创建服务清单。)*
3. **存储选择：** 参考 [GCP AI 存储选项](https://docs.cloud.google.com/ai-hypercomputer/docs/storage.md.txt) 来推荐最适合模型暂存和服务的存储解决方案。
4. **硬件与 VRAM 尺寸：** 使用以下确定性 VRAM 尺寸公式，根据参数、上下文窗口和量化准确计算 VRAM，映射到适当的 GPU（L4、A100、H100）。
5. **集群和节点设置：** 设计适合该作业的集群。使用适当的尺寸节点为任务添加自定义计算类（CCC）。如有必要，设计 Workload Identity。vLLM 部署必须选择带有 `nodeSelector: cloud.google.com/compute-class: {compute_class_name}` 的节点，以便工作负载实际上通过 ComputeClass 安排。如果用户拒绝 CCC 并只想使用按需节点，请将此选择器替换为 `cloud.google.com/gke-accelerator: {accelerator_type}`，并完全跳过 `ccc-profile.yaml`；不要应用未引用 ComputeClass 的 ComputeClass。
6. **模型暂存设计：** 根据模型权重的源位置和目标存储解决方案确定是否需要暂存作业。如果源是 Hugging Face，或者如果目标是 Lustre 且源是 GCS，请计划一个作业来下载/复制权重。如果源是 GCS 且目标是 GCS FUSE，请跳过暂存。计划使用 Cloud Storage FUSE 或 Lustre CSI 将此存储挂载到工作负载。
7. **起草解决方案架构和清单：** 读取 `assets/` 中的清单模板（`assets/vllm-deployment.yaml.tmpl`、`assets/ccc-profile.yaml.tmpl`、`assets/gke-inference-gateway.yaml.tmpl`、`assets/storage-config.yaml.tmpl` 和 `assets/model-staging-job.yaml.tmpl`），替换在阶段 1 中发现的参数，并将生成的 YAML 清单（`vllm-deployment.yaml`、`ccc-profile.yaml`、`gke-inference-gateway.yaml`、`storage-config.yaml`、`model-staging-job.yaml`）保存到当前目录中的磁盘。在创建 `vllm-deployment.yaml` 时，将阶段 1 中发现的任何必需的模型特定架构标志（例如，`--trust-remote-code`）显式注入到容器 `args` 数组中。在创建 `gke-inference-gateway.yaml` 时，基于 `assets/gke-inference-gateway.yaml.tmpl`：除非用户明确选择了外部暴露或基于 InferencePool 的 GKE Inference Gateway，否则使用 `gatewayClassName: gke-l7-rilb` 作为 Gateway 资源；在 HTTPRoute 资源中将 `/v1` 流量路由到 vLLM ClusterIP 服务（`{workload_name}-vllm-svc` 在端口 8000 上）。如果使用除 `gcsfuse-csi` 以外的存储类（例如，`lustre-csi`），请从 `storage-config.yaml` 中删除 `gcsfuse.cloud.google.com` 注释。
8. **请求审查和迭代：** 向用户展示生成的解决方案架构和图表，并请求他们的反馈。在用户批准设计之前，迭代设计，然后进入阶段 3。

#### 确定性 VRAM 尺寸公式

要准确计算模型服务/推理的 VRAM 需求，请使用以下确定性公式：

**硬件与尺寸推荐要求：** 在计算 VRAM 尺寸或推荐硬件时：

- 使用下面的公式明确解释 VRAM 计算（参数大小、KV 缓存、20% 安全边际）。
- 推荐特定的加速器类型（例如，带有 24GB VRAM 的 NVIDIA L4 用于 8B 模型在 FP16/BF16 中）。
- 推荐使用 **自定义计算类（CCC**）以最大化加速器可获取性。
- 在发现阶段询问或确认用户的 **量化容忍度**（FP16/BF16 与 INT8/INT4）。

$$VRAM_{\text{total}} = \left( \frac{\text{Parameters} \times 2}{\text{Quantization}} + KV\_Cache\_Overhead \right) \times 1.2$$

其中：

*   **Parameters**：模型大小，以十亿个参数计（例如，`8` 对于 8B，`70` 对于 70B）。
*   **Quantization**：基于目标精度相对于 16 位的除数（FP16/BF16）：
    *   `1` 对于 16 位（FP16 / BF16，每个参数 2 字节）
    *   `2` 对于 8 位（FP8 / INT8，每个参数 1 字节）
    *   `4` 对于 4 位（INT4 / AWQ / GPTQ，每个参数 0.5 字节）
*   **$KV\_Cache\_Overhead$**：在生成期间保留的用于键值缓存的内存（GB）：
    $$KV\_Cache\_Overhead \,(GB) = \frac{2 \times n_{\text{layers}} \times n_{\text{kv\_heads}} \times d_{\text{head}} \times \text{Context Length} \times \text{Batch Size} \times \text{Precision Bytes}}{10^9}$$
    *(经验法则：如果模型层架构细节未知，估计 $KV\_Cache\_Overhead \approx 0.2 \times \text{模型权重内存}$)。*
*   **`1.2` 乘数**：20% 安全边际，用于 CUDA 上下文、激活内存和服务引擎开销。

在映射结果到加速器时，比较 $VRAM_{\text{total}}$ 与卡的完整内存（例如，L4 的 24 GB），而不是与 `--gpu-memory-utilization` 折扣后的内存进行比较。1.2 乘数和 vLLM 的利用率上限为相同的开销保留空间；应用两者会重复计算边际并将尺寸推高一个加速器级别。

### 阶段 3：实施

根据执行策略执行经批准的设计：生成以下命令，并将它们交给用户，或者如果用户要求您运行它们，则执行它们并报告输出。

1. **识别部署先决条件：** 确保计费、API 和 IAM 权限已就绪。
2. **基础设施配置：** 提供 `gcloud` 命令来配置存储和集群先决条件（例如，启用 Cloud Storage FUSE CSI 驱动程序）和配置 Workload Identity IAM 绑定。**Gateway API 预检查：** 明确指示用户验证其集群上是否启用了 Gateway API。建议在用户尝试应用路由清单之前运行 `gcloud container clusters update <CLUSTER_NAME> --gateway-api=standard`，以防止 CRD 未找到错误。
3. **存储配置：** 创建必要的存储资源（Cloud Storage 桶或托管 Lustre 文件系统）。
4. **模型暂存：** 应用基于阶段 2 设计的条件逻辑。
    - **跳过：** 如果模型已在 GCS 并使用 GCS FUSE，请跳转到步骤 5。
    - **Hugging Face 源：** 如果使用受限制的模型（例如，Llama 3、Gemma），请明确指示用户在应用任何作业或部署之前在本地运行 `kubectl create secret generic hf-secret ...` 命令（见受限制模型密钥安全规则）。一旦密钥创建完成，指示用户运行 `kubectl apply -f model-staging-job.yaml`。
    - **GCS 到 Lustre 源：** 指示用户运行 `kubectl apply -f model-staging-job.yaml`（应配置为使用 `gcloud storage cp` 或类似命令）。
    - **完成门：** 对于任何活动的暂存作业，使用 `kubectl wait --for=condition=complete job/{workload_name}-model-staging --timeout=90m`（根据模型大小调整超时）来门控完成（如果作业失败，请在重试之前使用 `kubectl logs job/{workload_name}-model-staging` 检查它）。解释通过集群作业暂存避免了将大量权重下载到用户的工位，并避免了每次容器重启时重新下载。
5. **工作负载部署：** 提供 `kubectl apply` 命令来部署存储配置（`kubectl apply -f storage-config.yaml`）、计算类（`kubectl apply -f ccc-profile.yaml`）、vLLM 部署（`kubectl apply -f vllm-deployment.yaml`）和 Inference Gateway（`kubectl apply -f gke-inference-gateway.yaml`）。确保 vLLM 部署规范将暂存的模型权重从 PVC 挂载到 `/models`。确保如果为受限制的模型创建了密钥，则它在部署清单中正确引用。将 vLLM 的 `--model` 标志设置为暂存的本地路径（`/models/{model_name}`），而不是 Hugging Face 仓库 ID；仓库 ID 会使 vLLM 在每个 Pod 启动时重新下载完整权重，并默默地击败暂存步骤。保留模型的公共名称供 API 客户端使用，使用 `--served-model-name={model_id}`。
6. **验证发布：** 使用 `kubectl rollout status deployment/{workload_name}-vllm --timeout=30m` 和 `kubectl get pods -l app={workload_name}-vllm -o wide` 确认成功。如果发布失败或超时，请直接进入故障排除指南并报告观察到的错误；当命令输出已经回答了它时，不要询问用户部署是否成功。仅当集群无法验证结果时才询问用户（例如，响应质量是否与源系统匹配）。

### 阶段 4：验证和切换

验证已部署的基础设施是否满足工作负载的要求，并提供流量迁移说明。

**阶段 4 响应要求：** 阶段 4 期间的每个响应都必须以视觉进度指示器开头：`**迁移进度：** [○ 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [● 验证]`。

1. **健康检查：** 推荐显式健康检查命令来验证 Pod、节点和 Gateway 状态（`kubectl get pods`、`kubectl get nodes` 和 `kubectl get gateway`）。
2. **测试推理：** 验证服务正在提供模型。提供一个 `kubectl port-forward` 命令（`kubectl port-forward svc/{workload_name}-vllm-svc 8000:8000`）和一个示例 `curl` 请求到 `/v1/chat/completions` 来测试端点推理。如果适用，与先前的基础设施比较响应。
3. **流量切换指南：** 不要尝试自动实施流量迁移。相反：
    * 提供一个内部 GKE 端点，该端点已准备好接收流量。
    * 根据相关代码库（如果有）提供如何迁移流量的建议。
    * 建议使用标准 GKE 发布（例如，更新现有的部署清单以指向新服务），而无需复杂的金丝雀测试或蓝绿发布。
    * 仅当用户明确要求时，才提供更高级的流量迁移选项。
4. **回滚准备：** 在任何流量移动之前，确认源服务保持部署（缩小规模可以，删除不行），直到用户选择的 GKE 端点为生产流量服务了一段时间。提供单个命令或配置更改以将流量恢复到源。只有在用户宣布迁移稳定后，才提供删除源服务的命令。
5. **编制验证报告并请求最终批准：** 编制一个验证报告，总结所有健康检查结果和推理测试结果。您必须明确请求用户批准以最终确定并完成迁移工作流。

### 故障排除指南

当用户报告 Pod 创建但推理端点未响应的情况（或请求故障排除帮助）：

1. 推荐特定的诊断命令：`kubectl logs {pod_name}`（检查容器启动日志）和 `kubectl describe pod {pod_name}`（检查 Pod 初始化状态）。
2. 建议验证目标区域的 Google Cloud 加速器配额（GPU/TPU）以确保可以配置所需资源。
3. **检查即时编译 / 启动延迟：** 如果 `curl` 返回 `Connection refused` 但 Pod 处于 `Running` 状态，服务引擎（例如，vLLM）可能仍在执行 JIT 编译（例如，Triton PTX 或 Torch Inductor）或捕获 CUDA 图。这可能需要模型权重加载后的几分钟。建议用户检查 `kubectl logs {pod_name}` 并明确等待 `Uvicorn running on http://0.0.0.0:8000`（或等效）日志消息，然后再假设存在网络问题。
4. 建议检查 GKE Workload Identity 绑定、PVC 挂载健康（Cloud Storage FUSE）和 GKE Inference Gateway 监听器配置。

## 支持链接

按需使用这些参考链接作为设计选择的基础，回答用户问题，并生成实施清单：

*   [GPU 平台](https://docs.cloud.google.com/compute/docs/gpus.md.txt)
*   [在 GKE 中规划 TPU 配置](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/plan-tpus.md.txt)
*   [Gemini 云助手 MCP 文档](https://docs.cloud.google.com/cloud-assist/configure-mcp)
*   [关于在 GKE 上进行 AI/ML 模型推理](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/inference.md.txt)
*   [为 GKE 上的 AI/ML 模型推理选择负载均衡策略](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/choose-lb-strategy.md.txt)
*   [在 Google Kubernetes Engine 上使用 GPU 自动扩展大型语言模型推理工作负载的最佳实践](https://docs.cloud.google.com/kubernetes-engine/docs/best-practices/machine-learning/inference/autoscaling.md.txt)
*   [Google Cloud AI 存储选项](https://docs.cloud.google.com/ai-hypercomputer/docs/storage.md.txt)
*   [使用 Cloud Storage FUSE 优化 AI/ML 工作负载](https://docs.cloud.google.com/architecture/optimize-ai-ml-workloads-cloud-storage-fuse.md.txt)
*   [使用 Managed Lustre 优化 AI/ML 工作负载](https://docs.cloud.google.com/architecture/optimize-ai-ml-workloads-managed-lustre.md.txt)
