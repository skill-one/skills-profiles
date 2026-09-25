# Pyrefly 类型覆盖率技能

## 前置条件
- 文件必须位于具有 `pyrefly.toml` 的项目中。
- `pyrefly`、`lintrunner` 和项目的测试运行器必须在 PATH 环境变量中。**如果其中任何一个缺失，请停止并询问是否需要激活 conda 环境** —— 不要安装或替换（根据仓库 CLAUDE.md 的规定）。

### 第 1 步：移除文件级别的类型检查抑制

从文件顶部删除以下内容（pyrefly 兼容 `# mypy: ignore-errors`，因此必须删除）：

```python
# pyre-ignore-all-errors
# pyre-ignore-all-errors[16,21,53,56]
# @lint-ignore-every PYRELINT
# mypy: ignore-errors
```

### 第 2 步：向 `pyrefly.toml` 添加子配置条目

```toml
[[sub-config]]
matches = "path/to/directory/**"
[sub-config.errors]
implicit-import = false
implicit-any = true
bad-param-name-override = false
unannotated-return = true
unannotated-parameter = true
```

**重要提示**：在 `[sub-config.errors]` 中设置任何错误键仅会覆盖相对于父配置的该键，但启用 `unannotated-return` / `unannotated-parameter` / `implicit-any` 将会重新暴露之前被文件级隐藏的错误。如果你看到无关的错误（例如，`bad-param-name-override`）大量涌入输出，请在子配置中镜像父配置的该键设置以抑制它们。

### 第 3 步：运行 pyrefly

```bash
pyrefly check <FILENAME>
```

**目标**：通过添加注解解决所有 `unannotated-return`、`unannotated-parameter` 和 `implicit-any` 错误——参见第 4 步的阶梯。这三个目标类别总是可以解决的；**永远**不要用 `# pyrefly: ignore` 抑制它们。唯一的例外是 `@compatibility(is_backward_compatible=True)`（第 4 步）。

其他类别（`bad-argument-type`、`missing-attribute` 等）是真实的类型错误。根据 pyrefly 报告的位置处理它们：

- **报告在其他文件中**（路径 != 目标）：保留它。不要扩大范围。如果错误现在阻塞了目标，请在报告位置用 `# pyrefly: ignore[<类别>]  # TODO` 抑制。
- **报告在目标文件中，但消息名称指代其他位置定义的符号**（例如，因为导入函数的注解错误导致 `bad-return`）：
  本地抑制并添加相同的 TODO 注释。不要发明一个 `cast()` 来掩盖上游的差距。
- **报告在目标文件中，源自本地**：修复它。

仅作为最后手段使用 `# pyrefly: ignore[...]`，并且仅用于非目标类别。

### 第 4 步：添加注解

当函数体无法从右类型推断时，检查调用位置。

#### 注解规范

- 使用 PEP 604 / PEP 585 语法（`int | None`、`list[str]`）——假设 Python 版本 >= 3.10。
- 优先使用 `collections.abc` 而不是 `typing` 用于 ABC（`Callable`、`Sequence`、`Generator` 等）。
- 对于通用辅助函数，当项目最低 Python 版本可用时从 `typing` 导入，并且仅在需要较新功能时（例如，支持 < 3.11/3.12 的 `Self` 和 `override`，或 PEP 696 `default=` 用于 `TypeVar` / `ParamSpec`）从 `typing_extensions` 导入。不要从 `typing_extensions` 进行全盘导入。
- 始终参数化 `Callable`（永远不要使用裸 `Callable`）。优先使用 `Callable[..., object]`；仅在调用方确实消费动态返回时使用 `Callable[..., Any]` —— 如果结果只是传递（或调用方未调用该可调用对象），`object` 更严格且同样正确。（见下文的 ParamSpec 案例说明。）
- 为你**引入**的任何模块级全局变量添加前导下划线——`TypeVar`/`ParamSpec`（匹配字符串参数：`_T = TypeVar("_T")`、`_P = ParamSpec("_P")`、`_R = TypeVar("_R")`）、`TypeAlias`、辅助常量和哨兵。这是非公开名称的普遍惯例（在树中 `_P` 比 `P` 多约 6:1）。例外（保留未加下划线）：
  由其他模块导入的名称、列在 `__all__` 中或用作运行时标记（例如，注解字符串分派标记）的名称。仅适用于你添加的名称——**不要**重命名现有的全局变量；那是与此技能范围外的重构无关的操作。
