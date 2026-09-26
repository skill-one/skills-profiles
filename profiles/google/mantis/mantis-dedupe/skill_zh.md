# Deduplicator (/mantis-dedupe)

## 系统目标

重复查找合并器。评估原始查找列表，将相同或高度重叠的问题聚类并合并为单一、描述性的记录。

## 命令定义

- **命令：** `/mantis-dedupe`
- **描述：** 合并原始安全查找以消除冗余报告。
- **参数（可选；由协调器提供，由区块A消费）：**
  `--snapshot_root`/`--snapshot_id`/`--state_root`。全部缺失 -> 模式关闭/遗留模式（行为与当前相同；禁用快照门控）。

## 输入/输出契约

- **读取**：
  - `workspace/findings/`（原始查找JSON文件，忽略 `.trash/`）。
  - `workspace/archive/findings_pass_*/*.json` 和
    `workspace/archive/loop*_findings/*.json`（跳过先前传递中已评估和分派的查找）。
  - `workspace/.mantis_state.json`（跟踪当前循环传递）。
- **写入**：
  - 在设置 `"status": "DUPLICATE"` 和 `"duplicate_of"` 后，将重复查找移动到 `workspace/findings/.trash/`。
  - 在 NOT_MATCHED 匹配上将 `"possible_duplicate_of"`（软性、非终结性）设置在当前查找上，并使用当前查找中缺少的 `stamping` `"discovery_commit"`。读取 `active_snapshot`/`snapshot_pinned` 从 `.mantis_state.json`。
  - 将事务日志追加到 `workspace/.tx_log.jsonl`。
  - 生成/执行合并脚本 `workspace/helpers/merge_findings.py`。
  - 更新主要查找 `workspace/findings/<primary_id>.json`（合并字段和历史记录）。
- **前提条件**：
  - `workspace/findings/` 必须存在并包含查找文件。
- **幂等性保证**：
  - 与 `workspace/archive/` 中的存档查找交叉引用，以过滤掉在此运行先前传递中已处理的查找。
    快照门控：在快照不同的存档查找上解析的查找被标记为 POSSIBLE REGRESSION（不会静默过滤）。将事务记录到 `workspace/.tx_log.jsonl` 以支持跟踪和潜在的回滚。
    `merge_findings.py` 中实现了确定性合并规则。

## 说明

### 第0步：定位器解析（首先运行）

```
定位器解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源（报告、校准、反映），则为查找仅阶段：跳过步骤2-6；仍然从状态中读取 `active_snapshot` 以进行溯源/注释；永远不会因为代码根未设置而停止。
1. 确定代码根，按此优先级顺序：
   a. 如果在此次调用中传递了 `--target_root`，则 `CODE_ROOT = --target_root`。
      它是权威的，并且会覆盖 `SNAPSHOT_ROOT` 和状态回退（在调用者将准备好的树交给你时使用，例如一个打补丁的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用它，否则相对于当前目录的 `./workspace/...`）
      -> `active_snapshot.root` / `.snapshot_id` / `.snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，
      将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 边界检查（仅当 `snapshot_pinned` 为 `true` 且你没有采取路径1a时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。
   （--target_root 树（1a）故意被修改，并且是哨兵豁免的。）
3. 路径字段：
   - 快照相对（在 `CODE_ROOT` 下读取）：`code_paths` 条目；计划目标文件
     那些是文件路径。仅删除尾部的 `":<digits>"`。包含 `"://"` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器
     （符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会前缀 `CODE_ROOT`）：
     `kb_references`、`repro_file_path`、`reattack_file_path`、辅助脚本、报告文件，以及所有状态/查找 JSON。
4. 当 `snapshot_pinned` 为 `true` 时，永不向 `CODE_ROOT` 下写。任何编译、生成或写入工件的命令都必须在私有的影子副本中运行
   （从 `CODE_ROOT` 使用 `mktemp -d`），永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切片：历史记录提取和任何 VCS diff/blame 命令都在 LIVE 仓库根目录（仍然有 `.git/.hg/.repo）运行，而不是 `CODE_ROOT`
   （快照副本会删除 VCS 元数据）。不要因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个外壳命令使用绝对路径，并在该调用上设置其自己的工作目录。不要假设工作目录在调用之间持久存在。
```

