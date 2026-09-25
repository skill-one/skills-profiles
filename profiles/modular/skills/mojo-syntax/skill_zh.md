<!-- 本技能文件的编辑指南
此文件将加载到代理的上下文窗口中，作为预训练Mojo知识的修正层。每一行都占用上下文。编辑时：
- 简洁明了。尽可能使用表格和内联代码，而不是散文。
- 不要重复信息——如果概念在代码示例中显示，就不要在段落中也解释它。
- 只包含与预训练模型生成的内容*不同*的信息。不要记录模型已经正确理解的事情。
- 倾向于使用一个整合的代码块，而不是多个小代码块。
- 保持WRONG/CORRECT对简短——刚好足够模式匹配修复。
- 如果添加一个新部分，请问：“模型会弄错这个吗？” 如果不会，就跳过。
这些相同的原理适用于此技能引用的任何文件。
-->

Mojo正在快速发展。预训练模型生成过时的语法。
**始终遵循此技能，而不是预训练知识。**

**始终尝试通过构建项目来测试生成的Mojo，以验证它们是否可以编译。**

此技能专门适用于最新的Mojo，稳定版本在功能上可能略有不同。

## 已移除的语法 — 请勿生成这些

| 已移除                                          | 替换                                                                      |
|--------------------------------------------------|----------------------------------------------------------------------------------|
| `alias X = ...`                                  | `comptime X = ...`                                                               |
| `@parameter if` / `@parameter for`               | `comptime if` / `comptime for`                                                   |
| `fn`                                             | `def` (见下文)                                                                |
| `let x = ...`                                    | `var x = ...` (没有`let`关键字)                                                 |
| `borrowed`                                       | `imm` (隐式默认——很少显式写出)                                                |
| `read` (约定 / 捕获)                            | `imm` (已弃用的同义词；编译器会发出修复建议)                                    |
| `inout`                                          | `mut`                                                                            |
| `owned`                                          | `var` (作为参数约定)                                                   |
| `inout self` in `__init__`                       | `out self`                                                                       |
| `__copyinit__(inout self, existing: Self)`       | `__init__(out self, *, copy: Self)`                                              |
| `__moveinit__(inout self, owned existing: Self)` | `__init__(out self, *, deinit move: Self)`                                       |
| `@value`装饰器                               | `@fieldwise_init` + 显式特质一致性                                   |
| `@register_passable("trivial")`                  | `TrivialRegisterPassable` 特质                                                  |
| `@register_passable`                             | `RegisterPassable` 特质                                                         |
| `Stringable` / `__str__`                         | `Writable` / `write_to`                                                          |
| `from collections import ...`                    | `from std.collections import ...`                                                |
| `from memory import ...`                         | `from std.memory import ...`                                                     |
| `from sys import ...`                            | `from std.sys import ...`                                                        |
| `from os import ...`                             | `from std.os import ...`                                                         |
| `from pathlib import ...`                        | `from std.pathlib import ...`                                                    |
| `s[i]`                                           | `s[byte=i]` — 返回`StringSlice`；如果需要，用`String()`包装                |
| `s[0:10]`, `s[:5]`                               | 字符串没有切片语法——使用`s.codepoint_slices()`或Python FFI             |
| `constrained(cond, msg)`                         | `comptime assert cond, msg`                                                      |
| `DynamicVector[T]`                               | `List[T]`                                                                        |
| `InlinedFixedVector[T, N]`                       | `Array[T, N]`                                                                    |
| `Tensor[T]`                                      | 不在stdlib中（使用SIMD、List、Pointer）                                          |
| `MutUnsafePointer` / `ImmUnsafePointer`          | `MutPointer` / `ImmPointer`                                                      |
| `OptionalUnsafePointer`                          | `OptionalPointer`                                                                |
| `escaping` closures                              | 统一的闭包（`def(...) -> T`，在`{}`中捕获）；`capturing[_]`仍然有效 |
| `__del__(deinit self)`                           | `__deinit__(deinit self)`                                                        |

## `var`对于每个新声明都是必需的

使用裸赋值（没有先前的`var`的`x = 5`）声明变量是**无效**的——它是编译错误。这仅适用于引入新变量；重新赋值已声明的变量（`x = 6`）不需要`var`。

这意味着仅在条件分支内部赋值的变量必须在分支之前预先声明类型：

