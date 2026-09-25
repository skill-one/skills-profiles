# 使用 Lambda 和请求授权器自定义域名 REST API

## 概述

本标准操作程序 (SOP) 部署了一个具有区域自定义域名、Lambda 后端函数和基于请求的 Lambda 授权器的 REST API。它处理 ACM 证书配置、IAM 角色创建、Lambda 函数部署、具有自定义授权器的 API Gateway REST API 创建、自定义域名配置、基本路径映射和 Route 53 DNS 设置。

架构包括：

- 一个端点类型为 REGIONAL 的 API Gateway REST API
- 一个基于请求的 Lambda 授权器，用于验证头部、查询字符串参数和阶段变量
- 位于 `GET /example` 的 Lambda 后端函数
- 具有 TLS 1.2 的自定义域名
- 连接自定义域名和 API 阶段的基路径映射
- 指向 API Gateway 区域端点的 Route 53 A-别名记录

重要提示：本 SOP 使用区域端点。如果用户请求私有端点，请告知他们本技能仅涵盖区域端点。私有端点需要 VPC 端点配置。

## 参数

- custom_domain_name (必需)：API 的完全限定域名（例如，`api.example.com`）
- region (必需)：所有资源的 AWS 区域。对于区域端点，ACM 证书必须位于同一区域
- hosted_zone_id (必需)：域的 Route 53 托管区域 ID
- acm_certificate_arn (可选)：覆盖自定义域名的现有 ACM 证书的 ARN。如果未提供，步骤 2 将创建一个
- stage_name (可选，默认："dev")：API Gateway 阶段名称

参数获取约束：

- 您必须在单个提示中一次性请求所有必需参数，而不是一次一个
- 您必须支持多种输入方法（直接输入、文件路径、URL）
- 您必须在继续之前确认已成功获取所有参数
- 您必须告知用户本技能使用硬编码的演示授权值（headerValue1、queryValue1、stageValue1），这些值不适用于生产。对于生产环境，请使用 AWS Secrets Manager 或 Systems Manager Parameter Store 管理授权凭据。参见：https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- 您必须验证 custom_domain_name 是一个有效的 FQDN

## 步骤

### 0. 验证依赖项

约束：

- 您必须验证以下工具可用：aws-cli、python3、sed、node (v22+)
- 您必须向用户报告任何缺失的工具，并使用清晰的提示信息
- 您必须询问用户是否希望在缺少工具的情况下继续
- 您必须尊重客户随时中止的决定
- 您必须向客户解释正在执行哪个步骤、为什么以及正在调用哪个工具

### 1. 获取 AWS 账户 ID

此步骤必须在所有其他步骤之前执行。

约束：

- 您必须使用：`aws sts get-caller-identity --query 'Account' --output text` 获取账户 ID
- 您必须将结果存储为 {account_id}，并在所有引用 {account_id} 的后续步骤中重用它
- 如果凭证未配置，您必须中止

### 2. 请求 ACM 证书

如果已提供 acm_certificate_arn，则跳过此步骤。

约束：

- 您必须使用：`aws acm request-certificate --domain-name {custom_domain_name} --validation-method DNS --region {region}` 请求证书
- 您必须从响应中捕获 CertificateArn
- 您必须使用：`aws acm describe-certificate --certificate-arn {cert_arn} --query 'Certificate.DomainValidationOptions[0].ResourceRecord' --region {region}` 获取 DNS 验证记录
- 您必须使用：`aws route53 change-resource-record-sets --hosted-zone-id {hosted_zone_id} --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"{validation_name}","Type":"CNAME","TTL":300,"ResourceRecords":[{"Value":"{validation_value}"}]}}]}'` 在 Route 53 中创建验证 CNAME
- 您必须使用：`aws acm wait certificate-validated --certificate-arn {cert_arn} --region {region}` 等待证书验证
- 等待命令可能需要长达 30 分钟。如果超时，请手动检查状态：`aws acm describe-certificate --certificate-arn {cert_arn} --query 'Certificate.Status' --region {region}` 并如果状态仍然是 PENDING_VALIDATION，则重试等待命令
- 您必须不在证书状态为 ISSUED 之前继续
- 您必须将证书 ARN 存储为 acm_certificate_arn，以在步骤 7 中使用

### 3. 创建 IAM 执行角色

约束：

