本指南涵盖了设置和配置 Unity Localization 的内容，包括区域设置、字符串和资源表、Addressables 集成以及通过资源表支持 CJK 字体。

## 0. 包安装检查
在执行任何其他操作之前，请验证 Localization 包是否已安装。如果包未安装，本技能中的许多 API 会静默失败或抛出令人困惑的错误。

1. **通过读取项目来检查，而不是询问包管理器。** 在 **`Packages/packages-lock.json`** 中查找 `com.unity.localization`。该文件记录了 Unity 实际解析的内容，它是纯 JSON 格式，读取它无需编辑器或异步调用。
   (`Packages/manifest.json` 仅记录请求的内容，因此请检查锁定文件。)
2. **如果缺失则安装：** `UnityEditor.PackageManager.Client.Add("com.unity.localization")`。
3. **正确等待。** `Client.Add` 和 `Client.List` 是**异步**的：当调用返回时，它们返回的请求仍然是 `InProgress` 状态，因此在同一语句中读取结果不会告诉你任何信息。也不要在 `IsCompleted` 上忙等待；那会阻塞你正在运行的主线程。相反，在触发安装后返回，然后在后续调用中**轮询 `packages-lock.json`**，直到 ID 出现。安装还会触发域重新加载，因此请预期前几次轮询会失败；全新安装通常几秒钟内即可解析完成。
4. **在使用它们之前，确认类型是否实际上已加载**，因为锁定文件可以在程序集准备好之前写入：
   ```csharp
   var t = System.Type.GetType(
       "UnityEngine.Localization.Settings.LocalizationSettings, Unity.Localization");
   return t != null ? "ready" : "not loaded yet";
   ```
   只有在该返回 `ready` 后才能继续。

## 1. Localization 设置和区域设置
如果 `LocalizationEditorSettings.ActiveLocalizationSettings` 为 null，则必须找到或创建它：
1. **查找：** 使用 `AssetDatabase.FindAssets("t:LocalizationSettings", new[] { "Assets" })`。如果找到，则加载第一个并将其分配给 `LocalizationEditorSettings.ActiveLocalizationSettings`。
   - **始终传递搜索文件夹。** 无作用域的 `FindAssets` 搜索整个项目，包括只读包，因此它可能会返回来自包的资产，而你最终指向的是无法编辑的内容。本技能中的每个 `FindAssets` 调用都适用此规则。
2. **创建：** 如果未找到，则创建一个新实例并将其保存到 `Assets/Localization/LocalizationSettings.asset`。使用 `ScriptableObject.CreateInstance<LocalizationSettings>()` 后跟 `AssetDatabase.CreateAsset()`。
3. **激活：** 设置 `LocalizationEditorSettings.ActiveLocalizationSettings = settings`。
4. **区域设置：** 确保存在区域设置（en、fr、de 等）。如果缺失，则创建它们并使用 `LocalizationEditorSettings.AddLocale(locale)` 将它们添加到设置中。

## 2. 修改 Localization 表
对字符串或资源表进行程序化更改需要通知编辑器。
始终创建所需的资源表，除非项目中已存在一个。

### **安全填充模式**
从数据集填充表时，明确通过 `Locale.Identifier.Code` 进行匹配。`GetLocales()` 的顺序不一定与您的输入数据数组匹配——假设它会导致静默数据不匹配，这非常难以调试。
对于**资源表**，使用资产的 GUID：`table.GetEntry(sharedId) ?? table.AddEntry(sharedId, guid);`。

### **刷新和通知**
在修改任何内容（添加键、更新值）后，通知编辑器以便它可以刷新其内部状态。跳过此步骤将导致编辑器显示过时的数据，直到下次重新导入。
1. 对每个修改的 `Table` 调用 `EditorUtility.SetDirty(collection)`，`EditorUtility.SetDirty(collection.SharedData)`。
2. **Unity 6+ 通知：** `LocalizationEditorSettings.EditorEvents.RaiseCollectionModified(sender, collection);`
3. 始终在末尾调用 `AssetDatabase.SaveAssets()`。

