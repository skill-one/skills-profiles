# 群体编排技能

## 目的
多智能体群体协调处理复杂任务。使用分层拓扑结构并配备专业智能体，将复杂工作分解并在多个文件和模块中执行。

## 触发条件
- 3个以上文件需要修改
- 新功能实现
- 跨模块重构
- 带测试的API变更
- 与安全相关的变更
- 代码库性能优化
- 数据库模式变更

## 跳过条件
- 单文件编辑
- 简单的bug修复（1-2行）
- 文档更新
- 配置变更
- 快速探索

## 命令

### 初始化群体
使用分层拓扑结构（防止漂移）启动新的群体

```bash
npx @claude-flow/cli swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

**示例：**
```bash
npx @claude-flow/cli swarm init --topology hierarchical --max-agents 6 --strategy specialized
```

### 路由任务
根据任务类型将任务路由到适当的智能体

```bash
npx @claude-flow/cli hooks route --task "[任务描述]"
```

**示例：**
```bash
npx @claude-flow/cli hooks route --task "实现OAuth2认证流程"
```

### 生成智能体
生成特定类型的智能体

```bash
npx @claude-flow/cli agent spawn --type [类型] --name [名称]
```

**示例：**
```bash
npx @claude-flow/cli agent spawn --type coder --name impl-auth
```

### 监控状态
检查当前群体状态

```bash
npx @claude-flow/cli swarm status --verbose
```

### 编排任务
跨多个智能体编排任务

```bash
npx @claude-flow/cli task orchestrate --task "[任务]" --strategy adaptive
```

**示例：**
```bash
npx @claude-flow/cli task orchestrate --task "重构认证模块" --strategy parallel --max-agents 4
```

### 列出智能体
列出所有活跃的智能体

```bash
npx @claude-flow/cli agent list --filter active
```

## 脚本

| 脚本 | 路径 | 描述 |
|------|------|------|
| `swarm-start` | `.agents/scripts/swarm-start.sh` | 使用默认设置初始化群体 |
| `swarm-monitor` | `.agents/scripts/swarm-monitor.sh` | 实时群体监控仪表盘 |

## 参考

| 文档 | 路径 | 描述 |
|------|------|------|
| `智能体类型` | `docs/agents.md` | 智能体类型和能力的完整列表 |
| `拓扑指南` | `docs/topology.md` | 群体拓扑结构配置指南 |

## 最佳实践
1. 启动前检查现有模式的内存
2. 使用分层拓扑结构进行协调
3. 完成后存储成功的模式
4. 记录任何新的学习成果
