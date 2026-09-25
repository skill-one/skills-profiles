# C4 架构文档

使用 C4 模型图表和 Mermaid 语法生成软件架构文档。

## 工作流程

1. **理解范围** - 根据受众确定需要哪些 C4 层级
2. **分析代码库** - 探索系统以识别组件、容器和关系
3. **生成图表** - 在适当的抽象层级创建 Mermaid C4 图表
4. **文档化** - 将图表写入 markdown 文件并添加解释性上下文

## C4 图表层级

根据文档需求选择适当的层级：

| 层级 | 图表类型 | 受众 | 展示内容 | 创建时机 |
|------|----------|------|----------|----------|
| 1 | **C4Context** | 所有人员 | 系统 + 外部参与者 | 总是（必需） |
| 2 | **C4Container** | 技术人员 | 应用、数据库、服务 | 总是（必需） |
| 3 | **C4Component** | 开发人员 | 内部组件 | 仅当增加价值时 |
| 4 | **C4Deployment** | DevOps | 基础设施节点 | 用于生产系统 |
| - | **C4Dynamic** | 技术人员 | 请求流程（编号） | 用于复杂工作流 |

**关键洞察**："上下文 + 容器图表对大多数软件开发团队来说就足够了。" 仅在确实增加价值时才创建组件/代码图表。

## 快速入门示例

### 系统上下文（层级 1）
```mermaid
C4Context
  title 系统上下文 - Workout Tracker

  Person(user, "用户", "跟踪锻炼和练习")
  System(app, "Workout Tracker", "用于跟踪力量和 CrossFit 锻炼的 Vue PWA")
  System_Ext(browser, "Web 浏览器", "将数据存储在 IndexedDB")

  Rel(user, app, "使用")
  Rel(app, browser, "持久化数据到", "IndexedDB")
```

### 容器图表（层级 2）
```mermaid
C4Container
  title 容器图表 - Workout Tracker

  Person(user, "用户", "跟踪锻炼")

  Container_Boundary(app, "Workout Tracker PWA") {
    Container(spa, "SPA", "Vue 3, TypeScript", "单页应用程序")
    Container(pinia, "状态管理", "Pinia", "管理应用程序状态")
    ContainerDb(indexeddb, "IndexedDB", "Dexie", "本地锻炼存储")
  }

  Rel(user, spa, "使用")
  Rel(spa, pinia, "读取/写入状态")
  Rel(pinia, indexeddb, "持久化", "Dexie ORM")
```

### 组件图表（层级 3）
```mermaid
C4Component
  title 组件图表 - Workout 功能

  Container(views, "视图", "Vue Router 页面")

  Container_Boundary(workout, "Workout 功能") {
    Component(useWorkout, "useWorkout", "Composable", "锻炼执行状态")
    Component(useTimer, "useTimer", "Composable", "计时器状态机")
    Component(workoutRepo, "WorkoutRepository", "Dexie", "锻炼持久化")
  }

  Rel(views, useWorkout, "使用")
  Rel(useWorkout, useTimer, "控制")
  Rel(useWorkout, workoutRepo, "保存到")
```

### 动态图表（请求流程）
```mermaid
C4Dynamic
  title 动态图表 - 用户登录流程

  ContainerDb(db, "数据库", "PostgreSQL", "用户凭证")
  Container(spa, "单页应用程序", "React", "银行界面")

  Container_Boundary(api, "API 应用") {
    Component(signIn, "登录控制器", "Express", "认证端点")
    Component(security, "安全服务", "JWT", "验证凭证")
  }

  Rel(spa, signIn, "1. 提交凭证", "JSON/HTTPS")
  Rel(signIn, security, "2. 验证")
  Rel(security, db, "3. 查询用户", "SQL")

  UpdateRelStyle(spa, signIn, $textColor="blue", $offsetY="-30")
```

### 部署图表
```mermaid
C4Deployment
  title 部署图表 - 生产环境

  Deployment_Node(browser, "客户浏览器", "Chrome/Firefox") {
    Container(spa, "SPA", "React", "Web 应用")
  }

  Deployment_Node(aws, "AWS 云", "us-east-1") {
    Deployment_Node(ecs, "ECS 集群", "Fargate") {
      Container(api, "API 服务", "Node.js", "REST API")
    }
    Deployment_Node(rds, "RDS", "db.r5.large") {
      ContainerDb(db, "数据库", "PostgreSQL", "应用数据")
    }
  }

  Rel(spa, api, "API 调用", "HTTPS")
  Rel(api, db, "读取/写入", "JDBC")
```

## 元素语法

### 人物和系统
```
Person(alias, "标签", "描述")
Person_Ext(alias, "标签", "描述")       # 外部人物
System(alias, "标签", "描述")
System_Ext(alias, "标签", "描述")       # 外部系统
SystemDb(alias, "标签", "描述")         # 数据库系统
SystemQueue(alias, "标签", "描述")      # 队列系统
```

### 容器
```
Container(alias, "标签", "技术", "描述")
Container_Ext(alias, "标签", "技术", "描述")
ContainerDb(alias, "标签", "技术", "描述")
ContainerQueue(alias, "标签", "技术", "描述")
```

### 组件
```
Component(alias, "标签", "技术", "描述")
Component_Ext(alias, "标签", "技术", "描述")
ComponentDb(alias, "标签", "技术", "描述")
```

