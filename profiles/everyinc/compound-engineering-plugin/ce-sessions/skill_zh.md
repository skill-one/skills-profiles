# /ce-sessions

跨 Claude Code、Codex 和 Cursor 搜索会话历史记录，并综合分析先前会话中完成的工作、尝试过的方法、做出的决定或学到的东西。

## 使用方法

```
/ce-sessions [问题或主题]
/ce-sessions
```

## 预解析上下文

**Git 分支（预解析）：** !`git rev-parse --abbrev-ref HEAD 2>/dev/null || true`

如果上面的行解析为一个普通的分支名（如 `feat/my-branch`），则使用它进行分支过滤，并将其传递给综合子代理。如果它仍然包含反引号命令字符串或为空，则在运行时推导分支。

**仓库根目录（预解析）：** !`git rev-parse --show-toplevel 2>/dev/null || true`

如果上面的行解析为路径，则将其最后一个路径组件作为仓库文件夹名，并使用它进行会话发现。如果它为空或仍然包含反引号命令字符串，则在运行时推导仓库名。

## 注意：2026

当前年份是 2026 年。在解释会话时间戳时使用此年份。

## 安全约束

在编排和综合过程中始终适用这些规则。

- **永远不要将整个会话文件读入上下文。** 会话文件的大小为 1-7MB。始终使用提取脚本先进行过滤，然后对过滤后的输出进行推理。
- **永远不要逐字提取或重现工具调用输入/输出。** 总结尝试过的方法和发生的事情。
- **永远不要包含思考或推理块的内容。** Claude Code 的思考块是内部推理；Codex 的推理块是加密的。两者都不是可操作的。
- **永远不要分析当前会话。** 它的对话历史记录已经可供调用者使用。
- **展示技术内容，而不是个人内容。** 会话包含所有内容——凭证、挫败感、未形成的意见。使用判断力判断哪些内容属于技术摘要，哪些不属于。
- **在访问错误时快速失败。** 如果会话发现因权限问题失败，请立即报告该问题。不要使用不同的工具或方法重试相同的操作——重复重试浪费代币而不会改变结果。

## 执行

如果没有提供问题参数，请询问用户他们想了解的会话历史记录内容。使用平台的阻塞问题工具：Claude Code 中的 `AskUserQuestion`（如果其模式未加载，请首先使用 `ToolSearch` 调用 `select:AskUserQuestion`），Codex 中的 `request_user_input`，Gemini 中的 `ask_user`，Pi 中的 `ask_user`（需要 `pi-ask-user` 扩展）。当 harness 中不存在阻塞工具或调用出错时（例如 Codex 编辑模式）——不是因为需要加载模式——回退到仅使用纯文本提问。永远不要在存在阻塞工具时无声地跳过问题。

### 第 1 步——确定扫描窗口

根据用户的问题推断时间范围。从狭窄的范围开始；只有在狭窄的扫描未找到相关内容时才扩大范围。

| 信号 | 初始扫描窗口 |
|------|--------------|
| "今天"、"今早" | 1 天 |
| "最近"、"过去几天"、"本周" 或无时间信号 | 7 天 |
| "过去几周"、"本月" | 30 天 |
| "过去几个月"、"广泛的功能历史" | 90 天 |

Claude Code 默认保留会话历史记录约 30 天。更宽的窗口在 Claude Code 上可能找不到任何内容，除非用户已延长保留期限。

### 第 2 步——发现会话并提取元数据

运行发现 + 元数据管道（保留空分隔符 xargs 硬化，允许 `extract-metadata.py` 以批处理模式运行）：

```bash
bash scripts/discover-sessions.sh <repo> <days> | tr '\n' '\0' | xargs -0 python3 scripts/extract-metadata.py --cwd-filter <repo>
```

每行输出都是一个描述会话的 JSON 对象（平台、文件、大小、时间戳、会话，以及平台特定字段）。最后一行 `_meta` 包含 `files_processed` 和 `parse_errors`。

如果清单的 `_meta` 行显示 `files_processed: 0`，则返回 "没有相关的先前会话" 并停止。

