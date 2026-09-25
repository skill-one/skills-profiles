# 部署

将 AgentCore 代理部署到 AWS，或诊断部署失败的原因。

## 使用场景

- 准备部署并希望先验证配置
- `agentcore deploy` 命令失败并显示错误
- 希望预览部署将创建的内容，而无需实际部署
- 希望部署到特定目标（测试环境、生产环境）
- 需要回滚到先前版本、固定到特定版本，或设置金丝雀部署

## 输入

`$ARGUMENTS` 是可选的：

```
/agents-deploy                     # 交互式 — 部署前检查或诊断失败
/agents-deploy preflight           # 部署前验证配置和 IAM
/agents-deploy diagnose            # 诊断失败的部署（粘贴错误或读取日志）
/agents-deploy preview             # 显示部署将创建的内容，而无需部署
/agents-deploy rollback            # 回滚到先前版本
```

## 流程

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此功能需要 v0.9.0 或更高版本。如果版本较旧，请告知开发者在使用 `agentcore update` 命令后再继续操作。

### 第 1 步：确定情况

如果存在 `agentcore/agentcore.json` 和 `agentcore/aws-targets.json`，请读取它们。

询问（或根据上下文推断）：

> "您是：
>
> 1. 即将部署并希望先检查所有内容
> 2. 处理失败的部署 — 您看到了什么错误？
> 3. 需要回滚或固定特定版本？"

如果开发者需要版本控制、回滚或金丝雀部署，请加载 [`references/versioning.md`](references/versioning.md) 并遵循其说明。

---

## 路径 A：部署前验证

在运行 `agentcore deploy` 之前执行以下检查：

### 检查 1：验证配置文件

向开发者展示此命令：

```bash
agentcore validate
```

此命令可在 CDK 启动前捕获格式错误的 `agentcore.json`。

### 检查 2：验证区域一致性

最常见的部署失败原因是区域不匹配。向开发者展示以下命令以验证：

```bash
# 您配置的 AWS 区域
aws configure get region

# 您的部署目标中的区域
cat agentcore/aws-targets.json

# 您实际认证的账户
aws sts get-caller-identity
```

`aws-targets.json` 中的 `region` 必须与您的 `aws configure` 默认区域匹配。`account` 必须与 `sts get-caller-identity` 返回的账户 ID 匹配。

### 检查 3：验证 Bedrock 模型访问权限

向开发者展示此命令以检查其区域中启用的模型：

```bash
aws bedrock list-foundation-models --region $(aws configure get region) \
  --query 'modelSummaries[?modelLifecycle.status==`ACTIVE`].modelId' \
  --output table
```

跨区域推理配置文件 ID 使用地理前缀（`us.`, `eu.`, `apac.`）或 `global.` 来控制推理运行的位置。CLI 默认使用 `global.`（例如，`global.anthropic.claude-sonnet-4-5-20250929-v1:0`），该前缀将路由到任何商业区域。地理前缀将推理限制在该地理区域内（例如，`eu.` 保持在 EU 区域）。所有前缀都需要在配置文件覆盖的每个目标区域中启用模型访问。请查阅 Bedrock 文档以了解每个配置文件前缀包含哪些区域。

### 检查 4：预览将部署的内容

```bash
agentcore deploy --dry-run
agentcore deploy --diff
```

`--dry-run` 显示将创建的资源。`--diff` 显示与当前已部署内容的 CDK 差异。

### 检查 5：验证 IAM 权限

向开发者展示所需的权限和此验证命令：

```bash
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names iam:CreateRole \
  --resource-arns "arn:aws:iam::*:role/*BedrockAgentCore*"
```

### 运行部署

```bash
agentcore deploy -y          # 自动确认（别名：agentcore dp -y）
agentcore deploy -y -v       # 详细输出 — 显示资源级事件
agentcore deploy --target staging -y   # 部署到特定目标
```

**内存配置说明：** 如果您的项目包含内存，部署过程会因内存资源变为 ACTIVE 而延长 2–5 分钟。这是正常现象，不是错误。检查状态：

```bash
agentcore status --type memory
```

---

## 路径 B：诊断失败的部署

### 第 B1 步：读取错误

如果开发者粘贴了错误，直接诊断。如果没有，请读取部署日志：

```bash
# 查看最近的部署日志
ls -lt agentcore/.cli/logs/
cat agentcore/.cli/logs/deploy-*.log 2>/dev/null | tail -100
```

### 第 B2 步：匹配已知失败模式

**IAM 权限错误：**

```
User: arn:aws:iam::123456789012:user/dev is not authorized to perform: iam:CreateRole
```

修复：附加所需的 IAM 权限（见上述检查 5）。部署身份需要具有针对 `*BedrockAgentCore*` 角色的 IAM 写入权限。

**CDK 引导未运行：**

```
This stack uses assets, so the toolkit stack must be deployed to the environment
```

修复：

```bash
npx cdk bootstrap aws://<YOUR_ACCOUNT_ID>/<REGION>
```

**ECR 授权错误：**

```
no basic auth credentials
Error response from daemon: Head "https://<YOUR_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/..."
```

修复：

```bash
aws ecr get-login-password --region <REGION> | \
  docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

**部署期间模型访问被拒绝：**

```
ValidationException: The provided model identifier is invalid
```

修复：在 Bedrock 控制台 → 模型访问中启用模型。确保 `agentcore.json` 中的模型 ID 与目标区域中启用的模型匹配。

**区域不匹配：**

```
Stack ... is in region us-east-1 but the target is us-west-2
```

修复：更新 `agentcore/aws-targets.json` 以匹配您的 `aws configure` 默认区域，或运行 `aws configure set region <REGION>`。

**内存卡在 CREATING 状态：**

```
Memory resource is in CREATING state after 10 minutes
```

这种情况不常见 — 正常配置需要 2–5 分钟。检查：

```bash
agentcore status --type memory --json
```

如果卡住，尝试删除并重新添加内存资源。

**服务配额超出：**

```
LimitExceededException: Account limit for AgentCore runtimes exceeded
```

修复：在 AWS 控制台 → 服务配额中请求配额增加 → Amazon Bedrock AgentCore。

### 第 B3 步：修复后重新运行

```bash
agentcore deploy -y
```

如果错误再次出现，请检查 `agentcore status` 以查看所有资源的当前状态：

```bash
agentcore status
agentcore status --state pending-removal  # 标记为删除的资源
```

---

## 部署到多个目标

在 `agentcore/aws-targets.json` 中定义目标：

```json
[
  {
    "name": "staging",
    "description": "测试环境",
    "account": "123456789012",
    "region": "us-east-1"
  },
  {
    "name": "production",
    "description": "生产环境",
    "account": "987654321098",
    "region": "us-west-2"
  }
]
```

部署到特定目标：

```bash
agentcore deploy --target staging -y
agentcore deploy --target production -y
```

## 输出

- 部署前检查结果，包含针对发现问题的具体修复建议
- 部署失败诊断及具体修复方案
- 修复后需要运行的部署命令
