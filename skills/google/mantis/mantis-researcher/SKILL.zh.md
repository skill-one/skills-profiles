---
name: mantis-researcher
description: 基于 workspace/plan.json 中定义的策略，审计生产环境源代码文件。当存在评审计划，且需要对目标文件执行静态分析和深入评审时，请使用该功能。请勿用于制定计划、去重或编写补丁。
---

# Mantis Researcher (/mantis-researcher)

## 系统目标

弹性代码审计器。对源文件进行快速筛选和深入审查，以识别边界检查、前置条件、缺失的清理和接口违规。

## 命令定义

- **命令:** `/mantis-researcher`
- **描述:** 根据 `workspace/plan.json` 中的策略审计生产源代码文件。
- **参数（可选；由协调器提供，由区块 A 消费）:**
  - `--snapshot_root` / `SNAPSHOT_ROOT`: 此轮次固定、只读代码快照的绝对路径。这是所有快照相对路径字段解析的基准（区块 A 步骤 1b）。
  - `--snapshot_id` / `SNAPSHOT_ID`: 轮次快照标识符。用于哨兵检查（区块 A 步骤 2）并原封不动地嵌入到每个发现的 `discovery_commit` 中。
  - `--state_root`: `workspace/` 状态目录的绝对路径（`plan.json`、`.mantis_state.json`、`findings/`、`kb/`）。状态路径是 STATE-RELATIVE，并且永远不会以 CODE_ROOT 为前缀（区块 A 步骤 3）。
  - `--target_root`（权威覆盖，区块 A 步骤 1a）如果提供也会被尊重。
  - **所有标志缺失 -> 降级/遗留模式:** CODE_ROOT 回退到当前目录，`snapshot_pinned` 被视为 false，行为与今天完全一致（不写入 `discovery_commit`）。

## 输入/输出契约

- **读取**:
  - `workspace/plan.json`（如果缺失/为空，则回退到代码库扫描）。
  - `workspace/.mantis_state.json`（用于跟踪当前循环轮次）。
  - `"kb_references"` 中引用的 Markdown 文件（例如 `workspace/kb/entities/*.md`）。
  - 目标源代码文件。
  - `workspace/kb/structural_index/manifest.json`（用于检查结构索引的可用性/状态）。
  - `workspace/helpers/query_structural_index.py`（用于调用有界结构索引查询）。
- **写入**:
  - 原始发现文件到 `workspace/findings/<uuid>.json`（如果缺失则创建 `workspace/findings/`）。
- **前提条件**:
  - 目标文件必须可访问。
- **幂等性保证**:
  - 以唯一的 UUID 写入新的发现文件。依赖 `mantis-dedupe` 在后续步骤中对重复发现进行聚类和合并。

## 说明

### 步骤 0：定位器解析（快照感知路径处理）

在下方编号的研究步骤之前运行此操作。它修正此阶段中每个 `target_files` / `code_paths` 参考的单一 CODE_ROOT，以便所有子代理审计相同的固定快照。

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源代码（报告、校准、反映），则为发现仅阶段：跳过步骤 2-6；仍然从状态中读取 active_snapshot 以进行溯源/注释；仅因代码根未设置而永远不会停止。
1. 确定 CODE_ROOT，按此优先级顺序：
   a. 如果在此调用中传递了 --target_root，CODE_ROOT = --target_root。它是权威的，并覆盖 SNAPSHOT_ROOT 和状态回退（在调用者将您交给准备好的树时使用，例如一个补丁阴影）。
   b. 否则如果传递了 --snapshot_root（或 SNAPSHOT_ROOT），使用它。
   c. 否则读取 state_root/workspace/.mantis_state.json（如果传递了 --state_root，则使用来自 --state_root 的 state_root，否则相对于当前目录的 ./workspace/...）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（没有参数且没有可读的 active_snapshot）：CODE_ROOT = 当前目录，将 snapshot_pinned = false（模式关闭）。不要停止。
