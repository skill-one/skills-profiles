# Expo 技能评估

评估 `plugins/expo/skills/` 中的技能在 Expo Go 中的触发准确性、生成代码质量以及/或运行时渲染。

要求：macOS 配备 Xcode（iOS 模拟器）、至少有一个 AVD 的 Android SDK 以及 `bun`。不假设其他设备工具。

工作区根目录：`/private/tmp/expo-skill-eval-<skill-name>/iteration-N/`（例如 `/private/tmp/expo-skill-eval-expo-ui/iteration-4/`）。

## 开始前 — 明确范围

**确认以下所有内容，在管道工作之前 — 不要跳过任何**（如果请求中已经说明选择，则可以跳过给定的项目）。将它们分批处理为 `AskUserQuestion` 调用，每个调用最多 4 个问题，按此顺序：

1. **选择要评估的技能**（如果请求中不明显）。
2. **提示** — 哪些提示驱动评估。内置提示（来自技能的评估用例）**全部预先选择**；删除任何提示，添加自定义文本提示，或**从上传的屏幕截图构建**（目标 UI 是技能必须重现）。见 **提示** 下面。
3. **要验证的内容** — 三个选项的多选：运行时 + 截图 / 触发准确性 / 代码检查（无设备）。见 *要验证的内容* 下面。
4. **Expo SDK** — 最新版本（默认，自动检测）或固定版本。
5. **运行器** — Expo Go（默认）或开发构建。
6. **平台** — iOS / Android / Web（始终提供所有三个）。
7. `claude -p` 的 **权限标志** — 跳过权限（默认）或接受编辑。
8. **查看器交付** — 仅本地（默认）或发布可共享的 Artifact。
9. **如果选择触发准确性** — 确认发布的 `expo` 插件已禁用（或未安装）。

每个都详细说明如下。项目 4-6（SDK、运行器、平台）自然地适合一个 `AskUserQuestion` 调用。

**如果请求中不明确要评估的技能**，请列出 `plugins/expo/skills/` 中的可用技能，并询问要评估哪一个。

**测试技能的加载方式 — 两个机制，每个阶段一个**（不要全局选择一个）：executor 通过 **文件路径** (`SKILL_PATH = plugins/expo/skills/<skill>/SKILL.md`, 显式读取), 触发评估将其加载为 **插件** (`--plugin-dir plugins/expo`, 这样模型可以自动从其描述中选择它）。两者都指向 *本地、存储库* 版本 — 这就是你要评估的内容。你不需要任何特殊标志来 *启动* harness 会话本身（harness 通过存储库路径找到技能）；这些机制适用于 `claude -p` 它生成的子进程。见步骤 1 和 3 的原因。**一个预先运行检查（当触发评估在范围内时需要）：** 如果 *发布的* `expo` 插件已安装/启用，请在启动 harness 之前禁用它（通过 `/plugin`）并在之后重新启用。单个禁用是全局配置更改，此会话和生成的 `claude -p` 子进程都继承。为什么触发评估需要它：该阶段通过 `--plugin-dir` 加载本地技能，第二个已安装的 `expo` 与之冲突 — 模型可能会触发 *发布的* `expo:expo-ui`，由于检测只看到工具调用名称，所以会默默地评估已发布的描述而不是你的本地编辑（冲突也可能导致错误）。**executor / 运行时 / 静态** 阶段不受影响 — 它们通过本地 `SKILL_PATH` 读取要测试的技能，没有 `--plugin-dir` — 所以没有触发评估的运行可以跳过禁用。禁用 `expo` **不会** 禁用 `expo-skill-eval`（一个独立的存储库技能，不是 `expo` 插件的一部分），所以 harness 保持可用。

**以明确的前置确认方式向用户显示** — 与确认要评估的技能相同的方式。当触发评估在范围内时，请要求用户确认已发布的 `expo` 插件已禁用（或未安装）*在* 开始步骤 1 之前；如果它仍然启用，请暂停并让他们通过 `/plugin` 禁用它。不要运行触发评估，直到他们确认 — harness 无法可靠地检测已安装的插件（读取全局插件配置或 `claude plugin list` 会提示），所以这是一个手动确认，而不是自动检查。

**选择提示 — 内置、自定义或目标屏幕截图。** 提示是 *输入*，它们驱动 executor（带技能和不带技能）；它们与你要 *验证* 的内容是分开的。使用 `AskUserQuestion` 确认（如果请求中已经命名了提示，则跳过）：

- **内置提示** — 通过阅读要测试的技能（其 `SKILL.md` + `references/`) 和 `references/runtime-matrix.md` 生成有代表性的提示，覆盖技能的标准用例。 （如果技能已经在 `evals/evals.json` 下提供评估用例，则将其 `prompt` 字段合并进来 — 但大多数技能都没有，所以通常需要推导出来。）**预先选择所有**，以便默认运行执行技能的标准用例；允许用户取消选择任何内容。
- **自定义文本提示** — 用户输入的即时提示。不要为这个分配一个专门的选项槽：`AskUserQuestion` 自动添加一个 **"输入一些内容"** / 其他条目，输入的内容将变为自定义文本用例。
- **从上传的屏幕截图构建** — 用户提供目标屏幕截图的路径（要重现的 UI）。executor 告知它打开它（通过其 Read 工具）并构建一个匹配的应用；用例记录路径为 `reference_image`，并且评分器将生成的应用与该目标进行比较（步骤 6）。这是 UI 技能最强的视觉测试：**构建这个。**

