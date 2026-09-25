# 制定策略规则定义

**权限要求：** 需要拥有 `EnforceOMatic` 和 `PolicyRuleMDAPI` 组织权限。 
**最低 API 版本：** 64.0（使用 `PolicyJsonExpression` 的条件需为 66.0）。

本技能涵盖策略制定的**磁盘元数据 XML 格式**。每当任务要求编写 `*.policyRuleDefinition` 或 `*.policyRuleDefinitionSet` 文件，或发布包含这些文件的元数据包时，都应使用它。运行时部分（RuleProvider、钩子）不在范围内。

---

> **评估范围：** 该技能由团队的 ADK 评估框架执行，而不是技能目录下的 `tests/evals/` 中的测试。五个涵盖 ACCESS / GOVERNANCE / RECORD / TRANSFORM 变体的数据集位于 `packages/adk-eval/eval/domains/platform-policy-rule-generate/datasets/`。

## 1. 包布局

可部署的包始终包含：

```text
<fixture>/
  package.xml
  policyRuleDefinitionSets/<setName>.policyRuleDefinitionSet
  policyRuleDefinitions/<ruleName>.policyRuleDefinition
```

`package.xml` 模板（用于 ftests 使用 `<version>[ftest]</version>`，用于真实组织使用 `64.0` 或更高版本）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Rule0</members>
        <name>PolicyRuleDefinition</name>
    </types>
    <types>
        <members>Set1</members>
        <name>PolicyRuleDefinitionSet</name>
    </types>
    <version>64.0</version>
</Package>
```

---

## 2. PolicyRuleDefinitionSet 模式

```xml
<PolicyRuleDefinitionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Set1</label>
    <description>可选的自由文本</description>
    <replicated>false</replicated>             <!-- MinAppVersion 260 -->
    <builderCompatible>true</builderCompatible> <!-- MinAppVersion 262, 可由作者设置 -->
    <!-- builderValidated: 服务器管理 — 不要在编写的 XML 中设置 -->