2. 哨兵检查（仅当 snapshot_pinned 为 true 且您没有选择路径 1a 时）：
   验证 CODE_ROOT/.mantis_snapshot_id 存在且等于 SNAPSHOT_ID。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（一个 --target_root 树（1a）是故意被修改的，并且是哨兵豁免的。）
3. 路径字段：
   - SNAPSHOT-RELATIVE（在 CODE_ROOT 下读取）：code_paths 条目；plan target_files 是文件路径。只删除一个尾随的 ":<数字>"。一个 code_paths 条目包含 "://" 是 URL/端点，不是文件读取。一个 code_paths 条目如果不是 <现有路径>:<整数> 的形式，是非源定位器（符号/偏移/端点）：只检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在 state_root/workspace 下读取/写入，永远不会以 CODE_ROOT 为前缀）：
     kb_references、repro_file_path、reattack_file_path、辅助脚本、报告文件以及所有状态/发现 JSON。
4. 当 snapshot_pinned 为 true 时，永远不要在 CODE_ROOT 下写入。任何编译、生成或写入工件的命令都必须在 CODE_ROOT 的私有阴影副本中运行（从 CODE_ROOT 使用 mktemp -d），永远不会以 cwd=CODE_ROOT 运行。只读检查可以 cd 到 CODE_ROOT。
5. VCS-METADATA 切割：历史记录提取和任何在 LIVE 仓库根目录（仍然有 .git/.hg/.repo）中运行的 VCS diff/blame 命令，而不是 CODE_ROOT（快照副本会剥离 VCS 元数据）。仅因 CODE_ROOT 缺少 .git/.hg/.repo 而永远不会停止。
6. 每个 shell 命令使用绝对路径并在调用时设置其自己的工作目录。不要假设工作目录在调用之间持久存在。
```

研究人员的特定说明：

- 研究人员是读取代码的阶段，因此区块 A 步骤 0 的发现仅跳过不适用于此处——您必须解析 CODE_ROOT 并尊重哨兵。
- `workspace/plan.json` `target_files` 和发现 `code_paths` 是 SNAPSHOT-RELATIVE：在 CODE_ROOT 下解析它们（区块 A 步骤 3）。
- `kb_references`、`workspace/plan.json`、`workspace/.mantis_state.json` 以及 `workspace/findings/` 下的一切都是 STATE-RELATIVE：在 --state_root 下读取/写入，永远不会在 CODE_ROOT 下。
- 当固定时（区块 A 步骤 4），永远不要在 CODE_ROOT 下写入、编译或生成任何东西。

对目标代码库进行彻底的内存安全、逻辑正确性和健壮性审查。

按照以下方式执行研究阶段：

1. **加载审查计划和上下文：** 从 `workspace/.mantis_state.json` 读取活动轮次编号并解析当前 ISO 8601 时间戳。读取 `workspace/plan.json` 文件以检索目标调查。如果 `workspace/plan.json` 缺失或为空，则执行目录的通用列表并审查任何主要源文件。如果调查包含 `"kb_references"` 数组，则在开始审计 `"target_files"` 之前显式读取这些 Markdown 文件（例如 `workspace/kb/entities/auth.md`）以获得复合的历史上下文。还从 `workspace/.mantis_state.json` 读取 `active_snapshot`（`root`、`snapshot_id`、`snapshot_pinned`）。将 `active_snapshot.snapshot_id` 保存在内存中：它是您将嵌入到每个发现的 `discovery_commit` 中的值（见发现模式格式）。如果 `active_snapshot` 缺失或 `snapshot_pinned` 为 false，您处于降级/遗留模式——不要停止（区块 A 步骤 1d）；您将简单地省略 `discovery_commit`。

2. **子代理委托（基于波浪的群集并行化）：** 如果 CLI 或代理平台支持生成子代理（例如，使用专门的子代理工具或多代理协调器指令）：

   - 如果支持子代理，不要按顺序执行调查。将 `workspace/plan.json` 中的调查分成并行波浪，以最大限度地提高吞吐量和上下文效率。

   - **波浪 1：轻量级快速筛选（并发峰值）：** 生成并发、轻量级的子代理（例如，最多 10-20 个并行）以扫描 `workspace/plan.json` 中列出的所有文件。每个子代理只应输出快速分类：`{"potentially_flawed": true/false, "reason": "..."}`。

   - **波浪 2：深度安全缺陷热点审计和并行轨迹搜索：** 收集波浪 1 中标记的所有文件。生成并发深度审计子代理的波浪（例如，最多 4-8 个并行）以专注于那些已识别的热点。对于特别复杂的文件，使用不同的提示约束或一组较便宜的 LLM 生成多个针对同一文件的子代理，以探索并行攻击向量。依赖后续的去重阶段合并任何重叠的发现。

   - **令牌优化（分布式写入）：** 指示波浪 2 子代理生成唯一的 UUID 并将它们的发现直接写入磁盘上的 `workspace/findings/<id>.json` 文件。不要要求它们在消息中返回完整的 JSON 负载，因为聚合它们会耗尽您的上下文窗口。要求它们只返回它们创建的 UUID 列表。

   - **快照隔离（波浪固定）—— 必须执行：** 将相同的 `--snapshot_root`（在步骤 0 中解析的 CODE_ROOT）和相同的 `--snapshot_id` 值传递给每个波浪 1 和波浪 2 子代理，并指示每个子代理遵守区块 A（在 CODE_ROOT 下解析 `target_files`/`code_paths`，尊重哨兵）。任何写入发现的波浪 2 子代理都必须将 `discovery_commit` 签名 `snapshot_id`，完全按照发现模式格式中指定的方式。子代理必须不运行 `git pull`/`fetch`/ `checkout`/`reset`、`hg pull`/`update`、`repo sync` 或任何更改工作树或切换版本的命令——整个轮次中快照是不可变的。无法看到快照的子代理必须报告，而不是重新同步。

   - 如果当前环境不支持子代理或并发，则回退到按顺序执行扫描和深入调查。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波浪的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（在执行任何结构查询之前必须执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 缩小范围，或者为每个匹配的符号安排调查。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **覆盖感知解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码是权威的——仍然按仅提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波浪 1（快速筛选）：** 使用 `find_callers()` 作为 grep 的排名提示来补充——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波浪 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含的函数开始，然后根据需要扩展到调用者/被调用者/文件，以获取深度调查上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询助手缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

   - 如果子代理或并发不受当前环境支持，则回退到按顺序执行扫描和深入调查。

   - **结构索引（仅提示增强）：** 当结构索引可用时（`workspace/kb/structural_index/manifest.json` 存在），使用它来补充上述基于波浪的群集。结构索引决定顺序，永远不会决定成员资格。它永远不能取代彻底的步骤 3 调用点扫描。

     - **解析优先协议（在执行任何结构查询之前必须执行）：**

       1. 首先解析符号：
          `python3 workspace/helpers/query_structural_index.py resolve_symbol --name "<function_name>" [--language "<lang>"] [--file "<path>"] --state_root <state_root>`
       2. 如果响应有 `ambiguous: true`，调查所有匹配的符号——永远不要无声地选择一个。如果可能，使用 `--file`/`--language` 缩小范围，或者为每个匹配的符号安排调查。
       3. 使用解析的 `symbol_id` 进行有界查询：
          `python3 workspace/helpers/query_structural_index.py find_callers --symbol_id "<id>" --limit 100 --offset 0 --state_root <state_root>`

     - **覆盖感知解释：** 检查每个结构索引响应中的 `coverage.partition_status`：

       - `complete` + `precision == semantic` + 空结果 = "没有索引调用者"（对索引代码是权威的——仍然按仅提示规则运行 grep）。
       - `complete` + `precision != semantic` + 空结果 = "没有索引调用者"——不权威。必须运行 exhaustive grep。
       - `partial` / `empty` / `failed` + 空结果 = "未完全索引"——必须运行 exhaustive grep。
       - 使用每个结果的 `precision` 和 `backend` 字段来权衡信任（`semantic` > `typecheck` > `ast` > `symbol-only` > `heuristic` > `deferred` > `coverage-only`）。

     - **波浪 1（快速筛选）：** 使用 `find_callers()` 作为 grep 的排名提示来补充——顺序，永远不会是成员资格。结构索引结果优先标记哪些文件应标记为 `potentially_flawed`；它们永远不能取代彻底的步骤 3 调用点扫描。审计 grep 结果和结构索引结果的并集。

     - **波浪 2（深度审计）：** 使用 `get_function_boundary(file, line)` 从包含的函数开始，然后根据需要扩展到调用者/被调用者/文件，以获取深度调查上下文。

     - **优雅降级：** 如果结构索引缺失（没有 `manifest.json`）、为空或查询助手缺失，回退到基于 grep 的发现（今天的行行为）。结构索引只是一个覆盖提示。

3. **彻底的接口和调用点审查：** 如果目标源文件定义了公共或 API 函数（例如数字解析器、解码器、编码器或转换器），这些函数文档中明确说明了大小约束或安全要求（例如，期望调用者分配特定大小的缓冲区）：

   - 运行 repo-wide grep 以构建候选调用点的详尽集——这是强制性的底线。然后使用结构索引查询助手（`resolve_symbol` 然后是 `find_callers`）来排名和优先考虑哪些调用点首先审计（索引区分实际调用与注释/字符串/变量名）。审计两个结果集的并集——结构索引可能会遗漏基于宏的调用、函数指针和动态分发，因此 grep 仍然是底线。
   - 搜索代码库以找到并审查整个仓库中这些函数的所有调用点，以确保安全合同得到全局尊重。
   - 读取调用文件并验证每个调用点是否严格遵循输入约束、正确管理边界并检查大小。
   - 将任何差异标记为合同对齐错误或缺失检查。

4. **无约束/探索性调查：** 如果 `workspace/plan.json` 中的调查计划包含指令或明确要求无约束扫描、对抗性审计或随机探索：

   - 忽略 `workspace/kb/THREAT_MODEL.md` 中现有的安全假设和记录的信任边界。
   - 将所有输入和边界视为不受信任且可能格式不正确。
   - 从头开始以完全的自由和自主性分析实现。
   - 如果这是一个随机探索/挖掘任务且指令最少，则专注于映射目标文件的行为，识别关键入口点，并寻找意外的副作用或边界情况，而不受特定威胁模型的约束。

5. **编译和写入发现：** 不要使用单个庞大文件，而是创建 `workspace/findings/` 目录（如果不存在）。对于每个潜在的发现，生成一个唯一的 UUID 并将有效的 JSON 对象写入单独的文件 `workspace/findings/<id>.json`。这使发现保持隔离并防止在后续分析期间出现令牌限制问题。在文件中不要包含任何文本或 JSON 之前的文本。

- `normalized_title` = `title`转换为小写，并去除所有非字母数字字符（仅ASCII `[a-zA-Z0-9]`；所有其他字符，包括Unicode字母、标点符号和空格均被移除）。如果移除后`normalized_title`为空（例如，标题完全由非ASCII/Unicode字符组成），则将`normalized_title`设置为`sha256(<原始原始标题作为UTF-8字节>)`的前16个十六进制字符，以防止两个不同的非ASCII标题在空字符串上发生冲突。
      - `cwe_part` = 如果存在且非空，则为查找的`cwe`字段，否则为空字符串。
      - `primary_target` = 第一个`code_paths`条目，去除尾部的`:line`（例如，`src/auth.c:145` → `src/auth.c`）。如果`code_paths`为空，或第一个条目是非源定位符（包含`://`的URL，或根据块A步骤3的非文件符号/偏移），则使用空字符串。确定性地排序`code_paths`（首先使用主要汇点，并在多次传递中保持稳定），以防止`primary_target`——以及`signature`——在多次传递之间漂移。（如果顺序不稳定，唯一的成本是遗漏谱系继承→查找被过度报告为新的，从未被隐藏——但稳定顺序保留了跨传递的折叠。）
      - 如果`primary_target`非空：`signature` = `sha256(normalized_title + "|" + cwe_part + "|" + primary_target)`的前16个十六进制字符。
      - 如果`primary_target`为空：`signature` = `sha256(normalized_title + "|" + cwe_part + "|" + sorted(code_paths).join(","))`的前16个十六进制字符。
      - 在查找创建时仅计算一次签名，永不重新计算、编辑或虚构（与`discovery_commit`的规则相同）。

   3. **计算`lineage_id`（跨传递谱系链）：**

      - 扫描`workspace/archive/findings_pass_*/`和`workspace/archive/loop*_findings/`，查找任何归档的查找JSON，其`signature`字段与当前查找计算的`signature`相等。
      - 如果找到匹配项：`lineage_id` = 归档祖先的`lineage_id`（继承谱系链，以便消费者可以在传递之间折叠）。如果多个归档查找共享相同的签名，则从最最近的（最高传递编号）祖先继承。所有具有相同签名的祖先应该共享相同的`lineage_id`；如果它们不共享，则从最最近的祖先继承并记录警告。
      - 如果按精确签名未找到匹配项：尝试**basename重命名回退**，仅适用于真正的重命名。不要重新计算签名（签名在创建时仅计算一次，永不重新计算——不变量#4）。相反：
        1. 计算当前查找的basename：取`primary_target`（第一个`code_paths`条目，去除尾部的`:line`，已在步骤2中为签名计算时计算过）并取其basename（例如，`src/auth.c` → `auth.c`）。如果`primary_target`为空（非源定位符或空的`code_paths`），跳过此回退——转到下面的fresh UUIDv4。
        2. 对于步骤3的归档扫描中找到的每个归档查找：
           从其存储的`code_paths[0]`重建归档查找的basename（去除尾部的`:line`，取basename——例如，`lib/old_auth.c:88` → `old_auth.c`）。不要重新计算归档查找的签名，也不要比较签名；将两个basename作为字符串进行比较。
        3. 仅当（i）basename匹配且（ii）祖先的完整`primary_target`（其`code_paths[0]`去除`:line`）在当前快照中不再存在时，才通过此回退继承祖先的`lineage_id`（检查旧完整路径在CODE_ROOT下不存在——这可以区分真正的重命名与仅仅是basename共享的第二个独立文件）。如果多个归档祖先满足(i)和(ii)，则从最最近的（最高传递编号）继承。通过basename继承时，还添加一个查找历史记录注释`lineage-via-basename-rename`，以便下游消费者将链接视为basename派生的（报告仅在它们的完整`signature`也按相同的BUG谓词匹配时才会折叠两个查找——因此，basename派生的谱系链接永远不会折叠不同的BUG）。
        4. 如果旧完整路径在当前快照中仍然存在，则不要继承——视为未匹配（fresh UUIDv4以下）。
      - 如果按精确签名或basename重命名未找到匹配项：`lineage_id` = 一个新的UUIDv4。
      - 这些是STATE-RELATIVE路径（块A步骤3）——在`--state_root/workspace/archive/`下读取，绝不在CODE_ROOT下读取。

   4. **将三个字段**（`cwe`、`signature`、`lineage_id`）与`discovery_commit`一起写入查找JSON中。

   **模式独立性：** 与`discovery_commit`（在DEGRADED/legacy模式下被省略）不同，`signature`和`lineage_id`始终被计算——它们是内容标识字段，不是快照标识。无论快照是否固定、未固定或不存在（MODE-OFF），它们都能工作。这是一个故意的Phase-3改进：在MODE-OFF中，查找JSON现在包含2-3个额外的可选键（`cwe`、`signature`、`lineage_id`），这些键在Phase 1中不存在。这不会改变快照模型（没有`active_snapshot`、没有同步、没有固定——3状态规则不受影响）。dedupe MODE-OFF回退现在在存在时优先于`stable_key`，这更具有区分性（签名将`cwe`添加到标题+路径混合中），因此它只能拆分`stable_key`会合并的条目（新的预算，更保守=安全）——它永远不会产生错误的合并或抑制合法的查找。缺少`signature` → 今天`stable_key`的行为完全相同。

   **缺失或不可读的目标文件：** 如果`target_files`中的路径不存在或无法在CODE_ROOT下读取（例如，它已被删除或重命名，自计划编写以来），不要虚构查找、行号或文件内容。跳过该目标，并在与之相关的任何查找的`description`中明确记录跳过（或完全省略）。永远不要虚构你没有读取的代码。

   **非源目标：** 对于非源定位符（二进制文件、固件或URL端点——见块A步骤3），`code_paths`条目必须是稳定的定位符（符号名称、偏移或裸路径），不带`:line`后缀。不要将虚构的行号附加到您无法作为文本打开的目标上。

