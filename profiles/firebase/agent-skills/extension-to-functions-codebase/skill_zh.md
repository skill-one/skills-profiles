# 将 Firebase 扩展迁移至函数代码库及 npm 包

## 概述

将 Firebase 扩展迁移至以下目标之一：

1. **本地 Cloud Functions 代码库** (`functions/src/` 用于应用集成)。
1. **可发布的 npm 包**（可重用的开源包，导出 V2 函数）。

利用原生 Cloud Functions 功能（声明式 IAM、参数化配置、SDK 生命周期钩子），并使用解构兼容性遮罩层将第一代触发器现代化为第二代。

______________________________________________________________________

## 目标迁移工作流

- **目标 A：本地函数代码库**（用户端应用集成）

  - 输出：`functions/src/` 下的代码。配置在 `.env` 中。
  - 部署：`firebase deploy --only functions`。

- **目标 B：可发布的 npm 包 / 可共享包**

  - 输出：可重用的 npm 包，导出 V2 函数。
  - 配置：`package.json` 指定 `exports` 映射、`engines: { "node": ">=22" }` 以及
    `peerDependencies: { "firebase-functions": ">=6.0.0" }`。
  - 使用方式：消费者安装包并在 `index.ts` 中重新导出函数 (`export * from "<package-name>"`)。

______________________________________________________________________

## 核心规则与限制

### 1. 声明式 IAM 与 API（零本地开销）

使用原生 SDK 声明替代手动 `gcloud` 脚本或控制台指令：

- 使用 `requiresRole("roles/...")` 获取所需的 GCP IAM 权限。
- 使用 `requiresAPI("service.googleapis.com", "Description")` 获取 Google API。

### 2. 全局参数访问限制

- **在顶层模块加载作用域中永远不要调用 `.value()`。**
- 在 `onInit()` 或懒加载获取器中初始化全局 SDK 实例：
  ```typescript
  import { defineString } from "firebase-functions/params";
  import { onInit } from "firebase-functions/v2";

  const dataset = defineString("DATASET_ID");
  let client: BigQuery;

  onInit(() => {
    client = new BigQuery({ datasetId: dataset.value() });
  });
  ```

### 3. V2 并发与成本一致性

V2 支持并发（最多 80 个请求）。为保留 V1 单并发定价，设置 `cpu: "gcf_gen1"`。

______________________________________________________________________

## 步骤式迁移执行

### 第 1 步：盘点扩展资源

1. **`extension.yaml`**：
   - `params` → `defineString`, `defineInt`, `defineBoolean`, `defineSecret`。
   - `apis` → `requiresAPI(...)`。
   - `roles` → `requiresRole(...)`。
   - `lifecycleEvents` → `afterFirstDeploy` & `afterRedeploy`。
   - `resources` → 将第一代触发器升级为第二代 (`onDocumentWritten`,
     `onTaskDispatched`, `onRequest`)。
1. **文件与脚本**：保留 `devDependencies`、测试框架 (`jest`) 以及测试脚本。

### 第 2 步：配置 `package.json`

- 设置 `name: "<package-name>"`, `engines: { "node": ">=22" }`。
- 设置 `peerDependencies`：
  ```json
  "peerDependencies": {
    "firebase-admin": "^11.0.0 || ^12.0.0",
    "firebase-functions": ">=6.0.0"
  }
  ```
- 配置 `exports` 映射，目标 ESM/CommonJS 和 TypeScript 声明 (`lib/index.js`, `lib/index.d.ts`)。

### 第 3 步：将触发器从 V1 升级至 V2

- Firestore：使用 `onDocumentWritten` 从 `firebase-functions/v2/firestore`。
- 任务：使用 `onTaskDispatched` 从 `firebase-functions/v2/tasks`。在入队任务时移除
  `EXT_INSTANCE_ID`。
- HTTP：使用 `onRequest` 从 `firebase-functions/v2/https`。
- 在传统第一代处理程序期望 `(change, context)` 的地方应用解构兼容性遮罩层
  (`{ change, context }`, `{ snapshot, context }`)。

### 第 4 步：转换生命周期事件

将扩展生命周期事件映射到 `src/index.ts` 中的 SDK 生命周期钩子：

- `onInstall` → `afterFirstDeploy({ task: { function: "initTask" } })`
- `onUpdate` / `onConfigure` →
  `afterRedeploy({ task: { function: "setupTask" } })`

### 第 5 步：包 README 与导出说明

生成包含以下内容的 `README.md`：

1. 安装说明 (`npm install`)。
1. 重新导出片段 (`export * from "<package-name>"`)。
1. 参数化配置 `.env` 参考表。
1. 变更对比（扩展与包）表。

_提醒：永远不要执行 `npm publish`。_
