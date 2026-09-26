# Mermaid 图表专家

## 概述

**目的**：为文档、架构可视化和流程映射创建全面的 Mermaid 图表

**类别**：技术 **主要用户**：技术文档编写者、架构验证者、产品技术专家、技术主管

## 何时使用此技能

- 创建架构文档
- 可视化工作流和流程
- 记录数据模型（ERDs）
- 解释序列流
- 创建状态机
- 记录组件关系
- 创建决策树
- 可视化用户旅程

## 前置条件

**必需的**：

- 对要记录的系统/流程的理解
- 访问技术规范
- 了解所需的图表类型

**可选的**：

- 设计系统颜色以保持一致性
- 现有文档以供参考

## 输入

**技能需要的内容**：

- 流程/系统描述
- 实体和关系（用于 ERDs）
- 组件交互（用于序列图）
- 架构层（用于 C4 图）
- 状态和转换（用于状态图）

## 工作流程

### 第 1 步：图表类型选择

**目标**：为需求选择合适的图表类型

**可用图表类型**：

1. **流程图**：决策流、算法、流程
2. **序列图**：API 交互、消息流
3. **ERD**：数据库模式、实体关系
4. **类图**：面向对象设计
5. **状态图**：状态机、生命周期
6. **甘特图**：项目时间线、日程
7. **C4 图**：不同层级的架构
8. **饼图/条形图**：数据可视化
9. **Git 图**：版本控制流
10. **用户旅程**：用户体验流

**决策矩阵**：

- 带决策的流程 → **流程图**
- API/系统交互 → **序列图**
- 数据库结构 → **ERD**
- 系统架构 → **C4 图**
- 对象关系 → **类图**
- 状态转换 → **状态图**
- 项目时间线 → **甘特图**

**验证**：

- [ ] 图表类型与内容匹配
- [ ] 复杂度适当
- [ ] 考虑了受众
- [ ] 目的明确

**输出**：选定的图表类型

### 第 2 步：流程图创建

**目标**：创建流程和决策流图表

**语法**：

```mermaid
flowchart TD
    Start([开始]) --> Input[/用户输入/]
    Input --> Validate{有效？}
    Validate -->|是| Process[处理数据]
    Validate -->|否| Error[显示错误]
    Error --> Input
    Process --> Save[(保存到数据库)]
    Save --> Success[/成功响应/]
    Success --> End([结束])
```

**节点形状**：

- `[矩形]` - 处理步骤
- `([圆角])` - 开始/结束
- `{菱形}` - 决策
- `[/平行四边形/]` - 输入/输出
- `[(数据库)]` - 数据存储
- `((圆形))` - 连接器

**方向选项**：

- `TD` - 从上到下
- `LR` - 从左到右
- `BT` - 从下到上
- `RL` - 从右到左

**示例 - 预订流程**：

```mermaid
flowchart TD
    Start([用户发起预订]) --> CheckDates[检查日期可用性]
    CheckDates --> Available{日期可用？}
    Available -->|否| ShowError[/显示不可用消息/]
    ShowError --> End([结束])
    Available -->|是| CreateBooking[创建待处理预订]
    CreateBooking --> Payment[处理付款]
    Payment --> PaymentSuccess{付款成功？}
    PaymentSuccess -->|否| CancelBooking[取消预订]
    CancelBooking --> ShowError
    PaymentSuccess -->|是| ConfirmBooking[确认预订]
    ConfirmBooking --> SendEmail[/发送确认邮件/]
    SendEmail --> SaveDB[(保存到数据库)]
    SaveDB --> Success[/显示成功/]
    Success --> End
```

**验证**：

- [ ] 所有路径都覆盖
- [ ] 决策点清晰
- [ ] 开始和结束定义
- [ ] 流向逻辑

**输出**：流程流程图

### 第 3 步：序列图创建

**目标**：记录 API 交互和消息流

**语法**：

```mermaid
sequenceDiagram
    actor 用户
    participant 前端
    participant API
    participant 数据库
    participant 付款

    用户->>前端: 点击"预订"
    前端->>API: POST /api/bookings
    API->>数据库: 检查可用性
    数据库-->>API: 可用
    API->>付款: 处理付款
    付款-->>API: 付款成功
    API->>数据库: 创建预订
    数据库-->>API: 预订已创建
    API-->>前端: 201 已创建
    前端-->>用户: 显示确认
```

**参与者类型**：

- `actor` - 人类用户
- `participant` - 系统/服务
- `database` - 数据库

**箭头类型**：

- `->` - 实线（同步）
- `-->` - 虚线（响应）
- `->>` - 实线箭头（异步消息）
- `-->>` - 虚线箭头（异步响应）

**示例 - 身份验证流程**：

```mermaid
sequenceDiagram
    actor 用户
    participant 前端
    participant API
    participant Clerk
    participant 数据库

    用户->>前端: 输入凭证
    前端->>Clerk: 登录请求
    Clerk->>Clerk: 验证凭证
    alt 凭证有效
        Clerk-->>前端: JWT 令牌
        前端->>API: 带令牌请求
        API->>Clerk: 验证令牌
        Clerk-->>API: 令牌有效
        API->>数据库: 获取用户数据
        数据库-->>API: 用户数据
        API-->>前端: 用户会话
        前端-->>用户: 已登录
    else 凭证无效
        Clerk-->>前端: 身份验证错误
        前端-->>用户: 显示错误
    end
```

