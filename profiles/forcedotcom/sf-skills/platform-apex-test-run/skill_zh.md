# platform-apex-test-run: Salesforce 测试执行与覆盖率分析

在用户需要 **Apex 测试执行和失败分析** 时使用此技能：运行测试、检查覆盖率、解释失败、提高覆盖率，以及为 Salesforce 代码管理严格的测试-修复循环。

## 此技能负责任务的条件

当工作涉及以下内容时，使用 `platform-apex-test-run`：
- `sf apex run test` 工作流
- Apex 单元测试失败
- 代码覆盖率分析
- 识别未覆盖的行和缺失的测试场景
- Apex 代码的结构化测试-修复循环

当用户处于以下情况时，将任务委托给其他技能：
- 编写或重构生产 Apex → `platform-apex-generate` 技能
- 测试 Agentforce 代理 → `agentforce-test` 技能
- 使用 Jest 测试 LWC → [experience-lwc-generate](../experience-lwc-generate/SKILL.md)

---

## 首先收集所需的上下文

请求或推断：
- 目标组织别名
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
在调试失败时从狭窄的范围开始；只有在修复稳定后才能扩大范围。

### 3. 分析结果
关注：
- 失败的方法
- 异常类型和堆栈跟踪
- 未覆盖的行 / 覆盖率薄弱区域
- 失败是否表明测试数据问题、脆弱断言或生产逻辑损坏

### 4. 运行严格的修复循环
当问题在于代码或测试质量时：
- 当需要时，将代码修复委托给 `platform-apex-generate` 技能
- 添加或改进测试
- 在更广泛的回归之前重新运行聚焦的测试

### 5. 故意提高覆盖率
覆盖：
- 正向路径
- 负向/异常路径
- 批量路径（在适当情况下 251+ 记录）
- 当相关时，调用或异步路径

---

## 高信号规则

| 规则 | 理由 |
|------|-----------|
| 默认使用 `SeeAllData=false` | 确保测试隔离；防止依赖特定组织的数 |
| 每个测试必须断言有意义的输出 | 没有断言的测试证明不了任何东西，并会给出虚假的信心 |
| 使用 251+ 记录测试批量行为 | 触发 200 记录的批量处理；251 记录跨越了边界 |
| 当它们提高清晰度时使用工厂 / `@TestSetup` | 在一个地方一致地创建数据；在测试方法之间回滚 |
| 将 `Test.startTest()` 与 `Test.stopTest()` 配对用于异步 | 确保异步操作（可排队、未来）在断言之前完成 |
| 不要在测试中隐藏易出错的组织依赖 | 防止与组织状态相关的间歇性失败 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 测试在本地通过但在 CI 组织中失败 | 检查 `SeeAllData=true` 或对组织特定记录的未声明依赖 |
| 重构后覆盖率意外下降 | 首先运行聚焦的类级测试，然后扩大到 `RunLocalTests` 以确认 |
| 调用测试中出现的 "未提交的工作待处理" 错误 | DML 和 HTTP 调用不能在同一个测试上下文中混合，除非用 `Test.startTest()` 包装 |
| 模拟在测试中不起作用 | 确保 `Test.setMock()` 在进行调用之前被调用 |
| 测试方法中缺少 `@TestSetup` 数据 | `@TestSetup` 数据按测试方法提交 — 重新查询它；不要存储在静态变量中 |
| API 版本 67.0 及更高版本而没有必要的访问级别检查 | 检查失败的 SOQL/DML 堆栈跟踪中的 CRUD/FLS 访问错误，使用 `System.runAs` 与分配的权限集时用户模式行为预期，或在需要系统访问时记录合理的 `SYSTEM_MODE` 路径 |

---

## 输出格式

完成时按以下顺序报告：
1. **运行的测试**
2. **通过/失败摘要**
3. **覆盖率结果**
4. **根本原因发现**
5. **修复或下次运行建议**

建议的格式：

```text
测试运行： <范围>
组织： <别名>
结果： <通过 / 部分通过 / 失败>
覆盖率： <百分比 / 关键类>
问题： <最高信号失败>
下一步： <修复类，添加测试，重新运行范围，或扩大回归>
```

---

## 跨技能集成

| 需求 | 委托给 | 理由 |
|------|-------------|--------|
| 修复生产代码或编写测试类 | `platform-apex-generate` 技能 | 代码生成和修复 |
| 创建批量/边缘案例测试数据 | [platform-data-manage](../platform-data-manage/SKILL.md) | 真实的测试数据集 |
| 将更新的测试部署到组织 | [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) | 部署工作流 |
| 检查详细的运行时日志 | [platform-apex-logs-debug](../platform-apex-logs-debug/SKILL.md) | 更深入的失败分析 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/cli-commands.md` | 所有 `sf apex run test` 命令标志、输出格式、异步执行和覆盖率命令 |
| `references/test-patterns.md` | 测试类模板 — 基本模板、批量（251+）、模拟调用和数据工厂模式 |
| `references/testing-best-practices.md` | 核心测试原则 — AAA 模式、命名约定、批量、负向和模拟策略 |
| `references/test-fix-loop.md` | 智能体测试-修复循环实现和失败分析决策树 |
| `references/mocking-patterns.md` | HttpCalloutMock、DML 模拟、StubProvider 和选择器模拟模式 |
| `references/performance-optimization.md` | 减少测试执行时间的技巧 — DML 模拟、SOQL 模拟、循环优化 |
| `assets/basic-test.cls` | 模板：带有 `@TestSetup`、正向/负向/批量/边缘案例方法的标准测试类 |
| `assets/bulk-test.cls` | 模板：带有 251+ 记录的批量测试，跨越了 200 记录的触发器批量边界 |
| `assets/mock-callout-test.cls` | 模板：使用 `HttpCalloutMock` 的 HTTP 调用模拟 |
| `assets/test-data-factory.cls` | 模板：可重用的 `TestDataFactory`，带有创建和插入辅助工具 |
| `assets/dml-mock.cls` | 模板：`IDML` 接口 + `DMLMock` 实现用于无数据库单元测试 |
| `assets/stub-provider-example.cls` | 模板：基于 `StubProvider` 的依赖注入模拟 |
| `scripts/parse-test-results.py` | 后工具挂钩 — 解析 `sf apex run test` JSON 输出并格式化失败以供自动修复循环 |

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 108+ | 强大的生产级测试信心 |
| 96–107 | 良好的测试套件，存在轻微差距 |
| 84–95 | 可接受，但应加强覆盖率 / 断言 |
| < 84 | 低于标准；在依赖之前进行修订 |
