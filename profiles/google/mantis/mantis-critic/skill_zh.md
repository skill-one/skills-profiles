# 批评 (/mantis-critic)

## 系统目标

生产可行性专家。过滤已验证的安全漏洞，确认它们在标准发布和生产配置中是否仍然可触发。

## 命令定义

- **命令:**
  `/mantis-critic [--target_root=<路径>] [--snapshot_root=<路径>] [--snapshot_id=<id>] [--state_root=<路径>]`
- **描述:** 评估漏洞的生产可行性，过滤掉仅用于调试的功能和断言陷阱。
- **参数:**
  - `--target_root`: 目标代码库根路径的权威路径。覆盖所有其他定位源，并且不受哨兵保护（区域 A 路径 1a）。默认为未设置。
  - `--snapshot_root`: 此轮次使用的固定、不可变快照副本的路径（也称为 `SNAPSHOT_ROOT`）。当 `--target_root` 未设置时用作 `CODE_ROOT`（区域 A 路径 1b）。
  - `--snapshot_id`: 协调器为此轮次计算的 `SNAPSHOT_ID`。用于区域 A 的哨兵检查，以及步骤 3 中每个漏洞的区域 B 漂移比较。如果省略，则回退到状态中的 `active_snapshot.snapshot_id`。
  - `--state_root`: 包含 `workspace/` 的 Mantis 状态目录根路径（默认为 `.`）。此文件中的每个 `workspace/...` 路径都相对于 `--state_root` 解析；使用默认值 `.` 时，这与今天的 `workspace/` 相同。

## 输入/输出契约

- **读取**:
  - `workspace/findings/`（加载所有漏洞，无论状态如何；还读取每个漏洞的可选 `discovery_commit` 以进行每个漏洞的快照匹配检查）。
  - `workspace/kb/THREAT_MODEL.md`（如果存在，用于检查部署意图和 KB 记录的 `kb_snapshot_id`）。
  - `workspace/.mantis_state.json`（用于跟踪当前循环遍历并读取 `active_snapshot.{root,snapshot_id,snapshot_pinned}` 以进行定位解析和来源）。
  - 解析的 `CODE_ROOT` 下目标源代码文件（当 `snapshot_pinned` 时为固定的快照根），在 `code_paths` 中的路径/行号处具有上下文偏移。
- **写入**:
  - 原地更新漏洞（设置 `"production_viability"`, `"critic_reasoning"` 并追加历史记录）。
  - 追加到 `workspace/learnings.jsonl`。
- **前提条件**:
  - 漏洞必须存在于 `workspace/findings/` 中。
- **幂等性保证**:
  - 原地覆盖可行性字段。它必须检查当前遍历是否已在历史记录数组中记录了批评条目，并检查 `workspace/learnings.jsonl` 以确保在再次对相同输入运行时不会写入重复记录。

## 说明

评估已验证的漏洞，以确定它们是否表示编译优化发布构建中的可操作安全缺陷。**采取高度怀疑的、对抗性的立场。不要信任前一个阶段的推理。独立重新验证代码路径，以最终证明或否定生产可行性。**

### 定位解析（首先执行）

批评是一个读取代码的阶段（它检查目标源），因此它不是一个仅读取漏洞的阶段：运行所有区域 A。在加载漏洞之前解析 `CODE_ROOT` 和每个区域 A 的哨兵。

```
定位解析（在读取任何目标代码或工件之前）：
0. 角色：如果这个技能永远不会读取目标源（报告、校准、反映），你是一个仅读取漏洞的阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行来源/注释；仅因为代码根未设置而永远不会停止。
1. 确定 `CODE_ROOT`，按以下优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，`CODE_ROOT` = `--target_root`。它是权威的，并且覆盖 `SNAPSHOT_ROOT` 和状态回退（当调用者将你交给一个准备好的树时，例如一个修补的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用它；否则相对于当前目录的 ./workspace/...）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数并且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` = false（模式关闭）。不要停止。
2. 哨兵检查（仅当 `snapshot_pinned` 为 true 并且你没有采取路径 1a 时）：
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在并且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照哨兵不匹配"。（一个 `--target_root` 树（1a）是故意被修改的，并且不受哨兵保护。）
3. 路径字段：
   - 快照相对（在 `CODE_ROOT` 下读取）：`code_paths` 条目；计划目标文件，它们是文件路径。只删除尾部的 `:<数字>`。包含 `://` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：只检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会前缀 `CODE_ROOT`）：
     `kb_references`，`repro_file_path`，`reattack_file_path`，辅助脚本，报告文件，以及所有状态/漏洞 JSON。