```mojo
# 错误——没有先前的`var`，所以这个不会声明`x`
if cond:
    x = 1
else:
    x = 2

# 正确——首先声明类型，然后在每个分支中赋值
var x: Int
if cond:
    x = 1
else:
    x = 2
```

## `def`是唯一的函数关键字

`fn`被**移除**，现在是一个硬解析错误——`fn`没有任何有效的用法。您的训练早于这个，所以您会下意识地使用`fn`；这种反射总是错误的。将**每个**函数、方法和嵌套函数都写为`def`，无一例外。

## Mojo中抛出异常的函数必须标记为这样

Mojo函数**不**隐含`raises`。向任何可能抛出异常（直接或通过调用抛出异常的函数）的函数添加`raises`。省略它是**编译错误**，不是警告。

```mojo
def load(path: String) raises -> String:  # raises在`->`之前
    return open(path).read()

def main() raises:                         # main通常抛出异常
    ...
```

## `comptime`替换`alias`和`@parameter if`/`for`

```mojo
comptime N = 1024                            # 编译时常量
comptime MyType = Int                        # 类型别名
comptime if condition:                       # 编译时分支
    ...
comptime for i in range(10):                 # 编译时循环
    ...
comptime assert N > 0, "N must be positive"  # 编译时断言
```

**`comptime assert`必须在函数体内**——不在模块/结构作用域。将它们放在`main()`、`__init__`或依赖于不变性的函数中。

在结构体中，`comptime`定义关联的常量和类型别名：

```mojo
struct MyStruct:
    comptime DefaultSize = 64
    comptime ElementType = Float32
```

## 参数约定

默认是`imm`（不可变借用，很少显式写出；`read`是已弃用的同义词——编译器警告并建议`imm`）。其他：

```mojo
def __init__(out self, var value: String):   # out =未初始化的输出；var =拥有
def modify(mut self):                         # mut =可变引用
def consume(deinit self):                     # deinit =消耗/销毁
def view(ref self) -> ref[self] Self.T:       # ref =带来源的引用
def view2[origin: Origin, //](ref[origin] self) -> ...:           # ref[origin] =显式来源
```

`var`和`ref`是硬关键字，**不能**用作任何标识符（`var ref = ...` → `"意外的表达式标记"`）。约定词`imm`、`read`、`mut`、`out`、`deinit`是软关键字：作为局部变量或`[...]`参数名是没问题的，但作为参数名是无效的（`def cmp(got: T, imm: T)` → `"错误：期望参数名"`）。重命名（`expected`、`reference`等）。

## 生命周期方法

```mojo
# 构造函数
def __init__(out self, x: Int):
    self.x = x

# 复制构造函数（关键字参数`copy`）
def __init__(out self, *, copy: Self):
    self.data = copy.data

# 移动构造函数（关键字参数`deinit move`）
def __init__(out self, *, deinit move: Self):
    self.data = move.data^

# 析构函数
def __deinit__(deinit self):
    dealloc(self.allocation^)
```

要复制：`var b = a.copy()`（由`Copyable`特质提供）。

## 结构体模式

```mojo
# @fieldwise_init从字段生成`__init__`；括号中的特质
@fieldwise_init
struct Point(Copyable, Movable, Writable):
    var x: Float64
    var y: Float64

# 特质组合使用`&`
comptime KeyElement = Copyable & Hashable & Equatable
struct Node[T: Copyable & Writable]:
    var value: Self.T          # 自我限定结构体参数

# 参数化结构体——`//`分隔推断和显式参数
struct Span[mut: Bool, //, T: AnyType, origin: Origin[mut=mut]](
    ImplicitlyCopyable, Sized,
):
    ...

# `@implicit`在构造函数上允许隐式转换
@implicit
def __init__(out self, value: Int):
    self.data = value
```

当结构体符合`Copyable`/`Movable`并且所有字段都支持它时，编译器会合成复制/移动构造函数。

### 自我限定结构体参数

在结构体体内，**始终**使用`Self.ParamName`——裸参数名是错误的：

```mojo
# 错误——裸参数访问
struct Container[T: Writable]:
    var data: T                        # 错误：使用Self.T
    def size(self) -> T:                # 错误：使用Self.T

