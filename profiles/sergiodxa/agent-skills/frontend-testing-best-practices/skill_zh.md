# 测试最佳实践

编写有效、可维护的测试指南，提供真实信心。包含6条规则，侧重于优先选择E2E测试、最小化模拟，以及行为测试而非实现测试。

## 核心理念

1. **优先选择E2E测试而非单元测试** - 测试整个系统，而非孤立部分
2. **最小化模拟** - 如果需要复杂模拟，改写E2E测试
3. **测试行为而非实现** - 测试用户所见所做
4. **避免直接测试React组件** - 通过E2E测试组件

## 应用场景

在以下情况参考这些指南：

- 决定编写何种类型的测试
- 编写新的E2E或单元测试
- 审查测试代码
- 重构测试

## 规则概览

### 测试策略（关键）

#### prefer-e2e-tests - @rules/prefer-e2e-tests.md

默认使用E2E测试。仅对纯函数编写单元测试。

```typescript
// E2E测试（推荐）- 测试真实用户流程
test("用户可以下单", async ({ page }) => {
  await createTestingAccount(page, { account_status: "active" });
  await page.goto("/catalog");
  await page.getByRole("heading", { name: "示例商品" }).click();
  await page.getByRole("link", { name: "购买" }).click();
  // ... 完成流程
  await expect(page.getByAltText("感谢")).toBeVisible();
});

// 单元测试 - 仅对纯函数
test("formatCurrency格式化为两位小数", () => {
  expect(formatCurrency(1234.5)).toBe("$1,234.50");
});
```

#### avoid-component-tests - @rules/avoid-component-tests.md

不要单元测试React组件。通过E2E测试或根本不测试。

```typescript
// BAD: 组件单元测试
describe("OrderCard", () => {
  test("渲染金额", () => {
    render(<OrderCard amount={100} />);
    expect(screen.getByText("$100")).toBeInTheDocument();
  });
});

// GOOD: E2E测试自然覆盖组件
test("订单历史显示订单", async ({ page }) => {
  await page.goto("/orders");
  await expect(page.getByText("$100")).toBeVisible();
});
```

#### minimize-mocking - @rules/minimize-mocking.md

保持模拟简单。如果需要3个以上模拟，改写E2E测试。

```typescript
// BAD: 过多模拟 = 编写E2E测试
vi.mock("~/lib/auth");
vi.mock("~/lib/transactions");
vi.mock("~/hooks/useAccount");

// GOOD: 简单MSW模拟用于加载测试
mockServer.use(
  http.get("/api/user", () => HttpResponse.json({ name: "John" })),
);
```

### E2E测试（高优先级）

#### e2e-test-structure - @rules/e2e-test-structure.md

E2E测试放在`e2e/tests/`，而非`frontend/`。

```typescript
// e2e/tests/order.spec.ts
import { test, expect } from "@playwright/test";
import { addAccountBalance, createTestingAccount } from "./utils";

test.describe("订单", () => {
  test.beforeEach(async ({ page, context }) => {
    await createTestingAccount(page, { account_status: "active" });
    let cookies = await context.cookies();
    let account_id = cookies.find((c) => c.name === "account_id").value;
    await addAccountBalance({ account_id, amount: 10000, replaceBalance: true });
  });

  test("使用默认值下单", async ({ page }) => {
    await page.goto("/catalog");
    // ... 用户流程
  });
});
```

#### e2e-selectors - @rules/e2e-selectors.md

使用可访问选择器：role > label > text > testid。

```typescript
// GOOD: 基于角色（推荐）
await page.getByRole("button", { name: "提交" }).click();
await page.getByRole("heading", { name: "仪表盘" });

// GOOD: 基于标签
await page.getByLabel("邮箱").fill("test@example.com");

// OK: 当无可访问选择器时使用测试ID
await expect(page.getByTestId("balance")).toHaveText("$1,234");

// BAD: CSS选择器
await page.locator(".btn-primary").click();
```

### 单元测试（中优先级）

#### unit-test-structure - @rules/unit-test-structure.md

仅对纯函数编写单元测试。与源文件并列存放。

```typescript
// app/utils/format.test.ts
import { describe, test, expect } from "vitest";
import { formatCurrency } from "./format";

describe("formatCurrency", () => {
  test("格式化正数金额", () => {
    expect(formatCurrency(1234.5)).toBe("$1,234.50");
  });

  test("处理零值", () => {
    expect(formatCurrency(0)).toBe("$0.00");
  });
});
```

## 关键文件

- `e2e/tests/` - E2E测试（Playwright）
- `e2e/tests/utils.ts` - E2E测试工具
- `vitest.config.ts` - 单元测试配置
- `vitest.setup.ts` - 带MSW的全局测试设置
- `app/utils/test-utils.ts` - 单元测试工具
