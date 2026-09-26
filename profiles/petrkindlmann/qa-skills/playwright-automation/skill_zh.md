<objective>
如何编写稳定、可维护、适用于生产环境的 Playwright 测试（使用 TypeScript）。防止的失败：AI 代理会本能地使用三种模式来生成一次性通过但永远出现错误的测试套件——从不使用 `waitForTimeout`，从不默认使用 CSS 选择器，以及避免使用遗留的 `page.click()` 系列。这项技能包含了自动等待、面向用户定位符、基于 fixture 的规范，这些规范使得测试套件能够在重构后依然保持稳定。
</objective>

## 发现问题

首先检查 `.agents/qa-project-context.md` — 如果存在，使用它并跳过其中已回答的问题。然后只询问缺失的问题：

1. **TypeScript 还是 JavaScript？** 强烈建议使用 TypeScript — 它可以在编译时捕获定位符和断言错误，并且这里的每个示例都假设使用 TypeScript。
2. **哪些浏览器？** 本地开发使用 Chromium；在 CI 中添加 Firefox 和 WebKit。移动视图端口是独立的 Playwright 项目，而不是独立的测试文件——它们会改变设备描述符。
3. **现有套件还是重新开始？** 从 Cypress/Selenium 迁移，首先重写最容易出现错误的测试；不要进行大规模重构。这会完全改变顺序。
4. **单站点还是多站点？** 多站点需要共享的 fixture 和每个站点的配置对象——参见 `references/multi-site-architecture.md`。

---

## 核心原则

1. **首先使用面向用户的定位符。** `getByRole` > `getByLabel` > `getByTestId` > CSS（最后的选择）。定位符必须反映用户看到的内容，而不是 DOM 的结构。参见 `references/selector-strategies.md`。
2. **自动等待——绝对不要使用 `waitForTimeout`。** 每个 Playwright 操作和 web-first 断言都会自动等待。如果你认为需要超时，那么你需要更好的定位符或断言。
3. **测试隔离。** 每个测试都获得一个新鲜的 `BrowserContext`。测试绝不能依赖于其他测试的状态或执行顺序。
4. **默认并行，只有在必要时才串行。** 使用 `fullyParallel: true`。将 `test.describe.serial` 保留给那些确实无法隔离的流程（很少见）。
5. **使用 fixture 进行设置，而不是钩子。** Fixture 组合，提供类型安全，并自动销毁。对于任何非平凡的操作，优先使用它们而不是 `beforeEach`/`afterEach`。参见 `references/fixtures-and-projects.md`。

> **根据团队成熟度进行校准**（在 `.agents/qa-project-context.md` 中设置 `team_maturity`）：
> - **初创阶段** — 仅使用 Chromium，5–10 个关键路径测试，在 PR 上运行基本的 CI。直到套件稳定之前，跳过分片和视觉基线。
> - **成长阶段** — Chromium + Firefox，POM 结构，并行执行，CI 中的分片，HTML 报告工件。
> - **成熟阶段** — 完整的浏览器矩阵，认证 fixture，API 模拟层，视觉回归基线，失败时跟踪，错误率跟踪。

---

## 项目结构

```
project-root/
├── playwright.config.ts
├── e2e/
│   ├── fixtures/              # base.fixture.ts, auth.fixture.ts, data.fixture.ts
│   ├── pages/                 # 按功能划分的页面对象
│   │   ├── base.page.ts
│   │   ├── dashboard.page.ts
│   │   └── components/        # 可重用的组件对象（data-table, modal）
│   ├── tests/                 # 按功能划分的测试文件（auth/, dashboard/, settings/)
│   ├── helpers/               # test-data.ts, api-client.ts
│   └── global-setup.ts
├── .auth/                     # Git 忽略的 storageState 文件
└── test-results/              # Git 忽略的工件
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

const isCI = !!process.env.CI;
const baseURL = process.env.BASE_URL ?? 'http://localhost:3000';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? '50%' : undefined,
  reporter: isCI
    ? [['blob'], ['github'], ['json', { outputFile: 'test-results/results.json' }]]
    : [['html', { open: 'on-failure' }]],
  use: {
    baseURL,
    trace: isCI ? 'on-first-retry' : 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: isCI ? 'on-first-retry' : 'off',
    navigationTimeout: 30_000,
    // 避免全局的 actionTimeout——它可以掩盖一个真正缓慢的自动等待操作。
    // 仅在已知缓慢的组件需要时设置。
  },
  projects: [
    { name: 'setup', testMatch: /global-setup\.ts/, teardown: 'teardown' },
    { name: 'teardown', testMatch: /global-teardown\.ts/ },
    { name: 'chromium', use: { ...devices['Desktop Chrome'], storageState: '.auth/user.json' }, dependencies: ['setup'] },
    { name: 'firefox', use: { ...devices['Desktop Firefox'], storageState: '.auth/user.json' }, dependencies: ['setup'] },
    { name: 'webkit', use: { ...devices['Desktop Safari'], storageState: '.auth/user.json' }, dependencies: ['setup'] },
  ],
  webServer: isCI ? undefined : {
    command: 'npm run dev', url: baseURL, reuseExistingServer: !isCI, timeout: 120_000,
  },
});
```

