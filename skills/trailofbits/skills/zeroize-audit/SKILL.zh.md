---
name: zeroize-audit
description: 检测源代码中敏感数据的缺失清零，并识别编译器优化移除的清零操作，结合汇编级分析和控制流验证。用于审计处理秘密、密钥、密码或其他敏感数据的C/C++/Rust代码。
---

# zeroize-audit — Claude 技能

## 使用场景
- 审计加密实现（密钥、种子、nonce、密钥）
- 审查认证系统（密码、令牌、会话数据）
- 分析处理个人身份信息（PII）或敏感凭证的代码
- 验证安全关键代码库中的安全清理
- 调查敏感数据处理中的内存安全

## 不适用场景
- 无安全重点的常规代码审查
- 性能优化（除非与安全擦除相关）
- 与敏感数据无关的重构任务
- 不包含可识别密钥或敏感值的代码

---

## 运行方法

在类似“审计此存储库中留在内存中的密钥”或“检查此 C 库是否实际擦除其密钥”的请求中：

1. **收集输入。** 将请求映射到下表中的输入（完整模式：`{baseDir}/schemas/input.json`）。`path` 是必需的，加上至少一个 `compile_db`（C/C++）或 `cargo_manifest`（Rust）；如果未给出或无法从存储库中派生，则询问用户，因为预检会停止没有其中一个的运行。除非用户另有说明，否则将所有其他字段保留为默认值。
2. **读取编排器提示，`{baseDir}/prompts/task.md`**，将收集到的输入替换为其 `{{placeholder}}` 值。你充当它描述的编排器：它定义了状态恢复、阶段循环、早期终止和错误处理。与它一起读取 `{baseDir}/prompts/system.md` 以获取共享工作目录布局和每个阶段都依赖的代理错误协议。
3. **执行其阶段循环。** 依次运行阶段 0-7。在每个阶段之前，读取该阶段的工作流文件从 `{baseDir}/workflows/phase-{N}-{name}.md` 并遵循其先决条件、说明、状态更新和错误处理部分。每个工作流指定通过 `Task` 生成哪个代理及其参数。尊重每个阶段的跳过条件和任务.md 中的早期终止规则。
4. **返回报告**（阶段 8，内联）：读取 `{workdir}/report/final-report.md` 并将其内容作为技能输出返回。

要恢复中断的运行：如果从先前的上下文中知道 `workdir`，则读取 `{workdir}/orchestrator-state.json` 并从其 `current_phase` 继续而不是从阶段 0 开始（参见任务.md 的恢复部分）。

---

## 目的
检测源代码中敏感数据的缺失清除，并识别因编译器优化（例如，死存储消除）而移除或弱化的清除（例如，使用 LLVM IR/asm 证据。功能包括：
- 汇编级分析用于寄存器溢出和栈保留
- 数据流跟踪用于密钥副本
- 堆分配器安全警告
- 语义 IR 分析用于循环展开和 SSA 形式
- 控制流图分析用于路径覆盖验证
- 运行时验证测试生成

## 范围
- 对目标代码库只读（不会修改审计代码；将分析工件写入临时工作目录）。
- 生成结构化报告（JSON）。
- 需要有效的构建上下文（`compile_commands.json`）和可编译的翻译单元。
- “优化掉”的发现仅允许在具有编译器证据（IR/asm 差异）的情况下。

---

## 输入

有关完整模式，请参阅 `{baseDir}/schemas/input.json`。关键字段：

