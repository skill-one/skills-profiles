# Godot 3D 基础 (4.x)

构建一个可工作的 3D 场景：变换、相机、灯光、环境/后期处理、材质和 `GridMap` 块选区。目标 **Godot 4.7**。

## 使用场景

- 在开始或修复 3D 场景时使用：定位 `Camera3D`、添加灯光、设置 `WorldEnvironment`（天空、环境光、色调映射、辉光/SSAO）、分配材质或使用 `GridMap` 构建关卡。

**不适用场景：** 编写空间着色器 → `godot-shaders`；3D 物理体和射线检测 → `godot-physics`；角色动画混合 → `godot-animation`；完整 FPS 模板 → `fps-shooter` 游戏类型技能。

## 核心工作流程

1. **所有 3D 对象都是 `Node3D`**，具有 `Transform3D`（位置、旋转基、缩放）。
   使用 `global_position` 移动，使用 `rotate_y(angle)` 或 `look_at(target)` 旋转。
2. **添加 `Camera3D`。** 标记为 `current`（或调用 `make_current()`）；设置 `fov`、`near`、`far`。将其作为 Rig/Pivot 的子节点以实现轨道或跟随相机。
3. **照亮场景。** `DirectionalLight3D` 是太阳；`OmniLight3D`/`SpotLight3D` 是局部光源。为每个灯光启用阴影。没有灯光和环境光时，表面会渲染为黑色。
4. **添加 `WorldEnvironment`** 并使用 `Environment` 资源：背景（天空/颜色）、环境光、色调映射和后期处理（辉光、SSAO、雾、调整）。
5. **在 `MeshInstance3D` 上为网格分配材质** (`StandardMaterial3D` 或 `ShaderMaterial`)。
6. **使用 `GridMap` 块选区**，它将 `MeshLibrary` 中的项目放置在 3D 网格上（类似于瓦片地图的 3D 版本）。

## 模式

### 1. 跟随相机（第三人称，平滑）

```gdscript
extends Camera3D

@export var target: Node3D
@export var offset := Vector3(0, 4, 8)
@export var smooth := 6.0

func _physics_process(delta: float) -> void:
    if target == null:
        return
    var desired := target.global_position + offset
    global_position = global_position.lerp(desired, smooth * delta)  # 平滑跟随
    look_at(target.global_position, Vector3.UP)                      # 面向目标
```

### 2. 代码中的太阳 + 环境

```gdscript
func _ready() -> void:
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-45, -30, 0)
    sun.shadow_enabled = true
    add_child(sun)

    var we := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_SKY
    env.sky = Sky.new()
    env.sky.sky_material = ProceduralSkyMaterial.new()
    env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env.glow_enabled = true
    we.environment = env
    add_child(we)
```

### 3. 从代码中分配 `StandardMaterial3D`

```gdscript
func tint_mesh(mesh: MeshInstance3D, color: Color) -> void:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = 0.0
    mat.roughness = 0.6
    mat.emission_enabled = true
    mat.emission = color * 0.3
    mesh.material_override = mat       # 覆盖网格的表面材质
```

### 4. 将瓦片放置到 `GridMap` 中

```gdscript
@onready var grid: GridMap = $GridMap   # 在编辑器中设置 cell_size + mesh_library

func build_floor(width: int, depth: int, item_id: int) -> void:
    for x in width:
        for z in depth:
            # set_cell_item(Vector3i cell, int item, orientation = 0)
            grid.set_cell_item(Vector3i(x, 0, z), item_id)
```

## 陷阱

- **场景渲染为黑色** → 没有灯光和环境光。添加 `DirectionalLight3D` 和/或具有环境光/天空的 `WorldEnvironment`。新场景默认情况下既没有灯光也没有环境光。
- **没有相机 / 相机错误。** 如果看不到任何内容，则没有 `Camera3D` 被标记为 `current`。设置 `current = true` 或 `make_current()`；每个视口只渲染一个相机。
- **混淆局部和全局变换。** `position`/`rotation` 相对于父节点；`global_position`/`global_transform` 是世界空间。在旋转的父节点下混合它们会产生意想不到的结果。`look_at` 使用全局坐标。
- **缩放物理/灯光。** `Node3D` 的非均匀 `scale` 会扭曲子节点碰撞和灯光；优先缩放网格资源或使用均匀缩放。
- **忘记 `look_at` 中的 `from`/`up`。** `look_at(target, up)` — 目标等于节点的位置，或 `up` 平行于观看方向，会产生 NaNs/翻转。
- **没有 `MeshLibrary` 的 `GridMap`** 放置任何内容。创建 `MeshLibrary`（从场景）并分配它；`set_cell_item(cell, -1)` 清除一个单元格。
- **HDR/辉光过强** → 检查 `tonemap_mode` 和辉光阈值；在电影色调映射下，原始发射值会因过度辉光而失真。

## 参考

- 对于 `Transform3D` 数学、相机投影模式、灯光/阴影参数、完整的 `Environment`/后期处理选项、`MeshLibrary` 创建以及 `ReflectionProbe`/`LightmapGI` 灯光，请阅读 `references/scene-and-environment.md`。

## 相关技能

- `godot-physics` — 3D 物理体、区域和射线检测。
- `godot-shaders` — 用于自定义 3D 表面的空间着色器。
- `godot-animation` — 使用 `AnimationTree` 进行 3D 角色动画。
- `camera-systems` — 第三人称轨道 / 第一人称视角 Rig、构图和碰撞。
- `performance-optimization` — 将 3D 场景保持在帧预算内（绘制调用、灯光、LOD）。
- `fps-shooter` — 将 3D 移动、输入和 AI 组合成游戏。
