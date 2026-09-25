# Trigger.dev 配置

使用 `trigger.config.ts` 配置您的 Trigger.dev 项目并构建扩展。

## 使用场景

- 设置新的 Trigger.dev 项目
- 添加数据库支持（Prisma、TypeORM）
- 配置浏览器自动化（Playwright、Puppeteer）
- 添加媒体处理（FFmpeg）
- 从任务中运行 Python 脚本
- 同步环境变量
- 安装系统包

## 基本配置

```ts
// trigger.config.ts
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "<project-ref>",
  dirs: ["./trigger"],
  runtime: "node", // "node", "node-22" 或 "bun"
  logLevel: "info",

  retries: {
    enabledInDev: false,
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
      factor: 2,
    },
  },

  build: {
    extensions: [], // 在此处添加扩展
  },
});
```

## 常用构建扩展

### Prisma

```ts
import { prismaExtension } from "@trigger.dev/build/extensions/prisma";

export default defineConfig({
  // ...
  build: {
    extensions: [
      prismaExtension({
        schema: "prisma/schema.prisma",
        migrate: true,
        directUrlEnvVarName: "DIRECT_DATABASE_URL",
      }),
    ],
  },
});
```

### Playwright (浏览器自动化)

```ts
import { playwright } from "@trigger.dev/build/extensions/playwright";

extensions: [
  playwright({
    browsers: ["chromium"], // 或 ["chromium", "firefox", "webkit"]
  }),
]
```

### Puppeteer

```ts
import { puppeteer } from "@trigger.dev/build/extensions/puppeteer";

extensions: [puppeteer()]

// 设置环境变量：PUPPETEER_EXECUTABLE_PATH="/usr/bin/google-chrome-stable"
```

### FFmpeg (媒体处理)

```ts
import { ffmpeg } from "@trigger.dev/build/extensions/core";

extensions: [
  ffmpeg({ version: "7" }),
]
// 自动设置 FFMPEG_PATH 和 FFPROBE_PATH
```

### Python

```ts
import { pythonExtension } from "@trigger.dev/build/extensions/python";

extensions: [
  pythonExtension({
    scripts: ["./python/**/*.py"],
    requirementsFile: "./requirements.txt",
    devPythonBinaryPath: ".venv/bin/python",
  }),
]

// 在任务中使用：
const result = await python.runScript("./python/process.py", ["arg1"]);
```

### 系统包 (apt-get)

```ts
import { aptGet } from "@trigger.dev/build/extensions/core";

extensions: [
  aptGet({
    packages: ["imagemagick", "curl"],
  }),
]
```

### 额外文件

```ts
import { additionalFiles } from "@trigger.dev/build/extensions/core";

extensions: [
  additionalFiles({
    files: ["./assets/**", "./templates/**"],
  }),
]
```

### 环境变量同步

```ts
import { syncEnvVars } from "@trigger.dev/build/extensions/core";

extensions: [
  syncEnvVars(async (ctx) => {
    return [
      { name: "API_KEY", value: await getSecret(ctx.environment) },
      { name: "ENV", value: ctx.environment },
    ];
  }),
]
```

## 常用扩展组合

### 全栈 Web 应用

```ts
extensions: [
  prismaExtension({ schema: "prisma/schema.prisma", migrate: true }),
  additionalFiles({ files: ["./assets/**"] }),
  syncEnvVars(async (ctx) => [...envVars]),
]
```

### AI/ML 处理

```ts
extensions: [
  pythonExtension({
    scripts: ["./ai/**/*.py"],
    requirementsFile: "./requirements.txt",
  }),
  ffmpeg({ version: "7" }),
]
```

### 网页抓取

```ts
extensions: [
  playwright({ browsers: ["chromium"] }),
  additionalFiles({ files: ["./selectors.json"] }),
]
```

## 全局生命周期钩子

```ts
export default defineConfig({
  // ...
  onStartAttempt: async ({ payload, ctx }) => {
    console.log("任务开始:", ctx.task.id);
  },
  onSuccess: async ({ payload, output, ctx }) => {
    console.log("任务成功");
  },
  onFailure: async ({ payload, error, ctx }) => {
    console.error("任务失败:", error);
  },
});
```

## 机器默认值

```ts
export default defineConfig({
  // ...
  defaultMachine: "medium-1x",
  maxDuration: 300, // 秒
});
```

## 远程监控集成

```ts
import { PrismaInstrumentation } from "@prisma/instrumentation";

export default defineConfig({
  // ...
  telemetry: {
    instrumentations: [new PrismaInstrumentation()],
  },
});
```

## 最佳实践

1. **固定版本** 以实现可重复的构建
2. **使用 `syncEnvVars`** 处理动态密钥
3. **将原生模块** 添加到 `build.external` 数组
4. **使用 `--log-level debug --dry-run` 进行调试**

扩展仅影响部署，不影响本地开发。

请参阅 `references/config.md` 获取完整文档。
