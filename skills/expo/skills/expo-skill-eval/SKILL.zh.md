---
name: expo-skill-eval
description: 评估此存储库中 Expo 的端到端技能 - 通过 Expo Go（可选：Web）触发准确性、生成代码质量，以及在 iOS 模拟器和 Android 模拟器上的运行时截图。当用户希望评估 Expo 技能、测试技能能否生成可用代码、使用设备截图对技能进行基准测试，或验证技能输出是否正确渲染时使用。
---

# Expo 技能评估

评估 `plugins/expo/skills/` 中的技能在 Expo Go 中的触发准确性、生成代码质量以及/或运行时渲染。

要求：macOS 配备 Xcode（iOS 模拟器）、Android SDK（至少有一个 AVD）以及 `bun`。假设没有其他设备工具。

工作区根目录：`/private/tmp/expo-skill-eval-<skill-name>/iteration-N/`（例如 `/private/tmp/expo-skill-eval-expo-ui/iteration-4/`）。

## 开始前 — 明确范围

**在开始任何管道工作之前，确认以下所有内容——不要跳过任何**（只有当请求已经说明选择时才能跳过给定的项目）。将它们分批到 `AskUserQuestion` 调用中，每个调用最多 4 个问题，按以下顺序：

1. **评估哪个技能**（如果请求中不明显）。
2. **提示**——哪些提示驱动评估。内置提示（来自技能的评估用例）**全部预先选择**；删除任何提示，添加自定义文本提示，或**从上传的屏幕截图构建**（技能必须复制的目标 UI）。见 **提示** 部分。
3. **验证什么**——三个选项的多选：运行时 + 截图 / 触发准确性 / 代码检查（无设备）。见 *验证什么* 部分。
4. **Expo SDK**——最新版（默认，自动检测）或固定版本。
5. **运行器**——Expo Go（默认）或开发构建。
6. **平台**——iOS / Android / Web（始终提供所有三个）。
7. `claude -p` 的 **权限标志**——跳过权限（默认）或接受编辑。
8. **查看器交付**——仅本地（默认）或发布可共享的 Artifact。
9. **如果选择触发准确性**——确认发布的 `expo` 插件已禁用（或未安装）。

以下将详细说明每一项。第 4-6 项（SDK、运行器、平台）自然地适合在一个 `AskUserQuestion` 调用中。

**如果请求中不明确要评估的技能**，请列出 `plugins/expo/skills/` 中的可用技能，并询问要评估哪一个。

**测试技能的加载方式——两个机制，每个阶段一个**（不要全局选择一个）：executor 通过 **文件路径**（`SKILL_PATH = plugins/expo/skills/<skill>/SKILL.md`，显式读取）运行参考，而触发评估将其作为 **插件** 加载（`--plugin-dir plugins/expo`，以便模型可以从其描述中自动选择它）。两者都指向 *本地、存储库* 版本——这就是你要评估的。你**不需要**任何特殊标志来 *启动* harness 会话本身（harness 通过存储库路径找到技能）；这些机制适用于它生成的 `claude -p` 子进程。见步骤 1 和 3，了解每个阶段为何不同。**一个预运行检查（当触发评估在范围内时需要）：** 如果已发布的 `expo` 插件已安装/启用，请在启动 harness 之前禁用它（通过 `/plugin`），并在之后重新启用。单个禁用是全局配置更改，此会话和生成的 `claude -p` 子进程都将继承。为什么触发评估需要它：该阶段通过 `--plugin-dir` 加载本地技能，而第二个已安装的 `expo` 会与之冲突——模型可能会触发 *已发布的* `expo:expo-ui`，并且由于检测只看到工具调用名称，你可能会静默地评分已发布的描述而不是你的本地修改（冲突也可能导致错误）。**executor / 运行时 / 静态** 阶段**不受影响**——它们通过本地 `SKILL_PATH` 读取要测试的技能，没有 `--plugin-dir`——因此没有触发评估的运行可以跳过禁用。禁用 `expo` **不会**禁用 `expo-skill-eval`（一个独立的存储库技能，不是 `expo` 插件的一部分），因此 harness 仍然可用。

**将此显式地呈现给用户作为 upfront 确认**——与确认要评估哪个技能的方式相同。当触发评估在范围内时，请用户在开始步骤 1 之前确认已发布的 `expo` 插件已禁用（或未安装）；如果它仍然启用，请暂停并让他们通过 `/plugin` 禁用它。在用户确认之前**不要**运行触发评估——harness 无法可靠地检测已安装的插件（读取全局插件配置或 `claude plugin list` 会提示），所以这是一个手动确认，而不是自动检查。

**选择提示——内置、自定义或目标屏幕截图**。提示是驱动 executor（带技能和不带技能）的*输入*；它们与你要*验证*的内容分开。使用 `AskUserQuestion` 确认它们（如果请求中已经指定了提示，则跳过）：

- **内置提示**——通过阅读要测试的技能（其 `SKILL.md` + `references/`）和 `references/runtime-matrix.md` 生成的代表性提示，涵盖技能的标准用例。 （如果技能已经在 `evals/evals.json` 下提供评估用例，请将它们的 `prompt` 字段也合并进来——但大多数技能没有，所以通常需要推导它们。）**预先选择所有**，以便默认运行测试技能的标准用例；允许用户取消选择任何。
- **自定义文本提示**——用户输入的一次性提示。不要为这个分配一个专门的选项槽：`AskUserQuestion` 自动添加一个 **"输入一些内容"** / 其他条目，并且在那里输入的任何内容都成为自定义文本用例。
- **从上传的屏幕截图构建**——用户提供目标屏幕截图（要复制的 UI）的路径。executor 被告知打开它——`claude -p` 使用其 Read 工具读取 PNG——并构建一个匹配的应用；用例记录路径为 `reference_image`，评分比较生成应用与该目标的相似度（步骤 6）。这是 UI 技能最强的视觉测试："构建这个"。

