---
name: rust-review
description: 执行全面的 Rust 安全审查，涵盖安全/不安全边界问题、不安全代码块中的内存安全、并发风险、恐慌引发的拒绝服务（DoS）、FFI 安全性以及异步运行时错误。在审计 Rust 包、服务或库时使用，特别是包含 `unsafe`、FFI 或并发代码的。
---

# Rust 安全审查

在主对话中运行（通过 `/rust-review:rust-review` 调用）。协调器拥有 `Task*` 账本作为重试的簿记；工作进程和裁判没有任务工具。工作进程和裁判是命名的插件子代理（`rust-review:rust-review-worker`、`rust-review:rust-review-dedup-judge`、`rust-review:rust-review-fp-judge`）；工具集在 `plugins/rust-review/agents/*.md` 中声明。发现结果通过共享输出目录中的 Markdown with YAML 文件进行交换。

## 何时使用

Rust 应用程序/库安全审查：安全/不安全边界审计、`unsafe` 块中的内存安全、并发风险、服务器上的恐慌诱导拒绝服务、FFI 安全性、异步运行时错误。

## 何时不使用

- 纯 C / 纯 C++ 代码库——请使用 `c-review`。
- 智能合约（Solana 程序 / NEAR 合约 / Ink!）——请使用 `solana-vulnerability-scanner` 或合约特定技能。
- 没有用户空间分配的内核模式 Rust 驱动程序——覆盖率不完整；仅标记为建议性。
- 密钥/内存卫生（零化、`Zeroize`/`ZeroizeOnDrop`/`secrecy` 使用、残留的栈/堆副本）——请使用 `zeroize-audit` 技能；rust-review 不涵盖内存零化。

## 子代理

| 子代理类型 | 目的 | 工具集 |
|---|---|---|
| `rust-review:rust-review-worker` | 运行分配的集群，写入发现结果 | 读取、写入、编辑、Bash |
| `rust-review:rust-review-dedup-judge` | 合并重复项（运行**首先**） | 读取、写入、编辑、Glob |
| `rust-review:rust-review-fp-judge` | FP + 严重性 + 最终报告（运行**其次**） | 读取、写入、编辑、Bash |

工具来自每个代理的 frontmatter 在启动时提供。协调器的 `Task*`/`Agent`/`Bash`/等 来自此技能的 `allowed-tools`。**搜索工具 / `Bash` 交互**：在当前 Claude 代码中，授予 `Bash` 的代理**不**也被授予专门的 `Glob` **或 `Grep`** 工具（调用返回 `No such tool available`； harness 期望通过 `Bash` 使用 `find`/`grep`/`rg`）。因此，只有 dedup-judge——唯一一个**不**持有 `Bash` 的代理——使用 `Glob`；worker、fp-judge 和协调器通过 `Read` / `Bash` `find` / `rg` / `grep` / `test -f` 解决和搜索路径。由于集群/查找提示种子使用 ripgrep 正则表达式语法（`\s`、`\d`、`\b`），持有 `Bash` 的代理必须使用**`rg`** 运行它们。如果未安装 `rg`，其调用会大声失败（`command not found`）——回退到使用 POSIX 类的 `grep -E`（`\s`→`[[:space:]]`、`\d`→`[[:digit:]]`、丢弃 `\b`），永远不会使用原始的 `grep`，其*静默*的空值会变成一个坏 `cleared`。**不要**在持有 `Bash` 的代理协议中重新引入 `Glob`/`Grep`。

---

## 架构

```
coordinator: write context.md → build_run_plan.py → TaskCreate × M
          → spawn primer (foreground) → spawn M workers (parallel)
          → classify Phase-7 outcomes + write findings-index.txt
          → dedup-judge → fp-judge → report safety net (SARIF + REPORT.md) → return REPORT.md
```

输出目录包含：`context.md`、`plan.json`、`worker-prompts/`、`findings/`、`findings-index.d/`（每个 worker 的分片）、`findings-index.txt`、`coverage/`（每个 worker 的覆盖率门限文件）、`run-summary.md`、`dedup-summary.md`、`fp-summary.md`、`REPORT.md`、`REPORT.sarif`。

**路径约定**：每个后续阶段都通过 `${RUST_REVIEW_PLUGIN_ROOT}/scripts/*.py` 执行外壳命令，因此首先将此变量解析到包含 `prompts/clusters/unsafe-boundary.md`（以及 `scripts/build_run_plan.py`）的插件目录。按顺序尝试，第一个匹配的获胜：

1. **原生 Claude 代码** — `${CLAUDE_PLUGIN_ROOT}`，如果 `Bash: ls "${CLAUDE_PLUGIN_ROOT}/prompts/clusters/unsafe-boundary.md"` 解析则接受。
2. **Codex** — `${CODEX_PLUGIN_ROOT}`（如果该变量存在且解析到标记，则按相同方式设置）。
3. **回退搜索** — 覆盖 Codex 安装在 `~/.codex` 下、Claude 安装在 `~/.claude` 下以及本地检出/仓库运行：`Bash: find ~/.claude ~/.codex . -path '*/plugins/rust-review/prompts/clusters/unsafe-boundary.md' -print -quit 2>/dev/null`。取匹配项并删除尾部的 `/prompts/clusters/unsafe-boundary.md` 以获取根（家目录在 `.` 之前搜索，因此安装的副本优先于审计仓库中的任何 vendored 复本）。

将 `RUST_REVIEW_PLUGIN_ROOT` 设置为解析的根。如果所有三个都失败，**中止**并命名搜索的根——不要进入 Phase 4 时变量为空（每个 `uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/..."` 调用会因为路径错误而失败）。

**范围约定**：在整个运行过程中保持两个范围分开：

