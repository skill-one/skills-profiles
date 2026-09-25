# Chrome 扩展开发（Manifest V3）

本技能涵盖了构建、调试和发布 Chrome 扩展所需的一切，使用 MV3。它组织为路由文档：首先阅读此文件以了解架构和决策点，然后加载相关的参考文件以获取实现细节。

## 参考文件

仅阅读与当前任务相关的参考文件。每个文件都是自包含的。

| 文件 | 何时阅读 |
| --- | --- |
| `references/manifest-v3.md` | 设置或修改 manifest.json、配置图标、版本控制 |
| `references/service-worker.md` | 背景逻辑、生命周期、状态持久化、闹钟、事件 |
| `references/content-scripts.md` | 将代码注入页面、隔离/主世界、动态注入、SPA 处理、孤儿化 |
| `references/messaging-rpc.md` | 任何上下文之间的通信、类型化协议、RPC 层、异步处理模式 |
| `references/ui-surfaces.md` | 弹出窗口、选项页面、侧面板、上下文菜单、命令、通知、地址栏、开发者工具面板 |
| `references/storage.md` | chrome.storage（本地/同步/会话）、配额、响应式模式、框架钩子 |
| `references/network-csp.md` | 内容脚本发起的 HTTP 请求、CSP 绕过中继、声明式网络请求、离屏文档、CORS |
| `references/permissions.md` | 必要/可选权限、主机权限、活动标签页、运行时请求流程 |
| `references/web-accessible-resources.md` | 将扩展文件暴露给网页、安全影响 |
| `references/typescript-build.md` | TypeScript 设置、项目结构、构建工具比较、打包 |
| `references/publishing.md` | Chrome Web Store 提交、审核流程、拒绝原因、更新、隐私政策 |
| `references/execution-contexts.md` | 通信流程图、每个上下文的权限/限制、选择正确的消息传递方法 |
| `references/debugging-mistakes.md` | 扩展的 DevTools、测试 SW 终止、常见陷阱、错误模式 |

## 架构概述

Chrome 扩展最多有 5 个执行上下文，通过消息传递进行通信：

```
┌──────────────────────────────────────────────────────────┐
│ 扩展进程                                        │
│  ┌─────────────────┐  ┌───────┐  ┌─────────┐  ┌──────┐ │
│  │ 服务工作者   │  │ 弹出窗口 │  │ 选项页面 │  │ 侧面板 │ │
│  │ (后台)     │  │       │  │  全部   │  │ 全部 │ │
│  │ - 无 DOM         │  │ 全部  │  │  DOM    │  │ DOM  │ │
│  │ - 持久化 30s      │  │ DOM   │  │  DOM    │  │ DOM  │ │
│  │ - 所有 chrome.*   │  │ 所有  │  │  所有   │  │ 所有 │ │
│  │   API           │  │ APIs  │  │  APIs   │  │ APIs │ │
│  └────────┬─────────┘  └───┬───┘  └────┬────┘  └──┬───┘ │
│           │ chrome.runtime.sendMessage / connect   │     │
└───────────┼────────────────┼───────────┼──────────┼──────┘
            │                │           │          │
    chrome.tabs.sendMessage  │           │          │
            │                │           │          │
┌───────────┼────────────────┼───────────┼──────────┼──────┐
│ 网页  ▼                                              │
│  ┌──────────────────┐    ┌──────────────────┐            │
│  │ 内容脚本    │    │ 主世界脚本    │            │
│  │ (隔离世界)  │◄──►│ (页面上下文)    │            │
│  │ - 共享 DOM      │    │ - 共享 DOM      │            │
│  │ - 自有 JS 作用域    │    │ - 页面 JS 作用域   │            │
│  │ - chrome.runtime  │    │ - 无 chrome.* API │            │
│  │ - chrome.storage  │    │ - 全页访问        │            │
│  │ - 受 CSP 限制  │    │ - 受 CSP 限制   │            │
│  │   (仅网络)  │    │   (完全)         │            │
│  └──────────────────┘    └──────────────────┘            │
│           ▲ window.postMessage                           │
│           │ (通过共享 DOM)                           │
└──────────────────────────────────────────────────────────┘
```

