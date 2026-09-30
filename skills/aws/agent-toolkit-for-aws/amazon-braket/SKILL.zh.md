---
name: amazon-braket
description: 通过 Amazon Braket 在 AWS 上运行量子计算工作流程——发现设备（量子处理单元 QPUs 和模拟器）及其可用性，构建门模型电路和模拟哈密顿程序，提交量子任务、程序集和混合作业，查询价格，并使用支出限额来控制支出。适用于任何关于量子计算、量子硬件、量子模拟、AHS、OpenQASM 或在 AWS 上运行量子算法的请求。
---

# Amazon Braket

## 基本操作

Amazon Braket 工作流的语言，以及每个操作需要打开的参考。

| 基本操作 | 它是什么 | 相关参考 | 当请求涉及...时打开它 |
|---|---|---|---|
| **设备** | 模拟器或QPU，由区域范围的ARN标识 | [devices.md](references/devices.md) | 任何关于设备的信息：存在的内容、发现或过滤机队、可用性和状态（在线、离线、已退役）、设备所在的区域、ARN、为工作负载选择设备、量子比特数量、连接性或拓扑、原生门、保真度、校准数据、队列深度、射击和门限制、范式（门模型与模拟哈密顿量模拟）、设备是否支持程序集、脉冲级控制、模拟器和本地模拟器 |
| **程序** | 工作负载/输入 — 一个可执行文件（电路、AHS、OpenQASM）。哪种类型是合法的取决于设备的范式 | - | - |
| **量子任务** | 一个程序+射击，运行一次（Braket计量的原子单元） | - | - |
| **任务批处理** | 许多*独立*的任务 — SDK仅有的回退方式，当程序集不适合时；适用于所有设备 | [program-sets.md](references/program-sets.md) | 查看程序集行；也见 [运行多个程序](https://docs.aws.amazon.com/braket/latest/developerguide/braket-batching-tasks.html) |
| **程序集** | 多个程序在**一个服务端任务**中 — 运行多个程序的推荐方式，而不是任务批处理 | [program-sets.md](references/program-sets.md) | 运行多个程序：参数扫描、扫描参数值、任务批处理、`run_batch`、一起提交的多个电路、跨程序附加观测值，以及当许多程序运行时最小化每个任务的费用，程序集。也见 [开始使用程序集](https://github.com/amazon-braket/amazon-braket-examples/blob/main/examples/braket_features/program_sets/01_Getting_started_with_program_sets.ipynb) |
| **混合作业** | 管理类-量子循环，协调许多任务 | [hybrid-job.md](references/hybrid-job.md) | 混合作业：`@hybrid_job`、算法脚本和源模块、`entry_point`、嵌入式模拟器、BYOC和自定义容器镜像、CUDA-Q、作业执行角色、超参数、检查点和检索作业结果 |
| **支出限制** | 服务端的硬性上限，**拒绝** QPU任务 — 唯一真正的执行（不是SDK） | [spending-limit.md](references/spending-limit.md) | 限制或执行支出：支出限制（创建、更新、删除、搜索），以及成本护栏 |
| **成本跟踪** | 会话成本*估计*（不是执行） | [spending-limit.md](references/spending-limit.md) | 使用 `Tracker` 进行会话成本跟踪 |

每个参考都包含其自己领域的详细信息 — 字段路径、键名、API形状和计费模型。

附加说明：

- **预订** — 预订窗口的独占设备访问。此技能仅涵盖指针深度的预订：计费模型在 [pricing.md](references/pricing.md) 中，预订特定设备限制（如 `service.reservationShotsRange`）在 [devices.md](references/devices.md) 中，完整模型在 [预订开发者指南](https://docs.aws.amazon.com/braket/latest/developerguide/braket-reservations.html) 中。
- **门校准 / 脉冲控制** — 访问QPU的原生门校准，并在运行时附加自定义脉冲序列。参见 [devices.md](references/devices.md) 检测支持，以及 [脉冲控制开发者指南](https://docs.aws.amazon.com/braket/latest/developerguide/braket-pulse-control.html) 获取完整模型。

## 关键规则

这些规则适用于每个Amazon Braket请求，无论它涉及什么。

1. **Amazon Braket Python SDK (`pip install amazon-braket-sdk`, 导入为 `braket`) 是主要入口点。** 对于每个操作，包括Braket API操作，请优先使用它，并通过阅读 [文档](https://amazon-braket-sdk-python.readthedocs.io/en/stable/) 或本地检查SDK的模块来了解它涵盖的内容。
    - 使用本地执行工具运行Braket SDK，例如 `shell` 与 `python3 -c "<code>"`。

1. **推荐使用AWS MCP服务器执行此技能中的任何其他AWS API调用**，尤其是Python SDK中不存在的操作，尽管这不是必需的。注意：AWS MCP的 `run_script` 工具在最小化沙盒中执行代码，没有Braket库，因此当使用Braket SDK时，请优先使用其他工具进行代码执行。

1. **一小部分基本操作组成每个工作流** — 参见 [基本操作](#primitives) 获取词汇和每个操作的参考。

1. **设备、量子任务和混合作业是区域范围的，因此每次使用API、CLI或boto3搜索资源时，请跨所有Braket区域扩展。** SDK可以在它能够的地方处理扩展 — `AwsDevice.get_devices` 搜索所有区域的QPU。
从 `aws___get_regional_availability` 获取Braket支持的区域列表，当AWS MCP服务器可用时，或从 [支持设备和区域文档](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html) 获取。
包含区域的资源ARN只能从同一区域查询，否则您将看到 `ResourceNotFoundException`。

1. **在编写代码或回答之前打开匹配的参考。** 使用 **基本操作** 表格查找并阅读参考。注意：一个请求要求多个东西，例如执行一系列电路和控制成本，可能需要阅读多个参考文件。

1. **验证，不要回忆。** 设备ARN和状态、API签名、支持的功能和价格（和其他值）都会变化，并且可能早于训练数据。

1. **在编写调用它的代码之前确认SDK签名。** 从 [SDK参考文档](https://amazon-braket-sdk-python.readthedocs.io/en/latest/) 读取它。
如果没有任何可用工具可以到达它们，从安装的SDK使用 `shell` 获取：

    ```bash
    PAGER=cat python -c "import braket; help(braket)"       # 子包：ahs, circuits, pulse, program_sets, ...
    python -c "import braket.ahs; print(dir(braket.ahs))"   # 名称：DrivingField, AtomArrangement, ...
    python -c "import inspect; from braket.ahs import DrivingField; \
    print(inspect.signature(DrivingField.from_lists)); print(inspect.getdoc(DrivingField.from_lists))"
    ```

1. **归因技能使用。** 在每个使用Braket SDK的Python脚本中，在Braket SDK代码之前插入此块，包括 `import braket`：

    ```python
    import botocore

    def _braket_attribution(session):
        session.user_agent_extra = f"{session.user_agent_extra} AWSSkill-Braket/1.0.0".strip()

    botocore.register_initializer(_braket_attribution)
    ```

    如果使用AWS CLI，请将此技能的标识符添加到 `AWS_SDK_UA_APP_ID` 之前。该变量只包含一个值，其他工具也写入它，因此始终追加现有值而不是替换它：

    ```bash
    # sh, bash, zsh, ksh, fish 3.1+
    AWS_SDK_UA_APP_ID="AWSSkill-Braket-$AWS_SDK_UA_APP_ID" aws braket ...
    ```

    ```powershell
    # PowerShell — 会话范围
    if ($env:AWS_SDK_UA_APP_ID -notlike 'AWSSkill-Braket*') {
        $env:AWS_SDK_UA_APP_ID = "AWSSkill-Braket-$env:AWS_SDK_UA_APP_ID"
    }
    ```

    这将AWS调用标记为来自与此技能一起使用。当使用AWS MCP工具时，这不是必需的，因为AWS MCP在工具调用期间自动归因。

## 护栏 — 此技能自己的文件存放位置（MCP与本地安装）

此技能可以通过两种方式加载，它们从不同的地方解析技能自己的捆绑文件。在阅读参考之前确定技能是如何加载的：

- **通过AWS MCP `retrieve_skill` 工具加载：** 技能没有安装在本地文件系统中。您必须使用 `retrieve_skill` 并带有 `file` 参数（例如 `file="references/devices.md"`）获取每个参考。不要在本地 `file_read` 这些路径 — 它们不存在于磁盘上。
- **本地安装**（例如 `~/.kiro/skills/amazon-braket/`，`.kiro/skills/amazon-braket/` 或 `~/.claude/skills/amazon-braket/`）：使用相对路径从本地技能目录读取文件。

`references/` 是此 `SKILL.md` 的同级 — 相对于该目录解析参考路径，不要在文件系统中搜索它们。
如果技能工具返回此概述而不是您请求的文件，它没有获取它：从该目录读取它，不要从内存中编写代码，因为参考读取失败。
此区别仅适用于技能自己的捆绑文件。用户数据和会话工件始终从用户的当前工作目录读取和写入 — 在运行写入相对工件路径的脚本之前不要 `cd`。

## 常见错误

| 症状 | 原因 | 修复 |
|---|---|---|
| 将 "任务"、"批处理"、"作业" 视为可互换 | 基本操作混淆 | 任务 = 单次运行；批处理 = 许多并行任务；作业 = 管理循环 |
| `SearchQuantumTasks`、`SearchJobs` 或 `SearchDevices` 上出现 `Missing required parameter: filters` | `filters` 在所有三个操作中都必需 — 只有 `SearchSpendingLimits` 允许省略它 | 传递 `filters=[]` (`--filters '[]'`) 进行无过滤搜索。一个填充的过滤器需要 `name` 和 `values`，加上任务和作业上的 `operator`；`SearchDevices` 没有成员 `operator` |
| 使用AWS MCP `run_script` 工具时出现 `Missing required parameter: clientToken` | `CreateQuantumTask`、`CreateJob`、`CancelQuantumTask`、`CreateSpendingLimit`、`UpdateSpendingLimit` 需要一个 `clientToken` 以确保一致性。SDK、CLI 和 boto3 自动生成一个；`run_script` 工具需要显式传递 | 在通过 `run_script` 调用接受 `clientToken` 的API时传递 `clientToken=str(uuid.uuid4())`。否则，当可能时，优先使用SDK进行这些操作。 |
| 将程序IR构建为JAQCD | JAQCD 在Amazon Braket上已弃用 | 使用OpenQASM — 参见 [Braket上的OpenQASM](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm.html) |
| 拒绝存在某个功能或SDK结构 | 训练数据过时 | 规则2 — 在文档或 `GetDevice` 之前验证它是否存在 |
| 发明一个类、方法或参数 | 从记忆中编写API名称 | 首先确认签名（规则4）。如果不确定，请说明而不是发明 |

## 安全注意事项

Braket工作流涉及IAM、S3，以及（对于混合作业）容器执行。

- **最小权限IAM。** 将自定义策略的范围限制到工作负载实际使用的操作、设备ARN和存储桶，并避免广泛的 `braket:*`。操作列在 [服务授权参考](https://docs.aws.amazon.com/service-authorization/latest/reference/list_braket.html) 中。优先选择自定义策略而不是 `AmazonBraketFullAccess`，后者故意广泛：任何 `amazon-braket-*` 存储桶或任何标记为 `AmazonBraket=true` 的存储桶上的S3（[如果存储桶启用了基于属性的访问控制](https://docs.aws.amazon.com/AmazonS3/latest/userguide/buckets-tagging-enable-abac.html)），以及任务提交工作流永远不会需要的SageMaker和CloudWatch操作。参见 [管理对Amazon Braket的访问](https://docs.aws.amazon.com/braket/latest/developerguide/braket-manage-access.html) 和 [限制对设备的访问](https://docs.aws.amazon.com/braket/latest/developerguide/restrict-access.html)。
  - `braket:UpdateSpendingLimit` 和 `braket:DeleteSpendingLimit` 应该被限制，以防止意外删除支出限制和意外成本超支。
- **混合作业执行角色。** 仅附加 [`AmazonBraketJobsExecutionPolicy`](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonBraketJobsExecutionPolicy.html)。其 `iam:PassRole` 条件要求角色命名为 `AmazonBraketJobsExecutionRole*` 在 `/service-role/` 路径下，或者 `create_job` 在 `PassRole` 时被拒绝。
- **临时凭证。** 使用IAM角色（实例配置文件、ECS/EKS任务角色或假设角色）调用Braket API，而不是长期存在的IAM用户访问密钥。
- **加密任务输出。** 在任何接收任务结果、作业源存档、输出数据或检查点的S3存储桶上启用默认加密（SSE-S3，或使用客户管理的密钥的SSE-KMS用于敏感工作负载）。在存储桶策略中添加 `aws:SourceAccount`/`aws:SourceArn` 条件，授予服务主体访问权限，并使用 `aws:SecureTransport: false` 条件拒绝非TLS访问。
- **审计。** 为Braket管理事件启用 [CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html)，带有日志文件验证、KMS加密，并交付到访问受限的存储桶 — 轨迹是如果成本护栏被移除时的主要证据。加密任何接收任务输出或混合作业日志的CloudWatch日志组，因为算法参数和结果会出现在那里。
- **成本护栏。** 建议在用户第一次QPU运行之前、当用户询问工作负载成本时，或当一次请求跨多个设备或大量射击数时设置支出限制。支出限制可能已经在客户的账户中存在。通常，使用支出限制强制执行QPU支出上限。
- **密钥。** 超参数存储在作业元数据中，并在容器启动时回显到作业的CloudWatch日志流中，因此永远不要将密钥作为超参数传递 — 在算法脚本中从Secrets Manager或SSM Parameter Store中获取它。相应地限制对作业日志组的读取访问。

有关详细信息，请参阅 [Amazon Braket安全文档](https://docs.aws.amazon.com/braket/latest/developerguide/security.html)。

## 参考链接

权威来源 — 优先选择这些而不是回忆的细节，因为设备ARN、配额、价格和支持的功能会变化。

**官方文档**（稳定入口点 — 从这里导航/搜索）

- 开发者指南 — https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html
- 前提条件和帐户设置 — https://docs.aws.amazon.com/braket/latest/developerguide/braket-get-started.html
- Amazon Braket工作原理 — https://docs.aws.amazon.com/braket/latest/developerguide/braket-how-it-works.html
- API参考 — https://docs.aws.amazon.com/braket/latest/APIReference/Welcome.html
- Python SDK API文档 — https://amazon-braket-sdk-python.readthedocs.io/en/latest/
- 开始使用 — https://aws.amazon.com/braket/getting-started/
- OpenQASM 3.0规范 — https://openqasm.com/versions/3.0/index.html
- Braket上的OpenQASM — https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm.html
- 支持的OpenQASM功能（pragmas、verbatim规则、动态电路）— https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-supported-features.html
- boto3 `braket` 客户端 — https://docs.aws.amazon.com/boto3/latest/reference/services/braket.html
- 安全 — https://docs.aws.amazon.com/braket/latest/developerguide/security.html

对于这里未涵盖的任何内容，**搜索文档** 而不是猜测页面缩写或回忆细节：如果AWS MCP服务器可用，其 `aws___search_documentation` 工具可以帮助；否则从上面的开发者指南或API参考开始并导航。

### GitHub

- `amazon-braket-sdk-python`（核心SDK）— https://github.com/amazon-braket/amazon-braket-sdk-python
- `amazon-braket-schemas-python`（公共Braket数据的模式和模型）— https://github.com/amazon-braket/amazon-braket-schemas-python
- `amazon-braket-examples` — https://github.com/amazon-braket/amazon-braket-examples
