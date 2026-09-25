# C/C++ 安全审查

解析四个参数，执行一次 `Workflow` 调用，返回报告。工作流负责并发、重试和结果收集。

**适用对象：** 原生 C/C++ 用户空间 — 内存安全、整数溢出、竞争条件、类型混淆、Linux/macOS 守护进程、Windows 服务。

**不适用对象：** 内核驱动程序或模块；托管语言（Java、C#、Python、Go、Rust）；无 libc 的嵌入式或裸机代码。

## 第 0 阶段 — 参数

解析调用行上的任何自由文本（`flamenco only`、`high severity only`、`use haiku`）并预填其隐含内容。然后执行一次 **`AskUserQuestion`** 调用以解决任何未解决的问题。永远不要对必需参数进行静默默认。

| 参数 | 值 | 从调用中推断 |
|---|---|---|
| `threat_model` | `REMOTE` / `LOCAL_UNPRIVILEGED` / `BOTH` | "remote"、"network"、"attacker" → `REMOTE`；"local"、"unprivileged" → `LOCAL_UNPRIVILEGED`；否则询问 |
| `worker_model` | `haiku` / `sonnet` / `opus` / `inherit` | 显式模型名称。否则询问。`inherit` 使用会话模型 |
| `severity_filter` | `all` / `medium` / `high` | "all"、"every"、"noisy" → `all`；"medium and above" → `medium`；"high only" → `high`；否则询问 |
| `scope_subpath` | 仓库相对目录，可选 | "X only"、"just audit X/" → 匹配的子目录，与顶级目录进行模糊匹配。不存在 → `.`。歧义 → 询问 |

两个范围在整个运行期间保持分离：

- **`finding_scope_root`** = `scope_subpath`（默认 `.`）— 查找项必须位于其中，并且它是生成单元列表的树。
- **`context_roots`** = `.` — 自由读取以建立调用者、构建标志和可达性。如果用户明确禁止更广泛的读取，则将其缩小到 `finding_scope_root`，并且当您这样做时，可达性置信度会降低。

## 第 1 阶段 — 解析路径

```bash
root="${CLAUDE_PLUGIN_ROOT:-}"
if [ -z "$root" ] || [ ! -f "$root/workflows/c-review.js" ]; then
  # 缓存布局未设置变量的回退方案。~/.claude 仅限 — 永远不要 `.`：
  # `.` 是 AUDITED 仓库，而一个提供或镜像此市场的地方的树将赢得遍历并运行其脚本副本，具有不同的提问集和没有任何内容说明哪个副本运行。让 find 的标准错误通过；缺失的 ~/.claude 是报告的真实失败，而不是隐藏的噪音。
  hit="$(find "$HOME/.claude" -path '*/c-review/workflows/c-review.js' -print -quit)"
  root="${hit%/workflows/c-review.js}"
fi
[ -n "$root" ] && [ -f "$root/workflows/c-review.js" ] && echo "PLUGIN ROOT: $root"
```

如果两者都无法解析，则停止，而不是使用空路径运行 — 并说明您解析了哪个路径，以便在八个代理针对它运行之前可见其他副本。

```bash
# 工作流不能调用 Date.now()，因此时间戳在这里创建。
output_dir="$(pwd)/.c-review-results/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$output_dir"; echo "$output_dir"

# 工作流脚本没有文件系统 API，并且 `assemble_findings.py` 对其自己的 cwd 解析 `--scope`。在这里一次性解析它，并传递两种拼写，或者工作流在查找项的路径中删除 `src/`，而汇编器从 `/repo/src/` 中删除 `/`，并且两者对哪些查找项是彼此的重复项存在分歧。
scope_abs="$(cd "${scope_subpath:-.}" && pwd)" || echo "scope_subpath does not exist"
echo "$scope_abs"
```

`uv` 必须在 PATH 上：检测运行单元枚举器，汇编器运行 `assemble_findings.py`。如果 `uv` 缺失，请说明并停止 — 整个审查是从该单元列表分区的。

## 第 2 阶段 — 运行工作流

调用此技能 **就是** 多代理编排的自愿选择 — 再次调用 `Workflow` 而不询问。对真实代码库的审查也会越过任何默认工作流大小指南；该指南是建议性的，而这是它豁免的情况。不要缩小扇出以适应它，并且不要用手工生成的 `Agent` 调用替换。

