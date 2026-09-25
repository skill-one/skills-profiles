# 新 Unity 项目

一个从想法到可运行、受版本控制的 Unity 项目的引导流程。这个技能拥有**流程**——问题、它们的顺序、在您提问时后台运行缓慢的安装以及交接。它故意**不**重新记录命令；它将机制委托给其他技能。

**委托给（阅读这些以获取实际命令——不要重新发明它们）：**
- **`unity-cli`** — CLI 安装、认证/许可证、编辑器安装、项目创建、源代码控制、打开项目。它的“从零开始创建新项目”工作流是这里的骨干。
- **`unity-package-management`** — 通过 C# PackageManager Client API 安装包，并根据类型/平台/盈利方式选择包。
- **`urp-postprocessing`**、**`ui`**、**`2d-pixel-perfect`** — 视觉基线（步骤 6）：
  后处理卷设置、HUD 框架选择、像素完美 2D。
- **`implement-in-app-purchases`**、**`levelplay-unity-integration`**、**`build-live-game`** —
  盈利/后端*集成*（在步骤 8 中调用）。

**一步一步地工作。** 只提问当前步骤的问题，并等待用户再继续——平台和盈利答案会改变您要安装的内容，所以不要提前收集所有内容或在它们确定之前搭建脚手架。

## 流程——以及并行性的位置

1. **概念** — 他们正在构建的内容。
2. **平台 & 盈利** — 然后，一旦平台已知，**在后台启动编辑器安装**（它需要几分钟）并继续交谈。
3. **（加入）** 编辑器 + 平台模块完成安装。
4. **项目 + 源代码控制** — 从匹配 2D/3D 的 URP 模板创建；初始化 git。
5. **包** — 通过 C# 客户端 API 安装。
6. **视觉基线** — 后处理、相机、质量等级、UI 堆栈、管线正确的着色器，以便第一帧看起来不像是未处理的模板。
7. **保存 & 第一次提交。**
8. **交接** 盈利 / 后端。

引导流程与原始配方相比的目的：多分钟编辑器安装与用户花费在回答概念问题上的分钟数重叠，因此设置感觉是即时的。

## 步骤 1 — 概念

使用 `AskUserQuestion` 以便用户可以快速选择，但也允许他们自由回答。涵盖：

- **类型 / 核心循环** — 平台游戏、俯视射击游戏、解谜、休闲、RPG、赛车、卡牌、塔防、模拟、超休闲、第一人称等。
- **维度 & 外观** — 2D 或 3D；艺术风格（像素、低多边形、风格化、写实、仅 UI）。
- **游戏玩法** — 一句话“玩家每时每刻做什么。”
- **范围** — 单屏原型与多场景游戏；单人或多人。

还确定一个**项目名称**。写一个 2-4 行的**项目简介**，然后读回来确认。
简介驱动模板选择（步骤 4）、包（步骤 5）和视觉基线（步骤 6）：
注意用户给出的调色板/情绪词汇，以及外观是否为像素艺术。

## 步骤 2 — 平台 & 盈利，然后开始安装

两个决定，因为它们都会改变您要安装的内容：

- **目标平台**（多选）：桌面（Win/macOS/Linux）、移动（iOS/Android）、WebGL、主机。这些映射到编辑器**模块**（步骤 3）并主张在移动/WebGL 上安装更精简的包。
- **盈利**：无 / 精品 / 应用内购买 / 广告 / 混合。这仅决定您在步骤 8 中调用的哪个交接技能——现在不要集成它。

确认要使用的编辑器版本（默认：最新 LTS——参见 `unity-cli` 中的 LTS 与 Tech 与 beta 的权衡）。现在提问，在启动安装之前，这样您不会安装错误的版本。

然后确认先决条件并**将编辑器安装作为后台任务启动**，以便您继续交谈。查看 `unity-cli` 技能以获取确切语法、每个平台的模块名称以及认证 / 许可证设置：

```bash
unity --version
unity auth status --format json      # 如果已注销： unity auth login
unity license status --format json   # 如果没有活动： unity license activate

# 在后台启动，然后直接回到对话。每个平台的模块名称（android / ios / webgl / …）在
# unity-cli 技能中。
unity install lts --module <platform-modules> --yes --accept-eula
```

将此安装作为**后台任务**运行（不要阻塞它）。如果您没有其他问题要问，只需等待也可以——只有当有对话可以重叠时，并行性才有助于。

## 步骤 3 — 加入：编辑器准备就绪

