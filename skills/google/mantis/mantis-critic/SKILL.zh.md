---
name: mantis-critic
description: 评估发现的可生产性，过滤掉仅用于调试的功能和断言陷阱。当发现已被验证，并且需要确认它们在生产版本构建中（断言已禁用）可触发时使用。不应用于编写复现脚本或补丁。
---

# 批评 (/mantis-critic)

## 系统目标

生产可行性专家。过滤已验证的安全漏洞，确认它们在标准发布和生产配置中是否仍然可触发。

## 命令定义

- **命令:**
  `/mantis-critic [--target_root=<路径>] [--snapshot_root=<路径>] [--snapshot_id=<id>] [--state_root=<路径>]`
- **描述:** 评估漏洞的生产可行性，过滤掉仅用于调试的功能和断言陷阱。
- **参数:**
  - `--target_root`: 目标代码库根路径的权威路径。覆盖所有其他定位源，并且不受哨兵保护（区块A路径1a）。默认为未设置。
  - `--snapshot_root`: 此轮次固定的、不可变的快照副本路径（也称为 `SNAPSHOT_ROOT`）。当 `--target_root` 未设置时用作 `CODE_ROOT`（区块A路径1b）。
  - `--snapshot_id`: 协调器为此轮次计算的 `SNAPSHOT_ID`。用于区块A的哨兵检查，以及在步骤3中每个漏洞的区块B漂移比较。如果省略，则回退到状态中的 `active_snapshot.snapshot_id`。
  - `--state_root`: 包含 `workspace/` 的Mantis状态目录根路径（默认为 `.`）。此文件中的每个 `workspace/...` 路径都相对于 `--state_root` 解析；使用默认值 `.` 时，这与今天的 `workspace/` 相同。

## 输入/输出契约

- **读取**:
  - `workspace/findings/`（加载所有漏洞，无论状态如何；还读取每个漏洞的可选 `discovery_commit` 以进行每个漏洞的快照匹配检查）。
  - `workspace/kb/THREAT_MODEL.md`（如果存在，用于检查部署意图和KB记录的 `kb_snapshot_id`）。
  - `workspace/.mantis_state.json`（用于跟踪当前循环遍历并读取 `active_snapshot.{root,snapshot_id,snapshot_pinned}` 以进行定位解析和来源）。
  - 解析的 `CODE_ROOT` 下（当 `snapshot_pinned` 时为固定的快照根）的目标源代码文件，在 `code_paths` 中的路径/行号处，带有上下文偏移。
- **写入**:
  - 就地更新漏洞（设置 `"production_viability"`、`"critic_reasoning"` 并追加历史记录）。
  - 追加到 `workspace/learnings.jsonl`。
- **前提条件**:
  - 漏洞必须存在于 `workspace/findings/` 中。
- **幂等性保证**:
  - 就地覆盖可行性字段。它必须检查当前遍历是否已在历史记录数组中记录了批评条目，并检查 `workspace/learnings.jsonl` 以确保在再次对相同输入运行时不会写入重复记录。

## 说明

评估已验证的漏洞，以确定它们是否表示在编译的、优化的发布构建中的可行动安全缺陷。**采取高度怀疑的、对抗性的立场。不要信任前一个阶段的推理。独立重新验证代码路径，以最终证明或否认生产可行性。**

### 定位解析（首先执行此步骤）

批评是一个读取代码的阶段（它检查目标源），因此它不是一个仅读取漏洞的阶段：运行所有区块A。在加载漏洞之前，解析每个区块A的 `CODE_ROOT` 和哨兵。

```
定位解析（在读取任何目标代码或工件之前）：
0. 角色：如果此技能永远不会读取目标源（报告、校准、反映），则您是一个仅读取漏洞的阶段：跳过步骤2-6；仍然从状态中读取 `active_snapshot` 以进行来源/注释；仅因为代码根未设置而永远不会停止。
1. 确定代码根，按此优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，则 `CODE_ROOT` = `--target_root`。它是权威的，并且覆盖 `SNAPSHOT_ROOT` 和状态回退（用于调用者交给你一个准备好的树，例如一个修补的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用它；否则相对于当前目录的 ./workspace/...）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数并且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` 设置为 `false`（模式关闭）。不要停止。
2. 哨兵检查（仅当 `snapshot_pinned` 为 true 并且您没有采取路径1a时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在并且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（`--target_root` 树（1a）故意被修改，并且不受哨兵保护。）
3. 路径字段：
   - 快照相对（在 `CODE_ROOT` 下读取）：`code_paths` 条目；计划目标文件，它们是文件路径。仅删除尾部的 `:<数字>`。包含 `://` 的 `code_paths` 条目是URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会前缀 `CODE_ROOT`）：`kb_references`、`repro_file_path`、`reattack_file_path`、辅助脚本、报告文件以及所有状态/漏洞 JSON。