</PolicyRuleDefinitionSet>
```

| 元素 | 必填 | 备注 |
|---------|-----|-------|
| `<label>` | 是 | 主标签。文件基本名（devName）是 MDAPI 标识符，不是标签。 |
| `<description>` | 否 | 自由文本。 |
| `<replicated>` | 否 | `true` 触发跨配套组织的占位符转换。省略表示 null/false。 |
| `<builderCompatible>` | 否 | `true` = 根据 §7 检查表审计规则。`false` = 仅 API。省略 = 未审计。仅信息性 — 没有部署/运行时影响。 |
| `<builderValidated>` | 否 | **服务器管理。永远不要在编写的 XML 中设置。** 服务器在验证时覆盖。 |

---

## 3. PolicyRuleDefinition — 核心字段

| 元素 | 必填 | 备注 |
|---------|-----|-------|
| `<label>` | 是 | MasterLabel。 |
| `<category>` | 是 | 参考 §4。驱动 `resourceScopeType`，以及是否需要 `policyRuleResourceDomains`/`resourceTransform`。**不限制 TRANSFORM 外部的 `effect`。** |
| `<effect>` | 是 | `Permit`、`Forbid` 或 `Transform`。核心强制执行的唯一类别耦合：`effect=Transform ↔ category=TRANSFORM_POLICY_RULE_DEFINITION`（双向）。所有其他类别可自由接受 Permit 和 Forbid。 |
| `<action>` | 是（≥1） | `Read`、`TupleRead`、`Create` 等。多个元素 OR 组合。 |
| `<policyRuleDefinitionSetName>` | 是 | 父集的开发者名称。 |
| `<principalScopeType>` | 是 | 始终为 `ANY`。 |
| `<resourceScopeType>` | 是 | `ANY`、`FIELD`、`RECORD`、`DATASPACE` 或 `SPAN`。必须与类别（§4）匹配。 |
| `<principalAuthenticationLevel>` | 否 | `INTERNAL`、`AUTHENTICATED`、`UNIDENTIFIED`、`IDENTIFIED`。 |
| `<ruleConsumer>` | 否 | `ALL`、`DATACLOUD`、`MULESOFT`、`TABLEAU`、`CORE`。 |
| `<policyRuleResourceDomains>` | 否 | 仅 RECORD（RLS）和 FIELD 范围 TRANSFORM 规则需要。ACCESS/GOVERNANCE 上禁止。 |
| `<resourceTransform>` | 否 | 仅当 `category=TRANSFORM` 时需要（且仅在此情况下有效）。 |
| `<whenPolicyRuleDefinitionClauseConjunction>` | 否 | WHEN 条件。 |
| `<unlessPolicyRuleDefinitionClauseConjunction>` | 否 | UNLESS 条件。不在 UI 中可编辑 — 优先使用 WHEN + 否定运算符。 |

---

## 4. 类别决策树

**类别命名平台执行层中的域（规则适用于平台的哪个执行层）。效果命名操作（允许/拒绝/转换）。它们独立，除了 TRANSFORM。**

平台验证的唯一类别 × 效果规则：

- `effect=Transform` ⇔ `category=TRANSFORM_POLICY_RULE_DEFINITION`（双向；不匹配会抛出 `INVALIDFORCATEGORY`）。
- 所有其他类别（`ACCESS`、`GOVERNANCE`、`RECORD`、`IDENTIFIED_RECORD`）接受 `Permit` 或 `Forbid`。

> **关于平台自动填充默认值的说明：** 当 `<category>` 从编写的 XML 中省略时，服务器会根据 `effect` 填充：`Permit→ACCESS`、`Forbid→GOVERNANCE`、`Transform→TRANSFORM`。**这是一个默认填充，不是验证。** 如果你编写了一个与此默认值矛盾的显式类别，它将被接受并按原样持久化。

### 选择类别

```text
策略类型是什么？
│
├── 对标记或分类资源的 OLS/FLS 允许/拒绝
│     category = ACCESS_POLICY_RULE_DEFINITION（访问平面中的允许/拒绝断言）
│              | GOVERNANCE_POLICY_RULE_DEFINITION（治理审计）
│     effect = Permit | Forbid（独立于类别选择）
│     resourceScopeType = ANY | FIELD | DATASPACE
│     NO <policyRuleResourceDomains>
│     条件：resourcePath=TAG|CLASSIFICATION CONTAINS_ANY <ref>
│     对“对象及其所有字段” → action=TupleRead + OR of ENTITYTYPE 条件（§7）
│     注意：“阻止对 Foo 对象的访问” → 用 <yourTag> 标记 Foo，在标签上编写规则
│        不要使用 <resourceDomain>Foo</resourceDomain> — 在 ACCESS/GOVERNANCE 上禁止
│
├── DMO/DLO 的行级过滤
│     category = RECORD_POLICY_RULE_DEFINITION
│     effect = Permit | Forbid
│     resourceScopeType = RECORD
│     <policyRuleResourceDomains> = DMO/DLO API 名称 ← 允许在此处定位实体
│
├── 已识别访客记录访问
│     不能通过 MDAPI 编写 — SESSION_CONSUMER_ID 不在 RuleContextPathType 中
│        必须作为运行时 RuleProvider 实现。
│
└── 字段遮罩
      category = TRANSFORM_POLICY_RULE_DEFINITION   ← RuleBuilder 验证器要求
      effect = Transform                            ← RuleBuilder 验证器要求
      resourceScopeType = FIELD（结构化）或 SPAN（非结构化）
      <policyRuleResourceDomains> = 被遮罩字段的 DMO
      <resourceTransform> 需要（例如：NULL_RESOURCE_TRANSFORM、LAST_N_CHARS_RESOURCE_TRANSFORM）