一次 `Workflow` 调用。`scriptPath` 接收第 1 阶段解析的绝对路径；`args` 必须是一个真实的 JSON 对象，而不是 JSON 编码的字符串。

```
Workflow({
  scriptPath: "<plugin_root>/workflows/c-review.js",
  args: {
    outputDir:        "<output_dir>",
    pluginRoot:       "<plugin_root>",
    threatModel:      "REMOTE",
    severityFilter:   "all",
    findingScopeRoot: "expat/lib",
    findingScopeRootAbs: "/abs/path/to/repo/expat/lib",
    contextRoots:     ".",
    workerModel:      "sonnet"
  }
})
```

`findingScopeRootAbs` 是第 1 阶段的 `scope_abs`，并且在实践中不是可选的：省略，工作流会告诉汇编器未知绝对根，并且作为 `/repo/expat/lib/xmlparse.c` 提交的查找项不会与作为 `xmlparse.c` 提交的相同错误合并。

六个进一步参数是可选的。省略，每个参数都使用其默认值；传递类型错误，工作流会使用字段名而不是默认值抛出错误。仅在用户请求或运行评估时传递它们：

| 参数 | 默认值 | 用途 |
|---|---|---|
| `maxUnitLines` | `150` | 审查单元的限制；较大的函数会在语法缝隙处拆分。提高它会导致该限制防止的饱和 |
| `linesPerAgent` | `1500` | 每个审查代理的源代码行数。**在小型树上的无操作** — `--agent-min`（默认 4）将派生计数下限，因此两个非常不同的值可以产生相同的分配。使用 `reviewAgents` 来固定扇出 |
| `reviewAgents` | 派生 | 固定审查扇出，受派生计数的相同下限约束：两者都限制在 4–14，并且显式值高于 14 会将上限提高到自身。值低于 4 会被提高到 4，并且太小的尾切片不值得一个代理，因此最终计数可能比请求的低一个 |
| `invariantAudit` | `false` | 向扫描添加共享状态不变性审计。一个额外的代理；为状态机密集型目标开启它 |
| `exclude` | `[]` | 单元枚举器跳过的 glob 或子字符串数组（每个都成为重复的 `--exclude`）。在枚举中止命名它无法拥有的路径时使用 — 排除的路径作为覆盖差距出现在枚举器的总计中，而不是沉默 |
| `benchmarkMode` | `false` | **仅评估。** 向审查者提示添加外部源声明和两个模式字段。它不会改变查找项；为真实审计请关闭它 |

工作流验证自己的参数，如果缺少任何参数，会使用命名字段抛出错误。它运行五个阶段：

| 阶段 | 代理 | 它做什么 |
|---|---|---|
| 检测 | 1 | 运行 `enumerate_units.py` 以获取单元列表；来自实际 API 使用的平台标志；共享状态结构；每个错误类别，是否存在任何候选位置 |
| 审查 | 4–14 | 每个连续的单元列表切片一个代理。每个返回具有严重性和每个（单元 × 问题）的账目行 |
| 扫描 | 0–2 | 类轴：每个没有在检测中排除的 Bug 类别一个代理。没有，则跳过该阶段。加上结构字段审计，当 `invariantAudit: true` 时 |
| 去重 | 0–1 | 仅用于汇编器无法确定性合并的冲突。通常跳过 |
| 汇编 | 1 | 运行 `assemble_findings.py`：账目门禁、确定性合并、`findings.json`、`REPORT.md`、`REPORT.sarif` |

**在中等规模的目标上大约有 8–10 个代理。**

## 第 3 阶段 — 返回报告

`Read <output_dir>/REPORT.md` 并返回它。

**在查找项旁边简单地说一次，没有误报的审查运行。** 每个严重性都是审查者的意见（`severity_source: "reviewer"`），`judgeRan` 总是 `false`，并且没有拒绝任何内容。预期您看到的一些内容是错误的或超出范围的 — 这样说而不是将列表作为已裁决呈现，并且不要自己过滤它。

然后突出显示，与查找项分开，工作流结果中任何表示运行部分的内容：