在创建项目之前，确认后台安装已完成：

```bash
unity editors --installed --format json
```

如果它失败了，显示错误（参见 `unity-cli` 故障排除）并停止——没有编辑器，下游没有任何东西可以工作。

## 步骤 4 — 创建项目 + 源代码控制

遵循 `unity-cli` 的“从零开始创建新项目”工作流程：

- 列出编辑器提供的**实际**模板 ID（`unity templates list --type core`）并按**渲染管线**选择，而不仅仅是 2D/3D——不要猜测 ID。**默认为 URP：**
  `com.unity.template.urp-blank`（“通用 3D”）用于 3D，`com.unity.template.universal-2d`（“通用 2D”）用于 2D。`com.unity.template.3d` / `com.unity.template.2d` 是**内置渲染管线**模板——从 Unity 6.5 开始弃用，在 6.7 中移除——所以只有在用户明确要求内置时才选择它们。根据 JSON `renderPipeline` 字段确认选择（在当前发布中，`universal-2d` 的字段为空，所以按 ID 匹配该模板）。
- 使用 `unity projects create "<Name>" --path <dir> --editor-version <v> --template <id>` 创建。
- 设置源代码控制——**询问用户他们想要什么**，不要假设：Git（GitHub / GitLab；添加 `--git-lfs` 用于资源密集型游戏）或**Unity 版本控制**（`--vcs uvcs`，它原生处理大型二进制资源——无需 LFS），或纯本地 `git init` + Unity `.gitignore`。
  一步发布 `unity projects create --vcs … --git-token-stdin --no-initial-commit`（令牌在 stdin）。传递 **`--no-initial-commit`**，这样 CLI 不会在包和 `.meta` 文件存在之前提交裸项目——您在步骤 7 中进行真正的第一次提交/检查。查看 `unity-cli` 工作流程以获取确切标志。

## 步骤 5 — 包

将简介映射到具体的包列表，并通过 **`unity-package-management`** 技能（C# PackageManager Client API——**永远**不要手动编辑 `manifest.json`）安装。阅读该技能以获取类型/平台/盈利→包映射、安装脚本以及 `-quit` 惯例。模板已经提供了渲染管线——永远不要在内置模板项目上添加 `com.unity.render-pipelines.universal`（没有任何东西分配 URP 资产；材质会变粉）或反之。在安装之前将最终列表读回用户；之后验证 `manifest.json`。

## 步骤 6 — 视觉基线

一个干净的模板渲染正确，但看起来像默认的：没有色调映射、未处理的品质等级、平坦颜色。如果就这样留下，代理会使用 `OnGUI` 并猜测着色器名称，这就是材质变灰或品红色来自的地方。在游戏玩法工作之前应用这个基础。

**首先，`unity pipeline install --project-path "<project-path>"`，在打开编辑器之前。** 在编辑器中运行 C#，以及下面的 `unity command screenshot`，都需要项目的 `com.unity.pipeline` 包。在步骤 4 中创建的项目没有它，步骤 5 也没有添加它：该步骤通过启动编辑器二进制文件并使用 `-batchmode -executeMethod` 安装包，而从未触及包。在打开之前安装是支持顺序——安装更新 `Packages/manifest.json`，Unity 在项目加载时读取它。针对已打开的项目运行它，CLI 报告 `PIPELINE_MANIFEST_WRITE_FAILED`；询问用户关闭编辑器并重新运行。没有包，下面的一切都无法连接，这看起来像 `unity-cli` 描述的安全模式失败，但原因不同。

**然后** `unity open "<project-path>"`（也是步骤 7 需要的），等待 `unity status` 报告编辑器准备就绪，并应用下面的每一项，通过在它中运行 C#。**`unity-cli` 拥有这些命令及其语法**——不要在这里重新推导它们。

**项目 1、2、5 和 6 假设一个 URP 模板**，这是步骤 4 的默认值。如果用户明确选择了内置，不要按原文运行它们：`UniversalAdditionalCameraData`、`Light2D`、`urp-postprocessing` 卷框架和每个 `Universal Render Pipeline/*` 着色器都是 URP 类型，在内置中不存在，所以生成的 C# 不会编译。在内置上，项目 3 和 4 仍然按原文应用，后处理意味着传统的后处理堆栈，着色器名称是 `Standard` / `Unlit/Color`。不要尝试 `migrate-birp-to-urp`——用户选择了内置。

