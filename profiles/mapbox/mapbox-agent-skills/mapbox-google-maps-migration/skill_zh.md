# Mapbox 迁移 Google Maps 技能

从 Google Maps Platform 迁移到 Mapbox GL JS 的全面指南。提供 API 对应关系、模式转换和成功迁移的策略。

## 核心哲学差异

### Google Maps：命令式 & 面向对象

- 创建对象（Marker、Polygon 等）
- 添加到地图使用 `.setMap(map)`
- 使用设置器更新属性
- 严重依赖对象实例

### Mapbox GL JS：声明式 & 数据驱动

- 添加数据源
- 定义图层（视觉表现）
- 使用 JSON 样式
- 更新数据，而不是对象属性

**关键洞察：** Mapbox 将所有内容视为数据和样式，而不是独立的对象。

## 地图初始化

### Google Maps

```javascript
const map = new google.maps.Map(document.getElementById('map'), {
  center: { lat: 37.7749, lng: -122.4194 },
  zoom: 12,
  mapTypeId: 'roadmap' // 或 'satellite', 'hybrid', 'terrain'
});
```

### Mapbox GL JS

```javascript
mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN';
const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12', // 或 satellite-v9, outdoors-v12
  center: [-122.4194, 37.7749], // [lng, lat] - 注意顺序！
  zoom: 12
});
```

**关键差异：**

- **坐标顺序：** Google 使用 `{lat, lng}`，Mapbox 使用 `[lng, lat]`
- **认证：** Google 在脚本标签中使用 API 密钥，Mapbox 在代码中使用访问令牌
- **样式：** Google 使用地图类型，Mapbox 使用完整的样式 URL

## API 对应关系参考

### 地图方法

| Google Maps              | Mapbox GL JS                           | 备注                         |
| ------------------------ | -------------------------------------- | ----------------------------- |
| `map.setCenter(latLng)`  | `map.setCenter([lng, lat])`            | 坐标顺序颠倒                 |
| `map.getCenter()`        | `map.getCenter()`                      | 返回 LngLat 对象             |
| `map.setZoom(zoom)`      | `map.setZoom(zoom)`                    | 相同行为                     |
| `map.getZoom()`          | `map.getZoom()`                        | 相同行为                     |
| `map.panTo(latLng)`      | `map.panTo([lng, lat])`                | 带动画的平移                 |
| `map.fitBounds(bounds)`  | `map.fitBounds([[lng,lat],[lng,lat]])` | 不同的边界格式               |
| `map.setMapTypeId(type)` | `map.setStyle(styleUrl)`               | 完全不同的方法               |
| `map.getBounds()`        | `map.getBounds()`                      | 类似                         |

### 地图事件

| Google Maps                                       | Mapbox GL JS           | 备注                 |
| ------------------------------------------------- | ---------------------- | --------------------- |
| `google.maps.event.addListener(map, 'click', fn)` | `map.on('click', fn)`  | 更简单的语法        |
| `event.latLng`                                    | `event.lngLat`         | 事件属性名称         |
| `'center_changed'`                                | `'move'` / `'moveend'` | 不同的事件名称       |
| `'zoom_changed'`                                  | `'zoom'` / `'zoomend'` | 不同的事件名称       |
| `'bounds_changed'`                                | `'moveend'`            | 没有直接对应物       |
| `'mousemove'`                                     | `'mousemove'`          | 相同                 |
| `'mouseout'`                                      | `'mouseleave'`         | 不同的名称           |

## 标记点和点位

### 简单标记点

**Google Maps:**

```javascript
const marker = new google.maps.Marker({
  position: { lat: 37.7749, lng: -122.4194 },
  map: map,
  title: 'San Francisco',
  icon: 'custom-icon.png'
});

// 移除标记点
marker.setMap(null);
```

**Mapbox GL JS:**

```javascript
// 创建标记点
const marker = new mapboxgl.Marker()
  .setLngLat([-122.4194, 37.7749])
  .setPopup(new mapboxgl.Popup().setText('San Francisco'))
  .addTo(map);

// 移除标记点
marker.remove();
```

### 多个标记点

**Google Maps:**