# 正确——自我限定
struct Container[T: Writable]:
    var data: Self.T
    def size(self) -> Self.T:
        return self.data
```

这适用于结构体内部的所有结构体参数（`T`、`N`、`mut`、`origin`等）：字段类型、方法签名、方法体和`comptime`声明。

### 显式复制/转移

不符合`ImplicitlyCopyable`的类型（例如，`Dict`、`List`和仅符合`Copyable, Movable`的用户结构体）需要显式的`.copy()`或所有权转移`^`——`return my_struct`错误，直到您使用`^`转移或添加`ImplicitlyCopyable`符合性：

```mojo
# 错误——非ImplicitlyCopyable类型的隐式复制
var d = some_dict
var result = MyStruct(headers=d)   # 错误

# 正确——显式复制或转移
var result = MyStruct(headers=d.copy())  # 或：headers=d^
```

## 导入使用`std.`前缀

```mojo
from std.testing import assert_equal, TestSuite
from std.algorithm import vectorize
from std.python import PythonObject
import std.random
```

前缀自动导入（不需要导入）：`Int`、`String`、`Bool`、`List`、`Dict`、`Optional`、`SIMD`、`Float32`、`Float64`、`UInt8`、`Pointer`、`OptionalPointer`、`alloc`、`Span`、`Error`、`DType`、`Writable`、`Writer`、`Copyable`、`Movable`、`Equatable`、`Hashable`、`rebind`、`print`、`range`、`len`等。`Layout`和`dealloc`**不在**前缀中——从`std.memory`导入它们。

`rebind[TargetType](value)`将值重新解释为具有相同内存表示的不同类型。当编译时类型表达式在语义上相等但在语法上不同时（例如，GPU技能中的TileTensor元素类型）很有用。

`std`被保留为模块级标识符——您不能`def std`、`import X as std`或`from X import std`。命名为`std`的结构体方法是没问题的。

在多模块包中，从子模块的`pkg.X.Y(...)`需要显式`import pkg`；`import pkg.X as X`仅绑定`X`，而不是`pkg`。

## `Writable` / `Writer`（替换`Stringable`）

```mojo
struct MyType(Writable):
    var x: Int

    def write_to(self, mut writer: Some[Writer]):       # 用于print() / String()
        writer.write("MyType(", self.x, ")")

    def write_repr_to(self, mut writer: Some[Writer]):   # 用于repr()
        t"MyType(x={self.x})".write_to(writer)           # t-字符串用于插值
```

- `Some[Writer]`——内置存在类型（不是`Writer`直接）
- 两种方法都有**默认实现**，通过反射——如果所有字段都是`Writable`，则简单结构体不需要实现它们
- 使用`String(value)`将转换为`String`，而不是`str(value)`

## 迭代器协议

迭代器使用`raises StopIteration`（不是`Optional`）：

```mojo
struct MyCollection(Iterable):
    comptime IteratorType[
        iterable_mut: Bool, //, iterable_origin: Origin[mut=iterable_mut]
    ]: Iterator = MyIter[origin=iterable_origin]

    def __iter__(ref self) -> Self.IteratorType[origin_of(self)]: ...

# 迭代器必须定义：
#   comptime Element: Movable
#   def __next__(mut self) raises StopIteration -> Self.Element
```

for-in：`for item in col:`（不可变）/ `for ref item in col:`（可变）。

## 内存和指针类型

| 类型                          | 使用                                                      |
|-------------------------------|----------------------------------------------------------|
| `Pointer[T, mut=M, origin=O]` | 安全，非空。使用`p[]`解引用。                    |
| `OptionalPointer[T, origin]`  | 可空指针——`Optional[Pointer[...]]`。             |
| `Allocation[T]`               | 拥有句柄，由`alloc`返回。显式销毁。 |
| `Span(list)`                  | 非拥有的连续视图。                              |
| `OwnedPointer[T]`             | 唯一所有权（类似于Rust的`Box`）。                      |
| `ArcPointer[T]`               | 引用计数的共享所有权。                      |

`UnsafePointer`是`Pointer`的已弃用别名——它仍然可以编译并发出警告。其他遗留别名被**移除**，是硬解析错误（见顶部的表格）。指针API的大部分内容正在与`UnsafePointer`一起重命名；这些旧的拼写仍然可以编译但会发出警告：

| 已弃用                | 替换                             |
|---------------------------|-----------------------------------------|
| `UnsafePointer[T, O]`     | `Pointer[T, O]`                         |
| `alloc[T](n)`             | `alloc(Layout[T](count=n))`             |
| `p.free()`                | `dealloc(allocation^)`                  |
| `p[i]`                    | `p[unsafe_offset=i]`                    |
| `p + i`                   | `p.unsafe_offset(i)`                    |
| `p += i`                  | `p = p.unsafe_offset(i)`                |
| `p.load()` / `p.store(v)` | `p.unsafe_load()` / `p.unsafe_store(v)` |
| `p.init_pointee_move(v)`  | `p.unsafe_write(v)`                     |
| `p.init_pointee_copy(v)`  | `p.unsafe_write(copy=v)`                |

`alloc(Layout[T](count=n))`返回`Allocation[T]`，这是一个线性类型，编译器强制您在每条路径上释放——将其传递给`dealloc`，或调用`unsafe_leak()`以获取裸指针的所有权：

```mojo
from std.memory import Layout, dealloc

