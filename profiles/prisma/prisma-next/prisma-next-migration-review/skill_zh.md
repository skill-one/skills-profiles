# Prisma Next — 迁移审查（部署 + 并发）

> **编辑你的数据合约。Prisma 处理其余部分。**

这项技能是关于 *审查* 迁移，而不是编写它们。它涵盖了在部署时以及多个开发人员并发部署迁移时出现的问题。

这项技能教授 *系统的概念模型* — 什么是引用、什么是标记、什么是迁移图 — 并展示如何向系统查询其状态。它 **不** 规定僵化的分步程序：大多数“审查”问题都是通过理解模型并查询正确的内容来回答的。僵化的程序保留在极少数情况下确实只有一条安全路径的情况下。

## 何时使用

- 用户询问“我合并这个时，会运行哪些迁移？”或“部署将运行什么？”。
- 用户遇到并发迁移冲突（`main` 在他们的分支打开时前进）。
- 用户想要设置 `staging` / `production` 引用，以便 CI 可以针对它进行部署。
- 用户想要针对不是本地开发数据库的环境运行迁移。
- 用户询问迁移的 CI 集成。

## 何时不使用

- 用户想要 *编写* 一个迁移 → `prisma-next-migrations`。
- 用户想要修复单个环境中的哈希不匹配 / 分叉 → `prisma-next-migrations`（重新规划路径）或 `prisma-next-debug`（信封驱动）。
- 用户想要编辑合约 → `prisma-next-contract`。

## 关键概念 — 导航模型

**每个迁移问题都是从 *起点* 到 *终点* 的导航。** 一旦你有了这个模型，这项技能的其余部分就是“哪个命令向系统查询哪个导航。”

### 起点

**起点** 是数据库的 *当前合约哈希*。数据库在 PN 的标记表中携带一行，记录“这个数据库位于哈希 X”。当 CLI 在线运行（提供了 `--db <url>`，或在 `prisma-next.config.ts` 中设置了 `db.connection`）时，PN 读取标记，该哈希就是起点。离线（没有数据库连接），起点是未知的 — 许多命令会降级为列出磁盘上的迁移，并跳过每个边的已应用/待处理状态。

因此，一个活动的数据库是起点的权威来源。任何其他工件（引用、本地缓存、你的假设）中的“记录标记”只是一个工作副本，可能会漂移；活动的数据库永远不会漂移。

### 终点

**终点** 是你希望数据库位于的合约哈希。命名终点的两种方式：

- **一个 `--to <name>`** — 指向哈希的命名指针，存储在 `migrations/app/refs/<name>` 下。引用按惯例以环境命名（`staging`、`production`）来传达“生产预期位于此处”。引用本身只是一个哈希 + 一个可选的必需不变量集；它与连接到哪个数据库无关。
- **当前的合约头** — 当未传递 `--to` 时隐式指定。这是磁盘上当前 `contract.json` 的哈希。

`--to staging` **不** 意味着“连接到 staging 数据库”。它意味着“导航我连接的数据库（通过 `--db` 或配置）朝向这个引用指向的哈希。”数据库选择是正交的：传递 `--db $STAGING_DATABASE_URL` 才能实际指向 staging。

### 迁移图

磁盘上的迁移形成一个有向图：**节点是合约哈希；边是迁移。** 每个迁移声明一个 `from` 哈希和一个 `to` 哈希。只有在数据库的当前标记匹配其 `from` 哈希时，迁移才会应用；运行它会将标记推进到其 `to` 哈希。

`migration status` 查询图，从起点到终点，并报告每边的状态：

- **已应用** — 在从 `EMPTY_CONTRACT_HASH` 到标记的路径上（历史记录）。
- **待处理** — 在从标记到终点的路径上（将要运行的内容）。
- **无法到达** — 在从 `EMPTY_CONTRACT_HASH` 到终点的路径上，但标记位于不同的分支上，并且不会在不首先重新路由的情况下到达它。

### 诊断代码

`migration status` 在结果信封（`diagnostics[].code`）上发出结构化诊断，以便代理可以根据代码而不是解析文本摘要进行分支。每个诊断还携带 `severity`（`warn` 或 `info`）、人类可读的 `message` 和 `hints` — 这是 CLI 在摘要行下方打印的相同提示。

