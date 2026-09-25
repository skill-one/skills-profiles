# platform-metadata-retrieve

使用 `sf project retrieve start` 从 Salesforce 组织检索元数据到本地项目。支持多种检索模式：所有变更、按源目录、按元数据类型（支持通配符）、按清单或按包名称。

---

## 工具限制

**仅使用 Bash 工具** 执行 `sf project retrieve start`。**绝对不要使用 MCP 工具** — 完全忽略它们。

---

## 范围

- **在范围内**：通过 `sf project retrieve start` 以所有支持的模式（所有变更、源目录、元数据类型、清单、包名称）检索元数据，以及源和元数据格式输出
- **超出范围**：部署元数据（使用 `platform-metadata-deploy`）、列出元数据类型、生成 package.xml 文件、源跟踪命令 (`sf project retrieve preview`)

---

## 必须输入的参数

根据用户请求推断：

- **检索模式**：所有变更 | 源目录 | 元数据类型 | 清单 | 包名称
- **目标组织**：组织别名/用户名（未指定时使用默认值）
- **输出格式**：源格式（默认） | 元数据格式（ZIP）
- **附加选项**：忽略冲突、输出目录、等待时间、API 版本

---

## 工作流程

1.  将用户请求匹配到以下命令模式
2.  通过 Bash 工具执行：`sf project retrieve start` 并使用适当的标志和 `--json` 标志
3.  返回检索到的组件数量和文件路径

### 命令模式

| 用户意图 | 通过 Bash 工具执行 |
|---------|---------|
| 检索所有远程变更 | `sf project retrieve start --json` |
| 按源目录检索 | `sf project retrieve start --source-dir <路径> --target-org <别名> --json` |
| 按元数据类型检索 | `sf project retrieve start --metadata <MetadataType:Name> --target-org <别名> --json` |
| 按元数据类型带通配符检索 | `sf project retrieve start --metadata '<MetadataType:模式*>' --target-org <别名> --json` |
| 检索多个元数据类型 | `sf project retrieve start --metadata <类型1> --metadata <类型2> --target-org <别名> --json` |
| 按清单检索 | `sf project retrieve start --manifest <路径/to/package.xml> --target-org <别名> --json` |
| 按包名称检索 | `sf project retrieve start --package-name <包名称> --target-org <别名> --json` |
| 检索到元数据格式（ZIP） | `sf project retrieve start --source-dir <路径> --target-metadata-dir <输出> --unzip --target-org <别名> --json` |
| 忽略冲突 | `sf project retrieve start --source-dir <路径> --ignore-conflicts --target-org <别名> --json` |

---

## 规则 / 限制

| 限制 | 理由 |
|-------|-------|
| 必须始终使用 `--json` 标志 | 提供结构化输出，用于可靠的解析和错误处理 |
| 必须在 Salesforce 项目内运行 | 命令需要 `sfdx-project.json` 在仓库根目录 |
| 通配符模式必须加引号 | Shell 扩展会破坏未加引号的通配符，如 `ApexClass:My*` |
| 不能混合 `--manifest` 与 `--metadata` 或 `--source-dir` | 互斥标志 — 命令将报错 |
| 检索所有变更需要源跟踪 | 生产组织不支持源跟踪 — 必须使用其他检索模式 |
| `--ignore-conflicts` 仅在可跟踪组织中有效 | 对生产组织无效；仅适用于 Scratch/Sandbox |
| `--output-dir` 必须在项目目录内 | 命令验证输出路径在项目边界内 |
| `--output-dir` 不能与包目录匹配 | 如果目标匹配 `sfdx-project.json` 的 packageDirectories，命令将失败 |
| 默认等待时间为 33 分钟 | 使用 `--wait` 标志覆盖大检索的等待时间 |
| 包检索仅用于参考 | 检索的包元数据不应添加到源代码控制用于开发 |
| 检索 CustomField 时自动包含 CustomObject | 当检索 CustomField 时，CLI 会自动添加 CustomObject 以获取完整上下文 |

---

## 故障排除

| 问题 | 解决方案 |
|-------|------------|
| "此命令必须在 SFDX 项目内运行" | 不在 Salesforce 项目目录内 — 使用 `cd` 切换到项目根目录，其中包含 `sfdx-project.json` |
| "找不到 <别名> 的组织" 错误 | 组织别名不存在或未认证 — 使用 `sf org list` 验证 |
| "此组织不支持源跟踪" | 生产组织不允许 "检索所有变更" 模式 — 使用 `--source-dir`、`--metadata` 或 `--manifest` 代替 |
| "ERROR running project retrieve start: 不能混合 --manifest 与 --metadata 或 --source-dir" | 移除冲突标志 — 仅使用一种检索模式 |
| 通配符模式检索不到任何内容 | 模式未加引号 — 用单引号括起来：`'ApexClass:My*'` |
| "sfdx-project.json 中的包目录路径不存在" | 输出目录与包目录冲突 — 使用不同路径 |
| "输出目录必须在项目中" | `--output-dir` 路径在项目边界外 — 使用项目内的相对路径 |
| 检索超时 | 使用 `--wait 60` 增加等待时间，用于大元数据量 |
| 检索的文件覆盖本地变更 | 使用 `--output-dir` 检索到不同位置，或先提交本地变更 |
| SourceConflictError 与冲突表 | 在可跟踪组织（Scratch/Sandbox）中检测到本地和远程之间的冲突 — 手动解决冲突或使用 `--ignore-conflicts` 强制覆盖 |

---

## 输出预期

命令返回包含检索组件详细信息的 JSON 输出。

参考 `examples/success_output.json` 和 `examples/error_output.json` 了解响应结构。

---

## 跨技能集成

| 需要 | 代理给 |
|------|-------|
| 将元数据部署到组织 | `platform-metadata-deploy` 技能 |
| 预览检索而不执行 | 执行 `sf project retrieve preview --target-org <别名> --json` |
| 列出可用元数据类型 | 执行 `sf org list metadata-types --target-org <别名> --json` |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `examples/success_output.json` | 了解成功检索响应结构 |
| `examples/error_output.json` | 处理常见错误场景 |
| `references/retrieval_modes.md` | 了解所有检索模式的详细说明以及何时使用每种模式 |
| `references/cli_flags.md` | 获取完整的标志参考和用法模式 |
