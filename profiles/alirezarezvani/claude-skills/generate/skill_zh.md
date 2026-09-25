# 生成 Playwright 测试

根据用户故事、URL、组件名称或功能描述生成可生产的 Playwright 测试。

## 输入

`$ARGUMENTS` 包含要测试的内容。示例：
- `"用户可以使用邮箱和密码登录"`
- `"结账流程"`
- `"src/components/UserProfile.tsx"`
- `"带筛选功能的搜索页面"`

## 步骤

### 1. 理解目标

解析 `$ARGUMENTS` 以确定：
- **用户故事**：提取要验证的行为
- **组件路径**：读取组件源代码
- **页面/URL**：识别路由及其元素
- **功能名称**：映射到相关应用区域

### 2. 探索代码库

使用 `Explore` 子代理收集上下文：

- 读取 `playwright.config.ts` 中的 `testDir`、`baseURL`、`projects`
- 检查 `testDir` 中的现有测试以查找模式、配置文件和约定
- 如果提供了组件路径，则读取组件以了解其属性、状态和交互
- 检查 `pages/` 中的现有页面对象
- 检查 `fixtures/` 中的现有配置文件
- 检查认证设置（`auth.setup.ts` 或 `storageState` 配置）

### 3. 选择模板

检查此插件中的 `templates/` 目录以查找匹配的模式：

| 如果测试... | 从以下路径加载模板 |
|---|---|
| 登录/认证流程 | `../pw/templates/auth/login.md` |
| CRUD 操作 | `templates/crud/` |
| 结账/支付 | `templates/checkout/` |
| 搜索/筛选 UI | `templates/search/` |
| 表单提交 | `templates/forms/` |
| 仪表板/数据 | `templates/dashboard/` |
| 设置页面 | `templates/settings/` |
| 引导流程 | `templates/onboarding/` |
| API 端点 | `templates/api/` |
| 可访问性 | `templates/accessibility/` |

根据具体应用调整模板 — 将 `{{placeholders}}` 替换为实际选择器、URL 和数据。

### 4. 生成测试

遵循以下规则：

**结构：**
```typescript
import { test, expect } from '@playwright/test';
// 如果项目使用自定义配置文件，则导入它们

test.describe('功能名称', () => {
  // 分组相关行为

  test('应该 <预期行为>', async ({ page }) => {
    // 准备：导航、设置状态
    // 执行：执行用户操作
    // 断言：验证结果
  });
});
```

**定位器优先级**（使用第一个有效的）：
1. `getByRole()` — 按钮、链接、标题、表单元素
2. `getByLabel()` — 带标签的表单字段
3. `getByText()` — 非交互式文本内容
4. `getByPlaceholder()` — 带占位符文本的输入
5. `getByTestId()` — 当语义选项不可用时

**断言** — 始终以 Web 优先：
```typescript
// 好 — 自动重试
await expect(page.getByRole('heading')).toBeVisible();
await expect(page.getByRole('alert')).toHaveText('成功');

// 不好 — 无重试
const text = await page.textContent('.msg');
expect(text).toBe('成功');
```

**永远不要使用：**
- `page.waitForTimeout()`
- `page.$(selector)` 或 `page.$$(selector)`
- 除非绝对必要，否则使用裸 CSS 选择器
- `page.evaluate()` 用于定位器可以完成的事情

**始终包含：**
- 描述性测试名称，解释行为
- 沿着快乐路径包含错误/边缘情况测试
- 每个 Playwright 调用使用 `await`
- `baseURL`-相对导航（`page.goto('/')` 而不是 `page.goto('http://...')`）

### 5. 匹配项目约定

- 如果项目使用 TypeScript → 生成 `.spec.ts`
- 如果项目使用 JavaScript → 生成 `.spec.js` 并使用 `require()` 导入
- 如果项目有页面对象 → 使用它们而不是内联定位器
- 如果项目有自定义配置文件 → 导入并使用它们
- 如果项目有测试数据目录 → 在那里创建测试数据文件

### 6. 生成支持文件（如果需要）

- **页面对象**：如果测试在一个页面上触及 5+ 个唯一定位器，则创建页面对象
- **配置文件**：如果测试需要共享设置（认证、数据），则创建或扩展配置文件
- **测试数据**：如果测试使用结构化数据，则创建 JSON 文件在 `test-data/`

### 7. 验证

运行生成的测试：

```bash
npx playwright test <generated-file> --reporter=list
```

如果失败：
1. 读取错误
2. 修复测试（不是应用）
3. 再次运行
4. 如果是应用问题，向用户报告

## 输出

- 生成的测试文件路径
- 创建的任何支持文件（页面对象、配置文件、数据）
- 测试运行结果
- 覆盖率说明：现在测试了哪些行为
