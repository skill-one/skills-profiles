# 前端修改的端到端行为验证

## 核心原则：测试产品行为而非 UI 状态

**关键**：测试必须验证产品功能是否正常工作，而不仅仅是 UI 元素是否渲染。

### 不应测试的内容（UI 状态）：

- ❌ "点击后下拉菜单打开"
- ❌ "点击按钮后模态框出现"
- ❌ "请求期间显示加载动画"
- ❌ "表单字段可见"
- ❌ "侧边栏折叠"

### 应测试的内容（产品行为）：

- ✅ "选择 LLM 提供商配置将代理设置为使用该提供商"
- ✅ "创建新代理后持久化并显示在代理列表中"
- ✅ "带参数运行工具返回预期输出"
- ✅ "聊天消息正确流式传输并保持对话上下文"
- ✅ "工作流执行按正确顺序触发工具"

## BDD 结构（必填）

**每个 E2E 规范必须遵循与 MSW 测试相同的 BDD 结构。** 在 `packages/playground` 中，`e2e-bdd/test-needs-when-describe` 强制执行此结构。

结构恰好有三个级别：

1. **外层 `test.describe`** = 待测单元（每个文件对应一个页面或功能）。
2. **内层 `test.describe('when …')`** = 恰好一个前置条件。标题必须以 `when` 开头。
3. **每个 `test`** = 恰好一个可观察结果。

```ts
import { test, expect } from '@playwright/test';
import { resetStorage } from '../__utils__/reset-storage';

test.describe('Tools list page', () => {
  // 待测单元
  test.afterEach(async () => {
    await resetStorage();
  });

  test.describe('when a registered tool is clicked', () => {
    // 恰好一个前置条件（以 "when" 开头）
    test('navigates to that tool detail page', async ({ page }) => {
      // 恰好一个结果
      await page.goto('/tools');
      await page.locator('text=Get current weather for a location').click();
      await expect(page).toHaveURL(/\/tools\/weatherInfo$/);
    });

    test('shows the tool name as the page heading', async ({ page }) => {
      // 恰好一个结果
      await page.goto('/tools');
      await page.locator('text=Get current weather for a location').click();
      await expect(page.locator('h2')).toHaveText('weatherInfo');
    });
  });
});
```

规则：

- 每个文件对应一个外层 `test.describe` 命名待测单元。
- 每个叶级 `test` 都应位于 `test.describe('when …')` 前置条件组内。**不允许顶层扁平 `test()`。**
- 将多断言 `test()` 仅在断言代表**不同结果**的地方拆分；将紧密耦合的断言（证明单个结果）保留在一起。**永不丢弃断言。**
- 将 `beforeEach`/`afterEach` 放在需要它们的**最窄 `describe` 范围**内。

## 前置条件

需要 Playwright MCP 服务器。如果 `browser_navigate` 工具不可用，请指示用户添加它：

```sh
claude mcp add playwright -- npx @playwright/mcp@latest
```

## 第一步：理解功能意图

在编写任何测试之前，回答以下问题：

1. **此功能解决了什么用户问题？**
2. **功能正常工作时预期结果是什么？**
3. **系统中有哪些数据流？**（用户输入 → API → 状态 → UI）
4. **页面重新加载后应保留什么？**
5. **此操作应产生哪些下游效果？**

将这些问题作为注释记录在测试文件中。

## 第二步：构建和启动

```sh
pnpm build:cli
cd packages/playground/e2e/kitchen-sink && pnpm dev
```

验证服务器：http://localhost:4111

## 第三步：将功能映射到行为测试

### 功能到测试映射指南