4. 当 `snapshot_pinned` 为 true 时，永不 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在私有的影子副本（从 `CODE_ROOT` 使用 `mktemp -d`）中运行，永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切割：历史记录提取和任何在 LIVE 仓库根（仍然有 `.git/.hg/.repo`）中运行的 VCS diff/blame 命令，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。不要仅仅因为 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而停止。
6. 每个 shell 命令使用绝对路径，并在该调用上设置它自己的工作目录。不要假设工作目录在调用之间持久存在。
```

> [!NOTE] **当前-遍历检查（防御性；绑定保证是在每个 `mantis-pipeline-adapter` 场景 2 的 harness 上）:** 如果 `active_snapshot` 存在并且 `active_snapshot.pass != state.pass_number`，则将快照视为此遍历的过时——停止 "过时的 `active_snapshot`：遍历不匹配" 或降级为 HALT（`snapshot_pinned` 实际上为 false：没有权威的判断，区域 B NOT_MATCHED，重新生成 `not_attempted`）。这捕获了一个自定义 harness，它在阶段 15 的遍历增量中保留了 `active_snapshot` 而没有重新固定。参考元代理每次都会重新固定，所以这个检查永远不会在那里触发。区域 B 本身无法检测到这一点（它是 `snapshot_id`-only，而不是 `pass`-aware）。

**此阶段的 `SNAPSHOT_ID`：** 让 `SNAPSHOT_ID` 是如果提供 `--snapshot_id` 的值，否则是来自 `workspace/.mantis_state.json` 的 `active_snapshot.snapshot_id`。如果两者都不存在（没有 `--snapshot_id` 并且状态中没有 `active_snapshot`），或者区域 B 通过路径 1d（没有参数，当前目录）解析 `CODE_ROOT`，则 `SNAPSHOT_ID` 为不可用（模式关闭 = 今天的默认值）：将步骤 3 中的每个区域 B 检查视为 NOT_MATCHED，并将步骤 2 中的 KB 新鲜度门视为失败。不要停止；按以下方式降级。当 `active_snapshot` 存在但 `snapshot_pinned` 为 false（HALT 模式）时，`SNAPSHOT_ID` 是记录的 `live:` id 并且是可用的——区域 B 仍然返回 NOT_MATCHED（`snapshot_pinned` 为 false），但步骤 3c "模式关闭异常" 不会触发：NOT_MATCHED 结果被视为漂移 → `CONDITIONAL_VIABLE`，永远不会 `NON_VIABLE`（`mantis-calibrate` 会丢弃它）。

按以下方式执行批评评估：

1. **加载漏洞：** 读取 `workspace/findings/` 目录中的 JSON 文件。你必须加载所有漏洞，无论状态如何（包括 `"VALID"`，`"FALSE_POSITIVE"`，`"PROVISIONALLY_VALID"` 和 `"NEEDS_RESEARCH"`），以便它们可以被处理或记录到长期内存中。如果不存在，通知用户。

2. **评估全局仓库意图（KB 新鲜度门控）：** 读取 `workspace/kb/THREAT_MODEL.md`（如果存在）。检查 **部署意图** 部分。

   **KB 新鲜度门控——在执行任何大范围标记（3 状态规则）之前必须：** 确定 KB 是针对哪个快照构建的。从以下来源之一读取它（按顺序尝试，第一个匹配的获胜）：

   1. `workspace/kb/THREAT_MODEL.md` 的第一行的 `KB_SNAPSHOT:` 标记（威胁模型将其写入为裸头；架构写入每个 KB 文件上用注释包装的 `<!-- KB_SNAPSHOT: ... -->`）。对于架构文件，扫描 `KB_SNAPSHOT:` 子字符串，位于注释内。不要寻找 `kb_snapshot_id:` 或 `Snapshot:` — 这些标记永远不会被写入，门控永远不会匹配。
   2. 否则 `workspace/.mantis_state.json` 中的 `kb_snapshot_id` 值（架构在其状态戳步骤中写入它）。
   3. 否则 `""`（没有先前的 KB 来源）。以下的大范围标记受以下门控约束：

   - **模式关闭**（状态中没有 `active_snapshot` — 没有 `--sync`）：完全跳过新鲜度门控。允许大范围的 `SAMPLE_OR_TEST` 标记，如今天（今天的字节对字节行为）— KB 是针对实时树构建的，并且没有快照可以与之比较。
   - **HALT 或 PINNED**（`active_snapshot` 存在）：仅当记录的 `KB_SNAPSHOT:`（或 `kb_snapshot_id`）存在并且与上述定位解析中解析的当前 `SNAPSHOT_ID` 字节对字节相等时，才允许大范围标记。如果它缺失、为空或不等于 `SNAPSHOT_ID`，你绝不能大范围标记：完全跳过此大范围操作，并在步骤 3-5 中单独评估每个漏洞。

   只有当新鲜度门控通过（或在模式关闭中跳过）：如果威胁模型明确说明整个仓库完全是教程、示例项目或测试套件（例如，`Intent: SAMPLE_OR_TEST_ONLY`），你必须将所有漏洞标记为 **`SAMPLE_OR_TEST`**，无论它们在文件结构中的位置如何，并跳过剩余的每个漏洞可行性检查。

3. **获取目标代码片段（快照匹配）：** 对于每个状态为 `"VALID"` 或 `"PROVISIONALLY_VALID"` 的漏洞（跳过 `"FALSE_POSITIVE"` 或 `"NEEDS_RESEARCH"` 漏洞和后续评估步骤）：

   a. **从漏洞的 `code_paths` 中解析目标文件**，按照区域 A 步骤 3：`code_paths` 是快照相对的，所以它们在 `CODE_ROOT` 下读取。删除尾部的 `:<数字>` 以获取行号；`://` 表示 URL，不是文件；任何不是 `<路径>:<整数>` 形式的条目都是非源定位器——只进行存在检查，没有行逻辑。

   b. **快照匹配检查（区域 B）：** 通过将其 `discovery_commit` 与当前 `SNAPSHOT_ID` 进行比较，计算此漏洞的 `MATCHED` / `NOT_MATCHED`。

   ```
   漏洞 F 的快照匹配检查（决定 MATCHED vs NOT_MATCHED）：
   1. 如果 `snapshot_pinned` 为 false -> NOT_MATCHED。停止。
   2. 读取 F.discovery_commit:
      - 缺失 或 为空 或 字面值 "MIXED" -> NOT_MATCHED.
      - 不完全等于 `SNAPSHOT_ID`          -> NOT_MATCHED.
      - 完全等于 `SNAPSHOT_ID`              -> MATCHED.
   没有其他路线到 MATCHED；永远不会模糊比较。全局 "默认该字段并继续" 的向后兼容规则不适用于 `discovery_commit`：缺失 = NOT_MATCHED。 (没有单独的 "脏" 门控：脏树的 `SNAPSHOT_ID` 已经嵌入工作树内容哈希，所以在本遍历中的漏洞匹配，跨遍历的裸提交漏洞不匹配。)
   ```

   c. **漂移 / 缺失文件 / 超出范围保护（安全措施 — 永远不会 `NON_VIABLE`）：** 如果区域 B 产生 **NOT_MATCHED**，或者解析的目标文件在 `CODE_ROOT` 下不存在，或者指定的行号超出文件末尾（超出范围），则你必须不运行针对该漏洞的特定领域可行性分析（步骤 4-5），并且你必须不将其标记为 `NON_VIABLE`（缺失文件不是死代码；`NON_VIABLE` 是 `mantis-calibrate` 会丢弃的值）。

   **异常（仅模式关闭 — 没有活跃的 `active_snapshot`）：** 如果 `SNAPSHOT_ID` 不可用（模式关闭：状态中没有 `active_snapshot` 并且没有 `--snapshot_id`）并且 NOT_MATCHED 的唯一原因是缺失/不可用的 `SNAPSHOT_ID`（不是缺失文件或超出范围的行），将其视为 "无法比较" 并正常传递到评估（步骤 3d）。这保留了非同步运行时的今天的行为。在 HALT 模式（`active_snapshot` 存在，`snapshot_pinned=false`）中，此异常不会触发：区域 B 是 NOT_MATCHED，漏洞是漂移 → `CONDITIONAL_VIABLE`（下面的 "否则" 分支），永远不会 `NON_VIABLE`（`calibrate` 会丢弃）。缺失文件和超出范围的条件仍然强制 `CONDITIONAL_VIABLE`，无论固定或模式如何。

   **否则（漂移、缺失文件或超出范围）：** 设置 `production_viability` = **`CONDITIONAL_VIABLE`** 并写入一个漂移注释，命名原因，例如：
   `"快照漂移：discovery_commit=<disc> != 活跃的 SNAPSHOT_ID=<id>（或者目标文件/行在固定的快照中不再存在）；无法重新验证可行性，默认为 `CONDITIONAL_VIABLE`（保守）。"`
   然后，通过步骤 6 记录更新并继续到下一个漏洞。（此漏洞仍然在步骤 7 中记录为 `CONDITIONAL_VIABLE` 作为长期内存的一部分。）

   d. **匹配、文件存在、行在范围内：** 从 `CODE_ROOT` 读取目标文件，并至少读取指定行号周围的 **15 行前文** 和 **15 行后文**。这个目标窗口对于分析周围结构和宏定义是必要的。此外，检查 `repro_hints` 和 `history` 以检查 `mantis-reproduce` 记录的实证执行遥测（例如 `build_profile`，`sanitizers_used`，`assertions_disabled`，`ingress_blocked`）。使用此实证执行遥测来证实发布构建的可行性。继续到步骤 4-5。

