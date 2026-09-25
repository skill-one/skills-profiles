# 审计并减少依赖

减少 JavaScript 依赖足迹。仅使用 **pnpm**。除非有明确理由更改，否则保留锁文件、工作区布局和依赖范围样式。

对于 GitHub Actions 工作流筛选（操作选择、权限、固定版本），使用专用工作流审计——而不是下面的报告格式（工作流文件 + 步骤仅在发现 **pnpm install 政策**时使用）。

## 工作流

0.  强化门禁：运行 `/check-npm`（只读）。参见 [check-npm](../check-npm/SKILL.md)。
1.  建立基线。
2.  移除未使用的直接依赖。
3.  在单体仓库中消除直接依赖版本的重复。
4.  根据传递锁文件闭包对直接依赖进行排序。
5.  使用闭包数据查找低风险的次要/补丁升级。
6.  使用闭包数据查找值得内联的简单依赖。
7.  检查 e18e 推荐的替换/移除。
8.  重新安装、验证并报告测量影响。

## 步骤 0：强化门禁 (`/check-npm`)

在工作区清单或锁文件发生变更前运行 **`/check-npm`**。

- 如果任何检查 **失败**：报告表格和修复片段；在清理过程中**不要削弱** `pnpm-workspace.yaml`、`.npmrc`、CI 安装标志或 Renovate 年龄门禁。
- 不要将完整的强化配置粘贴到此工作流中——`/check-npm` 拥有版本阈值、脚本策略、git 依赖协议和最小发布年龄。
- 如果用户仅要求强化（不要求减少），在用户也需要清理的情况下，运行 `/check-npm` 后停止。

**pnpm 11+：** 脚本和发布年龄策略位于 `pnpm-workspace.yaml` 中，而不是 `.npmrc` 或 `package.json#pnpm`（pnpm 11 不再读取 `package.json#pnpm` 字段）。在建议配置前，将每个键与安装的 pnpm 主版本进行验证。不要添加不支持的键。在清理过程中不要降低现有的 `minimumReleaseAge`（或组织等效项）。

## 依赖筛选

对于每个非平凡的直接依赖（尤其是在步骤 4–7 之后），分配一个标签：

| 标签           | 含义         |
|---------------|--------------|
| **保留**       | 必需的；传递成本值得；维护良好。 |
| **用更好的替换** | 必需的；存在维护更好或更安全的选择。 |
| **用内部替换** | 必需的；外部风险值得内部实现。 |
| **移除**       | 可以移除或内联（步骤 6）。 |
| **需要用户审核** | 使用不明确、策略权衡或需要人工验证的变更。 |

**替换和新的直接依赖**

- **没有新的直接依赖**（包括交换）不得未经明确用户批准。
- 当等效时，优先选择 **移除**（内联/原生 API）而不是 **用更好的替换**。
- 对于 **用更好的替换**：说明原因（维护、安全、更小的树）；优先选择由受信任的维护者维护的、积极维护的、广泛采用的包。
- 尊重仓库 `minimumReleaseAge` / Renovate 门禁；命令级别的 72 小时新鲜度是底线，不是绕过更严格配置的许可。

## pnpm & 供应链

确认仓库使用 pnpm：`pnpm-lock.yaml`、`pnpm-workspace.yaml`，以及/或根 `package.json` 中的 `packageManager` / `devEngines.packageManager.name` 设置为 `pnpm`。如果不在 pnpm 上，停止——不要作为清理的一部分迁移包管理器。

当存在时，尊重仓库安装策略（例如 `pnpm install --frozen-lockfile --ignore-scripts`）。

| 操作         | 命令         |
|-------------|-------------|
| 安装/更新锁文件 | `pnpm install --ignore-scripts` (+ 仓库标志，例如 `--frozen-lockfile`) |
| 移除直接依赖   | `pnpm remove <pkg> --ignore-scripts` |
| 添加/更新直接依赖 | `pnpm add <pkg>@<version> --ignore-scripts` |
| 解释依赖     | `pnpm why <pkg>` |
| 消除锁文件重复 | `pnpm dedupe` (然后如果锁文件更改，运行 `pnpm install --ignore-scripts`) |
| 过期/版本信息 | `pnpm outdated <pkg>` |
| 一次性工具     | `pnpm --config.ignore-scripts=true dlx <pkg>@<version> <args...>` (固定版本；当在锁文件中时，优先使用 `pnpm exec`) |

**生命周期脚本：** 在 `pnpm install`、`pnpm add` 和 `pnpm remove` 上始终使用 `--ignore-scripts`，除非用户在相同消息中明确编写 **允许脚本**（说明将运行哪些脚本和风险）。对于 `pnpm dlx`，`dlx` 不接受 `--ignore-scripts` 直接——使用 `pnpm --config.ignore-scripts=true dlx`（`dlx` 之后的标志将转发到执行的二进制文件）。如果一个依赖项确实需要构建脚本（原生模块等），完成无脚本操作后，询问是否运行 **特定** 手动重建（例如 `pnpm rebuild <pkg>`）。

