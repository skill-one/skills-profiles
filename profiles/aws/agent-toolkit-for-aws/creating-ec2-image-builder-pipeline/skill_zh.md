# 创建 EC2 Image Builder 管道

## 概述

创建和管理自动化自定义 AMI 创建的 EC2 Image Builder 管道的领域专业知识。涵盖完整生命周期：IAM 角色设置、构建组件定义、镜像配方创建、基础设施和分发配置、管道执行和启动模板创建。

## 创建 Image Builder 管道

要创建具有自定义 AMI 构建和跨区域分发的完整 EC2 Image Builder 管道，请严格遵循以下步骤。
参见 [EC2 Image Builder 管道步骤](references/ec2-image-builder-pipeline.md)。

## 故障排除

### 管道操作中的 InvalidParameterValueException
使用 API 调用返回的确切 ARN —— 不要手动构造 ARN。管道 ARN 必须遵循 `arn:<分区>:imagebuilder:<区域>:<账户>:image-pipeline/<名称>`。

### InstanceProfileNotFoundException
创建实例配置文件后等待 10–15 秒再使用它。IAM 更改最终一致。

### ResourceAlreadyExistsException
首先删除现有资源，或使用不同的名称/版本。

### 构建实例无法启动
验证实例配置文件是否存在，所有三个 IAM 策略均已附加，并且实例类型在区域内可用。