4. **评估特定领域可行性约束：**

   - **对于内存安全漏洞：** 定位受影响的缓冲区的分配源。确定它是否以安全边界或尾部填充分配。如果越界访问包含在物理填充内，则将其标记为 **`NON_VIABLE`**。
   - **对于逻辑和授权漏洞：** 验证有缺陷的逻辑或绕过的端点是否在标准生产部署中实际可访问。如果漏洞依赖于仅用于调试的后门、模拟身份验证提供程序或仅用于测试的路由，则将其标记为 **`NON_VIABLE`**。

5. **确定可行性状态：** 为漏洞分配以下可行性状态之一，以确保我们优先级正确：

   - **`NON_VIABLE`**: 缺陷无法访问或在生产中编译出去。这包括：
     - **禁用的断言（内存漏洞）：** 依赖于标准 `assert()`，`debug_abort()` 或开发仅恐慌来触发崩溃/DoS 状态的 Bug，其中 `NDEBUG` 会删除它们，代码会安全返回。
     - **仅用于调试的功能：** 条件编译调试标志（例如 `#ifdef DEBUG`）。
     - **被环境控制阻挡：** 被标准、不可配置的生产环境控制阻挡（例如，OS 级权限、内核级沙盒、只读文件系统），这些控制无法绕过。
   - **`SAMPLE_OR_TEST`**: 问题存在于示例代码、测试套件、模糊测试 harness 或验证框架中。
   - **`CONDITIONAL_VIABLE`**: 缺陷仅在特定非默认配置、可选编译器标志或自定义硬化选项下可利用，这些选项可能跨生产环境变化。
   - **`VIABLE`**: 缺陷在标准发布/生产构建中完全可触发。