**尊重 `AskUserQuestion` 的 4 选项/问题限制，并按此优先级**（要避免的 bug：一旦四个槽位填满，上传选项会无声地丢失）：)

1. **始终预留一个槽位用于 "从上传的屏幕截图构建"。** 这是视觉评估的全部意义，并且绝不能是丢失的选项。
2. **不要添加一个明确的 "自定义文本提示" 选项** — 自动 "输入一些内容" / 其他条目已经涵盖了它。
3. 填充其余 ≤3 个槽位为内置/代表性提示，**预先选择**。如果有超过 3 个，将它们合并为一个预先选择的 **"所有内置提示 (默认)"** 选项，并提供子集选择，以便上传选项仍然适用。

将其作为 **多选** 呈现。当选择 "从上传的屏幕截图构建" 时，在后续步骤中询问目标图像路径。每个选择的提示（内置、输入或图像）都成为一项评估用例（带技能和不带技能运行）。

**除非请求使其明确，否则始终确认要验证的内容**。提供这些选项并允许用户选择一个或多个（基于技能的 `references/runtime-matrix.md` 条目的默认值）：)

| 选项 | 它的作用 | 建议作为默认值的时间 |
|------|----------|----------------------|
| **运行时 + 截图** | 完整管道：fixture → executor → 静态门控 → 在 iOS/Android 上运行应用程序并截图。运行器（Expo Go 或开发构建）是另一个问题 — 不要在这里命名。 | **默认** 对于任何渲染应用程序屏幕的技能（`references/runtime-matrix.md` 中的 `expo-go`/`dev-build` 行）。需要启动的模拟器/模拟器。 |
| **触发准确性** | 通过 `claude -p` 运行现实的提示，检查技能是否被读取。衡量召回率（仅针对应该触发查询）。 | 总是作为一个独立的检查很有用。 |
| **代码检查（无设备）** | `tsc --noEmit` + 差异感知的代码检查 + `expo export`，以及评分器检查生成的代码是否符合你提供的任何自定义期望。无设备。 | **默认** 对于 `static-only` 和 `n/a` 技能，以及当你不想运行设备时，验证代码模式（正确的导入路径、`Host` 包装器等）无需运行应用程序。 |

**将它们作为 ONE 多选问题呈现 — *"你想验证什么?"*** 这些是 *评分维度*（如何判断构建的内容）— 与 **提示** 阶段（要构建的内容）是分开的。用户可以选择任何组合。当提示是一个 **上传的屏幕截图**（见 **提示**），包括 **"运行时 + 截图"**，以便 harness 捕获结果以供评分器评分（步骤 6）。这是 UI 技能最强的视觉测试：**构建这个。**

读取 `references/runtime-matrix.md` 以找到技能的默认模式，然后再建议。如果请求已经指定了模式（例如，“只检查它是否触发”，“在设备上运行它”），请跳过问题并继续。

**选择 Expo SDK 版本 — 一次，在前端。** 使用 `bash /abs/path/expo-skill-eval/scripts/latest-sdk.sh` 检测最新版本（它打印出主版本号，例如 `56`；内部它使用 `bun` 运行 `npm view expo dist-tags --json` 并通过 `JSON.parse`/`semver` 读取主版本号，并且它受 bash-scripts 规则的覆盖 — 所以不要在行内自己运行注册查询，这会提示）。然后使用 `AskUserQuestion` 确认：默认使用最新 SDK，或允许用户固定一个较旧的版本（例如，以重现版本特定的问题）。在构建 fixture 时使用选定的版本 — 将它作为 `<sdk>` 参数传递给 `make-fixture.sh`，并将它写入每个评估用例的 `runtime.sdk`。如果请求已经命名了版本 (“在 SDK 54 上评估”)，请跳过检测并使用它。