**尊重 `AskUserQuestion` 的每个问题最多 4 个选项的限制，按此优先级**（要避免的 bug：一旦四个槽位填满，上传选项会静默丢失）：

1. **始终为 "从上传的屏幕截图构建" 保留一个槽位**。这是视觉评估的全部要点，并且绝不能是丢失的选项。
2. **不要添加一个明确的 "自定义文本提示" 选项**——自动的 "输入一些内容" / 其他条目已经涵盖了它。
3. 用剩余的 ≤3 个槽位填充内置/代表性提示，**预先选择**。如果有超过 3 个，将它们合并为一个预先选择的 **"所有内置提示（默认）"** 选项，并在简短的后续操作中提供子集选择，以便上传选项仍然适用。

将其作为**多选**呈现。当选择 "从上传的屏幕截图构建" 时，在后续操作中请求目标图像路径。每个选定的提示（内置、输入或图像）都成为一项评估用例（带技能和不带技能运行）。

**除非请求使其明确，否则始终确认要验证的内容**。提供这些选项并让用户选择一个或多个（基于技能的 `references/runtime-matrix.md` 条目的默认值）：

| 选项 | 它做什么 | 建议作为默认值的时间 |
|------|----------|---------------------|
| **运行时 + 截图** | 完整管道：fixture → executor → 静态门控 → 在 iOS/Android 上运行应用并截图。运行器（Expo Go 或开发构建）是另一个问题——不要在这里命名。 | **默认** 对于任何渲染应用屏幕的技能（`references/runtime-matrix.md` 中的 `expo-go`/`dev-build` 行）。需要一个启动的模拟器/模拟器。 |
| **触发准确性** | 通过 `claude -p` 运行现实提示，检查技能是否被读取。衡量召回率（仅应触发查询）。 | 总是有用作为单独检查。 |
| **代码检查（无设备）** | `tsc --noEmit` + 差异感知的 lint + `expo export`，加上评分器检查生成代码是否符合你提供的任何自定义预期。无设备。 | **默认** 对于 `static-only` 和 `n/a` 技能，以及当你想要验证代码模式（正确的导入路径、一个 `Host` 包装器、…）而不运行应用时。 |
**将它们作为 ONE 多选问题呈现——*"你想验证什么？*** 这些是*评分维度*（如何判断构建的内容）——与 **提示** 阶段（要构建什么）不同。用户可以选择任何组合。当提示是一个**上传的屏幕截图**（见 **提示**）时，包括 **"运行时 + 截图"**，以便 harness 捕获生成应用，并且评分器可以将其与目标评分（步骤 6）。

读取 `references/runtime-matrix.md` 以找到技能的默认模式，然后再建议。如果请求已经指定了模式（例如 "只检查是否触发"、"在设备上运行它"），则跳过问题并继续。

**选择 Expo SDK 版本——一次， upfront**。使用 `bash /abs/path/expo-skill-eval/scripts/latest-sdk.sh` 检测最新版本（它打印主版本号，例如 `56`；内部它使用 `bun` 运行 `npm view expo dist-tags --json` 并通过 `JSON.parse`/`semver` 读取主版本号，并且它受 bash-scripts 规则覆盖——所以不要自己 inline 运行存储库查询，这会提示）。然后使用 `AskUserQuestion` 确认：默认为最新 SDK，或允许用户固定一个较旧的版本（例如，以重现版本特定的问题）。在构建 fixture 时使用所选版本——将 `<sdk>` 参数作为 `make-fixture.sh` 传递，并将它写入每个评估用例的 `runtime.sdk`。如果请求已经指定了版本（"在 SDK 54 上评估"），则跳过检测并使用它。

**默认为最新版**——它保持与 `expo start` 在设备上安装的 Expo Go 兼容。固定比设备安装的 Expo Go *旧* 的 SDK 会使 `expo start` 尝试提示 "安装推荐的 Expo Go 版本"；在没有 TTY（快照脚本从 `/dev/null` 读取 stdin）的情况下，它会因 `Input is required, but 'npx expo' is in non-interactive mode` 而失败，并且 **每个快照都会失败**。因此，只有在您也预先在模拟器/模拟器上安装了匹配的 Expo Go 时，才固定一个较旧的 SDK——否则坚持使用最新版。

**选择运行器——Expo Go（默认）或开发构建**。使用 `AskUserQuestion` 询问（如果请求已经说明，则跳过）：

- **Expo Go（默认）**——快照脚本使用 `expo start --<platform>`/`expo start --android` 原样运行应用。快速（无需原生编译），并且它运行 Expo Go 打包的任何内容（包括 `@expo/ui` 在 SDK 56+ 上）。无法运行自定义原生代码（expo-modules、配置插件、不在 Expo Go 中的原生依赖）。
- **开发构建**——快照脚本运行 `expo run:ios`/`expo run:android` 而不是，为每个 fixture 编译一个原生开发客户端。用于输出需要自定义原生代码的技能（否则这些用例将是 `static-only`）。慢得多——`expo run` 预构建并原生编译每个 fixture（几分钟，尤其是第一个），并且需要完整的 iOS/Android 构建工具链——因此只有在技能实际上需要原生代码时才选择它。**磁盘密集型**：每个 fixture 的原生构建是多个 GB。快照阶段在每个 fixture 后运行 `clean-fixture.sh` 以将峰值使用量保持在 ~一个构建，但仍然更喜欢较少的评估用例和**单个平台**用于开发构建运行，并保留一些 GB 的空闲空间。`clean-fixture.sh` 删除每个 fixture 的构建*输出*（`node_modules`、`ios`、`android`、`.expo`、`dist` 以及 fixture 的 iOS DerivedData），并保留应用源代码 + git。开发构建磁盘的杠杆是**较少的评估用例 + 一个平台**——它只回收每个 fixture 的构建输出，并且永远不会触及共享依赖缓存，所以没有任何东西会被重新下载。

