---
name: autobrowse
description: 通过自动研究循环实现自我提升的浏览器自动化。迭代运行浏览任务，读取追踪记录，并改进导航技能（strategy.md），直到可靠地通过测试。支持在多个任务中并行运行，使用子代理。当你想要为特定网站任务构建或改进浏览器自动化技能时使用。
---

# AutoBrowse — 自我改进的浏览器技能

通过迭代实验来构建可靠的浏览器自动化技能。一个内部代理浏览网站（`evaluate.ts`），而您——外部代理——读取发生了什么并改进指令（`strategy.md`）。重复进行，直到它能够持续通过。

## 入口点

调用方式灵活——显式标志和自由形式的自然语言都有效：

```
/autobrowse --task google-flights
/autobrowse --task google-flights --iterations 10 --env remote
/autobrowse --task google-flights --browser-trace
/autobrowse --tasks google-flights,amazon-add-to-cart
/autobrowse --all

# 也可以自由解析：
/autobrowse https://flights.google.com/
/autobrowse book a flight on delta.com
/autobrowse fix the existing google-flights skill
```

`--browser-trace`（默认关闭，仅远程环境）：将每次迭代与兄弟`browser-trace`技能配对——将内部代理包裹在 CDP 捕获中，以获取每页网络/控制台/页面生命周期证据。隐含`--env remote`；如果与`--env local`结合使用，则会报错。需要兄弟`browser-trace`技能存在于`${CLAUDE_SKILL_DIR}/../browser-trace/`中，并且需要`BROWSERBASE_API_KEY`环境变量。

当用户不是使用`--task <name>`而是放下一个 URL 或自由形式的指令时：
- 如果`${WORKSPACE}/tasks/`中的现有任务明确匹配网站/意图，则使用它。
- 否则，选择一个短的小写中划线命名，从`${CLAUDE_SKILL_DIR}/references/example-task.md`创建`${WORKSPACE}/tasks/<name>/task.md`，根据用户所说的内容填写 URL/目标，然后继续。用一行告诉用户选择的名字。

---

## 如何运行

### 第一步 — 解析参数和定向

检查传递了什么：
- `--task <name>` → 单任务模式
- `--tasks a,b,c` 或 `--all` → 多任务模式（生成子代理）
- `--iterations N` → 多少个评估→改进周期（默认：5）
- `--env local|remote` → 浏览器环境（默认：本地；用于受机器人保护的网站使用远程）
- `--browser-trace` → 选择浏览器跟踪集成（默认关闭）。隐含`--env remote`。如果同时传递了`--env local --browser-trace`，则报错：`browser-trace 需要 Browserbase；放弃 --env local 或放弃 --browser-trace。`

如果用户传递了自由形式的文本，则在继续之前将其映射到上述之一。

### 第二步 — 设置工作区

所有训练工件（任务定义、策略迭代、跟踪、报告）都位于当前工作目录中的工作区目录中——不在`~/.claude/skills/`内。这使内部代理的文件写入不会进入 Claude 的主目录，并避免权限摩擦。

默认工作区：`${CWD}/autobrowse/`

```bash
mkdir -p ./autobrowse/tasks ./autobrowse/traces ./autobrowse/reports
```

如果任务目录（`./autobrowse/tasks/<task>/task.md`）还不存在，则使用模板进行脚手架：

```bash
mkdir -p ./autobrowse/tasks/<task>
cp ${CLAUDE_SKILL_DIR}/references/example-task.md ./autobrowse/tasks/<task>/task.md
# 然后编辑 task.md 来描述 URL、输入、步骤和预期的 JSON 输出
```

技能源位于`${CLAUDE_SKILL_DIR}`，保持只读——在训练期间，只有 CWD 中的`./autobrowse/`会被写入。毕业（最后一步）会将一个文件写入`~/.claude/skills/<task>/SKILL.md`。

列出可用任务：
```bash
ls ./autobrowse/tasks/
```

### 第三步 — 多任务：并行生成子代理

如果运行多个任务，请使用 Agent 工具为每个任务同时生成一个子代理。每个子代理都会收到一个自包含的提示，用于运行其任务的完整 AutoBrowse 循环：

