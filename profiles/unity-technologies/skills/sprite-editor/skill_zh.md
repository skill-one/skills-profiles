# 图标编辑器

图标元数据（矩形、边框、枢轴、轮廓）位于导入器内部，而不是在一个你可以编辑的文件中。要访问它，需要通过一个活动的编辑器运行 C#。

**`unity-cli` 技能负责带你到达那里**——安装 CLI、确认连接的编辑器、添加项目的 `com.unity.pipeline` 包、区分一个真正缺失的编辑器和一个卡在安全模式下的编辑器，以及发现编辑器的命令目录。首先遵循它；不要在这里重新推导任何内容。

有两件事它无法为你知道：

- **你需要 `eval`，而不仅仅是可访问的编辑器**。确认它出现在目录中——它的存在取决于 Pipeline 包的版本，而不是 CLI。
- **永远不要手动编辑 `.meta` 文件来更改图标元数据**。导入器拥有这些数据，并且下面的能力检查是为了防止损坏，所以一个无法访问的编辑器是一个停止信号，而不是一个让你即兴发挥的提示。

使用 `eval` 命令通过连接的编辑器运行 C#。从 `unity command --format json` 而不是假设一个参数形状来发现它的参数形状，内联形式是 `unity command eval --code '<snippet>'`，并且一些 Pipeline 版本还注册了 `eval_file` 来从文件中运行一个片段。**在尝试 `eval_file` 之前检查目录；它经常不存在**。`unity command` 默认的超时时间为 30 秒。

生成使用 ISpriteEditorDataProvider 来操作 Unity 图标的 C# 编辑器脚本。与 TextureImporter、PSBImporter 和自定义导入器一起工作。

### 将 C# 传递给 `eval`

`eval` 编译的是一个 **语句块，而不是文件**。有两个后果，两者都会导致编译错误而不是警告：

- **没有 `using` 指令**。编译器将 `using UnityEngine;` 读取为资源释放语句并拒绝它（`CS0210`）。
- **类型必须完全限定**。一个裸的 `AssetDatabase` 或 `Volume` 无法解析（`CS0246` / `CS0103`），而一个裸的 `Object` 与 `object` 混淆（`CS0104`）。

当下面的小片段被写为文件时——为了可读性，或者因为它打算保存到项目中——在传递给 `eval` 之前限定类型。

## 工作流程

所有生成的脚本都必须遵循 [references/templates.md](references/templates.md) 中的安全核心模式，这包括强制的能力检查。如果能力检查失败，永远不要尝试操作——这可以防止数据损坏。执行后，在 Unity 控制台和项目窗口中验证结果。

## 常见操作

**修改名称/矩形/边框/枢轴**：更新相应的 `SpriteRect` 字段（有关枢轴示例，请参阅脚本/SetPivotExample.cs）
- 需要：`EditSpriteName`、`EditSpriteRect`、`EditBorder` 或 `EditPivot`

**添加/删除/切片**：创建或过滤 `SpriteRect` 数组（有关 Unity 2021.2+ 的要求，请参阅 [references/background.md](references/background.md)）
- 需要：`CreateAndDeleteSprite`

**设置轮廓**：获取 `ISpriteOutlineDataProvider` → 调用 `SetOutlines()` 并传入 GUID + Vector2 数组

## 重要提示

- 不要使用 AssetPostprocessor 或 MenuItem 模式
- 仅生成独立的片段——没有 `AssetPostprocessor`，没有 `MenuItem`
- **枚举赋值**：始终使用枚举值并转换为数值类型。永远不要使用原始数字。
  - ✅ 正确：`(int)SpriteAlignment.Center`
  - ❌ 错误：`1`（魔术数字）
