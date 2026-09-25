# 实现Dart模式

## 目录
- [模式选择策略](#模式选择策略)
- [switch语句与表达式](#switch语句与表达式)
- [核心模式实现](#核心模式实现)
- [实用平衡与反模式](#实用平衡--反模式)
- [工作流程](#工作流程)
- [示例](#示例)

## 模式选择策略

根据数据结构和预期结果应用特定的模式类型。遵循以下条件指南：

*   **如果验证并从反序列化数据（例如JSON）中提取：** 使用Map、List和Object模式来验证模式结构并在一步中解构属性。
*   **如果处理多态有效负载或响应：** 使用`switch`表达式而不是map判别键来反序列化为`sealed`类层次结构。
*   **如果处理多个返回值：** 使用Record模式直接将字段解构到局部变量中。
*   **如果执行类型特定行为（代数数据类型）：** 使用Object模式结合`sealed`类来确保完备性。
*   **如果匹配数值范围或条件：** 在switch臂中使用关系（`>=`，`<=`）和逻辑与（`&&`）模式。
*   **如果多个情况共享逻辑：** 使用逻辑或（`||`）模式来共享单个情况体或守卫子句。
*   **如果忽略特定值：** 使用通配符模式（`_`）或集合中的不匹配Rest元素（`...`）。

## switch语句与表达式

根据执行上下文选择适当的switch结构：

*   **如果生成值：** 使用**switch表达式**。
    *   语法：`switch (value) { pattern => expression, }`
    *   规则：每个情况必须是单个表达式。没有隐式向下传递。必须完备。
*   **如果执行语句或副作用：** 使用**switch语句**。
    *   语法：`switch (value) { case pattern: statements; }`
    *   规则：空情况会向下传递到下一个情况。非空情况隐式中断（不需要`break`关键字）。

## 核心模式实现

使用以下语法和规则实现模式：

*   **逻辑或（`||`）：** `pattern1 || pattern2`。两个分支必须定义完全相同的变量集。
*   **逻辑与（`&&`）：** `pattern1 && pattern2`。分支不应定义重叠变量。
*   **关系：** `==`，`!=`，`<`，`>`，`<=`，`>=`后跟一个常量表达式。
*   **强制转换（`as`）：** `pattern as Type`。如果值不匹配类型则抛出异常。用于在解构期间强制断言类型。
*   **空值检查（`?`）：** `pattern?`。如果值为null则匹配失败。绑定变量到非空的基本类型。
*   **空值断言（`!`）：** `pattern!`。如果值为null则抛出异常。
*   **变量：** `var name`或`Type name`。将匹配的值绑定到新的局部变量。
*   **通配符（`_`）：** 匹配任何值并忽略它。
*   **列表：** `[pattern1, pattern2]`。匹配长度精确的列表，除非使用Rest元素（`...`或`...var rest`）。
*   **映射：** `{"key": pattern}`。匹配包含指定键的映射。忽略未匹配的键。
*   **记录：** `(pattern1, named: pattern2)`。匹配形状精确的记录。使用`:var name`来推断getter名称。
*   **对象：** `ClassName(field: pattern)`。匹配`ClassName`的实例。使用`:var field`来推断getter名称。

## 实用平衡与反模式

模式匹配和switch表达式应简化代码，而不是增加语法开销。注意以下界限：

### 1. 优先使用`is`类型提升而不是`if-case`用于单个可提升变量
当检查或提升单个变量时，使用标准的`is`检查，而不是引入阴影别名的`if-case`模式。

*   **优先：**
    ```dart
    // ✅ 直接原地提升`key`，无需额外变量
    for (final MapEntry(:key, :value) in map.entries) {
      if (key is String && value != null) {
        process(key, value);
      }
    }
    ```
*   **避免：**
    ```dart
    // ❌ 反模式：引入不必要的别名变量`k`
    for (final MapEntry(:key, :value) in map.entries) {
      if (key case final String k when value != null) {
        process(k, value);
      }
    }
    ```

### 2. 在switch臂中整合可空类型
当映射或返回值时，如果`null`和类型`T`都有效且处理方式相同，直接匹配可空类型`T?`，而不是创建冗余的`null`臂。

*   **优先：**
    ```dart
    // ✅ 清晰的可空模式匹配
    switch (value) {
      final String? s => s,
      _ => throw FormatException('无效值: $value'),
    }
    ```
*   **避免：**
    ```dart
    // ❌ 冗余的单独null臂
    switch (value) {
      final String s => s,
      null => null,
      _ => throw FormatException('无效值: $value'),
    }
    ```

### 3. 保留快速失败验证（不要静默丢弃数据）
不要在循环或反序列化中使用`if-case`来过滤元素，如果数据损坏应触发错误或诊断警告。

*   **优先：**
    ```dart
    // ✅ 快速失败，带显式诊断错误
    for (final raw in rawTasks) {
      if (raw is! Map<String, dynamic>) {
        throw FormatException('期望Map项，实际类型为${raw.runtimeType}: $raw');
      }
      _applyTask(raw);
    }
    ```
*   **避免：**
    ```dart
    // ❌ 静默忽略损坏的项
    for (final raw in rawTasks) {
      if (raw case final Map<String, dynamic> taskMap) {
        _applyTask(taskMap);
      }
    }
    ```

### 4. 避免单案例或布尔switch
*   使用`if (x is T)`而不是只有一个case和`default: break;`的switch语句。
*   使用标准的条件三元运算符（`condition ? a : b`）而不是`switch (condition) { true => a, false => b }`。

### 5. 避免过度的对象解构
使用标准属性访问（`user.name`）而不是对象模式解构（`final User(:name) = user;`）来读取已知非null实例上的单个属性。

### 6. 避免用于独立标量比较的`if-case`
使用标准布尔运算符（`if (code >= 200 && code < 300)`）而不是`if (code case >= 200 && < 300)`用于独立条件。将关系模式保留用于多臂switch表。

## 工作流程

### 任务进度：实现模式匹配
将此清单复制到实现复杂模式匹配逻辑时跟踪进度：

- [ ] 确定被评估的数据结构（JSON、Record、类、枚举）。
- [ ] 选择适当的switch结构（表达式用于值，语句用于副作用）。
- [ ] 定义所需的模式（Object、Map、List、Record）。
- [ ] 使用变量模式（`var x`，`:var y`）提取所需数据。
- [ ] 应用守卫子句（`when condition`）用于无法通过模式表达的逻辑。
- [ ] 使用通配符（`_`）或`default`子句（如果未使用sealed类）处理未匹配的情况。
- [ ] 运行静态分析器以检查完备性和死代码（`dart analyze`）。
- [ ] 验证运行时Map/JSON模式行为（省略键的`containsKey`语义）与显式null值。

### 反馈循环1：完备性检查（静态验证）
当在sealed类或枚举上switch时，确保在编译时处理所有子类型：

1. **运行分析器：** 执行`dart analyze`。
2. **查看错误：** 查找类型`'X'`未被switch情况完备匹配的错误或不可达模式臂警告。
3. **修复：** 为未处理的子类型添加缺失的Object模式，或者如果可以接受默认回退或错误，添加显式通配符（`_`）臂。

### 反馈循环2：运行时Map & JSON模式验证
因为`dart analyze`无法静态验证动态`Map<String, dynamic>`键，所以显式验证运行时模式语义：

1. **省略键与显式`null`：** 映射模式`{'key': String? val}`检查`map.containsKey('key')`。如果JSON有效负载中省略了`'key'`，即使`String?`是可空的，模式在运行时也会失败。直接从验证后的映射中提取可选键（`map['key'] as String?`）。
2. **快速失败回退：** 确保未匹配或格式错误的映射结构触发显式`_ => throw FormatException(...)`臂，而不是静默失败`if-case`检查。

## 示例

### 多态JSON反序列化（有区分的联合）
使用Map模式结合switch表达式来验证标记的JSON有效负载并构建`sealed`类层次结构。有关可执行实现示例，请参阅
[examples/json_patterns.dart](examples/json_patterns.dart)中标记的`ApiResponse`解析为`SuccessResponse`和`ErrorResponse`。

### 嵌套JSON验证和可选字段
使用嵌套Map和List模式在一步中验证所需模式结构并提取集合。有关`processUserPayload`的可执行实现示例，请参阅
[examples/json_patterns.dart](examples/json_patterns.dart)。

Map模式检查键存在（`containsKey`）。如果可选JSON键可能完全从有效负载中省略（而不是显式传递为`'key': null`），通过模式解构所需键，并直接从匹配的子映射中提取可选字段。

### 代数数据类型（sealed类）
使用Object模式结合switch表达式来完备处理家族类型。

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

// 由于`sealed`修饰符，switch表达式保证了完备性。
double calculateArea(Shape shape) => switch (shape) {
  Square(length: var l) => l * l,
  Circle(:var radius)   => math.pi * radius * radius,
};
```

### 变量交换和解构
使用变量赋值模式来交换值或解构记录字段，而无需临时变量。

```dart
var (a, b) = ('left', 'right');
(b, a) = (a, b); // 交换值

// 解构函数返回值
var (name, age) = getUserInfo();
```

### 守卫子句和逻辑或
使用`when`在模式匹配后评估任意条件。

```dart
switch (shape) {
  case Square(length: var s) || Circle(radius: var s) when s > 0:
    print('有效的正形状尺寸为 $s');
  case Square() || Circle():
    print('零或负尺寸形状');
}
```
