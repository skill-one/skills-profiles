# Semgrep 安全扫描

使用自动语言检测、并行执行和合并 SARIF 输出的 Semgrep 扫描。

## 基本原则

1. **始终使用 `--metrics=off`** — Semgrep 默认发送遥测数据；`--config auto` 也会发送遥测数据。每个 `semgrep` 命令都必须包含 `--metrics=off`，以防止在安全审计期间数据泄露。
2. **用户必须批准扫描计划（步骤 3 是硬性门槛）** — 原始的 "扫描此代码库" 请求**不等于**批准。展示确切的规则集、目标、引擎和模式；在生成扫描器之前，等待明确的 "yes"/"proceed"。
3. **第三方规则集是必需的，不是可选的** — Trail of Bits、0xdea 和 Decurity 规则捕获官方注册表中未列出的漏洞。在检测到的语言匹配时，始终包含它们。
4. **`scripts/run-scans.sh` 生成命令；不要自己编写** — 它从批准的列表中构建每个 `semgrep` 行。正是 `--metrics=off`、`--include` 范围规则和代码的并行调度属性，而不是指令。给它批准的规则集并让它运行。
5. **扫描前始终检查 Semgrep Pro** — Pro 启用跨文件污点跟踪，捕获约 250% 的真正阳性结果。跳过检查意味着无声地遗漏关键的跨文件漏洞。
6. **报告未运行的项** — `scans.json` 会携带 `failed` 和 `skipped`，与 `scans` 一起。如果某个规则集的仓库无法克隆，或者扫描以非零状态退出，都必须出现在报告中。将部分扫描呈现为完整扫描比不扫描更糟糕。

## 使用场景

- 代码库的安全审计
- 在代码审查前发现漏洞
- 扫描已知错误模式
- 第一次静态分析

## 不应使用的场景

- 二进制分析 → 使用二进制分析工具
- 已配置 Semgrep CI → 使用现有管道
- 需要跨文件分析但没有 Pro 许可 → 考虑 CodeQL 作为替代方案
- 创建自定义 Semgrep 规则 → 使用 `semgrep-rule-creator` 技能
- 将现有规则移植到其他语言 → 使用 `semgrep-rule-variant-creator` 技能

## 输出目录

所有扫描结果、SARIF 文件和临时数据都存储在一个输出目录中。

- **如果用户在提示中指定了输出目录**，将其用作 `OUTPUT_DIR`。
- **如果没有指定**，默认为 `./static_analysis_semgrep_1`。如果已存在，则递增为 `_2`、`_3` 等。

在两种情况下，**始终使用 `mkdir -p` 创建目录**，然后再写入任何文件。

```bash
# 解析输出目录
if [ -n "$USER_SPECIFIED_DIR" ]; then
  OUTPUT_DIR="$USER_SPECIFIED_DIR"
else
  BASE="static_analysis_semgrep"
  N=1
  while [ -e "${BASE}_${N}" ]; do
    N=$((N + 1))
  done
  OUTPUT_DIR="${BASE}_${N}"
fi
mkdir -p "$OUTPUT_DIR/raw" "$OUTPUT_DIR/results"
```

输出目录在步骤 1 开始时解析**一次**，并在所有后续步骤中使用。

```
$OUTPUT_DIR/
├── rulesets.json                # 批准的计划（步骤 3），由 run-scans.sh（步骤 4）读取
├── scans.json                   # 运行的、失败的、跳过的和未覆盖任何内容的项（步骤 4）
├── raw/                         # 每个扫描的原始输出（未过滤）
│   ├── python-python.json        # <语言>-<规则集> 用于语言范围的规则
│   ├── python-python.sarif
│   ├── python-django.json
│   ├── python-django.sarif
│   ├── all-security-audit.json   # all-<规则集> 用于跨语言规则，运行一次
│   ├── all-security-audit.sarif
│   └── ...
└── results/                     # 最终合并输出
    └── results.sarif
```

## 前置条件

