# 10x-cli：下载、使用、更新

在执行命令前，请先阅读捆绑的 [兼容性和渠道参考](references/compatibility.md)。其中包含固定运行者的设置、版本检查、辅助渠道和所有权保护措施。命令使用已发布的课程范围技能过滤器；在使用前，请验证实际选择的软件包和内容。本地构建或源成员资格并不能证明功能已发布。

下一次 CLI 发布还将通过 `10x helpers install --tool <选择的配置文件>` 提供仅针对项目的捆绑安装。此命令是 **未发布的**，并且不包含 1.21.0/1.22.0 主基线：请先检查实际运行者的 `helpers --help`。遵循本地参考中的 **捆绑公共副本** 以获取完整文件、明确目标和冲突处理；当运行者不支持时，保留现有的固定公共路线。

## 环境

重用设置交接：项目根目录、课程、工具、语言、运行者/版本、认证/访问状态、更新方法和辅助渠道/路径。如果任何内容缺失，请仅检查该项目。可正常工作的已安装 CLI 无需重新安装。如果需要设置，请定位其实际 SKILL.md 和参考，或通过公共渠道安装该辅助工具；不要通过名称调用缺失的兄弟命令。

引导接受上下文为 macOS/zsh、Claude Code、10xdevs4 和波兰语。根据环境确定实际操作系统和外壳，而不是一个将每个失败标记为 Windows 的 POSIX 命令。在任何写入操作前选择预期的项目根目录。对于 v4，保留现有的 v3 项目并使用单独的目录；普通的 get、sync 和 profile 更改不会迁移版本。如果版本/课程冲突，请保留 `.10x-cli.json` 和所有清单文件。

使用参考中定义的经过验证的 `10x_cli` 运行者，或用户确切的经过验证的全局/独立可执行文件：

```bash
10x_cli --version
10x_cli get --help
10x_cli sync --help
10x_cli auth --status
10x_cli list
```

在这些命令中省略 `--course`：当目录已绑定时，CLI 会从 `.10x-cli.json` 中读取版本，否则从实时 API 推荐中读取（账户可达到的最高版本）。`get` 会打印 `Course: <slug> (<reason>)`；在第一次写入前检查一次。仅使用 `--course <slug>` 查看其他授权版本——已绑定的项目不能重写为不同版本 (`course_mismatch`)，因此 v4 会从新的空目录开始。

检查课程参考、技能过滤器和课程范围同步的源/发布证据，然后使用以下过滤预览检查端点。不要将成功的帮助退出视为功能证明。保留不支持的 CLI 语法、未发布/缺失的内容、锁定模块、成员资格拒绝和网络故障的独立性。缺失最终发布证据无需阻止准备公共辅助工具或练习文件。

仅从 `config.json` 中读取需要的非秘密偏好设置。在 macOS/Linux 上，其基础是非空的 `$XDG_CONFIG_HOME`，否则 `~/.config`；在 Windows 上是 `%APPDATA%`，否则是用户的 `AppData/Roaming`。追加 `10x-cli/config.json`。不要打印 `auth.json`，丢弃 stderr，截断医生 JSON 或擦除配置以修复未知问题。在此过程中指定的课程/工具/语言优先于该命令的保存默认值。

## 会话管理

需要登录时，让用户选择交付渠道并完成：

```bash
10x_cli auth                  # 交互式：选择电子邮件或 Circle
10x_cli auth --method email   # 电子邮件魔法链接；默认用于 piped/JSON 输出
10x_cli auth --method circle  # 一次性批准链接通过 Circle 传递
10x_cli auth --status
10x_cli auth --logout
```

当电子邮件未到达时，Circle 很有用。批准链接在 15 分钟后过期；CLI 不会自动重新发送它。在非交互模式下，使用 `--email` 提供用户的电子邮件并显式选择 `--method circle`。在用户请求认证之前，不要发送登录消息。会话透明地刷新；只有当刷新无法恢复它们时，才需要重新登录。

## 下载

