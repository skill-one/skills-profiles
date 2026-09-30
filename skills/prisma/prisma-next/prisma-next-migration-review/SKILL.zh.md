---
name: prisma-next-migration-review
description: 检查 Prisma Next 迁移将在合并或部署时运行的内容，渲染迁移图，解决并发/菱形收敛冲突，并配置 CI 的环境引用。用于“将要运行哪些迁移”、“部署时运行的内容”、“合并冲突”、“菱形收敛”、“并发迁移”、“迁移状态”、“引用管理”、“预发布环境”、“生产环境”、“MIGRATION.DIVERGED”、“MIGRATION.NO_MARKER”、“MIGRATION.MARKER_NOT_IN_HISTORY”、“prisma migrate status”、“prisma migrate diff”、“prisma migrate resolve”。
---

# Prisma Next — 迁移审查 (部署 + 并发)

> **编辑你的数据合约。Prisma 处理其余部分。**

这项技能是关于 *审查* 迁移，而不是编写它们。它涵盖了在部署时以及多个开发人员并发进行迁移时出现的问题。

这项技能教授 *系统的心智模型* — 什么是引用、什么是标记、什么是迁移图 — 并展示如何向系统查询其状态。它 **不** 规定僵化的分步程序：大多数“审查”问题都是通过理解模型并查询正确的内容来回答的。僵化的程序保留在极少数情况下确实只有一条安全路径的情况下。

## 何时使用

- 用户询问 *"我合并这个时，会运行哪些迁移？"* 或 *"部署将运行什么？*。
- 用户遇到并发迁移冲突（`main` 在他们的分支打开时前进）。
- 用户想要设置 `staging` / `production` 引用，以便 CI 可以针对它进行部署。
- 用户想要针对不是本地开发数据库的环境运行迁移。
- 用户询问迁移的 CI 集成。

## 何时不用

- 用户想要 *编写* 一个迁移 → `prisma-next-migrations`。
- 用户想要修复单个环境中的哈希不匹配 / 分歧 → `prisma-next-migrations`（重新规划路径）或 `prisma-next-debug`（基于信封）。
- 用户想要编辑合约 → `prisma-next-contract`。

## 关键概念 — 导航模型

**每个迁移问题都是从 *起点* 到 *终点* 的导航。** 一旦你有了这个模型，这项技能的其余部分只是 *"哪个命令向系统查询哪个导航？*"

### 起点

**起点** 是数据库的 *当前合约哈希*。数据库在 PN 的标记表中包含一行，记录 *"这个数据库位于哈希 X"*。当 CLI 在线运行（提供了 `--db <url>`，或在 `prisma-next.config.ts` 中设置了 `db.connection`）时，PN 读取标记，该哈希就是起点。离线（没有数据库连接），起点是未知的 — 许多命令会降级为列出磁盘上的迁移，并跳过每个边的已应用/待处理状态。

因此，一个活动的数据库是起点的权威来源。任何其他工件（引用、本地缓存、你的假设）中的“记录标记”只是一个工作副本，可能会漂移；活动数据库永远不会漂移。

### 终点

**终点** 是你希望数据库达到的合约哈希。命名终点的两种方式：

- **一个 `--to <name>`** — 指向哈希的命名指针，存储在 `migrations/app/refs/<name>` 下。引用按惯例命名为环境（`staging`、`production`）以传达 *"生产预期位于此处"*。引用本身只是一个哈希 + 一个可选的必需不变量集；它与连接到哪个数据库无关。
- **当前的合约头** — 当未传递 `--to` 时隐含。这是磁盘上当前 `contract.json` 的哈希。

`--to staging` **不** 意味着“连接到 staging 数据库”。它的意思是“导航我通过 `--db` 或配置连接到的数据库（指向此引用指向的哈希）。数据库选择是正交的：传递 `--db $STAGING_DATABASE_URL` 才能实际指向 staging。

### 迁移图

磁盘上的迁移形成一个有向图：**节点是合约哈希；边是迁移。** 每个迁移声明一个 `from` 哈希和一个 `to` 哈希。迁移仅在数据库的当前标记与其 `from` 哈希匹配时才应用；运行它会将标记推进到其 `to` 哈希。

