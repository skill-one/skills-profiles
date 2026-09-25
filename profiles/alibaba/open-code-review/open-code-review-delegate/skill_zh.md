# 开放式代码评审 — 委托模式

一种用于执行 AI 代码评审的技能，其中 OCR 提供确定性工程（文件过滤、规则解析），而主机代理则使用其自身的智能和工具执行实际评审。

## 工作流程

### 第 1 步：预览 — 确定评审内容

```bash
ocr delegate preview --format json [--from <ref> --to <ref>] [--commit <hash>] [--exclude <patterns>]
```

此命令输出：
- **mode**（工作区 / 范围 / 提交）
- **from / to / commit / merge_base** — 构建 git 命令的引用元数据
- **可评审文件列表** — 路径、状态、插入/删除
- **排除文件** — 排除原因

**常见调用方式：**

| 场景 | 命令 |
|------|------|
| 工作区变更 | `ocr delegate preview` |
| 分支比较 | `ocr delegate preview --from main --to feature` |
| 单个提交 | `ocr delegate preview -c abc123` |

### 第 2 步：获取文件的规则

```bash
ocr delegate rule --format json <path1> <path2> ...
```

传递第 1 步中的可评审文件路径。输出按规则内容分组 — 共享相同规则的文件会出现在同一组下，避免重复。

### 第 3 步：获取差异

根据第 1 步中的模式/引用信息直接使用 git：

**范围模式**（预览输出中提供的 merge_base）：
```bash
git diff <merge_base>..<to> -- <path>
```

**提交模式**：
```bash
git show <commit> -- <path>
```

**工作区模式**：
```bash
# 已跟踪文件
git diff HEAD -- <path>
# 新的未跟踪文件 — 直接读取（整个文件是新代码）
cat <path>
```

### 第 4 步：逐个文件评审

创建一个包含每个 `reviewable_files` 条目的清单。对于每个可评审文件：

使用 `(path, status)` 作为清单标识。工作区模式下，当先有已提交删除后有未跟踪重建时，可能会报告相同的路径两次。

1. 获取其差异（第 3 步）
2. 咨询其规则组（来自第 2 步）以获取评审清单
3. 进行彻底评审，根据需要使用适当的上下文工具
4. 标记文件为 `reviewed`，或为 `skipped` 并给出具体原因

对于大变更，按共享规则和差异大小分批评审。找到第一个高严重性问题时不要停止。

### 第 5 步：格式化输出

每条评论必须遵循以下结构：

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| path | string | 是 | 相对文件路径 |
| content | string | 是 | 描述问题的评审评论 |
| start_line | integer | 否 | 新文件中的起始行 |
| end_line | integer | 否 | 新文件中的结束行 |
| category | enum | 否 | bug, security, performance, maintainability, test, style, documentation, other |
| severity | enum | 否 | critical, high, medium, low |

### 第 6 步：分类和报告

报告前，验证所有预览的文件都已处理。在摘要中包含 `total_files`、`reviewed_files`、`skipped_files` 和 `coverage_rate`。跳过的文件必须包含其原因。

按严重性分组发现：

- **Critical/High**：错误、安全问题、数据丢失风险 — 必须报告
- **Medium**：性能问题、错误处理缺失、可维护性问题 — 带上下文报告
- **Low**：风格小问题、轻微建议 — 仅在明确有价值时报告

静默丢弃可能的误报。

### 第 7 步：修复（可选）

如果用户请求“评审和修复”：
- 直接应用高/Critical 修复
- 描述需要手动干预的 Medium 修复
- 跳过低优先级项，除非非常简单

## 子命令参考

| 命令 | 目的 |
|------|------|
| `ocr delegate preview` | 哪些文件要评审 + 模式/引用元数据 |
| `ocr delegate rule <path...>` | 按内容分组的评审规则 |

## 共享标志

| 标志 | 描述 |
|------|------|
| `--from <ref>` | 范围模式中的源引用 |
| `--to <ref>` | 范围模式中的目标引用 |
| `-c, --commit <hash>` | 单个提交模式 |
| `--repo <path>` | 仓库根目录（默认：当前工作目录） |
| `--rule <path>` | 自定义 rule.json 路径 |
| `--exclude <patterns>` | 用逗号分隔的排除模式 |
| `-b, --background <text>` | 业务上下文 |
| `-B, --background-file <path>` | 来自 Markdown 文件的业务上下文（优先级高于 `-b`） |
| `-f, --format <text\|json>` | 输出格式；使用 `json` 以便代理集成 |

## 注意事项

- **OCR 端无需 LLM** — 委托模式从不调用 LLM。所有智能都来自主机代理。
- **规则分组** — 共享相同规则的文件在输出中分组在一起。每次调用可以传递任意数量的路径；对于大变更，按批次获取规则以边评审边获取。
- **工作目录重要** — `ocr delegate` 在当前目录的 Git 仓库上操作。使用 `--repo /path` 覆盖。
- **工作区模式中的未跟踪文件** — `preview` 包含未跟踪文件。对于这些文件，直接读取文件而不是使用 `git diff`。
- **背景上下文** — 当你有需求上下文时，向 `preview` 传递 `--background`；它会在评审期间作为参考出现在输出中。
- **覆盖率强制要求** — 每个 `reviewable_files` 条目必须以评审或明确跳过结束；不要静默忽略文件。

### 恢复过大的背景上下文

`--background-file` 有两个独立的限制。原始文件不能超过
1 MiB，清理后的内容不能超过 8000 个字符。任一条件都会中止命令。当命令报告任一限制：

1. 不要静默截断源文件。
2. 总结原始材料，同时保留其需求、约束、验收标准和其他评审关键细节。
3. 通过将摘要作为单个 shell 安全的参数传递来重试受影响的命令（例如，使用主机 shell 生成的引号/转义参数，或将其写入新的大小受限文件并传递该文件）。不要将不受信任的摘要文本直接放在双引号 shell 模板中；`$()`、反引号、引号和变量引用仍然可以求值。省略原始 `--background-file`，以免 CLI 重新加载同一过大的文件并再次失败。
4. 如果无法生成忠实摘要，则完全忽略 OCR 背景并直接在评审期间读取原始材料。

### 解决 CLI 版本兼容性问题

`--format` 标志在 `ocr` v1.9.0 及更高版本中可用。技能和安装的 CLI 可以独立更新。如果请求的 `preview` 或 `rule` 命令使用 `--format json` 失败，并具体报错 `unknown flag: --format`，则不使用该标志重新运行，并使用文本输出完成委托运行。保留该输出的显式模式、引用、文件和规则信息；不要将文本输出解析为 JSON 或编造缺失的 schema 字段。对于任何其他错误，不要省略该标志重试；报告它并停止受影响的流程。

主机代理技能可能会消耗等效的文本输出以完成其评审清单。需要 `schema_version` 或其他 JSON 字段的程序化集成必须使用支持 JSON 的 CLI：通过 `ocr --version` 验证并在必要时升级：

```bash
npm install -g @alibaba-group/open-code-review
```
