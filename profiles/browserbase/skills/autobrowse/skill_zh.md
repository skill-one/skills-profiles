# AutoBrowse — 自我改进的浏览器技能

通过迭代实验来构建可靠的浏览器自动化技能。一个内部代理浏览网站（`evaluate.ts`），而您——外部代理——阅读发生了什么并改进指令（`strategy.md`）。重复直到它能够持续通过。

## 入口点

调用方式灵活——显式标志和自由形式的自然语言都有效：

```
/autobrowse --task google-flights
/autobrowse --task google-flights --iterations 10 --env remote
/autobrowse --task google-flights --browser-trace
/autobrowse --tasks google-flights,amazon-add-to-cart
/autobrowse --all

# 也很好——自由解析：
/autobrowse https://flights.google.com/
/autobrowse book a flight on delta.com
/autobrowse fix the existing google-flights skill
```

`--browser-trace`（默认关闭，仅远程可用）：将每次迭代与兄弟的 `browser-trace` 技能配对——将内部代理包裹在 CDP 捕获中，以获取每页的网络/控制台/页面生命周期证据。隐含 `--env remote`；如果与 `--env local` 结合使用，则会出错。需要兄弟的 `browser-trace` 技能在 `${CLAUDE_SKILL_DIR}/../browser-trace/` 中存在，并且需要 `BROWSERBASE_API_KEY` 环境变量。

当用户而不是 `--task <name>` 拖放 URL 或自由形式指令时：
- 如果 `${WORKSPACE}/tasks/` 中的现有任务明确匹配网站/意图，则使用它。
- 否则，选择一个短的小写破折号命名，从 `${CLAUDE_SKILL_DIR}/references/example-task.md` 创建 `${WORKSPACE}/tasks/<name>/task.md`，根据用户所说的填写 URL/目标，然后继续。用一行告诉用户选择的名字。

---

## 如何运行

### 第 1 步 — 解析参数和定向

检查传递了什么：
- `--task <name>` → 单任务模式
- `--tasks a,b,c` 或 `--all` → 多任务模式（生成子代理）
- `--iterations N` → 多少个评估→改进周期（默认：5）
- `--env local|remote` → 浏览器环境（默认：本地；用于受机器人保护网站的远程）
- `--browser-trace` → 选择浏览器跟踪集成（默认关闭）。隐含 `--env remote`。如果同时传递了 `--env local --browser-trace`，则出错：`browser-trace 需要 Browserbase；放弃 --env local 或放弃 --browser-trace。`

如果用户传递了自由形式文本，则在继续之前将其映射到上述之一。

### 第 2 步 — 设置工作区

所有训练工件（任务定义、策略迭代、跟踪、报告）都存储在当前工作目录中的工作区目录中——不在 `~/.claude/skills/` 内。这使内部代理的文件写入与 Claude 的主目录分开，并避免权限摩擦。

默认工作区：`${CWD}/autobrowse/`

```bash
mkdir -p ./autobrowse/tasks ./autobrowse/traces ./autobrowse/reports
```

如果任务目录（`./autobrowse/tasks/<task>/task.md`）不存在，则搭建它：

```bash
mkdir -p ./autobrowse/tasks/<task>
cp ${CLAUDE_SKILL_DIR}/references/example-task.md ./autobrowse/tasks/<task>/task.md
# 然后编辑 task.md 来描述 URL、输入、步骤和预期的 JSON 输出
```

技能源在 `${CLAUDE_SKILL_DIR}` 保持只读——在训练期间，只有 CWD 中的 `./autobrowse/` 被写入。毕业（最后一步）将单个文件写入 `~/.claude/skills/<task>/SKILL.md`。

列出可用任务：
```bash
ls ./autobrowse/tasks/
```

### 第 3 步 — 多任务：生成并行子代理

如果运行多个任务，请使用 Agent 工具为每个任务同时生成一个子代理。每个子代理都会收到一个自我包含的提示，以运行其任务的完整 AutoBrowse 循环：

