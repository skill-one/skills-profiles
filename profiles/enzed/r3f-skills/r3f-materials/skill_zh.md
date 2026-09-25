# React Three Fiber 材质

首先检查已安装的渲染器、Three.js、Fiber 和 Drei 版本。示例使用 Fiber 9 / React 19 与 WebGL。不要假设 Drei 基于着色器的材质在 WebGPU 上能原样工作。

## 选择最简单的适用材质

| 需求 | 起始点 | 限制 |
| --- | --- | --- |
| 无光照的艺术品或 UI 表面 | `meshBasicMaterial` | 仍参与输出颜色/色调映射策略 |
| 普通PBR表面 | `meshStandardMaterial` | 金属尤其需要环境或合适的光线 |
| 透明层、透射、光泽 | `meshPhysicalMaterial` | 仅启用所需特性；需要更多着色器工作 |
| 样式化光照 | `meshToonMaterial` | 需要光线；渐变贴图需要适当过滤 |
| 法线调试 | `meshNormalMaterial` | 有助于几何/法线检查 |
| 自定义着色 | ShaderMaterial 或节点材质 | 匹配 WebGL/GLSL 与 WebGPU/TSL |

## 带环境光照的PBR表面

挂载在 Canvas 下方。这个小程序理环境避免了远程预设依赖。

```tsx
import { Environment, Lightformer } from '@react-three/drei'

export default function Example() {
  return (
    <>
      <Environment resolution={64} frames={1}>
        <Lightformer position={[0, 3, 2]} scale={[5, 5, 1]} intensity={3} />
      </Environment>
      <mesh>
        <sphereGeometry args={[1, 32, 24]} />
        <meshStandardMaterial color="goldenrod" metalness={1} roughness={0.3} />
      </mesh>
    </>
  )
}
```

## PBR和颜色决策

- 使用接近 0 的 metalness 表示电介质，接近 1 表示裸金属；中间值通常描述混合或纹理过滤。粗糙度控制微观表面响应，而不是不透明度。
- 颜色/反照率纹理和自发光纹理使用 sRGB；粗糙度、metalness、法线、AO 和遮罩使用 `NoColorSpace`。保留正确加载的 glTF 纹理元数据。
- 贴图乘以标量设置：metalness 贴图 `metalness={0}` 没有作用；自发光贴图需要一个非黑色的自发光颜色。
- 法线贴图改变着色；位移贴图改变顶点，需要足够的几何细分。法线贴图不会改变轮廓。
- 自发光表面不会照亮附近几何体或自动产生光晕。当需要这些效果时，添加合适的光照和 bloom 管道。
- 近期 Three.js 发布中 PBR 外观有所改变。通过受控光照/曝光进行验证；不要盲目用额外光线或颜色转换来补偿升级。

## 透明度和玻璃

- `opacity < 1` 需要 `transparent` 进行普通 alpha 混合。对于切割的植物或贴花，考虑 `alphaTest` 以避免排序伪影；仅在需要时选择柔和透明。
- `depthWrite={false}` 可以帮助某些透明层，但不是万能解决方案。测试重叠顺序、背面和与不透明对象的交集。
- 使用物理透射表示玻璃，通常使用不透明度 1 和有意义的 `thickness`/IOR。透射不等于普通透明。
- Drei `MeshTransmissionMaterial` 和 `MeshReflectorMaterial` 添加场景渲染。从低分辨率/样本开始，测量后再启用背面传递或每个对象一个独立缓冲区。
- 共享透射采样器在某些场景中更便宜，但不能重现所有透明/透射对象之间的可见性。选择它之前阅读助手的文档。
- 不要到处启用 `DoubleSide`：它会改变渲染成本，并可能隐藏错误的绕组或法线。

## 生命周期和更新

- 当对象应共享外观时共享材质。更改一个实例的颜色、贴图或 uniform 前克隆；可以复用缓存 glTF 材质。
- R3F 拥有声明式材质子元素。外部分配/共享的材质需要显式生命周期所有权。销毁材质不会销毁其纹理。
- 通过类型化 ref 动画普通材质属性。值变化如粗糙度或颜色不需要 `needsUpdate`；着色器特性变化如添加/删除贴图可能需要重新编译。
- 材质数组需要匹配几何体组。单独的数组不会将任意材质分配给面。

## 验证

在预期光照和输出管道下渲染，然后测试透明重叠、阴影和重复挂载/卸载。添加透射或反射传递前比较 GPU 成本。

## 来源

- [MeshStandardMaterial](https://threejs.org/docs/#MeshStandardMaterial), [MeshPhysicalMaterial](https://threejs.org/docs/#MeshPhysicalMaterial), [Material](https://threejs.org/docs/#Material).
- [Drei 透射材质](https://drei.docs.pmnd.rs/shaders/mesh-transmission-material), [反射器材质](https://drei.docs.pmnd.rs/shaders/mesh-reflector-material).
- [颜色管理](https://threejs.org/manual/en/color-management.html), [Three.js 迁移指南](https://github.com/mrdoob/three.js/wiki/Migration-Guide).