如果 `parse_errors > 0`，则注意某些会话无法解析，并继续处理返回的内容。

要缩小平台集，请在 `discover-sessions.sh` 调用中添加 `--platform claude`、`--platform codex` 或 `--platform cursor`。默认为全部三个。

### 第 3 步——过滤和排序

按顺序应用这些过滤器以选择值得深入研究的会话：

1. **分支过滤器（仅 Claude Code）。** 保留 `branch == dispatch_branch` 完全匹配的会话，或分支名包含问题主题中的关键词（例如，关于 "auth middleware" 的问题匹配分支 `feat/auth-fix`、`chore/auth-refactor`）。Codex 会话不携带 `gitBranch`——跳过此过滤器。

2. **如果分支过滤器返回零个会话，或者您正在处理 Codex 会话：**
   - 从问题主题中推导出 2-4 个关键词。对于 "最近 auth middleware 中的崩溃，其中 session-validation 拒绝有效令牌"，推导出 `auth,middleware,session,token`（或类似内容）。
   - 重新调用发现管道，在 `extract-metadata.py` 调用中附加 `--keyword K1,K2,...`。脚本返回 `match_count` 非零的会话以及每个关键词的计数。

   - **如果 `files_matched: 0`，返回 "没有相关的先前会话" 并停止。** 不要提取任何内容。

   - 如果 `files_matched > 0`，则将这些会话视为候选会话。按 `match_count` 排序，按每个关键词的计数打破平局。

3. **丢弃扫描窗口之外的会话。** 使用 `last_ts`（如果可用），否则使用 `ts`。丢弃两个时间戳都早于窗口开始时间的会话。

4. **排除当前会话**——它的对话历史记录已经可供调用者使用。

5. **应用深入研究的上限。** 最多从所有平台获取 **5 个会话**。按分支匹配 → `match_count` → 文件大小 > 30KB → 近期性缩小。

6. **只有在过滤后至少剩下一个会话时才继续。** 否则返回 "没有相关的先前会话" 并停止。

**注意：`gitBranch` 仅在第一个用户消息时捕获。** 一个在 `main` 上开始并在会话中途通过 `git checkout` 在功能分支上进行实质性工作的会话记录 `branch: "main"`。分支匹配返回空不是决定性证据——这就是为什么在步骤 2 中需要关键词过滤器回退的原因。

### 第 4 步——设置临时空间

创建每个运行时丢弃的临时目录：

```bash
SCRATCH=$(mktemp -d -t ce-sessions-XXXXXX)
```

捕获绝对路径；将其传递给步骤 5 和步骤 6。操作系统在会话结束时处理清理；在步骤 7 的末尾显式执行 `rm -rf "$SCRATCH"` 无害且使意图明确。

### 第 5 步——按会话提取内容（文件介导）

对于每个选定的会话，运行骨架提取器并使用 `--output`，以便内容直接写入临时文件——提取字节永远不会通过编排工具结果进行往返：

```bash
python3 scripts/extract-skeleton.py --output "$SCRATCH/<session-id>.skeleton.txt" < <session-file>
```

标准输出仅接收一行 JSON 状态（`{"_meta": true, "wrote": "...", "bytes": N, ...}`）。从每行状态中捕获 `bytes` 和 `parse_errors`。

**条件尾提取**——如果骨架在调查中途终止（最后一个可见回合是一个没有结果的工具调用，或者助手正在调试而没有结论），则重新提取并使用 `tail` 形状：

```bash
python3 scripts/extract-skeleton.py --output "$SCRATCH/<session-id>.skeleton.tail.txt" < <session-file>
```

（骨架脚本不接受 `tail:N` 直接限制；如果需要仅尾视图，则在提取后使用 shell 中的 `tail -n 50` 处理临时文件。仅在头输出表明会话在调查中途被截断时使用此方法。）

**条件错误模式**——对于调查可能遇到死路的会话：

```bash
python3 scripts/extract-errors.py --output "$SCRATCH/<session-id>.errors.txt" < <session-file>
```

有选择地使用——只有在理解出了什么问题有价值时才使用。Cursor 代理转录不记录工具结果，因此错误模式对 Cursor 会话不产生任何输出。