- `finding_scope_root` — 用户请求的审计子树。工作进程只能提交其易受攻击位置在此子树内的发现结果。
- `context_roots` — 工作进程和裁判可以检查的只读仓库根/文件，以验证可达性、调用者、包装器、构建标志、缓解措施和威胁模型详细信息。默认为 `.`，除非用户明确禁止更广泛的上下文。允许读取 `finding_scope_root` 外部的上下文；不允许在此处提交发现结果。

---

## 拒绝的理由

- **"`unsafe` 很少，所以手动跳过内存安全集群。"** 不要编辑集群列表——在 Phase 1 中准确设置 `has_unsafe` 并让 `build_run_plan.py` 决定。每个内存安全错误类别（UAF、double-free、未初始化读取、`Vec::set_len`、联合 UB）都需要 `unsafe`，因此当 `has_unsafe=true` 时规划器运行**整个** `memory-safety` 集群，当 `false` 时正确地省略它——没有“无论如何运行”。**unsafe-boundary** 集群不同：它没有 `requires` 并且始终运行（合并；其安全文档和 `repr(C)` 卫生适用于没有可见 `unsafe { }` 块的 FFI 声明）。
- **"编译器已经捕获了它。"** 借用检查器证明了安全代码数据竞争的不存在；它不能证明不安全块、恐慌可达性、ABBA 死锁、原子加载/存储顺序或 FFI ABI 不匹配。
- **"`unwrap()` 如果它是 `// SAFETY: 文档中不可落空` 是可以的。"** `// SAFETY:` 记录 `unsafe` 操作，而不是不可落空声明。在文档中不可落空的输入上的 `unwrap()` 如果文档是错误的，仍然有风险——低严重性提交并让 FP 裁判决定。
- **"`has_unsafe=false` 所以跳过运行。"** 纯安全 Rust 的 crate 仍然有恐慌拒绝服务、原子竞争、drop-panics 和 trait 实现风险。运行始终运行的集群。
- **"后台启动并行化工作进程。"** 它们不会——单个助手消息中的 `Agent` 调用已经运行并行。`run_in_background=true` 会破坏 Phase 6a 引导器缓存，因此每个工作进程都支付完整的缓存创建（`cache_read_input_tokens=0`）并且 ~15 K-token 引导器被浪费 M 次。默认：从工作进程启动中省略 `run_in_background`。
- **"我会重新导出集群列表 / 路径 / 通过前缀内联运行而不是运行 `build_run_plan.py`。"** 脚本是选择和渲染的唯一权威。释义它会导致工作进程自检需要的字段丢失，产生 `worker-N abort: spawn prompt malformed`。始终运行脚本并 `Read plan.json`。
- **"运行部分成功——我会直接从完成的写入 `REPORT.md`。"** 隐藏部分运行在成功报告后面是一个正确性错误。如果任何 Phase-5 集群任务不是 `completed`，在 `run-summary.md` 和最终响应中突出显示它。
- **"零发现——跳过 Phase 8。"** 始终运行两个裁判和 Phase 8b：dedup-judge 写入一个最小的无操作 `dedup-summary.md` 在空的索引上，fp-judge 写入空的 `REPORT.md`/`REPORT.sarif`，Phase 8b 的 SARIF 生成器在空的情况下发出 `results: []`。SARIF 消费者依赖于一个稳定的工件集。
- **"`Bash: ls README*` 对于预检是好的。"** 在 zsh 下，未匹配的 glob 会中止整个复合命令，在 `2>/dev/null` 运行之前。使用 `find`（永远不会在无匹配时失败）——并且不是 `Glob`，它不可用于同时持有 `Bash` 的代理。

---

## 协调工作流程

在主对话中运行这些阶段。

### Phase 0: 参数收集

**入口**：技能被调用。**出口**：`threat_model`、`worker_model`、`severity_filter` 解析；`scope_subpath` 解析或设置为 `"."`；`finding_scope_root=scope_subpath`；`context_roots` 解析。

技能直接被调用（没有命令包装器）。解析用户在 `/rust-review:rust-review` 行上传递的任何自由文本参数（例如 `flamenco only`、`high severity only`、`use haiku`），并预填它们暗示的答案——然后使用**一个** `AskUserQuestion` 调用询问任何缺失的必要参数。永远不要静默地默认必要参数。

必要参数：

| 参数 | 值 | 如何从参数推断 |
|---|---|---|
| `threat_model` | `REMOTE` / `LOCAL_UNPRIVILEGED` / `BOTH` | 像 "remote"、"network"、"attacker" 这样的词 → `REMOTE`；"local"、"unprivileged" → `LOCAL_UNPRIVILEGED`；否则询问。 |
| `worker_model` | `haiku` / `sonnet` / `opus` | 参数中显式模型名称。否则询问（没有静默默认值）。 |
| `severity_filter` | `all` / `medium` / `high` | "all"、"every"、"noisy" → `all`；"medium and above" → `medium`；"high only"、"criticals only" → `high`。否则询问——**没有静默默认值**。 |
| `scope_subpath` | 仓库相对目录（可选） | 像 "X only"、"just audit X/"、"审查子目录 X" 这样的短语 → `src/X/` 或匹配的子目录。对仓库顶层子目录进行模糊匹配。如果不存在，设置为 `"."`；如果歧义，询问。 |

调用 `AskUserQuestion` 恰好一次，只包含未解析的必要参数（`threat_model`、`worker_model`、`severity_filter`）加上 `scope_subpath` 仅当用户明确请求了缩小范围但它是歧义的时。如果所有必要参数都已预填并且范围不存在或已解析，则跳过问题。

解析 `scope_subpath` 后，设置 `finding_scope_root="${scope_subpath:-.}"`。默认将 `context_roots="."` 设置为让工作进程可以在缩小范围的子树外验证调用者/构建设置，而不会提交超出范围的发现结果。如果用户明确要求禁止更广泛的上下文，则设置 `context_roots="${finding_scope_root}"` 并注意可达性置信度可能较低。

