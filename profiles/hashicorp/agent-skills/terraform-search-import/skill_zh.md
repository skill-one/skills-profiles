# Terraform 搜索和批量导入

使用声明式查询发现现有云资源，并生成配置以批量导入到 Terraform 状态中。

**参考资料：**
- [Terraform Search - list 块](https://developer.hashicorp.com/terraform/language/block/tfquery/list)
- [批量导入](https://developer.hashicorp.com/terraform/language/import/bulk)

## 使用场景

- 将未管理的资源纳入 Terraform 管理
- 审计现有云基础设施
- 从手动配置迁移到 IaC
- 跨多个区域/账户发现资源

## 重要提示：首先检查提供程序支持

**在开始之前，你必须验证目标资源类型是否受支持：**

```bash
# 检查可用的 list 资源
./scripts/list_resources.sh aws      # 特定提供程序
./scripts/list_resources.sh          # 所有配置的提供程序
```

## 决策树

1. **识别目标资源类型**（例如，aws_s3_bucket、aws_instance）
2. **检查是否受支持**：运行 `./scripts/list_resources.sh <提供程序>`
3. **选择工作流**：
   - **如果受支持**：检查可用的 Terraform 版本。
   - **如果 Terraform 版本高于 1.14.0**：使用 Terraform 搜索工作流（下方）
   - **如果不受支持或 Terraform 版本低于 1.14.0**：使用手动发现工作流（参见 [references/MANUAL-IMPORT.md](references/MANUAL-IMPORT.md)）

   **注意**：受支持资源的列表正在快速扩展。在使用手动导入之前，始终验证当前支持情况。

## 前置条件

在编写查询之前，验证提供程序是否支持你的目标资源类型的 list 资源。

### 发现可用的 List 资源

运行辅助脚本从你的提供程序中提取受支持的 list 资源：

```bash
# 从包含提供程序配置的目录运行（如果需要，将运行 terraform init）
./scripts/list_resources.sh aws      # 特定提供程序
./scripts/list_resources.sh          # 所有配置的提供程序
```

或者手动查询提供程序架构：

```bash
terraform providers schema -json | jq '.provider_schemas | to_entries | map({key: (.key | split("/")[-1]), value: (.value.list_resource_schemas // {} | keys)})'
```

Terraform 搜索需要一个初始化的工作目录。确保在运行查询之前，你有一个包含所需提供程序的配置：

```hcl
# terraform.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

运行 `terraform init` 下载提供程序，然后继续运行查询。

## Terraform 搜索工作流（仅限受支持资源）

1. 创建 `.tfquery.hcl` 文件，其中包含 `list` 块来定义搜索查询
2. 运行 `terraform query` 来发现匹配的资源
3. 使用 `-generate-config-out=<文件>` 生成配置
4. 审查和改进生成的 `resource` 和 `import` 块
5. 运行 `terraform plan` 和 `terraform apply` 来导入

## 查询文件结构

查询文件使用 `.tfquery.hcl` 扩展名，并支持：
- `provider` 块用于身份验证
- `list` 块用于资源发现
- `variable` 和 `locals` 块用于参数化

```hcl
# discovery.tfquery.hcl
provider "aws" {
  region = "us-west-2"
}

list "aws_instance" "all" {
  provider = aws
}
```

## List 块语法

```hcl
list "<list_type>" "<symbolic_name>" {
  provider = <provider_reference>  # 必须提供

  # 可选：过滤配置（提供程序特定）
  # `config` 块的架构是提供程序特定的。使用 `terraform providers schema -json | jq '.provider_schemas."registry.terraform.io/hashicorp/<提供程序>".list_resource_schemas."<resource_type>"'` 发现可用选项

  config {
    filter {
      name   = "<filter_name>"
      values = ["<value1>", "<value2>"]
    }
    region = "<region>"  # AWS 特定
  }
  # 可选：限制结果
  limit = 100
}
```

## 受支持的 List 资源

提供程序对 list 资源的支持因版本而异。**始终使用发现脚本检查你的特定提供程序版本的可用性。**

## 查询示例

### 基本发现

```hcl
# 查找配置区域中的所有 EC2 实例
list "aws_instance" "all" {
  provider = aws
}
```

### 过滤发现

```hcl
# 按标签查找实例
list "aws_instance" "production" {
  provider = aws

  config {
    filter {
      name   = "tag:Environment"
      values = ["production"]
    }
  }
}

# 按类型查找实例
list "aws_instance" "large" {
  provider = aws

  config {
    filter {
      name   = "instance-type"
      values = ["t3.large", "t3.xlarge"]
    }
  }
}
```

### 跨区域发现

```hcl
provider "aws" {
  region = "us-west-2"
}

locals {
  regions = ["us-west-2", "us-east-1", "eu-west-1"]
}

list "aws_instance" "all_regions" {
  for_each = toset(local.regions)
  provider = aws

  config {
    region = each.value
  }
}
```

### 参数化查询

```hcl
variable "target_environment" {
  type    = string
  default = "staging"
}

list "aws_instance" "by_env" {
  provider = aws

  config {
    filter {
      name   = "tag:Environment"
      values = [var.target_environment]
    }
  }
}
```

## 运行查询

```bash
# 执行查询并显示结果
terraform query

# 生成配置文件
terraform query -generate-config-out=imported.tf

# 传递变量
terraform query -var='target_environment=production'
```

## 查询输出格式

```
list.aws_instance.all   account_id=123456789012,id=i-0abc123,region=us-west-2   web-server
```

列：`<query_address>   <identity_attributes>   <name_tag>`

## 生成的配置

`-generate-config-out` 标志创建：

```hcl
# __generated__ by Terraform
resource "aws_instance" "all_0" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  # ... 所有属性
}

import {
  to       = aws_instance.all_0
  provider = aws
  identity = {
    account_id = "123456789012"
    id         = "i-0abc123"
    region     = "us-west-2"
  }
}
```

## 生成后清理

生成的配置包含所有属性。通过以下方式清理：

1. 删除计算/只读属性
2. 将硬编码值替换为变量
3. 添加适当的资源命名
4. 组织到适当的文件中

```hcl
# 之前：生成
resource "aws_instance" "all_0" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t2.micro"
  arn                    = "arn:aws:ec2:..."  # 删除 - 计算属性
  id                     = "i-0abc123"        # 删除 - 计算属性
  # ... 许多其他属性
}

