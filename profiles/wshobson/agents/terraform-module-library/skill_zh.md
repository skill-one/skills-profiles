# Terraform 模块库

适用于 AWS、Azure、GCP 和 OCI 基础设施的即用型 Terraform 模块模式。

## 目的

为跨多个云提供商的常见云基础设施模式创建可重用、经过充分测试的 Terraform 模块。

## 使用场景

- 构建可重用的基础设施组件
- 标准化云资源配置
- 实施基础设施即代码最佳实践
- 创建多云兼容模块
- 建立组织 Terraform 标准

## 模块结构

```
terraform-modules/
├── aws/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── s3/
├── azure/
│   ├── vnet/
│   ├── aks/
│   └── storage/
├── gcp/
│   ├── vpc/
│   ├── gke/
│   └── cloud-sql/
└── oci/
    ├── vcn/
    ├── oke/
    └── object-storage/
```

## 标准模块模式

```
module-name/
├── main.tf          # 主资源
├── variables.tf     # 输入变量
├── outputs.tf       # 输出值
├── versions.tf      # 提供商版本
├── README.md        # 文档
├── examples/        # 使用示例
│   └── complete/
│       ├── main.tf
│       └── variables.tf
└── tests/           # Terratest 文件
    └── module_test.go
```

## AWS VPC 模块示例

**main.tf:**

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(
    {
      Name = var.name
    },
    var.tags
  )
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    {
      Name = "${var.name}-private-${count.index + 1}"
      Tier = "private"
    },
    var.tags
  )
}

resource "aws_internet_gateway" "main" {
  count  = var.create_internet_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name = "${var.name}-igw"
    },
    var.tags
  )
}
```

**variables.tf:**

```hcl
variable "name" {
  description = "VPC 的名称"
  type        = string
}

variable "cidr_block" {
  description = "VPC 的 CIDR 块"
  type        = string
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", var.cidr_block))
    error_message = "CIDR 块必须是有效的 IPv4 CIDR 表示法。"
  }
}

variable "availability_zones" {
  description = "可用区列表"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "私有子网的 CIDR 块"
  type        = list(string)
  default     = []
}

variable "enable_dns_hostnames" {
  description = "在 VPC 中启用 DNS 域名"
  type        = bool
  default     = true
}

variable "tags" {
  description = "附加标签"
  type        = map(string)
  default     = {}
}
```

**outputs.tf:**

```hcl
output "vpc_id" {
  description = "VPC 的 ID"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "私有子网的 ID"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr_block" {
  description = "VPC 的 CIDR 块"
  value       = aws_vpc.main.cidr_block
}
```

## 最佳实践

1. **为模块使用语义版本控制**
2. **为所有变量添加描述**
3. **在 examples/ 目录中提供示例**
4. **使用验证块进行输入验证**
5. **输出重要属性以支持模块组合**
6. **在 versions.tf 中固定提供商版本**
7. **使用 locals 处理计算值**
8. **使用 count/for_each 实现条件资源**
9. **使用 Terratest 测试模块**
10. **一致地标记所有资源**

**参考:** 查看 `references/aws-modules.md` 和 `references/oci-modules.md`

## 模块组合

```hcl
module "vpc" {
  source = "../../modules/aws/vpc"

  name               = "production"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  private_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

module "rds" {
  source = "../../modules/aws/rds"

  identifier     = "production-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.large"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids

  tags = {
    Environment = "production"
  }
}
```

## 测试

```go
// tests/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

## 相关技能

- `multi-cloud-architecture` - 用于架构决策
- `cost-optimization` - 用于成本优化设计
