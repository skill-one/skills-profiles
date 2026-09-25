# Unity SpriteAtlas V2

为 Unity 项目中的脚本化图集提供 *编辑器安全* 的过程知识。**V2 强制编辑器创建和运行时访问之间的严格分离。**

> ⚠️ **关键 V2 原则**：`SpriteAtlas` 是 **仅运行时** 的。`SpriteAtlasAsset` 是 **仅编辑器** 的。永远不要混用上下文。始终使用 V2。

## 🚨 关键：实现前必须进行的检查和用户输入

**在生成任何代码之前，始终执行这些检查并询问这些问题：**

### 在编写代码前阅读提供的资源（必需）

此技能在 `resources/` 下提供可工作的 C# 代码，而图集代码出错几乎总是因为编写代码时没有先阅读它。打开您所选择路径的文件，然后编写。

| 选择此路径 | 首先阅读 |
|---|---|
| 任何图集工作 | [resources/authoringvsruntime.cs](resources/authoringvsruntime.cs), [references/common-errors.md](references/common-errors.md) |
| 预构建生成（默认） | [resources/spriteatlasprebuildgenerator.cs](resources/spriteatlasprebuildgenerator.cs), [resources/enablespritepacking.cs](resources/enablespritepacking.cs), [resources/savespriteatlasasset.cs](resources/savespriteatlasasset.cs) |
| 选项 B，Addressables 延迟绑定 | [resources/buildaddressablespostprocess.cs](resources/buildaddressablespostprocess.cs), [resources/spriteatlaslatebinding.cs](resources/spriteatlaslatebinding.cs), [resources/handlelatebinding.cs](resources/handlelatebinding.cs) |
| 任何可能使用旧 API 的内容 | [resources/deprecatedmethods.cs](resources/deprecatedmethods.cs), [resources/dontscriptspriteatlasineditor.cs](resources/dontscriptspriteatlasineditor.cs), [resources/dontpackinruntimebuilds.cs](resources/dontpackinruntimebuilds.cs) |

`resources/` 包含所有 38 个文件，涵盖自定义打包器、变体、平台设置和运行时访问。当您的任务不在上述表格中时，请浏览此目录，而不是发明方法。从记忆中调用 API 而不是阅读这些是导致图集导入干净但在运行时无任何作用的最常见原因。

### 0. 检查现有脚本（必需的第一步）

**在生成任何代码之前，扫描项目以查找此技能生成的现有 SpriteAtlas 脚本。**

搜索包含标识符的文件：`// [UNITY-SKILL:SPRITEATLAS]`

**如果找到现有脚本，始终使用以下格式询问用户：**

> "我在您的项目中发现了现有的 SpriteAtlas 脚本：
>
> **预构建生成器：**
> - `Assets/Editor/SpriteAtlas/SpriteAtlasPrebuildGenerator.cs`
>
> **Addressables 构建：**
> - `Assets/Editor/SpriteAtlas/BuildAddressablesPostprocess.cs`
>
> **运行时加载器：**
> - `Assets/Scripts/SpriteAtlas/SpriteAtlasLateBinding.cs`
>
> 您想做什么？"

**然后提供选项：**

- **选项 A：更新现有脚本**（如果需求变更时推荐）
  - 在现有路径上重新生成脚本
  - 保留文件位置
  - 更新到最新版本
  - ⚠️ 可能会覆盖自定义修改

- **选项 B：使用不同名称创建新脚本**
  - 与现有脚本一起生成
  - 允许多个图集配置
  - 原始脚本保持不变
  - 您需要指定新的名称/路径

- **选项 C：中止（保持现有不变）**
  - 无代码生成
  - 项目无变化
  - 如果您想保持当前设置，请使用此选项

**用户选择处理：**

- **如果选择 A**：在现有路径上重新生成，版本增加到 2.0.1+
- **如果选择 B**：询问新脚本名称（例如，"SpriteAtlasPrebuild_Custom.cs"），然后生成
- **如果选择 C**：立即停止，告知用户未进行任何更改

### 1. 交付机制（必需）

询问："您想如何交付 SpriteAtlas？"

**选项 A：内置数据（立即加载）**
- 图集包含在构建中并立即加载
- 设置 `includeInBuild = true`
- **适用于**：核心 UI、主要游戏精灵、始终需要的资源
- **优点**：简单、无需额外包、即时访问
- **缺点**：增加初始构建大小、无法在不重新构建的情况下更新

**选项 B：通过 Addressables 延迟绑定（按需加载）**
- 图集不包含在构建中，通过 Addressables 按需加载
- 设置 `includeInBuild = false`
- 为每个图集创建 Addressables 条目
- 添加 Addressables 设置作为预构建步骤
- **🚨 必需**：作为构建步骤构建 Addressables 内容
- **🚨 必需**：创建延迟绑定运行时加载器脚本
- **适用于**：DLC 内容、可选功能、大型资源、可下载内容
- **优点**：初始构建较小、可独立更新、按需加载
- **缺点**：需要 Addressables 包、异步加载、网络依赖

