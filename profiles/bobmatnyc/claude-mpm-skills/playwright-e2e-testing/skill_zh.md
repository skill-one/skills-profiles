# Playwright E2E 测试技能

---
渐进式披露:
  入口点:
    概述: "现代 E2E 测试框架，支持跨浏览器自动化和内置测试运行器"
    使用场景:
      - "测试 Web 应用端到端"
      - "需要跨浏览器测试时"
      - "测试用户流程和交互时"
      - "需要截图/视频录制时"
    快速入门:
      - "npm init playwright@latest"
      - "选择 TypeScript 和测试位置"
      - "npx playwright test"
      - "npx playwright show-report"
  令牌估算:
    入口: 75-90
    完整: 4200-5200
---

<!-- 入口点 - 默认加载此部分 (75-90 令牌) -->

## 概述

Playwright 是一个现代的端到端测试框架，提供跨浏览器自动化和内置测试运行器、自动等待机制以及出色的开发者体验。

### 关键特性
- **自动等待**: 自动等待元素就绪
- **跨浏览器**: 支持 Chromium、Firefox、WebKit
- **内置运行器**: 并行执行、重试、报告器
- **网络控制**: 模拟和拦截网络请求
- **调试**: UI 模式、跟踪查看器、检查器

---

<!-- 完整内容 - 按需加载 (4200-5200 令牌) -->

## 安装

```bash
# 初始化新的 Playwright 项目
npm init playwright@latest

# 或添加到现有项目
npm install -D @playwright/test

# 安装浏览器
npx playwright install
```

### 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 基础知识

### 基本测试结构

```typescript
import { test, expect } from '@playwright/test';

test('基本测试', async ({ page }) => {
  await page.goto('https://example.com');

  // 等待元素并检查可见性
  const title = page.locator('h1');
  await expect(title).toBeVisible();
  await expect(title).toHaveText('Example Domain');

  // 获取页面标题
  await expect(page).toHaveTitle(/Example/);
});

test.describe('用户认证', () => {
  test('应成功登录', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message')).toContainText('Welcome');
  });

  test('应显示无效凭证的错误', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="username"]', 'invalid');
    await page.fill('[name="password"]', 'wrong');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toHaveText('Invalid credentials');
  });
});
```

### 测试钩子

```typescript
import { test, expect } from '@playwright/test';

test.describe('仪表盘测试', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前运行
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async ({ page }) => {
    // 每个测试后清理
    await page.close();
  });

  test.beforeAll(async ({ browser }) => {
    // 描述块中所有测试前运行一次
    console.log('开始测试套件');
  });

  test.afterAll(async ({ browser }) => {
    // 所有测试后运行一次
    console.log('测试套件完成');
  });

  test('显示用户数据', async ({ page }) => {
    await expect(page.locator('.user-name')).toBeVisible();
  });
});
```

## 定位器策略

### 最佳实践：基于角色的定位器

```typescript
import { test, expect } from '@playwright/test';

test('可访问定位器', async ({ page }) => {
  await page.goto('/form');

  // 通过角色 (最佳 - 可访问且稳定)
  await page.getByRole('button', { name: 'Submit' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('checkbox', { name: 'Subscribe' }).check();
  await page.getByRole('link', { name: 'Learn more' }).click();

  // 通过标签 (表单的最佳选择)
  await page.getByLabel('Password').fill('secret123');

  // 通过占位符
  await page.getByPlaceholder('Search...').fill('query');

  // 通过文本
  await page.getByText('Welcome back').click();
  await page.getByText(/hello/i).isVisible();

  // 通过测试 ID (动态内容的好选择)
  await page.getByTestId('user-profile').click();

  // 通过标题
  await page.getByTitle('Close dialog').click();

  // 通过替代文本 (图片)
  await page.getByAltText('User avatar').click();
});
```

### CSS 和 XPath 定位器

```typescript
test('CSS 和 XPath 定位器', async ({ page }) => {
  // CSS 选择器
  await page.locator('button.primary').click();
  await page.locator('#user-menu').click();
  await page.locator('[data-testid="submit-btn"]').click();
  await page.locator('div.card:first-child').click();

  // XPath (谨慎使用)
  await page.locator('xpath=//button[contains(text(), "Submit")]').click();

  // 链式定位器
  const form = page.locator('form#login-form');
  await form.locator('input[name="email"]').fill('user@example.com');
  await form.locator('button[type="submit"]').click();

  // 过滤定位器
  await page.getByRole('listitem')
    .filter({ hasText: 'Product 1' })
    .getByRole('button', { name: 'Add to cart' })
    .click();
});
```

