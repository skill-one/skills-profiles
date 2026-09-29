---
name: playwright-interactive
description: 通过 `js_repl` 实现浏览器和 Electron 的持续交互，以快速迭代 UI 调试。
---

# Playwright 交互技能

使用持久的 `js_repl` Playwright 会话来调试本地 Web 或 Electron 应用，跨迭代保持相同的句柄活跃，并在不重新启动整个工具链的情况下运行功能测试和视觉测试，除非进程所有权发生变化。

## 前置条件

- 此技能必须启用 `js_repl`。
- 如果 `js_repl` 缺失，请在 `~/.codex/config.toml` 中启用它：

```toml
[features]
js_repl = true
```

- 您也可以使用 `--enable js_repl` 启动新会话（相当于 `-c features.js_repl=true`）。
- 启用 `js_repl` 后，启动新的 Codex 会话以刷新工具列表。
- 目前，请禁用沙盒运行此工作流：使用 `--sandbox danger-full-access`（或 `sandbox_mode=danger-full-access` 的等效配置）启动 Codex。这是 `js_repl` + Playwright 在沙盒内支持仍在完成中的临时要求。
- 从您需要调试的项目目录运行设置。
- 将 `js_repl_reset` 视为恢复工具，而不是常规清理。重置内核会销毁您的 Playwright 句柄。

## 一次性设置

```bash
test -f package.json || npm init -y
npm install playwright
# 仅 Web，用于 headed Chromium 或移动模拟：
# npx playwright install chromium
# 仅 Electron，并且只有当目标工作区是应用程序本身时：
# npm install --save-dev electron
node -e "import('playwright').then(() => console.log('playwright import ok')).catch((error) => { console.error(error); process.exit(1); })"
```

如果您切换到不同的工作区，请在那里重复设置。

## 核心工作流

1. 在测试之前编写简要的 QA 清单：
   - 从三个来源构建清单：用户请求的需求、用户实际实现的可见功能或行为，以及您期望在最终响应中提出的声明。
   - 任何出现在这三个来源中的内容都必须至少映射到一个 QA 检查，然后再进行签收。
   - 列出您打算签收的用户可见声明。
   - 列出每个有意义的用户界面控件、模式开关或实现的交互行为。
   - 列出每个控件或实现的行为可以引起的状态变化或视图变化。
   - 将其用作功能测试和视觉测试的共享覆盖列表。
   - 对于每个声明或控件-状态对，记录预期的功能检查、视觉检查必须发生的特定状态以及您期望捕获的证据。
   - 如果一个需求在视觉上至关重要但主观，将其转换为可观察的 QA 检查，而不是留作隐含。
   - 添加至少 2 个探索性或非预期路径场景，以暴露易碎的行为。
2. 运行一次引导单元格。
3. 在持久的 TTY 会话中启动或确认任何必需的开发服务器。
4. 启动正确的运行时并重复使用相同的 Playwright 句柄。
5. 每次代码更改后，对于仅渲染器更改，重新加载；对于主进程/启动更改，重新启动。
6. 使用正常用户输入运行功能测试。
7. 运行单独的视觉测试。
8. 验证视口适配并捕获支持您声明的所需屏幕截图。
9. 只有在任务实际完成后才清理 Playwright 会话。

## 引导（运行一次）

```javascript
var chromium;
var electronLauncher;
var browser;
var context;
var page;
var mobileContext;
var mobilePage;
var electronApp;
var appWindow;

try {
  ({ chromium, _electron: electronLauncher } = await import("playwright"));
  console.log("Playwright loaded");
} catch (error) {
  throw new Error(
    `Could not load playwright from the current js_repl cwd. Run the setup commands from this workspace first. Original error: ${error}`
  );
}
```

绑定规则：

- 使用 `var` 为共享的顶层 Playwright 句柄，因为后续的 `js_repl` 单元格会重用它们。
- 以下设置单元格有意简短且为成功路径。如果句柄看起来过时，请将该绑定设置为 `undefined` 并重新运行单元格，而不是在所有地方添加恢复逻辑。
- 优先为每个您关心的表面（`page`、`mobilePage`、`appWindow`）使用命名句柄，而不是重复从上下文中发现页面。

共享 Web 辅助函数：

