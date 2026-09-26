# 发布技能

> **目的：** 将一个项目从“代码已准备好”的状态转变为“由操作员标记、推送，并在确切的标记 SHA 上验证为绿色”的状态。”

预发布验证、从 git 历史记录中生成变更日志、跨包文件的版本号更新、发布提交、带注释的标签、策划的发布说明以及发布后的确切的 SHA CI 验证。本地准备工作是可逆的。发布（包括 GitHub 发布页面）是 CI 的工作。

## 约束条件

- **保持准备工作可逆，发布操作由操作员负责。** 此技能可能会创建本地发布工件、一个提交和一个带注释的标签，但它永远不会推送、发布或触发 CI，因为这些操作跨越了可逆的本地边界。
- **要求确定性预发布。** 运行完整发布门禁以确认版本，并将 `--skip-checks` 视为操作员的明确降级选择，因为未经测试的标签不能成为可信的发布边界。
- **将完成与标记的提交绑定。** 记录标签 SHA、确切的 SHA CI 运行和协调结果，因为绿色的分支运行或未验证的标签并不能证明已发布的工件。
- **保持发布声明有证据支持。** 仅从选定的 git 范围和生成的工件中派生变更日志、说明、版本选择和审计，因为捏造或复制前向的声明会同时损害受众。
- **在拉起安灯前咨询 pawl。** WARN、FAIL 或 REFUTED 发布证据会自动修复和重新运行，因为普通拒绝表明准备工作不完整；只有真正的发布破坏者才会进入 HOLD 或消耗辅助通道。

## 断路器状态机

- **普通拒绝 — `WARN|FAIL|REFUTED -> AUTO-REDO`：** 修复由操作员拥有的发布工件或将缺陷路由回其生成的珠子，然后重新运行预发布和 pawl；普通的拒绝永远不会进入 HOLD，也永远不会消耗辅助通道。
- **断路器 — `BREAKER -> HOLD -> ONE-HELPER`：** 当不可逆的远程操作、模糊的工件标识或不可用的发布权限阻止安全进行时，冻结标签或发布指导，然后与审计包进行一次有界的辅助咨询。
- **已恢复 — `HELPER-UNSTUCK -> AUTO-REDO`：** 离开 HOLD，应用有界恢复，并重新获得本地验证、确切的 SHA 证据、协调和 pawl 裁决。
- **辅助升级 — `HELPER-ESCALATE -> HUMAN`：** 停止自动化并将辅助提供的发布证据发送给操作员。
- **直接人工通道 — `REFUSAL-LANE|EXPLICIT-JUDGMENT|EXHAUSTED-BUDGET -> HUMAN`：** 跳过辅助并直接路由到操作员；这些是唯一直接人工状态。

---

## 快速入门

```bash
/release 1.7.0                # 完整发布：变更日志 + 版本号更新 + 提交 + 标签
/release 1.7.0 --dry-run      # 显示会发生什么，不做任何更改
/release --check               # 仅进行就绪性验证 (GO/NO-GO)
/release                       # 从提交分析中建议版本
```

---

## 参数

| 参数 | 必填 | 描述 |
|------|------|------|
| `version` | 否 | Semver 字符串（例如，`1.7.0`）。如果省略，则根据提交分析建议 |
| `--check` | 否 | 仅就绪性验证 — 不生成或写入任何内容 |
| `--dry-run` | 否 | 显示生成的变更日志 + 版本号更新，但不写入 |
| `--skip-checks` | 否 | 跳过预发布验证（测试、代码风格检查） |
| `--changelog-only` | 否 | 仅更新 `CHANGELOG.md` — 不进行版本号更新、不提交、不标记 |

---

## 模式

