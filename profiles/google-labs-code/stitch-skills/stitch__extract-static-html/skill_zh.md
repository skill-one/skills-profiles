# 提取静态 HTML

从任何 Web 应用中提取一个自包含的静态 HTML 文件。

## 使用哪种策略

在进行下一步之前，你必须要求用户选择要使用的策略。清晰地呈现选项，**推荐 Strategy A 作为首选默认选项**，并为每个选项提供简短的优缺点总结，以帮助他们做出明智的决定。

| | Strategy A (Puppeteer) | Strategy B (Browser Subagent) |
| :--- | :--- | :--- |
| **何时使用** | 应用程序在本地运行，没有认证障碍 | 需要先与页面交互（点击、填写表单） |
| **保真度** | **最高——计算样式已解析** | 高——渲染的 DOM |
| **设置** | **零——无需模拟** | 零——无需模拟 |
| **框架** | **任何** | 任何 |
| **输出** | **写入文件——无大小限制** | 在代理上下文中可能会截断 |

> [!WARNING]
> **检查点——需要用户确认。**
> 你**必须**在继续之前询问用户他们更喜欢哪种策略。
> 呈现上表中的比较表，推荐 Strategy A 作为默认选项，并等待明确的批准。
> 不要自己做决定，或者在用户确认之前不要继续。

***

## Strategy A: Puppeteer 快照（推荐）

启动无头 Chrome，捕获完全渲染的 DOM，并生成一个自包含的 HTML 文件，其中包含所有内联的 CSS 和 base64 编码的图像。适用于**任何框架**——无需 MockPage.jsx。

### 前置条件

- 本地运行应用程序（例如，`npm run dev`）
- Node.js 可用 `puppeteer`（检查：`node -e "require('puppeteer')"`）

### 工作流程

1.  **启动应用程序**并记下端口。

    > [!WARNING]
    > **检查点——需要用户确认。**
    > 启动本地服务器后，你**必须**暂停并要求用户在运行快照脚本或启动浏览器子代理之前确认。
    > 向用户报告 URL 和端口，以便他们可以验证应用程序是否正在运行并且渲染正确。
    > 在用户确认之前，不要继续到快照步骤。

2.  **运行快照脚本**：
    ```bash
    npx tsx <SKILL_DIR>/scripts/snapshot.ts \
      --url http://localhost:5173 \
      --output .stitch/home.html \
      --wait 2000
    ```

3.  **多个页面**——每个路由运行一次：
    ```bash
    npx tsx <SKILL_DIR>/scripts/snapshot.ts \
      --url http://localhost:5173 --output .stitch/home.html --wait 2000
    npx tsx <SKILL_DIR>/scripts/snapshot.ts \
      --url http://localhost:5173/pricing --output .stitch/pricing.html --wait 2000
    npx tsx <SKILL_DIR>/scripts/snapshot.ts \
      --url http://localhost:5173/dashboard --output .stitch/dashboard.html --wait 2000 --html-class dark
    ```

4.  **清理开发服务器**：
    如果为快照提取而启动了本地开发服务器，请确保在提取完成后停止服务器进程或终止后台任务。

### 脚本标志

| 标志 | 默认值 | 描述 |
| :--- | :--- | :--- |
| `--url` | *(必需)* | 捕获的 URL |
| `--output` | *(必需)* | 输出文件路径 |
| `--wait` | `1000` | 网络空闲后的额外等待（毫秒）。对于懒加载应用程序，请增加。 |
| `--viewport` | `1280x800` | 视口大小作为 `WIDTHxHEIGHT` |
| `--html-class` | — | `<html>` 元素的类（例如，`dark`） |
| `--remove-fixed` | `false` | 移除固定/粘性元素（Cookie 横幅、聊天小部件） |
| `--full-height` | `false` | 调整视口为完整滚动高度 |
| `--title` | — | 覆盖页面标题（设置为路由路径，例如 `/dashboard` 或 `/settings/profile`） |
| `--auth-script` | — | 导出默认 `async (page) => void` 函数的 JS/TS 模块的路径，用于认证 |
| `--inline-canvas` | `false` | 将 `<canvas>` 元素（ECharts、Chart.js、D3）转换为 base64 `<img>` 标签 |

### 自动执行的操作

- 从 `document.styleSheets` 捕获所有 CSSOM 规则（保留动态 Vite/Tailwind 开发样式和 CSS-in-JS）
- 将所有 `<link rel="stylesheet">` → `<style>` 块内联
- 将 `<img>` `src` **和 `srcset`** → base64 数据 URI（跳过外部字体）
- 将同源和相对图标字体文件（`@font-face`）作为 base64 数据 URI 内联，以便连字永远不会渲染为 ASCII 文本
- 将 `<source srcset>` URL 作为 base64 内联
- 移除失败的/死掉的 `srcset` 条目，以便浏览器回退到内联的 `src`
- 移除 `<script>` 标签、Vite HMR 开发样式块（`createHotContext`、`import.meta.hot`）和开发覆盖层
- 在内联之前解析相对 CSS `url()` 路径

### 框架说明

| 框架 | 说明 |
| :--- | :--- |
| **React + Vite** | 开箱即用。`--wait 1000`。 |
| **Next.js** | `--wait 3000` 用于 SSR 渲染。URL: `http://localhost:3000`。`/_next/image` 的 `<img srcset>` 自动作为 base64 内联。 |
| **Angular (@angular/cli / v17+)** | 开箱即用，使用 `ng serve`（默认 URL: `http://localhost:4200`）。`--wait 2000` 用于 Angular Material / PrimeNG 动画渲染和懒加载路由。 |
| **Vue / Nuxt** | 开箱即用。 |
| **Svelte / SvelteKit** | 开箱即用。 |
| **Storybook** | 使用故事 URL：`--url http://localhost:6006/?path=/story/...` |
| **SSR (Webpack)** | 可能需要更长的 `--wait`。 |

