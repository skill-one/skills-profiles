# 技能：重构模块

## 概述
该技能指导 AI 代理将单体 Terraform 配置转换为遵循 HashiCorp 模块设计原则和社区最佳实践的可重用、可维护模块。

## 能力声明
代理将分析现有 Terraform 代码，并将其系统性地重构为具有以下结构的良好模块：
- 清晰的接口契约（变量和输出）
- 正确的封装和抽象
- 版本控制和文档
- 测试框架
- 现有状态的迁移路径

## 前置条件
- 需要重构的现有 Terraform 配置
- 对资源依赖关系的理解
- 通过 `terraform state list` / `terraform show -json` 访问以检查当前状态（用于迁移规划）
- 了解模块注册表模式

## 输入参数

| 参数 | 类型 | 是否必需 | 描述 |
|-----------|------|----------|-------------|
| `source_directory` | string | 是 | 现有 Terraform 配置的路径 |
| `module_name` | string | 是 | 新模块的名称 |
| `abstraction_level` | string | 否 | "简单"、"中级"、"高级"（默认：中级） |
| `preserve_state` | boolean | 是 | 是否保持状态兼容性 |
| `target_registry` | string | 否 | 目标模块注册表（本地、私有、公共） |

## 执行步骤

### 1. 分析阶段
```markdown
**识别重构候选**
- 按逻辑功能分组资源
- 识别重复模式
- 映射资源依赖关系
- 检测配置耦合
- 分析变量使用模式

**复杂度评估**
- 计算资源关系数量
- 衡量变量传播深度
- 识别跨资源引用
- 评估状态迁移复杂度
```

### 2. 模块设计

#### 接口设计
```hcl
# 定义清晰的输入契约
variable "network_config" {
  description = "网络配置参数"
  type = object({
    cidr_block         = string
    availability_zones = list(string)
    enable_nat         = bool
  })

  validation {
    condition     = can(cidrhost(var.network_config.cidr_block, 0))
    error_message = "CIDR 块必须是有效的 IPv4 CIDR。"
  }
}

# 定义输出契约
output "vpc_id" {
  description = "创建的 VPC ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "私有子网 ID 列表"
  value       = { for k, v in aws_subnet.private : k => v.id }
}
```

#### 封装策略
```markdown
**模块中应包含的内容：**
- 紧密耦合的资源（VPC + 子网）
- 具有共享生命周期的资源
- 具有清晰边界的配置

**应保持独立的内容：**
- 跨领域关注（监控、标记）
- 具有不同生命周期的资源
- 提供商特定配置
```

### 3. 代码转换

#### 转换前：单体配置
```hcl
# main.tf (单体)
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "production-vpc"
    Environment = "prod"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "public-subnet-1"
    Type = "public"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "public-subnet-2"
    Type = "public"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "production-igw"
  }
}

# ...更多重复的子网和路由资源
```

#### 转换后：模块化结构
```hcl
# modules/vpc/main.tf
locals {
  subnet_count = length(var.availability_zones)
}

resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    var.tags,
    {
      Name = var.name
    }
  )
}

resource "aws_subnet" "public" {
  for_each = var.create_public_subnets ? toset(var.availability_zones) : []

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.cidr_block, 8, index(var.availability_zones, each.value))
  availability_zone       = each.value
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-public-${each.value}"
      Type = "public"
    }
  )
}

resource "aws_internet_gateway" "main" {
  count  = var.create_public_subnets ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-igw"
    }
  )
}

# modules/vpc/variables.tf
variable "name" {
  description = "所有资源的名称前缀"
  type        = string
}

variable "cidr_block" {
  description = "VPC CIDR 块"
  type        = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "必须是有效的 IPv4 CIDR 块。"
  }
}

variable "availability_zones" {
  description = "可用区列表"
  type        = list(string)
}

variable "create_public_subnets" {
  description = "是否创建公共子网"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "在 VPC 中启用 DNS 域名"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "在 VPC 中启用 DNS 支持"
  type        = bool
  default     = true
}

variable "tags" {
  description = "应用于所有资源的标签"
  type        = map(string)
  default     = {}
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "VPC CIDR 块"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "可用区到公共子网 ID 的映射"
  value       = { for k, v in aws_subnet.public : k => v.id }
}

output "internet_gateway_id" {
  description = "互联网网关 ID"
  value       = try(aws_internet_gateway.main[0].id, null)
}

# 使用模块的根配置
module "vpc" {
  source = "./modules/vpc"

  name               = "production"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
```

