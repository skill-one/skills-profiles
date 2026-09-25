# AWS CDK

## 概述

针对 CDK 构建编写、部署工作流、合规性、漂移、导入资源、安全重构以及排错 CDK CLI / CloudFormation 错误的专业领域知识。

**不适用场景：** 原生 CloudFormation YAML/JSON。SAM。Terraform/Pulumi。超出 CDK Pipelines 的 CI/CD。这些场景应使用内置知识或专业技能处理。

## 严重警告

**致命的耦合：** 删除跨堆栈引用会导致部署死锁（`Export ... 不能被删除，因为它被 ... 使用`）。首选修复方法：先减弱引用 — `CrossStackReferences.of($RESOURCE).produce(ReferenceStrength.BOTH)` 然后改为 `WEAK`，最后删除（需要三次部署）。遗留回退方案：两步部署 `this.exportValue()` 配方。参见 [排错部署](references/troubleshooting-deployment.md)。

**构建 ID 变更会导致替换：** 重命名/移动构建会改变其逻辑 ID → CloudFormation 会替换资源（有状态资源会丢失数据）。部署前务必 `cdk diff`。参见 [重构并防止替换](references/refactor-and-prevent-replacement.md)。

**UPDATE_ROLLBACK_FAILED：** 堆栈卡住。使用 `cdk rollback $STACK` 或 `cdk rollback $STACK --orphan <LogicalId>` 修复。表达式模式堆栈是例外 — 它们根本无法回滚。参见 [排错部署](references/troubleshooting-deployment.md)。

**Hotswap 和表达式模式仅限开发使用：** `--hotswap` / `--hotswap-fallback` 会绕过 CloudFormation 并故意产生漂移；`--express` 在资源稳定前报告成功并禁用自动回滚。你绝对不能在生产环境中使用它们。失败的 `--express` 部署无法回滚 — 通过另一个 `--express` 部署向前推进来恢复。参见 [快速部署](references/fast-deployments.md)。

**非空 S3 桶在销毁后仍会保留：** 你必须同时设置 `removalPolicy: DESTROY` 和 `autoDeleteObjects: true`。版本化桶更糟 — 删除标记即使在看似删除后仍会保留。

## 常见工作流

| 任务 | 快速命令 | 详情 |
|------|--------------|---------|
| 初始化 | `cdk bootstrap aws://$ACCOUNT/$REGION` | [初始化和项目设置](references/bootstrap-and-project-setup.md) |
| 新建 TS 项目 | `cdk init app --language typescript` — 使用 `tsx`，`eslint-plugin-awscdk` | [初始化和项目设置](references/bootstrap-and-project-setup.md) |
| 新建 Python 项目 | `cdk init app --language python` — 固定依赖，使用虚拟环境 | [初始化和项目设置](references/bootstrap-and-project-setup.md) |
| 部署 | `cdk synth --strict` → `cdk diff` → `cdk deploy` | 部署到生产环境前务必 diff |
| 快速开发迭代 | `cdk deploy --hotswap-fallback`，`cdk watch` 或 `cdk deploy --express` — 仅限开发，绝不能用于生产 | [快速部署](references/fast-deployments.md) |
| cdk-nag | `Aspects.of(app).add(new AwsSolutionsChecks())` | [合规性和漂移](references/compliance-and-drift.md) |
| 漂移 | `cdk drift $STACK` (CI 中使用 `--fail`) | [合规性和漂移](references/compliance-and-drift.md) |
| 导入资源 | `cdk import` (交互式或 `--resource-mapping` 用于 CI)，`cdk deploy --import-existing-resources` | [导入和迁移](references/import-and-migrate.md) |
| 安全重构 | `cdk refactor --unstable=refactor` — 同一部署中不更改属性 | [重构并防止替换](references/refactor-and-prevent-replacement.md) |

## 快速部署 — Hotswap 与表达式（仅限开发）

两者都牺牲了安全性以换取速度，你绝对不能在生产环境中使用。

**选择它们之间的方法：** 当你主要使用可热替换资源且漂移不重要时，使用 `--hotswap` / `--hotswap-fallback` 以获得最快的循环。当漂移不可接受或资源不可热替换时，使用 `--express`。

恢复工作流（通过 `--revert-drift` 热替换漂移）、失败 `--express` 部署向前推进、可热替换资源规则以及生产环境的 IAM/监控禁令等所有内容都在完整指南中：[快速部署](references/fast-deployments.md)。

## 排错

