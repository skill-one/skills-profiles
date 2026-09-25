# Blender Web 渲染管线

## 概述

Blender Web 渲染管线技能提供了从 Blender 导出 3D 模型和动画到网络优化格式的流程（主要使用 glTF 2.0）。它涵盖了用于批量处理的 Python 脚本、针对网络性能的优化技术，以及与 Three.js 和 Babylon.js 等网络 3D 库的集成。

**何时使用此技能：**
- 为网络应用程序导出 Blender 模型
- 批量处理多个 3D 资产
- 优化文件大小以供网络传输
- 自动化重复的 Blender 任务
- 创建 3D 网络内容的制作流程
- 将旧格式转换为 glTF

**主要功能：**
- glTF 2.0 导出并优化
- Python (bpy) 自动化脚本
- 纹理烘焙和压缩
- 细节层次 (LOD) 生成
- 批量处理工作流程
- 针对 Web 的材质和光照优化

## 核心概念

### glTF 2.0 格式

**为何使用 glTF for Web：**
- 行业标准的网络 3D 格式
- 高效的二进制编码 (.glb)
- PBR 材质支持
- 动画和蒙皮
- 可扩展的自定义数据
- 广泛的库支持（Three.js、Babylon.js 等）

**glTF vs GLB：**
```
.gltf = JSON + 外部 .bin + 外部纹理
.glb  = 单个二进制文件（推荐用于网络）
```

### Blender Python API (bpy)

**通过 Python 访问 Blender 数据和操作：**

```python
import bpy

# 访问场景数据
scene = bpy.context.scene
objects = bpy.data.objects

# 修改对象
obj = bpy.data.objects['Cube']
obj.location = (0, 0, 1)
obj.scale = (2, 2, 2)

# 导出 glTF
bpy.ops.export_scene.gltf(
    filepath='/path/to/model.glb',
    export_format='GLB'
)
```

### 网络优化目标

**目标指标：**
- 文件大小：<5 MB 每个模型（理想 <1 MB）
- 多边形数量：<50k 三角形用于实时渲染
- 纹理分辨率：最大 2048x2048（推荐 1024x1024）
- 绘制调用：通过纹理图集最小化
- 加载时间：平均连接 <2 秒

## 常见模式

### 1. 基本glTF 导出（手动）

```python
# Blender Python 控制台或脚本

import bpy

# 选择要导出的对象（可选 - 如果未选择，则导出所有对象）
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['MyModel'].select_set(True)

# 导出为 GLB
bpy.ops.export_scene.gltf(
    filepath='/path/to/output.glb',
    export_format='GLB',                # 二进制格式
    use_selection=True,                 # 仅导出选定对象
    export_apply=True,                  # 应用修改器
    export_texcoords=True,              # UV 坐标
    export_normals=True,                # 法线
    export_materials='EXPORT',          # 导出材质
    export_colors=True,                 # 顶点颜色
    export_cameras=False,               # 跳过相机
    export_lights=False,                # 跳过灯光
    export_animations=True,             # 包含动画
    export_draco_mesh_compression_enable=True,  # 压缩几何体
    export_draco_mesh_compression_level=6,      # 0-10（推荐 6）
    export_draco_position_quantization=14,      # 8-14 位
    export_draco_normal_quantization=10,        # 8-10 位
    export_draco_texcoord_quantization=12       # 8-12 位
)
```

### 2. Python 脚本批量导出

```python
#!/usr/bin/env blender --background --python
"""
批量导出目录中的所有 .blend 文件到 glTF
用法：blender --background --python batch_export.py -- /path/to/blend/files
"""

import bpy
import os
import sys

# 获取命令行参数（-- 之后的部分）
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

input_dir = argv[0] if argv else "/path/to/models"
output_dir = argv[1] if len(argv) > 1 else input_dir + "_gltf"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 查找所有 .blend 文件
blend_files = [f for f in os.listdir(input_dir) if f.endswith('.blend')]

print(f"找到 {len(blend_files)} 个 .blend 文件")

for blend_file in blend_files:
    input_path = os.path.join(input_dir, blend_file)
    output_name = blend_file.replace('.blend', '.glb')
    output_path = os.path.join(output_dir, output_name)

    print(f"处理：{blend_file}")

    # 打开 blend 文件
    bpy.ops.wm.open_mainfile(filepath=input_path)

    # 导出为 GLB 并进行优化
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6
    )

    print(f"  导出：{output_name}")

print("批量导出完成！")
```

**运行批量脚本：**

```bash
blender --background --python batch_export.py -- /models/source /models/output
```

### 3. 为网络优化模型（简化）

```python
import bpy

def optimize_mesh(obj, target_ratio=0.5):
    """使用简化修改器减少多边形数量。"""

    if obj.type != 'MESH':
        return

    # 添加简化修改器
    decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = target_ratio  # 0.5 = 原始多边形数量的 50%
    decimate.use_collapse_triangulate = True

    # 应用修改器
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='Decimate')

    print(f"优化 {obj.name}：{len(obj.data.polygons)} 个多边形")

# 优化所有选定的网格
for obj in bpy.context.selected_objects:
    optimize_mesh(obj, target_ratio=0.3)
```

