# Unity 2D Tilemap

使用 `Grid`/`Tilemap` 系统、瓦片调色板、碰撞体和运行时绘制，在 Unity 6.3 LTS 中创建和编写脚本化的 2D 关卡。目标 **Unity 6.3 LTS (6000.3)**。

> **包说明**：核心 Tilemap (`Grid`, `Tilemap`, `Tile`, `TilemapCollider2D`) 已内置。**规则瓦片、动画瓦片和瓦片调色板笔刷位于单独的 "2D Tilemap 附加组件" 包 (`com.unity.2d.tilemap.extras`)** — 在使用 `RuleTile` 之前，请通过包管理器安装它。

## 使用场景

- 在通过绘制瓦片、设置 `Grid` + `Tilemap`、为地图添加碰撞、使用自动瓦片规则瓦片或从脚本生成/编辑瓦片时使用。
- 当场景包含带有 `Tilemap` 子对象的 `Grid`，或 `*.asset` 瓦片/调色板文件时使用。

**不使用场景**：关卡 _设计_ 实践（节奏、草稿、布局原则）→ `level-design`。3D 瓦片/网格放置 → Unity 自身的 3D 工具（ProBuilder / 网格笔刷；此处没有专门的技能）。在瓦片上移动的平台跳跃角色 → `platformer` / `unity-physics`。

## 核心工作流程

1. **创建网格**：GameObject → 2D 对象 → Tilemap → 矩形。这会创建一个 `Grid`，带有子 `Tilemap` (+ `TilemapRenderer`)。每个图层使用一个 Tilemap（背景、地面、前景），并设置每个渲染器的排序。
2. **打开瓦片调色板**（窗口 → 2D → 瓦片调色板），将切片精灵表拖入以创建 `Tile` 资产，然后使用笔刷工具绘制。
3. **为实心层添加碰撞**：`TilemapCollider2D`。对于单个合并的碰撞器（更高效且无间隙），还添加 `CompositeCollider2D` (+ 一个设置为 **静态** 的 `Rigidbody2D`)，并在瓦片碰撞器上启用 _Used By Composite_。
4. **使用规则瓦片自动瓦片**（2D Tilemap 附加组件），以便边缘/角落自动选择正确的精灵，而不是手动放置每个变体。
5. **通过脚本在运行时编辑**：使用单元格坐标 (`Vector3Int`)：`SetTile`, `GetTile`, `SetTilesBlock`，使用 `Grid`/`Tilemap` 转换世界↔单元格。
6. **在 Play 模式下验证**：确认碰撞（物理调试器）、排序顺序，并确保在批量编辑后运行了 `RefreshAllTiles`。

## 模式

### 1. 运行时绘制瓦片（单元格坐标）

```csharp
using UnityEngine;
using UnityEngine.Tilemaps;

public class TilePainter : MonoBehaviour
{
    [SerializeField] private Tilemap tilemap;   // 指定目标 Tilemap
    [SerializeField] private TileBase groundTile;

    // 世界位置 -> 单元格，然后放置瓦片。
    public void PaintAt(Vector3 worldPos)
    {
        Vector3Int cell = tilemap.WorldToCell(worldPos);
        tilemap.SetTile(cell, groundTile);
    }

    public bool IsSolid(Vector3 worldPos)
        => tilemap.GetTile(tilemap.WorldToCell(worldPos)) != null;
}
```

### 2. 批量填充区域（比逐单元格 `SetTile` 更快）

```csharp
// SetTilesBlock 一次调用写入整个 BoundsInt — 用于生成程序化房间/地板。
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
tilemap.SetTile(cell, null);   // null 删除该单元格的瓦片
tilemap.RefreshTile(cell);     // 重新评估此单元格的规则/动画邻居（廉价）
// RefreshAllTiles() 重新评估整个地图 — 仅用于完整再生，而非逐次编辑。
```

## 陷阱

- **找不到 `RuleTile` 类型** — 它不是内置的。通过包管理器安装 **2D Tilemap 附加组件** (`com.unity.2d.tilemap.extras`)。
- **每个瓦片一个碰撞器会严重影响性能 / 留下缝隙** — 添加带有静态 `Rigidbody2D` 和 _Used By Composite_ 的 `CompositeCollider2D`，将整个图层合并为一个平滑形状。
- **混淆世界和单元格坐标** — `SetTile`/`GetTile` 接受 `Vector3Int` _单元格_，不是世界位置。始终使用 `WorldToCell` / `CellToWorld` 进行转换。
- **瓦片意外地渲染在精灵后面/前面** — 设置每个 `TilemapRenderer` 的排序层和图层中的顺序；多个 Tilemap 需要显式排序。
- **规则/动画瓦片在脚本编辑后未更新** — 写入后刷新，但更倾向于使用目标 `RefreshTile(cell)` 进行少量编辑；`RefreshAllTiles()` 重新评估地图上的每个瓦片并卡住大型关卡。仅用于完整地图再生时保留完整刷新。
- **绘制到错误的图层** — Tile Palette 中的活动 Tilemap 决定了绘制位置；检查 "Active Tilemap" 下拉菜单。

## 参考

- 主要文档：Unity 手册 "Tilemaps"
  (`https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-reference.html`),
  `ScriptReference/Tilemaps.Tilemap`，以及 2D Tilemap 附加组件手册
  (`https://docs.unity3d.com/Packages/com.unity.2d.tilemap.extras@1.6/manual/index.html`) 用于规则瓦片。

## 相关技能

- `level-design` — 无引擎依赖的草稿、节奏和瓦片布局练习。
- `procedural-gen` — 生成你传递给 `SetTilesBlock` 的瓦片数据（噪声、RNG、地牢）。
- `platformer` / `roguelike` — 组合此技能与移动和生成的类型。
