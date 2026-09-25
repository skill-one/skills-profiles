# 开源代码审查

一项调用 [开源代码审查](https://github.com/alibaba/open-code-review) (`ocr`) 的技能 —— 这是一个读取 Git 差异并生成结构化、按行级评论的开源 AI 代码审查 CLI 工具。

## 工作流程

### 第 1 步：收集业务背景

分析审查目标（提交、分支或变更）以提取简洁的业务背景。通过 `--background` 传递此背景以提升审查质量。

### 第 2 步：运行代码审查

**不要预先检查 `ocr` 是否已安装** —— 跳过 `command -v ocr` 或 `ocr --version` 等探测。假设 CLI 可用，直接运行审查；这能在常用路径上节省一个工具调用。只有在审查因 `command not found` 失败时，才根据故障排除部分进行安装。

使用适当的标志运行 OCR 命令。**当可用时，始终通过 `--background` 传递业务背景**：

```bash
ocr review --audience agent --background "业务背景" [用户参数]
```

**参数处理**：

- **背景上下文**（推荐）：使用 `--background "上下文"` 或 `-b "上下文"` 提供业务背景以提升审查质量
- **默认**（无用户参数）：审查暂存、未暂存和未跟踪的变更（工作区模式）
- **特定提交**：使用 `--commit` 或 `-c` 对单个提交及其父提交进行审查
- **分支比较**：使用 `--from <ref>` 和 `--to <ref>` 审查两个引用之间的差异
- **超时**：每组审查的有效超时 = `--timeout` × 审查轮次。默认 `--timeout 15` 与默认努力程度 `medium`（2 轮）组合给出 30 分钟；`low`/`high` 分别给出 15/45 分钟。
- **并发**：默认并发是 8 个文件工作器；如果遇到速率限制，可通过 `--concurrency <n>` 减少
- **预览模式**：使用 `--preview` 或 `-p` 在不运行 LLM 的情况下预览将要审查的文件
- **输出文件**：使用 `--output <路径>` 将完整结果写入文件而不是标准输出。如果命令因 `unknown flag: --output` 失败，不要继续使用纯标准输出进行审查。询问用户是否要升级 (`npm i -g @alibaba-group/open-code-review@latest`)，并在得到答案前等待。用户确认且升级成功后，重新使用 `--output` 运行。
- **安装**：如果找不到 `ocr` 命令，通过运行 `npm i -g @alibaba-group/open-code-review` 安装它

**常见的调用模式**：

| 用户说 | 要运行的命令 |
|--------|-------------|
| "审查我的变更" / "审查工作副本" | `ocr review --audience agent -b "背景"` |
| "审查这个 PR" / "审查特性分支" | `ocr review --audience agent -b "背景" --from main --to <分支>` |
| "审查提交 abc123" | `ocr review --audience agent -b "背景" --commit abc123` |
| "会审查什么？"（干运行） | `ocr review --preview` |

**输出模式**：

- 始终使用 `--audience agent` 以抑制进度 UI 并仅发出最终摘要
- **防止输出截断**：对于大型审查或受限工具环境，传递 `--output /tmp/ocr_out.txt` 并通过文件读取工具完整检查该文件，而不是将标准输出通过 `tail` 或 `head`，这会丢弃早期的审查评论。

**失败时**：如果 `ocr review` 退出非零（例如 LLM 连接错误），不要盲目重试 —— 查阅下方的故障排除部分以获取匹配的修复方案，然后再重新运行。

### 第 3 步：报告

OCR 输出包括每个评论的结构化 `严重性`（关键 / 高 / 中 / 低）和 `类别`（错误 / 安全 / 性能 / 可维护性 / 测试 / 代码风格 / 文档 / 其他）。按严重性分组呈现结果，丢弃可能是误报或吹毛求疵的 `低` 严重性项。

### 第 4 步：修复

在应用修复之前，检查用户是否请求自动修复：

- 如果用户明确请求 "审查和修复" 或类似操作，则进行自动修复
- 如果用户仅请求 "审查" 而无修复意图，则在应用任何更改前请求权限

在修复问题和建议时：

- 专注于关键、高和中严重性项
- 在安全且定义明确的情况下直接将修复应用于代码
- 对于需要手动干预的复杂修复，明确描述需要执行的操作
- 始终在提交前与用户验证修复

## 输出格式

OCR 输出中的每个评论包含：

- `path`：文件路径
- `content`：审查评论文本
- `start_line` / `end_line`：行范围（两者都为 0 表示定位失败）
- `category`：问题类别（错误、安全、性能、可维护性、测试、代码风格、文档、其他）
- `severity`：问题严重性（关键、高、中、低）
- `suggestion_code`：可选的修复建议
- `existing_code`：可选的原始代码片段
- `thinking`：可选的 LLM 推理过程

使用此模板按严重性分组呈现结果：

```markdown
## 代码审查结果

**审查的文件数**：N
**发现的问题**：X 个关键，Y 个高，Z 个中

### 关键

- **`path/to/file.java:42`** [错误] — 简要描述
  > 建议：如何修复

### 高

- **`path/to/file.java:26`** [错误] — 简要描述
  > 建议：如何修复

### 中

- **`path/to/file.ts:88`** [性能] — 简要描述
  > 建议：如何修复（如果适用）
```

在过滤后如果没有关键、高或中严重性问题剩余，则声明："审查完成 —— 在 N 个文件中未发现关键、高或中严重性问题。"

**处理定位错误的评论**：

当 `start_line` 和 `end_line` 都为 `0` 时，评论在文件中定位失败。在这种情况下：

1. 读取评论内容以理解问题
2. 检查评论中提到的目标文件
3. 根据评论的上下文确定相关代码部分
4. 将修复或建议应用于正确位置

## 自定义审查规则

如果用户需要项目特定规则，OCR 按此优先级顺序解析它们：

1. `--rule <路径>` 标志（最高）
2. `<repo>/.opencodereview/rule.json`
3. `~/.opencodereview/rule.json`
4. 内建系统默认值（最低）

默认情况下，第一个匹配的用户规则将替换内建系统规则。在规则条目上设置 `merge_system_rule: true` 时，匹配的系统规则和用户规则都应包含。

规则文件格式：

```json
{
  "rules": [
    {
      "path": "**/*.java",
      "rule": "所有新方法必须验证必需参数是否为 null",
      "merge_system_rule": true
    },
    {
      "path": "**/*mapper*.xml",
      "rule": "检查 SQL 注入风险和缺失的关闭标签"
    }
  ]
}
```

在审查前预览应用于文件的规则：

```bash
ocr rules check src/main/java/com/example/Foo.java
```

## 高级审查选项

除了上述常见标志外，`ocr review` 提供了几组控制选项。运行 `ocr review --help` 获取完整列表。

**范围**

- `--exclude '<模式>'` — gitignore 风格的逗号分隔模式（例如 `--exclude '**/generated/*,**/testdata/*'`），与 `rule.json` 排除合并。
- `--background-file <路径>` — 从 Markdown 文件读取审查背景。优先级高于 `--background`。

**输出**

- `--format text|json|sarif` — `text`（默认）供人类阅读；`json` 供机器读取的发现；`sarif` 供 GitHub 代码扫描等代码扫描集成使用。

**模型**

- `--provider <名称>` / `--model <名称>` — 仅为此运行覆盖配置的提供者/模型（例如，使用不同模型重新检查差异；用户命名模型，`ocr llm providers` 列出内建模型）。

**预算**

- `--max-tokens <n>` — 每组提示天花板；默认为配置值或模板默认值（`200000`）。
- `--max-tokens-budget <n>` — 运行总输入 + 输出令牌上限。在每次 LLM 轮次前检查：已超出预算的组将获得最后一轮提交发现，不再分发其他组，部分结果仍会发布，跳过的文件会报告为 `failed(budget)`。
- `--no-filter` — 保留所有审查评论并跳过 LLM 后过滤调用。

## 注意事项

- **必须先配置 LLM** — 如果没有可用的 LLM，`ocr review` 会大声失败。如果发生这种情况，请参阅下方的故障排除部分。
- **工作目录很重要** — `ocr review` 在当前目录的 Git 仓库上操作。使用 `--repo /path/to/repo` 从其他位置运行。
- **未跟踪文件在工作区模式下审查** — 运行 `ocr review` 包括暂存、未暂存和未跟踪的变更。如果需要更窄的范围，请选择性地暂存。
- **大型差异可能超出令牌限制** — `MAX_TOKENS` 设置提示预算（审查模板中的 `200000`；`ocr scan` 使用 `58888`）；对话上下文被压缩以保持在提示预算内。模型输出由 `MAX_COMPLETION_TOKENS`（`16384`）单独限制。如果文件差异本身超过 ~80% 的 `MAX_TOKENS`，则在调用 LLM 前会跳过该文件。
- **计划阶段在两个阈值之一触发** — 当组中最大的变更文件达到 `PLAN_MODE_LINE_THRESHOLD`（默认 `50`）**或**其包含 2+ 个变更行总和达到 `PLAN_MODE_GROUP_LINE_THRESHOLD`（默认 `100`）时，该组会在主审查前运行额外的风险分析阶段。这会增加延迟，但能提升质量。
- **不要传递 `--audience human`** — 它会流式传输进度 UI，污染输出。始终使用 `--audience agent`。
- **评论语言遵循配置** — `language` 配置控制审查评论语言，默认为 `English`，并接受任何语言名称（例如 `English` 或 `中文`）。
- **避免输出截断** — 大型审查运行会产生大量输出。永远不要将命令输出通过 `tail` 或 `head`，因为它会丢弃早期部分的审查评论。使用 `--output <路径>` 并完整读取；在旧 CLI 上，请遵循上述 **输出文件** 指导。
- **恢复中断的审查** — 失败或中断的范围/提交审查可以使用 `ocr review --resume <id>` 继续进行，使用相同的 `--from`/`--to` 或 `--commit` 目标（ID 在失败时打印为 `retry with: --resume <id>`，或使用 `ocr session list` 找到它）。工作区恢复不受支持。

## 验证

审查完成后，通过检查以下内容来验证成功：

1. 命令以代码 0 退出
2. 生成了评论（或出现 "未生成评论" 消息）
3. 显示在 stderr 中的警告（如果有）

如果发生错误，请检查 stderr 警告以获取有关哪些文件失败及其原因的详细信息。

## 故障排除

**`ocr: command not found`**

安装 CLI：

```bash
npm install -g @alibaba-group/open-code-review
```

**`unknown flag: --output`**

CLI 旧于 v1.10.0。不要继续使用纯标准输出进行审查。询问用户是否要升级 (`npm i -g @alibaba-group/open-code-review@latest`)，并在得到答案前等待。用户确认且升级成功后，重新使用 `--output` 运行。

**`ocr review` 因 LLM 连接错误失败**

提示用户配置 LLM 提供者。

交互式设置（推荐）：

```bash
ocr config provider
```

手动设置（替代方案）：

```bash
ocr config set llm.url https://api.anthropic.com/v1/messages
ocr config set llm.auth_token <api-key>
ocr config set llm.model claude-opus-4-6
ocr config set llm.use_anthropic true
```

使用 `ocr llm test` 验证连接性。停止并询问用户提供凭证 —— 永远不要编造或硬编码 API 密钥。

## 参考

- 完整文档：https://github.com/alibaba/open-code-review
- NPM 包：https://www.npmjs.com/package/@alibaba-group/open-code-review
- 问题追踪器：https://github.com/alibaba/open-code-review/issues
