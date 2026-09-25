# 华为云 Terraform 生成器

## 1. 概述

该技能将用户的基础设施目标转换为华为云的 Terraform 配置。主要工作流程是：

1. 理解用户的实际部署意图
2. 确定应创建哪些资源
3. 确定是否应复用现有资源
4. 确认关键规格和依赖关系
5. **验证每个资源规格是否与目标区域的可用资源匹配 — 先查询，后编写**
6. 确保 Terraform 已安装
7. 生成 Terraform 配置文件
8. 运行验证步骤并修复生成问题，直到 `terraform plan` 成功
9. 请求用户确认，并在批准后执行 `terraform apply`

该技能提供交互式工作流程，代理将引导用户完成凭证配置、验证计划，并在明确用户确认后执行 apply。

## 2. 前置条件

在使用此技能之前，确保以下内容可用：

1. **Terraform** — 已安装在 PATH 中或可自动安装（见 validation-workflow.md）
2. **提供程序下载源** — 华为云镜像应可访问（见 validation-workflow.md）
3. **目标区域** — 部署区域（例如 cn-north-4, cn-south-1）必须确定

## 3. 参数确认

在生成 Terraform 之前，向用户确认具体的资源计划。计划应包括：

- 推荐的资源规格
- 在适用情况下可用的候选选项
- 是否创建新资源或复用现有资源
- 仅在从可靠来源获取时提供定价信息

参见 `reference/guardrails.md` 了解关于不编造规格和价格的规则。

不要要求用户手动提供每个参数。相反：

1. 从用户的目标中推断可能的架构
2. 提出具有推荐默认值的具体计划
3. 仅确认对正确性、成本或架构有实质性影响的少数决策

用户应主要确认提出的解决方案，而不是自己构建完整的参数集。

## 4. 工作流程

该技能分为九个阶段：

### 4.0 凭证处理（必读）

AK/SK 凭证从环境变量 `HW_ACCESS_KEY` 和 `HW_SECRET_KEY` 中读取。对于临时/STS 凭证，代理 **必须** 从环境变量中读取 `HW_SECURITY_TOKEN`（或 `HUAWEICLOUD_SECURITY_TOKEN`）并将其写入 `terraform.tfvars` 作为 `security_token`。提供程序无法可靠地从环境变量解析 `security_token`。如果环境变量未设置，则省略（永久 AK/SK 场景）。
在依赖凭证的任何步骤（资源查询、`terraform plan` 等）之前，读取 `reference/guardrails.md` 中的完整规则。
如果 API 或 Terraform 调用因身份验证错误失败：告知用户具体错误，在问题解决后请求他们确认，然后重试。不要指导用户如何配置凭证。

### 4.1 理解用户的真实目标

用户可能直接描述资源，例如创建 ECS 实例，也可能描述业务目标，例如部署网站或启动应用程序。
你必须首先从用户的目标中推断出预期的华为云架构，而不仅仅是显式的资源名称。

### 4.2 确定资源集

根据用户的目标，识别：

- 需要创建哪些资源
- 哪些现有资源可以复用
- 资源之间存在哪些依赖关系

例如：

- 一个简单的公共网站可能需要 VPC、子网、安全组、ECS 和 EIP
- 一个托管数据库部署可能需要 VPC、子网、安全组和 RDS
- 一个可扩展的公共服务可能需要 VPC、子网、安全组、ECS 或 AS、ELB 和公共访问

### 4.3 提出资源计划供确认

在生成 Terraform 之前，根据 Parameter Confirmation 部分的规则，向用户提出具体的资源计划供确认。

参见 `reference/guardrails.md` 了解处理敏感信息的规则。

### 4.3.1 与用户确认安全组规则（关键）

**必需工作流程：**

1. 从用户的目标中推断可能的端口（Web 服务器 → 80、443；SSH → 22；数据库 → 3306、5432）
2. 请求用户确认端口：“需要开放哪些端口？推荐：80、443、22”
3. 基于确认的端口生成规则，而不是默认规则

**Terraform 生成：**
```hcl
# 用户确认：80、443、22

resource "huaweicloud_networking_secgroup_rule" "http" {
  security_group_id = huaweicloud_networking_secgroup.main.id
  direction         = "ingress"
  ethertype         = "IPv4"
  port_range_min    = 80
  port_range_max    = 80
  protocol          = "tcp"
  remote_ip_prefix  = "0.0.0.0/0"
}

# ... 类似地用于 443、22（始终包括 ethertype = "IPv4"）

# 始终包括出站
resource "huaweicloud_networking_secgroup_rule" "egress" {
  security_group_id = huaweicloud_networking_secgroup.main.id
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
}
```

**禁止：**
- ❌ 仅使用出站规则而不使用入站规则
- ❌ 不询问用户而使用硬编码的默认端口
- ❌ 生成与用户确认不匹配的规则

### 4.4 在生成任何代码之前验证资源可用性