> "您正在运行任务 `<name>` 的 AutoBrowse 技能。工作区：`<绝对路径到工作区>`（例如 `/path/to/project/autobrowse`）。运行 `<N>` 次迭代：评估→读取跟踪→改进 strategy.md →重复。使用 `--env <env>`。向每个 evaluate.mjs 调用传递 `--workspace <workspace>`。如果父调用使用了 `--browser-trace`，您必须为每个迭代使用 SKILL.md 循环的跟踪路径块（预创建会话、附加 bb-capture、将 `--connect-url` 传递给 evaluate.mjs、停止+二分、释放）——不要回退到默认的单命令路径。请严格按照 AutoBrowse 循环指令进行操作。
>
> 毕业时，使用正确的 agentskills 前置（名称+描述）将技能安装到 `~/.claude/skills/<task-name>/SKILL.md`。不要只是复制 strategy.md —— 编写一个自包含的技能。
>
> 结束时，输出一个结构化摘要，包括任务名称、最终运行通过/失败、总累积成本、完成的迭代次数、每次迭代的表格（迭代编号、回合数、成本、状态、测试的假设），以及 2-3 个要点关键学习内容。"

并行生成所有子代理，等待所有完成，然后收集它们的摘要并编写会话报告。

**对于单个任务**，跳过此步骤并直接运行下面的循环。

---

## 循环（为每个任务运行此操作）

### 迭代开始

检查`./autobrowse/tasks/<task>/task.md`是否存在（如果不存在，则从模板中脚手架它——见步骤 2）。`strategy.md`由 harness 在第一次运行时自动创建为空。

### 要求

- `ANTHROPIC_API_KEY` 必须在环境中（或 CWD 中的 `.env` 文件中——`evaluate.mjs`自动加载它）。如果缺失，harness 会打印清晰的错误并退出；不要在其他路径中寻找密钥。

### 运行内部代理

**默认路径（没有 `--browser-trace`）**——单个命令，无编排：

```bash
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs --task <task-name> --workspace ./autobrowse
# 或对于受机器人保护的网站：
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs --task <task-name> --workspace ./autobrowse --env remote
```

这会运行浏览器会话并将完整的跟踪写入 `./autobrowse/traces/<task>/latest/`。

**跟踪路径（`--browser-trace`，仅远程）**——外部 harness 预创建一个 Browserbase 会话，将 `bb-capture` 作为被动观察者附加，并将会话的 `connectUrl` 传递给 `evaluate.mjs`，以便每个内部 `browse` 调用都使用 `--cdp $connectUrl --session autobrowse-main`（这是观察者获取完整网络/控制台事件的规范浏览器跟踪模式）。每个迭代运行此块一次，将 `$N` 设置为 1 索引的迭代编号：

```bash
# 预检查——如果浏览器跟踪未与 AutoBrowse 一起安装，则快速失败。
BT_DIR="${CLAUDE_SKILL_DIR}/../browser-trace"
if [ ! -f "$BT_DIR/scripts/bb-capture.mjs" ]; then
  echo "ERROR: --browser-trace 需要 browser-trace 技能在 $BT_DIR。" >&2
  echo "通过克隆 github.com/browserbase/skills 并将 skills/browser-trace/" >&2
  echo "复制到与 AutoBrowse 相同的父目录（例如 ~/.claude/skills/browser-trace/）来安装它。" >&2
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
export O11Y_ROOT="$TRACE_ROOT/.o11y"   # 将浏览器跟踪输出停靠在 AutoBrowse 运行目录中
export O11Y_RUN_ID="$RUN_ID"           # 告诉 browse CLI 写入 descriptors.ndjson 到哪个运行目录

# b. 附加浏览器跟踪——被动观察者；在后台运行
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/bb-capture.mjs "$sid" "$RUN_ID" &
sleep 2

# c. 运行 AUTOBROWSE——connectUrl 标志告诉 evaluate.mjs 注入 --cdp/--session
#    到每个内部 browse 调用。内部代理永远不会看到 --remote。
node ${CLAUDE_SKILL_DIR}/scripts/evaluate.mjs \
  --task <task-name> --workspace ./autobrowse --env remote \
  --connect-url "$connect_url" --run-number "$N"

# d. 停止 + 二分 + 合并——顺序很重要；二分需要会话仍然存在，并且 unify-trace 将二分输出与 AutoBrowse 的 trace.json 合并成一个时间排序的 NDJSON，外部代理在每次迭代开始时首先读取
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/stop-capture.mjs "$RUN_ID"
node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/bisect-cdp.mjs "$RUN_ID"
node ${CLAUDE_SKILL_DIR}/scripts/unify-trace.mjs \
  --trace-dir "$TRACE_ROOT" \
  --o11y-dir "$O11Y_ROOT/$RUN_ID"

# e. 释放
browse cloud sessions update "$sid" --status REQUEST_RELEASE
```

