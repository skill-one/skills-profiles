---
name: assertion-quality
description: 分析现有测试中的断言质量、深度、多样性以及虚假自信。当被问及关于薄弱、浅显、琐碎、始终为真、自我引用、无断言、仅检查存在/真值或多样性不足的断言时，必须使用，包括 MSTest、Jest、pytest 和 Go。不应用于直接修复：编写 MSTest 测试负责提供的 MSTest 断言；代码测试代理负责新案例。当被问及测试是否会捕获生产环境变更时，使用 test-gap-analysis，使用 test-anti-patterns 进行一般严重性排序的审计。
---

# 断言多样性分析

分析任何支持语言的测试代码，以衡量断言的多样性和意义。生成一个指标报告，揭示测试是否验证了正确性的不同方面——不仅仅是“输出等于X”，还包括结构、异常、状态转换、副作用和不变式。

> **语言特定指南**：调用 `test-analysis-extensions` 技能以发现可用的扩展文件，然后阅读与目标代码库的语言和框架匹配的文件（例如，`.NET` 的 `dotnet.md`，`pytest` 的 `python.md`，`Jest` 的 `typescript.md`，标准 `testing` 包的 `go.md`）。你必须在使用第3步分类断言之前阅读相关的扩展文件，因为断言API在不同的框架中差异很大。

## 断言多样性为何重要

低断言多样性表明测试不深入。测试可能通过，而错误隐藏在未断言的逻辑中。常见症状：

| 问题 | 症状 | 后果 |
|------|------|------|
| 简单断言 | 测试只包含 `Assert.IsNotNull(result)` / `assert result is not None` / `expect(x).toBeDefined()` | 测试通过但未验证正确性 |
| 单值痴迷 | 总是检查一个字段或返回值 | 未断言逻辑中的错误会溜走 |
| 无负断言 | 从不检查不应发生的情况 | 通过假阳性滑入回归 |
| 无状态检查 | 不验证对象状态变化 | 错过副作用或生命周期问题 |
| 无结构检查 | 只断言顶层值 | 嵌套对象中的错误未被注意到 |
| 无断言测试 | 调用但不验证的测试 | 代码覆盖率是虚假的 |

## 何时使用

- 用户要求评估断言质量或深度
- 用户问“我的测试是否真的在测试有意义的东西？”
- 用户想知道测试断言是否过于浅显或简单
- 用户要求断言覆盖率指标或多样性分析
- 用户怀疑测试虽然通过但给出虚假信心
- `code-testing-generator` 代理（或任何测试生成工作流）在生成的新测试上调用此技能作为完成前的自我审查步骤，在声明运行完成之前

## 何时不使用

- 用户想编写新测试（使用任何语言的 `code-testing-agent`，或特定于 MSTest 的 `writing-mstest-tests`）
- 用户想检测断言之外的抗模式（使用 `test-anti-patterns`）
- 用户想修复或重写断言（直接帮助他们）
- 用户询问代码覆盖率百分比（超出范围——这分析断言质量，而不是行覆盖率）

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 测试代码 | 是 | 一个或多个测试文件或要分析的测试项目目录 |
| 生产代码 | 否 | 要测试的代码，以评估断言是否覆盖了重要行为 |

## 工作流程

### 第1步：检测语言并加载扩展

识别目标代码库的语言和测试框架。调用 `test-analysis-extensions` 技能并阅读匹配的扩展文件（例如，`.NET` 的 `extensions/dotnet.md`，`pytest` 的 `extensions/python.md`，`Jest/Vitest` 的 `extensions/typescript.md`，`Go` 的 `extensions/go.md`）。扩展文件列出了你在第3步中将分类的框架特定断言API。

### 第2步：收集测试代码

读取用户提供的所有测试文件。如果用户指向一个目录或项目，使用语言扩展文件中的标记扫描所有测试文件（例如，MSTest 的 `[TestMethod]`，pytest 的 `def test_*`，Jest 的 `it()` / `test()`，Go 的 `func TestXxx`）。

### 第3步：分类每个断言

对于每个测试方法，识别所有断言并将它们分类到以下语言无关的类别中：

