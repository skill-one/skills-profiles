# 数据可视化模式技能

Mapbox地图上数据可视化的全面模式。涵盖分级统计图、热力图、3D凸起、数据驱动样式、动画可视化以及针对数据密集型应用的性能优化。

## 何时使用此技能

当您需要：

- 在地图上可视化统计数据（人口、销售额、人口统计）
- 创建带颜色编码的区域分级统计图
- 构建热力图或聚类以可视化密度
- 添加3D可视化（建筑高度、地形高程）
- 基于属性实现数据驱动样式
- 动画化时间序列数据
- 处理需要优化的庞大数据集

## 可视化类型

### 分级统计图

**最适合：** 区域数据（州、县、邮政编码）、统计比较

**模式：** 基于数据值对多边形进行颜色编码

```javascript
map.on('load', () => {
  // 添加数据源（带有属性的GeoJSON）
  map.addSource('states', {
    type: 'geojson',
    data: 'https://example.com/states.geojson' // 带有人口属性的要素
  });

  // 添加数据驱动的颜色填充层
  map.addLayer({
    id: 'states-layer',
    type: 'fill',
    source: 'states',
    paint: {
      'fill-color': [
        'interpolate',
        ['linear'],
        ['get', 'population'],
        0,
        '#f0f9ff', // 低人口量的浅蓝色
        500000,
        '#7fcdff',
        1000000,
        '#0080ff',
        5000000,
        '#0040bf', // 高人口量的深蓝色
        10000000,
        '#001f5c'
      ],
      'fill-opacity': 0.75
    }
  });

  // 添加边框层
  map.addLayer({
    id: 'states-border',
    type: 'line',
    source: 'states',
    paint: {
      'line-color': '#ffffff',
      'line-width': 1
    }
  });

  // 添加悬停效果与可复用的弹窗
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  map.on('mousemove', 'states-layer', (e) => {
    if (e.features.length > 0) {
      map.getCanvas().style.cursor = 'pointer';

      const feature = e.features[0];
      popup
        .setLngLat(e.lngLat)
        .setHTML(
          `
          <h3>${feature.properties.name}</h3>
          <p>人口：${feature.properties.population.toLocaleString()}</p>
        `
        )
        .addTo(map);
    }
  });

  map.on('mouseleave', 'states-layer', () => {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });
});
```

> **`step` vs `interpolate`：** 上述示例使用`interpolate`实现平滑的颜色渐变。对于**离散颜色区间**（例如"低/中/高"），应使用`['step', ['get', 'population'], '#f0f0f0', 500000, '#fee0d2', 2000000, '#fc9272', 10000000, '#de2d26']`。当数据具有自然分类或边界值精确度重要时，优先使用`step`。

**颜色比例策略：**

```javascript
// 线性插值（连续比例）
'fill-color': [
  'interpolate',
  ['linear'],
  ['get', 'value'],
  0, '#ffffcc',
  25, '#78c679',
  50, '#31a354',
  100, '#006837'
]

// 步长区间（离散区间）
'fill-color': [
  'step',
  ['get', 'value'],
  '#ffffcc',  // 默认颜色
  25, '#c7e9b4',
  50, '#7fcdbb',
  75, '#41b6c4',
  100, '#2c7fb8'
]

// 案例化（分类数据）
'fill-color': [
  'match',
  ['get', 'category'],
  'residential', '#ffd700',
  'commercial', '#ff6b6b',
  'industrial', '#4ecdc4',
  'park', '#45b7d1',
  '#cccccc'  // 默认
]
```

### 热力图

**最适合：** 点密度、事件位置、事故聚类

**模式：** 可视化点的密度