### 4. 网络纹理烘焙

```python
import bpy

def bake_textures(obj, resolution=1024):
    """将所有材质烘焙为单个纹理。"""

    # 设置烘焙设置
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'COMBINED'

    # 创建烘焙图像
    bake_image = bpy.data.images.new(
        name=f"{obj.name}_bake",
        width=resolution,
        height=resolution
    )

    # 创建烘焙材质
    mat = bpy.data.materials.new(name=f"{obj.name}_baked")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # 添加图像纹理节点
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = bake_image
    tex_node.select = True
    nodes.active = tex_node

    # 分配材质
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # 选择对象
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # 烘焙
    bpy.ops.object.bake(type='COMBINED')

    # 保存烘焙纹理
    bake_image.filepath_raw = f"/tmp/{obj.name}_bake.png"
    bake_image.file_format = 'PNG'
    bake_image.save()

    print(f"烘焙 {obj.name} 到 {bake_image.filepath_raw}")

# 烘焙选定对象
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        bake_textures(obj, resolution=2048)
```

### 5. 生成 LOD（细节层次）

```python
import bpy

def generate_lods(obj, lod_levels=[0.75, 0.5, 0.25]):
    """生成具有减少多边形数量的 LOD 复本。"""

    lod_objects = []

    for i, ratio in enumerate(lod_levels):
        # 复制对象
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = f"{obj.name}_LOD{i}"

        # 添加到场景
        bpy.context.collection.objects.link(lod_obj)

        # 添加简化修改器
        decimate = lod_obj.modifiers.new(name='Decimate', type='DECIMATE')
        decimate.ratio = ratio

        # 应用修改器
        bpy.context.view_layer.objects.active = lod_obj
        bpy.ops.object.modifier_apply(modifier='Decimate')

        lod_objects.append(lod_obj)

        print(f"创建 {lod_obj.name}：{len(lod_obj.data.polygons)} 个多边形")

    return lod_objects

# 为选定对象生成 LOD
if bpy.context.active_object:
    generate_lods(bpy.context.active_object)
```

### 6. 带纹理压缩的导出

```python
import bpy
import os

def export_optimized_gltf(filepath, texture_max_size=1024):
    """导出带纹理下采样的 glTF。"""

    # 下采样所有纹理
    for img in bpy.data.images:
        if img.size[0] > texture_max_size or img.size[1] > texture_max_size:
            img.scale(texture_max_size, texture_max_size)
            print(f"下采样 {img.name} 到 {texture_max_size}x{texture_max_size}")

    # 导出带 Draco 压缩
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_apply=True,
        export_image_format='JPEG',  # JPEG 以减小文件大小（或 PNG 以保证质量）
        export_jpeg_quality=85,       # 0-100
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=8,  # 最大压缩
        export_draco_position_quantization=12,
        export_draco_normal_quantization=8,
        export_draco_texcoord_quantization=10
    )

# 导出优化
export_optimized_gltf('/path/to/optimized.glb', texture_max_size=512)
```

### 7. 命令行自动化

```bash
#!/bin/bash
# 批量导出 Blender 文件到 glTF 而不打开 GUI

SCRIPT_DIR="$(dirname "$0")"

# 导出当前目录中的所有 .blend 文件
for blend_file in *.blend; do
    echo "导出 $blend_file..."

    blender --background "$blend_file" --python - <<EOF
import bpy
import os

# 获取输出文件名
filename = os.path.splitext(bpy.data.filepath)[0]
output = filename + '.glb'

# 导出
bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    export_apply=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6
)

print(f'导出到 {output}')
EOF

done

echo "所有文件导出完成！"
```

## 集成模式

### 与 Three.js

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const loader = new GLTFLoader();

// 设置 Draco 解码器以用于压缩模型
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');
loader.setDRACOLoader(dracoLoader);

// 加载 Blender 导出
loader.load('/models/exported.glb', (gltf) => {
  scene.add(gltf.scene);

  // 播放动画
  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(gltf.scene);
    const action = mixer.clipAction(gltf.animations[0]);
    action.play();
  }
});
```

### 与 React Three Fiber

```jsx
import { useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/models/exported.glb');
  return <primitive object={scene} />;
}

// 预加载以获得更好的性能
useGLTF.preload('/models/exported.glb');
```

### 与 Babylon.js

```javascript
import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

