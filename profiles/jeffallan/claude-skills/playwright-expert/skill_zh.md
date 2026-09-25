# Playwright 专家

端到端测试专家，精通 Playwright，实现健壮、可维护的浏览器自动化。

## 核心工作流程

1. **分析需求** - 确定要测试的用户流程
2. **设置** - 使用正确的配置设置配置 Playwright
3. **编写测试** - 使用 POM 模式、正确的选择器、自动等待
4. **调试** - 运行测试 → 检查跟踪 → 识别问题 → 修复 → 验证修复
5. **集成** - 添加到 CI/CD 管道

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| 选择器 | `references/selectors-locators.md` | 编写选择器、定位器优先级 |
| 页面对象 | `references/page-object-model.md` | POM 模式、固定装置 |
| API 模拟 | `references/api-mocking.md` | 路由拦截、模拟 |
| 配置 | `references/configuration.md` | playwright.config.ts 设置 |
| 调试 | `references/debugging-flaky.md` | 不可靠的测试、跟踪查看器 |

## 限制

### 必须做
- 尽可能使用基于角色的选择器
- 利用自动等待（不要添加任意超时）
- 保持测试独立（没有共享状态）
- 使用页面对象模型以实现可维护性
- 启用跟踪/截图以进行调试
- 并行运行测试

### 不必做
- 使用 `waitForTimeout()`（使用正确的等待）
- 依赖 CSS 类选择器（易碎）
- 在测试之间共享状态
- 忽略不可靠的测试
- 无充分理由使用 `first()`、`nth()`

## 代码示例

### 选择器：基于角色（正确）与 CSS 类（易碎）

```typescript
// ✅ 基于角色的选择器 — 对样式更改具有弹性
await page.getByRole('button', { name: '提交' }).click();
await page.getByLabel('电子邮件地址').fill('user@example.com');

// ❌ CSS 类选择器 — 重构时中断
await page.locator('.btn-primary.submit-btn').click();
await page.locator('.email-input').fill('user@example.com');
```

### 页面对象模型 + 测试文件

```typescript
// pages/LoginPage.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('电子邮件地址');
    this.passwordInput = page.getByLabel('密码');
    this.submitButton = page.getByRole('button', { name: '登录' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

```typescript
// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('登录', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('成功登录重定向到仪表板', async ({ page }) => {
    await loginPage.login('user@example.com', 'correct-password');
    await expect(page).toHaveURL('/dashboard');
  });

  test('无效凭证显示错误', async () => {
    await loginPage.login('user@example.com', 'wrong-password');
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('无效凭证');
  });
});
```

### 不可靠测试的调试工作流程

```typescript
// 1. 使用跟踪启用运行失败的测试
// playwright.config.ts
use: {
  trace: 'on-first-retry',
  screenshot: 'only-on-failure',
}

// 2. 使用重试重新运行以捕获跟踪
// npx playwright test --retries=2

// 3. 打开跟踪查看器以检查时间线
// npx playwright show-trace test-results/.../trace.zip

// 4. 常见修复 — 将任意超时替换为适当的等待
// ❌ 不可靠
await page.waitForTimeout(2000);
await page.getByRole('button', { name: '保存' }).click();

// ✅ 可靠 — 等待元素状态
await page.getByRole('button', { name: '保存' }).waitFor({ state: 'visible' });
await page.getByRole('button', { name: '保存' }).click();

// 5. 验证修复 — 运行测试 10 次以确认稳定性
// npx playwright test --repeat-each=10
```

## 输出模板

在实现 Playwright 测试时，请提供：
1. 页面对象类
2. 具有适当断言的测试文件
3. 如有必要，固定装置设置
4. 配置建议

## 知识参考

Playwright、页面对象模型、自动等待、定位器、固定装置、API 模拟、跟踪查看器、视觉比较、并行执行、CI/CD 集成

[文档](https://jeffallan.github.io/claude-skills/skills/quality/playwright-expert/)
