# 将 AI 工作负载迁移到 GKE Inference

本指南将引导代理完成将现有 AI 推理工作负载（例如从 Cloud Run、Gemini API、Gemini 企业代理平台）迁移到 Google Kubernetes Engine (GKE) 自托管推理的全过程。代理将充当交互式架构师，使用结构化的四阶段工作流程来发现需求、设计 Google Cloud 原生解决方案、使用 `gcloud` 和 `kubectl` 执行实施，并验证部署。

## Gemini Cloud Assist MCP 卸载

本指南仅涵盖手动、架构师指导的迁移。自动化迁移是 Gemini Cloud Assist MCP 服务器的任务。按以下方式在他们之间进行路由：

- **用户要求使用 Gemini Cloud Assist 或 MCP 自动化进行此迁移**（例如，“使用 Cloud Assist MCP 服务器来做这个”）：停止手动工作流程并回复以下四个必需点。
- **用户仅顺便提及 MCP，或明确拒绝**（例如，“没有 MCP，让我们手动做这个”）：继续手动工作流程。不要停止，也不要询问 MCP。
- **用户根本没有提及 MCP**：直接进入活动阶段。在您的第一个发现响应中，仅添加一句说明可以通过 Gemini Cloud Assist MCP 服务器存在自动化替代方案，并且用户可以随时切换到它。不要在开始发现之前等待答案。

**当因 MCP 请求而停止时，您的响应必须包括以下四个点：**