| 模式 | 调用方式 | 行为 |
|---|---|---|
| **完整发布** | `/release [version]` | 预发布 → 变更日志 → 发布说明 → 版本号更新 → 用户审查 → 写入 → 发布提交 → 标签 → 推送指导 → 确切的 SHA CI 验证。 |
| **检查** | `/release --check` | 仅进行预发布检查；报告 GO/NO-GO。可与 `/validate` 组合。不写入。 |
| **仅变更日志** | `/release X.Y.Z --changelog-only` | 仅更新 `CHANGELOG.md` — 不进行版本号更新、不提交、不标记。 |

---

## 工作流

**请参阅 [references/release-workflow-detail.md](references/release-workflow-detail.md) 了解完整的每步程序** — bash 命令、检查表、预期输出、审计记录模板和示例。下表仅用于方向；代理必须针对 `release-workflow-detail.md` 执行以验证正确性。

1. **预发布** — 运行 `scripts/ci-local-release.sh`（阻塞）以及版本/代码风格检查、测试/分支/变更日志/SBOM/安全检查。`--check` 模式在此步骤后停止。
2. **确定范围** — `<上一个标签>..HEAD`。对于非 HEAD 切割，请参阅 [references/release-cut-and-bump.md](references/release-cut-and-bump.md)。
3. **读取 git 历史记录** — `git log --oneline --no-merges <范围>` 加上用于模糊性解决的统计信息。
4. **分类和分组** — 为 `CHANGELOG.md` 添加/更改/修复/删除。说明性文本使用更丰富的 8 标签集，具体请参阅 [references/release-notes.md](references/release-notes.md)。
5. **建议版本** — 如果有破坏性变更则建议主版本号，如果有新功能则建议次版本号，如果只有修复则建议修订号。通过 AskUserQuestion 确认。
6. **生成变更日志条目** — Keep-a-Changelog 格式，今天的日期，与最近存在的条目风格匹配。
7. **检测和提供版本号更新** — 通用模式（`package.json`、`pyproject.toml` 等）加上 AgentOps 特定的清单，具体请参阅 [references/release-cut-and-bump.md](references/release-cut-and-bump.md)。
8. **用户审查** — 显示生成的变更日志和版本差异；通过 AskUserQuestion 确认继续。`--dry-run` 停止在此处。
9. **写入更改** — `CHANGELOG.md` 更新 + 版本文件编辑。
10. **生成发布说明** — 根据 [references/release-notes.md](references/release-notes.md) 定制的 `docs/releases/YYYY-MM-DD-v<版本>-notes.md`。必须在发布提交之前暂存。
11. **写入审计记录** — `docs/releases/YYYY-MM-DD-v<版本>-audit.md` 通过 `scripts/resolve-release-artifacts.sh` 解析。格式化方式请参阅工作流详细步骤 16。
12. **发布提交** — `git commit -m "发布 v<版本>"`，暂存所有发布工件。
13. **标记** — 带注释的 `git tag -a v<版本> -m "发布 v<版本>"`。
14. **GitHub 发布（CI 处理此部分）** — 不要本地 `gh release create`；GoReleaser 是唯一的创建者。
15. **发布后确切的 SHA CI 和协调验证** — 操作员推送后，要求 `scripts/verify-release-ci.sh v<版本>` 打印 `GO release-ci`，并运行 `ao reconcile --json | bash skills/release/scripts/validate-reconcile.sh "v<版本>"` 通过，以确切的预期标签；仅确切的 SHA CI 从未授权关闭。
16. **发布后指导** — 显示推送命令和验证命令；不要推送。
17. **审计记录格式** — 请参阅工作流详细步骤了解 markdown 模板。

**检查点：** 在写入之前，确认操作员已批准显示的变更日志和版本差异；在交接之前，证明发布提交、带注释的标签、审计和说明都同意版本；在推送后，要求确切的 SHA CI 加上协调，然后才声明完成。

---

## 边界

### 此技能执行的操作

