# Chrome 扩展

使用 Manifest V3 构建 production 级别的 Chrome 扩展，并将其发布到 Chrome Web Store。

## 第一部分 — 构建扩展

### 强制性规则

这些规则针对最常见的导致扩展损坏的原因。违反任何一条规则都会导致构建失败。

#### 1. 图标：仅引用您创建的文件 — 或完全省略图标

```
❌ 错误 — 引用不存在的文件或重复使用一个文件用于所有尺寸：
   "icons": { "16": "icon.png", "48": "icon.png", "128": "icon.png" }

✅ 正确 — 每个尺寸都是单独的文件，具有正确的像素尺寸：
   "icons": { "16": "icons/icon-16.png", "48": "icons/icon-48.png", "128": "icons/icon-128.png" }
   (其中 icon-16.png 是 16×16 像素，icon-48.png 是 48×48 像素，icon-128.png 是 128×128 像素)

✅ 也正确 — 如果无法生成真实的 PNG 文件，则从清单中省略图标：
   (只需删除 "icons" 和 "default_icon" 字段 — Chrome 使用默认图标)
```

**如果您包含图标引用，则必须创建实际的图像文件。** 使用脚本生成它们（见 `references/extensions/icons.md`）或省略它们。永远不要引用不存在的文件。

#### 2. 侧边面板：您必须提供一种打开它的方法

定义 `"side_panel": {"default_path": "..."}` 并不会使其可打开。添加触发器：

```js
// 在 service-worker.js 中 — 在扩展图标点击时打开侧边面板
// 重要提示：chrome.action.onClicked 仅在没有任何 default_popup 时触发
chrome.action.onClicked.addListener(async (tab) => {
  await chrome.sidePanel.open({ windowId: tab.windowId });
});
```

如果扩展同时具有弹窗和侧边面板，请在弹窗中添加一个按钮来调用 `chrome.sidePanel.open()`。或者，使用 `chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })` — 但属性是 `openPanelOnActionClick`，而不是 `openPanelOnActionIconClick`；“Icon”变体会导致同步 TypeError 并静默终止服务工作者。在使用 `setPanelBehavior` 时，不要同时定义 `default_popup`。见 `references/extensions/side-panel.md`。

#### 3. 代码执行：仅限沙盒 iframe

扩展 CSP 阻止 `eval()`、`new Function()` 和所有扩展页面中的内联 `<script>`。

```js
// ❌ 错误 — 直接 iframe DOM 访问会抛出 SecurityError
iframe.contentDocument.write(html);

// ❌ 错误 — 扩展页面中的 eval
eval(userCode); // CSP 阻止此操作

// ✅ 选项 A：清单中沙盒 + postMessage
// manifest.json: { "sandbox": { "pages": ["sandbox.html"] } }
iframe.contentWindow.postMessage({ html, css, js }, '*');
// sandbox.html 接收并执行：
window.addEventListener('message', (e) => { eval(e.data.js); /* 允许在沙盒中 */ });

// ✅ 选项 B：Blob URL（创建单独的源，绕过扩展 CSP）
iframe.src = URL.createObjectURL(new Blob([doc], { type: 'text/html' }));

// ✅ 选项 C：srcdoc
iframe.srcdoc = `<style>${css}</style>${html}<script>${js}<\/script>`;
```

有关完整详细信息，请参阅 `references/extensions/csp-sandbox.md`。

#### 4. `tab.url` 需要 `tabs` 权限

没有它，`tab.url` 会静默返回 `undefined` — 不会抛出错误。见
`references/extensions/permissions.md`。

#### 5. 始终使用 async/await — 永远不要 `.then()` 链

```js
// ❌ 差
chrome.tabs.query({active: true, currentWindow: true}).then(tabs => {
  chrome.scripting.executeScript({target: {tabId: tabs[0].id}, files: ['content.js']}).then(() => {});
});

// ✅ 好
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ['content.js'] });
```

