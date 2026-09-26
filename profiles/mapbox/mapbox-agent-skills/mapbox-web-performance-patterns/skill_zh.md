# Mapbox 性能模式技能

此技能提供构建快速、高效 Mapbox 应用的性能优化指导。模式按其对用户体验的影响进行优先级排序，从最关键的改进开始。

**性能理念**：这些不是微观优化。它们表现为等待时间、卡顿和重复成本，影响每个用户会话。

## 优先级级别

性能问题按其对用户体验的影响进行优先级排序：

- **🔴 关键（优先修复）**：直接导致初始加载缓慢或可见卡顿
- **🟡 高影响**：可感知的延迟或资源使用增加
- **🟢 优化**：为完善效果而进行的渐进式改进

---

## 🔴 关键：消除初始化级联延迟

**问题**：顺序加载会创建级联延迟，其中每个资源都等待前一个资源。

**注意**：现代打包工具（Vite、Webpack 等）和 ESM 动态导入会自动处理代码分割和库加载。需要消除的主要级联是**数据加载**——顺序获取地图数据而不是在地图初始化时并行获取。

### 反模式：顺序数据加载

```javascript
// ❌ BAD: 数据在地图初始化后加载
async function initMap() {
  const map = new mapboxgl.Map({
    container: 'map',
    accessToken: MAPBOX_TOKEN,
    style: 'mapbox://styles/mapbox/streets-v12'
  });

  // 等待地图加载，然后获取数据
  map.on('load', async () => {
    const data = await fetch('/api/data'); // 级联延迟！
    map.addSource('data', { type: 'geojson', data: await data.json() });
  });
}
```

**时间线**：地图初始化（0.5s）→ 数据获取（1s）= **1.5s 总时间**

### 解决方案：并行数据加载

```javascript
// ✅ GOOD: 数据立即开始获取（不等待地图）
async function initMap() {
  // 立即开始数据获取（不等待地图）
  const dataPromise = fetch('/api/data').then((r) => r.json());

  const map = new mapboxgl.Map({
    container: 'map',
    accessToken: MAPBOX_TOKEN,
    style: 'mapbox://styles/mapbox/streets-v12'
  });

  // 数据在地图加载时准备好
  map.on('load', async () => {
    const data = await dataPromise;
    map.addSource('data', { type: 'geojson', data });
    map.addLayer({
      id: 'data-layer',
      type: 'circle',
      source: 'data'
    });
  });
}
```

**时间线**：max(地图初始化, 数据获取) = **~1s 总时间**

### 设置精确的初始视口

```javascript
// ✅ 设置精确的中心/缩放，以便地图立即获取正确的瓦片
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [-122.4194, 37.7749],
  zoom: 13
});

// 使用 'idle' 知道初始视口完全渲染完成时
// （所有瓦片、精灵和其他资源都已加载；没有正在进行的过渡）
map.once('idle', () => {
  console.log('Initial viewport fully rendered');
});
```

如果你知道用户首先会看到的确切区域，提前设置 `center` 和 `zoom` 可以避免地图从默认视图开始然后平移/缩放到目标，这会浪费瓦片获取。

### 延迟非关键特性

```javascript
// ✅ 首先加载关键特性，延迟其他特性
const map = new mapboxgl.Map({
  /* 配置 */
});

map.on('load', () => {
  // 1. 立即添加关键图层
  addCriticalLayers(map);

  // 2. 延迟次要特性
  // 注意：标准样式 3D 建筑可以通过配置切换：
  // map.setConfigProperty('basemap', 'show3dObjects', false);
  requestIdleCallback(
    () => {
      addTerrain(map);
      addCustom3DLayers(map); // 用于经典样式带自定义填充挤压图层
    },
    { timeout: 2000 }
  );

  // 3. 延迟分析和非视觉特性
  setTimeout(() => {
    initializeAnalytics(map);
  }, 3000);
});
```