**默认为最新版本** — 它与 `expo start` 在设备上安装的 Expo Go 兼容。固定比设备安装的 Expo Go 更旧的 SDK 会导致 `expo start` 尝试提示“安装推荐的 Expo Go 版本？”；在没有 TTY（快照脚本从 `/dev/null` 读取 stdin）的情况下，它会在 `Input is required, but 'npx expo' is in non-interactive mode` 的情况下终止，并且 **所有快照都会失败**。因此，只有在您也在模拟器/模拟器上预先安装了匹配的 Expo Go 时，才固定一个较旧的 SDK — 否则坚持使用最新版本。

**选择运行器 — Expo Go（默认）或开发构建。** 使用 `AskUserQuestion` 确认（如果请求中已经说明哪个）：

- **Expo Go (默认)** — 快照脚本使用 `expo start --ios` / `expo start --android` 原样运行。快速（无需原生编译），并且它运行 Expo Go 封装的所有内容（包括 SDK 56+ 上的 `@expo/ui`）。无法运行自定义原生代码（expo-modules、配置插件、不在 Expo Go 中的原生依赖）。
- **开发构建** — 快照脚本使用 `expo run:ios` / `expo run:android` 替代，为每个 fixture 编译一个原生开发客户端。用于输出需要自定义原生代码的技能（否则原本是 `static-only` 的用例）。非常慢 — `expo run` 预编译并原生编译每个 fixture（每个 fixture 都需要几分钟，尤其是第一个），并且需要完整的 iOS/Android 构建工具链 — 所以只有在技能实际需要原生代码时才选择它。**磁盘密集型：** 每个 fixture 的原生构建大小为多 GB。快照阶段在每次 fixture 后运行 `clean-fixture.sh` 以将峰值使用率保持在 ~一个构建，但仍然更喜欢较少的评估用例和 **单个平台** 用于开发构建运行，并保留一些 GB 的空闲空间。`clean-fixture.sh` 删除每个 fixture 的构建输出（`node_modules`、`ios`、`android`、`.expo`、`dist` 以及 fixture 的 iOS DerivedData）并保留应用程序源代码 + git。开发构建磁盘的杠杆是 **较少的评估用例 + 单个平台** — 它只回收每个 fixture 的构建输出，并且永远不会触及共享依赖缓存，所以没有任何内容会被重新下载。

通过 `EXPO_SKILL_EVAL_RUNNER` 环境变量将选择传递给快照脚本（默认为 `expo-go`，或 `dev-build`），并在每个评估用例的 `runtime.mode` (`expo-go` 或 `dev-build`) 中反映它。见步骤 5。

**运行 + 截图（评估用例之间串行）**

写 `run_snapshots.py` 并使用 `python3` 运行它。模拟器和模拟器是共享资源，所以这个 orchestrator **串行** 运行（没有线程池）：对于通过静态门控通过的每个应用程序，以及每个平台，它 `os.makedirs` `outputs/` 目录并调用 `subprocess.run(["bash", "<scripts>/snapshot-<platform>.sh", app, f"{outputs}/<platform>.png", port], env={**os.environ, "EXPO_SKILL_EVAL_RUNNER": runner}, …)`. 将端口作为位置参数传递：使用 `8081` 对于 iOS 和 `8082` 对于 Android — `expo run:ios/android --port N` 是支持的，使用不同的端口可以避免端口冲突，如果您将来并行化。屏幕截图将保存在运行的 `outputs/` 目录中，以便查看器内联显示。

**每次构建后回收磁盘 — 对于 `dev-build` 运行至关重要。** 一旦选择了所选平台的每个应用程序的屏幕截图（并且在 *下一个 fixture 构建之前*），调用 `subprocess.run(["bash", "<scripts>/clean-fixture.sh", app])`. 每个快照脚本都会留下多 GB 的原生构建输出（iOS Pods + DerivedData, Android Gradle 构建在 Android 上启动后）。如果没有触发评估，评估用例 × 配置 × 迭代会堆积并导致运行时磁盘填满（您会看到的稳定性是磁盘填满）。`clean-fixture.sh` 删除重生成目录（`node_modules`、`ios`、`android`、`.expo`、`dist`）以及 fixture 的 iOS DerivedData，保留应用程序源代码 + git，以便评分器的 `git diff` 仍然有效。使用串行截图 + 每个用例的 `git diff`，以便 grader 可以看到 executor 改变了什么（对评分者很有用）。

