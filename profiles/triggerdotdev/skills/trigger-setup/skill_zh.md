# 使用 Trigger.dev 入门

在现有项目中设置 Trigger.dev。最终状态是：安装了 SDK，`trigger.config.ts` 指向一个项目引用，存在 `/trigger` 目录且至少包含一个导出的任务，并且 `trigger dev` 正在运行，以便任务显示在仪表板上。

最快的方式是 CLI 自带的向导，它会执行以下所有机械步骤，并提供安装 MCP 服务器和这些代理技能的选项：

```bash
npx trigger.dev@latest init
```

在可以的情况下优先使用 `init`。当 `init` 不适用时（如单体仓库、需要扩展的现有配置或非交互式环境），请执行下面的手动步骤。

## 需要人工参与的两大步骤

大部分设置都是可自动化的，但有两大步骤需要人工操作且无法在无头环境下完成。当你遇到这些步骤时，停止并要求用户执行它们，然后继续：

1. **CLI 身份验证。** `npx trigger.dev@latest login` 会打开浏览器让用户登录。如果他们没有账户，请先指向 https://cloud.trigger.dev（或自托管实例）。你不能替他们完成这一步。
2. **密钥和项目引用。** `TRIGGER_SECRET_KEY` 和项目引用（`proj_...`）来自仪表板。要求用户从项目的 API 密钥页面复制 **DEV** 密钥，并选择或创建项目以便你获取其引用。`trigger init` 在用户登录后可以交互式地选择项目。

将这些视为交接：明确说明你需要什么，等待用户，然后继续。

## 手动设置

### 1. 身份验证（人工步骤）

```bash
npx trigger.dev@latest login
# 自托管：
npx trigger.dev@latest login --api-url https://your-trigger-instance.com
```

### 2. 安装包

`@trigger.dev/sdk` 是运行时依赖项；`@trigger.dev/build` 是开发依赖项。将两者都固定为与运行 `trigger.dev` CLI 相同的版本；CLI 在 `dev`/`deploy` 过程中会警告版本不匹配。

```bash
npm add @trigger.dev/sdk@latest
npm add --save-dev @trigger.dev/build@latest
```

### 3. 编写 `trigger.config.ts`

在项目根目录下创建它（或 `trigger.config.mjs` 用于 JavaScript）。`project` 引用和 `dirs` 是唯一必需的字段。

```ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "<project ref>", // 例如 "proj_abc123"，来自仪表板
  dirs: ["./src/trigger"], // 你的任务所在位置
  maxDuration: 3600,
  retries: {
    enabledInDev: false,
    default: { maxAttempts: 3, factor: 2, minTimeoutInMs: 1000, maxTimeoutInMs: 10000, randomize: true },
  },
});
```

通过添加 `runtime: "bun"` 使用 Bun 运行时。扩展（`prismaExtension`、`puppeteer`、`additionalFiles` 等）来自 `@trigger.dev/build`，并放在 `build.extensions` 中。

### 4. 添加第一个任务

创建与 `dirs` 匹配的目录，并从其中导出一个任务。每个任务必须是一个具有项目唯一 `id` 的命名导出。

```ts
// src/trigger/example.ts
import { task } from "@trigger.dev/sdk";

export const helloWorld = task({
  id: "hello-world",
  run: async (payload: { name: string }) => {
    return { message: `Hello ${payload.name}!` };
  },
});
```

### 5. 配置 tsconfig 和 gitignore

将 `trigger.config.ts` 添加到 `tsconfig.json` 中的 `include` 数组，并将 `.trigger` 添加到 `.gitignore`（CLI 将本地开发状态写入此处）。

```jsonc
// tsconfig.json
{ "include": ["trigger.config.ts" /* ...现有内容 */] }
```

```bash
# .gitignore
.trigger
```

### 6. 设置密钥（人工步骤）

要从自己的代码触发任务，将 `TRIGGER_SECRET_KEY` 设置为仪表板 API 密钥页面上的 **DEV** 密钥。自托管用户也需要设置 `TRIGGER_API_URL`。

```bash
# .env（或 Next.js 的 .env.local）
TRIGGER_SECRET_KEY=tr_dev_xxxxxxxx
```

### 7. 运行开发服务器

```bash
npx trigger.dev@latest dev
```

保持运行状态。任务会注册到仪表板，用户可以在任务的测试页面触发测试运行。首次运行时，CLI 会提供安装 MCP 服务器和代理技能的选项；建议都安装。

## 从你的应用中触发

一旦任务存在，通过 **仅类型** 的导入从后端代码触发它，这样任务代码永远不会打包到你的应用中。通过 ID 触发，而不是调用任务对象。

```ts
import { tasks } from "@trigger.dev/sdk";
import type { helloWorld } from "@/trigger/example"; // 仅类型

const handle = await tasks.trigger<typeof helloWorld>("hello-world", { name: "Ada" });
```

`TRIGGER_SECRET_KEY` 必须在运行此代码的位置设置。框架特定内容在 Next.js / Remix / Node.js 指南中。

## 单体仓库

两种布局都受支持：将任务放在共享包中（`@repo/tasks` 具有自己独立的 `trigger.config.ts`，通过 `workspace:*` 消费），或直接在需要它的应用中安装 Trigger.dev。从包含 `trigger.config.ts` 的目录运行 `trigger dev`。在搭建任何布局之前，请查看手动设置文档中的完整 Turborepo 示例。

## 常见错误

1. **尝试无头方式执行仅人工步骤。** 你无法完成 `trigger login` 或为用户读取仪表板密钥。
   - 错误：在代理会话中启动 `trigger login` 并等待它完成。
   - 正确：要求用户登录并粘贴 DEV 密钥，然后继续。

2. **CLI 和 SDK 版本不匹配。** `trigger.dev` CLI 与 `@trigger.dev/sdk` 的主版本不同会破坏 `dev`/`deploy`。
   - 错误：使用旧版 SDK 的 `npx trigger.dev@latest dev`。
   - 正确：保持 `trigger.dev`、`@trigger.dev/sdk` 和 `@trigger.dev/build` 在相同版本。

3. **从 `@trigger.dev/sdk/v3` 导入或使用 `client.defineJob()`。** 两者都已过时。
   - 正确：始终从 `@trigger.dev/sdk` 导入；使用 `task()` 定义工作。

4. **任务未导出或不在 `dirs` 中。** 如果任务不是配置目录中的命名导出，则不会被选中。
   - 正确：在 `dirs` 路径下的文件中 `export const ... = task({ ... })`。

5. **将任务实例导入后端代码。** 这会打包任务。
   - 错误：在路由处理器中 `import { helloWorld } from "@/trigger/example"`。
   - 正确：`import type { helloWorld }` 加上 `tasks.trigger<typeof helloWorld>("hello-world", payload)`。

6. **忘记 `TRIGGER_SECRET_KEY`。** 没有它从你的应用触发会失败；一旦 CLI 登录，开发服务器本身就可以工作。

## 参考

兄弟技能：

- **trigger-tasks**：在设置完成后编写任务：重试、等待、队列、计划任务、触发，以及完整的 `trigger.config.ts`。
- **trigger-realtime**：在前端显示实时运行状态。
- **trigger-authoring-chat-agent** 和 **trigger-chat-agent-advanced**：用于构建 AI 聊天代理。

文档：

- [快速入门](https://trigger.dev/docs/quick-start)
- [手动设置](https://trigger.dev/docs/manual-setup)
- [配置文件](https://trigger.dev/docs/config/config-file)

## 版本

为 @trigger.dev/sdk 4.5.10 生成。升级后请重新运行 trigger.dev 技能安装器。