这将内部代理的跟踪写入 `./autobrowse/traces/<task-name>/latest/`，并将 CDP 二分写入 `./autobrowse/traces/<task-name>/latest/.o11y/<run-id>/`。跟踪的 `browse` CLI 还会发出每个命令的丰富节点描述符到 `.o11y/<run-id>/cdp/descriptors.ndjson`（每个驱动页面的调用都是一个 JSON 对象：目标标签/ID/角色/可访问名称/属性/xpath/bounding-rect）。描述符文件为下游代码生成提供输入；它**不是**用于假设形成所必需的——在读取跟踪时跳过它。

### 读取跟踪

```bash
cat ./autobrowse/traces/<task-name>/latest/summary.md
```

摘要包含持续时间、成本、回合数、决策日志和最终 JSON 输出。

如果代理失败或卡住，请深入查看：
- 读取 `./autobrowse/traces/<task-name>/latest/trace.json`——搜索失败回合
- 使用 Read 工具读取失败点周围的屏幕截图

**当使用 `--browser-trace` 时——从 `unified-events.jsonl` 开始。** harness 将代理的回合日志和浏览器的 CDP 水管合并为一个时间排序的 NDJSON 流在运行根。一个文件，源标记（`source: "agent" | "browser"`），按墙上时间戳交错。从上到下浏览它；失败原因是通常是一两行相邻的（代理发出命令 X，浏览器以 Y 响应）。

```bash
cat ./autobrowse/traces/<task-name>/latest/unified-events.jsonl
```

结构化文件（`trace.json`，`.o11y/<run-id>/cdp/*`）也是代理可消费的，以便在统一流指向需要更多信息时进行深入：

| 需要 | 钻取文件或命令 |
|---|---|
| 每页总计+时间（事件、网络计数、按页面的错误） | `.o11y/<run-id>/cdp/summary.json` |
| 所有失败的网络请求集中在一个地方 | `.o11y/<run-id>/cdp/network/failed.jsonl` |
| 完整的控制台异常有效负载（堆栈跟踪等） | `.o11y/<run-id>/cdp/console/exceptions.jsonl` |
| 每页切片（仅页面 N 上的事件） | `.o11y/<run-id>/cdp/pages/<pid>/` |
| 特定回合的完整推理文本/未截断的工具输出 | `trace.json`（按 `turn === N` 过滤） |
| 自由分组查询（例如顶级主机、按页面错误） | `O11Y_ROOT=./autobrowse/traces/<task-name>/latest/.o11y node ${CLAUDE_SKILL_DIR}/../browser-trace/scripts/query.mjs <run-id> <cmd>` |

统一流是默认的；仅在需要分组查询、完整文本有效负载或无法通过过滤流获得时才钻入结构化文件。

### 形成一个假设

找到问题发生的确切回合。有什么单一启发式方法可以防止它？

在 `--browser-trace` 下，假设必须引用来自 `unified-events.jsonl` 的**特定事件**（行号或时间戳）——或者如果你必须深入到一个钻取文件来命名它。这使更新基于证据而不是感觉驱动。仅基于代理命令的假设可能说“点击没有工作”；基于统一流的假设可以说“在 unified-events.jsonl 的第 47 行：`browse open` 后跟 `/api/checkout` 上的 `Network.responseReceived` 状态 403 —— 切换到 `--verified --proxies`。”

