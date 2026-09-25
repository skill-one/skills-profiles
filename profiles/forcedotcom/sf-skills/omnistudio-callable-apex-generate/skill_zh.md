# omnistudio-callable-apex-generate：Salesforce 行业通用核心可调用 Apex

Salesforce 行业通用核心可调用 Apex 实现专家。生成安全、确定性且可配置的 Apex，与 OmniStudio 和行业扩展点无缝集成。

## 范围

- **在范围内**：为行业扩展点创建 `System.Callable` 类；审查可调用实现的正确性和风险；将 `VlocityOpenInterface` / `VlocityOpenInterface2` 迁移到 `System.Callable`；120 分评分和验证
- **超出范围**：通用 Apex 类（无可调用接口，使用 `platform-apex-generate`）；构建集成流程（使用 `omnistudio-integration-procedure-generate`）；编写 OmniScripts（使用 `omnistudio-omniscript-generate`）；部署 Apex 类（使用 `platform-metadata-deploy`）

---

## 核心职责

1. **可调用生成**：构建具有安全动作调度的 `System.Callable` 类
2. **可调用审查**：审计现有可调用实现，确保正确性和风险
3. **验证与评分**：根据 120 分评分标准进行评估
4. **行业适配**：确保与 OmniStudio/行业扩展点兼容

---

## 工作流程（四阶段模式）

### 阶段 1：需求收集

收集以下信息：
- 入口点（OmniScript、集成流程、DataRaptor 或其他行业钩子）
- 动作名称（传递给 `call` 的字符串）
- 输入/输出契约（必需的键、类型和响应结构）
- 数据访问需求（对象/字段、CRUD/FLS（创建/读取/更新/删除和字段级安全）规则）
- 侧效应（DML、调用外部服务、异步需求）

然后：
1. 扫描现有可调用类：`Glob: **/*Callable*.cls`
2. 识别用于行业扩展的共享工具或基类
3. 创建任务列表

---

### 阶段 2：设计与契约定义

**定义可调用契约**：
- 动作列表（显式、版本化的字符串）
- 输入模式（必需的键 + 类型）
- 输出模式（一致的响应包）

**推荐响应包**：
```json
{
  "success": true|false,
  "data": {...},
  "errors": [ { "code": "...", "message": "..." } ]
}
```

**动作调度规则**：
- 使用 `switch on action`
- 默认情况抛出类型化异常
- 不使用动态方法调用或反射

**VlocityOpenInterface / VlocityOpenInterface2 契约映射**：

在为遗留 Open Interface 扩展点设计（或支持可调用 + Open Interface 双重模式）时，映射签名：

```text
invokeMethod(String methodName, Map<String, Object> inputMap, Map<String, Object> outputMap, Map<String, Object> options)
```

| 参数 | 角色 | 可调用等效项 |
|-------|------|---------------------|
| `methodName` | 动作选择器（与 `action` 具有相同语义） | `call(action, args)` 中的 `action` |
| `inputMap` | 主要输入数据（必需的键、类型） | `args.get('inputMap')` |
| `outputMap` | 可变映射，用于写入结果（按引用传递） | 返回值；可调用返回包而不是 `outputMap` |
| `options` | 额外上下文（父 DataRaptor/OmniScript 上下文、调用元数据） | `args.get('options')` |

Open Interface 契约设计规则：
- 将 `inputMap` 和 `options` 视为组合输入模式
- 定义每个动作必须写入 `outputMap` 的键（成功和错误情况）
- 保留 `methodName` 字符串，使其与可调用 `action` 字符串一致
- 记录每个动作的 `options` 是否必需、可选或未使用

---

### 阶段 3：实现模式

**纯 `System.Callable**`（扁平参数，无 Open Interface 关联）：

**在生成前阅读 `assets/pattern_callable_vanilla.cls`** — 当调用者传递扁平参数且无需 VlocityOpenInterface 集成时使用。

**可调用骨架**（与 VlocityOpenInterface 相同的输入）：

