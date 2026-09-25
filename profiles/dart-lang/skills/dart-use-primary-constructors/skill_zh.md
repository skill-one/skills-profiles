# Dart 主要构造函数与新建构造函数语法技能

在帮助用户使用 Dart 的 **主要构造函数** 功能编写、重构或调试代码时，使用此技能。

### Dart 版本要求
*   **Dart 3.13 及以上版本**：主要构造函数默认启用。
*   **Dart 3.12**：该功能可用但处于实验阶段。用户必须显式启用实验标志 `primary-constructors`，通过 `--enable-experiment=primary-constructors` 或在 `analysis_options.yaml` 中启用：
```yaml
analyzer:
  enable-experiment:
    - primary-constructors
```
*   **Dart 3.11 及更早版本**：不支持主要构造函数。

---

## 1. 概述
主要构造函数允许开发人员在类头中直接声明一个非重定向的生成式构造函数以及一组实例变量。这显著减少了样板代码并提高了代码可读性。

### 主要优势
- 将字段声明、参数声明和初始化合并为单个声明，称为声明参数声明。
- 允许在非延迟字段初始化器中安全地引用构造函数参数（主要初始化器作用域）。
- 允许使用分号 (`;`) 简洁地表示空声明体。
- 引入用于类体内构造函数的简写紧凑语法。

---

## 2. 语法参考

### 2.1 基本类头语法
要声明主要构造函数，请在类型名称（以及可选的类型参数）之后立即放置参数列表：

```dart
// 声明字段 x 和 y，以及生成式构造函数 Point(this.x, this.y)
class Point(var int x, var int y);

// 声明 final 字段
class PointFinal(final int x, final int y);
```

### 2.2 声明、初始化和普通参数
主要构造函数参数列表区分三种类型的参数：
1.  **声明参数**：由 `var` 或 `final` 修饰符指示（例如，`final int x`）。它们隐式地在类中创建相应的实例字段。
2.  **初始化参数**：由 `this.` 或 `super.` 前缀指示（例如，`this.x` 或 `super.x`）。它们分别初始化现有字段或超类构造函数参数。
3.  **普通参数**：没有修饰符声明（例如，`int y`）。它们不会成为字段，并且仅在初始化期间可用（例如，在字段初始化器或类体内的 `this :` 初始化列表中）。

```dart
// `x` 是一个字段和一个参数，因为它有 `final` 关键字。特别是，我们可以在主要构造函数的类体内部分的初始化列表中使用名称 `x`。'y' 只是一个参数，因为它既没有 `final` 也没有 `var` 关键字，但 `y` 通过 `this :` 初始化列表传递给超类构造函数。
class C(final int x, int y) extends Base {
  this : super(y);
}
```

声明参数和初始化参数是实现相同目标（声明具有在构造函数中设置的实例字段的类）的两种方式：普通参数不同之处在于它们的值不会自动路由到实例字段。

### 2.3 常量主要构造函数
要使主要构造函数为 `const`，请在声明头中将 `const` 关键字放在类/类型名称之前：

```dart
class const Point(final int x, final int y);
extension type const Ext(int x);
enum const MyEnum(final int x) {
  entry(1);
}
```

### 2.4 扩展类型
扩展类型 **必须** 使用主要构造函数。
- 头中的单个参数是表示字段。
- 表示变量不能使用 `var` 修饰符（使用 `var` 会触发 `representation_field_modifier` 错误）。
- 表示变量可以可选地使用 `final` 修饰符。如果 `final` 不存在，则会推断；即，参数声明它是否显式为 `final`。

### 2.5 空体分号简写 (`;`)
当类、混入类、混入、扩展或扩展类型具有空体时，可以用分号 (`;`) 替换 `{}` 大括号：

```dart
class C(int x);
mixin class MC;
extension type ET(int x);
mixin M;
extension Ext on C;
```

### 2.6 主要构造函数的类体内部分 (`this ...`)
如果主要构造函数需要断言或自定义字段初始化，可以使用 `this :` 语法在类体内声明：

```dart
class Point(var int x, var int y) {
  // 类体内的初始化列表
  this : assert(x >= 0), y = y * 2;
}
```

您也可以使用此语法编写构造函数体（`this {...}`）。

### 2.7 简写紧凑构造函数语法
在类体内声明的构造函数中，可以省略类名并替换为 `new` 或 `factory` 关键字：

| 传统语法 | 简写紧凑语法 |
| :--- | :--- |
| `MyClass() {}` | `new() {}` |
| `MyClass.name() {}` | `new name() {}` |
| `const MyClass();` | `const new();` |
| `const MyClass.name();` | `const new name();` |
| `factory MyClass() => ...` | `factory() => ...` |
| `factory MyClass.name() => ...` | `factory name() => ...` |

---

## 3. 语义与作用域规则

### 3.1 主要初始化器作用域
当声明主要构造函数时，其形式参数被引入到 **主要初始化器作用域** 中。此作用域是类体内非延迟字段初始化器和主要构造函数的初始化列表（在 `this :` 之后）的当前作用域。
这允许非延迟字段在声明期间直接引用构造函数参数：
  ```dart
  class DeltaPoint(final int x, int delta) {
    // 'x' 和 'delta' 在此作用域内
    final int y = x + delta;
  }
  ```

