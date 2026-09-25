# Rust 安全审查

在主对话中运行（通过 `/rust-review:rust-review` 调用）。协调器拥有 `Task*` 账本作为重试的簿记；工作进程和裁判没有任务工具。工作进程和裁判是命名的插件子代理（`rust-review:rust-review-worker`, `rust-review:rust-review-dedup-judge`, `rust-review:rust-review-fp-judge`）；工具集在 `plugins/rust-review/agents/*.md` 中声明。发现通过共享输出目录中的 Markdown with YAML 文件进行交换。

## 何时使用

Rust 应用/库安全审查：安全/不安全边界审计、`unsafe` 块中的内存安全、并发风险、服务器上的恐慌诱导拒绝服务、FFI 安全性、异步运行时错误。

## 何时不使用

- 纯 C / 纯 C++ 代码库 — 使用 `c-review`。
- 智能合约（Solana 程序 / NEAR 合约 / Ink!）— 使用 `solana-vulnerability-scanner` 或特定合约技能。
- 没有用户空间分配器的内核模式 Rust 驱动程序 — 覆盖不完整；仅标记为建议。
- 密钥/内存卫生（清零、`Zeroize`/`ZeroizeOnDrop`/`secrecy` 使用、残留的栈/堆副本）— 使用 `zeroize-audit` 技能；`rust-review` 不涵盖内存清零。

## 子代理

| 子代理类型 | 目的 | 工具集 |
|---|---|---|
| `rust-review:rust-review-worker` | 运行分配的集群，写入发现 | 读取、写入、编辑、Bash |
| `rust-review:rust-review-dedup-judge` | 合并重复项（运行 **首先**） | 读取、写入、编辑、Glob |
| `rust-review:rust-review-fp-judge` | FP + 严重性 + 最终报告（运行 **其次**） | 读取、写入、编辑、Bash |

工具来自每个代理的 frontmatter 在启动时。协调器的 `Task*`/`Agent`/`Bash`/等来自此技能的 `allowed-tools`。**搜索工具 / `Bash` 交互：** 在当前 Claude 代码中，授予 `Bash` 的代理**不**也授予专门的 `Glob` **或 `Grep`** 工具（调用返回 `No such tool available`；框架期望通过 `Bash` 进行 `find`/`grep`/`rg` 而不是 `Bash`）。因此，只有 dedup-judge — 唯一一个不持有 **`Bash`** 的代理 — 使用 `Glob`；工作进程、fp-judge 和协调器通过 `Read` / `Bash` `find` / `rg` / `grep` / `test -f` 解析和搜索路径。因为集群/查找提示种子使用 ripgrep 正则表达式语法（`\s`, `\d`, `\b`），`Bash` 持有代理必须使用 **`rg`** 运行它们。如果 `rg` 未安装，其调用会大声失败（`command not found`）— 回退到 `grep -E` 使用 POSIX 类别（`\s`→`[[:space:]]`, `\d`→`[[:digit:]]`, 移除 `\b`），永远不会是原始的 `grep`，其 *静默* 空白变为一个坏的 `cleared`。**不要**将 `Glob`/`Grep` 重新引入到持有 `Bash` 的代理协议中。

---

## 架构

```
coordinator: write context.md → build_run_plan.py → TaskCreate × M
          → spawn primer (foreground) → spawn M workers (parallel)
          → classify Phase-7 outcomes + write findings-index.txt
          → dedup-judge → fp-judge → report safety net (SARIF + REPORT.md) → return REPORT.md
```

输出目录包含：`context.md`, `plan.json`, `worker-prompts/`, `findings/`, `findings-index.d/`（每个工作进程的碎片），`findings-index.txt`, `coverage/`（每个工作进程的覆盖门文件），`run-summary.md`, `dedup-summary.md`, `fp-summary.md`, `REPORT.md`, `REPORT.sarif`.

**路径约定：** 每个后续阶段都通过 `${RUST_REVIEW_PLUGIN_ROOT}/scripts/*.py` 执行外壳命令，因此首先解析该变量到包含 `prompts/clusters/unsafe-boundary.md`（以及 `scripts/build_run_plan.py`）的插件目录。按顺序尝试，第一个匹配的获胜：

1. **原生 Claude 代码** — `${CLAUDE_PLUGIN_ROOT}`，如果 `Bash: ls "${CLAUDE_PLUGIN_ROOT}/prompts/clusters/unsafe-boundary.md"` 解析则接受。
2. **Codex** — `${CODEX_PLUGIN_ROOT}`（如果该变量存在且解析了标记，则按相同方式设置）。
3. **回退搜索** — 覆盖 Codex 安装在 `~/.codex` 下，Claude 安装在 `~/.claude` 下，以及本地检出/仓库运行：`Bash: find ~/.claude ~/.codex . -path '*/plugins/rust-review/prompts/clusters/unsafe-boundary.md' -print -quit 2>/dev/null`。取匹配项并删除尾部的 `/prompts/clusters/unsafe-boundary.md` 以获取根（家目录在 `.` 之前搜索，所以安装的副本优先于审计仓库中的任何 vendored 复本）。