- 预发布验证（测试、代码风格检查、干净树、版本、分支）
- 从 git 历史记录生成变更日志
- 从提交分类建议 Semver
- 在包文件中更新版本字符串
- 发布提交 + 带注释的标签
- GitHub 发布页面用的高亮 + 变更日志的发布说明
- CI 在 GitHub 发布页面上发布的策划发布说明
- 发布后指导 + 确切的 SHA CI 验证说明
- 审计记录

### 此技能不执行的操作

- **不发布** — 没有 `npm publish`、`cargo publish`、`twine upload`。CI 处理此部分。
- **不构建** — 没有 `go build`、`npm pack`、`docker build`。CI 处理此部分。
- **不推送** — 没有 `git push`、没有 `git push --tags`。用户决定何时推送。
- **不触发 CI** — 标签推送（由用户完成）触发 CI。
- **不单仓库多版本** — 一个版本、一个变更日志、一个标签。v2 的范围。

此技能执行的所有操作都是本地且可逆的：
- 坏的变更日志 → 编辑文件
- 错误的版本号更新 → `git reset HEAD~1`
- 坏的标签 → `git tag -d v<版本>`
- 坏的发布说明 → 在推送前编辑 `docs/releases/*-notes.md`

---

## 通用规则

- **不要捏造** — 仅记录 git log 显示的内容
- **最终输出中不包含** 提交哈希
- **最终输出中不包含** 作者名称
- **简洁** — 每个要点一句，技术但可读
- **适应，不要强加** — 与项目的现有风格匹配，而不是强制特定格式
- **用户确认** — 永远在显示草稿之前才写入
- **仅本地** — 永远不推送、发布或触发远程操作
- **在标签时未完成** — 用户推送后，验证确切的标记 SHA 的绿色 `validate.yml` 运行，运行 `ao reconcile --json`，并记录运行 ID/结论以及协调整体状态和发布标签查找状态到交接或发布审计说明中。
- **两个受众** — `CHANGELOG.md` 是为贡献者（文件路径、问题 ID、实现细节）。发布说明是为订阅者（普通英语、用户可见影响、无内部术语）。永远不要将变更日志复制粘贴到发布说明中。

---

## 输出规范

- **路径：** `docs/releases/YYYY-MM-DD-v<版本>-audit.md`，与 `docs/releases/YYYY-MM-DD-v<版本>-notes.md` 和带注释的引用 `refs/tags/v<版本>` 配对。
- **文件名约定：** `YYYY-MM-DD-v<版本>-audit.md` 和 `YYYY-MM-DD-v<版本>-notes.md`，其中 `<版本>` 是确认的 SemVer，不带重复的 `v` 前缀。
- **序列化/模式格式：** Markdown 审计，包含发布标题、日期、上一个标签、提交计数、本地 CI 工件路径、版本号更新、预发布结果和远程 CI 判决；带注释的 Git 标签指向发布提交，判决记录确切的 SHA、运行 ID、状态和结论。
- **验证器命令：** 设置 `VERSION="<版本>"`，然后运行 `bash scripts/validate-release-audit-artifacts.sh --mode target --target-release "$VERSION" && bash scripts/verify-release-ci.sh "v$VERSION" && ao reconcile --json | bash skills/release/scripts/validate-reconcile.sh "v$VERSION"`；命令成功本身是不够的，因为协调 JSON 必须命名确切的预期标签，语义上是绿色的，并且不包含中等/高发布查找。
- **下游交接：** 在推送前，将发布提交 SHA、带注释的标签 SHA、审计/说明路径、回滚命令和确切的推送/验证命令发送给操作员；在推送后，在关闭前追加确切的 SHA CI 和协调证据。

## 质量检查清单

- 变更日志和说明仅包含所选 git 范围支持的变化，使用仓库风格，并为贡献者和订阅者受众服务。
- 版本文件、发布提交、带注释的标签、审计和说明都命名相同的确认 Semver，并解析为一个发布边界。
- 在交接前通过完整的本地发布验证和工件检查；操作员推送后通过确切的标签 CI 和协调。
- 普通拒绝保持在 AUTO-REDO；HOLD 恰好有一个辅助，操作员升级仅限于声明的手动状态。

