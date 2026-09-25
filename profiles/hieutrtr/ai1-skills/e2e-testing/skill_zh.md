# 端到端测试

## 使用场景

在以下情况下启用此技能：
- 编写端到端测试以覆盖完整的用户工作流程（登录、CRUD操作、多页面流程）
- 创建关键路径回归测试以验证完整的技术栈
- 测试跨浏览器兼容性（Chromium、Firefox、WebKit）
- 验证端到端的身份验证流程
- 测试文件上传/下载工作流程
- 编写部署验证的冒烟测试

不要使用此技能：
- React组件单元测试（使用`react-testing-patterns`）
- Python后端单元/集成测试（使用`pytest-patterns`）
- 强制TDD工作流程（使用`tdd-workflow`）
- 无需浏览器的API契约测试（使用`pytest-patterns`配合httpx）

## 使用说明

### 测试结构

```
e2e/
├── playwright.config.ts         # 全局Playwright配置
├── fixtures/
│   ├── auth.fixture.ts          # 身份验证状态设置
│   └── test-data.fixture.ts     # 测试数据创建/清理
├── pages/
│   ├── base.page.ts             # 基础页面对象，包含共享方法
│   ├── login.page.ts            # 登录页面对象
│   ├── users.page.ts            # 用户列表页面对象
│   └── user-detail.page.ts     # 用户详情页面对象
├── tests/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   └── logout.spec.ts
│   ├── users/
│   │   ├── create-user.spec.ts
│   │   ├── edit-user.spec.ts
│   │   └── list-users.spec.ts
│   └── smoke/
│       └── critical-paths.spec.ts
└── utils/
    ├── api-helpers.ts           # 测试设置的直接API调用
    └── test-constants.ts        # 共享常量
```

**命名规范：**
- 测试文件：`<功能>.spec.ts`
- 页面对象：`<页面名称>.page.ts`
- 测试数据：`<关注点>.fixture.ts`
- 测试名称：描述用户操作和预期结果的易读句子

### 页面对象模型

每个页面都有一个页面对象类，封装选择器和操作。测试永远不会直接与选择器交互。

**基础页面对象：**
```typescript
// e2e/pages/base.page.ts
import { type Page, type Locator } from "@playwright/test";

export abstract class BasePage {
  constructor(protected readonly page: Page) {}

  /** 导航到页面的URL。 */
  abstract goto(): Promise<void>;

  /** 等待页面完全加载。 */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState("networkidle");
  }

  /** 获取toast/通知消息。 */
  get toast(): Locator {
    return this.page.getByRole("alert");
  }

  /** 获取页面标题。 */
  get heading(): Locator {
    return this.page.getByRole("heading", { level: 1 });
  }
}
```

**具体页面对象：**
```typescript
// e2e/pages/users.page.ts
import { type Page, type Locator } from "@playwright/test";
import { BasePage } from "./base.page";

export class UsersPage extends BasePage {
  // ─── 选择器 ─────────────────────────────────────────
  readonly createButton: Locator;
  readonly searchInput: Locator;
  readonly userTable: Locator;

  constructor(page: Page) {
    super(page);
    this.createButton = page.getByTestId("create-user-btn");
    this.searchInput = page.getByRole("searchbox", { name: /search users/i });
    this.userTable = page.getByRole("table");
  }

  // ─── 操作 ──────────────────────────────────────────
  async goto(): Promise<void> {
    await this.page.goto("/users");
    await this.waitForLoad();
  }

  async searchFor(query: string): Promise<void> {
    await this.searchInput.fill(query);
    // 等待搜索结果更新（防抖）
    await this.page.waitForResponse("**/api/v1/users?*");
  }

  async clickCreateUser(): Promise<void> {
    await this.createButton.click();
  }

  async getUserRow(email: string): Promise<Locator> {
    return this.userTable.getByRole("row").filter({ hasText: email });
  }

  async getUserCount(): Promise<number> {
    // 减去1为表头行
    return (await this.userTable.getByRole("row").count()) - 1;
  }
}
```

**页面对象规则：**
- 每个页面或主要UI部分一个页面对象
- 选择器是公共只读属性
- 操作是异步方法
- 页面对象不包含断言——测试断言
- 页面对象在操作后内部处理等待

### 选择器策略

**优先级顺序（从高到低）：**

| 优先级 | 选择器 | 示例 | 使用场景 |
|--------|--------|------|----------|
| 1 | `data-testid` | `getByTestId("submit-btn")` | 交互元素、动态内容 |
| 2 | Role | `getByRole("button", { name: /save/i })` | 按钮、链接、标题、输入 |
| 3 | Label | `getByLabel("Email")` | 带标签的表单输入 |
| 4 | Placeholder | `getByPlaceholder("Search...")` | 搜索输入 |
| 5 | Text | `getByText("Welcome back")` | 静态文本内容 |

**绝对不要使用：**
- CSS选择器（`.class-name`, `#id`）——脆弱，样式变化时会失效
- XPath (`//div[@class="foo"]`) ——难以阅读，极其脆弱
- DOM结构选择器（`div > span:nth-child(2)`）——布局变化时会失效

**添加data-testid属性：**
```tsx
// 在React组件中——为交互元素添加data-testid
<button data-testid="create-user-btn" onClick={handleCreate}>
  Create User
</button>

// 规范：kebab-case，描述性
// 模式：`<操作>-<实体>-<元素类型>`
// 示例：create-user-btn，user-email-input，delete-confirm-dialog
```

