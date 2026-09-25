# Swift API 设计指南

应用 Swift API 设计指南来规范命名、标签、文档和调用点清晰度。对于混合请求，在此处处理 API 设计部分，并将语言/类型系统工作路由到 `swift-language`，并发到 `swift-concurrency`，并将 lint 配置路由到 `swiftlint`。

## 目录

- [参数标签规则](#参数标签规则)
- [副作用命名](#副作用命名)
- [可变与不可变配对](#可变与不可变配对)
- [文档注释](#文档注释)
- [清晰度与命名](#清晰度与命名)
- [流畅用法与协议](#流畅用法与协议)
- [通用规范](#通用规范)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 参数标签规则

参数标签决定了调用点的阅读方式。应用第一个匹配的规则：

| 情况 | 规则 | 示例 |
|------|------|------|
| 第一个参数完成语法短语 | 省略标签，将单词合并到基本名称中 | `addSubview(y)` |
| 值保持的初始化转换 | 省略第一个标签 | `Int64(someUInt32)` |
| 参数是不可区分的同类 | 省略所有标签 | `min(x, y)` |
| 第一个参数完成介词短语 | 使用介词进行标签 | `fade(from: red)` |
| 前两个参数形成单个抽象 | 将介词合并到基本名称中 | `moveTo(x: b, y: c)` |
| 其他情况 | 进行标签 | `split(maxSplits: 2)` |

在解析抽象边界、多个介词、转换初始化器、不可区分的同类、参数命名或默认参数时，加载 [参数标签和参数](references/argument-labels-and-parameters.md)。

## 副作用命名

对于具有副作用的操作，使用祈使动词；对于没有副作用的操作，使用描述结果的名词或形容词短语；对于布尔 API，使用断言式名称。

```swift
array.sort()
array.append(newElement)
let d = point.distance(to: origin)
line.isEmpty
set.contains(element)
```

在审查扩展的纯/可变示例或布尔命名时，加载 [副作用和可变配对](references/side-effects-and-mutating-pairs.md)。

## 可变与不可变配对

根据操作的天然描述命名可变/不可变配对：

- 对于动词操作，使用祈使动词进行可变操作，使用描述结果的分词进行副本：`sort()/sorted()` 或 `append(_:)/appending(_:)`。优先使用 `-ed`；仅在 `-ed` 语法不正确或描述直接对象而不是返回结果时使用 `-ing`。
- 对于名词操作，使用名词进行副本，`form` + 名词进行可变操作：`union(_:)` / `formUnion(_:)`。
- 为创建新值的工厂前缀 `make`。

当返回结果的语法不明确时，加载 [`-ed`/`-ing` 决策树](references/side-effects-and-mutating-pairs.md#the--ed-ing-decision-tree)。相同的参考资料包含扩展的 `form`-前缀、布尔和工厂模式。

## 文档注释

每个公共声明都必须有文档注释。

### 按声明类型总结规则

| 声明 | 摘要描述 |
|------|----------|
| 函数/方法 | 它做什么以及它返回什么 |
| 下标 | 它访问什么 |
| 初始化器 | 它创建什么 |
| 类型/属性/变量 | 它**是什么** |

将摘要写为单个句子片段，以动词（对于动作）或名词短语（对于实体）开头，以句号结尾。

```swift
/// 返回指定索引处的元素。
func element(at index: Int) -> Element { ... }

/// 集合中的元素数量。
var count: Int { ... }

/// 创建一个包含给定元素的新数组。
init(_ elements: some Sequence<Element>) { ... }

/// 访问指定位置的元素。
subscript(index: Int) -> Element { ... }
```

### 符号标记

在摘要相关时，使用标准符号标记：

- `- Parameter name:` 用于单个参数
- `- Parameters:` 块用于多个参数
- `- Returns:` 用于返回值
- `- Throws:` 用于抛出的错误
- `- Complexity:` 用于算法复杂度

```swift
/// 删除并返回指定位置的元素。
///
/// - Parameter index: 要删除的元素的位置。
/// - Returns: 删除的元素。
/// - Complexity: O(*n*)，其中 *n* 是集合的长度。
mutating func remove(at index: Int) -> Element { ... }
```

### O(1) 复杂度规则

记录任何不是 O(1) 的计算属性的复杂度。调用者默认假设属性是 O(1)。如果一个属性执行了超过常量时间的工作，请明确说明复杂度。

```swift
/// 所有项目的总重量。
///
/// - Complexity: O(*n*)，其中 *n* 是项目的数量。
var totalWeight: Double {
    items.reduce(0) { $0 + $1.weight }
}
```

有关文档模式和示例，请参阅 [references/conventions-and-special-rules.md](references/conventions-and-special-rules.md)。

## 清晰度与命名

使用点上的清晰度是最重要的目标。每个设计决策都是为了阅读调用点的人。

**清晰度优先于简洁性。** 当较长的名称可以消除歧义时，它是可以接受的。不要缩写。

```swift
// 良好
employees.remove(at: position)

// 不良——模糊：删除元素？在位置删除？
employees.remove(position)
```

**包含避免歧义所需的词语。** 如果省略一个词语使调用点不明确，请保留它。

```swift
// 良好——"at" 澄清了参数的作用
friends.remove(at: index)

// 不良——"index" 是要删除的元素还是位置？
friends.remove(index)
```

**省略不必要的词语。** 不要重复上下文已经提供的类型信息。

```swift
// 良好
allViews.remove(cancelButton)

// 不良——"Element" 重复了类型
allViews.removeElement(cancelButton)
```

**按角色命名变量和参数，而不是类型。** 使用实体在当前上下文中的角色，而不是其类型名称。

```swift
// 良好——描述了角色
var greeting: String
func add(_ observer: NSObject, for keyPath: String)

// 不良——命名了类型
var string: String
func add(_ object: NSObject, for string: String)
```

**弥补弱类型信息。** 当参数类型是 `Any`、`AnyObject` 或像 `Int` 或 `String` 这样的基本类型时，在名称中添加角色澄清词语。

```swift
// 良好——尽管类型弱，但角色清晰
func addObserver(_ observer: NSObject, forKeyPath path: String)

// 不良——这里的 "string" 意思是什么？
func add(_ object: NSObject, for string: String)
```

有关扩展的命名示例和模式，请参阅 [references/naming-and-clarity.md](references/naming-and-clarity.md)。

## 流畅用法与协议

**调用点读作语法化的英语。** 优先选择在调用点形成语法短语的名称。

```swift
// 良好——流畅阅读
x.insert(y, at: z)          // "x, insert y at z"
x.subviews.remove(at: i)    // "x's subviews, remove at i"
x.makeIterator()             // "x, make iterator"

// 不良——语法不正确
x.insert(y, position: z)
x.subviews.remove(i)
```

**初始化器的第一个参数。** 初始化器的第一个参数不应形成继续类型名称的短语。

```swift
// 良好
let foreground = Color(red: 32, green: 64, blue: 128)

// 不良——"Color with red" 读起来很别扭
let foreground = Color(havingRGBValuesRed: 32, green: 64, blue: 128)
```

**协议命名规范：**

| 协议描述 | 命名模式 | 示例 |
|--------|--------|------|
| 描述某物**是什么** | 名词 | `Collection`，`IteratorProtocol` |
| 一种**能力** | `-able`，`-ible` 或 `-ing` 后缀 | `Equatable`，`Hashable`，`Sendable` |

## 通用规范

**大小写。** 类型协议使用 `UpperCamelCase`。其他所有内容使用 `lowerCamelCase`。美式英语中常见的首字母缩写词根据位置统一大写或小写。

```swift
var utf8Bytes: [UTF8.CodeUnit]
var isRepresentableAsASCII = true
var userSMTPServer: SMTPServer
```

**方法和属性优先于自由函数。** 仅在以下情况下使用自由函数：
1. 没有明显的 `self` — `min(x, y)`
2. 函数是无约束的泛型 — `print(value)`
3. 函数语法是已建立的领域符号 — `sin(x)`

**默认参数优先于方法族。** 优先于具有默认参数的单个方法，而不是仅接受不同参数的多个方法。将默认参数放在末尾。具有默认值的参数始终应有参数标签——默认参数通常在调用点省略，因此当它们出现时，其标签必须清晰。

```swift
// 良好——带有默认值标签
func decode(_ data: Data, encoding: String.Encoding = .utf8) -> String?

// 不良——方法族
func decode(_ data: Data) -> String?
func decode(_ data: Data, encoding: String.Encoding) -> String?
```

**重载安全性。** 当方法在不同的类型域中操作或其含义从上下文中清晰时，它们可以共享基本名称。避免仅在调用点造成歧义的返回类型重载。

有关大小写边缘情况、重载模式以及元组/闭包命名，请参阅 [references/conventions-and-special-rules.md](references/conventions-and-special-rules.md)。

## 常见错误

| 错误 | 修正 |
|------|------|
| 模糊或缺失标签 | 使调用点语法化，例如 `remove(at:)`。 |
| 可变/不可变形式错误 | 使用祈使动词进行可变操作，使用语法 `-ed`/`-ing` 或名词形式进行副本。 |
| 名称描述类型或实现 | 命名角色和语义效果。 |
| 公共 API 缺少目的或复杂度文档 | 添加简洁的摘要并记录非 O(1) 属性。 |
| `form` 或工厂前缀使用不当 | 为名词操作保留 `form`；为工厂使用 `make`。 |
| 类型信息重复 | 删除从声明和上下文中已清晰的词语。 |
| 重载仅通过返回类型不同 | 添加语义名称或参数区分。 |
| 元组或闭包组件是位置性的 | 标记公共组件和闭包参数。 |

## 审查清单

### 参数标签
- [ ] 第一个参数遵循正确的标签规则（语法短语、介词、转换或标签）
- [ ] 介词标签不会错误地将独立参数分组
- [ ] 值保持的转换初始化器省略了第一个标签
- [ ] 所有非特殊情况参数都有标签

### 命名语义
- [ ] 可变方法使用祈使动词形式
- [ ] 非可变方法使用 `-ed`/`-ing` 或名词形式
- [ ] 可变/不可变配对遵循正确的模式（动词对或名词/form-名词对）
- [ ] 布尔属性读作断言（`isEmpty`，`isValid`，`contains`）
- [ ] 变量和参数按角色命名，而不是类型

### 文档
- [ ] 每个公共声明都有文档注释
- [ ] 摘要是一个以句号结尾的句子片段
- [ ] 摘要按声明类型描述正确的内容（动作、访问、创建、实体）
- [ ] 非O(1) 计算属性记录其复杂度
- [ ] 参数、返回值和抛出的错误使用符号标记进行文档记录

### 规范
- [ ] 类型协议使用 `UpperCamelCase`；其他所有内容使用 `lowerCamelCase`
- [ ] 首字母缩写词根据位置统一大小写
- [ ] 默认参数优先于方法族
- [ ] 重载仅通过返回类型不同
- [ ] 协议名称遵循名词（是什么）或后缀（能力）规范

## 参考资料

- 命名清晰度、基于角色的命名、弱类型补偿和术语：[references/naming-and-clarity.md](references/naming-and-clarity.md)
- 参数标签边缘情况、参数命名和默认参数策略：[references/argument-labels-and-parameters.md](references/argument-labels-and-parameters.md)
- 副作用命名示例、`-ed`/`-ing` 决策树、`form`-前缀模式和工厂方法：[references/side-effects-and-mutating-pairs.md](references/side-effects-and-mutating-pairs.md)
- 大小写边缘情况、复杂度文档、重载安全性、元组/闭包命名和自由函数例外：[references/conventions-and-special-rules.md](references/conventions-and-special-rules.md)
