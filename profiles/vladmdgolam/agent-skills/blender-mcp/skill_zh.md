# Blender MCP

## 工具选择

使用**结构化 MCP 工具** (`get_scene_info`, `screenshot`) 进行快速检查。

使用 **`execute_python`** 处理任何非简单操作：层级遍历、材质提取、动画烘焙、批量操作。它提供完整的 `bpy` API 访问并避免工具模式限制。

使用**无头 CLI**进行 GLTF 导出 — MCP 服务器在导出操作上会超时。

## 健康检查（始终首先）

1. `get_scene_info` — 验证连接（默认端口 9876）
2. `execute_python` 使用 `print("ok")` — 验证 Python 是否正常工作
3. `screenshot` — 验证视口捕获是否正常

如果 MCP 无响应，请检查 Blender MCP 插件是否已启用以及套接字服务器是否正在运行。

## 完整导出工作流程

这是端到端的线性叙述。按顺序执行以下步骤。不要跳过步骤。

### 第 1 步：健康检查

在触摸其他任何内容之前，确认 MCP 是活跃的：

```bash
# 在 MCP 工具调用中：
get_scene_info
execute_python: print("ok")
screenshot
```

如果任何步骤失败，请停止并首先修复 MCP 连接性。参见 [已知错误](#已知错误--workarounds)。

### 第 2 步：检查场景

运行完整的层级提取以了解您正在处理的内容：

```python
import bpy, json

def extract_hierarchy(obj, depth=0):
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": not obj.hide_viewport,
        "children": [],
    }
    if obj.type == 'MESH' and obj.data:
        data["vertices"] = len(obj.data.vertices)
        data["faces"] = len(obj.data.polygons)
        data["materials"] = [slot.material.name for slot in obj.material_slots if slot.material]
    if obj.type == 'LIGHT':
        data["light_type"] = obj.data.type
        data["energy"] = obj.data.energy
        data["color"] = list(obj.data.color)
    for mod in obj.modifiers:
        if mod.type == 'ARRAY':
            data.setdefault("modifiers", []).append({
                "type": "ARRAY",
                "count": mod.count,
                "offset_object": mod.offset_object.name if mod.offset_object else None,
            })
    for child in obj.children:
        data["children"].append(extract_hierarchy(child, depth + 1))
    return data

scene_data = {
    "name": bpy.context.scene.name,
    "fps": bpy.context.scene.render.fps,
    "frame_start": bpy.context.scene.frame_start,
    "frame_end": bpy.context.scene.frame_end,
    "objects": [],
}
for obj in bpy.context.scene.objects:
    if obj.parent is None:
        scene_data["objects"].append(extract_hierarchy(obj))

print(json.dumps(scene_data, indent=2))
```

查找：
- Array 修改器（如果烘焙会膨胀文件大小 — 必须在运行时复制）
- 具有许多顶点的对象（导出风险慢或 GLB 文件大）
- 您可能想要或不想要导出的隐藏对象
- 缺失材质（空的 `material_slots`）

### 第 3 步：验证材质

运行材质提取以在提交导出之前捕获导出损失：

```python
import bpy, json

def extract_materials():
    materials = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        info = {"name": mat.name, "nodes": [], "warnings": []}
        has_principled = False
        for node in mat.node_tree.nodes:
            node_data = {"type": node.type, "name": node.name}
            if node.type == 'BSDF_PRINCIPLED':
                has_principled = True
                for inp in node.inputs:
                    if inp.is_linked:
                        node_data[inp.name] = "linked"
                    elif hasattr(inp, 'default_value'):
                        val = inp.default_value
                        try:
                            node_data[inp.name] = list(val)
                        except TypeError:
                            node_data[inp.name] = float(val)
            if node.type == 'TEX_IMAGE' and node.image:
                node_data["image"] = node.image.filepath
                node_data["size"] = [node.image.size[0], node.image.size[1]]
                if node.image.size[0] > 2048:
                    info["warnings"].append(f"大纹理: {node.image.filepath} ({node.image.size[0]}x{node.image.size[1]})")
            if node.type in ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MUSGRAVE'):
                info["warnings"].append(f"程序纹理节点 '{node.name}' ({node.type}) 在 GLTF 导出时将丢失")
            if node.type == 'VALTORGB':  # 颜色渐变
                info["warnings"].append(f"颜色渐变 '{node.name}' 映射将在 GLTF 导出时丢失")
        if not has_principled:
            info["warnings"].append("未找到 Principled BSDF — 导出结果不可预测")
        info["nodes"].append(node_data)
        materials.append(info)
    return materials

result = extract_materials()
for mat in result:
    if mat["warnings"]:
        print(f"WARN [{mat['name']}]: {'; '.join(mat['warnings'])}")
print(json.dumps(result, indent=2))
```

在继续之前查看所有警告。决定：现在烘焙程序纹理，或在导出后运行时修补材质。

### 第 4 步：通过无头 CLI 导出

MCP 服务器无法处理 GLTF 导出（超时）。始终使用无头 CLI：

```bash
# 如果 Blender 在 PATH 中，使用 'blender'，否则使用平台特定路径：
#   macOS:   /Applications/Blender.app/Contents/MacOS/Blender
#   Windows: "C:\Program Files\Blender Foundation\Blender 4.x\blender.exe"
#   Linux:   /usr/bin/blender
blender \
  --background "/path/to/scene.blend" \
  --python-expr "
import bpy, os
export_path = '/path/to/output.glb'
os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=True,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
)
size_mb = os.path.getsize(export_path) / 1024 / 1024
print(f'导出完成: {export_path} ({size_mb:.1f} MB)')
"
```

**关键标志：**
- `export_apply=False` — 不要应用修改器（Array 修改器将 1 MB 膨胀为 56 MB）
- `export_draco_mesh_compression_enable=False` — 之后通过 gltf-transform 应用 Draco
- 引用所有可能包含空格的路径

### 第 5 步：使用 gltf-transform 优化

导出成功后运行。始终使用单个步骤，决不使用 `optimize`：

```bash
# 1. 首先检查原始导出
npx @gltf-transform/cli inspect output.glb

# 2. 调整纹理大小（最大 1K 用于网络/移动）
npx @gltf-transform/cli resize output.glb resized.glb --width 1024 --height 1024

# 3. WebP 压缩（质量 90 保留细节）
npx @gltf-transform/cli webp resized.glb webp.glb --quality 90

# 4. Draco 网格压缩（最后一步 — 不可逆）
npx @gltf-transform/cli draco webp.glb final.glb

# 5. 检查最终结果
npx @gltf-transform/cli inspect final.glb
```

预期大小减少：~22 MB 原始 → ~3.7 MB (WebP) → ~1 MB (Draco)。参见 [references/texture-optimization.md](references/texture-optimization.md) 获取详细指标。

### 第 6 步：验证

在交付 GLB 进行集成之前，运行以下完整的导出后验证清单。

## 导出后验证清单

每次导出后，在移交 GLB 进行集成之前，验证以下内容：

- [ ] **文件大小合理** — 原始 GLB 小于 30 MB，优化后的 GLB 小于 5 MB 对于典型的网络场景。标记任何超过这些阈值的内容。
- [ ] **使用 gltf-transform CLI 检查** — 运行 `npx @gltf-transform/cli inspect final.glb` 并检查：网格数量、纹理数量、纹理大小、动画数量、访问器大小。没有意外的重复。
- [ ] **在 Babylon.js 沙盒中视觉测试** — 将 GLB 拖放到 [sandbox.babylonjs.com](https://sandbox.babylonjs.com)。验证：网格正确渲染、纹理显示、动画播放、没有黑色/粉色材质。
- [ ] **没有 Three.js 控制台错误** — 在最小化的 Three.js GLTFLoader 测试页面中加载并检查浏览器控制台。常见错误：`THREE.GLTFLoader: 未知扩展`、缺失纹理文件、不支持的 Draco 版本。
- [ ] **材质快速检查** — 选择 3-5 个材质并视觉确认粗糙度、金属度和基础颜色看起来正确。与 Blender 视口渲染进行比较。标记任何看起来平坦或过于闪亮的材质。
- [ ] **动画快速检查** — 如果场景有动画，验证至少一个在 Babylon.js 沙盒或 Three.js 中正确播放。检查帧数是否与预期匹配。
- [ ] **名称映射已验证** — 如果运行时代码引用网格名称，请确认导出后的 GLTF 转换后名称匹配（空格→下划线，点被移除）。参见 [关键规则 5](#5-gltf-name-mapping)。
- [ ] **没有缺失的纹理** — 检查 Babylon.js 沙盒网络标签。没有纹理文件的 404。所有纹理都应打包在 GLB 内。

## 示例

### 示例 1：导出带动画的角色绑定

**场景：** 您有一个类人角色，带有骨架、3 个 NLA 动作（空闲、行走、奔跑）、PBR 纹理集，以及通过父子关系附加的武器。您需要一个用于 Three.js 场景的 Web 兼容 GLB。

**步骤 1：健康检查和场景检查**

```bash
# MCP 工具调用
get_scene_info
execute_python: print("ok")
```

**步骤 2：检查绑定**

```python
import bpy, json

# 检查骨架和 NLA 条带
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        print(f"骨架: {obj.name}")
        if obj.animation_data:
            print(f"  活动动作: {obj.animation_data.action.name if obj.animation_data.action else '无'}")
            for track in obj.animation_data.nla_tracks:
                print(f"  NLA 轨道: {track.name}")
                for strip in track.strips:
                    print(f"    条带: {strip.name}, 帧 {strip.frame_start}-{strip.frame_end}")
```

**步骤 3：检查材质以防止导出损失**

运行上述材质提取。对于角色，注意：
- 程序皮肤纹理节点（噪声→颜色变化）—— 这些将被丢失
- 粗糙度上的颜色渐变—— 将被丢失，粗糙度看起来会平坦
- 决定：现在烘焙程序变化到图像纹理，或在运行时修补粗糙度值

**步骤 4：导出**

```bash
blender \
  --background "/path/to/character.blend" \
  --python-expr "
import bpy, os, tempfile
export_dir = tempfile.gettempdir()
bpy.ops.export_scene.gltf(
    filepath=os.path.join(export_dir, 'character.glb'),
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=False,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
    export_skins=True,
    export_morph=True,
)
print('完成:', os.path.getsize(os.path.join(export_dir, 'character.glb')) / 1024 / 1024, 'MB')
"
```

**步骤 5：验证动画是否导出**

```bash
npx @gltf-transform/cli inspect character.glb | grep -i anim
```

预期输出：3 个动画（空闲、行走、奔跑）。如果为 0，请检查 NLA 条带是否被静音或轨道是否设置为独占。

**步骤 6：优化**

```bash
npx @gltf-transform/cli resize character.glb char_resized.glb --width 1024 --height 1024
npx @gltf-transform/cli webp char_resized.glb char_webp.glb --quality 90
npx @gltf-transform/cli draco char_webp.glb character_final.glb
```

**步骤 7：运行时动画设置（Three.js）**

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import * as THREE from 'three';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');

const loader = new GLTFLoader();
loader.setDRACOLoader(dracoLoader);

loader.load('/character_final.glb', (gltf) => {
    const mixer = new THREE.AnimationMixer(gltf.scene);
    const clips = gltf.animations; // [空闲、行走、奔跑]
    const idleAction = mixer.clipAction(clips.find(c => c.name === 'Idle'));
    idleAction.play();
    // 在渲染循环中更新 mixer：mixer.update(delta)
});
```

---

### 示例 2：调试材质导出损失（粗糙度看起来平坦）

**场景：** 导出后，一个金属面板材质在 Three.js 中看起来均匀平坦和闪亮。在 Blender 中它有一个有趣的粗糙度变化，来自噪声纹理→颜色渐变→粗糙度输入。

**步骤 1：在 Blender 中确认问题**

```python
import bpy, json

mat = bpy.data.materials.get("MetalPanel")
if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
        print(f"节点: {node.type} - {node.name}")
        for inp in node.inputs:
            if inp.is_linked:
                print(f"  输入 '{inp.name}': 连接到某物")
```

预期输出显示：
```
节点: BSDF_PRINCIPLED - Principled BSDF
  输入 'Roughness': 连接到某物
节点: VALTORGB - 颜色渐变         <-- 这不会导出
节点: TEX_NOISE - 噪声纹理     <-- 这不会导出
```

**步骤 2：了解 GLTF 接收了什么**

导出导出了 Principled BSDF 的粗糙度输入。当链接到颜色渐变时，GLTF 导出器会取输入插座的**默认值**（备用），这通常是 `0.5` — 完全平坦。

**步骤 3A：通过 Blender 烘焙（最佳质量）**

```python
import bpy

# 选择对象
obj = bpy.data.objects["MetalPanelMesh"]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# 创建一个新的图像来烘焙
bake_img = bpy.data.images.new("MetalPanel_roughness_baked", width=1024, height=1024)
bake_img.colorspace_settings.name = 'Non-Color'

# 在材质中添加图像纹理节点
mat = obj.active_material
nodes = mat.node_tree.nodes
img_node = nodes.new('ShaderNodeTexImage')
img_node.image = bake_img
nodes.active = img_node

# 烘焙粗糙度（使用 ROUGHNESS 模式或 EMIT 把戏）
bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
bpy.ops.object.bake(type='ROUGHNESS', save_mode='INTERNAL')

# 保存烘焙图像
import tempfile, os
bake_path = os.path.join(tempfile.gettempdir(), 'MetalPanel_roughness_baked.png')
bake_img.filepath_raw = bake_path
bake_img.file_format = 'PNG'
bake_img.save()
print(f"烘焙粗糙度到 {bake_path}")
```

然后将新的图像纹理节点连接到粗糙度输入并重新导出。

**步骤 3B：在 Three.js 中运行时修补**

如果您无法烘焙，则加载后覆盖材质粗糙度：

```javascript
loader.load('/metal_panel.glb', (gltf) => {
    gltf.scene.traverse((child) => {
        if (child.isMesh && child.material) {
            const mats = Array.isArray(child.material) ? child.material : [child.material];
            mats.forEach(mat => {
                if (mat.name === 'MetalPanel') {
                    // 不要使用平坦的 0.5，设置带纹理的粗糙度或变化值
                    mat.roughness = 0.3;  // 调整以匹配预期外观
                    mat.metalness = 0.9;
                    mat.needsUpdate = true;
                }
            });
        }
    });
});
```

**步骤 4：验证修复**

重新导出并运行验证清单。在 Babylon.js 沙盒中，将金属面板材质与 Blender 视口截图进行比较，以确认粗糙度变化是否得到保留。

## 关键规则

### 1. MCP 服务器在导出时超时

Blender MCP 服务器无法处理 GLTF 导出——它们超时。始终使用无头 CLI：

```bash
blender --background "scene.blend" --python-expr "
import bpy, os
export_path = 'output.glb'
os.makedirs(os.path.dirname(export_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    export_apply=False,
    export_animations=True,
    export_nla_strips=True,
    export_cameras=True,
    export_lights=False,
    export_draco_mesh_compression_enable=False,
)
print(f'大小: {os.path.getsize(export_path)/1024/1024:.1f} MB')
"
```

### 2. 不要在导出时应用修改器

设置 `export_apply=False`。Array 修改器（圆形图案、线性重复）烘焙时会膨胀文件大小。在运行时复制它们。

示例：16 个滚轮实例通过 Array 修改器 = ~1 MB GLB。烘焙 = ~56 MB GLB。

### 3. 首先不使用 Draco 导出

如果您计划使用 `gltf-transform` 进行优化，请首先不使用 Draco 压缩导出。重新编码现有的 Draco 会损坏网格。在最后一步应用 Draco。

### 4. 程序纹理不会导出到 GLTF

这些 Blender 节点设置在导出时**丢失**：

| 节点设置 | 丢失的内容 | 解决方法 |
|----------|-------------|----------|
| 噪声纹理 → 粗糙度 | 整个程序链 | 烘焙到纹理，或在运行时修补 |
| 粗糙度纹理上的颜色渐变 | 值重映射范围 | 手动粗糙度值，或运行时重映射 |
| 程序凸起（噪声 → 凸起） | 凸起细节 | 在 Blender 中烘焙法线图 |
| 混合着色器（复杂因子） | 混合逻辑 | 在导出前简化为单个 BSDF |

**导出时保留的内容：** 平坦的粗糙度/金属值、图像纹理（没有颜色渐变重映射）、烘焙的法线图、PBR 纹理集（baseColor、metallicRoughness、normal）。

### 5. GLTF 名称映射

Blender 名称在 GLTF 中转换：
- 空格 → 下划线
- 点 → 移除
- 尾随空格 → 尾随下划线

| Blender | GLTF |
|--------|------|
| `RINGS ball L` | `RINGS_ball_L` |
| `Sphere.003` | `Sphere003` |
| `RINGS L.001` | `RINGS_L001` |
| `RINGS S `（尾随空格） | `RINGS_S_` |

始终在导出的 GLB 中检查名称，而不是 Blender，当在代码中引用网格时。

### 6. 决不使用 gltf-transform `optimize`

`optimize` 命令包括 `simplify`，它会破坏网格几何。使用单个步骤而不是：

```bash
# 调整纹理大小（最大 1024x1024）
npx @gltf-transform/cli resize input.glb resized.glb --width 1024 --height 1024

# WebP 纹理压缩
npx @gltf-transform/cli webp resized.glb webp.glb --quality 90

# Draco 网格压缩（最后一步）
npx @gltf-transform/cli draco webp.glb output.glb
```

### 7. 引用包含空格的路径

Blender 项目路径通常包含空格。始终双引号：
```bash
blender --background "$HOME/Downloads/blend 3/scene.blend" ...
```

## 场景提取模式

完整的层级，包括材质、变换和修改器：

```python
import bpy, json

def extract_hierarchy(obj, depth=0):
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "visible": not obj.hide_viewport,
        "children": [],
    }
    if obj.type == 'MESH' and obj.data:
        data["vertices"] = len(obj.data.vertices)
        data["faces"] = len(obj.data.polygons)
        data["materials"] = [slot.material.name for slot in obj.material_slots if slot.material]
    if obj.type == 'LIGHT':
        data["light_type"] = obj.data.type
        data["energy"] = obj.data.energy
        data["color"] = list(obj.data.color)
        if obj.data.type == 'AREA':
            data["size"] = obj.data.size
            data["size_y"] = obj.data.size_y
    # Array 修改器（对运行时复制很重要）
    for mod in obj.modifiers:
        if mod.type == 'ARRAY':
            data.setdefault("modifiers", []).append({
                "type": "ARRAY",
                "count": mod.count,
                "offset_object": mod.offset_object.name if mod.offset_object else None,
            })
    for child in obj.children:
        data["children"].append(extract_hierarchy(child, depth + 1))
    return data

scene_data = {
    "name": bpy.context.scene.name,
    "fps": bpy.context.scene.render.fps,
    "frame_start": bpy.context.scene.frame_start,
    "frame_end": bpy.context.scene.frame_end,
    "objects": [],
}

for obj in bpy.context.scene.objects:
    if obj.parent is None:
        scene_data["objects"].append(extract_hierarchy(obj))

print(json.dumps(scene_data, indent=2))
```

## 材质提取模式

```python
import bpy, json

def extract_materials():
    materials = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        info = {"name": mat.name, "nodes": []}
        for node in mat.node_tree.nodes:
            node_data = {"type": node.type, "name": node.name}
            if node.type == 'BSDF_PRINCIPLED':
                for inp in node.inputs:
                    if inp.is_linked:
                        node_data[inp.name] = "linked"
                    elif hasattr(inp, 'default_value'):
                        val = inp.default_value
                        try:
                            node_data[inp.name] = list(val)
                        except TypeError:
                            node_data[inp.name] = float(val)
            if node.type == 'TEX_IMAGE' and node.image:
                node_data["image"] = node.image.filepath
                node_data["size"] = [node.image.size[0], node.image.size[1]]
            info["nodes"].append(node_data)
        materials.append(info)
    return materials

print(json.dumps(extract_materials(), indent=2))
```

## 动画关键帧提取

```python
import bpy, json

def extract_animation(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return None
    tracks = []
    for fc in obj.animation_data.action.fcurves:
        keyframes = []
        for kp in fc.keyframe_points:
            keyframes.append({
                "frame": int(kp.co[0]),
                "value": float(kp.co[1]),
                "interpolation": kp.interpolation,
            })
        tracks.append({
            "data_path": fc.data_path,
            "index": fc.array_index,
            "keyframes": keyframes,
        })
    return {"object": obj.name, "tracks": tracks}

animations = []
for obj in bpy.data.objects:
    anim = extract_animation(obj)
    if anim:
        animations.append(anim)

print(json.dumps(animations, indent=2))
```

## GLTF 导出设置参考

| 设置 | 值 | 原因 |
|-------|-----|-----|
| `export_format` | `'GLB'` | 单个二进制文件 |
| `export_apply` | `False` | 不要烘焙修改器 (Array, 等) |
| `export_animations` | `True` | 包含动画数据 |
| `export_nla_strips` | `True` | 烘焙 NLA 条带到动作 |
| `export_cameras` | `True` | 包含相机构架 |
| `export_lights` | `False` | 在运行时处理灯光 (Three.js/R3F) |
| `export_draco_mesh_compression_enable` | `False` | 之后通过 gltf-transform 应用 Draco |

## 纹理优化流程

目标：最小的 GLB 与可接受的视觉质量。

```
Blender 导出（不使用 Draco）→ 调整大小 (最大 1K) → WebP (质量 90) → Draco
   ~22 MB                    ~3.7 MB           ~3.7 MB      ~1 MB
```

关键洞察：
- 4K 纹理 (4096x4096) = ~89 MB GPU 内存每个纹理。1K = ~5.6 MB。**16 倍减少**。
- PNG metallicRoughness 纹理在 WebP 中以质量 85-90 压缩良好。
- 移动 GPU（Adreno、Mali）从纹理缩小中受益最多。
- 使用 `npx @gltf-transform/cli inspect model.glb` 检查。

参见 [references/texture-optimization.md](references/texture-optimization.md) 获取具体命令和质量指标。

## 资产集成

通过配置 Blender MCP 可用：

| 集成 | 功能 |
|------|------|
| **PolyHaven** | 搜索、下载、导入免费的 HDRIs、纹理和 3D 模型，自动设置材质 |
| **Sketchfab** | 搜索并下载模型（需要访问令牌） |
| **Hyper3D Rodin** | 从文本描述或参考图像生成 3D 模型 |
| **Hunyuan3D** | 从文本提示、图像或两者创建 3D 资产 |

参见 [references/asset-integrations.md](references/asset-integrations.md) 获取使用示例和工作流程模式。

## 已知错误和解决方法

参见 [references/errors.md](references/errors.md) 获取完整的错误表。

## 数据输出

- `print()` + `json.dumps()` 用于小结果（场景信息、单个对象）
- 使用 `tempfile.gettempdir()` 用于大型提取结果（完整层级、动画数据、材质报告）
- 始终包含元数据：场景名称、fps、帧范围、Blender 版本
