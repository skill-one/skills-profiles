# 端到端测试模式

构建可靠、快速且可维护的端到端测试套件，为快速发布代码提供信心，并在用户发现问题之前捕获回归问题。

## 何时使用此技能

- 实现端到端测试自动化
- 调试不稳定或不可靠的测试
- 测试关键用户工作流
- 设置 CI/CD 测试流水线
- 跨多个浏览器进行测试
- 验证可访问性要求
- 测试响应式设计
- 建立端到端测试标准

## 核心概念

### 1. 端到端测试基础

**使用端到端测试测试的内容：**

- 关键用户旅程（登录、结账、注册）
- 复杂交互（拖放、多步骤表单）
- 跨浏览器兼容性
- 真实 API 集成
- 认证流程

**不应使用端到端测试测试的内容：**

- 单元级逻辑（使用单元测试）
- API 合约（使用集成测试）
- 边缘情况（太慢）
- 内部实现细节

### 2. 测试理念

**测试金字塔：**

```
        /\
       /E2E\         ← 少量，专注于关键路径
      /─────\
     /Integr\        ← 更多，测试组件交互
    /────────\
   /Unit Tests\      ← 很多，快速，隔离
  /────────────\
```

**最佳实践：**

- 测试用户行为，而不是实现细节
- 保持测试独立
- 使测试可确定
- 优化速度
- 使用 data-testid，而不是 CSS 选择器

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **使用数据属性**：`data-testid` 或 `data-cy` 用于稳定的选取器
2. **避免易碎的选择器**：不要依赖 CSS 类或 DOM 结构
3. **测试用户行为**：点击、输入、查看 - 而不是实现细节
4. **保持测试独立**：每个测试应在隔离环境中运行
5. **清理测试数据**：在每个测试中创建和销毁测试数据
6. **使用页面对象**：封装页面逻辑
7. **有意义的断言**：检查实际用户可见行为
8. **优化速度**：可能时模拟，并行执行

```typescript
// ❌ 坏选择器
cy.get(".btn.btn-primary.submit-button").click();
cy.get("div > form > div:nth-child(2) > input").type("text");

// ✅ 好选择器
cy.getByRole("button", { name: "Submit" }).click();
cy.getByLabel("Email address").type("user@example.com");
cy.get('[data-testid="email-input"]').type("user@example.com");
```

## 常见陷阱

- **不稳定测试**：使用适当的等待，而不是固定超时
- **慢速测试**：模拟外部 API，使用并行执行
- **过度测试**：不要用端到端测试每个边缘情况
- **耦合测试**：测试不应依赖于彼此
- **差选择器**：避免 CSS 类和 nth-child
- **无清理**：每次测试后清理测试数据
- **测试实现**：测试用户行为，而不是内部实现

## 调试失败的测试

```typescript
// Playwright 调试
// 1. 以带头模式运行
npx playwright test --headed

// 2. 以调试模式运行
npx playwright test --debug

// 3. 使用跟踪查看器
await page.screenshot({ path: 'screenshot.png' });
await page.video()?.saveAs('video.webm');

// 4. 添加 test.step 以获得更好的报告
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });

    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});

// 5. 检查页面状态
await page.pause();  // 暂停执行，打开检查器
```
