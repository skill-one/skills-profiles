# 将 Dart 测试迁移到 Package Checks

当你需要将 Dart 测试套件从传统的 `package:matcher`（默认从 `package:test/test.dart` 导出）迁移到现代、类型安全且易于阅读的 `package:checks` 断言库时，请使用此技巧。

## 内容
- [何时使用此技巧](#何时使用此技巧)
- [如何使用此技巧（工作流程）](#如何使用此技巧工作流程)
- [关键语法差异和陷阱](#关键语法差异和陷阱)
- [Matcher到Checks映射表](#matcher到checks映射表)
- [没有直接替代的Matcher](#没有直接替代的matchers)
- [发现策略](#发现策略)
- [示例](#示例)

---

## 何时使用此技巧
- 当被要求“将测试迁移到checks”、“使用package:checks”或“现代化测试断言”时。
- 当更新传统测试套件，希望获得静态类型安全、IDE中更好的自动补全以及高度详细的错误诊断时。

---

## 如何使用此技巧（工作流程）

遵循此结构化工作流程，以安全且系统性地迁移测试套件：

### 1. 依赖项设置
- 在 `pubspec.yaml` 中将 `package:checks` 添加为 `dev_dependency`：
  ```bash
  dart pub add dev:checks
  ```
- 如果 `dev_dependencies` 下明确列出了 `package:matcher`，请移除它（它通常由 `package:test` 传递包含，这是可以的）。

### 2. 确定和规划目标文件
- 使用 [发现策略](#发现策略) 中的grep模式定位所有包含传统 `expect` 或 `expectLater` 调用的测试文件。
- 决定是全面迁移文件还是逐步迁移。

### 3. 迁移文件（逐步或全面）
针对任何目标测试文件：
1. **更新导入**：
   - 将通用的 `import 'package:test/test.dart';` 替换为：
     ```dart
     import 'package:test/scaffolding.dart';
     import 'package:checks/checks.dart';
     ```
   - **对于逐步迁移**：如果你只想迁移文件中的一些测试用例，或者想逐步迁移，请添加：
     ```dart
     import 'package:test/expect.dart'; // 暂时允许使用 legacy expect()
     ```
2. **转换断言**：根据 [关键语法差异和陷阱](#关键语法差异和陷阱) 和 [Matcher到Checks映射表](#matcher到checks映射表)，将传统的 `expect` 和 `expectLater` 调用重写为 `check` 语法。
3. **通过编译器验证**：如果全面迁移，请移除 `import 'package:test/expect.dart';` 行。任何剩余未迁移的 `expect` 调用将立即作为编译器错误出现，使它们易于查找和修复。

### 4. 验证和反馈循环
- **静态分析**：对目标包运行静态分析：
  ```bash
  dart analyze
  ```
  仔细关注 `.isA<Type>()` 上的泛型类型参数，并确保异步期望已正确等待（检查 `unawaited_futures` 警告）。
- **运行测试**：执行测试以验证行为和正确的断言运行时逻辑：
  ```bash
  dart test
  ```
  如果测试失败，请查看 `package:checks` 的非常详细的失败输出，以诊断测试是否确实失败，还是期望转换不正确。

---

## 关键语法差异和陷阱

> [!IMPORTANT]
> 行对行的转换有时可能会引入微妙的错误或错误的通过。请务必仔细审查这些关键差异：

### 1. 集合等价陷阱（`equals` vs `deepEquals`）
- **传统Matcher**：`expect(actual, expected)` 或 `expect(actual, equals(expected))` 在参数为集合（Lists、Maps、Sets）时执行**深度等价检查**。
- **Package Checks**：`.equals(expected)` 严格对应 `operator ==`。由于 Dart 集合没有重写 `operator ==` 以进行元素级比较，在集合上使用 `.equals` 将检查*身份*，并且在运行时几乎肯定会失败。
- **修复**：你必须将集合等价断言替换为 `.deepEquals(expected)`。
  ```dart
  // BEFORE (Matcher)
  expect(myList, [1, 2, 3]);

  // AFTER (Checks)
  check(myList).deepEquals([1, 2, 3]);
  ```

### 2. `reason` 参数现在是 `because`
- **传统Matcher**：解释作为 `expect` 的尾随命名参数 `reason` 传递：
  ```dart
  expect(actual, expectation, reason: 'Explanation');
  ```
- **Package Checks**：解释作为 `check` 函数*之前*的命名参数 `because` 传递：
  ```dart
  check(because: 'Explanation', actual).expectation();
  ```

### 3. 正则表达式匹配（`matches` vs `matchesPattern`）
- **传统Matcher**：`matches(pattern)` matcher 会自动将 `String` 参数转换为 `RegExp`（例如，`matches(r'\d')` 匹配 `'1'`）。
- **Package Checks**：`.matchesPattern(pattern)` 将 `String` 参数视为字面字符串模式。
- **修复**：要使用正则表达式匹配，你必须显式传递一个 `RegExp` 对象：
  ```dart
  // BEFORE (Matcher)
  expect(someString, matches(r'\d+'));

  // AFTER (Checks)
  check(someString).matchesPattern(RegExp(r'\d+'));
  ```

### 4. 属性提取（`TypeMatcher.having` vs `.has`）
- **传统Matcher**：链式字段/属性期望使用 `TypeMatcher.having(feature, description, matcher)`：
  ```dart
  expect(actual, isA<Person>().having((p) => p.name, 'name', startsWith('A')));
  ```
- **Package Checks**：`.has(feature, description)` 扩展可用于所有 `Subject`，参数更少，并返回一个新的 `Subject` 表示该属性。你可以直接从它链式期望：
  ```dart
  check(actual).isA<Person>().has((p) => p.name, 'name').startsWith('A');
  ```

### 5. 同步与异步 `throws`
- **传统Matcher**：在 `package:matcher` 中，`throwsA` 对同步闭包和包装在 `expect` 或 `expectLater` 中的异步future的行为类似。
- **Package Checks**：`.throws<E>()` 期望根据主题是同步还是异步而表现不同，并具有不同的返回类型：
  - **同步**（`Subject<T Function()>`）：`.throws<E>()` 同步返回一个 `Subject<E>`。这**不接受**回调参数！你直接在返回的 `Subject<E>` 上链式或级联期望：
    ```dart
    // YES (同步链式)
    check(() => triggerSyncError()).throws<ArgumentError>()
      ..has((e) => e.message, 'message').equals('invalid input');

    // NO (向同步 throws 传递回调将导致编译错误！)
    check(() => triggerSync").throws<ArgumentError>((it) => ...); // ERROR!
    ```
  - **异步**（`Subject<Future<T>>`）：`.throws<E>()` 返回 `Future<void>`。由于你不能直接在 `Future<void>` 上链式，这**需要**一个检查回调：
    ```dart
    // YES (异步回调)
    await check(triggerAsyncError()).throws<ArgumentError>((it) => it
      ..has((e) => e.message, 'message').equals('invalid input'));
    ```
  - **关键陷阱**：尝试在异步 `.throws<E>()` 后立即链式期望（例如，`await check(future).throws<E>().equals(...)`）将无法编译，因为它返回 `Future<void>`。

### 6. 正则表达式/模式等价
- **传统Matcher**：在 `package:matcher` 中，`expect(myPattern,` `equals(RegExp('Hello')))` 可以工作，因为matcher比较规则处理了 `RegExp` 实例。
- **Package Checks**：`.equals()` 使用严格的 Dart `==` 等价性。由于单独的 `RegExp` 实例不满足 `==`，使用 `.equals()` 将在运行时失败。
- **修复**：使用 `.isA<RegExp>()` 类型精炼，并结合级联显式断言 `RegExp` 对象的属性：
  ```dart
  check(myPattern).isA<RegExp>()
    ..has((r) => r.pattern, 'pattern').equals('Hello')
    ..has((r) => r.isMultiLine, 'isMultiLine').isTrue();
  ```

### 7. 严格的空值布尔安全（`bool?` 字段）
- **传统Matcher**：静态上，`isTrue` 和 `isFalse` 在运行时执行松散的动态检查，这会静默接受可空的布尔值 (`bool?`)。
- **Package Checks**：`.isTrue()` 和 `.isFalse()` 严格定义在 `Subject<bool>`（非可空）上。它们**不**可用于 `Subject<bool?>`。
- **修复**：对于声明为 `bool?` 的字段，你必须要么精炼主题（例如，`.isNotNull().isTrue()`），要么简单地使用 `.equals(true)` 和 `.equals(false)`，它们是通用的，适用于所有类型：
  ```dart
  // 如果 options.flagOutdated 是一个 bool?
  check(options.flagOutdated).equals(true);
  check(options.flagOutdated).equals(false);
  ```

### 8. 映射键包含（`containsKey` vs `contains`）
- **传统Matcher**：在 `package:matcher` 中，`contains(key)` 用于断言 `Map` 包含特定的键。
- **Package Checks**：在 `Subject<Map>` 上调用 `.contains(...)` 未定义，并将导致编译失败。
- **修复**：使用特定于映射的 `.containsKey(key)` matcher：
  ```dart
  // BEFORE (Matcher)
  expect(myMap, contains('my_key'));

  // AFTER (Checks)
  check(myMap).containsKey('my_key');
  ```

### 9. 显式泛型参数用于扩展类型
- **传统Matcher**：`expect(extensionTypeConst, 3)` 编译是因为松散的动态等价性。
- **Package Checks**：如果 `QrEciValue` 是 `int` 的扩展类型表示（例如，`extension type const QrEciValue(int value) implements int`），在 `Subject<QrEciValue>` 上调用 `.equals(3)` 会失败，因为 `3`（一个 `int`）不可分配给 `QrEciValue`。使用 `as int` 的强制转换将触发“不必要的强制转换”静态分析警告，因为 `QrEciValue` 静态实现了 `int`。
- **修复**：显式指定 `check` 函数上的泛型类型参数，以强制检查将其视为原始类型：
  ```dart
  // YES (类型安全且无警告)
  check<int>(QrEciValue.iso8859_1).equals(3);
  ```

### 10. 动态映射/JSON查找强制转换
- **传统Matcher**：松散的动态类型允许将嵌套的json查找静态类型为 `dynamic` 直接与列表或映射比较。
- **Package Checks**：严格的类型安全性拒绝了 `dynamic` 到 `Iterable<Object?>` 的隐式赋值，在 `.deepEquals(...)` 中。
- **修复**：静态强制转换动态查找结果为 `List` 或 `Map`：
  ```dart
  // YES (显式强制转换为 List)
  check(myIterable).deepEquals(json['data']['items'] as List);
  ```

---

## Matcher到Checks映射表

使用此表作为快速参考，直接替换matcher：

| Legacy Matcher | Package Checks Equivalent | Notes |
| :--- | :--- | :--- |
| `expect(actual, expected)` | `check(actual).equals(expected)` | 使用 `.deepEquals` 对于集合！ |
| `expect(actual, equals(expected))` | `check(actual).equals(expected)` | 使用 `.deepEquals` 对于集合！ |
| `isA<T>()` | `check(actual).isA<T>()` | 支持直接链式 |
| `same(expected)` | `check(actual).identicalTo(expected)` | 验证身份 |
| `anyElement(matcher)` | `check(iterable).any(conditionCallback)` | 例如 `check(list).any((e) => e.equals(1))` |
| `everyElement(matcher)` | `check(iterable).every(conditionCallback)` | 例如 `check(list).every((e) => e.isGreaterThan(0))` |
| `hasLength(expected)` | `check(actual).length.equals(expected)` | 适用于 String、Map、Iterable 等 |
| `isNot(matcher)` | `check(actual).not(conditionCallback)` | 例如 `check(val).not((it) => it.equals(5))` |
| `contains(element)` | `check(actual).contains(element)` | 适用于 String、Iterable（使用 `containsKey` 对于 Map！） |
| `contains(key)` (on a Map) | `check(map).containsKey(key)` | 映射键包含 |
| `startsWith(prefix)` | `check(string).startsWith(prefix)` | 仅适用于 String |
| `endsWith(suffix)` | `check(string).endsWith(suffix)` | 仅适用于 String |
| `isEmpty` | `check(actual).isEmpty()` | 适用于 String、Map、Iterable |
| `isNotEmpty` | `check(actual).isNotEmpty()` | 适用于 String、Map、Iterable |
| `isNull` | `check(actual).isNull()` | |
| `isNotNull` | `check(actual).isNotNull()` | |
| `isTrue` / `true` | `check(actual).isTrue()` | 仅适用于非可空的 `bool` |
| `isFalse` / `false` | `check(actual).isFalse()` | 仅适用于非可空的 `bool` |
| `completion(matcher)` | `await check(future).completes(conditionCallback)` | 必须被等待！ |
| `throwsA(matcher)` | `await check(future).throws<Type>()` | 必须被等待！ |
| `emits(value)` | `await check(streamQueue).emits(conditionCallback)` | 必须被等待！ |
| `emitsThrough(value)` | `await check(streamQueue).emitsThrough(conditionCallback)` | 必须被等待！ |
| `stringContainsInOrder(list)` | `check(string).containsInOrder(list)` | 仅适用于 String |
| `pairwiseCompare(...)` | `check(actual).pairwiseMatches(...)` | |

---

## 没有直接替代的Matcher

由于API清理，一些传统matcher在 `package:checks` 中没有一对一的等效项。使用这些标准修复方法：

### 1. 特定错误Matcher
- **传统**：`throwsArgumentError`、`throwsStateError`、`throwsUnsupportedError` 等。
- **Checks**：使用 `.throws<T>()` 与特定的错误类型：
  ```dart
  await check(triggerError()).throws<ArgumentError>();
  ```

### 2. `anything` Matcher
- **传统**：`expect(actual, anything)`
- **Checks**：当需要条件时传递空条件回调 `(_) {}`：
  ```dart
  await check(someFuture).completes((_) {});
  ```

### 3. 特定数值切换
- **传统**：`isPositive`、`isNegative`、`isZero`、`isNonPositive`、`isNonNegative`、`isNonZero`
- **Checks**：使用显式比较期望：
  - `isPositive` $\rightarrow$ `isGreaterThan(0)`
  - `isNegative` $\rightarrow$ `isLessThan(0)`
  - `isZero` $\rightarrow$ `equals(0)`
  - `isNonNegative` $\rightarrow$ `isGreaterOrEqual(0)`

### 4. 数值范围
- **传统**：`inClosedOpenRange(min, max)`、`inInclusiveRange(min, max)` 等。
- **Checks**：使用级联操作符 (`..`) 链式边界：
  ```dart
  check(actualValue)
    ..isGreaterOrEqual(min)
    ..isLessThan(max);
  ```

---

## 编写自定义期望（替换自定义Matcher）

当从传统代码库迁移时，你可能会遇到自定义 `Matcher` 子类。在 `package:checks` 中，自定义断言作为 `Subject<T>` 的 `extension` 方法实现。

要编写自定义期望，你必须导入检查上下文API：
```dart
import 'package:checks/context.dart';
```

### 1. 简单自定义期望（使用 `expect`）
使用 `context.expect` 检查属性，并在失败时返回 `Rejection`：
```dart
extension CustomPersonChecks on Subject<Person> {
  void isAdult() {
    context.expect(
      () => ['is an adult (age >= 18)'],
      (actual) {
        if (actual.age >= 18) return null; // 通过
        return Rejection(
          which: ['is only ${actual.age} years old'],
        );
      },
    );
  }
}
```

### 2. 嵌套属性提取（使用 `nest` 或 `has`）
要提取属性并允许进一步链式检查，使用 `nest` 或更简单的 `has` 帮助程序：
- **使用 `has`（推荐用于简单的、非失败的字段访问）**：
  ```dart
  extension CustomPersonChecks on Subject<Person> {
    Subject<Address> get address => has((p) => p.address, 'address');
  }
  ```
- **使用 `nest`（用于可能失败或拒绝的属性提取）**：
  ```dart
  extension CustomPersonChecks on Subject<Person> {
    Subject<String> get ssn => context.nest(
      'has a valid SSN',
      (actual) {
        final ssnValue = actual.ssn;
        if (ssnValue == null) {
          return Extracted.rejection(which: ['has no SSN']);
        }
        return Extracted.value(ssnValue);
      },
    );
  }
  ```

### 3. 异步自定义期望
如果期望是异步的（例如，检查 Future 或 Stream），使用 `context.expectAsync` 或 `context.nestAsync` 并返回结果 `Future`：
```dart
extension CustomFutureChecks<T> on Subject<Future<T>> {
  Future<void> completesNormally() {
    return context.expectAsync(
      () => ['completes without throwing'],
      (actual) async {
        try {
          await actual;
          return null; // 通过
        } catch (e) {
          return Rejection(which: ['threw $e']);
        }
      },
    );
  }
}
```

---

## 发现策略

在终端执行这些命令，以识别需要迁移的传统matcher和文件：

```bash
# 1. 查找包含传统 expect() 或 expectLater() 的所有测试文件
grep -rn "expect(" test/
grep -rn "expectLater(" test/

# 2. 查找潜在的集合等价陷阱（字面列表或映射）
grep -rn "expect(.*, \[" test/
grep -rn "expect(.*, {" test/

# 3. 查找 matches() 调用（需要转换为 RegExp + matchesPattern）
grep -rn "matches(" test/

# 4. 查找传统 TypeMatcher.having() 调用（需要转换为 .has()）
grep -rn "having(" test/
```

---

## 示例

### 基本断言
**Before (Matcher):**
```dart
expect(someValue, isNotNull);
expect(result, isTrue, reason: 'should be successful');
expect(myString, startsWith('hello'));
```

**After (Checks):**
```dart
check(someValue).isNotNull();
check(because: 'should be successful', result).isTrue();
check(myString).startsWith('hello');
```

### 集合和深度等价
**Before (Matcher):**
```dart
expect(items, [1, 2, 3]);
expect(configMap, equals({'port': 8080}));
```

**After (Checks):**
```dart
check(items).deepEquals([1, 2, 3]);
check(configMap).deepEquals({'port': 8080});
```

### 链式和级联
**Before (Matcher):**
```dart
expect(someString, allOf([
  startsWith('a'),
  contains('b'),
  endsWith('c'),
]));
```

**After (Checks):**
```dart
check(someString)
  ..startsWith('a')
  ..contains('b')
  ..endsWith('c');
```

### 复杂属性匹配（has）
**Before (Matcher):**
```dart
expect(response, isA<Response>()
    .having((r) => r.statusCode, 'statusCode', 200)
    .having((r) => r.body, 'body', contains('success')));
```

**After (Checks):**
```dart
check(response).isA<Response>()
  ..has((r) => r.statusCode, 'statusCode').equals(200)
  ..has((r) => r.body, 'body').contains('success');
```

### 异步 Future
**Before (Matcher):**
```dart
expect(fetchData(), completes);
expect(fetchData(), completion(equals('data')));
expect(failingCall(), throwsA(isA<StateError>()));
```

**After (Checks):**
```dart
await check(fetchData()).completes();
await check(fetchData()).completes((it) => it.equals('data'));
await check(failingCall()).throws<StateError>();
```

### 异步 Stream
**Before (Matcher):**
```dart
var queue = StreamQueue(Stream.fromIterable([1, 2, 3]));
await expectLater(queue, emitsInOrder([1, 2, 3]));
```

**After (Checks):**
```dart
var queue = StreamQueue(Stream.fromIterable([1, 2, 3]));
await check(queue).inOrder([
  (s) => s.emits((e) => e.equals(1)),
  (s) => s.emits((e) => e.equals(2)),
  (s) => s.emits((e) => e.equals(3)),
]);
```