> "您正在运行任务 `<name>` 的 AutoBrowse 技能。工作区：`<绝对路径到工作区>`（例如 `/path/to/project/autobrowse`）。运行 `<N>` 次迭代：评估→读取跟踪→改进 strategy.md →重复。使用 `--env <env>`。将 `--workspace <workspace>` 传递给每个 evaluate.mjs 调用。如果父调用使用了 `--browser-trace`，您必须为每个迭代使用 SKILL.md 循环的跟踪路径块（预创建会话、附加 bb-capture、将 `--connect-url` 传递给 evaluate.mjs、停止+二分、释放）——不要回退到默认的单命令路径。请严格按照 AutoBrowse 循环指令操作。
>
> 毕业时，使用正确的 agentskills 前置（名称+描述）将技能安装到 `~/.claude/skills/<task-name>/SKILL.md`。不要只是复制 strategy.md —— 编写一个自我包含的技能。
>
> 在结束时，输出一个结构化摘要，包括：任务名称、最终运行通过/失败、总累积成本、完成的迭代次数、每次迭代的表格（迭代编号、回合数、成本、状态、测试的假设），以及 2-3 个要点关键学习。

并行生成所有子代理，等待所有完成，然后收集它们的摘要并写入会话报告。

**对于单任务**，跳过此步骤，直接运行下面的循环。

---

## 循环（为每个任务运行此操作）

### 迭代开始

检查 `./autobrowse/tasks/<task>/task.md` 是否存在（如果不存在，则从模板搭建——见第 2 步）。`strategy.md` 由 harness 在第一次运行时自动创建为空。

### 要求

- `ANTHROPIC_API_KEY` 必须在环境中（或 CWD 中的 `.env` 文件中——`evaluate.mjs` 自动加载它）。如果缺失，harness 会打印清晰的错误并退出；不要在其他路径中寻找密钥。

### 运行内部代理

**默认路径（没有 `--browser-trace`）**——单个命令，无编排：

```bash
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs --task <task-name> --workspace ./autobrowse
# 或对于受机器人保护的网站：
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs --task <task-name> --workspace ./autobrowse --env remote
```

这会运行浏览器会话并将完整的跟踪写入 `./autobrowse/traces/<task>/latest/`。

**跟踪路径（`--browser-trace`，仅远程）**——外部 harness 预创建一个 Browserbase 会话，将 `bb-capture` 作为被动观察者附加，并将会话的 `connectUrl` 传递给 `evaluate.mjs`，以便每个内部 `browse` 调用都使用 `--cdp $connectUrl --session autobrowse-main`（提供观察者完整网络/控制台事件的规范浏览器跟踪模式）。为每个迭代运行此块，并将 `$N` 设置为 1 索引迭代编号：

```bash
# 预检查——如果 browser-trace 没有与 autobrowse 一起安装，则快速失败。
BT_DIR="${CLAUDE_SKILL_DIR}/../browser-trace"
if [ ! -f "$BT_DIR/scripts/bb-capture.mjs" ]; then
  echo "ERROR: --browser-trace 需要 browser-trace 技能在 $BT_DIR。" >&2
  echo "通过克隆 github.com/browserbase/skills 并将 skills/browser-trace/" >&2
  echo "复制到与 autobrowse 相同的父目录（例如 ~/.claude/skills/browser-trace/）来安装它。" >&2
  exit 1
fi

# a. 会话设置——预创建保持活动的会话并导出其 connectUrl
sid=$(browse cloud sessions create --keep-alive --verified --proxies \
  | node -e "let s='';process.stdin.on('data',c=>s+=c).on('end',()=>process.stdout.write(JSON.parse(s).id))")
connect_url=$(browse cloud sessions get "$sid" \
  | node -e "let s='';process.stdin.on('data',c=>s+=c).on('end',()=>process.stdout.write(JSON.parse(s).connectUrl))")

RUN_ID="run-$(printf '%03d' "$N")"
TRACE_ROOT="./autobrowse/traces/<task-name>/$RUN_ID"
mkdir -p "$TRACE_ROOT"
export O11Y_ROOT="$TRACE_ROOT/.o11y"   # 在 AutoBrowse 运行目录中停放浏览器跟踪输出
export O11Y_RUN_ID="$RUN_ID"           # 告诉 browse CLI 要写入描述符.ndjson 的运行目录

# b. 附加浏览器跟踪——被动观察者；在后台运行
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/bb-capture.mjs "$sid" "$RUN_ID" &
sleep 2

# c. 运行 AutoBROWSE——connectUrl 标志告诉 evaluate.mjs 注入 --cdp/--session
#    到每个内部 browse 调用中。内部代理永远不会看到 --remote。
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs \
  --task <task-name> --workspace ./autobrowse --env remote \
  --connect-url "$connect_url" --run-number "$N"

# d. 停止+二分+统一——顺序很重要；二分需要在会话仍然存在时，并且 unify-trace 将二分输出与 AutoBROWSE 的 trace.json 合并
#    为外部代理读取的每个迭代创建单个时间排序的 NDJSON。
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/stop-capture.mjs "$RUN_ID"
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/bisect-cdp.mjs "$RUN_ID"
node ${CLAUDE_SKILL_DIR}/scripts/unify-trace.mjs \
  --trace-dir "$TRACE_ROOT" \
  --o11y-dir "$O11Y_ROOT/$RUN_ID"

# e. 释放
browse cloud sessions update "$sid" --status REQUEST_RELEASE
```