```javascript
map.on('load', () => {
  // 添加数据源（点）
  map.addSource('incidents', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [-122.4194, 37.7749]
          },
          properties: {
            intensity: 1
          }
        }
        // ...更多点
      ]
    }
  });

  // 添加热力图层
  map.addLayer({
    id: 'incidents-heat',
    type: 'heatmap',
    source: 'incidents',
    maxzoom: 15,
    paint: {
      // 基于intensity属性增加权重
      'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity'], 0, 0, 6, 1],
      // 随着缩放级别增加而增强强度
      'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 15, 3],
      // 热力图颜色渐变
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0,
        'rgba(33,102,172,0)',
        0.2,
        'rgb(103,169,207)',
        0.4,
        'rgb(209,229,240)',
        0.6,
        'rgb(253,219,199)',
        0.8,
        'rgb(239,138,98)',
        1,
        'rgb(178,24,43)'
      ],
      // 根据缩放级别调整半径
      'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 15, 20],
      // 在高缩放级别下降低不透明度
      'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 7, 1, 15, 0]
    }
  });

  // 在高缩放级别下添加单个点的圆层
  map.addLayer({
    id: 'incidents-point',
    type: 'circle',
    source: 'incidents',
    minzoom: 14,
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 14, 4, 22, 30],
      'circle-color': '#ff4444',
      'circle-opacity': 0.8,
      'circle-stroke-color': '#fff',
      'circle-stroke-width': 1
    }
  });
});
```

## 最佳实践

### 颜色可访问性

```javascript
// 使用ColorBrewer比例尺以提高可访问性
// https://colorbrewer2.org/

// 良好：顺序（单色相）
const sequentialScale = ['#f0f9ff', '#bae4ff', '#7fcdff', '#0080ff', '#001f5c'];

// 良好：发散（双色相）
const divergingScale = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850'];

// 良好：定性（不同类别）
const qualitativeScale = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00'];

// 避免：红绿组合（对色盲友好）
// 使用：蓝橙或紫绿组合
```

### 错误处理

```javascript
// 处理缺失或无效数据
map.on('load', () => {
  map.addSource('data', {
    type: 'geojson',
    data: dataUrl
  });

  map.addLayer({
    id: 'data-viz',
    type: 'fill',
    source: 'data',
    paint: {
      'fill-color': [
        'case',
        ['has', 'value'], // 检查属性是否存在
        ['interpolate', ['linear'], ['get', 'value'], 0, '#f0f0f0', 100, '#0080ff'],
        '#cccccc' // 缺失数据的默认颜色
      ]
    }
  });

  // 处理地图错误
  map.on('error', (e) => {
    console.error('地图错误:', e.error);
  });
});
```

## 数据大小规则

- **< 1 MB**：直接使用GeoJSON
- **1–10 MB**：根据复杂度考虑使用GeoJSON或矢量瓦片
- **> 10 MB**：使用矢量瓦片（上传至Mapbox作为瓦片集）

有关实现细节，请参阅[references/performance.md](references/performance.md)。

## 参考文件

为获取更多可视化模式，加载相关参考文件：

- **[references/clustering.md](references/clustering.md)** — 点聚类、自定义聚类属性、聚类与热力图对比
- **[references/3d-extrusions.md](references/3d-extrusions.md)** — 3D建筑凸起、自定义数据源、数据驱动高度
- **[references/circles-lines.md](references/circles-lines.md)** — 圆形/气泡图、线数据可视化、交通流量样式
- **[references/animation.md](references/animation.md)** — 时间序列动画、实时数据更新、平滑过渡
- **[references/performance.md](references/performance.md)** — 矢量瓦片与GeoJSON、要素状态、过滤、渐进式加载
- **[references/legends-use-cases.md](references/legends-use-cases.md)** — 图例UI、数据检查器、数据预处理、选举/COVID/房地产案例

## 资源

- [Mapbox表达式参考](https://docs.mapbox.com/style-spec/reference/expressions/)
- [ColorBrewer](https://colorbrewer2.org/) - 地图的色彩比例尺
- [Turf.js](https://turfjs.org/) - 空间分析
- [Simple Statistics](https://simple-statistics.github.io/) - 数据分类
- [数据可视化教程](https://docs.mapbox.com/help/tutorials/#data-visualization)