- 您必须创建两个 IAM 角色：一个用于授权器 Lambda，一个用于示例函数 Lambda
- 两个角色都使用来自 `scripts/lambda-trust-policy.json` 的相同信任策略。信任策略包括一个作用域到用户账户 ID 的 `aws:SourceAccount` 条件
- 您必须创建信任策略的工作副本，并将 `ACCOUNT_ID` 占位符替换为步骤 1 中的实际账户 ID。使用：`sed 's/ACCOUNT_ID/{account_id}/' scripts/lambda-trust-policy.json > /tmp/lambda-trust-policy.json`
- 您必须使用：`aws iam create-role --role-name request-authorizer-role --assume-role-policy-document file:///tmp/lambda-trust-policy.json` 创建授权器角色
- 您必须使用：`aws iam attach-role-policy --role-name request-authorizer-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole` 将基本执行策略附加到授权器角色
- 您必须使用：`aws iam create-role --role-name example-function-role --assume-role-policy-document file:///tmp/lambda-trust-policy.json` 创建示例函数角色
- 您必须使用：`aws iam attach-role-policy --role-name example-function-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole` 将基本执行策略附加到示例函数角色
- 您必须从每个 create-role 响应中捕获角色 ARN，以在步骤 4 中使用
- 您必须在创建 Lambda 函数之前等待至少 10 秒钟，因为 IAM 角色传播是最终一致的

### 4. 创建和部署 Lambda 函数

约束：

- 您必须创建两个 Lambda 函数：请求授权器和示例函数
- 对于授权器函数：
  - 您必须使用内联代码创建函数。首先将代码写入文件并打包：
    `python3 -c "import zipfile,io,base64; z=io.BytesIO(); f=zipfile.ZipFile(z,'w'); f.writestr('index.mjs', open('scripts/authorizer.mjs').read()); f.close(); open('/tmp/authorizer.zip','wb').write(z.getvalue())"`
  - 然后使用：`aws lambda create-function --function-name request-authorizer --runtime nodejs22.x --handler index.handler --role {authorizer_role_arn} --zip-file fileb:///tmp/authorizer.zip --timeout 10 --region {region}` 创建函数
- 对于示例函数：
  - 您必须使用内联代码创建函数。首先将代码写入文件并打包：
    `python3 -c "import zipfile,io; z=io.BytesIO(); f=zipfile.ZipFile(z,'w'); f.writestr('index.mjs', open('scripts/example_function.mjs').read()); f.close(); open('/tmp/example_function.zip','wb').write(z.getvalue())"`
  - 然后使用：`aws lambda create-function --function-name example-function --runtime nodejs22.x --handler index.handler --role {example_role_arn} --zip-file fileb:///tmp/example_function.zip --timeout 10 --region {region}` 创建函数
- 您必须通过调用：`aws lambda get-function --function-name {function_name} --region {region}` 验证每个函数是否已创建

### 5. 创建具有请求授权器的 REST API

约束：

- 您必须使用：`aws apigateway create-rest-api --name custom-domain-api --endpoint-configuration types=REGIONAL --region {region}` 创建 REST API
- 您必须捕获 API ID 并获取根资源 ID：`aws apigateway get-resources --rest-api-id {api_id} --region {region}`
- 您必须使用：`aws apigateway create-authorizer --rest-api-id {api_id} --name request-authorizer --type REQUEST --authorizer-uri 'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account_id}:function:request-authorizer/invocations' --identity-source 'method.request.header.HeaderAuth1,method.request.querystring.QueryString1,context.stage' --region {region}` 创建基于请求的 Lambda 授权器
- 您必须从响应中捕获授权器 ID
- 您必须使用：`aws lambda add-permission --function-name request-authorizer --statement-id apigateway-auth-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:{region}:{account_id}:{api_id}/authorizers/{authorizer_id}' --region {region}` 授予 API Gateway 调用授权器的权限
- 您必须使用：`aws apigateway create-resource --rest-api-id {api_id} --parent-id {root_resource_id} --path-part example --region {region}` 创建 /example 资源
- 您必须使用：`aws apigateway put-method --rest-api-id {api_id} --resource-id {example_resource_id} --http-method GET --authorization-type CUSTOM --authorizer-id {authorizer_id} --region {region}` 创建 GET 方法
- 您必须使用：`aws apigateway put-integration --rest-api-id {api_id} --resource-id {example_resource_id} --http-method GET --type AWS_PROXY --integration-http-method POST --uri 'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account_id}:function:example-function/invocations' --region {region}` 创建 Lambda 代理集成
- 您必须使用：`aws lambda add-permission --function-name example-function --statement-id apigateway-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn 'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/GET/example' --region {region}` 授予 API Gateway 调用示例函数的权限
- 您必须不在配置所有资源、方法和集成后创建部署
- 您必须通过验证 QueryString1 和 HeaderAuth1 是否匹配预期模式并强制执行大小限制来配置请求验证，以拒绝格式错误的查询参数和头部

