# 知识图谱技能

## 概述

知识图谱（KG）是一个持久的 JSON 文件，用于存储代码库分析的发现结果，消除重复探索并支持任务验证。

**位置**：`docs/specs/[ID-功能]/knowledge-graph.json`

**主要优势**：
- ✅ 避免重新探索已分析的代码库
- ✅ 基于实际代码库状态验证任务依赖关系
- ✅ 在团队成员间共享发现结果
- ✅ 通过缓存上下文加速任务生成

## 使用场景

在以下情况下使用此技能：

1. **spec-to-tasks 需要缓存/重用代码库分析** - 存储代理的发现结果以供后续重用
2. **task-implementation 需要验证任务依赖关系和契约** - 在实现前检查所需组件是否存在
3. **任何命令需要查询现有模式/组件/API** - 获取缓存的代码库上下文
4. **减少重复的代码库探索** - 避免重新分析已探索的代码

**触发短语**：
- "加载知识图谱"
- "查询知识图谱"
- "更新知识图谱"
- "与知识图谱验证"
- "检查组件是否存在"
- "查找现有模式"

## 使用说明

### 可用操作

**1. read-knowledge-graph** - 加载并解析规范对应的 KG
- **输入**：规范文件夹路径（例如，`docs/specs/001-功能/`）
- **输出**：包含元数据、模式、组件、API 的 KG 对象

**2. query-knowledge-graph** - 查询特定部分（组件、模式、API）
- **输入**：规范文件夹、查询类型、可选过滤器
- **输出**：符合标准的过滤结果

**3. update-knowledge-graph** - 使用新发现结果更新 KG
- **输入**：规范文件夹、更新内容（部分 KG）、来源描述
- **输出**：包含新发现的合并 KG

**4. validate-against-knowledge-graph** - 基于 KG 验证任务依赖关系
- **输入**：规范文件夹、要求（组件、API、模式）
- **输出**：包含错误/警告的验证报告

**5. validate-contract** - 验证任务间的 provides/expects
- **输入**：规范文件夹、expects（文件+符号）、已完成的依赖关系
- **输出**：满足/未满足的期望报告

**6. extract-provides** - 从已实现文件中提取符号
- **输入**：文件路径数组
- **输出**：包含文件、符号、类型的 provides 数组

**7. aggregate-knowledge-graphs** - 合并所有规范中的模式
- **输入**：项目根路径
- **输出**：包含去重模式的全局 KG

有关详细使用示例，请参阅 [references/query-examples.md](references/query-examples.md)。

## 示例

### 输入/输出示例

**读取知识图谱**：
```
输入：/knowledge-graph read docs/specs/001-酒店搜索/
输出：{
  metadata: { spec_id: "001-酒店搜索", version: "1.0" },
  patterns: { architectural: [...], conventions: [...] },
  components: { controllers: [...], services: [...]]}
}
```

**查询组件**：
```
输入：/knowledge-graph query docs/specs/001-酒店搜索/ components {"category": "services"}
输出：[{ id: "comp-svc-001", name: "HotelSearchService", type: "service"}]
```

**更新知识图谱**：
```
输入：/knowledge-graph update docs/specs/001-酒店搜索/ {
  patterns: { architectural: [{ name: "Repository Pattern"}] }
}
输出："已向知识图谱添加 1 个模式"
```

**验证依赖关系**：
```
输入：/knowledge-graph validate docs/specs/001-酒店搜索/ {
  components: ["comp-repo-001"]
}
输出：{ valid: true, errors: [], warnings: [] }
```

有关全面的流程示例，请参阅 [references/examples.md](references/examples.md)。

## KG 模式参考

有关完整的 JSON 模式及示例，请参阅 [references/schema.md](references/schema.md)。

## 集成模式

有关与 Developer Kit 命令的详细集成说明，请参阅 [references/integration-patterns.md](references/integration-patterns.md)。

## 错误处理

有关全面的错误处理策略和恢复流程，请参阅 [references/error-handling.md](references/error-handling.md)。

## 性能考虑

有关优化策略和性能特征，请参阅 [references/performance.md](references/performance.md)。

## 安全

有关安全考虑、威胁缓解和最佳实践，请参阅 [references/security.md](references/security.md)。

## 最佳实践

**何时查询 KG**：在代码库分析、任务生成、依赖关系验证之前

**何时更新 KG**：在代理发现结果、组件实现、模式发现之后

**KG 新鲜度**：
- < 7 天：新鲜
- 7-30 天：过期，提醒用户
- > 30 天：非常过期，建议重新生成

有关详细最佳实践，请参阅 [references/performance.md](references/performance.md) 和 [references/security.md](references/security.md)。

## 限制和警告

### 关键限制

- **源代码安全操作**：不会修改源代码文件。仅创建/更新 `knowledge-graph.json` 文件。
- **路径验证**：仅从 `docs/specs/[ID]/` 路径读取/写入 KG 文件。
- **无自动代码生成**：缓存分析结果，不生成实现代码。

### 限制

- **验证范围**：检查 KG 中组件是否存在，但无法验证实际代码库中组件的存在（如果 KG 过期）
- **新鲜度依赖**：KG 准确性取决于最近更新的时间
- **单规范优先**：每个 KG 主要针对单个规范
- **文件大小**：对于复杂规范，KG 文件可能很大（>1MB）

有关完整的限制和警告，请参阅 [references/error-handling.md](references/error-handling.md) 和 [references/security.md](references/security.md)。

## 参考文件

- [schema.md](references/schema.md) - 完整的 JSON 模式
- [query-examples.md](references/query-examples.md) - 查询模式
- [integration-patterns.md](references/integration-patterns.md) - 命令集成
- [error-handling.md](references/error-handling.md) - 错误处理指南
- [performance.md](references/performance.md) - 性能优化
- [security.md](references/security.md) - 安全考虑
- [examples.md](references/examples.md) - 实际示例
