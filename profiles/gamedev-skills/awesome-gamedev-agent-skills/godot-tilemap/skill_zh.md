# Godot TileMap (4.7 TileMapLayer)

使用 `TileMapLayer` + `TileSet` 创建基于瓦片的关卡，为每个瓦片添加碰撞和自定义数据，使用地形自动瓦片连接，并在运行时操作瓦片单元。目标为 **Godot 4.7**，其中 `TileMapLayer` 取代了已弃用的 `TileMap` 节点。

## 使用场景

- 在从瓦片网格设计 2D 关卡、配置 `TileSet`（碰撞、导航、自定义数据、地形）或从代码中读取/写入瓦片时使用。
- 在将 `TileMap` 节点（单个节点、多层）迁移到多个 `TileMapLayer` 节点（每层一个）时使用。

**不使用场景：** 移动玩家穿过瓦片 → `godot-2d-movement`；通用物理体/射线 → `godot-physics`；程序化地图 *生成* 算法 → `procedural-gen`；关卡 *设计* 练习 → `level-design`。

## 核心工作流程

1. **添加一个 `TileMapLayer` 节点**（每个视觉/逻辑层一个：背景、墙壁、前景）。每个节点只包含一层瓦片。
2. 在层的 `tile_set` 属性上创建或分配 `TileSet`。在 TileSet 编辑器中添加图集源（将纹理切割成瓦片）。将 TileSet 保存为外部 `.tres` 文件，以便多个层/关卡复用。
3. 在 TileSet 编辑器中添加瓦片数据：物理层（碰撞多边形）、导航层、遮挡，以及 **自定义数据层**（每个瓦片的值类型，如 `damage` 或 `is_ladder`）。
4. 在 TileMap 底部面板中绘制（绘制/线条/矩形/桶）。对于自连接瓦片，定义一个 **地形集** 并使用连接/路径模式绘制。
5. 通过层的 `collision_enabled` / `navigation_enabled` 属性启用每层碰撞/导航。
6. 使用 `local_to_map`、`set_cell`、`get_cell_source_id` 和 `get_cell_tile_data(...).get_custom_data(...)` 从代码中读取/写入。

## 模式

### 1. 将鼠标位置转换为瓦片并读取其自定义数据

```gdscript
extends TileMapLayer

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        # local_to_map 需要本地坐标；先从全局坐标转换。
        var cell := local_to_map(to_local(event.position))
        var data := get_cell_tile_data(cell)   # TileData 或 null
        if data:
            var dmg: int = data.get_custom_data("damage")  # 自定义数据层
            print("瓦片 %s 造成 %d 点伤害" % [cell, dmg])
```

### 2. 运行时放置和擦除瓦片

```gdscript
# set_cell(coords, source_id, atlas_coords, alternative_tile = 0)
func place_wall(cell: Vector2i) -> void:
    set_cell(cell, 0, Vector2i(2, 1))   # 源 0，图集瓦片位于第 2 列、第 1 行

func dig(cell: Vector2i) -> void:
    erase_cell(cell)                    # 与 set_cell(cell, -1) 相同

func clear_level() -> void:
    clear()                             # 删除该层上的所有瓦片
```

### 3. 使用地形集自动连接区域

```gdscript
# 用地形 `terrain` 的地形集 `terrain_set` 绘制填充区域；Godot 会选择正确的边缘/角落瓦片将它们连接起来。
func fill_with_grass(cells: Array[Vector2i]) -> void:
    var terrain_set := 0
    var grass_terrain := 0
    set_cells_terrain_connect(cells, terrain_set, grass_terrain, true)
```

### 4. 遍历已放置的瓦片（例如查找所有生成点）

```gdscript
func find_spawns() -> Array[Vector2i]:
    var spawns: Array[Vector2i] = []
    for cell in get_used_cells():
        var data := get_cell_tile_data(cell)
        if data and data.get_custom_data("is_spawn"):
            spawns.append(cell)
    return spawns
```

## 陷阱

- **4.3 中 `TileMap` 节点已弃用。** 使用 `TileMapLayer` 节点（每层一个节点）；将它们分组在父 `Node2D` 下。旧的 `TileMap` 调用（接受 `layer` 参数的 `set_cell(layer, ...)`）不适用于 `TileMapLayer`。
- **`local_to_map` 需要本地坐标。** 鼠标/全局位置必须先用 `to_local(...)` 转换，否则瓦片会偏移。
- **`get_cell_tile_data` 返回 `null`** 对于空瓦片或非图集源 — 在 `get_custom_data` 之前始终进行空检查。
- **自定义数据是类型化的。** 声明为 `int` 的层返回 `int`；以错误类型读取或引用不存在的层名会报错。先在 TileSet 中定义层。
- **地形需要定义所有组合。** 如果 TileSet 的地形掩码对齐不完整，`set_cells_terrain_connect` 会产生奇怪的结果。
- **运行时编辑会批量处理** 到帧末尾。如果你必须在 `set_cell` 后立即读取更新后的内部数据，调用 `update_internals()`（代价昂贵 — 避免在循环中使用）。
- **碰撞不工作？** 检查层的 `collision_enabled`，瓦片是否有物理层（多边形），以及 TileSet 的物理层掩码是否与你的物理体匹配。

## 参考

- 对于 TileSet 设置（图集源、物理/导航/自定义数据层、地形掩码）、场景瓦片、Y 排序和运行时瓦片数据覆盖（`_use_tile_data_runtime_update`），请阅读 `references/tileset-and-terrains.md`。

## 相关技能

- `godot-2d-movement` — 在这些瓦片上行走的人物。
- `godot-physics` — 瓦片碰撞参与其中的碰撞层/掩码。
- `procedural-gen` — 从噪声/RNG 生成瓦片图。
- `level-design` / `roguelike` — 设计练习和基于网格的游戏类型。