| 字段 | 含义和要做什么 |
|---|---|
| `artifactsWritten: false` | `REPORT.md` 和 `REPORT.sarif` 缺失；`parts/` 下的一部分文件完整。手动重新组装（见下文） — 永远不要从工具结果重建 |
| `artifactsWritten: null` | 汇编代理返回了空值，因此是否存在工件是 **未知的** — 命令可能已完成，但只有其结构化答案失败。在执行任何其他操作之前列出输出目录 |
| `gateAccepted: false` 与工件写入 | 看起来像成功的失败。工件是完整的；**覆盖门禁** 无法运行或拒绝了账目，因此审查被汇编但未验证。**不要** 重新运行汇编器 — 阅读 `ledger-gate.json` 并报告差距。`artifactError` 总是携带原因 |
| `coverage: null` | 覆盖是 **未测量的**，不完整。永远不要将此类运行报告为完全覆盖；指向 `ledger-gate.json` |
| `coverage` | 报告 `checksSatisfied` / `checksRequired`，以及 `checksCompleted` 仅作为 "answered" — 永远不要作为 "functions reviewed"。`checksSatisfied` 低于 `checksCompleted` 意味着门禁抛出了行：覆盖-*完整性* 失败。命名 `violations` |
| `groupsFailed`、`agentFailures`、`notes` | 那个区域 **未被覆盖**。不要让干净的报告暗示它是 |
| `unrecognisedParts` | 没有工件的整个代理输出。`null` 意味着 **未检查，而不是没有** |
| `silentClasses` / `ruledOutClasses` / `platformDroppedClasses` | "扫描且未找到" / "未查看" / "配置范围外"。单独报告 — 只有中间一个意味着人类应该查看 |

当 `artifactsWritten` 为 false 时的手动重新组装：

```
uv run --no-project <plugin_root>/scripts/assemble_findings.py --run-dir <output_dir> \
  --threat-model <MODEL> --severity-filter <FILTER> --no-judge \
  --scope <finding_scope_root> --context-roots <context_roots> \
  --worker-model <worker_model> \
  --expect <part-stem>=<finding-count>   # 每个工作流日志命名的部分一个
```

- **`--expect` 不是可选的。** 没有它，允许列表会接受 `parts/` 下面的每个文件，包括一个无人分派的文件，并且运行仅因此原因退出 **1**。如果您无法从工作流日志中恢复计数，退出 1 是正确的，并且运行是已汇编但未验证的。
- **永远不要省略 `--no-judge`。** 省略它会用中等覆盖每个审查者严重性，并记录 `judge_ran: true` 对于从未见过的一个运行。
- 六个标志根本无法重建（`--expect-complete`、`--benchmark-mode`、`--groups-attempted`、`--groups-failed`、`--agent-failure`、`--external-source`），因此文档会在可能丢失一个切片的运行上说明 `agent_failures: []`。报告它。没有 `units.json`，汇编器也会退出 **1**：没有运行门禁。

最后列出工件：`findings.json`、`REPORT.md`、`REPORT.sarif`、`units.json`、`ledger-gate.json`、`detect.json`，以及 `parts/` 和 `assignments/` 目录。

## 拒绝的理由

- **"运行基本正常，所以我只是展示报告。"** 失败的代理暴露了未覆盖的区域，而不是舍入误差。在查找项旁边报告它。
- **"覆盖率是 80%，基本上是完整的。"** 缺失的 20% 是 `ledger-gate.json` 中的确切（单元，问题）对列表。命名它们。
- **"我将自己编写查找项，而不是运行工作流。"** 手动编排的成本远高于召回率更低的成本。始终调用 `Workflow`。
- **"工件失败，所以我将从工具结果重建报告。"** 部分文件在磁盘上，汇编器是确定性的。重新运行它。
- **"零查找项，所以没有什么可报告的。"** 零查找项运行仍然产生两个工件，并且真实 C 代码中的零查找项本身也值得大声说出来。
- **"工作流返回了查找项，所以我可以跳过阅读 REPORT.md。"** 工具结果是限制的，并携带计数，而不是查找项。报告是工件。
- **"没有审查者运行，所以我应该自己过滤查找项。"** 不 — 静默删除查找项会复制审查者的成本而没有其严谨性，并且会让工件与您所说的不一致。报告管道产生的结果，标记为未裁决。
- **"没有审查者运行，所以我应该将严重性作为权威。"** 也不。它们是审查者意见。
- **"类-代理扇出会发现更多。"** 位置是故意分区；类目录是顶部的有界完整性扫描。不要添加一个。

设计理由、覆盖门禁的威胁模型及其已知限制在 [AGENTS.md](../../AGENTS.md) 中。更改提示或门禁规则之前请阅读它。