**新鲜度检查（≥ 72 小时）** — 在任何添加或升级 **命名包版本** (`pnpm add`、`pnpm dlx` 使用新的/升级的直接版本) 的命令之前都需要。**不要求** 对于没有新包参数的普通 `pnpm install` / `pnpm remove`。

对于每个直接命名的包：

1. `curl -s https://registry.npmjs.org/<package-name>`
2. 解析版本：固定 `pkg@1.2.3` → 该版本；范围/`latest`/未指定 → `dist-tags.latest`
3. 读取 `time["<version>"]`
4. 如果发布**少于 72 小时** → **停止**。告诉用户包、版本和确切年龄。除非用户编写 **覆盖新鲜度检查**，否则建议一个旧的已知良好固定版本。
5. **`@grafana/*`** 作用域包**豁免**新鲜度检查；`--ignore-scripts` 仍然适用。

在失败的新鲜度检查后，不得未经用户批准而替换为不同版本。

## 安全规则

- 分小批处理，以保持锁文件差异可审查。
- 不要盲目信任未使用的依赖项工具；验证导入、配置文件、脚本、生成代码钩子、框架约定、插件名称、CLI 和动态导入。
- 您可以编写脚本和解析来验证 `package.json` 和锁文件依赖项账户。
- 将 `peerDependencies`、`optionalDependencies`、包二进制使用、测试固定和发布包清单视为更高风险。
- 除非替换被证明是等效的，否则不要移除或内联用于安全、解析、加密、Unicode、URL 处理、日期/时间、i18n 或平台兼容性的依赖项。
- 不要切换包管理器、删除 `pnpm-lock.yaml` 或作为清理的一部分重写工作区结构。
- 将 `pnpm dedupe` 视为可能改变行为的；在保留结果前，检查锁文件差异并运行聚焦验证。
- 测量前后：直接依赖项计数、锁文件行数或条目计数、包计数，以及当可用时估计的 `node_modules` 大小。

## 步骤 1：基线

收集：

- 所有 `package.json` 文件和工作区边界 (`pnpm-workspace.yaml`)。
- `pnpm-lock.yaml`、`pnpm-workspace.yaml` 安全设置 (`minimumReleaseAge`、`strictDepBuilds`、`blockExoticSubdeps`、`allowBuilds`)，以及 `.npmrc` / CI 标志中的安装策略（例如 `--frozen-lockfile`、`--ignore-scripts`）。
- 按清单部分列出直接依赖项名称：`dependencies`、`devDependencies`、`peerDependencies`、`optionalDependencies`。
- 从脚本、CI 或仓库文档中现有的验证命令。
- **CI 快速检查**（`.github/workflows` 或等效）：安装应使用 `pnpm install --frozen-lockfile`，脚本阻塞应与工作区配置一致。标记在每次运行时都会重新生成锁文件的工作流。
- **Renovate / Dependabot**（如果存在）：注意 npm 包的 `minimumReleaseAge`；在清理过程中不要降低它。

记录基线指标：`git status --short`、`wc -l pnpm-lock.yaml`。如果安装了 `node_modules`，使用平台适用工具估计占用空间。锁文件减少是主要指标——不要依赖 `node_modules` 存在。

## 步骤 2：移除未使用的直接依赖

**不安全的直接依赖协议** — 扫描所有工作区 `package.json` 依赖项部分。标记不是以下值的值：semver 范围、`workspace:`、`patch:` 或 `npm:` 别名到 semver。标记 `git:` / `github:` / tarball URL / `user/repo` 简写 / `file:` / `link:` / `exec:` / 等（与 `/check-npm` 相同的允许列表）。不要无声地移除标记的条目；报告用于单独的强化 PR，除非用户要求修复它们。

使用静态分析器作为起点，而不是作为证明（knip、depcheck 或仓库原生工具）。当未安装时，使用固定 `pnpm --config.ignore-scripts=true dlx <tool>@<version> <args...>` 运行（首先新鲜度检查固定版本）。

对于每个候选项：

- 搜索代码、配置文件、包脚本、构建工具、测试和文档中的包名称和已知导入路径。
- 检查是否由已发布的包清单、同伴合同、插件加载器、CLI 命令或动态 `require`/`import` 需要。
- 仅在没有实际使用时移除。
- 运行 `pnpm install --ignore-scripts` (+ 仓库标志) 并进行聚焦验证。

如果使用仅在脚本或配置中，考虑在 `dependencies` 和 `devDependencies` 之间移动，而不是移除。

## 步骤 3：单体仓库直接版本消除重复

查找在包清单中用多个版本/范围声明的相同直接依赖项。首先使用现有策略：精确固定、尖号范围、目录/协议使用、工作区协议或中心约束。

