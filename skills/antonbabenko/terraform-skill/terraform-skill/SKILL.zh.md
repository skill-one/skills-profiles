---
name: terraform-skill
description: 在编写、审查或调试 Terraform/OpenTofu 模块、测试、CI、扫描或状态操作时使用——通过版本感知的防护措施诊断故障模式（身份变更、密钥、影响范围、CI 分支漂移、状态损坏）。
---

# Terraform 技能指南 for Claude

提供 Terraform 和 OpenTofu 的先诊断后指导方法。核心文件是一个工作流；深度体现在按需加载的引用中。

## 响应契约

每个 Terraform/OpenTofu 响应必须包含：

1. **假设与版本下限** — 运行时（`terraform` 或 `tofu`）、确切版本、提供者、状态后端、执行路径（本地/CI/云/Atlantis）、环境关键性。如果用户未提供，则明确假设状态。
2. **处理的风险类别** — 一个或多个：身份变更、密钥暴露、破坏范围、CI 漂移、合规差距、状态损坏、提供者升级风险、测试盲点。
3. **选择的修复措施与权衡** — 选择了什么、牺牲了什么、为什么。
4. **验证计划** — 针对运行时和风险等级定制的确切命令（`fmt -check`、`validate`、`plan -out`、策略检查）。
5. **回滚说明** — 对于任何破坏性或状态变更操作：如何撤销、保留哪些证据。

在没有经过审查的计划工件和批准的情况下，永远不要推荐直接生产环境应用。

在运行 `terraform destroy`（目标或全部）之前，必须先运行 `terraform plan -destroy` 并向用户展示所有将被删除的资源 — 包括通过 `locals` 或 `for_each` 拉入的隐式依赖项。在进行下一步之前获取明确确认。在销毁时永远不要使用 `-auto-approve`。

## 工作流

1. **捕获执行上下文** — 运行时+版本、提供者、后端、执行路径、环境关键性。
2. **使用下表中的路由表诊断故障模式**。如果意图跨越类别，则加载两个引用。
3. **仅加载匹配的引用文件** — 不要预加载任务不需要的深度。
4. **提出带风险控制的修复措施** — 为什么这能解决该模式、可能仍然出错的地方、护栏（测试/批准/回滚）。
5. **生成工件** — HCL、迁移块（`moved`、`import`）、CI 变更、策略规则。
6. **在最终确定前验证** — 运行针对风险等级定制的验证命令。
7. **在末尾发出响应契约**。

## 生成前先诊断

