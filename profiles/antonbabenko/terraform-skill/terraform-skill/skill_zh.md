# Terraform 技能指南 for Claude

针对 Terraform 和 OpenTofu 的诊断优先指导。核心文件是一个工作流；深度存在于按需加载的引用中。

## 响应合同

每个 Terraform/OpenTofu 响应必须包括：

1. **假设与版本下限** — 运行时（`terraform` 或 `tofu`）、确切版本、提供者、状态后端、执行路径（本地/CI/云/Atlantis）、环境关键性。如果用户未提供，则明确假设状态。
2. **解决的风险类别** — 一个或多个：身份变更、秘密泄露、破坏范围、CI 漂移、合规差距、状态损坏、提供者升级风险、测试盲点。
3. **选择的修复措施与权衡** — 选择了什么、权衡了什么、为什么。
4. **验证计划** — 针对运行时和风险层量身定制的确切命令（`fmt -check`、`validate`、`plan -out`、策略检查）。
5. **回滚说明** — 对于任何破坏性或状态变更的更改：如何撤销、保留哪些证据。

在没有经过审查的计划工件和批准的情况下，永远不要推荐直接生产应用。

在运行 `terraform destroy`（目标或全部）之前，必须先运行 `terraform plan -destroy` 并向用户展示将要删除的每个资源——包括通过 `locals` 或 `for_each` 拉入的隐式依赖项。在进行下一步之前获取明确确认。永远不要在销毁时使用 `-auto-approve`。

## 工作流

1. **捕获执行上下文** — 运行时+版本、提供者、后端、执行路径、环境关键性。
2. **使用下表中的路由表诊断故障模式**。如果意图跨越类别，则加载两个引用。
3. **仅加载匹配的引用文件** — 不要预加载任务不需要的深度。
4. **提出带风险控制的修复措施** — 为什么这解决了该模式、什么可能仍然出错、保护措施（测试/批准/回滚）。
5. **生成工件** — HCL、迁移块（`moved`、`import`）、CI 变更、策略规则。
6. **在最终确定之前验证** — 运行针对风险层的验证命令。
7. **在末尾发出响应合同**。

## 生成前先诊断