**验证**：

- [ ] 所有参与者已识别
- [ ] 消息流逻辑
- [ ] 返回消息显示
- [ ] Alt/循环块使用正确

**输出**：序列图

### 第 4 步：ERD 创建

**目标**：记录数据库模式和关系

**语法**：

```mermaid
erDiagram
    USER ||--o{ BOOKING : 创建
    ACCOMMODATION ||--o{ BOOKING : "预订"
    USER {
        uuid id PK
        string email UK
        string name
        timestamp created_at
    }
    BOOKING {
        uuid id PK
        uuid user_id FK
        uuid accommodation_id FK
        date check_in
        date check_out
        enum status
    }
    ACCOMMODATION {
        uuid id PK
        string name
        text description
        decimal price_per_night
    }
```

**关系类型**：

- `||--||` - 一对一
- `||--o{` - 一对多
- `}o--o{` - 多对多
- `||--o|` - 一对零或一个

**基数符号**：

- `||` - 恰好一个
- `o|` - 零或一个
- `}o` - 零或更多
- `}|` - 一个或更多

**示例 - 完整 Hospeda ERD**：

```mermaid
erDiagram
    USER ||--o{ BOOKING : 创建
    USER ||--o{ REVIEW : 撰写
    USER ||--o{ ACCOMMODATION : 拥有
    ACCOMMODATION ||--o{ BOOKING : "有预订"
    ACCOMMODATION ||--o{ REVIEW : "有评价"
    ACCOMMODATION }o--o{ AMENITY : 包括
    BOOKING ||--|| PAYMENT : "有付款"

    USER {
        uuid id PK
        string clerk_id UK
        string email UK
        string name
        enum role
        timestamp created_at
    }

    ACCOMMODATION {
        uuid id PK
        uuid owner_id FK
        string name
        text description
        decimal price_per_night
        int max_guests
        enum status
    }

    BOOKING {
        uuid id PK
        uuid user_id FK
        uuid accommodation_id FK
        date check_in
        date check_out
        int guests
        enum status
        decimal total_price
    }

    REVIEW {
        uuid id PK
        uuid user_id FK
        uuid accommodation_id FK
        int rating
        text comment
        timestamp created_at
    }

    PAYMENT {
        uuid id PK
        uuid booking_id FK
        string mercadopago_id UK
        decimal amount
        enum status
        timestamp processed_at
    }

    AMENITY {
        uuid id PK
        string name
        string icon
    }
```

**验证**：

- [ ] 所有实体已定义
- [ ] 关系准确
- [ ] 基数正确
- [ ] 主键/外键标记

**输出**：ERD 图表

### 第 5 步：C4 架构图表

**目标**：记录不同层级的系统架构

**上下文层**（系统在环境中）：

```mermaid
C4Context
    title 系统上下文 - Hospeda 平台

    Person(guest, "访客", "旅游者寻找住宿")
    Person(owner, "所有者", "住宿所有者")
    System(hospeda, "Hospeda 平台", "旅游预订平台")

    System_Ext(clerk, "Clerk", "身份验证提供者")
    System_Ext(mercadopago, "Mercado Pago", "付款处理者")
    System_Ext(email, "邮件服务", "交易邮件")

    Rel(guest, hospeda, "搜索和预订", "HTTPS")
    Rel(owner, hospeda, "管理房源", "HTTPS")
    Rel(hospeda, clerk, "验证用户", "API")
    Rel(hospeda, mercadopago, "处理付款", "API")
    Rel(hospeda, email, "发送通知", "SMTP")
```

**容器层**（应用程序和数据存储）：

```mermaid
C4Container
    title 容器 - Hospeda 平台

    Person(user, "用户")

    Container(web, "Web 应用", "Astro + React", "面向公众的网站")
    Container(admin, "管理面板", "TanStack Start", "管理界面")
    Container(api, "API", "Hono", "后端服务")
    ContainerDb(db, "数据库", "PostgreSQL", "存储所有数据")

    Rel(user, web, "使用", "HTTPS")
    Rel(user, admin, "管理", "HTTPS")
    Rel(web, api, "调用", "JSON/HTTPS")
    Rel(admin, api, "调用", "JSON/HTTPS")
    Rel(api, db, "读取/写入", "SQL")
```

**组件层**（内部结构）：

```mermaid
C4Component
    title 组件 - API 应用

    Container(api, "API", "Hono")

    Component(routes, "路由", "Hono 路由器", "HTTP 端点")
    Component(services, "服务", "业务逻辑", "领域操作")
    Component(models, "模型", "数据访问", "数据库操作")
    Component(middleware, "中间件", "跨切面", "身份验证、日志记录、错误处理")

    Rel(routes, middleware, "使用")
    Rel(routes, services, "调用")
    Rel(services, models, "使用")
    Rel(models, db, "查询")
```