# 之后：清理
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = {
    Name        = "web-server"
    Environment = var.environment
  }
}
```

## 基于身份导入

生成的导入使用基于身份的导入（Terraform 1.12+）：

```hcl
import {
  to       = aws_instance.web
  provider = aws
  identity = {
    account_id = "123456789012"
    id         = "i-0abc123"
    region     = "us-west-2"
  }
}
```

## 验证导入的状态

在运行 `terraform apply` 导入资源后，验证实际 landed 在状态中的内容。
优先使用文档化、稳定且更高效的令牌命令，而不是读取原始状态文件：

```bash
# 确认资源现在受管理（这也确认了地址）
terraform state list

# 检查导入资源的解析属性值
terraform show -json | jq '.values.root_module.resources[] | {address, type, name}'
```

`terraform show -json` 需要提供程序已安装（`terraform init`），因为它根据提供程序架构渲染值。**仅在**提供程序不可用且 `init` 无法运行时，回退到原始状态（`terraform state pull` / `terraform.tfstate`），你只需要粗略信息（地址、输出、`serial`/`lineage`），或者你必须避免执行 Terraform。避免解析原始版本 4 状态格式作为稳定接口。**注意**：状态以明文形式包含敏感值，在每种格式中都如此——永远不要将状态内容输出到日志或输出中。

## 最佳实践

### 查询设计
- 从宽泛开始，然后添加过滤器来缩小结果
- 使用 `limit` 来防止输出过载
- 在生成配置之前测试查询

### 配置管理
- 在应用之前审查所有生成代码
- 删除不必要的默认值
- 使用一致的命名约定
- 添加适当的变量抽象

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| "未找到 list 资源" | 检查提供程序版本是否支持 list 资源 |
| 查询返回空 | 验证区域和过滤值 |
| 生成的配置有错误 | 删除计算属性，修复已弃用的参数 |
| 导入失败 | 确保资源不在状态中 |

## 完整示例

```hcl
# main.tf - 初始化提供程序
terraform {
  required_version = ">= 1.14"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"  # 始终使用最新版本
    }
  }
}

# discovery.tfquery.hcl - 定义查询
provider "aws" {
  region = "us-west-2"
}

list "aws_instance" "team_instances" {
  provider = aws

  config {
    filter {
      name   = "tag:Owner"
      values = ["platform"]
    }
    filter {
      name   = "instance-state-name"
      values = ["running"]
    }
  }

  limit = 50
}
```

```bash
# 执行工作流
terraform init
terraform query
terraform query -generate-config-out=generated.tf
# 审查并清理 generated.tf
terraform plan
terraform apply
```