| 代码 | 严重性 | 导航模型中的含义 | 下一步操作 |
|---|---|---|---|
| `MIGRATION.UP_TO_DATE` | info | 标记 = 终点；没有需要遍历的边。 | 无需操作。 |
| `MIGRATION.DATABASE_BEHIND` | info | 标记是终点的祖先；之间有 N 个待处理的边。 | `migrate --to <name> --db $URL`。 |
| `MIGRATION.MISSING_INVARIANTS` | info | 标记在结构上达到终点，但缺少引用声明的必需不变量。 | `migrate --to <name> --db $URL` 以采取覆盖它们的路径。 |
| `MIGRATION.NO_MARKER` | warn | 在线，但数据库没有标记行 — 从未初始化。 | `migrate --db $URL`（首次应用会写入标记）。 |
| `MIGRATION.MARKER_NOT_IN_HISTORY` | warn | 在线；标记哈希不是图中的节点。数据库在迁移系统之外被更改。 | 确定哪一方是真相：`db sign`（接受数据库为真相）、`db update`（将合约推送到数据库）、`contract infer`（从数据库重新推导合约）、或 `db verify`（检查第一个）。**不** 与 `MIGRATION.MARKER_MISMATCH` 相同：`MARKER_NOT_IN_HISTORY` 在运行者的图遍历期间发出，当实时标记不在遍历的路径上时；`MARKER_MISMATCH` 更早发出，在 DDL 预处理阶段，当标记哈希根本不是图节点时。 |
| `MIGRATION.DIVERGED` | warn | 多个有效叶子；终点是模糊的。 | 传递 `--to <name>`，或 `ref set <name> <hash>` 来创建一个。 |
| `CONTRACT.AHEAD` | warn | 合约头不在图中 — 合约未经重新规划而被编辑。 | `migration plan` 以扩展图。 |
| `CONTRACT.UNREADABLE` | warn | `contract.json` 无法读取。 | `contract emit` 以重新生成它。 |

### 图树输出

`migration status`（以及 `migration list`）将迁移图作为彩色车道树在终端中渲染。两个标志控制渲染：

- `--legend` — 在树之前打印树符号和车道颜色的键。
- `--ascii` — 用安全的 ASCII 字符替换框绘制符号（在 CI 日志或不受支持 Unicode 的环境中很有用）。

这两个标志也适用于 `migration list` 和 `migration graph`。`migration log` 仅支持 `--ascii`（它渲染一个扁平的按时间顺序的表，而不是树）。

### 计划和应用时的诊断