### 通信流程（标记通道）

```
┌───────────────────────────────────────────────────────────────────────────┐
│ 扩展进程                                                         │
│                                                                           │
│  ┌─────────────────┐  chrome.runtime   ┌───────┐  ┌─────────┐  ┌──────┐ │
│  │ 服务工作者   │◄─.sendMessage()──│ 弹出窗口 │  │ 选项页面 │  │ 侧面板 │ │
│  │ (后台)     │◄─.connect()──────│       │  │  全部   │  │ 全部 │ │
│  │                  │                  └───────┘  └─────────┘  └──────┘ │
│  │ - 无 DOM         │  ┌────────────────────────────────────────────┐   │
│  │ - 持久化 30s      │  │ SW 不能推送到这些页面。             │   │
│  │ - 所有 chrome.*   │  │ 使用：端口 (.connect) 或 storage.onChanged │   │
│  └────────┬─────────┘  └────────────────────────────────────────────┘   │
│           │                                                              │
│  chrome.storage.onChanged ◄── 同时在所有上下文中触发  │
│                                                                           │
└───────────┼──────────────────────────────────────────────────────────────┘
            │ chrome.tabs.sendMessage(tabId, ...) [SW 必须知道 tabId]
            │
┌───────────┼──────────────────────────────────────────────────────────────┐
│ 网页  ▼                                                              │
│  ┌──────────────────┐  window.postMessage  ┌──────────────────┐         │
│  │ 内容脚本    │◄───────────────────►│ 主世界脚本    │         │
│  │ (隔离世界)  │  自定义 DOM 事件  │ (页面上下文)    │         │
│  │                   │                     │                   │         │
│  │ chrome.runtime ───┼── 到/来自 SW        │ 无 chrome.* APIs  │         │
│  │ chrome.storage    │                     │ 全页 JS          │         │
│  │ 共享 DOM        │                     │ 共享 DOM        │         │
│  │ 页面 CSP (网络)│                     │ 页面 CSP (完全)   │         │
│  └──────────────────┘                     └──────────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
```

有关详细流程图（三层桥接、跨扩展、存储广播）以及每个上下文中权限、限制和工作绕过的详细说明：→ 阅读 `references/execution-contexts.md`

### 通信方法概览

| 方法 | 方向 | 适用于 |
| --- | --- | --- |
| `chrome.runtime.sendMessage` | 任何扩展上下文 → SW | 单次请求/响应（90% 的情况） |
| `chrome.tabs.sendMessage` | SW → 内容脚本（通过 tabId） | 向特定标签页推送数据 |
| `chrome.runtime.connect` (端口) | 双向 | 流式传输、进度、SW ↔ 弹出窗口 |
| `window.postMessage` | 同一页面上的不同世界之间 | 页面 JS ↔ 内容脚本桥接 |
| `chrome.storage.onChanged` | 广播到所有上下文 | 设置同步，无需消息传递 |

→ 完整矩阵（包括限制和边缘情况）：`references/execution-contexts.md` → 实现模式、类型化协议、RPC 层：`references/messaging-rpc.md`

### 关键架构规则

1. **服务工作者是短暂的。** 它在 30 秒不活动后终止。所有状态必须持久化到 chrome.storage。所有事件监听器必须在顶层同步注册。永远不要使用 setTimeout/setInterval 超过几秒钟。→ 阅读 `references/service-worker.md`

2. **内容脚本在页面原点运行。** 内容脚本发起的网络请求受页面 CSP 和 CORS 的约束。要绕过，通过服务工作者中继。→ 阅读 `references/network-csp.md`