对于执行异步操作的 `runtime.onMessage` 监听器：

```js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    const data = await chrome.storage.local.get('key');
    sendResponse({ data });
  })();
  return true; // 保持通道打开
});
```

#### 6. 内容脚本：不要阻塞主线程

当修改许多 DOM 元素时，使用 `requestAnimationFrame` 批量处理并在批量之间 yield：

```js
async function highlightAll(elements) {
  const BATCH = 20;
  for (let i = 0; i < elements.length; i += BATCH) {
    await new Promise(r => requestAnimationFrame(() => {
      elements.slice(i, i + BATCH).forEach(el => el.style.backgroundColor = 'yellow');
      r();
    }));
    if (globalThis.scheduler?.yield) await scheduler.yield();
  }
}
```

有关内容脚本和 DOM 的详细信息，请参阅 `references/extensions/content-scripts.md`。

#### 7. 服务工作者是短暂的 — 永远不要在变量中存储状态

```js
// ❌ 错误 — 当 SW 终止时（约 30 秒不活动）状态丢失
let count = 0;
chrome.tabs.onUpdated.addListener(() => { count++; });

// ✅ 正确 — 在 chrome.storage 中持久化，每次事件时读取
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo) => {
  if (changeInfo.status !== 'complete') return;
  const { count = 0 } = await chrome.storage.local.get('count');
  await chrome.storage.local.set({ count: count + 1 });
  await chrome.action.setBadgeText({ text: String(count + 1) });
});
```

使用 `chrome.alarms` 而不是 `setTimeout`/`setInterval`。有关服务工作者生命周期的详细信息，请参阅 `references/extensions/service-worker.md`。

#### 8. `chrome.identity`：扩展 ID 在开发和生产之间不同

在使用 Google 登录时，OAuth client_id 与特定的扩展 ID 关联。该 ID 在未打包的开发和 Chrome Web Store 之间发生变化。

为了在开发期间稳定 ID，请将 `"key"` 字段添加到 `manifest.json`：
1. 打包扩展一次（chrome://extensions → Pack）
2. 从 .crx 中提取公钥
3. 将 `"key": "MIIBIjANBgkqh..."` 添加到 `manifest.json`

始终记录：“发布到 Chrome Web Store 后，请更新 OAuth client 以使用商店分配的扩展 ID。”有关详细信息，请参阅 `references/extensions/auth-identity.md`。

#### 9. 上下文菜单：在执行操作后向用户显示反馈

当上下文菜单项执行操作（保存、复制等）时，向用户确认。使用通知、徽章闪烁或注入的 toast — 不要让操作静默发生。有关完整的 toast 实现示例，请参阅 `references/extensions/context-menus.md`。

#### 10. Prompt API：在服务工作者、弹窗和侧边面板中可用

`LanguageModel` API 在所有扩展上下文中都有效 — 服务工作者、弹窗和侧边面板 — 无需额外的清单权限。扩展还可以获得 `LanguageModel.params()`，这在 Web 上不可用：

```js
const params = await LanguageModel.params();
// { defaultTopK: 3, maxTopK: 128, defaultTemperature: 1, maxTemperature: 2 }
```

对于一般 Prompt API 模式（可用性检查、会话创建、流式传输），请使用 `modern-web-guidance` 技能。有关扩展特定连接示例，请参阅 `references/extensions/prompt-api.md`。

#### 11. `chrome.action` API 需要 `action` 在清单中

使用 `chrome.action.setBadgeText`、`chrome.action.setIcon` 或 `chrome.action.onClicked` 需要 `manifest.json` 中的 `"action"` 键 — 即使它是空的。没有它，`chrome.action` 是 `undefined`。