| 功能类别           | 应测试的内容                                      | 示例断言                                            |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------------ |
| **代理配置**    | 配置更改影响代理行为                          | 发送消息 → 验证响应使用所选模型           |
| **LLM 提供商选择** | 选定的提供商在请求中使用             | 拦截 API 调用 → 验证请求负载中的提供商      |
| **工具执行**         | 工具带正确参数运行并返回结果    | 执行工具 → 验证输出匹配预期转换            |
| **工作流执行**     | 步骤按顺序执行，步骤间数据流动  | 运行工作流 → 验证每个步骤的输出为下一步提供输入     |
| **聊天/流式传输**         | 消息持久化，上下文跨回合保持 | 多回合对话 → 验证上下文感知           |
| **MCP 服务器工具**       | 服务器工具可调用并返回数据         | 调用 MCP 工具 → 验证响应结构和内容        |
| **内存/持久化**     | 数据在页面重新加载后仍然存在                         | 创建项目 → 重新加载 → 验证项目存在                    |
| **错误处理**         | 错误正确显示给用户                  | 触发错误条件 → 验证错误消息 + 恢复    |

## 第四步：编写以行为为中心的测试

### 测试结构模板

```ts
import { test, expect, Page } from '@playwright/test';
import { resetStorage } from '../__utils__/reset-storage';
import { selectFixture } from '../__utils__/select-fixture';
import { nanoid } from 'nanoid';

/**
 * 功能：[功能名称]
 * 用户故事：作为一个用户，我想[动作]以便[结果]
 * 待测行为：[正在验证的具体行为]
 */

test.describe('[功能名称] - 行为测试', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    const context = await browser.newContext();
    page = await context.newPage();
  });

  test.afterEach(async () => {
    await resetStorage(page);
  });

  test.describe('when [这些结果的单一前置条件]', () => {
    test('[描述单一可观察结果的动词]', async () => {
      // 准备：设置前置条件
      // - 导航到功能
      // - 配置任何所需状态
      // 行动：执行触发行为的用户操作
      // 断言：验证结果，而非 UI 状态
      // - 检查数据持久化
      // - 验证下游效果
      // - 确认 API 调用是否正确
    });
  });
});
```

### 行为测试模式

#### 模式 1：配置影响行为

```ts
test.describe('when a different LLM provider is selected', () => {
  test('uses that provider for agent responses', async () => {
    // 准备
    await page.goto('/agents/my-agent/chat');

    // 拦截 API 以验证提供商
    let capturedProvider: string | null = null;
    await page.route('**/api/chat', route => {
      const body = JSON.parse(route.request().postData() || '{}');
      capturedProvider = body.provider;
      route.continue();
    });

    // 行动：选择不同的提供商
    await page.getByTestId('provider-selector').click();
    await page.getByRole('option', { name: 'OpenAI' }).click();

    // 发送消息以触发代理
    await page.getByTestId('chat-input').fill('Hello');
    await page.getByTestId('send-button').click();

    // 断言：验证选定的提供商被使用
    await expect.poll(() => capturedProvider).toBe('openai');
  });
});
```

#### 模式 2：数据持久化

```ts
test.describe('when a new agent is created', () => {
  test('persists after page reload', async () => {
    // 准备
    await page.goto('/agents');
    const agentName = `Test Agent ${nanoid()}`;

    // 行动：创建新代理
    await page.getByTestId('create-agent-button').click();
    await page.getByTestId('agent-name-input').fill(agentName);
    await page.getByTestId('save-agent-button').click();

    // 等待创建完成
    await expect(page.getByText(agentName)).toBeVisible();

    // 断言：验证持久化
    await page.reload();
    await expect(page.getByText(agentName)).toBeVisible({ timeout: 10000 });
  });
});
```

#### 模式 3：工具执行产生正确输出

```ts
test.describe('when the weather tool is executed with a city', () => {
  test('returns formatted weather data for that city', async () => {
    // 准备
    await selectFixture(page, 'weather-success');
    await page.goto('/tools/weather-tool');

    // 行动：带参数执行工具
    await page.getByTestId('param-city').fill('San Francisco');
    await page.getByTestId('execute-tool-button').click();

    // 断言：验证输出内容，而不仅仅是输出出现
    const output = page.getByTestId('tool-output');
    await expect(output).toContainText('temperature');
    await expect(output).toContainText('San Francisco');

    // 如果适用，验证结构化数据
    const outputText = await output.textContent();
    const outputData = JSON.parse(outputText || '{}');
    expect(outputData).toHaveProperty('temperature');
    expect(outputData).toHaveProperty('conditions');
  });
});
```

