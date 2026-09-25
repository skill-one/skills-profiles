<!-- 本技能文件的编辑指南
此文件作为预训练Mojo知识的修正层加载到代理的上下文窗口中。每一行都占用上下文。编辑时：
- 简洁明了。尽可能使用表格和内联代码而不是散文。
- 不要重复信息——如果概念在代码示例中展示，不要在段落中也解释它。
- 只包含与预训练模型生成内容*不同*的信息。不要记录模型已经正确理解的事情。
- 倾向于使用一个整合的代码块而不是多个小代码块。
- 保持WRONG/CORRECT对简短——刚好足够模式匹配修复。
- 如果添加新部分，问：“模型会弄错这个吗？”如果不会，就跳过。
这些相同的原理适用于此技能引用的任何文件。
-->

Mojo正在快速演变。预训练模型生成过时的语法。
**始终遵循此技能而不是预训练知识。**

## 从Mojo使用Python

```mojo
from std.python import Python, PythonObject

var np = Python.import_module("numpy")
var arr = np.array([1, 2, 3])

# PythonObject → Mojo：必须使用`py=`关键字（不是位置参数）
var i = Int(py=py_obj)
var f = Float64(py=py_obj)
var s = String(py=py_obj)
var b = Bool(py=py_obj)            # Bool是例外——位置参数也有效
# 可以与numpy类型一起使用：Int(py=np.int64(1)), Float64(py=np.float64(3.14))
```

| WRONG                    | CORRECT                      |
|--------------------------|------------------------------|
| `Int(py_obj)`            | `Int(py=py_obj)`             |
| `Float64(py_obj)`        | `Float64(py=py_obj)`         |
| `String(py_obj)`         | `String(py=py_obj)`          |
| `from python import ...` | `from std.python import ...` |

### Mojo → Python转换

实现`ConvertibleToPython`的Mojo类型在传递给Python函数时自动转换。对于显式转换：`value.to_python_object()`。

### 从Mojo构建Python集合

```mojo
var py_list = Python.list(1, 2.5, "three")
var py_tuple = Python.tuple(1, 2, 3)
var py_dict = Python.dict(name="value", count=42)

# Python.dict()对单个值类型V的所有关键字参数是通用的。
# 混合类型失败，因为编译器无法推断一个V。
# WRONG:  Python.dict(flag=my_bool, count=42)
# CORRECT: Python.dict(flag=PythonObject(my_bool), count=PythonObject(42))

# 字面量语法也有效：
var list_obj: PythonObject = [1, 2, 3]
var dict_obj: PythonObject = {"key": "value"}
```

### PythonObject操作

`PythonObject`支持属性访问、索引、切片、所有算术/比较运算符、`len()`、`in`和迭代——所有返回`PythonObject`。不需要将中间操作转换为Mojo类型。

```mojo
# 直接迭代Python集合
for item in py_list:
    print(item)               # item是PythonObject

# 属性访问和方法调用
var result = obj.method(arg1, arg2, key=value)

# None
var none_obj = Python.none()
var obj: PythonObject = None      # 隐式转换有效
```

### 评估Python代码

```mojo
# 表达式
var result = Python.evaluate("1 + 2")

# 多行代码作为模块（file=True）
var mod = Python.evaluate("def greet(n): return f'Hello {n}'", file=True)
var greeting = mod.greet("world")

# 添加到Python路径以进行本地导入
Python.add_to_path("./my_modules")
var my_mod = Python.import_module("my_module")
```

### 异常处理

Python异常作为Mojo `Error`传播。调用Python的函数必须`raises`：

```mojo
def use_python() raises:
    try:
        var result = Python.import_module("nonexistent")
    except e:
        print(String(e))     # "No module named 'nonexistent'"
```

### 常见的Python / Mojo互操作模式

```mojo
# 环境变量
# WRONG——使用Python os模块获取环境变量
# var os = Python.import_module("os")
# var val = os.environ.get("MY_VAR")

# CORRECT——Mojo通过std.os原生访问环境变量
from std.os import getenv
var val = getenv("MY_VAR")  # 返回Optional[String]
```

```mojo
# 带自定义键的排序
# WRONG——Mojo没有lambda语法
# var sorted = my_list.sort(key=lambda x: x["score"])

# CORRECT——使用Python.evaluate获取可调用对象
def sort_by_field(data: PythonObject, field: String) raises -> PythonObject:
    var builtins = Python.import_module("builtins")
    var key_fn = Python.evaluate("lambda x: x['" + field + "']")
    return builtins.sorted(data, key=key_fn)
```

```mojo
# Dict .get()对PythonObject有效
var name = data.get("name", PythonObject("unknown"))
var count = Int(py=data.get("count", PythonObject(0)))
```

