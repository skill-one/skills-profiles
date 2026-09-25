# Unity 构建流程

配置、脚本和自动化 Unity 6.3 LTS 玩家构建：场景、平台目标、脚本后端、剥离以及无头/CI 构建。目标 **Unity 6.3 LTS (6000.3)**。

## 使用场景

- 在设置构建设置/配置文件、选择平台和脚本后端（Mono vs IL2CPP）、使用管理剥离减小构建体积、使用 `BuildPipeline.BuildPlayer` 脚本可重复的构建，或配置 CI/无头构建时使用。
- 当项目包含 `ProjectSettings/EditorBuildSettings.asset` 或 CI 构建脚本时使用。

**不使用场景：** 端到端编写 CI 服务配置是 DevOps；此技能涵盖 Unity 端的构建 API 和设置。控制台/平台认证细节属于平台 NDA 范围。商店提交 → `steam-publish` / `itch-publish`。

## 核心工作流

1. **列出要构建的场景** (文件 → 构建配置文件/设置 → 场景列表，或 `EditorBuildSettings.scenes`)。仅列出、启用的场景会发布；场景 0 是启动场景。
2. **选择平台目标**，如有需要切换活动构建目标 (`BuildTarget` / `EditorUserBuildSettings`)。
3. **选择脚本后端** (玩家设置)：**Mono** (快速迭代，桌面) vs **IL2CPP** (AOT C++; 许多平台所需，性能更好，更难逆向)。IL2CPP 需要安装平台的 C++ 工具链。
4. **调整大小/性能：** 设置管理剥离级别 (禁用 → 最小 → 低 → 中等 → 高) 并用 `link.xml` 保护仅反射代码。按平台设置质量设置。
5. **使用 `BuildPipeline.BuildPlayer(BuildPlayerOptions)` 脚本构建并** **检查返回的 `BuildReport`** — 非成功 (`Succeeded`) 结果必须使您的流程失败。
6. **为 CI 运行无头模式** (`-batchmode -quit -executeMethod`)，并检查退出代码。
7. **验证** 实际输出可运行 (启动玩家)，而不仅仅是构建返回且未抛出异常。

## 模式

### 1. 带结果检查的脚本化构建

```csharp
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class BuildScript
{
    [MenuItem("Build/Windows x64")]
    public static void BuildWindows()
    {
        var options = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/Main.unity", "Assets/Scenes/Level1.unity" },
            locationPathName = "Builds/Windows/Game.exe",
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None,            // 添加 BuildOptions.Development 进行开发构建
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary summary = report.summary;

        if (summary.result != BuildResult.Succeeded)
            throw new System.Exception($"构建失败：{summary.totalErrors} 个错误");
        Debug.Log($"构建成功：{summary.totalSize} 字节，耗时 {summary.totalTime}");
    }
}
```

### 2. 无头/CI 调用

```bash
# 成功时退出码为 0；-quit 确保编辑器关闭；-nographics 用于构建服务器。
Unity -batchmode -quit -nographics \
  -projectPath "/path/to/Project" \
  -executeMethod BuildScript.BuildWindows \
  -logFile -
```

### 3. 用 `link.xml` 保护剥离代码

```xml
<!-- Assets/link.xml — 保留链接器无法看到的类型 (反射、JSON、插件)。 -->
<linker>
  <assembly fullname="MyGameRuntime" preserve="all"/>
</linker>
```

## 陷阱

- **编辑器中加载场景但在构建中缺失** — 它不在构建设置场景列表中 (或被禁用)。`SceneManager.LoadScene` 只看到列表中的场景。
- **IL2CPP 构建在全新机器上失败** — 平台 C++ 工具链 (例如 Windows 构建工具、Android NDK) 未安装。Mono 没有此要求。
- **`MissingMethodException`/`TypeLoadException` 仅在构建中发生** — 管理剥离移除了仅反射代码。降低剥离级别或添加 `link.xml` 保留条目。
- **将 "BuildPlayer 返回" 视为成功** — 始终检查 `BuildReport.summary.result`；它可能带错误返回。
- **Addressables 内容陈旧/缺失** — Addressables (`com.unity.addressables`) 需要一个 *单独* 的内容构建 (构建 → Addressables) 和指向正确加载路径的配置文件；仅玩家构建不会重新构建它们。
- **发布开发构建** — `BuildOptions.Development` 启用分析器/调试并更慢；使用 `BuildOptions.None` 进行发布。

## 参考

- 对于完整的 **多平台 CI 构建脚本** (目标切换、版本戳、参数解析、退出代码) 和 Addressables 内容构建调用，请阅读 `references/ci-build-script.md`。
- 主要文档：`ScriptReference/BuildPipeline.BuildPlayer`，Unity 手册构建部分 (玩家设置、管理代码剥离)。

## 相关技能

- `steam-publish` / `itch-publish` — 发布您刚刚构建的玩家。
- `unity-csharp-scripting` — 构建脚本使用的编辑器脚本约定。