示例：
- "点击下拉菜单后等待 1 秒——选项在可点击之前会动画显示"
- "直接导航到 `/pay-invoice/`——完全跳过着陆页"
- "使用 `browse fill #field_3 value` 而不是 `browse type`——这个字段在获得焦点时会清除"
- "页面在回合 8 显示一个加载器——在快照之前添加 `browse wait timeout 2000`"
- （使用 `--browser-trace`）“在 unified-events.jsonl 的第 47 行，连续 3 个 `/api/availability` 上的 `Network.responseReceived` 事件在 `browse open` 后返回 403 —— 网站正在指纹识别；下一次迭代需要 `--verified --proxies`。”

### 更新 strategy.md

编辑 `./autobrowse/tasks/<task-name>/strategy.md`。保留所有有效的内容。修复特定的失败。添加一个具体的启发式方法。

好的策略有：
- **快速路径**：直接 URL 或跳过探索的快捷方式
- **逐步工作流**：带有时间注释的精确序列
- **特定网站知识**：选择器 ID、表单字段名称、成功指示器
- **失败恢复**：当 X 出错时要做什么

### 判断结果

读取新的摘要。是否通过？是否有明显进展？
- **通过或有进展** → 保留，下一个迭代
- **没有进展或倒退** → 将 strategy.md 还原为上一个版本并尝试不同的假设

### 生成可运行的脚本（可选）

一旦任务收敛，您可以通过 `scripts/codegen.mjs` 生成一个确定性可运行的脚本
在一个或多个框架中。这是一个针对每个框架的 LLM 调用，通过内容哈希缓存，可选的验证与新鲜会话和失败时重写。

```bash
node ${CLAUDE_SKILL_DIR}/scripts/codegen.mjs \
  --task <name> \
  --workspace ./autobrowse \
  --frameworks playwright,stagehand \
  --verify
```

每个框架都会在 `tasks/<name>/<framework>/` 下获得自己的子目录，其中包含发出的脚本和自包含的脚手架（`package.json`，`tsconfig.json`）。该目录可以独立运行，使用 `cd tasks/<name>/playwright && npm install && npx tsx <name>.ts`——唯一运行时要求是 `BROWSERBASE_API_KEY`（对于 Stagehand 目标还需要 `ANTHROPIC_API_KEY`）。

内置框架：`playwright`，`stagehand`。使用 `--prompt-template <path> --frameworks custom` 添加自定义框架（并提供您自己的运行器或传递 `--no-verify`）。

常见标志：

| 标志 | 目的 |
|---|---|
| `--frameworks a,b,...` | 逗号分隔；默认 `playwright` |
| `--verify` / `--no-verify` | 运行生成的脚本与新鲜 BB 会话；默认 `--verify` |
| `--max-retries N` | 验证失败重写上限；默认 2 |
| `--cache-only` | 缓存未命中时出错（CI 友好） |
| `--force` | 破坏缓存 |
| `--dry-run` | 估计提示大小+成本；不调用 LLM |
| `--run <id>` | 强制特定 `run-NNN`（默认：最新通过） |

输出是每个框架的 JSON 行到 stdout。如果任何选定的框架的最终状态是 `passed: false`，则非零退出。

参见 `references/playwright-cdp-bridge.md` 以了解发出的脚本遵循的规范 `connectOverCDP` 模式。

### 所有迭代后——如果准备好了就发布

如果任务在最后 3 次迭代中的 2 次或更多次通过**或已达到最大迭代限制**，则将其安装为 Claude Code 技能。**不要只是复制 strategy.md**——技能必须自包含且对从未见过此代码库的人来说有用。如果达到最大迭代次数而没有干净通过，请记录已知失败点，但仍记录所有学到的内容。

通过写入 `~/.claude/skills/<task-name>/SKILL.md` 来安装：

```bash
mkdir -p ~/.claude/skills/<task-name>
```

使用以下结构为 SKILL.md：