## 3. UI Localization 和布局
### **命名空间和冲突**
- **始终限定名称：** 使用 `UnityEngine.UI.Image`、`UnityEngine.UI.VerticalLayoutGroup`、`UnityEngine.UI.ScrollRect`、`UnityEngine.UI.Mask`、`UnityEngine.UI.CanvasScaler`、`UnityEngine.UI.GraphicRaycaster`、`UnityEngine.UI.ContentSizeFitter`、`UnityEngine.UI.LayoutRebuilder` 等。
- `UnityEngine.UI` 既是命名空间也是类容器，因此未限定名称的名称会产生 `CS0118`（命名空间像类型一样使用）。完全限定名称可以完全避免此问题。
- **单个实例：** 始终检查 `GameObject.Find("YourCanvasName")` 并在创建新实例之前销毁旧的实例。
- **区域设置切换：使用包，并将预览和运行时分开。** 这两种机制是不同的，将它们混淆是为什么区域设置切换通常需要手动编写的原因。
  - **在编写时预览区域设置**，使用 **Localization Scene Controls** 窗口（`Window > Asset Management > Localization Scene Controls`）。这是仅限编辑器的。它不是运行时功能，因此当游戏本身需要语言设置时，这不是答案。
  - **在运行时切换区域设置**，分配 `LocalizationSettings.SelectedLocale`。这是支持入口点，通过 `LocalizeStringEvent` 绑定的一切都会从此更新。
  - **固定游戏启动的区域设置**，在 Localization Settings 资产上配置启动区域设置选择器。`SpecificLocaleSelector` 会强制选择特定区域；默认链否则会拾取系统语言。
  - **永远不要手动编写区域状态。** 一个真实的游戏语言菜单是好的且预期的，只要它设置 `SelectedLocale` 并让包传播更改。禁止的是跟踪自己的“当前语言”变量的调试下拉菜单或菜单，自己交换字符串，或绕过包，因为项目中的其他内容不会跟随它。

### **本地化字符串事件（稳健绑定）**
- **检查组件类型：** 确定目标是否为 `TextMeshPro` 或传统的 `UnityEngine.UI.Text`。
- **正确绑定：** 添加公共的 `UnityEngine.Localization.Components.LocalizeStringEvent` 组件并自行连接——将 `StringReference` 设置为表条目，然后添加一个 `OnUpdateString` 监听器，将值分配给文本组件（`TMP_Text.text` 用于 TextMeshPro，`UnityEngine.UI.Text.text` 用于传统文本）。

  不要反射到 `UnityEditor.Localization.Plugins.TMPro.LocalizeComponent_TMPro` 或其 UGUI 对应物。这些是 `internal` 的（在 Localization 1.5.12 上测量），因此到达它们意味着绕过访问控制以到达 Unity 不做稳定性承诺的 API——它可以在任何包发布中更改或消失。`LocalizeStringEvent` 是公共的，并且通过显式连接完成相同的工作。
- **布局重建：** 在设置本地化文本或填充列表后，调用 `UnityEngine.UI.LayoutRebuilder.ForceRebuildLayoutImmediate(parentTransform)` 以确保尺寸更新。

## 4. 亚洲语言字体支持（CJK）
避免使用 TMP 回退字体用于 CJK 区域设置。相反，为每个特定区域设置使用**资源表字体交换**——回退是不可靠的，当缺少字形时难以调试。

### 先决条件：必须导入 TMP Essential Resources

在触摸任何 TMP API 之前检查此内容。在一个从未导入它们的项目中，`TMP_Settings.instance` 是 `null`，TMP 调用会失败，并带有无用的 `NullReferenceException`。`TMP_FontAsset.CreateFontAsset` 是其中之一，因此字体创建在第一行就会因代码中的错误而失败。

```csharp
// 检查。
var ready = TMPro.TMP_Settings.instance != null;
```

如果未准备好，请非交互式导入它们：

```csharp
// 不要使用 EditorApplication.ExecuteMenuItem("Window/TextMeshPro/Import TMP Essential Resources")。
// 它返回 true 然后打开一个对话框，等待人类，因此什么都没有被导入，运行看起来像挂起。直接导入包而不是。
string package = null;
var cache = System.IO.Path.GetFullPath(System.IO.Path.Combine(
    UnityEngine.Application.dataPath, "..", "Library", "PackageCache"));
foreach (var dir in System.IO.Directory.GetDirectories(cache))
{
    // TMP 在 Unity 6 中作为 com.unity.ugui 的一部分提供，并且文件夹名称包含版本哈希，
    // 因此搜索文件而不是硬编码路径。
    var candidate = System.IO.Path.Combine(dir, "Package Resources", "TMP Essential Resources.unitypackage");
    if (System.IO.File.Exists(candidate)) { package = candidate; break; }
}
UnityEditor.AssetDatabase.ImportPackage(package, false);   // false = 非交互式
```

