# PyTorch 文档字符串编写指南

本指南描述了如何在 PyTorch 项目中为函数和方法编写文档字符串，遵循 `torch/_tensor_docs.py` 和 `torch/nn/functional.py` 中的约定。

## 基本原则

- 使用原始字符串 (`r"""..."""`) 编写所有文档字符串，以避免 LaTeX/数学反斜杠问题
- 遵循 Sphinx/reStructuredText (reST) 格式编写文档
- 保持**简洁但完整** - 包含所有必要信息
- 总是在可能的情况下包含**示例**
- 使用**交叉引用**链接到相关的函数/类

## 文档字符串结构

### 1. 函数签名（第一行）

以显示所有参数的函数签名开头：

```python
r"""function_name(param1, param2, *, kwarg1=default1, kwarg2=default2) -> ReturnType
```

**注意：**
- 包含函数名
- 显示位置参数和仅关键字参数（使用 `*` 分隔）
- 包含默认值
- 显示返回类型注解
- 这一行**不应**以句号结尾

### 2. 简要描述

提供一行描述函数的作用：

```python
r"""conv2d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1) -> Tensor

对由多个输入平面组成的输入图像应用 2D 卷积。
```

### 3. 数学公式（如适用）

使用 Sphinx 数学指令编写数学表达式：

```python
.. math::
    \text{Softmax}(x_{i}) = \frac{\exp(x_i)}{\sum_j \exp(x_j)}
```

或内联数学： `:math:\`x^2\``

### 4. 交叉引用

使用 Sphinx 角色链接到相关的类和函数：

- `:class:\`~torch.nn.ModuleName\`` - 链接到类
- `:func:\`torch.function_name\`` - 链接到函数
- `:meth:\`~Tensor.method_name\`` - 链接到方法
- `:attr:\`attribute_name\`` - 引用属性
- `~` 前缀仅显示最后一部分（例如，`Conv2d` 而不是 `torch.nn.Conv2d`）

**示例：**
```python
See :class:`~torch.nn.Conv2d` 了解详细信息和输出形状。
```

### 5. 注意和警告

使用提示信息显示重要信息：

```python
.. note::
    此函数不能直接与 NLLLoss 一起使用，
    NLLLoss 期望在 Softmax 和其自身之间计算 Log。
    使用 log_softmax（它更快且具有更好的数值特性）。

.. warning::
    :func:`new_tensor` 总是复制 :attr:`data`。如果你有一个 Tensor
    ``data`` 并想避免复制，请使用 :func:`torch.Tensor.requires_grad_`
    或 :func:`torch.Tensor.detach`.
```

### 6. Args 部分

使用类型注解和描述记录所有参数：

```python
Args:
    input (Tensor): 输入张量，形状为 :math:`(\text{minibatch} , \text{in\_channels} , iH , iW)`
    weight (Tensor): 过滤器，形状为 :math:`(\text{out\_channels} , kH , kW)`
    bias (Tensor, optional): 可选的偏差张量，形状为 :math:`(\text{out\_channels})`。默认: ``None``
    stride (int or tuple): 卷积核的步长。可以是单个数字或
      元组 `(sH, sW)`。默认: 1
```

**格式规则：**
- 参数名使用**小写**
- 类型用括号括起来: `(Type)`，`(Type, optional)` 用于可选参数
- 描述紧跟在类型之后
- 对于可选参数，在末尾包含 "Default: ``value``"
- 使用双反引号表示内联代码：``` ``None`` ```
- 将续行缩进 2 个空格

### 7. 关键字参数部分（如适用）

有时关键字参数会单独记录：

```python
Keyword args:
    dtype (:class:`torch.dtype`, optional): 返回张量的期望类型。
        默认: 如果为 None，与该张量相同的 :class:`torch.dtype`
    device (:class:`torch.device`, optional): 返回张量的期望设备。
        默认: 如果为 None，与该张量相同的 :class:`torch.device`
    requires_grad (bool, optional): 如果 autograd 应该记录返回张量上的操作。默认: ``False``.
```

### 8. Returns 部分（如需要）

记录返回值：

```python
Returns:
    Tensor: 从 Gumbel-Softmax 分布中采样的张量，形状与 `logits` 相同。
        如果 ``hard=True``，返回的样本将是 one-hot，否则它们将是
        概率分布，在 `dim` 上求和为 1。
```

或者如果从上下文中明显，可以在函数签名行中直接包含。

### 9. 示例部分

尽可能包含示例：

```python
Examples::

    >>> inputs = torch.randn(33, 16, 30)
    >>> filters = torch.randn(20, 16, 5)
    >>> F.conv1d(inputs, filters)

    >>> # 使用正方形核和相同步长
    >>> filters = torch.randn(8, 4, 3, 3)
    >>> inputs = torch.randn(1, 4, 5, 5)
    >>> F.conv2d(inputs, filters, padding=1)
```

**格式规则：**
- 使用 `Examples::` 并带双冒号
- 使用 `>>>` 提示符表示 Python 代码
- 当有帮助时使用 `#` 注释
- 当有助于理解时显示实际输出（缩进，不带 `>>>`）

### 10. 外部引用

链接到论文或外部文档：

```python
.. _Link Name:
    https://arxiv.org/abs/1611.00712
```

