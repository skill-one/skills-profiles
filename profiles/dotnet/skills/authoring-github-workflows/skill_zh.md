# 安全编写 GitHub Actions 工作流

GitHub Actions 工作流文件是 YAML 格式，但**有效的 YAML 并不等于有效的工 作流**。工作流可能通过 `yaml.safe_load`（或随意审查）的解析，却在加载时被 GitHub Actions 拒绝 — 产生模糊的错误信息 *"这次运行很可能因为工作流文件问题而失败"*，并且**没有任何作业被启动**。这项技能将教你 YAML 与 Actions 之间的陷阱（上述 `#` 作为注释的陷阱尤其突出），如何正确引用表达式标量，以及如何在合并前使用 `actionlint` 进行验证。

> **范围：语法与语义**。这项技能关注的是工作流 YAML 的 *语法和结构* 正确性 — 引用、解析和 `actionlint` 级别的有效性，这些决定了 GitHub Actions 是否会加载并运行文件。它**不是**关于工作流应该做什么或智能式工作流应该如何行为。对于 *语义和功能* 指导（设计工作流逻辑、智能式工作流模式、gh-aw 编写），请使用 [`.github/agents/agentic-workflows.agent.md`](../../../.github/agents/agentic-workflows.agent.md)。这两者是互补的：使用代理来确保行为正确，使用这项技能来确保 YAML 正确。

## 何时使用

- 编辑、添加或审查 `.github/workflows/` 下任何文件。
- 编写 `run-name`、`name`、`if`、`env`、`with` 或 `run` 值，其中嵌入 `${{ }}` 表达式。
- 工作流运行失败，错误信息为 *"这次运行很可能因为工作流文件问题而失败"*，并且**没有作业运行**。
- 在 `main` 分支上，工作流编辑合并后，评估/CI 突然对所有运行都失效，即使更改看起来很正常。
- 判断 YAML 标量是否需要引用。

## 何时不用

- 编写非 Actions YAML（应用配置、Kubernetes、Compose、Azure Pipelines、GitLab CI）。
- 在已经有效的 `run:` 块内纯 shell/脚本逻辑（这是一个脚本任务，而不是工作流语法任务）。

## 最大的陷阱：未引用的表达式中的 `#` 变成 YAML 注释

在 YAML 中，空格后跟 `#` 开始一个**注释**。在未引用（普通）标量中，从空格-`#` 到行尾的所有内容都会被静默丢弃：

```yaml
# BAD — run-name 在 " #" 处被静默截断
run-name: ${{ inputs.pr_number != '' && format('Evaluate PR #{0} @ {1}', inputs.pr_number, inputs.head_sha) || '' }}
```

YAML 将其解析为 `run-name: ${{ inputs.pr_number != '' && format('Evaluate PR` — 一个**未结束的 `${{` 表达式**。`yaml.safe_load` 成功（它只看到一个带尾随注释的截断字符串），因此这个错误通过了简单的验证，但 GitHub Actions 拒绝了格式错误的表达式，拒绝启动任何运行。

