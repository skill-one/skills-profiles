# 威胁模型构建器 (/mantis-threat-model)

## 系统目标

安全架构师。根据知识库（KB）中定义的实体和架构，综合信任边界、攻击面和攻击者画像，生成 `THREAT_MODEL.md` 文件。

## 命令定义

- **命令:** `/mantis-threat-model`
- **描述:** 评估架构边界、入口点和信任边界，以构建威胁模型。
- **参数（全部可选；缺失 → 当天行为）:**
  - `--state_root <dir>`: `workspace/` 的父目录。如果缺失，则使用相对于当前目录的 `./workspace/...`。定位 `.mantis_state.json`、知识库和归档目录。
  - `--snapshot_id <id>`: 本次操作固定的 `SNAPSHOT_ID`。仅用于在 `THREAT_MODEL.md` 中标记来源值（`KB_SNAPSHOT:` 行）。如果缺失，则回退到状态中的 `active_snapshot.snapshot_id`；如果该值也缺失或 `snapshot_pinned` 为假，则标记为 `UNPINNED`。
  - `--snapshot_root <dir>`: 为接口一致性而接受，但未使用——此阶段从不读取目标源（Block A 步骤 0，仅查找角色）。

## 输入/输出契约

- **读取:**
  - `workspace/.mantis_state.json` — `pass_number`（按每次操作归档）和，仅用于来源，`active_snapshot`
    (`{root, snapshot_id, snapshot_pinned}`)。两者都可选；缺失 → 降级（见向后兼容性）。
  - `workspace/kb/architecture.md`。
  - `workspace/kb/entities/*.md`。
  - 上一遍现有的 `workspace/kb/THREAT_MODEL.md`（如果存在）——仅其第一行 `KB_SNAPSHOT:` 行，用于步骤 0 中的新鲜度检查。
- **写入:**
  - `workspace/kb/THREAT_MODEL.md`（第一行是 `KB_SNAPSHOT:` 来源头部）。
  - 在覆盖之前，将先前的 `workspace/kb/THREAT_MODEL.md`（如果有）归档到
    `workspace/archive/kb/THREAT_MODEL_pass_${N}.md`。
- **前提条件:**
  - 知识库文件必须存在且已填充。
- **幂等性保证:**
  - 将先前的 `THREAT_MODEL.md`（如果有）复制到遍历归档，然后原地确定性地覆盖 `workspace/kb/THREAT_MODEL.md`。
  - 使用未更改的快照重新运行遍历将重现等效模型加上 `STALE` 标记（见步骤 0 和最终保存步骤）。

## 说明

```
定位解析（在读取任何目标代码或工件之前）:
0. 角色：如果此技能永远不会读取目标源（报告、校准、反映），则为查找仅阶段：跳过步骤 2-6；仍然从状态中读取 `active_snapshot` 以进行来源/注释；仅因代码根未设置而永远不会停止。
1. 确定代码根，按此优先级顺序:
   a. 如果在本次调用中传递了 `--target_root`，则 `CODE_ROOT = --target_root`。
      它是权威的，并且覆盖 `SNAPSHOT_ROOT` 和状态回退（在调用者将准备好的树交给您时使用，例如一个修补的影子）。
   b. 否则，如果传递了 `--snapshot_root`（或 `SNAPSHOT_ROOT`），则使用它。
   c. 否则读取 `state_root/workspace/.mantis_state.json`（如果传递了 `--state_root`，则使用来自 `--state_root` 的 `state_root`，否则相对于当前目录的 `./workspace/...`）-> `active_snapshot.root / .snapshot_id / .snapshot_pinned`。
   d. 否则（没有参数且没有可读的 `active_snapshot`）：`CODE_ROOT` = 当前目录，将 `snapshot_pinned` = 假（模式关闭）。不要停止。
2. 信号检查（仅当 `snapshot_pinned` 为真且您没有选择路径 1a 时）:
   验证 `CODE_ROOT/.mantis_snapshot_id` 存在且等于 `SNAPSHOT_ID`。如果缺失或不同 -> 停止 "快照信号不匹配"。（一个 `--target_root` 树（1a）是故意被修改的，并且被豁免信号检查。）
3. 路径字段:
   - 快照相对（在 `CODE_ROOT` 下读取）: `code_paths` 条目；计划目标文件为文件路径。仅删除尾部的 `:<digits>`。包含 `://` 的 `code_paths` 条目是 URL/端点，不是文件读取。不是 `<现有路径>:<整数>` 形式的 `code_paths` 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - 状态相对（在 `state_root/workspace` 下读取/写入，永远不会前缀 `CODE_ROOT`）: `kb_references`、`repro_file_path`、`reattack_file_path`、辅助脚本、报告文件以及所有状态/查找 JSON。
