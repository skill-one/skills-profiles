# 解决 S3 文件问题

## 概述

诊断和解决 Amazon S3 文件问题：挂载失败、IAM 权限、同步、冲突解决和性能。

有关权威指南，请参阅 [S3 文件故障排除](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-troubleshooting.html)。

## 常见任务

### 0. 验证依赖项

- 您必须验证 `aws` CLI 是否可用且支持 `s3files` 子命令
- 您必须确认有效的 AWS 凭证
- 您必须仅检查工具的存在和版本 —— 在验证期间绝不能执行破坏性或修改性命令
- 您必须告知用户如果缺少任何必需工具
- 如果工具不可用，您必须尊重用户的中止决定
- 您应该在使用前解释步骤，并在写入命令上等待用户确认

### 1. 分类问题

| 症状 | 类别 |
|---|---|
| mount.s3files: 命令未找到 | A: 客户端安装 |
| 挂载期间连接超时 | B: 网络/安全组 |
| 挂载无限期挂起（无超时） | B: 网络/安全组 |
| 挂载期间访问被拒绝 | C: IAM 权限 |
| 文件系统卡在 "创建中" | C: IAM 权限 |
| 文件操作权限被拒绝 | C: IAM 权限 |
| 写入后 S3 中未出现文件 | D: 同步 |
| 文件出现在 .s3files-lost+found 目录 | E: 冲突解决 |
| 读速慢或高延迟 | F: 性能 |
| NFS 服务器错误 | G: 加密/KMS |
| DNS 名称解析失败 | H: VPC DNS |

### 2. 类别 A — 客户端安装

`mount.s3files: 命令未找到` 表示 `amazon-efs-utils` 缺失或 < v3.0.0。

```bash
sudo yum -y install amazon-efs-utils  # Amazon Linux
```

### 3. 类别 B — 网络/安全组

连接超时是挂载失败的首要原因 —— 几乎总是与安全组有关。

验证实例 AZ 中的挂载目标是否存在：

```bash
aws s3files list-mount-targets --file-system-id fs-ID --region REGION
```

跨 AZ 挂载可以工作但会增加延迟。

验证安全组 —— 最常见的修复方法：

- 挂载目标 SG 必须 从计算 SG 接收 TCP 2049 的入站流量
- 计算SG 必须 向挂载目标 SG 发送 TCP 2049 的出站流量
- 修复：`aws ec2 authorize-security-group-ingress --group-id sg-MT --protocol tcp --port 2049 --source-group sg-COMPUTE`

测试连接性：

```bash
nc -zv az-ID.fs-ID.s3files.REGION.on.aws 2049
```

> **注意:** 这些 SG 故障排除步骤也适用于 EFS — 使用 `aws efs describe-mount-targets` 替代。

**挂载在隔离的 VPC 中挂起**：如果 VPC 没有互联网访问权限，S3 文件需要一个 CloudWatch 日志 VPC 端点 (`com.amazonaws.REGION.logs`) 才能完成挂载。

### 4. 类别 C — IAM 权限

**文件系统卡在 "创建中" 状态：**
S3 文件在创建时不会验证 IAM 角色的权限。错误的信任策略或缺少权限 → 卡在 `creating` 状态，`statusMessage` 中访问被拒绝。

检查状态：

```bash
aws s3files get-file-system --file-system-id fs-ID --region REGION
```

检查 `statusMessage`。如果访问被拒绝，修复 IAM 角色 并删除/重新创建。

**挂载访问被拒绝**：计算角色需要 `s3files:ClientMount`。仅限开发/测试，`AmazonS3FilesClientFullAccess` 可以接受 — 避免在生产环境中使用。

**写入权限被拒绝**：计算角色需要 `s3files:ClientWrite`

**根访问被拒绝**：计算角色需要 `s3files:ClientRootAccess`。⚠️ 绕过 POSIX 权限 — 优先使用具有范围 POSIX 用户的访问点。

**检查文件系统策略：**

```bash
aws s3files get-file-system-policy --file-system-id fs-ID --region REGION
```

### 5. 类别 D — 同步

**文件未出现在 S3 中**：写入同步在 ~60 秒内完成。检查状态：

```bash
getfattr -n "user.s3files.status;$(date -u +%s)" filename --only-values
```

常见的 ExportError 值：

| 错误 | 修复 |
|---|---|
| S3AccessDenied | 文件系统 IAM 角色缺少 S3 写入权限 |
| S3BucketNotFound | 桶被删除或重命名 |
| RoleAssumptionFailed | 信任策略配置错误 |
| EncryptionKeyInaccessible | KMS 密钥被禁用或权限被撤销 |
| PathTooLong | 文件路径超过 1,024 字节的 S3 键限制 |

监控：`PendingExports` CloudWatch 指标。增长 = 超过 800 个文件/秒的速率。

### 6. 类别 E — 冲突解决

`.s3files-lost+found-{fs-id}` 中的文件 = 同步冲突（同时通过文件系统和 S3 修改）。S3 胜出；文件系统版本被移动到 lost+found。

### 7. 类别 F — 性能

**首次访问延迟**：正常 — 首次访问目录时导入元数据。

**智能读取路由未工作**：计算角色需要在桶上具有 `s3:GetObject`。

**慢速写入**：如果 `PendingExports` 增长，跨多个文件系统分配。

### 8. 类别 G — 加密/KMS

加密文件系统上的 NFS 服务器错误 = KMS 问题。验证密钥已启用且角色具有 KMS 权限。

### 9. 类别 H — VPC DNS

DNS 解析失败 = VPC DNS 设置被禁用。

```bash
aws ec2 describe-vpc-attribute --vpc-id vpc-ID --attribute enableDnsHostnames
aws ec2 describe-vpc-attribute --vpc-id vpc-ID --attribute enableDnsSupport
```

两者必须为 `true`。如果不是：

```bash
aws ec2 modify-vpc-attribute --vpc-id vpc-ID --enable-dns-hostnames Value=true
aws ec2 modify-vpc-attribute --vpc-id vpc-ID --enable-dns-support Value=true
```

## 故障排除

### AWS CLI 端点 URL 无法解析
CLI 对于 S3 文件来说太旧了。运行 `aws --version` — 如果是 v1.x，升级到 AWS CLI v2：[安装 AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)。

### ECS 任务因 DNS 解析错误失败
使用了 `efsVolumeConfiguration` 而不是 `s3filesVolumeConfiguration`。修复：在 S3 文件特定的卷配置中使用 `fileSystemArn`。

### S3 文件与其他产品混淆
S3 文件不是 S3 挂载点、S3 文件网关或文件缓存。使用 `aws s3files` CLI、`s3files:` IAM 操作、`mount -t s3files`。

### 启用调试日志

在 `/etc/amazon/efs/s3files-utils.conf` 中设置 `logging_level = DEBUG`。日志位于 `/var/log/amazon/efs/mount.log`。

### 收集 AWS 支持的日志

```bash
sudo tar -czf /tmp/s3files-logs.tar.gz /var/log/amazon/efs/ /etc/amazon/efs/s3files-utils.conf
```

## 安全注意事项

- 在诊断 IAM问题时，验证最小权限 — 避免使用 FullAccess 作为捷径
- 没有文件系统策略，任何 VPC 客户端都可以挂载
- 限制 `/var/log/amazon/efs/` 访问 — 日志包含 S3 密钥名称

## 其他资源

- [S3 文件故障排除](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-troubleshooting.html)
- [S3 文件最佳实践](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-best-practices.html)
- [S3 文件配额](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-quotas.html)
