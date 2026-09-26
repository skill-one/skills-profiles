# WebGPU Three.js with TSL

TSL（Three.js Shading Language）是一种基于节点的着色器抽象，它允许您使用 JavaScript 而不是 GLSL/WGSL 字符串来编写 GPU 着色器。

## 快速入门

```javascript
import * as THREE from 'three/webgpu';
import { color, time, oscSine } from 'three/tsl';

const renderer = new THREE.WebGPURenderer();
await renderer.init();

const material = new THREE.MeshStandardNodeMaterial();
material.colorNode = color(0xff0000).mul(oscSine(time));
```

## 技能内容

### 文档
- `docs/core-concepts.md` - 类型、运算符、uniforms、控制流
- `docs/materials.md` - 节点材质和所有属性
- `docs/compute-shaders.md` - 使用实例数组的 GPU 计算
- `docs/post-processing.md` - 内置和自定义效果
- `docs/wgsl-integration.md` - 自定义 WGSL 函数
- `docs/device-loss.md` - 处理 GPU 设备丢失和恢复
- `docs/limits-and-features.md` - WebGPU 设备限制和可选功能

### 示例
- `examples/basic-setup.js` - 最小 WebGPU 项目
- `examples/custom-material.js` - 自定义着色器材质
- `examples/particle-system.js` - GPU 计算粒子
- `examples/post-processing.js` - 效果管线
- `examples/earth-shader.js` - 完整地球带大气层

### 模板
- `templates/webgpu-project.js` - 启动项目模板
- `templates/compute-shader.js` - 计算着色器模板

### 参考
- `REFERENCE.md` - 快速参考速查表

## 关键概念

### 导入模式
```javascript
// 始终使用 WebGPU 入口
import * as THREE from 'three/webgpu';
import { /* TSL 函数 */ } from 'three/tsl';
```

### 节点材质
用 TSL 节点替换标准材质属性：
```javascript
material.colorNode = texture(map);        // 替代 material.map
material.roughnessNode = float(0.5);      // 替代 material.roughness
material.positionNode = displaced;         // 顶点位移
```

### 方法链式调用
TSL 使用方法链式调用来执行操作：
```javascript
// 替代：sin(time * 2.0 + offset) * 0.5 + 0.5
time.mul(2.0).add(offset).sin().mul(0.5).add(0.5)
```

### 自定义函数
使用 `Fn()` 来实现可重用的着色器逻辑：
```javascript
const fresnel = Fn(([power = 2.0]) => {
  const nDotV = normalWorld.dot(viewDir).saturate();
  return float(1.0).sub(nDotV).pow(power);
});
```

## 何时使用此技能

- 设置 Three.js 与 WebGPU 渲染器
- 使用 TSL 创建自定义着色器材质
- 编写 GPU 计算着色器
- 构建后处理管线
- 从 GLSL 迁移到 TSL
- 实现视觉效果（粒子、水、地形等）

## 资源

- [Three.js TSL Wiki](https://github.com/mrdoob/three.js/wiki/Three.js-Shading-Language)
- [WebGPU 示例](https://github.com/mrdoob/three.js/tree/master/examples) (文件以 `webgpu_` 开头)