| 字段 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `path` | 是 | — | 仓库根目录 |
| `compile_db` | 否 | `null` | C/C++ 分析的 `compile_commands.json` 路径。如果未设置 `cargo_manifest` 则必需。 |
| `cargo_manifest` | 否 | `null` | Rust crate 分析的 `Cargo.toml` 路径。如果未设置 `compile_db` 则必需。 |
| `config` | 否 | — | 定义启发式算法和批准擦除的 YAML |
| `opt_levels` | 否 | `["O0","O1","O2"]` | 用于 IR 比较的优化级别。O1 是诊断级别：如果 O1 时擦除消失，则它是简单的 DSE；O2 捕获更激进的消除。 |
| `languages` | 否 | `["c","cpp","rust"]` | 要分析的编程语言 |
| `max_tus` | 否 | `50` | 从编译 DB 处理的翻译单元限制 |
| `mcp_mode` | 否 | `prefer` | `off`、`prefer` 或 `require` — 控制 Serena MCP 使用 |
| `mcp_required_for_advanced` | 否 | `true` | 当 MCP 不可用时，将 `SECRET_COPY`、`MISSING_ON_ERROR_PATH` 和 `NOT_DOMINATING_EXITS` 降级为 `needs_review` |
| `mcp_timeout_ms` | 否 | `10000` | MCP 语义查询的超时预算 |
| `poc_categories` | 否 | 所有 11 个可利用的 | 生成 PoC 的发现类别。C/C++ 发现：支持所有 11 个类别。Rust 发现：仅支持 `MISSING_SOURCE_ZEROIZE`、`SECRET_COPY` 和 `PARTIAL_WIPE`；其他 Rust 类别标记 `poc_supported=false` |
| `poc_output_dir` | 否 | `generated_pocs/` | 生成的 PoC 的输出目录 |
| `enable_asm` | 否 | `true` | 启用汇编生成和分析（步骤 8）；生成 `STACK_RETENTION`、`REGISTER_SPILL`。如果缺少 `emit_asm.sh` 则自动禁用。 |
| `enable_semantic_ir` | 否 | `false` | 启用语义 LLVM IR 分析（步骤 9）；生成 `LOOP_UNROLLED_INCOMPLETE` |
| `enable_cfg` | 否 | `false` | 启用控制流图分析（步骤 10）；生成 `MISSING_ON_ERROR_PATH`、`NOT_DOMINATING_EXITS` |
| `enable_runtime_tests` | 否 | `false` | 启用运行时测试桩生成（步骤 11） |

---

## 先决条件

运行之前，请验证以下内容。每个都有定义的失败模式。

**C/C++ 先决条件：**

| 先决条件 | 缺失时的失败模式 |
|---|---|
| `compile_commands.json` 在 `compile_db` 路径 | 快速失败 — 不继续 |
| `clang` 在 PATH 上 | 快速失败 — IR/ASM 分析不可能 |
| `uvx` 在 PATH 上（用于 Serena） | 如果 `mcp_mode=require`：失败。如果 `mcp_mode=prefer`：继续而无需 MCP；根据置信度门控规则降级受影响的发现。 |
| `{baseDir}/tools/extract_compile_flags.py` | 快速失败 — 无法提取每个 TU 的标志 |
| `{baseDir}/tools/emit_ir.sh` | 快速失败 — IR 分析不可能 |
| `{baseDir}/tools/emit_asm.sh` | 警告并跳过汇编发现（STACK_RETENTION、REGISTER_SPILL） |
| `{baseDir}/tools/mcp/check_mcp.sh` | 警告并视为 MCP 不可用 |
| `{baseDir}/tools/mcp/normalize_mcp_evidence.py` | 警告并使用原始 MCP 输出 |

**Rust 先决条件：**