```javascript
var resetWebHandles = function () {
  context = undefined;
  page = undefined;
  mobileContext = undefined;
  mobilePage = undefined;
};

var ensureWebBrowser = async function () {
  if (browser && !browser.isConnected()) {
    browser = undefined;
    resetWebHandles();
  }

  browser ??= await chromium.launch({ headless: false });
  return browser;
};

var reloadWebContexts = async function () {
  for (const currentContext of [context, mobileContext]) {
    if (!currentContext) continue;
    for (const p of currentContext.pages()) {
      await p.reload({ waitUntil: "domcontentloaded" });
    }
  }
  console.log("Reloaded existing web tabs");
};
```

## 选择会话模式

对于 Web 应用，默认使用显式视口并将原生窗口模式视为单独的验证路径。

- 使用显式视口进行常规迭代、断点检查、可重复的屏幕截图、快照差异和模型辅助本地化。这是默认设置，因为它在机器之间稳定且避免了主机窗口管理器的可变性。
- 当您需要确定性高 DPI 行为时，保持显式视口并添加 `deviceScaleFactor`，而不是直接切换到原生窗口模式。
- 使用原生窗口模式（`viewport: null`）进行单独的 headed 路径，当您需要验证启动窗口大小、操作系统级 DPI 行为、浏览器边框交互或可能依赖于主机显示配置的 Bug 时。
- 对于 Electron，始终假设原生窗口行为。Electron 通过 Playwright 以 `noDefaultViewport` 启动，因此将其视为真实的桌面窗口，并在调整任何内容之前检查启动的大小和布局。
- 当签收依赖于布局断点和真实桌面行为时，执行两次路径：首先使用显式视口进行确定性 QA，然后使用原生窗口验证进行最终环境特定检查。
- 将切换模式视为上下文重置。不要重用模拟视口的 `context` 进行原生窗口路径或反之；关闭旧的 `page` 和 `context`，然后为新模式创建一个新的。

## 启动或重用 Web 会话

桌面和移动 Web 会话共享相同的 `browser`、辅助函数和 QA 流。主要区别在于您创建的上下文和页面对。

### 桌面 Web 上下文

将 `TARGET_URL` 设置为您正在调试的应用。对于本地服务器，请优先使用 `127.0.0.1` 而不是 `localhost`。

```javascript
var TARGET_URL = "http://127.0.0.1:3000";

if (page?.isClosed()) page = undefined;

await ensureWebBrowser();
context ??= await browser.newContext({
  viewport: { width: 1600, height: 900 },
});
page ??= await context.newPage();

await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
console.log("Loaded:", await page.title());
```

如果 `context` 或 `page` 过时，请设置 `context = page = undefined` 并重新运行单元格。

### 移动 Web 上下文

如果 `TARGET_URL` 已存在，请重用它；否则，直接设置移动目标。

```javascript
var MOBILE_TARGET_URL = typeof TARGET_URL === "string"
  ? TARGET_URL
  : "http://127.0.0.1:3000";

if (mobilePage?.isClosed()) mobilePage = undefined;

await ensureWebBrowser();
mobileContext ??= await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
});
mobilePage ??= await mobileContext.newPage();

await mobilePage.goto(MOBILE_TARGET_URL, { waitUntil: "domcontentloaded" });
console.log("Loaded mobile:", await mobilePage.title());
```

如果 `mobileContext` 或 `mobilePage` 过时，请设置 `mobileContext = mobilePage = undefined` 并重新运行单元格。

### 原生窗口 Web 路径

```javascript
var TARGET_URL = "http://127.0.0.1:3000";

await ensureWebBrowser();

await page?.close().catch(() => {});
await context?.close().catch(() => {});
page = undefined;
context = undefined;

browser ??= await chromium.launch({ headless: false });
context = await browser.newContext({ viewport: null });
page = await context.newPage();

await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
console.log("Loaded native window:", await page.title());
```

## 启动或重用 Electron 会话

将 `ELECTRON_ENTRY` 设置为当前工作区是 Electron 应用且 `package.json` 指向正确的入口文件时为 `.`。如果您需要直接针对特定的主进程文件，可以使用路径，例如 `./main.js`。

```javascript
var ELECTRON_ENTRY = ".";

if (appWindow?.isClosed()) appWindow = undefined;

if (!appWindow && electronApp) {
  await electronApp.close().catch(() => {});
  electronApp = undefined;
}

electronApp ??= await electronLauncher.launch({
  args: [ELECTRON_ENTRY],
});

appWindow ??= await electronApp.firstWindow();

console.log("Loaded Electron window:", await appWindow.title());
```