设置 `RUST_REVIEW_PLUGIN_ROOT` 为解析的根。如果所有三个都失败，**中止**并命名搜索的根 — 不要在 Phase 4 使用空变量（`uv run --no-project "${RUST_REVIEW_PLUGIN_ROOT}/scripts/..."` 调用将失败，并出现令人困惑的路径错误）。

**范围约定：** 在整个运行过程中保持两个范围分离：

- `finding_scope_root` — 用户请求的审计子树。工作进程只能提交其漏洞位置位于此子树内的发现。
- `context_roots` — 只读仓库根/文件，工作进程和裁判可以检查以验证可达性、调用者、包装器、构建标志、缓解措施和威胁模型详细信息。默认为 `.`，除非用户明确禁止更广泛的上下文。允许读取 `finding_scope_root` 外部的上下文，但禁止在此处提交发现。

---

## 拒绝的理由

- **"`unsafe` 很少使用，所以手动跳过内存安全集群。"** 不要编辑集群列表 — 准确设置 Phase 1 中的 `has_unsafe`，让 `build_run_plan.py` 决定。每个内存安全错误类别（UAF、double-free、未初始化读取、`Vec::set_len`、联合体 UB）都需要 `unsafe`，所以当 `has_unsafe=true` 时，规划器运行整个 `memory-safety` 集群，当 `false` 时正确省略它 — 没有运行它 anyway。**unsafe-boundary** 集群不同：它没有 `requires` 并始终运行（合并；其安全文档和 `repr(C)` 卫生适用于 FFI 声明，即使没有可见的 `unsafe { }` 块）。
- **"编译器已经捕获了它。"** 借助借用检查器证明安全代码数据竞争的缺失；它不能证明关于不安全块、恐慌可达性、ABBA 死锁、原子加载/存储顺序或 FFI ABI 不匹配。
- **"`unwrap()` 是安全的，如果它是 `// SAFETY: 文档中不可出错"** `// SAFETY:` 文档中记录了 `unsafe` 操作，而不是不可出错的主张。在文档中记录为不可出错输入上的 `unwrap()` 如果文档是错误的，仍然有风险 — 提交为低严重性，让 FP 裁判决定。
- **"`has_unsafe=false` 所以跳过运行。"** 纯安全 Rust 的包仍然有恐慌拒绝服务、原子竞争、丢弃恐慌和特征实现风险。运行始终开启的集群。
- **"后台启动并行化工作进程。"** 它们不会 — `Agent` 调用在单个助手消息中已经运行并发。`run_in_background=true` 会禁用 Phase 6a 的提示缓存，所以每个工作进程都支付完整的缓存创建 (`cache_read_input_tokens=0`)，而 ~15 K 令牌的提示被浪费 M 次。默认：从工作进程启动中省略 `run_in_background`。

## 找到文件的前matter — 三个阶段

权威模式：`agents/rust-review-worker.md`（“找到文件格式”）。三阶段写入：

1. **工作进程** — 基本字段（`id`, `bug_class`, `title`, `location`, `function`, `confidence`, `worker`) + 七个正文部分。
2. **Dedup-judge** — 在重复项上添加 `merged_into`，或在吸收的原始项上添加 `also_known_as` + `locations`。
3. **FP+严重性裁判** — 在每个原始项上添加 `fp_verdict` + `fp_rationale`；对于幸存者（`TRUE_POSITIVE`/`LIKELY_TP`）还添加 `severity`, `attack_vector`, `exploitability`, `severity_rationale`。

## 错误类别 / 集群

权威：`prompts/clusters/manifest.json`。37 个错误类别存在于始终开启的集群中（所以集群始终运行）；其中 35 个始终触发，而 2 个 — `adversarial-trait` (TRAITADV) 和 `closure-panic` (CLOSUREPANIC) 在 `logic-correctness` 中额外携带 `requires: has_unsafe`，所以它们仅在 `has_unsafe=true` 时触发。当每个条件门都启用时，所有集群中的 69 个错误类别。`memory-safety` 集群由 `has_unsafe` 触发（它所有的错误类别都需要 `unsafe`）；PATHJOIN 和 TOCTOU 由 `has_fs_io` 通过 `input-os-safety` 隔离，而 PACKEDREF 存在于条件 `layout-safety` 集群中（`has_packed_repr`）；PTREXPOSE 始终通过 `info-disclosure` 集群保持开启。`unsafe-boundary` 和 `concurrency-locking` 是完全合并的（它们的子提示在运行时不会重新读取）。

---

## 成功标准

阶段退出已经涵盖了其中大部分内容；协调器可见的最终状态是：

- 每个 Phase-5 集群任务都是 `completed`（通过 `TaskList` 验证）。
- `${output_dir}/run-summary.md` 存在并记录解析的范围/上下文、Cargo 配置文件探测结果、工作进程声明的发现数与索引计数、任务状态以及裁判/SARIF 状态。
- 每个原始发现（没有 `merged_into`) 都有 `fp_verdict` + `fp_rationale`；每个幸存者 (`TRUE_POSITIVE`/`LIKELY_TP`) 还具有 `severity`, `attack_vector`, `exploitability`, `severity_rationale`。
- `REPORT.md` 存在，按 `severity_filter` 进行过滤（Phase 8b 安全网保证了即使 fp-judge 无法写入它也是如此）。
- `REPORT.sarif` 存在（Phase 8b 安全网保证了这一点）。