```js
// ❌ 错误 — 清单中没有 "action" 键
await chrome.action.setBadgeText({ text: '5' });
// TypeError: Cannot read properties of undefined (reading 'setBadgeText')

// ✅ 修复 — 在 manifest.json 中添加 "action"（至少是一个空对象）
{ "action": {} }
// 或带有弹窗：
{ "action": { "default_popup": "popup/popup.html" } }
```

#### 12. `activeTab` 仅在直接用户手势下工作 — 不在侧边面板中

`activeTab` 仅在直接用户手势（操作图标点击、上下文菜单项、键盘快捷键、地址栏建议）下授予当前标签的临时访问权限 — 不在侧边面板或弹窗中的按钮点击。使用 `tabs` + `host_permissions` 代替。有关详细信息，请参阅
`references/extensions/permissions.md` 和 `references/extensions/side-panel.md`。

#### 13. DevTools 面板 URL 相对于扩展根目录

当创建 DevTools 面板时，面板 HTML 路径相对于 **扩展根目录**，而不是调用 `chrome.devtools.panels.create()` 的 DevTools 页面。

```js
// ❌ 错误 — 路径相对于 devtools/ 目录
chrome.devtools.panels.create("My Panel", "", "panel/panel.html");

// ✅ 正确 — 从扩展根目录的完整路径
chrome.devtools.panels.create("My Panel", "", "devtools/panel/panel.html");
```

有关详细信息，请参阅 `references/extensions/devtools.md`。

#### 14. 离屏文档无法访问大多数 chrome.* API

离屏文档 (`chrome.offscreen`) **严重受限**。大多数 `chrome.*` API 都不可用，包括 `chrome.downloads`、`chrome.tabs`、`chrome.action` 等。

```js
// ❌ 错误 — 离屏文档中 chrome.downloads 是 undefined
chrome.downloads.download({ url, filename: 'recording.webm' }); // TypeError

// ❌ 错误 — 离屏文档中 chrome.action 是 undefined
chrome.action.setBadgeText({ text: 'REC' }); // TypeError
```

**离屏文档中可用的唯一 API 是：**
- `chrome.runtime.sendMessage` / `chrome.runtime.onMessage`
- `chrome.runtime.getURL`
- 标准 Web API（DOM、fetch、MediaRecorder、Canvas、Web Audio 等）

**经验法则：** 离屏文档执行 Web API 工作（录制、解析、音频）。服务工作者执行所有 chrome.* API 工作（下载、徽章更新、通知）。使用 `chrome.runtime.sendMessage` 在它们之间进行桥接。有关详细信息，请参阅 `references/extensions/message-passing.md`。

#### 15. 通知和徽章图标必须引用真实的图像文件

`chrome.notifications.create()` 需要 `iconUrl` 指向一个实际图像文件。如果文件不存在或路径错误，调用会以 `"Unable to download all specified images."` 失败。

```js
// ❌ 错误 — 图标文件不存在
chrome.notifications.create('reminder', {
  type: 'basic',
  iconUrl: 'icons/icon-128.png', // 文件不在扩展中！
  title: 'Reminder',
  message: 'Time is up!'
});

// ✅ 生成数据 URL — 运行时通过 OffscreenCanvas — 无需文件。
// 见 `references/extensions/icons.md` 中的可重用实现。
const iconUrl = await getIconDataUrl();
chrome.notifications.create('reminder', { type: 'basic', iconUrl, title: 'Reminder', message: 'Time is up!' });
```

这适用于 chrome.* API 中的所有图像引用 — 通知、`chrome.action.setIcon`、上下文菜单图标等。**如果您引用文件，则它必须存在。**

#### 16. 标签捕获：使用状态锁定防止双重启动

如果调用 `chrome.tabCapture.getMediaStreamId()` 时之前的捕获仍然处于活动状态，则会失败并返回 `"Cannot capture a tab with an active stream"`。快速双击扩展图标很容易触发此错误。使用显式状态锁定：