- 布尔谓词——`is_*`/`has_*` 名称，接受广泛类型（通常为 `object`），返回 `bool`——通常需要 `TypeGuard[X]`（或 `TypeIs[X]`，它也缩小了负分支）。`TypeGuard` 在 `typing` 中（>= 3.10，因此从那里导入）；`TypeIs` 仅在 3.13 中进入 `typing`，因此从 `typing_extensions`（>= 4.10）导入以保持 3.10 兼容性。类似 `issubclass` 风格的辅助函数接受 `klass: type[_T]` 返回 `TypeGuard[type[_T]]`。优先使用显式的 `isinstance(x, type)` 护卫而不是围绕 `issubclass()` 的 `try/except TypeError` —— 更清晰，并且它允许检查器缩小。
- 当返回类型是从参数派生时——传递/身份函数、返回“这些参数之一”的辅助函数、装饰器、按类型键值的注册表——使用 `TypeVar`（或，对于签名流经的可调用参数，使用 `Callable[_P, _R]` 与 `ParamSpec`/`TypeVar`）而不是扩展到 `object`/`Any`。`输出类型 == 某些输入类型` 正是 `TypeVar` 编码的内容；`object` 在 / `object` 出会丢弃它。注意：如果函数*转换*了值，使得输出类型与输入类型不同（例如，将数组转换为整数），单个 `TypeVar` 是错误的——命名实际的域类型。
- 在 `__init__` 中分配的类属性应获得类级注解，以便 pyrefly 可以看到它们。
- 用 `if TYPE_CHECKING:` 打破导入循环——注解仅导入在守卫内，并使用 `from __future__ import annotations`（或字符串前向引用）以保持运行时导入惰性：
  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from torch.fx import GraphModule
  def transform(gm: GraphModule) -> GraphModule: ...
  ```
- **永远不要抑制这三个目标类别。** `unannotated-return`、`unannotated-parameter` 和 `implicit-any` 总是通过添加注解可以解决；`# pyrefly: ignore[<其中一个>]` 不是可接受的成果。唯一的例外是下文的向后兼容性例外。
- **放宽，不要放弃。** 当正确的类型难以推断时，沿着这个阶梯走而不是使用忽略：
  1. 从调用位置和返回路径可观察到的最具体的具体类型。
  2. 一个联合（`X | Y`）、`Sequence[X]` 风格的抽象类型，或用于真正通用函数的绑定 `TypeVar`。
  3. `object`——最严格的回退，仍然可以类型检查。迫使调用者在使用前缩小，例如，`def serialize(value: object) -> str:`。视觉上类似于 `Any` 但更严格——pyrefly 会拒绝 `value.foo()` 而没有 `isinstance`。
  4. `Any`——最后一级。始终优先于目标类别上的 `# pyrefly: ignore`，但仅在 1–3 失败后。能够说明为什么每个早期阶梯不适用（例如，“联合超过 8 种类型”，“没有可观察的共同边界”，“调用方确实永远不会缩小”）。
- 对返回位置中的 `object`/`Any` 要特别小心——函数通常比调用方更了解它生成的内容。只有在真实边界（它返回其输入不变，或值由处理程序/调用方定义）处宽泛返回才是正确的；如果体构建了已知形状，命名它（域别名或联合优于 `object`）。
- 在决定参数必须是 `Any` 之前至少阅读三个调用位置——不要在第一次尝试时根据“看起来动态”的模式匹配。
- 范围窄的 `# pyrefly: ignore[...]`（在非目标类别上）保留用于 pyrefly 实际上错误地报告特定本地错误的情况——动态元编程、第三方桩间隙：
  ```python
  # pyrefly: ignore[attr-defined]
  result = getattr(obj, dynamic_name)()
  ```
