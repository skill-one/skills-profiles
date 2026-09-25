`create pixi.js` 是官方用于搭建新 PixiJS v8 项目的 CLI 工具。使用任何包管理器（`npm`、`yarn`、`pnpm`、`bun`）运行它，并从交互式菜单中选择模板，或传递 `--template` 跳过提示。它会创建一个自包含的项目文件夹；然后你可以 `cd` 进入该文件夹，安装依赖项，并运行开发脚本。

## 快速入门

使用交互式提示搭建新项目：

```bash
npm create pixi.js@latest
```

或者通过传递项目名称和模板跳过提示：

```bash
npm create pixi.js@latest my-game -- --template bundler-vite
```

然后：

```bash
cd my-game
npm install
npm run dev
```

需要 Node.js 18+ 或 20+。某些模板（尤其是 `creation-web` 和 `framework-react`）可能需要更高版本的 Node；如果需要，包管理器会发出警告。

### 将 PixiJS 添加到现有项目中

如果你已经有一个打包器、框架或项目设置，请跳过 CLI 直接安装包：

```bash
npm install pixi.js
```

然后从 `pixi.js` 中导入并像 `pixijs-application` 中所示构建 `Application`。CLI 模板是针对新项目的便利工具；它们不会添加 `npm install pixi.js` 无法提供的库内容。

**相关技能：** `pixijs-application`（如何工作搭建的 `new Application()` + `app.init()` 入口点）、`pixijs-core-concepts`（渲染器和渲染循环的概念）、`pixijs-scene-core-concepts`（场景图基础，用于添加到舞台上的第一件事）、`pixijs-assets`（加载纹理、字体和模板期望你放入 `public/` 或 `src/assets/` 的资源包）。

## 核心模式

### 选择包管理器

每个包管理器的命令形状相同：

```bash
npm create pixi.js@latest
yarn create pixi.js
pnpm create pixi.js
bun create pixi.js
```

在 npm 7+ 中，你必须在使用 CLI 标志之前传递 `--`，这样 npm 才不会消耗它们：

```bash
npm create pixi.js@latest my-game -- --template bundler-vite
```

Yarn、pnpm 和 bun 不需要额外的分隔符：

```bash
yarn create pixi.js my-game --template bundler-vite
pnpm create pixi.js my-game --template bundler-vite
bun create pixi.js my-game --template bundler-vite
```

使用 `.` 作为项目名称将项目搭建到当前目录。

### 交互流程

不带参数运行会引导你完成提示：

1. 项目名称（默认为 `pixi-project`）。
2. 框架/模板类别。
3. 变体（在适用情况下 TypeScript 与 JavaScript）。
4. 是否立即安装依赖项（某些运行器）。

最后，CLI 会打印出你调用的包管理器的 `cd` + 安装 + 开发命令。

### 非交互流程

传递项目名称和 `--template` 跳过所有提示。这是脚本、CI 和快速入门文档所需的格式：

```bash
npm create pixi.js@latest my-game -- --template bundler-vite
```

### 可用的模板预设

模板分为两类：

- **打包器模板**（`bundler-*`）：通用的 PixiJS 设置，连接到你选择的打包器。当你想选择自己的结构时使用这些模板。
- **创建模板**（`creation-*`）：针对平台的启动器，已预装额外功能（AssetPack、声音、UI、场景路由）。当你想要所有功能时使用这些模板。
- **框架模板**（`framework-*`）：PixiJS 嵌入到 React 等主机框架中。
- **扩展模板**（`extension-*`）：用于构建可重用 PixiJS 包的脚手架。

对于大多数新项目，推荐从 `bundler-vite` 开始。

| 模板             | 你将获得的内容                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------ |
| `bundler-vite`       | Vite + TypeScript PixiJS 项目。默认的第一站模板。                                           |
| `bundler-vite-js`    | Vite + 纯 JavaScript。                                                                                     |
| `bundler-webpack`    | Webpack + TypeScript。                                                                                        |
| `bundler-webpack-js` | Webpack + 纯 JavaScript。                                                                                  |
| `bundler-esbuild`    | esbuild + TypeScript。                                                                                        |
| `bundler-esbuild-js` | esbuild + 纯 JavaScript。                                                                                  |
| `bundler-import-map` | 无打包器设置，使用浏览器导入映射（适用于学习/演示）。                                     |
| `creation-web`       | PixiJS 创建引擎的 Web 模板，带场景游戏脚手架、AssetPack、声音和 UI 集成。 |
| `framework-react`    | React + TypeScript + 通过 `@pixi/react` 包的 PixiJS。                                                   |
| `framework-react-js` | React + 纯 JavaScript + PixiJS。                                                                           |
| `extension-default`  | 构建可重用 PixiJS 扩展/包的启动器。                                                    |

当前列表在 `create-pixi` 仓库中维护；如果你需要确认，运行 `npm create pixi.js@latest` 不带参数即可看到当前菜单。

### 搭建后的流程

每个模板都附带相同的三个步骤引导：

```bash
cd my-game
npm install
npm run dev
```

`npm run dev` 在默认端口（Vite 5173、webpack 8080 等；模板的 README 中有确切数字）启动本地开发服务器。对 `src/` 的更改不会重新加载整个页面进行热重载。

每个模板都公开其他脚本（名称可能因预设略有不同）：

- `npm run build`：在 `dist/` 生成生产构建。
- `npm run preview` / `npm run serve`：本地提供生产构建。
- `npm run lint`：如果模板附带配置的 linter，则运行模板的配置 linter。

### 搭建到现有目录

