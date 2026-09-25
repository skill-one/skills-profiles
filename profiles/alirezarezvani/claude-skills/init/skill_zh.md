# 初始化 Playwright 项目

设置一个生产就绪的 Playwright 测试环境。检测框架、生成配置、文件夹结构、示例测试和 CI 工作流。

## 步骤

### 1. 分析项目

使用 `Explore` 子代理扫描项目：

- 检查 `package.json` 以确定框架（React、Next.js、Vue、Angular、Svelte）
- 检查是否存在 `tsconfig.json` → 使用 TypeScript；否则使用 JavaScript
- 检查 Playwright 是否已安装（依赖项中的 `@playwright/test`）
- 检查现有测试目录（`tests/`、`e2e/`、`__tests__/`）
- 检查现有 CI 配置（`.github/workflows/`、`.gitlab-ci.yml`）

### 2. 安装 Playwright

如果尚未安装：

```bash
npm init playwright@latest -- --quiet
```

或者如果用户更喜欢手动设置：

```bash
npm install -D @playwright/test
npx playwright install --with-deps chromium
```

### 3. 生成 `playwright.config.ts`

根据检测到的框架进行适配：

**Next.js:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: "chromium", use: { ...devices['Desktop Chrome'] } },
    { name: "firefox", use: { ...devices['Desktop Firefox'] } },
    { name: "webkit", use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**React (Vite):**
- 将 `baseURL` 改为 `http://localhost:5173`
- 将 `webServer.command` 改为 `npm run dev`

**Vue/Nuxt:**
- 将 `baseURL` 改为 `http://localhost:3000`
- 将 `webServer.command` 改为 `npm run dev`

**Angular:**
- 将 `baseURL` 改为 `http://localhost:4200`
- 将 `webServer.command` 改为 `npm run start`

**未检测到框架:**
- 省略 `webServer` 块
- 从用户输入设置 `baseURL` 或将其留为占位符

### 4. 创建文件夹结构

```
e2e/
├── fixtures/
│   └── index.ts          # 自定义 fixtures
├── pages/
│   └── .gitkeep          # 页面对象模型
├── test-data/
│   └── .gitkeep          # 测试数据文件
└── example.spec.ts       # 首个示例测试
```

### 5. 生成示例测试

```typescript
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
  });

  test('should have visible navigation', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('navigation')).toBeVisible();
  });
});
```

### 6. 生成 CI 工作流

如果存在 `.github/workflows/`，创建 `playwright.yml`：

```yaml
name: "playwright-tests"

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
      - name: "install-dependencies"
        run: npm ci
      - name: "install-playwright-browsers"
        run: npx playwright install --with-deps
      - name: "run-playwright-tests"
        run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: "playwright-report"
          path: playwright-report/
          retention-days: 30
```

如果存在 `.gitlab-ci.yml`，则添加 Playwright 阶段。

### 7. 更新 `.gitignore`

如果尚未存在，追加：

```
/test-results/
/playwright-report/
/blob-report/
/playwright/.cache/
```

### 8. 添加 npm 脚本

添加到 `package.json` 脚本：

```json
{
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui",
  "test:e2e:debug": "playwright test --debug"
}
```

### 9. 验证设置

运行示例测试：

```bash
npx playwright test
```

报告结果。如果失败，诊断并修复后再完成。

## 输出

确认已创建的内容：
- 配置文件路径和关键设置
- 测试目录和示例测试
- CI 工作流（如果适用）
- 添加的 npm 脚本
- 如何运行：`npx playwright test` 或 `npm run test:e2e`