```js
// ❌ 错误 — 没有防止快速点击的机制
let isRecording = false;
chrome.action.onClicked.addListener(async (tab) => {
  if (isRecording) { stopRecording(); isRecording = false; }
  else { isRecording = true; startRecording(tab); } // 第二次点击 = "active stream" 错误
});

// ✅ 正确 — 使用过渡状态锁定并发操作
// 状态机：'idle' → 'starting' → 'recording' → 'stopping' → 'idle'
// 将状态存储在 chrome.storage.session（在 SW 重启时存活，浏览器关闭时清除）
chrome.action.onClicked.addListener(async (tab) => {
  const { recordingState = 'idle' } = await chrome.storage.session.get('recordingState');

  if (recordingState === 'starting' || recordingState === 'stopping') return;

  if (recordingState === 'idle') {
    await chrome.storage.session.set({ recordingState: 'starting' });
    try {
      await startRecording(tab);
      await chrome.storage.session.set({ recordingState: 'recording' });
      await chrome.action.setBadgeText({ text: 'REC' });
      await chrome.action.setBadgeBackgroundColor({ color: '#FF0000' });
    } catch (err) {
      console.error('Failed to start recording:', err);
      await chrome.storage.session.set({ recordingState: 'idle' });
    }
  } else if (recordingState === 'recording') {
    await chrome.storage.session.set({ recordingState: 'stopping' });
    try { await stopRecording(); }
    finally {
      await chrome.storage.session.set({ recordingState: 'idle' });
      await chrome.action.setBadgeText({ text: '' });
    }
  }
});
```

此模式适用于管理独占资源的任何 chrome API：
`chrome.tabCapture`、`chrome.desktopCapture`、`chrome.offscreen.createDocument`（一次只允许一个 offscreen 文档）。有关详细信息，请参阅 `references/extensions/media-capture.md`。

#### 17. `chrome.desktopCapture` 需要一个具有 URL 访问权限的目标标签

从服务工作者调用 `chrome.desktopCapture.chooseDesktopMedia()` 时，您必须将活动标签作为 `targetTab` 参数传递。标签对象必须具有其 `url` 字段填充，这需要 `"tabs"` 权限。

```js
// ❌ 错误 — 从服务工作者调用时没有 targetTab
chrome.desktopCapture.chooseDesktopMedia(['screen', 'window'], (streamId) => { ... });
// 错误：从服务工作者上下文中调用时需要目标标签。

// ❌ 错误 — 标签没有 url 字段（缺少 "tabs" 权限）
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
chrome.desktopCapture.chooseDesktopMedia(['screen', 'window'], tab, (streamId) => { ... });
// 错误：targetTab 没有设置 URL 字段。

// ✅ 正确 — 清单中 "tabs" 权限 + 传递标签对象
// manifest.json: { "permissions": ["tabs", "desktopCapture"] }
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
chrome.desktopCapture.chooseDesktopMedia(['screen', 'window'], tab, (streamId) => {
  if (!streamId) return; // 用户取消了操作
});
```

**注意：** 优先使用 `chrome.tabCapture.getMediaStreamId()` 进行标签仅录制。仅在用户应选择要捕获的屏幕/窗口时使用 `chrome.desktopCapture`。有关详细信息，请参阅 `references/extensions/media-capture.md`。

#### 18. 用户脚本：四个不明显的陷阱

`chrome.userScripts` 在运行时执行**用户提供的代码**。用于脚本管理器和用户自动化 — 不要用于扩展捆绑的脚本。

- **API 在未启用时访问属性会抛出错误。** Chrome 138+ 要求用户在扩展的详情页上切换“允许用户脚本”；Chrome < 138 要求开发者模式。始终在 `chrome.userScripts.*` 调用之前调用 `isUserScriptsAvailable()`，并在返回 false 时显示错误 UI。
- **注册的脚本在扩展更新时被清除。** 将配置保存在 `chrome.storage` 中；在 `runtime.onInstalled` 中为 `"update"` 原因重新注册它们。
- **消息传递需要显式同意。** 首先调用 `configureWorld({ messaging: true })`；监听 `runtime.onUserScriptMessage`，而不是 `runtime.onMessage`。
- **`ScriptSource` 限制：** 每个 `js` 条目必须恰好有一个 `code` 或 `file`。**`id` 限制：** 不能以 `_` 开头。

