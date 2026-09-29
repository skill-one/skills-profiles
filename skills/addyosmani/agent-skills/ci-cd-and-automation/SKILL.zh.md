---
name: ci-cd-and-automation
description: 自动化 CI/CD 管道设置。在设置或修改构建和部署管道时使用。在需要自动化质量门禁、在 CI 中配置测试运行器或建立部署策略时使用。
---

# CI/CD 和自动化

## 概述

自动化质量门禁，确保没有变更未经测试、代码风格检查、类型检查和构建就到达生产环境。CI/CD 是其他所有技能的执行机制——它捕获人类和代理遗漏的问题，并且对每一个变更都始终如一地执行。

**左移 (Shift Left)：** 尽可能在管道的早期阶段捕获问题。在代码风格检查中发现的错误只需几分钟；同样的错误在生产环境中发现则可能耗费数小时。将检查移至上游——静态分析在测试之前，测试在预发布环境之前，预发布环境在生产环境之前。

**越快越安全 (Faster is Safer)：** 较小的批次和更频繁的发布会降低风险，而不是增加风险。包含 3 个变更的部署比包含 30 个变更的部署更容易调试。频繁发布本身就能建立对发布流程的信心。

## 何时使用

- 设置新项目的 CI 管道
- 添加或修改自动化检查
- 配置发布管道
- 当变更应触发自动化验证时
- 调试 CI 失败

## 质量门禁管道

每个变更在合并前都需通过这些门禁：

```
打开 Pull Request
    │
    ▼
┌─────────────────┐
│   代码风格检查     │  eslint, prettier
│   ↓ 通过         │
│   类型检查         │  tsc --noEmit
│   ↓ 通过         │
│   单元测试         │  jest/vitest
│   ↓ 通过         │
│   构建             │  npm run build
│   ↓ 通过         │
│   集成测试         │  API/DB 测试
│   ↓ 通过         │
│   端到端测试 (可选) │  Playwright/Cypress
│   ↓ 通过         │
│   安全审计         │  npm audit
│   ↓ 通过         │
│   打包大小         │  bundlesize 检查
└─────────────────┘
    │
    ▼
  准备审核
```

**不能跳过任何门禁。** 如果代码风格检查失败，修复代码风格——不要禁用规则。如果测试失败，修复代码——不要跳过测试。

## GitHub Actions 配置

### 基本CI管道

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'

      - name: 安装依赖
        run: npm ci

      - name: 代码风格检查
        run: npm run lint

      - name: 类型检查
        run: npx tsc --noEmit

      - name: 测试
        run: npm test -- --coverage

      - name: 构建
        run: npm run build

      - name: 安全审计
        run: npm audit --audit-level=high
```

### 带数据库集成测试

```yaml
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: ci_user
          POSTGRES_PASSWORD: ${{ secrets.CI_DB_PASSWORD }}
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - name: 运行迁移
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
      - name: 集成测试
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://ci_user:${{ secrets.CI_DB_PASSWORD }}@localhost:5432/testdb
```

> **注意：** 即使对于 CI 专用的测试数据库，也使用 GitHub Secrets 存储凭证，而不是硬编码值。这能培养良好的习惯，并防止在上下文中意外重用测试凭证。

### 端到端测试

```yaml
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - name: 安装 Playwright
        run: npx playwright install --with-deps chromium
      - name: 构建
        run: npm run build
      - name: 运行端到端测试
        run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## 将 CI 失败反馈给代理

CI 与 AI 代理结合的强大之处在于反馈循环。当 CI 失败时：

```
CI 失败
    │
    ▼
复制失败输出
    │
    ▼
将其反馈给代理：
"CI 管道失败，错误信息如下：
[paste specific error]
修复问题并在本地验证后再重新推送。"
    │
    ▼
代理修复 → 推送 → CI 再次运行
```

**关键模式：**

```
代码风格检查失败 → 代理运行 `npm run lint --fix` 并提交
类型错误  → 代理读取错误位置并修复类型
测试失败 → 代理遵循调试和错误恢复技能
构建错误 → 代理检查配置和依赖
```

## 发布策略

### 预览发布

每个 PR 都会获得预览发布以进行手动测试：

```yaml
# 在 PR 上预览发布 (Vercel/Netlify/etc.)
deploy-preview:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - name: 预览发布
      run: npx vercel --token=${{ secrets.VERCEL_TOKEN }}
```

### 功能标志

功能标志将发布与发布解耦。将不完整或风险较高的功能隐藏在标志后面，以便您可以：