| 故障类别 | 症状 | 主要引用 |
|----------|------|----------|
| **身份变更** | 重构后资源地址变化、`count` 索引变更、缺少 `moved` 块 | [代码模式：count vs for_each](references/code-patterns.md#count-vs-for_each-deep-dive)、[代码模式：moved 块](references/code-patterns.md#moved-blocks-terraform-11)、[代码模式：LLM 错误](references/code-patterns.md#llm-mistake-checklist--code-patterns) |
| **密钥暴露** | 默认值、状态、日志、CI 工件中的密钥 | [安全与合规](references/security-compliance.md)、[代码模式：只写](references/code-patterns.md#write-only-arguments-terraform-111)、[状态管理](references/state-management.md) |
| **破坏范围** | 过大的堆栈、共享生产/非生产状态、不安全的应用 | [状态管理](references/state-management.md)、[模块模式](references/module-patterns.md) |
| **销毁级联** | 目标销毁删除了超出预期的内容；引用目标资源的 `locals` 使所有 `for_each` 消费者成为隐式依赖项 | 响应契约：先执行 `plan-destroy`；[状态管理：安全销毁协议](references/state-management.md#safe-destroy-protocol) |
| **CI 漂移** | 本地计划 ≠ CI 计划、未经审查的工件应用、未固定版本 | [CI/CD 工作流](references/ci-cd-workflows.md)、[代码模式：版本](references/code-patterns.md#version-management) |
| **合规差距** | 缺少策略阶段、无审批模型、无证据保留 | [安全与合规](references/security-compliance.md)、[CI/CD 工作流](references/ci-cd-workflows.md) |
| **测试盲点** | 计算值的计划仅验证、集合类型索引、模拟/真实混淆 | [测试框架](references/testing-frameworks.md) |
| **状态损坏/恢复** | 卡住的锁、后端迁移、漂移协调 | [状态管理](references/state-management.md) |
| **提供者升级风险** | 引发破坏性变更的提供者升级、未固定的模块 | [代码模式：版本](references/code-patterns.md#version-management)、[模块模式](references/module-patterns.md) |
| **提供者生命周期** | 删除了仍有资源在状态中的提供者、遗弃资源、`removed` 块使用 | [状态管理：提供者移除](references/state-management.md#provider-removal) |
| **引导/编排滥用** | `null_resource` + `local-exec` 用于引导、`remote-exec` 用于设置脚本、提供者标准输出在 CI 日志中泄露密钥 | [代码模式：作为最后手段使用提供者](references/code-patterns.md#provisioners-as-last-resort) |
| **导航/安全重命名盲点** | 语义上无法定位符号定义/引用、值符号重命名作为盲文替换、仅使用 grep 的重构遗漏引用、想象的 `rg` 桥接 | [代码智能](references/code-intelligence-lsp.md#terraform-ls-capability-matrix) |
| **跨云/提供者映射** | "X 的 Azure/GCP 对等物是什么"、按云选择后端/认证模型 | [状态管理：跨云等价物](references/state-management.md#cross-cloud-equivalents) |

## 何时使用此技能

**激活时：** 创建或审查 Terraform/OpenTofu 配置或模块、设置或调试测试、结构化多环境部署、实施 IaC CI/CD、选择模块模式或状态组织、配置或迁移远程状态后端。

**不用于：** Claude 已知的 HCL 语法问题、提供者 API 参考（链接到文档）、与 Terraform/OpenTofu 无关的云平台问题。

## 核心原则

### 模块层次结构

| 类型 | 使用场景 | 范围 |
|------|----------|------|
| **资源模块** | 连接资源的一个逻辑组 | VPC + 子网、SG + 规则 |
| **基础设施模块** | 用于特定目的的资源模块集合 | 一个区域/帐户中的多个资源模块 |
| **组合** | 完整的基础设施 | 跨越多个区域/帐户 |

流程：资源 → 资源模块 → 基础设施模块 → 组合。

### 目录布局

```
environments/   # prod/ staging/ dev/  — 按环境配置
modules/        # networking/ compute/ data/ — 可重用模块
examples/       # minimal/ complete/ — 文档 + 集成固定件
```

将 **环境** 与 **模块** 分开。使用 `examples/` 作为文档和测试固定件。保持模块小且单一职责。

参见 [模块模式](references/module-patterns.md) 了解架构原则、命名约定、变量/输出契约。

### 命名约定（摘要）

- 描述性资源名称（`aws_instance.web_server`，而不是 `aws_instance.main`）
- 仅对真正的单例资源保留 `this`
- 以上下文为前缀的变量（`vpc_cidr_block`，而不是 `cidr`）
- 标准文件：`main.tf`、`variables.tf`、`outputs.tf`、`versions.tf`

参见 [模块模式：变量命名](references/module-patterns.md) 和 [代码模式：块排序](references/code-patterns.md#block-ordering--structure) 获取示例。

### 块排序（摘要）

资源块：`count`/`for_each` 首先→参数→`tags`→`depends_on`→`lifecycle`。
变量块：`description`→`type`→`default`→`validation`→`nullable`→`sensitive`。

参见 [代码模式：块排序 & 结构](references/code-patterns.md#block-ordering--structure) 获取完整规则和示例。

## 测试策略

### 决策矩阵：选择哪种测试方法？

| 情况 | 方法 | 工具 | 成本 |
|------|------|------|------|
| 快速语法检查 | 静态分析 | `validate`、`fmt` | 免费 |
| 提交前验证 | 静态+Lint | `validate`、`tflint`、`trivy`、`checkov` | 免费 |
| Terraform 1.6+、简单逻辑 | 原生测试框架 | `terraform test` | 免费-低 |
| 1.6 之前，或 Go 专业知识 | 集成测试 | Terratest | 低-中 |
| 安全/合规重点 | 策略即代码 | OPA、Sentinel | 免费 |
| 成本敏感工作流 | 模拟提供者（1.7+） | 原生测试+模拟 | 免费 |
| 多云、复杂 | 完整集成 | Terratest + 真实基础设施 | 中-高 |

### 原生测试规则（1.6+）

在编写测试代码之前：通过 Terraform MCP 验证资源模式，以便断言针对真实属性。

- `command = plan` — 快速，仅用于输入派生值
- `command = apply` — 必须用于**计算值**（ARN、生成名称）和**集合类型嵌套块**
- 集合类型块不能使用 `[0]` 索引 — 使用 `for` 表达式或通过 `command = apply` 实例化
- 常见集合类型：S3 加密规则、生命周期转换、IAM 策略语句

参见 [测试框架](references/testing-frameworks.md) 了解静态分析管道、原生测试模式、Terratest 集成、模拟提供者和完整的 LLM 错误清单。

## Count vs For_Each — 快速规则

| 场景 | 使用 | 原因 |
|------|------|------|
| 布尔条件（创建/不创建） | `count = condition ? 1 : 0` | 可选单例切换 |
| 项目可能被重新排序或删除 | `for_each = toset(list)` | 稳定的资源地址 |
| 通过键引用 | `for_each = map` | 命名访问 |
| 多个命名资源 | `for_each` | 更好的身份稳定性 |

**永远**不要使用列表索引作为长期身份 — 删除中间元素会重新排序它之后的每个地址。对于决策矩阵、安全迁移剧本、`moved` 块模式以及已知的计划失败情况，参见 [代码模式：count vs for_each](references/code-patterns.md#count-vs-for_each-deep-dive)。

## Locals 用于依赖管理

在 `local` 中使用 `try()` 以优先选择条件资源的属性而不是其父级是一个专业但高价值模式 — 它强制正确的删除顺序，而无需显式 `depends_on`。常见用途：VPC + 次要 CIDR 关联 + 子网。

参见 [代码模式：用于依赖管理的 Locals](references/code-patterns.md#locals-for-dependency-management) 获取完整模式和示例。

## 模块开发

标准布局：

```
my-module/
├── README.md       # 使用文档
├── main.tf         # 主要资源
├── variables.tf    # 带描述的定型输入
├── outputs.tf      # 输出值
├── versions.tf     # required_version + required_providers
├── examples/
│   ├── minimal/
│   └── complete/
└── tests/
    └── module_test.tftest.hcl   # 或 Go 用于 Terratest
```

**变量契约**：始终 `description`、始终显式 `type`、使用 `validation` 进行复杂约束、使用 `sensitive = true` 进行密钥、优先使用带定型默认值的 `optional()`（1.3+）而不是未定型的 `map(any)`。

**输出契约**：始终 `description`、标记敏感输出、暴露稳定子集（而不是整个提供者对象）。

参见 [模块模式](references/module-patterns.md) 获取完整的契约模式、模块发布清单和 LLM 错误清单。

## CI/CD

管道阶段：**验证** → **测试** → **计划** → **应用**（带环境保护）。

成本控制：PR 验证上的模拟提供者、仅在主分支或计划上使用真实云集成、标记测试资源、自动清理。

漂移预防：固定运行时和提供者、提交 `.terraform.lock.hcl`、应用来自计划阶段的**已审查计划工件**（不要在应用作业中重新运行 `plan`）、在每条应用路径上运行策略/安全阶段。

参见 [CI/CD 工作流](references/ci-cd-workflows.md) 了解 GitHub Actions、GitLab CI 和 Atlantis 模板以及 LLM 错误清单。

## 安全与合规

**必要检查：**

```bash
trivy config .
checkov -d .
```

**不要：** 将密钥存储在变量或 `.tfvars` 中、使用默认 VPC、跳过加密、安全组对 `0.0.0.0/0` 开放、使用内联 `ingress`/`egress` 块在 `aws_security_group` 中。

**要：** 从云密钥管理器（AWS Secrets Manager / Azure Key Vault / GCP Secret Manager）源密钥或使用 1.11+ 上的 `write_only` 参数、创建专用 VPC、强制加密和 TLS、最小权限 SG、使用单独的 `aws_vpc_security_group_{ingress,egress}_rule` 资源（例如 AWS 提供者 v5+）。

将变量 `sensitive = true` 仅掩码显示 — 值仍然存在于状态中。使用 1.11+ 上的 `write_only` / `*_wo`，或通过运行时查找完全将密钥材料从 Terraform 中排除。

参见 [安全与合规](references/security-compliance.md) 了解 trivy/checkov 管道、状态文件加固、合规映射和 LLM 错误清单。

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

在 Terraform < 1.10 时，使用 `dynamodb_table = "terraform-state-lock"` 而不是 `use_lockfile`。Azure 存储、GCS 和 Terraform Cloud 都提供内置锁定 — 参见状态管理参考以获取语法。对于在后端之间选择及其锁定模型，参见 [选择远程后端](references/state-management.md#choosing-a-remote-backend)。

### 状态组织

| 模式 | 使用场景 | 示例路径 |
|------|----------|----------|
| **按环境** | 不同团队每个环境 | `prod/terraform.tfstate`、`staging/...` |
| **按组件** | 独立生命周期 | `prod/vpc/`、`prod/eks/`、`prod/rds/` |
| **混合**（推荐） | 两者优点 | `prod/networking/`、`prod/compute/`、`staging/networking/` |

当：不同团队、不同更新节奏、或 >500 资源时拆分状态。当：紧密耦合资源、<100 资源、相同生命周期时合并状态。

参见 [状态管理](references/state-management.md) 了解锁定、迁移、多团队隔离、灾难恢复和 LLM 错误清单。

## 版本管理

| 组件 | 策略 | 示例 |
|------|------|------|
| Terraform 运行时 | 固定次要版本 | `required_version = "~> 1.9"` |
| 提供者 | 固定主版本 | `version = "~> 5.0"` |
| 模块（生产） | 固定确切版本 | `version = "5.1.2"` |
| 模块（开发） | 允许补丁 | `version = "~> 5.1"` |

有意提交 `.terraform.lock.hcl`。将提供者/运行时升级与功能变更分开在单独的 PR 中。参见 [代码模式：版本管理](references/code-patterns.md#version-management) 了解约束语法和升级工作流。

## 现代 Terraform 功能（1.0+）

| 功能 | 最小版本 | 常见用途 |
|------|----------|----------|
| `try()` | 0.13+ | 安全回退，替换 `element(concat())` |
| `nullable = false` | 1.1+ | 防止 `null` 沉默地覆盖默认值 |
| `moved` 块 | 1.1+ | 无需销毁/重新创建的重构 |
| `optional()` 带默认值 | 1.3+ | 定型对象属性 |
| `import` 块 | 1.5+ | 声明性导入，可在 VCS 中审查 |
| `check` 块 | 1.5+ | 运行时断言 |
| 原生 `terraform test` | 1.6+ | 内置测试框架 |
| 模拟提供者 | 1.7+ | 无成本的单元测试 |
| `removed` 块 | 1.7+ | 声明性资源移除 |
| 提供者定义的函数 | 1.8+ | 提供者特定转换（需要提供者声明函数） |
| 跨变量验证 | 1.9+ | 在 `validation` 块中引用其他 `var.*` |
| `write_only` 参数 | 1.11+ | 密钥永远不会存储在状态中 |
| S3 原生锁文件 | 1.10+ | 无需 DynamoDB 的状态锁定 |

在发布功能之前，请验证运行时最低版本。有关每个功能针对常见LLM错误模式的完整表格，请参阅 [代码模式：功能保护表](references/code-patterns.md#feature-guard-table--version-floor--common-llm-errors)。

## 运行时特定指南

- **Terraform 1.0-1.5（OpenTofu从1.6开始）**：使用Terratest进行集成测试，仅进行静态分析+计划验证（无原生测试）。
- **1.6+**：可用原生 `terraform test` / `tofu test` — 迁移简单的单元测试，保留Terratest用于复杂的集成测试。
- **1.7+**：模拟提供程序可降低测试成本 — 单元测试使用模拟，最终集成测试使用真实运行。
- **1.10+**：S3原生锁文件（`use_lockfile`）是新的配置的正确默认选项 — 不再需要DynamoDB锁定。
- **1.11+**：`write_only` 参数用于密钥处理，将凭证排除在状态之外。
- **Terraform与OpenTofu**：两者都受支持。有关许可、治理和功能差异，请参阅 [快速参考：Terraform与OpenTofu](references/quick-reference.md#terraform-vs-opentofu-comparison)。

## 代码智能（terraform-ls）

HCL的语义导航。terraform-ls是可选的；没有它，以下每一行都会降级为公开的 `rg` + 读取回退。

一个通用的代码智能学科的独立terraform-ls层 — 直接应用以下行。推荐的伴侣：`code-intelligence`插件（在相同的 `antonbabenko/agent-plugins` 市场中）携带通用学科（位置锚定、降级门、披露格式、反幽灵遮罩）并附带 `/code-intelligence:doctor` 用于就绪。如果已安装，则使用其通用协议；没有它，这项技能将保持完全独立。

| 目标 | 使用 | 交易成本 |
|------|-----|----------|
| 查找定义 / 所有引用 | terraform-ls `goToDefinition` / `findReferences` | 需要 `init` + 位置锚定 |
| 重命名值符号（变量/本地/输出/提供程序别名） | 手动：`findReferences` -> 每个文件的新鲜读取 -> 编辑 -> `validate` | 无重命名提供程序 |
| 重命名资源/模块地址 | `moved`块 + `plan`显示0销毁 | 文本重命名强制销毁/重新创建 |
| 精确文本 / 已知名称 / `.tfvars` / 非-HCL | `rg` + 读取 | 无语义范围 |

✅ 支持：`goToDefinition`、`findReferences`、`documentSymbol`、`hover`、`workspaceSymbol`。
❌ 不支持：`goToImplementation`、调用层次结构、重命名提供程序。不要调用它们，然后报告它们的缺失。

- ✅ 前置条件：本地 `terraform`/`tofu` 在PATH上，运行 `terraform init`；冷启动可能需要重试一次。
- ✅ LSP调用是位置锚定的（`file:line:character`）- 首先使用 `rg` 锚定，绝不能仅使用符号名。
- ❌ 在 [降级门](references/code-intelligence-lsp.md#degradation-gate) 通过之前，不要声称 "LSP损坏，使用rg"；在第一行披露任何工具替换。

深度：[代码智能](references/code-intelligence-lsp.md#terraform-ls-capability-matrix)。

## 参考文件

渐进式披露 — 基础知识在此处，按需深入：

- [测试框架](references/testing-frameworks.md) — 静态分析、原生测试、Terratest、模拟提供程序
- [模块模式](references/module-patterns.md) — 结构、变量/输出契约、`terraform_remote_state`规则、发布清单
- [CI/CD工作流](references/ci-cd-workflows.md) — GitHub Actions、GitLab CI、Atlantis、成本控制
- [安全与合规](references/security-compliance.md) — trivy/checkov、密钥处理、合规映射
- [状态管理](references/state-management.md) — 后端、锁定、迁移、多团队、恢复
- [代码模式](references/code-patterns.md) — 块排序、`count`/`for_each`深入、现代功能、版本管理、locals
- [代码智能](references/code-intelligence-lsp.md) - terraform-ls功能、位置锚定调用、手动重命名、降级门
- [快速参考](references/quick-reference.md) — 命令速查表、流程图、故障排除

## 许可证

Apache License 2.0。有关完整条款，请参阅 LICENSE。

**版权所有 © 2026 Anton Babenko**
