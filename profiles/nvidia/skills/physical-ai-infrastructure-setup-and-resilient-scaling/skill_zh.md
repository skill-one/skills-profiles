# 物理AI基础设施部署与弹性扩展

物理AI基础设施栈的规范技能。使用它将集群、推理、OSMO和工作负载阶段组合成一个可重复的物理AI SDG环境，并保持环境可观测和可恢复。

## 操作规则

- 仅读取所选目标所需的组件参考。不要默认加载所有组件。
- 将仓库作为持久化工件。修复已提交的配置或脚本，然后重新运行。不要用未跟踪的临时更改来恢复失败的安装。
- 当存在脚本时，通过已提交的脚本运行可变集群、OSMO、Helm、Terraform或Azure操作。允许只读诊断。
- 在第一个红灯处停止。按此顺序修复最低的拥有层：配置、脚本，然后技能指导。
- 尽可能从环境中派生值。只请求无法推断的值，例如API密钥、目标选择或配额权衡。
- 将密钥存储在`${REPO_ROOT}/.env`中。集群派生的值，如存储、数据库、Redis和端点名称来自Terraform输出或平台查询，而不是`.env`。
- 预检查意味着没有部署状态：没有集群API、Terraform输出、Helm发布、OSMO池或工作流状态。这些属于部署/验证门。
- 永远不要将原始密钥打印、回显或粘贴到命令、YAML、日志或转录中。优先使用凭证句柄、Kubernetes `secretKeyRef`和仅运行时密钥注入。在共享之前，用`scripts/scan_transcript_secrets.py`扫描原始转录导出。
- 使用绝对路径。用`git rev-parse --show-toplevel`派生仓库根路径。

## 组件参考

每个组件都生活在这个技能中，所以栈有一个规范的触发器。仅当所选目标需要该切片时才加载组件参考。

| 关注点 | 加载 | 资产 |
| --- | --- | --- |
| 阶段矩阵和旧驱动器笔记 | `components/driver/reference.md` | 无 |
| MicroK8s集群 | `components/cluster-microk8s/reference.md` | `components/cluster-microk8s/scripts/`, `components/cluster-microk8s/runtimeclass-nvidia-runc.yaml` |
| Azure AKS集群 | `components/cluster-azure/reference.md` | `components/cluster-azure/scripts/`, `components/cluster-azure/terraform/` |
| NIM Operator推理 | `components/inference-nim-operator/reference.md` | `components/inference-nim-operator/scripts/`, `components/inference-nim-operator/nims/` |
| NVCF推理 | `components/inference-nvcf/reference.md` | `components/inference-nvcf/scripts/` |
| Azure AI Foundry推理 | `components/inference-azure/reference.md` | `components/inference-azure/scripts/` |
| MicroK8s OSMO | `components/osmo-k8s/reference.md` | `components/osmo-k8s/scripts/`, upstream OSMO部署脚本 |
| Azure OSMO | `components/osmo-azure/reference.md` | `components/osmo-azure/scripts/`, upstream OSMO部署脚本加Azure TF输出 |
| Azure访问设置 | `components/azure-access/reference.md` | 无 |
| OSMO CLI和工作流操作 | `components/osmo-cli/reference.md` | `components/osmo-cli/scripts/`, `components/osmo-cli/references/`, `components/osmo-cli/agents/`, `components/osmo-cli/tests/` |
| OpenClaw Azure设备登录 | `components/openclaw-azure-login/reference.md` | 无 |

### OSMO CLI支持文件

OSMO CLI组件有二级支持文件，因为它的命令和工作流界面很大。仅当声明的情况直接加载这些文件。

| 文件 | 读取时 |
| --- | --- |
| `components/osmo-cli/agents/workflow-expert.md` | 生成工作流子代理或工作流失败子代理时。 |
| `components/osmo-cli/agents/logs-reader.md` | 为OSMO工作流失败生成日志摘要子代理时。 |
| `components/osmo-cli/references/cli-commands.md` | 需要确切的OSMO CLI标志、有效载荷或命令语法时。 |
| `components/osmo-cli/references/workflow-spec.md` | 需要工作流YAML模式、凭证、输出或提供者字段时。 |
| `components/osmo-cli/references/workflow-patterns.md` | 需要多任务、数据依赖、Jinja、串行或并行工作流设计时。 |
| `components/osmo-cli/references/advanced-patterns.md` | 需要检查点、重试/退出行为或节点排除时。 |
| `components/osmo-cli/tests/orchestrator-runtime-failure.md` | 验证或调试OSMO编排审查模式时。 |

## 目标选择

每个阶段选择一个选项。阶段2遵循阶段1。

1. Kubernetes：`MicroK8s`或`Azure`
2. OSMO：当Kubernetes是MicroK8s时为`MicroK8s OSMO`，当Kubernetes是Azure时为`Azure OSMO`
3. 推理：`NIM Operator`、`NVCF`、`Azure AI Foundry`或`None`
4. 工作负载：视频数据增强、缺陷图像生成、NuRec Carline适应、NRE、NCore、资产采集器或自定义工作流YAML

