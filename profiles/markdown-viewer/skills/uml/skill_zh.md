# UML 图表生成器
**快速入门：** 选择图表类型 → 编写 PlantUML 文本 → 定义元素和关系 → 用 ` ```plantuml ` 分隔符包裹。
> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码分隔符。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用标准的 PlantUML 关键字：`class`、`interface`、`abstract`、`enum`、`actor`、`participant`、`component`、`node`、`database`、`package`
- 关系使用箭头语法：`-->`、`<|--`、`*--`、`o--`、`..>`、`..|>`
- 使用 `skinparam` 进行全局样式和颜色设置
- 在单个元素上使用 `#color` 设置特定颜色
- 注释使用 `note left of`、`note right of`、`note over` 或独立的 `note "text" as N`

## UML 图表类型
| 类型 | 目的 | 关键语法 | 示例 |
|------|---------|------------|---------|
| 类图 | 类结构和关系 | `class`、`interface`、`<\|--` | [class-diagram.md](examples/class-diagram.md) |
| 时序图 | 消息交互 | `participant`、`->`、`-->` | [sequence-diagram.md](examples/sequence-diagram.md) |
| 活动图 | 工作流和流程 | `start`、`:action;`、`if/else` | [activity-diagram.md](examples/activity-diagram.md) |
| 泳道活动图 | 多角色泳道活动 | `\|Lane\|`、`:action;` | [swimlane-activity-diagram.md](examples/swimlane-activity-diagram.md) |
| 状态机图 | 对象生命周期状态 | `state`、`[*] -->` | [state-machine-diagram.md](examples/state-machine-diagram.md) |
| 组件图 | 系统组件组织 | `component`、`[name]`、`interface` | [component-diagram.md](examples/component-diagram.md) |
| 用例图 | 用户-系统交互 | `actor`、`usecase`、`(name)` | [use-case-diagram.md](examples/use-case-diagram.md) |
| 部署图 | 物理部署架构 | `node`、`artifact`、`database` | [deployment-diagram.md](examples/deployment-diagram.md) |
| 对象图 | 运行时对象快照 | `object "name" as id` | [object-diagram.md](examples/object-diagram.md) |
| 包图 | 模块组织 | `package "name"` | [package-diagram.md](examples/package-diagram.md) |
| 通信图 | 对象协作 | 带序列语法的编号消息 | [communication-diagram.md](examples/communication-diagram.md) |
| 复合结构图 | 内部类结构 | 嵌套 `port` 的 `component` | [composite-structure-diagram.md](examples/composite-structure-diagram.md) |
| 交互概览图 | 活动图 + 时序图组合 | `group`、`ref over` | [interaction-overview-diagram.md](examples/interaction-overview-diagram.md) |
| 配置文件图 | UML 扩展机制 | `<<stereotype>>` 标签 | [profile-diagram.md](examples/profile-diagram.md) |

## Mxgraph Stencil 图标

draw-uml 支持 9500+ 个 mxgraph stencil 图标（AWS、Azure、Cisco、Kubernetes 等）通过 `mxgraph.*` 语法。默认颜色会自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`。

**完整 stencil 参考：** 查看 [stencils/README.md](stencils/README.md)。

### 语法

```
mxgraph.<namespace>.<icon> "Label" as <alias>
mxgraph.<namespace>.<icon> "Label" as <alias> #color
mxgraph.<namespace>.<icon> <alias>
```

- `mxgraph.<namespace>.<icon>` — stencil 形状键（例如 `mxgraph.aws4.lambda`、`mxgraph.kubernetes.pod`）
- `"Label"` — 显示文本（如果包含空格则加引号，单字不加引号）
- `as <alias>` — 关系中的标识符
- `#color` — 可选的颜色覆盖（例如 `#FF6600`、`#LightBlue`）

### 示例

```plantuml
@startuml
' 简单图标声明
mxgraph.aws4.lambda "Lambda\nFunction" as fn
mxgraph.aws4.api_gateway "API GW" as gw
mxgraph.aws4.dynamodb "DynamoDB" as db

gw --> fn
fn --> db
@enduml
```

```plantuml
@startuml
' Kubernetes 架构图标
mxgraph.kubernetes.ing "Ingress" as ing
mxgraph.kubernetes.svc "Service" as svc
mxgraph.kubernetes.pod "Pod" as pod
mxgraph.kubernetes.deploy "Deployment" as deploy

ing --> svc
svc --> pod
deploy --> pod
@enduml
```

```plantuml
@startuml
' 混合标准 UML 和 stencil 图标
node "云" {
  mxgraph.aws4.ec2 "EC2" as ec2
  mxgraph.aws4.rds "RDS" as rds
}
database "遗留数据库" as legacy

ec2 --> rds
rds --> legacy
@enduml
```
