# Web 应用测试

这项技能能够使用 Playwright 自动化工具对本地 Web 应用进行全面测试和调试。

如果可能的话，你应该使用 Playwright MCP 服务器来执行工作。如果 MCP 服务器不可用，你可以在安装了 Playwright 的本地 Node.js 环境中运行代码。

## 使用场景

当你需要执行以下操作时，请使用这项技能：

- 在真实浏览器中测试前端功能
- 验证 UI 行为和交互
- 调试 Web 应用问题
- 捕获截图用于文档或调试
- 检查浏览器控制台日志
- 验证表单提交和用户流程
- 检查跨视口的响应式设计

## 前置条件

- 系统上安装了 Node.js
- 本地运行 Web 应用（或可访问的 URL）
- 如果未安装，Playwright 将自动安装

## 核心功能

### 1. 浏览器自动化

- 导航到 URL
- 点击按钮和链接
- 填写表单字段
- 选择下拉菜单
- 处理对话框和警告

### 2. 验证

- 断言元素存在
- 验证文本内容
- 检查元素可见性
- 验证 URL
- 测试响应式行为

### 3. 调试

- 捕获截图
- 查看控制台日志
- 检查网络请求
- 调试失败测试

## 使用示例

### 示例 1：基本导航测试

```javascript
// 导航到页面并验证标题
await page.goto("http://localhost:3000");
const title = await page.title();
console.log("页面标题:", title);
```

### 示例 2：表单交互

```javascript
// 填写并提交表单
await page.fill("#username", "testuser");
await page.fill("#password", "password123");
await page.click('button[type="submit"]');
await page.waitForURL("**/dashboard");
```

### 示例 3：截图捕获

```javascript
// 捕获截图用于调试
await page.screenshot({ path: "debug.png", fullPage: true });
```

## 指导原则

1. **始终验证应用正在运行** - 在运行测试前检查本地服务器是否可访问
2. **使用显式等待** - 在交互前等待元素或导航完成
3. **失败时捕获截图** - 捕获截图以帮助调试问题
4. **清理资源** - 完成后始终关闭浏览器
5. **优雅处理超时** - 为慢操作设置合理的超时
6. **逐步测试** - 先从简单交互开始，再测试复杂流程
7. **明智使用选择器** - 优先使用 data-testid 或基于角色的选择器，而非 CSS 类

## 常见模式

### 模式：等待元素

```javascript
await page.waitForSelector("#element-id", { state: "visible" });
```

### 模式：检查元素是否存在

```javascript
const exists = (await page.locator("#element-id").count()) > 0;
```

### 模式：获取控制台日志

```javascript
page.on("console", (msg) => console.log("浏览器日志:", msg.text()));
```

### 模式：处理错误

```javascript
try {
  await page.click("#button");
} catch (error) {
  await page.screenshot({ path: "error.png" });
  throw error;
}
```

## 限制

- 需要 Node.js 环境
- 无法测试原生移动应用（请使用 React Native Testing Library）
- 可能对复杂的认证流程存在问题
- 一些现代框架可能需要特定配置

## 辅助函数

一些辅助函数在 [`test-helper.js`](./assets/test-helper.js) 中可用，用于简化等待元素、捕获截图和处理错误等常见任务。你可以在测试中导入和使用这些函数，以提高可读性和可维护性。