| 类别 | 验证的内容 | 不同语言的示例 |
|------|-----------|----------------|
| **相等性** | 返回值与预期匹配 | `Assert.AreEqual` (MSTest), `Assert.Equal` (xUnit), `assert x == y` (pytest), `expect(x).toBe(y)` (Jest), `assertEquals` (JUnit), `if got != want { t.Error... }` / `assert.Equal(t, want, got)` (Go), `x shouldBe y` (Kotest), `Should -Be` (Pester), `EXPECT_EQ` (GoogleTest) |
| **布尔值** | 条件成立 | `Assert.IsTrue`, `assert flag` (Python), `expect(x).toBeTruthy()` (Jest), `assertTrue` (JUnit), `assert.True(t, ok)` (testify), `x.shouldBeTrue()` (Kotest), `Should -BeTrue` (Pester), `EXPECT_TRUE` |
| **空 / None / Nil** | 值的存在/缺失 | `Assert.IsNull` (.NET), `assert x is None` (pytest), `expect(x).toBeNull()` (Jest), `assertNull` (JUnit), `assert.Nil(t, v)` (testify), `XCTAssertNil` (XCTest), `Should -BeNullOrEmpty` (Pester) |
| **异常 / 错误** | 错误处理行为 | `Assert.Throws<T>()`, `pytest.raises(E)`, `expect(fn).toThrow(E)`, `assertThrows<E>`, `assert.Error(t, err)` / `assert.ErrorIs`, `#[should_panic]` (Rust), `XCTAssertThrowsError`, `Should -Throw`, `EXPECT_THROW` |
| **类型检查** | 运行时类型正确性 | `Assert.IsInstanceOfType`, `assert isinstance(x, T)`, `expect(x).toBeInstanceOf(T)`, `assertInstanceOf`, `assert.IsType(t, T{}, v)`, `assert!(matches!(value, Pattern))` (Rust), `Should -BeOfType` |
| **字符串** | 文本内容和格式 | `StringAssert.Contains`, `assert sub in s`, `expect(s).toMatch(/x/)`, `assertTrue(s.contains(...))`, `assert.Contains(t, s, sub)`, `s shouldContain sub`, `Should -Match`, `EXPECT_THAT(s, HasSubstr(...))` |
| **集合** | 集合内容和结构 | `CollectionAssert.Contains`, `assert item in collection`, `expect(arr).toContain(x)`, `assertIterableEquals`, `assert.Contains(t, slice, item)`, `col shouldContainExactly listOf(...)`, `Should -Contain`, `EXPECT_THAT(c, ElementsAre(...))` |
| **比较** | 排序和大小 | `Assert.IsTrue(x > y)`, `Is.GreaterThan`, `assert x > y`, `expect(x).toBeGreaterThan(y)`, `assertTrue(x > y)`, `assert.Greater(t, x, y)` (testify) |
| **近似值** | 浮点数或容差 | `Assert.AreEqual(expected, actual, delta)`, `pytest.approx(y)`, `expect(x).toBeCloseTo(y)`, `assertEquals(x, y, delta)`, `assert.InDelta(t, x, y, delta)`, `EXPECT_NEAR`, `EXPECT_DOUBLE_EQ` |
| **负断言** | 不应发生的情况 | `Assert.AreNotEqual`, `assert x != y`, `expect(x).not.toBe(y)`, `assertNotEquals`, `assert.NotEqual(t, x, y)`, `refute` (Minitest / Ruby), `Should -Not -Be` |
| **状态 / 副作用** | 状态转换和副作用 | 对象属性在修改后的断言；模拟调用验证：`mock.Verify(...)` (Moq), `mock_method.assert_called_with(...)` (Python `unittest.mock`), `expect(mock).toHaveBeenCalledWith(...)` (Jest), `verify(mock).method(...)` (Mockito), `Should -Invoke` (Pester), `expect { code }.to change(obj, :attr)` (RSpec) |
| **结构 / 深度** | 深度对象正确性 | `Assert.AreEqual` 与丰富等价类型，`assertThat(obj).usingRecursiveComparison()` (AssertJ), `.toEqual({...})` (Jest 深度等价), `cmp.Diff` (Go go-cmp), 快照测试 (`.toMatchSnapshot()`, `syrupy`, `SnapshotTesting`), `assertThat(col).extracting(...)` (AssertJ 链) |

一个断言可以属于多个类别（例如，`Assert.AreNotEqual` 是相等性和负断言；`expect(mock).toHaveBeenCalledWith(...)` 是状态/副作用和特定调用断言）。

阅读加载的语言扩展文件以获取特定框架的断言API的确切列表。

### 第4步：计算指标

为测试套件计算以下指标：

#### 每个测试的指标
- **断言计数**：每个测试方法中的断言数量
- **断言类别**：每个测试使用的类别

