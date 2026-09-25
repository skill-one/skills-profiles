# 过程生成

根据紧凑的规则和种子生成关卡、地形和战利品。好的过程生成的核心在于**确定性**：单个种子可以重现相同的世界，因此错误是可重复的，玩家可以分享种子。这项技能掌握着核心算法——噪声、种子随机数生成器、地下城布局、加权表；像`roguelike`和`生存制造`这样的游戏类型依赖它。

## 使用场景

- 用于生成地图、地下城、地形高度图、物品掉落或任何不想手动编写的內容。
- 当结果必须**从种子中可重复生成**时使用（调试、每日挑战、可分享的世界）。
- 用于选择加权随机结果（战利品稀有度、生成表）。

**不使用场景**：对于引擎的瓦片API来*绘制*结果，使用`godot-tilemap`或`unity-tilemap-2d`。对于通过生成的地图的路由AI，使用`game-ai`。对于精心手动设计的关卡，使用`level-design`——过程生成和手动设计是互补的，不是可互换的。

## 核心工作流程

1. **掌握你的随机性**。创建一个种子随机数生成器实例，并在所有地方传递它。不要在生成代码中调用全局/静态随机数——这会使结果不可重复且依赖于顺序。
2. **为内容选择技术**。连续地形/高度图→噪声。离散房间/走廊→空间划分或基于代理的雕刻。具有稀有度的结果→加权表。
3. **首先生成到普通的网格/数组中，与渲染解耦**。生成填充`int[][]`或字典；单独的步骤绘制它。
4. **在将结果发送给玩家之前进行验证**。每个房间都可到达吗？出生点安全吗？有通往出口的路径吗？拒绝或修复失败的布局；不要给玩家一个破地图。
5. **固定种子进行调优**，以便每个参数的更改都是单独可见的，然后扫描种子以检查分布，而不仅仅是幸运的一张地图。

## 模式

### 1. 种子确定性随机数生成器（基础）

```python
import random
rng = random.Random(seed)        # 一个专用实例——不是全局随机.*
room_count = rng.randint(5, 12)  # 同一个种子→相同的序列，每次运行
# 正确：将`rng`传递给每个做出选择的函数。
# 错误：调用random.randint(...)（全局状态）——依赖于顺序，无法种子化。
```

引擎等效：Godot `var rng = RandomNumberGenerator.new(); rng.seed = s`；Unity `var rng = new System.Random(seed)`（或`UnityEngine.Random.InitState`）。将种子保存在存档文件中，以便可以重新生成世界。

### 2. 分形（fBm）噪声用于高度图

```python
# 汇总多个八度：每个更高的八度具有更高的频率和更低的振幅。
def fbm(noise, x, y, octaves=5, lacunarity=2.0, gain=0.5):
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * noise(x * freq, y * freq)   # noise()返回~0..1
        norm  += amp                                # 跟踪总振幅
        amp   *= gain                               # 每个八度贡献较小
        freq  *= lacunarity                         # ...在更高的频率下
    return total / norm                             # 归一化回0..1

# 重新分配以雕刻平坦的谷地/锐化峰值：更高的指数→更多的低地。
elevation = pow(fbm(noise, nx, ny), 2.2)
```

使用真实的噪声库（`FastNoiseLite`、`opensimplex`、`Unity.Mathematics.noise`或`Mathf.PerlinNoise`）——不要自己实现梯度噪声。用不同的种子种子化高度和湿度，以便在两个字段上的生物群落查找不是完全相关的。完整的生物群落查找和岛屿塑形在`references/noise.md`中。

### 3. 加权战利品表（稀有度校正选择）

```python
# 按权重投掷：普通掉落比传奇掉落更频繁。
def weighted_pick(rng, table):           # table: (item, weight)列表
    total = sum(w for _, w in table)
    roll = rng.uniform(0, total)          # 累计线上的一个点
    upto = 0.0
    for item, w in table:
        upto += w
        if roll < upto:                   # 投掷落入的第一个桶
            return item
    return table[-1][0]                   # 浮点安全后备

loot = weighted_pick(rng, [("common", 70), ("rare", 25), ("legendary", 5)])
```

权重不必总和为100——它们是相对的。为了防止糟糕的连续性，使用“同情”/袋子系统（见`references/dungeon-generation.md`关于分布的注释）。

### 4. 房间和走廊地下城（草图）

```python
# 1. 放置不重叠的房间；2. 连接它们；3. 刻画到网格中。
rooms = []
for _ in range(attempts):
    r = Rect(rng.randint(1, W-w-1), rng.randint(1, H-h-1), w, h)
    if not any(r.intersects(o.expand(1)) for o in rooms):  # 保持1个瓦片的间隙
        rooms.append(r)
for a, b in zip(rooms, rooms[1:]):       # 将每个房间连接到下一个房间
    carve_l_corridor(grid, a.center, b.center, rng)   # 水平然后垂直
```

完整的生成器（BSP划分、L走廊、可达性检查和随机游走洞穴）在`references/dungeon-generation.md`中。

## 陷阱

- **在生成代码中使用全局RNG**会使世界不可重复，并且当调用顺序改变时就会破坏。始终传递一个种子实例。
- **相关的噪声字段**：从*同一个*种子/偏移量采样高度和湿度会产生排列成带的生物群落。偏移或重新种子化每个字段。
- **八度伪影**：在不重新归一化的情况下添加八度会将值推到`0..1`之外；除以总振幅（并注意库输出范围——有些返回`-1..1`，有些返回`0..1`）。
- **没有连通性检查**：房间或洞穴可能会最终孤立。从出生点开始泛洪填充，并在游戏前丢弃/重新连接无法到达的区域。
- **无界放置循环**：“不断尝试直到N个房间适合”在小网格上可能会无限循环。限制尝试次数并接受较少的房间。
- **全局一次性种子化，然后依赖帧时间**：任何非确定性输入（时间、物理、哈希随机化）泄漏到生成中都会破坏可重复性。

## 参考

- `references/noise.md` — 八度/分形/增益、重新分配、岛屿塑形、双轴生物群落查找、蓝色噪声对象散布。
- `references/dungeon-generation.md` — BSP、房间+走廊、随机游走洞穴、元胞自动机平滑、连通性验证、分布/同情表。

## 相关技能

- `godot-tilemap`、`unity-tilemap-2d` — 将生成的网格绘制到引擎中。
- `game-ai` — 在生成的图上路径查找。
- `level-design` — 节奏和手动编写的结构，过程生成补充。
- `roguelike`、`survival-crafting` — 组合这项技能的游戏类型。
