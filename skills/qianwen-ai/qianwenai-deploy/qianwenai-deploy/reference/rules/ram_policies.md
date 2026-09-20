# qianwenai-deploy 的 RAM 权限

部署需要创建云资源（ECS/EIP/VPC/SG 经 ROS 编排，OSS 临时桶存放产物），因此含写权限。
同一凭证也用于热更新与清理。

## 所需权限

| Action | 用途 |
|--------|------|
| `sts:GetCallerIdentity` | 环境检查时探测身份 |
| `ecs:DescribeAvailableResource` | 拉取当前地域实时有货规格与可用区 |
| `ecs:DescribeInstanceTypes` | 补齐规格的 vCPU / 内存 |
| `ecs:RunCommand` | 下发引导/探活/热更新命令 |
| `ecs:DescribeInvocations` | 读取云助手命令状态 |
| `ecs:DescribeInvocationResults` | 读取云助手命令输出 |
| `rds:DescribeAvailableClasses` | 含 RDS 时校验规格在可用区是否可用 |
| `ros:ValidateTemplate` | 建栈前验证模板 |
| `ros:GetTemplateEstimateCost` | 询价 |
| `ros:CreateStack` | 创建全栈 |
| `ros:GetStack` | 轮询栈状态 |
| `ros:ListStacks` | 存量检测 |
| `ros:ListStackResources` | 定位栈内 ECS/RDS/EIP 等物理资源 |
| `ros:DeleteStack` | 清理栈 |
| `oss:PutObject` / `oss:GetObject` / `oss:ListObjects` | 产物上传与校验 |
| `oss:PutBucket` / `oss:DeleteBucket` / `oss:GetBucketInfo` | 临时桶创建与清理 |

ROS 建栈时按 `from=qianwenai` tag 创建 ECS、EIP、VPC、SecurityGroup（及可选 RDS MySQL）；
这些资源由 ROS 服务代建，凭证需具备对应 `ecs:*` / `vpc:*` / `rds:*` 建删权限，或直接使用
`AliyunROSFullAccess` + `AliyunECSFullAccess` + `AliyunVPCFullAccess` + `AliyunRDSFullAccess`。

## 便捷授权（托管策略）

快速起步可直接附加托管策略：`AliyunROSFullAccess`、`AliyunECSFullAccess`、
`AliyunVPCFullAccess`、`AliyunOSSFullAccess`、`AliyunRDSFullAccess`（含 RDS 时）、
`AliyunSTSAssumeRoleAccess`。生产环境建议按上表收紧到最小权限。

## 权限失败处理

`Forbidden.RAM` 出现在创建类调用（`CreateStack` / `oss mb` / RDS 建实例）→ 停在写操作前，
汇报缺失的 action，不静默重试。只读调用失败 → 标记该项未知并继续。