如果 `js_repl` 没有从 Electron 应用工作区运行，请在启动时显式传递 `cwd`。

如果应用进程看起来过时，请设置 `electronApp = appWindow = undefined` 并重新运行单元格。

如果您已经有了 Electron 会话，但在主进程、预加载或启动更改后需要一个新的进程，请使用下一节中的重启单元格，而不是重新运行此单元格。

## 在迭代期间重用会话

尽可能保持相同的会话活跃。

Web 渲染器重新加载：

```javascript
await reloadWebContexts();
```

Electron 渲染器仅重新加载：

```javascript
await appWindow.reload({ waitUntil: "domcontentloaded" });
console.log("Reloaded Electron window");
```

Electron 在主进程、预加载或启动更改后重启：

```javascript
await electronApp.close().catch(() => {});
electronApp = undefined;
appWindow = undefined;

electronApp = await electronLauncher.launch({
  args: [ELECTRON_ENTRY],
});

appWindow = await electronApp.firstWindow();
console.log("Relaunched Electron window:", await appWindow.title());
```

如果您的启动需要显式的 `cwd`，请在此处包含相同的 `cwd`。

默认姿态：

- 保持每个 `js_repl` 单元格简短并专注于一次交互爆发。
- 重用现有的顶层绑定（`browser`、`context`、`page`、`electronApp`、`appWindow`），而不是重新声明它们。
- 如果您需要隔离，请在相同的浏览器内创建一个新的页面或新的上下文。
- 对于 Electron，仅使用 `electronApp.evaluate(...)` 进行主进程检查或专门构建的诊断。
- 在原地修复辅助函数错误；除非内核实际上损坏，否则不要重置 REPL。

## 清单

### 会话循环

- 引导 `js_repl` 一次，然后在迭代中保持相同的 Playwright 句柄活跃。
- 从当前工作区启动目标运行时。
- 进行代码更改。
- 使用正确的路径重新加载或重新启动以进行该更改。
- 如果探索发现额外的控件、状态或可见声明，请更新共享 QA 清单。
- 重新运行功能测试。
- 重新运行视觉测试。
- 仅在当前状态是您正在评估的状态后捕获最终工件。

### 重新加载决策

- 渲染器仅更改：重新加载现有的页面或 Electron 窗口。
- 主进程、预加载或启动更改：重新启动 Electron。
- 对进程所有权或启动代码的新不确定性：重新启动而不是猜测。

### 功能测试

- 使用真实用户控件进行签收：键盘、鼠标、点击、触摸或等效的 Playwright 输入 API。
- 验证至少一个端到端的关键流程。
- 确认该流程的可见结果，而不仅仅是内部状态。
- 对于实时或动画密集型应用，在实际交互时间下验证行为。
- 按照共享 QA 清单进行操作，而不是临时的点检查。
- 在签收之前至少覆盖每个明显的可见控件一次，而不仅仅是主快乐路径。
- 对于清单中的可逆控件或状态切换，测试完整周期：初始状态、更改状态并返回初始状态。
- 脚本检查通过后，使用正常输入进行 30-90 秒的短探索性路径，而不是仅遵循预期路径。
- 如果探索性路径揭示新的状态、控件或声明，请将其添加到共享 QA 清单，并在签收之前覆盖它。
- `page.evaluate(...)` 和 `electronApp.evaluate(...)` 可以检查或设置状态，但它们不计为签收输入。

### 视觉测试

