# 迁移到 MSK Express

## 概述

此技能帮助客户将自管理的 Apache Kafka 工作负载迁移到 Amazon MSK Express。它提供三个阶段——**发现**、**评估**和一个可选的**模拟**——可以根据客户的需求选择端到端运行或单独运行。

## 范围

此技能涵盖从**自管理的 Apache Kafka**（本地、EC2、Docker、Kubernetes 或其他非 MSK 部署）到 MSK Express 的迁移。从 **MSK 标准（按量付费）到 MSK Express** 的迁移不在范围内。

## 前置条件

建议使用 AWS MCP 服务器进行文档查找和信息性问题，但不是必需的。评估脚本是完全的文件处理器，没有 AWS API 调用。

## 意图路由

根据客户的意图路由请求：

### 1. 打开性/探索性问题（“我如何迁移到 MSK？”）

解释此技能提供的服务：

> 此技能帮助您分三个阶段迁移到 MSK Express：
>
> **阶段 1 — 发现**：清单您的源 Kafka 集群——代理、主题、分区计数、配置、身份验证和工作负载指标——以及两个决定成本的目标决策：消费者机架亲和性和任何协商的 AWS 定价。我可以从 IaC 文件（Terraform、CDK、Docker Compose、Kubernetes 资源清单）中发现这些信息，为您提供在集群上运行的命令，或者您可以手动提供这些信息。输出：`migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json`。
>
> **阶段 2 — 评估**：验证您的集群是否符合 MSK Express 的要求，涵盖 5 个兼容性支柱（拓扑、Kafka 版本、配置、身份验证、配额），并使用 managing-amazon-msk 技能的定价逻辑生成目标 Express 规范。我会标记 Express 将拒绝的内容和 Express 将静默转换的内容。输出：`compatibility.<cluster_name>.json`、Markdown 格式的定价结果 `msk_sizing_pricing.md` 和 `msk-sizing-inputs.<cluster_name>.json`。
>
> **阶段 3 — 模拟**：启动一个 MSK Express 集群和负载测试基础设施，以查看 Express 在您自己的工作负载上的表现，然后运行一个推荐的测试（端到端延迟或负载下的代理重启）并在 CloudWatch 仪表板上查看结果。
>
> **数据复制**：要迁移数据到您的 Express 集群，您可以使用 MSK Replicator。我可以提供设置和配置的指导。
>
> 您想从哪里开始？如果您指向我的基础设施代码或描述您的集群，我可以从发现阶段开始，或者如果您已经有了 `cluster-config.json` 文件，我可以直接跳到评估阶段，或者如果您已经知道目标 Express 配置，可以直接跳到模拟阶段。

**此概述响应的约束条件：**

- 此响应只是一个概述和路由问题。**不要**开始、模拟或预先执行任何阶段。
- **不要**在此处生成或估计评估输出——没有结论、支柱发现、兼容性结论、代理计数、实例建议或成本数字。这些值只有在您运行阶段 2 脚本并针对真实的 `cluster-config.json` 文件时才存在。
- **不要**打开、读取或总结 `compatibility.py`、`simulation_load_test_config.py` 或参考文件以解释阶段的工作原理。在上述级别描述阶段；不要引导客户了解实现细节。
- 当客户选择一个阶段时，运行该阶段脚本或流程以生成实际结果。始终操作技能来回答——而不是从阅读其源代码来回答。确切的命令，请参阅 [references/assessment-compatibility.md](references/assessment-compatibility.md) 中的“运行评估”部分（阶段 2），以及 [references/simulation.md](references/simulation.md)（阶段 3）。

### 2. 发现意图（当提供 IaC 文件时默认）

如果客户提供一个目录路径、IaC 文件或说“这是我们的基础设施”，这是发现意图。仅运行阶段 1（发现）。**不要**运行评估，**不要**建议迁移步骤，**不要**提及障碍或兼容性问题。生成 `migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json` 文件并停止。

### 3. 评估意图

客户明确要求评估或已经生成了 `migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json` 文件。仅运行阶段 2（评估）。