### Phase 1: 前提条件

**入口**：Phase 0 完成。**出口**：`has_unsafe`、`has_ffi`、`has_concurrency`、`has_async`、`has_packed_repr`、`has_fs_io` 标志确定。如果 `${finding_scope_root}` 下不存在 `*.rs` 文件，则带有清晰消息中止。

首先确认 `uv` 存在（`command -v uv`）——每个来自 Phase 4 及以后的辅助脚本都通过它运行。如果缺失，**中止**并告诉用户安装它（`brew install uv` 或官方安装程序）；没有它下游的任何东西都无法运行。

在 `${finding_scope_root:-.}` 内部使用以下 `Bash` 命令探测（非空输出 ⇒ 标志为 true）。由于协调器持有 `Bash`，因此无法使用专门的 `Grep`/`Glob` 工具——使用 `Bash` 中的 `grep`/`rg`/`find`。 （探测正则表达式使用 `\s`/`\b`；如果您的 `grep` 缺乏 GNU `\s` 支持，使用 `rg -uu` 运行它们——它尊重 `\s` 并仍然搜索忽略的文件——或者，如果 `rg` 未安装，则将 `\s`→`[[:space:]]` 并删除 `\b`。扩大是安全的：一个误报能力标志只会增加一个无害的额外工作进程，而一个漏报会跳过整个阶段。`has_fs_io` 基于路径类型（`PathBuf`/`Path`，这也覆盖了 `&Path` 参数和裸 `Path::` 调用）和文件系统锚点（`fs::`/`File::`/`OpenOptions`/`read_dir`/…）而不是裸 `.join(`/`.push(` 调用——路径构造通过路径类型锚点达到，因此从入口排除 join/push 可以避免匹配不相关的迭代器/`JoinHandle` join 和使几乎每个 crate 都触发门限的 `Vec::push`。

注意对于 `Cargo.toml`：还探测 `[dependencies] tokio`、`async-std` 等，以设置 `has_async=true`，即使范围子路径中没有 `.await`（库 crate 通常重新导出）。

也探测 `Cargo.toml` 存在（信息性——在 `run-summary.md` 中注意审计是否在 Cargo 工作区、单个 crate 或松散的 `.rs` 文件上）：

```bash
# context_roots 可能是逗号分隔的（build_run_plan.py 将其视为列表），
# 因此探测每个根而不是将 "a,b" 作为单个（不存在的）路径传递。
echo "${context_roots:-.}" | tr ',' '\n' | while IFS= read -r root; do
  find "${root:-.}" -name 'Cargo.toml' -print -quit
done | head -1
```

### Phase 2: 输出目录

**入口**：Phase 1 标志设置。**出口**：绝对 `output_dir` 解析；`${output_dir}/findings/` 和 `${output_dir}/coverage/` 存在。

解析 `output_dir` 的绝对路径（默认：`$(pwd)/.rust-review-results/$(date -u +%Y%m%dT%H%M%SZ)/`）：

```bash
mkdir -p "${output_dir}/findings" "${output_dir}/coverage"
```

`coverage/` 子目录包含每个 worker 的覆盖率门限审计文件（`coverage/worker-{N}.md`）。工作进程写入它而不是将其表嵌入其回复中——见 `agents/rust-review-worker.md` 步骤 5。

### Phase 3: 代码库上下文

**入口**：`${output_dir}` 存在。**出口**：`${output_dir}/context.md` 已写入。

快速浏览 `README.{md,rst,txt}` 和任何构建/清单文件（`Cargo.toml`、`Cargo.lock`、`rust-toolchain.toml`、`build.rs`）——在执行任何 `Read` 之前使用 `find`（通过 `Bash`）进行预检（对缺失文件的 `Read` 会中止回合；由于协调器持有 `Bash`，因此它无法使用 `Glob` 工具）。**不要**使用 `Bash: ls README*` 进行预检：在 zsh 下，未匹配的 glob 会中止整个复合命令，在 `2>/dev/null` 运行之前。使用 `find . -maxdepth 2 -name 'README*' -o -name 'Cargo.toml' -o -name 'rust-toolchain.toml' -o -name 'build.rs'`，它永远不会在无匹配时失败。

将 `${output_dir}/context.md` 写入内容：YAML 前置部分（`threat_model`、`severity_filter`、`scope_subpath`、`finding_scope_root`、`context_roots`、`has_unsafe`、`has_ffi`、`has_concurrency`、`has_async`、`has_packed_repr`、`has_fs_io`、`output_dir`、`cargo_manifest` 作为 `workspace`/`single-crate`/`absent` 加上路径（当存在时），然后是一个简短的 Markdown 正文，包含五个部分——**目的**（1-3 句话）、**范围**（`finding_scope_root` 中的内容，以及该范围之外的发现都超出范围）、**入口点**（不可信数据进入的地方：网络、文件、CLI、IPC、`serde` 反序列化、FFI 输入）、**信任边界**（沙盒与受信任的同伴与任意远程）、**现有硬化**（模糊测试框架、MIRI 运行、`clippy::pedantic`、`cargo-deny`、`cargo-audit`）。

### 第 4 步：构建运行计划（确定性）

**入口：** 能力标志 + `threat_model` 已知；`${output_dir}/findings/` 存在。**出口：** 写入 `${output_dir}/plan.json` 和 `${output_dir}/worker-prompts/*.txt`；`M = worker_count` 已知。

选择、过滤、路径解析和生成启动提示的任务被**委托给脚本**，以保持启动提示完整和一致：

