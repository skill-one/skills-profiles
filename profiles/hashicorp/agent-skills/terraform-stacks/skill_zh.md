# Terraform 堆栈

Terraform 堆栈通过在传统 Terraform 模块之上提供配置层，简化了大规模基础设施的供应和管理。堆栈支持跨环境、区域和云账户的多个组件的声明式编排。

## 核心概念

**堆栈**: 由组件和部署组成的完整基础设施单元，可以一起管理。

**组件**: 围绕 Terraform 模块定义基础设施片段的抽象。每个组件指定一个源模块、输入和提供者。

**部署**: 堆栈中所有组件的特定输入值实例。使用部署来管理不同环境（dev/staging/prod）、区域或云账户。

**堆栈语言**: 一种基于 HCL 的独立语言（不是常规的 Terraform HCL），具有不同的代码块和文件扩展名。

## 文件结构

Terraform 堆栈使用特定的文件扩展名：

- **组件配置**: `.tfcomponent.hcl`
- **部署配置**: `.tfdeploy.hcl`
- **提供者锁定文件**: `.terraform.lock.hcl`（由 CLI 生成）

所有配置文件都必须位于堆栈存储库的根级别。HCP Terraform 按依赖顺序处理所有文件。

### 推荐的文件组织

```
my-stack/
├── .terraform-version               # 此堆栈所需的 Terraform 版本
├── variables.tfcomponent.hcl        # 变量声明
├── providers.tfcomponent.hcl        # 提供者配置
├── components.tfcomponent.hcl       # 组件定义
├── outputs.tfcomponent.hcl          # 堆栈输出
├── deployments.tfdeploy.hcl         # 部署定义
├── .terraform.lock.hcl              # 提供者锁定文件（生成）
└── modules/                         # 本地模块（可选 - 仅在使用本地模块时）
    ├── s3/
    └── compute/
```

**注意**: `modules/` 目录仅在使用本地模块源时需要。组件可以引用来自：
- 本地文件路径: `./modules/vpc`
- 公共注册中心: `terraform-aws-modules/vpc/aws`
- 私有注册中心: `app.terraform.io/<org-name>/vpc/aws`
- Git: `git::https://github.com/org/repo.git//path?ref=v1.0.0`

HCP Terraform 按依赖顺序处理所有 `.tfcomponent.hcl` 和 `.tfdeploy.hcl` 文件。

## 所需的 Terraform 版本 (.terraform-version)

使用 Terraform v1.13.x 或更高版本以访问堆栈 CLI 插件并运行 terraform stacks CLI 命令。首先在堆栈的根目录中添加一个 .terraform-version 文件以指定堆栈所需的 Terraform 版本。例如，以下文件指定了 Terraform v1.14.5：

```
1.14.5
```

## 组件配置 (.tfcomponent.hcl)

### 变量块

声明堆栈配置的输入变量。变量必须定义一个 `type` 字段，并且不支持 `validation` 参数。

```hcl
variable "aws_region" {
  type        = string
  description = "AWS 区域用于部署"
  default     = "us-west-1"
}

variable "identity_token" {
  type        = string
  description = "OIDC 身份令牌"
  ephemeral   = true  # 不会持久化到状态文件
}

variable "instance_count" {
  type     = number
  nullable = false
}
```

**重要**: 使用 `ephemeral = true` 来处理凭证和令牌（身份令牌、API 密钥、密码），以防止它们持久化到状态文件中。使用 `stable` 来处理需要跨运行持久化的较长时间存在的值，例如许可证密钥。

### 必需提供者块

```hcl
required_providers {
  aws = {
    source  = "hashicorp/aws"
    version = "~> 6.0"
  }
  random = {
    source  = "hashicorp/random"
    version = "~> 3.5.0"
  }
}
```

### 提供者块

提供者块与传统 Terraform 不同：

1. 支持 `for_each` 伪参数
2. 在块头中定义别名（而不是作为参数）
3. 通过 `config` 块接受配置

**单个提供者配置:**