4. 当 `snapshot_pinned` 为 true 时，永不 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在 `CODE_ROOT` 的私有影子副本中运行（从 `CODE_ROOT` 使用 `mktemp -d`），永远不会将 `cwd` 设置为 `CODE_ROOT`。只读检查可以进入 `CODE_ROOT`。
5. VCS-METADATA 切割：历史记录提取和任何在 LIVE 仓库根（仍然有 `.git/.hg/.repo`）中运行的 VCS diff/blame 命令，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。仅因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而永远不会停止。
6. 每个shell命令使用绝对路径，并在调用时设置其自己的工作目录。不要假设工作目录在调用之间持久存在。
```

> [!NOTE] **当前遍历检查（防御性；绑定保证在 `mantis-pipeline-adapter` 的每个 `Scenario 2` 上）:** 如果 `active_snapshot` 存在并且 `active_snapshot.pass` 不等于 `state.pass_number`，则将快照视为此遍历中的过时 — 停止 "过时的 `active_snapshot`：遍历不匹配" 或降级为 HALT（`snapshot_pinned` 实际上为 false：没有权威的判断，区块B NOT_MATCHED，重放 `not_attempted`）。这捕获了自定义 harness 在阶段15遍历增量中保留 `active_snapshot` 而没有重新固定的情况。参考元代理每次都会重新固定，所以这个检查永远不会在那里触发。区块B本身无法检测到这一点（它是 `snapshot_id` 仅，不是 `pass` 感知的）。

**此阶段的 `SNAPSHOT_ID`：** 让 `SNAPSHOT_ID` 为如果提供，则为 `--snapshot_id` 的值，否则为 `workspace/.mantis_state.json` 中的 `active_snapshot.snapshot_id`。如果两者都不存在（没有 `--snapshot_id` 并且状态中没有 `active_snapshot`），或者区块A通过路径1d解析 `CODE_ROOT`（没有参数，当前目录），则 `SNAPSHOT_ID` 为不可用（模式关闭 = 今天的默认值）：将步骤3中的每个区块B检查视为 NOT_MATCHED，并将KB新鲜度门在步骤2中视为失败。不要停止；按以下方式降级。当 `active_snapshot` 存在但 `snapshot_pinned` 为 false（HALT模式）时，`SNAPSHOT_ID` 是记录的 `live:` id 并且是可用的 — 区块B仍然返回 NOT_MATCHED（`snapshot_pinned` 为 false），但步骤3c中的 "模式关闭异常" 不会触发：NOT_MATCHED 结果被视为漂移 → `CONDITIONAL_VIABLE`，永远不会 `NON_VIABLE`（`mantis-calibrate` 会丢弃它）。

按以下方式执行批评评估：

1. **加载漏洞：** 读取 `workspace/findings/` 目录中的 JSON 文件。您必须加载所有漏洞，无论状态如何（包括 `"VALID"`、`"FALSE_POSITIVE"`、`"PROVISIONALLY_VALID"` 和 `"NEEDS_RESEARCH"`），以便它们可以被处理或记录到长期内存中。如果不存在，请通知用户。

2. **评估全局仓库意图（KB新鲜度门控）：** 读取 `workspace/kb/THREAT_MODEL.md`（如果存在）。检查 **部署意图** 部分。

   **KB新鲜度门控 — 在任何空白批量标记（3状态规则）之前必需：** 确定KB构建的快照。从以下来源之一读取它（按顺序尝试，第一个匹配的获胜）：

   1. `workspace/kb/THREAT_MODEL.md` 的第一行的 `KB_SNAPSHOT:` 标记（威胁模型将其写入为裸头；架构模型在每个KB文件上写入包裹在注释中的 `<!-- KB_SNAPSHOT: ... -->`）。对于架构文件，扫描 `KB_SNAPSHOT:` 子字符串在注释内。不要寻找 `kb_snapshot_id:` 或 `Snapshot:` — 这些标记永远不会被写入，门控永远不会匹配。
   2. 否则 `workspace/.mantis_state.json` 中的 `kb_snapshot_id` 值（架构模型在其状态戳步骤中写入它）。
   3. 否则 `""`（没有先前的KB来源）。下面的空白批量标记按以下方式门控：

   - **模式关闭**（状态中没有 `active_snapshot` — 没有 `--sync`）：完全跳过新鲜度门控。允许空白 `SAMPLE_OR_TEST` 批量标记作为今天（字节对字节今天的行为） — KB 是针对实时树构建的，并且没有快照可以与之比较。
   - **HALT 或 PINNED**（`active_snapshot` 存在）：仅当记录的 `KB_SNAPSHOT:`（或 `kb_snapshot_id`）存在并且与上面定位解析中解析的当前 `SNAPSHOT_ID` 字节对字节相等时，才允许空白批量标记。如果它缺失、为空或不相等，则您必须不批量标记：完全跳过此空白操作，并在步骤3-5中单独评估每个漏洞。

   仅当新鲜度门控通过（或在模式关闭中跳过）：如果威胁模型明确说明整个仓库专用于教程、示例项目或测试套件（例如，`Intent: SAMPLE_OR_TEST_ONLY`），则您必须将所有漏洞标记为 **`SAMPLE_OR_TEST`**，无论它们在文件结构中的位置如何，并跳过剩余的每个漏洞可行性检查。

3. **获取目标代码片段（快照匹配）：** 对于每个状态为 `"VALID"` 或 `"PROVISIONALLY_VALID"` 的漏洞（跳过 `"FALSE_POSITIVE"` 或 `"NEEDS_RESEARCH"` 漏洞和以下评估步骤）：

   a. **从 `code_paths` 中解析目标文件**，按照区块A步骤3：`code_paths` 是快照相对的，因此在其下读取它们。删除尾部的 `:<数字>` 以获取行号；`://` 表示URL，不是文件；任何不是 `<路径>:<整数>` 形式的条目都是非源定位器 — 仅进行存在检查，没有行逻辑。

   b. **快照匹配检查（区块B）：** 通过将其 `discovery_commit` 与当前 `SNAPSHOT_ID` 进行比较，计算此漏洞的 `MATCHED` / `NOT_MATCHED`。

   ```
   漏洞 F 的快照匹配检查（决定 MATCHED vs NOT_MATCHED）：
   1. 如果 `snapshot_pinned` 为 false -> NOT_MATCHED。停止。
   2. 读取 F.discovery_commit:
      - 缺失 或 空或字面量 "MIXED" -> NOT_MATCHED。
      - 不完全等于 `SNAPSHOT_ID`          -> NOT_MATCHED。
      - 完全等于 `SNAPSHOT_ID`              -> MATCHED。
   没有其他路线可以匹配；永远不会模糊比较。全局 "默认该字段并继续" 的向后兼容规则不适用于 `discovery_commit`：缺失 = NOT_MATCHED。（没有单独的 "脏" 门控：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，因此在本遍历中的漏洞匹配，跨遍历的裸提交漏洞不匹配。）
   ```

   c. **漂移 / 缺失文件 / 超出范围保护（安全措施 — 永远不会 `NON_VIABLE`）：** 如果区块B返回 **NOT_MATCHED**，或者解析的目标文件不存在于 `CODE_ROOT` 下，或者指定的行号超出文件末尾（超出范围），则您必须不运行针对此漏洞的特定领域可行性分析（步骤4-5），并且您必须不将其标记为 `NON_VIABLE`（缺失文件不是死代码；`NON_VIABLE` 是 `mantis-calibrate` 会丢弃的值）。

   **异常（仅模式关闭 — 没有活跃的 `active_snapshot`）：** 如果 `SNAPSHOT_ID` 不可用（模式关闭：状态中没有 `active_snapshot` 并且没有 `--snapshot_id`）并且 NOT_MATCHED 的唯一原因是缺失/不可用的 `SNAPSHOT_ID`（不是缺失文件或超出范围的行），将其视为 "无法比较" 并正常传递到评估（步骤3d）。这保留了非同步运行时的今天的行为。在 HALT 模式（`active_snapshot` 存在，`snapshot_pinned=false`）中，此异常不会触发：区块B NOT_MATCHED，漏洞是漂移 → `CONDITIONAL_VIABLE`（下面的 "否则" 分支），永远不会 `NON_VIABLE`（`calibrate` 会丢弃）。缺失文件和超出范围的条件仍然强制 `CONDITIONAL_VIABLE`，无论固定或模式如何。

   **否则（漂移、缺失文件或超出范围）：** 设置 `production_viability` = **`CONDITIONAL_VIABLE`** 并写入漂移注释，命名原因，例如：
   `"快照漂移：discovery_commit=<disc> != 活跃的 `SNAPSHOT_ID`=<id>（或目标文件/行在固定的快照中不再存在）；无法重新验证可行性，默认为 `CONDITIONAL_VIABLE`（保守）。"`
   然后通过步骤6记录更新，并继续到下一个漏洞。（此漏洞仍然在步骤7中记录为 `CONDITIONAL_VIABLE` 作为长期内存的一部分。）

   d. **匹配、文件存在、行在范围内：** 从 `CODE_ROOT` 读取目标文件，并至少读取指定行号周围的 **15行前文** 和 **15行后文**。这个目标窗口对于分析周围结构和宏定义是必要的。此外，检查 `repro_hints` 和 `history` 以检查 `mantis-reproduce` 记录的实证执行遥测（例如 `build_profile`、`sanitizers_used`、`assertions_disabled`、`ingress_blocked`）。使用此实证执行遥测来证实发布构建的可行性。继续到步骤4-5。