### 等待策略

**绝对不要使用硬编码等待：**
```typescript
// BAD：硬编码等待——不稳定，慢
await page.waitForTimeout(3000);

// BAD：睡眠
await new Promise((resolve) => setTimeout(resolve, 2000));
```

**使用显式等待条件：**
```typescript
// GOOD：等待特定元素出现
await page.getByRole("heading", { name: "Dashboard" }).waitFor();

// GOOD：等待导航
await page.waitForURL("/dashboard");

// GOOD：等待API响应
await page.waitForResponse(
  (response) =>
    response.url().includes("/api/v1/users") && response.status() === 200,
);

// GOOD：等待网络空闲
await page.waitForLoadState("networkidle");

// GOOD：等待元素状态
await page.getByTestId("submit-btn").waitFor({ state: "visible" });
await page.getByTestId("loading-spinner").waitFor({ state: "hidden" });
```

**自动等待：** Playwright在点击、填充等操作前自动等待元素可交互。显式等待仅在断言或复杂状态转换时需要。

### 身份验证状态复用

避免在每次测试前登录。保存身份验证状态并复用。

**一次性设置身份验证状态：**
```typescript
// e2e/fixtures/auth.fixture.ts
import { test as base } from "@playwright/test";
import path from "path";

const AUTH_STATE_PATH = path.resolve("e2e/.auth/user.json");

export const setup = base.extend({});

setup("authenticate", async ({ page }) => {
  // 执行真实登录
  await page.goto("/login");
  await page.getByLabel("Email").fill("testuser@example.com");
  await page.getByLabel("Password").fill("TestPassword123!");
  await page.getByRole("button", { name: /sign in/i }).click();

  // 等待身份验证完成
  await page.waitForURL("/dashboard");

  // 保存登录状态
  await page.context().storageState({ path: AUTH_STATE_PATH });
});
```

**在测试中复用：**
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    // 设置项目首先运行并保存身份验证状态
    { name: "setup", testDir: "./e2e/fixtures", testMatch: "auth.fixture.ts" },
    {
      name: "chromium",
      use: {
        storageState: "e2e/.auth/user.json",  // 复用身份验证状态
      },
      dependencies: ["setup"],
    },
  ],
});
```

### 测试数据管理

**原则：**
- 测试创建自己的数据（不要依赖预存在数据）
- 测试清理自身（或使用API重置）
- 使用API调用进行设置，而不是UI交互（更快、更可靠）

**测试数据API辅助：**
```typescript
// e2e/utils/api-helpers.ts
import { type APIRequestContext } from "@playwright/test";

export class TestDataAPI {
  constructor(private request: APIRequestContext) {}

  async createUser(data: { email: string; displayName: string }) {
    const response = await this.request.post("/api/v1/users", { data });
    return response.json();
  }

  async deleteUser(userId: number) {
    await this.request.delete(`/api/v1/users/${userId}`);
  }

  async createOrder(userId: number, items: Array<Record<string, unknown>>) {
    const response = await this.request.post("/api/v1/orders", {
      data: { user_id: userId, items },
    });
    return response.json();
  }
}
```

**在测试中使用：**
```typescript
test("编辑用户名", async ({ page, request }) => {
  const api = new TestDataAPI(request);

  // 设置：通过API创建用户（快速）
  const user = await api.createUser({
    email: "edit-test@example.com",
    displayName: "编辑前",
  });

  try {
    // 测试：通过UI编辑
    const usersPage = new UsersPage(page);
    await usersPage.goto();
    // ... 通过UI执行编辑 ...
  } finally {
    // 清理：删除测试数据
    await api.deleteUser(user.id);
  }
});
```

### 不稳定测试调试

**1. 使用跟踪查看器查看失败：**
```typescript
// playwright.config.ts
use: {
  trace: "on-first-retry",  // 仅在重试时捕获跟踪
}
```

查看跟踪：`npx playwright show-trace trace.zip`

**2. 以带UI模式调试：**
```bash
npx playwright test --headed --debug tests/users/create-user.spec.ts
```

**3. 不稳定测试的常见原因：**
| 原因 | 解决方法 |
|------|----------|
| 硬编码等待 | 使用显式等待条件 |
| 共享测试数据 | 每个测试创建自己的数据 |
| 动画干扰 | 在配置中设置`animations: "disabled"` |
| 竞态条件 | 等待API响应后再断言 |
| 视口依赖行为 | 在配置中设置显式视口 |
| 测试间会话泄漏 | 正确使用`storageState`，清除cookies |

**4. 重试策略：**
```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // 仅在CI中重试
});
```

### CI配置

```yaml
# .github/workflows/e2e.yml
name: 端到端测试
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: 安装依赖
        run: npm ci

      - name: 安装Playwright浏览器
        run: npx playwright install --with-deps chromium

      - name: 启动应用程序
        run: |
          docker compose up -d
          npx wait-on http://localhost:3000 --timeout 60000

      - name: 运行端到端测试
        run: npx playwright test

      - name: 上传测试报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14

      - name: 失败时上传跟踪
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-traces
          path: test-results/
```

使用`scripts/run-e2e-with-report.sh`在本地运行Playwright并输出HTML报告。

## 示例

参考`references/page-object-template.ts`查看带注释的页面对象类。
参考`references/e2e-test-template.ts`查看带注释的端到端测试。
参考`references/playwright-config-example.ts`查看生产Playwright配置。
