# dotnet-aot-compat

使 .NET 项目兼容原生 AOT 和修剪，通过系统地解决所有 IL 修剪/AOT 分析器警告。

## 何时使用此技能

- **"使此项目 AOT 兼容"**
- **"修复修剪警告"** 或 **"修复 IL 警告"**
- **"解决 IL2070 / IL2067 / IL2072 / IL2026 / IL3050 警告"**
- **"添加 DynamicallyAccessedMembers 注解"**
- **"在 .csproj 中启用 IsAotCompatible"**
- **"在升级到 net8.0 后，我的项目有修剪分析器警告"**
- **"为修剪器注解反射代码"**

## 何时不使用此技能

当项目仅针对 .NET Framework (net4x) 时，不要使用此技能，因为 .NET Framework 不支持修剪/AOT 分析器。

## 前提条件

一个现有的、针对 net8.0 或更高版本的目标 .NET 项目（或具有至少一个 net8.0+ TFM 的多目标项目）以及相应的 .NET SDK 已安装。

## 背景：什么是 AOT 兼容性

原生 AOT 和 IL 修剪器执行静态分析以确定哪些代码是可访问的。反射会破坏这种分析，因为修剪器无法看到在运行时访问的类型/成员。`IsAotCompatible` 属性启用分析器，这些分析器将这些问题标记为构建警告（ILXXXX 代码）。

## 严重规则

### ❌ 切勿错误地抑制警告

- **绝不**使用 `#pragma warning disable` 来抑制 IL 警告。它在构建时隐藏了来自 Roslyn 分析器的警告，但 IL 链接器和 AOT 编译器仍然可以看到问题。代码将在修剪/发布时失败。
- **绝不**使用 `[UnconditionalSuppressMessage]`。它告诉分析器**和**链接器忽略警告，这意味着修剪器无法验证安全性。在构建时引发错误始终比隐藏问题并在运行时无声地破坏要好。

### 💡 推荐方法

- **优先**使用 `[DynamicallyAccessedMembers]` 注解来通过调用链传递类型信息。
- **优先**重构以消除破坏注解流模式（例如，通过 `object[]` 将 `Type` 进行装箱）。
- **使用** `[RequiresUnreferencedCode]` / `[RequiresDynamicCode]` / `[RequiresAssemblyFiles]` 来标记方法与修剪根本不兼容，将要求传递给调用者。这比隐藏问题更清楚地暴露了问题——调用者必须明确承认不兼容性。

### 注解流是关键

修剪器通过赋值、参数传递和返回值跟踪 `[DynamicallyAccessedMembers]` 注解。如果此流被破坏（例如，通过将 `Type` 装箱到 `object`、存储在无类型的集合中或通过接口进行强制转换），修剪器会丢失跟踪并发出警告。修复方法是保留流，而不是抑制警告。

## 分步流程

> **不要预先探索代码库。** 构建警告会告诉你哪些文件和行需要更改。遵循紧密的循环：**构建 → 选择一个警告 → 在该文件和该行处打开该文件 → 应用修复配方 → 重新构建**。超出特定警告所指明的范围进行读取或分析是浪费精力，并会导致超时。让编译器来指导你。
>
> ❌ 不要在构建之前运行 `find`、`ls` 或 `grep` 来理解项目结构。不要阅读 README、文档或架构文件。你的第一个操作应该是步骤 1（启用 AOT 分析）然后构建。

### 步骤 1：在 .csproj 中启用 AOT 分析

添加 `IsAotCompatible`。如果项目不专门针对 net8.0+，请添加 TFM 条件（AOT 分析需要 net8.0+）：

```xml
<PropertyGroup>
  <IsAotCompatible Condition="$([MSBuild]::IsTargetFrameworkCompatible('$(TargetFramework)', 'net8.0'))">true</IsAotCompatible>
</PropertyGroup>
```

这会自动设置 `EnableTrimAnalyzer=true` 和 `EnableAotAnalyzer=true` 对于兼容的 TFM。对于多目标项目（例如，`netstandard2.0;net8.0`），条件确保在较旧的 TFM 上不会出现 `NETSDK1210` 警告。

### 步骤 2：构建并收集警告

```bash
dotnet build <project.csproj> -f <net8.0-or-later-tfm> --no-incremental 2>&1 | grep 'IL[0-9]\{4\}'
```

