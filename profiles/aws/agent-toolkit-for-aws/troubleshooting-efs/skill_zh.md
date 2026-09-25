# EFS 故障排除

## 概述

诊断和解决 Amazon EFS 问题的领域专业知识。涵盖挂载失败、NFS 连接性、IAM 和 POSIX 权限、吞吐量和性能，以及加密问题。

有关权威指南，请参阅 [EFS 故障排除](https://docs.aws.amazon.com/efs/latest/ug/troubleshooting.html)。

## 常见任务

### 0. 验证依赖项

- 您必须验证 `aws` CLI 是否可用
- 您必须检查实例上是否安装了 `amazon-efs-utils` 或 `nfs-utils`
- 您必须仅检查工具的存在和版本 —— 绝不能在验证期间执行破坏性或可变命令
- 您必须告知用户如果缺少任何必需工具
- 如果工具不可用，您必须尊重用户的中止决定
- 您应该在使用它之前解释每个步骤的作用和原因
- 您应该显示写命令并在执行前等待用户确认

### 1. 分类问题

| 症状 | 类别 |
|---|---|
| "错误的文件系统类型" 或挂载命令失败 | A: 缺少 NFS 客户端 |
| 连接超时（挂起 2+ 分钟） | B: 网络/安全组 |
| "服务器拒绝访问" | C: IAM/权限 |
| 吞吐量慢或延迟高 | D: 性能 |
| 加密文件系统的 NFS 服务器错误 | E: 加密/KMS |
| DNS 名称解析失败 | F: VPC DNS |

### 2. 类别 A — 缺少 NFS 客户端

```bash
# Amazon Linux / RHEL / CentOS
sudo yum -y install amazon-efs-utils  # 推荐的（包含挂载辅助程序 + TLS）
# 或者
sudo yum -y install nfs-utils

# Ubuntu / Debian
sudo apt-get install nfs-common
```

### 3. 类别 B — 网络/安全组

连接超时是 EFS 挂载失败的 #1 原因 —— 几乎总是安全组问题。

1. 验证挂载目标是否存在于实例的可用区中：

```bash
aws efs describe-mount-targets --file-system-id fs-ID --region REGION
```

1. 验证安全组 — 检查双向：
   - 挂载目标 SG: `aws ec2 describe-security-groups --group-ids sg-MT` — 必须允许来自计算 SG 的 TCP 2049 入站
   - 计算 SG: 必须允许到挂载目标 SG 的 TCP 2049 出站
   - 快速修复: `aws ec2 authorize-security-group-ingress --group-id sg-MT --protocol tcp --port 2049 --source-group sg-COMPUTE`

2. 测试连接性：

```bash
nc -zv fs-ID.efs.REGION.amazonaws.com 2049
```

> **注意:** 这些安全组故障排除步骤也适用于 S3 文件。唯一的区别是 S3 文件使用 `aws s3files list-mount-targets` 而不是 `aws efs describe-mount-targets`。

### 4. 类别 C — IAM/权限

**使用 `-o iam` 时出现 "服务器拒绝访问":**

- 检查基于身份的 IAM 策略是否具有 `elasticfilesystem:ClientMount`
- 检查文件系统资源策略：

```bash
aws efs describe-file-system-policy --file-system-id fs-ID --region REGION
```

**注意:** 只有当存在需要 IAM 授权的文件系统策略时，IAM 授权才会生效。如果没有文件系统策略，VPC 中任何具有 TCP 2049 访问权限的客户端都可以挂载 —— 即使使用 `-o iam`。要强制执行 IAM，您必须创建一个拒绝匿名访问的文件系统策略。

**POSIX 权限拒绝（非 IAM）:**

- 检查文件/目录所有权: `ls -la /mnt/efs/`
- 使用访问点来强制执行一致的 UID/GID 权限

### 5. 类别 D — 性能

**检查吞吐量模式:**

```bash
aws efs describe-file-systems --file-system-id fs-ID --region REGION --query 'FileSystems[0].ThroughputMode'
```

**突发信用耗尽（仅限突发模式）:**

```bash
aws cloudwatch get-metric-statistics --namespace AWS/EFS --metric-name BurstCreditBalance --dimensions Name=FileSystemId,Value=fs-ID --period 3600 --statistics Average --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) --end-time $(date -u +%Y-%m-%dT%H:%M:%S)
```

如果信用接近零，切换到弹性吞吐量：

```bash
aws efs update-file-system --file-system-id fs-ID --throughput-mode elastic --region REGION
```

**通用与最大 I/O:**

- 检查 `PercentIOLimit` 指标 — 如果持续 >80%，请考虑最大 I/O
- 注意：性能模式是不可变的 — 必须创建新的文件系统并迁移

### 6. 类别 E — 加密/KMS

加密文件系统的 NFS 服务器错误 = KMS 密钥问题。

- 验证 KMS 控制台中的密钥是否已启用
- 验证 EFS 服务链接角色是否具有 KMS 权限
- 如果密钥被删除：如果在宽限期内的，取消删除

### 7. 类别 F — VPC DNS

DNS 解析失败 = VPC DNS 设置已禁用。

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

### 挂载挂起然后超时
最常见的原因：安全组。验证计算和挂载目标之间的 TCP 2049 是否开放。

### 重启时自动挂载失败
`/etc/fstab` 条目必须包含 `_netdev` 选项，以便在挂载前等待网络。

### 重连后 "nfs not responding"
旧内核 TCP 端口重用的 Bug。更新内核或添加 `noresvport` 挂载选项。

### 启用调试日志

在 `/etc/amazon/efs/efs-utils.conf` 中设置 `logging_level = DEBUG`。日志位于 `/var/log/amazon/efs/mount.log`。

### 收集 AWS 支持所需的日志

```bash
sudo tar -czf /tmp/efs-logs.tar.gz /var/log/amazon/efs/ /etc/amazon/efs/efs-utils.conf
```

## 安全注意事项

- 只有当存在文件系统策略时，IAM 授权才会生效 —— 没有策略，任何具有 TCP 2049 访问权限的 VPC 客户端都可以挂载
- 在故障排除访问拒绝时，验证基于身份和基于资源的策略
- 使用 `-o tls` 进行传输加密 —— 未加密的 NFS 流量在网络上是可见的
- 限制 `/var/log/amazon/efs/` 访问 —— 日志可能包含文件系统 ID 和挂载目标 IP

## 其他资源

- [EFS 故障排除](https://docs.aws.amazon.com/efs/latest/ug/troubleshooting.html)
- [EFS 性能](https://docs.aws.amazon.com/efs/latest/ug/performance.html)
- [EFS 挂载辅助程序](https://docs.aws.amazon.com/efs/latest/ug/using-amazon-efs-utils.html)
