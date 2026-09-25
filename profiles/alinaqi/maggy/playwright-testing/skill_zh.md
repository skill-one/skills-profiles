# Playwright E2E 测试技能

使用 Playwright 进行 Web 应用程序的端到端测试 - 跨浏览器、快速、可靠。

**来源：** [Playwright 最佳实践](https://playwright.dev/docs/best-practices) | [Playwright 文档](https://playwright.dev/docs/intro) | [Better Stack 指南](https://betterstack.com/community/guides/testing/playwright-best-practices/)

---

## 设置

### 安装

```bash
# 新项目
npm init playwright@latest

# 现有项目
npm install -D @playwright/test
npx playwright install
```

### 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['list'],
    process.env.CI ? ['github'] : ['line'],
  ],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // 认证设置 - 在所有测试之前运行一次
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
    // 移动视图端口
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
      dependencies: ['setup'],
    },
  ],

  // 在测试之前启动开发服务器
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

---

## 项目结构

```
project/
├── e2e/
│   ├── fixtures/
│   │   ├── auth.fixture.ts      # 认证辅助数据
│   │   └── test.fixture.ts      # 带有辅助数据的扩展测试
│   ├── pages/
│   │   ├── base.page.ts         # 基础页面对象
│   │   ├── login.page.ts        # 登录页面对象
│   │   ├── dashboard.page.ts    # 仪表盘页面对象
│   │   └── index.ts             # 导出所有页面
│   ├── tests/
│   │   ├── auth.spec.ts         # 认证测试
│   │   ├── dashboard.spec.ts    # 仪表盘测试
│   │   └── checkout.spec.ts     # 结账流程测试
│   ├── utils/
│   │   ├── helpers.ts           # 测试辅助函数
│   │   └── test-data.ts         # 测试数据工厂
│   └── auth.setup.ts            # 全局认证设置
├── playwright.config.ts
└── .auth/                        # 存储认证状态（忽略 git）
```

---

## 定位策略（优先级顺序）

使用与用户交互方式一致的定位器：

```typescript
// ✅ 最佳：基于角色（可访问、健壮）
page.getByRole('button', { name: 'Submit' })
page.getByRole('textbox', { name: 'Email' })
page.getByRole('link', { name: 'Sign up' })
page.getByRole('heading', { name: 'Welcome' })

// ✅ 良好：面向用户文本
page.getByLabel('Email address')
page.getByPlaceholder('Enter your email')
page.getByText('Welcome back')
page.getByTitle('Profile settings')

// ✅ 良好：测试 ID（稳定、明确）
page.getByTestId('submit-button')
page.getByTestId('user-avatar')

// ⚠️ 避免：CSS 选择器（易碎）
page.locator('.btn-primary')
page.locator('#submit')

// ❌ 绝对避免：XPath（极其易碎）
page.locator('//div[@class="container"]/button[1]')
```

### 定位器链式调用

```typescript
// 缩小到特定区域
const form = page.getByRole('form', { name: 'Login' });
await form.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
await form.getByRole('button', { name: 'Submit' }).click();

// 在列表中筛选
const productCard = page.getByTestId('product-card')
  .filter({ hasText: 'Pro Plan' });
await productCard.getByRole('button', { name: 'Buy' }).click();
```

---

## 页面对象模型

### 基础页面

```typescript
// e2e/pages/base.page.ts
import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string = '/') {
    await this.page.goto(path);
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  // 常见元素
  get header() {
    return this.page.getByRole('banner');
  }

  get footer() {
    return this.page.getByRole('contentinfo');
  }

  // 常见操作
  async clickNavLink(name: string) {
    await this.header.getByRole('link', { name }).click();
  }
}
```

### 页面实现

```typescript
// e2e/pages/login.page.ts
import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.navigate('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectLoggedIn() {
    await expect(this.page).toHaveURL(/.*dashboard/);
  }
}
```

```typescript
// e2e/pages/dashboard.page.ts
import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class DashboardPage extends BasePage {
  readonly welcomeHeading: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.welcomeHeading = page.getByRole('heading', { name: /welcome/i });
    this.userMenu = page.getByTestId('user-menu');
    this.logoutButton = page.getByRole('button', { name: 'Logout' });
  }

  async goto() {
    await this.navigate('/dashboard');
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }

  async expectWelcome(name: string) {
    await expect(this.welcomeHeading).toContainText(name);
  }
}
```