`migration status` 查询图，从起点到终点，并报告每边的状态：

- **已应用** — 在从 `EMPTY_CONTRACT_HASH` 到标记的路径上（历史记录）。
- **待处理** — 在从标记到终点的路径上（将要运行的内容）。
- **无法到达** — 在从 `EMPTY_CONTRACT_HASH` 到终点的路径上，但标记位于不同的分支上，并且不会在不首先重新路由的情况下到达它。

### 诊断代码

`migration status` 在结果信封（`diagnostics[].code`）上发出结构化诊断，以便代理可以根据代码而不是解析文本摘要进行分支。每个诊断还携带 `severity`（`warn` 或 `info`）、人类可读的 `message` 和 `hints` — 与 CLI 在摘要行下打印的提示相同。

| 代码 | 严重性 | 导航模型中的含义 | 下一步 |
|---|---|---|---|
| `MIGRATION.UP_TO_DATE` | info | 标记 = 终点；没有需要遍历的边。 | 无需操作。 |
| `MIGRATION.DATABASE_BEHIND` | info | 标记是终点的祖先；之间有 N 个待处理的边。 | `migrate --to <name> --db $URL`。 |
| `MIGRATION.MISSING_INVARIANTS` | info | 标记在结构上达到终点，但缺少引用声明的必需不变量。 | `migrate --to <name> --db $URL` 以选择一条涵盖它们的路径。 |
| `MIGRATION.NO_MARKER` | warn | 在线，但数据库没有标记行 — 从未初始化。 | `migrate --db $URL`（首次应用会写入标记）。 |
| `MIGRATION.MARKER_NOT_IN_HISTORY` | warn | 在线；标记哈希不是图中的节点。数据库在迁移系统外部被更改。 | 确定哪一方是真相：`db sign`（接受数据库为真相）、`db update`（将合约推送到数据库）、`contract infer`（从数据库重新推导合约）、或 `db verify`（检查）。**不** 与 `MIGRATION.MARKER_MISMATCH` 相同：`MARKER_NOT_IN_HISTORY` 在运行者的图遍历期间发出，当活动标记不在遍历路径上时；`MARKER_MISMATCH` 在 CLI 预 DDL 阶段发出，当标记哈希根本不是图节点时。 |
| `MIGRATION.DIVERGED` | warn | 多个有效叶子；终点是模糊的。 | 传递 `--to <name>`，或 `ref set <name> <hash>` 来创建一个。 |
| `CONTRACT.AHEAD` | warn | 合约头不在图中 — 合约未经重新规划编辑。 | `migration plan` 以扩展图。 |
| `CONTRACT.UNREADABLE` | warn | `contract.json` 无法读取。 | `contract emit` 以重新生成它。 |

### 图树输出

`migration status`（以及 `migration list`）将迁移图渲染为终端中的彩色车道树。两个标志控制渲染：

- `--legend` — 在树之前打印树符号和车道颜色的键。
- `--ascii` — 用安全的 ASCII 字符替换框绘制符号（在 CI 日志或不受支持 Unicode 的环境中很有用）。

这两个标志也适用于 `migration list` 和 `migration graph`。`migration log` 仅支持 `--ascii`（它渲染一个扁平的按时间顺序的表，而不是树）。

### 计划和应用时的诊断