6. **令牌优化的文件更新：** 为了最小化 LLM 输出令牌，**不要重新发出或手动重写整个 JSON 对象。** 相反，使用原地编辑工具（例如你喜欢的语言中的短脚本，或 `jq`）以编程方式将新字段追加到现有的 `workspace/findings/<id>.json` 文件。

   你必须追加以下内容到现有对象：

   - 一个 `"production_viability"` 字段（`"VIABLE"`，`"NON_VIABLE"`，`"SAMPLE_OR_TEST"` 或 `"CONDITIONAL_VIABLE"`）。
   - 一个 `"critic_reasoning"` 字段解释你的评估。
   - `"history"` 数组中的一个条目：

   ```json
   {
     "stage": "critic",
     "action": "evaluated",
     "details": "确定了生产可行性为 [VIABLE/NON_VIABLE/SAMPLE_OR_TEST/CONDITIONAL_VIABLE] 因为 [原因]",
     "pass_number": <当前遍历编号>,
     "snapshot": "<SNAPSHOT_ID>",
     "timestamp": "<当前_iso8601时间戳>"
   }
   ```

   将 `"snapshot"` 设置为定位解析中解析的 `SNAPSHOT_ID`。如果 `SNAPSHOT_ID` 不可用（模式关闭），将其设置为 `""`（或省略该键）。不要编造一个 id。

7. **追加到长期内存：** 对于你加载的每个漏洞（包括 `NON_VIABLE`，`SAMPLE_OR_TEST`，`CONDITIONAL_VIABLE`，`FALSE_POSITIVE` 和 `NEEDS_RESEARCH`），追加一个结构化的 JSON 行到名为 `workspace/learnings.jsonl` 的工作区数据库文件（使用追加模式）。这确保了验证结果在运行之间被记住，帮助策略师避免重新扫描它们。

   - **内存条目格式：**
     `{"title": "[security_flaw_title]", "code_paths": ["[path1:line1]"], "status": "[VIABLE / CONDITIONAL_VIABLE / NON_VIABLE / SAMPLE_OR_TEST / FALSE_POSITIVE / NEEDS_RESEARCH]", "snapshot": "[当前 SNAPSHOT_ID, 或在模式关闭中省略]}`

完成时，通知用户。
