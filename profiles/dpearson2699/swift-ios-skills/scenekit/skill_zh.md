# SceneKit

仅维护现有的 SceneKit 场景。苹果在 2025 年 WWDC 上弃用了 SceneKit，并将其限制在维护状态；将新项目、重大现代化和 USD/USDZ 管道路由到 RealityKit。现有应用将继续正常工作。

## 目录

- [场景设置](#场景设置)
- [节点和几何体](#节点和几何体)
- [材质](#材质)
- [光照](#光照)
- [相机](#相机)
- [动画](#动画)
- [物理](#物理)
- [粒子系统](#粒子系统)
- [加载模型](#加载模型)
- [SwiftUI 集成](#swiftui集成)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 场景设置

### UIKit 中的 SCNView

```swift
import SceneKit

let sceneView = SCNView(frame: view.bounds)
sceneView.scene = SCNScene()
sceneView.allowsCameraControl = true
sceneView.autoenablesDefaultLighting = true
sceneView.backgroundColor = .black
view.addSubview(sceneView)
```

`allowsCameraControl` 添加了内置的轨道、平移和缩放手势。在需要自定义相机控制的生产环境中，通常禁用此功能。

### 创建 SCNScene

```swift
let scene = SCNScene()                                          // 空场景
guard let scene = SCNScene(named: "art.scnassets/ship.scn")     // .scn 在 .scnassets 中
else { fatalError("缺少场景资源") }
let url = Bundle.main.url(forResource: "ship", withExtension: "dae")!
let scene = try SCNScene(url: url, options: [.checkConsistency: true])
```

## 节点和几何体

每个场景都有一个 `rootNode`。所有内容都作为其子节点存在。节点在其父坐标系统中定义位置、方向和缩放。SceneKit 使用右手坐标系：+X 向右，+Y 向上，+Z 指向相机。

```swift
let parentNode = SCNNode()
scene.rootNode.addChildNode(parentNode)

let childNode = SCNNode()
childNode.position = SCNVector3(0, 1, 0)  // 父节点上方 1 个单位
parentNode.addChildNode(childNode)
```

### 变换

```swift
node.position = SCNVector3(x: 0, y: 2, z: -5)
node.eulerAngles = SCNVector3(x: 0, y: .pi / 4, z: 0)  // Y 轴 45 度旋转
node.scale = SCNVector3(2, 2, 2)
node.simdPosition = SIMD3<Float>(0, 2, -5)  // 优先使用 simd 以提高性能
```

### 内置基本几何体

`SCNBox`, `SCNSphere`, `SCNCylinder`, `SCNCone`, `SCNTorus`, `SCNCapsule`,
`SCNTube`, `SCNPlane`, `SCNFloor`, `SCNText`, `SCNShape`（挤出贝塞尔路径）。

```swift
let node = SCNNode(geometry: SCNSphere(radius: 0.5))
```

### 查找节点

```swift
let maxNode = scene.rootNode.childNode(withName: "Max", recursively: true)
let enemies = scene.rootNode.childNodes { node, _ in
    node.name?.hasPrefix("enemy") == true
}
```

## 材质

`SCNMaterial` 定义表面外观。对于单一材质的几何体，使用 `firstMaterial`；对于多材质，使用 `materials` 数组。

### 颜色和纹理

```swift
let material = SCNMaterial()
material.diffuse.contents = UIColor.systemBlue     // 纯色
material.diffuse.contents = UIImage(named: "brick") // 纹理
material.normal.contents = UIImage(named: "brick_normal")
sphere.firstMaterial = material
```

### 基于物理的渲染 (PBR)

```swift
let pbr = SCNMaterial()
pbr.lightingModel = .physicallyBased
pbr.diffuse.contents = UIImage(named: "albedo")
pbr.metalness.contents = 0.8       // 标量或纹理
pbr.roughness.contents = 0.2       // 标量或纹理
pbr.normal.contents = UIImage(named: "normal")
pbr.ambientOcclusion.contents = UIImage(named: "ao")
```

### 光照模型

`.physicallyBased`（金属度/粗糙度）、`.blinn`（默认）、`.phong`,
`.lambert`（仅漫反射）、`.constant`（无光照）、`.shadowOnly`。

每个材质属性是 `SCNMaterialProperty`，接受 `UIColor`、`UIImage`、`CGFloat` 标量、`SKTexture`、`CALayer` 或 `AVPlayer`。

### 透明度

```swift
material.transparency = 0.5
material.transparencyMode = .dualLayer
material.isDoubleSided = true
```

## 光照

将 `SCNLight` 附加到节点。光的方向跟随节点的负 Z 轴。

### 光照类型

```swift
// 环境光：均匀，无方向
let ambient = SCNLight()
ambient.type = .ambient
ambient.color = UIColor(white: 0.3, alpha: 1)

// 平行光：平行光线（阳光）
let directional = SCNLight()
directional.type = .directional
directional.castsShadow = true

// 点光源：所有方向
let omni = SCNLight()
omni.type = .omni
omni.attenuationEndDistance = 20

// 聚光灯：锥形
let spot = SCNLight()
spot.type = .spot
spot.spotInnerAngle = 20
spot.spotOuterAngle = 60
```

附加到节点：

```swift
let lightNode = SCNNode()
lightNode.light = directional
lightNode.eulerAngles = SCNVector3(-Float.pi / 3, 0, 0)
lightNode.position = SCNVector3(0, 10, 10)
scene.rootNode.addChildNode(lightNode)
```

### 阴影

```swift
light.castsShadow = true
light.shadowMapSize = CGSize(width: 2048, height: 2048)
light.shadowSampleCount = 8
light.shadowRadius = 3.0
light.shadowColor = UIColor(white: 0, alpha: 0.5)
```

### 类别位掩码

```swift
light.categoryBitMask = 1 << 1     // 类别 2
node.categoryBitMask = 1 << 1      // 仅由类别 2 的光照照射
```

SceneKit 每个节点最多渲染 8 个光源。对点/聚光灯使用 `attenuationEndDistance`，以便 SceneKit 跳过远距离节点的渲染。

## 相机

将 `SCNCamera` 附加到节点以定义视点。

```swift
let cameraNode = SCNNode()
cameraNode.camera = SCNCamera()
cameraNode.position = SCNVector3(0, 5, 15)
cameraNode.look(at: SCNVector3Zero)
scene.rootNode.addChildNode(cameraNode)
sceneView.pointOfView = cameraNode
```

### 配置

```swift
camera.fieldOfView = 60                        // 度
camera.zNear = 0.1
camera.zFar = 500
camera.automaticallyAdjustsZRange = true

// 正交投影
camera.usesOrthographicProjection = true
camera.orthographicScale = 10
```

景深（`wantsDepthOfField`, `focusDistance`, `fStop`）和高动态范围效果
（`wantsHDR`, `bloomIntensity`, `bloomThreshold`, `screenSpaceAmbientOcclusionIntensity`）
直接在 `SCNCamera` 上配置。

## 动画

SceneKit 提供三种动画方法。

### SCNAction（声明式，面向游戏）

可重用、可组合的动画对象，附加到节点。

```swift
let move = SCNAction.move(by: SCNVector3(0, 2, 0), duration: 1)
let rotate = SCNAction.rotateBy(x: 0, y: .pi, z: 0, duration: 1)
node.runAction(.group([move, rotate]))

// 顺序
node.runAction(.sequence([.fadeOut(duration: 0.3), .removeFromParentNode()]))

// 无限循环
let pulse = SCNAction.sequence([
    .scale(to: 1.2, duration: 0.5),
    .scale(to: 1.0, duration: 0.5)
])
node.runAction(.repeatForever(pulse))
```

### SCNTransaction（隐式动画）

```swift
SCNTransaction.begin()
SCNTransaction.animationDuration = 1.0
node.position = SCNVector3(5, 0, 0)
node.opacity = 0.5
SCNTransaction.completionBlock = { print("Done") }
SCNTransaction.commit()
```

### 显式动画（Core Animation）

```swift
let animation = CABasicAnimation(keyPath: "rotation")
animation.toValue = NSValue(scnVector4: SCNVector4(0, 1, 0, Float.pi * 2))
animation.duration = 2
animation.repeatCount = .infinity
node.addAnimation(animation, forKey: "spin")
```

## 物理

### 物理体

```swift
node.physicsBody = SCNPhysicsBody(type: .dynamic, shape: nil)   // 力 + 碰撞
floor.physicsBody = SCNPhysicsBody(type: .static, shape: nil)    // 固定不动
platform.physicsBody = SCNPhysicsBody(type: .kinematic, shape: nil) // 代码驱动
```

当 `shape` 为 `nil` 时，SceneKit 从几何体中推导形状。为了提高性能，使用简化的形状：

```swift
let shape = SCNPhysicsShape(
    geometry: SCNBox(width: 1, height: 2, length: 1, chamferRadius: 0),
    options: nil
)
node.physicsBody = SCNPhysicsBody(type: .dynamic, shape: shape)
node.physicsBody?.mass = 2.0
node.physicsBody?.restitution = 0.3
```

### 施加力

```swift
node.physicsBody?.applyForce(SCNVector3(0, 10, 0), asImpulse: false) // 持续
node.physicsBody?.applyForce(SCNVector3(0, 5, 0), asImpulse: true)   // 瞬时
node.physicsBody?.applyTorque(SCNVector4(0, 1, 0, 2), asImpulse: true)
```

### 碰撞检测

```swift
struct PhysicsCategory {
    static let player:     Int = 1 << 0
    static let enemy:      Int = 1 << 1
    static let ground:     Int = 1 << 2
}

playerNode.physicsBody?.categoryBitMask = PhysicsCategory.player
playerNode.physicsBody?.collisionBitMask = PhysicsCategory.ground | PhysicsCategory.enemy
playerNode.physicsBody?.contactTestBitMask = PhysicsCategory.enemy

scene.physicsWorld.contactDelegate = self

func physicsWorld(_ world: SCNPhysicsWorld, didBegin contact: SCNPhysicsContact) {
    handleCollision(between: contact.nodeA, and: contact.nodeB)
}
```

### 重力

```swift
scene.physicsWorld.gravity = SCNVector3(0, -9.8, 0)
node.physicsBody?.isAffectedByGravity = false
```

## 粒子系统

`SCNParticleSystem` 创建火焰、烟雾、雨和火花等效果。

```swift
let particles = SCNParticleSystem()
particles.birthRate = 100
particles.particleLifeSpan = 2
particles.particleSize = 0.1
particles.particleColor = .orange
particles.emitterShape = SCNSphere(radius: 0.5)
particles.particleVelocity = 2
particles.isAffectedByGravity = true
particles.blendMode = .additive

let emitterNode = SCNNode()
emitterNode.addParticleSystem(particles)
scene.rootNode.addChildNode(emitterNode)
```

从 Xcode 粒子编辑器加载，使用
`SCNParticleSystem(named: "fire.scnp", inDirectory: nil)`。粒子可以通过 `colliderNodes` 与几何体碰撞。

## 加载模型

SceneKit 文档中指定的场景源格式是 `.scn`、`.dae` 和 `.abc`。
对于捆绑资源，将场景文件放在 `.scnassets` 文件夹中，将纹理图像放在资源库中，以便 Xcode 可以针对目标设备进行优化。

USD/USDZ 是 RealityKit 的迁移路径，而不是 SceneKit 的默认加载路径。对于新项目、重大更新或 SCN 到 USD 资产转换，转交给 RealityKit 技能。

```swift
enum SceneAssetError: Error { case missingResource, missingNode(String) }

func loadCheckedScene() throws -> SCNScene {
    guard let url = Bundle.main.url(forResource: "model", withExtension: "dae")
    else { throw SceneAssetError.missingResource }

    let scene = try SCNScene(url: url, options: [.checkConsistency: true])
    guard scene.rootNode.childNode(withName: "mesh", recursively: true) != nil
    else { throw SceneAssetError.missingNode("mesh") }
    return scene
}
```

将其作为作者/导入门：在一致性或必需节点失败时停止，修复源资产或导入选项，然后重复相同的检查。
对于生成的 `.scn` 文件，加载
[场景序列化](references/scenekit-patterns.md#scene-serialization) 并在提交之前要求导出成功和检查后的重新加载。

使用 `SCNReferenceNode` 和 `.onDemand` 加载策略加载大型模型。对于导入时的单位转换，使用 `SCNSceneSource.LoadingOption`：

```swift
let source = SCNSceneSource(url: url, options: nil)!
let scene = try source.scene(options: [.convertUnitsToMeters: 1.0])
```

不要使用 `SCNScene.Attribute.unit` 或 `UnitMetersPerUnit`。`SCNScene.Attribute`
仅是元数据：`.startTime`, `.endTime`, `.frameRate` 和 `.upAxis`。

## SwiftUI 集成

`SceneView` 将 SceneKit 嵌入 SwiftUI：

```swift
import SwiftUI
import SceneKit

struct SceneKitView: View {
    let scene: SCNScene = {
        let scene = SCNScene()
        let sphere = SCNNode(geometry: SCNSphere(radius: 1))
        sphere.geometry?.firstMaterial?.lightingModel = .physicallyBased
        sphere.geometry?.firstMaterial?.diffuse.contents = UIColor.systemBlue
        sphere.geometry?.firstMaterial?.metalness.contents = 0.8
        scene.rootNode.addChildNode(sphere)
        return scene
    }()

    var body: some View {
        SceneView(scene: scene,
                  options: [.allowsCameraControl, .autoenablesDefaultLighting])
    }
}
```

选项：`.allowsCameraControl`, `.autoenablesDefaultLighting`,
`.jitteringEnabled`, `.temporalAntialiasingEnabled`。

对于渲染循环控制，将 `SCNView` 包裹在 `UIViewRepresentable` 中，并使用 `SCNSceneRendererDelegate` 协调器。参见 [references/scenekit-patterns.md](references/scenekit-patterns.md)。

## 常见错误

### 未添加相机或灯光

```swift
// 不要：场景为空或黑色——没有相机，没有灯光
sceneView.scene = scene

// 要：添加相机 + 灯光，或使用便利标志
let cameraNode = SCNNode()
cameraNode.camera = SCNCamera()
cameraNode.position = SCNVector3(0, 5, 15)
scene.rootNode.addChildNode(cameraNode)
sceneView.pointOfView = cameraNode
sceneView.autoenablesDefaultLighting = true
```

### 使用精确几何体作为物理形状

```swift
// 不要
node.physicsBody = SCNPhysicsBody(type: .dynamic,
    shape: SCNPhysicsShape(geometry: complexMesh, options: nil))

// 要：简化基本形状
node.physicsBody = SCNPhysicsBody(type: .dynamic,
    shape: SCNPhysicsShape(
        geometry: SCNBox(width: 1, height: 2, length: 1, chamferRadius: 0),
        options: nil))
```

### 在动态体上修改变换

```swift
// 不要：重置物理模拟
dynamicNode.position = SCNVector3(5, 0, 0)

// 要：使用力/冲量
dynamicNode.physicsBody?.applyForce(SCNVector3(10, 0, 0), asImpulse: true)
```

## 审查清单

- [ ] 场景至少有一个相机节点设置为 `pointOfView`
- [ ] 场景有适当的光照（或 `autoenablesDefaultLighting` 用于原型设计）
- [ ] 物理形状使用简化几何体，而不是完整的网格细节
- [ ] `contactTestBitMask` 设置为需要碰撞回调的体
- [ ] `SCNPhysicsContactDelegate` 分配给 `scene.physicsWorld.contactDelegate`
- [ ] 动态体变换通过力/冲量更改，而不是直接位置
- [ ] 灯光限制为每个节点 8 个；对点/聚光灯设置 `attenuationEndDistance`
- [ ] 材质使用 `.physicallyBased` 光照模型以实现逼真的渲染
- [ ] SceneKit 资产使用文档中指定的 `.scn`、`.dae` 或 `.abc` 场景源格式
- [ ] 导入和导出资产在提交前通过一致性和必需节点检查
- [ ] 捆绑的 SceneKit 纹理/图像使用资源库或 Xcode 优化的资源
- [ ] 场景元数据/导入选项使用文档中指定的 API；没有虚构的 `SCNScene.Attribute.unit`
- [ ] 新的 USD/USDZ 管道或重大更新路由到 RealityKit
- [ ] Game Center 认证、排行榜、成就或多人游戏转交给 GameKit
- [ ] 使用 `SCNReferenceNode` 加载大型模型以启用懒加载
- [ ] 粒子 `birthRate` 和 `particleLifeSpan` 平衡以控制粒子数量
- [ ] `categoryBitMask` 用于将灯光和相机限制为相关节点
- [ ] SwiftUI 场景使用 `SceneView` 或 `UIViewRepresentable`-包装的 `SCNView`
- [ ] 确认弃用；评估 RealityKit 用于新项目

## 参考资料

- 参见 [references/scenekit-patterns.md](references/scenekit-patterns.md) 以获取自定义几何体、着色器修饰符、约束、变形目标、命中测试、场景序列化、渲染循环代理、性能、SpriteKit 叠加、LOD 和 Metal 着色器。
- [SceneKit 文档](https://sosumi.ai/documentation/scenekit), [SCNSceneSource](https://sosumi.ai/documentation/scenekit/scnscenesource), [SCNView](https://sosumi.ai/documentation/scenekit/scnview), [SceneView](https://sosumi.ai/documentation/scenekit/sceneview)
- [SCNPhysicsShape](https://sosumi.ai/documentation/scenekit/scnphysicsshape), [SCNShadable](https://sosumi.ai/documentation/scenekit/scnshadable)
- [WWDC 2025 会话 288：将您的 SceneKit 项目带到 RealityKit](https://sosumi.ai/videos/play/wwdc2025/288/)