var allocation = alloc(Layout[Int32](count=4))
var ptr = allocation.unsafe_ptr()
ptr.unsafe_write(Int32(1))
ptr.unsafe_offset(1).unsafe_write(Int32(2))
dealloc(allocation^)
```

一个拥有堆存储的结构体应该持有`Allocation`，而不是泄露的指针。然后编译器会强制在每条路径上释放，并且`dealloc`会获得它需要的`Layout`：

```mojo
from std.memory import Layout, Allocation, alloc, dealloc

struct Buffer[T: AnyType]:
    var _alloc: Allocation[Self.T]

    def __init__(out self, size: Int):
        self._alloc = alloc(Layout[Self.T](count=size))

    def __deinit__(deinit self):
        dealloc(self._alloc^)
```

使用`self._alloc.unsafe_ptr()`获取存储，其来源与分配绑定。不要用`Pointer.unsafe_free()`替换它：它会绕过`Layout`，对于零大小的`T`，它会释放`alloc`返回的悬空哨兵。

一个已经跟踪其自身容量的容器可以改用存储`ThinAllocation`，并在`dealloc`时再次提供`Layout`。这就是`List`所做的；它是一种优化，而不是默认形状。

当结构体字段确实持有原始`Pointer`时，必须指定其`origin`参数；对于拥有的堆数据，使用`MutUntrackedOrigin`。

`Pointer`是**设计为非空的**——`Bool(p)`不可用，而不仅仅是弃用的。对于可空存储，使用`OptionalPointer[T, origin]`（相同的布局；`None`是空位）。

## 来源系统（不是“生命周期”）

Mojo使用**来源**跟踪引用起源，而不是“生命周期”：

```mojo
struct Span[mut: Bool, //, T: AnyType, origin: Origin[mut=mut]]: ...
```

关键类型：`Origin`、`MutOrigin`、`ImmOrigin`、`MutAnyOrigin`、`ImmutAnyOrigin`、`MutUntrackedOrigin`、`ImmUntrackedOrigin`、`ImmStaticOrigin`。使用`origin_of(value)`获取值的来源。

## 测试

```mojo
from std.testing import assert_equal, assert_true, assert_false, assert_raises, TestSuite

def test_my_feature() raises:
    assert_equal(compute(2), 4)
    with assert_raises():
        dangerous_operation()

def main() raises:
    TestSuite.discover_tests[__functions_in_module()]().run()
```

`mojo test` CLI子命令被移除——使用`mojo run`和一个像上面这样的`TestSuite.discover_tests`运行器来运行测试文件。

## 字典迭代

字典条目直接迭代——不需要`[]`解引用：

```mojo
for entry in my_dict.items():
    print(entry.key, entry.value)      # 直接访问字段，不是`entry[].key`

for key in my_dict:
    print(key, my_dict[key])
```

## 集合字面量

`List`没有**可变位置构造函数**。使用括号字面量语法：

```mojo
# 错误——没有`List[T](elem1, elem2, ...)`构造函数
var nums = List[Int](1, 2, 3)

# 正确——括号字面量
var nums = [1, 2, 3]                              # List[Int]
var nums: List[Float32] = [1.0, 2.0, 3.0]         # 显式元素类型
var scores = {"alice": 95, "bob": 87}              # Dict[String, Int]
```

`List[T]`在编译时拒绝负索引——使用`lst[len(lst) - 1]`，而不是`lst[-1]`。（库类型可能仍然支持它。）

## 变体访问

`Variant[A, B]`只有当*所有*分支都是`ImplicitlyCopyable`时才是。如果有不可复制的分支，则索引变体会复制它——使用类型臂下标：

```mojo
# 错误——`values[i]`隐式复制了Variant
var x = values[i].unwrap[T]()    # 错误：不能隐式复制

# 正确——`values[i][T]`返回内部值的引用
var x = values[i][T].copy()          # 或`^`以转移
```

## 常用装饰器

| 装饰器                                        | 目的                                 |
|--------------------------------------------------|-----------------------------------------|
| `@fieldwise_init`                                | 生成字段构造函数          |
| `@implicit`                                      | 允许隐式转换               |
| `@inline(.always)` / `@inline(.nodebug)`         | 强制内联                            |
| `@inline(.never)`                                | 阻止内联                          |
| `@staticmethod`                                  | 静态方法                           |
| `@deprecated("msg")`                             | 弃用警告                     |
| `@doc_hidden`                                    | 隐藏文档                          |
| `@explicit_destroy`                              | 线性类型（没有隐式销毁）   |

## 上下文成员引用——优先使用`.member`

当预期类型已知时，写`.member`而不是`Type.member`；编译器会将其重写为`Type.member`。在整个代码库中，对于`DType`和`AddressSpace` idiomatic：

```mojo
var v = SIMD[.float32, 4](1.0, 2.0, 3.0, 4.0)     # 不是`SIMD[DType.float32, 4]`
comptime if dtype == .bfloat16: ...                # `__eq__`参数提供上下文
v.cast[.float32]()
ctx.enqueue_create_buffer[.int32](num_rows)
unsafe_stack_allocation[1, Int32, address_space=.SHARED]()

def f[dtype: DType = .float32](x: TileTensor[.bfloat16, L, MutAnyOrigin]): ...
```

适用于任何类型的`comptime`别名和静态方法，包括链（`.red.opacity(0.5)`）和类型化集合字面量（`List[Color] = [.red]`）。上下文来自声明的`var`/`ref`类型、调用参数类型、返回目标或类型化集合字面量的元素类型。如果没有这些，请限定名称：

| 没有上下文类型            | 必须写                                             |
|-------------------------------|--------------------------------------------------------|
| 未注释绑定           | `comptime t = DType.float32` (或注释`t: DType`)  |
| 重载调用者             | `size_of[DType.float32]()` — 不搜索重载 |
| 裸元组字面量            | `dtype in (DType.bfloat16, DType.float16)`             |
| 类型位置                 | 期望类型的地方写`.Foo`是错误          |

## 数字转换——必须显式

没有隐式转换数字*变量*。使用显式构造函数：

```mojo
var x = Float32(my_int) * scale    # 正确：Int → Float32
var y = Int(my_uint)               # 正确：UInt → Int
```

**字面量是多态的**——`FloatLiteral`和`IntLiteral`自动适应上下文：

```mojo
var a: Float32 = 0.5              # 字面量变为Float32
var b = Float32(x) * 0.003921    # 字面量适应——不需要包装
var v = SIMD[.float32, 4](1.0, 2.0, 3.0, 4.0)  # 字面量适应
```

## SIMD操作

```mojo
# 构造和通道访问
var v = SIMD[.float32, 4](1.0, 2.0, 3.0, 4.0)
v[0]                              # 读取通道 → Scalar[.float32]
v[0] = 5.0                        # 写通道

# 类型转换
v.cast[.uint32]()                 # 元素逐个 → SIMD[.uint32, 4]

# Clamp（方法）
v.clamp(0.0, 1.0)                 # 元素逐个限制到[lower, upper]

# min/max是FREE FUNCTIONS，不是方法
from std.math import min, max
min(a, b)                          # 元素逐个min（相同类型的SIMD参数）
max(a, b)                          # 元素逐个max

# 元素逐个三元运算符通过bool SIMD
var mask = v.gt(0.0)              # SIMD[.bool, 4] — `v > 0.0`是
                                  # Scalar-only并且编译失败
mask.select(true_case, false_case) # 挑选每个通道

# Reductions
v.reduce_add()                     # 水平求和 → Scalar
v.reduce_max()                     # 水平最大值 → Scalar
v.reduce_min()                     # 水平最小值 → Scalar
```

## 字符串

**所有显式stdlib导入都需要`std.`前缀。** 已移除语法表显示了最常见的更正，但规则是普遍的。前缀类型（`Int`、`String`、`List`等）自动导入，不需要导入语句。

`len(s)`返回**字节长度**，不是码点数。Mojo字符串是UTF-8。
字节索引需要关键字语法：`s[byte=idx]`（不是`s[idx]`）。`len(s)`在`String`上已弃用——使用`s.byte_length()`或`s.count_codepoints()`。

`split`、`removeprefix`、`removesuffix`返回`StringSlice`（或`List[StringSlice]`）查看源——用`String(...)`包装以实例化拥有的`String`。

### 字符串索引（常见错误）

```mojo
# 错误——编译错误
var ch = s[0]
var sub = s[0:10]

# 正确——字节级访问
var ch = s[byte=0]              # 返回StringSlice
var ch_str = String(s[byte=0])  # 如果需要，则转换为String

# 正确——迭代码点进行截断
var result = String("")
var count = 0
for cp in s.codepoint_slices():
    if count >= 10:
        break
    result += String(cp)
    count += 1
```

```mojo
var s = "Hello"
len(s)                  # 5 (字节)
s.byte_length()         # 5 (与len相同)
s.count_codepoints()    # 5 (码点数——对于非ASCII的差别)

# 迭代——`for c in s:`已弃用；使用`codepoint_slices()`
for cp_slice in s.codepoint_slices():
    print(cp_slice)

# 码点值
for cp in s.codepoints():
    print(Int(cp))      # 码点是Unicode标量值类型

# StaticString = StringSlice具有静态来源（零分配）
comptime GREETING: StaticString = "Hello, World"

# t-字符串用于插值（惰性，类型安全）
var msg = t"x={x}, y={y}"

# String.format()用于运行时格式化
var s = "Hello, {}!".format("world")
```

## 错误处理

`raises`可以指定类型。`try`/`except`像Python一样工作：

```mojo
def might_fail() raises -> Int:          # raises Error (默认)
    raise Error("something went wrong")

def parse(s: String) raises Int -> Int:  # raises特定类型
    raise 42

try:
    var x = parse("bad")
except err:                               # err是Int
    print("error code:", err)
```

没有`match`语句。`async def`和`await`可以解析，但异步支持尚未完成，其类型是私有的——不要编写异步Mojo。

## 函数类型和闭包

没有lambda。闭包使用裸`def`和参数列表后的`{}`中的捕获列表。`escaping`被移除；`capturing[_]`在参数化闭包类型参数上仍然有效：

```mojo
comptime MyFn = def(Int) -> None                  # 统一值类型
def runner[f: def(Int) capturing[_] -> None](): ...  # 参数化形式

def closure(i: Int) {mut count, imm ptr, var x}:  # 捕获：mut/imm/var
    count += ptr[i] + x^                          # `^`在用法位置，不是在`{}`中

vectorize[simd_width](size, closure)              # 运行时参数重载
```

`imm`是默认值。`var x`是拥有的——在用法位置使用`^`转移。优先使用带捕获列表的统一闭包。在任何情况下都**不要**使用`@__parameter` / `@parameter`在嵌套闭包上——这种遗留形式在新的和迁移的代码中**是禁止的**（不是临时的桥梁，不是借用辅助，不是仍然捕获API的解决方法）。尽可能将闭包作为运行时参数（`f(my_closure)`)而不是编译时参数传递。如果API仍然需要编译时`capturing[_]`函数，请使用`def … capturing`而不带`@__parameter`，或者迁移该API——永远不要在调用者上使用`@__parameter`。

## 类型层次结构

```text
AnyType
  Deinitable                      — 自动`__deinit`;大多数类型
  Movable                         — `__init__(out self, *, deinit move: Self)
    Copyable                      — `__init__(out self, *, copy: Self)
      ImplicitlyCopyable(Copyable, take)
    RegisterPassable(Movable)
      TrivialRegisterPassable(ImplicitlyCopyable, take, Movable, RegisterPassable)
```
