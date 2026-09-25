## 兄弟技能（仅限本地）

兄弟 CloudBase 技能会与此技能一同部署。使用本地相对路径，例如 `../auth-tool-cloudbase/SKILL.md`。

如果此环境中缺少引用的兄弟技能文件，请提示用户安装完整的 CloudBase 插件（或缺失的技能）。**不要**将远程技能或协议的 Markdown 通过 HTTP 获取到代理上下文中。

**跨领域协议**（代码更改或部署前必须满足的要求）：
- 变更安全协议：`../cloudbase-platform/references/protocols/change-safety-protocol.md`
- 部署门禁：`../cloudbase-platform/references/protocols/deployment-gate.md`

# Web 开发

## 激活契约

### 首次使用时

- 请求实现、集成、调试、构建、部署或验证 Web 前端或静态网站。
- 设计方向已确定，或用户要求工程执行而非视觉探索。
- 工作涉及 React、Vue、Vite、路由、浏览器验证或 CloudBase Web 集成。

### 编写代码前需阅读

- 任务包含项目结构、框架约定、构建配置、部署、路由或前端测试和验证流程。
- 请求包含 UI 实现，但视觉方向已固定；否则先阅读 `ui-design`。
- **⚠️ 任何涉及界面样式、布局、配色方案或字体选择的任务——在编写第一行 CSS/Tailwind 之前，你必须加载 `ui-design` 技能并输出设计规范。** 跳过此步骤会导致前端样式退化为通用 AI 模板默认值。`ui-design` 技能必须在任何视觉实现开始前加载，不能在用户抱怨外观后追溯加载。

### 然后还需阅读

- 通用 React / Vue / Vite 指南 -> `frameworks.md`
- 浏览器流程检查或页面验证 -> `browser-testing.md`
- 登录流程 -> `../auth-tool-cloudbase/SKILL.md`，然后 `../auth-web-cloudbase/SKILL.md`
- CloudBase 官方账号 JSAPI 支付、原生二维码支付或 WeChat OAuth -> `../cloudbase-wechat-integration/SKILL.md`（官方文档：`https://docs.cloudbase.net/integration/introduce.md`）
- CloudBase 数据库工作 -> 匹配的数据库技能

### 不适用于

- 视觉方向设置、原型优先设计工作或纯美学探索。
- 小程序、原生 App 或纯后端服务。
- WeChat 支付或官方账号 OAuth 契约细节；识别 Web 表面后使用 `cloudbase-wechat-integration`。

### 常见错误/注意事项

- 在明确任务是否为设计执行或工程执行前开始实现。
- 将框架设置、部署和 CloudBase 集成问题混为一谈，进行模糊变更。
- 将云函数视为 Web 身份验证的默认解决方案。
- UI 或路由变更后跳过浏览器级验证。
- **带历史模式的 SPA 与 CloudBase 静态托管**：使用历史模式（React Router / Vue Router）部署单页应用，但未将静态托管“404 错误文档”配置为 `index.html`。这会导致用户刷新或直接访问任何子路由时出现 `NoSuchKey` / 404 错误，因为静态托管在路径中查找文件，而不是将 SPA 路由传递给 `index.html`。
- 在现有应用中，在修补当前处理程序和服务之前，绕道进行 UI 重设计或广泛的代码库扫描。

## 工程宪章（不可协商）

这些规则优先于便利性。在说“完成”之前，将它们视为一道门坎。

### 1. TypeScript — 不要抑制类型系统

- **不要使用 `any` 来绕过类型错误。** 不是 `: any`，不是 `as any`，不是 `@ts-ignore`，不是 `@ts-nocheck`，不是没有书面理由的 `@ts-expect-error`。`any` 会无声传播并破坏此项目唯一的编译时安全网。
- 当出现类型错误时，修复根本原因：
  - 缺失/错误的库类型 → 安装 `@types/...`，或缩小导入范围，或为实际使用的形状编写精确的 `interface` / `type`。
  - 边界处形状确实未知（来自 API 的 JSON、`postMessage` 负载、`window.*` 注入）→ 将其类型化为 `unknown` 并使用类型守卫（`typeof`、`in`、一个区分字段，或 `zod` / 等效方案）进行缩小。
  - 第三方类型错误 → 在本地 `.d.ts` 中通过 `declare module` 进行扩展，而不是 `any`。
  - 真正动态的情况（例如通用事件总线）→ 使用带约束的泛型 `<T>`，而不是 `any`。
