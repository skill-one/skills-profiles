# AWS AMI Builder

使用 Packer 的 `amazon-ebs` 构建器构建 Amazon Machine Images (AMIs)。

**参考:** [Amazon EBS 构建器](https://developer.hashicorp.com/packer/integrations/hashicorp/amazon/latest/components/builder/ebs)

> **注意:** 构建AMIs会产生 AWS 费用（EC2 实例、EBS 存储和数据传输）。构建时间通常为 10-30 分钟，具体取决于配置复杂性。

## 基础 AMI 模板

```hcl
packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1.3"
    }
  }
}

variable "region" {
  type    = string
  default = "us-west-2"
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "amazon-ebs" "ubuntu" {
  region        = var.region
  instance_type = "t3.micro"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"] # Canonical
  }

  ssh_username = "ubuntu"
  ami_name     = "my-app-${local.timestamp}"

  tags = {
    Name      = "my-app"
    BuildDate = local.timestamp
  }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
    ]
  }
}
```

## 常用源 AMI 筛选器

### Ubuntu 22.04 LTS
```hcl
source_ami_filter {
  filters = {
    name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
    root-device-type    = "ebs"
    virtualization-type = "hvm"
  }
  most_recent = true
  owners      = ["099720109477"] # Canonical
}
```

### Amazon Linux 2023
```hcl
source_ami_filter {
  filters = {
    name                = "al2023-ami-*-x86_64"
    root-device-type    = "ebs"
    virtualization-type = "hvm"
  }
  most_recent = true
  owners      = ["amazon"]
}
```

## 多区域 AMI

```hcl
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
  ami_name     = "my-app-${local.timestamp}"

  # 复制到其他区域
  ami_regions = ["us-east-1", "us-east-2", "eu-west-1"]
}
```

## 身份验证

Packer 使用 AWS 凭证解析：

1. 环境变量：`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
2. AWS 凭证文件：`~/.aws/credentials`
3. IAM 实例配置文件（在 EC2 上运行时）

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-2"

packer build .
```

## 构建命令

```bash
# 初始化插件
packer init .

# 验证模板
packer validate .

# 构建 AMI
packer build .

# 使用变量构建
packer build -var "region=us-east-1" .
```

## 常见问题

**SSH 超时**
- 确保 安全组 允许 SSH（端口 22）
- 验证子网具有互联网访问权限

**AMI 已存在**
- AMI 名称必须唯一
- 在名称中使用时间戳：`my-app-${local.timestamp}`

**卷大小太小**
- 检查源 AMI 的卷大小
- 适当设置 `launch_block_device_mappings.volume_size`

## 参考

- [Amazon EBS 构建器](https://developer.hashicorp.com/packer/integrations/hashicorp/amazon/latest/components/builder/ebs)
- [AWS AMI 文档](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html)
