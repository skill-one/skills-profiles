# Godot 多人游戏（4.x 高级）

连接对等体，使用 `@rpc` 远程调用函数，分配权限，并使用 `MultiplayerSpawner`/`MultiplayerSynchronizer` 复制状态。目标 **Godot 4.7** (ENet)。将所有客户端输入视为不可信；保持服务器权威。

## 何时使用

- 添加网络多人游戏时使用：通过 ENet 主机/加入、调用 RPC、为每个节点分配权限，或跨对等体自动生成/同步节点。

**不使用的情况：** 本地分屏（无网络）；原始 TCP/UDP/WebSocket 协议工作（低级 `PacketPeer`）；HTTP 请求。对于保存/持久化 → `save-systems`。

## 核心工作流程

1. **创建对等体** (`ENetMultiplayerPeer`)，调用 `create_server(port, max)` 或 `create_client(ip, port)`，并将其分配给 `multiplayer.multiplayer_peer`。服务器的唯一 ID 始终是 `1`；客户端获得随机正 ID。
2. **处理 `multiplayer` 上的连接信号**：`peer_connected(id)`、`peer_disconnected(id)`、`connected_to_server`、`connection_failed`、`server_disconnected`。
3. **定义 RPC** 使用 `@rpc(...)`。通过 `Callable` 调用它们，使用 `rpc()`（所有对等体）或 `rpc_id(peer_id)`（一个对等体）。在内部，`multiplayer.get_remote_sender_id()` 告诉你是谁发送的。
4. **确保每个运行脚本的节点上的 RPC 签名相同** — Godot 会校验脚本中所有 `@rpc` 方法的校验和；不匹配会导致静默失败。
5. **为每个节点分配权限** 使用 `set_multiplayer_authority(id)`；通过 `is_multiplayer_authority()` 管理输入/RPC。
6. **使用 `MultiplayerSpawner`（在客户端自动实例化场景）和 `MultiplayerSynchronizer`（自动同步选定属性）复制状态**。
7. **在服务器上验证。** 不要信任客户端报告的位置/结果。

## 模式

### 1. 主机或加入（ENet）

```gdscript
const PORT := 7000
const MAX_PLAYERS := 8

func host() -> void:
    var peer := ENetMultiplayerPeer.new()
    var err := peer.create_server(PORT, MAX_PLAYERS)
    if err != OK:
        push_error("Cannot host: %s" % err); return
    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_on_peer_connected)

func join(ip := "127.0.0.1") -> void:
    var peer := ENetMultiplayerPeer.new()
    peer.create_client(ip, PORT)
    multiplayer.multiplayer_peer = peer
    multiplayer.connected_to_server.connect(func(): print("connected"))

func leave() -> void:
    multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
```

### 2. RPC：客户端将输入发送到服务器（any_peer, call_local）

```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("fire") and is_multiplayer_authority():
        request_fire.rpc_id(1)          # 仅发送给服务器（id 1）

# 客户端可以调用此方法；它在服务器上运行（如果服务器是玩家，也会在本地运行）。
@rpc("any_peer", "call_local", "reliable")
func request_fire() -> void:
    var sender := multiplayer.get_remote_sender_id()
    if not _can_fire(sender):           # 服务器端验证
        return
    spawn_projectile.rpc(sender)        # 告知所有人生成它

@rpc("authority", "call_local", "reliable")
func spawn_projectile(owner_id: int) -> void:
    _do_spawn(owner_id)
```

### 3. 每个节点权限（每个玩家控制自己的角色）

```gdscript
extends CharacterBody2D

func _ready() -> void:
    # 节点名称是拥有对等体的 ID；该对等体是权限方。
    set_multiplayer_authority(name.to_int())

func _physics_process(delta: float) -> void:
    if not is_multiplayer_authority():
        return                          # 仅所有者读取输入和移动
    velocity = Input.get_vector("left", "right", "up", "down") * 200.0
    move_and_slide()
```

### 4. MultiplayerSynchronizer 配置（编辑器 + 复制）

```gdscript
# 添加一个 MultiplayerSynchronizer 子节点；在其复制编辑器中添加要同步的属性（例如位置、速度）。为每个属性设置 "Sync"/"Spawn" 标志。在代码中你可以范围可见性：
@onready var sync: MultiplayerSynchronizer = $MultiplayerSynchronizer

func _ready() -> void:
    # 仅将此节点复制给特定对等体（例如私有信息）。
    sync.set_visibility_for(target_peer_id, true)
```

## 陷阱

- **RPC 签名校验和。** 脚本中的每个 `@rpc` 方法必须在客户端和服务器构建中存在相同的声明 — *即使未使用*。不匹配会导致错误，可能指向错误的方法。参数名称/数量不被检查，但 RPC 集合及其注解会被检查。
- **默认 `@rpc` 是 `"authority"`。** 客户端调用它会被忽略，除非你设置为 `"any_peer"`。使用 `"call_local"` 以确保主机（也是玩家）运行它。
- **节点路径必须在所有对等体中匹配。** RPC 路由使用节点的路径/名称；在所有对等体上使用相同名称生成节点（使用 `MultiplayerSpawner` 或 `add_child(node, true)` 以获得可读、确定的名称）。
- **不要信任客户端。** 绝不直接让客户端设置权威状态（生命值、位置、命中）。发送 *意图*，在服务器上验证，然后广播结果。
- **非 `Node` 类上的 RPC 失败。** `@rpc` 方法必须在 `Node` 派生类上，而不是普通的 `Resource`/`RefCounted`。
- **RPC 不序列化 `Objects`/`Callables`。** 传递纯数据（整数、字符串、数组、字典、PackedArrays）。
- **忘记重置对等体。** 要干净地断开连接，设置 `multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()`。
- **Android 需要在导出配置文件中添加 `INTERNET` 权限**，否则所有网络功能都会被阻止。

## 参考

- 对于 `MultiplayerSpawner` 设置、传输模式/通道、`SceneMultiplayer` 认证（`auth_callback`/`complete_auth`）、大厅骨架和专用服务器导出说明，请阅读 `references/replication-and-rpc.md`。

## 相关技能

- `godot-nodes-scenes` — 实例化生成/同步的场景。
- `godot-signals-groups` — 连接信号和事件流。
- `godot-export` — 导出无头专用服务器构建。
