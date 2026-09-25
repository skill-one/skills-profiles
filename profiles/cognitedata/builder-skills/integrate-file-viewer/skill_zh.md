# 集成 CogniteFileViewer

将 `CogniteFileViewer` 添加到此 Flows 应用中，以预览 CDF 文件（PDF、图像、文本）。

## 依赖项

文件查看器库文件（在步骤 2 中复制）需要此 npm 包：

| 包 | 版本 |
|---|---|
| `react-pdf` | `^9.1.1` |

`pdfjs-dist` 作为 `react-pdf` 的依赖项以正确的版本提供 — 不要单独安装它。
`react` 和 `@cognite/sdk` 假定已经在 Flows 应用中存在。

---

## 你的工作

按顺序完成这些步骤。修改每个文件之前请先阅读它。

---

## 步骤 1 — 理解应用

在触摸任何东西之前，请阅读这些文件：

- `package.json` — 检测包管理器（`packageManager` 字段或锁文件）和现有依赖项
- `vite.config.ts` — 了解当前的 Vite 设置
- 应该添加查看器的组件

---

## 步骤 2 — 复制文件查看器源文件

文件查看器库位于此技能文件旁边的 `code/` 目录中。阅读并复制那里**所有**文件到应用的 `src/cognite-file-viewer/` 中：

- `code/types.ts`
- `code/mimeTypes.ts`
- `code/fileResolution.ts`
- `code/useViewport.ts`
- `code/useFileResolver.ts`
- `code/useDocumentAnnotations.ts`
- `code/DocumentAnnotationOverlay.tsx`
- `code/CogniteFileViewer.tsx`
- `code/index.ts`

> PDF.js 工作线程在 `CogniteFileViewer.tsx` 内部配置 — 无需单独的消费者设置。

---

## 步骤 3 — 安装依赖项

使用应用的包管理器安装 `react-pdf`（见上文的**依赖项**）：

- pnpm → `pnpm add react-pdf@^9.1.1`
- npm  → `npm install react-pdf@^9.1.1`
- yarn → `yarn add react-pdf@^9.1.1`

> **pnpm 用户：** pnpm 严格的链接可能会阻止浏览器解析 `pdfjs-dist`。要么将 `pdfjs-dist` 作为直接依赖项添加（`pnpm add pdfjs-dist`），要么将 `public-hoist-pattern[]=pdfjs-dist` 添加到 `.npmrc`。

---

## 步骤 4 — 配置 Vite

将 `optimizeDeps.exclude: ['pdfjs-dist']` 添加到 `vite.config.ts` 中，以防止 Vite 预打包 pdfjs-dist（这会破坏工作线程）：

```ts
export default defineConfig({
  // ... 现有配置 ...
  optimizeDeps: {
    exclude: ['pdfjs-dist'],
  },
});
```

---

## 步骤 5 — 使用组件

从本地复制的文件中导入并渲染 `CogniteFileViewer`：

```tsx
import { CogniteFileViewer } from './cognite-file-viewer';
```

从 `useDune()` 钩子（在所有 Flows 应用中都可用）获取 `sdk`：

```tsx
import { useDune } from '@cognite/dune';
const { sdk } = useDune();
```

### 支持的文件类型

| 类型 | 格式 |
|---|---|
| PDF | `.pdf` — 页面导航、缩放、平移、图表注释叠加 |
| 办公文档 | Word、PowerPoint、Excel、ODS、ODP、ODT、RTF、TSV — 通过 CDF 文档预览 API 转换为 PDF，然后与 PDF 相同的方式渲染 |
| 图像 | JPEG、PNG、WebP、SVG、TIFF — 缩放、平移、旋转 |
| 文本 | `.txt`、`.csv`、`.json` — 渲染为预格式化文本 |
| 其他 | 回退到 `renderUnsupported` |

### 最小用法

这就是你需要的全部内容 — 缩放、平移和触摸手势由内部处理：

```tsx
<CogniteFileViewer
  source={{ type: 'internalId', id: file.id }}
  client={sdk}
  style={{ width: '100%', height: '600px' }}
/>
```

> **组件需要一个定义的高度。** 如果父元素没有显式的高度，查看器将折叠为零。始终通过 `style`、`className` 或父容器设置 `height`。

### 文件源

传递以下三种源类型中的任何一种：

```tsx
// 通过实例 ID（数据模型化文件 — 启用注释）
<CogniteFileViewer
  source={{ type: 'instanceId', space: 'my-space', externalId: 'my-file' }}
  client={sdk}
/>

// 通过 CDF 内部 ID
<CogniteFileViewer
  source={{ type: 'internalId', id: 12345 }}
  client={sdk}
/>

// 通过直接 URL
<CogniteFileViewer
  source={{ type: 'url', url: 'https://...', mimeType: 'application/pdf' }}
/>
```

**当可用时优先使用 `instanceId`** — 它是唯一支持图表注释叠加的源类型。当通过 `sdk.files.list()` 列出文件时，首先检查 `file.instanceId`：

```tsx
source={
  file.instanceId
    ? { type: 'instanceId', space: file.instanceId.space, externalId: file.instanceId.externalId }
    : { type: 'internalId', id: file.id }
}
```

### 完整的属性参考

