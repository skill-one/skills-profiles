# React Three Fiber 几何体

在复制构造函数参数或辅助属性之前，请检查已安装的 Three.js、Fiber 和 Drei 版本。示例针对 Fiber 9 / React 19 和 Three.js r185。

## 选择表示方式

- 使用原生 JSX 几何体表示普通形状。`args` 与 Three.js 构造函数匹配；更改它们会重建几何体，因此应动画化变换而不是构造函数输入。
- 使用 `BufferGeometry` 表示自定义拓扑，使用基于缓冲区的 `points` 表示大型粒子集。保持生成的数组稳定，并在结果必须可重复时使用确定性生成。
- 使用 Drei `Instances` 表示具有事件的便捷声明式实例。对于大型或频繁更新的集合，请阅读 [原生实例化](references/instancing.md) 以避免每个实例的 React 开销。
- 实例化共享几何体/材质并减少绘制调用。仅仅在单独的网格之间共享几何体并不会批量它们的绘制。
- Drei `Merged` 从 **网格** 创建实例化抽象，而不是 BufferGeometry 对象；它不会连接任意静态几何体。对于实际合并，请检查 `three/addons/utils/BufferGeometryUtils.js` 中的 `mergeGeometries` 并确保兼容的属性/索引。

## 声明式实例

在带有照明的 Canvas 下挂载。每个实例属于其最近的实例提供者。

```tsx
import { Instance, Instances } from '@react-three/drei'

export default function Example() {
  return (
    <Instances limit={3} range={3}>
      <boxGeometry args={[0.7, 0.7, 0.7]} />
      <meshStandardMaterial />
      <Instance position={[-1.2, 0, 0]} color="coral" />
      <Instance position={[0, 0, 0]} color="skyblue" />
      <Instance position={[1.2, 0, 0]} color="gold" />
    </Instances>
  )
}
```

## 自定义缓冲区和更新

- `position` 和 `normal` 属性通常具有项目大小 3；UVs 具有项目大小 2。使用 `args={[typedArray, itemSize]}` 和正确的 `attach` 构造 JSX 缓冲区属性，而不仅仅是没有构造函数参数的 `array`/`count` 属性。
- 索引引用顶点；绕组决定正面。在硬法线或 UV 缝合处重复顶点。索引顶点共享所有属性，而不仅仅是位置。
- 照明几何体需要法线。在适当的时候使用 `computeVertexNormals()`；如果着色器或分析法线可以更便宜地表达变形，则不要每帧重新计算。
- 在 CPU 缓冲区写入后，设置 `attribute.needsUpdate = true`。在缓冲区经常变化时，在第一次 GPU 上传之前选择动态使用。
- 在几何体变化影响它们之后重新计算边界框/球体。GPU 顶点位移不会自动更新 CPU 边界或射线投射。
- UV 选择在现代 Three.js 中是显式的：`texture.channel` 选择 `uv`、`uv1`、`uv2` 或 `uv3`。不要无条件地将 `uv` 复制到 `uv2` 以用于 AO。
- 避免为指针移动重建缓冲区。如果拓扑是固定的，请更改属性内容或uniforms而不是重建缓冲区。

## 辅助工具和权衡

- Drei `Line` 支持有用的线宽；原生 WebGL 线宽受限于平台。选择屏幕空间与世界空间厚度时，请检查 `worldUnits`。
- 使用 Drei `Text` 表示平面文本，使用 `Text3D` 表示挤压几何体。当前的 TextGeometry 使用 `depth` 而不是历史 `height`；验证辅助工具的已安装类型和字体格式。
- 使用 `Edges` 表示锐边轮廓，而不是作为屏幕空间选择效果的替代品。
- `Bounds` 和 `Center` 改变框架/变换；决定它们是否应在资源加载、调整大小或交互后更新。
- 段数应遵循轮廓、变形和观看距离。一个“高质量”的固定数量并不总是更好。
- 声明式创建的几何体可以由 R3F 拥有。共享或缓存的几何体需要一个共享的生命周期；不要在一个实例卸载时释放其他仍在挂载的实例。

## 验证

在更新后检查边界/剔除、射线投射命中位置、资源清理和绘制调用。在目标对象数量下测试；三个实例不会在十万个时建立性能。

## 来源

- [BufferGeometry](https://threejs.org/docs/#BufferGeometry), [BufferAttribute](https://threejs.org/docs/#BufferAttribute), [InstancedMesh](https://threejs.org/docs/#InstancedMesh).
- [Drei Instances](https://drei.docs.pmnd.rs/performances/instances), [Merged](https://drei.docs.pmnd.rs/performances/merged), [Text3D](https://drei.docs.pmnd.rs/abstractions/text3d).