**在生成前阅读 `assets/pattern_callable_openinterface.cls`** — 当集成 Open Interface 或调用者传递该结构时，在 `args` 中使用 `inputMap` 和 `options` 键。

**输入格式**：调用者将 `args` 传递为 `{ 'inputMap' => Map<String, Object>, 'options' => Map<String, Object> }`。为向后兼容扁平调用者，如果 `args` 缺少 `'inputMap'`，则将 `args` 本身视为 `inputMap`，并将 `options` 初始化为空映射。

**实现规则**：
1. 保持 `call()` 轻量级；委托给私有方法或服务类
2. 早期验证和强制转换输入类型（空值安全）
3. 强制执行 CRUD/FLS（创建/读取/更新/删除和字段级安全）和权限（`with sharing`，`Security.stripInaccessible()`）
4. 当参数包含记录集合时进行批量处理
5. 在适当情况下使用 `WITH USER_MODE` 进行 SOQL
6. **命名空间处理**：`System.Callable` 是标准接口（无需命名空间前缀）；`omnistudio.VlocityOpenInterface2` 使用 `omnistudio` 管理包命名空间 — 始终限定它。如果可调用类将部署到命名空间管理的包中，请询问用户命名空间前缀并应用于自定义类名（例如，`myns__Industries_XxxCallable`）

**VlocityOpenInterface / VlocityOpenInterface2 实现**：

在实现 `omnistudio.VlocityOpenInterface` 或 `omnistudio.VlocityOpenInterface2` 时，使用以下签名：

```apex
global Boolean invokeMethod(String methodName, Map<String, Object> inputMap,
                           Map<String, Object> outputMap, Map<String, Object> options)
```

**在生成前阅读 `assets/pattern_openinterface.cls`** — 完成 `VlocityOpenInterface2` 骨架，包含 `switch on` 调度和 `outputMap` 契约。

Open Interface 实现规则：
- 通过 `putAll()` 或单个 `put()` 调用将结果写入 `outputMap`；不要从 `invokeMethod` 返回包
- 成功返回 `true`，不支持的或失败的动作用于返回 `false`
- 使用与可调用相同的内部私有方法（具有相同的 `inputMap` 和 `options` 参数）；仅入口点不同
- 使用相同的包形状（`success`，`data`，`errors`）填充 `outputMap` 以保持一致性

可调用和 Open Interface 接受相同的输入（`inputMap`，`options`）并委托给相同的私有方法签名以实现共享逻辑。

---

### 阶段 4：测试与验证

最小测试：
- **正向**：支持的动作执行成功
- **负向**：不支持的动作用于抛出预期异常
- **契约**：缺失/无效输入返回错误包
- **批量**：处理列表输入而不触发限制

**在生成前阅读 `assets/pattern_test_class.cls`** — 完成测试类骨架（正向、负向、契约、批量和空参数情况）。

---

## 迁移：VlocityOpenInterface 到 System.Callable

在现代化行业扩展时，将 `VlocityOpenInterface` 或
`VlocityOpenInterface2` 实现迁移到 `System.Callable` 并保持动作契约稳定。

**指导**：
- 保留动作名称（`methodName`）作为 `call()` 中的 `action` 字符串
- 将 `inputMap` 和 `options` 作为 `args` 中的键传递：`{ 'inputMap' => inputMap, 'options' => options }`
- 返回一致的响应包，而不是修改 `outMap`
- 保持 `call()` 轻量级；委托给具有 `(inputMap, options)` 签名的相同内部方法
- 为每个动作和不受支持的动作用于添加测试

**在开始迁移工作前阅读 `assets/pattern_migration.cls`** — 标注的迁移前/后示例（VlocityOpenInterface2 → System.Callable）。

---

## 最佳实践（120 分评分）