| 先决条件 | 缺失时的失败模式 |
|---|---|
| `Cargo.toml` 在 `cargo_manifest` 路径 | 快速失败 — 不继续 |
| `cargo check` 通过 | 快速失败 — crate 必须可构建 |
| `cargo +nightly` 在 PATH 上 | 快速失败 — 需要 nightly 才能生成 MIR 和 LLVM IR |
| `uv` 在 PATH 上 | 快速失败 — 需要运行 Python 分析脚本 |
| `{baseDir}/tools/validate_rust_toolchain.sh` | 警告 — 手动运行预检。检查所有工具、脚本、nightly，以及可选的 `cargo check`。使用 `--json` 获取机器可读输出，`--manifest` 还要验证 crate 构建情况。 |
| `{baseDir}/tools/emit_rust_mir.sh` | 快速失败 — MIR 分析不可能（`--opt`、`--crate`、`--bin/--lib` 支持；`--out` 可以是文件或目录） |
| `{baseDir}/tools/emit_rust_ir.sh` | 快速失败 — LLVM IR 分析不可能（`--opt` 必需；`--crate`、`--bin/--lib` 支持；`--out` 必须是 `.ll`） |
| `{baseDir}/tools/emit_rust_asm.sh` | 警告并跳过汇编发现（`STACK_RETENTION`、`REGISTER_SPILL`）。支持 `--opt`、`--crate`、`--bin/--lib`、`--target`、`--intel-syntax`；`--out` 可以是 `.s` 文件或目录。 |
| `{baseDir}/tools/diff_rust_mir.sh` | 警告并跳过 MIR 级别优化比较。接受 2+ MIR 文件，规范化、成对差异，并报告第一个优化级别中清除 zeroize/drop-glue 模式的地方。 |
| `{baseDir}/tools/scripts/semantic_audit.py` | 警告并跳过语义源分析 |
| `{baseDir}/tools/scripts/find_dangerous_apis.py` | 警告并跳过危险 API 扫描 |
| `{baseDir}/tools/scripts/check_mir_patterns.py` | 警告并跳过 MIR 分析 |
| `{baseDir}/tools/scripts/check_llvm_patterns.py` | 警告并跳过 LLVM IR 分析 |
| `{baseDir}/tools/scripts/check_rust_asm.py` | 警告并跳过 Rust 汇编分析（`STACK_RETENTION`、`REGISTER_SPILL`、drop-glue 检查）。分派到 `check_rust_asm_x86.py`（生产）或 `check_rust_asm_aarch64.py`（**实验性** — AArch64 发现需要手动验证）。 |
| `{baseDir}/tools/scripts/check_rust_asm_x86.py` | 由 `check_rust_asm.py` 用于 x86-64 分析；如果缺失则警告并跳过 |
| `{baseDir}/tools/scripts/check_rust_asm_aarch64.py` | 由 `check_rust_asm.py` 用于 AArch64 分析（**实验性**）；如果缺失则警告并跳过 |

**通用先决条件：**

| 先决条件 | 缺失时的失败模式 |
|---|---|
| `{baseDir}/tools/generate_poc.py` | 快速失败 — PoC 生成是必需的 |

---

## 批准的擦除 API

以下被视为有效的清除。在 `{baseDir}/configs/` 中配置其他条目。

**C/C++**
- `explicit_bzero`
- `memset_s`
- `SecureZeroMemory`
- `OPENSSL_cleanse`
- `sodium_memzero`
- 易变擦除循环（基于模式；参见 `{baseDir}/configs/default.yaml` 中的 `volatile_wipe_patterns`）
- 在 IR 中：带易变标志的 `llvm.memset`、易变存储或不可消除的擦除调用

**Rust**
- `zeroize::Zeroize` 特性（`zeroize()` 方法）
- `Zeroizing<T>` 包装器（基于丢弃）
- `ZeroizeOnDrop` 宏

---

## 发现功能

发现按所需证据分组。仅尝试所需工具可用的发现。