### 边界
```
Enterprise_Boundary(alias, "标签") { ... }
System_Boundary(alias, "标签") { ... }
Container_Boundary(alias, "标签") { ... }
Boundary(alias, "标签", "类型") { ... }
```

### 关系
```
Rel(from, to, "标签")
Rel(from, to, "标签", "技术")
BiRel(from, to, "标签")                        # 双向
Rel_U(from, to, "标签")                        # 向上
Rel_D(from, to, "标签")                        # 向下
Rel_L(from, to, "标签")                        # 向左
Rel_R(from, to, "标签")                        # 向右
```

### 部署节点
```
Deployment_Node(alias, "标签", "类型", "描述") { ... }
Node(alias, "标签", "类型", "描述") { ... }  # 简写
```

## 样式和布局

### 布局配置
```
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```
- `$c4ShapeInRow` - 每行形状数量（默认：4）
- `$c4BoundaryInRow` - 每行边界数量（默认：2）

### 元素样式
```
UpdateElementStyle(alias, $fontColor="red", $bgColor="grey", $borderColor="red")
```

### 关系样式
```
UpdateRelStyle(from, to, $textColor="blue", $lineColor="blue", $offsetX="5", $offsetY="-10")
```
使用 `$offsetX` 和 `$offsetY` 来修复重叠的关系标签。

## 最佳实践

### 基本规则

1. **每个元素必须有**：名称、类型、技术（适用时）和描述
2. **仅使用单向箭头** - 双向箭头会制造歧义
3. **用动作动词标记箭头** - "使用电子邮件", "从读取", 而不是仅仅 "使用"
4. **包含技术标签** - "JSON/HTTPS", "JDBC", "gRPC"
5. **每张图表不超过 20 个元素** - 将复杂系统拆分为多个图表

### 清晰指南

1. **从层级 1 开始** - 上下文图表有助于框定系统范围
2. **每个文件一个图表** - 保持图表专注于单一抽象层级
3. **有意义的别名** - 使用描述性别名（例如 `orderService` 而不是 `s1`）
4. **简洁的描述** - 尽可能将描述保持在 50 个字符以内
5. **始终包含标题** - "系统上下文图表 - [系统名称]"

### 需要避免的事项

参见 [references/common-mistakes.md](references/common-mistakes.md) 获取详细的反模式：
- 混淆可部署的容器与不可部署的组件
- 将共享库建模为容器
- 将消息代理显示为单个容器而不是单独的主题
- 添加未定义的抽象层级，如 "子组件"
- 删除类型标签以 "简化" 图表

## 微服务指南

### 单个团队所有权
将每个微服务建模为容器（或容器组）：
```mermaid
C4Container
  title 微服务 - 单个团队

  System_Boundary(platform, "电子商务平台") {
    Container(orderApi, "订单服务", "Spring Boot", "订单处理")
    ContainerDb(orderDb, "订单数据库", "PostgreSQL", "订单数据")
    Container(inventoryApi, "库存服务", "Node.js", "库存管理")
    ContainerDb(inventoryDb, "库存数据库", "MongoDB", "库存数据")
  }
```

### 多个团队所有权
当由不同团队拥有时，将微服务提升为软件系统：
```mermaid
C4Context
  title 微服务 - 多个团队

  Person(customer, "客户", "下订单")
  System(orderSystem, "订单系统", "Alpha 团队")
  System(inventorySystem, "库存系统", "Beta 团队")
  System(paymentSystem, "支付系统", "Gamma 团队")

  Rel(customer, orderSystem, "下订单")
  Rel(orderSystem, inventorySystem, "检查库存")
  Rel(orderSystem, paymentSystem, "处理支付")
```

### 事件驱动架构
将单个主题/队列显示为容器，而不是一个 "Kafka" 盒子：
```mermaid
C4Container
  title 事件驱动架构

  Container(orderService, "订单服务", "Java", "创建订单")
  Container(stockService, "库存服务", "Java", "管理库存")
  ContainerQueue(orderTopic, "order.created", "Kafka", "订单事件")
  ContainerQueue(stockTopic, "stock.reserved", "Kafka", "库存事件")

  Rel(orderService, orderTopic, "发布到")
  Rel(stockService, orderTopic, "订阅")
  Rel(stockService, stockTopic, "发布到")
  Rel(orderService, stockTopic, "订阅到")
```

## 输出位置

将架构文档写入 `docs/architecture/`，命名规范：
- `c4-context.md` - 系统上下文图表
- `c4-containers.md` - 容器图表
- `c4-components-{feature}.md` - 按功能划分的组件图表
- `c4-deployment.md` - 部署图表
- `c4-dynamic-{flow}.md` - 特定流程的动态图表

## 面向受众的细节

| 受众 | 推荐图表 |
|------|----------|
| 高管 | 仅上下文图表 |
| 产品经理 | 上下文 + 容器 |
| 架构师 | 上下文 + 容器 + 关键组件 |
| 开发人员 | 根据需要使用所有层级 |
| DevOps | 容器 + 部署 |

## 参考文献

- [references/c4-syntax.md](references/c4-syntax.md) - 完整的 Mermaid C4 语法
- [references/common-mistakes.md](references/common-mistakes.md) - 避免的反模式
- [references/advanced-patterns.md](references/advanced-patterns.md) - 微服务、事件驱动、部署