**影响**：显著减少交互时间，尤其是在延迟地形和 3D 图层时

---

## 🔴 关键：优化初始包大小

**问题**：大型包在慢速网络上会延迟交互时间。

**注意**：现代打包工具（Vite、Webpack 等）会自动处理基于框架应用的代码分割。以下指导最适用于优化打包内容和时机。

### 样式 JSON 包的影响

```javascript
// ❌ BAD: 内联大型样式 JSON（可能 500+ KB）
const style = {
  version: 8,
  sources: {
    /* 100 行以上 */
  },
  layers: [
    /* 100 层以上 */
  ]
};

// ✅ GOOD: 引用 Mapbox 托管的样式
const map = new mapboxgl.Map({
  style: 'mapbox://styles/mapbox/streets-v12' // 按需获取
});

// ✅ 或：将大型自定义样式存储在外部
const map = new mapboxgl.Map({
  style: '/styles/custom-style.json' // 单独加载
});
```

**影响**：从内联切换到托管样式时，初始包减少 30-50%

---

## 🟡 高影响：优化标记数量

**问题**：过多的标记会导致渲染缓慢和交互卡顿。

### 性能阈值

- **< 100 个标记**：HTML 标记可以（Marker 类）
- **100-10,000 个标记**：使用符号图层（GPU 加速）
- **10,000+ 个标记**：建议使用聚类
- **100,000+ 个标记**：使用带服务器端聚类的矢量瓦片

### 反模式：数千个 HTML 标记

```javascript
// ❌ BAD: 5,000 个 HTML 标记 = 5+ 秒渲染，平移/缩放卡顿
restaurants.forEach((restaurant) => {
  const marker = new mapboxgl.Marker()
    .setLngLat([restaurant.lng, restaurant.lat])
    .setPopup(new mapboxgl.Popup().setHTML(restaurant.name))
    .addTo(map);
});
```

**结果**：5,000 个 DOM 元素，交互缓慢，内存高

### 解决方案：使用符号图层（GeoJSON）

```javascript
// ✅ GOOD: GPU 加速渲染，10,000+ 特征时流畅
map.addSource('restaurants', {
  type: 'geojson',
  data: {
    type: 'FeatureCollection',
    features: restaurants.map((r) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [r.lng, r.lat] },
      properties: { name: r.name, type: r.type }
    }))
  }
});

map.addLayer({
  id: 'restaurants',
  type: 'symbol',
  source: 'restaurants',
  layout: {
    'icon-image': 'restaurant',
    'icon-size': 0.8,
    'text-field': ['get', 'name'],
    'text-size': 12,
    'text-offset': [0, 1.5],
    'text-anchor': 'top'
  }
});

// 点击处理程序（一个监听器用于所有特征）
map.on('click', 'restaurants', (e) => {
  const feature = e.features[0];
  new mapboxgl.Popup().setLngLat(feature.geometry.coordinates).setHTML(feature.properties.name).addTo(map);
});
```

**性能**：10,000 个特征在 <100ms 内渲染

### 解决方案：高密度聚类

```javascript
// ✅ GOOD: 50,000 个标记 → 低缩放时约 500 个聚类
map.addSource('restaurants', {
  type: 'geojson',
  data: restaurantsGeoJSON,
  cluster: true,
  clusterMaxZoom: 14, // 在缩放 15 时停止聚类
  clusterRadius: 50 // 相对于瓦片尺寸的半径（512 = 完整瓦片宽度）
});

// 聚类圆圈图层
map.addLayer({
  id: 'clusters',
  type: 'circle',
  source: 'restaurants',
  filter: ['has', 'point_count'],
  paint: {
    'circle-color': ['step', ['get', 'point_count'], '#51bbd6', 100, '#f1f075', 750, '#f28cb1'],
    'circle-radius': ['step', ['get', 'point_count'], 20, 100, 30, 750, 40]
  }
});

// 聚类计数标签
map.addLayer({
  id: 'cluster-count',
  type: 'symbol',
  source: 'restaurants',
  filter: ['has', 'point_count'],
  layout: {
    'text-field': '{point_count_abbreviated}',
    'text-size': 12
  }
});

// 单个点图层
map.addLayer({
  id: 'unclustered-point',
  type: 'circle',
  source: 'restaurants',
  filter: ['!', ['has', 'point_count']],
  paint: {
    'circle-color': '#11b4da',
    'circle-radius': 6
  }
});
```

