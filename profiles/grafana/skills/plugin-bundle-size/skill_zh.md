# Grafana 插件捆绑包大小优化

`module.js` 是每个 Grafana 应用程序插件的渲染阻塞入口点。它越小，插件对 Grafana 整体启动时间的影响就越小。一个良好拆分的插件应该有一个大约 200 KB 的 `module.js`，其中只包含懒加载的包装器——所有功能代码都在按需加载。

**目标：** 总共约 15-25 个 JS 捆绑包。太少意味着拆分不足；太多（50 个以上）意味着过度设计。

## 风险等级

并非所有拆分机会都具有相同的风险。按以下顺序应用它们：

| 等级 | 内容 | 风险 | 影响 |
|---|---|---|---|
| **安全** | `module.tsx` 懒加载包装器（优先级 1） | 非常低——行为不会改变 | 最高——module.js 减少 90%+ |
| **安全** | 路由级别的 `lazy()`（优先级 2） | 低——每个路由都是自包含的 | 高——每个路由一个捆绑包 |
| **安全** | 扩展 `lazy()`（优先级 3） | 低——扩展是隔离的 | 中等——每个扩展一个独立的捆绑包 |
| **中等** | 组件注册表 / 选项卡面板（优先级 4） | 中等——验证 Suspense 的放置位置 | 中等——进一步拆分重型页面 |
| **不要触碰** | 商业库（`@grafana/scenes`，`@reduxjs/toolkit`） | N/A | N/A——webpack 会自动拆分这些 |
| **不要触碰** | 跨多个文件使用的共享实用组件（Markdown，Spinner） | 高变更，许多调用点 | 低——已经存在于共享商业捆绑包中 |

不确定时，在优先级 2 后停止。路由本身通常可以减少 `module.js` 95%+。

---

## 第 1 步：添加捆绑包大小 CI 报告（推荐）

将 `grafana/plugin-actions/bundle-size` 动作添加到每个 PR 上自动获取捆绑包大小比较评论。这会发布一个显示入口点大小变化、文件计数差异和总捆绑包影响的表格。

**根级插件**（存储库根目录中的插件）：

```yaml
# .github/workflows/bundle-size.yml
name: 捆绑包大小
on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  bundle-size:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write
      pull-requests: write
      actions: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
      - name: 安装和构建
        run: yarn install
      - name: 捆绑包大小
        uses: grafana/plugin-actions/bundle-size@a66a1c96cdbb176f9cccf10cf23593e250db7cce # bundle-size/v1.1.0
```

**子目录插件**（例如 monorepo 中的 `plugin/`）：

该动作的安装步骤在存储库根目录下运行，无法在子目录中找到 `yarn.lock`。通过自己安装依赖项并链接到根目录来解决这个问题：

```yaml
jobs:
  bundle-size:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      id-token: write
      pull-requests: write
      actions: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: ./plugin/.nvmrc
      - name: 安装依赖项
        working-directory: ./plugin
        run: yarn install
      - name: 将插件链接到根目录以供捆绑包大小动作使用
        run: |
          ln -s plugin/yarn.lock yarn.lock
          ln -s plugin/package.json package.json
          ln -s plugin/.yarnrc.yml .yarnrc.yml
          ln -s plugin/node_modules node_modules
      - name: 捆绑包大小
        uses: grafana/plugin-actions/bundle-size@a66a1c96cdbb176f9cccf10cf23593e250db7cce # bundle-size/v1.1.0
        with:
          working-directory: ./plugin
```

**工作原理：** 在推送到 main 时，构建并上传基线工件。在 PR 时，将其与基线进行比较并发布差异评论。使用 `workflow_dispatch` 生成第一个基线。