启动练习遵循第 1 课，“从想法到 PRD”，使用其现有的 10xCards 示例。`10x-plan` 不是这次启动演示的一部分。准备所有四个课程的技能：`10x-idea-check`、`10x-init`、`10x-shape` 和 `10x-prd`。想法评估是可选运行的；其文件在准备第 1 课时仍应可用。如果用户仅请求特定技能，请保留更窄的范围。在检查每个名称的功能和可用性后，下载四个独立的完整选择的技能树。在执行相应的写入前检查每个干运行：

```bash
10x_cli get m1l1 --type skills --name 10x-idea-check --tool claude-code --lang pl --dry-run
10x_cli get m1l1 --type skills --name 10x-idea-check --tool claude-code --lang pl
10x_cli get m1l1 --type skills --name 10x-init --tool claude-code --lang pl --dry-run
10x_cli get m1l1 --type skills --name 10x-init --tool claude-code --lang pl
10x_cli get m1l1 --type skills --name 10x-shape --tool claude-code --lang pl --dry-run
10x_cli get m1l1 --type skills --name 10x-shape --tool claude-code --lang pl
10x_cli get m1l1 --type skills --name 10x-prd --tool claude-code --lang pl --dry-run
10x_cli get m1l1 --type skills --name 10x-prd --tool claude-code --lang pl
```

检查每个报告和完整的支持树，而不仅仅是 SKILL.md。在选择的 macOS/zsh 练习目录中，每个检查在使用前都必须成功（任何失败都会停止；不要仅从最后一个检查推断成功）：

```bash
test -s .claude/skills/10x-idea-check/SKILL.md
test -s .claude/skills/10x-idea-check/references/examples.md
test -s .claude/skills/10x-idea-check/references/assessment-guide.md
test -s .claude/skills/10x-idea-check/references/10xdevs-4-dates.md
test -s .claude/skills/10x-idea-check/references/10xdevs-4-certification.md
test -s .claude/skills/10x-init/SKILL.md
test -s .claude/skills/10x-shape/SKILL.md
test -s .claude/skills/10x-shape/references/prd-schema.md
test -s .claude/skills/10x-prd/SKILL.md
test -s .claude/skills/10x-prd/../10x-shape/references/prd-schema.md
```

PRD 入口点相对于其自己的目录解析 `../10x-shape/references/prd-schema.md`。独立的 PRD 树是不够的。读取所有已安装的入口点及其所需的所有参考；上述路径是已知的源最小值，而不是发布捆绑包中丢弃额外文件的权限。还要检查 `.claude/.10x-cli-manifest.json`：`lessons.m1l1.skills` 必须包含所有四个名称，并在 `files.skills` 中包含文件哈希。这些是课程拥有的部分下载，不是独立的拥有者。检查 `.10x-cli.json` 以获取课程绑定；部分下载不会建立完整的课程发布身份。

CLI 1.21.0 随 v4 和过滤的技能下载发布；生产 m1l1 EN/PL 包含 idea-check/init/shape/prd 及其参考。这些修订的辅助工具是单独的源更改，而不是其课程副本已发布的证明。将所有四个名称与实际选择的发布进行验证。如果任何名称、模式、所有者或发布缺失/不匹配，请保留精确的错误并停止练习；永远不要无声地替换整个课程、另一个课程或过滤的 get。

`CLAUDE-m1l1` 是单独的课程规则，不是通过这些过滤的技能 get 传递的。检查的 init/shape/prd 源不需要该规则来运行此链。这并不能证明没有该规则，每个完整课程的步骤都能正常工作。使用学习者的现有第 1 课输入和说明：如果他们需要该规则，请检查现有的项目规则及其来源。如果缺失，请在该步骤之前报告缺失的先决条件，并从课程/发布所有者处获取支持的路由。不要发明规则命令或下载完整课程来绕过它。不要覆盖现有的项目规则。

用于浏览使用 `10x_cli list m1`。上述命令按技能名称过滤一个课程；`get 10x-init` 不受支持。`--print` 是检查：
TTY Markdown 只能包含 SKILL.md；非 TTY 输出是 JSON 信封。永远不要将打印输出重定向到 SKILL.md 作为软件包安装。

## 使用：10xCards，从想法到 PRD