```bash
uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/build_run_plan.py" \
  --plugin-root "${RUST_REVIEW_PLUGIN_ROOT}" --output-dir "${output_dir}" \
  --threat-model "${threat_model}" --severity-filter "${severity_filter}" \
  --scope-subpath "${finding_scope_root:-.}" --context-roots "${context_roots:-.}" \
  --has-unsafe "${has_unsafe}" --has-ffi "${has_ffi}" \
  --has-concurrency "${has_concurrency}" --has-async "${has_async}" \
  --has-packed-repr "${has_packed_repr}" --has-fs-io "${has_fs_io}" \
  --max-passes-per-worker 4
```

脚本会写入 `plan.json` + `worker-prompts/worker-N.txt` + （如果 `--cache-primer=true`，默认值）`worker-prompts/cache-primer.txt`，并在标准输出上打印 JSON 摘要。在缺少任何提示时非零退出——显示消息并停止。使用默认的 `--max-passes-per-worker 4`，规划器选择约 8 个集群 → **M ≈ 13 个工作器**用于纯安全的 Rust（无 FFI / 并发 / 异步；`info-disclosure` 始终开启），约 10 个集群 → **M ≈ 15**用于并发安全的 Rust，约 15 个集群 → **M ≈ 23**用于全 Rust（不安全 + FFI + 并发 + 异步，当 `has_fs_io` 时加上 `input-os-safety`，当 `has_packed_repr` 时加上 `layout-safety`）。M 是后分块的工作器计数（`plan.workers.length`），所以它运行在集群计数之上——分块将多轮 **非合并** 集群（例如 `panic-dos`、`memory-safety`）拆分，而两个 **合并** 集群（`unsafe-boundary`、`concurrency-locking`）永远不会分块：每个工作器各自构建一次共享清单并运行所有其阶段。`recursion-dos` 是每个工作器一轮。返回后，`Read plan.json` 以获取结构化选择——永远不会重新推导过滤或路径。

`--max-passes-per-worker N` 限制每个工作器的轮次计数。规划器确定性地将任何 **非合并** 集群（如果包含超过 `N` 轮次）拆分为 `ceil(K/N)` 个连续分块；每个分块成为自己的 `rust-review-worker` 启动，带有 `-{i}` 后缀的 `cluster_id`（例如 `panic-dos-1`、`panic-dos-2`）。**合并集群（`unsafe-boundary`、`concurrency-locking`）被豁免——永远不会分块，无论轮次计数或覆盖——所以一个工作器构建其共享的 Phase-A 清单一次并运行每个阶段**（合并集群的分块会强制每个分块重建该清单，而工作器在实践中会跳过）。共享提示缓存前缀和 `Cluster prompt:` 路径在分块中字节相同，所以缓存引脚仍然为每个工作器预热。默认值 4 是针对 `manifest.json` 中的重尾集群校准的。一些输出密集的非合并集群声明较小的 `manifest-level` `max_passes_per_worker` 覆盖，以便每个昂贵轮次都有自己的工作器（例如 `recursion-dos`）。传递 `--max-passes-per-worker 0` 以禁用所有分块，包括清单覆盖（每个集群一个工作器）。

### 第 5 步：创建账本任务（编排器内部）

**入口：** `${output_dir}/plan.json` 存在；`M = plan.workers.length`。**出口：** 创建 `cluster_task_ids[]`（与 `plan.workers` 1:1 对应），全部为 `pending`。

任务账本仅是 **编排器账本**（TUI 可见性 + 第 7 步重试跟踪）——工作器从不读取或写入它。每个工作器一个 `TaskCreate`，用 `kind="cluster"`、`worker_n`、`cluster_id`、`spawn_prompt_path`、`pass_prefixes`、`attempt=1` 填充 `metadata`——所有值都从 `plan.workers[i]` 原封不动地复制。在 `plan.workers` 顺序中跟踪 `cluster_task_ids[]`。

### 第 6 步：启动工作器（可选先缓存引脚，然后 M 并行）

**入口：** `cluster_task_ids[]` 已填充；每个工作器的启动提示文件存在于 `${output_dir}/worker-prompts/worker-N.txt`。**出口：** 所有 M 个 `Agent` 调用——跨所有波次——都已返回（并行启动块完成）。

#### 第 6a 步：缓存引脚（由 `plan.run.cache_primer` 控制）

从冷启动开始的并行批处理无法共享缓存（所有 M 请求同时分发，没有请求完成）。为了预热前缀，先启动一个小的引脚——**前台**（后台启动不会与后续前台启动共享缓存）。

如果 `plan.run.cache_primer == true`，`build_run_plan.py` 已写入 `${output_dir}/worker-prompts/cache-primer.txt`。在它自己的助手消息中启动它：`Read` 该文件，原封不动地作为 `Agent` `prompt` 传递，`subagent_type=rust-review:rust-review-worker`、`model=${worker_model}`、`description="Rust review cache primer"`，无 `run_in_background`。脚本将 `<context>` 块中的前缀字节与 `worker-1.txt` 完全相同——这种字节身份是并行工作器获得缓存命中的关键。引脚尾部包含 `Cache primer: true`，工作器系统提示将其视为一级模式，并在一条文本响应中返回 `worker-PRIMER abort: cache primer (no analysis performed)`，无工具调用。忽略中止行——第 7 步会忽略它（没有 `worker-N` id）。

前台启动已序列化——不需要 `sleep` 才能进入第 6b 步。如果 `plan.run.cache_primer == false`，则完全跳过第 6a 步。

#### 第 6b 步：并行启动 M 个真实工作器（每波 ≤16 个消息）

