# TresJS

基于 Three.js 构建 3D 场景的 Vue 3 框架。使用 Three.js 对象封装的声明式组件。

**包：** `@tresjs/core`（必需），`@tresjs/cientos`（辅助工具），`@tresjs/post-processing`（效果）

## 安装

```bash
# 核心（必需）
pnpm add three @tresjs/core

# 辅助工具 - 控制器、加载器、材质、场景
pnpm add @tresjs/cientos

# 后处理效果
pnpm add @tresjs/post-processing
```

## 快速参考

| 正在处理...                | 加载文件              |
| ---------------------------- | ---------------------- |
| TresCanvas, useTres, useLoop | references/core.md     |
| 控制器、加载器、材质       | references/cientos.md  |
| Bloom、glitch、DOF 效果   | references/effects.md  |
| 常见模式、配方             | references/cookbook.md |

## 加载文件

**根据您的任务进行加载：**

- [ ] [references/core.md](references/core.md) - TresCanvas 设置、组合式 API、事件、基础几何体
- [ ] [references/cientos.md](references/cientos.md) - OrbitControls、useGLTF、环境、材质
- [ ] [references/effects.md](references/effects.md) - EffectComposer、bloom、glitch、DOF
- [ ] [references/cookbook.md](references/cookbook.md) - 加载模型、带控制器的相机、动画循环、后处理

**不要一次性加载所有文件。** 仅加载相关的文件。

## 核心概念

### TresCanvas

创建 WebGL 渲染器和场景的根组件：

```vue
<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'
</script>

<template>
  <TresCanvas shadows alpha>
    <TresPerspectiveCamera :position="[5, 5, 5]" />
    <TresMesh>
      <TresBoxGeometry />
      <TresMeshStandardMaterial color="orange" />
    </TresMesh>
    <TresAmbientLight :intensity="0.5" />
    <TresDirectionalLight :position="[3, 3, 3]" :intensity="1" />
  </TresCanvas>
</template>
```

### 组件命名

所有 Three.js 类都可用作带有 `Tres` 前缀的 Vue 组件：

- `THREE.PerspectiveCamera` → `<TresPerspectiveCamera />`
- `THREE.Mesh` → `<TresMesh />`
- `THREE.BoxGeometry` → `<TresBoxGeometry />`
- `THREE.MeshStandardMaterial` → `<TresMeshStandardMaterial />`

通过 `:args` 属性传递构造函数参数：

```vue
<TresPerspectiveCamera :args="[75, 1, 0.1, 1000]" />
```

### 响应式

属性是响应式的 - 变化会更新 3D 场景：

```vue
<script setup>
const color = ref('orange')
const position = ref([0, 0, 0])
</script>

<template>
  <TresMesh :position="position">
    <TresMeshStandardMaterial :color="color" />
  </TresMesh>
</template>
```

### 基础几何体组件

直接注入现有的 Three.js 对象：

```vue
<script setup>
import { useGLTF } from '@tresjs/cientos'
const { scene } = await useGLTF('/model.glb')
</script>

<template>
  <primitive :object="scene" />
</template>
```

## 可用指南

**[references/core.md](references/core.md)** - TresCanvas 属性、useTres、useLoop、useGraph、事件、性能

**[references/cientos.md](references/cientos.md)** - OrbitControls、useGLTF、useTexture、环境、天空、材质、形状

**[references/effects.md](references/effects.md)** - EffectComposer vs EffectComposerPmndrs、bloom、glitch、DOF、效果堆叠

**[references/cookbook.md](references/cookbook.md)** - 加载 3D 模型、带控制器的相机、动画循环、后处理