---

## 示例

**用户说：** `/release 1.7.0`
代理运行预发布 → 读取 `v1.6.0..HEAD` git 历史记录 → 分类提交 → 草稿变更日志条目 + 定制的发布说明 → 检测版本文件（`package.json`、`version.go`、插件清单）→ 提交草稿供审查 → 批准后，写入文件，创建发布提交，创建带注释的标签，打印推送指导，然后用户推送后验证 `scripts/verify-release-ci.sh v1.7.0`，运行 `ao reconcile --json`，并记录运行 ID/结论以及协调状态。

**用户说：** `/release --check`
代理运行所有预发布检查并输出 GO/NO-GO 摘要表。不写入。

**用户说：** `/release`（无版本）
代理分类提交并建议版本（如有破坏性变更则建议主版本号，如有新功能则建议次版本号，只有修复则建议修订号），然后询问用户确认或覆盖。

**用户说：** `/release 1.7.0 --dry-run`
代理显示变更日志条目 + 版本号更新将如何显示，然后停止不写入。

请参阅 `references/release-workflow-detail.md` 了解完整的每步示例说明。

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|------|
| "自上次标签以来没有提交" 错误 | 工作区干净，没有新提交 | 提交待处理更改或跳过发布 |
| 版本不匹配警告 | `package.json` 和 `go` 版本不一致 | 发布前手动同步，或选择一个作为事实依据 |
| 预发布期间测试失败 | 未捕获破坏性变更 | 修复测试，或使用 `--skip-checks`（不推荐） |
| 工作区脏警告 | 存在未提交的更改 | 发布前提交或暂存 |
| GitHub 发布页面正文为空 | GoReleaser 与现有草稿冲突 | CI 在 GoReleaser 运行前删除现有发布；不要本地 `gh release create` |
| `ci-local-release.sh` 在 agents-hash 上挂起 | `~/.agents/patterns` 很大 | 在调用前设置 `AGENTS_HUB_OVERRIDE=/tmp/empty-hub` |

请参阅 `references/release-workflow-detail.md` 了解完整的故障排除矩阵。

## 参见

- [security](../security/SKILL.md) — 依赖项审计和漏洞扫描（吸收依赖项）

在连接或审计支持 `--check` 模式（或消费策划说明的标签触发发布管道）的 CI 工作流时，从 `references/gh-actions-ci-patterns.md`（通用 CI）或 `references/gh-actions-release-automation.md`（标签触发、草稿流、资产上传）中拉取相关模式。在生成策划的发布说明文件或审计 CHANGELOG.md 偏移时，将变更日志视为方向层，并使用 `references/changelog-as-research-artifact.md` 进行结构化部分、破坏性变更调用和说明与变更日志规则。

## 参考文档

- [references/release-workflow-detail.md](references/release-workflow-detail.md) — 完整每步程序
- [references/release-cut-and-bump.md](references/release-cut-and-bump.md) — 非HEAD切割 + AgentOps 特定的版本号更新目标
- [references/release-notes.md](references/release-notes.md) — 策划的发布说明格式 + 产品区域分类
- [references/release-preflight-and-publishers.md](references/release-preflight-and-publishers.md)
- [references/release-cadence.md](references/release-cadence.md)
- [references/changelog-as-research-artifact.md](references/changelog-as-research-artifact.md)
- [references/gh-actions-ci-patterns.md](references/gh-actions-ci-patterns.md)
- [references/gh-actions-release-automation.md](references/gh-actions-release-automation.md)
- [references/release.feature](references/release.feature) — 可执行规范：--check 就绪性、策划的发布说明 + CHANGELOG 协调、操作员执行的标签/推送、确切的 SHA 绿色验证（soc-qk4b）
