# Mapbox 集成模式技能

此技能提供官方模式，用于使用 React、Vue、Svelte、Angular 和原生 JavaScript 将 Mapbox GL JS 集成到 Web 应用中。这些模式基于 Mapbox 的 `create-web-app` 框架工具，代表了可投入生产的最佳实践。

## 版本要求

### Mapbox GL JS

**推荐：** v3.x（最新版）

- **最低要求：** v3.0.0
- **为什么 v3.x：** 现代 API、性能提升、积极开发
- **v2.x：** 遗留版本；不再积极开发（请参阅以下迁移说明）

**通过 npm 安装（推荐用于生产环境）：**

```bash
npm install mapbox-gl@^3.0.0    # 安装最新 v3.x 版本
```

**CDN（仅用于原型设计）：**

```html
<!-- 将 VERSION 替换为 https://docs.mapbox.com/mapbox-gl-js/ 上的最新 v3.x 版本 -->
<script src="https://api.mapbox.com/mapbox-gl-js/vVERSION/mapbox-gl.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/vVERSION/mapbox-gl.css" rel="stylesheet" />
```

### 框架要求

**React：** GL JS 与 React 16.8+（需要 hooks）兼容。`create-web-app` 框架使用 React 19.x。
**Vue：** GL JS 与 Vue 2.x+ 兼容（推荐使用 Vue 3 Composition API）。
**Svelte：** GL JS 与任何 Svelte 版本兼容。`create-web-app` 框架使用 Svelte 5.x。
**Angular：** GL JS 与 Angular 2+ 兼容。`create-web-app` 框架使用 Angular 19.x。
**Next.js：** 最小 13.x（App Router），Pages Router 12.x+。

### Mapbox 搜索 JS

```bash
npm install @mapbox/search-js-react@^1.0.0      # React
npm install @mapbox/search-js-web@^1.0.0        # 其他框架
```

### 版本迁移说明（v2.x 到 v3.x）

- 现在需要 WebGL 2
- 移除了 `optimizeForTerrain` 选项
- TypeScript 类型改进，更好的 tree-shaking 支持
- 核心初始化模式没有破坏性变更

**令牌模式（在 v2.x 和 v3.x 中均有效）：**

```javascript
const token = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN; // 在生产环境中使用环境变量

// 全局令牌（自 v1.x 起有效）
mapboxgl.accessToken = token;
const map = new mapboxgl.Map({ container: '...' });

// 每个地图的令牌（对于多地图设置更推荐）
const map = new mapboxgl.Map({
  accessToken: token,
  container: '...'
});
```

## 核心原则

**每个 Mapbox GL JS 集成必须：**

1. 在正确的生命周期钩子中初始化地图
2. 将地图实例存储在组件状态中（不要在每次渲染时重新创建）
3. **清理时始终调用 `map.remove()`** 以防止内存泄漏
4. 安全地处理令牌管理（环境变量）
5. 导入 CSS：`import 'mapbox-gl/dist/mapbox-gl.css'`

## React 集成（主要模式）

**模式：useRef + useEffect + 清理**

> **注意：** 这些示例使用 **Vite**（`create-web-app` 中使用的打包器）。如果使用 Create React App，请将 `import.meta.env.VITE_MAPBOX_ACCESS_TOKEN` 替换为 `process.env.REACT_APP_MAPBOX_TOKEN`。请参阅 [令牌管理模式](references/token-management.md) 以获取其他打包器的说明。

```jsx
import { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

function MapComponent() {
  const mapRef = useRef(null); // 存储地图实例
  const mapContainerRef = useRef(null); // 存储 DOM 引用

  useEffect(() => {
    mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      center: [-71.05953, 42.3629],
      zoom: 13
    });

    // 关键：清理以防止内存泄漏
    return () => {
      mapRef.current.remove();
    };
  }, []); // 空依赖数组 = 在挂载时运行一次

  return <div ref={mapContainerRef} style={{ height: '100vh' }} />;
}
```

**要点：**

- 使用 `useRef` 存储地图实例和容器
- 在 `useEffect` 中初始化，依赖数组为空 `[]`
- **始终返回清理函数** 调用 `map.remove()`
- 永远不要在渲染中初始化地图（会导致无限循环）

### React + 搜索 JS

