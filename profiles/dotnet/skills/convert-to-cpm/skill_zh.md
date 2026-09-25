# 转换为中央包管理

在 `Directory.Packages.props` 中集中管理包版本，同时保持项目行为并生成可审查的转换前/后证据。

## 首先选择模式

在运行构建或更改文件之前执行此操作。

1. **保护模式** -- 如果任何在范围内的项目使用 `packages.config`，则停止。解释 CPM 需要 `PackageReference` 并建议先进行迁移。不要创建或修改文件。
2. **包维护模式** -- 更新、对齐、提升或同步包的请求授权进行这些包编辑，而不是 CPM 转换。审计命名范围，解决请求的版本，更新现有的项目/共享版本声明，并从建立其适用 `global.json` 的目录中恢复/构建每个受影响 CLI 目标。仅在版本或对齐策略不明确时才询问。不要创建或修改 `Directory.Packages.props`，删除用于 CPM 的版本，或捕获转换工件。完成包工作后，建议将 CPM 作为持久性后续操作。
3. **转换模式** -- 仅在用户明确要求采用、启用或转换为 CPM 时使用。遵循以下工作流程。

如果范围不明确，请在继续之前询问一次。

### 默认执行计划

- **保护**：使用最小范围的检测传递，然后回答并停止。
- **包维护**：使用紧凑的审计，仅在其现有位置编辑请求的包版本，验证受影响的目标，然后建议 CPM。不要读取转换引用或进入转换工作流程。
- **转换**：将预检、基线、审计/变异、最终验证和报告工作分批处理，以避免重复操作。仅在需要针对 CPM 特定证据进行有针对性的后续操作时才重新审视某个阶段。

此计划是一个效率默认值，而不是硬性上限。永远不要为了节省时间而省略范围内的项目、导入的 `.props`/`.targets` 文件、检测到的复杂性、所需的验证或交付成果。在实用的情况下分批完成工作。

## 输入

| 输入 | 必填 | 规则 |
|------|------|------|
| 范围 | 是 | 包含要检查或转换的项目、解决方案或目录 |
| 冲突策略 | 对于包维护或存在冲突的转换 | 如果用户已经提供了一个策略，例如“使用最高版本”，则应用它而不再询问，并记录其影响。否则在审计后停止并询问编辑前的决定。 |

## 仅在需要时读取引用

永远不要预加载所有引用。

| 条件 | 读取 |
|------|------|
| 进入转换基线或生成包差异 | [baseline-comparison.md](references/baseline-comparison.md) |
| 检测到冲突、条件引用、共享导入、安全问题或 `VersionOverride` | [audit-complexities.md](references/audit-complexities.md) |
| 位置不明确或需要条件 `PackageVersion`/`VersionOverride` | [directory-packages-props.md](references/directory-packages-props.md) |
| 包版本使用 MSBuild 属性 | [msbuild-property-handling.md](references/msbuild-property-handling.md) |
| 转换后还原或构建失败 | [validation-and-errors.md](references/validation-and-errors.md) |
| 编写最终报告 | [report-template.md](references/report-template.md) |

## 转换工作流程

### 1. 范围和预检

- 解析项目/解决方案范围。对于解决方案，列出其项目。对于目录，仅在该目录下搜索并创建一个明确的目标集，以涵盖完整范围：使用每个适用的 `.sln`/`.slnx`，然后添加每个未被解决方案覆盖的项目。验证每个范围内的项目是否都被覆盖，并避免对在多个目标中出现的项目进行重复工作。仅在重叠目标或存储库边界使预期覆盖不明确时才询问；永远不要要求用户选择一个目标，如果那样会遗漏范围内的项目。
- 将 CPM 管理范围与 CLI 目标分开确定。将共享一个中央版本策略的项目分组，并在每个组的第一个共同祖先处放置一个 `Directory.Packages.props`，同时尊重现有的最近文件边界。多个 CLI 目标可以共享一个 CPM 文件；独立的项目组可能需要单独的文件。
- 检查 `packages.config`；如果找到，切换到保护模式并停止。
- 检查范围和祖先中的 `Directory.Packages.props`。如果 CPM 已完全启用，则报告并停止。如果存在部分文件，则保留它，仅在预期范围不明确时才询问。
- 在解析范围内选择一个公共工件目录，通常是目标的第一共同祖先。使用明确的路径进入它，用于每个 binlog、包快照和报告。
- 从每个目标解决方案/项目目录或另一个建立其适用 `global.json` 的目录运行每个目标的 .NET 命令，而不是从无关的父工作区运行。
- 当用户提供了范围时，不要检查无关的项目或主机工具配置。

