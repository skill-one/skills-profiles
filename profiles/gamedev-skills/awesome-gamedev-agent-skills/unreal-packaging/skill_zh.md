# Unreal 打包与烹饪

将 UE5 项目转换为可运行、可分发的构建版本：选择正确的构建配置、烹饪内容、设置启动地图，然后打包——从编辑器或命令行进行。目标 **UE 5.8**。

## 何时使用

- 在生成构建（测试或发布）、选择开发与发布版本、烹饪内容、配置打包/地图与模式设置，或使用 `RunUAT BuildCookRun` 通过 CI 自动化构建时使用。
- 当项目具有 `*.uproject` 和 `Config/Default*.ini`，且目标是打包的玩家程序而非在编辑器中运行时使用。

**不使用时**：商店提交/发布流程 → `steam-publish` / `itch-publish`。编辑时游戏/迭代不是打包。

## 核心工作流程

1. **设置启动地图**。项目设置 → **地图与模式** → **游戏默认地图** 是打包构建首先加载的地图。这里设置错误/为空是最常见的“打包游戏是黑色”的原因。
2. **选择构建配置**：**开发**（默认；优化但保留日志/统计/控制台用于测试）与 **发布**（所有优化，移除调试工具——用于发布）。`DebugGame`/`Debug` 用于调试引擎/游戏代码，不适合分发；`DebugGame` 不适用于仅使用蓝图的项目。
3. **理解烹饪与打包的区别**。**烹饪** 将资源转换为目标平台的格式，并打包到 `.pak` 文件中。**打包** 将编译的可执行文件 + 烹饪内容捆绑成一个独立的可分发文件集。打包会运行一个烹饪作为其一部分。
4. **从编辑器打包**：**平台** 菜单 → 选择平台（例如 Windows）→ 设置二进制配置 → **打包项目** → 选择输出文件夹。
5. **或使用 Unreal 自动化工具（`RunUAT BuildCookRun`）从命令行构建**，用于可重复/CI 构建。
6. **调整打包设置**（项目设置 → **打包**）：烹饪哪些地图/目录、完全重建、压缩，以及是否构建所有地图。
7. **通过运行打包构建来验证**，而不仅仅是成功烹饪——启动可执行文件并确认它加载了正确的地图并运行。

## 模式

### 1. 编辑器打包（菜单路径）

```text
Platforms (工具栏)
  -> Windows
     -> 二进制配置 -> 开发 | 发布
     -> 内容管理 -> 打包项目
  -> 选择/确认暂存输出文件夹
```

### 2. 使用 UAT 的命令行构建（适合 CI）

```bash
# 烹饪 + 构建 + 暂存 + pak + 归档一个发布 Windows 构建。
RunUAT BuildCookRun \
  -project="C:/Path/MyGame.uproject" \
  -noP4 -platform=Win64 -clientconfig=Shipping \
  -cook -allmaps -build -stage -pak -archive \
  -archivedirectory="C:/Builds/MyGame"
```

`RunUAT` 位于 `Engine/Build/BatchFiles/`（Windows 上的 `RunUAT.bat`，macOS/Linux 上的 `RunUAT.sh`）。移除 `-allmaps` 并传递 `-map=Map1+Map2` 以烹饪子集。

### 3. 仅烹饪（不打包），例如刷新内容

```bash
RunUAT BuildCookRun -project="C:/Path/MyGame.uproject" -noP4 \
  -platform=Win64 -clientconfig=Development -cook -skipstage
```

## 陷阱

- **打包构建加载黑色/空地图** — 游戏默认地图未设置（或该地图未烹饪）。在地图与模式中设置它，并确保它包含在烹饪中。
- **发布开发构建** — 开发保留日志/控制台/统计，且较慢；发布 **发布**。反之，发布移除 `UE_LOG`/控制台，因此调试仅发布问题需要开发或 `Test`。
- **运行时引用的地图/资源缺失** — 它未烹饪。将其添加到打包设置的地图/目录中烹饪，或烹饪所有地图。
- **构建在平台上失败** — 平台 SDK/工具链未安装（Windows 构建工具、Android SDK/NDK、控制台 SDK）。安装平台的先决条件。
- **期望蓝图原生化** — 它在 UE5 中**已移除**；不要依赖它来提升性能。分析并将热点逻辑移至 C++（`unreal-cpp-gameplay`）。
- **首次烹饪非常慢** — 着色器和所有资源从头开始烹饪；后续烹饪是增量。不要将慢的首次烹饪误认为是卡死。

## 参考

- 主要文档："打包你的项目"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project`) 和构建配置 / `BuildCookRun` 参考。

## 相关技能

- `steam-publish` / `itch-publish` — 将打包构建分发到商店。
- `unreal-cpp-gameplay` — 蓝图原生化已移除，现在将热点逻辑移至 C++。
