# 创建 MCP 应用

构建在支持 MCP 的主机（如 Claude Desktop）内部运行的交互式 UI。MCP 应用将 MCP 工具与 HTML 资源结合，以显示丰富的交互式内容。

## 核心概念：工具 + 资源

每个 MCP 应用需要两个相互关联的部分：

1. **工具** - 由 LLM/主机调用，返回数据
2. **资源** - 提供打包的 HTML UI 以显示数据

工具的 `_meta.ui.resourceUri` 引用资源的 URI。

主机调用工具 → 主机渲染资源 UI → 服务器返回结果 → UI 接收结果。

## 快速入门决策树

### 框架选择

| 框架 | SDK 支持 | 适合 |
|-----------|-------------|----------|
| React | 提供 `useApp` 钩子 | 熟悉 React 的团队 |
| 纯 JavaScript | 手动生命周期 | 简单应用，无构建复杂度 |
| Vue/Svelte/Preact/Solid | 手动生命周期 | 框架偏好 |

### 项目上下文

**添加到现有 MCP 服务器：**
- 从 SDK 导入 `registerAppTool`, `registerAppResource`
- 使用 `_meta.ui.resourceUri` 添加工具注册
- 添加提供打包 HTML 的资源注册

**创建新的 MCP 服务器：**
- 使用传输（stdio 或 HTTP）设置服务器
- 注册工具和资源
- 使用 `vite-plugin-singlefile` 配置构建系统

## 获取参考代码

克隆 SDK 仓库以获取工作示例和 API 文档：

```bash
git clone --branch "v$(npm view @modelcontextprotocol/ext-apps version)" --depth 1 https://github.com/modelcontextprotocol/ext-apps.git /tmp/mcp-ext-apps
```

### 框架模板

从 `/tmp/mcp-ext-apps/examples/basic-server-{framework}/` 学习并调整：

| 模板 | 关键文件 |
|----------|-----------|
| `basic-server-vanillajs/` | `server.ts`, `src/mcp-app.ts`, `mcp-app.html` |
| `basic-server-react/` | `server.ts`, `src/mcp-app.tsx` (使用 `useApp` 钩子) |
| `basic-server-vue/` | `server.ts`, `src/App.vue` |
| `basic-server-svelte/` | `server.ts`, `src/App.svelte` |
| `basic-server-preact/` | `server.ts`, `src/mcp-app.tsx` |
| `basic-server-solid/` | `server.ts`, `src/mcp-app.tsx` |

每个模板包含：
- 使用 `registerAppTool` 和 `registerAppResource` 的 `server.ts`
- HTTP 和 stdio 传输设置的入口点 `main.ts`
- 带有生命周期处理器的客户端应用（例如 `src/mcp-app.ts`, `src/mcp-app.tsx`）
- 全局样式和主机样式变量回退的 `src/global.css`
- 使用 `vite-plugin-singlefile` 的 `vite.config.ts`
- 包含 `npm run` 脚本和所需依赖的 `package.json`
- 排除 `node_modules/` 和 `dist/` 的 `.gitignore`

### API 参考（源文件）

直接从 `/tmp/mcp-ext-apps/src/` 阅读 JSDoc 文档：

| 文件 | 内容 |
|------|----------|
| `src/app.ts` | `App` 类，处理程序 (`ontoolinput`, `ontoolresult`, `onhostcontextchanged`, `onteardown` 等)，生命周期 |
| `src/server/index.ts` | `registerAppTool`, `registerAppResource`, 辅助函数 |
| `src/spec.types.ts` | 所有类型定义：`McpUiHostContext`, `McpUiStyleVariableKey` (CSS 变量名), `McpUiResourceCsp` (CSP 配置) 等 |
| `src/styles.ts` | `applyDocumentTheme`, `applyHostStyleVariables`, `applyHostFonts` |
| `src/react/useApp.tsx` | React 应用的 `useApp` 钩子 |

### 高级模式

查看 `/tmp/mcp-ext-apps/docs/patterns.md` 获取详细配方：