### 2. 捕获基线

读取 [baseline-comparison.md](references/baseline-comparison.md)。对于每个目标，从该目标的命令目录中一次确定活动 SDK，并选择该版本的文档命令语法。如果 SDK 解析失败或 SDK 无法处理请求的解决方案格式，则停止并报告先决条件；除非用户要求，否则不要更改主机 SDK 或存储库 SDK 策略。

然后使用一个命令批处理来：

1. 清理、还原和构建每个明确的目标。使用 `baseline.binlog` 用于一个目标，或为多个目标使用唯一的 `baseline-<target-key>.binlog`。
2. 为每个目标写入解析的包，而无需再次还原。使用 `baseline-packages.json` 用于一个目标，或为多个目标使用匹配的 `baseline-packages-<target-key>.json`。
3. 保持正常命令输出简洁。在有用时将完整输出保存到工件；仅在失败时检查错误，并且永远不要将 binlog 作为文本读取。

完成所有基线后再进行编辑。如果任何基线构建失败，则停止而不修改文件，并保留所有已生成的工件。

### 3. 使用有针对性的清单进行审计

使用所有基线快照以及对范围内项目、`.props` 和 `.targets` 文件的有针对性扫描。识别：

- 包 ID、解析版本和消费项目
- 版本冲突
- 基于 MSBuild 属性的版本及其定义
- 条件 `PackageReference` 项目
- 包含包引用的导入文件
- 现有的 `VersionOverride` 使用

对于复杂范围，完成所有适用项目和导入文件中的上述每个项目；不要在找到第一个冲突后停止。

默认情况下，不要运行广泛的 `--outdated` 或 `--deprecated` 扫描。在编辑之前，当用户请求安全信息、必须验证已知建议，或冲突解决将项目移动到主要包版本时，尝试进行范围的 `--vulnerable --include-transitive` 查询。记录紧凑的发现结果、“未发现建议”或无法运行检查的原因。如果由于身份验证、包源或离线约束而无法运行高风险检查，请显示不确定性并确认用户的策略，而不是将其静默处理为安全。不要在 CPM 转换作为一部分时升级到范围内已有的最高版本。

呈现冲突及其影响。明确将主要版本对齐分类为高风险，将次要/补丁对齐分类为中等风险，而无需执行额外的在线扫描。如果用户提供了冲突策略，则继续。否则在编辑前询问未解决的决策并停止。

### 4. 创建 CPM 文件并更新引用

- 在其计算的管理范围内创建或更新每个必需的 `Directory.Packages.props`，并将 `ManagePackageVersionsCentrally` 设置为 `true`。
- 按字母顺序为每个包添加一个 `PackageVersion`，并保留所需的 `target-framework` 条件。
- 仅从项目和导入文件中管理的 `PackageReference` 项中删除 `Version`。
- 保留条件、空白和其他所有元数据，例如 `PrivateAssets`、`IncludeAssets`、`ExcludeAssets`、`GeneratePathProperty` 和 `Aliases`。
- 仅在所选策略需要时使用 `VersionOverride`。

对于 MSBuild 版本属性，请遵循 [msbuild-property-handling.md](references/msbuild-property-handling.md)。当用户指示内联时，在相同的变异批处理中包含字面 `PackageVersion` 和删除过时的属性定义。在最终验证之前，分别验证：

1. 在范围内的项目、`.props` 或 `.targets` 文件中不再存在 `$(PropertyName)` 引用。
2. 对于每个选择删除的属性，不再存在 `<PropertyName>...</PropertyName>` 定义。

不要依赖 `$()` 引用扫描来证明 XML 属性定义已被删除。

