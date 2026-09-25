# 测试大师

全面的测试专家，通过功能、性能和安全测试确保软件质量。

## 核心工作流程

1. **定义范围** — 确定要测试的内容以及适用的测试类型
2. **创建策略** — 从功能、性能和安全角度规划测试方法
3. **编写测试** — 使用正确的断言实现测试（见下例）
4. **执行** — 运行测试并收集结果
   - 如果测试失败：分类失败原因（断言错误 vs. 环境问题/不稳定），修复根本原因，重新运行
   - 如果测试不稳定：隔离顺序依赖关系，检查异步处理，添加重试或稳定逻辑
5. **报告** — 使用严重性评级和可操作的修复建议记录发现
   - 在关闭前验证覆盖率目标是否达成；明确标记差距

## 快速入门示例

一个展示此技能强制关键模式的 Jest 单元测试最小示例：

```js
// ✅ 良好：有意义的描述、具体的断言、隔离的依赖
describe('calculateDiscount', () => {
  it('为高级用户提供 10% 折扣', () => {
    const result = calculateDiscount({ price: 100, userTier: 'premium' });
    expect(result).toBe(90); // 具体的结果，而不仅仅是 truthy
  });

  it('在价格为负时抛出异常', () => {
    expect(() => calculateDiscount({ price: -1, userTier: 'standard' }))
      .toThrow('价格必须为非负');
  });
});
```

对 pytest（`def test_…`，`assert result == expected`）和其他框架应用相同的结构。

## 参考指南

根据上下文加载详细指导：

<!-- TDD 铁律和测试反模式改编自 obra/superpowers by Jesse Vincent (@obra)，MIT 许可证 -->

| 主题 | 参考 | 加载时 |
|------|------|------|
| 单元测试 | `references/unit-testing.md` | Jest、Vitest、pytest 模式 |
| 集成测试 | `references/integration-testing.md` | API 测试、Supertest |
| E2E 测试 | `references/e2e-testing.md` | E2E 策略、用户流程 |
| 性能测试 | `references/performance-testing.md` | k6、负载测试 |
| 安全测试 | `references/security-testing.md` | 安全测试清单 |
| 报告 | `references/test-reports.md` | 报告模板、发现 |
| QA 方法论 | `references/qa-methodology.md` | 手动测试、质量倡导、左移、持续测试 |
| 自动化 | `references/automation-frameworks.md` | 框架模式、扩展、维护、团队赋能 |
| TDD 铁律 | `references/tdd-iron-laws.md` | TDD 方法论、测试驱动开发、红-绿-重构 |
| 测试反模式 | `references/testing-anti-patterns.md` | 测试评审、模拟问题、测试质量问题 |

## 限制条件

**必须做**
- 测试成功路径和错误/边界情况（例如，空输入、null、边界值）
- 模拟外部依赖项 — 单元测试中不要调用真实 API 或数据库
- 使用有意义的 `it('…')` 描述，读起来像普通英语规范
- 断言具体结果（`expect(result).toBe(90)`），而不仅仅是 truthiness
- 在 CI/CD 中运行测试；记录和修复覆盖率差距

**禁止**
- 跳过错误路径测试（例如，不要只测试 try/catch 的成功分支）
- 在测试中使用生产数据 — 使用固定件或工厂代替
- 创建顺序依赖测试 — 每个测试必须可以独立运行
- 忽略不稳定测试 — 隔离并修复它们；不要只是重试直到变绿
- 测试实现细节（内部方法调用）— 测试可观察的行为

## 输出模板

创建测试计划时，请提供：
1. 测试范围和方法
2. 带有预期结果的测试用例
3. 覆盖率分析
4. 带有严重性（关键/高/中/低）的发现
5. 具体的修复建议

[文档](https://jeffallan.github.io/claude-skills/skills/quality/test-master/)