- 当内联 `# pyrefly: ignore[...]` 会将一行推过长度限制时，将其放在标记行立即上方，而不是使用 `# fmt: skip` 保持内联——pyrefly 尊重前一行忽略。（例外：下文的向后兼容性例外，必须位于 `def` 行。）

#### 向后兼容性（唯一不抑制的例外）

**关键**：装饰有 `@compatibility(is_backward_compatible=True)` 的函数**不能**更改其签名。向后兼容性测试（`test_function_back_compat`）比较字符串化的 `inspect.signature` 与黄金文件——添加注解（即使是 `-> None`）会改变该字符串并导致测试失败。使用 pyrefly 忽略注释：

```python
@compatibility(is_backward_compatible=True)
def my_function(  # pyrefly: ignore[unannotated-return]
    self,
    arg1,  # 也不能在这里添加类型
):
    ...
```

`# pyrefly: ignore` 注释必须在 `def` 行（pyrefly 报告错误的位置），而不是在闭合的 `)`。

**ParamSpec 用于签名保留的包装器**（装饰器、`functools.wraps` 风格的辅助函数）。使用 `Callable[P, R]` 以使包装函数的签名流经到调用方——`Callable[..., Any]` 会丢失它。如果包装器确实接受任意可调用对象，则跳过 ParamSpec。与 `Concatenate[X, P]` 配对，当包装器预置或追加参数时。

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

def log_calls(fn: Callable[_P, _R]) -> Callable[_P, _R]:
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        return fn(*args, **kwargs)
    return wrapper
```

### 第 5 步：迭代

重新运行 `pyrefly check`。新的注解通常会暴露函数实际返回不兼容类型的 `bad-return` 错误——修复这些。重复直到干净。

收紧共享辅助函数（例如，添加 `TypeGuard` 或精确返回）可能会使调用者中的预存 `# pyrefly: ignore` 注释失效。重新检查并删除现已过时的抑制和任何陈旧的说明注释——不要留下。

### 第 6 步：检查

提交前必须执行——注解经常改变导入顺序和行长度：

```bash
lintrunner -a <files...>
```

手动解决 `lintrunner` 无法自动修复的任何问题。

### 第 7 步：测试

**失败时的优先级**：测试通过 > pyrefly 清洁 > 注解严格性。如果新添加的注解破坏了测试，请在纪律阶梯中缩小一级（例如，具体 → `object`，或移除导致下游 `isinstance` 检查失败的 `Any` 扩展）之前回滚文件。

1. **向后兼容性检查。** 仅当
   `grep -l '@compatibility(is_backward_compatible=True)' <target>` 返回文件时运行——装饰器是黄金文件的实际先决条件。更广泛的“导入 `torch.fx`”启发式规则捕获了 `torch/` 的一半。
   ```bash
   python -m pytest test/test_fx.py::TestFXAPIBackwardCompatibility -x -v
   ```

2. **修改模块的单元测试。** 在得出不存在覆盖率之前双向搜索：
   ```bash
   # torch/foo/bar.py 通常由 test/test_foo.py 或 test/test_bar.py 覆盖
   ls test/ | grep -i <module-name>
   # 或通过导入
   grep -rl "from torch.foo.bar import\|import torch.foo.bar" test/
   ```

   如果两者都为空，请告知用户——不要静默跳过。类型更改可能引入真实的运行时回归（`Optional[X]` vs `X`，`.append` 被调用时的 `Sequence` vs `list` 等）。

## 注意事项

- **类体中的前向引用** 而没有 `from __future__ import annotations` 仍然需要字符串引用：
  ```python
  class MyClass:
      def __new__(cls) -> "MyClass": ...
  ```
- **提交**：除非用户明确要求（根据仓库 CLAUDE.md），否则不要提交。当文件干净时停止并显示差异以供审查。