- 将视觉测试视为独立于功能测试。
- 使用在测试前定义并更新期间更新的相同共享 QA 清单；不要从不同的隐式列表开始视觉覆盖。
- 重申用户可见声明并明确验证每个声明；不要假设功能通过证明视觉声明。
- 用户可见声明只有在特定状态下被检查时才签收。
- 在滚动之前检查初始视口。
- 确认初始视图明显支持界面的主要声明；如果核心承诺元素在那里不明显，则将其视为 Bug。
- 检查所有必需的可见区域，而不仅仅是主要交互表面。
- 检查清单中已列出的状态和模式，包括至少一个有意义的交互后状态。
- 如果运动或过渡是体验的一部分，除了稳定的端点外，至少检查一个过渡状态。
- 如果标签、覆盖层、注释、指南或高亮旨在跟踪更改的内容，请在相关状态更改后验证这种关系。
- 对于动态或交互相关的视觉效果，检查足够长的时间以判断稳定性、层叠和可读性；不要依赖单个屏幕截图进行签收。
- 对于在加载或交互后可能变得更密集的界面，检查在 QA 期间可以达到的最密集的合理状态，而不仅仅是空、加载或折叠状态。
- 如果产品有定义的最小支持视口或窗口大小，请运行单独的视觉测试；否则，选择一个较小但仍为现实的大小并明确检查它。
- 区分存在与实现：如果预期的可供性在技术上存在但由于对比度弱、遮挡、裁剪或不稳定而不明显，则将其视为视觉失败。
- 如果任何必需的可见区域在您正在评估的状态中被裁剪、切断、遮挡或推到视口之外，即使页面级滚动指标看起来可以接受，也将其视为 Bug。
- 寻找裁剪、溢出、失真、布局不平衡、不一致的间距、对齐问题、难以阅读的文本、对比度弱、层叠损坏和笨拙的运动状态。
- 评估美观性与正确性。UI 应该感觉有意、连贯且对任务具有视觉吸引力。
- 优先使用视口屏幕截图进行签收。仅将全页捕获用作次要调试工件，并在需要更仔细检查的区域捕获聚焦屏幕截图。
- 如果运动使屏幕截图模糊，请稍等片刻让 UI 平静下来，然后捕获您实际评估的图像。
- 在签收之前，明确询问：我还没有仔细检查这个界面的哪个可见部分？
- 在签收之前，明确询问：如果用户仔细查看，最可能让这个结果尴尬的可见缺陷是什么？

### 签收

- 通过正常用户输入传递的功能路径。
- 覆盖共享的 QA 库存是明确的：注意哪些需求、已实现的功能、控制项、状态和声明被执行了，并指出任何有意排除的内容。
- 视觉 QA 通过覆盖了所有相关的界面。
- 每个用户可见的声明都有一个匹配的视觉检查和来自该声明重要状态和视口或窗口大小的已审查屏幕截图工件。
- 视口适应检查针对预期的初始视图以及任何所需的最低支持视口或窗口大小都通过了。
- 如果产品以窗口形式启动，则在任何手动调整大小或重新定位之前，会检查启动时的尺寸、位置和初始布局。
- UI 不仅仅是功能性的；它视觉上协调一致，并且对于任务而言在美学上不薄弱。
- 功能正确性、视口适应性和视觉质量必须各自通过；一个不能暗示其他。
- 对于交互式产品，完成了快速的探索性检查，响应中提到了该检查覆盖的内容。
- 如果屏幕截图审查和数值检查在任何点上不一致，则会在签出前调查差异；屏幕截图中的可见裁剪是无法解决的，而不是指标可以覆盖的。
- 包括对您检查过但未发现的主要缺陷类别的简短否定确认。
- 执行了清理，或者您有意保持会话活动以进行进一步的工作。

## 屏幕截图示例

如果您计划通过 `codex.emitImage(...)` 发射屏幕截图，默认情况下请使用下一节中的 CSS 标准化路径。这些是模型将解释的屏幕截图的规范示例，或用于基于坐标的后续操作。将原始捕获保留为仅用于对保真度敏感的调试的例外情况；原始例外示例出现在标准化指南之后。

### 模型相关的屏幕截图（默认）

如果您将通过 `codex.emitImage(...)` 发射屏幕截图以供模型解释，请在发射之前将其标准化为 CSS 像素，以捕获您想要的确切区域。这确保了返回的坐标与 Playwright CSS 像素对齐（如果稍后使用它们进行点击），并且还减少了图像有效负载大小和模型令牌成本。

默认情况下不要发射原始原生窗口屏幕截图。仅在您明确需要设备像素保真度时才跳过标准化，例如 Retina 或 DPI 差异调试、像素精确的渲染检查或另一个保真度敏感的情况，其中原始像素比有效负载大小更重要。对于仅在本地检查且不会发射到模型的原始捕获是合适的。

不要假设 `page.screenshot({ scale: "css" })` 在原生窗口模式（`viewport: null`）下就足够了。在 macOS Retina 显示的 Chromium 上，即使请求 `scale: "css"`，带头的原生窗口屏幕截图仍然可能以设备像素大小返回。由于 Electron 通过 Playwright 启动，而 Electron 以 `noDefaultViewport` 运行，因此 `appWindow.screenshot({ scale: "css" })` 可能仍然返回设备像素输出。