- `unknown` + 缩小是可接受的逃生通道。`any` 不是。
- 如果你确实无法避免为特定行使用 `any`（极为罕见），请留下一行注释说明**原因**和**什么可以移除它**，以便审查者可以审计。
- 相同的精神适用于 ESLint：不要随意添加 `// eslint-disable` 来屏蔽真实信号。修复规则违规，或在禁用前讨论。

### 2. 在声称完成前自我验证

在做出任何非平凡的代码或配置更改之前，你必须首先遵循 `cloudbase-platform/references/protocols/change-safety-protocol.md` 中的变更安全协议（声明影响 → 用户确认 → 编辑后验证）。
在静态托管发布或自定义域名工作之前，完成 `cloudbase-platform/references/protocols/deployment-gate.md` 中的检查。

没有证据说“我已实现” / “修复了” / “应该可以工作了”是不接受的。在声明完成前，你必须实际运行检查并报告结果。

**静态/构建层（始终适用，当适用时）：**

- `tsc --noEmit`（或 `vue-tsc --noEmit`）顺利通过——零错误，零你添加的抑制诊断。
- `eslint` / 项目代码检查器在更改文件上通过。
- 项目的构建命令（`npm run build` / `pnpm build` / `vite build`）完成而没有你引入的新警告。
- 如果存在并覆盖了触及的区域，项目的单元测试通过。

**运行时/浏览器层（每当更改影响渲染、路由、表单、身份验证或异步流程时）：**

- 使用 **`agent-browser`** 工具实际打开页面并重现用户可见流程。遵循 `browser-testing.md` 中的具体工作流程。
- 确认：目标路由加载，你声称修复的交互按你声称的方式工作，没有引入新的控制台错误，且相邻路由没有回归。
- 记录你检查了什么（路由、操作、预期结果、实际结果）。

**只有当两层都通过后**，你才能说任务完成。如果任何一层无法本地执行（例如被凭证阻止、缺少后端、付费 API），请明确说明哪些步骤仍需验证——不要含糊其辞。

### 3. 不要掩盖失败

- 不要用 `try { ... } catch {}` 将错误的逻辑包裹起来以使其消失。
- 不要删除或跳过失败的测试以使 CI 变绿——修复它，或解释为什么测试实际上错误并更改测试（附带理由）。
- 不要因为“代码可以编译”就标记任务完成。编译是最低要求，不是目标。

## 何时使用此技能

用于 Web 工程工作，例如：

- 实现 React 或 Vue 页面和组件
- 设置或维护基于 Vite 的前端项目
- 处理路由、数据加载、表单和构建配置
- 运行基于浏览器的验证和冒烟测试
- 集成 CloudBase Web SDK 和静态托管，当项目需要 CloudBase 功能时

**不要用于：**
- 仅 UI 方向或视觉系统设计；使用 `ui-design`
- 小程序开发；使用 `miniprogram-development`
- 后端服务实现；使用 `cloudrun-development` 或 `cloud-functions`

## 如何使用此技能（针对编码代理）

1. **明确执行表面**
   - 确认任务是否为框架设置、页面实现、调试、部署、验证或 CloudBase 集成。
   - 将工作范围限制在实际的 Web 应用表面，而不是扩散到无关的后端更改。
   - 如果工作空间是带有 TODO 的现有应用，将其视为有针对性的修复任务，而不是绿地构建。

2. **遵循框架和构建约定**
   - 如果已存在项目堆栈，优先使用它。
   - 对于新工作，除非代码库或用户约束另有说明，否则将 Vite 视为默认打包器。
   - 将可重用的应用代码放在 `src` 下，构建输出放在 `dist` 下，除非代码库已使用不同的约定。
   - 在结构固定的现有应用中，在阅读广泛文档前检查已拥有流程的文件：`src/lib/backend.*`，`src/lib/auth.*`，`src/lib/*service.*`，路由守卫，以及绑定到提交按钮的页面处理程序。