有关详细信息，请参阅 `references/extensions/user-scripts.md`。

#### 19. `chrome.windows` 没有 `.query()` 方法 — 使用 `getAll`、`getLastFocused` 或 `getCurrent`

与 `chrome.tabs.query()` 不同，`chrome.windows` API **没有** `.query()` 方法。

```js
// ❌ 错误 — chrome.windows.query 不存在
const windows = await chrome.windows.query({ focused: true });
// TypeError: chrome.windows.query is not a function

// ✅ 正确 — 根据您的需求使用正确的方法
const focused = await chrome.windows.getLastFocused({ populate: true });
const current = await chrome.windows.getCurrent({ populate: true });
const all     = await chrome.windows.getAll({ populate: true });
```

**`chrome.windows` 方法：** `getAll`、`getLastFocused`、`getCurrent`、`get(windowId)`、`create`、`update`、`remove`。有关详细信息，请参阅 `references/extensions/tab-management.md`。

#### 20. 服务工作者中的 `chrome.permissions.request()` 必须在消息监听器中的 `await` 之前调用

来自 UI 上下文（侧边面板、弹窗）的用户手势会传播到 `chrome.runtime.sendMessage` 到服务工作者的 `onMessage` 监听器 — 但仅限于该同步轮次。如果监听器在调用 `chrome.permissions.request()` 之前执行 `await`（即使是一个短暂的延迟），手势就会消失，调用会抛出 `"This function must be called during a user gesture"`。在监听器中作为第一件事调用它，在其之前没有任何 `await` — 请参阅
`references/extensions/permissions.md`。

### 始终使用 Manifest V3

永远不要生成 Manifest V2 代码。
- `background.service_worker` 而不是 `background.scripts`
- `chrome.action` 而不是 `chrome.browserAction`
- `chrome.scripting.executeScript` 而不是 `chrome.tabs.executeScript`
- `host_permissions` 与 `permissions` 分开
- HTML 中没有内联脚本 — 使用 `<script src="file.js">`
- 没有内联事件处理程序 — 使用 `addEventListener`

---

## 第二部分 — 发布到 Chrome Web Store

管理 `CHROMEWEBSTORE.md` — 这是 Chrome 扩展项目 Chrome Web Store 列表元数据的唯一信息来源、权限说明、隐私声明、版本历史和发布就绪情况。

### 核心工作流程

每次您以影响其商店存在的方式触摸 Chrome 扩展项目时，都在项目根目录中更新（或创建）`CHROMEWEBSTORE.md`。该文件跟踪开发人员需要在 Chrome 开发者控制面板中填写的一切，以便他们可以从单个文档中复制粘贴，而不是在发布时手忙脚乱。

#### 创建 CHROMEWEBSTORE.md 的时机

在以下任何情况发生时立即创建它：
- 用户表示他们想要发布扩展
- 用户要求“准备发布”或“准备发布”
- 您正在构建一个显然最终会发布到商店的新扩展
- 用户询问商店列表要求

使用 `references/webstore/chromewebstore-template.md` 中的模板作为您的起点。在生成文件之前阅读它。

#### 更新 CHROMEWEBSTORE.md 的时机

