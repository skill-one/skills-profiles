# 店铺定位模式技能

构建店铺定位器、餐厅查找器和基于位置的搜索应用程序的全面模式，使用 Mapbox GL JS。涵盖标记显示、筛选、距离计算、交互式列表和路线集成。

## 何时使用此技能

在构建以下应用程序时使用此技能：

- 在地图上显示多个位置（店铺、餐厅、办公室等）
- 允许用户筛选或搜索位置
- 计算从用户位置的距离
- 提供与地图标记同步的交互式列表
- 在弹窗或侧边栏中显示位置详情
- 集成到选定位置的路线

## 依赖项

**必需的：**

- Mapbox GL JS v3.x
- [@turf/turf](https://turfjs.org/) - 用于空间计算（距离、面积等）

**安装：**

```bash
npm install mapbox-gl @turf/turf
```

## 核心架构

### 模式概述

典型的店铺定位器通常包含：

1. **地图显示** - 显示所有位置为标记
2. **位置数据** - 包含店铺/位置信息的 GeoJSON
3. **交互式列表** - 侧边栏列出所有位置
4. **筛选** - 搜索、分类筛选、距离筛选
5. **详情视图** - 弹窗或面板显示位置详情
6. **用户位置** - 用于距离计算的地理位置。对于蓝色点位置指示器，使用内置的 `mapboxgl.GeolocateControl` —— 比自定义标记更简单。
7. **路线** - 到选定位置的路线（可选）

### 数据结构

**位置 GeoJSON 格式：**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-77.034084, 38.909671]
      },
      "properties": {
        "id": "store-001",
        "name": "市中心店铺",
        "address": "123 主街, 华盛顿特区, DC 20001",
        "phone": "(202) 555-0123",
        "营业时间": "周一至周六: 9am-9pm, 周日: 10am-6pm",
        "分类": "零售",
        "网站": "https://example.com/downtown"
      }
    }
  ]
}
```

**关键属性：**

- `id` - 每个位置的唯一标识符
- `name` - 显示名称
- `address` - 用于显示和地理编码的完整地址
- `coordinates` - `[经度, 纬度]` 格式
- `category` - 用于筛选（零售、餐厅、办公室等）
- 根据需要自定义属性（营业时间、电话、网站等）

## 基本店铺定位器实现

### 第一步：初始化地图和数据

```javascript
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

// 店铺位置数据
const stores = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [-77.034084, 38.909671]
      },
      properties: {
        id: 'store-001',
        name: '市中心店铺',
        address: '123 主街, 华盛顿特区, DC 20001',
        phone: '(202) 555-0123',
        category: '零售'
      }
    }
    // ... 更多店铺
  ]
};

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/standard',
  center: [-77.034084, 38.909671],
  zoom: 11
});
```

### 第二步：将标记添加到地图

**根据位置数量选择的标记策略：**

| 数量               | 策略                   | 原因                                                                         |
| ------------------- | -------------------------- | ------------------------------------------------------------------------------ |
| **少于 100**  | HTML 标记               | 完全控制 DOM/CSS；DOM 节点数量可管理                                     |
| **100–1,000**       | **符号图层**（默认） | 通过 WebGL 在 GPU 上渲染 — 一个 `<canvas>`，每个点零 DOM 元素                |
| **超过 1,000** | 聚类                 | 在大比例尺下减少视觉杂乱                                          |

> HTML 标记为每个点创建一个 DOM 元素。超过 ~100 个位置后，浏览器在布局/绘制上花费过多时间。符号图层完全绕过 DOM — GPU 在单个 WebGL 绘制调用中绘制所有点。

**符号图层实现**（100–1,000 个位置的最佳选择）。对于 HTML 标记（少于 100）或聚类（超过 1,000），请参阅 `references/markers.md`。

```javascript
map.on('load', () => {
  // 将店铺数据作为源添加
  map.addSource('stores', {
    type: 'geojson',
    data: stores
  });

  // 添加自定义标记图像
  map.loadImage('/marker-icon.png', (error, image) => {
    if (error) throw error;
    map.addImage('custom-marker', image);

    // 添加符号图层
    map.addLayer({
      id: 'stores-layer',
      type: 'symbol',
      source: 'stores',
      layout: {
        'icon-image': 'custom-marker',
        'icon-size': 0.8,
        'icon-allow-overlap': true,
        'text-field': ['get', 'name'],
        'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
        'text-offset': [0, 1.5],
        'text-anchor': 'top',
        'text-size': 12
      }
    });
  });

  // 使用交互式 API 处理标记点击（推荐）
  map.addInteraction('store-click', {
    type: 'click',
    target: { layerId: 'stores-layer' },
    handler: (e) => {
      const store = e.feature;
      flyToStore(store);
      createPopup(store);
    }
  });

  // 或使用传统事件监听器：
  // map.on('click', 'stores-layer', (e) => {
  //   const store = e.features[0];
  //   flyToStore(store);
  //   createPopup(store);
  // });
  //
  // 关于为什么推荐 addInteraction 而不是 map.on()，以及如何与
  // setFeatureState/appearances 配对以实现悬停和选中样式，请参阅
  // mapbox-style-patterns 技能中的 "interactions" 参考文件。

  // 悬停时更改光标
  map.on('mouseenter', 'stores-layer', () => {
    map.getCanvas().style.cursor = 'pointer';
  });

  map.on('mouseleave', 'stores-layer', () => {
    map.getCanvas().style.cursor = '';
  });
});
```

### 第三步：构建交互式位置列表

```javascript
function buildLocationList(stores) {
  const listingContainer = document.getElementById('listings');

  stores.features.forEach((store, index) => {
    const listing = listingContainer.appendChild(document.createElement('div'));
    listing.id = `listing-${store.properties.id}`;
    listing.className = 'listing';

    const link = listing.appendChild(document.createElement('a'));
    link.href = '#';
    link.className = 'title';
    link.id = `link-${store.properties.id}`;
    link.innerHTML = store.properties.name;

    const details = listing.appendChild(document.createElement('div'));
    details.innerHTML = `
      <p>${store.properties.address}</p>
      <p>${store.properties.phone || ''}</p>
    `;

    // 处理列表点击
    link.addEventListener('click', (e) => {
      e.preventDefault();
      flyToStore(store);
      createPopup(store);
      highlightListing(store.properties.id);
    });
  });
}