3. **通过浏览器验证，而不仅仅是阅读代码**
   - 对于交互、路由、渲染或回归检查，使用 `agent-browser` 工作流从 `browser-testing.md`。
   - 在声称前端工作完成前，优先使用轻量级冒烟验证更改的流程。

4. **将 CloudBase 视为集成分支**
   - 仅当项目实际需要 CloudBase 平台功能时，使用 CloudBase Web SDK 和静态托管指南。
   - 使用 `auth-tool-cloudbase` 和 `auth-web-cloudbase` 进行登录或提供者就绪，而不是重新描述这些流程。

## 核心工作流程

### 1. 选择正确的工程路径

- **React / Vue 功能工作**：在应用的现有组件、路由和状态约定内实现
- **新 Web 应用**：除非代码库已标准化其他工具链，否则优先使用 Vite
- **调试和回归**：在浏览器中重现，缩小到特定页面或交互，然后修补
- **CloudBase 集成**：仅在基础前端路径清晰后，才连接 Web SDK、身份验证、数据或静态托管

### 2. 使实现扎根于项目现实

- 遵循代码库的包管理器、脚本和代码检查/测试模式
- 除非用户明确要求，否则避免框架重写
- 优先满足任务的最小可行页面/组件/配置更改
- 在基于 TODO 的应用中，直接完成现有实现，而不是创建并行的帮助程序、示例页面或分离的原型

### 3. 明确验证更改的流程

- 当可用时，运行相关的本地构建 / 代码检查 / 类型检查 / 测试命令。干净的 `tsc --noEmit` 和干净的构建是最低标准——不是正确性的证明。
- 对于任何用户可见的（路由、表单、渲染、身份验证、异步流程），使用 **`agent-browser`** 在浏览器中打开受影响的页面或流程。单独阅读代码不足以作为证据——见上述工程宪章。
- 记录检查了什么：路由、操作、预期结果、实际结果，以及任何剩余差距。

## CloudBase Web 集成

仅当 Web 项目需要 CloudBase 平台功能时使用此部分。

### Web SDK 规则

- 对于 React、Vue、Vite 和其他基于打包器的项目，优先使用 npm 安装：`npm install @cloudbase/js-sdk`
- 仅用于静态 HTML 页面、快速演示、嵌入式片段或 README 示例的 CDN：`https://static.cloudbase.net/cloudbase-js-sdk/latest/cloudbase.full.js`
- 仅使用文档化的 CloudBase Web SDK API；不要编造方法或选项
- 保持共享的 `app` 或 `auth` 实例，而不是每次调用都重新初始化
- 如果用户只提供环境别名、昵称或其他简称，在编写 SDK 初始化代码、控制台链接或配置文件之前，将其解析为标准的完整 `EnvId`。不要将类似别名的简短形式直接传递给 `cloudbase.init({ env })`。

### 身份验证边界

- 身份验证必须使用 CloudBase SDK 内置功能
- 不要将 Web 登录逻辑移入云函数
- 对于提供者就绪、登录方法设置或发布密钥问题，路由到 `auth-tool-cloudbase` 和 `auth-web-cloudbase`

### 静态托管默认值

- 构建后再部署
- 优先使用相对资源路径以兼容静态托管
- 当项目缺乏服务器端路由重写时，默认使用哈希路由
- 如果用户未指定根路径，默认避免直接部署到网站根目录
- **SPA 路由（历史模式）**：当使用 React Router / Vue Router 的历史模式（非哈希模式）时，配置 CloudBase 静态托管的 **“404 错误文档”** 为 `index.html`。否则刷新或直接访问任何子路由返回 `NoSuchKey` / 404 错误，因为静态托管在路径中查找文件，而不是让 SPA 处理路由。

  使用 MCP 工具应用此配置：
  ```json
  manageHosting({ action: "setWebsiteDocument", indexDocument: "index.html", errorDocument: "index.html" })
  ```

  然后验证：
  ```json
  queryHosting({ action: "websiteConfig" })
  ```

### CloudBase 快速入门

```js
// npm install @cloudbase/js-sdk
import cloudbase from "@cloudbase/js-sdk";

const app = cloudbase.init({
  env: "your-full-env-id", // 从 queryEnv 或控制台解析的标准完整 CloudBase 环境ID
});

const auth = app.auth
```