### 4. 状态迁移

#### 检查当前状态
在编写 `moved` 块或 `state mv` 命令之前，检查当前状态以映射现有资源地址。优先选择文档化、稳定且更高效的命令，而不是读取原始状态文件：

```bash
# 列出当前资源地址（`moved` / `state mv` 的输入）
terraform state list

# 当需要时检查解析后的属性值
terraform show -json | jq '.values.root_module'
```

`terraform show -json` 需要安装提供者（`terraform init`），因为它根据提供者模式渲染值。**仅在**提供者不可用且无法运行 `init`、只需要粗略信息（地址、输出、`serial`/`lineage`）或必须避免执行 Terraform 时才回退到原始状态（`terraform state pull` / `terraform.tfstate`）。**避免解析原始的版本 4 状态格式作为稳定接口。** **注意：** 状态在每种格式中都包含明文敏感值——**永远不要**将状态内容输出到日志或输出中。

#### 生成迁移计划
```hcl
# migration.tf
# 使用 moved 块进行状态重构（Terraform 1.1+）

moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.main
}

moved {
  from = aws_subnet.public_1
  to   = module.vpc.aws_subnet.public["us-east-1a"]
}

moved {
  from = aws_subnet.public_2
  to   = module.vpc.aws_subnet.public["us-east-1b"]
}

moved {
  from = aws_internet_gateway.main
  to   = module.vpc.aws_internet_gateway.main[0]
}
```

#### 手动状态迁移（1.1 之前）
```bash
# 生成状态迁移命令
terraform state mv aws_vpc.main module.vpc.aws_vpc.main
terraform state mv aws_subnet.public_1 'module.vpc.aws_subnet.public["us-east-1a"]'
terraform state mv aws_subnet.public_2 'module.vpc.aws_subnet.public["us-east-1b"]'
terraform state mv aws_internet_gateway.main 'module.vpc.aws_internet_gateway.main[0]'
```

### 5. 模块文档

```markdown
# VPC 模块

## 概述
创建具有可配置公共和私有子网的 VPC，支持跨多个可用区部署。

## 功能
- 多可用区子网部署
- 可选 NAT 网关配置
- VPC 流日志集成
- 可自定义的 CIDR 分配

## 使用

\`\`\`hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "my-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]

  create_public_subnets  = true
  create_private_subnets = true
  enable_nat_gateway     = true

  tags = {
    Environment = "production"
  }
}
\`\`\`

## 要求

| 名称 | 版本 |
|------|------|
| terraform | >= 1.5.0 |
| aws | ~> 5.0 |

## 输入

| 名称 | 描述 | 类型 | 默认 | 是否必需 |
|------|------|------|------|----------|
| name | 资源的名称前缀 | `string` | n/a | 是 |
| cidr_block | VPC CIDR 块 | `string` | n/a | 是 |
| availability_zones | 可用区列表 | `list(string)` | n/a | 是 |

## 输出

| 名称 | 描述 |
|------|------|
| vpc_id | VPC 标识符 |
| public_subnet_ids | 公共子网 ID 映射 |
| private_subnet_ids | 私有子网 ID 映射 |

## 示例

见 [examples/](./examples/) 目录以获取完整的用法示例。
```

### 6. 测试
使用技能 terraform-test

**测试文件**：包含测试配置和运行块的 `.tftest.hcl` 或 `.tftest.json` 文件，用于验证 Terraform 配置。

**测试块**：可选配置块，定义测试范围的设置（自 Terraform 1.6.0 起可用）。

**运行块**：定义单个测试场景，包含可选变量、提供者配置和断言。每个测试文件至少需要一个运行块。