排序并去重。常见的警告代码：
- **IL2070**：对 `Type` 参数的反射调用缺少 `[DynamicallyAccessedMembers]`
- **IL2067**：向期望 `[DynamicallyAccessedMembers]` 的方法传递未注解的 `Type`
- **IL2072**：返回值或提取值缺少注解（通常来自装箱）
- **IL2057**：`Type.GetType(string)` 使用非常量参数
- **IL2026**：调用标记为 `[RequiresUnreferencedCode]` 的方法
- **IL2050**：具有 COM 封装参数的 P/invoke 方法
- **IL2075**：返回值通过反射流入未注解
- **IL2091**：泛型参数缺少 `[DynamicallyAccessedMembers]` 约束所需
- **IL3000**：在单文件/AOT 应用中 `Assembly.Location` 返回空字符串
- **IL3050**：调用标记为 `[RequiresDynamicCode]` 的方法

### 步骤 3：按代码筛选警告（不要读取每个文件）

按警告代码对步骤 2 中的警告进行分组并计数。**不要打开单个文件。** 通过计数识别前 1-2 个模式——这些驱动你的修复策略：

| 模式 | 典型修复 |
|------|---------|
| 许多 IL2026 + IL3050 来自 `JsonSerializer` | **立即转到策略 C**——创建一个 `JsonSerializerContext`，然后批量更新所有调用位置 |
| `Type` 参数上的 IL2070/IL2087 | 在最内层方法中添加 `[DynamicallyAccessedMembers]`，然后向外级联 |
| 传递未注解的 `Type` 的 IL2067 | 在源位置注解参数 |

**在大多数实际项目中，IL2026/IL3050 来自 JsonSerializer 占主导地位。** 除非警告分解清楚地显示否则立即开始策略 C。在批量 JSON 修复后，使用策略 A–B 处理剩余警告。仅作为最后手段使用策略 D。

### 步骤 4：迭代修复警告（从最内层开始）

从**最内层**的反射调用开始向外工作。每个修复可能会级联新的警告到调用者。

**保持警告驱动。** 对于每个警告，仅打开编译器报告的文件和行，识别模式，应用下面的匹配修复配方，然后继续。不要扫描代码库以寻找相似的模式或尝试理解完整架构——修复编译器告诉你的内容，立即重新构建，并让新的警告指导下一个更改。修复一小批警告（5-10 个），然后立即重新构建以检查进度。

**使用子代理（如果可用）。** 如果你可以在 `task` 工具中启动子代理，请并行派遣**多个子代理**来同时编辑不同的文件。保持主循环专注于构建、解析警告和派遣——将实际文件编辑委托给子代理。对于批量 JSON 更新，给每个子代理 5-10 个文件在一个提示中更新。**在 2 次构建修复周期后，将所有剩余文件编辑并行派遣给子代理——不要继续按顺序修复文件。** 示例：

> 更新这些文件以使用源生成的 JSON：`src/Models/Resource.Serialization.cs`，`src/Models/Identity.Serialization.cs`，`src/Models/Plan.Serialization.cs`。在每个文件中，将 `JsonSerializer.Serialize(writer, value)` 替换为 `JsonSerializer.Serialize(writer, value, MyProjectJsonContext.Default.TypeName)` 并将 `JsonSerializer.Deserialize<T>(ref reader)` 替换为 `JsonSerializer.Deserialize(ref reader, MyProjectJsonContext.Default.TypeName)`。仅编辑 JsonSerializer 调用位置。

#### 策略 A：添加 `[DynamicallyAccessedMembers]`（推荐）

当方法使用反射在一个 `Type` 参数上时，注解参数以告诉修剪器需要哪些成员：

```csharp
using System.Diagnostics.CodeAnalysis;

// 之前（警告 IL2070）：
void Process(Type t) {
    var method = t.GetMethod("Foo");  // 修剪器无法验证
}

// 之后（干净）：
void Process([DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.PublicMethods)] Type t) {
    var method = t.GetMethod("Foo");  // 修剪器保留公共方法
}
```