### 3.2 晚实例变量限制
主要初始化器作用域对 `late` 实例变量初始化器 **不** 处于活动状态。
- 由于 `late` 变量可以在构造完成后进行评估，因此它们的初始化器不能安全地访问构造函数参数。
- 在 `late` 字段初始化器中尝试访问主要构造函数参数会导致编译时错误。

### 3.3 遮蔽
主要构造函数参数在主要初始化器作用域中遮蔽同名的类成员（字段）：
- 在非延迟初始化器中：`int y = x` 引用参数 `x`。
- 在 `late` 初始化器中：`late int y = x` 引用字段 `x`（如果存在），因为参数 `x` 已超出作用域。

### 3.4 生成式构造函数限制
为保证主要构造函数（以及相关联的初始化器作用域）始终执行：
- 声明主要构造函数的类、混入类或枚举声明 **不能** 声明任何其他非重定向的生成式构造函数（扩展类型除外）。
- 类体内声明的所有其他生成式构造函数 **必须** 重定向（直接或间接）到主要构造函数。

### 3.5 参数突变错误
在初始化阶段，主要构造函数参数不可赋值。
- 在字段初始化器或 `this :` 初始化列表中对参数进行任何赋值（例如，`p = value`，`p++`）是编译时错误。

### 3.6 重复初始化错误
多次初始化字段（例如，在字段声明/初始化器中初始化一次，并在 `this :` 初始化列表或作为初始化形式初始化一次）是编译时错误。

---

## 4. 诊断与故障排除

大多数错误和 lint 都有快速修复，运行 `dart fix` 来修复这些违规行为。对于其他常见错误，使用以下表格进行修复：

| 错误/Lint 代码 | 常见原因 | 解决方案 |
| :--- | :--- | :--- |
| **无效的晚访问** | 在 `late` 字段初始化器中引用主要构造函数参数。 | 将字段改为非延迟，或将值通过另一个非延迟字段传递。 |
| `fieldInitializedInInitializerAndDeclaration` | 在其声明和 `this :` 列表中初始化变量。 | 移除其中一个初始化。 |
| `nonRedirectingGenerativeConstructorWithPrimary` | 在类体内声明未重定向到主要构造函数的生成式构造函数。 | 将类体内构造函数更改为重定向（例如 `this(...)`）或移除类体内构造函数。 |

---

## 5. 分步重构工作流

### 工作流 5.1：将类迁移到主要构造函数

按照以下步骤将冗长类迁移到新的主要构造函数语法：

1.  **识别候选字段和构造函数**：
    定位生成式构造函数及其初始化的字段。在这种情况下，这是 `name` 和 `age` 字段。
    ```dart
    // 之前
    class User {
      final String name;
      final int age;
      User(this.name, this.age);
    }
    ```

2.  **将字段移至头**：
    将字段放在头中，并使用 `final` 或 `var` 修饰符，如果体为空则追加分号 (`;`)。`name` 和 `age` 字段现在作为声明参数 `final String name` 和 `final int age` 分别写入主要构造函数。
    ```dart
    // 之后
    class User(final String name, final int age);
    ```

3.  **处理自定义初始化器和断言**：
    如果有初始化列表或断言块，将其移至类体内的 `this` 块内：
    ```dart
    // 之前
    class Point {
      final int x;
      final int y;
      Point(this.x, this.y) : assert(x >= 0);
    }

    // 之后
    class Point(final int x, final int y) {
      this : assert(x >= 0);
    }
    ```

4.  **利用主要初始化器作用域进行计算**：
    如果字段值从参数计算得出，则在体中声明并直接使用参数赋值：
    ```dart
    // 之前
    class Rect {
      final double width;
      final double height;
      final double area;
      Rect(this.width, this.height) : area = width * height;
    }

    // 之后
    class Rect(final double width, final double height) {
      // 'width' 和 'height' 在此作用域内
      final double area = width * height;
    }
    ```

5.  **将类体内构造函数转换为重定向**：
    确保所有类体内生成式构造函数都重定向到主要构造函数：
    ```dart
    // 之前
    class Point {
      final int x;
      final int y;
      Point(this.x, this.y);
      Point.zero() : x = 0, y = 0;
    }

    // 之后
    class Point(final int x, final int y) {
      new zero() : this(0, 0); // 重定向到主要构造函数
    }
    ```

### 工作流 5.2：应用简写（紧凑）类体内构造函数

当用户希望保留构造函数在类体内但想减少冗长性时，建议使用简写构造函数语法：

```dart
// 之前
class DatabaseService {
  final String url;
  DatabaseService(this.url);
  DatabaseService.local() : url = 'localhost';
  factory DatabaseService.create() => DatabaseService('default');
}

// 之后
class DatabaseService {
  final String url;
  new(this.url); // 省略类名，使用 'new'
  new local() : url = 'localhost'; // 使用 'new local' 为命名构造函数
  factory create() => DatabaseService('default'); // 从工厂中省略类名
}
```
