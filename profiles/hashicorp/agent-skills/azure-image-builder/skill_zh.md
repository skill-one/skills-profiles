# Azure 图像构建器

使用 Packer 的 `azure-arm` 构建器构建 Azure 管理图像和 Azure 计算库图像。

**参考：** [Azure ARM 构建器](https://developer.hashicorp.com/packer/integrations/hashicorp/azure/latest/components/builder/arm)

> **注意：** 构建 Azure 图像会产生费用（计算、存储、数据传输）。构建时间通常为 15-45 分钟，具体取决于配置和操作系统。

## 基本管理图像

```hcl
packer {
  required_plugins {
    azure = {
      source  = "github.com/hashicorp/azure"
      version = "~> 2.0"
    }
  }
}

variable "client_id" {
  type      = string
  sensitive = true
}

variable "client_secret" {
  type      = string
  sensitive = true
}

variable "subscription_id" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "resource_group" {
  type    = string
  default = "packer-images-rg"
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "azure-arm" "ubuntu" {
  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id

  managed_image_resource_group_name = var.resource_group
  managed_image_name                = "my-app-${local.timestamp}"

  os_type         = "Linux"
  image_publisher = "Canonical"
  image_offer     = "0001-com-ubuntu-server-jammy"
  image_sku       = "22_04-lts-gen2"

  location = "East US"
  vm_size  = "Standard_B2s"

  azure_tags = {
    Name      = "my-app"
    BuildDate = local.timestamp
  }
}

build {
  sources = ["source.azure-arm.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
    ]
  }
}
```

## Azure 计算库

```hcl
source "azure-arm" "ubuntu" {
  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id

  os_type         = "Linux"
  image_publisher = "Canonical"
  image_offer     = "0001-com-ubuntu-server-jammy"
  image_sku       = "22_04-lts-gen2"

  location = "East US"
  vm_size  = "Standard_B2s"

  shared_image_gallery_destination {
    resource_group       = "gallery-rg"
    gallery_name         = "myImageGallery"
    image_name           = "ubuntu-webapp"
    image_version        = "1.0.${formatdate("YYYYMMDD", timestamp())}"
    replication_regions  = ["East US", "West US 2"]
    storage_account_type = "Standard_LRS"
  }
}
```

## 身份验证

### 服务主体
```bash
# 创建服务主体
az ad sp create-for-rbac \
  --name "packer-sp" \
  --role Contributor \
  --scopes /subscriptions/<subscription-id>

# 设置环境变量
export ARM_CLIENT_ID="<client-id>"
export ARM_CLIENT_SECRET="<client-secret>"
export ARM_SUBSCRIPTION_ID="<subscription-id>"
export ARM_TENANT_ID="<tenant-id>"
```

### 管理身份
```hcl
source "azure-arm" "ubuntu" {
  use_azure_cli_auth = true
  subscription_id    = var.subscription_id
  # ... 其余配置
}
```

## 构建命令

```bash
# 设置身份验证
export ARM_CLIENT_ID="your-client-id"
export ARM_CLIENT_SECRET="your-client-secret"
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_TENANT_ID="your-tenant-id"

# 初始化插件
packer init .

# 验证模板
packer validate .

# 构建图像
packer build .
```

## 常见问题

**身份验证失败**
- 验证服务主体凭证
- 确保资源组上的 Contributor 角色
- 检查订阅和租户 ID

**计算库版本已存在**
- 图像版本是不可变的
- 使用带日期/构建编号的唯一版本号
- 无法覆盖现有版本

**配置期间超时**
- 检查构建虚拟机的网络连接
- 验证 NSG 规则是否允许所需流量
- 如有需要，增加超时时间

## 参考

- [Azure ARM 构建器](https://developer.hashicorp.com/packer/integrations/hashicorp/azure/latest/components/builder/arm)
- [Azure 计算库](https://learn.microsoft.com/en-us/azure/virtual-machines/azure-compute-gallery)
