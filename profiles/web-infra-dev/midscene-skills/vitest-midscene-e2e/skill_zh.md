# Vitest Midscene E2E

## 模块

| 模块 | 角色 |
|------|------|
| **Vitest** | TypeScript 测试框架。提供 `describe`/`it`/`expect`/hooks 用于测试组织、断言和生命周期。 |
| **Midscene** | AI 驱动的 UI 自动化。通过自然语言与 UI 元素交互 — 无脆弱的选择器。核心 API：`aiAct`。 |

支持的平台：

- **Web** — `WebTest` (Playwright Chromium)：`ctx.agent` + `ctx.page`
- **Android** — `AndroidTest` (ADB + scrcpy)：仅 `ctx.agent`
- **iOS** — `IOSTest` (WebDriverAgent)：仅 `ctx.agent`

## 工作流程

### 第 1 步：克隆基础模板并确保项目就绪

```bash
bash scripts/clone-boilerplate.sh
```

位于 `~/.midscene/boilerplate/vitest-all-platforms-demo/` 的基础模板是项目结构、配置、平台上下文类和测试约定的权威参考。将当前项目与它进行比较。如果缺少任何内容，请询问用户他们需要哪些平台（Web / Android / iOS），然后使用基础模板作为目标状态来补充缺失的部分。仅包含请求的平台文件。不要覆盖现有的配置或文件。如果不存在，从基础模板复制 `.env.example` 为 `.env`，并提示用户填写环境变量。

### 第 2 步：编写测试前，先阅读下文的 **Midscene Agent API** 部分

它包含使用 `aiAct` 的强制性规则 — 所有 UI 操作的主要 API。不要跳过这一步。

### 第 3 步：创建、更新或运行测试

使用基础模板的 `e2e/` 目录和 `src/context/` 作为模式和约定的参考。在运行测试前，确保依赖已安装且 `.env` 已配置。在调试失败时，请查看 [troubleshooting.md](./references/troubleshooting.md)。

## Midscene Agent API

`ctx.agent` 是一个平台特定的代理实例。所有方法都返回 Promise。

- **Web**：来自 `@midscene/web/playwright` 的 `PlaywrightAgent`
- **Android**：来自 `@midscene/android` 的 `AndroidAgent`
- **iOS**：来自 `@midscene/ios` 的 `IOSAgent`

这三个代理共享以下相同的 AI 方法。

### 强制规则：使用 `aiAct` 处理用户描述的步骤

> **当用户用自然语言描述 UI 操作或状态确认时，你必须使用 `aiAct` 来实现它。** 不要将用户指令分解为 `aiTap`/`aiInput`/`aiAssert` 或其他细粒度 API。直接将用户的意图传递给 `aiAct`，让 Midscene 的 AI 处理规划和执行。

```typescript
// 用户说：在搜索框中输入 iPhone 并点击搜索

// 错误 — 手动分解为细粒度 API
await ctx.agent.aiInput('search box', { value: 'iPhone' });
await ctx.agent.aiTap('search button');

// 正确 — 直接将意图传递给 aiAct
await ctx.agent.aiAct('在搜索框中输入 "iPhone"，然后点击搜索按钮');
```

断言、数据提取和等待也应通过 `aiAct` 进行 — 它处理所有这些。不要单独使用 `aiAssert`、`aiQuery`、`aiWaitFor`、`aiTap` 或 `aiInput`。

### aiAct(taskPrompt, opt?) — 主要 API

**`aiAct` 是所有 UI 操作和状态确认的主要 API。** 它接受自然语言指令并自主规划和执行多步交互。

```typescript
// UI 操作
await ctx.agent.aiAct('在搜索框中输入 "iPhone"，然后点击搜索按钮');
await ctx.agent.aiAct('将鼠标悬停在右上角的用户头像上');

// 状态确认 / 断言 — 也使用 aiAct
await ctx.agent.aiAct('验证页面显示 "登录成功"');
await ctx.agent.aiAct('验证错误消息可见');
```

### Web 仅限的提示驱动文件上传

当 `aiAct` 提示要求 Midscene 上传文件时，显式传递 `fileChooserAllowedDir`。使用包含该测试用例 fixtures 的最小目录，并在提示中相对于它引用文件。不要使用项目根目录或主目录。将下面的 `./fixtures` 替换为相对于测试进程工作目录的 fixtures 目录。

```typescript
await ctx.agent.aiAct(
  '点击上传按钮并上传 avatar.png',
  { fileChooserAllowedDir: './fixtures' },
);
```

**阶段拆分：** 如果任务提示过长或涵盖多个不同阶段，将其拆分为多个 `aiAct` 调用 — 每个阶段一个。每个阶段应该是自包含的逻辑步骤，所有阶段组合起来必须匹配用户的原始意图。

```typescript
// 错误 — 提示跨越多个页面和过多步骤，AI 可能在中途丢失上下文
await ctx.agent.aiAct('点击顶部导航的设置按钮，进入设置页面，找到个人信息并点击进入，将邮箱改为 "test@example.com"，将电话改为 "13800000000"，点击保存，等待成功');

// 正确 — 按页面/阶段边界拆分，每个阶段保持在一个逻辑上下文中
await ctx.agent.aiAct('点击顶部导航的设置按钮，进入设置页面，找到个人信息并点击进入');
await ctx.agent.aiAct('将邮箱改为 "test@example.com"，将电话改为 "13800000000"，点击保存');
await ctx.agent.aiAct('验证保存成功消息出现');
```

> `aiAction` 已弃用。使用 `aiAct` 或 `ai` 代替。

### 常见错误

- **模糊定位器** — `'button'` 是模糊的；使用 `'页面顶部的蓝色 "提交" 按钮'`
- **弃用的 `aiAction`** — 使用 `aiAct` 代替
- **模糊的多元素目标** — 指定行/位置：`'第一个产品行的删除按钮'`

### 代理配置 — `aiActionContext`

`aiActionContext` 是代理执行的 AI 操作附加的系统提示字符串。用它来定义 AI 的角色和专长。

```typescript
// 通过 setup() 中的 agentOptions 设置
const ctx = WebTest.setup('https://example.com', {
  agentOptions: {
    aiActionContext: '你是一个 Web UI 测试专家。',
  },
});
```

**好的示例：**
- `'你是一个 Web UI 测试专家。'`
- `'你是一个熟悉中文 UI 的 Android 应用测试专家。'`

**坏的示例：**
- `'点击登录按钮。'` — 具体操作属于 `aiAct`，不属于 `aiActionContext`
- `'页面是中文的。'` — 这是页面描述，不是系统提示

### 如何查找更多信息

1. 在 `node_modules/@midscene/web`、`node_modules/@midscene/android` 和 `node_modules/@midscene/ios` 中，找到代理类的类型定义
2. 如果类型不够，跟随 `.d.ts` 文件中的源代码引用，阅读 `node_modules` 中的实现代码
3. 下载 https://midscenejs.com/llms.txt，然后使用 `grep` 搜索你需要的 API 或概念（文件很大，不要全文阅读）