每当发生以下情况时更新它：
- **面向用户的更改**：更新“最后更新”日期，更新描述中的功能列表，并在版本历史中添加条目
- **manifest.json 更改**：如果权限、host_permissions 或内容脚本更改，请更新权限说明部分 — 每个权限都需要一个 plain-English 原因，以便审核团队理解
- **新版本**：添加一个版本历史条目，包含版本号、日期和摘要
- **与隐私相关的更改**：如果数据收集、存储或传输发生变化，请更新隐私与数据使用部分和隐私政策
- **资源更改**：如果图标或 UI 发生变化，请记录需要刷新的截图
- **拒绝响应**：如果用户报告了 CWS 拒绝，请更新文件以进行修复，并在版本历史中添加注释

### 如何填写

对于每个部分，从实际项目文件中提取信息：
1. 阅读 `manifest.json` 以提取名称、版本、描述、权限、host_permissions
2. 扫描代码库以查找数据收集（存储、fetch 调用、分析）
3. 检查图标文件及其尺寸
4. 查看扩展的 UI 以了解描述中的功能

使用具体、诚实、以用户利益为导向的语气撰写面向商店的副本。Chrome Web Store 审核团队会拒绝模糊的描述。“让您的更轻松”将被拒绝。“在任何网页上突出显示搜索结果并允许您将突出显示保存到本地列表”将通过。

**永远不要提及实现细节。** 用户关心扩展为他们做了什么，而不是它是如何构建的。删除任何提及 API、库、框架或代码模式的提及：

| ❌ 实现细节（删除它） | ✅ 用户利益（保留它） |
|----------------------|----------------------|
| “使用 MutationObserver 检测页面变化” | “自动检测您浏览时的新内容” |
| “使用自定义元素和 Shadow DOM 构建” | “无缝工作，不会影响页面样式” |
| “使用服务工作者进行后台处理” | “在后台安静运行，不会减慢您的浏览器” |
| “利用 chrome.storage.sync API” | “您的设置在所有设备之间同步” |
| “实现 declarativeNetRequest 进行过滤” | “在不读取您页面内容的情况下阻止广告和跟踪器” |

### CHROMEWEBSTORE.md 部分

在生成文件之前阅读 `references/webstore/chromewebstore-template.md` — 它定义了每个部分涵盖的内容以及如何填写它。风险最高的部分是权限说明：为每个权限和每个 host_permission 撰写一个具体的 plain-English 原因。“需要扩展才能工作”将被拒绝。有关生成隐私政策的指导，请参阅 `references/webstore/privacy-policy.md`。

### 发布前检查清单

提交之前，请运行 `references/webstore/review-checklist.md`。最常见的首次提交失败：
- 每个权限和 host_permission 都必须有具体的说明（不能是“需要工作”）
- 隐私政策 URL 必须是活动的，并与数据使用披露表单匹配
- 至少 1 张 1280×800 或 640×400 的截图
- ZIP 必须排除 `.git/`、`node_modules/`、`.env`、`CHROMEWEBSTORE.md`

### 商店列表副本指南

有关副本指南和常见拒绝原因，请参阅 `references/webstore/store-listing.md`。关键规则：以功能开头（“在任何网页上突出显示搜索结果”），而不是感觉（“再次享受搜索”）。

---

## 参考文件

在编写代码或内容之前，阅读相关文件以获取详细的 API 模式和发布指南：