通过 `EXPO_SKILL_EVAL_RUNNER` 环境变量将选择传递给快照脚本（默认为 `expo-go`，或 `dev-build`），并在每个评估用例的 `runtime.mode`（`expo-go` 或 `dev-build`）中反映它。见步骤 5。

**选择平台——无论技能如何，始终询问**。使用 `AskUserQuestion` 提供 iOS / Android / Web（多选）；默认为 iOS + Android，但始终提供 Web 作为选项——不要根据技能预过滤。 **Web 对于大多数技能都是有效选择**：`@expo/ui` 的*通用*组件（`Host`、`Row`、`Column`、`Button`、`List`、…）在 Web 上渲染，`expo-dom`、NativeWind/Tailwind、API 路由和纯 React Native 也一样。唯一不会在 Web 上显示的是*平台特定*的原生树（`@expo/ui/swift-ui` 或 `@expo/ui/jetpack-compose`），它在 Web 上渲染为空白——而空白本身也是一个有用的信号，所以用户仍然可以决定。Web 通过 `snapshot-web.sh`（`expo start --web` + Playwright/Chromium）运行**无论运行器如何**（`expo run` 仅限原生；没有 Web 开发构建），并且它是最少执行的路径。将选择集写入每个评估用例的 `runtime.platforms`，并让 `run_snapshots.py` 循环它们。

**确认 `claude -p` 子进程如何运行——一次，在开始之前**。使用 `AskUserQuestion` 询问他们是否可以运行 `--dangerously-skip-permissions`，然后将相同的答案应用于此运行中的每个子进程（运行期间永不重新提示）：

- **跳过权限（推荐）**——传递 `--dangerously-skip-permissions`。每个子进程在 `/private/tmp/expo-skill-eval-*` 下以无提示方式运行在一个一次性 fixture 中，并且可以写入文件和运行设置命令而无需提示。
- **仅接受编辑**——改为传递 `--permission-mode acceptEdits`。Bash/installs 自动拒绝（没有 TTY），因此某些评估可能产生部分输出。

一个没有标志的裸 `claude -p` 完全无法写入文件。如果请求已经说明偏好（"跳过权限"、"不要使用危险标志"），则跳过问题。

**确认如何交付结果查看器——一次， upfront**。发布到 claude.ai 是面向外部的，因此永远不会在运行期间意外地执行；在 upfront `AskUserQuestion` 中询问（与权限标志一起）：

- **仅本地（默认）**——`generate_viewer.py` 写入 `viewer.html` 并在本地浏览器中打开它。没有任何东西离开机器。
- **发布一个可共享的 Artifact**——此外，在最后将查看器渲染到 claude.ai Artifact（一个默认为私有的网页，用户可以与队友分享）中。只有在用户在此处选择加入时才这样做。

如果请求已经说明是否要共享/发布，则跳过问题。见 **查看器** 部分发布机制。

## 评估用例模式

你生成运行评估用例——每个选定的提示一个——并将它们写入 `<workspace>/iteration-N/evals.json`（查看器从那里读取它们）。每个用例扩展了标准技能创建器评估用例形状，增加了 `runtime` 块和视觉预期：

```json
{
  "id": 1,
  "prompt": "为我构建一个带有暗黑模式切换和选项列表的设置屏幕",
  "expected_output": "工作中的 Expo Router 屏幕",
  "expectations": [
    "使用 Expo Router 基于文件的路由",
    "TypeScript 编译无错误"
  ],
  "runtime": {
    "mode": "expo-go",
    "platforms": ["ios", "android"],
    "sdk": "56"
  },
  "visual_expectations": [
    "在任何平台上都没有红色错误屏幕或 Expo Go 错误覆盖层",
    "渲染了一个带有可见切换控制的设置屏幕"
  ]
}
```

- `runtime.mode`：评估在静态门控后如何运行——
  - `"expo-go"`：在 Expo Go（`expo start --<platform>`）中运行并截图。快速，仅 JS。**默认。**
  - `"dev-build"`：构建一个原生开发客户端（`expo run:<platform>`）并截图。用于输出使用自定义原生代码的技能；慢得多（每个 fixture 原生编译）。
  - `"static-only"`：在静态门控后停止——用于不产生 UI 的技能，或者当你完全不想在设备上运行时（CI）。

  参考 `references/runtime-matrix.md` 了解哪些存储库技能支持哪种模式。（`dev-build` 允许你实际运行之前必须为需要原生代码而 `static-only` 的技能。）
- `runtime.platforms`：`ios`、`android`、`web` 的子集—— upfront 选择（始终提供，不依赖于技能；见 **开始前**）。默认为 `["ios", "android"]`。
- `runtime.sdk`：fixture 应用的 Expo SDK 主版本——设置为 upfront 选择（见 **开始前 — 明确范围**）。省略以使用最新模板。
- `reference_image`（可选——**图像提示**）：要复制的**目标屏幕截图**的绝对路径。设置后，executor 被告知打开它（通过其 Read 工具）并构建一个匹配的应用，并且评分器根据目标（步骤 6）对生成应用进行评分。在 **提示** 阶段通过 "从上传的屏幕截图构建" 设置。

图像提示用例是一个设置了 `reference_image` 的普通用例；启用“运行时 + 截图”以便 harness 捕获结果以与目标进行比较：

```json
{
  "prompt": "构建一个 UI 与附加参考截图匹配的应用程序。",
  "reference_image": "/abs/path/to/target.png",
  "runtime": { "mode": "expo-go", "platforms": ["ios"], "sdk": "56" },
  "visual_expectations": ["与参考布局、组件和颜色处理匹配"]
}
```

## 每个评估用例的管道