> **停止——在编写启动消息之前阅读此内容。**
>
> 工作器必须以 **前台** 启动（没有 `run_in_background` 字段，或 `run_in_background=false`）。
> “并行”在这里意味着 *一条助手消息包含该波次的 `Agent` 调用*——这已经使它们并行运行。（对于大的 `M`，分成连续的波次，每波 ≤16 个调用，每波一条消息——见下文“必需的启动形状”）。**后台启动不是并行化这个技能的方式。**
>
> 后台启动破坏了第 6a 步的引脚缓存：每个工作器在其第一次轮次上支付完整的缓存创建成本（`cache_read_input_tokens=0`），并且引脚的 ~15 K token 被重复浪费 M 次。两次真实运行都有这个症状——每个工作器开始时 `first_cr=0`。
>
> 在发送启动消息之前，审核你的草稿：每个 `Agent` 调用必须**没有** `run_in_background` 键。如果你写了 `run_in_background=true`，请删除它。

**必需的启动形状：** 发送一条助手消息，其中包含该波次的 `Agent` 工具调用——这条消息会并行运行它们。顺序启动（每条 `Agent` 调用一条消息）会序列化审查，这也是错误的，但这个失败是响亮的（时间）；后台启动的失败是沉默的（成本）。

**当 `M` 超过每消息限制时的波次。** 启动器限制它将从单条助手消息中分发的 `Agent` 调用数量（观察：Claude Code 中约 ~20 个——一个真实的 25 工作器运行默默地只保留了前 20 个，不得不在第二条消息中启动其余 5 个）。所以当 `M > 16` 时，**提前规划波次**：将工作器分成连续的波次，每个波次 **≤16 个 `Agent` 调用**，每个波次自己的单条助手消息。规则：

- **波次内：** 所有 `Agent` 调用在**一条**消息中，**前台**（无 `run_in_background`）——与单波次运行形状相同。
- **波次间：** 波次 _k+1_ 是**单独**的消息，只能在该波次 _k_ 的 `Agent` 调用全部返回（工具使用消息结束回合）后发送。因此，波次彼此**序列化**——这是正确的且响亮的；不要尝试重叠它们。
- **永远**不要使用 `run_in_background=true` 来将更多工作器放入一条消息。更多 *波次*，永远不要后台——后台会破坏引脚缓存（见“停止”框）并且是这个技能要防止的主要错误。
- **跨波次缓存：** 引脚前缀的 ~5 分钟缓存 TTL 在每次命中时刷新，所以连续波次会继续命中它（25 工作器运行确认第二波 `cache_read≈14 K`）。如果后续波次将在超过 ~5 分钟后开始（非常大的 `M` 或工作器缓慢），则先在自己的消息中重新启动第 6a 步的引脚，以在波次之前重新预热前缀。
- **平衡波次**（例如 `M=25` → 13+12，而不是 20+5）以避免波次紧贴上限，并且最后一个波次不是微小的拖尾者。
- 每个波次返回后，继续第 7 步，并使用**完整的** M 工作器结果集。

对于每个工作器 `N ∈ [1..M]`（在其分配的波次中）：

1. `Read: ${output_dir}/worker-prompts/worker-N.txt`
2. 将文件内容**原封不动**作为 `Agent` 工具的 `prompt` 参数传递：

| 参数 | 值 |
|-------|-------|
| `subagent_type` | `rust-review:rust-review-worker` |
| `model` | `${worker_model}`（haiku / sonnet / opus） |
| `description` | `Rust review worker N` |
| `prompt` | `worker-N.txt` 的完整文本（无修改） |
| `run_in_background` | **字段必须省略，或设置为 `false`。** 永远不要 `true`。见上文的前台启动警告。 |

启动提示是唯一的权威。原封不动地传递它——每个字段都是工作器自我检查所必需的；任何偏差都会触发 `worker-N abort: 启动提示格式错误`。

**要拒绝的反模式：**

- **传递 `run_in_background=true`**（见上文的警告）。
- **当 `M` 较大时将超过 ~16 个 `Agent` 调用压缩到一条消息中**——启动器会沉默地只保留前 ~20 个并丢弃其余的。使用平衡的波次，≤16，永远不要后台启动，以覆盖所有 M。
- 手动输入启动提示而不是读取 `worker-N.txt`。
- 插入与任务相关的指令（“第一次调用 TaskList”、“分配任务 ID: <N>”）。工作器没有任务工具。
- 在传递之前编辑渲染的提示（修剪“冗余”字段，合并轮次列表）。

### 第 7 步：等待工作器并分类结果

**入口：** 所有 M 个第 6 步的 `Agent` 调用都已返回。**出口：** 每个集群要么成功，要么重试到上限；写入 `${output_dir}/findings-index.txt`。

第 6 步的 `Agent` 调用会阻塞，直到每个工作器返回。检查每个工作器的返回文本，并按顺序应用此分类器——第一个匹配者胜出：

| # | 匹配（在返回文本中） | 结果 | 动作 |
|---|---|---|---|
| 1 | `worker-N complete:` | **临时成功** | 解析 `wrote N finding files` 计数，然后在 `TaskUpdate` 到 `completed` 之前运行下面的工件验证器。 |
| 2 | `abort: spawn prompt malformed`、`abort: pre-work budget exceeded` 或 `abort: TaskList unavailable`（遗留） | **不可重试的编排器错误** | 停止运行，显示中止 + 启动提示路径。重新运行相同的提示会重复失败——预工作预算耗尽意味着工作器无法通过其自我检查，重试无法修复。 |
| 3 | 其他 `worker-N abort:` | **可重试** | 标记 `pending`，设置 `metadata.abort_reason`、`needs_respawn=true`，递增 `attempt`。 |
| 4 | `Agent` 出错或没有 `complete:`/`abort:` 令牌 | **可重试** | 与 #3 相同（临时的工作器崩溃）。 |

如果任何不可重试，停止。否则，**在重新启动之前，清除每个可重试工作器在磁盘上的前缀空间**——第 7 步索引是从磁盘构建的，所以崩溃尝试的较高 ID 拖尾者（工作器从未重新发出的文件）否则会被复活到报告中。遍历工作器的实际 `pass_prefixes`（来自其任务 `metadata`），将每个真实前缀替换为 `${pfx}`——不要用字面值 `PREFIX` 运行命令：