在配置前拒绝无效组合：

| 集群 | NIM Operator | NVCF | Azure AI Foundry |
| --- | --- | --- | --- |
| MicroK8s | 是 | 是 | 否，Foundry需要Azure身份 |
| Azure | 是 | 是 | 是 |

对于OpenClaw或任何无法打开浏览器的纯聊天环境，在Azure先决条件之前阅读`components/openclaw-azure-login/reference.md`。对于任何Azure目标，在Azure组件预检之前阅读`components/azure-access/reference.md`。

## 部署流程

1. 确认目标选择和工作负载计算需求。
2. 加载所选组件参考。
3. 提前解决先决条件，包括API密钥、Azure访问、调用者CIDR、GPU配额、存储类和OSMO登录要求。
4. 在配置前，为每个所选的基础设施组件加上任何OSMO CLI/工作负载预检运行`scripts/preflight.sh`；从结果构建实施计划并在红灯预检时停止。
5. 首先部署Kubernetes。在集群门变绿之前，什么也不启动。
6. 部署OSMO和推理在Kubernetes之后。一旦集群存在，这些可以并行进行，但工作负载提交等待所有选定的门。
7. 仅在OSMO、存储凭证、计算池和选定的推理端点验证后提交工作负载。对于VDA，这包括`preflight_credentials.sh`、`pre_submit_guard.py`与解析的`--set`值、非空的模型缓存前缀和工作流命名空间端点冒烟检查。
8. 监控到完成。在失败的工作流状态下，从`components/osmo-cli/reference.md`检查事件和日志；不要盲目重新提交。

## 推理发现

避免过度部署昂贵的端点。

1. 扫描所选工作流规范和默认值中的端点参考：`*.osmo-nims.svc.cluster.local`、`api.nvcf.nvidia.com/*`、`*.inference.ai.azure.com`或`*.cognitiveservices.azure.com`。
2. 将每个参考映射到所选后端：
   - NIM Operator：服务名称必须匹配`components/inference-nim-operator/nims/`下的一个目录。
   - NVCF：函数URL或函数ID必须由环境提供。
   - Azure AI Foundry：端点名称必须通过`components/inference-azure/scripts/install.sh`部署。
3. 如果工作流需要所选后端缺乏的功能，停止并报告不匹配。不要无声地替换另一个模型。

## 验证门

每个阶段在其组件参考中的自己的验证部分。这些门是强制的：

| 阶段 | 门 |
| --- | --- |
| Kubernetes | 集群API可访问、节点Ready、GPU容量为GPU路径宣传、CPU+NVCF路径有`runtimeclass/nvidia`映射到`runc` |
| 推理 | 工作负载引用的每个端点都是可访问的。NIM就绪使用`/v1/health/ready`；NVCF和Foundry仍然需要特定任务的认证检查 |
| OSMO | OSMO Pod Ready、池ONLINE、端口转发看门狗活跃、存储凭证配置、并验证-hello工作流COMPLETED |
| 工作负载 | 在提交前选定的预提交守卫通过。`osmo workflow query <id>`报告`COMPLETED`并且每个任务都是绿色的。失败的终端状态在重试前需要事件和日志 |

## 弹性扩展

- 在配置前根据工作负载需求调整集群大小。对于Azure，在`terraform apply`前检查所选VM系列的CPU和GPU配额。
- 对于NIM Operator，仅部署工作负载引用的NIMServices。每个服务为集群的整个生命周期固定GPU和模型缓存存储。
- 保持OSMO存储URL方案与活动后端一致。本地MicroK8s使用MinIO，Azure使用Blob支持的配置。
- 将Pending、Unknown、ImagePullBackOff、未绑定PVC或0 Ready副本视为层故障。在重试相同命令前调查调度、存储、图像凭证和相邻平台状态。
- 对于长部署或工作流监视，提供心跳更新，包括当前状态、经过的时间、最后一个有用观察和下一个检查。

## 工作负载路由

- 视频数据增强：使用`skills/physical-ai-video-data-augmentation/SKILL.md`。
- 缺陷图像生成：使用`skills/physical-ai-defect-image-generation/SKILL.md`。
- NuRec carline适应：使用`skills/carline-adaptation/SKILL.md`。
- NRE、NCore和资产采集器位于`skills/INDEX.md`中列出的规范NuRec目录中。
- 自定义工作负载：在检查资源请求、图像凭证、数据凭证和推理URL后，通过OSMO提交提供的 workflow YAML。

## 评估提示和结果

- 正面触发："为Azure AKS上的VDA设置弹性物理AI基础设施，使用NIM Operator。"
  预期：使用此技能。
- 负面触发："总结此工作流ID的最近OSMO工作流日志。"
  预期：除非请求也涉及基础设施栈的设置、扩展、验证或恢复，否则不要使用此基础设施设置技能。

最新静态审查：2026-05-26，描述关键字与上述预期路由匹配。