在文本中引用： ```See `Link Name`_```

## 方法类型

### 原生 Python 函数

对于普通 Python 函数，使用标准文档字符串：

```python
def relu(input: Tensor, inplace: bool = False) -> Tensor:
    r"""relu(input, inplace=False) -> Tensor

    对每个元素应用整流线性单元函数。更多详情请见
    :class:`~torch.nn.ReLU`。
    """
    # 实现
```

### C 绑定函数（使用 add_docstr）

对于 C 绑定函数，使用 `_add_docstr`：

```python
conv1d = _add_docstr(
    torch.conv1d,
    r"""
conv1d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1) -> Tensor

对由多个输入平面组成的输入信号应用 1D 卷积。

详情和输出形状请见 :class:`~torch.nn.Conv1d`。

Args:
    input: 输入张量，形状为 :math:`(\text{minibatch} , \text{in\_channels} , iW)`
    weight: 过滤器，形状为 :math:`(\text{out\_channels} , kW)`
    ...
""",
)
```

### 原地变体

对于原地操作（以 `_` 结尾），引用原始函数：

```python
add_docstr_all(
    "abs_",
    r"""
abs_() -> Tensor

:method:`~Tensor.abs` 的原地版本
""",
)
```

### 别名函数

对于别名，直接引用原始函数：

```python
add_docstr_all(
    "absolute",
    r"""
absolute() -> Tensor

:func:`abs` 的别名
""",
)
```

## 常见模式

### 形状文档

使用 LaTeX 数学符号记录张量形状：

```python
:math:`(\text{minibatch} , \text{in\_channels} , iH , iW)`
```

### 可重用参数定义

对于常用参数，定义一次并重用：

```python
common_args = parse_kwargs(
    """
    dtype (:class:`torch.dtype`, optional): 返回张量的期望类型。
        默认: 如果为 None，与该张量相同。
"""
)

# 然后使用 .format()：
r"""
...

Keyword args:
    {dtype}
    {device}
""".format(**common_args)
```

### 模板插入

插入可重复性说明或其他常见文本：

```python
r"""
{tf32_note}

{cudnn_reproducibility_note}
""".format(**reproducibility_notes, **tf32_notes)
```

## 完整示例

以下示例展示了所有元素：

```python
def gumbel_softmax(
    logits: Tensor,
    tau: float = 1,
    hard: bool = False,
    eps: float = 1e-10,
    dim: int = -1,
) -> Tensor:
    r"""
    从 Gumbel-Softmax 分布中采样并可选离散化。

    Args:
        logits (Tensor): `[..., num_features]` 未归一化的对数概率
        tau (float): 非负标量温度
        hard (bool): 如果 ``True``，返回的样本将被离散化为 one-hot 向量，
              但在 autograd 中将被差异化。默认: ``False``
        dim (int): softmax 计算的维度。默认: -1

    Returns:
        Tensor: 形状与 `logits` 相同的 Gumbel-Softmax 分布中采样的张量。
            如果 ``hard=True``，返回的样本将是 one-hot，否则它们将是
            概率分布，在 `dim` 上求和为 1。

    .. note::
        此函数是为了遗留原因，未来可能从 nn.Functional 中移除。

    Examples::
        >>> logits = torch.randn(20, 32)
        >>> # 使用重参数化技巧采样软分类：
        >>> F.gumbel_softmax(logits, tau=1, hard=False)
        >>> # 使用 "Straight-through" 技巧采样硬分类：
        >>> F.gumbel_softmax(logits, tau=1, hard=True)

    .. _Link 1:
        https://arxiv.org/abs/1611.00712
    """
    # 实现
```

## 快速检查清单

编写 PyTorch 文档字符串时，请确保：

- [ ] 使用原始字符串 (`r"""`)
- [ ] 在第一行包含函数签名
- [ ] 提供简要描述
- [ ] 在 Args 部分用类型记录所有参数
- [ ] 包含可选参数的默认值
- [ ] 使用 Sphinx 交叉引用 (`:func:`, `:class:`, `:meth:`)
- [ ] 如适用，添加数学公式
- [ ] 在 Examples 部分至少包含一个示例
- [ ] 添加警告/提示以说明重要注意事项
- [ ] 使用 `:class:` 链接到相关模块类
- [ ] 使用正确的数学符号记录张量形状
- [ ] 保持一致的格式和缩进

## 常见 Sphinx 角色参考

- `:class:\`~torch.nn.Module\`` - 类引用
- `:func:\`torch.function\`` - 函数引用
- `:meth:\`~Tensor.method\`` - 方法引用
- `:attr:\`attribute\`` - 属性引用
- `:math:\`equation\`` - 内联数学
- `:ref:\`label\`` - 内部引用
- ``` ``code`` ``` - 内联代码（使用双反引号）

## 其他说明

- **缩进**：代码使用 4 个空格，参数描述续行使用 2 个空格
- **行长度**：尽可能保持行长度在 100 个字符以内
- **句号**：句子以句号结尾，但签名行不以句号结尾
- **反引号**：使用双反引号表示代码：``` ``True`` ``None`` ``False`` ```
- **类型**：常见类型包括 `Tensor`，`int`，`float`，`bool`，`str`，`tuple`，`list` 等
