# TabletopKit

构建visionOS板游，其同步状态变化通过`TabletopAction`流转，并使用RealityKit渲染。下方的可用性矩阵包含版本详细信息。

## 内容

- [设置](#设置)
- [游戏配置](#游戏配置)
- [桌子和棋盘](#桌子和棋盘)
- [装备（棋子、卡牌、骰子）](#装备棋子卡牌骰子)
- [玩家座位](#玩家座位)
- [游戏动作和回合](#游戏动作和回合)
- [交互](#交互)
- [RealityKit渲染](#realitykit渲染)
- [组活动集成](#组活动集成)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

| 等级 | API |
|---|---|
| visionOS 2.0+ | 核心游戏玩法、装备、座位、动作、渲染、组活动 |
| visionOS 2.2+ | `TabletopInteraction.Configuration` |
| visionOS 26.0+ | 自定义动作/状态、注册、高级抛掷结果、已丢弃动作观察 |

模拟器支持单人布局测试，不支持多人。

### 项目配置

1. 在定义游戏逻辑的源文件中导入`TabletopKit`。
2. 导入`RealityKit`以进行基于实体的渲染。
3. 对于多人游戏，在“签名与能力”中添加**组活动**功能。
4. 在RealityKit内容包中提供桌子、棋子、卡牌和骰子的USDZ资源。

### 关键类型概述

| 类型 | 角色 |
|---|---|
| `TabletopGame` | 中央游戏管理器；拥有设置、动作、观察者、渲染 |
| `TableSetup` | 传递给`TabletopGame`初始化的配置对象 |
| `Tabletop` / `EntityTabletop` | 桌面表面的协议 |
| `Equipment` / `EntityEquipment` | 交互式游戏棋子的协议 |
| `TableSeat` / `EntityTableSeat` | 玩家座位位置的协议 |
| `TabletopAction` | 修改游戏状态的命令 |
| `TabletopInteraction` | 基于手势的玩家与装备的交互 |
| `TabletopGame.Observer` | 反应于确认动作的回调协议 |
| `TabletopGame.RenderDelegate` | 视觉更新的回调协议 |
| `EntityRenderDelegate` | RealityKit特定的渲染代理 |

## 游戏配置

按以下顺序构建和验证游戏：

1. 定义桌面、装备和座位。
2. 配置`TableSetup`并注册每个自定义动作类型。
3. 创建游戏，附加其观察者和渲染器，申明座位，并建立自动或手动更新处理。
4. 在开始多人游戏前，检查当前快照以获取必需的装备ID、父级、座位和计数器。如果不变式失败，则修复设置并重新构建。

```swift
import TabletopKit
import RealityKit

let table = GameTable()
var setup = TableSetup(tabletop: table)
setup.add(seat: PlayerSeat(index: 0, pose: seatPose0))
setup.add(seat: PlayerSeat(index: 1, pose: seatPose1))
setup.add(equipment: GamePawn(id: .init(1)))
setup.add(equipment: GameDie(id: .init(2)))

let game = TabletopGame(tableSetup: setup)
game.claimAnySeat()
```

如果未通过`.tabletopGame(_:parent:automaticUpdate:)`修饰符启用自动更新，则每帧调用`update(deltaTime:)`。使用`withCurrentSnapshot(_:)`安全地读取状态。

## 桌子和棋盘

### Tabletop协议

实现`EntityTabletop`以定义游戏表面。提供`shape`（圆形或矩形）和RealityKit的`Entity`以进行视觉表示。

```swift
struct GameTable: EntityTabletop {
    var shape: TabletopShape
    var entity: Entity
    var id: EquipmentIdentifier

    init() {
        entity = try! Entity.load(named: "table/game_table", in: contentBundle)
        shape = .round(entity: entity)
        id = .init(0)
    }
}
```

### 桌面形状

在`TabletopShape`上使用工厂方法：

```swift
// 从尺寸创建圆形桌子
let round = TabletopShape.round(
    center: .init(x: 0, y: 0, z: 0),
    radius: 0.5,
    thickness: 0.05,
    in: .meters
)

// 从实体创建矩形桌子
let rect = TabletopShape.rectangular(entity: tableEntity)
```

## 装备（棋子、卡牌、骰子）

### Equipment协议

所有交互式游戏对象都实现`Equipment`（RealityKit渲染的棋子实现`EntityEquipment`）。每个棋子都有一个`id`（`EquipmentIdentifier`）和`initialState`属性。

根据装备选择状态类型：

| 状态类型 | 用例 |
|---|---|
| `BaseEquipmentState` | 通用棋子、棋子、标记 |
| `CardState` | 扑克牌（跟踪`faceUp` / 面朝下） |
| `DieState` | 骰子（具有整数`value`） |
| `RawValueState` | 作为`UInt64`编码的自定义数据 |
| `CustomEquipmentState` | 自定义状态，具有`BaseEquipmentState`和游戏数据；参见可用性矩阵 |

### 定义Equipment

```swift
// 棋子 -- 使用BaseEquipmentState
struct GamePawn: EntityEquipment {
    var id: EquipmentIdentifier
    var initialState: BaseEquipmentState
    var entity: Entity

    init(id: EquipmentIdentifier) {
        self.id = id
        self.entity = try! Entity.load(named: "pieces/pawn", in: contentBundle)
        self.initialState = BaseEquipmentState(
            parentID: .init(0), seatControl: .any,
            pose: .identity, entity: entity
        )
    }
}

// 卡牌 -- 使用CardState（跟踪faceUp）
struct PlayingCard: EntityEquipment {
    var id: EquipmentIdentifier
    var initialState: CardState
    var entity: Entity

    init(id: EquipmentIdentifier) {
        self.id = id
        self.entity = try! Entity.load(named: "cards/card", in: contentBundle)
        self.initialState = .faceDown(
            parentID: .init(0), seatControl: .any,
            pose: .identity, entity: entity
        )
    }
}

// 骰子 -- 使用DieState（跟踪整数value）
struct GameDie: EntityEquipment {
    var id: EquipmentIdentifier
    var initialState: DieState
    var entity: Entity

    init(id: EquipmentIdentifier) {
        self.id = id
        self.entity = try! Entity.load(named: "dice/d6", in: contentBundle)
        self.initialState = DieState(
            value: 1, parentID: .init(0), seatControl: .any,
            pose: .identity, entity: entity
        )
    }
}
```

### ControllingSeats

通过`seatControl`限制哪些玩家可以与棋子交互：
- `.any` -- 任何玩家
- `.restricted([seatID1, seatID2])` -- 仅限特定座位
- `.restrictedCurrent([seatID1, seatID2])` -- 仅限当前回合的特定座位
- `.current` -- 仅限当前回合的座位
- `.inherited` -- 从父级装备继承

### Equipment Hierarchy and Layout

装备可以成为其他装备的子级。重写`layoutChildren(for:visualState:)`以定位子级。返回以下之一：
- `.planarStacked(layout:animationDuration:)` -- 卡牌/瓦片垂直堆叠
- `.planarOverlapping(layout:animationDuration:)` -- 卡牌展开或重叠
- `.volumetric(layout:animationDuration:)` -- 完整3D布局

参见[参考资料/tabletopkit-patterns.md](references/tabletopkit-patterns.md)以获取卡牌展开、网格和重叠布局示例。

## 玩家座位

实现`EntityTableSeat`并提供桌子周围的姿态：

```swift
struct PlayerSeat: EntityTableSeat {
    var id: TableSeatIdentifier
    var initialState: TableSeatState
    var entity: Entity

    init(index: Int, pose: TableVisualState.Pose2D) {
        self.id = TableSeatIdentifier(index)
        self.entity = Entity()
        self.initialState = TableSeatState(pose: pose, context: 0)
    }
}
```

在交互前申明座位：`game.claimAnySeat()`、`game.claimSeat(matching:)`或`game.releaseSeat()`。通过`TabletopGame.Observer.playerChangedSeats`观察变化。

## 游戏动作和回合

### 内置动作

使用`TabletopAction`工厂方法修改游戏状态：

```swift
// 将装备移动到新的父级
game.addAction(.moveEquipment(matching: pieceID, childOf: targetID, pose: newPose))

// 翻转卡牌面朝上
game.addAction(.updateEquipment(card, faceUp: true))

// 更新骰子值
game.addAction(.updateEquipment(die, value: 6))

// 设置当前回合
game.addAction(.setTurn(matching: TableSeatIdentifier(1)))

// 更新计分器
game.addAction(.updateCounter(matching: counterID, value: 100))

// 创建状态书签（用于撤销/重置）
game.addAction(.createBookmark(id: StateBookmarkIdentifier(1)))
```

### 自定义动作

对于游戏特定逻辑，在可用性矩阵允许时实现`CustomAction`。自定义动作的应用和验证必须仅依赖于动作数据和提供的`TableState` / `TableSnapshot`，以便每个对等方解析相同结果。在分发之前注册自定义动作类型：

```swift
setup.register(action: CollectCoin.self)
game.addAction(CollectCoin(coinID: coinID, playerID: playerID))
```

在分发之前注册每个自定义动作类型。参见[参考资料/tabletopkit-patterns.md](references/tabletopkit-patterns.md)以获取完整的自定义动作和自定义状态示例。

### 计分器

```swift
setup.add(counter: ScoreCounter(id: .init(0), value: 0))
// 更新：game.addAction(.updateCounter(matching: .init(0), value: 42))
// 读取：   snapshot.counter(matching: .init(0))?.value
```

### 状态书签

保存和恢复游戏状态以进行撤销/重置：

```swift
game.addAction(.createBookmark(id: StateBookmarkIdentifier(1)))
game.jumpToBookmark(matching: StateBookmarkIdentifier(1))
```

书签恢复是异步的，按网络顺序。等待`stateDidResetToBookmark`，然后读取`withCurrentSnapshot`，从该权威回调状态重建本地UI，并验证恢复的不变式。不要在`jumpToBookmark`后立即检查或在冲突时排队另一个跳转。加载[状态书签和撤销](references/tabletopkit-patterns.md#state-bookmarks-and-undo)以获取观察者协调模式。

## 交互

### TabletopInteraction.Delegate

从`.tabletopGame`修饰符返回交互代理以处理玩家在装备上的手势：

```swift
.tabletopGame(game.tabletopGame, parent: game.renderer.root) { value in
    if game.tabletopGame.equipment(of: GameDie.self, matching: value.startingEquipmentID) != nil {
        return DieInteraction(game: game)
    }
    return DefaultInteraction(game: game)
}
```

使用`interaction.value.gesture`获取手势特定状态。避免使用已弃用的`gesturePhase`。对于目的地控制，当可用时，优先使用`interaction.setConfiguration(.init(allowedDestinations: ...))`而不是已弃用的`setAllowedDestinations(_:)`或`value.allowedDestinations`。

### 处理手势和抛掷骰子

基本的`toss(equipmentID:as:)`是TabletopKit的核心；可用性矩阵包含高级抛掷结果。

```swift
class DieInteraction: TabletopInteraction.Delegate {
    let game: Game

    func update(interaction: TabletopInteraction) {
        switch interaction.value.phase {
        case .started:
            interaction.setConfiguration(.init(allowedDestinations: .any))
        case .update:
            if interaction.value.gesture?.phase == .ended {
                interaction.toss(
                    equipmentID: interaction.value.controlledEquipmentID,
                    as: .cube(height: 0.02, in: .meters)
                )
            }
        case .ended, .cancelled:
            break
        }
    }

    func onTossStart(interaction: TabletopInteraction,
                     outcomes: [TabletopInteraction.TossOutcome]) {
        for outcome in outcomes {
            let face = outcome.tossableRepresentation.face(for: outcome.restingOrientation)
            interaction.addAction(.updateEquipment(
                die, rawValue: face.rawValue, pose: outcome.pose
            ))
        }
    }
}
```

### Tossable Representations

骰子物理形状：`.cube`（d6）、`.tetrahedron`（d4）、`.octahedron`（d8）、`.decahedron`（d10）、`.dodecahedron`（d12）、`.icosahedron`（d20）、`.sphere`。所有形状都接受`height:in:`（或`radius:in:`用于球体）和可选的`restitution:`。

### 程序化交互

从代码启动交互：`game.startInteraction(onEquipmentID: pieceID)`。

参见[参考资料/tabletopkit-patterns.md](references/tabletopkit-patterns.md)以获取组抛掷、预定结果、交互接受/拒绝和目的地限制模式。

## RealityKit渲染

实现`EntityRenderDelegate`以将状态桥接至RealityKit。提供一个`root`实体。TabletopKit自动定位`EntityEquipment`实体。

```swift
class GameRenderer: EntityRenderDelegate {
    let root = Entity()

    func onUpdate(timeInterval: Double, snapshot: TableSnapshot,
                  visualState: TableVisualState) {
        // 超出自动定位的自定义视觉更新
    }
}
```

使用`.tabletopGame(_:parent:automaticUpdate:)`修饰符在`RealityView`上连接到SwiftUI：

```swift
struct GameView: View {
    let game: Game

    var body: some View {
        RealityView { content in
            content.entities.append(game.renderer.root)
        }
        .tabletopGame(game.tabletopGame, parent: game.renderer.root) { value in
            GameInteraction(game: game)
        }
    }
}
```

调试轮廓：`game.tabletopGame.debugDraw(options: [.drawTable, .drawSeats, .drawEquipment])`

## 组活动集成

TabletopKit直接与组活动集成，用于基于FaceTime的多人游戏。定义一个`GroupActivity`，然后调用`coordinateWithSession(_:)`。TabletopKit自动同步所有装备状态、座位分配、动作和交互。无需手动消息传递。

```swift
import GroupActivities

struct BoardGameActivity: GroupActivity {
    var metadata: GroupActivityMetadata {
        var meta = GroupActivityMetadata()
        meta.type = .generic
        meta.title = "Board Game"
        return meta
    }
}

@Observable
class GroupActivityManager {
    let tabletopGame: TabletopGame
    private var sessionTask: Task<Void, Never>?

    init(tabletopGame: TabletopGame) {
        self.tabletopGame = tabletopGame
        sessionTask = Task { @MainActor in
            for await session in BoardGameActivity.sessions() {
                tabletopGame.coordinateWithSession(session)
            }
        }
    }

    deinit { tabletopGame.detachNetworkCoordinator() }
}
```

实现`TabletopGame.MultiplayerDelegate`以处理`joinAccepted()`、`playerJoined(_:)`、`didRejectPlayer(_:reason:)`和`multiplayerSessionFailed(reason:)`。参见[参考资料/tabletopkit-patterns.md](references/tabletopkit-patterns.md)以获取自定义网络协调器和仲裁者角色管理。

## 常见错误

- **跳过座位申明。** 玩家必须在交互装备前调用`claimAnySeat()`或`claimSeat(_:)`。没有座位，动作将被拒绝。
- **在动作外修改状态。** 所有状态更改必须通过`TabletopAction`或`CustomAction`。直接修改装备属性会绕过同步。
- **遗漏自定义动作注册。** 在使用前注册每个自定义动作`setup.register(action:)`。
- **未处理动作回滚。** 动作会乐观应用，如果仲裁者验证失败，则可以回滚。实现`actionWasRolledBack(_:snapshot:)`以还原UI状态。
- **在可用时忽略已丢弃的动作。** 当本地动作队列压力重要时，实现`actionWasDiscarded(_:)`；它被调用于无法入队的本地动作。
- **使用错误的父ID。** 状态中的装备`parentID`必须引用有效装备ID（通常是桌子或容器）。无效的父级会导致棋子消失。
- **忽略TossOutcome面。** 抛掷后，从`outcome.tossableRepresentation.face(for: outcome.restingOrientation)`读取面，而不是生成随机值。物理模拟决定结果。
- **在模拟器中测试多人游戏。** 组活动在模拟器中不起作用。多人游戏需要物理Apple Vision Pro设备在FaceTime通话中。

## 审查清单

- [ ] 应用集中平台/可用性矩阵
- [ ] 使用符合`Tabletop`/`EntityTabletop`类型的`TableSetup`创建
- [ ] 所有装备符合`Equipment`或`EntityEquipment`，并具有正确的状态类型
- [ ] 座位添加并在游戏开始时调用`claimAnySeat()` / `claimSeat(_:)`
- [ ] 所有自定义动作注册`setup.register(action:)`
- [ ] `TabletopGame.Observer`将确认、回滚、丢弃和书签重置的结果与当前快照协调
- [ ] 连接`EntityRenderDelegate`或`RenderDelegate`
- [ ] `RealityView`上的`.tabletopGame(_:parent:automaticUpdate:)`修饰符
- [ ] 定义`GroupActivity`并调用`coordinateWithSession(_:)`；多人游戏描述为组活动/SharePlay同步
- [ ] 在Xcode中为多人游戏构建添加组活动功能
- [ ] 发布前禁用调试可视化（`debugDraw`）
- [ ] 设备备注状态模拟器仅支持单人游戏；多人游戏需要2个+ Apple Vision Pro单元在FaceTime上

## 参考资料

- [参考资料/tabletopkit-patterns.md](references/tabletopkit-patterns.md) -- 观察者实现、自定义动作、骰子模拟、卡牌重叠和网络协调的扩展模式
- [Apple文档：TabletopKit](https://sosumi.ai/documentation/tabletopkit), [创建板游](https://sosumi.ai/documentation/tabletopkit/creating-tabletop-games), [同步组游戏玩法](https://sosumi.ai/documentation/tabletopkit/synchronizing-group-gameplay-with-tabletopkit)
- [模拟骰子抛掷](https://sosumi.ai/documentation/tabletopkit/simulating-dice-rolls-as-a-component-for-your-game), [实现扑克牌重叠](https://sosumi.ai/documentation/tabletopkit/implementing-playing-card-overlap-and-physical-characteristics)
- [WWDC24会话10091：构建空间板游](https://sosumi.ai/videos/play/wwdc2024/10091/)
