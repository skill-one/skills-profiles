# 遗留系统现代化工具

## 核心工作流程

1. **评估系统** — 分析代码库、依赖项、风险和业务约束。在进行下一步之前，生成依赖关系图和风险登记册。
   - *验证检查点*：在进入步骤2之前，确认所有外部集成和数据合同都已记录。

2. **规划迁移** — 设计具有明确回滚策略的增量路线图。参考 `references/system-assessment.md` 获取代码分析模板。
   - *验证检查点*：确认每个阶段都有定义的回滚触发器和负责人。

3. **构建安全网** — 在修改生产代码之前，创建特征化测试和监控。目标覆盖现有行为的80%以上。
   - *验证检查点*：在继续之前，在未修改的遗留系统上运行特征化测试套件并确认其通过绿色。

4. **增量迁移** — 应用 strangler fig 模式并使用功能标志。通过外观路由流量；逐步转移负载。
   - *验证检查点*：在每次流量增量后（例如，5% → 25% → 50% → 100%）验证错误率和延迟指标是否保持在基线阈值内。

5. **验证和迭代** — 运行完整测试套件，查看监控仪表板，并在退役遗留代码之前确认业务行为得以保留。
   - *验证检查点*：新代码必须在100%流量下至少一个发布周期内证明稳定，然后才能移除遗留路径。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| Strangler Fig | `references/strangler-fig-pattern.md` | 增量替换、外观层、路由 |
| 重构 | `references/refactoring-patterns.md` | 提取服务、通过抽象分支、适配器 |
| 迁移 | `references/migration-strategies.md` | 数据库、UI、API、框架迁移 |
| 测试 | `references/legacy-testing.md` | 特征化测试、黄金主、批准 |
| 评估 | `references/system-assessment.md` | 代码分析、依赖关系映射、风险评估 |

## 代码示例

### Strangler Fig 外观 (Python)
```python
# facade.py — 根据功能标志将请求路由到遗留或新服务
import os
from legacy_service import LegacyOrderService
from new_service import NewOrderService

class OrderServiceFacade:
    def __init__(self):
        self._legacy = LegacyOrderService()
        self._new = NewOrderService()

    def get_order(self, order_id: str):
        if os.getenv("USE_NEW_ORDER_SERVICE", "false").lower() == "true":
            return self._new.fetch(order_id)
        return self._legacy.get(order_id)
```

### 功能标志包装器
```python
# feature_flags.py — 环境或基于配置的标志存储的薄包装器
import os

def flag_enabled(flag_name: str, default: bool = False) -> bool:
    """检查迁移功能标志是否处于活动状态。"""
    return os.getenv(flag_name, str(default)).lower() == "true"

# 使用示例
if flag_enabled("USE_NEW_PAYMENT_GATEWAY"):
    result = new_gateway.charge(order)
else:
    result = legacy_gateway.charge(order)
```

### 特征化测试模板 (pytest)
```python
# test_characterization_orders.py
# 将现有遗留行为捕获为黄金主安全网。
import pytest
from legacy_service import LegacyOrderService

service = LegacyOrderService()

@pytest.mark.parametrize("order_id,expected_status", [
    ("ORD-001", "SHIPPED"),
    ("ORD-002", "PENDING"),
    ("ORD-003", "CANCELLED"),
])
def test_order_status_golden_master(order_id, expected_status):
    """如果遗留行为意外变化，则大声失败。"""
    result = service.get(order_id)
    assert result["status"] == expected_status, (
        f"特征化损坏："
        f"预期 {expected_status}，得到 {result['status']}"
    )
```

## 约束条件

### 必须做
- 在所有迁移过程中保持零生产中断
- 在重构之前创建全面的测试覆盖率（目标80%以上）
- 使用功能标志进行所有增量发布
- 实施监控和回滚程序
- 记录所有迁移决策和理由
- 保留现有的业务逻辑和行为
- 透明地沟通进展和风险

### 严禁做
- 爆炸式重写或替换
- 在更改之前跳过测试遗留行为
- 没有回滚能力就部署
- 破坏现有的集成或API
- 在新代码中忽略技术债务
- 没有适当的验证就匆忙迁移
- 在新代码被证明之前移除遗留代码

## 输出模板

在实施现代化时，提供：
1. 评估摘要（风险、依赖项、方法）
2. 迁移计划（阶段、回滚策略、指标）
3. 实现代码（外观、适配器、新服务）
4. 测试覆盖率（特征化、集成、端到端）
5. 监控设置（指标、警报、仪表板）

## 知识参考

Strangler fig 模式、通过抽象分支、特征化测试、增量迁移、功能标志、金丝雀部署、API 版本控制、数据库重构、微服务提取、技术债务减少、零停机部署

[文档](https://jeffallan.github.io/claude-skills/skills/specialized/legacy-modernizer/)