为网页和 Electron 窗口使用单独的标准化路径：

- 网页：直接使用 `page.screenshot({ scale: "css" })`。如果原生窗口 Chromium 仍然返回设备像素输出，请在当前页面内部使用 canvas 调整大小；不需要草稿页面。
- Electron：不要使用 `appWindow.context().newPage()` 或 `electronApp.context().newPage()` 作为草稿页面。Electron 上下文可靠地支持该路径。在主进程中使用 `BrowserWindow.capturePage(...)` 捕获，使用 `nativeImage.resize(...)` 调整大小，并直接发射这些字节。

共享帮助程序和约定：

```javascript
var emitJpeg = async function (bytes) {
  await codex.emitImage({
    bytes,
    mimeType: "image/jpeg",
    detail: "original",
  });
};

var emitWebJpeg = async function (surface, options = {}) {
  await emitJpeg(await surface.screenshot({
    type: "jpeg",
    quality: 85,
    scale: "css",
    ...options,
  }));
};

var clickCssPoint = async function ({ surface, x, y, clip }) {
  await surface.mouse.click(
    clip ? clip.x + x : x,
    clip ? clip.y + y : y
  );
};

var tapCssPoint = async function ({ page, x, y, clip }) {
  await page.touchscreen.tap(
    clip ? clip.x + x : x,
    clip ? clip.y + y : y
  );
};
```

- 使用 `page` 或 `mobilePage` 对于网页，或 `appWindow` 对于 Electron，作为 `surface`。
- 将 `clip` 视为来自渲染器的 `getBoundingClientRect()` 的 CSS 像素。
- 除非需要无损保真度，否则优先选择 `quality: 85` 的 JPEG。
- 对于全图像捕获，直接使用返回的 `{ x, y }`。
- 对于裁剪捕获，点击时添加裁剪原点。

### 网页 CSS 标准化

显式视口上下文中首选的网页路径，并且通常适用于网页：

```javascript
await emitWebJpeg(page);
```

移动网页使用相同的路径；将 `page` 替换为 `mobilePage`：

```javascript
await emitWebJpeg(mobilePage);
```

如果模型返回 `{ x, y }`，则直接点击它：

```javascript
await clickCssPoint({ surface: page, x, y });
```

移动网页点击路径：

```javascript
await tapCssPoint({ page: mobilePage, x, y });
```

对于此正常路径中的网页裁剪屏幕截图或元素屏幕截图，`scale: "css"` 通常可以直接工作。点击时添加区域原点。

- `await emitWebJpeg(page, { clip })`
- `await emitWebJpeg(mobilePage, { clip })`
- `await clickCssPoint({ surface: page, clip, x, y })`
- `await tapCssPoint({ page: mobilePage, clip, x, y })`
- `await clickCssPoint({ surface: page, clip: box, x, y })` 在 `const box = await locator.boundingBox()` 之后

当 `scale: "css"` 仍然以设备像素大小返回时，网页原生窗口回退：

```javascript
var emitWebScreenshotCssScaled = async function ({ page, clip, quality = 0.85 } = {}) {
  var NodeBuffer = (await import("node:buffer")).Buffer;
  const target = clip
    ? { width: clip.width, height: clip.height }
    : await page.evaluate(() => ({
        width: window.innerWidth,
        height: window.innerHeight,
      }));

  const screenshotBuffer = await page.screenshot({
    type: "png",
    ...(clip ? { clip } : {}),
  });

  const bytes = await page.evaluate(
    async ({ imageBase64, targetWidth, targetHeight, quality }) => {
      const image = new Image();
      image.src = `data:image/png;base64,${imageBase64}`;
      await image.decode();

      const canvas = document.createElement("canvas");
      canvas.width = targetWidth;
      canvas.height = targetHeight;

      const ctx = canvas.getContext("2d");
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(image, 0, 0, targetWidth, targetHeight);

      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", quality)
      );

      return new Uint8Array(await blob.arrayBuffer());
    },
    {
      imageBase64: NodeBuffer.from(screenshotBuffer).toString("base64"),
      targetWidth: target.width,
      targetHeight: target.height,
      quality,
    }
  );

  await emitJpeg(bytes);
};
```

对于全视口回退捕获，将返回的 `{ x, y }` 视为直接 CSS 坐标：