**必需：** Semgrep CLI (`semgrep --version`)。如果未安装，请参阅 [Semgrep 安装文档](https://semgrep.dev/docs/getting-started/)。

**可选：** Semgrep Pro — 启用跨文件污点跟踪、跨过程分析和支持额外语言（Apex、C#、Elixir）。检查：

```bash
# --metrics=off 因为原则 1 没有例外，并且这是运行中的第一个 semgrep 命令。stderr 被保留，因为 "OSS only" 有多个原因（已登出、无订阅、注册表被阻止），并且对于所有这些原因，运行都会无声降级。
if PRO_ERR=$(semgrep --pro --validate --metrics=off --config p/default 2>&1); then
  echo "Pro 可用"
else
  echo "OSS only"
  echo "  原因: $(printf '%s' "$PRO_ERR" | tail -n 3)"
fi
```

**限制：** OSS 模式无法跨文件跟踪数据流。Pro 模式使用 `-j 1` 进行跨文件分析（每个规则集较慢，但并行规则集可以弥补）。

## 扫描模式

在步骤 2 中选择模式。模式会影响扫描标志和后处理。

| 模式 | 覆盖范围 | 报告的发现 |
|------|----------|------------|
| **全部运行** | 所有规则集、所有严重性级别 | 所有内容 |
| **仅重要** | 所有规则集、预过滤和后过滤 | 仅安全漏洞，中等高置信度/影响 |

**仅重要** 应用两层过滤器：
1. **预过滤**：`--severity WARNING --severity ERROR`（CLI 标志）
2. **后过滤**：JSON 元数据 — 仅保留 `category=security`、`confidence∈{MEDIUM,HIGH}`、`impact∈{MEDIUM,HIGH}`

有关元数据标准和 jq 过滤命令，请参阅 [scan-modes.md](references/scan-modes.md)。

## 协调架构

```
┌──────────────────────────────────────────────────────────────────┐
│ MAIN SESSION (此技能)                                          │
│ 步骤 1：检测语言 + 检查 Pro 可用性                            │
│ 步骤 2：选择扫描模式 + 规则集（参考：rulesets.md）             │
│ 步骤 3：展示计划 + 规则集，获取批准 [⛔ 硬性门槛]             │
│ 步骤 4：使用批准的规则集运行 scripts/run-scans.sh              │
│ 步骤 5：后处理、合并、报告、删除仓库/                        │
└──────────────────────────────────────────────────────────────────┘
         │ 步骤 4：Bash
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ scripts/run-scans.sh                                             │
│   克隆       每个第三方仓库一次，到 repos/                        │
│   生成       每个规则集一个 semgrep 命令                        │
│                ├── python     p/python, p/django   --include=*.py│
│                ├── javascript p/javascript         --include=*.js│
│                ├── docker     p/dockerfile                       │
│                └── 跨语言  p/security-audit, p/secrets,  │
│                                    克隆的仓库  （无过滤） │
│   运行       批量运行 --jobs，每个进程读取退出代码               │
│   写入       scans.json — 扫描、失败、跳过                      │
└──────────────────────────────────────────────────────────────────┘
```

批准门槛保持在会话中；脚本仅执行且不询问任何内容。批准列表作为 JSON 文件到达它，因此扫描不能到达用户拒绝的规则集。

跨语言规则集放在一个共享单元中，而不是每个语言重复一次。
`p/security-audit`、`p/secrets` 和第三方仓库扫描整个目标无范围，因此每次运行每个语言运行相同的命令 N 次，并将 SARIF 合并留给副本去重。

## 作为工作流运行

此插件提供 `/static-analysis:semgrep-scan`，它运行整个扫描端到端：
检测语言和 Pro，从 [rulesets.md](references/rulesets.md) 选择规则集，运行 `scripts/run-scans.sh`，合并和报告。给它一个 JSON 对象，而不是文本：

```
/static-analysis:semgrep-scan {"target": "/abs/path", "mode": "run-all"}
```

**它不会停止以等待规则集批准。** 使用目标调用它就是选择，与 `/variant-analysis:variants` 的工作方式相同。这是安全的，因为扫描是针对目标的只读操作 — 没有 `--autofix`，输出目录内的每个写入 — 因此步骤 3 下的批准门槛只是一个范围确认，而不是安全确认。无论怎样，运行的内容都记录在 `rulesets.json` 和 `scans.json` 中。

当您希望运行扫描时使用工作流；当规则集选择本身很重要，并且您希望在编辑列表之前看到和编辑列表时，使用以下五个步骤。

## 工作流

**请遵循 [scan-workflow.md](workflows/scan-workflow.md) 中的详细工作流。** 摘要：

| 步骤 | 操作 | 门槛 | 关键参考 |
|------|------|------|----------|
| 1 | 解析输出目录，检测语言 + Pro 可用性 | — | 使用 Glob，而不是 Bash |
| 2 | 选择扫描模式 + 规则集 | — | [rulesets.md](references/rulesets.md) |
| 3 | 展示计划，获取明确批准 | ⛔ 硬性 | AskUserQuestion |
| 4 | 运行扫描 | — | `scripts/run-scans.sh` |
| 5 | 后处理、合并、报告、清理 | — | 合并脚本（下方） |

**任务强制执行：** 在调用时，创建 5 个任务，具有 blockedBy 依赖关系（每个步骤阻止前一个步骤）。步骤 3 是硬性门槛 — 仅在用户明确批准后标记完成。

**合并命令（步骤 5）：**

```bash
# run-all
uv run --no-project {baseDir}/scripts/merge_sarif.py "$OUTPUT_DIR/raw" "$OUTPUT_DIR/results/results.sarif" \
  --scans "$OUTPUT_DIR/scans.json"

# important-only，在 raw/ 中的每个文件运行 JSON 后过滤后
uv run --no-project {baseDir}/scripts/merge_sarif.py "$OUTPUT_DIR/raw" "$OUTPUT_DIR/results/results.sarif" \
  --important --scans "$OUTPUT_DIR/scans.json"
```

`--scans` 会丢弃在 `.failed` 下列出的扫描的输出。一个中途失败的扫描可能仍然写了一个 `.sarif`，在 `--important` 下该文件没有后过滤，这是一个错误而不是空过滤器。没有该标志，一个失败的扫描会拒绝每个健康的扫描合并结果。排除的文件在 stdout 上命名，因此它们可以出现在报告中。

后过滤读取 SARIF 不携带的元数据，因此不能重新运行合并文件上的后过滤；`--important` 而是保留 JSON 过滤器保留的发现，匹配 `(rule, file, line)`。没有它 `results.sarif` 是未过滤的，而 JSON 方面不是。

## 工作流和代理

| 组件 | 目的 |
|------|------|
| `scripts/run-scans.sh` | 从批准的规则集构建每个扫描命令，批量运行它们，并写入 `scans.json` |

步骤 4 是一个 Bash 调用。没有子代理运行扫描的任何部分：从进程读取退出代码和发现计数，以及它们写入的 JSON。

## 拒绝的理由

| 快捷方式 | 为什么不正确 |
|----------|--------------|
| "用户请求了扫描，那就是批准" | 原始请求 ≠ 计划批准。展示计划，使用 AskUserQuestion，等待明确的 "yes" |
| "步骤 3 任务阻塞，直接标记完成" | 谎报任务状态会破坏强制执行。仅在真实批准后才标记完成 |
| "我已经知道他们想要什么" | 假设会导致扫描错误目录/规则集。展示计划以验证 |
| "直接使用默认规则集" | 用户必须在扫描前看到并批准确切的规则集 |
| "未经询问添加额外规则集" | 未经同意修改批准列表会破坏信任 |
| "第三方规则集是可选的" | Trail of Bits、0xdea、Decurity 捕获官方注册表中未列出的漏洞 — 必需的 |
| "使用 --config auto" | 发送遥测数据；对规则集控制较少 |
| "我会直接运行 semgrep 命令" | `run-scans.sh` 是执行 `--metrics=off`、`--include` 规则和输出目录 `--exclude` 的东西。手写命令会无声地丢失它们 |
| "脚本失败，我会直接运行 semgrep 以获取一些东西" | 非零退出意味着没有扫描成功。报告并停止；手运行子集被视为完整扫描 |
| "一些扫描失败，运行仍然完成" | `failed` 和 `skipped` 是 `scans.json` 的一部分。报告它们或用户会将部分扫描视为干净的 |
| "Pro 太慢，跳过 --pro" | 跨文件分析捕获 250% 的真正阳性结果；值得花时间 |
| "Semgrep 原生处理 GitHub URL" | URL 处理在具有非标准 YAML 的仓库上失败；始终先克隆 |
| "清理是可选的" | 克隆的仓库会污染用户的工位，并在运行之间累积 |
| "使用 `.` 或相对路径作为目标" | 子代理需要绝对路径以避免歧义 |
| "让用户稍后选择输出目录" | 输出目录必须在步骤 1 中解析，在创建任何文件之前 |

## 参考索引

| 文件 | 内容 |
|------|------|
| [rulesets.md](references/rulesets.md) | 完整规则集目录和选择算法 |
| [scan-modes.md](references/scan-modes.md) | 预/后过滤标准和 jq 命令 |

| 工作流 | 目的 |
|------|------|
| [scan-workflow.md](workflows/scan-workflow.md) | 完整 5 步骤扫描执行过程 |
| `scripts/run-scans.sh` | 步骤 4 调用的扫描运行器 |

## 成功标准

- [ ] 解析输出目录（用户指定或自动递增默认值）
- [ ] 所有生成的文件存储在 `$OUTPUT_DIR` 内
- [ ] 检测语言并统计文件数量；检查 Pro 状态
- [ ] 用户选择扫描模式（全部运行 / 仅重要）
- [ ] 规则集包含所有检测语言的第三方规则
- [ ] 用户明确批准了扫描计划（步骤 3 门槛通过）
- [ ] `run-scans.sh` 退出 0 并写入 `$OUTPUT_DIR/scans.json`
- [ ] `scans.json` 中的 `failed` 和 `skipped` 为空，或列在报告中
- [ ] `scans.json` 中标记为 `partial` 的扫描为空，或列在报告中 — 它们运行时部分规则编译失败
- [ ] 每个使用的 `semgrep` 命令都使用 `--metrics=off`
- [ ] 在步骤 3 门槛时将批准的计划写入 `$OUTPUT_DIR/rulesets.json`，并原封不动地传递给扫描器
- [ ] `scans.json` 中的 `coveredNothing` 为空，或列在报告中
- [ ] 原始每个扫描输出存储在 `$OUTPUT_DIR/raw/`
- [ ] `$OUTPUT_DIR/results/` 中存在 `results.sarif` 且为有效 JSON
- [ ] 仅重要模式：合并前应用后过滤，合并运行使用 `--important`，未过滤结果保留在 `raw/`
- [ ] 结果摘要报告，包含严重性和类别细分
- [ ] 清理（如果有）从 `$OUTPUT_DIR/repos/`