当你注解一个参数时，**所有调用者**现在必须传递正确注解的类型。这级联向外——跟随每个调用者并根据需要注解或重构。**调用者的注解必须至少包括与被调用者相同的成员类型。** 如果被调用者需要 `PublicConstructors | NonPublicConstructors`，调用者必须指定相同或超集——使用 `NonPublicConstructors` 只会产生 IL2091。

#### 策略 B：重构以保留注解流

当注解流因装箱（将 `Type` 存储在 `object`、`object[]` 或无类型的集合中）而被破坏时，**重构**以直接传递 `Type`：

```csharp
// 破坏：Type 装箱到 object[]，注解丢失
void Process(object[] args) {
    Type t = (Type)args[0];  // IL2072：通过装箱丢失注解
    Evaluate(t, ...);
}

// 修复：将 Type 作为单独的、注解的参数传递
void Process(
    object[] args,
    [DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.PublicMethods)] Type calleeType,
    ...) {
    Evaluate(calleeType, ...);  // 注解流清晰
}
```

破坏注解流并如何修复的常见模式：
- **object[] 参数包**：将 `Type` 提取到专用的注解参数中
- **字典/列表存储**：使用带注解的注解类型字段
- **接口间接**：向接口方法的参数添加注解
- **带装箱获取器的属性**：注解属性的返回类型

#### 策略 C：源生成的 JSON 序列化（批量修复）

当大多数警告来自 `JsonSerializer.Serialize`/`Deserialize` 时，这是一个单一机械的修复，可以批量应用：

1. **收集受影响的类型**——grep 所有 `JsonSerializer.Serialize` 和 `JsonSerializer.Deserialize` 调用位置。提取正在序列化的类型（`Deserialize<T>` 中的 `<T>`，或 `Serialize` 中对象的运行时类型）。

2. **创建一个 `JsonSerializerContext`**，带有 `[JsonSerializable]` 对于找到的每个类型。**跳过来自外部包的类型**（例如，`ResponseError` 来自 `Azure.Core`）——它们不会为类型源生成，因为你不拥有这些类型。单独处理外部类型，通过 Gotcha #1 下方。

```csharp
[JsonSerializerContext]
[JsonSerializable(typeof(ManagedServiceIdentity))]
[JsonSerializable(typeof(SystemData))]
// ... 每个你拥有的类型一个属性
// 不要添加来自外部包的类型（例如，ResponseError）
internal partial class MyProjectJsonContext : JsonSerializerContext { }
```

3. **批量更新所有调用位置**——不要逐个读取文件。机械地应用模式：
   - `JsonSerializer.Serialize(obj)` → `JsonSerializer.Serialize(obj, MyProjectJsonContext.Default.TypeName)`
   - `JsonSerializer.Deserialize<T>(json)` → `JsonSerializer.Deserialize(json, MyProjectJsonContext.Default.TypeName)`

   找到并更新所有匹配文件一次：
   ```bash
   # 查找包含 JsonSerializer 调用的所有文件
   grep -rl 'JsonSerializer\.\(Serialize\|Deserialize\)' src/ --include='*.cs'
   ```
   然后使用顺序 `edit` 调用来将相同的转换应用于每个匹配文件。**不要使用 `sed` 来处理 C# 代码**——泛型如 `Deserialize<T>()` 有尖括号和嵌套括号，sed 会破坏它们。

4. **构建一次**以验证。剩余的警告将是非序列化问题——使用策略 A–B 或 D 处理。

#### 策略 D：`[RequiresUnreferencedCode]`（最后手段）

当一个方法根本需要任意反射，而无法静态描述时：

```csharp
[RequiresUnreferencedCode("使用 Assembly.Load 按名称加载插件")]
public void LoadPlugin(string assemblyName) {
    var asm = Assembly.Load(assemblyName);
    // ...
}
```

这传播到调用者——它们也必须用 `[RequiresUnreferencedCode]` 注解。谨慎使用；它标记整个调用链为修剪不兼容。

### 步骤 5：重新构建并重复

每次修复一小批警告（5-10 个）后，使用 `--no-incremental` 重新构建并检查新警告。**不要尝试在重新构建之前修复所有警告**——频繁重新构建可以尽早捕获错误并揭示级联警告。修复会级联——注解一个内部方法可能会在其调用者中暴露警告。重复直到 `0 Warning(s)`。

### 步骤 6：验证所有 TFM