CI 中的 `blob` 报告器使得分片运行是可合并的——参见分片部分。`setup` 项目在浏览器项目依赖它之前，会一次性写入 `storageState`。

### 全局设置（storageState）

```typescript
import { test as setup, expect } from '@playwright/test';

setup('以默认用户身份进行认证', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/.*dashboard/);
  await page.context().storageState({ path: '.auth/user.json' });
});
```

这是 `setup` 项目的模式：设置项目（或 `globalSetup` 文件）运行一次 UI 登录，并且每个浏览器项目通过 config 中的 `storageState` 重放保存的 cookies/localStorage。对于多角色认证（管理员/用户/访客）和 token 种子，参见 `references/auth-patterns.md`。

---

## 页面对象模型

```typescript
import { type Page, type Locator, expect } from '@playwright/test';

export abstract class BasePage {
  constructor(protected readonly page: Page) {}
  abstract readonly path: string;
  async goto(): Promise<void> {
    await this.page.goto(this.path);
    await this.page.waitForLoadState('domcontentloaded');
  }
}
```

**组件对象** 表示可重用的 UI 片段（模态框、表格、导航）。它们接受一个根 `Locator`，而不是 `Page`：

```typescript
export class DataTable {
  readonly rows: Locator;
  constructor(private readonly root: Locator) {
    this.rows = root.getByRole('row');
  }
  getRowByText(text: string | RegExp): Locator {
    return this.rows.filter({ hasText: text });
  }
}
```

**组合，而不是深度继承。** 页面持有它的组件；它不扩展一个五层的层次结构：

```typescript
export class UsersPage extends BasePage {
  readonly path = '/admin/users';
  readonly table: DataTable;
  constructor(page: Page) {
    super(page);
    this.table = new DataTable(page.getByRole('table', { name: 'Users' }));
  }
}
```

**通过 fixture 注入页面对象**，而不是在测试文件中通过构造函数注入：

```typescript
export const test = base.extend<{ usersPage: UsersPage }>({
  usersPage: async ({ page }, use) => { await use(new UsersPage(page)); },
});
export { expect } from '@playwright/test';
```

POM 方法返回状态（定位符、值）；它们不进行断言。断言存在于测试中，这样失败时指向的是测试，而不是页面对象。

---

## 测试模式

### 使用 test.step 进行表单交互

将逻辑操作组包裹在 `test.step()` 中，以便在 trace-viewer 输出中更易读：

```typescript
test('提交一个多步骤表单', async ({ page }) => {
  await page.goto('/onboarding');
  await test.step('填写个人信息', async () => {
    await page.getByLabel('First name').fill('Jane');
    await page.getByRole('button', { name: 'Next' }).click();
  });
  await test.step('提交', async () => {
    await page.getByRole('button', { name: 'Complete setup' }).click();
  });
  await expect(page).toHaveURL('/dashboard');
});
```

### API 模拟

```typescript
// 模拟响应
await page.route('**/api/products*', async (route) => {
  await route.fulfill({ json: { items: [{ id: '1', name: 'Widget', price: 29.99 }] } });
});

// 修改真实响应
await page.route('**/api/feature-flags', async (route) => {
  const response = await route.fetch();
  const body = await response.json();
  body.flags['new-checkout'] = true;
  await route.fulfill({ response, json: body });
});

// 模拟错误
await page.route('**/api/products*', (route) => route.fulfill({ status: 500 }));

// WebSocket（v1.48+）
await page.routeWebSocket('**/ws/notifications', (ws) => {
  ws.onMessage(() => ws.send(JSON.stringify({ type: 'alert', title: 'Deployed' })));
});
```