| 主题 | 参考 |
|------|------|
| 权限 | `references/extensions/permissions.md` |
| 侧边面板 | `references/extensions/side-panel.md` |
| 内容脚本 & DOM | `references/extensions/content-scripts.md` |
| 弹窗 | `references/extensions/popup-ui.md` |
| 服务工作者生命周期 | `references/extensions/service-worker.md` |
| 代码执行 & CSP | `references/extensions/csp-sandbox.md` |
| API 调用 | `references/extensions/api-calling.md` |
| Declarative Net Request | `references/extensions/declarative-net-request.md` |
| Chrome Prompt API | `references/extensions/prompt-api.md` |
| DevTools 面板 | `references/extensions/devtools.md` |
| 身份验证 | `references/extensions/auth-identity.md` |
| 上下文菜单 | `references/extensions/context-menus.md` |
| 地址栏 | `references/extensions/omnibox.md` |
| 存储 | `references/extensions/storage.md` |
| 标签 & 窗口管理 | `references/extensions/tab-management.md` |
| 标签/桌面捕获 | `references/extensions/media-capture.md` |
| 用户脚本 | `references/extensions/user-scripts.md` |
| 消息传递 | `references/extensions/message-passing.md` |
| 图标 | `references/extensions/icons.md` |
| CHROMEWEBSTORE.md 模板 | `references/webstore/chromewebstore-template.md` |
| 隐私政策指导 | `references/webstore/privacy-policy.md` |
| 发布前检查清单 | `references/webstore/review-checklist.md` |
| 商店列表技巧 & 拒绝 | `references/webstore/store-listing.md` |

## 输出检查清单

在交付之前，验证每一项：

- [ ] `manifest_version: 3` — 不在任何地方使用 V2 API
- [ ] 所有清单中引用的图标文件都存在并具有正确的尺寸 — 或省略图标
- [ ] 侧边面板具有显式的打开触发器（而不仅仅是清单声明）
- [ ] 代码执行使用沙盒/blob/srcdoc — 扩展页面中不使用 `eval()`
- [ ] 如果访问 `tab.url` 或 `tab.title`，则声明 `tabs` 权限
- [ ] 所有代码都使用 `async`/`await` — 不使用 `.then()` 链
- [ ] 内容脚本使用 `requestAnimationFrame` 批量 DOM 更新
- [ ] 服务工作者不在全局变量中存储状态 — 使用 `chrome.storage`
- [ ] HTML 中没有内联脚本或事件处理程序
- [ ] 上下文菜单操作向用户显示确认
- [ ] `"action": {}`（或更多）在清单中存在，如果使用 `chrome.action.*` API
- [ ] 如果从侧边面板读取/脚本标签：使用 `tabs` + `host_permissions`（不是 `activeTab`）
- [ ] DevTools 面板路径在 `chrome.devtools.panels.create()` 中相对于扩展根目录
- [ ] 离屏文档仅使用 `chrome.runtime` 消息传递 — 没有 `chrome.downloads`、`chrome.action` 等
- [ ] chrome.* API 中的所有图像引用都指向真实的文件（或使用数据 URL）
- [ ] 标签/桌面捕获使用状态锁定以防止双重启动错误
- [ ] `chrome.desktopCapture.chooseDesktopMedia` 传递具有 `tabs` 权限的 `targetTab`
- [ ] `chrome.windows` 调用使用 `getAll`/`getLastFocused`/`getCurrent` — 不使用 `.query()`（它不存在）
- [ ] 服务工作者 `onMessage` 监听器中的 `chrome.permissions.request()` 在其之前不能使用 `await`
- [ ] 在使用 `chrome.userScripts` 之前检查可用性（如果用户未启用，API 会抛出错误）
- [ ] 用户脚本配置保存在 `chrome.storage` 中，并在 `runtime.onInstalled` 的 `"update"` 原因下恢复
- [ ] `configureWorld({ messaging: true })` 在发送消息之前调用；监听 `onUserScriptMessage` 而不是 `onMessage`
- [ ] `ScriptSource` 条目每个都恰好有一个 `code` 或 `file`（不能同时存在，也不能都不存在）
- [ ] 用户脚本 `id` 值不能以下划线开头
- [ ] `sidePanel.setPanelBehavior` 使用 `openPanelOnActionClick` — 不是 `openPanelOnActionIconClick`
- [ ] 所有异步操作的错误处理
- [ ] `host_permissions` 限制为特定域（除非需要 `<all_urls>`）
- [ ] `onMessage` 监听器中的异步响应 `return true`
- [ ] 在 `chrome.contextMenus` `contexts` 中使用 `"tab"` 需要 Chrome M150+