| 发现 ID | 描述 | 需要 | PoC 支持 |
|---|---|---|---|
| `MISSING_SOURCE_ZEROIZE` | 在源代码中未找到清除 | 仅源代码 | 是（C/C++ + Rust） |
| `PARTIAL_WIPE` | 擦除大小不正确或不完整 | 仅源代码 | 是（C/C++ + Rust） |
| `NOT_ON_ALL_PATHS` | 在某些控制流路径上缺少擦除（启发式） | 仅源代码 | 是（C/C++ 仅） |
| `SECRET_COPY` | 未跟踪密钥副本的敏感数据复制 | 源代码 + MCP 推荐使用 | 是（C/C++ + Rust） |
| `INSECURE_HEAP_ALLOC` | 密钥使用不安全的分配器（malloc vs. secure_malloc） | 仅源代码 | 是（C/C++ 仅） |
| `OPTIMIZED_AWAY_ZEROIZE` | 编译器移除了清除 | 需要 IR 差异（永远不会仅源代码） | 是 |
| `STACK_RETENTION` | 返回后栈帧可能保留密钥 | 汇编需要（C/C++）；LLVM IR `alloca`+`lifetime.end` 证据（Rust）；汇编佐证升级为 `confirmed` | 是（C/C++ 仅） |
| `REGISTER_SPILL` | 密钥从寄存器溢出到栈 | 汇编需要（C/C++）；LLVM IR `load`+调用点证据（Rust）；汇编佐证升级为 `confirmed` | 是（C/C++ 仅） |
| `MISSING_ON_ERROR_PATH` | 错误处理路径缺少清理 | 需要CFG或MCP | 是 |
| `NOT_DOMINATING_EXITS` | 擦除不支配所有退出 | 需要CFG或MCP | 是 |
| `LOOP_UNROLLED_INCOMPLETE` | 展开的循环擦除不完整 | 需要语义 IR | 是 |

---

## 代理架构

分析管道使用 8 个阶段中的 11 个代理，由编排器（`{baseDir}/prompts/task.md`）通过 `Task` 调用。代理将持久发现文件写入共享工作目录（`/tmp/zeroize-audit-{run_id}/`），启用并行执行并防止上下文压力。

| 代理 | 阶段 | 目的 | 输出目录 |
|---|---|---|---|
| `0-preflight` | 阶段 0 | 预检检查（工具、工具链、编译 DB、crate 构建）、配置合并、工作目录创建、TU 枚举 | `{workdir}/` |
| `1-mcp-resolver` | 阶段 1、波浪 1（C/C++ 仅） | 通过 Serena MCP 解析符号、类型和跨文件引用 | `mcp-evidence/` |
| `2-source-analyzer` | 阶段 1、波浪 2a（C/C++ 仅） | 识别敏感对象、检测擦除、验证正确性、数据流/堆 | `source-analysis/` |
| `2b-rust-source-analyzer` | 阶段 1、波浪 2b（Rust 仅，与 2a 并行） | Rustdoc JSON 特性感知分析 + 危险 API grep | `source-analysis/` |
| `3-tu-compiler-analyzer` | 阶段 2、波浪 3（C/C++ 仅，N 并行） | 每个TU的IR差异、汇编、语义 IR、CFG 分析 | `compiler-analysis/{tu_hash}/` |
| `3b-rust-compiler-analyzer` | 阶段 2、波浪 3R（Rust 仅，单个代理） | Crate 级别的 MIR、LLVM IR 和汇编分析 | `rust-compiler-analysis/` |
| `4-report-assembler` | 阶段 3（中间）+ 阶段 6（最终） | 从所有代理收集发现，应用置信度门控；合并 PoC 结果并生成最终报告 | `report/` |
| `5-poc-generator` | 阶段 4 | 编制定制的概念验证程序（C/C++：所有类别；Rust：MISSING_SOURCE_ZEROIZE、SECRET_COPY、PARTIAL_WIPE） | `poc/` |
| `5b-poc-validator` | 阶段 5 | 编译并运行所有 PoC | `poc/` |
| `5c-poc-verifier` | 阶段 5 | 验证每个 PoC 证明其声称的发现 | `poc/` |
| `6-test-generator` | 阶段 7（可选） | 生成运行时验证测试桩 | `tests/` |

编排器一次读取 `{baseDir}/workflows/` 中的一个每个阶段工作流文件，并维护 `orchestrator-state.json` 以在上下文压缩后进行恢复。代理通过文件路径（`config_path`）而不是值接收配置。

### 执行流程

