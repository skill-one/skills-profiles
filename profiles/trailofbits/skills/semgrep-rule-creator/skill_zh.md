# Semgrep 规则创建器

使用适当的测试和验证来创建生产级 Semgrep 规则。

## 使用场景

**理想场景：**
- 为特定漏洞模式编写 Semgrep 规则
- 编写规则以检测代码库中的安全漏洞
- 编写用于数据流漏洞的 taint 模式规则
- 编写用于强制执行编码标准的规则

## 不应使用场景

**请勿使用此技能用于：**
- 运行现有的 Semgrep 规则集
- 在没有自定义规则的情况下进行一般静态分析（使用 `static-analysis` 技能）

## 拒绝的常见理由

在编写 Semgrep 规则时，拒绝以下常见捷径：

- **"模式看起来是完整的"** → 仍然运行 `semgrep --test --config <rule-id>.yaml <rule-id>.<ext>` 进行验证。未经测试的规则存在隐藏的误报/漏报。
- **"它匹配了漏洞情况"** → 匹配漏洞只是工作的一半。验证安全情况不匹配（误报会破坏信任）。
- **"taint 模式对这种情况来说过于复杂"** → 如果数据从用户输入流向危险接收端，taint 模式比模式匹配提供更好的精确性。
- **"一个测试就足够了"** → 包括边界情况：不同的编码风格、清理输入、安全替代方案和边界条件。
- **"我会先优化模式"** → 先编写正确的模式，通过所有测试后再优化。过早优化会导致回归。
- **"抽象语法树转储太复杂"** → 抽象语法树揭示了 Semgrep 如何看待代码。跳过它会导致忽略语法变体的模式。

## 反模式

**过于宽泛** - 匹配所有内容，对检测无用处：
```yaml
# BAD: 匹配任何函数调用
pattern: $FUNC(...)

# GOOD: 特定的危险函数
pattern: eval(...)
```

**测试中缺少安全情况** - 导致未检测到的误报：
```python
# BAD: 仅测试漏洞情况
# ruleid: my-rule
dangerous(user_input)

# GOOD: 包括安全情况以验证无误报
# ruleid: my-rule
dangerous(user_input)

# ok: my-rule
dangerous(sanitize(user_input))

# ok: my-rule
dangerous("hardcoded_safe_value")
```

**过于具体的模式** - 错过变体：
```yaml
# BAD: 仅匹配确切格式
pattern: os.system("rm " + $VAR)

# GOOD: 匹配所有 os.system 调用并使用 taint 跟踪
mode: taint
pattern-sources:
  - pattern: input(...)
pattern-sinks:
  - pattern: os.system(...)
```

## 严格级别

此工作流是**严格**的 - 不要跳过步骤：
- **先阅读文档**：在编写 Semgrep 规则前，请查看 [文档](#documentation)
- **测试优先是强制性的**：编写规则前必须先编写测试
- **必须通过 100% 测试**："大部分测试通过"是不可接受的
- **优化最后进行**：只有在所有测试通过后才能简化模式
- **避免通用模式**：规则必须具体，不能匹配宽泛的模式
- **优先考虑 taint 模式**：用于数据流漏洞
- **一个 YAML 文件 - 一个 Semgrep 规则**：每个 YAML 文件必须只包含一个 Semgrep 规则；不要将多个规则合并到一个文件中
- **无通用规则**：针对特定语言编写 Semgrep 规则时 - 避免通用模式匹配（`languages: generic`）
- **禁止 `todook` 和 `todoruleid` 测试注解**：在测试文件中禁止使用 `todoruleid: <rule-id>` 和 `todook: <rule-id>` 注解，以供未来改进规则

## 概述

此技能指导创建检测安全漏洞和代码模式的 Semgrep 规则。规则是迭代创建的：分析问题，先编写测试，分析抽象语法树结构，编写规则，迭代直到所有测试通过，优化规则。

**方法选择：**
- **taint 模式（优先）**：数据流问题，其中不受信任的输入到达危险接收端
- **模式匹配**：简单的语法模式，没有数据流要求

**为什么优先考虑 taint 模式？** 模式匹配发现语法但忽略上下文。模式 `eval($X)` 匹配 `eval(user_input)`（漏洞）和 `eval("safe_literal")`（安全）。taint 模式跟踪数据流，因此仅在不受信任的数据实际到达接收端时才会发出警报，大大减少注入漏洞的误报。

**在方法之间迭代**：实验是可以的。如果你从 taint 模式开始，但效果不佳（例如，taint 未能按预期传播，误报/漏报过多），切换到模式匹配。反之，如果模式匹配在安全情况下产生过多误报，尝试 taint 模式。目标是工作规则 - 而不是死守一种方法。

**输出结构** - 目录名称为规则 ID，恰好包含 2 个文件：
```
<rule-id>/
├── <rule-id>.yaml     # Semgrep 规则
└── <rule-id>.<ext>    # 测试文件，包含 ruleid/ok 注解
```

## 快速入门

```yaml
rules:
  - id: insecure-eval
    languages: [python]
    severity: HIGH
    message: 用户输入传递给 eval() 允许代码执行
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
    pattern-sinks:
      - pattern: eval(...)
```

测试文件 (`insecure-eval.py`)：
```python
# ruleid: insecure-eval
eval(request.args.get('code'))

# ok: insecure-eval
eval("print('safe')")
```

运行测试（从规则目录）: `semgrep --test --config <rule-id>.yaml <rule-id>.<ext>`

## 快速参考

- 关于命令、模式运算符和 taint 模式语法，请参阅 [quick-reference.md]({baseDir}/references/quick-reference.md)。
- 关于详细工作流程和示例，你必须查看 [workflow.md]({baseDir}/references/workflow.md)

## 工作流程

复制此清单并跟踪进度：

```
Semgrep 规则进度：
- [ ] 第 1 步：分析问题
- [ ] 第 2 步：先编写测试
- [ ] 第 3 步：分析抽象语法树结构
- [ ] 第 4 步：编写规则
- [ ] 第 5 步：迭代直到所有测试通过（semgrep --test）
- [ ] 第 6 步：优化规则（删除冗余，重新测试）
- [ ] 第 7 步：最终运行
```

## 文档

**必须**：在编写任何规则前，使用 WebFetch 阅读**所有**以下 7 个 Semgrep 文档链接：

1. [规则语法](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/rule-syntax.mdx)
2. [模式语法](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/pattern-syntax.mdx)
3. [测试规则](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/testing-rules.mdx)
4. [taint 分析](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/data-flow/taint-mode/overview.mdx)
5. [taint 分析的高级技术](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/data-flow/taint-mode/advanced.mdx)
6. [常量传播](https://raw.githubusercontent.com/semgrep/semgrep-docs/refs/heads/main/docs/writing-rules/data-flow/constant-propagation.mdx)
7. [Trail of Bits 测试手册 - Semgrep 章节](https://raw.githubusercontent.com/trailofbits/testing-handbook/refs/heads/main/content/docs/static-analysis/semgrep/10-advanced.md)
