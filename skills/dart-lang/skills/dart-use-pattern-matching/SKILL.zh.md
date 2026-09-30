---
name: dart-use-pattern-matching
description: 使用 Dart 3 的模式匹配、switch 表达式和解构惯用法来验证数据模式、处理代数数据类型以及分解控制流。在重构复杂的 if-else 链、解析多态 JSON 或 API 响应、解构列表、URI/路径段、String.split() 令牌、记录或映射，或对密封类执行穷尽性检查时使用。不要用于简单的布尔条件、单变量类型提升（使用 `is`）或基本的集合过滤。
---

# 实现 Dart 模式

## 目录
- [模式选择策略](#模式选择策略)
- [switch 语句与表达式](#switch-语句与表达式)
- [核心模式实现](#核心模式实现)
- [实用平衡与反模式](#实用平衡--反模式)
- [工作流程](#工作流程)
- [示例](#示例)

## 模式选择策略

根据数据结构和预期结果应用特定的模式类型。遵循以下条件指南：

*   **如果验证和提取来自反序列化数据（例如 JSON）：** 使用 Map、List 和 Object 模式来验证模式结构并在单个步骤中解构属性。
*   **如果检查 URL/路径段（`uri.pathSegments`、`p.split(path)`）或 `String.split()` 令牌：** 使用带有 rest 元素的 List 模式（`['api', 'comments', ...]`、`['assets', ...final rest]`、`[..., final parent, _]`）而不是手动 `.length` 检查、`.first`、`.skip(1)` 或 `length - N` 索引运算。
*   **如果处理多态有效负载或响应：** 使用 `switch` 表达式而不是 map 判别键来反序列化为 `sealed` 类层次结构。
*   **如果处理多个返回值：** 使用 Record 模式直接将字段解构到本地变量。
*   **如果执行类型特定行为（代数数据类型）：** 使用 Object 模式结合 `sealed` 类来确保穷尽性。
*   **如果匹配数值范围或条件：** 在 switch 臂中使用关系（`>=`、`<=`）和逻辑与（`&&`）模式。
*   **如果多个 case 共享逻辑：** 使用逻辑或（`||`）模式来共享单个 case 身体或守卫子句。
*   **如果忽略特定值：** 在集合中使用通配符模式（`_`）或非匹配的 Rest 元素（`...`）。

## switch 语句与表达式

根据执行上下文选择适当的 switch 结构：

*   **如果生成值：** 使用 **switch 表达式**。
    *   语法：`switch (value) { pattern => expression, }`
    *   规则：每个 case 必须是单个表达式。没有隐式向下传递。必须穷尽。
*   **如果执行语句或副作用：** 使用 **switch 语句**。
    *   语法：`switch (value) { case pattern: statements; }`
    *   规则：空 case 会向下传递到下一个 case。非空 case 会隐式中断（不需要 `break` 关键字）。

## 核心模式实现

使用以下语法和规则实现模式：

*   **逻辑或 (`||`):** `pattern1 || pattern2`。两个分支必须定义完全相同的变量集。
*   **逻辑与 (`&&`):** `pattern1 && pattern2`。分支不应定义重叠的变量。
*   **关系：** `==`、`!=`、`<`、`>`、`<=`、`>=` 后跟常量表达式。
*   **强制转换 (`as`):** `pattern as Type`。如果值不匹配类型则抛出异常。用于在解构期间强制断言类型。
*   **空值检查 (`?`):** `pattern?`。如果值为 null 则匹配失败。将变量绑定到非空基本类型。
*   **空值断言 (`!`):** `pattern!`。如果值为 null 则抛出异常。
*   **变量：** `var name` 或 `Type name`。将匹配的值绑定到新的本地变量。
*   **通配符 (`_`):** 匹配任何值并忽略它。
*   **List：** `[pattern1, pattern2]`。匹配长度精确的列表，除非使用 Rest 元素（`...` 或 `...var rest`）。
*   **Map：** `{"key": pattern}`。匹配包含指定键的 map。忽略未匹配的键。
*   **Record：** `(pattern1, named: pattern2)`。匹配形状精确的记录。使用 `:var name` 推断 getter 名称。
*   **Object：** `ClassName(field: pattern)`。匹配 `ClassName` 的实例。使用 `:var field` 推断 getter 名称。

## 实用平衡与反模式

模式匹配和 switch 表达式应简化代码，而不是增加语法开销。注意以下边界：

### 1. 优先使用 `is` 类型提升而不是 `if-case` 处理单个可提升变量
在检查或提升单个变量时，使用标准的 `is` 检查，而不是引入阴影别名（shadow aliases）的 `if-case` 模式。

*   **推荐：**
    ```dart
    // ✅ 直接原地提升 `key` 而无需额外变量
    for (final MapEntry(:key, :value) in map.entries) {
      if (key is String && value != null) {
        process(key, value);
      }
    }
    ```
*   **避免：**
    ```dart
    // ❌ 反模式：引入不必要的别名变量 `k`
    for (final MapEntry(:key, :value) in map.entries) {
      if (key case final String k when value != null) {
        process(k, value);
      }
    }
    ```

### 2. 在 switch 臂中合并可空类型
当映射或返回值时，如果 `null` 和类型 `T` 都有效且处理方式相同，直接匹配可空类型 `T?` 而不是创建冗余的 `null` 臂。

*   **推荐：**
    ```dart
    // ✅ 干净的可空模式匹配
    switch (value) {
      final String? s => s,
      _ => throw FormatException('无效值: $value'),
    }
    ```
*   **避免：**
    ```dart
    // ❌ 冗余的单独 null 臂
    switch (value) {
      final String s => s,
      null => null,
      _ => throw FormatException('无效值: $value'),
    }
    ```

### 3. 保持快速失败验证（不要无声地丢弃数据）
不要在循环或反序列化中使用 `if-case` 来过滤元素，如果数据损坏应触发错误或诊断警告。

*   **推荐：**
    ```dart
    // ✅ 快速失败并显式诊断错误
    for (final raw in rawTasks) {
      if (raw is! Map<String, dynamic>) {
        throw FormatException('期望 Map 项目，实际为 ${raw.runtimeType}: $raw');
      }
      _applyTask(raw);
    }
    ```
*   **避免：**
    ```dart
    // ❌ 无声地忽略损坏的项目
    for (final raw in rawTasks) {
      if (raw case final Map<String, dynamic> taskMap) {
        _applyTask(taskMap);
      }
    }
    ```

### 4. 避免 单 case 或布尔 switch
*   使用 `if (x is T)` 而不是只有一个 case 和 `default: break;` 的 switch 语句。
*   使用标准条件三元运算符（`condition ? a : b`）而不是 `switch (condition) { true => a, false => b }`。

### 5. 避免 过度使用 Object 解构
使用标准属性访问（`user.name`）而不是 object 模式解构（`final User(:name) = user;`）来读取已知非 null 实例上的单个属性。

### 6. 避免 `if-case` 处理独立标量比较
使用标准布尔运算符（`if (code >= 200 && code < 300)`）而不是 `if (code case >= 200 && < 300)` 处理独立条件。将关系模式保留用于多臂 switch 表。

## 工作流程

### 任务进度：实现模式匹配
将此清单复制到实现复杂模式匹配逻辑时跟踪进度：

- [ ] 确定被评估的数据结构（JSON、List/段、Record、类、枚举）。
- [ ] 选择适当的 switch 结构（表达式用于值，语句用于副作用）。
- [ ] 定义所需的模式（Object、Map、List、Record）。
- [ ] 使用 Variable 模式（`var x`、`:var y`、`...final rest`）提取所需数据。
- [ ] 应用守卫子句（`when condition`）用于无法通过模式表达的逻辑。
- [ ] 使用通配符（`_`）或 `default` 子句（如果未使用 sealed 类）处理未匹配的 case。
- [ ] 运行静态分析器以检查穷尽性和死代码（`dart analyze`）。
- [ ] 验证运行时 Map/JSON 模式行为（省略键的 `containsKey` 语义）与显式 `null` 值的区别。

### 反馈循环 1：穷尽性检查（静态验证）
在 switch over `sealed` 类或枚举时，确保所有子类型在编译时都得到处理：

1. **运行分析器：** 执行 `dart analyze`。
2. **查看错误：** 查找 "类型 'X' 没有被 switch case 穷尽匹配" 或不可达模式臂警告。
3. **修复：** 为未处理的子类型添加缺失的 Object 模式，或如果可以接受默认回退或错误，添加显式通配符（`_`）臂。

### 反馈循环 2：运行时 Map & JSON 模式验证
由于 `dart analyze` 无法静态验证动态 `Map<String, dynamic>` 键，需要显式验证运行时模式语义：

1. **省略键与显式 `null`：** Map 模式 `{'key': String? val}` 检查 `map.containsKey('key')`。如果 JSON 负载省略了 `'key'`，模式在运行时无法匹配，尽管 `String?` 是可空的。直接从验证后的 map 中提取可选键（`map['key'] as String?`）。
2. **快速失败回退：** 确保未匹配或格式错误的 map 结构触发显式 `_ => throw FormatException(...)` 臂，而不是无声地失败 `if-case` 检查。

## 示例

### 多态 JSON 反序列化（区分联合）
使用 Map 模式结合 switch 表达式来验证标记的 JSON 负载并构建 `sealed` 类层次结构。有关可执行示例，请参阅
[examples/json_patterns.dart](examples/json_patterns.dart)，展示了如何将标记的 `ApiResponse` 解析为 `SuccessResponse` 和 `ErrorResponse`。

### 嵌套 JSON 验证和可选字段
使用嵌套 Map 和 List 模式在单个步骤中验证必需的模式结构并提取集合。有关可执行示例，请参阅
[examples/json_patterns.dart](examples/json_patterns.dart) 中的 `processUserPayload` 实现。

Map 模式检查键存在（`containsKey`）。如果可选 JSON 键可能完全从负载中省略（而不是显式传递为 `'key': null`），通过模式解构必需键，并直接从匹配的子 map 中提取可选字段。

### List 和路径段解构
使用带有 list rest 元素（`...final rest`）的 `if-case` 来验证前缀并提取剩余元素，而无需 2 臂 `_ => null` switch 或手动 `.first` 和 `.skip(1)` 索引。

```dart
String? resolveAllowedAssetSubpath(List<String> segments) {
  if (segments case ['assets', ...final rest]
      when rest.isNotEmpty && !rest.contains('..')) {
    return rest.join('/');
  }
  return null;
}
```

### 代数数据类型（Sealed Classes）
使用 Object 模式结合 switch 表达式来穷尽处理家族类型。

```dart
sealed class Shape {}

class Square implements Shape {
  final double length;
  Square(this.length);
}

class Circle implements Shape {
  final double radius;
  Circle(this.radius);
}

// 由于 `sealed` 修饰符，switch 表达式保证了穷尽性。
double calculateArea(Shape shape) => switch (shape) {
  Square(length: var l) => l * l,
  Circle(:var radius)   => math.pi * radius * radius,
};
```

### 变量交换和解构
使用变量赋值模式来交换值或解构 record 字段而无需临时变量。

```dart
var (a, b) = ('left', 'right');
(b, a) = (a, b); // 交换值

// 解构函数返回值
var (name, age) = getUserInfo();
```

### 守卫子句和逻辑或
使用 `when` 在模式匹配后评估任意条件。

```dart
switch (shape) {
  case Square(length: var s) || Circle(radius: var s) when s > 0:
    print('有效的正形状维度 $s');
  case Square() || Circle():
    print('零或负形状维度');
}
```