然后在后续调用中轮询 `TMP_Settings.instance != null`，与步骤 0 中的包检查相同，并且只有在它非 null 时才继续。在 Unity 6000.5.8f1 上验证：非交互式导入在几秒钟内完成，资产位于 `Assets/TextMesh Pro`。

1. **使用特定区域设置字体：** 西方字体如 Arial 或 Liberation Sans 不包含 CJK 字形，这会导致“豆腐”（方块）出现。始终使用为目标语言设计的字体：
   - 对于**简体中文（zh-Hans）**：使用 `msyh.ttc`（微软雅黑）或等效字体。
   - 对于**日语（ja）**：使用 `msgothic.ttc`（MS Gothic）或等效字体。
   - 对于**韩语（ko）**：使用 `malgun.ttf`（말곤 고딕）或等效字体。
   - 如果系统字体复制失败，请停止并报告。不要用西方字体替代。
2. **稳健字体创建：** 从导入的字体创建动态 `TMP_FontAsset`。
3. **多图集和动态：** CJK 字符集太大，无法用于静态图集；单个图集会立即耗尽空间。
   - `fontAsset.atlasPopulationMode = AtlasPopulationMode.Dynamic;`
   - `fontAsset.isMultiAtlasTexturesEnabled = true;`
4. **子资产：** 添加图集纹理**和材质**。仅添加纹理是常见的错误，材质将永远不会到达文件：在 Unity 6000.5.8f1 上测量，没有第二个调用保存的字体资产在磁盘上包含**零** `Material` 对象。仅存在于内存中的材质不是资产的一部分，因此任何加载资产的人都得到 TMP 重建的内容，而不是您配置的材质，并且您应用的所有设置都会被静默删除。
    ```csharp
    // 每个图集纹理，而不仅仅是第一个。步骤 3 启用了多图集，因此可能有多个。
    foreach (var atlas in fontAsset.atlasTextures)
    {
        UnityEditor.AssetDatabase.AddObjectToAsset(atlas, fontAsset);
    }
    // 材质也是如此。没有这一行，它不会被写入资产。
    UnityEditor.AssetDatabase.AddObjectToAsset(fontAsset.material, fontAsset);
    ```
    - 显式链接材质的纹理：`fontAsset.material.mainTexture = fontAsset.atlasTexture;`
      并在保存之前设置字体资产、其材质及其纹理为脏。(`atlasTexture` 是 `atlasTextures` 的第一个条目，这是主要材质绘制的来源，因此这与上面添加每个纹理一致。)
    - **根据文件而不是您持有的对象进行验证。** 在 `AssetDatabase.SaveAssets()` 之后，调用 `AssetDatabase.LoadAllAssetsAtPath(path)` 并确认返回的对象中包含 `Material`。不要满足于 `fontAsset.material != null`：无论材质是否已保存，它都会保持 true，因为 TMP 将返回一个内存中的材质，因此它无法区分已保存的材质和未保存的材质。
5. **Addressables：** 资源表中引用的每个资产都必须标记为 Addressable。
    - 不要在资源表中引用 `Resources/` 文件夹中的资产。这会导致 `OperationException: Failed to load sub-asset` 错误。如果资产在 `Resources/` 中，请在将其标记为 Addressable 之前将其复制到 `Assets/Fonts/` 或类似位置。
    - 如果字体资产被删除并重新创建，新的 GUID 必须在资源表中手动更新并重新添加到 Addressables。
6. **专用类型：** 对于 TextMesh Pro 字体交换，优先使用 `LocalizedTmpFont` 而不是 `LocalizedAsset<TMP_FontAsset>` 以避免隐式转换错误。
7. **构建要求：** 在更新资源表或 Addressable 组后，触发构建：`AddressableAssetSettings.BuildPlayerContent();`。

