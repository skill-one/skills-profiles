---
name: reveal-3d
description: 将 @cognite/reveal-widget npm 包集成到 Flows 应用中，以实现交互式 Cognite Reveal 3D 场景/CAD/点云/360°图像查看器。在向 Flows 应用添加 3D 查看器、3D 可视化、Reveal、CAD 模型、点云模型、360°图像集、场景、RevealWidget、RevealWidgetController、DM 3D 地图、资产 3D 模型、模型浏览器或 Cognite 3D 内容时使用。
---

# Reveal 3D 查看

使用发布的 `@cognite/reveal-widget` npm 包将 Cognite Reveal 3D 查看器添加到 Flows 应用中。渲染 CAD 模型、点云、360° 图片集合以及来自 CDF 的 CDF 场景，支持模型浏览或直接模型/版本 ID。

可视化 DM 实例：**$ARGUMENTS**

## 使用场景

当用户希望在 Flows 应用中嵌入交互式 Cognite Reveal 查看 CDF 3D 内容时使用此技能。

**不要**将此技能用于静态图表、图形可视化或无关的定制 Three.js 场景。

**不要**使用已弃用的本地应用“复制包”方法——该模式（`src/features/reveal-3d/` 文件夹中的复制提供者/钩子源）已被直接安装 `@cognite/reveal-widget` 所取代。如果应用仍然有先前的集成中的复制包，请将其迁移到此包，而不是扩展它。

## 前置条件

- 应用使用 React + TypeScript，并包装在 `@cognite/app-sdk` 的 `CogniteSdkProvider`（Flows 认证）中，该提供者通过 `@cognite/app-sdk/react` 中的 `useCogniteSdk()` 提供了 `CogniteClient`（`sdk`）。`@cognite/cli` 是用于创建/部署应用的 CLI，而不是运行时认证库——使用 `npx @cognite/cli apps create` 创建的应用依赖于 `@cognite/app-sdk` 而不是 `@cognite/cli` 本身（`useDune()`/`@cognite/dune/auth` 钩子仅存在于遗留 `--classic` 创建中）。
- CDF 项目具有 3D 模型，或用户已提供直接模型/版本 ID 或 CDM（`externalId`/`space`）模型引用。
- 对于 DM 链接的 3D，实例/模型必须可通过 CDM `externalId`/`space` 对或经典 `modelId`/`revisionId` 进行识别；一旦模型加载且实例被上下文化（映射）到模型上，实例高亮就会生效。
- 在设置 `viewerOptions.useCoreDm` 之前，确定项目 3D 内容是否位于 **核心数据模型** 或经典 3D API 中——不要默认将其设置为 `true`。没有单个标志用于此目的；[csp-and-fixes.md](references/csp-and-fixes.md) 提供了直接检查确切 SDK 调用的方法。

## 集成工作流

按顺序执行以下步骤。将路径调整为目标应用的规范，而不是发明新的路径。