### 第 6 步——派发综合子代理

通过平台的子代理原语（Claude Code 中的 `Agent`，Codex 中的 `spawn_agent`，Pi 中的 `subagent` 通过 `pi-subagents` 扩展）派发 `ce-session-historian` 子代理。省略 `mode` 参数，以便应用用户的配置权限设置。在中间层模型上运行（例如，Claude Code 中的 `model: "sonnet"`）——综合器不需要前沿推理。

派发提示是代理的输入合同。传递以下字段：

- `problem_topic` — 一句话命名具体问题。从用户参数中提取，如果缺失，则从无参数提示的答案中提取。
- `scratch_dir` — `$SCRATCH` 的绝对路径。
- `sessions` — 一个对象数组，每个提取的会话一个，每个对象包含：
  - `path` — 骨架文件的绝对路径（以及当提取时 `errors_path` 用于错误文件）
  - `platform` — `claude`、`codex` 或 `cursor`
  - `branch` — 当存在时 git 分支（Claude Code 仅限）
  - `cwd` — 当存在时工作目录（Codex 仅限）
  - `ts` 和 `last_ts` — 会话时间戳
  - `match_count` 和 `keyword_matches` — 当使用关键词过滤时
- `output_schema` — 代理响应应遵循的结构。默认模式：
  ```
  使用以下部分构建你的响应（如有无发现则省略任何部分）：
  - 之前尝试过什么
  - 什么没有成功
  - 关键决定
  - 相关上下文
  ```
  当调用者（例如，`ce-compound`）在技能参数中提供模式时，逐字传递。

示例派发形状：

```
从这些先前会话中综合发现：

问题主题：<一句话主题>

要读取的会话（$SCRATCH 中的路径）：
1. /tmp/ce-sessions-XXXX/abc123.skeleton.txt
   platform=claude branch=feat/auth-fix ts=2026-05-01
2. /tmp/ce-sessions-XXXX/def456.skeleton.txt  errors=/tmp/ce-sessions-XXXX/def456.errors.txt
   platform=codex cwd=/Users/.../my-project ts=2026-05-03
...

输出模式：
- 之前尝试过什么
- 什么没有成功
- 关键决定
- 相关上下文

过滤规则：仅展示与当前特定问题直接相关的发现。
忽略同一会话或分支中的无关工作。
```

代理通过平台的本地文件读取工具读取每个路径，并返回文本发现。批量提取内容仅存在于代理的子代理上下文中——编排器的工作状态保持为文件路径加上小的清单元数据。

### 第 7 步——返回发现

将综合器的输出文本逐字返回给调用者。如果发现或关键词过滤返回零个会话（步骤 2 或步骤 3），则返回字面字符串 `no relevant prior sessions`。

可选地清理临时文件：

```bash
rm -rf "$SCRATCH"
```

操作系统最终会处理清理，无论是否显式清理；显式清理是为了满足期望它的读者。

## 输出

当调用者（通常是键入 `/ce-sessions` 的用户，或通过平台的技能调用原语调用 ce-sessions 的另一个技能）未指定输出格式时，包括一个简短标题，注明搜索了什么：

```
**搜索的会话**：[数量] ([N] Claude Code, [N] Codex, [N] Cursor) | [日期范围]
```

然后是综合器的文本发现。当调用者提供模式时，逐字遵循它并省略默认标题。

## 时间预算

一旦有完整的答案就停止。在几秒钟内自信地返回 "没有相关的先前会话" 是完整的答案；不要扩展搜索以填满时间。步骤 3 中的结构上限（最多深入 5 个会话）和步骤 5 中的条件尾/错误提取构造了运行时限制。

## 错误处理

如果发现管道失败（例如，不可读的主目录、权限失败），将错误展示给调用者。不要用 git log、文件列表或其他来源替代——此技能的合同是会话元数据和综合。

如果提取 `--output` 写入失败（磁盘满、权限），展示清晰的错误，不要在部分路径下派发综合器。

如果 `_meta` 报告 `parse_errors > 0` 从任何脚本，则在派发提示中注意部分提取，并继续；综合器在发现中标记部分。
