# 亚马逊 EC2 计算

与 AWS MCP 服务器配合使用效果最佳；单独使用 AWS CLI 也可工作——两者均无硬性依赖。

## 严重警告

**启动配置已弃用**，不支持当前的 EC2 实例类型；新账户无法创建它们。为每个新的自动扩展组使用启动模板。参见 [auto-scaling.md](references/auto-scaling.md)。

**自动扩展组默认忽略 ELB 健康检查**：自动扩展组仅使用 EC2 状态检查，除非您设置 `--health-check-type ELB`。如果没有设置，则负载均衡器的健康检查失败的实例将永远处于服务状态。参见 [auto-scaling.md](references/auto-scaling.md)。

**IMDSv2 跳数限制会导致容器中断**：默认的 `HttpPutResponseHopLimit` 为 1，使得 IMDSv2 令牌 PUT 响应无法到达容器化进程（额外的跳数超过了响应 TTL），因此令牌请求超时。为 bridge/awsvpc 容器工作负载设置 `HttpPutResponseHopLimit=2`。 （如果 IMDSv2 是 *必需的*，后续的无令牌 GET 将返回 `401`；如果可选，则静默回退到 IMDSv1。）参见 [provisioning.md](references/provisioning.md)。

**T3/T3a/T4g 默认为无限制模式**：与 T2（标准）不同，这些实例会无限制地突发，但在 24 小时平均 CPU 超过基线时会产生额外 CPU 信用额度——这是一个隐蔽的成本泄漏。参见 [instance-selection.md](references/instance-selection.md)。

**实例存储是易失的**：实例存储卷上的数据在停止、休眠、终止、实例类型更改和主机故障时丢失——只有在重启时才会保留。将任何持久数据放在 EBS/EFS/S3 上。参见 [instance-selection.md](references/instance-selection.md)。

## 您需要什么？

| 如果您正在决定... | 指导 |
|-----------------------|----------|
| 实例系列 / 大小 / Graviton / GPU / 突发 | [instance-selection.md](references/instance-selection.md) — 从工作负载→系列的表格开始 |
| 如何定义实例并重复使用（启动模板） | [provisioning.md](references/provisioning.md) |
| 如何运行许多可以自动扩展的实例 | [auto-scaling.md](references/auto-scaling.md) |
| 如何在没有 SSH 密钥的情况下访问/修补/管理实例 | [systems-manager.md](references/systems-manager.md) |

## 快速导航

| 您想要... | 前往 |
|----------------|-------|
| 选择实例类型、Graviton vs x86、突发信用额度、GPU、实例存储 vs EBS | [instance-selection.md](references/instance-selection.md) |
| 创建启动模板、用户数据、密钥对、IMDSv2、放置组、弹性 IP | [provisioning.md](references/provisioning.md) |
| 设置或修复自动扩展组、扩展策略、实例刷新、Spot、生命周期挂钩 | [auto-scaling.md](references/auto-scaling.md) |
| 获取无 SSH 访问、修补舰队或修复不显示为管理节点的实例 | [systems-manager.md](references/systems-manager.md) |
| 创建、共享或退役（弃用/禁用/注销）AMI | [ami-management.md](references/ami-management.md) |
| 修复故障（无法连接、状态检查失败、容量错误、卡住的实例） | [troubleshooting.md](references/troubleshooting.md) |

## 常见工作流

**"快速搭建自动扩展的 Web 舰队"** → 创建启动模板（AMI、类型、IMDSv2），然后创建引用它的自动扩展组，并使用 `--health-check-type ELB` 和目标跟踪策略，参见 [auto-scaling.md](references/auto-scaling.md)。对于公共入口点，根据下文的 Security Considerations 和 [auto-scaling.md](references/auto-scaling.md) 中的负载均衡器说明，通过 TLS/ACM、WAF 和安全响应头保护负载均衡器——负载均衡器的构建本身属于 `aws-networking`。

**"将新的 AMI 部署到我的舰队"** → 新的启动模板版本 → 实例刷新；固定一个数字的启动模板版本以便回滚工作，参见 [auto-scaling.md](references/auto-scaling.md)。

**"无堡垒机连接到私有实例"** → 给实例 SSM 权限（一个具有 `AmazonSSMManagedInstanceCore` 的实例配置文件，或账户级别的 DHMC）加上网络路径，然后使用会话管理器，参见 [systems-manager.md](references/systems-manager.md)。

