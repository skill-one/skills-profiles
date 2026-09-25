# Remotion 地图

从预想镜头中选择一种技术，然后仅加载该技术的 `TECHNIQUE.md` 文件。
每个技术目录都是自包含的，可以移除而不会影响其他技术。

## [静态地图](techniques/static-map/TECHNIQUE.md)

- 需要您获取卫星图像并在 `<Img>` 标签中挂载它，并在其上方进行动画

## [Mapbox](techniques/mapbox/TECHNIQUE.md)

- 需要一个 Mapbox 密钥
- 默认样式更美观
- 放大时地图可以显示圆形地球
- 包含精美的 3D 建筑，如埃菲尔铁塔

## [MapLibre](techniques/maplibre/TECHNIQUE.md)

- 无需 API 密钥，完全免费
- 不包含 3D 建筑

## [MapTiler](techniques/maptiler/TECHNIQUE.md)

- 使用 MapTiler
- 注释可以在地理特征（如边界、河流、标签）上方绘制

## [CesiumJS](techniques/cesium/TECHNIQUE.md)

- 飞越地形和山脉
- "飞行模拟器"视角
