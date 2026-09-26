# Mantis Researcher (/mantis-researcher)

## 系统目标

弹性代码审计员。执行快速筛选和深入审查源文件，以识别边界检查、前置条件、缺失的清理和接口违规。

## 命令定义

- **命令:** `/mantis-researcher`
- **描述:** 基于策略 `workspace/plan.json` 审计生产源代码文件。
- **参数（可选；由协调器提供，由区块 A 消费）:**
  - `--snapshot_root` / `SNAPSHOT_ROOT`: 此轮次固定、只读代码快照的绝对路径。这是所有快照相对路径字段解析的 CODE_ROOT（区块 A 步骤 1b）。
  - `--snapshot_id` / `SNAPSHOT_ID`: 轮次快照标识符。用于哨兵检查（区块 A 步骤 2）并原封不动地嵌入到每个发现的 `discovery_commit` 中。
  - `--state_root`: `workspace/` 状态目录的绝对路径（`plan.json`、`.mantis_state.json`、`findings/`、`kb/`）。状态路径是 STATE-RELATIVE，并且永远不会以 CODE_ROOT 为前缀（区块 A 步骤 3）。
  - `--target_root`（权威覆盖，区块 A 步骤 1a）如果提供也会被尊重。
  - **所有标志缺失 -> 降级/遗留模式:** CODE_ROOT 回退到当前目录，`snapshot_pinned` 被视为 false，行为与今天完全一致（不写入 `discovery_commit`）。

## 输入/输出契约

- **读取:**
  - `workspace/plan.json`（如果缺失/为空则回退到代码库扫描）。
  - `workspace/.mantis_state.json`（用于跟踪当前循环轮次）。
  - `"kb_references"` 中引用的 Markdown 文件（例如 `workspace/kb/entities/*.md`）。
  - 目标源代码文件。
  - `workspace/kb/structural_index/manifest.json`（用于检查结构索引的可用性/状态）。
  - `workspace/helpers/query_structural_index.py`（用于调用有界结构索引查询）。
- **写入:**
  - 原始发现文件到 `workspace/findings/<uuid>.json`（如果缺失则创建 `workspace/findings/`）。
- **前提条件:**
  - 目标文件必须可访问。
- **幂等性保证:**
  - 以唯一的 UUID 写入新的发现。依赖 `mantis-dedupe` 在后续步骤中对重复发现进行聚类和合并。

## 说明

### 步骤 0：定位器解析（快照感知路径处理）

在编号的研究步骤之前运行此操作。它修正此阶段中每个 `target_files` / `code_paths` 参考的单一 CODE_ROOT，以便所有子代理审计相同的固定快照。

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源代码（报告、校准、反映），则为发现仅阶段：跳过步骤 2-6；仍然从状态中读取 active_snapshot 以进行溯源/注释；仅因代码根未设置而永远不会停止。
1. 确定 CODE_ROOT，按此优先级顺序：
   a. 如果在此调用中传递了 --target_root，CODE_ROOT = --target_root。它是权威的，并覆盖 SNAPSHOT_ROOT 和状态回退（当调用者将您交给准备好的树时，例如一个补丁阴影）。
   b. 否则如果传递了 --snapshot_root（或 SNAPSHOT_ROOT），使用它。
   c. 否则读取 state_root/workspace/.mantis_state.json（如果传递了 --state_root，则使用它，否则相对于当前目录的 ./workspace/...）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（没有参数且没有可读的 active_snapshot）：CODE_ROOT = 当前目录，将 snapshot_pinned 视为 false（模式关闭）。不要停止。
2. 哨兵检查（仅当 snapshot_pinned 为 true 且您没有采取路径 1a 时）：
   验证 CODE_ROOT/.mantis_snapshot_id 存在且等于 SNAPSHOT_ID。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（--target_root 树 (1a) 是故意被修改的，并且是哨兵豁免的。）
3. 路径字段：
   - SNAPSHOT-RELATIVE（在 CODE_ROOT 下读取）：code_paths 条目；plan target_files 是文件路径。只删除尾部的 ":<digits>"。包含 "://" 的 code_paths 条目是 URL/端点，不是文件读取。不是 <现有路径>:<整数> 形式的 code_paths 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在 state_root/workspace 下读取/写入，永远不会以 CODE_ROOT 为前缀）：
     kb_references、repro_file_path、reattack_file_path、辅助脚本、报告文件以及所有状态/发现 JSON。
