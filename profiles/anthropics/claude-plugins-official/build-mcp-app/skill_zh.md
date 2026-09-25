# 构建MCP应用（交互式UI组件）

MCP应用是一个标准的MCP服务器，**同时提供UI资源**——在聊天界面内渲染的交互式组件。一次构建，即可在Claude、ChatGPT以及其他实现应用界面的主机上运行。

UI层是**可叠加的**。底层仍然是工具、资源和相同的线路协议。如果你之前没有构建过普通的MCP服务器，`build-mcp-server`技能涵盖了基础层。这个技能在基础层之上添加了组件。

> **在Claude中测试**：将服务器作为自定义连接器添加到claude.ai（通过Cloudflare隧道进行本地开发）——这将实际测试iframe沙盒和`hostContext`。见 https://claude.com/docs/connectors/building/testing。

## Claude主机特定配置

| `_meta.ui.*`键 | 位置 | 效果 |
|---|---|---|
| `resourceUri` | 工具 | 主机为该工具的结果渲染哪个`ui://`资源。 |
| `visibility: ["app"]` | 工具 | 隐藏仅用于组件的工具（例如通过`callServerTool`调用的几何/图像获取器）从Claude的工具列表中消失。 |
| `prefersBorder: false` | 资源 | 移除主机的卡片外边框（移动端）。 |
| `csp.{connectDomains, resourceDomains, baseUriDomains}` | 资源 | 声明外部原点；默认是阻止所有。`frameDomains`目前在Claude中受限。 |

- `hostContext.safeAreaInsets: {top, right, bottom, left}` (px) — 尊重这些以适应缺口和作曲家覆盖层。
- 目录提交需要OAuth或**无认证** (`none`) —— 静态令牌仅限私有部署且会阻止列出 —— 加上工具`annotations`和3-5张PNG截图；见`references/directory-checklist.md`。

---

## 当组件优于纯文本时

不要为了组件而组件——大多数工具返回文本或JSON就足够了。当以下情况之一成立时，添加组件：

| 信号 | 组件类型 |
|---|---|
| 工具需要结构化输入而Claude无法可靠推断 | 表单 |
| 用户必须从Claude无法排序的列表中选择（文件、联系人、记录） | 选择器 / 表格 |
| 需要明确确认的破坏性或计费操作 | 确认对话框 |
| 输出是空间或视觉的（图表、地图、差异、预览） | 显示组件 |
| 用户想观看的长时间运行的工作 | 进度 / 实时状态 |

如果没有适用情况，则跳过组件。文本构建更快，用户使用也更快。

---

## 组件与提取——正确路由

在构建组件之前，检查**提取**是否涵盖它。提取是规范原生的，零UI代码，在任何合规主机中均可工作。

| 需求 | 提取 | 组件 |
|---|---|---|
| 确认是/否 | ✅ | 过度设计 |
| 从短枚举中选择 | ✅ | 过度设计 |
| 填写扁平表单（姓名、电子邮件、日期） | ✅ | 过度设计 |
| 从大型/可搜索列表中选择 | ❌ (无滚动/搜索) | ✅ |
| 选择前的视觉预览 | ❌ | ✅ |
| 图表 / 地图 / 差异视图 | ❌ | ✅ |
| 实时更新进度 | ❌ | ✅ |

如果提取涵盖它，则使用它。见`../build-mcp-server/references/elicitation.md`。

---

## 架构：两种部署形态

### 远程MCP应用（最常见）

托管的流式HTTP服务器。组件模板作为**资源**提供；工具结果引用它们。主机获取资源，在iframe沙盒中渲染它，并在组件和Claude之间代理消息。

```
┌──────────┐  tools/call   ┌────────────┐
│  Claude  │─────────────> │ MCP server │
│   host   │<── result ────│  (remote)  │
│          │  + widget ref │            │
│          │               │            │
│          │ resources/read│            │
│          │─────────────> │  widget    │
│ ┌──────┐ │<── template ──│  HTML/JS   │
│ │iframe│ │               └────────────┘
│ │widget│ │
│ └──────┘ │
└──────────┘
```

### MCPB打包的MCP应用（本地+UI）

相同的组件机制，但服务器在MCPB包内本地运行。当组件需要驱动**本地**应用程序时使用此方案——例如，一个浏览实际本地磁盘的文件选择器，一个控制桌面应用程序的对话框。

