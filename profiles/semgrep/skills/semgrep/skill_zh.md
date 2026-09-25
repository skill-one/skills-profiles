# Semgrep 静态分析

快速、基于模式的静态分析，用于安全扫描和自定义规则创建。

## 可用的 MCP 工具

如果您的环境中提供了 Semgrep MCP 工具，请优先使用它们进行扫描：

- **`semgrep_scan`** — 使用内置规则集扫描代码文件中的安全漏洞。传递绝对文件路径和可选配置（例如，`p/security-audit`，`auto`）。
- **`semgrep_scan_with_custom_rule`** — 使用您编写的自定义 YAML 规则扫描代码。将代码内容内联传递以及规则。
- **`semgrep_findings`** — 从 Semgrep AppSec 平台获取存储库的现有发现。
- **`semgrep_rule_schema`** — 获取编写 Semgrep 规则的完整架构。
- **`get_supported_languages`** — 列出 Semgrep 支持的所有语言。

当 MCP 工具不可用时，请回退到下面的 CLI 命令。

## 何时使用 Semgrep

**理想场景：**
- 快速安全扫描（分钟，而不是小时）
- 基于模式的错误和漏洞检测
- 强制编码标准和最佳实践
- 查找已知的漏洞模式（OWASP，CWE）
- 为您的代码库创建自定义检测规则
- 带有污染模式的控制流分析

## 安装（CLI）

```bash
# pip（推荐）
python3 -m pip install semgrep

# Homebrew
brew install semgrep

# Docker
docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep --config auto /src
```

---

# 第一部分：运行扫描

## 快速扫描

```bash
semgrep --config auto .                    # 自动检测规则
```

## 使用规则集

```bash
semgrep --config p/<RULESET> .             # 单个规则集
semgrep --config p/security-audit --config p/trailofbits .  # 多个
```

| 规则集 | 描述 |
|---------|-------------|
| `p/default` | 通用安全和代码质量 |
| `p/security-audit` | 全面安全规则 |
| `p/owasp-top-ten` | OWASP Top 10 漏洞 |
| `p/cwe-top-25` | CWE Top 25 漏洞 |
| `p/trailofbits` | Trail of Bits 安全规则 |
| `p/python` | Python 特定 |
| `p/javascript` | JavaScript 特定 |
| `p/golang` | Go 特定 |

## 输出格式

```bash
semgrep --config p/security-audit --sarif -o results.sarif .   # SARIF
semgrep --config p/security-audit --json -o results.json .     # JSON
```

## 扫描特定路径

```bash
semgrep --config p/python app.py           # 单个文件
semgrep --config p/javascript src/         # 目录
semgrep --config auto --include='**/test/**' .  # 包含测试
```

## 配置

### .semgrepignore

```
tests/fixtures/
**/testdata/
generated/
vendor/
node_modules/
```

### 抑制误报

```python
password = get_from_vault()  # nosemgrep: hardcoded-password
dangerous_but_safe()  # nosemgrep
```

---

# 第二部分：创建自定义规则

## 何时创建自定义规则

- 检测项目特定的漏洞模式
- 强制内部编码标准
- 为自定义框架构建安全检查
- 创建用于控制流分析的污染模式规则

## 方法选择

| 方法 | 何时使用 |
|----------|----------|
| **污染模式** | 数据从不可信源流向危险接收器（注入漏洞） |
| **模式匹配** | 没有控制流要求的句法模式（过时的 API，硬编码值） |

**优先使用污染模式**来检测注入漏洞。仅使用模式匹配无法区分 `eval(user_input)`（易受攻击）和 `eval("safe_literal")`（安全）。

## 快速入门：模式匹配

```yaml
rules:
  - id: hardcoded-password
    languages: [python]
    message: "检测到硬编码密码：$PASSWORD"
    severity: ERROR
    pattern: password = "$PASSWORD"
```

## 快速入门：污染模式

```yaml
rules:
  - id: command-injection
    languages: [python]
    message: 用户输入流向命令执行
    severity: ERROR
    mode: taint
    pattern-sources:
      - pattern: request.args.get(...)
      - pattern: request.form[...]
    pattern-sinks:
      - pattern: os.system(...)
      - pattern: subprocess.call($CMD, shell=True, ...)
    pattern-sanitizers:
      - pattern: shlex.quote(...)
```

## 模式语法快速参考

| 语法 | 描述 | 示例 |
|--------|-------------|---------|
| `...` | 匹配任何内容 | `func(...)` |
| `$VAR` | 捕获 metavariable | `$FUNC($INPUT)` |
| `<... ...>` | 深表达式匹配 | `<... user_input ...>` |

