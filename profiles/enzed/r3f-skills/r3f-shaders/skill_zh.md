# React Three Fiber着色器

## 选择着色器路径

首先检查已安装的Fiber、Drei、Three.js和渲染器的版本。示例使用Fiber 9 / React 19和WebGL。保留现有项目的版本。

- 当内置材质的属性表达效果时使用内置材质。对于自定义WebGL着色，使用Drei的`shaderMaterial`或原生`<shaderMaterial>`。
- WebGPU使用节点材质和TSL；GLSL的`ShaderMaterial`和`onBeforeCompile`无法移植到WebGPU。仅在渲染器相关时阅读[WebGPU和TSL](references/webgpu.md)。
- 着色器不会自动进行光照、阴影、雾化、实例化或蒙皮。在替换内置材质前选择所需功能。

## 动画WebGL材质

挂载在Canvas下方。将材质类和`extend`调用放在渲染外；局部组件避免全局JSX增强。

```tsx
import { useRef } from 'react'
import { extend, useFrame } from '@react-three/fiber'
import { shaderMaterial } from '@react-three/drei'
import { Color } from 'three'

const WaveMaterial = shaderMaterial(
  { uTime: 0, uColor: new Color('coral') },
  `uniform float uTime;
   varying vec2 vUv;
   void main() {
     vUv = uv;
     vec3 p = position;
     p.z += sin(p.x * 4.0 + uTime) * 0.15;
     gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
   }`,
  `uniform vec3 uColor;
   varying vec2 vUv;
   void main() {
     gl_FragColor = vec4(uColor * (0.4 + 0.6 * vUv.y), 1.0);
     #include <tonemapping_fragment>
     #include <colorspace_fragment>
   }`,
)
const Wave = extend(WaveMaterial)

export default function Example() {
  const material = useRef<InstanceType<typeof WaveMaterial>>(null)
  useFrame((_, delta) => {
    if (material.current) material.current.uTime += delta
  })
  return (
    <mesh>
      <planeGeometry args={[3, 3, 32, 32]} />
      <Wave ref={material} key={WaveMaterial.key} />
    </mesh>
  )
}
```

## Uniforms和编译

- Drei的`shaderMaterial`创建uniform访问器：分配`material.uTime`。原生ShaderMaterial使用`material.uniforms.uTime.value`。
- 保持uniform容器稳定；每帧无需通过React状态改变值。对于仅值变化的uniform，不要设置`material.needsUpdate`。
- 着色器源代码、定义和功能变化可能需要重新编译。使用类的`key`进行热重载；动画期间不要更改React键。
- Fiber 9中可用`extend(Class)`。对于小写全局元素，使用`ThreeElements`增强`ThreeElement<typeof Class>`；移除的`Object3DNode`不是材质类型的替代品。
- TypeScript不检查GLSL字符串。渲染它们并检查着色器编译错误，包括实际渲染器和效果的配置。
- 着色器源代码位于JavaScript模板字面量中，因此GLSL中的反引号或`${`任何位置（包括在注释中）都会静默结束字符串并破坏模块。编写着色器注释时不要使用反引号，让类型检查器捕获它而不是读取它。

## 空间、颜色和几何体

- 保持法线、光照方向和视图方向在同一坐标系中。`normalMatrix * normal`是视图空间；不要与世界空间相机方向点乘。
- 通过`Color`传递的CSS/十六进制颜色转换为线性工作空间。数值uniform向量已经是线性的；避免两次转换。
- 将颜色输入纹理标记为`SRGBColorSpace`；数据纹理使用`NoColorSpace`。纹理采样和输出转换必须与材质/渲染器管线匹配。
- 对于直接写入画布的WebGL着色器，按示例应用色调映射和输出颜色转换。不要手动伽马校正并应用输出块。当通过一个渲染时，让composer拥有最终输出。
- 顶点变形需要足够的几何体细分。如果需要光照，一致更新法线。对于阴影，深度/距离材质需要匹配变形；CPU射线投射和边界不会自动跟随GPU变形。
- 原生自定义实例化着色器必须考虑`instanceMatrix`和任何每个实例属性。蒙皮和形变目标同样需要相应的着色器逻辑。

## 修补内置WebGL材质

仅在保留内置材质的光照有用时使用`onBeforeCompile`。着色器块名称对版本敏感：检查安装的源代码，并在Three.js更新后进行渲染测试。

在首次编译前设置回调。当配置变化生成GLSL时，提供匹配的`customProgramCacheKey`并触发重新编译；将动画值保持在uniform中。不要假设`.clone()`或序列化会保留回调。当任务已针对WebGPU时，优先使用节点材质。

## 来源

- [Drei shaderMaterial](https://drei.docs.pmnd.rs/shaders/shader-material)，[Fiber类型迁移](https://github.com/pmndrs/react-three-fiber/blob/v9.7.0/docs/tutorials/v9-migration-guide.mdx)。
- [ShaderMaterial](https://threejs.org/docs/#ShaderMaterial)，[颜色管理](https://threejs.org/manual/en/color-management.html)。
- [Three.js迁移指南](https://github.com/mrdoob/three.js/wiki/Migration-Guide) — 仅检查安装版本的变化。