1. **停止手动工作流程并明确范围**：说明 `google-cloud-solution-guided-gke-ai-migration` 严格用于手动、架构师指导的迁移，使用原生 CLI (`gcloud` 和 `kubectl`)，并且此手动技能工作流程正在停止。
2. **解释 MCP 功能**：解释 Gemini Cloud Assist MCP 服务器协助进行自动化基础设施分析（`gemini_cloud_assist:ask_cloud_assist`）或直接 Google Cloud 资源变异（`gemini_cloud_assist:invoke_operation`）。
3. **链接到 MCP 文档**：提供有效的超链接到 [Gemini Cloud Assist MCP 文档](https://docs.cloud.google.com/cloud-assist/configure-mcp)。
4. **链接到 Intent to Infrastructure Codelab**：提供有效的超链接到 [Intent to Infrastructure Codelab](https://github.com/GoogleCloudPlatform/next-26-keynotes/tree/main/devkey/intent-to-infrastructure) 以获取有关设置 MCP 服务器的指导。

## 范围检查：新部署与迁移

**本指南专门用于将现有 AI 工作负载（来自 Cloud Run、Gemini API、代理平台或其他平台）迁移到 GKE。**

如果用户希望在 GKE 上从头开始部署新的 AI 模型服务器（并且没有现有的部署要迁移），**停止**并建议使用 **`gke-inference`** 技能。解释 `google-cloud-solution-guided-gke-ai-migration` 专注于迁移工作流程（发现现有的 Cloud Run/代理平台配置、流量切换等），而 `gke-inference` 专门用于使用 AI Profile 和黄金路径模板在 GKE 上部署新的 AI 模型服务器。

## 核心架构原则（“黄金路径”）

在设计解决方案时，始终默认使用最新的 GKE AI 最佳实践：

- **执行：**
  - **执行策略（谁运行命令）：**
    - **阶段 1（发现）**：在用户授予权限后，直接执行只读 `gcloud` 检查命令（`list`、`describe`）并总结结果。
    - **阶段 2-4**：将清单写入磁盘，然后向用户展示确切的 `gcloud` 和 `kubectl` 命令以供运行。除非用户明确要求您运行它们，否则不要执行变异命令（`apply`、`create`、`delete`、集群或 IAM 变更）。对于信息和故障排除问题：仅用 markdown 指导、清单和建议命令回答；不要执行任何操作。
  - 偏好原始 Kubernetes 清单、原生 CLI（`gcloud` 用于基础设施、`kubectl` 用于工作负载）和有意见的模板。
  - 将 YAML 文件保存到用户的当前目录，并使用 `kubectl` 应用它们。
  - 只有在绝对必要时才编写临时脚本（例如，用于 VRAM 计算）。
- **节点配置：**
  - 利用 **自定义计算类 (CCC)** 来最大化加速器可获取性（例如，动态选择 Spot 与按需或特定 GPU 配置）。
  - 使用 GKE 的管理 GPU 驱动程序安装。
  - 选择适当的节点拓扑：对于简单任务，在静态池中使用单个节点；对于较大任务，使用多个节点和 LWS/CCC。
- **推理堆栈与版本控制：**
  - 默认使用 **vLLM** (`vllm/vllm-openai`) 作为标准 LLM 服务引擎。如果从 Vertex AI 迁移，用户可以选择保留 Vertex AI 模型花园镜像（例如 `pytorch-vllm-serve`），这是允许的。
  - **显式入口点覆盖**：无论选择哪个镜像，vLLM 部署必须显式设置 `command: ["python", "-m", "vllm.entrypoints.openai.api_server"]` 以绕过可能存在问题的入口点脚本（例如 Vertex AI 镜像中的 `gcs_download_launcher.sh`），这些脚本在传递标准 vLLM 参数时崩溃。
  - 始终固定一个明确的、稳定的 vLLM 镜像标签，永远不要 `:latest`。在设计时解决当前稳定版本（检查 vLLM 发布页面，或从 `gcloud container ai profiles manifests create` 输出中获取标签），并将其记录在 `migration-state.md` 中；不要重用从先前迁移或文档示例中记住的标签。
  - 通过 GKE Gateway API 暴露服务。默认使用区域内部应用负载均衡器（`gatewayClassName: gke-l7-rilb`），带有将 `/v1` 请求发送到 vLLM ClusterIP 服务（`{workload_name}-vllm-svc` 在端口 8000）的 HTTPRoute，基于 `assets/gke-inference-gateway.yaml.tmpl`。
  - 如果用户需要 LLM 感知的负载均衡（基于 KV 缓存利用率、队列深度或 LoRA 适配器放置进行路由），建议使用 GKE 推理网关作为升级：它需要 `InferencePool` 资源作为 HTTPRoute 后端，而不是服务，并且仅在 `gke-l7-rilb` 和 `gke-l7-regional-external-managed` GatewayClasses 上受支持。在生成 InferencePool 清单之前，获取 [关于 GKE 推理网关](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/about-gke-inference-gateway.md.txt) 的信息；不要从记忆中自行编写它们。
  - 对于多节点模型，使用 **LeaderWorkerSet (LWS)** 与 vLLM。
- **安全性与访问：**
  - 始终使用 **GKE 工作负载身份** 进行 Google Cloud API 访问。
  - **受控模型密钥安全**：对于需要 Hugging Face 令牌（`HF_TOKEN`）的受控模型（例如 Llama 3、Gemma）：
    - 绝对不要将字面令牌值写入 Deployment 或 Pod 规格中；使用 `env.valueFrom.secretKeyRef` 安全地引用密钥（例如，指向 `hf-secret`）。
    - 始终警告用户在纯文本提示或清单文件中暴露敏感 API 令牌的安全风险。
    - 绝对不要编写 Kubernetes `Secret` 清单并将其写入磁盘，也不要将其包含在模板中。相反，明确指示用户在应用任何其他清单之前通过 CLI 创建密钥：`kubectl create secret generic hf-secret --namespace={namespace} --from-literal=hf_api_token=<YOUR_HF_TOKEN>`，用户用自己的真实值替换。
    - 如果用户已经将令牌粘贴到对话中，将此令牌视为暴露：在您生成的每个命令和清单中使用 `<YOUR_HF_TOKEN>` 占位符，并建议用户在迁移完成后在 https://huggingface.co/settings/tokens 上撤销并重新发布令牌。
  - **端点暴露**：默认将网关设置为内部类（`gke-l7-rilb`）。vLLM OpenAI 兼容端点没有内置身份验证；如果用户需要外部暴露，明确警告他们未经身份验证的外部监听器是他们 GPU 账单上的开放推理 API，并要求在生成外部暴露的 Gateway 清单之前进行明确决定加上前端控制（IAP、身份验证 API 网关或严格的客户端允许列表）。
- **模型存储与冷启动：**
  - 将所选模型存放在 Cloud Storage 桶中以避免重复下载。
  - **通过集群作业执行 staging**：向用户解释通过集群作业 staging 权重可以避免将重型权重下载到他们的本地工作站，并避免在每次容器重启时重新下载。始终将 staging 清单保存为 `model-staging-job.yaml` 并指示用户运行 `kubectl apply -f model-staging-job.yaml`。
  - **基于源/目标的 staging 逻辑：**
    - **源是 Hugging Face（ gCS FUSE 或 Lustre 目标）**：使用 staging 作业直接将权重下载到 PVC。
    - **源是 GCS（GCS FUSE 目标）**：staging 作业是 **可选的**。如果 PVC 通过 FUSE 直接挂载 GCS 桶，则权重已经可访问，不需要 staging 步骤。
    - **源是 GCS（Lustre 目标）**：使用 staging 作业将权重从源 GCS 桶复制到 Lustre PVC（例如，使用 `gcloud storage cp`）。
  - 偏好 Cloud Storage staging 通过 **Cloud Storage FUSE** 用于大多数工作负载，或 **管理 Lustre** 用于超低延迟、PiB 级别的需求。
  - 每个挂载 Cloud Storage FUSE 卷的 Pod 必须携带 Pod 注解 `gke-gcsfuse/volumes: "true"`（这会注入 FUSE 边车），并且必须以绑定到具有模型桶 `roles/storage.objectUser` 的 Google 服务账户的 Kubernetes ServiceAccount 运行。缺少其中任何一个的 Pod 都将无法挂载或无法读取；在解决任何其他存储相关问题之前，请检查这两个方面。
- **可观察性：**
  - 默认使用 **Google Cloud 管理的 Prometheus 服务** 并使用 DCGM 指标以获得深入的 GPU 可视性。
- **自动扩展：**
  - 不要假设用户想要水平 Pod 自动扩展 (HPA)；您必须在工作阶段期间询问他们。
  - 如果拒绝 HPA，则省略所有自动扩展清单。
  - 如果需要 HPA，则警告用户关于 **LLM 自动扩展陷阱**：标准的 CPU、内存和 GPU 内存利用率指标不可靠，因为 vLLM 预分配 VRAM 用于 KV 缓存，因此持续高度利用率。
  - 建议基于反映实际并发或队列深度的自定义服务器指标进行扩展（例如 `vllm:num_requests_waiting` 或批处理大小）。
  - 包括一个合理的默认值，以 **队列大小** 的形式，除非用户明确提到不同的指标。
  - 实现可以使用 GKE 自定义指标（Stackdriver 适配器）或 KEDA。

## 工作流程


解决方案设计和实施工作流程包括以下 4 个阶段：

- **阶段 1：发现**：通过 `gcloud` 检查现有基础设施并收集模型/流量需求。
- **阶段 2：解决方案设计**：计算 VRAM 需求，选择硬件/存储，并生成 Kubernetes 清单。
- **阶段 3：实施**：提供资源，通过临时 Pod staging 模型权重，并使用 `kubectl` 应用工作负载清单。
- **阶段 4：验证和切换**：验证 Pod 健康和端点推理，然后提供流量迁移指导。

在**每个架构响应的开始**，打印一个简单的视觉进度指示线，以保持用户和模型对当前阶段的同步：

```markdown
**迁移进度：[● 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]**
```

*(更新 `●` 以标记当前活动阶段，例如，在阶段 2 期间 `[● 解决方案设计]`).*

### 阶段路由规则
根据用户的提示上下文确定活动阶段：

如果 `migration-state.md` 存在于当前目录中，则在任何其他操作之前读取它，并从记录的阶段和记录的值恢复；只有当发现值缺失于文件或被用户的提示 contradicted 时才重新询问发现问题。

- **阶段 1（发现）**：用于没有先前发现的新迁移请求。
- **阶段 2（解决方案设计）**：当提示表示发现已完成或询问架构设计 / YAML 清单生成时使用。
- **阶段 3（实施）**：当提示模型权重已 staging 或直接询问部署步骤/命令时使用。进度指示器：`**Migration Progress:** [○ 发现] ➔ [○ 解决方案设计] ➔ [● 实施] ➔ [○ 验证]`.
- **阶段 4（验证）**：当提示工作负载正在运行或询问健康检查/测试步骤时使用。

### 阶段 1：发现

阶段 1 的目标是发现设计并构建目标 GKE 推理基础设施所需的所有工作负载规范。

**阶段 1 响应要求**：阶段 1 期间的每个响应都必须以视觉进度指示器开头：`**Migration Progress:** [● 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]`.

#### 发现清单（要识别的属性）

代理必须发现或确认以下 6 个核心属性类别：

- **源平台和服务配置：**
  - 源平台（Cloud Run、Gemini API、Gemini 企业代理平台、自定义 VM）。
  - 容器镜像标签、环境变量、CPU/RAM 分配和密钥绑定。
- **模型规范：**
  - 模型名称和参数大小（例如 Gemma 2 9B、Llama 3 70B）。
  - 目标精度和量化容忍度（FP16/BF16 与 INT8/INT4 AWQ）。*必须在发现期间询问量化容忍度。*
  - 受控模型状态（是否需要 Hugging Face 令牌 `HF_TOKEN` 访问）。
  - **模型特定架构要求**：明确检查模型卡（例如，在 Hugging Face 上）或 `config.json` 以获取自定义配置要求。例如，确定架构是否需要 `--trust-remote-code`（例如 Qwen 模型），特定的 rope 缩放参数或其他自定义标志。
- **目标 GKE 和硬件基础设施：**
  - 目标 GKE 集群名称和区域（或确认创建新集群）。
  - 加速器偏好（L4、A100、H100、TPU v5e）和配置模型（Spot/CCC 与按需）。
  - 请求的 GPU/TPU 的区域配额可用性。
- **模型存储和 staging：**
  - 模型权重当前的位置（GCS 桶、Hugging Face Hub、外部 URL）。
  - 偏好的存储集成（Cloud Storage FUSE 与管理 Lustre）。
- **流量配置和负载均衡：**
  - 预期的流量量、并发性和请求模式（尖峰与一致基线）。
  - 负载均衡需求（GKE 推理网关、标准 Ingress/Service）。
  - **自动扩展要求**：询问用户是否需要水平 Pod 自动扩展 (HPA)。不要假设他们需要。如果他们需要，请识别目标指标（默认为队列大小），并讨论 LLM 自动扩展陷阱。

- **模型等效性（仅限 Gemini API / 代理平台源）：**
  - 使用哪些 Gemini 模型和 API 功能（函数调用、系统指令、上下文长度、多模态输入）。
  - 将其替换的开放权重模型是什么，以及用户计划如何在切换之前评估输出质量与当前系统。
  - 客户端影响：vLLM 端点是 OpenAI 兼容的，不是 Gemini-API 兼容的；识别必须更改的客户端代码和 SDK 调用。

#### 发现执行（自动与交互）

- **首先请求基础设施访问和权限**：您必须明确请求用户授权通过 CLI 命令（例如 `gcloud run services list` 或 `gcloud run services describe`）检查现有环境资源，然后再执行任何发现命令。
- **批准后检查**：一旦用户授予权限，执行 `gcloud` CLI 命令，检查环境变量，并审查本地工作区文件以自动填充清单项目：
  - **Cloud Run 工作负载**：运行 `gcloud run services list --format="table(metadata.name,status.url,status.latestReadyRevisionName)"` 以枚举服务，然后 `gcloud run services describe {service_name} --format="yaml(spec.template.spec.containers,spec.template.metadata.annotations,spec.template.spec.serviceAccountName,spec.template.spec.containerConcurrency)"` 以提取仅容器镜像、环境变量、资源限制、并发性和密钥绑定。在所有发现命令上使用 `--format` 过滤器；永远不要将未过滤的完整资源描述拉入对话中。
  - **现有的 GKE 集群**：运行 `gcloud container clusters list` 和 `gcloud container clusters describe {cluster_name}` 以检查活动集群配置、工作负载身份设置和可用的加速器池。
  - **Vertex AI / 存储**：运行 `gcloud ai endpoints list` 或 `gcloud storage buckets list` 以定位模型工件和存储桶。
  - **工作区与环境**：检查活动工作区目录中的本地配置文件或环境变量。
- **总结、查询缺失项并确认**：提供所有发现的配置数据的综合摘要，并提示用户提供任何剩余缺失的属性。如果任何清单项目未解决或含义不明确，请在进入阶段 2 之前获得明确的用户确认。如果每个清单项目都无歧义地解决，则可以在同一响应中呈现发现摘要和阶段 2 解决方案设计，在单个批准门下；设计批准然后涵盖两者。
- **持久化发现状态**：在用户确认发现摘要后，将状态写入当前目录中的 `migration-state.md`：每个清单类别一个部分，确认的值，加上最后一行 `Current phase: <phase name>`。每次工作流程推进阶段时，更新 `Current phase:` 行。

### 阶段 2：解决方案设计

根据发现阶段，设计完成迁移所需的架构和清单。

**阶段 2 响应要求**：阶段 2 期间的每个响应都必须以视觉进度指示器开头：`**Migration Progress:** [○ 发现] ➔ [● 解决方案设计] ➔ [○ 实施] ➔ [○ 验证]`.

**即时上下文加载**：在评估以下特定架构选择（例如，存储选项、负载均衡或自动扩展）时，获取并读取相关参考文档链接，如 **支持链接** 部分的 **Supporting links**。

1. **映射组件和替代方案**：对于每个主要组件（例如，负载均衡、自动扩展、单节点与多节点），请提供您的推荐“黄金路径”选项以及替代方案。如果用户请求 HPA，请确保设计解决 LLM 自动扩展陷阱，并建议使用自定义指标（默认为队列大小）。
2.  **加速器选择**：参考
    [GPU 平台](https://docs.cloud.google.com/compute/docs/gpus.md.txt) 或
    [在 GKE 中规划 TPU 配置](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/plan-tpus.md.txt) 推荐
    最佳加速器以供目标模型使用。
    *(注意：`assets/` 中的清单模板仅限 GPU。如果用户选择 Cloud TPU，请明确说明，并基于 GKE TPU 服务文档而不是本指南中的模板构建服务清单。)*
3. **存储选择**：参考 [GCP AI 存储选项](https://docs.cloud.google.com/ai-hypercomputer/docs/storage.md.txt) 推荐最佳存储解决方案用于模型 staging 和服务。
4. **硬件与 VRAM 尺寸**：使用以下确定性 VRAM 尺寸公式准确计算 VRAM 需求：
    **硬件与尺寸推荐要求**：在计算 VRAM 尺寸或推荐硬件时：
    - 明确使用公式（参数大小、KV 缓存、20% 安全边际）解释 VRAM 计算。
    - 推荐特定加速器类型（例如，NVIDIA L4 配备 24GB VRAM 用于 8B 模型在 FP16/BF16）。
    - 推荐使用 **自定义计算类 (CCC)** 来最大化加速器可获取性。
    - 在发现阶段询问或确认用户的 **量化容忍度**（FP16/BF16 与 INT8/INT4）。
5. **集群和节点设置**：设计适当的集群以供任务使用。使用适当大小的节点添加到任务中，使用 Custom Compute Classes (CCC)。设计工作负载身份（如果需要）。vLLM 部署必须选择具有 `nodeSelector: cloud.google.com/compute-class: {compute_class_name}` 的节点，以便工作负载实际上通过 ComputeClass 安排。如果用户拒绝 CCC 并只想使用按需节点，则用 `cloud.google.com/gke-accelerator: {accelerator_type}` 替换此选择器，并完全跳过 `ccc-profile.yaml`；不要应用任何工作负载引用的 ComputeClass。
6. **模型 staging 设计**：根据阶段 2 的设计确定是否需要 staging 作业。如果模型权重源是 Hugging Face，或者如果目标是 Lustre 且源是 GCS，则计划使用作业下载/复制权重。如果源是 GCS 且目标是 GCS FUSE，则跳过 staging。计划使用 Cloud Storage FUSE 或 Lustre CSI 将此存储挂载到工作负载。
7. **草拟解决方案架构和清单**：读取 `assets/` 中的清单模板（`assets/vllm-deployment.yaml.tmpl`、`assets/ccc-profile.yaml.tmpl`、`assets/gke-inference-gateway.yaml.tmpl`、`assets/storage-config.yaml.tmpl` 和 `assets/model-staging-job.yaml.tmpl`），将 Phase 1 中发现的参数替换，并将生成的 YAML 清单（`vllm-deployment.yaml`、`ccc-profile.yaml`、`gke-inference-gateway.yaml`、`storage-config.yaml`、`model-staging-job.yaml`) 保存到当前目录中的磁盘。在创建 `vllm-deployment.yaml` 时，将 Phase 1 中发现的任何必需的模型特定架构标志（例如 `--trust-remote-code`）明确注入到容器 `args` 数组中。在创建 `gke-inference-gateway.yaml` 时，基于 `assets/gke-inference-gateway.yaml.tmpl`：使用 `gatewayClassName: gke-l7-rilb` 为 Gateway 资源，除非用户明确选择了外部暴露或基于 InferencePool 的 GKE 推理网关，并基于 HTTPRoute 资源将 `/v1` 流量路由到 vLLM ClusterIP 服务（`{workload_name}-vllm-svc` 在端口 8000））。如果使用其他存储类（例如 `lustre-csi`），则从 `storage-config.yaml` 中删除 `gcsfuse.cloud.google.com` 注释。
8. **请求审查和迭代**：向用户展示生成的解决方案架构和图表并请求他们的反馈。在用户批准设计之前迭代设计，然后才能进入阶段 3。

### 阶段 4：验证和切换

验证部署的基础设施是否满足工作负载的要求，并提供流量迁移说明。

**阶段 4 响应要求**：阶段 4 期间的每个响应都必须以视觉进度指示器开头：`**Migration Progress:** [○ 发现] ➔ [○ 解决方案设计] ➔ [○ 实施] ➔ [● 验证]`.

1. **健康检查**：建议使用显式健康检查命令来验证 Pod、节点和网关状态 (`kubectl get pods`, `kubectl get nodes`, 和 `kubectl get gateway`).
2. **测试推理**：验证服务正在提供模型。提供 `kubectl port-forward` 命令 (`kubectl port-forward svc/{workload_name}-vllm-svc 8000:8000`) 和一个样本 `curl` 请求到 `/v1/chat/completions` 来测试端点推理。如果适用，请与先前的基础设施进行比较。
3. **流量切换指导**：不要尝试自动实施流量迁移。相反：
    * 提供准备接收流量的内部 GKE 端点。
    * 提供基于相关代码库（如果有）的建议，说明如何迁移流量。
    * 建议使用标准 GKE 推流（例如，更新现有的部署清单以指向新服务）而不需要花哨的金丝雀测试或蓝绿部署。
    * 仅当用户明确要求时，才提供更高级的流量迁移选项。
4. **回滚准备**：在任何流量移动之前，确认源服务保持部署（缩小规模可以，删除则不可以）直到用户选择 GKE 端点已服务生产流量一段时间。提供恢复流量的单个命令或配置更改。只有在用户宣布迁移稳定后，才提供删除源服务的命令。
5. **编制验证报告并请求最终批准**：编制一个验证报告，总结所有健康检查结果和推理测试结果。您必须明确请求最终用户批准以完成和结束迁移工作流程。

### 故障排除指导

当用户报告 Pod 已创建但推理端点未响应（或请求故障排除帮助）时：

1. 建议特定的诊断命令：`kubectl logs {pod_name}`（检查容器启动日志）和 `kubectl describe pod {pod_name}`（检查 Pod 初始化状态）。
2. 建议验证 Google Cloud 加速器配额（GPU/TPU）在目标区域以确保可以配置所需资源。
3. **检查 JIT 编译 / 启动延迟**：如果 `curl` 返回 `Connection refused` 但 Pod 是 `Running`，服务引擎（例如，vLLM）可能仍在执行 JIT 编译（例如 Triton PTX 或 Torch Inductor）或捕获 CUDA 图表。这可能需要几分钟 *在模型权重加载后* 才能完成。建议用户检查 `kubectl logs {pod_name}` 并明确等待 `Uvicorn running on http://0.0.0.0:8000`（或等效）日志消息，然后再假设存在网络问题。
4. 建议检查 GKE 工作负载身份绑定、PVC 挂载健康（Cloud Storage FUSE）和 GKE 推理网关监听器配置。