**编排模型 — 在主线程上运行 `python3 <编排器>` 以及几乎其他任何操作。** 每个阶段都由一个小的 Python 编排器驱动，您将其写入工作区并使用 `python3 /private/tmp/expo-skill-eval-<技能>/<阶段>.py`（由 `python3` 规则覆盖）运行（编排器是**唯一**调用 `scripts/*.sh` 文件的地方——总是通过 `subprocess.run(["bash", "<scripts>/<名称>.sh", …])`，它作为 `python3` 的子进程运行，无需自己的规则——并且是并行性、日志记录和目录创建的唯一地方。因此，在主线程上，您永远只：**写入**编排器、**运行**它们使用 `python3`、**检查**输出使用 `Read`/`Glob`/`Grep` 工具，以及**启动**评分子代理。永远不要在链接/后台/管道的 shell 构造中放入命令，并且永远不要运行 ad-hoc `mkdir`/`ls`/`cat`/`tail`/`echo`——那是提示。 (单个独立的 `bash …/scripts/<名称>.sh …` 用于一次性手动调试，例如重新运行一个不可靠的快照，但管道本身通过编排器进行。) **在前景中运行每个编排器**——让工具调用阻塞直到完成；编排器已经在阶段内部并行化，因此您不需要重叠阶段。**不要**使用 `… & echo "$!"` / `wait` 在阶段中 shell 后台（`&`、`echo` 和 `wait` 段没有规则并提示）。如果您确实必须在继续其他工作时运行阶段，请使用 Bash 工具的 `run_in_background` 参数在纯 `python3 <编排器> 2>&1 | tee <ws>/…log` 调用上——永远不要手写的 shell `&`。 **在开始时预期**恰好一个权限提示：第一次写入工作区。`allowed-tools` 可以抑制 `Bash`/`Read` 但不能 `Write`/`Edit`，因此请在第一个提示上选择**“允许此目录会话中的所有编辑”**——它涵盖了每个编排器、`evals.json` 和整个运行中的查看器文件。

### 0. 工作区设置

使用工作区脚本一次性创建运行目录树——**永远不要使用 ad-hoc `mkdir`**（原始 `mkdir` 提示：没有 `mkdir` 规则，并且 `"$WORKSPACE/…"` 变量无法匹配路径通配符）： 

```bash
bash /abs/path/expo-skill-eval/scripts/make-workspace.sh /private/tmp/expo-skill-eval-<技能> iteration-N <num-evals>
```

这为每个评估创建了 `trigger-evals/scratch` 和 `iteration-N/eval-<i>/{with_skill,without_skill}/outputs`。它由 `Bash(bash *expo-skill-eval/scripts/*)` 覆盖，并且脚本内的 `mkdir` 作为脚本的子进程运行（没有自己的规则）。之后，其他目录由需要它们的脚本/编排器创建（`make-fixture.sh`、执行器编排器的 `os.makedirs`、快照脚本）或由 `Write` 工具自动创建父目录——因此您永远不需要另一个 `mkdir`。

### 1. 触发评估（仅应触发）

在工作区的 `trigger-evals/` 目录下编写 `run_trigger_eval_real.py` 脚本。使用**仅 `"should_trigger": true` 查询**——expo 插件是一系列互补的技能，因此多个技能在同一提示上触发不是失败。仅测量召回率：现实中的提示应使用该技能，由触发率评分。

脚本应针对每个查询运行 `claude -p <查询>`（使用 `--output-format=stream-json --verbose --include-partial-messages`、`CLAUDECODE` 从环境中剥离，并在**开始之前——明确范围**中确认权限标志），并通过在流中查找其 `Skill` 或 `Read` 工具调用来检测目标技能是否被触发。注意：`--include-partial-messages` 需要 `--output-format=stream-json` 和 `--verbose`——省略任何一项都会导致立即的 CLI 错误。

**加载要测试的技能——将 `--plugin-dir` 传递给每个触发子进程。** 触发评估测量的是技能的*描述*使模型去使用它，因此子进程必须加载**本地**技能（带有您的编辑的版本）。`claude -p` 子进程**不会**继承父会话的 `--plugin-dir`，因此请显式添加：`--plugin-dir <plugin-root>`，其中 `<plugin-root>` 是拥有技能的插件目录的**绝对**路径——包含 `.claude-plugin/plugin.json` 的 `plugins/expo` 祖先（例如 `--plugin-dir /Users/.../skills/plugins/expo`）。它必须是绝对的：子进程从可丢弃的 `scratch/` cwd 运行，因此相对的 `plugins/expo` 无法解析——并且缺少插件目录会静默加载任何内容，这伪装成 0% 的触发率。然后等待技能在其插件限定名称下触发（`<plugin>:<skill>`，例如 `expo:expo-ui`）。有两个注意事项：(1) 如果**发布的** `expo` 插件也全局安装，请禁用它（通过 `/plugin`）进行运行并在之后重新启用——否则两个 `expo` 副本在子进程中冲突，模型可能会触发*发布的* `expo:expo-ui`，静默地评分其描述而不是您的本地编辑（触发检测仅看到工具调用名称，因此无法区分副本；开发检出通常没有安装它）。 (2) 永远不要制作技能的合成副本——一个真实的加载副本总是获胜，因此合成 harness 评分 0%。执行器不受已安装插件的 影响：它们直接读取本地 `SKILL_PATH` 并不传递 `--plugin-dir`。

从空的可丢弃 cwd 运行每个查询的子进程（例如 `trigger-evals/scratch/`），而不是存储库根目录。像 "为我构建一个设置屏幕" 这样的应触发提示可以使子进程写入文件，并且使用 `--dangerously-skip-permissions` 这些写入原本会落入技能存储库。触发检测只需要技能的 `Skill`/`Read` 调用在流中出现——它不需要固定装置——因此任何附带写入都是可丢弃的。

为每个查询子进程设置至少 **300 秒** 的超时。180 秒的限制太短——某些查询会导致模型在触发技能之前开始生成代码，这将使总运行时间超过 3 分钟。

每个技能运行一次触发评估，而不是每个代码评估用例。

### 2. 固定装置