```

### ACCESS 与 GOVERNANCE — 如何选择

两者在法律上都接受 Permit 和 Forbid。根据*哪个执行层应记录/审计规则*以及**提示词的字面要求**来选择：

| 用例 | 选择 | 理由 |
|---|---|---|
| 提示词明确命名为 "ACCESS 策略规则" / "access rule" / "OLS/FLS" | `ACCESS_POLICY_RULE_DEFINITION` | 与提示词的词汇匹配；位于数据访问执行层。 |
| 提示词命名为 "governance" / "audit" / "policy framework" / 数据驻留或合规性语言 | `GOVERNANCE_POLICY_RULE_DEFINITION` | 与提示词的词汇匹配；规则在治理报告中显示。 |
| 提示词模糊且仅描述允许/拒绝语义 | 默认为 Permit 选择 `ACCESS`，为 Forbid 选择 `GOVERNANCE`（镜像平台的自动填充默认值；安全且可部署，但**不强制要求**） |

> **重要 — 尊重提示词中的显式类别。** 如果提示词说 "ACCESS 策略规则拒绝…" 或 "GOVERNANCE 策略规则允许…"，请精确输出该类别。不要因为效果是 Forbid（或 Permit）而无声地切换到自动填充默认值。平台接受两者。代理不应覆盖用户的明确意图。

**范围 × 类别兼容性** — 此矩阵外的任何组合都会抛出 `INVALIDFORCATEGORY`：

|            | `ACCESS` | `GOVERNANCE` | `TRANSFORM` | `RECORD` |
|------------|:--------:|:------------:|:-----------:|:--------:|
| `ANY`      | Yes | Yes | No  | No  |
| `DATASPACE`| Yes | Yes | No  | No  |
| `FIELD`    | Yes | Yes | Yes | No  |
| `RECORD`   | No  | No  | No  | Yes |
| `SPAN`     | No  | No  | Yes | No  |

---

## 5. 条件模式（快速参考）

每个 `<conditions>` 块都需要**全部四个**：`<clause>`、`<operator>`、一个路径元素和值。

| 目标 | 路径元素 | 运算符 | 值 |
|------|-------------|----------|-------|
| 资源具有标签 | `<resourcePath>TAG</resourcePath>` | `CONTAINS_ANY` | `<valueReferenceType>CUSTOM_TAG` \| `STANDARD_TAG</valueReferenceType>` |
| 资源具有分类 | `<resourcePath>CLASSIFICATION</resourcePath>` | `CONTAINS_ANY` | `CUSTOM_CLASSIFICATION` \| `STANDARD_CLASSIFICATION` |
| 主体具有权限 | `<principalPath>ASSIGNED_PERMISSIONS_PATH</principalPath>` | `CONTAINS_ANY` \| `CONTAINS_NONE` | `<valueReferenceType>CUSTOM_PERMISSION</valueReferenceType>` |
| 会话在数据空间 | `<contextPath>SESSION_DATASPACE</contextPath>` | `CONTAINS_ANY` | `<valueReferenceType>DATASPACE</valueReferenceType>` |
| 记录字段 = 用户属性 | `<resourcePath>RECORDFIELD</resourcePath>` + `<valueDomain>Schema:field</valueDomain>` | `EQUALS` | `<valuePrincipalPath>USER_ID` \| `ORGANIZATION_ID` \| `USER_ROLE_ID</valuePrincipalPath>` |
| 实体类型检查 | `<resourcePath>ENTITYTYPE</resourcePath>` | `IS` | `<valueString>{"t":"Text","v":"FIELD"}</valueString>` |

`<conjunctionExpression>` 是 1 索引前缀表示法：`1`、`(AND 1 2)`、`(OR 1 2)`、`(AND (OR 1 2) (AND 3))`。一个裸的顶层索引（例如 `<conjunctionExpression>1</conjunctionExpression>`）可以无错误地部署 — 服务器端解析器接受顶层级别的裸标记。它**不是**部署时的验证错误。但它会导致 Data Governance Policy Builder 在加载时崩溃 — 参考 §7 如果 UI 可编辑性重要。

对于完整路径枚举（`RulePrincipalPathType`、`RuleResourcePathType`、`RuleContextPathType`）、运算符和 JSON 表达式（PROJECTION / ARGLIST / SOQLTARGETLISTEXPR），请参阅 [`references/policy-schema-full.md`](references/policy-schema-full.md)。 
对于所有策略变体的复制粘贴模板，请参阅 [`references/templates.md`](references/templates.md)。

---

## 6. 验证护栏

1. 每个 `<conditions>` 需要一个 `<operator>`。缺少运算符 → 拒绝。
2. 每个 `<conditions>` 需要至少一个路径元素（`<resourcePath>`、`<principalPath>`、`<contextPath>` 或 `<valueDomain>`）。
3. `<contextPath>` 专用于 `SESSION_DATASPACE`。永远不要将资源路径值放在这里。
4. 范围 × 类别必须在 §4 矩阵中。常见违规者：ACCESS/GOVERNANCE + RECORD 范围；RECORD + ANY/FIELD 范围；TRANSFORM + ANY/RECORD 范围。（效果除 TRANSFORM 外独立于类别 — 参考 §4。）
5. `<resourceTransform>` 和 `effect=Transform` 耦合。Transform 效果需要一个 resourceTransform。Permit/Forbid 必须没有。
6. `<policyRuleResourceDomains>` 对于 RECORD（RLS）和 FIELD 范围 TRANSFORM 是**必需**的；在 ACCESS/GOVERNANCE 上是**禁止**的。
7. `<conjunctionExpression>` 索引必须与实际 `<conditions>` 数量匹配。错一位 → 拒绝。
8. `<conditions>` 内部的 `<clause>` 必须与包装器（`WHEN` 在 `<when…>` 内，`UNLESS` 在 `<unless…>` 内）匹配。
9. `<valueString>` 中的 JSON 字面量必须将 `"` 转义为 `&quot;`。错误的转义会无声地损坏字面量。
10. 引用目标（`<valueReference>`、`<resourceDomain>`）必须在部署时目标组织中存在。
11. `SCALAR_ATTRIBUTE` / `PLURAL_ATTRIBUTE` 不在 `RulePrincipalPathType` 中 — 不在 MDAPI 合约中。对于这些形状，使用运行时 RuleProvider。
12. `IDENTIFIED_RECORD` 不能通过 MDAPI 编写 — `SESSION_CONSUMER_ID` 不在 `RuleContextPathType` 中。
13. 标准标签/分类开发名称是完全限定的点路径（例如 `DataGovernanceTags.ExternalData.Visibility.Public`）。在编写之前获取现有规则的准确字符串。
14. 最低 API 版本：`PolicyRuleDefinition` = 64.0；`PolicyJsonExpression` 条件 = 66.0；`<replicated>` = 260+；`<builderCompatible>` / `<builderValidated>` = 262+。