| 类别 | 分数 | 关键规则 |
|------|------|-----------|
| **契约与调度** | 20 | 显式动作列表；`switch on`；版本化的动作字符串 |
| **输入验证** | 20 | 验证必需的键；安全强制转换类型；空值保护 |
| **安全** | 20 | `with sharing`；CRUD/FLS 检查；`Security.stripInaccessible()` |
| **错误处理** | 15 | 类型化异常；一致的错误包；无空 catch |
| **批量处理与限制** | 20 | 循环中无 SOQL/DML；支持列表输入 |
| **测试** | 15 | 正向/负向/契约/批量测试 |
| **文档** | 10 | ApexDoc（`/** ... */` 块注释 — Salesforce Apex 文档标准）用于类和动作方法 |

**阈值**：[通过] 90+（就绪） | [审查] 70-89（审查） | [阻止] <70（阻止）

---

## 安全限制（强制）

如果引入以下任何内容，请停止并询问用户：
- 基于用户输入的动态方法执行（无反射）
- 循环中的 SOQL/DML
- 可调用类上的 `without sharing`
- 静默失败（空 catch，吞噬异常）
- 动作之间不一致的响应形状

---

## 注意事项

| 问题 | 解决方案 |
|------|-----------|
| 调用者传递扁平参数但代码期望 `inputMap` 键 | 防御性检查：如果 `args` 缺少 `'inputMap'` 键，则将 `args` 本身视为输入映射 |
| `call()` 接收 `null` 作为 `args` | 始终在访问键之前对 `args` 进行空值检查；如果为空，则初始化为空映射 |
| 测试类使用 `(Map<String, Object>) svc.call(...)` 但调用返回错误类型 | 确保每个动作返回相同的包类型（`Map<String, Object>`）— 混合返回类型会破坏调用者 |
| VlocityOpenInterface2 迁移破坏了读取 `outputMap` 按引用的调用者 | 迁移到可调用后，调用者必须读取返回值而不是读取 `outputMap` — 更新所有调用者 |
| 项目中缺少 `IndustriesCallableException` 类 | 此自定义异常必须与可调用类一起部署 — 在每个部署包中包含它 |
| 组织同时具有遗留 Open Interface 和新的可调用，连接到同一动作 | 一次只有一个入口点应处于活动状态；在确认可调用工作正常后禁用旧接口 |

---

## 常见反模式

- `call()` 包含业务逻辑而不是委托
- 动作名称未版本化或不文档化
- 假设输入映射具有键而无需检查
- 混合响应类型（有时是 Map，有时是 String）
- 无不支持动作的测试

---

## 跨技能集成

| 技能 | 使用场景 | 示例 |
|------|-------------|---------|
| platform-apex-generate | 超出可调用实现的通用 Apex 工作 | "为 Account 创建触发器" |
| platform-custom-object-generate / platform-custom-field-generate | 在编码前验证对象/字段可用性 | "描述 Product2 字段" |
| platform-metadata-deploy | 验证/部署可调用类 | "部署到沙盒" |

---

## 参考技能

在以下位置使用核心 Apex 标准、测试模式和限制：
- [skills/platform-apex-generate/SKILL.md](../platform-apex-generate/SKILL.md)

---

## 嵌套示例

- [examples/Test_QuoteByProductCallable/](examples/Test_QuoteByProductCallable/) — 带有 `WITH USER_MODE` 的只读查询示例
- [examples/Test_VlocityOpenInterfaceConversion/](examples/Test_VlocityOpenInterfaceConversion/) — 从遗留 `VlocityOpenInterface` 迁移
- [examples/Test_VlocityOpenInterface2Conversion/](examples/Test_VlocityOpenInterface2Conversion/) — 从 `VlocityOpenInterface2` 迁移

## 输出预期

此技能生成的可交付成果：

- `<ClassName>.cls` — 实现 `System.Callable` 并具有 `switch on action` 调度的可调用类
- `<ClassName>Test.cls` — 具有正向、负向、契约和批量测试方法的测试类
- `IndustriesCallableException.cls` — 自定义异常类（如果项目中尚未存在）

