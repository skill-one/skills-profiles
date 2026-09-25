**在进行下一步操作前：** 如果用户询问创建新的编辑器窗口、自定义检查器或 PropertyDrawer，但未明确提及 IMGUI/OnGUI，建议使用 UI Toolkit (CreateGUI)，因为这是现代方法。仅在以下情况下使用 IMGUI：
- 用户正在修改现有的 IMGUI 代码
- 用户明确要求使用 IMGUI/即时模式
- 项目仅使用 IMGUI 作为编辑器工具

当启用时，读取参考文件：
- [references/templates.md](references/templates.md) — 编辑器窗口、检查器、PropertyDrawer 模板
- [references/gui-elements.md](references/gui-elements.md) — GUI 元素、布局组、样式

## 何时使用此技能

**重要提示：** 此技能仅用于**遗留 IMGUI 代码**。使用此技能时：

- 用户正在维护/更新现有的 IMGUI 编辑器代码（带有 `OnGUI()`、`OnInspectorGUI()` 的文件）
- 用户**明确要求**使用 IMGUI/即时模式 GUI
- 项目仅使用 IMGUI 作为所有编辑器工具

**不要使用此技能：**
- 新的编辑器窗口（使用 UI Toolkit 和 `CreateGUI()` 代替）
- 新的自定义检查器（使用 UI Toolkit 代替）
- 未明确提及 IMGUI 或 OnGUI 的请求

**遗留 IMGUI 用于：**
- **编辑器窗口** — 带有 `OnGUI()` 的 `EditorWindow` 类
- **自定义检查器** — 带有 `OnInspectorGUI()` 的 `Editor`、`PropertyDrawer` 类
- **调试覆盖层** — MonoBehaviour 中的 `OnGUI()`（运行时）

IMGUI **不**用于运行时游戏 UI — 请使用 UI Toolkit 或 uGUI。

## 范围

**仅生成请求的内容（针对遗留 IMGUI 代码）：**

| 请求 | 输出 | 备注 |
|------|------|------|
| 编辑器窗口 (IMGUI/OnGUI) | `EditorWindow` 带有 `OnGUI()` | 仅在明确为 IMGUI 时 |
| 自定义检查器 (IMGUI) | `Editor` 带有 `OnInspectorGUI()` | 仅在明确为 IMGUI 时 |
| Property drawer (IMGUI) | `PropertyDrawer` 带有 `OnGUI()` | 仅在明确为 IMGUI 时 |
| 调试覆盖层 | `MonoBehaviour` 带有 `OnGUI()` | 运行时调试 |
| 更新现有 IMGUI 脚本 | 修改现有 OnGUI 代码 | 总是适用 |

**如果模糊不清，请澄清：**
- "检查器" → 特定类型的自定义编辑器，还是 PropertyDrawer？**同时询问：** 应该使用 UI Toolkit（现代）还是 IMGUI（遗留）？
- "编辑器窗口" → **首先询问：** 应该使用 UI Toolkit（现代/CreateGUI）还是 IMGUI（遗留/OnGUI）？
- "工具窗口" → `EditorWindow` 具备什么功能？使用哪个 UI 系统？

## 规范

**首先遵循项目模式。** 在应用默认值之前，搜索现有的编辑器脚本。

| 类型 | 规范 | 良好 | 不良 |
|------|------|------|------|
| 脚本名称 | PascalCase | `MyToolWindow.cs` | `my-tool-window.cs` |
| EditorWindow | `[Name]Window.cs` | `LevelEditorWindow.cs` | `LevelEditor.cs` |
| 自定义编辑器 | `[Type]Editor.cs` | `EnemyEditor.cs` | `EnemyInspector.cs` |
| PropertyDrawer | `[Type]Drawer.cs` | `RangeDrawer.cs` | `RangePropertyDrawer.cs` |
| 位置 | `Editor` 文件夹 | `Assets/Editor/` | `Assets/Scripts/` |