```jsx
import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { SearchBox } from '@mapbox/search-js-react';
import 'mapbox-gl/dist/mapbox-gl.css';

const accessToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
const center = [-71.05953, 42.3629];

function MapWithSearch() {
  const mapRef = useRef(null);
  const mapContainerRef = useRef(null);
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    mapboxgl.accessToken = accessToken;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      center: center,
      zoom: 13
    });

    return () => {
      mapRef.current.remove();
    };
  }, []);

  return (
    <>
      <div
        style={{
          margin: '10px 10px 0 0',
          width: 300,
          right: 0,
          top: 0,
          position: 'absolute',
          zIndex: 10
        }}
      >
        <SearchBox
          accessToken={accessToken}
          map={mapRef.current}
          mapboxgl={mapboxgl}
          value={inputValue}
          proximity={center}
          onChange={(d) => setInputValue(d)}
          marker
        />
      </div>
      <div ref={mapContainerRef} style={{ height: '100vh' }} />
    </>
  );
}
```

## 搜索 JS 集成总结

**安装：**

```bash
npm install @mapbox/search-js-react      # React
npm install @mapbox/search-js-web        # 原生/Vue/Svelte
```

两个包都包含 `@mapbox/search-js-core` 作为依赖项。除非正在构建自定义搜索 UI，否则不要直接安装 `-core`。

**关键配置选项：**

- `accessToken`：您的 Mapbox 公共令牌
- `map`：地图实例（必须先初始化）
- `mapboxgl`：mapboxgl 库引用
- `proximity`：`[lng, lat]` 以地理偏移结果
- `marker`：布尔值以显示/隐藏结果标记
- `placeholder`：搜索框占位符文本

### 定位搜索框

**绝对定位（叠加层）：**

```jsx
<div
  style={{
    position: 'absolute',
    top: 10,
    right: 10,
    zIndex: 10,
    width: 300
  }}
>
  <SearchBox {...props} />
</div>
```

**常见位置：**

- 右上角：`top: 10px, right: 10px`
- 左上角：`top: 10px, left: 10px`
- 左下角：`bottom: 10px, left: 10px`

## 常见错误（关键）

### 错误 1：忘记调用 map.remove()

```javascript
// 错误 - 内存泄漏！
useEffect(() => {
  const map = new mapboxgl.Map({ ... })
  // 没有清理函数
}, [])

// 正确 - 正确清理
useEffect(() => {
  const map = new mapboxgl.Map({ ... })
  return () => map.remove()  // 清理
}, [])
```

**原因：** 每个地图实例创建 WebGL 上下文、事件监听器和 DOM 节点。如果没有清理，这些会累积并导致内存泄漏。

### 错误 2：在渲染中初始化地图

```javascript
// 错误 - React 中无限循环！
function MapComponent() {
  const map = new mapboxgl.Map({ ... })  // 每次渲染都会运行
  return <div />
}

// 正确 - 在效果中初始化
function MapComponent() {
  useEffect(() => {
    const map = new mapboxgl.Map({ ... })
  }, [])
  return <div />
}
```

**原因：** React 组件频繁重新渲染。在每次渲染中创建新地图会导致无限循环和崩溃。

### 错误 3：未正确存储地图实例

```javascript
// 错误 - map 变量在渲染之间丢失
function MapComponent() {
  useEffect(() => {
    let map = new mapboxgl.Map({ ... })
    // map 变量在后续不可访问
  }, [])
}

// 正确 - 使用 useRef 存储
function MapComponent() {
  const mapRef = useRef()
  useEffect(() => {
    mapRef.current = new mapboxgl.Map({ ... })
    // mapRef.current 在整个组件中可访问
  }, [])
}
```

**原因：** 您需要访问地图实例以进行添加图层、标记或调用 `remove()` 等操作。

### 错误 4：在 Vue 的 data() 中存储地图实例（Vue 特定）

```javascript
// 错误 - Vue 的响应性将 data() 对象包装在 Proxy 中，破坏了 mapbox-gl 的内部机制！
export default {
  data() {
    return {
      map: null  // 将被包装在 Proxy 中
    }
  },
  mounted() {
    this.map = new mapboxgl.Map({ ... })  // Proxy 破坏 GL 内部机制
  }
}

// 正确 - 将地图作为普通实例属性分配，而不是在 data() 中
export default {
  mounted() {
    this.map = new mapboxgl.Map({
      container: this.$refs.mapContainer,
      center: [-71.05953, 42.3629],
      zoom: 13
    })
  },
  unmounted() {
    this.map?.remove()
  }
}
```

