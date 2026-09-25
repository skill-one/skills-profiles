# Electron 应用提取

从已安装的 Electron 应用的 `app.asar` 中提取资源和代码。当存在 `.js.map` 文件时，会从嵌入的 `sourcesContent` 中恢复原始源文件；否则，使用 Prettier 格式化压缩后的代码。源映射路径首先相对于 `.js.map` 文件解析，因此像 `../../src/main.ts` 这样的捆绑路径会恢复为可读路径，如 `restored/src/main.ts`，而不是哈希占位符。始终跳过 `node_modules`。适用于 macOS 和 Windows。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用当前代理运行时暴露的内置用户输入工具** — 例如 `AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级**：如果没有这样的工具，则发出编号的纯文本消息，并要求用户回复选择的编号/答案以回答每个问题。
3. **批处理**：如果工具支持每调用多次问题，则将所有适用问题组合为单个调用；如果仅支持单次问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用是示例 — 在其他运行时中替换本地等效项。

## 脚本目录

位于 `scripts/` 子目录中。`{baseDir}` = 此 `SKILL.md` 的目录路径。解析 `${BUN_X}` 运行时：如果 `bun` 已安装 → `bun`；如果 `npx` 可用 → `npx -y bun`；否则建议安装 bun。将 `{baseDir}` 和 `${BUN_X}` 替换为实际值。

| 脚本            | 目的                                                                        |
| -------------- | ------------------------------------------------------------------------------ |
| `scripts/main.ts` | 应用发现 + asar 提取 + 源映射恢复 + Prettier 格式化 |

## 使用场景

每当用户想要查看已安装的 Electron 应用内部或检查其捆绑代码时，请使用此技能。触发短语包括：

- "提取 Electron 应用", "反编译这个 Electron 应用", "解包 app.asar"
- "显示 <app> 的源码", "查看 <app> 内部", "<app> 是如何构建的"
- "获取 Codex / Cursor / Discord / Slack / VS Code / Notion / Obsidian / ChatGPT 桌面应用的源代码"
- "提取 Electron 应用", "看 <app> 的源码", "反编译 Electron", "解包 app.asar", "还原 source map"

**应用名称**（例如 `Codex`）和**绝对路径**（例如 `/Applications/Codex.app`、一个 `.asar` 文件或 Windows 安装目录）都受支持。脚本处理两个平台的发现。

## 工作流程

**1. 确定输入。** 如果用户没有提供应用名称或路径，请询问用户。如果他们想要自定义输出目录，也请询问。

**2. 运行脚本。**

```bash
${BUN_X} {baseDir}/scripts/main.ts "<app>" [--output <dir>] [--asar <path>] [--force]
```

如果您不确定发现是否能够找到正确的捆绑包，请首先使用 `--dry-run` — 它会打印解析的路径并退出而不触摸文件系统。

**3. 处理结果。**

- **成功** → 报告输出路径和计数（提取的 / 恢复的 / 格式化的）。
- **多个匹配** → 脚本列出候选者并退出非零。向用户显示候选者，询问要使用哪一个（通过 `AskUserQuestion` 或运行时等效项），然后使用选定的绝对路径重新运行。
- **现有的非空输出目录** → 脚本在不使用 `--force` 的情况下拒绝。询问用户是否要覆盖 (`--force`) 或选择新的 `--output` 路径。
- **不支持的平台 / 无匹配** → 如果用户知道捆绑包的位置，建议传递 `--asar /full/path/to/app.asar`。

**4. 指引用户查看结果。** 默认输出目录是 `~/Downloads/<AppName>-electron-extract/`。最有趣的子目录取决于找到的内容：

- `restored/` 存在 → 从 `.js.map` 文件重建了原始源树；这是首先需要阅读的。
- 仅存在 `extracted/`（没有映射）→ `extracted/` 中的 JS/CSS 已原地使用 Prettier 格式化；从那里读取。

## 源映射路径恢复

脚本应尽可能保留源映射允许的原始文件名和目录结构：

- 当存在 `sourceRoot` 时，使用它解析每个 `sources[]` 条目，然后相对于 `extracted/` 内的 `.js.map` 文件的目录。
- 将普通的捆绑器相对路径折叠到恢复的项目树中。例如，`.vite/main/index.js.map` + `../../src/main.ts` 变成 `restored/src/main.ts`。
- 如果源路径向上爬出 `extracted/`，则在 `restored/` 下保留可读的剩余路径，而不是将其哈希化。例如，`.vite/main/index.js.map` + `../../../shared/src/lib/foo.ts` 变成 `restored/shared/src/lib/foo.ts`。
- 从源名称中删除 URL/查询装饰，包括常见的 `webpack://`、`file://` 和 `?loader` 后缀。
- 只有当源名称为空或无法简化为安全的文件路径时，才使用 `restored/__unknown/<hash>.<ext>`。
- 继续跳过 `node_modules` 和 `webpack/runtime/*` 条目；这些是捆绑器/运行时噪音，不是应用源代码。