`runner` 是前端的选择（默认为 `expo-go` 或开发构建）。快照脚本尊重 `EXPO_SKILL_EVAL_RUNNER`：`expo-go` 启动时执行 `expo start --<platform>`（以及 Expo Go 安装/深度链接的舞蹈）；`dev-build` 启动时执行 `expo run:<platform> --port <port>`，这会编译并安装一个原生开发客户端，跳过 Expo Go 步骤。脚本已经将 `dev-build` 超时设置为 900s，但如果第一个原生编译需要，请将 `EXPO_SKILL_EVAL_BUNDLE_TIMEOUT` 设置得更高。`make-fixture.sh` 在每个 fixture 中预安装 `expo-dev-client`，以便在 `expo run` 尝试深度链接打开应用程序时注册开发客户端 URL 方案。**dev-build 重新启动：** Metro 启动后，脚本通过 `xcrun simctl launch`（iOS）和 `adb shell am start -n <pkg>/.MainActivity`（Android）重新启动应用程序 — 两者都避免了 URL 方案深度链接首次启动时触发的“在 X 中打开”系统对话框。如果 `host` 在给定机器上自我中止模拟器（Apple Silicon 上的 qemu `SIGABRT` 深入gfxstream/Metal — 可能），请编辑 `snapshot-android.sh` 中的 `GPU_MODE` 为软件模式（`guest` 渲染可靠但缓慢 — 增加稳定时间；避免 `swiftshader_indirect`，它在 arm64 上启动时挂起）。`snapshot-web.sh` 仅当 `platforms` 包括 Web 时运行。每个脚本在旁边写入 Metro 日志（`<name>.metro.log`）— 将它作为评分器输入的一部分。如果脚本退出非零，它仍然尝试最佳尝试截图（错误屏幕本身也是证据）。**dev-build 重新启动：** Metro 启动后，脚本通过 `xcrun simctl launch`（iOS）和 `adb shell am start -n <pkg>/.MainActivity`（Android）重新启动应用程序 — 两者都避免了 URL 方案深度链接首次启动时触发的“在 X 中打开”系统对话框。**Web 运行方式：** 通过 `snapshot-web.sh`（使用 Playwright via `bunx`；首次运行会下载 Chromium）运行，无论运行器如何（`expo run` 仅限原生），并且它是最少使用的路径。

在捕获所有迭代屏幕截图后，始终生成查看器 — 将工作区根传递给已检查的脚本：

```bash
python3 /abs/path/expo-skill-eval/scripts/generate_viewer.py /private/tmp/expo-skill-eval-<skill>
```

它将 `viewer.html` 写入工作区根目录（在 `iteration-N/` 上一级）并自行打开它（通过 `webbrowser.open`）— 所以不需要单独的 `open` 命令（并且没有 `Bash(open:*)` 规则）。见 **查看器** 部分以下。

### 生成查看器（仅在前端确认后）

本地 `viewer.html` 始终生成。**只有在用户在前端确认中选择 "发布可共享的 Artifact"** 时，在运行结束前才会将它渲染到 claude.ai Artifact 中 — 从不未经确认就发布（它是面向外部的，已发布的页面可以被缓存/索引）。机制：

- `Artifact` 工具将文件包裹在其自己的 `<!doctype html>…<head></head><body>` 骨架中，所以传递给它的文件必须是 **页面内容** — 内联 `<style>`/`<script>`、base64 `data:` 图片，以及 `<title>`，但 **没有** 自己的 `<!DOCTYPE>/<html>/<head>/<body>` 标签（一个完整的独立文档会被双重包装并渲染错误）。
- 脚本在添加 `--artifact` 时发出 Artifact 友好的变体：`python3 /abs/path/expo-skill-eval/scripts/generate_viewer.py /private/tmp/expo-skill-eval-<skill> --artifact` 写入 `viewer_artifact.html`（内容相同，骨架被剥离，没有浏览器打开）。将此文件传递给 `Artifact` 工具（`favicon: "📊"`），而不是独立的文件。

查看器已经自包含（base64 截图，内联 CSS/JS），所以它满足 Artifact CSP（没有外部主机）。

## 参考

- `references/runtime-matrix.md` — 每个技能的运行时适用性（expo-go 与 static-only，平台说明）。
- `agents/visual-grader.md` — 评分器子代理的屏幕截图评分说明。