- 使用 `syncpack list-mismatches` 或等效项进行发现。
- 当包可以共享兼容的相同版本时，标准化直接范围。
- 优先选择清单级别的兼容性，然后再添加 `pnpm.overrides`。
- 仅用于传递收敛或安全修复使用 `pnpm.overrides`，并记录原因。

消除重复后，运行 `pnpm install --ignore-scripts` (+ 仓库标志) 并检查清单和锁文件差异。然后考虑 `pnpm dedupe`——小心使用；可能会改变传递解析。

## 步骤 4：排序传递锁文件闭包

对于每个重要的直接依赖项，估计闭包：从该依赖项可达的传递锁文件条目。

报告两者：

- **总闭包**：从依赖项可达的所有包。
- **排他性闭包**：如果移除此依赖项将消失且不由其他直接依赖项保留的包。

优先使用确定性测量：

1. 保存基线锁文件指标。
2. 从拥有清单中暂时移除一个直接依赖项。
3. 运行 `pnpm install --ignore-scripts` (+ 仓库标志)。
4. 测量锁文件行/条目减少和包计数减少。
5. 在测量下一个依赖项之前，将清单 *和* `pnpm-lock.yaml` （例如 `git checkout -- <manifest> pnpm-lock.yaml`）还原。

使用 `pnpm why <pkg>` 查找大型传递包。按影响和风险排序，而不仅仅是原始大小。

## 步骤 5：查找低风险高影响升级

使用闭包排名针对直接依赖项，其更新的次要/补丁版本可减少传递依赖项。

对于每个候选项：

- 使用 `pnpm outdated` 检查可用的非主版本。
- 审查依赖项树的变化的变更日志/发布说明。
- 新鲜度检查目标版本，然后一次一个依赖项或紧密集群升级 (`pnpm add <pkg>@<version> --ignore-scripts`)。
- 运行 `pnpm install --ignore-scripts` (+ 仓库标志) 并比较闭包指标。
- 运行聚焦测试和相关的构建/类型检查命令。

除非用户明确接受迁移风险，否则避免主版本升级。

## 步骤 6：内联简单使用

使用闭包排名查找具有小、明显使用但大型传递成本的直接依赖项。

仅当所有以下情况都为真时内联：

- 使用非常小且易于完全描述。
- 等效代码比保留依赖项更短或更清晰。
- 行为由测试覆盖或可以通过小描述性测试覆盖。
- 依赖项没有解决跨平台、安全、解析、Unicode、区域设置或规范合规性边缘情况。

当所需行为简单时，优先选择原生 API 而不是新的替换依赖项。

## 步骤 7：应用 e18e 指导

```bash
# 在新鲜度检查后固定 @e18e/cli@<version>；在 dlx 安装上禁用脚本
pnpm --config.ignore-scripts=true dlx @e18e/cli@<version> analyze
pnpm --config.ignore-scripts=true dlx @e18e/cli@<version> migrate --dry-run
```

还检查 https://e18e.dev/docs/replacements/。将建议视为候选项，而不是强制要求；验证捆绑/运行时行为并运行测试。在用户批准后，将 e18e 交换映射到 **用更好的替换**。

## 报告

总结测量影响的结果：

- `/check-npm` 结果（PASS/FAIL 摘要；如果 FAIL，链接修复）。
- 移除或移动的直接依赖项。
- 消除重复的直接版本。
- 锁文件行/条目减少。
- 当可用时，估计包或 `node_modules` 减少量。
- 推迟的高影响候选项及其原因（包括等待批准的替换）。
- 基线中的不安全协议 / CI / Renovate 发现（如果有）。
- 运行和结果的验证命令。
- 供应链：检查新鲜度（或豁免），所有安装/添加上使用 `--ignore-scripts`，`pnpm dlx` 上使用 `--config.ignore-scripts=true`。

当移除依赖于静态分析而不是运行时覆盖时，明确指出风险。

### 报告格式

仅用于 **依赖项清理发现**——不是 GitHub Actions 工作流筛选。

对于每个发现：

- **证据**：包名和版本/范围；清单路径和部分；支持信号（导入位置、`pnpm why`、knip/depcheck 命中、闭包测量、`/check-npm` 行，或仅对于 **pnpm install 政策**的工作流文件 + 步骤）。
- **决策**：一个 **依赖项筛选** 标签。
- **建议变更**：确切的清单/锁文件命令或编辑。如果尚未应用，请明确说明。
- **理由**：占用空间（排他性/总闭包）、供应链、维护或验证风险。
- **需要用户审核**：要运行的测试/构建/类型检查；同伴/插件/CLI 消费者；已发布包或动态导入风险；在 **用更好的替换** 或任何新的直接依赖项之前获得批准。

当发现是非平凡时，使用一个块（每个包或每个协议/CI 发现），而不是单行摘要。
