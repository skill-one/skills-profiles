# React Three Fiber 纹理

首先检查已安装的 Three.js、Fiber、Drei 和渲染器版本。示例针对 Fiber 9 / React 19 和 Three.js r185（使用 WebGL）。保留正确配置的资产，而不是每次都重置纹理。

## 颜色与数据

| 纹理内容 | 颜色空间注释 |
| --- | --- |
| PNG/JPEG 基色或自发光色 | `SRGBColorSpace` |
| 粗糙度、金属度、法线、AO、透明度/蒙版 | `NoColorSpace` |
| 线性 HDR/EXR 光照数据 | 保留加载器提供的线性元数据 |

`NoColorSpace` 不是 `LinearSRGBColorSpace` 的另一个名称：标量/向量数据没有颜色空间。不要将所有贴图一概转换为 sRGB。

## 加载颜色贴图

在 Suspense 下挂载到 Canvas 中。文件路径是应用程序资产，而不是由此技能提供的文件。

```tsx
import { useTexture } from '@react-three/drei'
import { SRGBColorSpace } from 'three'

export default function Example() {
  const map = useTexture('/textures/checker.png', (texture) => {
    // 此 URL 总是被所有消费者用作颜色纹理。
    texture.colorSpace = SRGBColorSpace
    texture.needsUpdate = true
  })
  return (
    <mesh>
      <planeGeometry args={[3, 3]} />
      <meshStandardMaterial map={map} roughness={1} />
    </mesh>
  )
}
```

Fiber 处理常见的内置颜色贴图属性，glTF 加载器设置纹理元数据。显式注释对于自定义着色器统一变量或手动创建的纹理尤为重要。

## 缓存和所有权

- `useTexture`/`useLoader` 按加载器和 URL 输入进行缓存。相同的源可以返回相同的 Texture 对象。重复、偏移、包裹、过滤和 colorSpace 变化会影响所有消费者。
- 在进行实例配置之前克隆 Texture 对象。尽可能重用底层图像；仅单独销毁你拥有的克隆。不要从单个消费者处销毁缓存的源。
- 在渲染期间不要清除加载器缓存。缓存淘汰和 GPU 销毁是单独的操作，需要知道没有活动的消费者仍然需要该资源。
- 避免每帧替换统一变量/纹理对象；直接更新偏移或拥有的值。在按需循环中，在强制性更改后使纹理失效。

## UV 和采样

- `texture.channel = 0` 选择 `uv`，1 选择 `uv1`，然后是 `uv2` 和 `uv3`。选择实际的几何属性；AO/光照贴图不再需要将 `uv` 复制到 `uv2`。
- 在 [0, 1] 外重复需要 RepeatWrapping 或 MirroredRepeatWrapping。偏移/重复/旋转是纹理变换；纹理动画通常不需要每帧的 React 状态。
- 包裹、颜色空间和上传配置更改可能需要 `texture.needsUpdate`。偏移/重复变化使用纹理矩阵，通常不需要重新上传图像数据。
- 对于像素艺术，故意使用最近邻过滤。对于压缩表面，mipmaps 减少闪烁；将各向异性限制为渲染器支持的最高值和场景需求。
- 2 的幂次方尺寸不是 WebGL2 的通用要求。根据屏幕覆盖范围、内存、压缩格式约束和质量来调整纹理尺寸，而不是过时的通用规则。
- 下载大小不是 GPU 内存大小。在支持的情况下考虑 KTX2/Basis；故意配置渲染器能力检测和主机解码器/转码器资产。
- 对于替换的 glTF 颜色贴图，匹配模型的 UV/方向约定；手动加载的纹理通常需要 `flipY=false`。不要再次翻转已配置的 glTF 贴图。

## 专用纹理

- 当其生命周期匹配时，优先使用 `useVideoTexture`。检查自动播放/静音、CORS、用户手势和源清理；更改视频分辨率可能需要新纹理。不要承诺所有浏览器都成功自动播放。
- Canvas/DataTexture 内容变化需要 `needsUpdate`；数据纹理应保留数据颜色空间语义。在帧循环中创建纹理除非故意管理，否则会泄漏工作/资源。
- 对于渲染目标，请参阅 [离屏渲染](references/render-targets.md)。在渲染到同一目标时，永远不要从该纹理中采样。
- 将环境贴图保留在光照路径上（`Environment`/`useEnvironment`），而不是直接分配没有合适映射/PMREM 工作流的普通 2D 图像。

## 验证

测试已知颜色样本、在变化光照下的数据贴图、纹理方向、重复挂载和具有不同 UV 变换的两个消费者。检查 GPU 纹理计数；它们是计数，不是精确的字节内存测量。

## 来源

- [颜色管理](https://threejs.org/manual/en/color-management.html)，[纹理](https://threejs.org/docs/#Texture)。
- [Drei useTexture](https://drei.docs.pmnd.rs/loaders/texture-use-texture)，[useVideoTexture](https://drei.docs.pmnd.rs/loaders/video-texture-use-video-texture)。
- [Fiber 9 纹理变更](https://github.com/pmndrs/react-three-fiber/blob/v9.7.0/docs/tutorials/v9-migration-guide.mdx)。