```bash
# zsh-safe: `find … -delete` 永远不会在无匹配时中止（`rm PREFIX-*.md` 通配符会）。。
# 用工作器的实际空格分隔的 pass_prefixes 替换 `PREFIX1 PREFIX2`。
for pfx in PREFIX1 PREFIX2; do
  find "${output_dir}/findings" -maxdepth 1 -type f -name "${pfx}-*.md" -delete
done
```

然后并行重新启动每个 `pending` 可重试的 `attempt <= 2`（限制 = 每个集群 2 次尝试）。`attempt` 刚刚在第一次失败时递增到 `2`，所以守卫必须允许 `2` 以允许单个重试——`attempt < 2` 会阻止每个重试。第二次失败递增到 `3`，这会失败 `<= 2` 并结束重试。替换工作器为每个前缀重用确定的发现 ID，所以清除的前缀空间加上新的写入会产生一致的碎片 / 覆盖 / 磁盘集。

#### 检查点 + 写入索引

对于每个临时的 `complete:` 集群，在将其任务标记为完成之前，验证工作器拥有的碎片、覆盖文件、覆盖行、文件 ID 和声明的发现计数与 `plan.json`。可以运行每个完成工作器的一条命令，或在一个命令中验证多个工作器。以下两种声明的计数形式都有效；不要在不使用 `--claimed-count` 标志分组 `worker-N=N` 值或重复标志的情况下传递裸 `worker-N=N` 值。

```bash
uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/validate_artifacts.py" "${output_dir}/plan.json" \
  --worker worker-N --claimed-count worker-N=<claimed_count_from_complete_line>
```

```bash
uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/validate_artifacts.py" "${output_dir}/plan.json" \
  --worker worker-1 --worker worker-2 \
  --claimed-count worker-1=0 worker-2=3
```

```bash
uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/validate_artifacts.py" "${output_dir}/plan.json" \
  --worker worker-1 --worker worker-2 \
  --claimed-count worker-1=0 --claimed-count worker-2=3
```

如果验证非零退出，将其完成视为格式错误并重试（分类器行 #4）：标记任务 `pending`，将验证器输出存储在 `metadata.abort_reason` 中，设置 `needs_respawn=true`，并递增 `attempt`。缺少 `findings-index.d/worker-N.txt`、缺少 `coverage/worker-N.md`、缺少覆盖行、无效的 `skipped:` 行、文件 ID 缺失于碎片或磁盘，以及声明的计数不匹配都是格式错误的完成。重试上限后，将集群任务保留为未完成，并在 `run-summary.md` 和最终响应中显示验证器输出。只有验证干净的临时完成才能 `TaskUpdate` 到 `completed`。

然后构建索引。规范索引是磁盘上**实际存在的发现文件**集合，而不是碎片联合——从磁盘构建可以保证即使没有匹配的碎片条目（工作器在它的 `Write` 和其碎片追加之间崩溃，或者工作器提示警告的单前缀空碎片陷阱）的发现仍然会被 dedup → fp-judge → REPORT/SARIF 而不是沉默地消失，并且每个索引条目都解析到一个真实文件：

```bash
# 标准索引 = 磁盘上每个查找文件。`find` 在无匹配时永不失败
# （空的查找/ 将产生一个空的索引 — 无歧义的“零查找”信号）。`sort -u` 合并 Phase-7 重试重复项：替换工作进程重用确定性 ID，因此相同路径只出现一次。
find "${output_dir}/findings" -maxdepth 1 -type f -name '*.md' 2>/dev/null \
  | sort -u > "${output_dir}/findings-index.txt"

# 与每个工作进程的碎片进行核对：磁盘上的任何路径但在 NO 碎片中都是孤儿，其工作进程未能记录它。它已经在上面的索引中（因此它不会被丢弃）— 打印它以便暴露账目差距。非致命。
if [ -d "${output_dir}/findings-index.d" ]; then
  # 通过 basename（查找 ID 是唯一的）进行核对，因此工作进程 `find` 和这个之间的路径格式差异
  # （尾随斜杠，/var↔/private/var）不能制造假孤儿。磁盘上的任何 basename 但在无碎片中都是孤儿，
  # 其工作进程未能记录它。
  comm -13 \
    <(find "${output_dir}/findings-index.d" -maxdepth 1 -type f -name 'worker-*.txt' -exec awk 1 {} + 2>/dev/null | sed 's#.*/##; /^[[:space:]]*$/d' | sort -u) \
    <(find "${output_dir}/findings" -maxdepth 1 -type f -name '*.md' 2>/dev/null | sed 's#.*/##' | sort -u)
fi
```

碎片仍然保留为每个工作进程的审计追踪（`validate_artifacts.py` 检查它们）和去重判断器的崩溃恢复回退，但它们不再控制什么到达管道。对于 reconcile 打印的每个孤儿 basename，通过 `plan.json` 将其 `<PREFIX>` 映射到拥有它的工作进程，并在 `run-summary.md` 中注明该工作进程的碎片不完整 — 查找已经在索引中（因此它没有被丢失），但账目差距应该可见。仍然核对索引行数与 `wrote N` 工作进程声明的总和；记录不匹配但不要中止。

任务更新和索引创建后，运行 `TaskList` 并使用 `${output_dir}/run-summary.md` 写入：

- 解析参数（`threat_model`，`severity_filter`，`finding_scope_root`，`context_roots`，能力标志 `has_unsafe`/`has_ffi`/`has_concurrency`/`has_async`，Cargo 软件包清单状态）
- 工作进程结果表（`worker_n`，`cluster_id`，声明的查找数量，碎片行数，覆盖率文件路径（`coverage/worker-{N}.md`），任务状态，重试/中止状态）
- `findings-index.txt` 行数和与工作进程声明的任何不匹配
- 一旦 Phase 8 完成或跳过/失败的原因，判断器状态

