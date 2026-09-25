# 控制界面

使用本地浏览器自动化来验证界面行为并提供证据。首先重用存储库自带的 Playwright、浏览器或 Electron 执行框架（如果存在）；否则围绕应用的开发服务器或 Chromium 调试端口组装一个临时的本地执行框架。

## 用途

- 复现依赖于真实浏览器焦点、键盘输入、滚动、调整大小或渲染的界面错误。
- 使用截图和快照验证视觉或可访问性变更。
- 在发布前检查本地网页、IDE 或 Electron 行为。
- 捕获控制台日志、网络日志、CPU 分析、跟踪或堆快照。
- 为 `verify-this` 创建前后证据。

## 设置模式

1. 使用存储库文档中记录的开发命令在本地启动应用。
2. 发现现有的本地执行框架：Playwright 测试、Cypress 规范、Storybook、浏览器脚本、Electron 启动脚本或快照工具。
3. 对于网页应用，使用现有的浏览器工具连接到本地 URL。
4. 对于 Electron/Chromium，在支持时启用远程调试端口。
5. 通过稳定的应用标记选择正确的页面，而不仅仅是根据标签顺序。
6. 优先使用可访问性角色、标签和稳定的 `data-*` 选择器，而不是坐标。

## 通用网页执行框架

尽可能使用存储库安装的浏览器工具。如果存储库已有 Playwright，一个最小的单次探测看起来像：

```javascript
import { chromium } from "playwright";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto("http://127.0.0.1:<port>");
await page.getByRole("button", { name: /submit/i }).click();
await page.screenshot({ path: "/tmp/ui-harness-after.png", fullPage: true });
await browser.close();
```

除非用户要求，否则不要将 Playwright 作为项目依赖项仅为此探测添加。优先使用现有的开发依赖项或环境中已有的外部浏览器工具。

## 通用 CDP 执行框架

对于 Electron 或使用 `--remote-debugging-port=<port>` 启动的 Chromium 应用，通过 CDP 连接：

```javascript
import { chromium } from "playwright";

const browser = await chromium.connectOverCDP("http://127.0.0.1:<debug-port>");
const pages = browser.contexts().flatMap((context) => context.pages());
let page;
for (const candidate of pages) {
  if (await candidate.locator("<app-root-selector>").count()) {
    page = candidate;
    break;
  }
}

if (!page) {
  console.log(await Promise.all(pages.map(async (p) => ({
    title: await p.title(),
    url: p.url(),
  }))));
  throw new Error("未找到匹配的应用页面");
}

await page.screenshot({ path: "/tmp/ui-harness-cdp.png", fullPage: true });
await browser.close();
```

将 `<app-root-selector>` 替换为当前存储库的稳定标记，例如应用根节点、地标或特定产品的 `data-*` 属性。

## 交互循环

1. 在执行操作前捕获页面快照或截图。
2. 从最新的页面结构中选择目标。
3. 执行一个结构性行为：点击、输入、按键、拖动、滚动、导航或调整大小。
4. 捕获新的快照/截图。
5. 验证预期的状态变更。
6. 当用户要求证据时，保存用于前后比较的工件。

## CDP 功能

仅当高级浏览器 API 不足时使用原始 CDP：

- 性能：CPU 分析、跟踪、绘制闪烁、FPS 计数器、布局偏移检查。
- 内存：堆快照和强制垃圾回收以调查泄漏。
- 网络：请求拦截、限速、禁用缓存、请求/响应日志。
- 渲染：视口变更、配色方案模拟、减少动画、可访问性检查。
- 调试：控制台流式传输、异常捕获、DOM 快照。

## 页面选择

当多个应用窗口/标签共享一个调试端口时：

- 优先使用测试表面的阳性标记，例如应用根选择器。
- 在必要时使用阴性标记以避免选择错误表面。
- 如果没有页面匹配，列出可用的页面标题和 URL 而不是猜测。

## 安全限制

- 导航或结构变更后不要依赖过期的元素引用。
- 除非点击前立即捕获了新的截图，否则避免坐标点击。
- 保持测试数据本地化和可丢弃。
- 除非用户明确同意，否则不要从隐私敏感的工作空间存储截图或堆快照。
- 不要硬编码来自其他存储库的选择器、端口或脚本路径。发现当前存储库的本地应用标记。
- 完成后清理开发服务器、调试会话和临时配置文件。