**断言块**：包含条件，必须为真才能使测试通过。失败的断言会导致测试失败。

**模拟提供者**：模拟提供者行为而不创建真实基础设施（自 Terraform 1.7.0 起可用）。

**测试模式**：测试在应用模式（默认，创建真实基础设施）或计划模式（验证逻辑而不创建资源）下运行。

#### 文件结构

Terraform 测试文件使用 `.tftest.hcl` 或 `.tftest.json` 扩展名，通常组织在 `tests/` 目录中。使用清晰的命名约定区分单元测试（计划模式）和集成测试（应用模式）：

```
my-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── tests/
    ├── unit_test.tftest.hcl      # 单元测试（计划模式）
    └── integration_test.tftest.hcl  # 集成测试（应用模式 - 创建真实资源）
```

## 重构模式

### 模式 1：资源分组
将相关资源提取到连贯的模块中：
- 网络（VPC、子网、路由表）
- 计算（ASG、启动模板、负载均衡器）
- 数据（RDS、ElastiCache、S3）

### 模式 2：配置分层
```hcl
# 基础模块带默认值
module "vpc_base" {
  source = "./modules/vpc-base"
  # 最小必需输入
}

# 环境特定包装
module "vpc_prod" {
  source = "./modules/vpc-production"
  # 继承自基础，添加 prod 特定配置
}
```

### 模式 3：组合
```hcl
# 小型、专注的模块
module "vpc" {
  source = "./modules/vpc"
}

module "security_groups" {
  source = "./modules/security-groups"
  vpc_id = module.vpc.vpc_id
}

module "application" {
  source     = "./modules/application"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  sg_ids     = module.security_groups.app_sg_ids
}
```

## 常见陷阱

### 1. 过度抽象
```hcl
# ❌ 不要创建过于通用的模块
variable "resources" {
  type = map(map(any))  # 太灵活，难以验证
}

# ✅ 使用特定、类型的接口
variable "database_config" {
  type = object({
    engine         = string
    instance_class = string
  })
}
```

### 2. 紧密耦合
```hcl
# ❌ 不要通过直接引用耦合模块
# module A
output "instance_id" { value = aws_instance.app.id }

# module B（在同一配置中）
resource "aws_eip" "app" {
  instance = module.a.instance_id  # 紧密耦合
}

# ✅ 通过根模块传递依赖关系
module "compute" {
  source = "./modules/compute"
}

resource "aws_eip" "app" {
  instance = module.compute.instance_id
}
```

### 3. 状态迁移错误
始终先在非生产环境中测试迁移：
```bash
# 创建计划以验证迁移后无变化
terraform plan -out=migration.tfplan

# 仔细检查
terraform show migration.tfplan

# 仅当计划显示无变化时应用
terraform apply migration.tfplan
```

## 版本控制策略

```hcl
# 使用语义版本控制模块
module "vpc" {
  source  = "git::https://github.com/org/terraform-modules.git//vpc?ref=v1.2.0"
  version = "~> 1.2"
}

# 在生产中固定特定版本
# 开发中使用版本范围
```

## 成功标准

- [ ] 模块具有单一、明确定义的职责
- [ ] 所有变量都有描述和类型
- [ ] 验证规则防止无效配置
- [ ] 输出为消费者提供足够信息
- [ ] 文档包含使用示例
- [ ] 测试验证模块行为
- [ ] 状态迁移完成且无需重建资源
- [ ] 重构后无计划差异

## 相关技能
- [Terraform 代码生成](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/plugins/terraform/skills/terraform-style-guide/SKILL.md) - 新 Terraform 模块的样式指南
- [Azure 验证模块](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/plugins/terraform/skills/azure-verified-modules/SKILL.md) - Azure 推荐的模块规范

## 资源
- [Terraform 模块开发](https://developer.hashicorp.com/terraform/language/modules/develop)
- [模块最佳实践](https://developer.hashicorp.com/terraform/cloud-docs/registry/design)

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2025-11-07 | 初始技能定义 |
