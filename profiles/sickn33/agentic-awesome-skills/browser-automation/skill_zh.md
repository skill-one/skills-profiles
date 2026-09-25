# 浏览器自动化

使用用户已选择或项目中安装的浏览器工具。Playwright、Puppeteer 和 Selenium 具有不同的集成方式；应根据实际需求选择，而不是依赖不支持的成功率声明。由 AAS 维护者于 2026-09-05 修改：删除未经验证的比较，绕过默认设置，澄清等待和证据限制。

将您控制的应用程序的测试与与现有经过身份验证的浏览器的交互分开。不要用一个新的未经过身份验证的会话来替换后者，也不要提取凭证来使自动化测试工作。

## 详细指南

在执行此技能之前，请阅读 [详细指南](references/detailed-guide.md)。它保留了完整的过程和参考材料。将其安全性、先决条件和验证要求视为强制性。对于专注的工作，加载相关部分；对于端到端工作，请完整阅读指南。

## Playwright 测试示例
"""
import { test, expect } from '@playwright/test';

// 每个测试都在隔离的浏览器上下文中运行
test('用户可以将商品添加到购物车', async ({ page }) => {
  // 新的上下文 - 没有Cookie，没有来自其他测试的存储
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add to Cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});

test('用户可以从购物车中移除商品', async ({ page }) => {
  // 完全隔离 - 购物车为空
  await page.goto('/cart');
  await expect(page.getByText('Your cart is empty')).toBeVisible();
});
"""

## 良好示例（面向用户）
"""
// 通过角色 - 最佳选择
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('link', { name: 'Sign up' }).click();
await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
await page.getByRole('textbox', { name: 'Search' }).fill('query');

// 通过文本内容
await expect(page.getByText('Welcome back')).toBeVisible();
await page.getByText(/Order #\d+/).click();  // 支持正则表达式

// 通过标签（表单）
await page.getByLabel('Email address').fill('user@example.com');
await page.getByLabel('Password').fill('secret');

// 通过占位符
await page.getByPlaceholder('Search...').fill('query');

// 通过测试 ID（当没有面向用户的选项可用时）
await page.getByTestId('submit-button').click();
"""

## 不好示例（易碎）
"""
// 不要 - 与结构绑定的 CSS 选择器
await page.locator('.btn-primary.submit-form').click();
await page.locator('#header > div > button:nth-child(2)').click();

// 不要 - 与结构绑定的 XPath
await page.locator('//div[@class="form"]/button[1]').click();

// 不要 - 自动生成的选择器
await page.locator('[data-v-12345]').click();
"""

## 何时使用

用于验证真实的浏览器工作流程、诊断 UI 定时失败或收集明确授权的页面数据。在选择定位器或操作之前，请检查当前页面和可用的工具 API。

## 工作示例和先决条件

输入：从本地 Web 应用程序导出经过审查的 JSON 文件。确保应用程序正在运行，预期的浏览器可用，并有一个合成表单值。观察导出控件，在点击之前注册下载事件，检查下载的 JSON 并确认修改输入会使旧预览失效。预期：一个包含经过审查的值的文件，没有隐藏的项目数据或网络提交。

在任务包含可用性时，使用显式的桌面/移动视口并检查键盘/焦点行为。锁定的桌面会留下交互验证待定；单元测试和头less探测是独立的证据。

## 限制

- 自动等待检查可操作性，而不是业务正确性或后端成功写入。
- 截图、HTML、跟踪和 auth-state 文件可能包含私人信息；仅捕获授权范围。
- 重试读取可能是安全的；重试结账、删除或发送消息可能会重复副作用。在重复之前验证状态。
- 资源阻塞和模拟响应会改变环境，无法建立未经修改的生产行为。
- 示例需要项目的导入、运行器和 fixture 路由；此技能不会安装任何浏览器、服务或账户。