这将内部代理的跟踪写入 `./autobrowse/traces/<task-name>/latest/`，并将 CDP 二分写入 `./autobrowse/traces/<task-name>/latest/.o11y/<run-id>/`。跟踪的 `browse` CLI 还会向 `.o11y/<run-id>/cdp/descriptors.ndjson` 发射每个命令的丰富节点描述符（每个驱动页面的调用都有一个 JSON 对象：目标标签/ID/角色/可访问名称/属性/xpath/bounding-rect）。描述符文件为下游代码生成提供输入；它**不是**用于假设形成的——读取跟踪时跳过它。

### 读取跟踪

```bash
cat ./autobrowse/traces/<task-name>/latest/summary.md
```

摘要包含持续时间、成本、回合数、决策日志和最终 JSON 输出。

如果代理失败或卡住，请深入查看：
- 阅读 `./autobrowse/traces/<task-name>/latest/trace.json`——搜索失败回合
- 使用 Read 工具读取失败点周围的屏幕截图

**当使用 `--browser-trace` 时——从 `unified-events.jsonl` 开始。** Harness 将代理的回合日志和浏览器的 CDP 水管合并为一个按时间排序的 NDJSON 流在运行根。一个文件，源标记（`source: "agent" | "browser"`），按墙上时间戳交错。从上到下浏览它；失败原因是通常是一两行相邻的行（代理发出命令 X，浏览器以 Y 响应）。

```bash
cat ./autobrowse/traces/<task-name>/latest/unified-events.jsonl
```

结构化文件（`trace.json`，`.o11y/<run-id>/cdp/*`）也是代理可消耗的，作为深入挖掘**当统一流指向您需要更多信息的东西时：

| 需要 | 深入挖掘文件或命令 |
|---|---|
| 每页总计+时间（事件、网络计数、按页面的错误） | `.o11y/<run-id>/cdp/summary.json` |
| 所有失败的网络安全请求集中在一个地方 | `.o11y/<run-id>/cdp/network/failed.jsonl` |
| 完整的控制台异常有效负载（堆栈跟踪等） | `.o11y/<run-id>/cdp/console/exceptions.jsonl` |
| 每页切片（仅页面 N 上的事件） | `.o11y/<run-id>/cdp/pages/<pid>/` |
| 特定回合的完整推理文本/未截断的工具输出 | `trace.json`（按 `turn === N` 过滤） |
| 任意分组查询（例如顶级主机、按页面错误） | `O11Y_ROOT=./autobrowse/traces/<task-name>/latest/.o11y node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/query.mjs <run-id> <cmd>` |

统一流是默认的；仅在您需要分组查询、完整文本有效负载或无法通过流过滤时才深入到结构化文件。

### 形成一个假设

找到问题发生的确切回合。什么单一启发式方法可以防止它？

在 `--browser-trace` 下，假设必须引用来自 `unified-events.jsonl` 的**特定事件**（行号或时间戳）——或者如果您必须深入到某个钻取文件。这使更新基于证据而不是感觉驱动。仅基于代理命令的假设可能说“点击没有工作”；基于统一流，它可以说“在 unified-events.jsonl 的第 47 行：`browse open` 后跟 `/api/checkout` 上的 `Network.responseReceived` 状态 403 —— 切换到 `--verified --proxies`。”