**原因：** 在 Vue（尤其是 Vue 3）中，`data()` 属性被包装在 `Proxy` 中以实现响应性。Mapbox GL JS 内部检查对象身份，并使用不会经过 Proxy 包装的属性。将地图存储在 `data()` 中会导致难以调试的微妙失败。相反，在 `mounted()` 中直接分配地图实例为 `this.map` —— 在 `data()` 外分配的属性不会被设置为响应性。

### 错误 5：无声的样式/瓦片失败（无错误处理器）

```javascript
// 错误 — 令牌/样式失败时地图空白
const map = new mapboxgl.Map({ ... });

// 正确 — 表面失败
map.on('error', (e) => {
  console.error(e.error || e);
  // 可选地显示页面上的错误消息
});
```

### 错误 6：通过 jsDelivr `+esm` 的 Deck.gl CDN 故障

```html
<!-- 错误 — 常常抛出：不提供名为 'makeBatchFromTable' 的导出 -->
<script type="module">
  import { MapboxOverlay } from 'https://cdn.jsdelivr.net/npm/@deck.gl/mapbox@9.0.0/+esm';
</script>

<!-- 正确 — UMD 包（或 esm.sh） -->
<script src="https://unpkg.com/deck.gl@9.1.14/dist.min.js"></script>
<script>
  const { MapboxOverlay, ScatterplotLayer } = deck;
  map.addControl(
    new MapboxOverlay({
      interleaved: false,
      layers: [
        /* ... */
      ]
    })
  );
</script>
```

使用 `MapboxOverlay`（Mapbox IControl），而不是作为地图控制的裸 `Deck`。

### 错误 7：没有 `draw.create` 的绘图工具栏

如果您加载了 `mapbox-gl-draw`，请监听 `draw.create`（并从 `draw.getAll()` 更新 UI）。半删除的处理器会留下悬空的 `});` 导致页面崩溃。

### 错误 8：`setStyle` 后丢失图层（没有 `style.load` 重新绑定）

`map.setStyle(...)` 替换样式树。先前添加的自定义源/图层/处理器会被擦除，除非您重新附加它们。

```javascript
function onStyleReady() {
  // 在此处重新添加源、图层和交互处理器
}

map.on('style.load', onStyleReady);

document.querySelectorAll('[data-style]').forEach((btn) => {
  btn.addEventListener('click', () => {
    map.setStyle(btn.dataset.style);
    // 不要仅在第一次 'load' 时添加图层 — 每次切换后等待 'style.load'
  });
});
```

**代理反模式：** 调用 `setStyle` 一次且没有 `style.load` 重新绑定的样式切换按钮。第一个样式正常；之后的切换看起来都损坏了。

## 参考文件

加载这些以获取框架特定模式和附加详细信息：

- `references/vue.md` — Vue 集成（mounted/unmounted 生命周期）
- `references/svelte.md` — Svelte 集成（onMount/onDestroy）
- `references/angular.md` — Angular 集成（处理 SSR）
- `references/vanilla.md` — 原生 JavaScript（Vite）+ 原生 JavaScript（CDN）
- `references/web-components.md` — Web 组件（基本 + 响应性 + 在 React/Vue/Svelte 中的使用）
- `references/nextjs.md` — Next.js App Router + Pages Router
- `references/common-mistakes.md` — 常见错误 4-7 + 测试模式
- `references/token-management.md` — 按打包器分代的令牌管理 + 样式配置

## 何时使用此技能

在以下情况下调用此技能：

- 在新项目中设置 Mapbox GL JS
- 将 Mapbox 集成到特定框架（React、Vue、Svelte、Angular、Next.js）
- 构建框架无关的 Web 组件
- 创建可重用的地图组件用于组件库
- 调试地图初始化问题
- 添加 Mapbox 搜索功能
- 实施适当的清理和生命周期管理
- 在框架之间转换（例如，React 到 Vue）
- 审查代码以进行 Mapbox 集成最佳实践

## 相关技能

- **mapbox-cartography**：地图设计原则和样式
- **mapbox-token-security**：令牌管理和安全
- **mapbox-style-patterns**：常见地图样式模式

## 资源

- [Mapbox GL JS 文档](https://docs.mapbox.com/mapbox-gl-js/)
- [Mapbox 搜索 JS 文档](https://docs.mapbox.com/mapbox-search-js/)
- [create-web-app GitHub](https://github.com/mapbox/create-web-app)
