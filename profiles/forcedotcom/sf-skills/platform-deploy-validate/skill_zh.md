# 部署验证

在部署元数据之前，请执行服务器端验证。验证过程会暴露错误，而不会修改组织，并且对于生产目标——会生成一个可用于 `platform-quick-deploy` 的作业 ID，以便快速、无测试的部署。

## 能力解析

始终优先选择 `sf project deploy validate`（生产环境）或 `sf project deploy start --dry-run`（沙盒/草稿环境），而不是直接使用 Tooling API。

## 工作流

### 第 1 步 — 确认目标组织

使用门的分类器对组织进行分类——它是权威的真相来源（它处理沙盒/草稿标记、试用版和开发者版主机以及开发中心，并返回 `production|sandbox|scratch|trial|devhub|unknown` 之一）：

```bash
sf org display --target-org <别名> --json | "${CLAUDE_PLUGIN_ROOT}/scripts/sf-deploy-gate" classify
```

只有 `production` 会采用生产路径（第 2b 步）；其他所有结果都会采用沙盒/草稿路径（第 2a 步）。

### 第 2a 步 — 沙盒/草稿路径（干运行）

```bash
sf project deploy start --dry-run --target-org <别名> --json [作用域标志]
```

作用域标志（使用其中一个，而不是全部）：
- `--source-dir <路径>` — 部署目录
- `--metadata <类型:名称>` — 部署特定组件
- `--manifest manifest/package.xml` — 从清单部署

默认测试级别：对于沙盒，省略 `--test-level`（委托给组织默认值）。仅在用户要求时添加 `--test-level RunLocalTests`。

反馈：成功/失败、尝试的组件、任何错误。**干运行不会返回作业 ID**（这是预期的）。

### 第 2b 步 — 生产路径（验证）

```bash
sf project deploy validate --target-org <别名> --json [作用域标志] --test-level RunLocalTests
```

生产验证需要测试级别。默认使用 `RunLocalTests`；如果用户明确列出了测试，则切换到 `RunSpecifiedTests --tests <ClassName>...`。

响应会返回一个**有效的作业 ID**（`result.id`），有效期**10 天**。将其持久化以供 `platform-quick-deploy` 使用：

```bash
mkdir -p .sfdx
echo '{"jobId":"<id>","createdAt":"<iso8601>","targetOrg":"<别名>","testLevel":"RunLocalTests"}' > .sfdx/last-validation.json
```

报告：
- 验证结果（通过/失败）
- 作业 ID 和 10 天过期日期
- 测试结果摘要（运行/通过/失败）
- 推荐的下一步操作：使用此作业 ID 的 `platform-quick-deploy`

### 第 3 步 — 失败分类处理

如果验证失败，请解析 `result.details.componentFailures` 和 `result.details.runTestResult.failures` 并暴露：
- 前 5 个组件错误（带完整消息）
- 前 5 个测试失败（带堆栈）
- 建议的修复方案（组件名称 → 可能的原因：缺少依赖项、FLS、语法等）

**不要建议更改与验证报告无关的元数据的修复方案**。始终局限于验证报告的范围。

## 规则

- 在每个 CLI 调用中**始终**使用 `--json`
- 针对 Production 目标**永远**不要跳过验证（不要从本技能直接运行 `sf project deploy start` 对生产环境）
- 验证期间**永远**不要使用 `--ignore-errors` 或 `--ignore-warnings`；这些标志属于实际部署，而不是验证
- 如果用户要求“部署到 prod”而没有先进行验证，请**首先**运行验证，然后将其转交给 `platform-quick-deploy`（不要对生产环境启动常规部署）
- 将验证作业 ID 持久化到 `.sfdx/last-validation.json`，以便快速部署技能可以找到它

## 输出

始终以以下内容结束：
- ✅ 验证通过 → 指向 `platform-quick-deploy`（带作业 ID + 过期日期）的下一步操作指针，或对于非生产环境指向 `platform-metadata-deploy`
- ❌ 验证失败 → 分类错误列表和建议的下一步迭代