---

## 注意事项

- 优先选择确定性、感知副作用的可调用动作
- 保持动作契约稳定；为破坏性变更引入新动作
- 避免在同步可调用中执行长时间运行的工作；需要时使用异步

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/pattern_callable_vanilla.cls` | 阶段 3 — 扁平参数、无 Open Interface 关联的 `System.Callable` 骨架 |
| `assets/pattern_callable_openinterface.cls` | 阶段 3 — 具有输入映射/`options` 参数的 `System.Callable` 骨架（Open Interface 兼容） |
| `assets/pattern_openinterface.cls` | 阶段 3 — `VlocityOpenInterface2` 骨架，包含 `switch on` 调度和 `outputMap` 契约 |
| `assets/pattern_test_class.cls` | 阶段 4 — 测试类骨架（正向、负向、契约、批量和空参数情况） |
| `assets/pattern_migration.cls` | 迁移 — 标注的迁移前/后模式（VlocityOpenInterface2 → System.Callable） |
| `examples/Test_QuoteByProductCallable/Industries_QuoteByProductCallable.cls` | 阶段 3 — 完整可调用实现，带有 `WITH USER_MODE` SOQL 和错误包 |
| `examples/Test_QuoteByProductCallable/Industries_QuoteByProductCallableTest.cls` | 阶段 4 — 覆盖正向、契约和不支持动作情况的完整测试类 |
| `examples/Test_QuoteByProductCallable/IndustriesCallableException.cls` | 阶段 3 — 用于不支持动作的自定义异常模式 |
| `examples/Test_QuoteByProductCallable/TRANSCRIPT.md` | 参考 — Quote-by-Product 可调用示例的推理转录 |
| `examples/Test_VlocityOpenInterfaceConversion/MyCustomCallable.cls` | 阶段 3 — 从遗留 `VlocityOpenInterface` 迁移的模式 |
| `examples/Test_VlocityOpenInterfaceConversion/MyCustomCallableTest.cls` | 阶段 4 — VlocityOpenInterface 迁移示例的测试类 |
| `examples/Test_VlocityOpenInterfaceConversion/IndustriesCallableException.cls` | 阶段 3 — 部署在 VlocityOpenInterface 迁移旁边的自定义异常类 |
| `examples/Test_VlocityOpenInterfaceConversion/MyCustomClass.cls` | 阶段 3 — 迁移前的原始遗留 VlocityOpenInterface 类 |
| `examples/Test_VlocityOpenInterfaceConversion/TRANSCRIPT.md` | 参考 — VlocityOpenInterface 迁移的推理转录 |
| `examples/Test_VlocityOpenInterface2Conversion/MyCustomCallable.cls` | 阶段 3 — 从 `VlocityOpenInterface2` 迁移的模式 |
| `examples/Test_VlocityOpenInterface2Conversion/MyCustomCallableTest.cls` | 阶段 4 — VlocityOpenInterface2 迁移示例的测试类 |
| `examples/Test_VlocityOpenInterface2Conversion/IndustriesCallableException.cls` | 阶段 3 — 部署在 VlocityOpenInterface2 迁移旁边的自定义异常类 |
| `examples/Test_VlocityOpenInterface2Conversion/MyCustomRemoteClass.cls` | 阶段 3 — VlocityOpenInterface2 迁移示例使用的远程类 |
| `examples/Test_VlocityOpenInterface2Conversion/TRANSCRIPT.md` | 参考 — VlocityOpenInterface2 迁移的推理转录 |

---

## 交付前检查清单

- [ ] `call()` 在访问键前对 `args` 进行空值检查
- [ ] `IndustriesCallableException` 类包含在部署包中
- [ ] 为 `omnistudio.VlocityOpenInterface2` 限定命名空间（如适用）
- [ ] 每个动作的 `outputMap` 键文档化（成功和错误情况）
- [ ] 迁移后调用者读取返回值而不是按引用读取 `outputMap`