这些代码出现在 `migration plan`、`ref set` 和 `migrate` — 不出现在 `migration status`。参见 [迁移系统 § 恢复功能](../../docs/architecture%20docs/subsystems/7.%20Migration%20System.md#recovery-affordances) 和 [ADR 218](../../docs/architecture%20docs/adrs/ADR%20218%20-%20带有配对合约快照的引用和通用图节点不变量.md)。

| 代码 | 何时 | 含义 | 下一步操作 |
|---|---|---|---|
| `MIGRATION.HASH_NOT_IN_GRAPH` | `migration plan`（非空图）或 `ref set` | 解析的哈希不是磁盘迁移图中的节点 — 在开发专用 `db update` 循环后，默认 `db` 引用指向图尖端之后时典型。 | `migration plan --from <可到达引用>`（例如 `--from production`）；或使用 `ref set db <图节点哈希>` 对齐引用。 |
| `MIGRATION.SNAPSHOT_MISSING` | `migration plan` | 命名引用没有指向文件（`<name>.json`），并且解析的哈希也不是迁移图中的节点。 | `ref set <name> <hash>` 来创建引用，`db update --advance-ref <name>` 来推进它，或传递一个图节点是图节点的哈希。 |
| `MIGRATION.MARKER_MISMATCH` | `migrate`（DDL 之前，运行者之前） | 实时数据库标记哈希不是图节点 — 离线规划器无法看到的漂移。 | `migration plan --from <图尖端>` 如果标记是规范的；`ref set db <标记哈希>` 如果磁盘图是规范的；调查外部应用。 |
| `MIGRATION.PATH_UNREACHABLE` | `migrate`（路径解析） | 在磁盘图中从当前标记到解析的目标没有迁移路径。 | 阅读改进的 `fix` 负载 — 它命名 `fromHash` / `targetHash` 并建议 `migration plan --from <from> --to <target>`；运行 `migration list` 以检查图。 |

CI 网关应读取 `--json` 输出的 `diagnostics` 并根据 `severity` 加上 `code` 进行决策；参见 *工作流 — CI* 下面的结构。

## 工作流 — “部署将运行什么？”

用户询问：“我即将合并这个 PR。当我部署到 staging 时，将运行哪些迁移？”

这是一个导航问题：**起点** = staging 的实时标记；**终点** = 引用 `staging`（如果你还没有设置一个，则为合约头）。向系统查询：

```bash
pnpm prisma-next migration status --to staging --db "$STAGING_DATABASE_URL"
```

该命令：

1. 读取 staging 数据库的标记（起点）。
2. 解析 `staging` 为一个合约哈希（终点）。
3. 将它们之间的路径作为有序的迁移列表渲染，带有每边的 `applied` / `pending` / `unreachable` 状态，以及一个明确的总线条，形式为“引用 'staging' 落后 N 个迁移”。
4. 打印一个标头，命名配置、迁移目录、活动引用和数据库连接（掩码）— 这样可以在输出中看到上下文。

如果你省略 `--db`，该命令将离线运行：它列出磁盘上的迁移，但无法告诉你已应用的内容，因为它没有起点。对于“这个分支上有什么”来说，这很好；对于“staging 将运行什么”来说，这不好 — 对于后者，你需要 staging 的实时标记。

如果你省略 `--to`，终点默认为合约头 — 这将回答“这个分支的合约能否从数据库到达，以及如何到达”，而不是“部署将运行什么”。当问题是关于特定环境时，请显式传递引用。

`migration status` 通过类别（`additive`、`widening`、`data`、`destructive`）总结每个待处理迁移的操作，并在存在破坏性操作时报告破坏性操作计数。在用户合并或部署之前向他们展示该计数 — 破坏性操作是值得手动审查的类别。

## 工作流 — “每个环境处于什么状态？”

对每个环境的数据库运行 `migration status --db $URL`。标记（起点）来自数据库本身；总结行告诉您环境是否处于合约头、命名引用、头前或发散分支。

## 概念 — 同一分支点上的并发迁移

这以前在某些 PN 文档中称为 *菱形汇聚*；无论标签如何，情况都相同。

**正在发生什么。** 两个主题分支各自在相同的父合约哈希上编写了一个迁移。第一个分支合并到 `main`；目标引用（例如 `production`）前进到该分支的 `to` 哈希。你的分支的迁移仍然将其 `from` 哈希指向 *旧的* 父。迁移图在 rebase 后不再有通过你的迁移的干净路径：

- 你的迁移的 `from` 不再是新头的祖先。
- 或者你的迁移的 `from` 是可到达的，但通过你的迁移的路径到达的哈希不是两个分支更改的并集。

无论如何，磁盘上的计划都是陈旧的。

**解决方法。** 磁盘上的计划是陈旧的，因为它的 `from` 哈希不再是图的头；对 post-rebase 状态应用集群的标准 *编辑 → 计划 → 应用* 循环，规划器将生成一个新的迁移，其 `from` 匹配新的头。

**规划器无法为你做的一件事** 是将自定义数据转换逻辑从被放弃的 `migration.ts` 移植到新的迁移中 — 模式增量是从合约派生的，但任何手写的 `data` 操作都是你的责任，在应用之前要携带过。没有单独的“重新验证”步骤，没有特殊的“菱形应用”流程。

## 工作流 — 设置、列出、获取、删除引用

引用是小的工件。没有每个环境的生命周期；你只是将一个名称指向一个哈希。

```bash
pnpm prisma-next ref set production <contract-hash>
pnpm prisma-next ref list
# `ref get` 已被移除 — 使用 `ref list` 并按名称过滤
pnpm prisma-next ref list | grep production
pnpm prisma-next ref delete production
```

`ref set` 在 `migrations/app/refs/<name>` 处写入一个文件，其中包含哈希和任何必需的不变量。引用是提交友好的工件 — 将它们保存在 git 中；团队就 `production` 指向的内容达成一致的方式与他们对 `main` 的共识相同。

## 工作流 — 对环境应用迁移

```bash
pnpm prisma-next migrate --to production --db "$PRODUCTION_DATABASE_URL"
```

终点是引用的哈希；起点是生产数据库的实时标记。该命令计算它们之间的路径，并按顺序应用每个待处理的迁移，推进标记。

`--db` 是环境选择旋钮。`--to` 是目的地哈希旋钮。它们是独立的。

## 概念 — CI / 部署上的引用不匹配

CI 报告：“记录的引用 `production` 位于哈希 X；实时数据库位于哈希 Y。”

不匹配是关于 *两个不一致的状态的事实*。调查与哪个部分是错误的无关：

- **数据库领先于引用。** 有人在不属于 CI 的情况下应用了迁移，而没有在 git 中更新引用。使用 `prisma-next ref set <ref-name> <db-marker-hash>`（提交 + 推送）重新记录引用；然后审核外部应用是如何发生的。
- **数据库落后于引用。** 先前的部署被回滚，或者数据库是从旧备份恢复的。要么使用 `prisma-next migrate --to <ref-name> --db $URL` 向前重新应用，要么使用 `prisma-next ref set <ref-name> <db-marker-hash>` 将引用向后重新路由以匹配实际部署的内容。选择是用户的 — 名称这两个选项。
- **数据库位于不同的分支上。** 一个外部模式更改（手动 SQL、临时迁移）写入了一些迁移图无法建模的内容。运行 `prisma-next db verify` 以检查漂移，然后要么使用 `prisma-next contract infer` 从数据库重新推导合约，要么编辑合约并运行 `prisma-next migration plan`，以便数据库是最终目的地。

`ref set` 以静默方式将引用与数据库当前所处的状态对齐几乎从不正确。它会掩盖你以后会为它付出代价的漂移。

## 工作流 — CI：验证分支能否推进目标环境

网关是 `migration status --to <env> --db $URL`：它计算从实时标记到引用的路径并报告它，而不进行任何更改。`migrate` 没有 `--dry-run` 标志；检查/网关步骤是 `migration status`。

对于在应用之前的人类可读的迁移路径有序预览，请使用 `migrate --show --db $URL`。对于部署后的应用历史，请使用 `migration log --db $URL`（扁平的按时间顺序的表）。

```yaml
- name: 验证 staging 是可到达的
  run: |
    pnpm prisma-next migration status \
      --to staging --db "$STAGING_DATABASE_URL" --json > status.json
    node -e '
      const s = JSON.parse(require("fs").readFileSync("status.json", "utf8"));
      const warns = (s.diagnostics ?? []).filter(d => d.severity === "warn");
      if (warns.length) {
        console.error("阻塞诊断:", warns);
        process.exit(1);
      }
    '
- name: 应用
  run: pnpm prisma-next migrate --to staging --db "$STAGING_DATABASE_URL"
```

`migration status` 仅在硬错误（不可读的迁移目录、无法满足的不变量、无法重建的历史）的情况下退出非零。像 `MIGRATION.MARKER_NOT_IN_HISTORY`、`MIGRATION.DIVERGED`、`CONTRACT.AHEAD` 和 `MIGRATION.NO_MARKER` 这样的诊断在结果信封上报告 `severity: 'warn'`，但进程退出 `0` — 代理（或 CI 网关）必须检查 `diagnostics[]` 并自行失败构建。使用 `--json` 以便网关解析结构化形状，而不是人类摘要。

`migrate` 是交互式的，并且没有破坏性操作确认提示 — 提示破坏性更改的安全栏杆存在于 `db update`（参见 `prisma-next-migrations` 技能）。规划器放入迁移图中的内容是 `migrate` 运行的；审查发生在 `migration plan` 和 `migration status` 时间，在应用步骤之前。

## 常见陷阱

1. **对于部署问题，没有 `--to` 读取 `migration status`。** 这会询问“这个分支的合约能否到达头？”而不是“staging 将运行什么？”。当问题是关于特定环境时，始终传递引用。
2. **对于部署问题，没有 `--db` 读取 `migration status`。** 没有实时数据库，你就没有起点。输出列出了磁盘上的内容；它无法说环境上应用了什么。对于任何高风险问题，传递 `--db $URL`。
3. **混淆引用与数据库连接。** `--to staging` 选择目的地哈希，而不是数据库。显式传递 `--to` 和 `--db`。
4. **将菱形汇聚视为特殊程序。** 它不是。它是正常 *编辑 → 计划 → 应用* 循环应用于 post-rebase 状态。唯一额外的步骤是“将任何数据转换逻辑从旧的 `migration.ts` 转移到新的一个。”
5. **在 CI 中，在理解原因之前运行 `ref set` 以静默处理 CI 不匹配。** 这可能会掩盖外部更改或回滚漂移。先调查。