## 使用方法

```bash
# 通过应用名称提取（默认输出：~/Downloads/Codex-electron-extract/）
${BUN_X} {baseDir}/scripts/main.ts Codex

# 通过绝对路径提取（适用于 .app 捆绑包、安装目录或 .asar 文件）
${BUN_X} {baseDir}/scripts/main.ts "/Applications/Visual Studio Code.app"
${BUN_X} {baseDir}/scripts/main.ts "C:\Users\you\AppData\Local\Programs\codex"
${BUN_X} {baseDir}/scripts/main.ts --asar /Applications/Codex.app/Contents/Resources/app.asar Codex

# 自定义输出
${BUN_X} {baseDir}/scripts/main.ts Codex --output ~/work/codex-source

# 预览发现而不写入任何内容
${BUN_X} {baseDir}/scripts/main.ts Codex --dry-run

# 覆盖现有的输出目录
${BUN_X} {baseDir}/scripts/main.ts Codex --force

# 机器可读结果（一行 JSON 输出到标准输出）
${BUN_X} {baseDir}/scripts/main.ts Codex --json
```

## 选项

| 选项           | 短选项 | 描述                                                     | 默认值                                  |
| -------------- | ------ | ------------------------------------------------------- | -------------------------------------- |
| `<app>`        |        | 应用名称或绝对路径。如果给出 `--asar` 则非必需。           | —                                      |
| `--output`     | `-o`   | 输出目录                                                | `~/Downloads/<AppName>-electron-extract` |
| `--asar`       |        | 覆盖解析的 `.asar` 路径                                  | 自动发现                              |
| `--force`      | `-f`   | 允许写入到非空的现有输出目录                           | false                                  |
| `--skip-format` |        | 跳过 Prettier 格式化                                    | false                                  |
| `--skip-restore` |        | 跳过源映射恢复                                          | false                                  |
| `--no-unpacked` |        | 不与 `app.asar.unpacked/` 一起复制                     | false                                  |
| `--dry-run`    |        | 打印解析的路径并退出而不写入                           | false                                  |
| `--json`       |        | 在标准输出上发出一行 JSON 摘要（抑制正常输出）           | false                                  |

## 输出布局

```
~/Downloads/<AppName>-electron-extract/
├── extract-report.json          # JSON 摘要：计数、警告、解析的路径
├── extracted/                   # 原始 asar 内容（如果没有映射则原地 Prettier 格式化）
│   └── ...                      # node_modules 保持不变（从格式化中跳过）
├── extracted.unpacked/          # 如果存在，则从 <asar>.unpacked/ 复制
│   └── ...                      # 本地模块 (.node)、大型资源
└── restored/                    # 如果至少有一个可用的 .js.map 则存在
    └── <原始/源树>              # 从每个 .js.map 中的 sourcesContent 重建
```

## 注意事项

- **node_modules** 始终被跳过 — 无论是源映射恢复还是 Prettier 格式化 — 因为在检查应用时，依赖项是噪音。
- **源映射恢复** 仅在 `.js.map` 嵌入 `sourcesContent` 时有效。这是现代捆绑器（webpack、esbuild、Vite、rollup）的常见情况。如果映射引用了未嵌入的外部 `.ts`/`.js` 文件，则跳过该映射并将相应的 `.js` 使用 Prettier 格式化。跳过的映射在 `extract-report.json` 的 `warnings` 下列出。
- **可读路径优先于哈希** — 不要将源映射路径中的 `../` 段视为自动不安全。首先从映射位置解析它们，然后清理最终的输出路径，使其仍然保持在 `restored/` 下。哈希回退仅用于不可用的源名称。
- **应用发现** 在 macOS 上搜索 `/Applications` + `~/Applications`，在 Windows 上搜索 `%LOCALAPPDATA%\Programs`、`%PROGRAMFILES%`、`%PROGRAMFILES(X86)%`、`%APPDATA%`。如果发现多个匹配项，脚本会退出并列出它们 — 使用绝对路径重新运行。在 Linux 或其他平台上，显式传递 `--asar /path/to/app.asar`。
- **安全性** — 脚本拒绝写入 `/`、用户主目录直接或当前工作目录，并且在不使用 `--force` 的情况下拒绝填充现有的非空输出目录。
- **无全局安装** — `@electron/asar` 和 `prettier` 通过 `npx -y` 动态解析。第一次运行会较慢，因为 npx 会缓存它们。