**此步骤是强制性的，绝不能跳过。查询失败不是继续的许可 — 它是一个必须解决的障碍。**

在编写 Terraform 的第一行代码之前，你必须确认计划中的每个资源规格与目标区域匹配。目标区域已在步骤 4.3 的确认计划中知晓 — 如果缺少区域，则表示步骤 4.3 不完整并必须重新访问。没有不知道你部署到哪个区域的借口。

1. **步骤 1 — 首先阅读目标技能的 SKILL.md（不要跳过）：** 你必须在调用技能之前阅读文件 `../huawei-cloud-computing-query/SKILL.md`。这告诉了你确切的调用格式、所需参数、参数格式以及如何传递目标区域。你不能正确调用你未阅读的技能。
2. **步骤 2 — 使用确认的参数调用技能：** 只有在阅读了技能定义之后，才能使用确切的参数调用 `huawei-cloud-computing-query` 技能，并将步骤 4.3 中的确认计划中的目标区域传递给它。确认确认计划中的每个资源规格实际上存在于目标区域，并且可用。任何无法确认的规格都绝不能出现在任何 .tf 文件中。
3. **禁止跨区域假设** — 区域 A 中可用的资源并不表示在区域 B 中可用。始终为目标区域重新查询。

**禁止：**
- ❌ 在未首先阅读其 SKILL.md 的情况下调用 `huawei-cloud-computing-query` 技能
- ❌ 猜测或编造技能调用的参数
- ❌ 当资源规格无法确认可用时继续生成 Terraform
- ❌ 假设资源可用性会跨区域传递

**如果查询失败（环境错误、网络问题、SDK 崩溃）：**

- 你绝不能继续生成 Terraform。立即停止。
- 诊断并修复问题：调用 `huawei-cloud-computing-query` 技能的环境检查，验证凭证，检查网络。
- 重试查询。如果再次失败，修复并重试。
- 没有“优雅降级” — 未验证的规格是一个等待发生的故障部署。
- 只有以下结果是可接受的：(a) 所有规格确认可用，或 (b) 确认某个规格不可用，并请求用户选择不同的规格。

**为什么这很重要：** 将不可用的 flavor 写入 `main.tf` 生成一个通过 `terraform validate` 但在 `terraform apply` 时失败的配置 — 这是最糟糕的错误，因为它只在等待数分钟后才出现。

**在修改现有 Terraform**（用户要求更改 flavor、切换区域、使用不同的实例类型等.）：在新区域中重新运行可用性查询新规格**之前**编辑任何 .tf 文件。不要假设之前查询的结果仍然适用。

### 4.5 确认后生成 Terraform

**关键：生成之前必须阅读相关参考文档，来自第 8.1 映射表。**

一旦用户确认资源计划，就按照所需的结构和样式规则生成 Terraform 文件。

参见 `reference/terraform-generation-guide.md` 了解详细的文件结构和内容规则。

**关键：** 在继续之前，必须生成所有必需的文件（providers.tf、variables.tf、main.tf、terraform.tfvars、README.md）并验证它们是否存在。

### 4.6 验证凭证配置

在继续验证之前，验证是否通过环境变量配置了华为云凭证。

参见 `reference/guardrails.md` 了解关于 AK/SK 处理的规则。

### 4.6.1 配置华为云镜像以供提供程序下载

**在运行 terraform init 之前，配置华为云镜像以避免从官方 Terraform 注册中心缓慢下载。**
**不要首先尝试从官方注册中心下载。始终使用华为云镜像。**

**步骤：**
1. 检查本地提供程序缓存是否存在（见 validation-workflow.md 中的位置）
2. 如果缓存存在且版本 >= 1.90.0，则跳过下载
3. 如果需要下载，在项目目录中创建 `.tfrc` 文件：
   ```hcl
   provider_installation {
     network_mirror {
       url = "https://mirrors.huaweicloud.com/terraform/"
       include = ["registry.terraform.io/huaweicloud/*"]
     }
   }
   ```
4. 将 `TF_CLI_CONFIG_FILE` 环境变量设置为 `.tfrc` 文件路径
5. **每个 `terraform init` 命令都必须在同一命令行中包含 `TF_CLI_CONFIG_FILE`。没有环境变量的 `terraform init` 是禁止的。示例：**
   ```bash
   export TF_CLI_CONFIG_FILE="/path/to/project/.tfrc" && terraform init -upgrade
   ```

### 4.7 验证并修复生成的配置

按顺序运行验证：`terraform fmt -recursive` → `terraform init` → `terraform validate` → `terraform plan`

如果任何步骤失败，检查错误，修复配置，并重试，直到 `terraform plan` 成功。

参见 `reference/validation-workflow.md` 了解详细的验证步骤。

### 4.8 显示成本估算（关键 — 必须不跳过）

**此步骤是强制性的，必须在 `terraform plan` 成功后、任何确认对话框或 `terraform apply` 之前立即执行。跳过此步骤是严重的违规。**