BABYLON.SceneLoader.ImportMesh(
  '',
  '/models/',
  'exported.glb',
  scene,
  (meshes) => {
    console.log('加载的网格：', meshes);
  }
);
```

## 优化技术

### 1. 几何体优化

**简化修改器：**
```python
# 减少 70% 的多边形数量
obj.modifiers.new(name='Decimate', type='DECIMATE')
obj.modifiers['Decimate'].ratio = 0.3
```

**合并距离：**
```python
# 删除重复顶点
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.object.mode_set(mode='OBJECT')
```

**三角化面：**
```python
# 确保所有面都是三角形（某些引擎需要）
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.quads_convert_to_tris()
bpy.ops.object.mode_set(mode='OBJECT')
```

### 2. 纹理优化

**图像压缩：**
```python
# 将纹理保存为 JPEG（有损但文件更小）
for img in bpy.data.images:
    img.file_format = 'JPEG'
    img.filepath_raw = f"/output/{img.name}.jpg"
    img.save()
```

**纹理图集：**
```python
# 将多个纹理合并为一个图集
# 使用智能 UV 投影进行自动图集
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
```

### 3. 材质简化

**转换为 PBR：**
```python
# 确保材质使用 Principled BSDF（glTF 标准）
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    principled = nodes.get('Principled BSDF')

    if not principled:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.get('Material Output')
        mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
```

## 常见陷阱

### 1. 文件过大

**问题：** 导出的 .glb 文件超过 20+ MB

**解决方案：**
- 启用 Draco 压缩（减少 60-90%）
- 减少纹理分辨率（2048 → 1024 或 512）
- 使用 JPEG 而不是 PNG 作为纹理
- 简化几何体（目标 <50k 三角形）
- 删除未使用的材质/纹理

### 2. 导出时缺少纹理

**问题：** 纹理在 Web 查看器中未显示

**解决方案：**
- 确保所有图像已保存（未打包）
- 使用相对路径引用纹理
- 导出时启用“导出图像”
- 检查图像格式兼容性（PNG/JPEG）

### 3. 动画无法播放

**问题：** 动画未导出或播放不正确

**解决方案：**
- 确保动画在时间轴上（不是 NLA 带状）
- 导出时启用“导出动画”
- 检查动画动作是否分配给对象
- 使用“烘焙动作”处理复杂骨架

### 4. 材质外观不同

**问题：** 材质在 Web 和 Blender 中渲染不同

**解决方案：**
- 使用 Principled BSDF（映射到 glTF PBR）
- 避免自定义着色器节点（无法导出）
- 使用支持的纹理类型（基础颜色、金属度、粗糙度、法线、发射）
- 在部署前在 glTF 查看器中测试

### 5. 导出时间过长

**问题：** 导出需要 10+ 分钟

**解决方案：**
- 导出前应用所有修改器（不要非破坏性导出）
- 减少几何体复杂度
- 删除未使用的数据（或进行孤儿清理）
- 使用命令行导出（比 GUI 更快）

### 6. 浏览器中的性能问题

**问题：** 模型在浏览器中卡顿

**解决方案：**
- 生成 LOD（细节层次）
- 使用实例化处理重复对象
- 限制绘制调用（合并对象、纹理图集）
- 减少多边形数量（<50k 三角形）
- 优化着色器（避免透明/折射）

## 最佳实践

### 导出前检查清单

```
☐ 应用所有修改器
☐ 合并顶点（删除重复）
☐ 三角化面（如果需要）
☐ 优化多边形数量（<50k 三角形）
☐ UV 展开 所有网格
☐ 烘焙材质（如果复杂）
☐ 调整纹理大小（最大 2048x2048）
☐ 使用 Principled BSDF 材质
☐ 删除未使用的数据（孤儿清理）
☐ 描述性命名对象
☐ 正确设置原点
☐ 应用变换（Ctrl+A）
```

### 导出设置

```python
# 推荐的 glTF 导出设置
bpy.ops.export_scene.gltf(
    filepath='/output.glb',
    export_format='GLB',                # 二进制格式
    export_apply=True,                  # 应用修改器
    export_image_format='JPEG',         # 更小的文件大小
    export_jpeg_quality=85,             # 质量与文件大小的平衡
    export_draco_mesh_compression_enable=True,  # 启用压缩
    export_draco_mesh_compression_level=6,      # 速度/大小的平衡（推荐 6）
    export_animations=True,             # 包含动画
    export_lights=False,                # 跳过灯光（在代码中重新创建）
    export_cameras=False                # 跳过相机
)
```

## 资源

此技能包含：

### scripts/
- `batch_export.py` - 批量导出 .blend 文件到 glTF
- `optimize_model.py` - 为网络优化几何体和纹理
- `generate_lods.py` - 自动生成 LOD 复本

### references/
- `gltf_export_guide.md` - 完整 glTF 导出参考
- `bpy_api_reference.md` - Blender Python API 快速参考
- `optimization_strategies.md` - 详细优化技术

### assets/
- `export_template.blend` - 预配置的导出模板
- `shader_library/` - 针对 Web 优化的 PBR 着色器

## 相关技能

- **threejs-webgl** - 在 Three.js 中加载和渲染导出的 glTF 模型
- **react-three-fiber** - 在 React 应用中使用 glTF 模型
- **babylonjs-engine** - 另一种用于网络的 3D 引擎
- **playcanvas-engine** - 支持 glTF 导入的游戏引擎