示例：
- “点击下拉菜单后等待 1s——选项在可点击之前会动画显示”
- “直接导航到 `/pay-invoice/`——完全跳过着陆页”
- “使用 `browse fill #field_3 value` 而不是 `browse type`——此字段在获得焦点时会清除”
- “页面在回合 8 显示一个加载器——在快照之前添加 `browse wait timeout 2000`”
- （使用 `--browser-trace`）“在 unified-events.jsonl 的第 47 行，`/api/availability` 上的 3 个连续 `Network.responseReceived` 事件在 `browse open` 后返回 403 —— 该网站正在指纹识别；下一次迭代需要 `--verified --proxies`。”

### 更新 strategy.md

编辑 `./autobrowse/tasks/<task-name>/strategy.md`。保留所有有效内容。修复特定失败。添加一个具体的启发式方法。

好的策略有：
- **快速路径**：直接 URL 或跳过探索的快捷方式
- **逐步工作流**：带有时间注释的精确序列
- **特定网站知识**：选择器 ID、表单字段名称、成功指示器
- **失败恢复**：当 X 出错时要做什么

### 判断结果

阅读新的摘要。它通过了吗？有明显的进展吗？
- **通过或有进展** → 保留，下一次迭代
- **没有进展或倒退** → 将 strategy.md 还原为上一个版本并尝试不同的假设

### 生成可运行的脚本（可选）

一旦任务收敛，您可以通过 `scripts/codegen.mjs` 生成一个确定性可运行的脚本
在一个或多个框架中。这是一个针对每个框架的 LLM 调用的单次射击，通过内容哈希缓存，并可选地验证与新鲜会话和失败时重写。

```bash
node ${CLAUDE_SKILL_DIR}/scripts/codegen.mjs \
  --task <name> \
  --workspace ./autobrowse \
  --frameworks playwright,stagehand \
  --verify
```

每个框架都会在 `tasks/<name>/<framework>/`
下获得自己的子目录，其中包含发出的脚本和自我包含的脚手架（`package.json`，
`tsconfig.json`）。该目录可以独立运行，使用
`cd tasks/<name>/playwright && npm install && npx tsx <name>.ts`——唯一运行时要求是 `BROWSERBASE_API_KEY`（对于 Stagehand 目标还需要 `ANTHROPIC_API_KEY`）。

内置框架：`playwright`，`stagehand`。使用 `--prompt-template <path> --frameworks custom` 添加自定义框架（并提供您自己的运行器或传递 `--no-verify`）。

常见标志：

| 标志 | 目的 |
|---|---|
| `--frameworks a,b,...` | 逗号分隔；默认 `playwright` |
| `--verify` / `--no-verify` | 运行生成的脚本针对新鲜 BB 会话；默认 `--verify` |
| `--max-retries N` | 验证失败重写上限；默认 2 |
| `--cache-only` | 缓存未命中时出错（CI 友好） |
| `--force` | 破坏缓存 |
| `--dry-run` | 估计提示大小+成本；不调用 LLM |
| `--run <id>` | 强制特定 `run-NNN`（默认：最新通过） |

输出是每个框架在 stdout 上的一条 JSON 行。如果任何选定的框架的最终状态是 `passed: false`，则非零退出。

有关规范 `connectOverCDP` 模式的更多信息，请参阅 `references/playwright-cdp-bridge.md`。

### 所有迭代后——如果准备好了就发布

如果任务在最后 3 次迭代中的 2 次或更多次上通过**或者已达到最大迭代限制**，则将其安装为 Claude Code 技能。**不要只是复制 strategy.md**——技能必须是自我包含的，并且对从未见过此代码库的人来说有用。如果达到最大迭代次数而没有干净通过，请记录已知失败点，但仍记录所有学到的内容。

通过写入到 `~/.claude/skills/<task-name>/SKILL.md` 来安装它：

```bash
mkdir -p ~/.claude/skills/<task-name>
```

使用以下结构为 SKILL.md：