```javascript
const markers = locations.map(
  (loc) =>
    new google.maps.Marker({
      position: { lat: loc.lat, lng: loc.lng },
      map: map
    })
);
```

**Mapbox GL JS (等效方法):**

```javascript
// 相同的面向对象方法
const markers = locations.map((loc) => new mapboxgl.Marker().setLngLat([loc.lng, loc.lat]).addTo(map));
```

**Mapbox GL JS (数据驱动方法 - 推荐用于 100+ 点):**

```javascript
// 添加为 GeoJSON 源 + 图层（使用 WebGL，而不是 DOM）
map.addSource('points', {
  type: 'geojson',
  data: {
    type: 'FeatureCollection',
    features: locations.map((loc) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [loc.lng, loc.lat] },
      properties: { name: loc.name }
    }))
  }
});

map.addLayer({
  id: 'points-layer',
  type: 'circle', // 或 'symbol' 用于图标
  source: 'points',
  paint: {
    'circle-radius': 8,
    'circle-color': '#ff0000'
  }
});
```

**性能优势：** Google Maps 将所有标记点作为 DOM 元素渲染（即使使用数据层），当使用 500+ 标记点时会变慢。Mapbox 的圆圈和符号图层由 WebGL 渲染，对于大型数据集（1,000-10,000+ 点）速度要快得多。这在构建包含许多点的应用程序时是一个显著的优势。

## 信息窗口 / 弹窗

### Google Maps

```javascript
const infowindow = new google.maps.InfoWindow({
  content: '<h3>Title</h3><p>Content</p>'
});

marker.addListener('click', () => {
  infowindow.open(map, marker);
});
```

### Mapbox GL JS

```javascript
// 选项 1：附加到标记点
const marker = new mapboxgl.Marker()
  .setLngLat([-122.4194, 37.7749])
  .setPopup(new mapboxgl.Popup().setHTML('<h3>Title</h3><p>Content</p>'))
  .addTo(map);

// 选项 2：图层点击（用于数据驱动标记点）
map.on('click', 'points-layer', (e) => {
  const coordinates = e.features[0].geometry.coordinates.slice();
  const description = e.features[0].properties.description;

  new mapboxgl.Popup().setLngLat(coordinates).setHTML(description).addTo(map);
});
```

## 迁移策略

### 第 1 步：审计当前实现

识别您使用的所有 Google Maps 功能：

- [ ] 基本地图带标记点
- [ ] 信息窗口/弹窗
- [ ] 多边形/折线
- [ ] 地理编码
- [ ] 导航
- [ ] 聚类
- [ ] 自定义样式
- [ ] 绘图工具
- [ ] 街景（Mapbox 没有对应物）
- [ ] 其他高级功能

### 第 2 步：设置 Mapbox

```html
<!-- 替换 Google Maps 脚本 -->
<script src="https://api.mapbox.com/mapbox-gl-js/v3.18.1/mapbox-gl.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v3.18.1/mapbox-gl.css" rel="stylesheet" />
```

### 第 3 步：转换核心地图

从基本地图初始化开始：

1. 将 `new google.maps.Map()` 替换为 `new mapboxgl.Map()`
2. 修正坐标顺序（lat,lng -> lng,lat）
3. 更新缩放/中心

### 第 4 步：逐个转换功能

按复杂度优先级：

1. **简单：** 地图控件、基本标记点
2. **中等：** 弹窗、多边形、线条
3. **复杂：** 聚类、自定义样式、数据更新

### 第 5 步：更新事件处理程序

更改事件语法：

- `google.maps.event.addListener()` -> `map.on()`
- 更新事件属性名称（`latLng` -> `lngLat`）

### 第 6 步：针对 Mapbox 优化

利用 Mapbox 功能：

- 将多个标记点转换为数据驱动图层
- 使用聚类（内置）
- 利用矢量瓦片进行自定义样式
- 使用表达式进行动态样式

### 第 7 步：彻底测试

- 跨浏览器测试
- 移动端响应式
- 真实数据量下的性能
- 触摸/手势交互

## 常见问题和陷阱

### 坐标顺序

```javascript
// Google Maps
{ lat: 37.7749, lng: -122.4194 }

// Mapbox (颠倒！)
[-122.4194, 37.7749]
```

**务必检查坐标顺序！**