### 导出所有页面

```typescript
// e2e/pages/index.ts
export { BasePage } from './base.page';
export { LoginPage } from './login.page';
export { DashboardPage } from './dashboard.page';
```

---

## 认证

### 全局认证设置

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  // 跳转到登录页面
  await page.goto('/login');

  // 使用测试凭证登录
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();

  // 等待认证完成
  await expect(page).toHaveURL(/.*dashboard/);

  // 保存认证状态以供重复使用
  await page.context().storageState({ path: authFile });
});
```

### 在测试中使用认证

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### 无需认证的测试

```typescript
// e2e/tests/public.spec.ts
import { test } from '@playwright/test';

// 覆盖以跳过认证
test.use({ storageState: { cookies: [], origins: [] } });

test('homepage loads for anonymous users', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

---

## 编写测试

### 基本测试结构

```typescript
// e2e/tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // 跳过存储的认证以进行登录测试
    await page.context().clearCookies();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('user@example.com', 'password123');
    await loginPage.expectLoggedIn();
  });

  test('invalid credentials show error', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login('wrong@example.com', 'wrongpass');
    await loginPage.expectError('Invalid email or password');
  });

  test('empty form shows validation errors', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.submitButton.click();

    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });
});
```

### 用户流程测试

```typescript
// e2e/tests/checkout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test('complete purchase flow', async ({ page }) => {
    // 1. 浏览产品
    await page.goto('/products');
    await page.getByTestId('product-card')
      .filter({ hasText: 'Pro Plan' })
      .getByRole('button', { name: 'Add to cart' })
      .click();

    // 2. 查看购物车
    await page.getByRole('link', { name: 'Cart' }).click();
    await expect(page.getByText('Pro Plan')).toBeVisible();
    await expect(page.getByTestId('cart-total')).toContainText('$29.99');

    // 3. 结账
    await page.getByRole('button', { name: 'Checkout' }).click();

    // 4. 填写支付（使用 Stripe 测试卡）
    const stripeFrame = page.frameLocator('iframe[name*="stripe"]');
    await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
    await stripeFrame.getByPlaceholder('MM / YY').fill('12/30');
    await stripeFrame.getByPlaceholder('CVC').fill('123');

    // 5. 完成购买
    await page.getByRole('button', { name: 'Pay now' }).click();

    // 6. 验证成功
    await expect(page).toHaveURL(/.*success/);
    await expect(page.getByRole('heading', { name: 'Thank you' })).toBeVisible();
  });
});
```

---

## 断言

### Web 首先断言（自动等待）

```typescript
// ✅ 这些会自动等待和重试
await expect(page.getByRole('button')).toBeVisible();
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('button')).toHaveText('Submit');
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle(/Dashboard/);

// ❌ 避免手动等待
await page.waitForTimeout(3000);  // 绝对不要这样做
```

### 软断言

```typescript
// 即使断言失败，也继续测试
await expect.soft(page.getByTestId('price')).toHaveText('$29.99');
await expect.soft(page.getByTestId('stock')).toHaveText('In Stock');

// 如果任何软断言失败，在末尾失败
```

### 常见断言

```typescript
// 可见性
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeAttached();

// 文本内容
await expect(locator).toHaveText('exact text');
await expect(locator).toContainText('partial');
await expect(locator).toHaveValue('input value');

// 状态
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeChecked();
await expect(locator).toBeFocused();

// 数量
await expect(locator).toHaveCount(5);

// 页面
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard | App');
await expect(page).toHaveScreenshot('dashboard.png');
```

---

## 模拟与网络

### 模拟 API 响应

```typescript
test('shows error when API fails', async ({ page }) => {
  // 模拟 API 返回错误
  await page.route('**/api/users', (route) => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Server error' }),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Failed to load users')).toBeVisible();
});

test('displays user data from API', async ({ page }) => {
  // 模拟成功响应
  await page.route('**/api/users', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Doe', email: 'jane@example.com' },
      ]),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('John Doe')).toBeVisible();
  await expect(page.getByText('Jane Doe')).toBeVisible();
});
```

### 等待 API 调用

```typescript
test('submits form and shows success', async ({ page }) => {
  await page.goto('/contact');

  // 填写表单
  await page.getByLabel('Name').fill('John');
  await page.getByLabel('Email').fill('john@example.com');
  await page.getByLabel('Message').fill('Hello!');

  // 提交时等待 API 调用
  const responsePromise = page.waitForResponse('**/api/contact');
  await page.getByRole('button', { name: 'Send' }).click();

  const response = await responsePromise;
  expect(response.status()).toBe(200);

  await expect(page.getByText('Message sent!')).toBeVisible();
});
```

---

## 可视化测试

```typescript
// 全页截图
await expect(page).toHaveScreenshot('homepage.png');

// 元素截图
await expect(page.getByTestId('chart')).toHaveScreenshot('chart.png');

// 带选项
await expect(page).toHaveScreenshot('dashboard.png', {
  maxDiffPixels: 100,
  mask: [page.getByTestId('timestamp')], // 忽略动态内容
});
```

---

## CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        run: npx playwright test --project=chromium
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
          TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

### 运行特定测试

```bash
# 运行所有测试
npx playwright test

# 运行特定文件
npx playwright test e2e/tests/auth.spec.ts

# 运行带标签的测试
npx playwright test --grep @critical

# 带界面模式运行（调试）
npx playwright test --headed

# 运行特定浏览器
npx playwright test --project=chromium

# 调试模式
npx playwright test --debug

# 显示 HTML 报告
npx playwright show-report
```

---

## 测试数据

### 工厂

```typescript
// e2e/utils/test-data.ts
import { faker } from '@faker-js/faker';

export const createUser = (overrides = {}) => ({
  email: faker.internet.email(),
  password: faker.internet.password({ length: 12 }),
  name: faker.person.fullName(),
  ...overrides,
});

export const createProduct = (overrides = {}) => ({
  name: faker.commerce.productName(),
  price: faker.commerce.price({ min: 10, max: 100 }),
  description: faker.commerce.productDescription(),
  ...overrides,
});
```

### 环境变量

```bash
# .env.test
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123
```

---

## 调试

### 跟踪查看器

```typescript
// 在配置中启用以在失败时查看
use: {
  trace: 'on-first-retry',
}

// 查看跟踪
npx playwright show-trace trace.zip
```

### 调试模式

```bash
# 单步调试测试
npx playwright test --debug

# 在特定点暂停
await page.pause();  // 在测试代码中
```

### VS Code 扩展

安装 "Playwright Test for VS Code" 以实现：
- 从编辑器运行测试
- 带断点调试
- 可视化选择定位器
- 监视模式

---

## 死链检测（必须）

**每个项目都必须包含死链检测测试。** 在每次部署时运行这些测试。

### 链接验证测试

```typescript
// e2e/tests/links.spec.ts
import { test, expect } from '@playwright/test';

const PAGES_TO_CHECK = ['/', '/about', '/pricing', '/blog', '/contact'];

test.describe('Dead Link Detection', () => {
  for (const pagePath of PAGES_TO_CHECK) {
    test(`no dead links on ${pagePath}`, async ({ page, request }) => {
      await page.goto(pagePath);

      // 获取页面上的所有链接
      const links = await page.locator('a[href]').all();
      const hrefs = await Promise.all(
        links.map(link => link.getAttribute('href'))
      );

      // 筛选内部和绝对外部链接
      const uniqueLinks = [...new Set(hrefs.filter(Boolean))] as string[];

      for (const href of uniqueLinks) {
        // 跳过 mailto、tel 和锚点链接
        if (href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#')) {
          continue;
        }

        // 构建完整 URL
        const url = href.startsWith('http') ? href : new URL(href, page.url()).href;

        // 检查链接状态
        const response = await request.get(url, {
          timeout: 10000,
          ignoreHTTPSErrors: true,
        });

        expect(
          response.ok(),
          `Dead link found on ${pagePath}: ${href} returned ${response.status()}`
        ).toBeTruthy();
      }
    });
  }
});
```

### 全面的链接爬虫

```typescript
// e2e/tests/site-links.spec.ts
import { test, expect, Page, APIRequestContext } from '@playwright/test';

interface LinkResult {
  url: string;
  status: number;
  foundOn: string;
}

async function checkAllLinks(
  page: Page,
  request: APIRequestContext,
  startUrl: string
): Promise<LinkResult[]> {
  const visited = new Set<string>();
  const results: LinkResult[] = [];
  const toVisit = [startUrl];
  const baseUrl = new URL(startUrl).origin;

  while (toVisit.length > 0) {
    const currentUrl = toVisit.pop()!;
    if (visited.has(currentUrl)) continue;
    visited.add(currentUrl);

    try {
      await page.goto(currentUrl);
      const links = await page.locator('a[href]').all();

      for (const link of links) {
        const href = await link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) {
          continue;
        }

        const fullUrl = href.startsWith('http') ? href : new URL(href, currentUrl).href;

        // 检查链接
        const response = await request.get(fullUrl, {
          timeout: 10000,
          ignoreHTTPSErrors: true,
        });

        results.push({
          url: fullUrl,
          status: response.status(),
          foundOn: currentUrl,
        });

        // 添加内部链接到队列
        if (fullUrl.startsWith(baseUrl) && !visited.has(fullUrl)) {
          toVisit.push(fullUrl);
        }
      }
    } catch (error) {
      results.push({
        url: currentUrl,
        status: 0,
        foundOn: 'navigation',
      });
    }
  }

  return results;
}

test('no dead links on entire site', async ({ page, request, baseURL }) => {
  const results = await checkAllLinks(page, request, baseURL!);
  const deadLinks = results.filter(r => r.status >= 400 || r.status === 0);

  if (deadLinks.length > 0) {
    console.error('Dead links found:');
    deadLinks.forEach(link => {
      console.error(`  ${link.url} (${link.status}) - found on ${link.foundOn}`);
    });
  }

  expect(deadLinks, `Found ${deadLinks.length} dead links`).toHaveLength(0);
});
```

### 图片链接验证

```typescript
// e2e/tests/images.spec.ts
import { test, expect } from '@playwright/test';

test('no broken images on homepage', async ({ page, request }) => {
  await page.goto('/');

  const images = await page.locator('img[src]').all();

  for (const img of images) {
    const src = await img.getAttribute('src');
    if (!src) continue;

    const url = src.startsWith('http') ? src : new URL(src, page.url()).href;

    // 跳过数据 URL
    if (url.startsWith('data:')) continue;

    const response = await request.get(url);
    expect(
      response.ok(),
      `Broken image: ${src}`
    ).toBeTruthy();

    // 验证它确实是一个图片
    const contentType = response.headers()['content-type'];
    expect(
      contentType?.startsWith('image/'),
      `${src} is not an image (${contentType})`
    ).toBeTruthy();
  }
});
```

### CI 集成用于链接检查

```yaml
# .github/workflows/link-check.yml
name: Link Check

on:
  schedule:
    - cron: '0 6 * * 1'  # 每周一早上
  push:
    branches: [main]

jobs:
  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install chromium
      - run: npx playwright test e2e/tests/links.spec.ts --project=chromium
        env:
          BASE_URL: ${{ secrets.PRODUCTION_URL }}
```

---

## 反模式

- **硬编码等待** - 使用自动等待断言
- **CSS/XPath 选择器** - 使用角色/文本/testid 定位器
- **测试第三方网站** - 模拟外部依赖
- **测试间共享状态** - 每个测试必须隔离
- **缺少 awaits** - 使用 ESLint 规则 `no-floating-promises`
- **易碎的时间测试** - 模拟日期/时间
- **测试实现细节** - 测试用户可见行为
- **过大的测试文件** - 按功能/页面拆分

---

## 快速参考

```bash
# 安装
npm init playwright@latest

# 运行测试
npx playwright test
npx playwright test --headed
npx playwright test --project=chromium
npx playwright test --grep @smoke

# 调试
npx playwright test --debug
npx playwright show-report
npx playwright show-trace trace.zip

# 生成测试
npx playwright codegen localhost:3000
```

### package.json 脚本

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report",
    "test:e2e:codegen": "playwright codegen"
  }
}
```