### **验证步骤**
在完成任何 CJK 本地化任务之前：
1. **豆腐检查：** 将编辑器区域设置切换为 `zh-Hans`、`ja` 和 `ko`。检查 UI。如果任何字符显示为方块（豆腐），则字体设置已失败。
2. **资源表检查：** 验证 CJK 区域设置的资源表指向正确的 CJK `TMP_FontAsset`，而不是默认的西方字体。
3. **多图集检查：** 确认 CJK 字体资产的 `isMultiAtlasTexturesEnabled` 为 `true`。

## 5. 自动布局（UGUI）
- **父级：** `VerticalLayoutGroup`，`Child Control Height: True`，`Child Force Expand Height: False`。
- **标签：** 每个标签必须设置 `ContentSizeFitter` 为 `Vertical Fit: Preferred Size`。
- **TMP：** 设置 `Enable Word Wrapping: True` 和 `Overflow: Overflow`。

### 翻译现有项目时的注意事项
- **最小代码更改：** 不要修改与本地化无关的代码。使用静态辅助类（例如 `L10n`）来包装 `LocalizationSettings.StringDatabase.GetLocalizedString`，以便轻松地将其注入现有脚本。
- **稳健映射策略：** 在将现有 UI 文本映射到键时，按字符串长度（降序）排序键，并首先匹配最长的字符串。这可以防止短字符串（如 "NO"）与较长句子的部分匹配。在适当的地方使用不区分大小写的匹配。
- **组件事件监听器：** 使用 `UnityEventTools.AddPersistentListener` 将 `LocalizeStringEvent.OnUpdateString` 与文本组件的公共 `text` 设置器构建的委托连接。设置器没有 C# 方法组名称，因此通过名称构建委托：
  `(UnityAction<string>)Delegate.CreateDelegate(typeof(UnityAction<string>), text, "set_text")`。
  这是在公共成员上的反射，这是可以的。有关工作版本，请参阅
  [resources/L10nBatchProcessor.cs](resources/L10nBatchProcessor.cs)，包括首先清除任何现有持久监听器，以便重复运行不会堆叠重复项。
  - 不要通过 `SerializedObject` 直接写入持久调用字段（`m_MethodName`、`m_Mode`、`m_PersistentCalls`）。这些是私有的序列化名称，没有兼容性保证，而且没有必要：使用上述委托的 `AddPersistentListener` 产生相同的序列化调用（目标 = 文本组件，方法 = `set_text`，模式 = `EventDefined`）。
  - **然后必须设置调用状态，否则编辑器中的标签不会立即更新。**
    `AddPersistentListener` 将调用保留在 `UnityEventCallState.RuntimeOnly`，因此绑定在 Play 模式之外是正确的但休眠的：在编辑器中切换区域设置不会改变，并且通过保存和重新加载仍然如此。使用公共的
    `UnityEventBase.SetPersistentListenerState` 来修复它：
    ```csharp
    UnityEventTools.AddPersistentListener(lse.OnUpdateString, setText);
    var index = lse.OnUpdateString.GetPersistentEventCount() - 1;
    lse.OnUpdateString.SetPersistentListenerState(
        index, UnityEngine.Events.UnityEventCallState.EditorAndRuntime);
    ```
    在 Unity 6000.5.8f1 上验证：如果没有第二个调用，即使在预制件保存和重新加载后，监听器也不会在编辑模式下触发；有了它，调用状态变为 `EditorAndRuntime`，文本立即更新。
  - 持久监听器**必须**指向 `UnityEngine.Object` 上的方法；lambda 会失败。
  - **然后确认绑定是活跃的，不要假设。** 在 Inspectors 中看起来正确的连接但什么也不做是这一步的特征性失败。您需要的所有回读都在事件上的公共 API 上，因此这不需要触摸序列化字段：

    | 检查 | 调用 | 预期 |
    |---|---|---|
    | 有东西被连接 | `GetPersistentEventCount()` | `> 0` |
    | 它指向文本组件 | `GetPersistentTarget(i)`, `GetPersistentMethodName(i)` | 组件, `set_text` |
    | 它将在编写时触发 | `GetPersistentListenerState(i)` | `EditorAndRuntime` |
    | 它实际上更新了标签 | `lEvent.RefreshString()` | 文本值发生变化 |

    执行所有四个。计数大于零仅证明已连接某些内容，而 `RuntimeOnly` 调用在构建时是完美的，因此读取状态才能区分休眠的绑定和损坏的绑定。一个添加并配置但从未触发的组件比未本地化的标签更糟，因为它看起来已完成。