4. 当 snapshot_pinned 为 true 时，永远不要在 CODE_ROOT 下写入。任何编译、生成或写入工件的命令都必须在 CODE_ROOT 的私有阴影副本（从 CODE_ROOT mktemp -d）中运行，永远不会以 cwd=CODE_ROOT 运行。只读检查可以 cd 到 CODE_ROOT。
5. VCS-METADATA 切割：历史记录提取和任何在 LIVE 仓库根目录（仍然有 .git/.hg/.repo）中运行的 VCS diff/blame 命令，而不是 CODE_ROOT（快照副本会删除 VCS 元数据）。不要因为 CODE_ROOT 缺少 .git/.hg/.repo 而停止。
6. 每个 shell 命令使用绝对路径，并在该调用上设置它自己的工作目录。不要假设工作目录在调用之间持续存在。
```

研究人员的特定说明：

- 研究人员是 CODE-读取阶段，因此区块 A 步骤 0 的发现仅跳过不适用于此——您必须解析 CODE_ROOT 并尊重哨兵。
- `workspace/plan.json` `target_files` 和发现 `code_paths` 是 SNAPSHOT-RELATIVE：在 CODE_ROOT 下解析它们（区块 A 步骤 3）。
- `kb_references`、`workspace/plan.json`、`workspace/.mantis_state.json` 和 `workspace/findings/` 下的所有内容都是 STATE-RELATIVE：在 --state_root 下读取/写入，永远不会在 CODE_ROOT 下。
- 当 pinned 时，永远不要在 CODE_ROOT 下写入、编译或生成任何内容（区块 A 步骤 4）。

对目标代码库进行彻底的内存安全、逻辑正确性和鲁棒性审查。

按照以下方式执行研究阶段：

1. **加载审查计划和上下文：** 从 `workspace/.mantis_state.json` 读取当前轮次编号，并解析当前 ISO 8601 时间戳。读取 `workspace/plan.json` 文件以检索目标调查。如果 `workspace/plan.json` 缺失或为空，则执行目录的通用列表并审查任何主要源文件。如果调查包含 `"kb_references"` 数组，则显式读取这些 Markdown 文件（例如 `workspace/kb/entities/auth.md`），以在开始审计 `"target_files"` 之前获得复合的历史上下文。还从 `workspace/.mantis_state.json` 读取 `active_snapshot`（`root`、`snapshot_id`、`snapshot_pinned`）。将 `active_snapshot.snapshot_id` 保存在内存中：这是您将嵌入到每个发现的 `discovery_commit` 中的值（见发现模式格式）。如果 `active_snapshot` 缺失或 `snapshot_pinned` 为 false，您处于降级/遗留模式——不要停止（区块 A 步骤 1d）；您将简单地省略 `discovery_commit`。

2. **子代理委托（基于波的群集并行化）：** 如果 CLI 或代理平台支持生成子代理（例如，使用专门的子代理工具或多代理协调器指令）：

   - 如果支持子代理，不要按顺序执行调查。将 `workspace/plan.json` 中的调查拆分为并行波，以最大限度地提高吞吐量和上下文效率。

   - **波 1：轻量级快速筛选（并发峰值）：** 生成并发、轻量级的子代理（例如，最多并行 10-20 个）来扫描 `workspace/plan.json` 中列出的所有文件。每个子代理只应输出快速分类：`{"potentially_flawed": true/false, "reason": "..."}`。

   - **波 2：深度安全缺陷热点审计和并行轨迹搜索：** 收集 Wave 1 中标记的所有文件。生成并发深度审计子代理的波（例如，最多并行 4-8 个）以专注于那些已识别的热点。对于特别复杂的文件，使用不同的提示约束或一组较便宜的 LLM 生成多个子代理来探索并行攻击向量。依赖后续的去重阶段来合并任何重叠的发现。

   - **令牌优化（分布式写入）：** 指示 Wave 2 子代理生成唯一的 UUID 并将它们的发现直接写入磁盘上的 `workspace/findings/<id>.json` 文件。不要要求它们在消息中返回完整的 JSON 有效负载，因为聚合它们将耗尽您的上下文窗口。要求它们只返回它们创建的 UUID 列表。

   - **快照隔离（波固定）—— 必须执行：** 向每个 Wave-1 和 Wave-2 子代理传递相同的 `--snapshot_root`（在步骤 0 中解析的 CODE_ROOT）和相同的 `--snapshot_id` 值，并指示每个子代理遵守区块 A（在 CODE_ROOT 下解析 `target_files`/`code_paths`，尊重哨兵）。任何 Wave-2 子代理写入发现都必须将 `discovery_commit` 签名 `snapshot_id`，完全按照发现模式格式中指定的方式。子代理必须不会运行 `git pull`/`fetch`/ `checkout`/`reset`、`hg pull`/`update`、`repo sync` 或任何更改工作树或切换版本的命令——整个传递中快照是不可变的。无法看到快照的子代理必须报告，而不是重新同步。

   - 如果当前环境不支持子代理或并发，则回退到按顺序执行扫描和深度挖掘。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（任何结构查询之前必须强制执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 进行缩小，或者为每个匹配的符号安排调查。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **感知覆盖的解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码的权威——仍然按提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不是权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波 1（快速筛选）：** 使用 `find_callers()` 作为排名提示来补充 grep——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含函数开始，然后根据需要扩展到调用者/被调用者/文件以进行深度挖掘上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询辅助工具缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

   - 如果子代理或并发不受当前环境支持，则回退到按顺序执行扫描和深度挖掘。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（任何结构查询之前必须强制执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 进行缩小，或者安排调查每个匹配的符号。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **感知覆盖的解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码的权威——仍然按提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不是权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波 1（快速筛选）：** 使用 `find_callers()` 作为排名提示来补充 grep——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含函数开始，然后根据需要扩展到调用者/被调用者/文件以进行深度挖掘上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询辅助工具缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

   - 如果子代理或并发不受当前环境支持，则回退到按顺序执行扫描和深度挖掘。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（任何结构查询之前必须强制执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 进行缩小，或者安排调查每个匹配的符号。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **感知覆盖的解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码的权威——仍然按提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不是权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波 1（快速筛选）：** 使用 `find_callers()` 作为排名提示来补充 grep——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含函数开始，然后根据需要扩展到调用者/被调用者/文件以进行深度挖掘上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询辅助工具缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

   - 如果子代理或并发不受当前环境支持，则回退到按顺序执行扫描和深度挖掘。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（任何结构查询之前必须强制执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 进行缩小，或者安排调查每个匹配的符号。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **感知覆盖的解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码的权威——仍然按提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不是权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波 1（快速筛选）：** 使用 `find_callers()` 作为排名提示来补充 grep——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含函数开始，然后根据需要扩展到调用者/被调用者/文件以进行深度挖掘上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询辅助工具缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

   - 如果子代理或并发不受当前环境支持，则回退到按顺序执行扫描和深度挖掘。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（任何结构查询之前必须强制执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 进行缩小，或者安排调查每个匹配的符号。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 3. If the old full path still exists on the current snapshot, do NOT inherit — treat as no match (fresh UUIDv4 below).
      - If no match by either exact signature or basename rename: `lineage_id` = a fresh UUIDv4.
      - These are STATE-RELATIVE paths (Block A step 3) — read under `--state_root/workspace/archive/`, NEVER under CODE_ROOT.

   - **写入所有三个字段** (`cwe`, `signature`, `lineage_id`) 到发现 JSON 中，与 `discovery_commit` 一起。

   **模式独立性：** 与 `discovery_commit`（在降级/遗留模式下被省略）不同，`signature` 和 `lineage_id` 始终被计算——它们是内容标识字段，不是快照标识。它们无论快照是否 pinned、unpinned 或 absent（模式关闭）都能工作。这是一个故意的 Phase-3 改进：在 MODE-OFF，发现 JSON 现在包含 2-3 个额外的可选键 (`cwe`, `signature`, `lineage_id`)，这些在 Phase 1 中不存在。这不会改变快照模型（没有 `active_snapshot`，没有同步，没有 pin——3 状态规则不受影响）。去重 MODE-OFF 回退现在优先考虑 `signature` 覆盖 `stable_key` 当存在时，这更加区分（signature 在标题+路径混合中添加了 `cwe`），因此它只能拆分 `stable_key` 会合并的条目（新鲜预算，更保守 = 安全）——它永远不会产生错误合并或抑制合法发现。缺失 `signature` → 今天 `stable_key` 行为完全相同。

   **目标文件缺失或不可读：** 如果 `target_files` 中的路径不存在或无法在 CODE_ROOT 下读取（例如，自计划编写以来已被删除或重命名），不要编造发现、行号或文件内容。跳过该目标并在与之相关的任何发现的 `description` 中明确记录跳过（或完全省略）。永远不要编造您未读取的代码。

   **非源目标：** 对于非源定位器（二进制、固件或 URL 端点——见区块 A 步骤 3），`code_paths` 条目必须是稳定的定位器（符号名称、偏移或裸路径）而不带 `:line` 后缀。不要将编造的行号附加到您无法作为文本打开的目标。