#### 套件范围的指标
- **每个测试的平均断言数**：总断言数 / 总测试方法数
- **断言类型分布**：套件中使用的不同断言类别数量（12个类别中）
- **无断言的测试**：没有断言的测试方法数量和百分比
- **只有简单断言的测试**：每个断言都是空检查或 `Assert.IsTrue(true)` 的测试数量和百分比——简单意味着没有有意义的值验证
- **自引用断言的测试**：断言将输入与自身或身份转换版本进行比较的测试数量和百分比（例如，`Assert.AreEqual(input, Parse(input.ToString()))`）或断言字段与其自身（`Assert.AreEqual(dto.Name, dto.Name)`）。这些是同义语——它们验证了管道，而不是行为。
- **负断言的测试**：数量和百分比（目标：至少10%的测试应验证不应发生的情况）
- **异常断言的测试**：数量和百分比
- **状态/副作用断言的测试**：数量和百分比
- **结构/深度断言的测试**：数量和百分比
- **单类别测试**：使用单个断言类别的测试数量和百分比

### 第5步：应用校准规则

在报告之前校准结果：

- **在描述其弱点之前评估匹配器谓词**。对于每个弱断言，命名一个现实中的有缺陷的值或行为，该值仍然满足该精确的谓词。对于每个被计为有意义的断言，命名它固定了的行为。如果你无法从测试和可用的生产合同中给出这样的反例，请不要推测断言是弱的。
- **简单意味着真正简单**。单独的空/None/nil 检查是简单的 (`Assert.IsNotNull(result)`, `assert result is not None`, `expect(x).toBeDefined()`)。但空检查后跟有意义的值断言不是简单的——空检查是真实断言前的保护。只有当测试没有有意义的值断言时，才将其标记为“简单”。
- **使用精确的 Jest 语义**。`toBeDefined()` 仅拒绝 `undefined`；`null` 满足它，但仅在 `null` 是一个现实的合同破坏结果时才提及。`toMatchObject(expected)` 结构性地验证预期子集；它既不能证明对象身份，也不能证明完整对象等价。永远不要声称它能做到。
- **检查有意义条件的布尔断言不是简单的**。`Assert.IsTrue(result.IsValid)` / `assert result.is_valid` / `expect(result.isValid).toBe(true)` 检查特定属性——这些是布尔断言，而不是简单的断言。总是为真的断言 (`Assert.IsTrue(true)`, `assert True`, `expect(true).toBe(true)`) 是简单的。
- **精确构造和映射检查是有意义的**。一个构建对象并固定每个请求属性到独立预期字面量的测试可以捕获交换、丢失或错误分配的值。不要仅仅因为实现是构造函数、记录、属性映射或内存存储而降低其等级。
- **考虑测试的意图**。对于空方法的测试，即使它只使用一个布尔断言，验证依赖项上的状态变化也是合法的。
- **异常测试本质上断言计数低**。`Assert.ThrowsException<T>(() => ...)` / `with pytest.raises(E): ...` / `expect(fn).toThrow(E)` / `#[should_panic]` 可能是唯一的断言——这对异常焦点测试来说很好。不要因为断言计数低而惩罚它们。
- **模拟调用验证和裸断言形式计算在内**。将 `verify(mock).method(...)` (Mockito), `expect(mock).toHaveBeenCalledWith(...)` (Jest), `Should -Invoke` (Pester), `bare assert` (pytest), `if got != want { t.Errorf(...) }` (Go) 都视为适当类别的真实断言。不要将它们视为缺失框架API的气味。
- **快照断言** (`.toMatchSnapshot()`, `syrupy`, `SnapshotTesting`) 计算为结构/深度断言。单独标记陈旧或从未更新的快照。
- **属性基础测试** (`@given` Hypothesis, `proptest!`, `forAll` Kotest) 通过生成的用例隐式生成断言——计算内部断言逻辑，而不是外部脚手架。
- **不要将多样性与数量混淆**。具有20个相等性断言的测试具有高数量但低多样性。具有一个相等性、一个空检查和一个异常断言的测试具有低数量但良好的多样性。
- **自引用断言不是有意义的相等性检查**。断言输出等于输入的循环看起来像真实的相等性断言，但当测试的操作是身份时是同义语。将它们与正常相等性断言分开标记。如果测试的*目的*是验证循环（序列化/反序列化，编码/解码），断言是有效的——但它应该伴随着对非平凡输入的断言，以执行转换。
- **将建议与命名行为匹配**。格式化测试应固定精确的格式化表示，验证测试需要拒绝的输入，并且循环测试需要执行转义、空/空处理或另一个转换边界的输入。对于每个无断言的创建/更新/删除操作，建议其特定的返回值或可观察的后置条件，而不是一个通用的“检查状态”补救措施。
- **如果断言多样化良好，请这样说**。一个得出套件具有良好多样性的报告是完全有效的。

### 第6步：报告结果

