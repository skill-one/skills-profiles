---
name: platform-quick-deploy
description: 将验证后的元数据部署到生产环境的 Salesforce 组织，无需重新运行测试。当用户想要部署到生产环境时触发，例如输入“快速部署”、“推广”、“部署到生产”或刚刚验证后想要将更改上线。需要最近执行的 `sf project deploy validate` 任务 ID（≤10天旧，≤3天为 --use-most-recent）。不要触发沙盒/草稿部署（使用 platform-metadata-deploy）或未验证部署（先使用 platform-deploy-validate）。
---

# 快速部署到生产环境

使用先前的 `sf project deploy validate` 生成的作业 ID 将经过验证的部署提升到生产组织。无需重新运行测试，无需重新验证组件 — 只需进行提升。

## 前置条件（严格校验）

在执行任何操作之前，请验证以下四点：

1. **目标为生产环境**
   ```bash
   sf org display --target-org <alias> --json
   ```
   确认目标确实是生产环境。可靠的检查是门的分类器（返回 `production|sandbox|scratch|trial|devhub|unknown`）：
   ```bash
   sf org display --target-org <alias> --json | "${CLAUDE_PLUGIN_ROOT}/scripts/sf-deploy-gate" classify
   ```
   生产环境意味着 `isSandbox=false` AND `isScratch=false` AND 实例 URL 中没有 `--`（沙盒标记）AND 没有 `test.salesforce.com` **AND 它不是试用/开发者版主机**（`orgfarm-*`、`*.develop.my.salesforce.com`、`*.pc-rnd.*` 或响应中包含 `trialExpirationDate` — 这些报告 `isSandbox`/`isScratch` 为 `null` 且不能被视为生产环境）。

   如果目标不是生产环境（分类器返回任何不是 `production` 的情况）→ 停止并重定向到 `platform-metadata-deploy`（该命令原生处理非生产环境）。

2. **存在验证记录**
   - 如果存在，则读取 `.sfdx/last-validation.json`（由 `platform-deploy-validate` 留下）
   - 或者要求用户提供作业 ID
   - 或者回退到 `--use-most-recent`（在最近 3 天内验证）

3. **验证记录足够新鲜**
   - 明确的 `--job-id`：必须 ≤10 天旧（根据 Salesforce 的快速部署窗口）
   - `--use-most-recent`：必须 ≤3 天旧
   - 如果记录的 `createdAt` 超过窗口 → 停止并首先运行 `platform-deploy-validate`

4. **明确用户确认**
   - 打印确认块（别名、实例 URL、版本、验证组件数量、测试结果），并询问："确认部署到生产环境？(yes/no)"
   - 未提供明确的 "yes" 时不继续

## 工作流

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
└─────────────────────────────────────────────────┘
确认部署到生产环境？(yes/no)
```

### 第 2 步 — 运行快速部署

在输入 "yes" 后：

```bash
sf project deploy quick --job-id <id> --target-org <alias> --wait 30 --json
```

或者如果用户选择使用 `--use-most-recent`。

快速部署将：
- 将验证的组件提升到组织
- 不重新运行测试（根据 Salesforce 平台行为）
- 返回最终部署状态

### 第 3 步 — 捕获部署报告

完成部署后，持久化以供审计：

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
- 检查设置 → 部署状态以确认
- 如果出现任何回归：准备回滚计划（重新部署先前版本的包）

## 规则

- 永远不要对生产目标运行 `sf project deploy start`（始终先验证，然后快速部署）
- 永远不要在生产环境中使用 `--ignore-errors` 或 `--ignore-warnings`
- 永远不要自动确认 — 要求用户提供明确的 "yes"
- 永远不要快速部署过期的作业 ID — 重新验证
- 永远将部署报告持久化到 `.sfdx/deploy-history/` 以供审计记录
- 如果生产检查钩子拒绝操作，不要绕过它 — 向用户展示拒绝信息，并建议首先运行 `platform-deploy-validate`
