# Pydantic 验证

简而言之，Pydantic 是带有运行时验证的数据类。它利用类型提示来理解如何执行验证（以及序列化）。当处理外部不可信数据时，它非常实用，例如在定义 HTTP API 时。

通常不建议使用 Pydantic 来定义用户代码中实例化的类。这样做会失去灵活性（例如，您无法使用 Pydantic 不支持的类型，并且执行初始化后更改更加困难）。在这种情况下，最好使用普通的类（或标准库数据类），因为静态类型检查器已经可以捕获类型不匹配。

## 基本用法

以下是一个使用 Pydantic 模型的简单示例：

```python
from datetime import date

from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str
    age: int = Field(description='人的年龄')
    birthdate: date | None = None


p = Person(name='John', age=20, birthdate='1970-01-01')
```

Pydantic 强制兼容的输入：ISO 日期字符串 `'1970-01-01'` 被解析为 `date`。

## 约束和字段元数据

`Field()` 函数用于提供元数据和约束。您需要区分两种类型的元数据：

* *字段特定*元数据：仅在附加到字段时才有意义的元数据，例如 `deprecated` 和 `alias`。
* *类型特定*元数据：包括 `gt`、`max_length` 等约束，以及影响 JSON Schema 的元数据（例如 `description`、`title`）。

模型字段使用 `Field()` 声明，使用赋值形式：

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    first_name: str = Field(alias='name')
```

或使用注解模式：

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    value: Annotated[int, Field(deprecated=True)] = 1
```

注解模式有一些优点：

* 使用 `f: <type> = Field()` 形式（无默认值）可能会令人困惑，并可能让用户误以为 `f` 有默认值，而实际上字段仍然是必需的。
* 您可以为字段提供任意数量的元数据元素。如上例所示，`Field()` 函数仅支持有限的一组约束/元数据，在某些情况下您可能需要使用不同的 Pydantic 工具，例如 `WithJsonSchema`。

但请注意：

* 对于静态类型检查器有意义的元数据，应使用赋值形式。这包括：`alias`、`default` 和 `default_factory`。
* *字段特定*元数据只能用于“顶层”类型。一个常见的陷阱是这样做：

    ```python
    from typing import Annotated

    from pydantic import BaseModel, Field


    class Model(BaseModel):
        field_bad: Annotated[int, Field(deprecated=True)] | None = None
        field_ok: Annotated[int | None, Field(deprecated=True)] = None
    ```

  *字段特定*元数据应适用于此示例中的整个联合。

### 约束

尽可能使用“内置”验证约束，而不是定义自定义验证器：

```python
from typing import Annotated

from annotated_types import Gt  # annotated_types 是 `Field()` 函数的替代方案。
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    constrained_int_ok: Annotated[int, Gt(1)]  # 这是好的

    constrained_int_bad: int

    @field_validator('constrained_int_bad')  # 这是坏的
    @classmethod
    def validate(cls, v: int) -> int:
        if not v > 1:
            raise ValueError('值不大于 1')
        return v
```

有时，约束无法使用 `Field()` 函数表达。例如，字符串约束（如 `strip_whitespace`、`to_upper`、`to_lower` 和 `ascii_only`）只能使用 `pydantic.StringConstraints` 指定：

```python
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class Model(BaseModel):
    # 代替调用 s.strip() 的验证器：
    a: Annotated[str, StringConstraints(strip_whitespace=True)]
```

<https://pydantic.dev/docs/validation/latest/api/pydantic/standard_library_types/> 是所有支持的标凈库类型及其约束的规范文档。

### 验证器

在某些情况下，您可能需要使用自定义验证器。尽可能使用*后置*验证器。因为它们在 Pydantic 验证之后运行，所以值已经是字段的类型。如果您使用*前置*验证器，输入数据可以是任何东西，因此更容易出错（特别是对于模型验证器，输入不一定是字典，也可能是任意对象）。

如果可能，请使用注解模式来定义验证器：

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel, field_validator


def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} 不是偶数')
    return value


class Model(BaseModel):
    # 建议这种形式：验证器紧跟字段旁边，易于理解
    even: Annotated[int, AfterValidator(is_even)]
    odd: int

    # 如果您将验证器定义为装饰器，请确保将其定义为类方法。
    @field_validator('odd', mode='after')
    @classmethod
    def is_odd(cls, value: int) -> int:
        if value % 2 == 0:
            raise ValueError(f'{value} 不是奇数')
        return value