**根据套件的大小和复杂性调整报告深度**。以下结构是大量套件（大约15个以上测试或多文件项目）的完整模板。对于小而简单的输入（单个文件只有少量测试），不要发出每个部分——在简单输入上的填充多部分仪表板读起来像噪音，并掩盖了答案。相反，直接简洁地回答用户的问题：哪些测试是无断言的或只有简单断言，整体断言质量结论，以及具体建议（仍然区分有意冒烟测试和伪装成真实验证的测试）。仅使用对当前输入具有真实信号的章节；一个简短的指标摘要加上无断言列表和建议通常就足够了。永远不要省略与评分相关的实质内容（无断言/简单识别、质量结论和具体建议）——仅修剪添加无信息的结构性开销。

对于包含五到八个测试的文件，默认为一个结论加上一个紧凑的每个测试表。省略类别分布仪表板和假设性失败模式，除非调用者要求指标。仅陈述断言谓词和可用生产行为支持的反例。

以以下结构呈现分析：

1. **摘要仪表板**——关键指标的快速参考表：
   ```
   | 指标                        | 值  | 评估 |
   |-------------------------------|-----|------|
   | 总测试                     | 25  | —    |
   | 每个测试的平均断言数        | 2.4 | 中等 |
   | 断言类型分布               | 5/12 | 低   |
   | 无断言的测试               | 3 (12%)| 令人担忧 |
   | 只有简单断言的测试         | 4 (16%)| 可接受 |
   | 负断言的测试               | 2 (8%) | 低于目标 |
   | 单类别测试                 | 15 (60%)| 高   |
   ```

2. **类别分解**——对于每个断言类别，显示：
   - 使用它的测试数量
   - 代码中的代表性示例
   - 相对于要测试的代码是否过度使用或使用不足

3. **差距分析**——基于生产代码（如果可用），识别：
   - 仅使用相等性检查测试的行为
   - 没有异常断言的错误路径
   - 没有状态验证的状态更改方法
   - 返回但未检查内容的集合

4. **建议**——优先级改进列表：
   - 哪些测试将从额外的断言类型中受益最多
   - 哪些断言类别缺失以及它们为何重要
   - 可以添加的具体断言示例

5. **无断言测试** — 如果存在，请列出每个测试及其方法名以及它看似在测试的内容，以便用户决定是否添加断言或将它们标记为有意为之的冒烟测试。

## 验证

- [ ] 测试套件中的每个断言都被归类到至少一个类别
- [ ] 指标计算正确（计数相加）
- [ ] 简单断言测试被正确识别（未过度标记）
- [ ] 异常测试因断言计数低而被惩罚
- [ ] 对有意义属性的真值断言不被归类为简单
- [ ] 每个弱断言声明都包含一个真实反例，该反例会被精确匹配器接受
- [ ] Jest 匹配器语义精确（`toBeDefined` 与 `undefined`；`toMatchObject` 子集匹配与身份/完全等价）
- [ ] 建议 具体（指定测试方法名称并建议具体的断言类型）
- [ ] 如果套件具有良好多样性，报告应承认这一点

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 因断言计数低而惩罚异常测试 | 异常断言本身是完整的 — 跳过这些测试的计数警告 |
| 在值检查之前将 null/None/nil 检查标记为简单 | 仅标记 null/None/nil 检查是**唯一**断言的测试 |
| 将任何真值断言计为简单 | 仅始终为真的断言（`Assert.IsTrue(true)`，`assert True`，`expect(true).toBe(true)`）是简单的 |
| 忽略框架差异 | 每个框架都有独特的断言 API — 始终先阅读匹配的语言扩展。MSTest 的 `Assert.AreEqual`，xUnit 的 `Assert.Equal`，NUnit 的 `Is.EqualTo`，pytest 的裸 `assert ==`，Jest 的 `expect().toBe()`，Go 的 `if … { t.Error… }` 都映射到 **等价** 类别 |
| 将裸断言形式视为缺少框架 | 裸 `assert`（pytest），`if got != want { t.Error... }`（Go），和 `assert!()`（Rust）都是规范形式 — 在正确的类别中计数 |
| 将模拟调用验证视为无断言 | `verify(mock).method(...)`，`expect(mock).toHaveBeenCalledWith(...)`，`Should -Invoke` 是状态/副作用断言 |
| 为了多样性而推荐多样性 | 仅建议添加会在被测试代码中捕获真实错误的断言类型 |
| 遗漏隐式断言 | 异常断言既是异常也是否定；快照/属性基础测试是具有隐式结构的真实断言 |
| 带有未等待断言的异步测试 | TUnit、Jest 带有 `.resolves`/`.rejects`、pytest-asyncio、Swift Testing 和 Kotest 都会静默通过未 `await` 的断言的测试 — 即使存在断言调用，也将其视为无断言 |
