# 架构图

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

使用基于代码的绘图工具（如 Mermaid 和 PlantUML）创建清晰、可维护的架构图，用于系统设计、数据流和技术文档。

## 使用场景

- 系统架构文档
- C4 模型图
- 数据流图
- 序列图
- 组件关系
- 部署图
- 基础设施架构
- 微服务架构
- 数据库模式（可视化）
- 集成模式

## 快速入门

最小工作示例：

```mermaid
graph TB
    subgraph "客户端层"
        Web[Web 应用]
        Mobile[移动应用]
        CLI[命令行工具]
    end

    subgraph "API 网关层"
        Gateway[API 网关<br/>速率限制<br/>认证]
    end

    subgraph "服务层"
        Auth[认证服务]
        User[用户服务]
        Order[订单服务]
        Payment[支付服务]
        Notification[通知服务]
    end

    subgraph "数据层"
        UserDB[(用户数据库<br/>PostgreSQL)]
        OrderDB[(订单数据库<br/>PostgreSQL)]
        Cache[(Redis 缓存)]
        Queue[消息队列<br/>RabbitMQ]
    end
// ... (参考指南查看完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [系统架构图](references/system-architecture-diagram.md) | 系统架构图 |
| [序列图](references/sequence-diagram.md) | 序列图 |
| [C4 上下文图](references/c4-context-diagram.md) | C4 上下文图 |
| [组件图](references/component-diagram.md) | 组件图 |
| [部署图](references/deployment-diagram.md) | 部署图 |
| [数据流图](references/data-flow-diagram.md) | 数据流图 |
| [类图](references/class-diagram.md) | 类图 |
| [组件图](references/component-diagram-2.md) | 组件图 |
| [部署图](references/deployment-diagram-2.md) | 部署图 |

## 最佳实践

### ✅ 应该做

- 使用一致的符号和标记
- 复杂图包含图例
- 保持图专注于一个方面
- 有意义地使用颜色编码
- 包含标题和描述
- 对图进行版本控制
- 使用文本格式（Mermaid, PlantUML）
- 清晰显示数据流方向
- 包含部署细节
- 记录图例约定
- 保持图与代码同步
- 使用子图进行逻辑分组

### ❌ 不应该做

- 图表过度填充细节
- 使用不一致的样式
- 跳过图例
- 仅创建二进制图像文件
- 忘记记录关系
- 在一个图中混合抽象级别
- 使用专有格式
