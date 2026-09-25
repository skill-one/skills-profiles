# 存档系统

存档文件是游戏状态的**序列化快照**，能够在重启后继续存在。
困难的部分不在于写入字节——而在于选择*要*存什么，如何写入以防止存档中途崩溃导致损坏，以及在发布补丁后如何读取*旧*存档。掌握好这三点，其余的就是一些基础工作。

## 使用场景

- 用于持久化进度：玩家属性、背包、世界标志、设置、位置——跨会话和游戏更新。
- 用于设计存档槽、快速存档/自动存档和崩溃安全写入。
- 当内容/代码变更后旧存档文件失效时使用（版本控制 & 迁移）。

**不使用场景**：对于 Roblox 云持久化特定需求，使用 `roblox-datastores`。对于存档序列化的数据模型（资源/SOs），使用 `godot-resources` / `unity-scriptableobjects`。对于 Godot 的 `FileAccess`/`ResourceSaver` 和 `user://` 路径，在应用此处模式时参考 Godot 引擎技能。

## 核心工作流程

1. **确定权威状态**。存档*数据*（生命值、位置、种子、解锁标志），而不是引擎对象或场景节点。加载时将从数据重建对象——永远不要序列化活节点引用。
2. **定义版本化模式**。每个存档嵌入一个 `version` 整数。这是打算打补丁的游戏中最重要的字段。
3. **选择格式**。JSON/文本用于可读性和可调试性；二进制格式用于大小/速度或轻微防篡改。从 JSON 开始。
4. **原子写入**。序列化到临时文件，刷新，然后重命名覆盖真实文件。崩溃时要么保留旧存档，要么保留新存档——永远不会保留半完成的存档。
5. **防御性加载**。读取版本 → 迁移到当前版本 → 验证 → 实例化。保留最后一个良好存档的备份，并在解析错误时回退。
6. **在安全边界自动存档**（关卡变更、检查点），带节流，并到单独的槽位，以免覆盖手动存档。
7. **验证**：存档，完全退出，重新启动，加载——通过检查确认状态匹配。测试加载上一个版本的存档。

## 模式

### 1. 将状态序列化为纯数据（非引擎对象）

```gdscript
# 构建纯数据的字典。每个可存档对象报告自己的状态。
func capture_state() -> Dictionary:
    return {
        "version": SAVE_VERSION,                 # 始终标记模式版本
        "player": { "hp": player.hp, "pos": [player.position.x, player.position.y] },
        "inventory": player.inventory.to_array(),  # ID + 数量，不是 Item 节点
        "flags": world.flags,                    # 例如 {"met_guard": true}
        "seed": world.seed,                      # 重新生成程序性内容
    }

# 加载时，从数据*重建*对象——不要期望返回活引用。
func apply_state(data: Dictionary) -> void:
    player.hp = data["player"]["hp"]
    player.position = Vector2(data["player"]["pos"][0], data["player"]["pos"][1])
    player.inventory.from_array(data["inventory"])
    world.flags = data["flags"]
```

### 2. 原子、崩溃安全写入（临时文件 + 重命名）

```gdscript
# 正确：写入临时文件，然后原子重命名覆盖目标。
func save_atomic(path: String, data: Dictionary) -> void:
    var tmp := path + ".tmp"
    var f := FileAccess.open(tmp, FileAccess.WRITE)
    f.store_string(JSON.stringify(data))
    f.flush()                                    # 确保字节写入磁盘
    f.close()
    DirAccess.rename_absolute(tmp, path)         # 替换目标；POSIX 上原子
# 错误：直接打开 `path` 并就地写入——写入中途崩溃会留下一个
# 被截断且无法加载的存档，并破坏玩家的进度。
```

重命名覆盖目标是 POSIX 上原子的（同一卷）；在 Windows 上，替换式重命名不保证原子性，所以在重命名前保留旧文件为 `path + ".bak"`——这个备份才是真正保证你能从错误写入中恢复的。

### 3. 带迁移的版本化加载

```python
SAVE_VERSION = 3

def load_save(raw_bytes):
    data = parse(raw_bytes)                  # JSON/binary -> dict
    v = data.get("version", 0)
    if v > SAVE_VERSION:
        raise NewerSaveError(v)              # 存档来自更新的构建；拒绝
    while v < SAVE_VERSION:                   # 按顺序应用迁移，v -> v+1
        data = MIGRATIONS[v](data)
        v += 1
        data["version"] = v
    validate(data)                            # 检查必需键 / 范围
    return data

# 每个迁移是一个纯函数，从旧版本形状到新版本。
def migrate_1_to_2(d):
    d["flags"] = {k: True for k in d.pop("completed_quests", [])}  # 列表 -> 集合映射
    return d
MIGRATIONS = {1: migrate_1_to_2, 2: migrate_2_to_3}
```

### 4. 存档槽 + 节流自动存档

```gdscript
const SLOT_PATH := "user://save_%d.json"      # 手动槽位 0..N
const AUTOSAVE_PATH := "user://autosave.json"  # 独立文件：永远不会覆盖手动存档
var _autosave_cooldown := 0.0

func autosave_if_due(dt: float) -> void:
    _autosave_cooldown -= dt
    if _autosave_cooldown <= 0.0:
        save_atomic(AUTOSAVE_PATH, capture_state())
        _autosave_cooldown = 60.0             # 节流：最多每分钟一次
# 在检查点/关卡过渡时触发立即自动存档，而不是战斗中途。
```

## 陷阱

- **序列化引擎对象/节点路径**将存档与场景结构绑定；重命名节点会破坏每个旧存档。存档数据，加载时重建对象。
- **没有版本字段**。发布补丁的那天，每个现有存档都成了猜测游戏。从版本 1 开始标记 `version`。
- **就地写入**崩溃/断电时损坏存档。始终临时写入然后重命名；保留 `.bak`。
- **盲目信任文件**。存档会被截断、手动编辑或云同步陈旧数据。加载时验证，失败时回退到备份。
- **浮点数和区域设置**。文本序列化器在某些区域设置中会丢失精度或使用逗号小数分隔符。使用区域设置无关的序列化器。
- **自动存档覆盖手动存档**，或在动作中途触发并保存不一致状态。使用专用自动存档槽，并在安全边界存档。
- **存储秘密或信任多人游戏中的客户端存档**。本地存档受玩家控制；永远不要将其视为在线状态的权威。对于云，处理设备的限制和冲突（`roblox-datastores`）。

## 参考

- `references/versioning-and-migration.md` — 模式演化策略、迁移链、备份/回滚、格式权衡（JSON vs 二进制）和加载时验证清单。

## 相关技能

- `roblox-datastores` — 云持久化、请求限制、会话锁定。
- `godot-resources`, `unity-scriptableobjects` — 你序列化的数据模型。
- `procedural-gen` — 存储种子以重新生成世界，而不是保存世界。
- `rpg`, `survival-crafting`, `visual-novel` — 组合此技能的类型。