#### 模式 4：工作流步骤链

```ts
test.describe('when a multi-step workflow is run', () => {
  test('passes data between steps correctly', async () => {
    // 准备
    await selectFixture(page, 'workflow-multi-step');
    const sessionId = nanoid();
    await page.goto(`/workflows/data-pipeline?session=${sessionId}`);

    // 行动：触发工作流执行
    await page.getByTestId('workflow-input').fill('test input data');
    await page.getByTestId('run-workflow-button').click();

    // 断言：验证每个步骤正确接收前一个步骤的输入
    // 等待完成
    await expect(page.getByTestId('workflow-status')).toHaveText('completed', { timeout: 30000 });

    // 检查步骤输出显示数据转换链
    const step1Output = await page.getByTestId('step-1-output').textContent();
    const step2Output = await page.getByTestId('step-2-output').textContent();

    // 验证步骤 2 接收步骤 1 的输出作为输入
    expect(step2Output).toContain(step1Output);
  });
});
```

#### 模式 5：带上下文的流式聊天

```ts
test.describe('when a multi-turn conversation is held', () => {
  test('maintains conversation context across messages', async () => {
    // 准备
    await selectFixture(page, 'contextual-chat');
    const chatId = nanoid();
    await page.goto(`/agents/assistant/chat/${chatId}`);

    // 行动：多回合对话
    await page.getByTestId('chat-input').fill('My name is Alice');
    await page.getByTestId('send-button').click();
    await expect(page.getByTestId('assistant-message').last()).toBeVisible({ timeout: 20000 });

    await page.getByTestId('chat-input').fill('What is my name?');
    await page.getByTestId('send-button').click();

    // 断言：验证上下文被保持
    const response = page.getByTestId('assistant-message').last();
    await expect(response).toContainText('Alice', { timeout: 20000 });
  });
});
```

#### 模式 6：错误恢复

```ts
test.describe('when the API fails during tool execution', () => {
  test('shows an actionable error and allows a successful retry', async () => {
    // 准备：设置失败 fixture
    await selectFixture(page, 'api-failure');
    await page.goto('/tools/flaky-tool');

    // 行动：触发错误
    await page.getByTestId('execute-tool-button').click();

    // 断言：显示可操作的错误并允许成功重试
    await expect(page.getByTestId('error-message')).toContainText('failed');
    await expect(page.getByTestId('retry-button')).toBeVisible();

    // 切换到成功 fixture 并重试
    await selectFixture(page, 'api-success');
    await page.getByTestId('retry-button').click();

    // 验证恢复是否成功
    await expect(page.getByTestId('tool-output')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('error-message')).not.toBeVisible();
  });
});
```

## 第五步：更新现有测试

当测试文件已存在时：

1. **阅读现有测试**以理解当前覆盖范围
2. **识别测试是 UI 聚焦还是行为聚焦**
3. **重构 UI 聚焦测试**以验证行为：

### 重构示例

**之前（UI 聚焦）：**

```ts
test('dropdown opens when clicked', async () => {
  await page.getByTestId('model-dropdown').click();
  await expect(page.getByRole('listbox')).toBeVisible();
});
```

**之后（行为聚焦 + BDD 嵌套）：**

```ts
test.describe('when a model is selected from the dropdown', () => {
  test('updates and persists the agent configuration', async () => {
    // 打开下拉菜单并选择模型
    await page.getByTestId('model-dropdown').click();
    await page.getByRole('option', { name: 'GPT-4' }).click();

    // 验证选择持久化并影响行为
    await page.reload();
    await expect(page.getByTestId('model-dropdown')).toHaveText('GPT-4');

    // 可选：验证模型在实际请求中使用
    // （通过请求拦截或检查响应元数据）
  });
});
```