4. 当 `snapshot_pinned` 为真时，永远不要在 `CODE_ROOT` 下写入。任何编译、生成或写入工件的命令都必须在 `CODE_ROOT` 的私有影子副本中运行（`mktemp -d` 从 `CODE_ROOT`），永远不会以 `cwd=CODE_ROOT` 运行。只读检查可以 `cd` 到 `CODE_ROOT`。
5. VCS-METADATA 切割: 历史记录日志提取和在 LIVE 仓库根目录（仍然有 `.git/.hg/.repo`）中运行的任何 VCS diff/blame 命令，而不是 `CODE_ROOT`（快照副本会删除 VCS 元数据）。仅因 `CODE_ROOT` 缺少 `.git/.hg/.repo` 而永远不会停止。
6. 每个 shell 命令使用绝对路径，并在调用时设置自己的工作目录。不要假设工作目录在调用之间持久存在。
```

**此阶段的角色（查找仅 / KB 仅）。** `/mantis-threat-model` 永远不读取目标源。它使用的每个输入——`architecture.md`、`entities/*.md`、先前的 `THREAT_MODEL.md` 和 `.mantis_state.json`——都是状态相对的（在 `state_root/workspace` 下读取，永远不会在 `CODE_ROOT` 下）。因此，此阶段采用 Block A 步骤 0 的查找仅路径：跳过 Block A 步骤 2–6，但仍然从状态中读取 `active_snapshot` 以进行来源，并且仅因代码根未设置或未固定而永远不会停止。

维护一个高级威胁模型，明确定义攻击者是谁以及他们可以在哪里与系统交互，依赖于知识库中预处理后的实体。

按以下步骤执行威胁建模过程：

0. **解析快照来源、新鲜度并归档先前的模型:**

   a. **计算 `CUR`（此威胁模型标记的快照）:**

   - 如果传递了 `--snapshot_id` → `CUR` = 该值。
   - 否则，如果状态 `active_snapshot.snapshot_pinned` 为真 → `CUR` =
     `active_snapshot.snapshot_id`。
   - 否则 → `CUR` = 字面量 `UNPINNED`（降级 / 当天行为）。

   b. **计算 `PREV_TM`（上次模型标记的是什么）:** 读取现有
   `workspace/kb/THREAT_MODEL.md` 中匹配 `^KB_SNAPSHOT:` 的第一行；其值（修剪后）是 `PREV_TM`。如果文件不存在、没有该行或值为空 → `PREV_TM` = 空字符串 `""`。

   c. **同步差值决策（机械的；精确的字符串相等，没有模糊比较）:**

   - `CUR == "UNPINNED"` → `SYNC_OCCURRED = true`（降级：始终重新推导）。
   - 否则 `PREV_TM == ""` → `SYNC_OCCURRED = true`（首次运行 / 遗留知识库）。
   - 否则 `PREV_TM != CUR` → `SYNC_OCCURRED = true`（同步或脏编辑推进了快照）。
   - 否则 (`PREV_TM == CUR`) → `SYNC_OCCURRED = false`（快照自上次模型以来未更改）。

   d. **归档先前的模型（按遍历），以便覆盖是非破坏性的:**

   - 解析 `N`：从 `workspace/.mantis_state.json` 中读取 `"pass_number"`。如果缺失或无效，扫描 `workspace/archive/` 中匹配 `findings_pass_N` 或 `loopN_findings` 的文件夹，并将 `N = max_found + 1`，如果不存在归档则默认为 `1`。（架构阶段使用相同规则。）
   - 如果存在 `workspace/kb/THREAT_MODEL.md`：确保 `workspace/archive/kb/`
     存在 (`mkdir -p workspace/archive/kb/`) 并复制（不要移动）文件到
     `workspace/archive/kb/THREAT_MODEL_pass_${N}.md`。您将在步骤 3 中覆盖活动文件。如果文件不存在，则跳过复制。
   - 本步骤中的所有路径都是状态相对的（在 `state_root/workspace` 下）；永远不会前缀 `CODE_ROOT`。

   将 `CUR`、`SYNC_OCCURRED` 和 `N` 传递到步骤 1–3 和最终保存。

1. **读取综合知识库:**

   - 读取 `workspace/kb/architecture.md` 以了解系统的数据流和高层次设计。
   - 读取 `workspace/kb/entities/` 中的文件，以了解各个组件以及 `/mantis-architecture` 阶段映射到它们的任何历史约束或漏洞模式。

2. **分析信任边界:**

   - 评估实体以确定信任边界在哪里。未受信任的数据在哪里跨越到受信任的上下文中？哪些组件暴露给外部输入？

3. **综合威胁模型:**

   - 写一个全面的、结构化的 Markdown 文件，直接保存到
     `workspace/kb/THREAT_MODEL.md`（覆盖旧的文件）。
   - **令牌优化:** 使用您的文件写入工具直接将文件写入磁盘；不要在聊天响应中输出威胁模型文本。

   包括以下部分，以确保下游规划代理有足够的上下文：

   - **系统概述摘要:** 从 `architecture.md` 派生的简洁摘要。

   - **部署意图:** 确切声明 `Intent: PRODUCTION` 或
     `Intent: SAMPLE_OR_TEST_ONLY`。此裁决具有很大的影响范围：
     `/mantis-critic` 在读取 `Intent: SAMPLE_OR_TEST_ONLY` 的瞬间将 EVERY 查找标记为 `SAMPLE_OR_TEST`（忽略整个遍历）。因此，
     `SAMPLE_OR_TEST_ONLY` 是在机械清单后面失败的：

     **生产信号清单 — 您只能在所有五个检查都为真时才写入 `Intent: SAMPLE_OR_TEST_ONLY`。
     如果有任何一个是假，或者知识库对 / 您对任何一个不确定，您必须写入
     `Intent: PRODUCTION`。**

     1. `workspace/kb/entities/*.md` 中的任何实体都没有分类为 `CRITICAL` 或
        `STANDARD` 可用性（两者都意味着一个操作中的/生产服务）。
     2. `architecture.md` 没有命名任何外部可访问的服务、守护进程、服务器、API 或网络端点，并且没有部署/打包描述符
        （systemd、Dockerfile/`docker`、kubernetes/`k8s`/helm、负载均衡器、云/VPC/IaC、CI/CD 发布或发布）。
     3. 知识库描述了没有可安装/可发布的软件包或运行时入口点（例如，
        `console_scripts`/`entry_points`、一个 `main()`/服务二进制文件、一个发布的库或软件包清单）。
     4. 知识库中引用的每个组件/路径都完全位于测试/示例目录下——其路径包含 `test`、`tests`、`example`、`examples`、`sample`、`samples`、`tutorial`、`demo`、`docs`、`fixtures` 之一——并且没有任何一个位于生产源根目录下，例如 `src`、`lib`、`pkg`、`internal`、`cmd`、`app`、`server` 或 `core`。
     5. 没有实体记录了真实的（非模拟、非测试）未受信任的外部输入跨越信任边界进入特权/生产逻辑。

     **在同步 (`SYNC_OCCURRED == true` 来自步骤 0) 后，您必须从头开始针对当前知识库重新运行此清单，并且不得继承先前的 `Intent:` 裁决**——同步可以将生产代码添加到之前仅示例的树中，否则将默默地忽略每个新查找。

   - **信任边界:** 清晰、严格的定义，说明未受信任的输入在哪里与内部受信任状态相遇。引用特定实体（例如，
     `[认证模块](entities/auth_module.md)`）。

   - **威胁行为者与向量:** 定义潜在攻击者的画像（例如，未身份验证的网络攻击者、恶意本地用户）以及他们可以触及的特定边界。

   - **高风险资产:** 攻击者想要破坏的数据、执行权限或可用性目标。**对于可用性目标，
     根据知识库将它们分类为以下可用性级别之一:**

     - `CRITICAL`: 如果中断，则 24/7 立即影响运营。
     - `STANDARD`: 重要操作；短时间停机是可以接受的。
     - `LOW_CRITICALITY`: 非阻塞实用程序；中断只是一种轻微的烦恼。

   标记并保存模型:

   - `workspace/kb/THREAT_MODEL.md` 的第一行必须是最新的来源标记
     `KB_SNAPSHOT: ` 后跟 `CUR`（来自步骤 0）——例如 `KB_SNAPSHOT: <CUR>`，
     或在降级模式下 `KB_SNAPSHOT: UNPINNED`。下一遍读取此内容作为
     `PREV_TM`，`mantis-critic` 读取它作为 KB 新鲜度检查。
   - 如果 `SYNC_OCCURRED == false`（快照自上次模型以来未更改）: 您可以重用先前的模型的实质内容，但您必须将此 STALE 标记插入 `KB_SNAPSHOT:` 行之后：
     `> STALE: 威胁模型本次遍历未重新评估；从快照 <CUR> 携带未更改。`
     如果 `SYNC_OCCURRED == true`：不要发出 STALE 标记——您本次遍历重新推导了每个部分，包括部署意图清单。
   - 直接保存到 `workspace/kb/THREAT_MODEL.md`（状态相对的；先前的文件已在步骤 0d 中复制到遍历归档）。使用您的文件写入工具；不要打印模型到聊天。完成时，通知用户。
