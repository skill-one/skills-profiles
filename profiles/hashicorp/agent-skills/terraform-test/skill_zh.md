# Terraform 测试

Terraform 的内置测试框架验证配置更新不会引入破坏性变更。测试针对临时资源运行，保护现有基础设施和状态文件。

## 参考文件

- `references/MOCK_PROVIDERS.md` — Mock 提供者语法、常见默认值、何时使用 Mock（仅限 Terraform 1.7.0+ — 如果用户版本低于 1.7 则跳过）
- `references/CI_CD.md` — GitHub Actions 和 GitLab CI 管道示例
- `references/EXAMPLES.md` — 完整示例测试套件（VPC 模块的单元测试、集成测试和 Mock 测试）

当用户询问关于 Mock、CI/CD 集成或需要完整示例时，请阅读相关的参考文件。

## 核心概念

- **测试文件**（`.tftest.hcl` / `.tftest.json`）：包含验证您配置的 `run` 块
- **Run 块**：单个测试场景，包含可选的变量、提供者和断言
- **Assert 块**：测试必须为真才能通过的条件
- **Mock 提供者**：模拟提供者行为而不使用真实基础设施（仅限 Terraform 1.7.0+）
- **测试模式**：`apply`（默认，创建真实资源）或 `plan`（仅验证逻辑）

## 文件结构

```
my-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── tests/
    ├── defaults_unit_test.tftest.hcl         # plan 模式 — 快速，无资源
    ├── validation_unit_test.tftest.hcl        # plan 模式
    └── full_stack_integration_test.tftest.hcl # apply 模式 — 创建真实资源
```

使用 `*_unit_test.tftest.hcl` 用于 plan 模式测试，使用 `*_integration_test.tftest.hcl` 用于 apply 模式测试，以便在 CI 中单独过滤。

## 测试文件结构

```hcl
# 可选：全局测试设置
test {
  parallel = true  # 启用所有 run 块的并行执行（默认：false）
}

# 可选：文件级变量（最高优先级，覆盖所有其他来源）
variables {
  aws_region    = "us-west-2"
  instance_type = "t2.micro"
}

# 可选：提供者配置
provider "aws" {
  region = var.aws_region
}

# 必须至少有一个 run 块
run "test_default_configuration" {
  command = plan

  assert {
    condition     = aws_instance.example.instance_type == "t2.micro"
    error_message = "默认实例类型应为 t2.micro"
  }
}
```

## Run 块

```hcl
run "test_name" {
  command  = plan  # 或 apply（默认）
  parallel = true  # 可选，自 v1.9.0 起支持

  # 覆盖文件级变量
  variables {
    instance_type = "t3.large"
  }

  # 引用特定模块
  module {
    source  = "./modules/vpc"  # 仅本地或注册（不支持 git/http）
    version = "5.0.0"          # 仅注册模块
  }

  # 控制状态隔离
  state_key = "shared_state"  # 自 v1.9.0 起支持

  # Plan 行为
  plan_options {
    mode    = refresh-only  # 或 normal（默认）
    refresh = true
    replace = [aws_instance.example]
    target  = [aws_instance.example]
  }

  # 断言
  assert {
    condition     = aws_instance.example.id != ""
    error_message = "实例应有有效的 ID"
  }

  # 预期失败（如果这些失败，测试通过）
  expect_failures = [
    var.instance_count
  ]
}
```

## 常见测试模式

### 验证 Outputs

```hcl
run "test_outputs" {
  command = plan

  assert {
    condition     = output.vpc_id != null
    error_message = "VPC ID 输出必须定义"
  }

  assert {
    condition     = can(regex("^vpc-", output.vpc_id))
    error_message = "VPC ID 应以 'vpc-' 开头"
  }
}
```

### 条件资源

```hcl
run "test_nat_gateway_disabled" {
  command = plan

  variables {
    create_nat_gateway = false
  }

  assert {
    condition     = length(aws_nat_gateway.main) == 0
    error_message = "禁用时不应创建 NAT 网关"
  }
}
```

### 资源计数

```hcl
run "test_resource_count" {
  command = plan

  variables {
    instance_count = 3
  }

  assert {
    condition     = length(aws_instance.workers) == 3
    error_message = "应创建恰好 3 个工作实例"
  }
}
```

### 标签

```hcl
run "test_resource_tags" {
  command = plan

  variables {
    common_tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
    }
  }

  assert {
    condition     = aws_instance.example.tags["Environment"] == "production"
    error_message = "环境标签应正确设置"
  }

  assert {
    condition     = aws_instance.example.tags["ManagedBy"] == "Terraform"
    error_message = "ManagedBy 标签应正确设置"
  }
}
```

### 数据源

```hcl
run "test_data_source_lookup" {
  command = plan

  assert {
    condition     = data.aws_ami.ubuntu.id != ""
    error_message = "应找到有效的 Ubuntu AMI"
  }

  assert {
    condition     = can(regex("^ami-", data.aws_ami.ubuntu.id))
    error_message = "AMI ID 应为正确格式"
  }
}
```

### 验证规则

```hcl
run "test_invalid_environment" {
  command = plan

  variables {
    environment = "invalid"
  }

  expect_failures = [
    var.environment
  ]
}
```

### 带依赖的顺序测试