- **初始化和刷新：**
    - `LocalizationEditorSettings.CreateStringTableCollection` 期望一个**目录路径**（例如 `Assets/Localization`），而不是完整的资产路径。
    - 始终在程序化分配 `LocalizedString` 引用后调用 `lEvent.RefreshString()` 以立即更新 UI。
    - 键必须在集合的每个表中存在**非空值**（en、de、ja、…）。一个存在空值的键是常见的差距，它不是静默的：包会将其自己的“未找到…的翻译”文本打印到游戏 UI 中，因此发布的屏幕显示开发人员消息。不要通过肉眼检查。运行下面的完整性检查。
- **命名空间和 Linq：** 在搜索集合时始终包含 `using System.Linq;`，在处理区域设置或表时包含 `using UnityEngine.Localization;`。
- **验证：** 在修改表或 Addressables 后，运行 `AddressableAssetSettings.BuildPlayerContent()` 并切换编辑器区域设置以验证更改。激活后检查 `LocalizationSettings.Instance` 状态。

### 表完整性检查（在声明工作完成之前运行）

枚举表机械地回答“每个键在每个区域设置中是否都获得了值”，因此可以在游戏之前找到缺失的条目。运行它并报告输出。

```csharp
var gaps = new System.Collections.Generic.List<string>();
var checkedCount = 0;

foreach (var col in UnityEditor.Localization.LocalizationEditorSettings.GetStringTableCollections())
{
    foreach (var key in col.SharedData.Entries)
    {
        foreach (var table in col.StringTables)
        {
            checkedCount++;
            var entry = table.GetEntry(key.Id);
            // 缺失条目和存在但为空的条目在游戏中都显示为未翻译。
            if (entry == null || string.IsNullOrWhiteSpace(entry.Value))
            {
                gaps.Add($"{col.TableCollectionName} / {table.LocaleIdentifier.Code} / {key.Key}");
            }
        }
    }
}

// 条目为零不是通过。这意味着没有集合或没有区域设置表，因此检查未检查任何内容：在信任此检查之前修复它。
if (checkedCount == 0)
{
    return "INCONCLUSIVE: 未找到表条目。要么不存在 String Table Collection，要么集合没有区域设置表。在信任此检查之前修复。";
}

return gaps.Count == 0
    ? $"COMPLETE: {checkedCount} entries checked, no gaps"
    : $"GAPS ({gaps.Count} of {checkedCount} checked):\n  " + string.Join("\n  ", gaps);
```

在 Unity 6000.5.8f1 上针对一个故意清空的 `ja` 值的表进行验证：它报告 `GAPS 1 of 4` 指出确切的该条目，`COMPLETE (4 checked)` 一旦值被填充，以及在没有表的项目中 `INCONCLUSIVE`。

**报告差距列表而不是静默解决。** 一些差距是决定，而不是错误：未要求翻译的区域设置，或跨语言故意相同的键。用英文文本填充这些会隐藏决定。列出它们并让用户说哪些是故意的。
- **智能字符串：** 在需要的地方设置智能字符串。通过将 UI 它所在的整个 UI 以及任何影响它的脚本都考虑在内来检查每个字符串的上下文。在字符串表中设置上下文以确保翻译有意义。

## 6. 推荐的翻译策略
为了高效地翻译现有项目，请遵循以下多步骤工作流程：