### 6. 部署 API

约束：

- 您必须使用：`aws apigateway create-deployment --rest-api-id {api_id} --stage-name {stage_name} --region {region}` 创建部署
- 您必须使用：`aws apigateway update-stage --rest-api-id {api_id} --stage-name {stage_name} --patch-operations op=replace,path=/variables/StageVar1,value=stageValue1 --region {region}` 设置授权器所需的阶段变量
- 您必须通过调用：`aws apigateway get-stage --rest-api-id {api_id} --stage-name {stage_name} --region {region}` 并确认 StageVar1 是否存在于变量中来验证部署和阶段变量
- 您必须启用阶段上的访问日志。首先创建日志组：`aws logs create-log-group --log-group-name api-gw-access-logs --region {region}`。然后使用以下格式启用日志：`aws apigateway update-stage --rest-api-id {api_id} --stage-name {stage_name} --patch-operations op=replace,path=/accessLogSettings/destinationArn,value=arn:aws:logs:{region}:{account_id}:log-group:api-gw-access-logs op=replace,path=/accessLogSettings/format,value='{"requestId":"$context.requestId","ip":"$context.identity.sourceIp","requestTime":"$context.requestTime","httpMethod":"$context.httpMethod","resourcePath":"$context.resourcePath","status":"$context.status"}' --region {region}`

### 7. 创建自定义域名和基路径映射

约束：

- 您必须使用：`aws apigateway create-domain-name --domain-name {custom_domain_name} --regional-certificate-arn {acm_certificate_arn} --endpoint-configuration types=REGIONAL --security-policy TLS_1_2 --region {region}` 创建自定义域名
- 您必须从响应中捕获 regionalDomainName 和 regionalHostedZoneId，以在步骤 8 中使用
- 您必须使用：`aws apigateway create-base-path-mapping --domain-name {custom_domain_name} --rest-api-id {api_id} --stage {stage_name} --base-path '(none)' --region {region}` 创建基路径映射
- 您必须通过调用：`aws apigateway get-domain-name --domain-name {custom_domain_name} --region {region}` 验证域名是否已创建
- 您必须不在将安全策略降级到 TLS_1_2 以下

### 8. 创建 Route 53 DNS 记录

约束：

- 您必须创建 `scripts/dns-record.json` 的工作副本并替换占位符：`sed -e 's/CUSTOM_DOMAIN_NAME/{custom_domain_name}/' -e 's/REGIONAL_DOMAIN_NAME/{regional_domain_name}/' -e 's/REGIONAL_HOSTED_ZONE_ID/{regional_hosted_zone_id}/' scripts/dns-record.json > /tmp/dns-record.json`
- 命令是：`aws route53 change-resource-record-sets --hosted-zone-id {hosted_zone_id} --change-batch file:///tmp/dns-record.json`
- 您必须使用从步骤 7 捕获的 regionalDomainName 和 regionalHostedZoneId，而不是用户的托管区域 ID 作为 AliasTarget
- 当使用 Route 53 作为 DNS 提供商时，您必须使用 A-别名记录（而不是 CNAME）
- 您应该告知用户 DNS 传播可能需要长达 48 小时

### 9. 验证最终设置

约束：

- 您应该运行 `scripts/validate.sh {custom_domain_name} {api_id} {region}` 来检查所有资源
- 您必须告知用户使用：`curl 'https://{custom_domain_name}/example?QueryString1=queryValue1' -H 'HeaderAuth1: headerValue1'` 进行测试
- 您必须解释预期响应是 200 并包含 `{"message": "Hello from the example function!"}`
- 您必须解释缺少正确 HeaderAuth1 头部或 QueryString1 查询参数的请求将被授权器拒绝
- 您必须提供所有创建资源的摘要，包括：
  - ACM 证书 ARN
  - IAM 角色ARN
  - Lambda 函数 ARN
  - REST API ID 和阶段名称
  - 授权器 ID
  - 自定义域名和区域域名
  - Route 53 DNS 记录

## 示例

### 示例输入

```
custom_domain_name: api.example.com
region: us-east-2
hosted_zone_id: Z2OJLYMUO9EFXC
stage_name: prod
```

### 示例输出

