# Unity 包管理（无头模式，通过 C# 客户端 API）

使用 `UnityEditor.PackageManager.Client` 以编程方式添加、删除、升级和发现 UPM（Unity 包管理器）包，该客户端由终端或 CI 驱动无头运行。**不要**手动编辑 `Packages/manifest.json` — 客户端 API 可以正确解析依赖项和兼容版本，而手动编辑通常会破坏解析。

这与 **`unity-cli`** 技能（编辑器安装、项目创建、构建/测试）相辅相成：CLI 没有包管理命令，因此所有包工作都通过编辑器的 C# API 进行。

## 何时使用

- 在现有或新创建的项目中添加/删除/升级一个或多个包。
- 在 CI 中非交互式地设置项目的包。
- 在依赖某个包之前，验证其 ID 是否存在，或查找其可用版本。
- 确定游戏实际需要的哪些包 — 请参阅
  [references/select-packages.md](references/select-packages.md)。

## 选择要安装的内容

安装项目实际需要的包，而不是所有包；优先选择所选模板已经提供的包（URP 模板已经包含渲染管线、Input System 等）。游戏类型 / 外观 / 平台 / 盈利方式 → 包的映射，以及如何搜索注册表，在 [references/select-packages.md](references/select-packages.md) 中。在安装之前，生成一个**去重后的包 ID 列表**并读回用户。

## `-quit` 问题 — 为什么**不**使用 `unity run` 进行安装

`Client.Add` / `Client.AddAndRemove` 是**异步**的：它们返回一个 `Request`，该请求仅在后续的 `EditorApplication.update` 轮次上完成（UPM 子进程将其结果回传到编辑器的主循环泵，因此阻塞的 `while (!req.IsCompleted)` 会导致死锁）。编辑器必须在 `-executeMethod` 返回后**保持活动状态**，直到请求完成。

`unity run` **不能**用于安装程序：其默认路径会注入 `-quit`（请参阅 **`unity-cli`** 技能中的保留标志）。使用 `-quit`，编辑器在方法返回的瞬间就会退出 — 在 UPM 解析之前 — 因此包永远不会安装，回调也永远不会运行。

**解决方案**：直接以 `-batchmode` 启动**编辑器二进制文件**，**不**带 `-quit`。编辑器保持活动状态，`EditorApplication.update` 持续进行，轮询回调运行，并在完成时调用 `EditorApplication.Exit(code)` 自身 — 这既会退出也会设置进程退出代码。

## 安装脚本