```markdown
---
name: <任务名称>
description: <用1-2句话描述这项技能的作用以及何时使用它。包含触发关键词。>
---

# <任务标题> — 浏览器技能

## 目的
<用1-2句话说明这项技能自动化的内容及其存在的原因。>

## 何时使用
<在什么情况下应该使用这项技能。>

## 浏览器CLI参考
内部代理使用 `browse` CLI。这项任务的关键命令：
- `browse stop` — 终止现有会话（切换到远程之前始终运行）
- `browse open <url> --remote` — 启动一个新的Browserbase云端会话并导航
- `browse open <url> --local` — 启动一个干净的本地浏览器并导航
- `browse tab new <url>` — 在新标签页中打开URL
- `browse wait load` — 等待页面完全加载
- `browse wait timeout <ms>` — 等待固定时间以等待加载指示器或动画
- `browse wait selector "<selector>"` — 等待元素变为可见
- `browse get title` — 验证是否在正确的页面
- `browse get text body` — 提取所有可见文本（内容提取的首选方法）
- `browse snapshot` — 获取可访问性树；每个节点都有[X-Y]格式的引用（例如 `[0-5]`，`[2-147]`）
- `browse click [X-Y]` — 通过最新快照中的引用[X-Y]点击元素（包括括号）

**在SKILL.md中永远不要使用 `--session <name>` 标志。** 命名会话是一个并行运行的解决方案——它们会污染技能与基础设施问题。技能必须在默认会话中独立工作。

## 工作流程

### 第1步 — 启动会话
<按顺序输入确切的 browse 命令>

### 第2步 — 导航
<确切的URL和验证步骤>

### 第3步 — 提取
<确切的提取命令>

### 第4步 — 输出
<要发出什么JSON，参考下方架构>

## 站点特定注意事项
<每个从迭代中获得的硬性启发式的列表。这是这项技能的核心价值。>

## 失败恢复
<在导航失败、会话被污染或提取返回垃圾时该做什么>

## 预期输出
```json
<粘贴任务.md中的预期输出架构>
```
```

编写完SKILL.md后，确认其已安装：
```bash
ls ~/.claude/skills/<任务名称>/SKILL.md
```

该技能现在可在Claude Code中的 `/<任务名称>` 下使用。

---

## 最终报告（多任务模式）

所有子代理完成后，打印一个Markdown表格：

| 任务 | 迭代次数 | 最终状态 | 通过 | 成本 |
|------|-----------|--------------|-----------|------|
| google-flights | 5 | ✅ 通过 | 是 | $0.42 |
| amazon-add-to-cart | 5 | ❌ 失败 | 否 | $1.20 |

然后将持久会话报告写入 `./autobrowse/reports/`，以便在工作空间内有持久记录：

```bash
mkdir -p ./autobrowse/reports
```

写入文件 `./autobrowse/reports/YYYY-MM-DD-HH-MM-<任务>.md`，包含：

```markdown
# AutoBrowse 会话报告
**日期:** <ISO日期>
**任务:** <逗号分隔列表>
**环境:** 远程|本地
**总成本:** $X.XX

## 结果

| 任务 | 迭代次数 | 通过率 | 最终状态 | 通过 | 成本 |
|------|-----------|-----------|--------------|-----------|------|
| ... | ... | X/5 | ✅/❌ | 是/否 | $X.XX |

## 每个任务的收获

### <任务名称>
- **关键洞察1:** <代理学到的内容>
- **关键洞察2:** <另一个启发式>
- **修复失败模式:** <什么在失败以及如何解决的>

## 迭代日志

### <任务名称>
| 迭代 | 轮次 | 成本 | 状态 | 测试的假设 |
|------|-------|------|--------|-------------------|
| 1 | 79 | $18.75 | ❌ 失败 | 基线 |
| 2 | 9 | $0.26 | ✅ 通过 | 会话污染修复 |
| ... | ... | ... | ... | ... |
```

---

## 规则

- **仅编辑 `strategy.md`** — 不要触碰 `task.md`（除非从模板创建）或 `evaluate.mjs`
- **停留在工作空间** — 所有训练写入都去 `./autobrowse/`，永远不去 `~/.claude/skills/autobrowse/`。技能源是只读的。
- **每次迭代一个假设** — 一次测试一个更改
- **基于成功** — 保留有效部分，在此基础上添加
- **信任追踪** — 内部代理显示它所见所做
- **通过到 `~/.claude/skills/`** — 你在那里写的唯一文件是最终通过的 `SKILL.md`
- **在二分法之前不要发布** — 在 `--browser-trace` 下，每次迭代的末尾顺序是不可协商的：`stop-capture` → `bisect-cdp` → `browse cloud sessions update REQUEST_RELEASE`。二分法依赖于追踪停止时会话仍然存在。