```

使用装饰器模式可能导致行为不明确，特别是在验证器运行顺序方面（特别是在子类上）。

### 类型转换、集合和联合

除非您使用[严格模式](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/)，否则 Pydantic 在大多数情况下会应用类型转换。例如，对于类型为 `int` 的字段，字符串 `'123'` 也会被接受。这也适用于集合类型：`list[str]` 也接受元组、集合等。

这就是为什么您应该避免：

* 使用联合，如 `int | str`，如果您的目标是通过验证器将 `str` 强制转换为 `int`。
* 使用抽象集合，如 `collections.abc.Sequence`，如果您的目标是可以接受列表和元组。使用这些抽象集合效率低下。

在一般情况下，最好避免使用联合，因为每个使用字段的操作都需要在对其进行任何操作之前检查每个类型。

### 前向注解

Python 允许使用字符串编写注解作为前向引用。这可能导致 Pydantic 在评估它们时遇到挑战，因此如果可能，最好避免使用。

如果您在模块中定义 Pydantic 模型，如果可能的话，避免使用 `from __future__ import annotations`（默认情况下会将所有注解转换为字符串）。仅将显式引号添加到尚未定义的注解中，例如：

```python
from pydantic import BaseModel


class Model(BaseModel):
    self_ref: 'Model'
```

还请注意，在 Python >= 3.14 中，注解评估被延迟，因此您不应使用字符串注解。

#### 递归类型别名

您可能会想这样定义别名：

```python
from typing import TypeAlias

JsonValue: TypeAlias = 'list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None'
```

别名需要加引号，因为它具有递归性。Pydantic 通常*不会*能够评估带引号的 `TypeAlias`。相反，请使用显式类型别名（Python 3.12+ 上的 `type`，或 `TypeAliasType`），Pydantic 可以解析它们：

```python
type JsonValue = list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None
# 或者，如果不在 Python >= 3.12 上：
from typing_extensions import TypeAliasType

JsonValue = TypeAliasType('JsonValue', 'list[JsonValue] | dict[str, JsonValue] | str | bool | int | float | None')
```

### 模型子类、区分联合

子类是一个常见的 Python 模式，但在 Pydantic 中可能是一个陷阱。您可能会想这样做：

```python
from pydantic import BaseModel


class Base(BaseModel):
    base_field: int

    def common_method(self) -> None: ...


class Sub1(Base):
    sub1_field: str


class Sub2(Base):
    sub2_field: bool


class Main(BaseModel):
    model: Base


m: Main = Main(model=Sub1(base_field=1, sub1_field='test'))
```

这个示例可以工作，但在序列化 `m` 时不会按预期工作：

```python
m.model_dump()
#> {'model': {'base_field': 1}} -> sub1_field 缺失
```

这是因为 Pydantic 根据声明的类型（`Base`）进行序列化，而不是运行时子类。验证遵循相同的规则：`Main(model={'base_field': 1, 'sub1_field': 'test'})` 对 `Base` 进行验证，因此忽略 `sub1_field` 而不是创建 `Sub1` 实例。

相反，请尝试使用区分联合（前提是您可以设置一个 `type` 字段来区分模型）：

```python
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field


class Sub1(Base):
    type: Literal['sub1']
    sub1_field: str


class Sub2(Base):
    type: Literal['sub2']
    sub2_field: bool


Subs: TypeAlias = Annotated[Sub1 | Sub2, Field(discriminator='type')]


class Main(BaseModel):
    model: Subs
```

或者使用泛型：

```python
from pydantic import BaseModel


class Main[BaseT: Base](BaseModel):
    model: BaseT


m: Main[Sub1] = Main[Sub1](model={'base_field': 1, 'sub1_field': 'test'})  # 会工作
```

如果区分联合和泛型都不适用，可以使用[多态序列化](https://pydantic.dev/docs/validation/latest/concepts/serialization/#polymorphic-serialization)（Pydantic >=2.13）或[*序列化为任意*](https://pydantic.dev/docs/validation/latest/concepts/serialization/#serializing-as-any)（Pydantic <2.13）作为最后的手段。
