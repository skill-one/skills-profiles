# @json-render/react-three-fiber

json-render的React Three Fiber渲染器。19个内置3D组件。

## 两个入口点

| 入口点 | 导出 | 用于 |
|-------------|---------|---------|
| `@json-render/react-three-fiber/catalog` | `threeComponentDefinitions` | 目录模式（无R3F依赖，适用于服务器） |
| `@json-render/react-three-fiber` | `threeComponents`, `ThreeRenderer`, `ThreeCanvas`, 模式 | R3F实现和渲染器 |

## 使用模式

从标准定义中选择所需的3D组件：

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { threeComponentDefinitions } from "@json-render/react-three-fiber/catalog";
import { defineRegistry } from "@json-render/react";
import { threeComponents, ThreeCanvas } from "@json-render/react-three-fiber";

// 目录：选择定义
const catalog = defineCatalog(schema, {
  components: {
    Box: threeComponentDefinitions.Box,
    Sphere: threeComponentDefinitions.Sphere,
    AmbientLight: threeComponentDefinitions.AmbientLight,
    DirectionalLight: threeComponentDefinitions.DirectionalLight,
    OrbitControls: threeComponentDefinitions.OrbitControls,
  },
  actions: {},
});

// 注册：选择匹配的实现
const { registry } = defineRegistry(catalog, {
  components: {
    Box: threeComponents.Box,
    Sphere: threeComponents.Sphere,
    AmbientLight: threeComponents.AmbientLight,
    DirectionalLight: threeComponents.DirectionalLight,
    OrbitControls: threeComponents.OrbitControls,
  },
});
```

## 渲染

### ThreeCanvas（便利包装器）

```tsx
<ThreeCanvas
  spec={spec}
  registry={registry}
  shadows
  camera={{ position: [5, 5, 5], fov: 50 }}
  style={{ width: "100%", height: "100vh" }}
/>
```

### 手动Canvas设置

```tsx
import { Canvas } from "@react-three/fiber";
import { ThreeRenderer } from "@json-render/react-three-fiber";

<Canvas shadows>
  <ThreeRenderer spec={spec} registry={registry}>
    {/* 额外的R3F元素 */}
  </ThreeRenderer>
</Canvas>
```

## 可用组件（19）

### 基本组件（7）
- `Box` -- 宽度、高度、深度、材质
- `Sphere` -- 半径、宽度段数、高度段数、材质
- `Cylinder` -- 顶部半径、底部半径、高度、材质
- `Cone` -- 半径、高度、材质
- `Torus` -- 半径、管径、材质
- `Plane` -- 宽度、高度、材质
- `Capsule` -- 半径、长度、材质

所有基本组件共享：`position`, `rotation`, `scale`, `castShadow`, `receiveShadow`, `material`.

### 灯光（4）
- `AmbientLight` -- 颜色、强度
- `DirectionalLight` -- 位置、颜色、强度、castShadow
- `PointLight` -- 位置、颜色、强度、距离、衰减
- `SpotLight` -- 位置、颜色、强度、角度、半影

### 其他（8）
- `Group` -- 具有位置/旋转/缩放的容器，支持子元素
- `Model` -- 通过url属性加载GLTF/GLB
- `Environment` -- HDRI环境贴图（预设、背景、模糊、强度）
- `Fog` -- 线性雾（颜色、近、远）
- `GridHelper` -- 参考网格（大小、分割、颜色）
- `Text3D` -- SDF文本（文本、字体大小、颜色、锚点X、锚点Y）
- `PerspectiveCamera` -- 相机（位置、fov、近、远、makeDefault）
- `OrbitControls` -- 轨道控制（enableDamping、enableZoom、autoRotate）

## 共享模式

用于自定义3D目录定义的可重用Zod模式：

```typescript
import { vector3Schema, materialSchema, transformProps, shadowProps } from "@json-render/react-three-fiber";
import { z } from "zod";

// 自定义3D组件
const myComponentDef = {
  props: z.object({
    ...transformProps,
    ...shadowProps,
    material: materialSchema.nullable(),
    myCustomProp: z.string(),
  }),
  description: "我的自定义3D组件",
};
```

## 材质模式

```typescript
materialSchema = z.object({
  color: z.string().nullable(),         // 默认 "#ffffff"
  metalness: z.number().nullable(),     // 默认 0
  roughness: z.number().nullable(),     // 默认 1
  emissive: z.string().nullable(),      // 默认 "#000000"
  emissiveIntensity: z.number().nullable(), // 默认 1
  opacity: z.number().nullable(),       // 默认 1
  transparent: z.boolean().nullable(),  // 默认 false
  wireframe: z.boolean().nullable(),    // 默认 false
});
```

## Spec格式

3D规格使用标准的json-render扁平元素格式：

```json
{
  "root": "scene",
  "elements": {
    "scene": {
      "type": "Group",
      "props": { "position": [0, 0, 0] },
      "children": ["light", "box"]
    },
    "light": {
      "type": "AmbientLight",
      "props": { "intensity": 0.5 },
      "children": []
    },
    "box": {
      "type": "Box",
      "props": {
        "position": [0, 0.5, 0],
        "material": { "color": "#4488ff", "metalness": 0.3, "roughness": 0.7 }
      },
      "children": []
    }
  }
}
```

## 依赖项

必需的横向依赖：
- `@react-three/fiber` >= 8.0.0
- `@react-three/drei` >= 9.0.0
- `three` >= 0.160.0
- `react` ^19.0.0
- `zod` ^4.0.0