```javascript
await emitWebScreenshotCssScaled({ page });
await clickCssPoint({ surface: page, x, y });
```

对于裁剪回退捕获，添加裁剪原点：

```javascript
await emitWebScreenshotCssScaled({ page, clip });
await clickCssPoint({ surface: page, clip, x, y });
```

### Electron CSS 标准化

对于 Electron，在主进程中进行标准化，而不是打开一个草稿 Playwright 页面。下面的帮助程序返回 CSS 缩放的字节，用于完整的内容区域或裁剪的 CSS 像素区域。将 `clip` 视为内容区域 CSS 像素，例如从渲染器中的 `getBoundingClientRect()` 获取的值。

```javascript
var emitElectronScreenshotCssScaled = async function ({ electronApp, clip, quality = 85 } = {}) {
  const bytes = await electronApp.evaluate(async ({ BrowserWindow }, { clip, quality }) => {
    const win = BrowserWindow.getAllWindows()[0];
    const image = clip ? await win.capturePage(clip) : await win.capturePage();

    const target = clip
      ? { width: clip.width, height: clip.height }
      : (() => {
          const [width, height] = win.getContentSize();
          return { width, height };
        })();

    const resized = image.resize({
      width: target.width,
      height: target.height,
      quality: "best",
    });

    return resized.toJPEG(quality);
  }, { clip, quality });

  await emitJpeg(bytes);
};
```

完整 Electron 窗口：

```javascript
await emitElectronScreenshotCssScaled({ electronApp });
await clickCssPoint({ surface: appWindow, x, y });
```

使用来自渲染器的 CSS 像素进行裁剪的 Electron 区域：

```javascript
var clip = await appWindow.evaluate(() => {
  const rect = document.getElementById("board").getBoundingClientRect();
  return {
    x: Math.round(rect.x),
    y: Math.round(rect.y),
    width: Math.round(rect.width),
    height: Math.round(rect.height),
  };
});

await emitElectronScreenshotCssScaled({ electronApp, clip });
await clickCssPoint({ surface: appWindow, clip, x, y });
```

### 原始屏幕截图例外示例

仅在原始像素比 CSS 坐标对齐更重要时使用这些情况，例如 Retina 或 DPI 差异调试、像素精确的渲染检查或其他保真度敏感的审查。

网页桌面原始发射：

```javascript
await codex.emitImage({
  bytes: await page.screenshot({ type: "jpeg", quality: 85 }),
  mimeType: "image/jpeg",
  detail: "original",
});
```

Electron 原始发射：

```javascript
await codex.emitImage({
  bytes: await appWindow.screenshot({ type: "jpeg", quality: 85 }),
  mimeType: "image/jpeg",
  detail: "original",
});
```

在移动网页上下文已经运行后，移动原始发射：

```javascript
await codex.emitImage({
  bytes: await mobilePage.screenshot({ type: "jpeg", quality: 85 }),
  mimeType: "image/jpeg",
  detail: "original",
});
```

## 视口适应检查（必需）

不要因为主小部件可见就假设屏幕截图可以接受。在签出前，使用屏幕截图审查和数值检查明确验证预期的初始视图是否与产品要求匹配。

- 在签出前定义预期的初始视图。对于可滚动页面，这是页面上方的体验。对于类似应用程序的外壳、游戏、编辑器、仪表板或工具，这是完整的交互式表面以及使用它所需的控件和状态。
- 使用屏幕截图作为适应的主要证据。数值检查支持屏幕截图；它们不能覆盖可见的裁剪。
- 如果任何必需的可见区域在预期的初始视图中被裁剪、切断、遮挡或推到视口之外，即使页面级别的滚动指标看起来可以接受，签出也会失败。
- 当产品设计为可滚动并且初始视图仍然传达核心体验并暴露主要操作或所需起始上下文时，滚动是可以接受的。
- 对于固定外壳界面，如果需要滚动以到达部分主要交互式表面或基本控件，则滚动不是一个可接受的解决方案。
- 不要仅依赖文档滚动指标。固定高度外壳、内部窗格和隐藏溢出容器可以在页面级别的滚动检查看起来干净的情况下裁剪必需的 UI。
- 检查区域边界，而不仅仅是文档边界。验证每个必需的可见区域在启动状态下是否适合视口内。
- 对于 Electron 或桌面应用程序，在手动调整大小或重新定位之前，验证启动时启动的窗口大小和位置以及渲染器的初始可见布局。
- 通过视口适应检查通过仅证明预期的初始视图可见且没有意外的裁剪或滚动。它不能证明 UI 视觉上正确或在美学上成功。