| 错误 | 原因 → 修复 |
|-------|------------|
| **DeployFailed / DeploymentError** | CDK 错误不是根本原因。`cdk deploy $STACK --verbose`，然后 `cdk --unstable=diagnose diagnose $STACK` (CLI ≥ 2.1120.0)；否则 `aws cloudformation describe-events --stack-name $STACK --filters FailedEvents=true` — 第一个 `_FAILED` 事件是原因。[详情](references/troubleshooting-deployment.md) |
| **NoCredentials / ExpiredToken / AssumeRoleFailed** | `aws sts get-caller-identity` + `cdk doctor`。过期 SSO、缺少 `env`、缺少 `sts:AssumeRole`。[详情](references/troubleshooting-credentials.md) |
| **Asset errors** (CannotFindAsset, FailedToBundleAsset, AssetBuildFailed, AssetPublishFailed) | 路径错误、Docker 未运行或 bootstrap 桶权限。使用 `path.join(__dirname, ...)`。[详情](references/troubleshooting-synth.md) |
| **AppRequired** | 在 `cdk.json` 中添加 `"app": "npx tsx bin/my-app.ts"`。[详情](references/troubleshooting-synth.md) |
| **AnnotationErrors** | 修复根本问题；仅作为最后手段使用 `NagSuppressions` 抑制。[详情](references/troubleshooting-synth.md) |
| **ConcurrentReadLock / ConcurrentWriteLock** | `rm -rf cdk.out` 然后重新运行。并行 CI：`--output ./cdk.out.$BUILD_ID`。[详情](references/troubleshooting-synth.md) |
| **BootstrapVersionValidation** | 重新初始化。所有地方匹配 `--qualifier`。[详情](references/troubleshooting-credentials.md) |
| **DependencyCycle** | 将共享资源提取到第三个堆栈或使用 SSM 进行延迟绑定。[详情](references/troubleshooting-synth.md) |
| **UnresolvedAccount** | 在堆栈上显式设置 `env: { account, region }`。提交 `cdk.context.json`。[详情](references/troubleshooting-credentials.md) |
| **NoStacksMatched** | CDK 使用逻辑 ID（第二个构造函数参数），而不是 CFN 名称。使用 `cdk list` 查找 ID。[详情](references/troubleshooting-synth.md) |
| **Cannot find module** (合成时) | 运行 `npx tsc --noEmit`，检查 `cdk.json` 应用路径与 `tsconfig.json` 的 `outDir` 匹配，删除过时的 `.js` 文件。Python：激活虚拟环境。[详情](references/troubleshooting-synth.md) |
| **V1 import paths / 重复 aws-cdk-lib** | V1 `@aws-cdk/*` 导入、错误的 `Construct` 导入、单体仓库中重复的库副本。[详情](references/v1-to-v2-migration.md) |
| **Lambda Cannot find module** (运行时) | 处理器值错误、缺少 AWS SDK v3 迁移、Python 依赖未打包。[详情](references/troubleshooting-deployment.md) |
| **API Gateway 多阶段冲突** | 在 `RestApi` 上设置 `deploy: false`，显式创建 `Deployment` 和 `Stage`。[详情](references/troubleshooting-deployment.md) |
| **在 `--hotswap` 下未部署变更** | 对非可热替换资源的更改会被静默忽略并仅记录 — 命令仍报告成功。查看输出；使用 `--hotswap-fallback` 强制 CloudFormation 部署。[详情](references/fast-deployments.md) |
| **失败的 `--express` 部署 / 无法回滚** | 表达式模式无法使用 Rollback Stack API，标准部署绝不能用于恢复它。向前推进：修复原因，然后 `cdk deploy $STACK --express`。[详情](references/fast-deployments.md) |
| **开发堆栈出现意外漂移** | Hotswap 和 `cdk watch` 会故意产生漂移。直到恢复前，实际资源 — 而不是 CloudFormation 的记录 — 是权威的。使用 `cdk deploy $STACK --revert-drift` 与之协调，该命令使用漂移感知变更集将实际资源与模板对齐（更新现实以匹配期望状态；不会重写 CF 记录以匹配漂移的资源）。[详情](references/fast-deployments.md) |

## 构建模式

优先使用 L2。当 L2 缺少属性时使用 L1 与 Mixins/Facades。逃生通道：`node.defaultChild` → `addPropertyOverride`。参见 [构建模式](references/construct-patterns.md)。

## 其他资源

- 搜索 AWS 文档中的 "CDK 开发者指南"、"CDK API 参考" 和 "CDK Pipelines" 分别

## 安全注意事项

- 使用 OIDC 处理 CI/CD 凭证（无静态密钥）
- 在初始化时使用 `--custom-permissions-boundary`
- 使用 `grant*()` 处理跨资源 IAM
- 在 CI 中使用 `cdk-nag` + `--strict`
- 将有状态资源放在自己的堆栈中并设置 `terminationProtection: true`
- 提交 `cdk.context.json`