### 故障排除

| 问题 | 解决方案 |
| :--- | :--- |
| 图像丢失 | 增加 `--wait` |
| 服务器停止后图像显示为损坏 | 验证 `srcset` 是否已内联——检查日志中的 "Inlined N images"。如果 `srcset` URL 失败，它们会自动移除，因此使用 `src`（内联）。 |
| 图标显示为文本 / 无样式字体 | 确保 `snapshot.ts` 从 `document.styleSheets` 捕获 CSSOM（步骤 0），并将同源图标字体（`@font-face`）作为 base64 数据 URI 内联。 |
| Next.js `/_next/image` 未内联 | 确保开发服务器在快照运行时正在运行——脚本从正在运行的服务器获取优化图像。 |
| 暗黑模式未应用 | `--html-class dark` |
| 输出中包含 Cookie 横幅 | `--remove-fixed` |
| 页面需要登录 | 使用 `--auth-script ./auth.ts`（见下文“受认证保护的页面”） |
| 图表/图形显示为空白框 | 使用 `--inline-canvas` 将 `<canvas>` 序列化为 base64 `<img>` |
| `Cannot find module 'puppeteer'` | `npm install -g puppeteer` |

### 受认证保护的页面

对于具有登录保护的应用程序（Vue Router `beforeEach`、React `ProtectedRoute` 等），创建一个在 Puppeteer 会话中运行的简单认证脚本：

```ts
// auth-myapp.ts
import type { Page } from 'puppeteer';

export default async function authenticate(page: Page) {
  // 示例 1：填写并提交登录表单
  await page.type('#username', 'admin');
  await page.type('#password', 'password123');
  await page.click('#login-button');
  await page.waitForNavigation({ waitUntil: 'networkidle2' });

  // 示例 2：直接注入 cookies/localStorage
  // await page.evaluate(() => {
  //   localStorage.setItem('token', 'mock-jwt-token');
  // });

  // 示例 3：通过模块注入调用应用程序自己的登录 API（Vue/Vite）
  // await page.evaluate(() => {
  //   return new Promise((resolve) => {
  //     const script = document.createElement('script');
  //     script.type = 'module';
  //     script.textContent = `
  //       import { useUserStore } from '/src/store/modules/user.ts';
  //       import { fetchLogin } from '/src/api/auth.ts';
  //       const res = await fetchLogin({ userName: 'Admin', password: '123456' });
  //       useUserStore().setToken(res.token, res.refreshToken);
  //       window.dispatchEvent(new CustomEvent('auth-done'));
  //     `;
  //     document.head.appendChild(script);
  //     window.addEventListener('auth-done', () => resolve(true), { once: true });
  //   });
  // });
}
```

然后使用它：
```bash
npx tsx <SKILL_DIR>/scripts/snapshot.ts \
  --url http://localhost:5173/#/dashboard \
  --output .stitch/dashboard.html \
  --auth-script ./auth-myapp.ts \
  --inline-canvas \
  --wait 5000
```

该脚本首先导航到 `--url`（可能会重定向到登录），运行你的认证函数，然后**重新导航**到原始 `--url` 并带有认证的会话。

***

## Strategy B: Browser Subagent Capture

当你需要**与页面交互**（点击按钮、填写表单、切换标签）后再捕获时使用。浏览器子代理给你完全的控制权，但输出可能会因大页面而截断。

### 工作流程

1.  **本地启动应用程序**。
2.  **使用浏览器子代理导航**。
3.  **按需交互**（点击、滚动、填写表单）。
4.  **提取 DOM**：`document.documentElement.outerHTML`

    > [!WARNING]
    > 大页面可能会截断。要处理此问题：
    > - 在提取前移除 `<style>` 标签：`document.querySelectorAll('style').forEach(el => el.remove())`
    > - 静态重新添加样式（Tailwind CDN 链接、源 CSS）
5.  **保存**到文件。

***

## 附录：静态回退（MockPage.jsx）

> [!NOTE]
> 此方法是在应用程序无法本地运行时（依赖项损坏、缺少后端、无绕过认证墙）的**最后手段**。它需要手动将 React 组件展平为单个 JSX 文件。**尽可能使用 Strategy A。**

### 何时使用

- 应用程序完全无法本地运行
- 页面需要认证且没有模拟/绕过
- 你需要一个特定 UI 状态，通过导航无法达到（错误屏幕、空状态）

### 快速参考

```bash
npx tsx <SKILL_DIR>/scripts/extract_inline_html.ts \
  --index-css src/css/App.css \
  --extra-css index.html \
  --outdir .stitch \
  --page src/MockPage.jsx:Page.html:"Page Title"
```

**关键标志**：`--no-tailwind`（非 Tailwind 应用程序）、`--html-class dark`（暗黑模式）、`--css-files`（额外 CSS 文件）。

**自动检测**：Tailwind 配置自动检测。`@apply` 指令自动使用 `<style type="text/tailwindcss">`。

### MockPage.jsx 规则

1. **包含完整布局**——页眉、侧边栏、页脚（首先读取 `App.js`）
2. **展平所有条件**——选择一个状态，移除所有三元运算符和 `&&` 守卫
3. **硬编码所有数据**——用具体值替换 `{variable}`，展开 `.map()` 循环
4. **保留标志**——使用 `<img>` 带本地路径（后处理将内联它们）
5. **移除浮动元素**——Cookie 横幅、聊天小部件、反馈按钮

### 后处理

内联本地图像：
```bash
npx tsx <SKILL_DIR>/scripts/post_process.ts \
  .stitch/Page.html --base-dir <app-directory>
```
