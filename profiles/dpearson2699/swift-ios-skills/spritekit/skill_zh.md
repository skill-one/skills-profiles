# SpriteKit

使用 SpriteKit 和 Swift 6.3 为 iOS 26+ 构建 2D 游戏和交互式动画。涵盖场景生命周期、节点层级结构、动作、物理、粒子、相机、触摸处理和 SwiftUI 集成。

## 目录

- [场景设置](#场景设置)
- [节点和精灵](#节点和精灵)
- [动作和动画](#动作和动画)
- [物理](#物理)
- [触摸处理](#触摸处理)
- [相机](#相机)
- [粒子效果](#粒子效果)
- [SwiftUI 集成](#swiftui集成)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 场景设置

SpriteKit 通过 `SKView` 渲染内容，`SKView` 呈现 `SKScene`，它是框架逐帧动画和渲染的树的根节点。

### 创建场景

子类化 `SKScene` 并重写生命周期方法。坐标系统原点默认在左下角。

```swift
import SpriteKit

final class GameScene: SKScene {
    override func didMove(to view: SKView) {
        backgroundColor = .darkGray
        physicsWorld.contactDelegate = self
        physicsBody = SKPhysicsBody(edgeLoopFrom: frame)
        setupNodes()
    }

    override func update(_ currentTime: TimeInterval) {
        // 每帧在评估动作之前调用一次。
    }
}
```

### 显示场景 (UIKit)

```swift
guard let skView = view as? SKView else { return }
skView.ignoresSiblingOrder = true

let scene = GameScene(size: skView.bounds.size)
scene.scaleMode = .resizeFill
skView.presentScene(scene)
```

### 缩放模式

当场景应适应视图大小变化（旋转、多任务处理）时，使用 `.resizeFill`。对于固定设计的游戏场景，使用 `.aspectFill`。`.aspectFit` 产生画中画效果；`.fill` 拉伸并可能失真。

### 帧循环

每帧按以下顺序执行：

1. `update(_:)` -- 游戏逻辑
2. 评估动作
3. `didEvaluateActions()` -- 动作后逻辑
4. 模拟物理
5. `didSimulatePhysics()` -- 物理后调整
6. 应用约束
7. `didApplyConstraints()`
8. `didFinishUpdate()` -- 渲染前的最终调整

仅重写需要工作的回调。

## 节点和精灵

使用 `SKNode`（无视觉表现）作为不可见的容器或布局组。子节点继承父节点的位置、缩放、旋转、透明度和速度。`SKSpriteNode` 是主要的可视节点。

### 常见节点类型

| 类 | 用途 |
|-------|---------|
| `SKSpriteNode` | 带纹理的图像或纯色 |
| `SKLabelNode` | 文本渲染 |
| `SKShapeNode` | 矢量路径（每个绘制调用成本高） |
| `SKEmitterNode` | 粒子效果 |
| `SKCameraNode` | 视口控制 |
| `SKTileMapNode` | 基于网格的瓦片 |
| `SKAudioNode` | 定位音频 |
| `SKCropNode` / `SKEffectNode` | 掩码 / CIFilter |
| `SK3DNode` | 嵌入的 SceneKit 内容 |

### 创建精灵

```swift
let player = SKSpriteNode(imageNamed: "hero")
player.position = CGPoint(x: frame.midX, y: frame.midY)
player.name = "player"
addChild(player)
```

### 绘制顺序

在 `SKView` 上设置 `ignoresSiblingOrder = true` 以提高性能；SpriteKit 然后使用 `zPosition` 确定顺序。否则，节点按树顺序绘制。

```swift
background.zPosition = -1
player.zPosition = 0
foregroundUI.zPosition = 10
```

### 命名和搜索

为查找无实例变量的节点分配 `name`。使用 `childNode(withName:)`、`enumerateChildNodes(withName:using:)` 或 `subscript`。模式：`//` 搜索整个树，`*` 匹配任何字符，`..` 指向父节点。

```swift
player.name = "player"
if let found = childNode(withName: "player") as? SKSpriteNode { /* ... */ }
```

## 动作和动画

`SKAction` 对象定义应用于节点随时间的变化。动作是不可变和可重用的。使用 `node.run(_:)` 运行。

### 基本动作

```swift
let moveUp = SKAction.moveBy(x: 0, y: 100, duration: 0.5)
let grow = SKAction.scale(to: 1.5, duration: 0.3)
let spin = SKAction.rotate(byAngle: .pi * 2, duration: 1.0)
let fadeOut = SKAction.fadeOut(withDuration: 0.3)
let remove = SKAction.removeFromParent()
```

### 组合动作

```swift
// 顺序：一个接一个运行
let dropAndRemove = SKAction.sequence([
    SKAction.moveBy(x: 0, y: -500, duration: 1.0),
    SKAction.removeFromParent()
])

// 并行：同时运行
let scaleAndFade = SKAction.group([
    SKAction.scale(to: 0.0, duration: 0.3),
    SKAction.fadeOut(withDuration: 0.3)
])

// 重复
let pulse = SKAction.repeatForever(
    SKAction.sequence([
        SKAction.scale(to: 1.2, duration: 0.5),
        SKAction.scale(to: 1.0, duration: 0.5)
    ])
)
```

### 纹理动画

```swift
let walkFrames = (1...8).map { SKTexture(imageNamed: "walk_\($0)") }
let walkAction = SKAction.animate(with: walkFrames, timePerFrame: 0.1)
player.run(SKAction.repeatForever(walkAction))
```

使用 `timingMode`（`.linear`、`.easeIn`、`.easeOut`、`.easeInEaseOut`）控制速度曲线。为后续访问分配键：

```swift
let easeIn = SKAction.moveTo(x: 300, duration: 1.0)
easeIn.timingMode = .easeInEaseOut

player.run(pulse, withKey: "pulse")
player.removeAction(forKey: "pulse") // 后续停止
```

## 物理

SpriteKit 提供内置的 2D 物理引擎。场景的 `physicsWorld` 管理重力和碰撞检测。

### 添加物理体

```swift
// 圆形体
player.physicsBody = SKPhysicsBody(circleOfRadius: player.size.width / 2)
player.physicsBody?.restitution = 0.3

// 静态矩形
ground.physicsBody = SKPhysicsBody(rectangleOf: ground.size)
ground.physicsBody?.isDynamic = false

// 基于纹理的体，用于不规则形状
player.physicsBody = SKPhysicsBody(texture: player.texture!, size: player.size)
```

### 类别和接触掩码

使用位掩码控制碰撞和接触回调：

```swift
struct PhysicsCategory {
    static let player:  UInt32 = 0b0001
    static let enemy:   UInt32 = 0b0010
    static let ground:  UInt32 = 0b0100
}

player.physicsBody?.categoryBitMask = PhysicsCategory.player
player.physicsBody?.contactTestBitMask = PhysicsCategory.enemy
player.physicsBody?.collisionBitMask = PhysicsCategory.ground
```

`categoryBitMask` 识别物理体。`collisionBitMask` 控制物理响应（弹跳）。`contactTestBitMask` 触发 `didBegin`/`didEnd`。

### 接触检测

实现 `SKPhysicsContactDelegate` 并在 `didMove(to:)` 中设置 `physicsWorld.contactDelegate = self`：

```swift
extension GameScene: SKPhysicsContactDelegate {
    func didBegin(_ contact: SKPhysicsContact) {
        let mask = contact.bodyA.categoryBitMask | contact.bodyB.categoryBitMask
        if mask == PhysicsCategory.player | PhysicsCategory.enemy {
            queuePlayerHit()
        }
    }
}
```

接触回调在物理模拟期间运行。使 `queuePlayerHit()` 设置标志或追加事件，然后在 `update(_:)` 中应用节点/物理体/世界突变。

### 力和冲量

```swift
player.physicsBody?.applyForce(CGVector(dx: 0, dy: 50))      // 持续
player.physicsBody?.applyImpulse(CGVector(dx: 0, dy: 200))   // 瞬时
player.physicsBody?.applyAngularImpulse(0.5)                  // 旋转
```

使用 `.applyImpulse` 进行跳跃和发射物。使用 `physicsWorld.gravity = CGVector(dx: 0, dy: -9.8)` 配置重力，使用 `affectedByGravity` 配置每个物理体。

## 触摸处理

`SKScene` 继承自 `UIResponder`。在场景上重写 `touchesBegan`、`touchesMoved`、`touchesEnded`。使用 `nodes(at:)` 进行命中测试。

```swift
override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
    guard let touch = touches.first else { return }
    let location = touch.location(in: self)
    let tappedNodes = nodes(at: location)

    if tappedNodes.contains(where: { $0.name == "playButton" }) {
        startGame()
    }
}
```

对于节点级触摸处理，子类化节点并设置 `isUserInteractionEnabled = true`。该节点然后直接接收触摸，而不是场景。

## 相机

`SKCameraNode` 控制场景的可见部分。将其作为子节点添加并分配给 `scene.camera`。

```swift
let cameraNode = SKCameraNode()
addChild(cameraNode)
camera = cameraNode
cameraNode.position = CGPoint(x: frame.midX, y: frame.midY)
```

### 跟随角色

在 `didSimulatePhysics()` 中更新相机位置，或使用约束：

```swift
override func didSimulatePhysics() {
    cameraNode.position = player.position
}

// 将相机约束在世界边界内
let xRange = SKRange(lowerLimit: frame.midX, upperLimit: worldWidth - frame.midX)
let yRange = SKRange(lowerLimit: frame.midY, upperLimit: worldHeight - frame.midY)
cameraNode.constraints = [SKConstraint.positionX(xRange, y: yRange)]
```

### 相机缩放和 HUD

逆相地缩放相机节点：`setScale(0.5)` 放大 2 倍，`setScale(2.0)` 缩小 2 倍。作为相机子节点的节点保持在屏幕上（HUD 元素）：

```swift
let scoreLabel = SKLabelNode(text: "Score: 0")
scoreLabel.position = CGPoint(x: 0, y: frame.height / 2 - 40)
scoreLabel.fontName = "AvenirNext-Bold"
scoreLabel.fontSize = 24
cameraNode.addChild(scoreLabel)
```

## 粒子效果

`SKEmitterNode` 生成粒子效果。在 Xcode 的 SpriteKit 粒子文件编辑器（`.sks`）中设计发射器，或在代码中配置。

```swift
// 从文件加载
guard let emitter = SKEmitterNode(fileNamed: "Fire") else { return }
emitter.position = CGPoint(x: frame.midX, y: 100)
addChild(emitter)
```

### 单次发射器

设置 `numParticlesToEmit` 用于有限效果，完成后移除：

```swift
func spawnExplosion(at position: CGPoint) {
    guard let explosion = SKEmitterNode(fileNamed: "Explosion") else { return }
    explosion.position = position
    explosion.numParticlesToEmit = 100
    addChild(explosion)

    let wait = SKAction.wait(forDuration: TimeInterval(explosion.particleLifetime))
    explosion.run(SKAction.sequence([wait, .removeFromParent()]))
}
```

将 `targetNode` 设置为场景，以便在发射器移动时粒子保持在世界空间：`emitter.targetNode = self`。

## SwiftUI 集成

`SpriteView` 将 SpriteKit 场景嵌入 SwiftUI。

```swift
import SwiftUI
import SpriteKit

struct GameView: View {
    @State private var scene: GameScene = {
        let s = GameScene()
        s.size = CGSize(width: 390, height: 844)
        s.scaleMode = .resizeFill
        return s
    }()

    var body: some View {
        SpriteView(scene: scene)
            .ignoresSafeArea()
    }
}
```

### SpriteView 选项

传递 `options: [.allowsTransparency]` 用于透明背景、`.shouldCullNonVisibleNodes` 用于离屏剔除、或 `.ignoresSiblingOrder` 用于基于 `zPosition` 的绘制顺序。使用 `debugOptions: [.showsFPS, .showsNodeCount]` 在开发期间进行调试。

### SwiftUI 和场景之间的通信

通过共享 `@Observable` 对象传递数据。将场景存储在 `@State` 中以避免在视图重新渲染时重新创建：

```swift
@Observable final class GameState {
    var score = 0
    var isPaused = false
}

struct GameContainerView: View {
    @State private var gameState = GameState()
    @State private var scene = GameScene()

    var body: some View {
        SpriteView(scene: scene, isPaused: gameState.isPaused)
            .onAppear { scene.gameState = gameState }
    }
}
```

## 常见错误

### 每次 SwiftUI 重新渲染时创建新场景

```swift
// 不要：场景在每次 body 评估时都会重新创建
var body: some View {
    SpriteView(scene: GameScene(size: CGSize(width: 390, height: 844)))
}

// 要：创建一次并重用
@State private var scene = GameScene(size: CGSize(width: 390, height: 844))
var body: some View {
    SpriteView(scene: scene)
}
```

### 添加已具有父节点的子节点

节点只能有一个父节点。首先从当前父节点移除，或创建单独的实例。添加已具有父节点的节点会导致崩溃。

### 忘记设置 contactTestBitMask

```swift
// 不要：物理体碰撞但 never 调用 didBegin
player.physicsBody?.categoryBitMask = PhysicsCategory.player
enemy.physicsBody?.categoryBitMask = PhysicsCategory.enemy

// 要：设置 contactTestBitMask 以接收接触回调
player.physicsBody?.contactTestBitMask = PhysicsCategory.enemy
```

### 在性能关键渲染路径中使用 SKShapeNode

`SKShapeNode` 对每个实例使用单独的绘制调用。对于重复元素，优先使用具有纹理的 `SKSpriteNode` 以启用批量渲染。

### 未移除离开屏幕的节点

```swift
// 不要
enemy.run(SKAction.moveBy(x: -800, y: 0, duration: 3.0))
addChild(enemy)

// 要：离开可见区域后移除
enemy.run(SKAction.sequence([
    SKAction.moveBy(x: -800, y: 0, duration: 3.0),
    SKAction.removeFromParent()
]))
addChild(enemy)
```

### 过晚设置 physicsWorld.contactDelegate

在 `didMove(to:)` 中设置 `physicsWorld.contactDelegate = self`，而不是在 `update(_:)` 或延迟后设置。

## 审查清单

- [ ] 场景子类化重写 `didMove(to:)` 进行设置，而不是 `init`
- [ ] `scaleMode` 根据游戏设计选择适当值
- [ ] `ignoresSiblingOrder` 在 `SKView` 上设置为 `true` 以提高性能
- [ ] 当 `ignoresSiblingOrder` 启用时，`zPosition` 使用一致
- [ ] 物理的 `contactDelegate` 在 `didMove(to:)` 中设置
- [ ] 类别、碰撞和接触掩码配置正确
- [ ] 为任何需要 `didBegin`/`didEnd` 回调的对设置 `contactTestBitMask`
- [ ] 接触回调排队更改，而不是直接修改物理世界
- [ ] 静态体使用 `isDynamic = false`
- [ ] 在性能关键路径中避免使用 `SKShapeNode`；优先使用 `SKSpriteNode`
- [ ] 移动节点出屏的动作序列中包含 `.removeFromParent()`
- [ ] 单次发射器在粒子生命周期到期后移除自己
- [ ] 当粒子应保持在世界空间时设置发射器 `targetNode`
- [ ] 使用 `SpriteView` 在 SwiftUI 中使用场景时将其存储在 `@State` 中
- [ ] 使用纹理集合并排精灵以减少绘制调用
- [ ] `update(_:)` 使用 delta 时间进行帧率无关的移动
- [ ] 从父节点移除节点后再添加到其他位置

## 参考资料

- 参考 [references/spritekit-patterns.md](references/spritekit-patterns.md) 获取瓦片地图、纹理集、着色器、场景过渡、游戏循环模式、音频和 SceneKit 嵌入。
- [SpriteKit 文档](https://sosumi.ai/documentation/spritekit)
- [SKScene](https://sosumi.ai/documentation/spritekit/skscene)
- [SKSpriteNode](https://sosumi.ai/documentation/spritekit/skspritenode)
- [SKAction](https://sosumi.ai/documentation/spritekit/skaction)
- [SKPhysicsBody](https://sosumi.ai/documentation/spritekit/skphysicsbody)
- [SKEmitterNode](https://sosumi.ai/documentation/spritekit/skemitternode)
- [SKCameraNode](https://sosumi.ai/documentation/spritekit/skcameranode)
- [SpriteView](https://sosumi.ai/documentation/spritekit/spriteview)
- [SKTileMapNode](https://sosumi.ai/documentation/spritekit/sktilemapnode)