```
为 api.example.com 发行的 ACM 证书
  ARN: arn:aws:acm:us-east-2:123456789012:certificate/abc-123

创建 IAM 角色
  授权器: arn:aws:iam::123456789012:role/request-authorizer-role
  示例: arn:aws:iam::123456789012:role/example-function-role

部署 Lambda 函数
  授权器: arn:aws:lambda:us-east-2:123456789012:function:request-authorizer
  示例: arn:aws:lambda:us-east-2:123456789012:function:example-function

部署 REST API
  API ID: a1b2c3d4e5
  阶段: prod (StageVar1=stageValue1)
  授权器: request-authorizer (REQUEST 类型)

配置自定义域名
  域名: api.example.com
  区域端点: d-abc123.execute-api.us-east-2.amazonaws.com
  TLS: 1.2

创建 Route 53 DNS 记录
  A-别名: api.example.com -> d-abc123.execute-api.us-east-2.amazonaws.com

测试命令（授权）:
  curl 'https://api.example.com/example?QueryString1=queryValue1' -H 'HeaderAuth1: headerValue1'

测试命令（拒绝）:
  curl 'https://api.example.com/example'
```

## 故障排除

### 证书卡在 PENDING_VALIDATION
通过运行 `aws acm describe-certificate --certificate-arn {arn} --query 'Certificate.DomainValidationOptions'` 验证 Route 53 中是否存在 DNS 验证 CNAME 记录。确保 CNAME 创建在正确的托管区域。

### API 调用返回 403 Forbidden
请求授权器检查三个值：`HeaderAuth1` 头部必须为 `headerValue1`，`QueryString1` 查询参数必须为 `queryValue1`，阶段变量 `StageVar1` 必须为 `stageValue1`。验证所有三个都存在且正确。检查授权器函数的 CloudWatch 日志以获取详细错误消息。

### 返回 401 Unauthorized
当授权器函数无法被调用时，API Gateway 返回 401。验证是否为 API Gateway 添加了调用授权器的 Lambda 权限。检查授权器 URI 是否正确。

### 缺少身份验证令牌（403）
请求路径与配置的资源不匹配。通过 `aws apigateway get-resources --rest-api-id {api_id}` 验证是否存在 `/example` 资源。确保在创建所有资源后部署 API。

### 自定义域名无响应
DNS 传播可能需要长达 48 小时。使用 `dig {custom_domain_name}` 进行检查。验证 A-别名记录指向正确的 regionalDomainName 和 regionalHostedZoneId，这些信息来自 create-domain-name 响应。

### 阶段变量未设置
如果授权器拒绝所有请求，请验证是否使用 `aws apigateway get-stage --rest-api-id {api_id} --stage-name {stage_name} --query 'variables'` 设置了阶段变量。StageVar1 变量必须设置为 `stageValue1`。

### 创建 Lambda 时找不到 IAM 角色
IAM 角色传播是最终一致的。在创建 Lambda 函数之前，请等待至少 10 秒钟。使用 `aws iam get-role --role-name {role_name}` 验证角色 ARN。

### 基路径映射不工作
通过 `aws apigateway get-base-path-mappings --domain-name {custom_domain_name}` 进行验证。基路径 `(none)` 将域名根映射到阶段。确保成功部署到阶段。

## 安全注意事项

- Lambda 授权器中的硬编码授权值（`headerValue1`、`queryValue1`、`stageValue1`）仅用于**演示**，不适用于生产。在生产环境中，请使用适当的身份验证机制（JWT 验证、来自 AWS Secrets Manager 的 API 密钥或 OAuth）。
- 在 API 阶段上启用请求速率限制以防止滥用。使用以下命令配置速率和突发限制：`aws apigateway update-stage --rest-api-id {api_id} --stage-name {stage_name} --patch-operations op=replace,path=/throttle/rateLimit,value=1000 op=replace,path=/throttle/burstLimit,value=2000`
- 为 Lambda 日志组启用 CloudWatch 日志加密。关联一个 KMS 密钥：`aws logs associate-kms-key --log-group-name /aws/lambda/request-authorizer --kms-key-arn <KMS_KEY_ARN>`
- 使用 AWS WAF 保护公共 API，以减轻常见攻击（SQL 注入、XSS、基于速率的规则）：`aws wafv2 associate-web-acl --web-acl-arn <WAF_ACL_ARN> --resource-arn arn:aws:apigateway:{region}::/restapis/{api_id}/stages/{stage_name}`

## 额外资源

- [API Gateway 自定义域名](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains.html)
- [ACM 证书验证](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html)
- [Lambda 授权器](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [Route 53 别名记录](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html)
- [API Gateway 区域端点](https://docs.aws.amazon.com/apigateway/latest/developerguide/create-regional-api.html)