**"降低 EC2 成本"** → 合理调整大小（突发 vs 固定性能），在支持 Arm64 的应用程序中使用 Graviton，使用 `price-capacity-optimized` 的 Spot 来创建容错舰队，释放空闲的弹性 IP，参见 [instance-selection.md](references/instance-selection.md)。

## 故障排除

| 症状 | 可能的原因 | 快速修复 |
|---------|-------------|-----------|
| SSH "连接超时" | 网络路径（SG/NACL/路由/无公网 IP） | 从您的 IP 打开 TCP 22；检查路由到 IGW；验证公网 IP — 参见 [troubleshooting.md](references/troubleshooting.md) |
| SSH "连接被拒绝" | 主机：sshd 停止或仍在启动 | 等待启动；通过会话管理器或串行控制台检查 sshd/端口 |
| `InsufficientInstanceCapacity` | AWS 在 AZ 中缺乏该类型的容量（不是配额） | 尝试另一个 AZ / 实例类型 / 重试；不要请求配额增加 |
| `InstanceLimitExceeded` | vCPU 配额达到（这是配额） | 请求实例系列的 Service Quotas 增加 |
| 自动扩展组从未替换 LB 不健康的实例 | 健康检查类型仍然是 EC2 | 设置 `--health-check-type ELB` |
| 实例卡在 `Pending:Wait`，终止后约 1 小时 | 生命周期挂钩从未完成（心跳 3600 秒，默认 ABANDON） | 调用 `complete-lifecycle-action` CONTINUE，或设置 DefaultResult CONTINUE |
| 系统状态检查失败 | AWS 主机/硬件 | 停止/启动以迁移到新硬件（重启不会） |
| 实例状态检查失败 | 实例 OS/网络配置 | 重启或修复 OS/网络配置 |

完整表格和更多错误参见 [troubleshooting.md](references/troubleshooting.md)。

## 安全注意事项

- **强制执行 IMDSv2** (`HttpTokens=required`) 在启动模板上，以阻止基于 SSRF 的凭证窃取；按区域设置账户级默认值（仅适用于新启动）。
- **优先使用会话管理器而不是入站 SSH** — 无需打开端口 22，无需密钥管理，并且会话 API 调用有 CloudTrail 记录；启用会话管理器会话日志记录到 CloudWatch Logs/S3（默认关闭）以捕获会话中的命令本身 — 参见 [systems-manager.md](references/systems-manager.md)。
- **使用实例配置文件，绝不要使用嵌入式凭证**；将角色限制为最小权限。
- **加密 EBS/AMIs**；要跨账户共享加密的 AMI，请在客户管理的 KMS 密钥下重新加密（默认的 `aws/ebs` 密钥无法共享）。
- **在所有区域启用 CloudTrail** 以审计 EC2/ASG/SSM API 活动，并对敏感操作（安全组更改、来自意外主体的 `RunInstances`/`TerminateInstances`）设置警报，以便未授权的更改能够暴露。
- **对于面向公众的 Web 舰队**，在负载均衡器的 HTTPS 监听器上使用 ACM 证书加密传输中的流量，并添加 AWS WAF 以提供深度防御，防止常见的 Web 攻击 — 负载均衡器/WAF 的设置本身属于 `aws-networking`。
- 超出此指导的建议，请参阅 [AWS EC2 安全最佳实践](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security.html) 和客机 OS 的 CIS 基准。

## 未涵盖于此技能的内容

- **使用最佳实践默认值快速启动单个加固实例** → 使用 `launching-ec2-instance-with-best-practices` 技能
- **为 EC2 创建 IAM 角色 / 实例配置文件** → 使用 `setting-up-ec2-instance-profiles` 技能
- **使用 Image Builder 管道构建 AMI** → 使用 `amazon-ec2-image-builder` 技能
- **Lambda / 无服务器** → `aws-serverless`；**ECS/Fargate** → `aws-containers`；**EKS/Kubernetes** → `kubernetes`
- **VPC、子网、ALB/NLB、端点** → `aws-networking` 或内置知识
- **IAM 策略逻辑和 CloudWatch 仪表板/代理设置** → `aws-iam`，`aws-observability`
