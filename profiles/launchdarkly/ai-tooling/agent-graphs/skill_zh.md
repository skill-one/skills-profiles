# 配置代理图

您正在使用一个技能，它将指导您在 LaunchDarkly 中创建和管理代理图。您的工作是设计图拓扑结构，使用正确的边和转接创建它，并验证配置节点之间的路由。

## 前置条件

此技能要求您的环境中配置了远程托管的 LaunchDarkly MCP 服务器。

**必需的 MCP 工具：**
- `create-agent-graph` -- 使用节点和边创建新图
- `get-agent-graph` -- 检查图的结构和边
- `list-agent-graphs` -- 浏览项目中的现有图

**可选的 MCP 工具：**
- `update-agent-graph` -- 修改边、根配置或描述
- `delete-agent-graph` -- 永久删除图
- `get-ai-config` -- 检查作为节点的单个配置
- `create-ai-config` -- 创建新的配置以用作图节点

## 核心概念

### 什么是代理图？

代理图是一个有向图，其中：
- **节点** 是配置（每个配置都是一个代理，具有自己的模型、提示和工具）
- **边** 定义配置之间的路由（源 -> 目标）
- **转接数据** 在边上控制代理之间如何传递上下文
- **根配置** 是入口点——第一个接收用户输入的代理

### 何时使用代理图

| 场景 | 示例 |
|------|------|
| **多步骤工作流** | 筛选代理 -> 专家代理 -> 摘要代理 |
| **按意图路由** | 路由代理决定哪个专家处理请求 |
| **升级链** | L1 支持 -> L2 支持 -> 人工转接 |
| **管道处理** | 提取 -> 转换 -> 验证 -> 存储 |

### 图结构

```
[根配置] --边--> [配置 A] --边--> [配置 C]
            \--边--> [配置 B]
```

每条边具有：
- `key` -- 边的唯一标识符
- `sourceConfig` -- 路由的配置键（从...）
- `targetConfig` -- 路由的配置键（到...）
- `handoff` (可选) -- 在过渡期间传递的数据/指令

## 核心原则

1. **先设计后构建**：先在纸板/白板上绘制节点和边
2. **一个代理一个任务**：每个节点应有明确、专注的责任
3. **根配置是路由器**：入口点应了解如何分派
4. **转接数据很重要**：定义代理之间流动的上下文
5. **验证完整路径**：测试端到端的路由是否正常

## 工作流程

### 第 1 步：设计图

在创建任何东西之前：

1. 确定需要的代理（配置）——每个都是图节点
2. 绘制路由：哪个代理转接到哪个？
3. 定义转接数据：每条边携带什么上下文？
4. 确定根配置：哪个代理接收初始输入？
5. 使用 `list-agent-graphs` 检查现有图，避免重复
6. 使用 `get-ai-config` 检查现有配置，查看哪些节点已存在

### 第 2 步：确保节点存在

图中的每个节点必须是现有配置。如果配置尚不存在：
1. 使用 `create-ai-config` 创建每个代理配置
2. 为每个代理角色设置适当的模型和提示
3. 使用 `get-ai-config` 验证每个配置是否存在

### 第 3 步：创建图

使用 `create-agent-graph` 并提供：
- `projectKey` -- 包含配置的项目
- `key` -- 图的唯一标识符
- `name` -- 人类可读的显示名称
- `description` (可选) -- 解释图的目的
- `rootConfigKey` -- 入口点配置键
- `edges` -- 配置之间连接的数组

```json
{
  "projectKey": "my-project",
  "key": "support-triage-graph",
  "name": "Customer Support Triage",
  "description": "将客户查询路由到适当的专家代理",
  "rootConfigKey": "triage-agent",
  "edges": [
    {
      "key": "triage-to-billing",
      "sourceConfig": "triage-agent",
      "targetConfig": "billing-specialist",
      "handoff": {"category": "billing", "priority": "normal"}
    },
    {
      "key": "triage-to-technical",
      "sourceConfig": "triage-agent",
      "targetConfig": "technical-specialist",
      "handoff": {"category": "technical", "priority": "normal"}
    }
  ]
}
```

### 第 4 步：验证

1. 使用 `get-agent-graph` 确认图已按正确结构创建
2. 验证边连接了正确的源和目标配置
3. 检查根配置键是否与预期的入口点匹配
4. 确认需要在边上的转接数据是否存在

**报告结果：**
- 图创建，包含 N 个节点和 M 条边
- 根配置设置正确
- 所有边已验证

## 边缘情况

| 情况 | 操作 |
|------|------|
| 配置尚不存在 | 在引用它之前，先使用 `create-ai-config` 创建它 |
| 循环路由 | 允许但警告用户——确保代理逻辑中存在终止条件 |
| 单节点图 | 有效但罕见——考虑是否真的需要图 |
| 更新边 | 使用 `update-agent-graph` —— 提供完整的新边列表 |

## 不要做的事情

- 在配置节点存在之前不要创建图
- 当代理需要从前置代理获取上下文时不要忘记转接数据
- 不要创建过于复杂的图——从简单开始，按需添加节点
- 在不了解图是否在代理工作流中活跃使用的情况下不要删除图

## 其他资源

要了解更多信息，请阅读 [代理图](https://launchdarkly.com/docs/home/agentcontrol/agent-graphs.md)。