## 页面对象模型

### 页面类模式

```typescript
// pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Log in' });
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectErrorMessage(message: string) {
    await this.errorMessage.waitFor({ state: 'visible' });
    await expect(this.errorMessage).toHaveText(message);
  }
}

// pages/DashboardPage.ts
export class DashboardPage {
  readonly page: Page;
  readonly welcomeMessage: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.welcomeMessage = page.locator('.welcome-message');
    this.logoutButton = page.getByRole('button', { name: 'Logout' });
  }

  async waitForLoad() {
    await this.welcomeMessage.waitFor({ state: 'visible' });
  }

  async logout() {
    await this.logoutButton.click();
  }
}

// tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

test('成功登录流程', async ({ page }) => {
  const loginPage = new LoginPage(page);
  const dashboard = new DashboardPage(page);

  await loginPage.goto();
  await loginPage.login('testuser', 'password123');

  await dashboard.waitForLoad();
  await expect(dashboard.welcomeMessage).toContainText('Welcome');
});
```

### 组件模式

```typescript
// components/NavigationComponent.ts
import { Page, Locator } from '@playwright/test';

export class NavigationComponent {
  readonly page: Page;
  readonly homeLink: Locator;
  readonly profileLink: Locator;
  readonly searchInput: Locator;

  constructor(page: Page) {
    this.page = page;
    const nav = page.locator('nav');
    this.homeLink = nav.getByRole('link', { name: 'Home' });
    this.profileLink = nav.getByRole('link', { name: 'Profile' });
    this.searchInput = nav.getByPlaceholder('Search...');
  }

  async navigateToProfile() {
    await this.profileLink.click();
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }
}
```

## 用户交互

### 表单交互

```typescript
test('表单交互', async ({ page }) => {
  await page.goto('/form');

  // 文本输入
  await page.fill('input[name="email"]', 'user@example.com');
  await page.type('textarea[name="message"]', 'Hello', { delay: 100 });

  // 复选框
  await page.check('input[type="checkbox"][name="subscribe"]');
  await page.uncheck('input[type="checkbox"][name="spam"]');

  // 单选按钮
  await page.check('input[type="radio"][value="option1"]');

  // 选择下拉菜单
  await page.selectOption('select[name="country"]', 'US');
  await page.selectOption('select[name="color"]', { label: 'Blue' });
  await page.selectOption('select[name="size"]', { value: 'large' });

  // 多选
  await page.selectOption('select[multiple]', ['value1', 'value2']);

  // 文件上传
  await page.setInputFiles('input[type="file"]', 'path/to/file.pdf');
  await page.setInputFiles('input[type="file"]', [
    'file1.jpg',
    'file2.jpg'
  ]);

  // 清空文件输入
  await page.setInputFiles('input[type="file"]', []);
});
```

### 鼠标和键盘

```typescript
test('鼠标和键盘交互', async ({ page }) => {
  // 点击变体
  await page.click('button');
  await page.dblclick('button'); // 双击
  await page.click('button', { button: 'right' }); // 右键点击
  await page.click('button', { modifiers: ['Shift'] }); // Shift+点击

  // 悬停
  await page.hover('.tooltip-trigger');
  await expect(page.locator('.tooltip')).toBeVisible();

  // 拖放
  await page.dragAndDrop('#draggable', '#droppable');

  // 键盘
  await page.keyboard.press('Enter');
  await page.keyboard.press('Control+A');
  await page.keyboard.type('Hello World');
  await page.keyboard.down('Shift');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.up('Shift');

  // 聚焦
  await page.focus('input[name="email"]');
  await page.fill('input[name="email"]', 'test@example.com');
});
```

### 等待策略

```typescript
test('等待策略', async ({ page }) => {
  // 等待元素
  await page.waitForSelector('.dynamic-content');
  await page.waitForSelector('.modal', { state: 'visible' });
  await page.waitForSelector('.loading', { state: 'hidden' });

  // 等待加载状态
  await page.waitForLoadState('load');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');

  // 等待 URL
  await page.waitForURL('**/dashboard');
  await page.waitForURL(/\/product\/\d+/);

  // 等待函数
  await page.waitForFunction(() => {
    return document.querySelectorAll('.item').length > 5;
  });

  // 等待超时 (尽量避免)
  await page.waitForTimeout(1000);

  // 等待事件
  await page.waitForEvent('load');
  await page.waitForEvent('popup');
});
```