| 用例 | 推荐 |
|----------|-------------|
| 始终可见的核心 UI 精灵 | **选项 A：内置** |
| 指南或引导精灵 | **选项 A：内置** |
| 特定于关卡的精灵（100+ 关卡） | **选项 B：Addressables** |
| DLC 或季节性内容 | **选项 B：Addressables** |
| 本地化 UI 精灵（多种语言） | **选项 B：Addressables** |
| 角色皮肤或外观 | **选项 B：Addressables** |

### 2. SpritePacker 模式（必需）

**在创建图集之前启用 SpritePacker 模式，然后读取设置并确认是否生效。**
使用 [resources/enablespritepacking.cs](resources/enablespritepacking.cs) 中的代码；它设置 `EditorSettings.spritePackerMode` 并配置导入器的打包设置。

这是决定您生成的图集是否有效的步骤。`Disabled` 是 `SpritePackerMode` 的零值，因此任何项目中没有人设置它的项目都携带打包 **禁用**，在禁用状态下创建的图集仍然可以导入，仍然显示为资源，仍然看起来完整，但永远无法打包。Unity 在 Inspector 中说明：*"Sprite Atlas 打包已禁用"*。工作流中的其他部分没有失败，因此以这种方式交付的图集被视为成功。不要假设项目已经配置：读取该值。

因此不要将"我已设置"视为完成。设置后，读取 `EditorSettings.spritePackerMode`，确认它不是 **禁用**，并报告您实际读取的值。如果您无法读取它，请说明而不是假设写入已成功。

**不要直接编辑元文件。**

## 🚨 关键：默认方法是预构建生成

**始终使用 `IPreprocessBuildWithReport` 在构建管道期间自动生成或更新 SpriteAtlas。** 这是默认和必需的方法，除非用户明确请求手动创建。

### ❌ 不要创建手动菜单项脚本