使用 `.` 作为项目名称写入当前工作目录。如果存在非空且冲突的文件，CLI 会拒绝运行，除非你确认提示。

```bash
mkdir my-game
cd my-game
npm create pixi.js@latest . -- --template bundler-vite
```

### TypeScript 设置

PixiJS 支持 WebGPU，因此其类型声明依赖于 WebGPU 类型。这些类型来自你的 TypeScript 版本。

- **TypeScript 5：** 没有内置 WebGPU 类型，因此 PixiJS 会为你添加 `@webgpu/types`。无需额外设置。
- **TypeScript 6 和 7：** WebGPU 类型内置在 `"dom"` 库中，但某些版本可能遗漏部分内容，例如 `GPUTextureUsage`。使用 `@types/web` 替换 `"dom"`，它包含完整集。如果存在，从 `types` 中删除 `@webgpu/types`，因为它与内置类型冲突。

```bash
npm install --save-dev @types/web
```

```json
{
  "compilerOptions": {
    "lib": ["esnext"],
    "types": ["@types/web"]
  }
}
```

## 下一步

运行 `npm run dev` 后，模板会在空白或兔子精灵场景中打开。通常的进展是：

1. 阅读 `pixijs-application` 了解模板的入口点如何构建 `new Application()` 并调用 `await app.init(...)`，`app.stage` / `app.renderer` / `app.canvas` 如何相互关联，以及默认情况下 ResizePlugin 和 TickerPlugin 的行为。
2. 阅读 `pixijs-core-concepts` 了解渲染器和渲染循环的概念模型。
3. 在添加第一个非平凡场景之前阅读 `pixijs-scene-core-concepts`，以便了解容器与叶子的规则。
4. 一旦准备好加载真实艺术，通过 `pixijs-assets` 添加纹理。

## 常见错误

### [高] 在 npm 7+ 中缺少 `--` 分隔符

错误：

```bash
npm create pixi.js@latest my-game --template bundler-vite
```

正确：

```bash
npm create pixi.js@latest my-game -- --template bundler-vite
```

npm 7+ 会在包规范之后消耗标志，除非你传递 `--` 将它们转发。如果没有分隔符，CLI 会忽略 `--template` 并退回到交互式提示。Yarn、pnpm 和 bun 不需要分隔符。

### [中] 使用旧版 Node 版本运行

PixiJS 需要 Node 18+ 或 20+。某些模板（`framework-react`、`creation-web`）需要较新的 Node 才能运行其工具。如果你看到包管理器发出的“engines”警告，请在重新运行 CLI 前升级 Node。

### [中] Vite 生产构建中 top-level `await app.init()` 出错

在 Vite 版本 `<=6.0.6` 中，top-level `await` 在开发环境中工作，但在生产构建中会出错，因此执行 `npm run build` 后，`bundler-vite` 项目在模块作用域中这样做会失败：

```ts
const app = new Application();
await app.init({ resizeTo: window }); // 在生产构建的模块顶层出问题
```

将初始化包装在异步 IIFE 中：

```ts
(async () => {
  const app = new Application();
  await app.init({ resizeTo: window });
  document.body.appendChild(app.canvas);
})();
```

将 Vite 升级到 6.0.6 以上也可以解决此问题，但 IIFE 模式在所有版本中都安全，并匹配 PixiJS 快速入门指南。

### [高] 在 TypeScript 6 或 7 中保留 `@webgpu/types` 在 `types` 中

错误：

```json
{
  "compilerOptions": {
    "types": ["@webgpu/types"]
  }
}
```

正确：删除 `"@webgpu/types"` 条目并保留任何其他条目。

TypeScript 6 和 7 在其内置的 `"dom"` 库中声明 WebGPU 类型，因此 `@webgpu/types` 会重复声明它们。在 `skipLibCheck: false` 的情况下，这会在 `lib.dom.d.ts` 和 `@webgpu/types` 中产生数十个冲突声明错误。仅在 TypeScript 5 中保留它，因为 PixiJS 会为你加载它。

### [中] TypeScript 6 或 7 中 `Cannot find name 'GPUTextureUsage'`

在 TypeScript 6.0.3 和 7.0.2 之前，内置的 `"dom"` 库没有 WebGPU 标志常量（`GPUBufferUsage`、`GPUColorWrite`、`GPUMapMode`、`GPUShaderStage`、`GPUTextureUsage`），因此使用它们的原始 WebGPU 代码会因 `TS2552` 失败。重新添加 `@webgpu/types` 只能在 `skipLibCheck: true` 下编译，因为它与内置类型冲突。安装 `@types/web` 0.0.352 或更高版本，从 `lib` 中删除 `"dom"`，并将 `"@types/web"` 添加到 `types` 中，并保留任何现有条目，如 [TypeScript 设置](#typescript-setup)中所示。

### [中] `moduleResolution: "node"` 破坏子路径导入

错误：

```json
{
  "compilerOptions": {
    "moduleResolution": "node"
  }
}
```

正确：

```json
{
  "compilerOptions": {
    "module": "esnext",
    "moduleResolution": "bundler"
  }
}
```

`"node"`（也称为 `"node10"`）会忽略 PixiJS `package.json` 中的 `exports` 字段，因此 `import 'pixi.js/advanced-blend-modes'` 和其他子路径导入无法解析。TypeScript 6 为它们报告 `TS2882` 并弃用此设置（`TS5107`）；TypeScript 7 移除了它（`TS5108`）。如果你使用打包器，请使用 `"bundler"`，否则使用 `"nodenext"`。