**验证**：

- [ ] 选择了合适的层级
- [ ] 所有系统/容器显示
- [ ] 关系清晰
- [ ] 识别了外部系统

**输出**：C4 架构图表

### 第 6 步：状态图创建

**目标**：记录状态机和生命周期

**语法**：

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Confirmed : 付款成功
    Pending --> Cancelled : 付款失败
    Pending --> Cancelled : 用户取消
    Confirmed --> CheckedIn : 入住日期
    Confirmed --> Cancelled : 取消请求
    CheckedIn --> CheckedOut : 退房日期
    CheckedOut --> Reviewed : 用户提交评价
    CheckedOut --> [*] : 30 天已过
    Reviewed --> [*]
    Cancelled --> [*]
```

**示例 - 预订生命周期**：

```mermaid
stateDiagram-v2
    [*] --> Draft : 创建预订

    state "待付款" as Pending
    state "付款处理中" as Processing

    Draft --> Pending : 提交预订
    Pending --> Processing : 启动付款

    Processing --> Confirmed : 付款批准
    Processing --> PaymentFailed : 付款被拒

    PaymentFailed --> Pending : 重试付款
    PaymentFailed --> Cancelled : 最大重试次数

    Confirmed --> Active : 到达入住日期
    Active --> Completed : 到达退房日期

    Confirmed --> CancelRequested : 取消请求
    CancelRequested --> RefundProcessing : 批准取消
    RefundProcessing --> Cancelled : 退款完成

    Completed --> [*]
    Cancelled --> [*]

    note right of Confirmed
        所有者通知
        日历锁定
    end note

    note right of Completed
        请求评价
        付款释放
    end note
```

**验证**：

- [ ] 所有状态定义
- [ ] 转换逻辑
- [ ] 开始/结束状态标记
- [ ] 注释解释关键状态

**输出**：状态图

### 第 7 步：样式和定制

**目标**：对图表应用一致的样式

**主题应用**：

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#3B82F6',
  'primaryTextColor':'#fff',
  'primaryBorderColor':'#2563EB',
  'lineColor':'#6B7280',
  'secondaryColor':'#10B981',
  'tertiaryColor':'#F59E0B'
}}}%%
flowchart TD
    A[开始] --> B[处理]
    B --> C[结束]
```

**类样式**：

```mermaid
flowchart TD
    A[普通] --> B[成功]
    B --> C[错误]

    classDef successClass fill:#10B981,stroke:#059669,color:#fff
    classDef errorClass fill:#EF4444,stroke:#DC2626,color:#fff

    class B successClass
    class C errorClass
```

**验证**：

- [ ] 颜色与品牌匹配
- [ ] 对比度足够
- [ ] 样式一致
- [ ] 在两种主题中都可读

**输出**：样式图表

## 输出

**产生**：

- Mermaid 图表代码（Markdown 格式）
- 多种图表类型（按需）
- 样式和主题图表
- 文档化就绪的可视化

**成功标准**：

- 图表准确表示系统
- 所有元素正确标记
- 关系清晰且正确
- 样式与品牌一致
- 在 Markdown 中正确渲染

## 最佳实践

1. **简洁性**：保持图表专注且不杂乱
2. **标签**：所有元素都有清晰、描述性的标签
3. **方向**：保持一致的流向（通常从上到下或从左到右）
4. **分组**：使用子图将相关元素分组
5. **颜色**：使用颜色突出显示重要元素
6. **注释**：添加注释以解释复杂逻辑
7. **层级**：为受众选择适当的抽象层级
8. **更新**：保持图表与代码同步
9. **注释**：在 mermaid 代码中添加注释以保持可维护性
10. **测试**：在目标平台上验证图表渲染

## 常见模式

### API 请求流

```mermaid
sequenceDiagram
    Client->>+API: GET /resource
    API->>+Service: fetchResource()
    Service->>+Model: findById()
    Model->>+DB: SELECT 查询
    DB-->>-Model: 行数据
    Model-->>-Service: 实体
    Service-->>-API: DTO
    API-->>-Client: JSON 响应
```

### 错误处理流

```mermaid
flowchart TD
    Request[请求] --> Validate{有效？}
    Validate -->|否| ValidationError[验证错误]
    ValidationError --> ErrorHandler[错误处理程序]
    Validate -->|是| Process[处理请求]
    Process --> DB{数据库成功？}
    DB -->|否| DBError[数据库错误]
    DBError --> ErrorHandler
    DB -->|是| Success[成功响应]
    ErrorHandler --> LogError[记录错误]
    LogError --> ErrorResponse[错误响应]
```

## 备注

- Mermaid 在 GitHub、GitLab、Notion 和大多数 Markdown 查看器中渲染
- 实时编辑器可在 mermaid.live 上使用
- 最大复杂度：保持少于 20 个节点以保持可读性
- 使用子图对相关节点进行分组
- 在提交前在目标平台上测试渲染
- 将图表源保持在 Markdown 文件中，而不是图像
- 使用代码进行图表版本控制
- 在代码审查期间更新图表