| 操作符 | 描述 |
|----------|-------------|
| `pattern` | 匹配确切模式 |
| `patterns` | 所有必须匹配（AND） |
| `pattern-either` | 任何匹配（OR） |
| `pattern-not` | 排除匹配 |
| `pattern-inside` | 仅在上下文中匹配 |
| `pattern-not-inside` | 仅在上下文外匹配 |
| `metavariable-regex` | 捕获值的正则表达式 |

## 测试规则

**必须先测试。** 创建带注释的测试文件：

```python
# test_rule.py
def test_vulnerable():
    user_input = request.args.get("id")
    # ruleid: my-rule-id
    cursor.execute("SELECT * FROM users WHERE id = " + user_input)

def test_safe():
    user_input = request.args.get("id")
    # ok: my-rule-id
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_input,))
```

运行测试：
```bash
semgrep --test --config rule.yaml test-file
```

## 命令参考

| 任务 | 命令 |
|------|---------|
| 运行测试 | `semgrep --test --config rule.yaml test-file` |
| 验证 YAML | `semgrep --validate --config rule.yaml` |
| 抛出 AST | `semgrep --dump-ast -l <lang> <file>` |
| 调试污染流 | `semgrep --dataflow-traces -f rule.yaml file` |

## 规则创建工作流程

1. **分析问题** - 理解错误模式，确定污染 vs 模式方法
2. **首先创建测试用例** - 在规则之前编写 `ruleid:` 和 `ok:` 注释
3. **分析 AST** - 运行 `semgrep --dump-ast` 以了解代码结构
4. **编写规则** - 从简单开始，迭代
5. **测试直到 100% 通过** - 没有“遗漏的行”或“错误的行”
6. **优化模式** - 只有在测试通过后才能删除冗余项

**输出结构：**
```
<rule-id>/
├── <rule-id>.yaml     # Semgrep 规则
└── <rule-id>.<ext>    # 测试文件
```

## 详细参考

**官方 Semgrep 文档：**
- [规则语法](https://semgrep.dev/docs/writing-rules/rule-syntax) - 完整 YAML 结构，操作符和选项
- [规则架构](https://github.com/semgrep/semgrep-interfaces/blob/main/rule_schema_v1.yaml) - 完整 JSON 架构规范

**本地参考：**
- [工作流程指南](references/workflow.md) - 完整的逐步规则创建过程
- [快速参考](references/quick-reference.md) - 模式操作符和污染组件

## 避免的反模式

**过于宽泛：**
```yaml
# BAD: 匹配任何函数调用
pattern: $FUNC(...)

# GOOD: 特定的危险函数
pattern: eval(...)
```

**缺少安全情况：**
```python
# BAD: 仅测试易受攻击的情况
# ruleid: my-rule
dangerous(user_input)

# GOOD: 包括安全情况
# ruleid: my-rule
dangerous(user_input)

# ok: my-rule
dangerous(sanitize(user_input))
```

## 拒绝的理由

| 简化 | 为什么不正确 |
|----------|----------------|
| "Semgrep 没有发现任何内容，代码是干净的" | Semgrep 是基于模式的；无法跟踪复杂的跨函数数据流 |
| "模式看起来是完整的" | 未测试的规则有隐藏的误报/漏报 |
| "它匹配了易受攻击的情况" | 匹配漏洞只是工作的一半；验证安全情况不会匹配 |
| "污染模式过于复杂" | 对于注入漏洞，污染模式提供更好的精确度 |
| "一个测试用例就足够了" | 包括边缘情况：不同的编码风格，清理输入，安全替代方案 |

---

# CI/CD 集成

## GitHub Actions

```yaml
name: Semgrep

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 1 * *'

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 运行 Semgrep
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            semgrep ci --baseline-commit ${{ github.event.pull_request.base.sha }}
          else
            semgrep ci
          fi
        env:
          SEMGREP_RULES: >-
            p/security-audit
            p/owasp-top-ten
            p/trailofbits
```

---

# 资源

**规则编写：**
- 规则语法：https://semgrep.dev/docs/writing-rules/rule-syntax
- 模式语法：https://semgrep.dev/docs/writing-rules/pattern-syntax
- 规则架构：https://github.com/semgrep/semgrep-interfaces/blob/main/rule_schema_v1.yaml

**通用：**
- 注册中心：https://semgrep.dev/explore
- 玩具场：https://semgrep.dev/playground
- 文档：https://semgrep.dev/docs/
- Trail of Bits 规则：https://github.com/trailofbits/semgrep-rules
