# Windows Builder

使用 Packer 构建 Windows 镜像的跨平台模式。

**参考：** [WinRM Communicator](https://developer.hashicorp.com/packer/docs/communicators/winrm)

> **注意：** Windows 构建会带来显著的成本和时间。由于 Windows 更新，每次构建预计需要 45-120 分钟。失败的构建可能会使资源持续运行——始终验证清理操作。

## WinRM Communicator 设置

Windows 需要 WinRM 才能进行 Packer 通信。

### AWS 示例

```hcl
source "amazon-ebs" "windows" {
  region        = "us-west-2"
  instance_type = "t3.medium"

  source_ami_filter {
    filters = {
      name = "Windows_Server-2022-English-Full-Base-*"
    }
    most_recent = true
    owners      = ["amazon"]
  }

  ami_name = "windows-server-2022-${local.timestamp}"

  communicator   = "winrm"
  winrm_username = "Administrator"
  winrm_use_ssl  = true
  winrm_insecure = true
  winrm_timeout  = "15m"

  user_data_file = "scripts/setup-winrm.ps1"
}
```

### WinRM 设置脚本 (scripts/setup-winrm.ps1)

```powershell
<powershell>
# 配置 WinRM
winrm quickconfig -q
winrm set winrm/config '@{MaxTimeoutms="1800000"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'

# 配置防火墙
netsh advfirewall firewall add rule name="WinRM 5985" protocol=TCP dir=in localport=5985 action=allow
netsh advfirewall firewall add rule name="WinRM 5986" protocol=TCP dir=in localport=5986 action=allow

# 重启 WinRM
net stop winrm
net start winrm
</powershell>
```

### Azure 示例

```hcl
source "azure-arm" "windows" {
  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id

  managed_image_resource_group_name = "images-rg"
  managed_image_name                = "windows-${local.timestamp}"

  os_type         = "Windows"
  image_publisher = "MicrosoftWindowsServer"
  image_offer     = "WindowsServer"
  image_sku       = "2022-datacenter-g2"

  location = "East US"
  vm_size  = "Standard_D2s_v3"

  # Azure 自动配置 WinRM
  communicator   = "winrm"
  winrm_use_ssl  = true
  winrm_insecure = true
  winrm_timeout  = "15m"
  winrm_username = "packer"
}
```

## PowerShell 提供者

### 安装软件

```hcl
build {
  sources = ["source.amazon-ebs.windows"]

  # 安装 Chocolatey
  provisioner "powershell" {
    inline = [
      "Set-ExecutionPolicy Bypass -Scope Process -Force",
      "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    ]
  }

  # 安装应用程序
  provisioner "powershell" {
    inline = [
      "choco install -y googlechrome",
      "choco install -y 7zip",
    ]
  }

  # 安装 IIS
  provisioner "powershell" {
    inline = [
      "Install-WindowsFeature -Name Web-Server -IncludeManagementTools"
    ]
  }
}
```

### Windows 更新

```hcl
provisioner "powershell" {
  inline = [
    "Install-PackageProvider -Name NuGet -Force",
    "Install-Module -Name PSWindowsUpdate -Force",
    "Import-Module PSWindowsUpdate",
    "Get-WindowsUpdate -Install -AcceptAll -AutoReboot",
  ]
  timeout = "2h"
}

# 等待重启
provisioner "windows-restart" {
  restart_timeout = "30m"
}
```

## 清理

```hcl
provisioner "powershell" {
  inline = [
    "# 清理临时文件",
    "Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue",
    "# 清理 Windows 更新缓存",
    "Stop-Service -Name wuauserv -Force",
    "Remove-Item -Path 'C:\\Windows\\SoftwareDistribution\\*' -Recurse -Force -ErrorAction SilentlyContinue",
    "Start-Service -Name wuauserv",
  ]
}
```

## 常见问题

**WinRM 超时**
- 将 `winrm_timeout` 增加到 15 分钟或更长
- 验证安全组允许端口 5985/5986
- 检查用户数据脚本是否成功执行

**PowerShell 执行策略**
```hcl
provisioner "powershell" {
  inline = [
    "Set-ExecutionPolicy Bypass -Scope Process -Force",
    "# 您的命令在这里",
  ]
}
```

**构建时间过长**
- Windows 更新可能需要 1-2 小时
- 当可用时使用预修补的基镜像
- 设置提供者 `timeout = "2h"`

## 参考

- [WinRM Communicator](https://developer.hashicorp.com/packer/docs/communicators/winrm)
- [PowerShell Provisioner](https://developer.hashicorp.com/packer/docs/provisioners/powershell)