**必须使用 Editor 文件夹** — 使用 `UnityEditor` 命名空间的脚本必须位于 `Editor` 文件夹中，否则将无法构建。

## 工作流程

1. **分析** — 确定所需的脚本类型（EditorWindow、Editor、PropertyDrawer 等）
2. **搜索** — 查找现有的编辑器脚本以匹配模式
3. **遵循项目模式** — 匹配文件夹结构和命名
4. **创建脚本** — 使用适当的基类和属性
5. **实现 OnGUI** — 使用布局组构建界面

## 脚本结构

### EditorWindow
```
[MenuItem 属性] → 添加到菜单
ShowWindow() 静态方法 → 打开窗口
OnGUI() → 绘制界面
OnEnable/OnDisable → 初始化/清理
```

### Custom Editor
```
[CustomEditor 属性] → 目标组件类型
OnInspectorGUI() → 绘制检查器
OnEnable() → 缓存 SerializedProperties
serializedObject.Update/ApplyModifiedProperties → 撤销支持
```

### PropertyDrawer
```
[CustomPropertyDrawer 属性] → 目标类型或属性
OnGUI(Rect, SerializedProperty, GUIContent) → 绘制属性
GetPropertyHeight() → 如果需要，自定义高度
```

## 关键规则

- **缓存 GUIStyle 对象** — 在 OnGUI 中永不创建新的 GUIStyle（会导致每帧内存分配）
- **使用 SerializedProperty** — 为检查器提供适当的撤销/重做支持
- **调用 ApplyModifiedProperties()** — 在任何序列化对象更改后
- **使用 EditorGUILayout** — 用于编辑器脚本（自动布局）
- **使用 GUILayout** — 用于运行时 OnGUI
- **使用 Begin/End 对** — 始终匹配 BeginHorizontal 与 EndHorizontal 等
- **必须使用 Editor 文件夹** — 脚本若不在 Editor 文件夹中将无法构建

## 布局基础

**水平分组：**
```csharp
EditorGUILayout.BeginHorizontal();
// 元素并排显示
EditorGUILayout.EndHorizontal();
```

**垂直分组：**
```csharp
EditorGUILayout.BeginVertical("box");
// 元素堆叠显示，带框样式
EditorGUILayout.EndVertical();
```

**滚动视图：**
```csharp
scrollPos = EditorGUILayout.BeginScrollView(scrollPos);
// 可滚动内容
EditorGUILayout.EndScrollView();
```

**可折叠区域：**
```csharp
showSection = EditorGUILayout.Foldout(showSection, "区域名称");
if (showSection)
{
    EditorGUI.indentLevel++;
    // 区域内容
    EditorGUI.indentLevel--;
}
```

## 常见模式

**带动作的按钮：**
```csharp
if (GUILayout.Button("执行操作"))
{
    // 动作代码
}
```

**带标签的属性字段：**
```csharp
EditorGUILayout.PropertyField(myProperty, new GUIContent("标签"));
```

**对象引用字段：**
```csharp
myObject = (MyType)EditorGUILayout.ObjectField("标签", myObject, typeof(MyType), true);
```

**禁用组：**
```csharp
EditorGUI.BeginDisabledGroup(condition);
// 禁用元素
EditorGUI.EndDisabledGroup();
```

## 最佳实践

- 使用 `SerializedObject` 和 `SerializedProperty` 以支持撤销
- 在 `OnEnable()` 中缓存属性引用
- 仅对非序列化更改使用 `EditorUtility.SetDirty()`
- 在直接修改对象前使用 `Undo.RecordObject()`
- 使用 `EditorStyles` 以保持一致外观
- 使用 `GUILayout.FlexibleSpace()` 推动元素分开

参考 `references/templates.md` 获取完整的脚本模板。
参考 `references/gui-elements.md` 获取完整的元素参考。