每个执行器运行都会获得一个新鲜的 Expo 应用程序，由 `scripts/make-fixture.sh <app-path> <sdk> [clean|full]` 创建：

```bash
scripts/make-fixture.sh <workspace>/iteration-N/eval-X/<config>/app <sdk>          # 空白应用程序（默认）
scripts/make-fixture.sh <workspace>/iteration-N/eval-X/<config>/app <sdk> full     # 保留示例标签
```

该脚本使用 `bunx create-expo-app -t default@sdk-<版本>`（如果没有给出版本则使用最新模板）为每个 SDK 版本 + 变体一次性创建应用程序，并将其缓存到 `~/.cache/expo-skill-eval/fixtures/` 下，并使用 APFS 写时复制克隆缓存——因此每个变体的第一次运行支付安装成本，而之后的运行几乎是即时的。默认的 `clean` 变体运行模板的 `reset-project` 脚本，因此执行器从空白应用程序开始，并且输出中的每个屏幕都是它们自己的——一个更干净的评分信号。仅在评估提示假设现有应用程序时使用 `full`（例如 "我有一个具有两个标签的应用程序..."）。该脚本还将克隆内的 git 重置，因此应用程序中的 `git diff` 显示执行器更改的确切内容（对评分者有用）。

**按顺序构建固定装置，然后发散执行器——永远不要并发创建固定装置。** `make-fixture.sh` 在 `~/.cache/expo-skill-eval/fixtures/` 下共享一个缓存，按 SDK+变体键入。如果两个运行都发现缓存为冷并同时在同一时间调用 `bunx create-expo-app`， bun 的链接步骤冲突，并且一个会以 `EEXIST` / "无法确定要运行的可执行文件 for package create-expo-app" 失败。因此，在执行器编排器（步骤 3）中，首先一次创建**所有**固定装置——一个纯 Python 循环调用 `subprocess.run(["bash", "<scripts>/make-fixture.sh", app, sdk, variant])`（其中 `sdk` 是预先选择的版本）——然后使用 `ThreadPoolExecutor` 发散 `claude -p` 执行器。顺序创建是廉价的：每个 SDK+变体的第一个固定装置支付安装成本；其余的是 ~1s APFS 克隆。(并且永远不要使用 ad-hoc shell 发散固定装置，如 `make-fixture.sh A & make-fixture.sh B & wait`——`&`/`wait` 段提示；顺序的 Python 循环避免了竞争和提示。)

### 3. 生成（执行器子代理）

作为 Python 脚本中的 `claude -p` 子进程调用运行执行器，**而不是**通过 `Agent` 工具。`Agent` 工具使用自己的权限上下文生成子代理——固定装置应用程序中的文件编辑将提示用户。`claude -p` 子进程是完全独立于权限系统之外的一个进程（与触发评估 harness 使用的模式相同）。

将 Python 脚本写入 `/private/tmp/expo-skill-eval-<技能>/run_executors.py`。**首先按顺序循环创建每个运行的固定装置**——`subprocess.run(["bash", "<scripts>/make-fixture.sh", app, sdk, variant], …)` 一次一个（并发创建与共享 bun 缓存竞争——见步骤 2）。**然后**通过 `ThreadPoolExecutor` 以并行方式运行 with-skill 和 without-skill 的 `claude -p` 调用。这两个阶段都位于 Python 内部（由 `python3` 规则覆盖），因此主线程上不会运行任何 ad-hoc shell。每个执行器提示必须包括：

- 技能路径（仅 with-skill 运行）和评估提示。
- **图像提示用例（`reference_image` 设置）：** 目标截图的绝对路径加上类似 "使用您的 Read 工具打开 `<path>` 处的参考截图，并构建一个 UI 与之尽可能匹配的应用程序——布局、组件、间距和颜色。" (`claude -p` 渲染以此方式读取的 PNG，因此执行器实际上可以看到目标。)
- 固定装置应用程序路径："在 `<app-path>` 内进行更改。项目已经存在并且安装了依赖项。对所有文件操作使用绝对路径。"
- "在写入任何文件之前，检查项目布局——运行 `ls`，读取 `package.json` 和 `app.json`——以找到正确的路由目录。最近的 SDK 默认模板将 Expo Router 路由放在 `src/app/` 中；较旧的模板在项目根目录下使用 `app/`——检查以确认此固定装置使用的是哪一个。"
- "不要启动开发服务器、启动模拟器或拍摄截图——harness 在您完成后会做这些。"
- 保存构建摘要的位置。

`claude -p` 子进程的标志：
- 从环境中剥离 `CLAUDECODE` (`env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}`)——否则 `claude -p` 在运行中的 Claude Code 会话内嵌套时静默挂起。
- 一个权限标志，在用户面前确认（见 **开始之前——明确范围**）：`--dangerously-skip-permissions` 或 `--permission-mode acceptEdits`。将选择的标志烘焙到生成的脚本中。一个没有标志的裸 `claude -p` 无法写入文件——它没有 TTY 来批准编辑，而是作为文本发出代码。
- **不要**向执行器传递 `--plugin-dir`（与触发评估不同）。with-skill 运行已经通过其绝对 `SKILL_PATH` 读取技能，因此它直接测试本地内容；并且 without-skill 运行必须**完全**没有技能可用——加载插件将允许技能自动触发并污染基线。保持执行器路径基础也干净地分离了两个问题：执行器测量*内容质量*（一旦读取，技能是否有用？），触发评估测量*触发*（描述是否让它被选中？）。

将每个运行的 stdout/stderr 捕获到固定装置旁边的日志文件中，以供评分证据。为每个执行器设置 900 秒的超时——with-skill 运行在编码之前读取多个参考文件，并且定期需要 5–10 分钟。

### 4. 静态门

