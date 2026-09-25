# Swift 架构

选择最小的架构，使状态所有权、依赖关系、副作用和测试显式化。默认将 SwiftUI 新功能设置为 MV；仅在观察到复杂性时才升级。

## 目录

- [作用域边界](#作用域边界)
- [决策工作流](#决策工作流)
- [模式选择](#模式选择)
- [MV 默认](#mv-默认)
- [升级信号](#升级信号)
- [迁移](#迁移)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 作用域边界

这项技能拥有模式选择、模块边界、依赖方向、迁移策略和架构级测试接口。将 SwiftUI 属性包装器路由和视图组合路由到 `swiftui-patterns`，导航 API 和路由模型路由到 `swiftui-navigation`，隔离诊断路由到 `swift-concurrency`，测试语法/固定值路由到 `swift-testing`。

## 决策工作流

1.  记录功能的状态所有者、输入、输出、依赖关系、副作用、导航交接和当前测试。
2.  识别具体压力：复杂的状态机、共享派生状态、依赖控制、功能组合、团队所有权或 UIKit 导航。
3.  选择解决该压力的最小模式；记录它添加了什么以及什么保持不变。
4.  实现一个垂直切片，具有注入的依赖关系和可观察的状态转换。
5.  运行现有行为测试加上状态转换和依赖失败测试。如果行为发生变化，则恢复固定值，修复最小的边界，然后重新运行，然后再迁移另一个切片。

## 模式选择

| 模式 | 选择时机 | 主要成本 |
|---|---|---|
| MV | SwiftUI 功能具有直接的状态和编排 | 逻辑可能在没有分解的情况下漂移到大型视图中 |
| MVVM | 呈现逻辑需要一个可独立测试的适配器 | 额外层可能变成一个转发外壳 |
| MVI | 一个功能最好被建模为显式的状态 + 意图 + 红ucer/效果 | 重复代码和集中式转换设计 |
| TCA | 许多可组合的功能需要确定的效果、依赖关系和测试 | 框架学习和架构承诺 |
| Clean Architecture | 大型产品需要在领域/数据/UI 跨越严格的依赖方向 | 协议和映射开销 |
| Coordinator | UIKit 或混合导航需要一个单独的流程所有者 | 另一个生命周期和路由所有者 |
| VIPER | 维护具有已建立 VIPER 边界的现有 UIKit 模块 | 非常高的仪式感；对新 SwiftUI 工作的不良默认值 |

当导航复杂性是压力时，与另一个状态模式一起使用 Coordinator；它不是领域/状态的架构替代品。

## MV 默认

将视图保留为状态表达式，并将业务操作放在可观察的模型和注入的服务中：

```swift
@MainActor
@Observable
final class TripStore {
    private let client: TripClient
    var trips: [Trip] = []
    var error: Error?

    init(client: TripClient) { self.client = client }

    func load() async {
        do { trips = try await client.fetchTrips() }
        catch { self.error = error }
    }
}

struct TripList: View {
    @State private var store: TripStore

    init(client: TripClient) {
        _store = State(initialValue: TripStore(client: client))
    }

    var body: some View {
        List(store.trips) { Text($0.name) }
            .task { await store.load() }
    }
}
```

加载 [架构模式配方](references/architecture-patterns.md) 以获取 MVVM、MVI、TCA、Clean Architecture、Coordinator 和 VIPER 结构。

## 升级信号

-  当必须在不渲染的情况下测试大量呈现转换并且适配器具有实际行为时，选择 MVVM。
-  当转换、无效状态和效果需要一个可审计的 reducer 类似路径时，选择 MVI。
-  当功能组合、依赖覆盖、取消和确定性的效果测试在模块之间重复出现时，选择 TCA。
-  当独立的领域规则和依赖方向在多个交付/数据层中很重要时，选择 Clean Architecture。
-  为 UIKit/混合路由所有权、深度流程组合或视图控制器外部的条件导航添加 Coordinator。
-  保持 VIPER 用于兼容的遗留模块或有意迁移；不要习惯性地用它开始新的 SwiftUI 功能。

不要仅仅因为视图很长就升级。首先提取子视图、服务和专注的可观察模型。

## 迁移

一次迁移一个功能边界：

1.  用测试和依赖关系/状态清单冻结行为。
2.  在现有操作周围引入目标边界。
3.  一次移动一个状态转换或依赖关系，同时不重新编写 UI 和持久性。
4.  在每次切片后比较行为、导航、取消、错误和持久性结果。
5.  仅在没有任何调用者或测试依赖于它之后才移除旧路径。

对于 `ObservableObject` 到 Observation 的迁移，在替换包装器之前保留相同的所有者和突变隔离。对于 MVVM 到 MV，仅在视图绑定到相同的模型/服务行为之后才删除转发视图模型成员。对于 TCA 采用，包装一个功能的状态/动作/效果，并逐步迁移依赖关系。

## 常见错误

| 错误 | 修复 |
|---|---|
| 由流行度选择的模式 | 将其与观察到的功能压力挂钩。 |
| 视图模型仅转发属性 | 删除它并使用 MV。 |
| 一个对象拥有导航、网络、格式化、持久性和 UI 状态 | 按责任和依赖方向进行拆分。 |
| 将 TCA 或 Clean Architecture 应用于琐碎的屏幕 | 从 MV 开始并保留一个升级接口。 |
| 将 Coordinator 用作状态架构 | 保持它专注于路由/生命周期所有权。 |
| 在一个功能内混合多个模式 | 定义一个本地状态/效果模型并在功能边界处迁移。 |
| 大爆炸迁移 | 移动一个测试的垂直切片并重新运行相同的证明矩阵。 |

## 审查清单

-  [ ] 选择由具体功能/团队压力证明
-  [ ] 状态所有者、突变路径、依赖关系、效果和导航所有者是显式的
-  [ ] 依赖关系在测试中是注入的和可替换的
-  [ ] 模式成本与功能复杂性成正比
-  [ ] UI 机制、导航 API、隔离和测试语法路由到兄弟技能
-  [ ] 迁移一次一个垂直切片地保留行为
-  [ ] 在每次切片后验证失败、取消、导航和持久性行为
-  [ ] 没有转发层或神对象剩余

## 参考资料

- 详细的模式结构：[references/architecture-patterns.md](references/architecture-patterns.md)
- Apple：[Observation](https://sosumi.ai/documentation/observation) · [从 ObservableObject 迁移到 Observable](https://sosumi.ai/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)
- TCA：[ComposableArchitecture](https://sosumi.ai/external/https://swiftpackageindex.com/pointfreeco/swift-composable-architecture/main/documentation/composablearchitecture)