### 查找模式格式（每个文件）

```json
{
  "id": "为该查找生成的唯一标识符（例如，UUID或随机哈希）。这必须包含且与文件名匹配。",
  "title": "授权绕过或内存边界违规在[函数名]",
  "description": "详细的根本原因分析，说明函数在不受信任的输入下为何存在缺陷。",
  "impact": "利用结果（例如，权限提升、内存损坏、数据窃取）。",
  "severity": "CRITICAL / HIGH / MEDIUM / LOW",
  "privileges_required": "NONE / LOW / HIGH",
  "attacker_position": "EXTERNAL / INTERNAL_NETWORK / IN_CLUSTER / LOCAL / HOST_SYSTEM / SUPPLY_CHAIN / PHYSICAL_TEMPORARY / PHYSICAL_LONG_TERM",
  "user_interaction": "NONE / REQUIRED",
  "status": "PROVISIONALLY_VALID",
  "code_paths": ["CODE_ROOT下的快照相对路径，例如'relative/file/path.c:145'。对于非源目标（二进制/固件/URL，根据块A步骤3）使用稳定的定位符（符号名称、偏移或裸路径），不带虚构的':line'。永远不要虚构行号。"],
  "discovery_commit": "从workspace/.mantis_state.json在开始此传递时读取的active_snapshot.snapshot_id（步骤1）。每当快照固定时必须非空：逐字复制，在查找创建时精确设置一次，永不重新计算、编辑或虚构它。如果active_snapshot不存在或snapshot_pinned为false（DEGRADED/legacy模式），则完全省略此键（不要写入""或null）。",
  "cwe": "CWE-787（可选；如果没有CWE则省略）",
  "signature": "sha256(normalized_title + '|' + cwe_part + '|' + primary_target)的前16个十六进制字符。在创建时仅计算一次，永不重新计算。",
  "lineage_id": "UUIDv4，或从具有相同签名的归档查找继承。在创建时计算。",
  "mitigation": "建议的纠正修改。",
  "history": [
    {
      "stage": "researcher",
      "action": "created",
      "details": "初始审计查找记录。",
      "pass_number": <当前传递编号>,
      "timestamp": "<当前iso8601时间戳>"
    }
  ]
}
```

**`discovery_commit`规则（设置一次，在创建时）：** 此阶段是`discovery_commit`的创建位置。当快照固定时，您（或您的Wave-2子代理）写入的每个查找都必须包含一个非空的`discovery_commit`，等于`active_snapshot.snapshot_id`。下游阶段将缺少`discovery_commit`视为NOT_MATCHED（保守分支），因此写入空字符串或错误值将静默损坏匹配——永远不要这样做。在DEGRADED/legacy模式下（没有`active_snapshot`，或`snapshot_pinned`为false）省略该键，以便行为与当前管道匹配。

**`signature`/`lineage_id`规则（设置一次，在创建时）：** 这些字段始终被计算（与`discovery_commit`不同，在degraded模式下被省略）。签名是查找内容标识的确定性哈希；谱系_id将查找链接到其归档祖先。下游消费者（dedupe、链、报告、重现）以UUID回退为键签名/谱系_id：缺少`signature` → 今天UUID的行为完全相同（不会产生静默错误结果）。

确保所有单个查找文件都写入到`workspace/findings/`目录。完成时，通知用户。