**影响**：50,000 个标记在 60 FPS 下交互流畅

---

## 总结：性能检查清单

构建 Mapbox 应用时，按顺序验证这些优化：

### 🔴 关键（优先执行）

- [ ] 并行加载地图库和数据（消除级联延迟）
- [ ] 使用动态导入加载地图代码（减少初始包）
- [ ] 延迟非关键特性（地形、自定义 3D 图层、分析）
- [ ] 使用符号图层（> 100 个标记，不是 HTML 标记）
- [ ] 实现基于视口的按需数据加载（适用于大型数据集）

### 🟡 高影响

- [ ] 防抖/节流地图事件处理程序（geocode 输入、`moveend`）
- [ ] 使用图层过滤器和边界框优化 `queryRenderedFeatures`
- [ ] 使用 GeoJSON（< 5 MB），矢量瓦片（> 20 MB）
- [ ] SPA/页面卸载时始终调用 `map.remove()`（清理）
- [ ] 添加 `map.on('error', …)`（或可见错误 UI），以便样式/瓦片/令牌失败不是静默的
- [ ] 重用弹窗实例（不要在每次交互时创建）
- [ ] 使用特征状态而不是动态图层（用于悬停/选择）
- [ ] 聚类示例：生成足够多的点以测试聚类（数千个，而不是几百个）

### 代理反模式：仅成功路径

第一版代理代码通常会发布一个没有 `map.on('error')`、没有 `map.remove()`、点集很小且永远不会触发 `cluster: true` 的地图。生产演示需要错误可见性、卸载和真实规模。

### 🟢 优化

- [ ] 使用数据驱动样式合并多个图层
- [ ] 添加移动端特定优化（圆圈图层、禁用旋转）
- [ ] 在图层上设置 minzoom/maxzoom，避免在无关紧要的缩放级别渲染
- [ ] 避免启用 preserveDrawingBuffer 或 antialias，除非需要

### 测量

```javascript
// 测量初始加载时间
console.time('map-load');
map.on('load', () => {
  console.timeEnd('map-load');
  // isStyleLoaded() 在样式、源、瓦片、精灵和模型全部加载时返回 true
  console.log('Style loaded:', map.isStyleLoaded());
});

// 监控帧率
let frameCount = 0;
map.on('render', () => frameCount++);
setInterval(() => {
  console.log('FPS:', frameCount);
  frameCount = 0;
}, 1000);

// 检查内存使用（Chrome DevTools -> Performance -> Memory）
```

**目标指标**：

- **交互时间**：3G 网络下 < 2 秒
- **帧率**：平移/缩放时 60 FPS
- **内存增长**：使用 1 小时内存增长 < 10 MB
- **包大小**：初始 < 500 KB（地图按需加载）

---

## 参考文件

对于特定主题的详细模式，加载相应的参考文件：

- **`references/data-loading.md`** — GeoJSON 与矢量瓦片决策矩阵、基于视口加载、渐进式加载、用于大型数据集的矢量瓦片
- **`references/interactions.md`** — 防抖/节流事件、优化特征查询、批量 DOM 更新
- **`references/memory.md`** — 地图清理模式、弹窗/标记重用、特征状态与动态图层
- **`references/mobile.md`** — 设备检测、移动端优化图层、触摸交互、构造函数选项
- **`references/layers-styles.md`** — 使用数据驱动样式合并图层、简化表达式、基于缩放的可见性