> **关于 `<conjunctionExpression>` 形状的说明：** 一个裸的顶层索引（例如 `<conjunctionExpression>1</conjunctionExpression>`）可以无错误地部署 — 服务器端解析器接受顶层级别的裸标记。它**不是**部署时的验证错误。但它会导致 Data Governance Policy Builder 在加载时崩溃 — 参考 §7。

---

## 7. UI 兼容性 — 核心规则

Data Governance Policy Builder 编辑 MDAPI 的**严格子集**。默认目标：生成 UI 兼容的策略。始终在生成 API-only XML 之前与操作员确认。

**硬性阻止器** — 任何这些都会使策略不可编辑（并且一些会在加载时崩溃 builder）：

- **在 ACCESS/GOVERNANCE 规则中缺少 OR-of-ENTITYTYPE 条件** → 硬性崩溃：`Cannot use 'in' operator to search for 'Permit' in undefined`。即使与 `TupleRead` 配对（在运行时功能上冗余），也需要包含 `IS` 条件 `{"t":"Text","v":"OBJECT"}` 和 `{"t":"Text","v":"FIELD"}`。
- **`<conjunctionExpression>` 中的裸顶层条件索引**（例如 `1`，或 `(AND (OR 1 2) 3)`）→ 在 `buildCriteria` 中加载时崩溃。部署不受影响，但策略在 UI 中不可编辑。如果 UI 可编辑性重要（§7），请始终包装：单个条件 `(AND 1)`；`(AND (OR 1 2) (AND 3))` 而不是 `(AND (OR 1 2) 3)`。
- `category = ACCESS_POLICY_RULE_DEFINITION` + `effect = Forbid` → **Data Governance Policy Builder UI**（不是 MDAPI）在保存时将其折叠为 GOVERNANCE；通过 builder 的往返会重写类别。MDAPI 部署不受影响 — 原始 ACCESS+Forbid 组合有效且无需修改即可部署。如果目标是 UI 往返性，对于 Forbid 优先选择 GOVERNANCE；如果源是 MDAPI，ACCESS+Forbid 很好。
- 任何 `<unlessPolicyRuleDefinitionClauseConjunction>` 块 → 在第一次 UI 保存时无声丢弃。
- 超过一个 `<action>` → 仅保留第一个。
- `ruleConsumer` ≠ `DATACLOUD` → UI 在保存时强制 DATACLOUD。
- 顶层 `(OR 1 2)` 联合 → 触发 `// ERROR: Unsupported rule!` 路径，规则无声丢弃。