## 断言

### 常用断言

```typescript
import { test, expect } from '@playwright/test';

test('断言', async ({ page }) => {
  await page.goto('/dashboard');

  // 可见性
  await expect(page.locator('.header')).toBeVisible();
  await expect(page.locator('.loading')).toBeHidden();
  await expect(page.locator('.optional')).not.toBeVisible();

  // 文本内容
  await expect(page.locator('h1')).toHaveText('Dashboard');
  await expect(page.locator('h1')).toContainText('Dash');
  await expect(page.locator('.message')).toHaveText(/welcome/i);

  // 属性
  await expect(page.locator('button')).toBeEnabled();
  await expect(page.locator('button')).toBeDisabled();
  await expect(page.locator('input')).toHaveAttribute('type', 'email');
  await expect(page.locator('input')).toHaveValue('test@example.com');

  // CSS
  await expect(page.locator('.button')).toHaveClass('btn-primary');
  await expect(page.locator('.button')).toHaveClass(/btn-/);
  await expect(page.locator('.element')).toHaveCSS('color', 'rgb(255, 0, 0)');

  // 数量
  await expect(page.locator('.item')).toHaveCount(5);

  // URL 和标题
  await expect(page).toHaveURL('http://localhost:3000/dashboard');
  await expect(page).toHaveURL(/dashboard$/);
  await expect(page).toHaveTitle('Dashboard - My App');
  await expect(page).toHaveTitle(/Dashboard/);

  // 截图比较
  await expect(page).toHaveScreenshot('dashboard.png');
  await expect(page.locator('.widget')).toHaveScreenshot('widget.png');
});
```

### 自定义断言

```typescript
test('自定义匹配器', async ({ page }) => {
  // 软断言 (失败后继续测试)
  await expect.soft(page.locator('.title')).toHaveText('Welcome');
  await expect.soft(page.locator('.subtitle')).toBeVisible();

  // 多个元素
  const items = page.locator('.item');
  await expect(items).toHaveCount(3);
  await expect(items.nth(0)).toContainText('First');
  await expect(items.nth(1)).toContainText('Second');

  // 轮询断言
  await expect(async () => {
    const response = await page.request.get('/api/status');
    expect(response.ok()).toBeTruthy();
  }).toPass({
    timeout: 10000,
    intervals: [1000, 2000, 5000],
  });
});
```

## 认证模式

### 存储状态模式

```typescript
// auth.setup.ts - 一次性保存认证状态
import { test as setup } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="username"]', 'testuser');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.waitForURL('/dashboard');

  // 保存认证状态
  await page.context().storageState({ path: authFile });
});

// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: authFile,
      },
      dependencies: ['setup'],
    },
  ],
});

// tests/dashboard.spec.ts - 已认证
test('查看仪表盘', async ({ page }) => {
  await page.goto('/dashboard');
  // 已登录!
  await expect(page.locator('.user-menu')).toBeVisible();
});
```

### 多用户角色

```typescript
// fixtures/auth.ts
import { test as base } from '@playwright/test';

type Fixtures = {
  adminPage: Page;
  userPage: Page;
};

export const test = base.extend<Fixtures>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/admin.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  userPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

// tests/permissions.spec.ts
import { test } from '../fixtures/auth';

test('管理员可以访问管理员面板', async ({ adminPage }) => {
  await adminPage.goto('/admin');
  await expect(adminPage.locator('.admin-panel')).toBeVisible();
});

test('普通用户无法访问管理员面板', async ({ userPage }) => {
  await userPage.goto('/admin');
  await expect(userPage.locator('.access-denied')).toBeVisible();
});
```

## 网络控制

### 请求模拟

