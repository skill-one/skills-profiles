# AWS Clean Rooms

## 概述

针对 AWS Clean Rooms 协作和定制机器学习建模的领域专业知识，涵盖权限调试、数据访问问题和 CloudWatch 日志配置。

## 常见任务

### 调试 Clean Rooms 错误

确定失败类型：

**访问拒绝或权限错误？** → 查看 [权限调试步骤](references/permission-debugging.md)。涵盖 IAM 角色策略（内联 + 附加托管）、S3 存储桶策略、KMS 密钥策略、Lake Formation 权限和跨账户信任。

**自定义模型作业缺少 CloudWatch 日志？** → 查看 [自定义模型日志调试步骤](references/custom-model-logging-debugging.md)。涵盖配置模型算法关联的隐私配置、ML 配置角色权限和日志组验证。

## 其他资源

- [Clean Rooms 服务角色设置](https://docs.aws.amazon.com/clean-rooms/latest/userguide/setting-up-roles.html)
- [跨服务混淆代理人预防](https://docs.aws.amazon.com/clean-rooms/latest/userguide/cross-service-confused-deputy-prevention.html)
- [ML 角色文档](https://docs.aws.amazon.com/clean-rooms/latest/userguide/ml-roles.html)
- [Lake Formation 欢迎指南](https://docs.aws.amazon.com/lake-formation/latest/dg/onboarding-lf-permissions.html)