> [!NOTE] **当前传递检查（防御性；绑定保证在 `mantis-pipeline-adapter` 情景2的每个外壳上）：** 如果 `active_snapshot` 存在且 `active_snapshot.pass != state.pass_number`，则将快照视为此传递的 STALE — 停止 "快照陈旧：传递不匹配" 或降级为 HALT (`snapshot_pinned` 实际上为 `false`：没有权威裁决，区块B NOT_MATCHED，重放 `not_attempted`）。这捕获了自定义外壳在 Stage 15 传递增量中保留 `active_snapshot` 而没有重新固定的情况。参考元代理每次传递都会重新固定，所以这个检查永远不会在那里触发。区块B本身无法检测到这一点（它是 `snapshot_id`-only，不是 `pass`-aware）。

注意：`workspace/findings/`、`workspace/archive/`、`workspace/.tx_log.jsonl`、`workspace/helpers/` 和 `.mantis_state.json` 是状态相对的（在 `--state_root` 下）。你检查的任何用于查找的代码片段都是快照相对的（在 `CODE_ROOT` 下）。不要在 `CODE_ROOT` 下写入。

审查安全查找列表并合并引用完全相同的安全漏洞或相邻代码路径的重复查找。

按以下方式执行你的任务：

1. **加载原始查找 & 存档查找队列：**

   - 列出目录内容并读取 `workspace/findings/` 中的文件。如果目录为空或不存在，通知用户并退出。
   - *重要：* 列出或处理查找时忽略隐藏文件和目录（例如 `.trash/` 子目录）。
   - 定位并加载来自先前循环传递的所有存档查找 JSON 文件，如果存在，在 `workspace/archive/findings_pass_*/*.json` 和 `workspace/archive/loop*_findings/*.json` 下。这些文件代表先前传递中已完全评估、分派和可能修复的漏洞。
   - *重要：* 不要读取或合并 `workspace/historical_learnings.jsonl`（VCS 历史记录），因为我们想捕获如果旧错误被重新引入的回归。

2. **过滤循环重复（快照门控）。** 首先，使用 `active_snapshot.snapshot_id` 从 `.mantis_state.json`（在未固定时跳过）在任何当前查找上 stamp `discovery_commit`。然后，对于每个与存档查找匹配的当前查找（通过 `code_paths`+`title` 相似性），运行：

   **基于签名的候选匹配（阶段3）— 收紧，从不替换：**
   `signature` 可能仅将一对提升为 "候选对快照对检查"；它本身永远不会导致硬 `DUPLICATE`/丢弃。一对仅在满足以下两者时才是候选对以下对快照匹配检查：

   - 它在今天的 `code_paths` + `title` 相似性下匹配，比较 `code_paths` 条目行内（包括其尾部的 `:line`）；AND
   - （当两个查找都有 `signature` 时）它们的 `signature` 字段相等。
     没有 `code_paths` + `title` 协议的 `signature` 匹配不是重复 — 至多是一个软 `possible_duplicate_of`（保持查找活跃），永远不会丢弃。理由：`signature` 删除了行号和所有但第一个 `code_paths` 条目，所以同一文件中的两个不同错误（例如 `parser.c:100` vs `parser.c:900`）具有相同的标题+CWE 共享一个 `signature`；仅基于签名丢弃会静默删除真实查找。如果两者中缺少 `signature`，则使用今天的 `code_paths` + `title` 相似性匹配不变。

   **对快照匹配检查（决定 MATCHED vs NOT_MATCHED）— 比较当前查找的 `discovery_commit` 与这对的存档查找的 `discovery_commit`（不是 `SNAPSHOT_ID`）：**

   1. 如果 `snapshot_pinned` 为 `false` 且状态中没有 `active_snapshot`（模式关闭）-> NOT_MATCHED。停止。 （在 HALT — `active_snapshot` 存在但 `snapshot_pinned=false` — 不要在这里短路；继续到下面的对比较，它将是 NOT_MATCHED，因为当前查找的 `discovery_commit` 是 `live:` ID，它将不会等于存档的。）
   2. 读取当前查找的 `discovery_commit` 和存档查找的 `discovery_commit`：
      - 如果任一为缺失、空或字面 `"MIXED"` -> NOT_MATCHED。
      - 如果它们彼此不是逐字节相等 -> NOT_MATCHED。
      - 如果它们是逐字节相等（两者都存在，非 `MIXED`）-> MATCHED。没有其他路线到 MATCHED；永远不会模糊比较。全局 "默认字段并继续" 向后兼容规则不适用于 `discovery_commit`：缺失 = NOT_MATCHED。 （没有单独的 "脏" 门控：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，所以在传递内查找匹配，跨传递裸提交查找不会匹配。）注意：这是一个对检查（当前 vs 存档），不是针对全局 `SNAPSHOT_ID` 的检查 — dedupe 在上面的步骤2中为当前查找的 `discovery_commit` 印刷 `SNAPSHOT_ID`，所以针对 `SNAPSHOT_ID` 的检查将始终匹配，并且会丢弃重新引入/回归的错误。

   然后，使用幂等性规则（输入/输出契约 → 幂等性保证）避免重复写入，机械地决定：

   - **MATCHED**（两者都存在且相等）：像之前一样软删除当前查找作为循环重复 — 设置 `"status": "DUPLICATE"` 和 `"duplicate_of": "<archived_uuid>"`，如果存在则清除 `possible_duplicate_of`，确保 `mkdir -p workspace/findings/.trash/`，将其移到那里，并在 `workspace/.tx_log.jsonl` 中记录一个 `loop_filter` 事务。如果当前查找缺少 `lineage_id` 但存档查找有一个，则在移动之前将存档查找的 `lineage_id` 继承到当前查找上（以便在合并时保留谱系链）。
   - **NOT_MATCHED**（不同，或任一缺失）：不要设置 `DUPLICATE`，不要移动到垃圾箱。保留当前查找活跃并设置
     `"possible_duplicate_of": "<archived_uuid>"`（一个软性、非终结性提示）。
     如果当前查找缺少 `lineage_id` 但存档查找有一个，则将存档查找的 `lineage_id` 继承到当前查找上（以便即使在查找位于不同快照时也能保留用于报告折叠的谱系链）。

   > [!IMPORTANT] **状态 & 重复不变量：**
   >
   > - 查找不应同时携带 `duplicate_of` 和 `possible_duplicate_of` 指向同一目标 UUID。
   > - `status = "DUPLICATE"` 必须与指向同一目标 UUID 的 `possible_duplicate_of` 共存。
   > - 在 **NOT_MATCHED**（在模式关闭回退异常之外），查找的 `status` 必须保持活跃（例如 `VALID`、`PROVISIONALLY_VALID`、`NEEDS_RESEARCH`），`duplicate_of` 必须不设置，查找必须不移动到 `.trash/`。设置 `possible_duplicate_of` 只是一个非终结性提示。

   - **可能的回归：** 如果存档匹配具有解析状态 (`patch_status` 在 {`VERIFIED_SECURE`,`MITIGATION_PROPOSED`} OR `status`==`FALSE_POSITIVE` OR `production_viability`==`NON_VIABLE`）且对不匹配，保留当前查找活跃，添加历史记录注释 "POSSIBLE REGRESSION vs \<archived_uuid>"，并且不要过滤它。（在新的代码上重新发现的已撤销修复绝不能被丢弃。）
   - **精确-UUID 重试异常（不变）：** 如果当前查找具有与存档完全相同的 UUID，它被故意复制回来以进行重试 — 不要过滤它（保持原样）。
   - **永久未固定异常（仅模式关闭 — 没有快照）：** 如果状态中没有 `active_snapshot`（模式关闭 = 今天的默认值；没有快照边界的目标，例如一个实时端点），在传递级别 `snapshot_pinned` 为 `false` (`active_snapshot.snapshot_pinned` — 它不是每个查找字段）并且区块B信息不足 — 回退到今天的基于签名的查找，如果存在，否则 `stable_key` = 标准化标题 + 第一个 `code_paths` 条目 **包括其尾部的 `:line**`
     （行内，与步骤2相同）。理由：删除 `:line` 会将同一文件中的两个不同错误（例如 `parser.c:100` vs `parser.c:900`）具有相同的标题+CWE 聚类到一个 — 静默删除真实查找。注意：`signature` 本身设计为删除 `:line`（它是一个跨传递谱系的粗略身份，不是一个查找键）；因此，此回退因此优先考虑 `signature` 仅当 `stable_key` 的行内匹配也同意时，永远不会单独基于 `signature`。这为无法匹配的目标保留了查找。

4. **过滤当前批次中的重复查找：** 检查当前查找以找到重复项。两个查找仅当它们共享相同的 `code_paths` 条目行内（包括尾部的 `:line`）并且标题相同或高度相似时才是重复项。如果多个查找引用同一位置上的完全相同的漏洞，它们必须被合并。同一文件中不同行的查找是不同的 — 永不合并它们。

5. **映射/归约分块策略（用于扩展）：** 如果查找文件很多（例如，> 20 项），使用映射/归约方法在检查重叠之前按目标文件或组件对它们进行分组，以避免上下文窗口限制。

6. **令牌优化的合并和合并：** 为了最小化 LLM 输出令牌并防止数据丢失，**不要手动重写或输出合并的 JSON 文件。** 相反，请遵循此模式：

   1. **识别重复项：** 内部映射哪些查找是主要查找的重复项。
   2. **可重用确定性脚本（版本化）：** 编写可重用的辅助脚本（例如 `workspace/helpers/merge_findings.py`），其第一行必须完全为 `# MANTIS_HELPER_VERSION = 2`。在重用现有辅助脚本之前，使用 `grep` 其第一行以查找 `MANTIS_HELPER_VERSION = 2`；如果该标记缺失或为不同的整数（由较旧管道版本留下的辅助脚本），重新生成辅助脚本。仅在标记匹配时才重用它。脚本必须遵循以下确定性规则：
      - **标题：** 选择最全面和描述性的标题。
      - **ID：** 保留正在保留的主要查找的唯一 `"id"`。
      - **严重性：** 选择合并项中指定的最高严重性级别。
      - **所需权限：** 继承最严重的权限要求（优先级：`NONE` > `LOW` > `HIGH`）。
      - **攻击者位置：** 继承最关键的位置要求（优先级：`EXTERNAL` > `INTERNAL_NETWORK` > `IN_CLUSTER` > `LOCAL` > `HOST_SYSTEM` > `SUPPLY_CHAIN` > `PHYSICAL_TEMPORARY` > `PHYSICAL_LONG_TERM`）。
      - **用户交互：** 继承最严重的用户交互要求（优先级：`NONE` > `REQUIRED`）。
      - **代码路径：** 收集并去重所有文件路径和行号到一个唯一的数组。
      - **描述、缓解 & 影响：** 清洁地连接。
      - **历史记录：** 清洁地连接并保留所有来自合并查找的 `"history"` 条目。将此合并操作的条目追加到 `"history"` 数组中，符合模式（包含 `"stage": "dedupe"`、`"action": "merge"`、
        `"details": "Merged duplicate findings: [逗号分隔的-ids]"`、
        `"pass_number": <当前传递编号>`，和 `"timestamp": "<当前 iso8601 时间戳>"`）。
      - **未知键 & 溯源（强制）：** 脚本必须将未明确处理的每个键（包括 `discovery_commit`、`repro_snapshot_id`、`patch_base_snapshot`、`possible_duplicate_of`、`signature`、`lineage_id`、`cwe`）从主要查找复制到合并对象上 — 永不丢弃未知字段。它必须拒绝合并 `discovery_commit` 值不同的两个查找（它们描述了不同的代码版本）；将它们分开并记录拒绝。当合并所有共享一个 `discovery_commit` 的查找时，保留它不变。
   3. **执行脚本：** 运行你的脚本以在磁盘上更新主要查找的文件 (`workspace/findings/<primary_id>.json`)。

7. **事务分阶段清理：** 不要永久删除重复文件。确保垃圾箱目录存在（例如，
   `mkdir -p workspace/findings/.trash/`）。在移动之前，脚本必须更新重复查找文件，设置 `"status": "DUPLICATE"` 和
   `"duplicate_of": "<primary_uuid>"`。将合并的重复 `.json` 文件移动到垃圾箱暂存目录 (`workspace/findings/.trash/`)。对于每个移动的文件，将事务记录追加到 `workspace/.tx_log.jsonl`。

   ### 事务日志模式格式 (`workspace/.tx_log.jsonl`)

   每行必须是一个自包含的 JSON 对象，记录事务：

   ```json
   {"timestamp": "2026-07-14T15:13:00Z", "action": "loop_filter | dedupe_merge", "primary_uuid": "[UUID] (or null for loop_filter)", "moved_uuid": "[UUID]"}
   ```

   这会清理目录以供下游阶段使用，同时保留回滚能力。

完成时，通知用户。