```hcl
provider "aws" "this" {
  config {
    region = var.aws_region
    assume_role_with_web_identity {
      role_arn           = var.role_arn
      web_identity_token = var.identity_token
    }
  }
}
```

**使用 for_each 的多个提供者配置:**

```hcl
provider "aws" "configurations" {
  for_each = var.regions

  config {
    region = each.value
    assume_role_with_web_identity {
      role_arn           = var.role_arn
      web_identity_token = var.identity_token
    }
  }
}
```

**认证最佳实践**: 将 **工作负载身份**（OIDC）作为堆栈的首选认证方法。这种方法：
- 避免使用长期存在的静态凭证
- 提供每个部署运行的范围有限的临时凭证
- 与云提供商 IAM（AWS IAM 角色和策略、Azure 管理身份、GCP 服务账户）集成
- 无需平台管理的环境变量

使用 `identity_token` 块和 `assume_role_with_web_identity` 在提供者配置中配置工作负载身份。有关 AWS、Azure 和 GCP 的详细设置说明，请参阅：https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials

### 组件块

每个堆栈至少需要一个组件块。为要在堆栈中包含的每个模块添加一个组件。组件从本地路径、注册中心或 Git 引用模块。

```hcl
component "vpc" {
  source  = "app.terraform.io/my-org/vpc/aws"  # 本地、注册中心或 Git URL
  version = "2.1.0"          # 对于注册中心模块

  inputs = {
    cidr_block  = var.vpc_cidr
    name_prefix = var.name_prefix
  }

  providers = {
    aws = provider.aws.this
  }
}
```

有关依赖项、for_each、注册中心模块、Git 源等示例，请参阅 `references/component-blocks.md`。

**要点:**
- 引用输出: `component.<name>.<output>` 或 `component.<name>[key].<output>` 用于 for_each
- 依赖项自动从组件引用推断
- 使用 for 表达式聚合: `[for x in component.s3 : x.bucket_name]`
- 对于具有 `for_each` 的组件，引用特定实例: `component.<name>[each.value].<output>`
- 提供者引用是普通值: `provider.<type>.<alias>` 或 `provider.<type>.<alias>[each.value]`

### 输出块

输出需要一个 `type` 参数，并且不支持 `preconditions`:

```hcl
output "vpc_id" {
  type        = string
  description = "VPC ID"
  value       = component.vpc.vpc_id
}

output "endpoint_urls" {
  type      = map(string)
  value     = {
    for region, comp in component.api : region => comp.endpoint_url
  }
  sensitive = false
}
```

### Locals 块

Locals 块在 `.tfcomponent.hcl` 和 `.tfdeploy.hcl` 文件中工作方式相同：

```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform Stacks"
    Project     = var.project_name
  }

  region_config = {
    for region in var.regions : region => {
      name_suffix = "${var.environment}-${region}"
    }
  }
}
```

### Removed 块

用于从堆栈中安全地移除组件。HCP Terraform 需要组件的提供者来移除它。

```hcl
removed {
  from   = component.old_component
  source = "./modules/old-module"

  providers = {
    aws = provider.aws.this
  }
}
```

## 部署配置 (.tfdeploy.hcl)

### 身份令牌块

为 OIDC 认证生成 JWT 令牌：

```hcl
identity_token "aws" {
  audience = ["aws.workload.identity"]
}

identity_token "azure" {
  audience = ["api://AzureADTokenExchange"]
}
```

在部署中引用令牌，使用 `identity_token.<name>.jwt`

### Store 块

访问 HCP Terraform 变量集：

```hcl
store "varset" "aws_credentials" {
  id       = "varset-ABC123"  # 或者使用: name = "varset_name"
  source   = "tfc-cloud-shared"
  category = "terraform"      # 或者使用: category = "env" 用于环境变量
}

deployment "production" {
  inputs = {
    aws_access_key = store.varset.aws_credentials.AWS_ACCESS_KEY_ID
  }
}
```