- **推送代码而不启用它。** 早期合并到 main，准备好时再启用。
- **无需重新发布即可回滚。** 禁用标志而不是回滚代码。
- **金丝雀发布新功能。** 对 1% 的用户启用，然后 10%，然后 100%。
- **运行 A/B 测试。** 比较启用功能和未启用功能的行为。

```typescript
// 简单的功能标志模式
if (featureFlags.isEnabled('new-checkout-flow', { userId })) {
  return renderNewCheckout();
}
return renderLegacyCheckout();
```

**标志生命周期：** 创建 → 用于测试启用 → 金丝雀发布 → 全部发布 → 删除标志和死代码。永远存在的标志会变成技术债务——在创建时设置清理日期。

### 分阶段发布

```
PR 合并到 main
    │
    ▼
  预发布环境自动发布
    │ 手动验证
    ▼
  生产环境发布 (手动触发或预发布后自动触发)
    │
    ▼
  监控错误 (15 分钟窗口)
    │
    ├── 检测到错误 → 回滚
    └── 清洁 → 完成
```

### 回滚计划

每个发布应该是可逆的：

```yaml
# 手动回滚工作流
name: Rollback
on:
  workflow_dispatch:
    inputs:
      version:
        description: '回滚到的版本'
        required: true

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: 回滚发布
        run: |
          # 部署指定的先前版本
          npx vercel rollback ${{ inputs.version }}
```

## 环境管理

```
.env.example       → 提交 (开发人员模板)
.env                → 不提交 (本地开发)
.env.test           → 提交 (测试环境，无真实密钥)
CI 密钥             → 存储在 GitHub Secrets / vault
生产环境密钥        → 存储在发布平台 / vault
```

CI 不应包含生产环境密钥。为 CI 测试使用单独的密钥。

## 超越 CI 的自动化

### Dependabot / Renovate

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
```

### 构建警卫角色

指定一个人负责保持 CI 绿色。当构建失败时，构建警卫的工作是修复或回滚——而不是引发问题的那个人。这可以防止构建损坏而无人修复。

### PR 检查

- **必需的审核：** 合并前至少需要 1 个批准
- **必需的状态检查：** 合并前必须通过 CI
- **分支保护：** 不允许强制推送到 main
- **自动合并：** 如果所有检查通过且已批准，则自动合并

## CI 优化

当管道超过 10 分钟时，按以下策略的顺序应用：

```
慢速 CI 管道？
├── 缓存依赖
│   └── 使用 actions/cache 或 setup-node 缓存选项缓存 node_modules
├── 并行运行作业
│   └── 将代码风格检查、类型检查、测试、构建拆分为单独的并行作业
├── 只运行已更改的
│   └── 使用路径过滤器跳过不相关的作业 (例如，仅文档 PR 跳过端到端测试)
├── 使用矩阵构建
│   └── 将测试套件分散到多个运行器
├── 优化测试套件
│   └── 从关键路径中移除慢速测试，改为按计划运行
└── 使用更大的运行器
    └── GitHub 托管的更大运行器或自托管用于 CPU 密集型构建
```

**示例：缓存和并行化**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage
```

## 常见借口

| 借口 | 现实 |
|---|---|
| "CI 太慢" | 优化管道 (见下文 CI 优化)，不要跳过它。5 分钟的管道可以防止数小时的调试。 |
| "这个变更很小，跳过 CI" | 小变更也会导致构建失败。CI 对小变更也很快。 |
| "测试不稳定，只是重跑" | 不稳定的测试会掩盖真实错误并浪费大家的时间。修复不稳定性。 |
| "我们稍后添加 CI" | 没有 CI 的项目会积累损坏状态。第一天就设置它。 |
| "手动测试足够了" | 手动测试无法扩展且不可重复。自动化你能自动化的部分。 |

## 警报

- 项目中没有 CI 管道
- 忽略或静音 CI 失败
- 在 CI 中禁用测试以使管道通过
- 没有预发布环境验证的生产环境发布
- 没有回滚机制
- 密钥存储在代码或 CI 配置文件中 (不在密钥管理器中)
- CI 时间过长且没有优化努力

## 验证

设置或修改 CI 后：

- [ ] 所有质量门禁都存在 (代码风格检查、类型检查、测试、构建、审计)
- [ ] 管道在每次 PR 和 main 推送时都运行
- [ ] 失败会阻止合并 (分支保护配置)
- [ ] CI 结果会反馈到开发循环
- [ ] 密钥存储在密钥管理器中，不在代码中
- [ ] 发布有回滚机制
- [ ] 管道对测试套件运行时间少于 10 分钟