1. **提取和组件设置：**
   - **查找所有实例。** 有两个独立的隐藏位置，扫描一个会遗漏另一个。
     - **编写的文本**位于场景和预制件上的组件上：传统的 `UnityEngine.UI.Text` 和 TextMeshPro (`TMP_Text`，`TextMeshProUGUI` 和 `TextMeshPro` 的基础)。遍历**这两种**类型。在一个真实项目中测量：`FindObjectsByType<Text>` 找到 1 个组件，而 `FindObjectsByType<TMP_Text>` 找到 13 个，因此仅通过传统类型的遍历报告成功几乎什么都没做。
     - **代码中组成的文本**永远不会在编辑时出现在组件上，因此没有场景遍历可以看到它。`scoreLabel.text = $"EXP {value}"` 是无法通过基于组件的扫描看到的字符串，并且是“完成”本地化过程中幸存的字符串。在 C# 中找到它：
       ```bash
       # 赋值和 SetText 调用中包含字符串字面量。
       grep -rnE '\.text\s*(=|\+=)\s*\$?"|SetText\(\s*\$?"' --include='*.cs' Assets/
       ```
       该模式捕获纯文本、插值、连接和 `+=` 形式以及 `SetText`，并且故意不匹配 `label.text = someVariable` 或 `label.text = Localize("KEY")`（第一个没有要提取，第二个已经通过 `Localize` 路由）。它的盲点是一个在别处声明的变量或 const 中持有的字面量；如果项目的计数看起来很低，请也检查该文件中的字符串字面量。
   - **报告未转换的内容。** 组成的字符串通常需要一个智能字符串或格式参数，这是一个判断，有些确实不值得本地化。无论你选择什么，请列出扫描找到的每个位置以及它是否被转换，以及如果没有转换，请说明原因。报告“本地化 24 个字符串”而九个找到的站点未转换是这种列表存在的失败模式：工作看起来已完成，而差距只有在从另一个区域设置获取的屏幕截图时才会出现。
   - **共享表：** 创建一个中央字符串表（例如 `UIStrings`），其中包含基础语言和一个“上下文”列，以指导翻译者。
   - **附加组件：** 对于每个找到的 UI 元素，附加一个 `LocalizeStringEvent`（用于文本）和一个 `LocalizedFont` 辅助组件（用于字体交换）。
   - **验证：** 确保这些组件使用持久监听器（`EditorAndRuntime`）设置，以便在区域设置更改时立即在编辑器中更新。

2. **上下文感知翻译：**
   - **翻译：** 一旦表被填充，请为每个区域设置提供翻译。
   - **上下文是关键：** 始终参考“上下文”列或检查 UI 布局以确保翻译符合预期含义和空间。
   - **语法和语气：** 确保语气与游戏风格匹配。例如，对按钮使用祈使动词（例如，德语：“Lauf!” 而不是 “Laufen”）并正确处理标签的复数形式（例如，“Punkte” 而不是 “Punkt”）。

3. **质量保证（QA）：**
   - **场景控制：** 使用 `Window > Asset Management > Localization Scene Controls` 或脚本：`LocalizationSettings.SelectedLocale = LocalizationSettings.AvailableLocales.GetLocale("de");`。
   - **视觉检查：** 系统地检查基础语言和所有目标语言的每个预制件和场景。
   - **布局适应：** 检查是否有文本溢出或“豆腐”（缺少字形）。如果字符串太长，请调整字体大小或使用 `ContentSizeFitter`。

## API 参考
有关详细 API 使用说明、常见的命名空间冲突、Addressables 模式和字体修复步骤，请参阅 [references/api-notes.md](references/api-notes.md)。

## 7. 加速本地化工作流程
为了高效地本地化整个项目，请使用处理所有场景的单次遍历的批处理脚本。

**在执行任何批处理操作之前询问：** 在运行任何批处理操作之前，请与用户确认：
> “这将打开项目中的每个场景，附加 `LocalizeStringEvent` 组件，并保存所有修改的场景。这无法自动撤销。您要继续吗？”

只有用户确认后才能继续。批处理处理器模板在 [resources/L10nBatchProcessor.cs](resources/L10nBatchProcessor.cs) 中。

它遍历**两种** `Text` 和 `TMP_Text`，并且 `LocalizeAll` **返回它无法匹配的标签**（`scene :: object :: "text"`）。打印该列表。返回值的目的正是：一个连接了 20 个标签而默默遗漏了 9 个的运行看起来与其他完全相同。列表仅涵盖编写的文本，因此请将其与第 6 节中的代码扫描和第 5 节中的表完整性检查配对。

### **加速技术提示**
- **表引用：** 使用 `TableReference` 名称（字符串）而不是 GUID——它们更容易阅读和维护。
- **批量刷新：** 使用 `LocalizationSettings.Instance.ForceRefresh()` 在修改后强制编辑器中的 UI 更新。
- **字体交换自动化：** 创建一次 `GameAssets` 表，并使用脚本一次性重新分配所有标签的 `LocalizeFontEvent`。
- **LocalizedFontAsset 组件：** 模板在 [resources/LocalizedFontAsset.cs](resources/LocalizedFontAsset.cs) 中。