```hcl
run "setup_vpc" {
  command = apply

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC 应创建"
  }
}

run "test_subnet_in_vpc" {
  command = plan

  variables {
    vpc_id = run.setup_vpc.vpc_id
  }

  assert {
    condition     = aws_subnet.example.vpc_id == run.setup_vpc.vpc_id
    error_message = "子网应属于 setup_vpc 创建的 VPC"
  }
}
```

### Plan 选项（refresh-only, targeted）

```hcl
run "test_refresh_only" {
  command = plan

  plan_options {
    mode = refresh-only
  }

  assert {
    condition     = aws_instance.example.tags["Environment"] == "production"
    error_message = "标签应正确刷新"
  }
}

run "test_specific_resource" {
  command = plan

  plan_options {
    target = [aws_instance.example]
  }

  assert {
    condition     = aws_instance.example.instance_type == "t2.micro"
    error_message = "目标资源应被规划"
  }
}
```

### 并行模块

```hcl
run "test_networking_module" {
  command  = plan
  parallel = true

  module {
    source = "./modules/networking"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC 应创建"
  }
}

run "test_compute_module" {
  command  = plan
  parallel = true

  module {
    source = "./modules/compute"
  }

  assert {
    condition     = output.instance_id != ""
    error_message = "实例应创建"
  }
}
```

### State key 共享

```hcl
run "create_foundation" {
  command   = apply
  state_key = "foundation"

  assert {
    condition     = aws_vpc.main.id != ""
    error_message = "基础 VPC 应创建"
  }
}

run "create_application" {
  command   = apply
  state_key = "foundation"

  variables {
    vpc_id = run.create_foundation.vpc_id
  }

  assert {
    condition     = aws_instance.app.vpc_id == run.create_foundation.vpc_id
    error_message = "应用应使用基础 VPC"
  }
}
```

### 清理顺序（S3 对象先于存储桶）

```hcl
run "create_bucket" {
  command = apply

  assert {
    condition     = aws_s3_bucket.example.id != ""
    error_message = "存储桶应创建"
  }
}

run "add_objects" {
  command = apply

  assert {
    condition     = length(aws_s3_object.files) > 0
    error_message = "对象应添加"
  }
}

# 清理按相反顺序销毁：对象先，然后存储桶
```

### 多个别名提供者

```hcl
provider "aws" {
  alias  = "primary"
  region = "us-west-2"
}

provider "aws" {
  alias  = "secondary"
  region = "us-east-1"
}

run "test_with_specific_provider" {
  command = plan

  providers = {
    aws = provider.aws.secondary
  }

  assert {
    condition     = aws_instance.example.availability_zone == "us-east-1a"
    error_message = "实例应在 us-east-1 区域"
  }
}
```

### 复杂条件

```hcl
assert {
  condition = alltrue([
    for subnet in aws_subnet.private :
    can(regex("^10\\.0\\.", subnet.cidr_block))
  ])
  error_message = "所有私有子网应使用 10.0.0.0/8 CIDR 范围"
}
```

## 清理

测试完成后，资源按 **run 块的相反顺序** 销毁。这对于依赖关系很重要（例如，S3 对象先于存储桶）。使用 `terraform test -no-cleanup` 跳过清理以进行调试。

## 运行测试

```bash
terraform test                                        # 所有测试
terraform test tests/defaults.tftest.hcl             # 特定文件
terraform test -filter=test_vpc_configuration        # 按 run 块名称过滤
terraform test -test-directory=integration-tests     # 自定义目录
terraform test -verbose                              # 详细输出
terraform test -no-cleanup                           # 跳过资源清理
```

## 最佳实践

1. **命名**：`*_unit_test.tftest.hcl` 用于 plan 模式，`*_integration_test.tftest.hcl` 用于 apply 模式
2. **测试命名**：使用描述性的 run 块名称来解释正在测试的场景
3. **默认为 plan**：除非需要测试真实资源行为，否则使用 `command = plan`
4. **使用 Mock** 处理外部依赖 — 更快且无需凭证（见 `references/MOCK_PROVIDERS.md`）
5. **错误消息**：确保它们足够具体，以便在不重新运行测试的情况下诊断失败
6. **负向测试**：使用 `expect_failures` 验证验证规则拒绝无效输入
7. **变量覆盖**：测试不同的变量组合以验证所有代码路径 — 测试变量具有最高优先级并覆盖所有其他来源
8. **模块来源**：测试文件仅支持本地路径和注册模块 — 不支持 git 或 HTTP URL
9. **并行执行**：使用 `parallel = true` 用于具有不同状态文件的独立测试
10. **清理**：集成测试自动按相反 run 块顺序销毁资源；使用 `-no-cleanup` 进行调试
11. **CI/CD**：在每次 PR 上运行单元测试，在合并时运行集成测试（见 `references/CI_CD.md`）

## 故障排除

| 问题               | 解决方案                     |
|--------------------|------------------------------|
| 断言失败           | 使用 `-verbose` 查看实际与预期值 |
| 缺少凭证           | 使用 Mock 提供者进行单元测试   |
| 不支持的模块来源   | 将 git/HTTP 来源转换为本地模块 |
| 测试相互干扰       | 使用 `state_key` 或分离模块隔离 |
| 测试缓慢           | 使用 `command = plan` 和 Mock；单独运行集成测试 |

## 参考

- [Terraform 测试文档](https://developer.hashicorp.com/terraform/language/tests)
- [Terraform 测试命令](https://developer.hashicorp.com/terraform/cli/commands/test)