```yaml
# GOOD — 用双引号将整个值括起来，以便 `#` 保持在标量内
run-name: "${{ inputs.pr_number != '' && format('Evaluate PR #{0} @ {1}', inputs.pr_number, inputs.head_sha) || '' }}"
```

内部表达式已经使用了单引号，因此对标量使用双引号是安全的。这正是导致 `dotnet/skills` 在 `main` 上评估失败的错误（通过引用修复）。

## 其他强制在普通标量中引用的字符

| 字符 / 模式 | 为什么会出错 | 修复方法 |
|-------------|--------------|----------|
| 空格后跟 `#`（空格-哈希） | 开始 YAML 注释；截断值 | 引用整个值 |
| 开头的 `*`、`&`、`!`、`?`、`\|`、`>`、`@`、`` ` `` | YAML 锚点/别名/标签/块标量 | 引用值 |
| 开头的 `{` 或 `[` | 解析为流映射/序列（裸的 `${{ }}` 以 `$` 开头是安全的，但 `{{` 在开头字符后是危险的） | 引用值 |
| 值内的 `:` 后跟空格（冒号-空格） | 解析为嵌套映射键 | 引用值 |
| 重要的开头/结尾空格 | 普通标量会移除它们 | 引用值 |
| 值是 `true`/`false`/`yes`/`no`/`on`/`off`/数字但必须保持字符串 | YAML 类型转换 | 引用值 |

**经验法则**：如果 `name`、`run-name`、`if`、`env` 或 `with` 值包含 `${{ }}` 表达式，并且包含任何字面 `#`、`:` 或开头特殊字符，**用双引号将整个标量括起来**。

## 工作流步骤

### 第 1 步：识别已更改/编写的工 作流文件

```bash
git diff --name-only origin/main... -- .github/workflows/
```

对于每个文件，扫描包含 `${{` 以及 `#`、冒号-空格或开头特殊字符的每一行。

### 第 2 步：引用有风险的表达式标量

当值嵌入表达式并包含 `#` 或其他特殊字符时（见上表），用双引号将完整值括起来。当内部表达式使用单引号时优先使用双引号，反之亦然。**不要**转义 `${{` 括号 — 引用标量就足够了。

### 第 3 步：使用 actionlint 进行权威验证

`actionlint` 理解 GitHub Actions 模式和表达式语法，因此它能捕获普通 YAML 语法检查器遗漏的这类错误。下载一个固定版本的 release 并运行它：

```bash
ACTIONLINT_VERSION=1.7.7
ACTIONLINT_SHA256=023070a287cd8cccd71515fedc843f1985bf96c436b7effaecce67290e7e0757
curl -fsSLo actionlint.tar.gz \
  "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz"
# 在提取/执行之前，使用固定校验和验证下载：
echo "${ACTIONLINT_SHA256}  actionlint.tar.gz" | sha256sum -c -
tar -xzf actionlint.tar.gz actionlint
# 关注工作流/表达式正确性；忽略 shell/py 风格噪音：
./actionlint -shellcheck= -pyflakes= -color .github/workflows/*.yml
```

在 Windows PowerShell 中，使用 `actionlint_<ver>_windows_amd64.zip` 资产和 `Expand-Archive`。

截断表达式错误会表现为：

```
got unexpected EOF while lexing end of string literal, expecting ''' [expression]
```

干净的退出代码 `0` 表示工作流在结构上有效。

### 第 4 步：确认仅 YAML 检查是不够的

**不要**依赖 `yaml.safe_load`、`yamllint` 或 "它能解析" 作为证据。它们接受截断注释的形式。只有 `actionlint`（或推送到 GitHub Actions 观察其解析）才能验证 Actions 层。

### 第 5 步：保持 CI 红绿灯

此仓库会自动运行 `actionlint`（见 `.github/workflows/actionlint.yml`）在触及 `.github/workflows/` 的任何 PR 上。确保你的更改通过该检查后再请求审查。如果你添加了新工作流，门禁会自动覆盖它。

## 验证

- [ ] 每个 `${{ }}` 值包含 `#`、冒号-空格或开头特殊字符，都被双引号括起来。
- [ ] `actionlint -shellcheck= -pyflakes= .github/workflows/*.yml` 退出 `0`。
- [ ] 没有工作流运行报告 *"这次运行很可能因为工作流文件问题而失败"*。
- [ ] PR 上的 `actionlint` CI 检查是绿色的。

## 常见陷阱

| 陷阱 | 解决方法 |
|------|----------|
| 未引用的 `run-name`/`name` 中表达式内包含 `#` | 用双引号将整个值括起来 |
| 依赖 `yaml.safe_load`/`yamllint`/代码审查来捕获它 | 运行 `actionlint`；YAML 仅检查接受截断形式 |
| 用转义 `${{` 括号来 "修复" 它 | 不要 — 引用标量而不是转义；转义会破坏表达式 |
| 用单引号包围包含单引号的值 | 对外标量使用双引号 |
| 启用 shellcheck 的 `actionlint` 并被现有 shell 风格警告淹没 | 用 `-shellcheck= -pyflakes=` 运行以专注于工作流/表达式错误 |
| 假设 YAML 语法检查绿色意味着工作流会运行 | 推送并确认作业实际启动，或依赖 `actionlint` 门禁 |

## 参考文献

- [actionlint](https://github.com/rhysd/actionlint) — GitHub Actions 工作流的静态检查器。
- [GitHub Actions: 工作流语法](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [YAML 1.2 规范 — 注释](https://yaml.org/spec/1.2.2/#66-comments)
- 仓库技能编写指南：[`.agents/skills/create-skill/SKILL.md`](../create-skill/SKILL.md)