**除非明确请求，否则永远不要为图集生成创建带有 `[MenuItem]` 属性的脚本。** 预构建方法消除了手动点击的需求。**仅用于**：手动优化的布局、特定的精灵排列或编辑器预览需求。见 [高级：手动创建](#advanced-manual-authoring)。

## 🚨 关键：精灵源位置限制

**仅从项目的 Assets 文件夹添加精灵。永远不要从 Unity 内置资源、包或外部位置添加精灵。** Unity 内置资源无法打包到 SpriteAtlas，包资源可能导致导入/依赖问题。

## 关键 V2 架构

| 上下文 | 组件 | 目的 | 允许使用 |
|---------|-----------|---------|---------------|
| **编辑器创建** | `SpriteAtlasAsset` | 添加/删除精灵/文件夹；存储元数据 | ✅ 仅编辑器脚本 |
| **编辑器设置** | `SpriteAtlasImporter` | 配置纹理、打包、平台设置 | ✅ 仅编辑器脚本 |
| **编辑器打包** | `SpriteAtlasUtility.PackAtlases()` | *可选* 编辑器预览打包（不用于构建） | ⚠️ 仅用于预览；构建时自动打包 |
| **运行时** | `SpriteAtlas` | 查询打包的精灵（只读） | ✅ 仅运行时脚本 |
| **运行时加载** | `SpriteAtlasManager` | 动态加载回调 | ✅ 仅运行时脚本 |

### 禁止跨上下文使用（常见错误来源）

| ❌ 无效模式 | ✅ 正确模式 |
|--------------------|-------------------|
| 在编辑器代码中使用 `new SpriteAtlas()` | 使用 `SpriteAtlasAsset` + `SpriteAtlasImporter` |
| 在编辑器中使用 `AssetDatabase.LoadAssetAtPath<SpriteAtlas>(...)` | 使用 `SpriteAtlasAsset.Load(...)` |
| 在编辑器中使用 `SpriteAtlasAsset.GetPackables()` | 使用 `SpriteAtlas.GetPackables()` |
| 在编辑器脚本中修改 `SpriteAtlas` | 修改 `SpriteAtlasAsset` → 重新导入 → 使用 `SpriteAtlasImporter` |
| 从原始可打包对象（精灵/文件夹）创建变体 | 从主运行时 `SpriteAtlas` 创建变体 |

**永远不要在编辑器代码中针对 `SpriteAtlas` 编写脚本** — 它仅在 V2 的运行时使用，除了 `GetPackables` 实例方法。

## 核心V2工作流（仅作参考 - 使用预构建）

> 🚨 **重要**：此工作流仅作参考。**始终在 `IPreprocessBuildWithReport.OnPreprocessBuild()` 内实现此工作流**，而不是在手动脚本中。见 [快速入门](#quick-start-automated-prebuild-generation-default-approach)。

## 前提条件

- Unity 6000.3 或更高版本
- 对 Unity 资源导入管道的基本理解
- 熟悉用于图集创建的编辑器脚本

## 快速入门：自动预构建生成（默认方法）

### 概述

**这是创建 SpriteAtlas 的主要和默认方法。** 实现 `IPreprocessBuildWithReport` 以根据分类规则在每次构建之前自动生成或更新 SpriteAtlas。无需手动菜单点击。

### 工作流步骤

**步骤 1：询问用户交付机制**

在生成代码之前，询问："您想如何交付 SpriteAtlas： (A) 内置数据或 (B) 通过 Addressables 延迟绑定？"

**步骤 2：创建预构建脚本**

在 Editor 文件夹中创建此脚本。根据用户的交付选择进行自定义：

### 选项 A：内置数据（立即加载）

内置数据（立即加载）

### 选项 B：通过 Addressables 延迟绑定（按需加载）

> 🚨 **关键强制执行**：当用户选择 Addressables 时，您必须生成以下所有三个脚本。永远不要只生成一个或两个 - 所有三个都是 Addressables 交付工作正常所必需的。

**必需脚本（全部三个强制要求）：**

1. **预构建脚本**（IPreprocessBuildWithReport）- 生成图集并自动创建 Addressables 条目
2. **构建 Addressables 脚本**（IPostprocessBuildWithReport）- 构建 Addressables 内容包
3. **延迟绑定运行时加载器**（MonoBehaviour）- 处理运行时的按需加载

见 [references/addressables-delivery.md](references/addressables-delivery.md) 获取完整实现。

#### 完整工作流

```
用户请求
    ↓
步骤 0：检查带有 [UNITY-SKILL:SPRITEATLAS] 标识符的现有脚本
    ↓
    ├─ 找到现有脚本？
    │   ↓ YES
    │   询问用户：更新现有 / 创建新 / 中止
    │   ↓
    │   处理用户选择
    │
    └─ NO 现有脚本或用户选择 "创建新"
        ↓
        询问 "内置数据或 Addressables?"
        ↓
        ├─ 选项 A：内置
        │   ↓
        │   生成 1 个脚本：预构建生成器 (includeInBuild=true)
        │
        └─ 选项 B：Addressables
            ↓
            生成 3 个脚本：
              1. 预构建：生成图集 + 创建 Addressables 条目 (includeInBuild=false)
              2. 后处理：构建 Addressables 包
              3. 运行时：延迟绑定加载器组件
```

**步骤 3：自定义分类规则**

编辑 `OnPreprocessBuild` 方法以匹配您项目的精灵组织。选择一个或组合多个策略：

| 策略 | 使用场景 | 实现 |
|----------|-------------|----------------|
| **基于文件夹** | 精灵按文件夹结构组织 | `GenerateAtlasByFolder("Assets/Art/UI", "Assets/Atlases/UI.spriteatlasv2")` |
| **命名约定** | 精灵遵循命名模式 | `GenerateAtlasByNaming("Assets/Art", "icon_", "Assets/Atlases/Icons.spriteatlasv2")` |
| **资源标签** | 精灵带有标签 |
| **基于场景** | 精灵在特定场景中使用 | 查询场景引用 |

**步骤 4：构建您的项目**

图集在构建期间自动生成/更新。**无需手动菜单点击。** 这是为什么预构建是默认方法的原因。

**对于内置数据（选项 A）：**
- 图集包含在构建中
- 准备好在运行时立即使用

**对于 Addressables（选项 B）- 额外必需步骤：**

您必须生成三个脚本（而不仅仅是其中一个）：

1. **预构建脚本**（IPreprocessBuildWithReport）- 自动生成图集和创建 Addressables 条目
2. **构建 Addressables 脚本**（IPostprocessBuildWithReport）- 构建 Addressables 内容包
3. **延迟绑定运行时加载器**（MonoBehaviour）- 通过 SpriteAtlasManager 处理按需加载

构建过程将：
- 生成图集（预构建步骤）
- 自动创建地址条目
- 构建地址ables 内容包（后处理步骤）
- 在运行时：延迟绑定加载器在精灵首次访问时自动加载图集

### 常见分类模式

**按文件夹结构：**
```csharp
GenerateAtlasByFolder("Assets/Art/UI/Buttons", "Assets/Atlases/UI_Buttons.spriteatlasv2");
GenerateAtlasByFolder("Assets/Art/UI/Icons", "Assets/Atlases/UI_Icons.spriteatlasv2");
GenerateAtlasByFolder("Assets/Art/Characters/Player", "Assets/Atlases/Player.spriteatlasv2");
```

**按命名约定：**
```csharp
GenerateAtlasByNaming("Assets/Art", "icon_", "Assets/Atlases/Icons.spriteatlasv2");
GenerateAtlasByNaming("Assets/Art", "bg_", "Assets/Atlases/Backgrounds.spriteatlasv2");
```

### 预构建中的变体生成

为不同分辨率生成变体图集。

## 高级：手动创建（非默认 - 仅在明确请求时使用）

> ⚠️ **警告**：手动创建不是默认方法。仅在用户明确请求手动控制或开发期间编辑器预览时使用这些模式。

> 🚨 **默认方法**：使用预构建生成与 `IPreprocessBuildWithReport` 代替。见 [快速入门](#quick-start-automated-prebuild-generation-default-approach)。

**手动创建仅适用于：**
- 手动优化的精灵布局，其中精确位置很重要
- 定制的精灵排列要求
- 编辑器预览期间创建工作流
- 用户明确请求

**当不使用手动创建时：**
- 用户要求"创建精灵图集"（使用预构建）
- 用户要求"优化精灵"（使用预构建）
- 用户要求自动工作流（使用预构建）
- 未提及特定手动控制要求

有关完整手动创建模式，包括主图集创建、变体创建和运行时加载，请参阅 [references/manual-authoring.md](references/manual-authoring.md)。

## 关键要求（V2 特定）

1. **🚨 始终首先检查现有脚本**：在生成代码之前，扫描带有 `[UNITY-SKILL:SPRITEATLAS]` 标识符的脚本，并提示用户更新或创建新脚本
2. **🚨 始终标记生成的脚本**：在每个生成的脚本顶部包含技能标识符，以便将来检测
3. **🚨 始终询问交付机制**：在生成代码之前，询问用户"内置数据或 Addressables?"
4. **🚨 始终启用 SpritePacker 模式**：在预构建脚本中设置 `EditorSettings.spritePackerMode = SpritePackerMode.SpriteAtlasV2`
5. **🚨 始终使用预构建生成**：作为创建图集的默认方法实现 `IPreprocessBuildWithReport`
6. **🚨 仅添加来自 Assets/ 文件夹的精灵**：永远不要添加来自 Unity 内置资源、包或外部位置的精灵
7. **🚨 对于 Addressables 交付，始终生成三个脚本**：
   - 预构建图集生成器（带 Addressables 设置）
   - `IPostprocessBuildWithReport` - 构建 Addressables 内容
   - 延迟绑定运行时加载器脚本（扩展 `SpriteAtlasManager`）
8. **正确设置 includeInBuild**：内置数据为 `true`，Addressables 为 `false`
9. **两步编辑器模式**：使用 `SpriteAtlasAsset` 创建 → 保存 → 导入 → 通过 `SpriteAtlasImporter` 配置 → SaveAndReimport()
10. **永远不要在编辑器代码中使用 `SpriteAtlas`** — 除了加载运行时图集的 `SpriteAtlas.GetPackables()` 实例方法
11. **变体引用主图集**：使用 `SetMasterAtlas(SpriteAtlas)` 与通过 `AssetDatabase.LoadAssetAtPath<SpriteAtlas>()` 加载的运行时实例
12. **平台格式分配**：直接使用 `format = TextureImporterFormat.ASTC_6x6`（无需强制转换）
13. **文件扩展名**：V2 图集使用 `.spriteatlasv2`（不是 `.spriteatlas`）
14. **`SpriteAtlasUtility.PackAtlases()` 是可选的**：仅用于编辑器预览；构建时自动打包

有关常见错误和无效模式，请参阅 [references/common-errors.md](references/common-errors.md)。

## 详细参考

- **Addressables 交付**：[references/addressables-delivery.md](references/addressables-delivery.md) - 完整的 Addressables 延迟绑定设置
- **手动创建**：[references/manual-authoring.md](references/manual-authoring.md) - 手动模式（非默认 - 仅在明确请求时使用）
- **常见错误**：[references/common-errors.md](references/common-errors.md) - 无效模式和 API 修正
- **API 参考**：[references/api.md](references/api.md) - 完整 V2 类文档
- **自定义打包**：[references/custom-packing.md](references/custom-packing.md) - `ScriptablePacker` 实现
- **最佳实践**：[references/best-practices.md](references/best-practices.md) - 优化和常见陷阱

## 命名空间

**编辑器脚本：**
```csharp
using UnityEditor;            // AssetImporter, AssetDatabase
using UnityEditor.U2D;        // SpriteAtlasAsset, SpriteAtlasImporter, SpriteAtlasUtility
using UnityEngine;            // 运行时类型（例如，TextureImporterFormat）
using UnityEngine.U2D;        // SpriteAtlas
```

**运行时脚本：**
```csharp
using UnityEngine;            // 核心Unity类型
using UnityEngine.U2D;        // SpriteAtlas, SpriteAtlasManager
```