**UI 兼容的 "unless" 重写：**

| 作者意图 | UI 兼容形状 |
|---|---|
| `unless principal has permission X` | `WHEN ASSIGNED_PERMISSIONS_PATH CONTAINS_NONE X` |
| `unless resource has tag X` | `WHEN TAG CONTAINS_NONE X` |
| `unless record field = value` | `WHEN RECORDFIELD NOT_EQUALS value` |

对于完整的 UI 兼容性清单、往返规则和操作员/路径支持矩阵，请参阅 [`references/ui-compatibility.md`](references/ui-compatibility.md)。

---

## 8. 编写工作流

1. **从最近的模板** 在 [`references/templates.md`](references/templates.md) 开始 — 从那里修改，不要空白开始。
2. **首先选择类别**（§4）。类别会固定效果、resourceScopeType，以及是否需要 policyRuleResourceDomains/resourceTransform。
3. **布置基本规则**：仅顶级字段，无条件。匹配 [`references/templates.md`](references/templates.md) 中的类别模板。
4. **逐个添加条件**，每个条件都带有全部四个锚点：`<clause>`、`<operator>`、一个路径元素和值。
5. **更新 `<conjunctionExpression>`** — 1 索引前缀表示法。裸顶层索引（例如 `1`）可以部署但会破坏 UI；如果 UI 可编辑性重要（§7），请包装为 `(AND 1)`。
6. **运行 UI 兼容性检查**（§7 / [`references/ui-compatibility.md`](references/ui-compatibility.md)）。如果任何项触发，首先尝试 "unless" 重写；如果不可能，则在继续之前获取操作员的明确确认。
7. **更新 `package.xml`** — 列出两种类型的每个 `<members>`。
8. **将 `<builderCompatible>`** 在集上设置为 `true`（如果 §7 清单通过）；`false`（如果故意 API-only）。
9. **在考虑完成之前，对照 §6（护栏）进行自检**。
10. **在向持久化组织进行任何非干运行部署之前，使用干运行进行验证**。使用 [`references/deploy-errors.md`](references/deploy-errors.md) 中的错误引用来显示错误。

**三层正确性检查** 在完成之前：
- **运行时执行** — 规则是否执行了预期的内容？（操作选择、条件形状）
- **MDAPI 部署有效性** — 是否可以部署？（§6 护栏、范围×类别、标签开发名称、组织权限）
- **UI 可编辑性** — 构建器能否渲染并重新保存它？（§7 清单、OR-of-ENTITYTYPE 要求）

---

## 9. 输出卫生 — 代理必须不对用户说的事情

代理的用户界面聊天响应伴随着每个生成的文件。客户永远不应该看到内部引擎或实现细节。

- **不要在用户界面文本中命名内部评估引擎** — 包括但不限于 `Cedar`、`policy engine`、`AuthZ engine`、`evaluation engine`、`Rego`、`OPA` 或类似名称。面向客户的表面是 *Data Governance*、*Policy Builder*、*Data Cloud Governance* — 仅使用这些术语。
- **不要发出尾随的“运行时工作原理”叙述**，这些叙述描述评估流程、主体-资源匹配语义或引擎内部条件排序。生成的文件是工件；部署的简要总结就足够了。如果用户明确询问执行如何工作，请使用产品术语描述（例如 "Data Governance 拒绝读取…"），永远不要使用引擎术语。
- **不要在用户界面文本中命名内部包、源目录、Java 类名、方法名或行号引用**。内部实现标识符不是面向客户的；仅使用产品术语指代平台行为（"服务器验证…"、"Data Governance 拒绝…"）。
- **除非用户询问，否则不要解释自动填充/默认填充/回退语义**。发送规则；仅在它们影响用户下一步需要做什么时才显示约束（例如 "DMO 标签在部署之前必须存在"）。

如果用户需要更多上下文，他们会询问 — 然后在产品语言中回复。