## 第六步：厨房水槽 Fixtures 用于行为测试

Fixtures 应代表**真实场景**，而不仅仅是模拟数据：

### Fixture 命名约定

```
<功能>-<场景>.fixture.ts

示例：
- agent-with-tools.fixture.ts
- chat-multi-turn-context.fixture.ts
- workflow-parallel-execution.fixture.ts
- tool-validation-error.fixture.ts
- mcp-server-timeout.fixture.ts
```

### Fixture 内容要求

每个 fixture 必须定义：

1. **场景描述**（它使哪些行为可被测试）
2. **预期结果**（应通过哪些断言）
3. **覆盖的边缘情况**（错误状态、空状态等）

```ts
// fixtures/agent-provider-switch.fixture.ts
export const agentProviderSwitch = {
  name: 'agent-provider-switch',
  description: 'Tests that switching LLM providers changes agent behavior',

  // 不同提供商的模拟响应
  responses: {
    openai: { content: 'Response from OpenAI', model: 'gpt-4' },
    anthropic: { content: 'Response from Anthropic', model: 'claude-3' },
  },

  expectedBehavior: {
    // 当切换提供商时，后续消息使用新提供商
    providerSwitchAffectsNextMessage: true,
    // 提供商选择跨页面重新加载后仍然存在
    providerPersistsOnReload: true,
  },
};
```

## 第七步：运行和验证

```sh
cd packages/playground && pnpm test:e2e
```

### 测试质量检查清单

在考虑测试完成之前，验证：

- [ ] 每个测试都有清晰的用户故事注释
- [ ] 一个外层 `test.describe` 命名待测单元
- [ ] 每个 `test` 都嵌套在 `test.describe('when …')` 前置条件块内（没有顶层扁平 `test()`）
- [ ] 每个 `test` 恰好断言一个可观察结果
- [ ] 测试验证结果，而非中间 UI 状态
- [ ] 测试在功能损坏时会失败（而不仅仅是 UI 变化）
- [ ] 验证通过 `page.reload()`（在适用情况下）
- [ ] 覆盖错误场景
- [ ] 测试为异步操作使用适当的超时
- [ ] Fixtures 代表真实的用例场景

## 快速参考

| 步骤      | 命令/操作                                        |
| --------- | ----------------------------------------------------- |
| 构建     | `pnpm build:cli`                                      |
| 启动     | `cd packages/playground/e2e/kitchen-sink && pnpm dev` |
| 应用 URL   | http://localhost:4111                                 |
| 路由    | `@packages/playground/src/App.tsx`                    |
| 运行测试 | `cd packages/playground && pnpm test:e2e`             |
| 测试目录  | `packages/playground/e2e/tests/`                      |
| Fixtures  | `packages/playground/e2e/kitchen-sink/fixtures/`      |

## 应避免的反模式

| ❌ 不要                                              | ✅ 而应这样做                                                |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| 测试模态框打开                                 | 测试模态框操作完成并持久化                |
| 测试按钮可点击                         | 测试点击按钮产生预期结果           |
| 测试加载动画出现                          | 测试加载的数据是否正确                             |
| 测试表单验证消息显示                    | 测试无效表单无法提交 AND 有效表单成功提交 |
| 测试下拉菜单有选项                             | 测试选择选项改变系统行为           |
| 测试侧边栏导航工作                         | 测试导航的页面具有正确的数据/功能      |
| 断言元素可见                             | 断言元素包含预期数据/状态                  |
| 顶层扁平 `test()` 无前置条件 describe | 每个测试都嵌套在 `test.describe('when …')` 块内       |
| 一个 `test()` 断言多个不相关的结果     | 每个测试只对应一个可观察结果                          |