如果任何 Phase-5 簇任务不是 `completed` — **或者**任何工作进程返回了 `complete:` 行并带有 `truncated at hard cap` 标记（它在搜索每个通过之前达到工具调用上限；它的覆盖率文件将显示一个或多个 `cleared (NOT SEARCHED — truncated at hard cap)` 行）— 在 `run-summary.md` 和最终响应中突出显示它。硬上限截断的工作进程在账目目的上被标记为 `completed` 但是一个 **部分** 结果：不要让这个 `completed` 状态隐藏在成功报告后面的不完整覆盖率。

**即使零查找也要始终运行 Phase 8** — 两个判断器在空索引上都会短路：去重判断器写入最小的无操作 `dedup-summary.md`，fp 判断器写入空的 `REPORT.md`/`REPORT.sarif`，以便 SARIF 消费者获得一个稳定的工件集。

### Phase 8: 判断器管道（顺序，去重 → fp+严重性）

**入口：** `findings-index.txt` 存在。**出口：** 去重判断器和 fp 判断器已返回；`dedup-summary.md`，`fp-summary.md`，`REPORT.md` 和理想的 `REPORT.sarif` 已写入。

每个判断器的完整协议是其系统提示（`agents/rust-review-{dedup,fp}-judge.md`）；启动提示仅传递每次运行变量。**不要**引用 `prompts/internal/judges/` — 这些文件不存在。

> **停止 — 这两个判断器按顺序运行，而不是并行运行。** 与 Phase-6b 工作进程不同（你作为 M `Agent` 调用在 *一条* 消息中启动它们，正是因为那会并发运行），判断器有一个硬数据依赖：fp 判断器必须看到去重判断器写入的 `merged_into` / `also_known_as` 注释，并且它仅跳过已经携带 `merged_into` 的文件。如果你在一个消息中发出两个 `Agent` 调用，它们会并发运行 — fp 判断器在合并注释存在之前读取查找，将每个重复项判断为单独的主要项，并且（因为 `dedup-summary.md` 还不存在）触发它的“去重未运行”回退，产生一个膨胀的、重复的 `REPORT.md`/SARIF。
>
> 在它自己的 **单独** 助手消息中启动去重判断器，等待它的 `dedup-judge complete:`（或 `abort:`）返回，**然后**在 **单独** 的消息中启动 fp 判断器。在编写 fp 判断器启动之前，确认去重已完成 — `Bash: test -f ${output_dir}/dedup-summary.md` 必须成功（或者你看到了去重的 `complete:` 标记）。**永远不要将两个判断器 `Agent` 调用在同一个消息中。**

1. **第一个消息** — `Agent(subagent_type="rust-review:rust-review-dedup-judge", description="去重判断器", prompt=f"output_dir: {output_dir}")`。等待它的返回并分类它（下面）后再继续。
2. **然后，在一个单独的消息中** — `Agent(subagent_type="rust-review:rust-review-fp-judge", description="FP + 严重性判断器", prompt=f"output_dir: {output_dir}\nsarif_generator_path: {sarif_generator_path}")` — 解析 `sarif_generator_path` 到 `${RUST_REVIEW_PLUGIN_ROOT}/scripts/generate_sarif.py`。

**判断器失败处理。** 与 Phase 7 的分类器形状相同，应用于判断器返回文本：

- `… complete:` → **成功。**
- `… abort:` → **对于该判断器不可重试。** 打印中止行加上 `ls -l ${output_dir}/findings-index.txt`，然后 **仍然运行 Phase 8b**（它的 SARIF + `REPORT.md` 安全网保证即使判断器中止时工件集 — 见 Phase 8b 的“fp 判断器返回，或运行中止早期”入口），然后停止不启动更多判断器。“停止”意味着不要继续判断器管道 — 它不 **意味着** 跳过 Phase 8b。
- 没有 `complete:`（帮助消息 / 错误 / 问题）→ **可重试一次。** `SendMessage(to=<agentId>, …)` 而不是重新启动（代理已经支付了协议解析成本）。包括来自 `findings-index.txt` 的明确查找路径。如果第二次尝试仍然失败，显示文本记录并继续到 Phase 8b。

### Phase 8b: 报告安全网（SARIF + REPORT.md）

**入口：** fp 判断器返回，或运行中止早期。**出口：** `${output_dir}/REPORT.sarif` 和 `${output_dir}/REPORT.md` 都存在。

```bash
test -d "${output_dir}/findings" && uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/generate_sarif.py" "${output_dir}"
```

无论何时 `findings/` 存在，都无条件运行 SARIF 生成器 — 它是幂等的（完全覆盖），对零生存者运行发出 `results: []`，并处理部分运行（没有 `fp_verdict` 的查找作为 `LIKELY_TP` 发出，**由于它们的严重性从未被判断器验证，因此免于 `severity_filter`**，并标记为 `unjudged: true` / `severity_validated: false` 并带有 `[UNVALIDATED SEVERITY — not judged]` 消息前缀 — 因此一个推断的严重性猜测永远不会在 `medium`/`high` 过滤下无声地丢弃它们）。始终覆盖可以防止 fp 判断器在写入中途崩溃并在磁盘上留下损坏的 `REPORT.sarif`。

如果生成器在 stdout 上打印一条 `WARNING: skipped N …` 行（它还记录 `invocations[].properties.skipped_findings` 在 SARIF 中，并为每个丢弃的文件记录一个 `warning` 通知），一个或多个查找文件不可读或没有可解析的前置内容，并且被 **排除在报告之外**。这是一个丢失的结果 — 在 `run-summary.md` 和最终响应中突出显示其数量和路径，与未 `completed` 的簇任务相同的方式。不要让干净的 SARIF 隐藏损失。