3. **消息传递是骨干。** 所有跨上下文交互都使用 chrome.runtime 消息传递。第一个错误：忘记在异步消息监听器中返回 `true`。→ 阅读 `references/messaging-rpc.md`

4. **权限决定 CWS 审核速度。** 广泛的主机权限会触发人工审核（数周）。activeTab + 可选权限 = 快速自动审核。→ 阅读 `references/permissions.md`

5. **弹出窗口在失去焦点时被销毁。** 侧面板会保留。根据交互持续时间选择。→ 阅读 `references/ui-surfaces.md`

## 决策树：哪个上下文处理什么？

### "我需要在用户访问页面时运行代码"

→ 内容脚本。静态（manifest）用于已知 URL 模式，动态（chrome.scripting）用于用户触发的注入。默认使用隔离世界，除非你需要页面 JS 访问。→ 阅读 `references/content-scripts.md`

### "我需要向我的 API 发起 HTTP 请求"

- 从弹出窗口/选项页面/侧面板：直接 fetch() 工作（扩展原点，无 CSP 问题）
- 在具有限制性 CSP 的页面的内容脚本：通过服务工作者中继
- 从服务工作者：直接 fetch() 工作（需要目标域的主机权限）→ 阅读 `references/network-csp.md`

### "我需要存储用户设置"

- 在设备之间同步的设置：chrome.storage.sync（100KB 限制）
- 大数据或缓存：chrome.storage.local（10MB，或使用权限无限制）
- 在 SW 重启后持续存在的临时状态：chrome.storage.session → 阅读 `references/storage.md`

### "我需要修改 HTTP 标头或阻止请求"

→ declarativeNetRequest（不是 webRequest，它在 MV3 中失去了阻止功能）→ 阅读 `references/network-csp.md`

### "我需要页面的 JavaScript 与我的扩展通信"

→ 三层桥接：页面（window.postMessage）→ 内容脚本 → 服务工作者 → 阅读 `references/messaging-rpc.md`

### "我需要了解每个上下文可以和不能做什么"

→ 阅读 `references/execution-contexts.md` — 每个上下文的卡片列出了 chrome.\* 访问、DOM、网络、存储、生命周期、硬限制和实用工作绕过。

### "我需要周期性后台任务"

→ chrome.alarms（最小 30 秒间隔）。不是 setTimeout。→ 阅读 `references/service-worker.md`

### "我需要在后台使用 DOM API"（DOMParser、Canvas、Audio）

→ 离屏文档。每个扩展一个，只有 chrome.runtime 可用。→ 阅读 `references/network-csp.md`

### "我需要使用 OAuth 进行身份验证"

→ chrome.identity.launchWebAuthFlow() 或 chrome.identity.getAuthToken()（仅限 Google）→ 阅读 `references/service-worker.md`（身份验证部分）

## 工作流程：从零开始创建新扩展

1. **定义 manifest**，使用最小权限。从 `activeTab` + `scripting` 开始。→ 阅读 `references/manifest-v3.md`

2. **设置 TypeScript 和构建工具**（或使用 CRXJS 进行基于 Vite 的开发）。→ 阅读 `references/typescript-build.md`

3. **实现服务工作者**，在顶层注册所有事件监听器。→ 阅读 `references/service-worker.md`

4. **添加内容脚本**，如果你需要页面交互。→ 阅读 `references/content-scripts.md`

5. **构建 UI 表面**（弹出窗口、选项页面、侧面板）按需。→ 阅读 `references/ui-surfaces.md`

6. **连接所有上下文之间的消息传递**。→ 阅读 `references/messaging-rpc.md`

7. **使用 DevTools 进行测试**，特别是测试服务工作者终止。→ 阅读 `references/debugging-mistakes.md`

8. **发布到 Chrome Web Store**。→ 阅读 `references/publishing.md`

## 工作流程：向现有扩展添加功能