参见 `references/network-and-mocking.md` 了解 HAR 回放和条件路由。

### 认证 APIRequestContext fixture

为了播种数据或断言后端状态而不驱动 UI，注入一个预认证的 `APIRequestContext`。在 fixture 中获取 token；永远不要硬编码它：

```typescript
import { test, request, type APIRequestContext } from '@playwright/test';

// test.extend 为 base test 对象添加了一个 `api` fixture。
export const apiTest = test.extend<{ api: APIRequestContext }>({
  api: async ({ baseURL }, use) => {
    const ctx = await request.newContext({
      baseURL,
      extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN!}` },
    });
    await use(ctx);
    await ctx.dispose();
  },
});
```

### 标签和注释

```typescript
test('checkout @smoke', async ({ page }) => { /* npx playwright test --grep @smoke */ });
test.slow();                                    // 增加三倍超时
test.skip(({ browserName }) => browserName === 'webkit', 'WebKit bug');
test.fixme('已知问题跟踪在 JIRA-1234', async ({ page }) => { /* ... */ });
```

---

## 断言

始终优先使用 web-first 断言——它们会自动重试，直到条件成立或超时过期：

```typescript
await expect(page.getByRole('alert')).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page).toHaveURL('/dashboard');
await expect(page.getByRole('button', { name: 'Save' })).toBeEnabled();
await expect(page.getByRole('listitem')).toHaveCount(5);
await expect(page.getByRole('listitem')).toHaveText(['Apple', 'Banana', 'Cherry']);
```

**软断言** 收集所有失败，而不是在第一个失败时停止：

```typescript
await expect.soft(page.getByLabel('Name')).toHaveValue('Jane Doe');
await expect.soft(page.getByLabel('Email')).toHaveValue('jane@example.com');
```

**ARIA 快照** 验证可访问性树结构并捕获语义回归：

```typescript
await expect(page.getByRole('navigation', { name: 'Main' })).toMatchAriaSnapshot(`
  - navigation "Main":
    - link "Home"
    - link "Products"
`);
```

### 视觉回归（单行；延迟工作流）

Playwright 的内置 `toHaveScreenshot` 会自动重试并在第一次运行时写入基线。遮盖动态区域；不要在它前面使用 `waitForTimeout`：

```typescript
await expect(page.getByTestId('product-card')).toHaveScreenshot('product-card.png', {
  mask: [page.getByTestId('price')],
});
```

对于基线管理、阈值（`maxDiffPixelRatio`、`maskColor`、`stylePath`）和审查工作流，使用 `visual-testing`——视觉基线属于那里。

### 可访问性扫描（axe；深度审计在其他地方）

上面的 ARIA 快照检查结构，而不是 WCAG 规则。对于基于规则的扫描，添加 `@axe-core/playwright`：

```typescript
import AxeBuilder from '@axe-core/playwright';