这些代码出现在 `migration plan`、`ref set` 和 `migrate` — 不出现在 `migration status`。参见 [迁移系统 § 恢复功能](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#recovery-affordances) 和 [ADR 218](../../docs/architecture%20docs/adrs/ADR%20218%20-%20带有配对合约快照和通用图节点不变量的引用.md)。

| 代码 | 何时 | 含义 | 下一步 |
|---|---|---|---|
| `MIGRATION.HASH_NOT_IN_GRAPH` | `migration plan`（非空图）或 `ref set` | 解析的哈希不是磁盘迁移图中的节点 — 在开发仅 `db update` 循环后默认 `db` 引用指向图尖端之后很常见。 | `migration plan --from <可到达引用>`（例如 `--from production`）；或使用 `ref set db <图节点哈希>` 对齐引用。 |
| `MIGRATION.SNAPSHOT_MISSING` | `migration plan` | 命名引用没有指向文件（`<name>.json`），并且解析的哈希也不是迁移图中的节点。 | `ref set <name> <hash>` 来创建引用，`db update --advance-ref <name>` 来推进它，或传递一个图节点中的哈希。 |
| `MIGRATION.MARKER_MISMATCH` | `migrate`（预 DDL，运行者之前） | 活动数据库标记哈希不是图节点 — 离线规划器无法看到的漂移。 | `migration plan --from <图尖端>` 如果标记是规范的；`ref set db <标记哈希>` 如果磁盘图是规范的；调查外部的应用。 |
| `MIGRATION.PATH_UNREACHABLE` | `migrate`（路径解析） | 在磁盘图中从当前标记到解析的目标没有迁移路径。 | 阅读改进的 `fix` 负载 — 它命名 `fromHash` / `targetHash` 并建议 `migration plan --from <from> --to <target>`；运行 `migration list` 检查图。 |

CI 网关应从 `--json` 输出中读取 `diagnostics` 并根据 `严重性` 加上 `代码` 进行决策；见下文 *工作流 — CI* 的结构。

## 工作流 — *"部署将运行什么？"*

用户询问：*"我即将合并这个 PR。当我部署到 staging 时，将运行哪些迁移？*"

这是一个导航问题：**起点** = staging 的活动标记；**终点** = 引用 `staging`（如果你没有设置，则为合约头）。向系统查询：

```bash
pnpm prisma-next migration status --to staging --db "$STAGING_DATABASE_URL"
```

该命令：

1. 读取 staging 数据库的标记（起点）。
2. 解析 `staging` 为一个合约哈希（终点）。
3. 将它们之间的路径渲染为按顺序排列的迁移列表，带有每边的 `已应用` / `待处理` / `无法到达` 状态，以及一个明确的摘要行 *"N 个迁移落后于引用 'staging'"*。
4. 打印一个标头，命名配置、迁移目录、活动引用和数据库连接（掩码） — 这样可以在输出中看到上下文。

如果你省略 `--db`，命令将离线运行：它列出磁盘上的迁移，但无法告诉你已应用的内容，因为它没有起点。这对于 *"这个分支上有什么？"* 很好；对于 *"部署到 staging 将运行什么？"* 不行 — 你需要 staging 的活动标记。

如果你省略 `--to`，终点默认为合约头 — 这回答了 *"这个分支的合约能否从数据库到达，以及如何？"*，而不是 *"部署将运行什么？"*。当问题是关于特定环境时，请明确传递引用。

`migration status` 通过类别（`additive`、`widening`、`data`、`destructive`）总结每个待处理迁移的操作，并在存在破坏性操作时报告破坏性操作计数。在用户合并或部署之前向他们显示该计数 — 破坏性操作是需要手动审查的类别。

## 工作流 — *"每个环境处于什么状态？"*

只需对每个环境数据库运行 `migration status --db $URL`。标记（起点）来自数据库本身；摘要行告诉您环境是否处于合约头、命名引用、领先于头或位于分支上。

## 概念 — 同一分支点上的并发迁移

这以前在某些 PN 文档中称为 *菱形收敛*；无论标签如何，情况都相同。

**正在发生什么。** 两个主题分支各自在相同的父合约哈希上编写了迁移。第一个分支合并到 `main`；目标引用（例如 `production`）前进到该分支的 `to` 哈希。你的分支的迁移仍然将其 `from` 哈希指向 *旧的* 父。在重置后，迁移图不再有通过你的迁移的干净路径：

- 你的迁移的 `from` 不再是新头的祖先。
- 或者你的迁移的 `from` 是可到达的，但通过你的迁移的路径到达的哈希不是两个分支更改的并集。

无论如何，磁盘上的计划都已过时。

**解决方法。** 磁盘上的计划已过时，因为它的 `from` 哈希不再是图的头部；应用集群的标准 *编辑 → 计划 → 应用* 循环到重置后的状态，规划器将生成一个新的迁移，其 `from` 与新头匹配。

**规划器无法为你做的一件事** 是将自定义数据转换逻辑从被放弃的 `migration.ts` 移植到新的迁移中 — 模式差异是从合约派生的，但任何手写的 `data` 操作都需要你在应用之前携带。没有单独的“重新验证”步骤，没有特殊的“菱形应用”流程。

## 工作流 — 设置、列出、获取、删除引用

引用是小的工件。没有每个环境的生命周期；你只是将一个名称指向一个哈希。

```bash
pnpm prisma-next ref set production <contract-hash>
pnpm prisma-next ref list
# `ref get` 已被移除 — 使用 `ref list` 并按名称过滤
pnpm prisma-next ref list | grep production
pnpm prisma-next ref delete production
```

`ref set` 在 `migrations/app/refs/<name>` 处写入一个文件，其中包含哈希和任何必需的不变量。引用是提交友好的工件 — 将它们放在 git 中；团队同意 `production` 指向什么，就像他们同意 `main` 是什么一样。

## 工作流 — 对环境应用迁移

```bash
pnpm prisma-next migrate --to production --db "$PRODUCTION_DATABASE_URL"
```

终点是引用的哈希；起点是生产数据库的活动标记。该命令计算它们之间的路径，并按顺序应用每个待处理的迁移，推进标记。

`--db` 是环境选择旋钮。`--to` 是终点哈希旋钮。它们是独立的。

## 概念 — CI / 部署上的引用不匹配

CI 报告：*"记录的引用 `production` 位于哈希 X；活动数据库位于哈希 Y。*"

不匹配是关于 *两个不一致的状态的事实*。调查与哪个部分错误无关：

- **数据库领先于引用。** 有人在不属于 CI 的情况下应用了迁移，而没有在 git 中更新引用。使用 `prisma-next ref set <ref-name> <db-marker-hash>`（提交 + 推送）重新记录引用；然后审计如何发生的外部应用。
- **数据库落后于引用。** 以前的部署被回滚，或者数据库从较旧的备份恢复。无论使用 `prisma-next migrate --to <ref-name> --db $URL` 向前重新应用，还是使用 `prisma-next ref set <ref-name> <db-marker-hash>` 将引用向后重新路由以匹配实际部署的内容。选择是用户的 — 名称这两个选项。
- **数据库位于不同的分支上。** 一个外部模式更改（手动 SQL、临时迁移）写入了一些迁移图没有建模的内容。运行 `prisma-next db verify` 以检查漂移，然后要么使用 `prisma-next contract infer` 从数据库重新推导合约，要么编辑合约并运行 `prisma-next migration plan` 以使数据库成为最终目的地。

使用 `ref set` 默默地将引用与数据库当前所处的任何内容对齐几乎从不正确。它掩盖了你将来需要为它付出代价的漂移。

## 工作流 — CI：验证分支可以推进目标环境

网关是 `migration status --to <env> --db $URL`：它计算从活动标记到引用的路径并报告它，而不进行任何更改。没有 `--dry-run` 标志在 `migrate` 上；检查/网关步骤是 `migration status`。

对于在应用之前的人类可读的迁移路径顺序预览，请使用 `migrate --show --db $URL`。对于部署后的应用历史，请使用 `migration log --db $URL`（扁平的按时间顺序的表）。

```yaml
- name: Verify staging is reachable
  run: |
    pnpm prisma-next migration status \
      --to staging --db "$STAGING_DATABASE_URL" --json > status.json
    node -e '
      const s = JSON.parse(require("fs").readFileSync("status.json", "utf8"));
      const warns = (s.diagnostics ?? []).filter(d => d.severity === "warn");
      if (warns.length) {
        console.error("Blocking diagnostics:", warns);
        process.exit(1);
      }
    '
- name: Apply
  run: pnpm prisma-next migrate --to staging --db "$STAGING_DATABASE_URL"
```

`migration status` 仅在硬错误（不可读的迁移目录、无法满足的不变量、无法重建的历史）的情况下退出非零。像 `MIGRATION.MARKER_NOT_IN_HISTORY`、`MIGRATION.DIVERGED`、`CONTRACT.AHEAD` 和 `MIGRATION.NO_MARKER` 这样的诊断以 `severity: 'warn'` 报告，但进程退出 `0` — 代理（或 CI 网关）必须检查 `diagnostics[]` 并自行失败构建。使用 `--json` 以便网关解析结构化形状，而不是人类摘要。

`migrate` 命令无需交互，且没有破坏性操作的确认提示——用于提示破坏性更改的安全护栏存在于 `db update`（参见 `prisma-next-migrations` 技能）。规划器放入迁移图中的任何内容都是 `migrate` 执行的内容；审查发生在 `migration plan` 和 `migration status` 阶段，在应用步骤之前。

## 常见陷阱

1. **在部署问题时未使用 `--to` 读取 `migration status`。** 这会询问 *"这个分支的合约能否达到主分支？"*，而不是 *"即将在测试环境中运行什么？"*。当问题涉及特定环境时，请始终传递引用。
2. **在部署问题时未使用 `--db` 读取 `migration status`。** 没有实时数据库，你就没有原始数据。输出列出了磁盘上的内容；它无法说明环境中已应用的内容。对于任何高风险问题，请传递 `--db $URL`。
3. **将引用与数据库连接混淆。** `--to staging` 选择目标哈希值，而不是数据库。请明确传递 `--to` 和 `--db`。
4. **将菱形收敛视为特殊流程。** 它不是。这是应用于 rebase 后状态的正常 *编辑 → 规划 → 应用* 循环。唯一额外的步骤是 *"将旧 `migration.ts` 中的任何数据转换逻辑迁移过来。*"
5. **在未理解原因的情况下运行 `ref set` 来消除 CI 不匹配。** 这会掩盖外部更改或回滚漂移。先进行调查。

## Prisma Next 尚未实现的功能

- **超出默认链的按环境迁移排序。** 如果你需要测试环境跳过生产环境所需的迁移（反之亦然），支持的方法是作为单独的迁移编写按环境分叉的迁移，并在部署脚本中设置门禁。如果你需要按环境的一流路由，请通过 `prisma-next-feedback` 技能提交功能请求。
- **内置的并排“分支差异”视图。** 存在一个完整图渲染 (`migration graph`)，显示分支，但没有 `git diff` 风格的两个分支迁移集之间的比较。解决方法：在每个分支上运行 `migration status` 并 `diff` 输出。如果你需要一个内置的分支比较视图，请通过 `prisma-next-feedback` 技能提交功能请求。

## 参考文件

此技能有意仅包含正文；底层 CLI 参考 (`prisma-next migration status --help`, `migrate --help`, `ref --help`) 是标志级细节的权威表面。如有疑问，请运行 `--help` 并阅读实际命令的描述，而不是根据此技能猜测。

## 检查清单

- [ ] 为用户提出的问题指定了 **原始数据**（实时数据库标记）和 **目标**（引用或合约头）。
- [ ] 在涉及特定环境的问题时，传递了 `--db $URL`。
- [ ] 在关于部署到命名环境的问题时，传递了 `--to <name>`，而不仅仅是当前分支头的 *从*。
- [ ] 在读取每个边的列表之前，阅读了 `migration status` 标题（它命名了配置、引用、数据库）和摘要行（它命名了原始数据/目标距离）。
- [ ] 对于并发迁移冲突：重新应用了 *核心* 工作流（编辑 → 规划 → 应用），而不是遵循记忆中的“菱形收敛”程序。将任何数据转换逻辑从放弃的 `migration.ts` 迁移过来。
- [ ] 对于引用不匹配：调查了 *哪个* 状态部分是错误的（数据库超前、数据库滞后、数据库位于分叉分支）。没有使用 `ref set` 来消除不匹配。
- [ ] 在部署之前，从 `migration status` 中暴露了破坏性操作计数（唯一需要手动审查的 操作类别），然后用户合并或部署。
- [ ] 在 CI 中：解析了 `migration status --json` `diagnostics[]` 并基于 `severity === 'warn'` 设置门禁；没有依赖 `migrate` 的 `--dry-run` 标志（该标志不存在）。
- [ ] 没有 将 `--to` 与数据库选择混淆 (`--to` 选择目标哈希值；`--db` 选择数据库)。
- [ ] 没有 使用 `--ref`（已移除；使用 `--to`）。
- [ ] 没有 编造“分支差异”CLI 子命令、`migration revalidate` 步骤或任何其他上述技能未引用的 API。