编写 `run_static.py` 并使用 `python3` 运行它。对于每个评估/配置应用程序，它调用 `subprocess.run(["bash", "<scripts>/check-static.sh", app, "ios,android"], capture_output=True, …)` 在 `ThreadPoolExecutor` 内（静态门是独立的——在 Python 内部运行它们，永远不要使用 shell `&`/`wait`），并将每个结果写入 `eval-<i>/<config>/static.json`（退出代码 + 捕获的输出）供评分者使用。

`check-static.sh` 运行 `tsc --noEmit`、`expo lint` 和 `expo export` 对于列出的平台。通过在不接触设备的情况下通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过通过

每个 `snapshot-<platform>.sh` **在启动时释放其 Metro 端口**（杀死任何由崩溃的前运行遗留在其上的陈旧进程）并在退出时拆除 Metro — 因此你永远不需要自己运行 `lsof`/`kill`/`pkill` 来清除端口（那会提示，而它已经被处理了）。然后它启动 Metro，等待 Metro 日志中的“Bundled”行，稳定下来，捕获屏幕截图，并拆除 Metro。iOS 如果没有启动 iPhone 模拟器，则启动最新可用的 iPhone 模拟器；Android 如果没有连接设备，则启动第一个 AVD（慢路径 — 启动一次并在整个迭代中重用）。Android 首先**回收卡死的/`offline` 模拟器**（优雅的 `adb emu kill`，然后强制杀死 + `adb reset`），以防止半死的实例污染运行，并使用**硬件 GPU** (`-gpu host`，在 Apple Silicon 上 Metal 加速）。如果 `host` 在给定机器上自我中止模拟器（qemu 在 gfxstream/Metal 深处发出 `SIGABRT` — 在 Apple Silicon 上负载下可能），请将 `GPU_MODE` 在 `snapshot-android.sh` 中编辑为软件模式（`guest` 渲染可靠但缓慢 — 增加稳定时间；避免 `swiftshader_indirect`，它在 arm64 上启动时**卡住**）。`snapshot-web.sh` 仅在 `platforms` 包含 web 时运行。每个脚本在屏幕截图旁边写入 Metro 日志（`<name>.metro.log`）— 将其包含在评分器的输入中。如果脚本以非零状态退出，它仍然尝试最佳努力屏幕截图（错误屏幕也是证据）。**dev-build 重启**：在 Metro 启动后，脚本通过 `xcrun simctl launch`（iOS）和 `adb shell am start -n <pkg>/.MainActivity`（Android）重新启动应用程序 — 两者都避免了 URL 方案深度链接在首次启动时触发的“在 X 中打开？”系统对话框。

在迭代的所有屏幕截图捕获完成后，始终生成查看器 — 将工作区根目录传递给已检查入的脚本：

```bash
python3 /abs/path/expo-skill-eval/scripts/generate_viewer.py /private/tmp/expo-skill-eval-<skill>
```

它将 `viewer.html` 写入工作区根目录（在 `iteration-N/` 上一级），并自己在浏览器中打开它（通过 `webbrowser.open`）— 因此不需要单独的 `open` 命令（并且不需要 `Bash(open:*)` 规则）。见下文的 **查看器** 部分。

### 6. 评分

在前台启动评分器子代理。其提示必须包括：

- 评估提示、期望列表和来自评估用例的 `visual_expectations`。
- `agents/visual-grader.md` 中的说明（屏幕截图评分、红框检测）。
- 屏幕截图文件、Metro 日志和步骤-4 的 `static.json` 作为输入。
- **图像提示用例**（用例有 `reference_image`）：还包括 **目标屏幕截图**（`reference_image`），`references/design-rubric.md`，以及固定件的 `git diff`。告诉评分器将生成的屏幕截图与目标进行比较，并发出下面的 `reference_match` + `quality` 块。

评分器将 `grading.json` 与输出文件旁边写入此形状：
```json
{
  "score": 8.5,
  "max_score": 9,
  "expectations": [
    {"text": "...", "passed": true, "evidence": "..."}
  ],
  "reference_match": {
    "score": 7, "max": 10,
    "evidence": "ios.png vs target.png: 相同的两部分分组列表 + 切换；强调颜色不同（蓝色 vs 目标的绿色）；行间距比目标更紧密"
  },
  "quality": {
    "dimensions": [
      {"name": "布局和层次结构", "score": 2, "max": 3, "evidence": "ios.png: …"}
    ],
    "subtotal": 17,
    "max": 24,
    "summary": "…"
  },
  "user_notes_summary": {"needs_review": false, "notes": ""}
}
```
视觉期望进入相同的 `expectations` 数组，证据命名屏幕截图文件并描述可见内容。`reference_match` 块（生成的应用程序如何紧密地再现目标屏幕截图）和 `quality` 块（来自 `references/design-rubric.md` 的设计评分标准）仅在图像提示用例中发出 — 或者在明确请求质量评分时。对于纯文本提示运行，省略两者。

## 部署阶段

按此顺序构建和调试管道 — 每个阶段都是独立有用的：

1. **静态**：仅步骤 1–4（`runtime.mode: "static-only"` 用于所有内容）。不需要设备；对 CI 友好。
2. **iOS**：将 `snapshot-ios.sh` 添加到循环中。`simctl` 是最可脚本化的目标。
3. **Android**：添加 `snapshot-android.sh`。模拟器启动是最慢的部分 — 在整个会话中保持一个模拟器运行。
4. **Web**：为针对 web 的技能添加 `snapshot-web.sh`（使用 `bunx`；首次运行下载 Chromium）。

## 实用提示

- **临时位置**：所有评估工作区都在 `/private/tmp/expo-skill-eval-<skill-name>/iteration-N/` 下。此运行中的所有内容 — `Read`、`Write`、`Edit` 和 `Bash` — 都包含在 `allowed-tools` 前置中，因此正确加载的技能可以无提示运行。
- **权限规则形式（为什么这个技能保持无提示）**：规则语法很重要，两个工具系列的行为不同：
  - **`Bash(...)` 规则 — 路径范围到技能自己的代码（没有广泛的解释器）。** `Bash(python3 /private/tmp/expo-skill-eval-*)`（加上 `/tmp` 别名）运行你在工作区下生成的 Python 协调器；`Bash(python3 *expo-skill-eval/scripts/*)` 运行已检查入的 `scripts/generate_viewer.py`；`Bash(tee /private/tmp/expo-skill-eval-*)`（加上 `/tmp`）允许 `python3 … 2>&1 | tee <workspace>/…log` 无提示写入日志；`Bash(bash *expo-skill-eval/scripts/*)` 仅运行此技能的 `scripts/*.sh`。由于每个路径都是固定的，逃生通道保持拒绝：`python3 -c …`、`bash -c …`、`tee /etc/…`，以及在其他地方运行代码都**不匹配**（通过经验验证 — 范围规则允许 `bash <dir>/run.sh`，但阻止 `bash -c …` 和任何其他路径）。脚本内部调用的命令 — `bunx`、`xcrun simctl`、`adb`、`git`、`mkdir`、`expo` — 是脚本的子进程，不是 Bash 工具调用，因此不需要规则。**不要**从主线程运行 ad-hoc `mkdir`/`ls`/`find`/`cat`/`grep`（它们没有规则且会提示 — 并且原始的 `mkdir "$WORKSPACE/…"` 不能匹配路径通配符，因为路径是未展开的变量）：使用 `make-workspace.sh`（步骤 0）创建目录树，让协调器创建自己的目录（`os.makedirs`），并**使用 `Read`/`Glob`/`Grep` 工具**（不需要 Bash 规则）检查结果。
  - **Bash 规则匹配（测试过，不明显）**：Bash 规则是对命令字符串的 gitignore 风格通配符。`*` 匹配任何字符序列**包括 `/` 和空格**，并且可以在**模式中间**工作 — 所以 `Bash(python3 /private/tmp/expo-skill-eval-*)` 匹配 `python3 /private/tmp/expo-skill-eval-x/run.py 2>&1`，并且 `Bash(bash *expo-skill-eval/scripts/*)` 匹配 `bash /任何/绝对路径/expo-skill-eval/scripts/foo.sh args`。两个烧毁早期尝试的陷阱：`**` 匹配**字面量**（永远不要在 Bash 规则中使用它），并且 `:*` 后缀只在命令标记**之后**才有效（`Bash(python3:*)`）— **不在**部分路径之后（`Bash(python3 /path-:*)` 不匹配）。复合命令按 `|`、`&&`、`||`、`;`、`&` 分割，每个段都需要自己的匹配规则。
  - **`Read` 规则抑制提示；`Write`/`Edit` 规则**不**。这是 Claude Code 的不对称性（不是模式错误，也不是重新加载 — 在一个会话中，来自这个前置的 `Bash`/`Read` 规则显然在起作用，`Write` 仍然会提示）：文件创建/编辑始终通过 Claude Code 的编辑批准流程，无论 `allowed-tools` 如何。前置仍然将 `Read`/`Write`/`Edit` 范围到 `…/expo-skill-eval-*/**`（`/tmp` 和 `/private/tmp` 形式，因为 macOS 没有自动解析符号链接）作为文档和护栏，但那些 `Write`/`Edit` 条目不会单独抑制提示。**实际后果**：在运行开始时，你得到**一个** `Write` 提示，用于工作区 — 选择**“是，允许在此目录会话中所有编辑”**，之后在同一个工作区下的所有后续协调器 / `evals.json` / 查看器写入都将无声运行。这个单一目录批准，而不是规则，是使文件写入无提示的原因。
  - **编辑前置后重新加载 — 完全重启，不是 `/reload-skills`。** `allowed-tools` 在会话开始时加载技能时读取一次；`/reload-skills` 重新加载技能*体*，但**不**可靠地刷新权限规则。编辑此文件后，**完全退出 Claude Code 并启动新会话**，然后重新运行技能 — 否则，即使磁盘上的文件正确，陈旧的（缓存的）规则集仍然会提示。
  - **评分器子代理**具有自己的权限上下文，仍然会提示文件访问 — 这是预期的，与主线程的规则分开。
- **调用评估脚本 — 一个独立的命令，永远不要链接。** 使用绝对路径作为自己的 Bash 调用调用每个脚本：`bash /abs/path/expo-skill-eval/scripts/snapshot-ios.sh arg1 arg2`（包含在 `Bash(bash *expo-skill-eval/scripts/*)` 中）。**不要**将其与 `&`、`&&`、`||`、`;`、`wait`、`tail`、`head` 或 `echo` 结合使用 — 复合命令按段检查，那些额外的段没有规则，因此整个命令都会提示，即使 `bash …/scripts/…` 部分是允许的。（允许的唯一管道是 `… 2>&1 | tee <workspace>/…log`，因为范围的 `tee` 规则涵盖了它。）需要并行性或输出修剪？将其放入 Python 协调器（包含在 `python3 /…/expo-skill-eval-*` 中），它通过 `subprocess` 在 `ThreadPoolExecutor` 中运行脚本。使用 `Read`/`Glob`/`Grep` 工具检查结果，而不是 `cat`/`ls`/`grep`。**一般规则**：在此技能的严格范围内，任何代理即兴编写的 ad-hoc shell 都会提示 — 修复方法是将它移入脚本/协调器（或使用范围的 `tee`），而不是放宽规则。
- **检查输出（屏幕截图、日志、文件）— 使用工具，而不是 shell。** 要查找文件，使用 **Glob** 工具（例如 `/private/tmp/expo-skill-eval-<skill>/iteration-N/**/ios.png`）；要查看它们，使用 **Read** 工具 — Read 可视化渲染 PNG，这正是你需要确认屏幕截图渲染的内容。要搜索文件内容，使用 **Grep**。永远不要使用 `find`/`ls`/`cat`：它们会提示，并且 `find … -exec …` 故意*不*允许，因为它的 `-exec` 可以运行任何东西（例如 `-exec rm`）。这些工具是范围化的，无提示；每次你原本要输入 `find`/`ls`/`cat` 时，都要使用它们。
- **生成的 Python 脚本**：在工作区下编写协调/聚合脚本（例如 `/private/tmp/expo-skill-eval-<skill>/aggregate.py`），并使用 `python3` 运行它们（包含在 `Bash(python3 /private/tmp/expo-skill-eval-*)` 中）。查看器是例外 — 它是已检查入的 `scripts/generate_viewer.py`，通过 `Bash(python3 *expo-skill-eval/scripts/*)` 运行。`Write` 自动创建父目录，但第一次会提示 — 批准工作区目录一次（见上文的 `Write`/`Edit` 提示）。通过脚本自己写入日志或通过 `python3 … 2>&1 | tee <workspace>/…log`（包含在范围的 `tee` 规则中）捕获输出；使用 `Read` 工具读取日志。不要使用 `python3 -c …` 进行设置（范围的规则仅匹配工作区脚本路径，所以裸 `-c` 会提示）。

- **触发评估 vs 安装插件**：在流中检测真实安装的技能名称（例如 `expo:expo-ui`）— 当真实插件安装时，合成副本套件始终得分为 0%，因为模型会选择真实的技能而不是合成副本。
- **基准聚合**：将每个运行的 `grading.json` + `timing.json` 保存到 `eval-<N>/<config>/run-1/`。在工作区下编写 Python 聚合脚本，并使用 `python3` 运行它。
- **Expo Go 限制**：任何需要自定义原生代码（expo-module、App Clips、brownfield）的内容都不能在 Expo Go 中运行。为这些使用 `static-only` 模式 — 在编写技能的评估用例之前查看 `references/runtime-matrix.md`（注意：`@expo/ui` *在 SDK 56+ 上*在 Expo Go 中运行）。
- **API 路由技能**：而不是屏幕截图，在 Metro 启动时使用 `curl` 与路由进行验证；将响应记录为用于评分的输出文件。
- **时间数据**：在每次执行器运行后立即捕获 token 数和持续时间到 `timing.json` — 它不能恢复。要捕获 token 数，请将 `--output-format=stream-json --verbose` 添加到执行器 `claude -p` 调用中，并从日志中解析 `message_start` / `message_delta` 事件。如果没有这些标志，日志仅包含散文和经过的秒数是唯一可恢复的指标。
- **首次启动对话框**：Expo Go 偶尔在干净的模拟器上显示一次性提示。如果屏幕截图捕获对话框而不是应用程序，重新运行屏幕截图脚本（它重新打开 URL）并重新捕获。

## 查看器

在捕获屏幕截图后，始终生成并打开 HTML 查看器，以便用户可以立即查看结果而无需被询问。查看器是已检查入的 `scripts/generate_viewer.py` — 使用工作区根目录作为其参数运行它：

```bash
python3 /abs/path/expo-skill-eval/scripts/generate_viewer.py /private/tmp/expo-skill-eval-<skill>
```

它将自包含的 `/private/tmp/expo-skill-eval-<skill>/viewer.html` 写入，并自己在浏览器中打开它（通过 `webbrowser.open`）。它渲染的内容：

- 每个迭代一个标签（工作区根目录下的 `iteration-*`；记住最后活动的标签在 `localStorage` 中）。
- 对于每个评估用例（从 `<iteration>/evals.json` 读取）：并排显示 with_skill / without_skill 列，每个显示静态门状态、分数、平台屏幕截图（点击缩放；嵌入为 base64 `data:` URI，因此文件是自包含的）、期望列表带有 PASS/FAIL 徽章，以及审阅者笔记。
- 对于**图像提示用例**（带有 `grading.json` 和 `reference_match` / `quality`）：生成的屏幕截图旁边是目标屏幕截图，生成的 vs 目标的 `reference_match` 分数，每个配置的 `quality` 评分（每个维度一个条形图及其分数/最大值加上子总计），以及总结栏中的**质量差**（with_skill − without_skill 子总计）与正确性差值一起显示。
- 一个总结栏，带有 with_skill %、without_skill % 和差值。
- 当 `trigger-evals/trigger_results.json` 存在时，一个触发精度表。
- 一个深色背景，带有颜色编码的分数（绿色 ≥85%、琥珀色 ≥65%、红色低于）。

### 发布查看器（仅在事先选择加入时）

本地 `viewer.html` 始终生成。**仅在用户在事先确认中选择“发布可共享的 Artifact”** 时，在最后额外渲染它到 claude.ai Artifact — 永远不要在没有选择加入的情况下发布（它是面向外部的，并且发布的页面可能会被缓存/索引）。机制：

- `Artifact` 工具将文件包裹在其自己的 `<!doctype html>…<head></head><body>` 骨架中，因此你必须**传递给它的文件仅是页面内容** — 内联 `<style>`/`<script>`、base64 `data:` 图片，以及 `<title>`，但**没有**自己的 `<!DOCTYPE>/<html>/<head>/<body>` 标签（一个完整的独立文档会被双重包裹并渲染错误）。
- 当你添加 `--artifact` 时，脚本会发出 Artifact 友好的变体：`python3 /abs/path/expo-skill-eval/scripts/generate_viewer.py /private/tmp/expo-skill-eval-<skill> --artifact` 写入 `viewer_artifact.html`（相同内容，骨架剥离，没有打开浏览器）。将这个文件传递给 `Artifact` 工具（`favicon: "📊"`），而不是独立的文件。
- 查看器已经是自包含的（base64 屏幕截图、内联 CSS/JS），因此它满足 Artifact CSP（没有外部主机）。

## 参考

- `references/runtime-matrix.md` — 每个技能的运行时适用性（expo-go vs static-only，平台说明）。
- `agents/visual-grader.md` — 评分器子代理的屏幕截图评分说明。