test('dashboard 没有可访问性违规', async ({ page }) => {
  await page.goto('/dashboard');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

对于 WCAG 级别、规则调整和修复指导，使用 `accessibility-testing`。

---

## 并行执行与 CI

### 在 CI 节点之间分片

将套件分成矩阵作业，然后将分片报告合并成一个 HTML 报告。分片在 `growing`+ 成熟度时才有其价值；一个 5–10 个测试的 `startup` 套件不应该分片。

```yaml
strategy:
  fail-fast: false
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npx playwright test --shard=${{ matrix.shard }}/4
```

每个分片上传它的 `blob-report/`；一个最终作业运行 `npx playwright merge-reports --reporter=html ./all-blob-reports`。上面的 `blob` 报告器（在配置中设置）使得合并工作成为可能——单独使用 `--shard` 产生碎片化的 HTML 报告。参见 `references/ci-recipes.md` 了解完整的 GitHub Actions 工作流、blob 上传/下载和工件模式。

### 调试

- **Trace viewer:** `npx playwright show-trace test-results/.../trace.zip` — 操作、网络、DOM 快照、控制台的时序图。
- **UI 模式:** `npx playwright test --ui` — 实时、逐步、时间旅行。
- **调试标志:** `npx playwright test my-test.spec.ts --debug` — 带头部的，每个操作都会暂停。
- **VS Code 扩展** `ms-playwright.playwright` — 从沟槽运行/调试，选择定位符，监视模式。
- **`page.pause()`** 在测试中途打开 Inspector。仅限本地——永远不要提交它。

参见 `references/debugging-and-triage.md` 了解错误率测试的排查和工件分析。

---

## 新功能（2025-2026）

当前最新版本是 **Playwright 1.60.0**（2026 年 5 月）。在 `package.json` 和 CI Docker 镜像中固定相同版本。最近值得了解的新功能：

| 版本 | 功能 | 它的作用 |
|------|------|----------|
| v1.45 | 时钟 API | `page.clock.install()` / `fastForward()` — 无需猴子修补 `Date` 即控制时间 |
| v1.45 | `--fail-on-flaky-tests` | 如果任何测试需要重试才能通过，则失败 CI 运行 |
| v1.46 | `--only-changed` | 仅运行受更改文件影响的测试（git-diff 感知） |
| v1.46 | ARIA 快照 | `toMatchAriaSnapshot()` 用于可访问性树断言 |
| v1.48 | `routeWebSocket` | 一流的 WebSocket 中断（取代 CDP 把戏） |
| v1.55 | 测试迁移器 | 通过 `npx playwright migrate` 自动从 Cypress→/Selenium→Playwright 迁移 |
| v1.56 | 测试代理 | `npx playwright init-agents --loop=claude\|vscode\|opencode` — 在编码代理的循环内运行的规划器/生成器/修复代理 |
| v1.57 | 测试默认为 Chrome for Testing | 带头部的使用 `chrome`，无头使用 `chrome-headless-shell` 而不是捆绑的 Chromium。注意：报告了一个高内存回归（microsoft/playwright #38489）——为 CI 固定一个已知良好的镜像标签。 |
| v1.57 | `toHaveScreenshot` 选项 | `maskColor`、`stylePath`、`pathTemplate` 用于遮盖颜色、自定义样式和输出路径控制 |
| v1.59 | 屏幕录制 API | `page.screencast.start()` / `.stop()` 用于具有开始/停止控制的测试中视频——是 `recordVideo` 的替代方案，而不是替代品。添加操作注释、章节标记、自定义 HTML 覆盖层，以及 `screencast.showOverlays()` / `hideOverlays()`。对于代理自我验证很有用：编码代理可以转交一个可审查的视频收据。 |
| v1.59 | `--debug=cli` | 暂停并附加，以便代理可以逐步执行测试 |
| v1.60 | `locator.drop()` | 模拟将外部文件/剪贴板拖放到元素上 |
| v1.60 | `tracing.startHar()` | HAR 录制作为一流的跟踪 API |

### AI 增强编写（测试代理 vs MCP）

两条集成路径——根据代理是否在编辑器循环内运行或远程驱动真实浏览器来选择。

**路径 A — 测试代理 (`npx playwright init-agents --loop=claude`)**：为编码代理在循环期间加载的规划器/生成器/修复代理搭建脚手架。高效——没有 MCP 服务器，没有进程间流量。最适合“Claude/VS Code/opencode 为我编写 Playwright 测试。”

**路径 B — `@playwright/mcp`**：一个暴露浏览器操作给任何 MCP 感知的代理的 MCP 服务器。开销较高（进程边界、JSON 序列化），但在代理必须交互式地驱动真实浏览器而不是离线编写测试时是正确的选择。配置：在 `.mcp.json` 中 `{ "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }`。

对于测试失败修复，参见 `test-reliability`。对于从 PRD/规范中的首次生成，参见 `ai-test-generation`。

---

## 反模式

设计时的错误，悄无声息地使套件腐烂。代码级别的“永远不要做 X”列表在 `references/anti-patterns.md` 中与 BAD/GOOD 对应——在编写测试体时加载它。

### 1. 神页对象
一个类用于整个应用程序会变成一个 2000 行的文件，每个测试都会导入它，并且没有任何东西可以安全地重构。按页面/功能划分，并通过根 `Locator` 组合组件对象。

### 2. 断言的 POM 方法
一个页面对象，其方法调用 `expect` 会将断言隐藏在测试中。当它失败时，堆栈指向页面对象，而不是失败的场景。返回定位符/状态；在测试中断言。

### 3. 基于实现的断言
键入到 CSS 类、DOM 嵌套或内部 ID 的测试在每次重构时都会在没有真正行为变化的情况下失败。断言用户感知的内容——可见文本、角色、URL。

### 4. 依赖测试顺序的 fixture
一个在共享模块状态上变异的 fixture，或假设另一个测试首先运行，在测试并行化或独立运行时就会失败。每个 fixture 必须独立。

### 5. `data-testid` 而不是 `getByRole`
在已经具有可访问名称的按钮和标题上撒上测试 ID，会跳过免费获得的最低可访问性信号。保留 `getByTestId` 用于没有稳定角色/标签的元素。

最有害的 *运行时* 错误——使用 `waitForTimeout` 而不是自动等待定位符：

```typescript
// BAD — 在快速机器上慢，在慢机器上不可靠，掩盖了真实条件
await page.waitForTimeout(2000);
await page.click('#submit');

// GOOD — 操作自动等待可操作性
await page.getByRole('button', { name: 'Submit' }).click();
```

其他九个代码级违规（CSS 覆盖角色、`page.*` 覆盖定位符、`force: true`、共享状态、每个测试登录、`locator.all()` 而没有稳定性检查、`allTextContents()` 覆盖 `toHaveText()`、访问真实第三方服务、提交的 `test.only`) 在 `references/anti-patterns.md` 中。

---

## 验证

按生成的工件从小到大运行这些：

```bash
npx playwright test --list                 # 测试被发现并解析
grep -rn 'waitForTimeout\|page.pause' e2e/  # 必须打印为空
npx tsc --noEmit                            # 定位符/断言类型编译
```

使用 `eslint-plugin-playwright` 在 CI 中强制执行“永远不要做 X”规则——规则 `no-wait-for-timeout`、`no-force-option`、`no-element-handle`、`no-page-pause` 将这项技能的文本禁令转换为失败的 lint。

---

## 完成

- `playwright.config.ts` 存在，并且至少为 Chromium 定义了 `projects`（Firefox + WebKit 在针对 CI 时添加），并且 `forbidOnly: !!process.env.CI`。
- 页面对象模型文件位于 `e2e/pages/`（或等效位置），通过根 `Locator` 组合组件对象，并且 POM 方法中没有任何 `expect`。
- `grep -rn 'waitForTimeout' e2e/` 返回为空，并且 `eslint-plugin-playwright` 的 `no-wait-for-timeout` 已启用。
- 每个定位符使用 `getByRole` / `getByLabel` / `getByTestId` — `grep -rn 'page.locator(\|xpath=\|css=' e2e/` 返回为空（或仅限于合理的注释例外）。
- CI 在 PR 上运行套件；在 `growing`+ 成熟度时，它在矩阵作业之间分片，使用 `blob` 报告器和一个 `merge-reports` 步骤，将 HTML 报告作为失败时的工件上传。

## 相关技能

- **visual-testing** — 屏幕快照基线创建、阈值调整和审查/批准工作流。对于任何超出单个内联 `toHaveScreenshot` 检查的内容，请从这里开始。
- **accessibility-testing** — WCAG 级别、axe 规则调整和修复。这项技能只显示一个最小的 axe 扫描。
- **api-testing** — 后端 API 验证、架构/合同测试，以及完整的 `APIRequestContext` 模式。
- **ci-cd 集成** — 管道配置、并行化、报告超出 Playwright 自身的。
- **test-reliability** — 单个错误率测试的运行时修复（隔离、重试策略）。
- **selector-drift-recovery** — 在 UI 重构破坏许多测试后，离线批量重新生成选择符。

### 参考文件（在 `references/` 中）

| 文件 | 目的 |
|------|------|
| `anti-patterns.md` | BAD vs GOOD 代码对每个代码级错误 |
| `fixtures-and-projects.md` | 认证 fixture、数据 fixture、多环境项目、组合 |
| `selector-strategies.md` | 定位符决策树、`getByRole` 示例、稳定性评分 |
| `auth-patterns.md` | storageState、多角色、token 播种、会话过期 |
| `multi-site-architecture.md` | 共享 fixture、每个站点的配置、单仓库模式 |
| `network-and-mocking.md` | `page.route`、`route.fetch`、HAR、WebSocket、条件路由 |
| `debugging-and-triage.md` | Trace viewer、错误率测试的排查、重试、工件 |
| `ci-recipes.md` | 报告器、分片 + 合并、`--only-changed`、浏览器缓存、Docker |