用于集中管理凭证并在堆栈之间共享变量。有关详细信息，请参阅 `references/deployment-blocks.md`。

### 部署块

定义部署实例（最小 1 个，最大每个堆栈 20 个）：

```hcl
deployment "production" {
  inputs = {
    aws_region     = "us-west-1"
    instance_count = 3
    role_arn       = local.role_arn
    identity_token = identity_token.aws.jwt
  }
}

# 为不同环境创建多个部署
deployment "development" {
  inputs = {
    aws_region     = "us-east-1"
    instance_count = 1
    name_suffix    = "dev"
    role_arn       = local.role_arn
    identity_token = identity_token.aws.jwt
  }
}
```

**要销毁部署**: 设置 `destroy = true`，上传配置，批准销毁运行，然后删除部署块。有关详细信息，请参阅 `references/deployment-blocks.md`。

### 部署组块

将部署组合在一起以共享设置（HCP Terraform 高级版本功能）。免费/标准版本使用默认组 `{deployment-name}_default`。

```hcl
deployment_group "canary" {
  auto_approve_checks = [deployment_auto_approve.safe_changes]
}

deployment "dev" {
  inputs = { /* ... */ }
  deployment_group = deployment_group.canary
}
```

多个部署可以引用同一个组。有关详细信息，请参阅 `references/deployment-blocks.md`。

### 部署自动批准块

定义自动批准部署计划规则（HCP Terraform 高级版本功能）：

```hcl
deployment_auto_approve "safe_changes" {
  deployment_group = deployment_group.canary

  check {
    condition = context.plan.applyable
    reason    = "Cannot auto-approve plans with resource deletions"
  }
}
```

**可用的上下文变量**: `context.plan.applyable`, `context.plan.changes.add/change/remove/total`, `context.success`

**注意**: `orchestrate` 块已弃用。使用 `deployment_group` 和 `deployment_auto_approve` 代替。

有关所有上下文变量和模式的详细信息，请参阅 `references/deployment-blocks.md`。

### 发布输出和上游输入块

通过从一个堆栈发布输出并在另一个堆栈中消费它们来链接堆栈：

```hcl
# 在网络堆栈中 - 发布输出
publish_output "vpc_id_network" {
  type  = string
  value = deployment.network.vpc_id
}

# 在应用程序堆栈中 - 消费输出
upstream_input "network_stack" {
  type   = "stack"
  source = "app.terraform.io/my-org/my-project/networking-stack"
}

deployment "app" {
  inputs = {
    vpc_id = upstream_input.network_stack.vpc_id_network
  }
}
```

有关完整文档和示例，请参阅 `references/linked-stacks.md`。

## Terraform Stacks CLI

**注意**: Terraform Stacks 自 Terraform CLI v1.13+ 起已正式发布 (GA)。Stacks 现在计入 HCP Terraform 的资源管理 (RUM)。

### 初始化和验证

```bash
terraform stacks init              # 下载提供者、模块，生成锁定文件
terraform stacks providers-lock    # 重新生成锁定文件（如果需要添加平台）
terraform stacks validate          # 检查语法而不上传
```

### 部署工作流

**重要**: 没有 `plan` 或 `apply` 命令。上传配置会自动触发部署运行。

```bash
# 1. 上传配置（触发部署运行）
terraform stacks configuration upload

# 2. 监控部署
terraform stacks deployment-run list                          # 列出运行（非交互式）
terraform stacks deployment-group watch -deployment-group=... # 流式传输状态更新

# 3. 批准部署（如果未配置自动批准）
terraform stacks deployment-run approve-all-plans -deployment-run-id=...
terraform stacks deployment-group approve-all-plans -deployment-group=...
terraform stacks deployment-run cancel -deployment-run-id=...  # 如有必要取消
```

### 配置管理

```bash
terraform stacks configuration list                    # 列出配置版本
terraform stacks configuration fetch -configuration-id=...  # 下载配置
terraform stacks configuration watch                   # 监控上传状态
```

### 其他命令