```
阶段 0: 0-preflight 代理 — 预检 + 配置 + 创建工作目录 + 枚举 TUs
           → 写入 orchestrator-state.json、merged-config.yaml、preflight.json
阶段 1: 波浪 1:  1-mcp-resolver              (如果 mcp_mode=off 或 language_mode=rust 则跳过)
         波浪 2a: 2-source-analyzer           (C/C++ 仅；如果未设置 compile_db 则跳过)  ─┐ 并行
         波浪 2b: 2b-rust-source-analyzer     (Rust 仅；如果未设置 cargo_manifest 则跳过) ─┘
阶段 2: 波浪 3:  3-tu-compiler-analyzer x N  (C/C++ 仅；每个 TU 并行)
         波浪 3R: 3b-rust-compiler-analyzer   (Rust 仅；单个 crate 级别代理)
阶段 3: 波浪 4:  4-report-assembler          (mode=interim → findings.json；读取所有代理输出)
阶段 4: 波浪 5:  5-poc-generator             (C/C++：所有类别；Rust：MISSING_SOURCE_ZEROIZE、SECRET_COPY、PARTIAL_WIPE；其他 Rust 类别：poc_supported=false)
阶段 5: PoC 验证和验证
           步骤 1: 5b-poc-validator 代理      (编译并运行所有 PoC)
           步骤 2: 5c-poc-verifier 代理       (验证每个 PoC 证明其声称的发现)
           步骤 3: Orchestrator 通过 AskUserQuestion 向用户展示验证失败
           步骤 4: Orchestrator 将所有结果合并到 poc_final_results.json
阶段 6: 波浪 6: 4-report-assembler           (mode=final → 合并 PoC 结果，final-report.md)
阶段 7: 波浪 7: 6-test-generator             (可选)
阶段 8: Orchestrator — 返回 final-report.md
```

## 跨参考约定

ID 按代理命名空间划分，以防止并行执行时发生冲突：

| 实体 | 模式 | 分配者 |
|---|---|---|
| 敏感对象（C/C++） | `SO-0001`–`SO-4999` | `2-source-analyzer` |
| 敏感对象（Rust） | `SO-5000`–`SO-9999` (Rust 命名空间) | `2b-rust-source-analyzer` |
| 源发现（C/C++） | `F-SRC-NNNN` | `2-source-analyzer` |
| 源发现（Rust） | `F-RUST-SRC-NNNN` | `2b-rust-source-analyzer` |
| IR 发现（C/C++） | `F-IR-{tu_hash}-NNNN` | `3-tu-compiler-analyzer` |
| ASM 发现（C/C++） | `F-ASM-{tu_hash}-NNNN` | `3-tu-compiler-analyzer` |
| CFG 发现 | `F-CFG-{tu_hash}-NNNN` | `3-tu-compiler-analyzer` |
| 语义 IR 发现 | `F-SIR-{tu_hash}-NNNN` | `3-tu-compiler-analyzer` |
| Rust MIR 发现 | `F-RUST-MIR-NNNN` | `3b-rust-compiler-analyzer` |
| Rust LLVM IR 发现 | `F-RUST-IR-NNNN` | `3b-rust-compiler-analyzer` |
| Rust 汇编发现 | `F-RUST-ASM-NNNN` | `3b-rust-compiler-analyzer` |
| 翻译单元 | `TU-{hash}` | Orchestrator |
| 最终发现 | `ZA-NNNN` | `4-report-assembler` |

每个发现 JSON 对象都包括 `related_objects`、`related_findings` 和 `evidence_files` 字段，用于代理之间的交叉参考。

---

## 检测策略

分析分两个阶段运行。有关完整分步指导，请参阅 `{baseDir}/references/detection-strategy.md`。

| 阶段 | 步骤 | 产生的发现 | 所需工具 |
|---|---|---|---|
| 阶段 1（源代码） | 1–6 | `MISSING_SOURCE_ZEROIZE`、`PARTIAL_WIPE`、`NOT_ON_ALL_PATHS`、`SECRET_COPY`、`INSECURE_HEAP_ALLOC` | 源代码 + 编译数据库 |
| 阶段 2（编译器） | 7–12 | `OPTIMIZED_AWAY_ZEROIZE`、`STACK_RETENTION`*、`REGISTER_SPILL`*、`LOOP_UNROLLED_INCOMPLETE`†、`MISSING_ON_ERROR_PATH`‡、`NOT_DOMINATING_EXITS`‡ | `clang`、IR/汇编工具 |