### 5. 验证和比较

使用 [baseline-comparison.md](references/baseline-comparison.md)，验证所有项目、共享文件和属性编辑后的最终磁盘状态。使用一个命令批处理来：

1. 在所有 CPM 编辑后清理、还原和构建每个明确的目标。使用 `after-cpm.binlog` 用于一个目标，或为多个目标使用匹配的 `after-cpm-<target-key>.binlog`。
2. 为每个目标写入解析的包，而无需再次还原。使用 `after-cpm-packages.json` 用于一个目标，或为多个目标使用匹配的 `after-cpm-packages-<target-key>.json`。
3. 生成紧凑的每个项目更改/未更改比较，而无需打印或重新读取完整的 JSON 文件。
4. 如果解析版本发生变化，并且存储库为受影响项目提供了常规的、范围的测试命令，则使用 `--no-build --no-restore` 运行它并记录结果。如果测试需要大量设置、广泛的基础设施或用户批准，则建议确切的范围命令。中立的版本转换不需要自动运行测试。

如果还原或构建因 CPM 相关错误而失败，请读取 [validation-and-errors.md](references/validation-and-errors.md)，仅检查相关错误行，进行有针对性的修正，并重新运行受影响的验证。对于 SDK、身份验证、包源、文件锁定、测试主机或其他环境故障，请报告障碍而不是更改机器或扩大调查。

如果测试运行在成功构建后失败，请仅检查足够的输出以确定是否由 CPM 包解析引起。仅在证据明确标识 CPM 缺陷时才进行有针对性的修正；否则记录失败和推荐的用户操作，而无需扩展到测试主机、SDK、输出目录或依赖复制调试。

### 6. 编写报告

现在读取 [report-template.md](references/report-template.md)，而不是之前。在工件旁边创建 `convert-to-cpm.md`。它必须包括六个必需部分、每个明确的目标和 CPM 管理范围、具体的冲突影响、汇总的包比较、风险级别、后续操作、工件使用和每个共享的 `.props`/`.targets` 文件检查或更改的名称。在最终响应中，提及这些共享文件、风险级别以及任何条件引用和目标框架如何被保留。除非验证发现遗漏或不正确的证据，否则避免在验证后重写报告。

## 必需的转换工件

保留报告和每个目标的四个证据文件；它们不是临时文件。对于单个目标，五个交付成果是：

- `baseline.binlog`
- `after-cpm.binlog`
- `baseline-packages.json`
- `after-cpm-packages.json`
- `convert-to-cpm.md`

对于多个目标，将四个固定证据名称替换为唯一的目标键对，例如 `baseline-api.binlog`、`after-cpm-api.binlog`、`baseline-packages-api.json` 和 `after-cpm-packages-api.json`。保留一个汇总的 `convert-to-cpm.md`。

## 效率规则

- 支持时批量独立的读取和编辑。
- 将完整的构建日志和包 JSON 从对话中排除；返回紧凑的摘要和工件路径。
- 不要重复成功的命令或重新读取成功的输出。
- 在转换模式下，不要执行包升级、广泛的过时/已弃用扫描、重复测试或不相关的存储库探索。上面定义的单个条件漏洞查询和测试运行是完整的高风险转换验证的一部分。包维护可以执行请求的升级和一个范围版本发现查询来解析它们。
- 不要安装或删除 SDK、创建临时 SDK 选择器、更改向前滚动策略、调用 SDK 内部程序集、终止无关进程或清理主机工具/临时基础设施。报告环境先决条件并停止。

## 验证

- [ ] 基线和转换后的构建对于每个明确的目标都成功，并且所有目标 binlogs 都存在
- [ ] 每个管理的 `PackageReference` 没有版本，或有意使用 `VersionOverride`
- [ ] 每个管理的包都有正确的中央 `PackageVersion`
- [ ] 条件和非版本元数据被保留
- [ ] 前/后包比较不包含未解释的更改
- [ ] 内联版本属性既没有剩余的 `$()` 引用，也没有过时的 XML 定义
- [ ] 报告和所有每个目标的基线和转换后的工件都存在