4. **评估特定领域可行性约束:**

   - **对于内存安全漏洞：** 定位受影响的缓冲区的分配源。确定它是否以安全边界或尾随填充分配。如果越界访问包含在物理填充内，则将其标记为 **`NON_VIABLE`**。
   - **对于逻辑和授权漏洞：** 验证有缺陷的逻辑或绕过的端点在标准生产部署中是否实际可访问。如果漏洞依赖于仅用于调试的后门、模拟身份验证提供程序或仅用于路由，则将其标记为 **`NON_VIABLE`**。

5. **确定可行性状态：** 为漏洞分配以下可行性状态之一，以确保我们正确地优先级排序：

   - **`NON_VIABLE`**: 缺陷不可达或在生产中编译出去。这包括：
     - **禁用的断言（内存漏洞）：** 依赖标准 `assert()`、`debug_abort()` 或开发仅恐慌来触发崩溃/DoS状态的错误，其中 `NDEBUG` 将它们删除，代码安全返回。
     - **仅用于调试的功能：** 条件编译调试标志（例如 `#ifdef DEBUG`）。
     - **被环境控制阻挡：** 被标准、不可配置的生产环境控制阻挡（例如，OS级权限、内核级沙盒、只读文件系统），这些控制无法绕过。
   - **`SAMPLE_OR_TEST`**: 问题存在于示例代码、测试套件、模糊测试 harness 或验证框架中。
   - **`CONDITIONAL_VIABLE`**: 缺陷仅在特定非默认配置、可选编译器标志或可能跨生产环境变化的自定义硬化选项下可利用。
   - **`VIABLE`**: 缺陷在标准发布/生产构建中完全可触发。

