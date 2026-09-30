---
name: unity-tilemap-2d
description: 在 Unity 6.3 LTS 中构建和脚本 2D 图层地图：网格 + 图层组件、图层调色板、图层碰撞器、规则图层以及运行时 SetTile/GetTile 绘制。适用于绘制图层关卡、添加 TilemapCollider2D、使用规则或动画图层、从代码生成图层地图，或在用户提及 Unity 图层地图、图层调色板、规则图层或网格时使用。
---

# Unity 2D Tilemap

使用 `Grid`/`Tilemap` 系统在 Unity 6.3 LTS 中创建和编写基于瓦片的 2D 关卡，包括 Tile 调色板、碰撞体和运行时绘制。目标 **Unity 6.3 LTS (6000.3)**。

> **包说明**：核心 Tilemap (`Grid`, `Tilemap`, `Tile`, `TilemapCollider2D`) 已内置。**规则瓦片、动画瓦片和 Tile 调色板笔刷位于单独的 "2D Tilemap 附加组件" 包 (`com.unity.2d.tilemap.extras`) 中** — 在使用 `RuleTile` 之前，请通过包管理器安装它。

## 使用场景

- 当通过绘制瓦片、设置 `Grid` + `Tilemap`、为地图添加碰撞、使用自动瓦片规则瓦片或从脚本生成/编辑瓦片时使用。
- 当场景包含带有 `Tilemap` 子对象的 `Grid`，或 `*.asset` 瓦片/调色板文件时使用。

**不使用场景**：关卡设计练习（节奏、草稿、布局原则）→ `level-design`。3D 瓦片/网格放置 → Unity 自身的 3D 工具（ProBuilder / 网格笔刷；此处没有专门的技能）。在瓦片上移动的平台跳跃角色 → `platformer` / `unity-physics`。

## 核心工作流程

1. **创建网格**：GameObject → 2D 对象 → Tilemap → 矩形（`Grid` 的 **单元布局** 还提供六边形和等距布局，用于六边形/等距关卡）。这将创建一个带有子 `Tilemap`（+ `TilemapRenderer`）的 `Grid`。每个图层使用一个 Tilemap（背景、地面、前景），并设置每个渲染器的排序。
2. **打开 Tile 调色板**（窗口 → 2D → Tile 调色板），将切片精灵表拖入以创建 `Tile` 资产，然后使用笔刷工具绘制。
3. **为实心图层添加碰撞**：`TilemapCollider2D`。对于单个合并碰撞器（性能更高且无间隙），还添加 `CompositeCollider2D`（+ 设置为 **静态** 的 `Rigidbody2D`）并启用瓦片碰撞器上的 _Used By Composite_。
4. **使用规则瓦片自动瓦片化**（2D Tilemap 附加组件），以便边缘/角落自动选择正确的精灵，而不是手动放置每个变体。
5. **通过脚本在运行时编辑**：使用单元坐标 (`Vector3Int`)：`SetTile`, `GetTile`, `SetTilesBlock`，使用 `Grid`/`Tilemap` 转换世界↔单元。
6. **在 Play 模式下验证**：确认碰撞（物理调试器）、排序顺序，并确保在批量编辑后运行了 `RefreshAllTiles`。

## 模式

### 1. 运行时绘制瓦片（单元坐标）

```csharp
using UnityEngine;
using UnityEngine.Tilemaps;

public class TilePainter : MonoBehaviour
{
    [SerializeField] private Tilemap tilemap;   // 指定目标 Tilemap
    [SerializeField] private TileBase groundTile;

    // 世界位置 -> 单元，然后放置瓦片。
    public void PaintAt(Vector3 worldPos)
    {
        Vector3Int cell = tilemap.WorldToCell(worldPos);
        tilemap.SetTile(cell, groundTile);
    }

    public bool IsSolid(Vector3 worldPos)
        => tilemap.GetTile(tilemap.WorldToCell(worldPos)) != null;
}
```

### 2. 批量填充区域（比逐单元 `SetTile` 更快）

```csharp
// SetTilesBlock 一次调用写入整个 BoundsInt — 用于程序化房间/地板。
public void FillFloor(Tilemap map, TileBase tile, int width, int height)
{
    var bounds = new BoundsInt(0, 0, 0, width, height, 1);
    var tiles  = new TileBase[width * height];
    for (int i = 0; i < tiles.Length; i++) tiles[i] = tile;
    map.SetTilesBlock(bounds, tiles);
}
```

### 3. 清除和刷新

```csharp
tilemap.SetTile(cell, null);   // null 删除该单元的瓦片
tilemap.RefreshTile(cell);     // 重新评估此单元的规则/动画邻居（快速）
// RefreshAllTiles() 重新评估整个地图 — 仅用于完整再生，而非逐次编辑。
```

## 陷阱

- **找不到 `RuleTile` 类型** — 它不是内置的。通过包管理器安装 **2D Tilemap 附加组件** (`com.unity.2d.tilemap.extras`)。
- **每个瓦片一个碰撞器会严重影响性能 / 留下缝隙** — 添加带有静态 `Rigidbody2D` 和 _Used By Composite_ 的 `CompositeCollider2D`，将整个图层合并为一个平滑形状。
- **混淆世界和单元坐标** — `SetTile`/`GetTile` 接受 `Vector3Int` _单元_，不是世界位置。始终使用 `WorldToCell` / `CellToWorld` 转换。
- **瓦片意外地渲染在精灵后面/前面** — 设置每个 `TilemapRenderer` 的排序层和层中的顺序；多个 Tilemap 需要显式排序。
- **规则/动画瓦片在脚本编辑后未更新** — 写入后刷新，但优先使用目标 `RefreshTile(cell)` 进行少量编辑；`RefreshAllTiles()` 重新评估地图上的每个瓦片并卡住大型关卡。仅保留完整刷新用于整个地图再生。
- **绘制到错误的图层** — Tile 调色板中的活动 Tilemap 决定了绘制位置；检查 "Active Tilemap" 下拉菜单。

## 参考

- 主要文档：Unity 手册 "Tilemaps"
  (`https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html`),
  `ScriptReference/Tilemaps.Tilemap`，以及 2D Tilemap 附加组件手册
  (`https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@6.0/manual/index.html`) 用于规则瓦片。(`@6.0` 是随 Unity 6.3 LTS 一起发布的版本；旧的 `@1.6` 文档适用于 2021 年代的 Unity 项目。)

## 相关技能

- `level-design` — 无引擎依赖的草稿、节奏和瓦片布局练习。
- `procedural-gen` — 生成你传递给 `SetTilesBlock` 的瓦片数据（噪声、随机数、地牢）。
- `platformer` / `roguelike` — 组合此技能与移动和生成的类型。