- **仅应用工具** — `visibility: ["app"]`，从模型隐藏工具
- **轮询** — 实时仪表板，间隔管理
- **分块响应** — 大文件，分页，base64 编码
- **错误处理** — `isError`，通知模型失败
- **二进制资源** — 音频/视频等通过 `resources/read`，blob 字段
- **网络请求** — 资产，fetch，CSP，`_meta.ui.csp`，CORS，`_meta.ui.domain`
- **主机上下文** — 主题，样式，字体，安全区域偏移
- **全屏模式** — `requestDisplayMode`，显示模式更改
- **模型上下文** — `updateModelContext`，`sendMessage`，保持模型知情
- **视图状态** — `viewUUID`，localStorage，状态恢复
- **基于可见性的暂停** — IntersectionObserver，暂停动画/WebGL
- **流式输入** — `ontoolinputpartial`，渐进式渲染

### 参考主机实现

`/tmp/mcp-ext-apps/examples/basic-host/` 展示了实现支持 MCP 应用的主机的一种方式。现实中的主机（如 Claude Desktop）更复杂——使用 basic-host 进行本地测试和协议理解，而不是作为主机行为的保证。

## 关键实现注意事项

### 添加依赖

**始终**使用 `npm install` 添加依赖，而不是手动编写版本号：

```bash
npm install @modelcontextprotocol/ext-apps @modelcontextprotocol/client@^2.0.0 @modelcontextprotocol/server@^2.0.0 @modelcontextprotocol/node@^2.0.0 @modelcontextprotocol/express@^2.0.0 zod@^4.2.0 express cors
npm install -D typescript vite vite-plugin-singlefile concurrently cross-env @types/node @types/express @types/cors
```

ext-apps 2.x 需要 `@modelcontextprotocol/client`, `server`, `node`, `express` 分割的 MCP SDK 包 (`^2.0.0`)；`@modelcontextprotocol/core` 会传递进来。不要添加遗留的 `@modelcontextprotocol/sdk` v1 包或替换未发布的本地包。

### TypeScript 服务器执行

除非用户另有指定，否则使用 `tsx` 运行 TypeScript 服务器文件。例如：

```bash
npm install -D tsx

npm pkg set scripts.dev="cross-env NODE_ENV=development concurrently 'cross-env INPUT=mcp-app.html vite build --watch' 'tsx --watch main.ts'"
```

> [!NOTE]
> SDK 示例使用 `bun`，但生成的项目应默认为 `tsx` 以提高兼容性。

### 处理程序注册顺序

在调用 `app.connect()` 之前注册**所有**处理程序：

```typescript
const app = new App({ name: "My App", version: "1.0.0" });

// 首先注册处理程序
app.ontoolinput = (params) => { /* 处理输入 */ };
app.ontoolresult = (result) => { /* 处理结果 */ };
app.onhostcontextchanged = (ctx) => { /* 处理上下文 */ };
app.onteardown = async () => { return {}; };
// 等。

// 然后连接
await app.connect();
```

## 常见错误避免

1. **无文本回退** - 始终为非 UI 主机提供 `content` 数组
2. **缺少 CSP 配置** - MCP 应用 HTML 作为 MCP 资源提供，无同源服务器；所有网络请求（即使是到 `localhost`）都需要 CSP 配置
3. **CSP 或 CORS 配置在错误的 _meta 对象中** - `_meta.ui.csp` 和 `_meta.ui.domain` 应在 `registerAppResource()` 的读回调返回的 `contents[]` 对象中，而不是在 `registerAppResource()` 的配置对象中
4. **处理程序在 app.connect() 之后** - 在调用 `app.connect()` 之前注册**所有**处理程序
5. **无流式处理大输入** - 使用 `ontoolinputpartial` 在输入生成期间显示进度

## 测试

### 使用 basic-host

使用 basic-host 示例在本地测试 MCP 应用：

```bash
# 终端 1：构建并运行您的服务器
npm run build && npm run serve

# 终端 2：运行 basic-host (从克隆的仓库)
cd /tmp/mcp-ext-apps/examples/basic-host
npm install
SERVERS='["http://localhost:3001/mcp"]' npm run start
# 打开 http://localhost:8080
```

使用 JSON 数组配置 `SERVERS`（默认：`http://localhost:3001/mcp`）。

### 使用 sendLog 调试

将调试日志发送到主机应用（而不仅仅是 iframe 的开发者控制台）：

```typescript
await app.sendLog({ level: "info", data: "Debug message" });
await app.sendLog({ level: "error", data: { error: err.message } });
```