\* 需要 `enable_asm=true`（默认值）
† 需要 `enable_semantic_ir=true`
‡ 需要 `enable_cfg=true`

对于 Rust，`{baseDir}/references/rust-zeroization-patterns.md` 列出了 40 种具名反模式，并按检测各自对应的脚本进行归类：A 部分用于 rustdoc-JSON 语义（`semantic_audit.py`），B 部分用于危险 API（`find_dangerous_apis.py`），C 部分用于 MIR/LLVM IR/汇编（`check_mir_patterns.py`、`check_llvm_patterns.py`、`check_rust_asm.py`）。在处理 Rust 发现、编写修复建议或判断手工标记的模式是否已被覆盖时，请阅读相关部分。

该参考文档的覆盖范围存在两个限制。A–C 部分中的 34 个条目是当前脚本能够检测的内容；D 部分的六个条目是已知但没有脚本覆盖的缺口，因此应将它们视为未审计，而非干净。A 部分和 C 部分也是不完整的——脚本会发出一些没有对应条目的类别——因此，即使某个发现不匹配任何已编目模式，它仍然是一个发现，并携带脚本产生的相应证据。

---

## 输出格式

每次运行产生两种输出：

1. **`final-report.md`** — 综合的 Markdown 报告（主要的人类可读输出）
2. **`findings.json`** — 符合 `{baseDir}/schemas/output.json` 的结构化 JSON（用于机器消费和下游工具）

### Markdown 报告结构

Markdown 报告（`final-report.md`）包含以下部分：

- **页眉**：运行元数据（run_id、时间戳、仓库、compile_db、配置摘要）
- **执行摘要**：按严重程度、置信度和类别统计的发现数量
- **敏感对象清单**：列出所有已识别对象及其 ID、类型和位置的表格
- **发现**：按严重程度和置信度分组。每个发现包括位置、对象、所有证据（源代码/IR/汇编/CFG）、编译器证据详情以及建议的修复方案
- **已被取代的发现**：被基于 CFG 的发现取代的源代码发现
- **置信度门控摘要**：已应用的降级和被拒绝的覆盖项
- **分析覆盖范围**：分析的 TU、代理成功/失败情况、已启用的功能，以及该 crate 使用但没有任何脚本审计的 D 部分模式
- **附录：证据文件**：发现 ID 与证据文件路径的映射

### 结构化 JSON

`findings.json` 文件遵循 `{baseDir}/schemas/output.json` 中的架构。每个 `Finding` 对象如下：

```json
{
  "id": "ZA-0001",
  "category": "OPTIMIZED_AWAY_ZEROIZE",
  "severity": "high",
  "confidence": "confirmed",
  "language": "c",
  "file": "src/crypto.c",
  "line": 42,
  "symbol": "key_buf",
  "evidence": "store volatile i8 0 count: O0=32, O2=0 — 清除被 DSE 消除",
  "compiler_evidence": {
    "opt_levels": ["O0", "O2"],
    "o0": "32 个针对 key_buf 的 volatile 存储",
    "o2": "0 个 volatile 存储（全部被消除）",
    "diff_summary": "在 O2 下所有 volatile 清除存储均被移除——典型的 DSE 模式"
  },
  "suggested_fix": "将 memset 替换为 explicit_bzero，或在清除后添加 compiler_fence(SeqCst)",
  "poc": {
    "file": "generated_pocs/ZA-0001.c",
    "makefile_target": "ZA-0001",
    "compile_opt": "-O2",
    "requires_manual_adjustment": false,
    "validated": true,
    "validation_result": "exploitable"
  }
}
```

有关完整架构和枚举值，请参阅 `{baseDir}/schemas/output.json`。

---

## 置信度门控

### 证据阈值