```markdown
---
name: <task-name>
description: <用 1-2 句话描述此技能的作用和何时使用它。包括触发关键字。>
---

# <任务标题> — 浏览器技能

## 目的
<用 1-2 句话说明此自动化操作及其存在的原因。>

## 何时使用
<何时应该有人选择此技能。>

## Browse CLI 参考
内部代理使用 `browse` CLI。此任务的关键命令：
- `browse stop` — 杀死现有会话（切换到远程前始终运行）
- `browse open <url> --remote` — 启动一个新的 Browserbase 云会话并导航
- `browse open <url> --local` — 启动干净的本地浏览器并导航
- `browse tab new <url>` — 在新标签页中打开 URL
- `browse wait load` — 等待页面加载完成
- `browse wait timeout <ms>` — 等待固定时间以等待旋转器或动画
- `browse wait selector "<selector>"` — 等待元素变为可见
- `browse get title` — 验证您是否在正确的页面上
- `browse get text body` — 提取所有可见文本（内容提取的首选）
- `browse snapshot` — 获取可访问性树；每个节点都有一个 `[X-Y]` 格式的引用（例如 `[0-5]`，`[2-147]`）
- `browse click [X-Y]` — 通过最新快照中的引用元素进行点击（包括括号）

**SKILL.md 中永远不要使用 `--session <name>` 标志。** 命名会话是一个并行运行的工作绕过——它们会污染技能与基础设施问题。技能必须在隔离状态下工作，使用默认会话。

## 工作流

### 第 1 步 — 启动会话
<按顺序中的精确 browse 命令>

### 第 2 步 — 导航
<精确的 URL 和验证步骤>

### 第 3 步 — 提取
<精确的提取命令>

### 第 4 步 — 输出
<要发出的 JSON，参考下面的模式>

## 特定网站陷阱
<每个从迭代中获得的硬赢得启发式方法的点列表。这是技能的核心价值。>

## 失败恢复
<当导航失败、会话被污染或提取返回垃圾时要做什么>

## 预期输出
```json
<paste the exact expected output schema from task.md>
```
```

写入 SKILL.md 后，确认它已安装：
```bash
ls ~/.claude/skills/<task-name>/SKILL.md
```

技能现在可用作 `/<task-name>` 在 Claude Code 中。

---

## 最终报告（多任务模式）

所有子代理完成后，打印一个 markdown 表格：

| 任务 | 迭代次数 | 最终状态 | 毕业了 | 成本 |
|------|-----------|--------------|-----------|------|
| google-flights | 5 | ✅ 通过 | 是 | $0.42 |
| amazon-add-to-cart | 5 | ❌ 失败 | 否 | $1.20 |

然后写入持久会话报告到 `./autobrowse/reports/`，以便在工作区内部有一个耐久的运行记录：

```bash
mkdir -p ./autobrowse/reports
```

写入文件 `./autobrowse/reports/YYYY-MM-DD-HH-MM-<tasks>.md` 与：

```markdown
# AutoBrowse 会话报告
**日期：** <ISO 日期>
**任务：** <逗号分隔列表>
**环境：** remote|local
**总成本：** $X.XX

## 结果

| 任务 | 迭代次数 | 通过率 | 最终状态 | 毕业了 | 成本 |
|------|-----------|-----------|--------------|-----------|------|
| ... | ... | X/5 | ✅/❌ | 是/否 | $X.XX |

## 每个任务的学习

### <task-name>
- **关键洞察 1：** <代理学到的内容>
- **关键洞察 2：** <另一个启发式方法>
- **修复的失败模式：** <什么在失败以及如何解决的>

## 迭代日志

### <task-name>
| 迭代 | 回合数 | 成本 | 状态 | 测试的假设 |
|------|-------|------|--------|-------------------|
| 1 | 79 | $18.75 | ❌ 失败 | 基线 |
| 2 | 9 | $0.26 | ✅ 通过 | 会话污染修复 |
| ... | ... | ... | ... | ... |
```

---

## 规则

- **仅编辑 `strategy.md`** —— 不要触摸 `task.md`（除非从模板创建）或 `evaluate.mjs`
- **保持在工作区** — 所有训练写入都去 `./autobrowse/`，永远不会去 `~/.claude/skills/autobrowse/`。技能源是只读的。
- **每个迭代一个假设** — 一次测试一个更改
- **建立在对成功的信任上** — 保留有效内容，添加到它
- **信任跟踪** — 内部代理显示了它看到和做的事情
- **毕业到 `~/.claude/skills/`** — 您在那里写入的唯一文件是最终的 `SKILL.md`
- **不要在二分之前释放** — 在 `--browser-trace` 下，每个迭代结束时非议的顺序是：`stop-capture` → `bisect-cdp` → `browse cloud sessions update REQUEST_RELEASE`。二分依赖于跟踪停止时会话仍然存在。