function flyToStore(store) {
  map.flyTo({
    center: store.geometry.coordinates,
    zoom: 15,
    duration: 1000
  });
}

function createPopup(store) {
  const popups = document.getElementsByClassName('mapboxgl-popup');
  // 移除现有弹窗
  if (popups[0]) popups[0].remove();

  new mapboxgl.Popup({ closeOnClick: true })
    .setLngLat(store.geometry.coordinates)
    .setHTML(
      `<h3>${store.properties.name}</h3>
       <p>${store.properties.address}</p>
       <p>${store.properties.phone}</p>
       ${store.properties.website ? `<a href="${store.properties.website}" target="_blank">访问网站</a>` : ''}`
    )
    .addTo(map);
}

// 重要提示：highlightListing 必须包含 scrollIntoView —— 没有它，
// 在地图上选择标记不会滚动侧边栏到列表。
function highlightListing(id) {
  // 移除现有高亮
  const activeItem = document.getElementsByClassName('active');
  if (activeItem[0]) {
    activeItem[0].classList.remove('active');
  }

  // 为选定列表添加高亮
  const listing = document.getElementById(`listing-${id}`);
  listing.classList.add('active');

  // 将选定列表滚动到视图中（关键用户体验要求）
  listing.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 加载时构建列表
map.on('load', () => {
  buildLocationList(stores);
});
```

## 参考文件

根据需要加载这些参考文件以获取更多模式：

| 参考文件                 | 文件                                   | 内容                                                         |
| ------------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| HTML 标记 & 聚类         | `references/markers.md`                | HTML 标记 (< 100 个位置), 聚类 (> 1000 个位置)    |
| 搜索 & 筛选           | `references/search-filter.md`          | 文本搜索, 分类筛选                                     |
| 地理位置 & 路线          | `references/geolocation-directions.md` | 用户位置, 距离计算, 路线方向                          |
| 样式 & 布局          | `references/styling-layout.md`         | 完整 HTML/CSS 布局, 自定义标记 CSS                          |
| 性能 & 可访问性        | `references/optimization-a11y.md`      | 防抖搜索, 数据管理, 错误处理, 可访问性                  |
| 变体 & React        | `references/variations-react.md`       | 移动优先, 全屏, 仅地图, React 实现                 |

## 资源

- [Turf.js](https://turfjs.org/) - 空间分析库（推荐用于距离计算）
- [Mapbox GL JS API](https://docs.mapbox.com/mapbox-gl-js/)
- [交互式 API 指南](https://docs.mapbox.com/mapbox-gl-js/guides/user-interactions/interactions/)
- [GeoJSON 规范](https://geojson.org/)
- [路线 API](https://docs.mapbox.com/api/navigation/directions/)
- [店铺定位器教程](https://docs.mapbox.com/help/tutorials/building-a-store-locator/)