**成本显示格式（用计划中的实际资源填充）：**
```
💰 费用预估

即将创建的资源：
- [资源类型] ([规格]): [预估费用]
- [资源类型] ([规格]): [预估费用]
- ...

预估合计: [总费用]

📌 华为云价格计算器: https://www.huaweicloud.com/pricing.html#/calculator
```

**必需元素（所有元素都必须存在）：**
- 带规格的资源列表（来自确认计划）
- 每个资源的预估月成本（范围可以接受）
- 预估总成本
- 华为云价格计算器链接（固定 URL）

**如果你无法估算成本：** 仍然列出资源并注明“费用请参考价格计算器” — 不要从列表中省略资源。

**验证：** 在进入步骤 4.9 之前，确认你已经输出了上述所有必需元素。如果任何元素缺失，停止并添加它。

### 4.9 带用户确认执行 terraform apply

成本估算显示后，在执行 apply 之前，弹出一个确认对话框以供用户确认。

参见 `reference/guardrails.md` 了解关于用户确认工作流程的规则。

### 4.10 Apply 错误修复循环

如果 `terraform apply` 失败，检查错误，修复配置，重新运行 `terraform plan`，并重新执行 `terraform apply`。重复直到成功。

### 4.11 Apply 后资源验证

`terraform apply` 成功后，验证部署的资源是否与确认的计划匹配。如果发现差异，报告并修复它们。

## 5. 安全规则

参见 `reference/guardrails.md` 了解详细的安全规则。

关键原则：
- 不要编造规格、价格或资源事实
- 带有明确用户确认执行 terraform apply
- 不要请求敏感信息
- 在阅读该技能的 SKILL.md 文件之前，不要调用任何引用的技能

## 6. Terraform 生成规则

在用户确认资源计划后，生成与确认的解决方案一致的最小、有效且一致的 Terraform。

参见 `reference/terraform-generation-guide.md` 了解有关文件结构、内容规则、数据源使用和变量设计的详细指南。

核心原则：
1. 从确认的资源计划开始
2. 遵循最小可行配置原则
3. 优先考虑 Terraform 有效性而不是不必要的灵活性
4. 在相关情况下使用现有软件包引用

## 7. 环境准备和验证

参见 `reference/validation-workflow.md` 了解有关确保 Terraform 可用性、提供程序下载 **（从华为云镜像）**、验证顺序、身份验证和修复循环的详细指南。

## 8. 参考使用和模板指导

在相关情况下，使用技能包中的参考材料、模板、示例和辅助工具。

### 8.1 在相关情况下使用现有参考

**必须在这些参考之前生成：**

| 资源 | 参考文档 | 关键模式 |
|------|-------------------|-------------|
| **通用规则** | `reference/guardrails.md` + `reference/terraform-generation-guide.md` | 密码自动生成、不向用户要敏感信息 |
| 安全组 | `reference/VPC-best-practices/VPC-best-practices.md` → "Deploy Security Group" | `ethertype` 是必需的 |
| ECS with EIP | `reference/ECS-best-practices/Deploy-Instance-with-EIP-best-practices.md` | 使用 `huaweicloud_compute_eip_associate`，`public_ip = .address` |
| VPC/Subnet | `reference/VPC-best-practices/VPC-best-practices.md` → "Deploy Basic Network" | VPC/子网结构 |
| RDS | `reference/RDS-best-practices/RDS-best-practices.md` | 数据库 + 网络配置 |

### 8.2 使用现有示例和模板作为起点

如果包中包含与目标场景接近的示例，则将其作为起点。保留有用的结构，根据确认的计划进行适配，并删除不需要的资源。

### 8.3 将用户目标映射到相关参考

将业务目标映射到服务参考（例如，“部署网站”→ VPC + ECS + EIP，“托管数据库”→ RDS + 网络）。

### 8.4 使用参考来改进，而不是过度构建

保持最终的 Terraform 与用户确认的计划一致，并遵循最小可行配置原则。

### 8.5 不要盲目依赖模板

始终验证模板是否与确认的计划匹配，并通过正常验证工作流程进行验证。

## 9. 质量检查清单

最终确定前，确保：

- [ ] 生成的 Terraform 与确认的资源计划匹配
- [ ] 生成了并验证了所有 5 个必需文件（providers.tf、variables.tf、main.tf、terraform.tfvars、README.md）
- [ ] 没有向用户请求敏感信息
- [ ] 验证达到了 `terraform plan`，或清楚地解释了障碍
- [ ] 在用户确认之前显示成本估算（步骤 4.8 — 必须不跳过）
- [ ] 成本估算包括所有必需元素：资源列表、规格、每个资源的预估成本、总成本、价格计算器链接
- [ ] 通过确认对话框请求用户确认，然后再执行 terraform apply
- [ ] 仅在明确用户确认（或用户拒绝）后执行 `terraform apply`
