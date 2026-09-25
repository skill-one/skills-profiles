# 顺序思维

通过迭代推理、修订和分支能力，实现结构化问题解决。

## 核心功能

- **迭代推理**：将复杂问题分解为顺序思维步骤
- **动态范围**：随着理解的深入调整总思考次数
- **修订跟踪**：重新考虑并修改之前的结论
- **分支探索**：从任何一点探索替代的推理路径
- **保持上下文**：在整个分析过程中跟踪推理链

## 使用场景

当需要使用 `mcp__reasoning__sequentialthinking` 时：
- 问题需要多个相互关联的推理步骤
- 初始范围或方法不确定
- 需要过滤复杂性以找到核心问题
- 可能需要回溯或修订早期的结论
- 希望探索替代的解决方案路径

**不适用于**：简单查询、直接事实或单步任务。

## 基本用法

MCP 工具 `mcp__reasoning__sequentialthinking` 接受以下参数：

### 必填参数

- `thought` (字符串): 当前推理步骤
- `nextThoughtNeeded` (布尔值): 是否需要更多推理
- `thoughtNumber` (整数): 当前步骤编号（从1开始）
- `totalThoughts` (整数): 预计需要的总步骤数

### 可选参数

- `isRevision` (布尔值): 指示此修订之前的思考
- `revisesThought` (整数): 正在被重新考虑的步骤编号
- `branchFromThought` (整数): 从哪个步骤分支
- `branchId` (字符串): 此推理分支的标识符

## 工作流模式

```
1. 以初始思考开始（thoughtNumber: 1）
2. 对于每个步骤：
   - 在 `thought` 中表达当前推理
   - 通过 `totalThoughts` 估计剩余工作（动态调整）
   - 设置 `nextThoughtNeeded: true` 以继续
3. 当达到结论时，设置 `nextThoughtNeeded: false`
```

## 简单示例

```typescript
// 第一步骤
{
  thought: "问题涉及优化数据库查询。首先需要识别瓶颈。",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
}

// 第二步骤
{
  thought: "分析查询模式显示用户获取存在N+1问题。",
  thoughtNumber: 2,
  totalThoughts: 6, // 调整了范围
  nextThoughtNeeded: true
}

// ... 继续直到完成
```

## 高级功能

对于修订模式、分支策略和复杂工作流，请参阅：
- [高级用法](references/advanced.md) - 修订和分支模式
- [示例](references/examples.md) - 真实世界的用例

## 小贴士

- 开始时对 `totalThoughts` 做粗略估计，随着进展逐步完善
- 当假设被证明错误时使用修订
- 当多个方法看似可行时使用分支
- 在思考中明确表达不确定性
- 自由调整范围 - 准确性不如进展可见性重要