**参考：** [grafana-k8s-plugin 工作流](https://github.com/grafana/grafana-k8s-plugin/blob/main/.github/workflows/grafana.yml)

---

## 第 2 步：检测插件上下文

```bash
# 确认这是一个应用程序插件（类型："app"——数据源/面板插件具有不同的需求）
jq -r '"\(.id) — \(.type)"' src/plugin.json

# 定位入口点
ls src/module.ts src/module.tsx 2>/dev/null

# 在进行任何更改之前测量当前生产环境的捆绑包大小
# 开发构建未压缩且体积更大——始终测量生产环境
yarn build 2>/dev/null || npm run build
echo "=== module.js ===" && ls -lah dist/module.js
echo "=== 所有 JS 捆绑包 ===" && ls -lah dist/*.js | sort -k5 -rh | head -20
echo "=== 捆绑包计数 ===" && ls dist/*.js | wc -l
```

记录基线。拆分前的插件通常有一个 1-3 MB 的 `module.js`，且没有其他 JS 捆绑包。

---

## 第 3 步：检查和更新 create-plugin

`@grafana/create-plugin` 工具控制 `.config/webpack/`，`.config/jest/` 和其他构建脚手架。更新它通常可以解锁更快的 SWC 编译和更好的捆绑包输出。

```bash
cat .config/.cprc.json 2>/dev/null || grep '"@grafana/create-plugin"' package.json
npm view @grafana/create-plugin version
npx @grafana/create-plugin@latest update
```

更新后，查看差异（尤其是 `.config/webpack/webpack.config.ts`），并运行一个测试构建。如果插件有一个顶层 `webpack.config.ts` 会 `webpack-merge` 基本配置，请查看合并是否存在冲突。

---

## 第 4 步：分析代码库——找出要拆分的内容

在阅读所有这些内容之前，不要开始实施。

```bash
# 入口点——查找直接（非懒加载）导入的 App，ConfigPage，exposeComponent 目标
cat src/module.ts 2>/dev/null || cat src/module.tsx

# 根 App 组件——查找应该懒加载的直接页面/路由导入
cat src/App.tsx src/components/App.tsx src/feature/app/components/App.tsx 2>/dev/null | head -80

# 扩展注册——每个都应该成为一个独立的捆绑包
grep -r "exposeComponent\|addComponent\|addLink" src/ --include="*.ts" --include="*.tsx" -n

# 导出的副作用单例（Faro，analytics）——必须在拆分之前提取
grep -n "^export const\|^export let" src/module.ts src/module.tsx 2>/dev/null
grep -rn "from '.*module'" src/ --include="*.ts" --include="*.tsx" | grep -v node_modules

# 重型同步导入
grep -rn "from 'monaco-editor\|@codemirror\|d3\b\|recharts\|chart\.js" \
  src/ --include="*.ts" --include="*.tsx" | grep -v node_modules
```

**关键规则：** 如果一个文件直接被 `module.ts` 导入（即使是传递的），它最终会进入 `module.js`。从懒加载边界可达的所有内容都会成为它自己的捆绑包。

---

## 第 5 步：按优先级顺序实施拆分

> **命名导出与默认导出：** `React.lazy()` 需要一个 `default` 导出。大多数 Grafana 插件组件使用命名导出——使用 `.then()` 来重新映射：
> ```ts
> // 命名导出
> const LazyMyComp = lazy(() => import('./MyComponent').then(m => ({ default: m.MyComponent })));
> // 默认导出
> const LazyMyComp = lazy(() => import('./MyComponent'));
> ```

### 优先级 1：module.tsx（最高影响，始终先做这个）

如果入口点是 `module.ts`，将其重命名为：`git mv src/module.ts src/module.tsx`

使 `module.tsx` 除了通过 `lazy()` 之外，不导入任何功能代码：

```tsx
import React, { lazy, Suspense } from 'react';
import { AppPlugin, AppRootProps } from '@grafana/data';
import { LoadingPlaceholder } from '@grafana/ui';

import type { MyExtensionProps } from './extensions/MyExtension';  // import type——编译时会被移除
import type { JsonData } from './features/app/state/slice';

// 懒加载 Faro 初始化——将 @grafana/faro-react 从 module.js 中排除
let faroInitialized = false;
async function initFaro() {
  if (faroInitialized) { return; }
  faroInitialized = true;
  const { initializeFaro } = await import('faro');
  initializeFaro();
}

const LazyApp = lazy(async () => {
  await initFaro();
  return import('./features/app/App').then(m => ({ default: m.App }));
});

function App(props: AppRootProps<JsonData>) {
  return <Suspense fallback={<LoadingPlaceholder text="" />}><LazyApp {...props} /></Suspense>;
}

const LazyMyExtension = lazy(() =>
  import('./extensions/MyExtension').then(m => ({ default: m.MyExtension }))
);
function MyExtension(props: MyExtensionProps) {
  return <Suspense fallback={<LoadingPlaceholder text="" />}><LazyMyExtension {...props} /></Suspense>;
}

export const plugin = new AppPlugin<JsonData>().setRootPage(App);
plugin.exposeComponent({ id: 'my-plugin/my-extension/v1', title: 'My Extension', component: MyExtension });
```

**关键细节：**
- `import type` 用于 props 防止 webpack 将导入跟随到急切捆绑包中
- 如果 App 使用 `AppRootProps<JsonData>`，请使用泛型——如果没有泛型，`setRootPage()` 类型将不匹配
- 移除任何 `App as unknown as ComponentClass<AppRootProps>` 转换——懒加载包装器是一个有效的函数组件

**预期影响：** `module.js` 从 MB 范围减少到 ~50-200 KB。

**单例（例如 Faro）：** 如果 `module.ts` 有 `export const faro = initializeFaro()`，不要将其作为顶级导入保留。将其提取到 `src/faro.ts`，更新所有内部导入从 `'*/module'` → `'*/faro'`，然后使用上面动态的 `initFaro()` 模式。

---

### 优先级 2：App.tsx 中的基于路由的拆分

```tsx
import React, { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { LoadingPlaceholder } from '@grafana/ui';

const HomePage     = lazy(() => import('../pages/Home'));
const SettingsPage = lazy(() => import('../pages/Settings'));
const DetailPage   = lazy(() => import('../pages/Detail'));

function App(props: AppRootProps) {
  return (
    <Suspense fallback={<LoadingPlaceholder text="" />}>
      <Routes>
        <Route path="home"       element={<HomePage />} />
        <Route path="settings"   element={<SettingsPage />} />
        <Route path="detail/:id" element={<DetailPage />} />
        <Route path=""           element={<HomePage />} />
      </Routes>
    </Suspense>
  );
}
export default App;
```

**绕过棒文件：** 在 `import()` 中目标实际组件文件，而不是重新导出多个内容的 `index.ts` 棒文件：

```tsx
// 有风险——棒文件可能会拉入其他重型模块
const Catalog = lazy(() => import('features/catalog'));
// 更好——只拉入 Catalog 的树
const Catalog = lazy(() => import('features/catalog/Catalog').then(m => ({ default: m.Catalog })));
```

### 优先级 3：扩展组件

每个扩展都应该 `export default` 其组件。对于加载速度快的扩展，使用 `fallback={null}`：

```tsx
// src/extensions/MyExtension.tsx
export default function MyExtension(props: MyExtensionProps) {
  return <AppProviders><MyExtensionContent {...props} /></AppProviders>;
}
```

**外科手术拆分：** 如果扩展包装器必须保留在 `module.tsx` 中急切加载，则懒加载它渲染的重型组件：

```tsx
const HeavyInner = lazy(() => import('components/features/HeavyInner'));
export function MyExtension() {
  return <Suspense fallback={<LoadingPlaceholder text="" />}><HeavyInner /></Suspense>;
}
```

### 优先级 4：组件注册表和选项卡面板

对于包含 React 组件的对象数组的数组（例如选项卡面板），懒加载每个条目。**关键：** 确保在组件渲染位置存在 `<Suspense>` 边界。

```tsx
const ConfigDetails = lazy(() => import('./ConfigDetails/ConfigDetails').then(m => ({ default: m.ConfigDetails })));
const Overview      = lazy(() => import('./Overview/Overview').then(m => ({ default: m.Overview })));

const tabs = [
  { id: 'overview', component: Overview },
  { id: 'config',   component: ConfigDetails },
];

// 在渲染活动选项卡的父组件中：
<Suspense fallback={<LoadingPlaceholder text="" />}>
  {ActiveTab && <ActiveTab />}
</Suspense>
```

对于**数据源插件**（`setConfigEditor`，`setQueryEditor`，`VariableSupport`，`AnnotationSupport`），请参阅 [references/datasource-plugins.md](references/datasource-plugins.md)。

---

## 第 6 步：如果过度拆分，则分组相关的捆绑包

如果构建产生超过 ~25 个 JS 文件，请使用 webpack 魔术注释：

```tsx
const FleetList   = lazy(() => import(/* webpackChunkName: "fleet" */ '../pages/FleetList'));
const FleetDetail = lazy(() => import(/* webpackChunkName: "fleet" */ '../pages/FleetDetail'));
```

每个逻辑功能区域一个 `webpackChunkName`。不要分组不相关的页面。

---

## 第 7 步：测量和验证

```bash
yarn build 2>/dev/null || npm run build
echo "=== module.js ===" && ls -lah dist/module.js
echo "=== 所有 JS 捆绑包（按大小降序排列） ===" && ls -lah dist/*.js | sort -k5 -rh | head -30
echo "=== 捆绑包计数 ===" && ls dist/*.js | wc -l
```

| 指标 | 目标 |
|---|---|
| `module.js` 大小 | < 200 KB |
| 总 JS 捆绑包计数 | 15–25 |
| 最大单个捆绑包 | < 1 MB |

```bash
# 如果一个捆绑包意外地很大，分析捆绑包组成
npx webpack-bundle-analyzer dist/stats.json 2>/dev/null
```

---

## 第 8 步：测试正在运行的插件

1. 在 Grafana 实例中打开插件
2. 导航到**每个路由**——每个路由都会触发新的捆绑包下载
3. **DevTools → Network → JS**：确认懒加载捆绑包在导航时加载，而不是所有内容都预先加载
4. 检查**控制台**是否有错误
5. 测试来自其他 Grafana 应用的任何 `exposeComponent` 扩展

有关常见问题的故障排除，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 参考

- [grafana-collector-app](https://github.com/grafana/grafana-collector-app) — 应用程序插件参考实现
- [grafana/plugin-actions](https://github.com/grafana/plugin-actions) — 官方 Grafana 插件 CI 动作
- [Web.dev — 使用 lazy 和 Suspense 进行代码拆分](https://web.dev/articles/code-splitting-suspense)
- [SurviveJS — webpack 代码拆分](https://survivejs.com/books/webpack/building/code-splitting/)
- [webpack 魔术注释](https://webpack.js.org/api/module-methods/#magic-comments)