```typescript
test('模拟 API 响应', async ({ page }) => {
  // 模拟 API 响应
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        users: [
          { id: 1, name: 'John Doe' },
          { id: 2, name: 'Jane Smith' },
        ],
      }),
    });
  });

  await page.goto('/users');
  await expect(page.locator('.user-list')).toContainText('John Doe');
});

test('条件模拟', async ({ page }) => {
  await page.route('**/api/**', route => {
    const url = route.request().url();

    if (url.includes('/users/1')) {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ id: 1, name: 'Test User' }),
      });
    } else if (url.includes('/users')) {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ users: [] }),
      });
    } else {
      route.continue();
    }
  });
});

test('模拟网络错误', async ({ page }) => {
  await page.route('**/api/data', route => {
    route.abort('failed');
  });

  await page.goto('/data');
  await expect(page.locator('.error-message')).toBeVisible();
});
```

### 请求拦截

```typescript
test('拦截和修改请求', async ({ page }) => {
  // 修改请求头
  await page.route('**/api/**', route => {
    const headers = route.request().headers();
    route.continue({
      headers: {
        ...headers,
        'X-Custom-Header': 'test-value',
      },
    });
  });

  // 修改 POST 数据
  await page.route('**/api/submit', route => {
    const postData = route.request().postDataJSON();
    route.continue({
      postData: JSON.stringify({
        ...postData,
        timestamp: Date.now(),
      }),
    });
  });
});

test('等待 API 响应', async ({ page }) => {
  // 等待特定请求
  const responsePromise = page.waitForResponse('**/api/users');
  await page.click('button#load-users');
  const response = await responsePromise;

  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data.users).toHaveLength(10);
});
```

## 测试组织

### 自定义固定装置

```typescript
// fixtures/todos.ts
import { test as base } from '@playwright/test';

type TodoFixtures = {
  todoPage: TodoPage;
  createTodo: (title: string) => Promise<void>;
};

export const test = base.extend<TodoFixtures>({
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await use(todoPage);
  },

  createTodo: async ({ page }, use) => {
    const create = async (title: string) => {
      await page.fill('.new-todo', title);
      await page.press('.new-todo', 'Enter');
    };
    await use(create);
  },
});

// tests/todos.spec.ts
import { test } from '../fixtures/todos';

test('可以创建新的待办事项', async ({ todoPage, createTodo }) => {
  await createTodo('Buy groceries');
  await expect(todoPage.todoItems).toHaveCount(1);
  await expect(todoPage.todoItems).toHaveText('Buy groceries');
});
```

### 测试标签和过滤

```typescript
test('冒烟测试', { tag: '@smoke' }, async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Home');
});

test('回归测试', { tag: ['@regression', '@critical'] }, async ({ page }) => {
  // 复杂测试
});

// 运行: npx playwright test --grep @smoke
// 运行: npx playwright test --grep-invert @slow
```

## 可视化测试

### 截图比较

```typescript
test('可视化回归', async ({ page }) => {
  await page.goto('/dashboard');

  // 全页截图
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
  });

  // 元素截图
  await expect(page.locator('.widget')).toHaveScreenshot('widget.png');

  // 带滚动全页
  await expect(page).toHaveScreenshot('full-page.png', {
    fullPage: true,
  });

  // 掩码动态元素
  await expect(page).toHaveScreenshot('masked.png', {
    mask: [page.locator('.timestamp'), page.locator('.avatar')],
  });

  // 自定义阈值
  await expect(page).toHaveScreenshot('comparison.png', {
    maxDiffPixelRatio: 0.05, // 允许 5% 的差异
  });
});
```

### 视频和跟踪

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    video: 'retain-on-failure',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
});

// 程序化视频
test('记录视频', async ({ page }) => {
  await page.goto('/');
  // 测试操作...

  // 视频自动保存到 test-results/
});

// 查看跟踪: npx playwright show-trace trace.zip
```

## 并行执行

### 测试分片

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 4 : undefined,
});

// 在 CI 中运行分片
// npx playwright test --shard=1/4
// npx playwright test --shard=2/4
// npx playwright test --shard=3/4
// npx playwright test --shard=4/4
```

### 串行测试

```typescript
test.describe.configure({ mode: 'serial' });

test.describe('顺序很重要', () => {
  let orderId: string;

  test('创建订单', async ({ page }) => {
    // 创建订单
    orderId = await createOrder(page);
  });

  test('验证订单', async ({ page }) => {
    // 使用前一个测试的 orderId
    await verifyOrder(page, orderId);
  });
});
```

## CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/playwright.yml
name: Playwright 测试
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: 安装依赖
        run: npm ci

      - name: 安装 Playwright 浏览器
        run: npx playwright install --with-deps

      - name: 运行 Playwright 测试
        run: npx playwright test

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### Docker

```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npx", "playwright", "test"]
```

## 调试

### UI 模式

```bash
# 交互式调试
npx playwright test --ui

# 调试特定测试
npx playwright test --debug login.spec.ts

# 单步调试
npx playwright test --headed --slow-mo=1000
```

### 跟踪查看器

```typescript
// 生成跟踪
test('带跟踪', async ({ page }) => {
  await page.context().tracing.start({ screenshots: true, snapshots: true });

  // 测试操作
  await page.goto('/');

  await page.context().tracing.stop({ path: 'trace.zip' });
});

// 查看: npx playwright show-trace trace.zip
```

### 控制台日志

```typescript
test('捕获控制台', async ({ page }) => {
  page.on('console', msg => console.log(`浏览器: ${msg.text()}`);
  page.on('pageerror', error => console.error(`错误: ${error.message}`));

  await page.goto('/');
});
```

## 最佳实践

### 1. 使用稳定定位器
```typescript
// ✅ 好 - 基于角色，稳定
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByLabel('Email').fill('test@example.com');

// ❌ 坏 - 易碎，依赖于实现
await page.click('button.btn-primary.submit-btn');
await page.locator('div.card:first-child').click();
```

### 2. 利用自动等待
```typescript
// ✅ 好 - 自动等待
await page.click('button');
await expect(page.locator('.result')).toBeVisible();

// ❌ 坏 - 手动等待
await page.waitForTimeout(2000);
await page.click('button');
```

### 3. 使用页面对象模型
```typescript
// ✅ 好 - 可重用，可维护
const loginPage = new LoginPage(page);
await loginPage.login('user', 'pass');

// ❌ 坏 - 重复的选择器
await page.fill('[name="username"]', 'user');
await page.fill('[name="password"]', 'pass');
```

### 4. 并行安全的测试
```typescript
// ✅ 好 - 独立
test('用户注册', async ({ page }) => {
  const uniqueEmail = `user-${Date.now()}@test.com`;
  await signUp(page, uniqueEmail);
});

// ❌ 坏 - 共享状态
test('用户注册', async ({ page }) => {
  await signUp(page, 'test@test.com'); // 并行时冲突
});
```

### 5. 处理不稳定
```typescript
// ✅ 好 - 等待网络空闲
await page.goto('/', { waitUntil: 'networkidle' });
await expect(page.locator('.data')).toBeVisible();

// 配置重试
test.describe(() => {
  test.use({ retries: 2 });

  test('不稳定的测试', async ({ page }) => {
    // 带自动重试的测试
  });
});
```

## 常见模式

### 多页面场景

```typescript
test('弹出窗口处理', async ({ page, context }) => {
  // 监听新页面
  const popupPromise = context.waitForEvent('page');
  await page.click('a[target="_blank"]');
  const popup = await popupPromise;

  await popup.waitForLoadState();
  await expect(popup).toHaveTitle('New Window');
  await popup.close();
});
```

### 条件逻辑

```typescript
test('处理可选元素', async ({ page }) => {
  await page.goto('/');

  // 如果存在模态框则关闭
  const modal = page.locator('.modal');
  if (await modal.isVisible()) {
    await page.click('.modal .close-button');
  }

  // 或使用数量
  const cookieBanner = page.locator('.cookie-banner');
  if ((await cookieBanner.count()) > 0) {
    await page.click('.accept-cookies');
  }
});
```

### 数据驱动测试

```typescript
const testCases = [
  { input: 'hello', expected: 'HELLO' },
  { input: 'World', expected: 'WORLD' },
  { input: '123', expected: '123' },
];

for (const { input, expected } of testCases) {
  test(`将 "${input}" 转换为 "${expected}"`, async ({ page }) => {
    await page.goto('/transform');
    await page.fill('input', input);
    await page.click('button');
    await expect(page.locator('.result')).toHaveText(expected);
  });
}
```

## 资源

- [Playwright 文档](https://playwright.dev/)
- [最佳实践指南](https://playwright.dev/docs/best-practices)
- [API 参考](https://playwright.dev/docs/api/class-playwright)
- [GitHub 示例](https://github.com/microsoft/playwright/tree/main/examples)