1. 确定功能属于哪个上下文（见上文的决策树）。
2. 阅读该上下文相关的参考文件。
3. 检查是否需要新权限。对于新功能，优先使用可选权限。→ 阅读 `references/permissions.md`
4. 如果添加新的内容脚本、UI 表面或权限，则更新 manifest。
5. 处理扩展更新的优雅方式（内容脚本孤儿化）。→ 阅读 `references/content-scripts.md`（孤儿化部分）

## 最小 manifest.json 模板

```json
{
  "manifest_version": 3,
  "name": "我的扩展",
  "version": "1.0.0",
  "description": "一句话描述它做什么",
  "permissions": ["storage", "activeTab", "scripting"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

→ 完整 manifest 参考（包含所有字段）：`references/manifest-v3.md`

## 代码模式快速参考

### 异步消息处理器（安全模式）

```typescript
// 包装异步处理器以避免 return-true 陷阱
function asyncHandler(
  fn: (msg: any, sender: chrome.runtime.MessageSender) => Promise<any>,
) {
  return (
    message: any,
    sender: chrome.runtime.MessageSender,
    sendResponse: (r: any) => void,
  ) => {
    fn(message, sender)
      .then(sendResponse)
      .catch((e) => sendResponse({ __error: true, message: e.message }));
    return true; // 字面量 true，不是 Promise<true>
  };
}

chrome.runtime.onMessage.addListener(
  asyncHandler(async (msg, sender) => {
    if (msg.type === "FETCH") {
      const res = await fetch(msg.url);
      return { ok: res.ok, data: await res.text() };
    }
  }),
);
```

### CSP 绕过中继（内容脚本 → 服务工作者 → API）

```typescript
// content-script.ts
async function apiCall(endpoint: string, options?: RequestInit) {
  return chrome.runtime.sendMessage({ type: "API_RELAY", endpoint, options });
}

// background.ts
const ALLOWED_ENDPOINTS = ["https://api.example.com"];
chrome.runtime.onMessage.addListener(
  asyncHandler(async (msg) => {
    if (msg.type !== "API_RELAY") return;
    if (!ALLOWED_ENDPOINTS.some((e) => msg.endpoint.startsWith(e))) {
      throw new Error("Blocked endpoint");
    }
    const res = await fetch(msg.endpoint, msg.options);
    return { ok: res.ok, status: res.status, data: await res.text() };
  }),
);
```

### 跨 SW 重启持久化状态

```typescript
// 使用 chrome.storage.session 存储临时状态
chrome.storage.session.setAccessLevel({
  accessLevel: "TRUSTED_AND_UNTRUSTED_CONTEXTS",
});

async function getState<T>(key: string, fallback: T): Promise<T> {
  const result = await chrome.storage.session.get(key);
  return result[key] ?? fallback;
}
async function setState<T>(key: string, value: T): Promise<void> {
  await chrome.storage.session.set({ [key]: value });
}
```

### 孤儿内容脚本检测

```typescript
function isExtensionContextValid(): boolean {
  try {
    return !!chrome.runtime?.id;
  } catch {
    return false;
  }
}

// 在任何 chrome.runtime 调用之前
if (!isExtensionContextValid()) {
  showRefreshBanner();
  return;
}
```

## 不要这样做

- 不要使用 `eval()`、`new Function()` 或加载远程脚本。MV3 禁止这样做。
- 不要在服务工作者中使用 `setTimeout`/`setInterval` 超过 5 秒。
- 不要在回调或异步函数中注册事件监听器。
- 不要使用 `<all_urls>` 主机权限，除非绝对必要。
- 不要依赖 DevTools 在测试期间保持服务工作者活跃。
- 不要在异步消息监听器中忘记 `return true`。
- 不要在服务工作者中使用 `localStorage` 或 `sessionStorage`（它们在那里不存在）。
- 不要假设内容脚本会存活于扩展更新。
- 不要使用 `webRequest` 阻止（MV3 中已移除）。使用 `declarativeNetRequest`。
- 不要使用 `chrome.extension.getBackgroundPage()`（MV3 中已移除）。
