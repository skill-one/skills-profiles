# 华为云 Terraform 安装器

跨平台 Terraform CLI 安装，默认使用 **华为云镜像**（避免 GitHub 网络问题）。

## 前置条件

- **Python 3.6+**（安装脚本必需）
- 网络访问至：
  - `releases.hashicorp.com`（Terraform 二进制文件）
  - `mirrors.huaweicloud.com`（华为云 Provider）

## 平台支持

| 平台 | 方法 | 备注 |
|------|------|------|
| **Linux** | 二进制文件 | 直接下载二进制文件 |
| **Windows** | 二进制文件 | 直接下载 |

**为何仅使用二进制下载？**

- 简单且在所有平台上更可靠
- 无需依赖包管理器的可用性
- 故障排除行为一致

**注意：** macOS 目前不支持。

### Windows 特殊说明

**Provider 安装方法：**

- 使用 `filesystem_mirror`（本地文件镜像）
- 从华为云镜像下载 zip 文件，解压到本地
- 配置 `terraform.rc` 指向本地目录

**不支持的安装方法：**

- ❌ `direct`（注册表 → GitHub）：GitHub 超时
- ❌ `network_mirror`：华为云镜像目录结构不兼容

## 快速入门

### 基本安装

```bash
# 自动安装（默认使用华为云镜像）
python scripts/install_terraform.py

# 安装 + 初始化
python scripts/install_terraform.py --init

# 安装 + 测试
python scripts/install_terraform.py --test
```

### 指定版本

```bash
# 安装指定版本
python scripts/install_terraform.py --version 1.15.4
```

### 其他操作

```bash
# 仅检查状态
python scripts/install_terraform.py --check

# 卸载
python scripts/install_terraform.py --uninstall
```

## 镜像策略

| 资源 | 源 | 备注 |
|------|------|------|
| Terraform 二进制文件 | HashiCorp 发布 | 官方源 |
| Provider | 华为云镜像（默认） | 避免GitHub网络问题 |

**华为云镜像：** `https://mirrors.huaweicloud.com/terraform/`

## 故障排除

### 问题 1：Windows 环境变量 PATH 无效

**解决方案：** 重新打开终端（PowerShell/CMD）

### 问题 2：权限被拒绝

```text
[ERROR] 权限被拒绝，请以管理员权限运行
```

**解决方案：**

- Windows：右键点击 → 以管理员身份运行
- Linux：`sudo python3 install_terraform.py`

### 问题 3：网络超时

**解决方案：** 默认使用华为云镜像，不应遇到此问题
