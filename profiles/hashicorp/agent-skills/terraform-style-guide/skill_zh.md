# Terraform 风格指南

遵循 HashiCorp 官方风格约定和最佳实践来生成和维护 Terraform 代码。

**参考:** [HashiCorp Terraform 风格指南](https://developer.hashicorp.com/terraform/language/style)

## 代码生成策略

生成 Terraform 代码时：

1.  先配置 provider 和版本约束
2.  在依赖资源之前创建数据源
3.  按依赖顺序构建资源
4.  为关键资源属性添加输出
5.  使用变量来表示所有可配置的值

## 文件组织

| 文件         | 目的                 |
|--------------|----------------------|
| `terraform.tf` | Terraform 和 provider 版本要求 |
| `providers.tf` | Provider 配置         |
| `main.tf`    | 主要资源和数据源       |
| `variables.tf` | 输入变量声明（按字母顺序） |
| `outputs.tf`  | 输出值声明（按字母顺序） |
| `locals.tf`   | 本地值声明           |

### 示例结构

```hcl
# terraform.tf
terraform {
  required_version = ">= 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# variables.tf
variable "environment" {
  description = "目标部署环境"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "环境必须是 dev、staging 或 prod。"
  }
}

# locals.tf
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# main.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-vpc"
  })
}

# outputs.tf
output "vpc_id" {
  description = "创建的 VPC ID"
  value       = aws_vpc.main.id
}
```

## 代码格式化

### 缩进和对齐

- 每个嵌套级别使用 **两个空格**（不要使用制表符）
- 连续参数的等号对齐

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id     = "subnet-12345678"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
```

### 块组织

参数在前，元参数优先：

```hcl
resource "aws_instance" "example" {
  # 元参数
  count = 3

  # 参数
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  # 块
  root_block_device {
    volume_size = 20
  }

  # 生命周期最后
  lifecycle {
    create_before_destroy = true
  }
}
```

## 命名约定

- 所有名称使用 **小写和下划线**
- 使用 **描述性名词**，不包括资源类型
- 具体且有意义
- 资源名称必须使用单数，不是复数
- 当特定描述性名称冗余或不可用时，默认使用 `main`，前提是只有一个实例

```hcl
# 不推荐
resource "aws_instance" "webAPI-aws-instance" {}
resource "aws_instance" "web_apis" {}
variable "name" {}

# 推荐
resource "aws_instance" "web_api" {}
resource "aws_vpc" "main" {}
variable "application_name" {}
```

## 变量

每个变量必须包含 `type` 和 `description`：

```hcl
variable "instance_type" {
  description = "Web 服务器的 EC2 实例类型"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "实例类型必须是 t2.micro、t2.small 或 t2.medium。"
  }
}

variable "database_password" {
  description = "数据库管理员密码"
  type        = string
  sensitive   = true
}
```

## 输出

每个输出必须包含 `description`：

```hcl
output "instance_id" {
  description = "EC2 实例 ID"
  value       = aws_instance.web.id
}

output "database_password" {
  description = "数据库管理员密码"
  value       = aws_db_instance.main.password
  sensitive   = true
}
```

## 动态资源创建

### 优先使用 `for_each` 而不是 `count`

```hcl
# 不推荐 - 使用 count 创建多个资源
resource "aws_instance" "web" {
  count = var.instance_count
  tags  = { Name = "web-${count.index}" }
}

# 推荐 - 使用 for_each 命名实例
variable "instance_names" {
  type    = set(string)
  default = ["web-1", "web-2", "web-3"]
}

resource "aws_instance" "web" {
  for_each = var.instance_names
  tags     = { Name = each.key }
}
```

### 使用 `count` 进行条件创建

```hcl
resource "aws_cloudwatch_metric_alarm" "cpu" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name = "high-cpu-usage"
  threshold  = 80
}
```

## 安全最佳实践

参考 SECURITY.md。其中包含有关加密资源、防止敏感数据在状态中、安全配置的指导。

## 版本锁定

```hcl
terraform {
  required_version = ">= 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

使用每个 provider 的最新主版本和 Terraform 的最新次版本，除非受依赖锁定文件或其他配置使用的模块约束。

**版本约束运算符:**
- `= 1.0.0` - 精确版本
- `>= 1.0.0` - 大于或等于
- `~> 1.0` - 允许最右边组件递增
- `>= 1.0, < 2.0` - 版本范围

## Provider 配置

```hcl
provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = var.project_name
    }
  }
}

# 多区域别名 provider
provider "aws" {
  alias  = "east"
  region = "us-east-1"
}
```

## 版本控制

**永远不要提交:**
- `terraform.tfstate`, `terraform.tfstate.backup`
- `.terraform/` 目录
- `*.tfplan`
- 包含敏感数据的 `.tfvars` 文件

**始终提交:**
- 所有 `.tf` 配置文件
- `.terraform.lock.hcl`（依赖锁定文件）

## 验证工具

提交前运行：

```bash
terraform fmt -recursive
terraform validate
```

其他工具：
- `tflint` - 代码检查和最佳实践
- `checkov` / `tfsec` - 安全扫描

## 代码审查清单

- [ ] 使用 `terraform fmt` 格式化代码
- [ ] 使用 `terraform validate` 验证配置
- [ ] 文件按标准结构组织
- [ ] 所有变量都有类型和描述
- [ ] 所有输出都有描述
- [ ] 资源名称使用描述性名词和下划线
- [ ] 明确锁定版本约束
- [ ] 敏感值标记为 `sensitive = true`
- [ ] 没有硬编码的凭证或密钥
- [ ] 应用安全最佳实践

---

*基于: [HashiCorp Terraform 风格指南](https://developer.hashicorp.com/terraform/language/style)*