然后保证 `REPORT.md` 存在。与 SARIF（机械）不同，`REPORT.md` 是 fp 判断器的 **精选** 工件，因此**不要**覆盖一个由判断器写入的工件。 （fp 判断器使用 `Bash` 套接字写入 `REPORT.md`，而不是 `Write` 工具，因为 harness 阻止了 `Write` 工具用于子代理报告文件 — 不要“修复”判断器通过重新指定 `Write`。协调器是主代理并且**不**受此阻塞，因此它自己的 `Write` 下面可以工作。）检查它，如果它丢失（判断器崩溃，即使它的 `Bash`-套接字写入失败，或者它将报告作为聊天文本而不是写入文件返回），**协调器自己写入 `REPORT.md`** 而不是让运行失败：

- 如果 fp 判断器在其文本记录中返回了报告正文，`Write` 该文本逐字到 `${output_dir}/REPORT.md`。
- 否则，从磁盘上的查找合成它：取生存的主要项（`fp_verdict ∈ {TRUE_POSITIVE, LIKELY_TP}`，没有 `merged_into`；如果判断器从未运行，将没有 `fp_verdict` 的查找视为生存者）列在 `findings-index.txt` 中，应用 `context.md` 中的 `severity_filter` **仅对已判断的生存者** — 未判断的查找（没有 `fp_verdict`）无论过滤如何都包含在内，并在带有 `[UNVALIDATED SEVERITY — not judged]` 标签的 `Unvalidated (severity not judged)` 部分下渲染，以模仿 SARIF 行为，以便严格的过滤永远不会无声地丢弃它们 — 并 `Write` 一个 `REPORT.md` 模仿 fp 判断器模板 — YAML 前置内容（`stage: final-report`，`threat_model`，`severity_filter`，`total_primaries`，`reported_findings`），一个严重性分布表，然后每个报告查找按严重性分组的一个部分（嵌入 CRITICAL/HIGH 的描述 / 代码 / 数据流 / 影响 / 建议正文；对 MEDIUM/LOW 引用查找文件）。

无论如何，在 `${output_dir}/run-summary.md` 中注明 `REPORT.md` 是由协调器合成的（不是判断器编写的）。如果 `${output_dir}/findings/` 不存在（Phase 2 失败），则跳过 SARIF 生成器和此检查。在此阶段后，更新 `${output_dir}/run-summary.md` 以包含判断器 / SARIF / 报告状态。

### Phase 9: 返回报告

**入口：** Phase 8b 完成。**出口：** [成功标准](#success-criteria) 中的每个项目都验证为真；`REPORT.md` 返回给调用者。

在编写响应之前，走 [成功标准](#success-criteria) 检查清单（如下）并确认每个项目与磁盘工件（`TaskList` 用于簇任务，`ls`/`Read` 用于文件）的匹配。如果任何标准失败，在响应中突出显示失败 — 不要让部分运行在成功报告后面隐藏。

然后 `Read ${output_dir}/REPORT.md` 并将其内容返回给调用者。附加一个指向 `findings/`、`findings-index.txt`、`run-summary.md`、`dedup-summary.md`、`fp-summary.md`、`REPORT.md`、`REPORT.sarif` 的工件列表。

---

## 查找文件前置内容 — 三阶段

权威模式：`agents/rust-review-worker.md`（“查找文件格式”）。三阶段写入：

1. **工作进程** — 基本字段（`id`，`bug_class`，`title`，`location`，`function`，`confidence`，`worker`）+ 七个正文部分。
2. **去重判断器** — 在重复项上添加 `merged_into`，或在吸收了主要项上添加 `also_known_as` + `locations`。
3. **FP+严重性判断器** — 在每个主要项上添加 `fp_verdict` + `fp_rationale`；在生存者（`TRUE_POSITIVE`/`LIKELY_TP`）上也添加 `severity`，`attack_vector`，`exploitability`，`severity_rationale`。

## 错误类别 / 簇

权威：`prompts/clusters/manifest.json`。37 个错误类别存在于 `always`-门控簇中（因此簇始终运行）；其中 35 个始终触发，而 2 个 — `adversarial-trait`（TRAITADV）和 `closure-panic`（CLOSUREPANIC）在 `logic-correctness` 中 — 额外携带 `requires: has_unsafe`，因此它们仅在 `has_unsafe=true` 时触发。所有簇中 69 个错误类别，当每个条件门控都启用时。`memory-safety` 簇的门控在 `has_unsafe` 上（它所有的错误类别都需要 `unsafe`）；PATHJOIN 和 TOCTOU 通过 `input-os-safety` 在 `has_fs_io` 后门控，而 PACKEDREF 存在于条件 `layout-safety` 簇（`has_packed_repr`）；PTREXPOSE 通过 `info-disclosure` 簇始终开启。`unsafe-boundary` 和 `concurrency-locking` 是完全整合的（它们的子提示在运行时不会重新读取）。

---

## 成功标准

阶段退出已经涵盖了大部分内容；协调器可见的最终状态是：

- 每个 Phase-5 簇任务都是 `completed`（通过 `TaskList` 验证）。
- `${output_dir}/run-summary.md` 存在并记录了解析的范围/上下文、Cargo 软件包清单探测结果、工作进程声明与索引计数、任务状态和判断器/SARIF 状态。
- 每个主要查找（没有 `merged_into`）都有 `fp_verdict` + `fp_rationale`；每个生存者（`TRUE_POSITIVE`/`LIKELY_TP`）还都有 `severity`，`attack_vector`，`exploitability`，`severity_rationale`。
- `REPORT.md` 存在，按 `severity_filter` 严重性过滤（Phase 8b 安全网保证即使 fp 判断器未能写入它）。
- `REPORT.sarif` 存在（Phase 8b 安全网保证）。
