# 推送到 HCP Packer 注册中心

配置 Packer 模板以将构建元数据推送到 HCP Packer 注册中心。

**参考：** [HCP Packer 注册中心](https://developer.hashicorp.com/hcp/docs/packer)

> **注意：** HCP Packer 基本使用免费。构建仅推送元数据（不推送实际镜像），开销极小（<1 分钟）。

## 基本注册中心配置

```hcl
packer {
  required_version = ">= 1.7.7"
}

variable "image_name" {
  type    = string
  default = "web-server"
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "amazon-ebs" "ubuntu" {
  region        = "us-west-2"
  instance_type = "t3.micro"

  source_ami_filter {
    filters = {
      name = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
    }
    most_recent = true
    owners      = ["099720109477"]
  }

  ssh_username = "ubuntu"
  ami_name     = "${var.image_name}-${local.timestamp}"
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  hcp_packer_registry {
    bucket_name = var.image_name
    description = "Ubuntu 22.04 基础镜像用于 Web 服务器"

    bucket_labels = {
      "os"   = "ubuntu"
      "team" = "platform"
    }

    build_labels = {
      "build-time" = local.timestamp
    }
  }

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
    ]
  }
}
```

## 身份验证

构建前设置环境变量：

```bash
export HCP_CLIENT_ID="your-service-principal-client-id"
export HCP_CLIENT_SECRET="your-service-principal-secret"
export HCP_ORGANIZATION_ID="your-org-id"
export HCP_PROJECT_ID="your-project-id"

packer build .
```

### 创建 HCP 服务主体

1. 导航到 HCP → 访问控制 (IAM)
2. 创建服务主体
3. 授予项目 "贡献者" 角色
4. 生成客户端密钥
5. 保存客户端 ID 和密钥

## 注册中心配置选项

### bucket_name (必需)
镜像标识符。构建之间必须保持一致！

```hcl
bucket_name = "web-server"  # 保持此值不变
```

### bucket_labels (可选)
桶级别的元数据。每次构建都会更新。

```hcl
bucket_labels = {
  "os"        = "ubuntu"
  "team"      = "platform"
  "component" = "web"
}
```

### build_labels (可选)
每次迭代对应的元数据。构建完成后不可变。

```hcl
build_labels = {
  "build-time" = local.timestamp
  "git-commit" = var.git_commit
}
```

## CI/CD 集成

### GitHub Actions

```yaml
name: Build and Push to HCP Packer

on:
  push:
    branches: [main]

env:
  HCP_CLIENT_ID: ${{ secrets.HCP_CLIENT_ID }}
  HCP_CLIENT_SECRET: ${{ secrets.HCP_CLIENT_SECRET }}
  HCP_ORGANIZATION_ID: ${{ secrets.HCP_ORGANIZATION_ID }}
  HCP_PROJECT_ID: ${{ secrets.HCP_PROJECT_ID }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-packer@main

      - name: Build and push
        run: |
          packer init .
          packer build \
            -var "git_commit=${{ github.sha }}" \
            .
```

## 在 Terraform 中查询

```hcl
data "hcp_packer_artifact" "ubuntu" {
  bucket_name  = "web-server"
  channel_name = "production"
  platform     = "aws"
  region       = "us-west-2"
}

resource "aws_instance" "web" {
  ami           = data.hcp_packer_artifact.ubuntu.external_identifier
  instance_type = "t3.micro"

  tags = {
    PackerBucket = data.hcp_packer_artifact.ubuntu.bucket_name
  }
}
```

## 常见问题

**身份验证失败**
- 验证 HCP_CLIENT_ID 和 HCP_CLIENT_SECRET
- 确保服务主体具有贡献者角色
- 检查组织和项目 ID

**桶名称不匹配**
- 构建 `bucket_name` 保持一致
- 不要在 bucket_name 中包含时间戳
- 名称变更时会创建新桶

**构建失败**
- 如果无法推送元数据，Packer 会立即失败
- 防止工件和注册中心之间的差异
- 检查与 HCP API 的网络连接

## 最佳实践

- **一致的桶名称** - 相同镜像类型永不更改
- **有意义的标签** - 用于版本、团队、合规性
- **CI/CD 自动化** - 自动化构建和注册中心推送
- **不可变的构建标签** - 将变化数据（git SHA、日期）放在 build_labels

## 参考

- [HCP Packer 文档](https://developer.hashicorp.com/hcp/docs/packer)
- [hcp_packer_registry 块](https://developer.hashicorp.com/packer/docs/templates/hcl_templates/blocks/build/hcp_packer_registry)
- [HCP Terraform 提供程序](https://registry.terraform.io/providers/hashicorp/hcp/latest/docs/data-sources/packer_artifact)