下载树只是准备工作。使用现有的 10xCards 示例和学习者从第 1 课的实际答案。如果这些输入缺失，请请求它们；不要发明产品需求、一个替换的 task.md 或一个现成的计划。将私人课程文本从公共固定文件和转录中排除。
不要假设原生斜杠/$ 发现或从 npm install 自动激活。给代理明确的本地路径。如果学习者想评估想法是否符合他们的经验、时间和课程目标，请先阅读 `.claude/skills/10x-idea-check/SKILL.md` 及其参考，并遵循该技能。当学习者准备好塑造时，不要将评估作为先决条件。然后分别执行以下步骤：

1. 阅读 `.claude/skills/10x-init/SKILL.md` 并在选定的项目中遵循它。
   检查 create-if-absent 上下文/更改、上下文/存档和上下文/基础目录及其 README。保留现有文件。
2. 阅读 `.claude/skills/10x-shape/SKILL.md` 和
   `.claude/skills/10x-shape/references/prd-schema.md`。使用学习者的 10xCards 输入跟随技能的发现。
   让学习者回答并批准检查点；不要为他们回答。在继续之前，检查
   `context/foundation/shape-notes.md` 与这些答案。
3. 阅读 `.claude/skills/10x-prd/SKILL.md` 及其兄弟模式，然后从实际的
   `context/foundation/shape-notes.md` 生成草稿。检查
   `context/foundation/prd.md` 与该输入和安装的模式；未解决的领域选择保持开放。
   尊重技能的现有文件冲突选择（版本化文件可能是适当的结果）。

成功需要学习者的笔记和符合模式规范的 PRD，差距明确且原始项目工作得到保留。仅下载的转录是不够的。在审查 PRD 后停止；不要链入堆栈选择、引导或实现。如果读取了不同的全局/本地技能副本，请在接受结果前更正路径。记录实际代理、配置文件、语言、输出路径和检查；使用新的隔离练习目录而不是强制覆盖两个规范输出文件名。

## 更新

使用相同的运行者、目录、工具和语言；版本仍然是项目自己的，因此 `sync` 无需 `--course`。同步更新整个下载的课程，包括这些过滤 get 后的 m1l1。其预览可能包括其他技能、提示、配置和课程规则。检查扩展的范围并在用户接受时应用；要更新单个技能，请重复其过滤预览/get。不要将同步用作隐藏规则先决条件工作的绕过方法：

```bash
10x_cli sync --tool claude-code --lang pl --dry-run
10x_cli sync --tool claude-code --lang pl
```

正常同步刷新清单中记录的完整课程，而不仅仅是四个选择的技能。`--all` 将范围扩展到未锁定的课程，对于此练习不需要。应修复缺失的管理文件；本地编辑应作为冲突或保留文件可见。即使退出状态为 0，也要读取所有报告结果和资源计数：仅跳过的冲突不是进程错误。不要将未更改的远程摘要等同于完整的本地文件。

对于单个冲突技能，检查差异并在交互式终端中从同一目录和相同工具/语言重试其过滤 get，在重试前备份本地工作。保留用户的解决选择。如果 CLI 提示省略上下文，请在建议的命令中恢复这些标志。永远不要运行自动 `--force`；它可以覆盖本地技能/提示编辑，并且不会绕过受保护的规则或安全删除。配置模板保持创建仅。清理保留修改/未跟踪文件和属于其他位置的文件；不要在同步后手动清理技能目录。

三个更新是独立的：更改 npm/二进制版本更新 CLI；重复固定的公共 `skills add` 并使用故意选择的新保留 SHA 更新公共辅助工具；CLI 同步更新 CLI 拥有的课程技能。它不会更新可执行文件或公共安装器拥有的辅助工具副本。

## 渠道：两个辅助工具通过两条路线都可用

公共按需路线在 CLI/认证之前工作，并在选定的源 SHA 安装一个项目辅助工具。CLI 路线在辅助工具内容发布后且 m1l1 可访问时使用认证的过滤 get 一次。遵循参考中 `10x-cli-setup` 和 `10x-cli-guide` 的确切命令和守卫；仅安装需要的部分。两条路线都交付每个辅助工具自己的 `references/compatibility.md`。