6. **令牌优化文件更新：** 为最小化LLM输出令牌，**请勿重新发出或手动重写整个JSON对象**。相反，应使用就地编辑工具（例如，您首选语言中的短脚本或 `jq`）将新字段编程追加到现有的 `workspace/findings/<id>.json` 文件中。

   您必须将以下内容追加到现有对象中：

   - 一个 `"production_viability"` 字段（`"VIABLE"`、`"NON_VIABLE"`、`"SAMPLE_OR_TEST"` 或 `"CONDITIONAL_VIABLE"`）。
   - 一个 `"critic_reasoning"` 字段，解释您的评估。
   - 一个到 `"history"` 数组的条目：

   ```json
   {
     "stage": "critic",
     "action": "evaluated",
     "details": "确定生产可行性为 [VIABLE/NON_VIABLE/SAMPLE_OR_TEST/CONDITIONAL_VIABLE]，因为 [原因]",
     "pass_number": <当前_pass_number>,
     "snapshot": "<SNAPSHOT_ID>",
     "timestamp": "<当前_iso8601_timestamp>"
   }
   ```

   将 `"snapshot"` 设置为在定位器解析中解析的 `SNAPSHOT_ID`。如果 `SNAPSHOT_ID` 为不可用（模式关闭），则将其设置为 `""`（或省略该键）。不要编造ID。

7. **追加到长期记忆：** 对于您加载的每个发现（包括 `NON_VIABLE`、`SAMPLE_OR_TEST`、`CONDITIONAL_VIABLE`、`FALSE_POSITIVE` 和 `NEEDS_RESEARCH`），使用追加模式将一个结构化JSON行追加到名为 `workspace/learnings.jsonl` 的工作区数据库文件中。这确保了验证结果可以在多次运行中记住，帮助策略师避免重新扫描它们。

   - **记忆条目格式：**
     `{"title": "[安全漏洞标题]", "code_paths": ["[路径1:行1]"], "status": "[VIABLE / CONDITIONAL_VIABLE / NON_VIABLE / SAMPLE_OR_TEST / FALSE_POSITIVE / NEEDS_RESEARCH]", "snapshot": "[当前 SNAPSHOT_ID，或模式关闭时省略]"}`

完成时，通知用户。