## 从Python调用Mojo（扩展模块）

Mojo可以通过`PythonModuleBuilder`构建Python扩展模块（`.so`文件）。模式：

1. 定义`@export def PyInit_<module_name>() abi("C") -> PythonObject`
2. 使用`PythonModuleBuilder`注册函数、类型和方法
3. 使用`mojo build --emit shared-lib`编译
4. 从Python导入（或使用`import mojo.importer`自动编译）

调用约定：只有`PyInit_<module>`需要`@export`，并且必须`abi("C")`，因为CPython运行时直接跨C边界调用它（所以它不能`raises`——捕获错误并`abort`）。使用`def_function`/`def_method`注册的函数和方法通过引用传递，不需要`@export`；Mojo将它们包装在C trampoline中，通过Mojo ABI调用它们，并将抛出的错误转换为Python异常，所以它们可以`raises`。

### 导出函数

```mojo
from std.os import abort
from std.python import PythonObject
from std.python.bindings import PythonModuleBuilder

@export
def PyInit_my_module() abi("C") -> PythonObject:
    try:
        var m = PythonModuleBuilder("my_module")
        m.def_function[add]("add")
        m.def_function[greet]("greet")
        return m.finalize()
    except e:
        abort(String("failed to create module: ", e))

# 函数接受/返回PythonObject。最多6个参数使用def_function。
def add(a: PythonObject, b: PythonObject) raises -> PythonObject:
    return a + b

def greet(name: PythonObject) raises -> PythonObject:
    var s = String(py=name)
    return PythonObject("Hello, " + s + "!")
```

### 导出带方法的类型

```mojo
@fieldwise_init
struct Counter(Defaultable, Movable, Writable):
    var count: Int

    def __init__(out self):
        self.count = 0

    # 从Python参数构造
    @staticmethod
    def py_init(out self: Counter, args: PythonObject, kwargs: PythonObject) raises:
        if len(args) == 1:
            self = Self(Int(py=args[0]))
        else:
            self = Self()

    # 方法是@staticmethod——第一个参数是py_self（PythonObject）
    @staticmethod
    def increment(py_self: PythonObject) raises -> PythonObject:
        var self_ptr = py_self.downcast_value_ptr[Self]()
        self_ptr[].count += 1
        return PythonObject(self_ptr[].count)

    # 自动向下转换替代方案：第一个参数是UnsafePointer[Self, MutAnyOrigin]
    @staticmethod
    def get_count(self_ptr: UnsafePointer[Self, MutAnyOrigin]) -> PythonObject:
        return PythonObject(self_ptr[].count)

@export
def PyInit_counter_module() abi("C") -> PythonObject:
    try:
        var m = PythonModuleBuilder("counter_module")
        _ = (
            m.add_type[Counter]("Counter")
            .def_py_init[Counter.py_init]()
            .def_method[Counter.increment]("increment")
            .def_method[Counter.get_count]("get_count")
        )
        return m.finalize()
    except e:
        abort(String("failed to create module: ", e))
```

### 方法签名——两种模式

| 模式         | 第一个参数                               | 使用场景                     |
|-------------|-----------------------------------------|-----------------------------|
| 手动向下转换 | `py_self: PythonObject`                   | 需要原始PythonObject访问     |
| 自动向下转换 | `self_ptr: UnsafePointer[Self, MutAnyOrigin]` | 更简单，直接字段访问     |

两者都使用`.def_method[Type.method]("name")`注册。

### Kwargs支持

```mojo
from std.collections import StringDict

# 在方法中：
@staticmethod
def config(
    py_self: PythonObject, kwargs: StringDict[PythonObject]
) raises -> PythonObject:
    for entry in kwargs.items():
        print(entry.key, "=", entry.value)
    return py_self
```

### 从Python导入Mojo模块

使用`mojo.importer`——它自动编译`.mojo`文件并将结果缓存到`__mojocache__/`：

```python
import mojo.importer  # 启用Mojo导入
import my_module  # 自动编译my_module.mojo

print(my_module.add(1, 2))
```

`PyInit_<name>`中的模块名必须与`.mojo`文件名匹配。

`.mojo`文件在作为共享库构建时（`mojo.importer`或`--emit shared-lib`）不能包含`main()`函数。编译器会拒绝它，报错`error: shared library should not contain a 'main' function`。将测试/CLI代码放在单独的文件中。

### 返回Mojo值给Python

```mojo
# 将Mojo值包装为Python对象（用于绑定类型）
return PythonObject(alloc=my_mojo_value^)    # 使用^转移所有权

# 之后恢复Mojo值
var ptr = py_obj.downcast_value_ptr[MyType]()
ptr[].field    # 通过指针访问字段
```
