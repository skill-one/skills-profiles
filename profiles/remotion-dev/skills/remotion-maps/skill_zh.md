# Remotion Maps

从预期的镜头中精确选择一种技术，然后仅加载该技术的 `TECHNIQUE.md`。
每个技术目录都是自包含的，删除其他文件而不会影响其运作。

## [Static map](techniques/static-map/TECHNIQUE.md)

- 需要将卫星图像抓取并挂载到 `<Img>` 标签中，并在其上层进行动画

## [Mapbox](techniques/mapbox/TECHNIQUE.md)

- 需要 Mapbox 密钥
- 默认样式更加美观
- 缩小后地图可以显示为圆形地球
- 包含埃菲尔铁塔等美观的 3D 建筑

## [MapLibre](techniques/maplibre/TECHNIQUE.md)

- 无需 API 密钥，完全免费
- 不包含 3D 建筑

## [MapTiler](techniques/maptiler/TECHNIQUE.md)

- 使用 MapTiler
- 可以在地理要素（边界、河流、标签）之上绘制标注

## [CesiumJS](techniques/cesium/TECHNIQUE.md)

- 可以穿越地形和山脉
- “飞行模拟器”视角