```tsx
<CogniteFileViewer
  // 必填
  source={source}
  client={sdk}              // 对于 instanceId 和 internalId 源是必需的

  // PDF 分页
  page={page}               // 控制的当前页面（1 索引）
  onPageChange={setPage}
  onDocumentLoad={({ numPages }) => setNumPages(numPages)}

  // 缩放和平移（适用于 PDF 和图像）
  zoom={zoom}               // 1 = 100%；Ctrl/Cmd+滚轮、捏合缩放和中键拖动内置
  onZoomChange={setZoom}
  minZoom={0.25}            // 默认
  maxZoom={5}               // 默认
  panOffset={pan}           // 控制的平移偏移；在页面更改时重置
  onPanChange={setPan}

  // 适应模式
  fitMode="width"           // 'width' 适应容器宽度；'page' 将整个页面适应容器

  // 旋转（PDF 和图像）
  rotation={rotation}       // 0 | 90 | 180 | 270

  // 图表注释（仅限 instanceId 源）
  showAnnotations={true}    // 默认
  onAnnotationClick={(annotation) => { /* annotation.linkedResource 包含 space + externalId */ }}
  onAnnotationHover={(annotation) => {}}

  // 自定义注释工具提示（替换原生 `<title>` 工具提示）
  renderAnnotationTooltip={(annotation, rect) => (
    <div style={{
      position: 'absolute',
      left: rect.x + rect.width,
      top: rect.y,
      zIndex: 11,
    }}>
      {annotation.text}
    </div>
  )}

  // 自定义叠加（SVG 路径、高亮、绘图 — 适用于 PDF 和图像）
  renderOverlay={({ width, height, originalWidth, originalHeight, pageNumber, rotation }) => (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${originalWidth} ${originalHeight}`}
      preserveAspectRatio="none"
      style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'all' }}
    >
      <path d="..." stroke="cyan" fill="none" />
    </svg>
  )}

  // 自定义渲染器（全部可选）
  renderLoading={() => <MySpinner />}
  renderError={(error) => <MyError message={error.message} />}
  renderUnsupported={(mimeType) => <div>无法预览 {mimeType}</div>}

  // 布局
  className="..."
  style={{ width: '100%', height: '100%' }}
/>
```

---

## 小技巧和窍门

**当源更改时重置页面、缩放和旋转。**
组件不会在切换文件时自动重置这些内容 — 你需要自己完成：

```ts
const navigateToFile = (file: FileInfo) => {
  setSelectedFile(file);
  setPage(1);
  setZoom(1);
  setRotation(0);
};
```

**在 `numPages > 0` 时才显示分页 UI。**
`onDocumentLoad` 仅对 PDF 触发。在知道有分页页面之前不要渲染分页控件：

```tsx
{numPages > 0 && (
  <>
    <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>‹</button>
    <span>{page} / {numPages}</span>
    <button disabled={page >= numPages} onClick={() => setPage(p => p + 1)}>›</button>
  </>
)}
```

**注释点击 → 导航到链接的文件。**
`annotation.linkedResource` 包含链接 CDF 实例的 `space` 和 `externalId`。将其与 `file.instanceId` 匹配以导航：

```ts
onAnnotationClick={(annotation) => {
  if (!annotation.linkedResource) return;
  const { space, externalId } = annotation.linkedResource;
  const linked = files.find(
    f => f.instanceId?.space === space && f.instanceId?.externalId === externalId
  );
  if (linked) navigateToFile(linked);
}}
```

**触摸支持是内置的。** 双指捏合缩放和双指拖动平移在触摸设备上自动工作。无需配置。

**平移是中键拖动**（缩放时）在桌面设备上。左键仍然可用于注释点击和文本选择。

**Ctrl/Cmd + 滚轮缩放至光标** — 也内置了。如果你想要程序化的缩放按钮或持久化缩放状态，请连接 `zoom`/`onZoomChange`；否则它完全不受控制。

**`renderOverlay` 接收原始页面尺寸**（`originalWidth`、`originalHeight`），因此你可以在原始坐标空间中设置 SVG `viewBox`。在 PDF 点或图像像素坐标中绘制的路径将正确映射到任何缩放级别的渲染页面。

---

## 常见陷阱

| 问题 | 原因 | 解决方法 |
|---|---|---|
| `Failed to resolve module specifier 'pdf.worker.mjs'` | pdfjs-dist 未提升（pnpm） | 将 `public-hoist-pattern[]=pdfjs-dist` 添加到 `.npmrc`，或直接 `pnpm add pdfjs-dist` |
| `API version does not match Worker version` | 应用和 `react-pdf` 之间的 `pdfjs-dist` 版本不匹配 | 不要单独安装 `pdfjs-dist` — 让 `react-pdf` 提供。如果已安装，请删除它 |
| 注释从未显示 | `instanceId` 是 `undefined` — 没有它注释叠加被禁用 | 使用 `instanceId` 源，或回退并接受经典文件没有注释 |
| 注释显示但为空 | 文件在 CDF 中没有 `CogniteDiagramAnnotation` 边缘 | 预期 — 只有与数据模型同步的 P&ID/图表文件有注释 |
| 查看器折叠为零高度 | 父元素没有显式高度 | 通过 `style`、`className` 或父 CSS 设置 `height` |
