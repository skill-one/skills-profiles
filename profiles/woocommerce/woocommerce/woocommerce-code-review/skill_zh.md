# WooCommerce 代码审查

对照 WooCommerce 编码规范和惯例审查代码变更。

## 需要标记的关键违规项

### 后端 PHP 代码

参考 `woocommerce-backend-dev` 技能获取详细规范。以这些规范为指导，标记以下违规项及其他类似问题：

**架构与结构：**

- ❌ **独立函数** - 必须使用类方法 ([file-entities.md](../woocommerce-backend-dev/file-entities.md))
- ❌ **使用 `new` 注入依赖管理的类** - `src/` 中的类必须使用 `$container->get()` ([dependency-injection.md](../woocommerce-backend-dev/dependency-injection.md))
- ❌ **`src/Internal/` 外部的类** - 默认位置，除非明确声明为公共 ([file-entities.md](../woocommerce-backend-dev/file-entities.md))

**命名与惯例：**

- ❌ **camelCase 命名** - 方法/变量/钩子必须使用 snake_case ([code-entities.md](../woocommerce-backend-dev/code-entities.md))
- ❌ **Yoda 条件违规** - 必须遵循 WordPress 编码规范 ([coding-conventions.md](../woocommerce-backend-dev/coding-conventions.md))
- ❌ **与现有枚举常量比较的魔法字符串** - 新代码比较或分配枚举值（订单状态、产品类型等）时必须使用 `Automattic\WooCommerce\Enums` 常量，而不是原始字面量 — 除非在可运行于安装/升级期间的代码中 ([coding-conventions.md](../woocommerce-backend-dev/coding-conventions.md))

**文档：**

- ❌ **缺少 `@since` 注释** - 公共/受保护方法及钩子必须包含 ([code-entities.md](../woocommerce-backend-dev/code-entities.md))
- ❌ **缺少文档块** - 所有钩子和方法必须包含 ([code-entities.md](../woocommerce-backend-dev/code-entities.md))
- ❌ **冗长的文档块** - 保持简洁，一行即可 ([code-entities.md](../woocommerce-backend-dev/code-entities.md))

**数据完整性：**

- ❌ **缺少验证** - 删除/修改前必须验证状态 ([data-integrity.md](../woocommerce-backend-dev/data-integrity.md))

**测试：**

- ❌ **测试中使用 `$instance`** - 必须使用 `$sut` 变量名 ([unit-tests.md](../woocommerce-backend-dev/unit-tests.md))
- ❌ **缺少 `@testdox`** - 测试方法文档块必须包含 ([unit-tests.md](../woocommerce-backend-dev/unit-tests.md))
- ❌ **测试文件命名** - 必须遵循 `includes/` 与 `src/` 的命名惯例 ([unit-tests.md](../woocommerce-backend-dev/unit-tests.md))
- ❌ **重复基础生命周期清理** - 在请求断言后 fixture 删除或状态恢复前，先识别测试的基础类；标记已被其事务或清理覆盖的清理操作 ([unit-tests.md](../woocommerce-backend-dev/unit-tests.md#fixture-lifecycle-and-cleanup))

### 前端 JS/TS 代码

**架构与结构：**

- ❌ **自身导入的模块化（循环依赖）** — monorepo 中的任何 JS/TS 文件从其自身的包模块导入（`from '../'`, `from '../../'`, `from '../index'`, `from '../../index'`），而该模块会重新导出它。与 SWC TDZ / esbuild 树摇动 / tsc 增量构建相关。修复：使用直接模块路径。

### UI 文本与文案

参考 `woocommerce-copy-guidelines` 技能。标记：

- ❌ **UI 中的标题大小写** - 必须使用句子大小写 ([sentence-case.md](../woocommerce-copy-guidelines/sentence-case.md))
    - 错误: "Save Changes", "Order Details", "Payment Options"
    - 正确: "Save changes", "Order details", "Payment options"
    - 例外: 专有名词（WooPayments）、缩写（API）、品牌名称

## 审查方法

1. **扫描上述列出的关键违规项**
2. **标记问题时引用具体技能文件**
3. **提供技能文档中的正确示例**
4. **将相关问题分组以增强清晰度**
5. **保持建设性** - 在相关时解释标准存在的理由

## 输出格式

对于每个发现的违规项：

```text
❌ [问题类型]: [具体问题]
位置: [文件路径和行号]
标准: [相关技能文件的链接]
修复: [简要说明或示例]
```

## 注意事项

- 所有详细标准都在 `woocommerce-backend-dev`, `woocommerce-dev-cycle`, `woocommerce-copy-guidelines` 技能中
- 咨询这些技能以获取完整上下文和示例
- 不确定时，参考上述链接的特定技能文档