将以下内容写入 `Assets/Editor/ProjectBootstrap/PackageInstaller.cs`。它必须位于 `Editor/` 文件夹下（或仅限编辑器的程序集）因为它使用 `UnityEditor`。

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace ProjectBootstrap
{
    // 通过 PackageManager 客户端 API 安装（并可选地删除）一组固定的包，无头安全。
    public static class PackageInstaller
    {
        // **编辑**此列表以匹配包选择（请参阅 references/select-packages.md）。
        static readonly string[] PackagesToAdd =
        {
            "com.unity.inputsystem",
            "com.unity.cinemachine",
            "com.unity.render-pipelines.universal",
            // "com.unity.package@1.2.3"  // 当需要最低版本时，使用 @ 锚定版本
        };

        // 可选地，在同一解析过程中删除包（例如，您不想的模板默认值）。
        static readonly string[] PackagesToRemove = { };

        const double TimeoutSeconds = 600; // UPM 解析 + 下载可能很慢

        static AddAndRemoveRequest _request;
        static double _deadline;

        // 调用方式：-executeMethod ProjectBootstrap.PackageInstaller.Install  (NO -quit)
        public static void Install()
        {
            if (PackagesToAdd.Length == 0 && PackagesToRemove.Length == 0)
            {
                Debug.Log("[PackageInstaller] 无需执行。");
                EditorApplication.Exit(0);
                return;
            }

            Debug.Log($"[PackageInstaller] 添加：{string.Join(", ", PackagesToAdd)}");
            _request = Client.AddAndRemove(packagesToAdd: PackagesToAdd, packagesToRemove: PackagesToRemove);
            _deadline = EditorApplication.timeSinceStartup + TimeoutSeconds;
            EditorApplication.update += Poll;
        }

        static void Poll()
        {
            if (_request == null) return;

            if (!_request.IsCompleted)
            {
                if (EditorApplication.timeSinceStartup > _deadline)
                {
                    EditorApplication.update -= Poll;
                    Debug.LogError("[PackageInstaller] 等待 UPM 超时。");
                    EditorApplication.Exit(2);
                }
                return;
            }

            EditorApplication.update -= Poll;

            if (_request.Status == StatusCode.Success)
            {
                var names = _request.Result.Select(p => $"{p.name}@{p.version}");
                Debug.Log($"[PackageInstaller] 解析：{string.Join(", ", names)}");
                EditorApplication.Exit(0);
            }
            else
            {
                Debug.LogError($"[PackageInstaller] 失败：{_request.Error?.message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
```

`AddAndRemove` 在单个 UPM 解析过程中安装整个包集 — 比每个包一个 `Client.Add` 更快且更不易出错。

**使用一个脚本进行添加/删除/升级**：
- **添加**：在 `PackagesToAdd` 中列出 ID。
- **删除**：在 `PackagesToRemove` 中列出 ID。
- **升级/锚定**：使用 `@<版本>` 添加 ID（例如 `com.unity.cinemachine@2.9.7`）。如果没有版本，解析将选择最新的兼容版本。

## 发现/验证包

在添加之前确认 ID 是否存在或列出其版本，请搜索注册表。编辑器内的 `Client.SearchAll()` / `Client.Search("<id>")` 调用也是异步的，因此它们使用**相同的轮询和 `Exit` 模式**以及**相同的无头运行**，就像安装程序一样。编写 `Assets/Editor/ProjectBootstrap/PackageSearch.cs`：

```csharp
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace ProjectBootstrap
{
    public static class PackageSearch
    {
        const double TimeoutSeconds = 120;
        static SearchRequest _request;
        static double _deadline;

        // 调用方式：-executeMethod ProjectBootstrap.PackageSearch.SearchAll  (NO -quit)
        public static void SearchAll()
        {
            _request = Client.SearchAll();                 // 或 Client.Search("com.unity.cinemachine")
            _deadline = EditorApplication.timeSinceStartup + TimeoutSeconds;
            EditorApplication.update += Poll;
        }

        static void Poll()
        {
            if (_request == null) return;
            if (!_request.IsCompleted)
            {
                if (EditorApplication.timeSinceStartup > _deadline)
                {
                    EditorApplication.update -= Poll;
                    Debug.LogError("[PackageSearch] 超时。");
                    EditorApplication.Exit(2);
                }
                return;
            }
            EditorApplication.update -= Poll;

            if (_request.Status == StatusCode.Success)
            {
                foreach (var p in _request.Result.OrderBy(p => p.name))
                    Debug.Log($"[PackageSearch] {p.name}@{p.versions.latestCompatible}  {p.displayName}");
                Debug.Log($"[PackageSearch] 找到 {_request.Result.Length} 个包。");
                EditorApplication.Exit(0);
            }
            else
            {
                Debug.LogError($"[PackageSearch] 失败：{_request.Error?.message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
```

`_request.Result` 是一个 `PackageInfo[]`；每个条目都暴露 `name`、`displayName`、`description` 和 `versions`（`.latest`、`.latestCompatible`、`.all`）。对于终端-only 检查（一个**已知的** ID，而不是自由文本搜索），直接查询注册表 — 请参阅
[references/select-packages.md](references/select-packages.md#discovering-and-verifying-packages)。

## 无头运行（直接调用编辑器，不带 `-quit`）

从版本解析编辑器二进制文件，然后以批处理模式运行它。脚本通过 `EditorApplication.Exit` 拥有退出权，因此**不要**传递 `-quit`：

```bash
VERSION="<version>"          # 例如 6000.0.47f1（或已安装的版本）
PROJECT="<project-path>"
METHOD="ProjectBootstrap.PackageInstaller.Install"   # 或 ...PackageSearch.SearchAll

# 该编辑器的安装目录（Hub 布局），通过 unity CLI
ED=$(unity editors path "$VERSION" --format json | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['path'])")

# 按操作系统解析可执行文件（处理“包含 Unity.app 的目录”和“.app”本身）
case "$(uname)" in
  Darwin) if [ -d "$ED/Unity.app" ]; then UNITY_BIN="$ED/Unity.app/Contents/MacOS/Unity";
          elif [[ "$ED" == *.app ]]; then UNITY_BIN="$ED/Contents/MacOS/Unity";
          else UNITY_BIN="$ED/Unity"; fi ;;
  Linux)  UNITY_BIN="$ED/Editor/Unity" ;;
  *)      UNITY_BIN="$ED/Editor/Unity.exe" ;;   # Windows (Git Bash / MSYS); 在 PowerShell 中使用 Editor\Unity.exe
esac

"$UNITY_BIN" -batchmode -projectPath "$PROJECT" -executeMethod "$METHOD" -logFile -
echo "退出代码：$?"   # 0 = 成功，1 = UPM 错误，2 = 超时
```

`-logFile -` 将编辑器日志（包括 `[PackageInstaller]` / `[PackageSearch]` 行）流到 stdout，以便您可以观察解析进度并读取任何 UPM 错误。如果 `unity editors path` 输出形状在您的构建中不同，则从 `unity editors --installed --format json` 获取目录。

## 验证

```bash
# 每个请求的 ID 都应作为依赖项出现
cat "<project-path>/Packages/manifest.json"
```

确认运行退出 `0`，并且列表中的每个包都存在于 `manifest.json` 中。如果包解析失败，`_request.Error.message` 将被记录；读取它并检查 ID/版本是否与注册表一致。编辑器自己的日志（包括 `[PackageInstaller]` 行）是您使用 `-logFile -` 流出的 stdout — 在那里阅读，而不是通过 `unity logs`（它显示 CLI 的日志，而不是编辑器的日志）。

## 无头导入和保存（生成 `.meta` 文件）

在脚本或工具写入新的 `.cs`/资源文件后，Unity 必须**导入**它们，以便它为每个资源生成所需的 `.meta` 文件 — 并且每个 `.cs`/资源**必须**与其 `.meta` 一起提交。仅打开项目一次 (`unity open "<project-path>"`) 就会导入并生成它们；当您需要**无头**（在脚本或 CI 中）时，使用此方法。

与包安装程序不同，这是**同步**的 — 它在返回之前完成 — 因此可以通过 `unity run` 安全运行（其注入的 `-quit` 无害；该方法也调用 `EditorApplication.Exit` 以获取干净的退出代码）。编写
`Assets/Editor/ProjectBootstrap/ProjectSaver.cs`：

```csharp
using UnityEditor;
using UnityEngine;

namespace ProjectBootstrap
{
    public static class ProjectSaver
    {
        // 调用方式：-executeMethod ProjectBootstrap.ProjectSaver.SaveAll
        public static void SaveAll()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
            AssetDatabase.SaveAssets();
            Debug.Log("[ProjectSaver] 资源导入并保存。");
            EditorApplication.Exit(0);
        }
    }
}
```

```bash
unity run "<project-path>" --editor-version <version> \
  -- -executeMethod ProjectBootstrap.ProjectSaver.SaveAll
```

## 注意事项

- 这些编辑器脚本是一个启动便利。将它们保留在
  `Assets/Editor/ProjectBootstrap/`（除非被调用否则它们什么也不做）或设置后删除它们 — 您决定；通知用户。
- 所有脚本都位于 `Editor/` 下，因为它们使用 `UnityEditor`；它们永远不会包含在构建中。
- 盈利 / 后端包（`com.unity.purchasing`、`com.unity.services.levelplay`、UPG 包）通过相同的机制安装，但实际的**集成**通过专用技能：**implement-in-app-purchases**、**levelplay-unity-integration**、**build-live-game** 进行。
