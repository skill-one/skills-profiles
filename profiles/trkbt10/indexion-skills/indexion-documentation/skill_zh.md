# indexion 文档 — 文档分析

评估文档状态并检测漂移。这项技能涵盖了文档生命周期中的**评估方面**：存在什么、缺失什么、过时什么。构建 README 请参考 `indexion-readme`。

## "需要哪些文档？"

```bash
# 快速覆盖率概览 — 公共 API 有多少被文档化？
indexion plan documentation --style=coverage .
```

报告：
- 总体覆盖率百分比（已文档化 / 总公共项）
- 按包分解，包含 README 存在情况
- 函数与类型覆盖率对比

输出示例：
```
总体覆盖率：81% (2285/2806)
函数：89%，类型：75%
```

获取包含优先级操作项的详细计划：

```bash
# 带优先级和包清单的完整计划
indexion plan documentation .

# 作为 GitHub 问题进行跟踪
indexion plan documentation --format=github-issue .

# JSON 格式用于脚本
indexion plan documentation --format=json .
```

获取未文档化项的快速按文件列表：

```bash
# 哪些 pub 声明缺少文档注释？
indexion grep --undocumented src/
```

**检测原理：** 使用 KGF 分词器查找可见性关键字（`pub`、`public`、`export`）与声明关键字（`fn`、`struct`、`enum`、`type`、`trait`）配对。将 `///` 文档注释与声明关联。语言无关——适用于任何 KGF 支持的语言。

**注意事项：** `///|` 仅标记注释即使没有描述性文本也计为“已文档化”。检查输出中的 `doc_preview` 以评估质量，而不仅仅是覆盖率。

## "我的文档是否更新了？"

检测实现代码与文档之间的漂移。

```bash
# Markdown 格式的完整对齐报告
indexion plan reconcile --format=md .
```

这会对比代码符号与文档，并报告：
- **词汇漂移**：源代码术语缺失在相邻文档中
- **过时文档**：代码在文档最后更新后已更改
- **缺失文档**：无文档覆盖的代码模块

**阅读报告：**

词汇漂移表显示代码词汇与文档之间的距离（0-100%）。90%+ 距离意味着 README 与当前代码基本无关。检查差距术语列以获取具体缺失的词汇。

**范围检查：**

```bash
# 仅检查包级文档
indexion plan reconcile --scope=package-docs .

# 仅检查树级文档
indexion plan reconcile --scope=tree-docs .

# 检查特定文档
indexion plan reconcile --doc='docs/**/*.md'
indexion plan reconcile --doc-spec=markdown .
```

**时间戳策略：**

```bash
# 使用 git 提交时间戳（更适用于协作项目）
indexion plan reconcile --git .

# 仅使用文件 mtime（更快，无 git 依赖）
indexion plan reconcile --mtime-only .
```

**缓存与漂移：**

`plan reconcile` 在 `.indexion/cache/reconcile/` 维护缓存。在模式更改或 indexion 升级后，缓存可能变得过时并导致反序列化错误。清除它：

```bash
rm -rf .indexion/cache/reconcile
```

## "显示依赖结构"

生成依赖图以理解模块关系。

```bash
# Mermaid 图（默认 — 可嵌入 GitHub README）
indexion doc graph src/config/

# 其他格式
indexion doc graph --format=dot src/     # Graphviz DOT
indexion doc graph --format=d2 src/      # D2
indexion doc graph --format=text src/    # ASCII 文本
indexion doc graph --format=json src/    # 机器可读

# 自定义标题和输出文件
indexion doc graph --title="KGF 依赖" --output=deps.mmd src/kgf/
```

## 分析工作流

```bash
# 1. 当前状态是什么？
indexion plan documentation --style=coverage .

# 2. 哪些具体项缺少文档？
indexion grep --undocumented src/

# 3. 代码是否与现有文档漂移？
indexion plan reconcile --format=md .

# 4. 依赖结构是什么样子？
indexion doc graph --output=deps.mmd src/

# 5. 修复标记的文档，重新验证
indexion plan reconcile --format=md .
```

## 常见陷阱

**"plan reconcile 显示到处都是 90%+ 漂移"**
- 自动生成的骨架 README（仅 API 列表）漂移率高，因为它们缺乏实际实现的词汇。用代码实际功能的描述丰富它们，而不仅仅是导出内容。

**"plan documentation 说 100% 覆盖率但文档是错的"**
- 覆盖率衡量文档注释的存在，而非准确性。`///|` 标记计为已文档化。使用 `plan reconcile` 检查内容准确性。

**"plan reconcile 启动时崩溃"**
- 模式更改后的缓存反序列化错误。清除它：
  `rm -rf .indexion/cache/reconcile`

**"plan reconcile 检测到我已经修复的漂移"**
- `--git` 标志使用提交时间戳。如果你修复了文档但尚未提交，基于 mtime 的检测（`--mtime-only`）会看到修复，但基于 git 的检测不会。

**Reconcile 仅检查实现到文档的方向。** 它检测代码术语缺失在文档中，但**不**检测文档引用不存在的 CLI 选项。对于该方向，手动比较每个 README 与 `indexion <command> --help`。
