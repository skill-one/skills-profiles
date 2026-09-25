# CI/CD与自动化

## 概述

自动化质量门禁，确保没有变更未经测试、代码风格检查、类型检查和构建就到达生产环境。CI/CD是其他所有技能的执行机制——它捕获人类和代理遗漏的问题，并且对每一个变更都保持一致的处理。

**左移（Shift Left）：** 尽可能在管道的早期阶段发现问题。在代码风格检查中发现的bug只需几分钟修复；而同样的bug在生产环境中发现则可能耗费数小时。将检查上移——静态分析在测试之前，测试在预发布环境之前，预发布环境在生产环境之前。

**越快越安全（Faster is Safer）：** 较小的批次和更频繁的发布会降低风险，而不是增加风险。包含3个变更的部署比包含30个变更的部署更容易调试。频繁发布会增强对发布流程本身的信心。

## 使用场景

- 设置新项目的CI管道
- 添加或修改自动化检查
- 配置部署管道
- 当变更需要触发自动化验证时
- 调试CI失败

## 质量门禁管道

每个变更在合并前都需要通过以下门禁：

```
打开Pull Request
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
│   集成测试         │  API/DB测试
│   ↓ 通过         │
│   E2E（可选）     │  Playwright/Cypress
│   ↓ 通过         │
│   安全审计         │  npm audit
│   ↓ 通过         │
│   打包大小         │  bundlesize检查
└─────────────────┘
    │
    ▼
  准备审核
```

**不能跳过任何门禁。** 如果代码风格检查失败，修复代码风格——不要禁用规则。如果测试失败，修复代码——不要跳过测试。

## GitHub Actions配置

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

### 包含数据库集成测试

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

> **注意：** 即使对于CI专用的测试数据库，也使用GitHub Secrets来存储凭证，而不是硬编码值。这能培养良好的习惯，并防止在上下文中意外重用测试凭证。

### E2E测试

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
      - name: 安装Playwright
        run: npx playwright install --with-deps chromium
      - name: 构建
        run: npm run build
      - name: 运行E2E测试
        run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## 将CI失败反馈给代理

CI与AI代理结合的强大之处在于反馈循环。当CI失败时：

```
CI失败
    │
    ▼
复制失败输出
    │
    ▼
将其反馈给代理：
"CI管道失败，错误信息如下：
[paste specific error]
在推送之前本地修复问题。"
    │
    ▼
代理修复→推送→CI再次运行
```

**关键模式：**

```
代码风格检查失败 → 代理运行 `npm run lint --fix` 并提交
类型错误  → 代理读取错误位置并修复类型
测试失败 → 代理遵循调试和错误恢复技能
构建错误 → 代理检查配置和依赖
```

## 部署策略

### 预览部署

每个PR都会获得预览部署进行手动测试：

```yaml
# 在PR上部署预览（Vercel/Netlify等）
deploy-preview:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - name: 部署预览
      run: npx vercel --token=${{ secrets.VERCEL_TOKEN }}
```

### 功能标志

功能标志将部署与发布解耦。将不完整或风险较高的功能隐藏在标志后面，以便您可以：

- **在不启用功能的情况下发布代码。** 早期合并到main，准备好时再启用。
- **无需重新部署即可回滚。** 禁用标志而不是回滚代码。
- **灰度发布新功能。** 对1%的用户启用，然后是10%，然后是100%。
- **运行A/B测试。** 比较有和没有功能的行为。

```typescript
// 简单的功能标志模式
if (featureFlags.isEnabled('new-checkout-flow', { userId })) {
  return renderNewCheckout();
}
return renderLegacyCheckout();
```

**标志生命周期：** 创建→用于测试→灰度发布→全面推广→移除标志和死代码。永远存在的标志会变成技术债务——在创建时设定清理日期。

### 分阶段发布

```
PR合并到main
    │
    ▼
  预发布环境部署（自动）
    │ 手动验证
    ▼
  生产环境部署（手动触发或预发布后自动）
    │
    ▼
  监控错误（15分钟窗口）
    │
    ├── 检测到错误→回滚
    └── 清洁→完成
```

### 回滚计划

每个部署应该是可逆的：

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
      - name: 回滚部署
        run: |
          # 部署指定的先前版本
          npx vercel rollback ${{ inputs.version }}
```

## 环境管理

```
.env.example       → 提交（开发者的模板）
.env                → 不提交（本地开发）
.env.test           → 提交（测试环境，没有真实凭证）
CI凭证             → 存储在GitHub Secrets / vault
生产凭证            → 存储在部署平台 / vault
```

CI不应该包含生产凭证。为CI测试使用单独的凭证。

## CI之外的自动化

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

指定一个人负责保持CI绿色。当构建失败时，构建警卫的工作是修复或回滚——而不是引发问题的那个人。这可以防止构建损坏而无人修复。

### PR检查

- **必需的审核：** 合并前至少需要1个批准
- **必需的状态检查：** 合并前必须通过CI
- **分支保护：** 不允许强制推送main
- **自动合并：** 如果所有检查通过且已批准，则自动合并

## CI优化

当管道超过10分钟时，按以下顺序应用这些策略：

```
慢速CI管道？
├── 缓存依赖
│   └── 使用actions/cache或setup-node缓存选项为node_modules
├── 并行运行作业
│   └── 将代码风格检查、类型检查、测试、构建分成单独的并行作业
├── 只运行已更改的
│   └── 使用路径过滤器跳过无关的作业（例如，仅文档PR跳过E2E）
├── 使用矩阵构建
│   └── 将测试套件分散到多个运行器
├── 优化测试套件
│   └── 从关键路径中移除慢速测试，改为按计划运行
└── 使用更大的运行器
    └── GitHub托管的更大运行器或自托管用于CPU密集型构建
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

| 借口       | 现实       |
|---|---|
| "CI太慢"   | 优化管道（见下文CI优化），不要跳过它。5分钟的管道可以防止数小时的调试。 |
| "这个变更很 trivial，跳过CI" | trivial变更会破坏构建。CI对trivial变更也很快。 |
| "测试不稳定，只是重跑"   | 不稳定的测试会掩盖真实bug并浪费大家的时间。修复不稳定性。 |
| "我们稍后会添加CI"   | 没有CI的项目会积累损坏状态。第一天就设置它。 |
| "手动测试就足够了"   | 手动测试无法扩展且不可重复。自动化你能做到的。 |

## 警报

- 项目中没有CI管道
- 忽略或抑制CI失败
- 在CI中禁用测试以使管道通过
- 没有预发布验证的生产部署
- 没有回滚机制
- 凭证存储在代码或CI配置文件中（不是凭证管理器）
- 长CI时间且没有优化努力

## 验证

设置或修改CI后：

- [ ] 所有质量门禁都存在（代码风格检查、类型检查、测试、构建、审计）
- [ ] 管道在PR和main推送时都运行
- [ ] 失败会阻止合并（分支保护已配置）
- [ ] CI结果会反馈到开发循环
- [ ] 凭证存储在凭证管理器中，而不是代码中
- [ ] 部署有回滚机制
- [ ] 测试套件在10分钟内完成