### 事件属性

```javascript
// Google Maps
map.on('click', (e) => {
  console.log(e.latLng.lat(), e.latLng.lng());
});

// Mapbox
map.on('click', (e) => {
  console.log(e.lngLat.lat, e.lngLat.lng);
});
```

### 时间问题

```javascript
// Google Maps - 立即
const marker = new google.maps.Marker({ map: map });

// Mapbox - 等待加载
map.on('load', () => {
  map.addSource(...);
  map.addLayer(...);
});
```

### 移除功能

```javascript
// Google Maps
marker.setMap(null);

// Mapbox - 必须移除两者
map.removeLayer('layer-id');
map.removeSource('source-id');
```

### 更新数据而不闪烁

**永远**不要移除并重新添加图层来更新数据——这会重新初始化 WebGL 资源并导致可见的闪烁。相反：

```javascript
// ✅ 原地更新数据（无闪烁）
map.getSource('stores').setData(newGeoJSON);

// ✅ 过滤现有数据（GPU 端，最快）
map.setFilter('stores-layer', ['==', ['get', 'category'], 'coffee']);

// ❌ BAD：移除 + 重新添加导致闪烁
map.removeLayer('stores-layer');
map.removeSource('stores');
map.addSource('stores', { ... });
map.addLayer({ ... });
```

## 不应迁移的情况

如果以下情况，考虑继续使用 Google Maps：

- **街景至关重要** - Mapbox 没有对应物
- **与 Google Workspace 深度集成** - 地点 API 深度集成
- **已经高度优化** - 迁移成本 > 收益
- **团队专业知识** - 培训成本过高
- **短期项目** - 不值得迁移努力

## 快速参考：并排比较

```javascript
// GOOGLE MAPS
const map = new google.maps.Map(el, {
  center: { lat: 37.7749, lng: -122.4194 },
  zoom: 12
});

const marker = new google.maps.Marker({
  position: { lat: 37.7749, lng: -122.4194 },
  map: map
});

google.maps.event.addListener(map, 'click', (e) => {
  console.log(e.latLng.lat(), e.latLng.lng());
});

// MAPBOX GL JS
mapboxgl.accessToken = 'YOUR_TOKEN';
const map = new mapboxgl.Map({
  container: el,
  center: [-122.4194, 37.7749], // 颠倒！
  zoom: 12,
  style: 'mapbox://styles/mapbox/streets-v12'
});

const marker = new mapboxgl.Marker()
  .setLngLat([-122.4194, 37.7749]) // 颠倒！
  .addTo(map);

map.on('click', (e) => {
  console.log(e.lngLat.lat, e.lngLat.lng);
});
```

**记住：** Mapbox 中 lng, lat 顺序！

## 额外资源

- [Mapbox GL JS 文档](https://docs.mapbox.com/mapbox-gl-js/)
- [官方 Google Maps 到 Mapbox 迁移指南](https://docs.mapbox.com/help/tutorials/google-to-mapbox/)
- [Mapbox 示例](https://docs.mapbox.com/mapbox-gl-js/examples/)
- [样式规范](https://docs.mapbox.com/mapbox-gl-js/style-spec/)

## 与其他技能的集成

**适用于：**

- **mapbox-web-integration-patterns**：特定框架的迁移指导
- **mapbox-web-performance-patterns**：迁移后优化
- **mapbox-token-security**：正确安全地使用 Mapbox 令牌
- **mapbox-geospatial-operations**：有效使用 Mapbox 的地理空间工具
- **mapbox-search-patterns**：迁移地理编码/搜索功能

## 参考文件

以下参考文件包含特定主题的详细迁移指南。在处理这些区域时加载它们：

- **`references/shapes-geocoding.md`** — 多边形、折线、自定义图标、地理编码
- **`references/directions-controls.md`** — 导航/路线、控件
- **`references/clustering-styling.md`** — 聚类、样式/外观
- **`references/data-performance.md`** — 数据更新、性能、常见迁移模式（店铺定位器、绘图工具、热图）
- **`references/api-services.md`** — API 服务比较、定价、插件、框架集成、测试、迁移清单

要加载参考文件，相对于此技能目录读取文件，例如：

```
Load references/shapes-geocoding.md
```
