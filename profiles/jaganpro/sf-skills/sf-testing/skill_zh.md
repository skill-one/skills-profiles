# sf-testing：Salesforce 测试执行与覆盖率分析

当用户需要 **Apex 测试执行和失败分析** 时使用此技能：运行测试、检查覆盖率、解释失败、提高覆盖率，并为 Salesforce 代码管理一个严格的测试-修复循环。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `sf-testing`：
- `sf apex run test` 工作流
- Apex 单元测试失败
- 代码覆盖率分析
- 识别未覆盖的行和缺失的测试场景
- Apex 代码的结构化测试-修复循环

当用户处于以下情况时，将任务委托给其他技能：
- 编写或重构生产 Apex → [sf-apex](../sf-apex/SKILL.md)
- 测试 Agentforce 代理 → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- 使用 Jest 测试 LWC → [sf-lwc](../sf-lwc/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 目标组织的别名
- 期望的测试范围：单个类、特定方法、套件或本地测试
- 覆盖率阈值预期
- 用户是否只想进行诊断或进行测试-修复循环
- 是否已存在相关的测试数据工厂

---

## 推荐的工作流程

### 1. 发现测试范围
识别：
- 现有的测试类
- 目标生产类
- 测试数据工厂 / 设置辅助工具

### 2. 首先运行最小的有用测试集
在调试失败时从狭窄的范围开始；仅在修复稳定后扩大范围。

### 3. 分析结果
关注：
- 失败的方法
- 异常类型和堆栈跟踪
- 未覆盖的行 / 覆盖率薄弱区域
- 失败是否表明测试数据不良、脆弱的断言或生产逻辑损坏

### 4. 运行严格的修复循环
当问题是代码或测试质量时：
- 当需要时，将代码修复委托给 [sf-apex](../sf-apex/SKILL.md)
- 添加或改进测试
- 在更广泛的回归之前重新运行聚焦的测试

### 5. 故意提高覆盖率
覆盖：
- 正向路径
- 负向/异常路径
- 批量路径（在适当情况下 251+ 记录）
- 相关的调用或异步路径

---

## 高信号规则

- 默认使用 `SeeAllData=false`
- 每个测试都应该断言有意义的输出
- 测试批量行为，而不仅仅是单记录的快路径
- 当它们提高清晰度和速度时，使用工厂 / `@TestSetup`
- 当异步行为重要时，将 `Test.startTest()` 与 `Test.stopTest()` 配对
- 不要在测试中隐藏易出错的组织依赖项

---

## 输出格式

完成时，按以下顺序报告：
1. **运行了哪些测试**
2. **通过/失败摘要**
3. **覆盖率结果**
4. **根本原因发现**
5. **修复或下次运行建议**

建议的格式：

```text
Test run: <范围>
Org: <别名>
Result: <通过 / 部分通过 / 失败>
Coverage: <百分比 / 关键类>
Issues: <最高信号失败>
Next step: <修复类、添加测试、重新运行范围或扩大回归>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 修复生产代码或编写测试 | [sf-apex](../sf-apex/SKILL.md) | 代码生成和修复 |
| 创建批量/边缘案例数据 | [sf-data](../sf-data/SKILL.md) | 真实的测试数据集 |
| 部署更新的测试 | [sf-deploy](../sf-deploy/SKILL.md) | 推广 |
| 检查详细的运行时日志 | [sf-debug](../sf-debug/SKILL.md) | 更深入的失败分析 |

---

## 参考地图

### 从这里开始
- [references/cli-commands.md](references/cli-commands.md)
- [references/test-patterns.md](references/test-patterns.md)
- [references/testing-best-practices.md](references/testing-best-practices.md)
- [references/test-fix-loop.md](references/test-fix-loop.md)

### 专门指导
- [references/mocking-patterns.md](references/mocking-patterns.md)
- [references/performance-optimization.md](references/performance-optimization.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 108+ | 强大的生产级测试信心 |
| 96–107 | 良好的测试套件，存在微小差距 |
| 84–95 | 可接受但应加强覆盖范围 / 断言 |
| < 84 | 低于标准；在依赖之前应进行修订 |