1. **后处理。** 带色调映射（ACES）的全局卷、低晕影（强度 0.5–1、阈值 0.9）和微妙的暗角（≈ 0.25）；在主相机的 `UniversalAdditionalCameraData` 上设置 `renderPostProcessing = true`。**必需子技能：** `urp-postprocessing`——它的代码模板创建卷并检查 HDR 和卷层掩码。
2. **相机和灯光。** 2D → 正交，从简介的调色板中获取实心背景颜色，如果模板场景没有，则在场景中添加一个类型为全局的 `Light2D`（如果没有，Sprite-Lit 着色器会渲染黑色）。3D → 透视；保留模板的方向光和天空盒，主光阴影开启。
3. **品质等级。** 首先读取 `QualitySettings.names`——每个模板的等级名称都不同——然后 `QualitySettings.SetQualityLevel` 到匹配主要目标的那个：桌面最高等级，移动/WebGL 最低等级。保留线性色域和模板设置的输入系统。
4. **UI 堆栈。** HUD 和菜单使用 uGUI Canvas + TextMeshPro 或 UI Toolkit——**永远不要 `OnGUI`**。**必需子技能：** `ui` 为项目选择它们之间。
5. **材质和着色器。** 在 URP 下使用 `Universal Render Pipeline/Lit`、`…/Unlit`、`…/2D/Sprite-Lit-Default` 或 `…/2D/Sprite-Unlit-Default`。`Standard` 和 `Unlit/Color` 在 URP 下渲染粉色或褪色。优先选择 `GraphicsSettings.currentRenderPipeline.defaultMaterial` / `.default2DMaterial` 覆盖 `Shader.Find`，并将 `Shader.Find` 的 `null` 视为错误。`currentRenderPipeline`，不是 `defaultRenderPipeline`：品质等级可以携带自己的管线资产，上面 3 项只是设置了等级。
6. **仅像素艺术。** 像素的精灵点过滤模式和一个像素完美相机——参见 `2d-pixel-perfect`。

保存场景，然后确认这两点。**不要用 `unity logs`**——它读取 CLI 自己的日志，永远不会读取编辑器的日志，所以它报告干净无论场景看起来如何：

- 编辑器侧没有渲染管线或着色器错误。通过 `unity-cli` 读取编辑器控制台，或直接读取 `Editor.log`——该技能的“从安全模式恢复”部分有每个平台的路径。
- `unity command screenshot --output baseline.png` 看起来有照明和色调映射，而不是平坦的灰色。

## 步骤 7 — 保存 & 第一次提交

项目已经在步骤 6 中打开，所以 `.meta` 文件存在。使用步骤 4 中设置的任何 VCS 进行第一次提交：

```bash
unity open "<project-path>"     # 如果尚未打开；对于无头/CI 使用
                                # unity-package-management 中的“无头导入并保存”
```

- **Git（GitHub / GitLab / 本地）：**
  ```bash
  cd "<project-path>"
  git add -A
  git status                    # Library/ Temp/ obj/ Build/ 必须不处于暂存状态
  git commit -m "Initial Unity project: <Name>"
  ```
  每个 `.cs`/资源必须与其 `.meta` 一起提交。
- **Unity 版本控制（UVCS）：** 通过您的 UVCS 客户端/工作区提交（在步骤 4 中创建）——没有 `git` 步骤。生成的文件夹仍然被忽略规则排除。

如果您在步骤 4 中通过 `--vcs` 发布**而没有** `--no-initial-commit`，CLI 已经对裸项目进行了初始提交——在这里添加一个后续提交，而不是双重提交。

## 步骤 8 — 交接

根据步骤 2 的盈利，调用匹配的实际集成技能：
- IAP → **implement-in-app-purchases**
- Ads → **levelplay-unity-integration**
- 账户 / 云保存 / 经济 / 远程配置 / 排行榜 → **build-live-game**

报告项目路径、编辑器版本、渲染管线和模板、安装的包、应用的视觉基线以及下一步。

## 范围——这个技能不做什么

- **没有游戏玩法脚手架。** 它带您到一个运行、连接的项目，并有一个视觉基础；构建实际游戏（场景、控制器、艺术）是下一步对话——通过 `unity-cli` MCP 服务器和包管理器在编辑器中迭代那里。通用的类型骨架往往产生可丢弃的模拟基元，所以这个技能故意在干净的起点停止。视觉基线（步骤 6）是设置，不是内容。
- **没有命令参考。** 语法存在于 `unity-cli` / `unity-package-management`。