构建所有目标框架以确保：
- **net8.0+ TFM 上 0 IL 警告**
- **没有 NETSDK1210 警告**（`IsAotCompatible` 条件处理此问题）
- **较旧 TFM（netstandard2.0、net472 等）上的干净构建**

```bash
dotnet build <project.csproj>  # 构建所有 TFM
```

## 停止信号

- **不要分析超过 2-3 个代表文件每个警告模式。** 确定模式的修复后，无需读取每个文件即可将其应用于所有匹配文件。
- **在第一次构建后开始修复。** 不要进行第二次分析传递——立即开始实施修复最常见的警告模式，在步骤 3 筛选后。
- 在 net8.0+ TFM 上实现 **0 IL 警告** 后停止。不要优化或重构已经干净的注解。
- 如果警告需要**架构重构**超出注解流修复（例如，替换整个序列化层），记录它并停止——不要重写大型子系统。
- 限制为**3 次构建修复迭代**每个警告。如果注解流在 3 次尝试后无法解决，则升级到 `[RequiresUnreferencedCode]`。
- 不要追逐**第三方依赖项**中你无法修改的警告。记录它们并继续。
- 如果用户提出了范围问题（例如，“修复此文件的警告”），不要扩展到整个项目。

## 兼容旧 TFM 的 Polyfills

对于包含 netstandard2.0 或 net472 的多目标项目，您需要 `DynamicallyAccessedMembersAttribute` 和相关类型的 polyfills。参见 [references/polyfills.md](references/polyfills.md)。

## 常见陷阱

1. **没有 AOT 安全序列化的外部类型**：当类型来自你无法修改的依赖项（例如，`ResponseError` 来自 `Azure.Core`）并且它缺少源生成序列器时，`Options.GetConverter<T>()` 基于反射并会产生 IL 警告。首先检查类型是否实现 `IJsonModel<T>`（Azure SDK 中常见）——如果是，则完全绕过 `JsonSerializer`：

```csharp
// 之前（IL2026 — JsonSerializer 使用反射）：
JsonSerializer.Serialize(writer, errorValue);

// 之后（AOT 安全 — 直接使用 IJsonModel）：
((IJsonModel<ResponseError>)errorValue).Write(writer, ModelReaderWriterOptions.Json);

// 对于反序列化：
var error = ((IJsonModel<ResponseError>)new ResponseError()).Create(ref reader, ModelReaderWriterOptions.Json);
```

**不要**将外部类型添加到你的 `JsonSerializerContext`——它不会为类型源生成，因为你没有拥有这些类型。如果类型没有实现 `IJsonModel<T>`，编写一个具有手动 `Utf8JsonReader`/`Utf8JsonWriter` 逻辑的自定义 `JsonConverter<T>` 并通过 `[JsonSourceGenerationOptions]` 在你的上下文中注册它。

2. **序列化库**：大多数基于反射的序列化器（例如，`Newtonsoft.Json`、`XmlSerializer`）不是 AOT 兼容的。迁移到基于源生成的序列化器，例如 `System.Text.Json` 与 `JsonSerializerContext`。如果迁移不可行，请用 `[RequiresUnreferencedCode]` 标记序列化调用位置。

3. **共享项目 / projitems**：当通过 `<Import>` 在多个项目之间共享源时，添加到共享代码的注解会影响所有消费项目。验证所有消费者是否仍然干净构建。

## 参考

[限制](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/?tabs=windows%2Cnet8#limitations-of-native-aot-deployment)
[概念：理解修剪](https://learn.microsoft.com/en-us/dotnet/core/deploying/trimming/trimming-concepts)
[如何：trim 兼容](https://learn.microsoft.com/en-us/dotnet/core/deploying/trimming/fixing-warnings)

## 检查清单

- [ ] 在 .csproj 中添加 `<IsAotCompatible>` 带有 TFM 条件
- [ ] 使用 AOT 分析器启用构建（net8.0+ TFM）
- [ ] 通过注解或重构修复所有 IL 警告
- [ ] 未使用任何 IL 警告的 `#pragma warning disable` 或 `[UnconditionalSuppressMessage]`
- [ ] 如果需要，存在较旧 TFM 的 polyfills
- [ ] 所有目标框架构建时 0 警告
- [ ] 验证共享/链接源不会破坏兄弟项目
