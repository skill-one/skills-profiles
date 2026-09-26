# 工作流自动化技能

## 目的
为复杂的多步骤流程创建和执行自动化工作流。

## 触发时机
- 多步骤自动化流程
- 可复用工作流的创建
- 复杂任务的编排
- CI/CD 管道设置

## 命令

### 创建工作流
```bash
npx claude-flow workflow create --name "deploy-flow" --template ci
```

### 执行工作流
```bash
npx claude-flow workflow execute --name "deploy-flow" --env production
```

### 列出工作流
```bash
npx claude-flow workflow list
```

### 导出模板
```bash
npx claude-flow workflow export --name "deploy-flow" --format yaml
```

### 查看状态
```bash
npx claude-flow workflow status --name "deploy-flow"
```

## 内置模板

| 模板 | 描述 |
|----------|-------------|
| `ci` | 持续集成管道 |
| `deploy` | 部署工作流 |
| `test` | 测试工作流 |
| `release` | 发布自动化 |
| `review` | 代码审查工作流 |

## 工作流结构
```yaml
name: example-workflow
steps:
  - name: analyze
    agent: researcher
    task: "分析需求"
  - name: implement
    agent: coder
    depends: [analyze]
    task: "实现解决方案"
  - name: test
    agent: tester
    depends: [implement]
    task: "编写和运行测试"
```

## 最佳实践
1. 定义清晰的步骤依赖关系
2. 根据步骤使用适当的代理类型
3. 包含验证关卡
4. 导出工作流以供复用
