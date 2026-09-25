# Mapbox 样式模式技能

此技能提供经过实战检验的样式模式和图层配置，适用于常见的地图场景。

## 模式库

### 模式 1：餐厅/兴趣点查找器

**使用场景**：展示餐厅、咖啡馆、酒吧或其他兴趣点的消费类应用

**视觉要求**：

- 兴趣点必须立即可见
- 导航的街道上下文
- 中性背景（照片/内容叠加）
- 优化移动端

**推荐图层**：

```json
{
  "layers": [
    {
      "id": "background",
      "type": "background",
      "paint": {
        "background-color": "#f5f5f5"
      }
    },
    {
      "id": "water",
      "type": "fill",
      "source": "mapbox-streets",
      "source-layer": "water",
      "paint": {
        "fill-color": "#d4e4f7",
        "fill-opacity": 0.6
      }
    },
    {
      "id": "landuse-parks",
      "type": "fill",
      "source": "mapbox-streets",
      "source-layer": "landuse",
      "filter": ["==", "class", "park"],
      "paint": {
        "fill-color": "#e8f5e8",
        "fill-opacity": 0.5
      }
    },
    {
      "id": "roads-minor",
      "type": "line",
      "source": "mapbox-streets",
      "source-layer": "road",
      "filter": ["in", "class", "street", "street_limited"],
      "paint": {
        "line-color": "#e0e0e0",
        "line-width": {
          "base": 1.5,
          "stops": [
            [12, 0.5],
            [15, 2],
            [18, 6]
          ]
        }
      }
    },
    {
      "id": "roads-major",
      "type": "line",
      "source": "mapbox-streets",
      "source-layer": "road",
      "filter": ["in", "class", "primary", "secondary", "tertiary"],
      "paint": {
        "line-color": "#ffffff",
        "line-width": {
          "base": 1.5,
          "stops": [
            [10, 1],
            [15, 4],
            [18, 12]
          ]
        }
      }
    },
    {
      "id": "restaurant-markers",
      "type": "symbol",
      "source": "restaurants",
      "layout": {
        "icon-image": "restaurant-15",
        "icon-size": 1.5,
        "icon-allow-overlap": false,
        "text-field": ["get", "name"],
        "text-offset": [0, 1.5],
        "text-size": 12,
        "text-allow-overlap": false
      },
      "paint": {
        "icon-color": "#FF6B35",
        "text-color": "#333333",
        "text-halo-color": "#ffffff",
        "text-halo-width": 2
      }
    }
  ]
}
```

**关键特性**：

- 去饱和度基础地图（不与照片竞争）
- 高对比度标记（#FF6B35 橙色突出显示）
- 清晰的道路网络（浅灰色上的白色）
- 公园可见但微妙
- 文本光晕提高可读性

## 模式选择指南

### 决策树

**问题 1：主要内容是什么？**

- 用户生成的标记/图钉 -> **兴趣点查找器模式**
- 房产数据/边界 -> **房地产模式**
- 统计/分析数据 -> **数据可视化模式**
- 路线/导航 -> **导航模式**
- 实时跟踪/配送区域 -> **配送/物流模式**（客户标记应通过第二个圆圈图层 + requestAnimationFrame + setPaintProperty 包含脉冲动画；参见 references/delivery-logistics.md）

**问题 2：查看环境是什么？**

- 白天/办公室 -> 浅色主题
- 夜晚/暗环境 -> **暗黑模式模式**
- 可变 -> 提供主题切换

**问题 3：用户的主要操作是什么？**

- 浏览/探索 -> 专注于兴趣点，丰富细节
- 导航 -> 专注于道路，路线可见性
- 跟踪配送/物流 -> 实时更新，区域，状态
- 分析数据 -> 最小化基础地图，最大化数据
- 选择位置 -> 清晰边界，上下文

**问题 4：平台是什么？**

- 移动端 -> 简化，更大的触摸目标，较少细节
- 桌面端 -> 可以包含更多细节和复杂性
- 两者 -> 设计移动优先，增强桌面端

## 图层优化模式

### 性能模式：按缩放简化

```json
{
  "id": "roads",
  "type": "line",
  "source": "mapbox-streets",
  "source-layer": "road",
  "filter": [
    "step",
    ["zoom"],
    ["in", "class", "motorway", "trunk"],
    8,
    ["in", "class", "motorway", "trunk", "primary"],
    12,
    ["in", "class", "motorway", "trunk", "primary", "secondary"],
    14,
    true
  ],
  "paint": {
    "line-width": {
      "base": 1.5,
      "stops": [
        [4, 0.5],
        [10, 1],
        [15, 4],
        [18, 12]
      ]
    }
  }
}
```

## 参考文件

额外的模式和配置可在 `references/` 目录中找到。当需要特定模式时，加载相关文件。

| 文件                                                                         | 内容                                                                                             |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [references/real-estate.md](references/real-estate.md)                       | 模式 2：房地产地图 -- 房产边界，价格颜色编码，设施标记               |
| [references/data-viz-base.md](references/data-viz-base.md)                   | 模式 3：数据可视化基础地图 -- 最小化灰度基础地图用于分级统计/热力图叠加     |
| [references/navigation.md](references/navigation.md)                         | 模式 4：导航/路线地图 -- 路线显示，用户位置，转弯箭头                       |
| [references/dark-mode.md](references/dark-mode.md)                           | 模式 5：暗黑模式/夜间主题 -- 接近黑色背景，降低亮度                      |
| [references/delivery-logistics.md](references/delivery-logistics.md)         | 模式 6：配送/物流地图 -- 实时跟踪，区域，司机标记，预计到达时间徽章           |
| [references/expressions-clustering.md](references/expressions-clustering.md) | 数据驱动表达式模式 + 聚类用于密集兴趣点                                          |
| [references/common-modifications.md](references/common-modifications.md)     | 3D 建筑，地形/山影，自定义标记                                                      |
| [references/interactions.md](references/interactions.md)                     | `addInteraction` vs `setFeatureState` vs `appearances` -- 它们如何组合以及何时使用每个 |

**加载说明**：阅读与用户用例匹配的参考文件。例如，如果实现配送跟踪地图，加载 `references/delivery-logistics.md`。

## 测试模式

### 视觉回归检查清单

- [ ] 在缩放级别测试：4，8，12，16，20
- [ ] 在移动端验证（375px 宽度）
- [ ] 在桌面端验证（1920px 宽度）
- [ ] 测试密集数据
- [ ] 测试稀疏数据
- [ ] 检查标签冲突
- [ ] 验证颜色对比度（WCAG）
- [ ] 测试加载性能

## 何时使用此技能

在以下情况下调用此技能：

- 开始为特定用例创建新的地图样式
- 寻找图层配置示例
- 实现常见地图模式
- 优化现有样式
- 需要典型场景的成熟方案
- 调试样式问题
- 学习 Mapbox 样式最佳实践
