---
name: diagram-creator
description: 使用 Mermaid、PlantUML 等基于文本的图表工具创建专业图表。生成流程图、时序图、架构图等。
---

# 图表创建技能

## 概述

我帮助你使用基于文本的图表工具（如Mermaid和PlantUML）创建专业图表。这些图表可以在文档、演示文稿和开发工具中渲染。

**我能做什么：**
- 创建流程图和流程图
- 生成时序图
- 构建架构和系统图
- 设计ER（实体关系）图
- 创建类图和UML
- 生成组织结构图
- 构建甘特图和时间线

**我不能做什么：**
- 直接渲染图像（使用Mermaid在线编辑器或类似工具）
- 创建像素级精确的定制设计
- 生成光栅图像

---

## 如何使用我

### 第一步：描述你的图表

告诉我：
- 要可视化的流程/系统/概念
- 需要的图表类型
- 详细程度
- 目标受众

### 第二步：选择格式

- **Mermaid**：最适合网页、Markdown、GitHub
- **PlantUML**：最适合UML、复杂图表
- **ASCII**：简单、通用兼容性
- **D2**：现代、时尚图表

### 第三步：指定样式

- 颜色和主题
- 方向（自上而下、自左而右）
- 详细程度

---

## 图表类型

### 1. 流程图 / 流程图

**用于**：业务流程、决策树、工作流

```mermaid
flowchart TD
    A[开始] --> B{决策？}
    B -->|是| C[操作1]
    B -->|否| D[操作2]
    C --> E[结束]
    D --> E
```

### 2. 时序图

**用于**：API调用、用户交互、系统通信

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as 应用
    participant S as 服务器
    participant D as 数据库
    
    U->>A: 点击登录
    A->>S: POST /auth/login
    S->>D: 查询用户
    D-->>S: 用户数据
    S-->>A: JWT令牌
    A-->>U: 重定向到仪表盘
```

### 3. 架构图

**用于**：系统设计、基础设施、组件关系

```mermaid
flowchart TB
    subgraph 客户端
        A[Web应用]
        B[移动应用]
    end
    
    subgraph 后端
        C[API网关]
        D[认证服务]
        E[用户服务]
        F[订单服务]
    end
    
    subgraph 数据
        G[(PostgreSQL)]
        H[(Redis)]
        I[(S3)]
    end
    
    A & B --> C
    C --> D & E & F
    D --> H
    E --> G
    F --> G & I
```

### 4. 实体关系图

**用于**：数据库设计、数据模型

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : 下单
    ORDER ||--|{ LINE_ITEM : 包含
    PRODUCT ||--o{ LINE_ITEM : "订购"
    
    CUSTOMER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        date created_at
        int customer_id FK
    }
    PRODUCT {
        int id PK
        string name
        decimal price
    }
```

### 5. 类图

**用于**：面向对象设计、代码结构

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +boolean 室内
        +meow()
    }
    
    Animal <|-- Dog
    Animal <|-- Cat
```

### 6. 状态图

**用于**：状态机、状态工作流

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: 提交
    Submitted --> InReview: 指派审阅者
    InReview --> Approved: 批准
    InReview --> Rejected: 拒绝
    Rejected --> Draft: 修改
    Approved --> [*]
```

### 7. 甘特图

**用于**：项目时间线、日程安排

```mermaid
gantt
    title 项目时间线
    dateFormat  YYYY-MM-DD
    
    section 规划
    Requirements    :a1, 2024-01-01, 14d
    Design          :a2, after a1, 21d
    
    section 开发
    Backend         :b1, after a2, 30d
    Frontend        :b2, after a2, 30d
    
    section 测试
    QA Testing      :c1, after b1, 14d
    UAT             :c2, after c1, 7d
```

### 8. 思维导图

**用于**：头脑风暴、概念组织

```mermaid
mindmap
    root((项目))
        功能
            功能A
            功能B
            功能C
        团队
            前端
            后端
            设计
        时间线
            Q1
            Q2
            Q3
```

### 9. Git图

**用于**：分支可视化、Git工作流

```mermaid
gitGraph
    commit
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
```

---

## 输出格式

```markdown
# 图表：[名称]

**类型**：[流程图 / 时序图 / 架构图 / 等.]
**工具**：[Mermaid / PlantUML]
**目的**：[说明内容]

---

## 图表代码

### Mermaid

```mermaid
[Mermaid代码]
```

### PlantUML（替代方案）

```plantuml
[PlantUML代码]
```

---

## 渲染说明

1. **Mermaid在线编辑器**：https://mermaid.live/
2. **GitHub**：直接粘贴到Markdown文件中
3. **VS Code**：安装Mermaid扩展
4. **Notion**：使用mermaid类型的代码块

---

## 定制选项

### 颜色主题
添加到开头：
```
%%{init: {'theme':'forest'}}%%
```

可用主题：default、forest、dark、neutral

### 方向
- TB（自上而下）
- BT（自下而上）
- LR（自左而右）
- RL（自右而左）

---

## 注意事项

- [关于图表的任何备注]
- [做出的假设]
```

---

## PlantUML示例

### 时序图
```plantuml
@startuml
actor 用户
participant "Web应用" as 应用
participant "API服务器" as API
database "数据库" as DB

用户 -> 应用: 登录请求
应用 -> API: POST /auth/login
API -> DB: SELECT用户
DB --> API: 用户记录
API --> 应用: JWT令牌
应用 --> 用户: 重定向到仪表盘
@enduml
```

### 组件图
```plantuml
@startuml
package "前端" {
    [React应用]
    [移动应用]
}

package "后端" {
    [API网关]
    [认证服务]
    [用户服务]
}

数据库 "PostgreSQL" as DB

[React应用] --> [API网关]
[移动应用] --> [API网关]
[API网关] --> [认证服务]
[API网关] --> [用户服务]
[用户服务] --> DB
@enduml
```

---

## 创建更好图表的技巧

1. **保持简洁** - 不要过度拥挤
2. **使用一致的命名** - 清晰、描述性标签
3. **分组相关项** - 使用子图/包
4. **选择合适的类型** - 使图表与概念匹配
5. **考虑受众** - 技术型 vs. 商业型
6. **谨慎使用颜色** - 仅用于强调
7. **添加图例** - 当使用符号/颜色时
8. **保持层次结构** - 自上而下或自左而右的流程

---

## 渲染工具

| 工具 | URL | 最适合 |
|------|-----|----------|
| Mermaid在线 | mermaid.live | 快速编辑 |
| PlantUML服务器 | plantuml.com | PlantUML渲染 |
| Draw.io | draw.io | 手动编辑 |
| Excalidraw | excalidraw.com | 手绘风格 |
| Lucidchart | lucidchart.com | 专业图表 |

---

## 限制

- 无法直接渲染图像
- 复杂布局可能需要手动调整
- 与设计工具相比，样式有限
- 部分图表类型在所有工具中都不支持

---

*由Claude办公技能社区构建。欢迎贡献！*