每个已安装副本使用一个所有者。在写入前检查目标路径/符号链接、CLI 清单和公共安装器的项目注册。如果辅助工具已经是 CLI 拥有的，请使用该副本并同步。对于公共→CLI 接管，在管理树外备份整个辅助工具和元数据，使用原始固定安装器的项目/代理移除流程仅注销该辅助工具，验证注册和目标不存在，然后过滤 get。有意识地从备份中合并本地编辑。如果任何所有者仍然存在，请停止接管。CLI→公共没有经过验证的每个技能注销合同：使用新的隔离项目而不是手动编辑清单。

## 配置文件和故障排除

完整技能树位于选定配置文件的 `skills/<规范名称>/` 下：

| 配置文件 | 工具目录 | 完整课程交付的规则文件 |
|---|---|---|
| claude-code | `.claude/` | `CLAUDE.md` |
| cursor | `.cursor/` | `.cursor/rules/10x-course.mdc` |
| copilot | `.github/` | `.github/copilot-instructions.md` |
| codex | `.agents/` | `AGENTS.md` |
| devin-desktop | `.devin/` | `AGENTS.md` |
| gemini | `.gemini/` | `GEMINI.md` |
| generic | `.ai/` | `AGENTS.md` |

配置文件更改可能提供迁移、删除符合条件的已管理文件，或保留两者；没有则意味着删除任意用户内容或切换课程版本。
遗留的 windsurf 别名和孤儿处理应遵循选定版本的帮助/输出。这些路径映射不是完成 Windows 或其他代理演练的证据。将外壳语法转换为用户实际的外壳。

当诊断有用时运行 `10x_cli doctor --json`；检查完整的 `data.overall` 和 `data.checks` 以及退出状态。它检查配置文件，而不是 `--tool` 或 `--course` 参数。其认证检查报告解析的版本和选择原因 (`details.course`, `details.selectionReason`) — 这是此目录属于哪个版本的自我检查。在第一次 get 前，可以预期缺少工具目录；仅解释该失败并保留其他失败可见。医生退出 78 可以与外部的 JSON `status: "ok"` 共存。

| 症状 | 下一步 |
|---|---|
| 缺失/过期的认证 | 检查认证状态和实时访问结果；让用户通过设置完成登录。登录可能会发送电子邮件。 |
| 未收到电子邮件 | 提供 `10x_cli auth --method circle`；让用户请求消息。 |
| `circle_login_disabled` | Circle 不可用；使用 `10x_cli auth --method email`。 |
| `dm_rejected` | 启用 Circle 直接消息或使用电子邮件登录。 |
| `circle_login_expired` | 请求新的 Circle 登录或使用电子邮件；永远不要自动重新发送。 |
| 拒绝课程访问 | 确认选择的课程和成员资格；更改工具/重新安装不会授予访问权限。 |
| 锁定或未发布的 v4 | 检查模块可用性/发布证据；不要绕过门或回退到 v3。 |
| 不支持名称/缺失索引 | 验证确切的 CLI 软件包和内容发布；为发布所有者保留错误。 |
| 网络/API 失败 | 保留诊断，当服务恢复时重试相同上下文；无需重置配置。 |
| 缺失 `10x-idea-check` 后设置 | 较旧的辅助工具旅程仅选择了 init/shape/prd。检查实际命令、选定的配置文件路径和清单；使用上述 idea-check 预览/get 添加其完整树。如果文件已存在，请读取确切的 SKILL.md 并检查代理的发现/重新加载行为，然后再重新安装。仅缺失的斜杠命令本身并不能证明缺失文件。 |
| 错误的目录/配置文件 | 重新检查 cwd 和显式标志；新项目可能合法地没有工具目录。 |
| 签名/发布不匹配 | 保留失败和源身份；不要禁用验证或重用无关的字节。 |
| 版本/清单冲突 | 保留绑定和清单以进行修复；使用单独的 v4 项目而不是删除它们。 |
| 文件冲突或权限失败 | 检查受影响的路径和本地编辑，保留备份并解决具体问题。不要广泛的 chmod/重置/force。 |

仅在需要时使用 `--verbose`，并在共享诊断前编辑凭证。对于 `bench` 等不相关的日常命令，请检查此运行者的匹配帮助；不要将任意主 README 作为较旧二进制的权威依据。