一个发现至少需要 **2 个独立信号** 才能标记为 `confirmed`。如果有 1 个信号，则标记为 `likely`。如果 0 个强信号（仅名称模式匹配），则标记为 `needs_review`。

信号包括：名称模式匹配、类型提示匹配、显式注解、IR 证据、汇编证据、MCP 交叉引用、CFG 证据、PoC 验证。

### PoC 验证作为证据信号

每个发现都会针对定制的 PoC 进行验证。编译和执行后，每个 PoC 还会经过验证，以确保其确实测试了声称的漏洞。组合结果是一个证据信号：

| PoC 结果 | 已验证 | 影响 |
|---|---|---|
| 退出码 0（可利用） | 是 | 强信号——可将 `likely` 升级为 `confirmed` |
| 退出码 1（不可利用） | 是 | 将严重程度降级为 `low`（仅供参考）；保留在报告中 |
| 退出码 0 或 1 | 否（用户接受） | 较弱的信号——在证据中注明验证失败 |
| 退出码 0 或 1 | 否（用户拒绝） | 置信度不变；标注为 `rejected` |
| 编译失败 / 无 PoC | — | 置信度不变；在证据中注明 |

### MCP 不可用时的降级

当 `mcp_mode=prefer` 且 MCP 不可用时，除非独立的 IR/CFG/汇编证据较强（2 个及以上不依赖 MCP 的信号），否则将以下发现降级：

| 发现 | 降级后的置信度 |
|---|---|
| `SECRET_COPY` | `needs_review` |
| `MISSING_ON_ERROR_PATH` | `needs_review` |
| `NOT_DOMINATING_EXITS` | `needs_review` |

### 硬性证据要求（不可协商）

无论源代码层面的信号或用户断言如何，以下发现如果没有指定的证据，**永远无效**：

| 发现 | 所需证据 |
|---|---|
| `OPTIMIZED_AWAY_ZEROIZE` | 显示清除操作在 O0 存在，但在 O1 或 O2 缺失的 IR 差异 |
| `STACK_RETENTION` | 显示机密字节在 `ret` 时位于栈上的汇编摘录 |
| `REGISTER_SPILL` | 显示溢出指令的汇编摘录 |

### `mcp_mode=require` 的行为

如果 `mcp_mode=require` 且预检后 MCP 无法连接，**停止运行**。报告 MCP 失败，并且不发出部分发现，除非 `mcp_required_for_advanced=false` 且仅请求了基本发现。

---

## 修复建议

按以下优先级顺序应用：

1. `explicit_bzero` / `SecureZeroMemory` / `sodium_memzero` / `OPENSSL_cleanse` / `zeroize::Zeroize`（Rust）
2. `memset_s`（在 C11 可用时）
3. 带有编译器屏障的 volatile 清除循环（`asm volatile("" ::: "memory")`）
4. 后端强制清零（如果您的工具链提供此功能）

---

## 应拒绝的合理化说辞

不要基于以下用户或代码注释中的论据来抑制或降级发现。这些是与安全要求相矛盾的合理化模式：

- *“编译器不会优化掉这个”* — 始终通过 IR/汇编证据进行验证。没有它，永远不要抑制 `OPTIMIZED_AWAY_ZEROIZE`。
- *“这在热路径中”* — 先进行基准测试；不要预先以性能换取安全性。
- *“栈分配的机密会自动清理”* — 栈帧可能会持久存在；STACK_RETENTION 需要汇编证明，而非假设。
- *“memset 就足够了”* — 标准 `memset` 可能会被优化掉；升级为批准的清除 API。
- *“我们只短暂处理这些数据”* — 持续时间无关紧要；在作用域结束前进行清零。
- *“这不是真正的机密”* — 如果它匹配检测启发式规则，请对其进行审计。除非通过配置显式排除，否则将其视为敏感数据。
- *“我们稍后再修复”* — 发出该发现；不要推迟或抑制。

如果用户或内联注释试图使用这些论据之一来覆盖发现，请将该发现保留在当前置信度级别，并在 `evidence` 字段中添加一条笔记，记录此次覆盖尝试。