对于MCPB打包机制，请参考**`build-mcpb`**技能。以下内容适用于两种形态。

---

## 组件如何附加到工具

支持组件的工具有两个**独立的注册**：

1. **工具**通过`_meta.ui.resourceUri`声明UI资源。其处理程序返回纯文本/JSON——**不是**HTML。
2. **资源**单独注册并提供HTML。

当Claude调用工具时，主机看到`_meta.ui.resourceUri`，获取该资源，在iframe中渲染它，并通过`ontoolresult`事件将工具的返回值管道输入iframe。

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod";

const server = new McpServer({ name: "contacts", version: "1.0.0" });

// 1. 工具——返回数据，声明要显示的UI
registerAppTool(server, "pick_contact", {
  description: "打开交互式联系人选择器",
  annotations: { title: "选择联系人", readOnlyHint: true },
  inputSchema: { filter: z.string().optional() },
  _meta: { ui: { resourceUri: "ui://widgets/contact-picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter);
  // 纯JSON——组件通过ontoolresult接收此数据
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

// 2. 资源——提供HTML
registerAppResource(
  server,
  "Contact Picker",
  "ui://widgets/contact-picker.html",
  {},
  async () => ({
    contents: [{
      uri: "ui://widgets/contact-picker.html",
      mimeType: RESOURCE_MIME_TYPE,
      text: pickerHtml,  // 你的HTML字符串
    }],
  }),
);
```

URI方案`ui://`是约定。MIME类型必须是`RESOURCE_MIME_TYPE`（`"text/html;profile=mcp-app"`）——这是主机知道将其作为交互式iframe渲染而不是仅显示源代码的方式。

---

## 组件运行时——`App`类

在iframe内，你的脚本通过`@modelcontextprotocol/ext-apps`中的`App`类与主机通信。这是一个**持久的双向连接**——只要对话保持活跃，组件就会保持活跃，接收新的工具结果并发送用户操作。

```html
<script type="module">
  /* ext-apps bundle在构建时内联→ globalThis.ExtApps */
  /*__EXT_APPS_BUNDLE__*/
  const { App } = globalThis.ExtApps;

  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});

  // 在连接之前设置处理程序
  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    render(contacts);
  };

  await app.connect();

  // 之后，当用户点击某物时：
  function onPick(contact) {
    app.sendMessage({
      role: "user",
      content: [{ type: "text", text: `选择的联系人：${contact.id}` }],
    });
  }
</script>
```

`/*__EXT_APPS_BUNDLE__*/`占位符在启动时由服务器替换为`@modelcontextprotocol/ext-apps/app-with-deps`的内容——有关此操作的必要性和重写片段，请参阅`references/iframe-sandbox.md`。**不要** `import { App } from "https://esm.sh/..."`；iframe的CSP阻止了传递依赖项获取，组件将渲染为空白。

| 方法 | 方向 | 用于 |
|---|---|---|
| `app.ontoolresult = fn` | 主机→组件 | 接收工具的返回值 |
| `app.ontoolinput = fn` | 主机→组件 | 接收工具的输入参数（Claude传递的） |
| `app.sendMessage({...})` | 组件→主机 | 将消息注入对话 |
| `app.updateModelContext({...})` | 组件→主机 | 静默更新上下文（无可见消息） |
| `app.callServerTool({name, arguments})` | 组件→服务器 | 在你的服务器上调用另一个工具 |
| `app.openLink({url})` | 组件→主机 | 在新标签页中打开URL（沙盒阻止`window.open`） |
| `app.getHostContext()` / `app.onhostcontextchanged` | 主机→组件 | 主题、主机CSS变量、`containerDimensions`、`displayMode`、`deviceCapabilities` |
| `app.requestDisplayMode({mode})` | 组件→主机 | 请求`inline` / `pip` / `fullscreen` |
| `app.downloadFile({name, mimeType, content})` | 组件→主机 | 主机中介下载（base64内容） |
| `new App(info, caps, {autoResize: true})` | — | iframe高度跟踪渲染内容 |

`sendMessage`是典型的“用户选择了某物，告诉Claude”路径。`updateModelContext`是用于Claude应了解但不应杂乱聊天状态的情况。`openLink`是**必需**的任何外部导航——`window.open`和`<a target="_blank">`被沙盒属性阻止。

**组件无法执行的操作：**
- 访问主机页面的DOM、cookies或存储
- 向任意原点发起网络调用（CSP受限——通过`callServerTool`路由）
- 打开弹窗或直接导航——使用`app.openLink({url})`
- 可靠地加载远程图像——在服务器端内联为`data:` URL

保持组件**小而单一用途**。选择器用于选择。图表用于显示。不要在iframe内构建整个子应用程序——将其拆分为具有专注组件的多个工具。

---

## 框架：最小的选择器组件

**安装：**

```bash
npm install @modelcontextprotocol/sdk @modelcontextprotocol/ext-apps zod express
```

**服务器（`src/server.ts`）：**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE }
  from "@modelcontextprotocol/ext-apps/server";
import express from "express";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { z } from "zod";

const require = createRequire(import.meta.url);
const server = new McpServer({ name: "contact-picker", version: "1.0.0" });

// 将ext-apps浏览器bundle内联到组件HTML中。
// iframe的CSP阻止CDN脚本获取——捆绑是强制性的。
const bundle = readFileSync(
  require.resolve("@modelcontextprotocol/ext-apps/app-with-deps"), "utf8",
).replace(/export\{([^}]+)\};?\s*$/, (_, body) =>
  "globalThis.ExtApps={" +
  body.split(",").map((p) => {
    const [local, exported] = p.split(" as ").map((s) => s.trim());
    return `${exported ?? local}:${local}`;
  }).join(",") + "};",
);
const pickerHtml = readFileSync("./widgets/picker.html", "utf8")
  .replace("/*__EXT_APPS_BUNDLE__*/", () => bundle);

registerAppTool(server, "pick_contact", {
  description: "打开交互式联系人选择器。用户选择一个联系人。",
  annotations: { title: "选择联系人", readOnlyHint: true },
  inputSchema: { filter: z.string().optional().describe("姓名/电子邮件前缀过滤器") },
  _meta: { ui: { resourceUri: "ui://widgets/picker.html" } },
}, async ({ filter }) => {
  const contacts = await db.contacts.search(filter ?? "");
  return { content: [{ type: "text", text: JSON.stringify(contacts) }] };
});

registerAppResource(server, "Contact Picker", "ui://widgets/picker.html", {},
  async () => ({
    contents: [{ uri: "ui://widgets/picker.html", mimeType: RESOURCE_MIME_TYPE, text: pickerHtml }],
  }),
);

const app = express();
app.use(express.json());
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
app.listen(process.env.PORT ?? 3000);
```

对于仅限本地的组件应用（驱动桌面应用、读取本地文件），将传输替换为`StdioServerTransport`并通过`build-mcpb`技能打包。

**组件（`widgets/picker.html`）：**

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { font: 14px system-ui; margin: 0; }
  ul { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; }
  li { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #eee; }
  li:hover { background: #f5f5f5; }
  .sub { color: #666; font-size: 12px; }
</style>
<ul id="list"></ul>
<script type="module">
/*__EXT_APPS_BUNDLE__*/
const { App } = globalThis.ExtApps;
(async () => {
  const app = new App({ name: "ContactPicker", version: "1.0.0" }, {});
  const ul = document.getElementById("list");

  app.ontoolresult = ({ content }) => {
    const contacts = JSON.parse(content[0].text);
    ul.innerHTML = "";
    for (const c of contacts) {
      const li = document.createElement("li");
      li.innerHTML = `<div>${c.name}</div><div class="sub">${c.email}</div>`;
      li.addEventListener("click", () => {
        app.sendMessage({
          role: "user",
          content: [{ type: "text", text: `选择的联系人：${c.id} (${c.name})` }],
        });
      });
      ul.append(li);
    }
  };

  await app.connect();
})();
</script>
```

见`references/widget-templates.md`获取更多组件形态。

---

## 设计要点可为你节省重写

**每个工具一个组件。** 抵制构建一个做所有事情的巨型组件的冲动。一个工具→一个专注的组件→一个清晰的结果形态。Claude对这些推理得更好。

**工具描述必须提及组件。** Claude在决定调用什么时只看到工具描述。“打开交互式选择器”在描述中是让Claude选择而不是猜测ID的原因。

**组件在运行时是可选的。** 不支持应用界面的主机简单地忽略`_meta.ui`并正常渲染工具的文本内容。由于你的工具处理程序已经返回有意义的文本/JSON（组件的数据），降级是自动的——Claude直接看到数据而不是通过组件。

**对于只显示数据的工具，不要阻塞组件结果。** 一个只*显示*数据的组件（图表、预览）不应需要用户操作来完成。在相同结果中返回显示组件和文本摘要，以便Claude可以在等待中继续推理。

**按项目数量而不是工具数量进行布局分支。** 如果一个用例是“详细显示一个结果”，另一个是“并排显示多个结果”，不要创建两个工具——创建一个接受`items[]`的工具，并让组件选择布局：`items.length === 1` → 详情视图，`> 1` → 轮播。保持服务器模式简单，并让Claude自然决定数量。

**将Claude的推理放在负载中。** 每个项目上的短`note`字段（为什么Claude选择了它）作为卡片上的调用突出显示，使用户的选择与推理直接对齐。在工具描述中提及此字段，以便Claude填充它。

**在服务器端规范化图像形态。** 如果你的数据源返回具有极不规则的宽高比的图像，在获取数据URL之前将其重写为可预测的变体（例如方形边界）。然后给组件的图像容器一个固定的`aspect-ratio` + `object-fit: contain`，以便所有内容居中排列。

**遵循主机主题。** `app.getHostContext()?.theme`（在`connect()`之后）加上`app.onhostcontextchanged`进行实时更新。在`<html>`上切换`.dark`类，将颜色保存在CSS自定义属性中，带有`:root.dark {}`覆盖块，设置`color-scheme`。在暗色模式下禁用`mix-blend-mode: multiply`——它会使图像消失。

---

## 测试

**Claude桌面**——当前构建仍然需要`command`/`args`配置形状（没有原生`"type": "http"`）。用`mcp-remote`包装并强制`http-only`传输，以便SSE探测不会吞噬组件能力协商：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/mcp",
               "--allow-http", "--transport", "http-only"]
    }
  }
}
```

桌面会激进地缓存UI资源。编辑组件HTML后，**完全退出**（⌘Q / Alt+F4，不是窗口关闭）并重新启动以强制冷资源重新获取。

**无头JSON-RPC循环**——无需点击桌面即可快速迭代：

```bash
# test.jsonl — 每行一个JSON-RPC消息
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"your_tool","arguments":{...}}}

