# 快速部署到生产环境

使用先前 `sf project deploy validate` 命令返回的作业 ID 将验证后的部署提升到生产组织。无需重新运行测试，无需重新验证组件 — 仅执行提升操作。

## 前置条件（严格校验）

在执行任何操作之前，请验证以下四项：

1. **目标为生产环境**
   ```bash
   sf org display --target-org <alias> --json
   ```
   确认目标确实是生产环境。可靠的检查是门的分类器（返回 `production|sandbox|scratch|trial|devhub|unknown`）：
   ```bash
   sf org display --target-org <alias> --json | "${CLAUDE_PLUGIN_ROOT}/scripts/sf-deploy-gate" classify
   ```
   生产环境意味着 `isSandbox=false` AND `isScratch=false` AND 实例 URL 中没有 `--`（沙盒标记）AND 没有 `test.salesforce.com` **AND 它不是试用/开发者版主机**（`orgfarm-*`、`*.develop.my.salesforce.com`、`*.pc-rnd.*` 或响应中包含 `trialExpirationDate` — 这些报告 `isSandbox`/`isScratch` 为 `null` 且不能被视为生产环境）。

   如果目标不是生产环境（分类器返回任何不是 `production` 的值）→ 停止并重定向到 `platform-metadata-deploy`（该命令原生处理非生产环境）。

2. **存在验证记录**
   - 如果存在，则读取 `.sfdx/last-validation.json`（由 `platform-deploy-validate` 留下）
   - 或要求用户提供作业 ID
   - 或回退到 `--use-most-recent`（最近 3 天内的验证）

3. **验证记录足够新鲜**
   - 明确的 `--job-id`：必须 ≤10 天旧（根据 Salesforce 快速部署窗口）
   - `--use-most-recent`：必须 ≤3 天旧
   - 如果记录的 `createdAt` 超过窗口 → 停止并首先运行 `platform-deploy-validate`

4. **明确用户确认**
   - 打印确认块（别名、实例 URL、版本、验证组件数量、测试结果）并询问："确认部署到生产环境？(yes/no)"
   - 未提供明确 "yes" 时不继续

## 工作流程

### 第 1 步 — 显示生产确认横幅

格式必须完全一致：

```
┌─ 生产部署 ─────────────────────────────┐
│ 组织别名:      <alias>                         │
│ 实例:       <instanceUrl>                   │
│ 版本:        <edition>                       │
│ 验证 ID:  <jobId>                         │
│ 验证时间:      <createdAt> (X 天前)        │
│ 组件:     <componentCount> 已排队         │
│ 测试:          <run>/<passed>/<failed>         │
└─────────────────────────────────────────┘
确认部署到生产环境？(yes/no)
```

### 第 2 步 — 运行快速部署

输入 "yes" 后：

```bash
sf project deploy quick --job-id <id> --target-org <alias> --wait 30 --json
```

或如果用户选择使用 `--use-most-recent`。

快速部署将：
- 将验证的组件提升到组织
- 不重新运行测试（根据 Salesforce 平台行为）
- 返回最终部署状态

### 第 3 步 — 捕获部署报告

完成部署后，用于审计：

```bash
mkdir -p .sfdx/deploy-history
sf project deploy report --job-id <id> --target-org <alias> --json > ".sfdx/deploy-history/<id>.json"
```

向用户展示：
- ✅ 部署成功 — 组件已部署，耗时
- ⚠️ 部署失败 — 错误摘要；建议查看报告

### 第 4 步 — 部署后指导

成功部署生产环境后，建议：
- 在组织中测试关键路径（如果知道，提供直接 URL）
- 监控生产环境 30 分钟
- 检查设置 → 部署状态确认
- 如果出现任何回归：准备回滚计划（重新部署先前版本的包）

## 规则

- 永远不要对生产目标运行 `sf project deploy start`（始终先验证再快速部署）
- 永远不要在生产环境中使用 `--ignore-errors` 或 `--ignore-warnings`
- 永远不要自动确认 — 要求用户提供明确的 "yes"
- 永远不要快速部署超过其有效窗口的作业 ID — 重新验证
- 永远将部署报告保存在 `.sfdx/deploy-history/` 以便审计
- 如果生产检查钩子拒绝操作，不要绕过它 — 向用户展示拒绝并建议首先运行 `platform-deploy-validate`