网页或渲染器检查：

```javascript
console.log(await page.evaluate(() => ({
  innerWidth: window.innerWidth,
  innerHeight: window.innerHeight,
  clientWidth: document.documentElement.clientWidth,
  clientHeight: document.documentElement.clientHeight,
  scrollWidth: document.documentElement.scrollWidth,
  scrollHeight: document.documentElement.scrollHeight,
  canScrollX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  canScrollY: document.documentElement.scrollHeight > document.documentElement.clientHeight,
})));
```

Electron 检查：

```javascript
console.log(await appWindow.evaluate(() => ({
  innerWidth: window.innerWidth,
  innerHeight: window.innerHeight,
  clientWidth: document.documentElement.clientWidth,
  clientHeight: document.documentElement.clientHeight,
  scrollWidth: document.documentElement.scrollWidth,
  scrollHeight: document.documentElement.scrollHeight,
  canScrollX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  canScrollY: document.documentElement.scrollHeight > document.documentElement.clientHeight,
})));
```

当裁剪是一个现实的失败模式时，使用 `getBoundingClientRect()` 检查来增强数值检查，以检查您特定 UI 中的必需可见区域；仅文档级指标不足以用于固定外壳。

## 开发服务器

对于本地网页调试，在持久 TTY 会话中保持应用程序运行。不要依赖来自短期 shell 的一次性后台命令。

使用项目的正常启动命令，例如：

```bash
npm start
```

在 `page.goto(...)` 之前，验证所选端口正在监听并且应用程序有响应。

对于 Electron 调试，通过 `_electron.launch(...)` 从 `js_repl` 启动应用程序，以便相同的会话拥有进程。如果 Electron 渲染器依赖于单独的开发服务器（例如 Vite 或 Next），请保持该服务器在持久 TTY 会话中运行，然后从 `js_repl` 重新启动或重新加载 Electron 应用程序。

## 清理

仅在任务实际完成后才运行清理：

- 此清理是手动执行的。退出 Codex、关闭终端或丢失 `js_repl` 会话不会隐式运行 `electronApp.close()`、`context.close()` 或 `browser.close()`。
- 对于 Electron 特别，假设如果您在执行清理单元之前离开会话，应用程序可能会继续运行。

```javascript
if (electronApp) {
  await electronApp.close().catch(() => {});
}

if (mobileContext) {
  await mobileContext.close().catch(() => {});
}

if (context) {
  await context.close().catch(() => {});
}

if (browser) {
  await browser.close().catch(() => {});
}

browser = undefined;
context = undefined;
page = undefined;
mobileContext = undefined;
mobilePage = undefined;
electronApp = undefined;
appWindow = undefined;

console.log("Playwright 会话已关闭");
```

如果您计划在调试后立即退出 Codex，请先运行清理单元，并等待 `"Playwright 会话已关闭"` 日志后再退出。

## 常见失败模式

- `找不到模块 'playwright'`：请在当前工作区运行一次性设置，并在使用 `js_repl` 前验证导入。
- Playwright 包已安装但浏览器可执行文件缺失：运行 `npx playwright install chromium`。
- `page.goto: net::ERR_CONNECTION_REFUSED`：确保开发服务器仍在持久 TTY 会话中运行，重新检查端口，并优先使用 `http://127.0.0.1:<端口>`。
- `electron.launch` 卡住、超时或立即退出：验证本地 `electron` 依赖，确认 `args` 目标，并确保任何渲染器开发服务器在启动前已运行。
- `Identifier has already been declared`：重用现有的顶层绑定，选择新名称，或将代码包裹在 `{ ... }` 中。仅在内核确实卡住时使用 `js_repl_reset`。
- 在使用 Electron 时，`browserContext.newPage: Protocol error (Target.createTarget): Not supported`：不要使用 `appWindow.context().newPage()` 或 `electronApp.context().newPage()` 作为草稿页；使用模型绑定截图部分中的 Electron 特定截图规范化流程。
- `js_repl` 超时或重置：重新运行引导单元格，并使用更短、更聚焦的单元格重新创建会话。
- 浏览器启动或网络操作立即失败：确认会话是以 `--sandbox danger-full-access` 启动的，如有需要则以此方式重新启动。
