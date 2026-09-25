# Swift 风格指南

用于编写干净、易读的 Swift 代码的代码风格约定。

## 核心原则

**清晰度 > 简洁性 > 一致性**

代码应无警告地编译。

## 命名

- `UpperCamelCase` — 类型、协议
- `lowerCamelCase` — 其他所有内容
- 调用处的清晰度
- 除通用（URL、ID）外，不使用缩写

```swift
// 推荐
let maximumWidgetCount = 100
func fetchUser(byID id: String) -> User
```

## 主路径

左对齐是主路径。不要嵌套 `if` 语句。

```swift
// 推荐
func process(value: Int?) throws -> Result {
    guard let value = value else {
        throw ProcessError.nilValue
    }
    guard value > 0 else {
        throw ProcessError.invalidValue
    }
    return compute(value)
}
```

## 代码组织

使用扩展和 MARK 注释：

```swift
class MyViewController: UIViewController {
    // 核心实现
}

// MARK: - UITableViewDataSource
extension MyViewController: UITableViewDataSource { }
```

## 间距

- 括号在同一行打开，在新行关闭
- 方法之间空一行
- 冒号：前面不加空格，后面加一个空格

## self

除非编译器要求，否则避免使用 `self`。

```swift
// 推荐
func configure() {
    backgroundColor = .systemBackground
}
```

## 计算属性

对于只读属性省略 `get`：

```swift
var diameter: Double {
    radius * 2
}
```

## 闭包

仅当闭包参数为单个参数时使用尾随闭包。

## 类型推断

当清晰时让编译器推断。对于空集合，使用类型注解：

```swift
var names: [String] = []
```

## 语法糖

```swift
// 推荐
var items: [String]
var cache: [String: Int]
var name: String?
```

## 访问控制

- `private` 优于 `fileprivate`
- 不要添加 `internal`（它是默认值）
- 访问控制作为引导指定符

## 内存管理

```swift
resource.request().onComplete { [weak self] response in
    guard let self else { return }
    self.updateModel(response)
}
```

## 注释

- 解释**为什么**，而不是**什么**
- 使用 `//` 或 `///`，避免 `/* */`
- 保持更新或删除

## 常量

使用无大小写的枚举进行命名空间：

```swift
enum Math {
    static let pi = 3.14159
}
```

## 常见错误

1. **超出 URL、ID、UUID 的缩写** — 像 `cfg`、`mgr`、`ctx`、`desc` 这样的缩写会降低可读性。将它们写出来：`configuration`、`manager`、`context`、`description`。三个例外是 URL、ID、UUID。

2. **嵌套 guard/if 语句** — 深层嵌套使代码难以理解。使用早期返回和 guard 将主路径左对齐。

3. **不一致的 self 使用** — 要么始终省略 `self`（推荐），要么始终使用它。混合会使代码扫描更困难并混淆捕获语义。

4. **过于泛型的类型名称** — `Manager`、`Handler`、`Helper`、`Coordinator` 太模糊。名称应解释职责：`PaymentProcessor`、`EventDispatcher`、`ImageCache`、`NavigationCoordinator`。

5. **隐式访问控制** — 不要省略访问控制。显式的 `private`、`public` 帮助未来的维护者理解模块边界。`internal` 是默认值，所以省略它。