| 故障类别 | 症状 | 主要引用 |
|---------|------|----------|
| **身份变更** | 重构后资源地址变化、`count` 索引变更、缺少 `moved` 块 | [代码模式：count vs for_each](references/code-patterns.md#count-vs-for_each-deep-dive)、[代码模式：moved 块](references/code-patterns.md#moved-blocks-terraform-11)、[代码模式：LLM 错误](references/code-patterns.md#llm-mistake-checklist--code-patterns) |
| **秘密泄露** | 默认值、状态、日志、CI 工件中的秘密 | [安全与合规](references/security-compliance.md)、[代码模式：只写](references/code-patterns.md#write-only-arguments-terraform-111)、[状态管理](references/state-management.md) |
| **破坏范围** | 过大的堆栈、共享生产/非生产状态、不安全的提交 | [状态管理](references/state-management.md)、[模块模式](references/module-patterns.md) |
| **销毁级联** | 目标销毁删除了更多预期之外的内容；引用目标资源的 `locals` 使所有 `for_each` 消费者成为隐式依赖项 | 响应合同：先执行 `plan-destroy`；[状态管理：安全销毁协议](references/state-management.md#safe-destroy-protocol) |
| **CI 漂移** | 本地计划 ≠ CI 计划、未经审查工件的提交、未固定版本 | [CI/CD 工作流](references/ci-cd-workflows.md)、[代码模式：版本](references/code-patterns.md#version-management) |
| **合规差距** | 缺少策略阶段、没有审批模型、没有证据保留 | [安全与合规](references/security-compliance.md)、[CI/CD 工作流](references/ci-cd-workflows.md) |
| **测试盲点** | 计算值的仅计划验证、集合类型索引、模拟/真实混淆 | [测试框架](references/testing-frameworks.md) |
| **状态损坏/恢复** | 卡住的锁、后端迁移、漂移协调 | [状态管理](references/state-management.md) |
| **提供者升级风险** | 引入破坏性变更的提供者升级、未固定的模块 | [代码模式：版本](references/code-patterns.md#version-management)、[模块模式](references/module-patterns.md) |
| **提供者生命周期** | 删除了仍有资源在状态中的提供者、遗弃资源、`removed` 块的使用 | [状态管理：提供者移除](references/state-management.md#provider-removal) |
| **引导/编排滥用** | 使用 `null_resource` + `local-exec` 进行引导、使用 `remote-exec` 进行设置脚本、提供者标准输出在 CI 日志中泄露秘密 | [代码模式：提供者作为最后手段](references/code-patterns.md#provisioners-as-last-resort) |
| **导航/安全重命名盲点** | 从语义上无法定位符号定义/引用、作为盲文替换进行值符号重命名、仅使用 `grep` 的重构遗漏引用、想象的 `rg` 桥接 | [代码智能](references/code-intelligence-lsp.md#terraform-ls-capability-matrix) |
| **跨云/提供者映射** | “X 的 Azure/GCP 对等物是什么”、为每个云选择后端/认证模型 | [状态管理：跨云对等物](references/state-management.md#cross-cloud-equivalents) |

## 何时使用此技能

**激活时：** 创建或审查 Terraform/OpenTofu 配置或模块、设置或调试测试、构建多环境部署、实施 IaC CI/CD、选择模块模式或状态组织、配置或迁移远程状态后端。

**不要用于：** Claude 已经知道的 basic HCL 语法问题、提供者 API 参考（链接到文档）、与 Terraform/OpenTofu 无关的云平台问题。

## 核心原则

### 模块层次结构

| 类型 | 使用场景 | 范围 |
|------|----------|-------|
| **资源模块** | 连接资源的单个逻辑组 | VPC + 子网、SG + 规则 |
| **基础设施模块** | 用于特定目的的资源模块集合 | 一个区域/帐户中的多个资源模块 |
| **组合** | 完整的基础设施 | 跨越多个区域/帐户 |

流程：资源 → 资源模块 → 基础设施模块 → 组合。

### 目录布局

```
environments/   # prod/ staging/ dev/  — 按环境配置
modules/        # networking/ compute/ data/ — 可重用模块
examples/       # minimal/ complete/ — 文档 + 集成固定装置
```

将 **环境** 与 **模块** 分开。使用 `examples/` 作为文档和测试固定装置。保持模块小而单一职责。

参见 [模块模式](references/module-patterns.md) 了解架构原则、命名约定、变量/输出合同。

### 命名约定（摘要）

- 描述性资源名称（`aws_instance.web_server`，而不是 `aws_instance.main`）
- 仅对真正的单例资源保留 `this`
- 以上下文为前缀的变量（`vpc_cidr_block`，而不是 `cidr`）
- 标准文件：`main.tf`、`variables.tf`、`outputs.tf`、`versions.tf`

参见 [模块模式：变量命名](references/module-patterns.md) 和 [代码模式：块排序](references/code-patterns.md#block-ordering--structure) 获取示例。

### 块排序（摘要）

资源块：`count`/`for_each` 首先→ 参数→ `tags`→ `depends_on`→ `lifecycle`。
变量块：`description`→ `type`→ `default`→ `validation`→ `nullable`→ `sensitive`。

参见 [代码模式：块排序 & 结构](references/code-patterns.md#block-ordering--structure) 获取完整规则和示例。

## 测试策略

### 决策矩阵：选择哪种测试方法？

| 情况 | 方法 | 工具 | 成本 |
|------|------|------|------|
| 快速语法检查 | 静态分析 | `validate`、`fmt` | 免费 |
| 提交前验证 | 静态 + 代码检查 | `validate`、`tflint`、`trivy`、`checkov` | 免费 |
| Terraform 1.6+、简单逻辑 | 原生测试框架 | `terraform test` | 免费-低 |
| 1.6 之前，或 Go 专业知识 | 集成测试 | Terratest | 低-中 |
| 安全/合规重点 | 代码即策略 | OPA、Sentinel | 免费 |
| 成本敏感工作流 | 模拟提供者（1.7+） | 原生测试 + 模拟 | 免费 |
| 多云、复杂 | 完整集成 | Terratest + 真实基础设施 | 中-高 |

### 原生测试规则（1.6+）

在编写测试代码之前：通过 Terraform MCP 验证资源模式，以便断言针对真实属性。

- `command = plan` — 快速，仅用于输入派生值
- `command = apply` — 对于 **计算值**（ARN、生成名称）和 **集合类型嵌套块** 是必需的
- 集合类型块不能使用 `[0]` 进行索引——使用 `for` 表达式或通过 `command = apply` 实例化
- 常见的集合类型：S3 加密规则、生命周期转换、IAM 策略声明

参见 [测试框架](references/testing-frameworks.md) 了解静态分析管道、原生测试模式、Terratest 集成、模拟提供者以及完整的 LLM 错误清单。

## Count vs For_Each — 快速规则

| 场景 | 使用 | 原因 |
|------|------|------|
| 布尔条件（创建/不创建） | `count = condition ? 1 : 0` | 可选单例切换 |
| 项目可能被重新排序或删除 | `for_each = toset(list)` | 稳定的资源地址 |
| 通过键引用 | `for_each = map` | 命名访问 |
| 多个命名资源 | `for_each` | 更好的身份稳定性 |

**永远**不要使用列表索引作为长期身份——删除中间元素会重新排序它之后的每个地址。对于决策矩阵、安全迁移剧本、`moved` 块模式以及已知的计划失败情况，参见 [代码模式：count vs for_each](references/code-patterns.md#count-vs-for_each-deep-dive)。

## Locals for Dependency Management

在 `try()` 中使用本地以优先选择条件资源的属性而不是其父资源是一个专业但高价值的模式——它强制正确的删除顺序，而无需显式 `depends_on`。常见用途：VPC + 次要 CIDR 关联 + 子网。

参见 [代码模式：用于依赖管理的 Locals](references/code-patterns.md#locals-for-dependency-management) 获取完整模式和示例。

## 模块开发

标准布局：

```
my-module/
├── README.md       # 使用文档
├── main.tf         # 主要资源
├── variables.tf    # 带描述的输入类型
├── outputs.tf      # 输出值
├── versions.tf     # required_version + required_providers
├── examples/
│   ├── minimal/
│   └── complete/
└── tests/
    └── module_test.tftest.hcl   # 或 Go 用于 Terratest
```

**变量合同**：始终 `description`、始终显式 `type`、使用 `validation` 进行复杂约束、使用 `sensitive = true` 进行秘密、优先使用带类型默认值的 `optional()`（1.3+）而不是未类型的 `map(any)`。

**输出合同**：始终 `description`、标记敏感输出、暴露稳定子集（而不是整个提供者对象）。

参见 [模块模式](references/module-patterns.md) 了解完整的合同模式、模块发布清单和 LLM 错误清单。

## CI/CD

管道阶段：**验证** → **测试** → **计划** → **应用**（带环境保护）。

成本控制：PR 验证上的模拟提供者、仅在 main 或计划上运行真实云集成、标记测试资源、自动清理。

漂移预防：固定运行时和提供者、提交 `.terraform.lock.hcl`、应用来自计划阶段的**已审查计划工件**（不要在应用作业中重新运行 `plan`）、在每条应用路径上运行策略/安全阶段。

参见 [CI/CD 工作流](references/ci-cd-workflows.md) 了解 GitHub Actions、GitLab CI 和 Atlantis 模板以及 LLM 错误清单。

## 安全与合规

**基本检查：**

```bash
trivy config .
checkov -d .
```

**不要：** 将秘密存储在变量或 `.tfvars` 中、使用默认 VPC、跳过加密、开放安全组到 `0.0.0.0/0`、使用内联 `ingress`/`egress` 块在 `aws_security_group` 中。

**要：** 从云秘密管理器（AWS Secrets Manager / Azure Key Vault / GCP Secret Manager）源密钥，或在 1.11+ 上使用 `write_only` 参数、创建专用 VPC、强制加密和 TLS、最小权限 SG、使用 `aws_vpc_security_group_{ingress,egress}_rule` 资源（例如 AWS 提供者 v5+）。

标记变量 `sensitive = true` 仅掩码显示——值仍然存在于状态中。使用 1.11+ 上的 `write_only` / `*_wo`，或通过运行时查找完全将秘密材料从 Terraform 中排除。

参见 [安全与合规](references/security-compliance.md) 了解 trivy/checkov 管道、状态文件强化、合规映射和 LLM 错误清单。

## 状态管理

**在团队或生产中永远不要使用本地状态。** 远程后端提供自动锁定、加密、版本控制、审计日志和安全的协作。

### 选择远程后端

AWS 示例（Azure `azurerm` / GCP `gcs` / TF Cloud 语法：参见 [状态管理：选择远程后端](references/state-management.md#choosing-a-remote-backend)）：

```hcl
terraform {
  backend "s3" {
    bucket        = "my-terraform-state"
    key           = "prod/vpc/terraform.tfstate"
    region        = "us-east-1"
    encrypt       = true
    use_lockfile  = true   # 原生 S3 锁定，1.10+
  }
}
```

在 Terraform < 1.10 时，使用 `dynamodb_table = "terraform-state-lock"` 而不是 `use_lockfile`。Azure 存储、GCS 和 Terraform Cloud 都提供内置锁定——参见状态管理参考中的语法。对于在锁模型之间选择后端，参见 [选择远程后端](references/state-management.md#choosing-a-remote-backend)。

### 状态组织

| 模式 | 使用场景 | 示例路径 |
|------|----------|----------|
| **按环境** | 不同团队每个环境 | `prod/terraform.tfstate`，`staging/...` |
| **按组件** | 独立生命周期 | `prod/vpc/`，`prod/eks/`，`prod/rds/` |
| **混合**（推荐） | 两者都有好处 | `prod/networking/`，`prod/compute/`，`staging/networking/` |

当：不同团队、不同更新节奏、或 >500 资源时拆分状态。当：紧密耦合资源、<100 资源、相同生命周期时合并。

参见 [状态管理](references/state-management.md) 了解锁定、迁移、多团队隔离、灾难恢复和 LLM 错误清单。

## 版本管理

| 组件 | 策略 | 示例 |
|------|------|------|
| Terraform 运行时 | 固定次要版本 | `required_version = "~> 1.9"` |
| 提供者 | 固定主要版本 | `version = "~> 5.0"` |
| 模块（生产） | 固定确切版本 | `version = "5.1.2"` |
| 模块（开发） | 允许补丁 | `version = "~> 5.1"` |

有意提交 `.terraform.lock.hcl`。将提供者/运行时升级与功能变更分开的 PR。参见 [代码模式：版本管理](references/code-patterns.md#version-management) 了解约束语法和升级工作流。

## 现代 Terraform 功能（1.0+）

| 功能 | 最小版本 | 常用用途 |
|------|----------|----------|
| `try()` | 0.13+ | 安全回退、替换 `element(concat())` |
| `nullable = false` | 1.1+ | 防止 `null` 沉默地覆盖默认值 |
| `moved` 块 | 1.1+ | 无需销毁/重新创建的重构 |
| `optional()` 带默认值 | 1.3+ | 带类型的对象属性 |
| `import` 块 | 1.5+ | 声明性导入，可在 VCS 中审查 |
| `check` 块 | 1.5+ | 运行时断言 |
| 原生 `terraform test` | 1.6+ | 内置测试框架 |
| 模拟提供者 | 1.7+ | 免费的单元测试 |
| `removed` 块 | 1.7+ | 声明性资源移除 |
| 提供者定义的函数 | 1.8+ | 提供者特定转换（需要提供者声明函数） |
| 跨变量验证 | 1.9+ | 在 `validation` 块中引用其他 `var.*` |
| `write_only` 参数 | 1.11+ | 秘密永远不会存储在状态中 |
| S3 原生锁文件 | 1.10+ | 无需 DynamoDB 的状态锁定 |

在发出功能之前，验证运行时下限。参见 [代码模式：功能保护表](references/code-patterns.md#feature-guard-table--version-floor--common-llm-errors) 获取完整表格，其中包含每个功能的常见 LLM 错误模式。

## 运行时特定指导

- **Terraform 1.0-1.5（OpenTofu 从 1.6 开始）**：Terratest 用于集成，仅静态分析 + 计划验证（无原生测试）。
- **1.6+**：原生 `terraform test` / `tofu test` 可用——迁移简单的单元测试，保留 Terratest 用于复杂的集成。
- **1.7+**：模拟提供者降低了测试成本——模拟用于单元测试，真实运行用于最终集成。
- **1.10+**：S3 原生锁文件（`use_lockfile`）是新的配置的正确默认值——不再需要 DynamoDB 锁定。
- **1.11+**：`write_only` 参数用于秘密处理，将凭证从状态中排除。
- **Terraform vs OpenTofu**：两者都受支持。对于许可、治理和功能差异，参见 [快速参考：Terraform vs OpenTofu](references/quick-reference.md#terraform-vs-opentofu-comparison)。

## 代码智能 (terraform-ls)

HCL 的语义导航。terraform-ls 是可选的；如果没有它，下面的每一行都会降级为披露的 `rg` + Read 回退。

自包含的 terraform-ls 层面，属于通用的代码智能学科——直接应用下面的行。推荐的伴侣：`code-intelligence` 插件（相同的 `antonbabenko/agent-plugins` 市场上的插件）携带通用学科（位置锚定、退化门、披露格式、反幽灵桥接）并附带 `/code-intelligence:doctor` 用于就绪。如果已安装，则委托其通用协议；此技能在没有它的情况下保持完全自包含。

| 目标 | 使用 | 权衡 |
|------|------|------|
| 查找定义/所有引用 | terraform-ls `goToDefinition` / `findReferences` | 需要 `init` + 位置锚定 |
| 重命名值符号（变量/本地/输出/提供者别名） | 手动：`findReferences` -> 每个文件 Fresh Read -> 编辑 -> `validate` | 没有重命名提供者 |
| 重命名资源/模块地址 | `moved` 块 + `plan` 显示 0 销毁 | 文本重命名强制销毁/重新创建 |
| 精确文本/已知名称/.tfvars/非 HCL | `rg` + Read | 无语义范围 |

✅ 支持：`goToDefinition`，`findReferences`，`documentSymbol`，`hover`，`workspaceSymbol`。
❌ 不支持：`goToImplementation`，调用层次结构，重命名提供者。然后报告它们不存在作为发现。

- ✅ 前置条件：PATH 上的本地 `terraform`/`tofu`，运行 `terraform init`；冷启动可能需要一次重试。
- ✅ LSP 调用是位置锚定的（`file:line:character`）- 首先使用 `rg` 锚定，永远不要仅使用符号名称。
- ❌ 在 [退化门](references/code-intelligence-lsp.md#degradation-gate) 通过之前，不要声称“LSP 故障，使用 rg”。在第一行披露任何工具替代。

深度：[代码智能](references/code-intelligence-lsp.md#terraform-ls-capability-matrix)。

## 引用文件

渐进式披露——此处是基础，深度按需：

- [测试框架](references/testing-frameworks.md) — 静态分析、原生测试、Terratest、模拟提供者
- [模块模式](references/module-patterns.md) — 结构、变量/输出合同、`terraform_remote_state` 规则、发布清单
- [CI/CD 工作流](references/ci-cd-workflows.md) — GitHub Actions、GitLab CI、Atlantis、成本控制
- [安全与合规](references/security-compliance.md) — trivy/checkov、秘密处理、合规映射
- [状态管理](references/state-management.md) — 后端、锁定、迁移、多团队、恢复
- [代码模式](references/code-patterns.md) — 块排序、`count`/`for_each` 深入分析、现代功能、版本管理、locals
- [代码智能](references/code-intelligence-lsp.md) - terraform-ls 功能、位置锚定的调用、手动重命名、退化门
- [快速参考](references/quick-reference.md) — 命令速查表、流程图、故障排除

## 许可证

Apache License 2.0。完整条款见 LICENSE。

**版权所有 © 2026 Anton Babenko**