1. **检查目标应用。** 阅读 `package.json`、`vite.config.ts`、`src/main.tsx` 以及应用的文件夹/别名规范。
2. **使用应用的包管理器安装包和依赖项。** 参考 [依赖项](#dependencies)。在满足依赖范围的情况下重用现有的 React 和 SDK 版本。
3. **配置 Vite。** 阅读 [vite-config.md](references/vite-config.md) 并添加 `three`/`@cognite/reveal` 去重条目。不需要任何过程/实用/断言 polyfills——该包提供浏览器就绪的版本。
4. **配置 `manifest.json` 的 CSP 允许**，针对实际场景/模型内容（场景地面/天空盒纹理、360° 图片集合）。阅读 [csp-and-fixes.md](references/csp-and-fixes.md)——它还涵盖了应用端点云所需的修复点（`manifest.json` 不能直接授予它）以及 StrictMode 的陷阱，因此即使应用还没有场景/360 内容，也建议阅读它。
5. **添加一个控制器类**，该类包装 `RevealWidgetController` 并从自己的事件处理程序中强制驱动它（加载资源、样式/高亮实例、控制相机）——而不是从 `useEffect` 对 prop 变化做出反应。参考 [implementation.md](references/implementation.md)。
6. **挂载 `RevealWidget`**，使用 `viewerOptions={{ sdk, useCoreDm }}`（根据项目设置 `useCoreDm`，而不是硬编码——参考 [csp-and-fixes.md](references/csp-and-fixes.md)）、`setControllerRef` 以及必要的 `appIdentifier`（标识主机应用的字符串）在一个具有明确高度的容器内。`RevealWidget` 管理自己的内部 Reveal 上下文——不要将其包装在此包中的另一个提供者内。
7. **选择资源模式。** 默认使用模型浏览器模式（`sdk.models3D.list()` + 经典 `modelId`/`revisionId`），除非用户已经提供了 CDM `externalId`/`space` 模型引用。完整示例在 [implementation.md](references/implementation.md)。
8. **清理。** 当不再需要时，对 `addResource` 返回的任何 `Reveal3DResourceHandle` 调用 `.remove()`（选择更改、卸载时）。
9. **运行类型检查和构建** (`tsc --noEmit`、`pnpm build` 等）并修复任何依赖项/依赖项版本问题。

## 最小示例

```tsx
import { useRef } from 'react';
import type { CogniteClient } from '@cognite/sdk';
import {
  RevealWidget,
  type Reveal3DResourceHandle,
  type RevealWidgetController,
  type ThreeDResourceIdentifier,
} from '@cognite/reveal-widget';

class ThreeDViewerController {
  private model: Reveal3DResourceHandle | undefined;

  constructor(private readonly widgetController: RevealWidgetController) {}

  async loadModel(resource: ThreeDResourceIdentifier): Promise<void> {
    this.model = await this.widgetController.addResource(resource);
    this.widgetController.cameraController.focusModel(this.model);
  }

  dispose(): void {
    this.model?.remove();
  }
}

export function ViewerPage({
  sdk,
  resource,
}: {
  sdk: CogniteClient;
  resource: ThreeDResourceIdentifier;
}) {
  const viewerRef = useRef<ThreeDViewerController>();

  function handleWidgetController(widgetController: RevealWidgetController | undefined) {
    viewerRef.current?.dispose();

    if (widgetController === undefined) {
      viewerRef.current = undefined;
      return;
    }

    const viewer = new ThreeDViewerController(widgetController);
    void viewer.loadModel(resource);
    viewerRef.current = viewer;
  }

  return (
    <div style={{ width: '100%', height: '70vh', position: 'relative' }}>
      <RevealWidget
        viewerOptions={{ sdk, useCoreDm }} // 根据项目设置——参考 csp-and-fixes.md
        setControllerRef={handleWidgetController}
        appIdentifier="my-flows-app"
      />
    </div>
  );
}
```

## 依赖项

建议版本是起点。如果目标应用已经固定了兼容版本，请遵循应用的版本。

| 包 | 建议版本 | 目的 |
|---------|-------------------|---------|
| `@cognite/reveal-widget` | `^0.3.0` | `RevealWidget` 组件及其类型 |
| `react` / `react-dom` | `^18.3.1` (依赖项) | UI 框架——依赖项，必须与应用匹配 |
| `@cognite/reveal` | `4.36.0` | Reveal 查看器运行时——必须完全匹配。固定到 `4.36.0`，而不是 `@cognite/reveal-widget` 自己声明的依赖项范围中的 `4.35.3`——参考下注。 |
| `@cognite/sdk` | `^10.14.0` (依赖项) | CDF API 客户端——依赖项 |

其他所有内容（`three`、`@tanstack/react-query`、`@base-ui/react`、`@floating-ui/react`、`@tabler/icons-react`、`dayjs`、`lodash-es`、`ml-matrix`、`random-seed`、`@cognite/aura`、`@cognite/reveal-components`）是此包的传递依赖项，会自动安装——除非应用需要固定版本，**或者**应用代码直接从它导入——[implementation.md](references/implementation.md) 中的模型浏览器模式确实使用 `@tanstack/react-query` (`useInfiniteQuery`/`useQuery`)——在这种情况下，将其作为直接依赖项添加，因为从未声明的传递依赖项导入会在严格包管理器（如 pnpm）下导致错误。

示例安装（pnpm；根据应用的包管理器调整）：

```bash
pnpm add @cognite/reveal-widget @cognite/reveal@4.36.0 @cognite/sdk react react-dom
```

`@cognite/reveal-widget@0.3.0` 自己的依赖项范围仍然说 `@cognite/reveal@4.35.3`，但其依赖项 `@cognite/reveal-components` 内部硬编码了 `@cognite/reveal@4.36.0`。将应用固定到 `4.36.0` 并确认锁文件解析了单个 `@cognite/reveal` 版本——依赖项范围已过时，此处的真实版本分割（与 `resolve.dedupe` 间隙不同）会无声地破坏 Reveal 的共享查看器状态。

**不要**将任何源包复制到应用中，也不要为此包安装 `process`、`util`、`assert`、`ajv` 或 `vite-plugin-node-polyfills`——所有这些都不需要。

## 关键规则

- 通过 `RevealWidgetController` **强制**驱动查看器，通过 `setControllerRef` 获取。不要尝试重建 Reveal 的旧声明式提供者树（`CacheProvider`/`RevealProvider`/`RevealCanvas`/`Reveal3DResources`）——该 API 属于旧的复制包方法，此包不提供。
- `RevealWidget` 内部包装自己的 Reveal 上下文——永远不要将其嵌套在此包中的另一个提供者内。
- 在 `setControllerRef` 内部调用 `.dispose()`（调用 `.remove()` 对跟踪的句柄）以销毁先前的控制器类实例，然后构造一个新的实例，并且当 `widgetController` 变为 `undefined`（卸载）时再次调用。
- 传递给 `addResource` 的资源必须匹配其 `type`/`sourceType` 组合的确切标识符形状（参考 [implementation.md](references/implementation.md)）——混合经典和 CDM 字段是类型错误。
- 实例高亮仅影响已经上下文化（映射）到已加载模型的实例；先加载模型，然后调用 `styleByInstance`/`focusInstances`。
- `RevealWidget` 的容器必须具有明确的高度——它会填充其父元素。
- 使用 `React.lazy` + `Suspense` 懒加载画布密集型查看器内容，当添加路由/页面时。
- `useCoreDm` 必须与项目匹配，不能默认为 `true`——否则会出现错误的 401 和无声的 360 集合失败。不要将应用包装在 `React.StrictMode` 中——它会在开发期间在加载过程中销毁 `RevealWidget` 的查看器，并产生在生产环境中不会出现的错误。点云需要应用端的同源修复，因为 `manifest.json` 无法授予它们通常需要的 `data:` CSP 允许。所有三个：参考 [csp-and-fixes.md](references/csp-and-fixes.md)。
- `appIdentifier`（命名主机应用的字符串）是自 `@cognite/reveal-widget@0.3.0` 起的**必需**属性——如果没有它挂载 `RevealWidget` 是类型错误。默认情况下，查看器向专用的 `mixpanel-browser` 实例报告匿名使用指标（例如使用哪些功能，例如添加资源、移动相机）。传递可选的 `tracking` 属性来更改此行为：`tracking={{ disabled: true }}` 完全禁用它，或 `tracking={{ mixpanelToken }}` 报告到不同的 Mixpanel 项目。

## 高级参考

有关完整资源标识符目录（CAD、点云、360° 图片、场景）、实例高亮和相机控制，请阅读 [implementation.md](references/implementation.md)。

有关 Vite/去重配置，请阅读 [vite-config.md](references/vite-config.md)。

有关 CSP/`manifest.json` 允许、`useCoreDm`/StrictMode 陷阱、点云应用端修复和 360° 集合故障排除，请阅读 [csp-and-fixes.md](references/csp-and-fixes.md)。

## 验证检查清单

- [ ] `@cognite/reveal-widget` 与其依赖项（`react`、`react-dom`、`@cognite/reveal`、`@cognite/sdk`）一起安装，版本兼容。
- [ ] 应用的 `@cognite/reveal` 固定为 `4.36.0`（不是 `@cognite/reveal-widget` 依赖项范围中的过时 `4.35.3`），锁文件中只有一个解析的 `@cognite/reveal` 版本。
- [ ] 没有源包复制到应用中；所有导入来自 `@cognite/reveal-widget`，并且应用代码没有直接从 `@cognite/reveal-components` 导入。
- [ ] `vite.config.ts` 包含 `resolve.dedupe: ['three', '@cognite/reveal']`（以及应用的现有去重条目）。
- [ ] 没有为此包添加 `process`/`util`/`assert` polyfills 或 `vite-plugin-node-polyfills`。
- [ ] `RevealWidget` 只挂载一次，不嵌套在另一个 Reveal 提供者内，其容器具有明确的高度，并且它被赋予了必需的 `appIdentifier` 字符串属性。
- [ ] `viewerOptions.useCoreDm` 与目标项目是否实际基于核心数据模型匹配。
- [ ] 应用没有包装在 `React.StrictMode` 中。
- [ ] 如果应用加载带有地面/天空盒的场景，则 `manifest.json` 授予 `img-src` 对于 `https://*.cognitedata.com`，如果它加载 360° 图片集合，则授予 `connect-src` 对于实际从 CSP 违规中观察到的签名 URL 主机。如果应用需要点云支持，则已应用并验证了同源 `Blob` 修复。
- [ ] 一个控制器类包装 `RevealWidgetController`，通过 `setControllerRef` 获取，并强制驱动 `addResource`/`styleByInstance`/`focusInstances`/`cameraController`。
- [ ] 控制器类在设置新控制器时以及卸载（`widgetController === undefined`）时都会被销毁（并调用跟踪资源句柄的 `.remove()`）。
- [ ] 资源标识符使用加载模型的正确 `type`/`sourceType` 形状。
- [ ] 类型检查和构建通过。
