# 将 Lambda 连接到 DynamoDB

## 概述

连接 AWS Lambda 函数到 DynamoDB 表的领域专业知识，包括 IAM 执行角色创建、函数部署、DynamoDB 流配置以及事件源映射设置。

## 将 Lambda 函数连接到 DynamoDB

要设置具有 IAM 角色、流和事件源映射的端到端 Lambda-DynamoDB 集成，请严格按照程序操作。
参见 [Lambda-DynamoDB 连接程序](references/lambda-dynamodb-connection.md)。

## 故障排除

### Lambda 函数未触发
验证事件源映射是否处于活动状态，DynamoDB 流是否已启用并具有正确的视图类型，以及执行角色是否具有适当的权限。有关详细信息，请参阅完整的 [程序](references/lambda-dynamodb-connection.md)。

### 权限被拒绝错误
检查 IAM 角色是否附加了 `AWSLambdaDynamoDBExecutionRole`，并且信任策略允许 Lambda 假定该角色。

### 函数超时问题
增加超时设置或在事件源映射中调整批处理大小。