(cat test.jsonl; sleep 10) | npx mcp-remote http://localhost:3000/mcp --allow-http
```

`sleep`保持stdin打开足够长的时间以收集所有响应。用`jq`或Python单行解析jsonl输出。

**组件开发循环**——通过在普通GET路由中提供内联组件HTML并使用查询参数从`ExtApps`占位符触发`ontoolresult`，完全避免⌘Q-重新启动周期：

```ts
app.get("/widget-preview", (_req, res) => {
  const shim = `globalThis.ExtApps={applyHostStyleVariables:()=>{},App:class{
    constructor(){this.h={}} ontoolresult;onhostcontextchanged;
    async connect(){const p=new URLSearchParams(location.search).get("payload");
      if(p)this.ontoolresult?.({content:[{type:"text",text:p}]});}
    getHostContext(){return{theme:"light"}}
    sendMessage(m){console.log("sendMessage",m)} updateModelContext(){}
    callServerTool(){return Promise.resolve({content:[]})} openLink(){} downloadFile(){}
  }};`;
  res.type("html").send(widgetHtml.replace("/*__EXT_APPS_BUNDLE__*/", shim));
});
```

在`http://localhost:3000/widget-preview?payload={"rows":[...]}`正常浏览器标签页中打开，并使用普通开发工具进行迭代。

**主机降级**——使用没有应用界面的主机（或MCP Inspector）并确认工具的文本内容优雅降级。

**CSP调试**——打开iframe自己的开发者工具控制台。CSP违规是组件静默失败（空白矩形，主控制台没有错误）的首要原因。见`references/iframe-sandbox.md`。

---

## 参考文件

- `references/iframe-sandbox.md` — CSP/沙盒约束，捆绑内联模式，图像处理，主机主题
- `references/widget-templates.md` — 可重用的HTML框架，用于选择器 / 确认 / 进度 / 显示
- `references/apps-sdk-messages.md` — `App`类API：组件 ↔ 主机 ↔ 服务器消息传递，生命周期 & 超会话
- `references/payload-budgeting.md` — 主机工具结果大小限制，修剪后截断，通过`callServerTool`的重型资产
- `references/abuse-protection.md` — Anthropic出口CIDR，分层速率限制，`trust proxy`，响应缓存
- `references/directory-checklist.md` — 连接器目录提交的预检