```bash
terraform stacks create              # 创建新堆栈（交互式）
terraform stacks fmt                 # 格式化堆栈文件
terraform stacks list                # 显示所有堆栈
terraform stacks version             # 显示版本
terraform stacks deployment-group rerun -deployment-group=...  # 重新运行部署
```

## 使用 HCP Terraform API 监控部署

对于自动化、CI/CD 或非交互式环境（如 AI 代理）中的程序化监控，请使用 HCP Terraform API 而不是 CLI 监控命令。API 提供用于以下方面的端点：
- 配置状态和验证
- 部署组摘要
- 部署运行状态
- 部署步骤详细信息（计划/应用）
- 带文件位置和代码片段的错误诊断
- 通过工件端点访问堆栈输出

**要点:**
- CLI 监控命令无限流式传输，不适用于自动化
- 使用工件端点检索堆栈输出: `GET /api/v2/stack-deployment-steps/{step-id}/artifacts?name=apply-description`
- 诊断端点需要 `stack_deployment_step_id` 查询参数
- 工件端点返回 HTTP 307 重定向（使用 `curl -L`）

有关完整 API 工作流、身份验证、轮询最佳实践和示例脚本，请参阅 `references/api-monitoring.md`。

## 常见模式

**组件依赖**: 当一个组件引用另一个组件的输出时（例如，`subnet_ids = component.vpc.private_subnet_ids`），依赖项会自动推断。

**多区域部署**: 使用 `for_each` 在提供者和组件上部署到多个区域。每个区域都有自己的提供者配置和组件实例。

**延迟更改**: 堆栈支持延迟更改以处理依赖项，其中值仅在应用后才知道。这使复杂的组件部署成为可能，其中一些资源依赖于其他组件的运行时值（集群端点、生成的密码等）。

有关包括多区域部署、组件依赖、延迟更改模式和链接堆栈的完整示例，请参阅 `references/examples.md`。

## 最佳实践

1. **组件粒度**: 为共享生命周期逻辑基础设施单元创建组件
2. **模块兼容性**:
   - 与堆栈一起使用的模块不能包含提供者块（在堆栈配置中配置提供者）
   - **在生产堆栈中使用前测试公共注册中心模块** - 一些模块可能与堆栈不兼容
   - 如果模块兼容性不确定，考虑使用原始资源进行关键基础设施
   - 示例: 发现一些 terraform-aws-modules 版本与堆栈不兼容（例如，ALB 和 ECS 模块）
3. **状态隔离**: 每个部署都有自己的隔离状态
4. **输入变量**: 使用变量来处理跨部署不同的值；使用 locals 来处理共享值
5. **提供者锁定文件**: 始终生成并提交 `.terraform.lock.hcl` 到版本控制
6. **命名约定**: 为组件和部署使用描述性名称
7. **部署组**: 您可以将部署组织成部署组。部署组支持自动批准规则、逻辑组织，并为扩展提供基础。部署组是 HCP Terraform 高级版本功能
8. **测试**: 在生产部署之前在 dev/staging 部署中测试堆栈配置

## 故障排除

**循环依赖**: 重构以打破循环引用或使用中间组件。

**部署销毁**: 无法从 UI 销毁。在部署块中设置 `destroy = true`，上传配置，然后 HCP Terraform 创建销毁运行。

**空诊断**: 向诊断 API 请求添加必需的 `stack_deployment_step_id` 查询参数。

**模块兼容性**: 在生产使用前测试公共注册中心模块。一些模块可能与堆栈不兼容。

## 参考

有关详细文档，请参阅：
- `references/component-blocks.md` - 完整组件块参考，包括所有参数和语法
- `references/deployment-blocks.md` - 完整部署块参考，包括所有配置选项
- `references/linked-stacks.md` - 发布输出和上游输入以链接堆栈
- `references/examples.md` - 多区域和组件依赖的完整工作示例
- `references/api-monitoring.md` - 程序化监控和自动化的完整 API 工作流
- `references/troubleshooting.md` - 详细故障排除指南，包括常见问题和解决方案