### 4. 模拟意图

客户希望使用他们自己的工作负载测试 MSK Express。他们可以直接提供集群规模（实例类型、代理数量、Kafka 版本），或参考先前的评估。直接进入 [阶段 3 — 模拟](#phase-3--simulation-optional)。评估很有帮助但不是必需的——模拟直接要求提供规模输入。

### 5. 信息性问题

客户询问 Express 功能、限制、配置差异、身份验证支持、定价或压缩行为，但没有提供集群特定数据。如果可用，使用 AWS 文档工具（`aws___search_documentation`、`aws___read_documentation`）从 MSK Express 文档中查找答案。如果 MCP 工具不可用，请参考 [MSK Express 文档](https://docs.aws.amazon.com/msk/latest/developerguide/msk-broker-types-express.html) 并根据对 AWS MSK 的了解回答。

### 6. 迁移策略问题

客户询问 MSK Replicator 兼容性、版本升级路径、MirrorMaker 2 或迁移策略。MSK Replicator 是 AWS 支持的原生数据复制解决方案，适用于 MSK 到 MSK 和非 MSK 到 MSK 的迁移。如果可用，使用 AWS 文档工具（`aws___search_documentation`、`aws___read_documentation`）检索当前要求和支持的配置。如果 MCP 工具不可用，请参考 [MSK Replicator 文档](https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator.html) 并根据对 AWS MSK 的了解回答。

---

## 阶段 1 — 发现

**目的**：清单源集群以构建迁移配置文件。

**输入**：以下之一：

- 包含 IaC 文件（CDK、CloudFormation、Docker Compose、Kubernetes 资源清单、Terraform）的目录路径
- 客户在集群上运行的 Kafka CLI 命令的输出
- 客户在对话中提供的手动信息

**输出**：`migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json`——保存到工作目录。

### 发现规则

- 在发现中的任何操作之前，您**必须**完整阅读 [references/discovery.md](references/discovery.md)。它定义了输入方法、必需的响应模板、禁止的内容和 `cluster-config.json` 架构。**在阅读它之前不要响应**，并**精确遵循**其模板。
- **始终**将 `migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json` 保存到工作目录。
- **未经客户明确确认，不要**进入阶段 2。

---

## 阶段 2 — 评估

**目的**：评估集群是否符合 MSK Express 要求，并生成目标 Express 规范（实例类型、代理数量、月度成本预测）。

**输入**：来自阶段 1 的 `migrate-to-msk-skill-artifacts/<cluster_name>/cluster-config.json`。

**输出：**

- `migrate-to-msk-skill-artifacts/<cluster_name>/compatibility.<cluster_name>.json`——五个支柱的裁决。
- `migrate-to-msk-skill-artifacts/<cluster_name>/msk_sizing_pricing.md`——managing-amazon-msk 技能的定价报告，包含代理数量和成本建议。
- `migrate-to-msk-skill-artifacts/<cluster_name>/msk-sizing-inputs.<cluster_name>.json`——规模逻辑的六个输入值的记录。

评估有两个独立的半部分；可以按任何顺序运行它们，一个部分的失败不会阻止另一个部分：

- **兼容性**——`scripts/compatibility.py`，一个纯文件处理器（没有实时 AWS API 调用），通过 `uv run` 运行，并使用 PEP 723 内联依赖项。它验证源集群的五个支柱——拓扑、Kafka 版本、配置、身份验证和配额——并为每个支柱发出一个裁决（`INFO`、`ADVISORY` 或 `ACTION_REQUIRED`，整体为最差情况）。使用这三个字符串的原始值。
- **规模**——此技能中不是脚本。加载 managing-amazon-msk 技能并运行其 `scripts/msk_sizing.py`，使用从 `cluster-config.json` 派生的负载输入，传递 `--broker-classes express`。

### 评估规则

- 在响应之前阅读 [references/assessment-compatibility.md](references/assessment-compatibility.md)。它包含调用命令、每个支柱的阈值和证据代码、裁决定义、完整的禁止行为列表以及**覆盖两个艺术品的必需响应模板**。不要自由发挥后续脚本摘要。
- 在运行规模之前阅读 [references/assessment-sizing.md](references/assessment-sizing.md)。它包含输入派生（其中一些不是一对一的——错误地获取它们会导致错误的代理数量），`target`-块标志用于机架亲和性和协商折扣，Express 仅限的显示规则和源足迹比较。
- 将任何 `ACTION_REQUIRED` 证据显示给用户以供了解，但不要将其作为进一步阶段的障碍。Express 可能仍然接受具有缓解措施的工作负载。
- **不要**回到发现。评估在现有的 `cluster-config.json` 上按原样运行。部分数据是好的——脚本会为缺失的字段发出 ADVISORY 证据（`METRICS_MISSING`、`AZ_COUNT_UNKNOWN` 等）；显示这些发现并停止。不要建议 Kafka CLI 命令、IaC 步行、脚本或问卷以填补空白。
- 仅报告代理数量和成本，作为从规模脚本输出中读取的原始值。**不要**四舍五入、重新派生或估计它们。

---

## 阶段 3 — 模拟（可选）

在客户的账户中部署一个临时的、隔离的 MSK Express 集群和客户端舰队，以便他们可以看到 Express 在他们自己的工作负载上的表现，然后运行两个推荐的测试之一（端到端延迟、负载下的代理重启），并交出 CloudWatch 仪表板。遵循 12 步对话流程和所有部署、规模和约束细节，在 [references/simulation.md](references/simulation.md)；它驱动的确定性工件是 [scripts/simulation_load_test_config.py](scripts/simulation_load_test_config.py) 和静态的 [assets/simulation-stack.yaml](assets/simulation-stack.yaml)。

---

## 执行模型

脚本通过 `uv run` 在客户的本地计算机上运行。它们声明自己的依赖项（PEP 723），并且是完全的文件处理器——没有 AWS API 调用、没有网络访问，也没有第三方依赖（仅使用标准库）。

## 安全注意事项

在每个阶段应用这些控制。有关更多详细信息，请参阅 [MSK 安全最佳实践](https://docs.aws.amazon.com/msk/latest/developerguide/security.html) 和 [MSK IAM 访问控制](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html)。

1. **传输中加密（强制）**。在 MSK Express 目标上强制执行 TLS，用于客户端-代理流量（`EncryptionInTransit.ClientBroker = TLS`）。

2. **静态加密（强制）**。使用客户管理的 KMS 密钥（如果您的合规性立场允许，则使用 AWS 管理的密钥）配置目标集群。

3. **身份验证——优先使用 IAM 而不是长期凭证**。使用 IAM 身份验证配置 MSK Express 目标作为唯一的客户端身份验证方法。这提供了基于角色的临时凭证，并具有完整的 CloudTrail 覆盖。

4. **凭证存储——使用 AWS Secrets Manager**。将源集群访问的 SASL/SCRAM 和 TLS 凭证存储在 Secrets Manager 中。**永远不要**将密码作为 CLI 参数传递。

5. **网络隔离**。在私有子网中部署 MSK 集群。使用针对特定 CIDR 范围或安全组引用的安全组。**不要**使用 0.0.0.0/0 入站规则。

6. **CloudTrail 日志记录和 CloudWatch 报警**。确保在目标账户中启用 CloudTrail 并涵盖 `kafka.amazonaws.com` API 调用。配置警报：
   - `ClientAuthenticationFailure`——激增表示凭证问题或攻击
   - `ConnectionCloseCount`——异常激增可能表示连接洪水
   - CloudTrail 指标过滤器，用于拒绝的 `kafka-cluster:*` 操作
   - 接近 100 conn/sec/broker IAM 限制的连接速率警报

7. **敏感数据处理**。发现和评估输出包含代理地址、身份验证提示和代理配置值。将它们视为敏感信息——不要在没有编辑的情况下将它们粘贴到公共频道或工单系统中。

## 故障排除

支柱发现，包括源拓扑和超出范围的配置案例，在 [references/assessment-compatibility.md](references/assessment-compatibility.md) 中解释。
