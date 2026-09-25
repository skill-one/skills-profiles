# 将生成的文件包含到您的构建中

## 概述

构建过程中生成的文件通常会被构建过程忽略。这会导致一些令人困惑的结果，例如：
- 生成的文件没有被包含在输出目录中
- 生成的源文件没有被编译
- 通配符没有捕获构建过程中创建的文件

这发生的原因是MSBuild的构建阶段的工作方式。

## 快速要点

对于构建过程中生成的代码文件 - 我们需要将这些文件添加到生成这些文件的目标的`Compile`和`FileWrites`项组中：

```xml
  <ItemGroup>
    <Compile Include="$(GeneratedFilePath)" />
    <FileWrites Include="$(GeneratedFilePath)" />
  </ItemGroup>
```

生成文件的`目标`应该在`CoreCompile`和`BeforeCompile`目标之前被挂钩 - `BeforeTargets="CoreCompile;BeforeCompile"`

## 生成的文件被忽略的原因

有关详细解释，请参阅[MSBuild如何构建项目](https://docs.microsoft.com/visualstudio/msbuild/build-process-overview)。

### 评估阶段

MSBuild读取您的项目，导入所有内容，创建属性，展开项的通配符**在目标之外**，并设置构建过程。

### 执行阶段

MSBuild使用提供的属性和项运行目标和任务来执行构建。

**关键要点**：执行阶段生成的文件在评估阶段不存在，因此它们没有被找到。这特别影响默认情况下被通配符捕获的文件，例如源文件（`.cs`）。

## 解决方案：手动添加生成的文件

当构建过程中生成文件时，手动将它们添加到构建过程中。方法取决于正在生成的文件类型。

### 使用`$(IntermediateOutputPath)`作为生成文件位置

始终使用`$(IntermediateOutputPath)`作为生成文件的基本目录。**不要**硬编码`obj\`或手动构造中间路径（例如，`obj\$(Configuration)\$(TargetFramework)\`）。中间输出路径可以在某些构建配置中重定向到不同的位置（例如，共享输出目录，CI环境）。使用`$(IntermediateOutputPath)`确保您的目标无论实际路径如何都能正常工作。

### 始终将生成的文件添加到`FileWrites`

每个生成的文件都应该添加到`FileWrites`项组中。这确保了MSBuild的`Clean`目标可以正确删除您的生成文件。没有这个，生成的文件会随着构建累积为过时的工件。

```xml
<ItemGroup>
  <FileWrites Include="$(IntermediateOutputPath)my-generated-file.xyz" />
</ItemGroup>
```

### 基本模式（非代码文件）

对于需要复制到输出的生成文件（配置文件，数据文件等），在`BeforeBuild`之前将它们添加到`Content`或`None`项：

```xml
<Target Name="IncludeGeneratedFiles" BeforeTargets="BeforeBuild">
  
  <!-- 您生成文件的逻辑放在这里 -->

  <ItemGroup>
    <None Include="$(IntermediateOutputPath)my-generated-file.xyz" CopyToOutputDirectory="PreserveNewest"/>
    
    <!-- 使用通配符捕获特定类型的所有文件 -->
    <None Include="$(IntermediateOutputPath)generated\*.xyz" CopyToOutputDirectory="PreserveNewest"/>

    <!-- 注册生成文件以进行正确的清理 -->
    <FileWrites Include="$(IntermediateOutputPath)my-generated-file.xyz" />
    <FileWrites Include="$(IntermediateOutputPath)generated\*.xyz" />
  </ItemGroup>
</Target>
```

### 对于生成的源文件（需要编译的代码）

如果您正在生成需要编译的`.cs`文件，请使用**`BeforeTargets="CoreCompile;BeforeCompile"`**。这是添加`Compile`项的正确时间——它运行得足够晚，以便文件生成已经发生，但在编译器运行之前。使用`BeforeBuild`对于某些场景来说太早了，并且可能无法可靠地与所有SDK功能一起使用。

```xml
<Target Name="IncludeGeneratedSourceFiles" BeforeTargets="CoreCompile;BeforeCompile">
  <PropertyGroup>
    <GeneratedCodeDir>$(IntermediateOutputPath)Generated\</GeneratedCodeDir>
    <GeneratedFilePath>$(GeneratedCodeDir)MyGeneratedFile.cs</GeneratedFilePath>
  </PropertyGroup>

  <MakeDir Directories="$(GeneratedCodeDir)" />

  <!-- 您生成.cs文件的逻辑放在这里 -->

  <ItemGroup>
    <Compile Include="$(GeneratedFilePath)" />
    <FileWrites Include="$(GeneratedFilePath)" />
  </ItemGroup>
</Target>
```

注意：指定`CoreCompile`和`BeforeCompile`都确保目标在第一个目标之前运行，无论构建中的自定义情况如何，都能提供稳健的排序。

## 目标时间

根据正在生成的文件类型选择`BeforeTargets`值：

- **`BeforeTargets="BeforeBuild"`** — 对于添加到`None`或`Content`的非代码文件。对于复制到输出的场景来说运行得足够早。
- **`BeforeTargets="CoreCompile;BeforeCompile"`** — 对于添加到`Compile`的生成源文件。确保在编译器运行之前包含文件。
- **`BeforeTargets="AssignTargetPaths"`** — 在`None`和`Content`项（以及其他项）转换为新项之前的“最终停止”。如果`BeforeBuild`太早，则用作后备。

## 通配符行为

通配符的行为取决于**通配符何时发生**：

| 通配符位置 | 捕获的文件 |
|---------------|----------------|
| 目标之外 | 仅在评估阶段（构建开始之前）可见的文件 |
| 目标之内 | 目标运行时可见的文件（如果时间正确，可以捕获生成的文件） |

这就是为什么解决方案将`<ItemGroup>`放在`<Target>`内的原因——通配符在执行阶段运行时生成文件存在。

## 相关链接

- [MSBuild如何构建项目](https://docs.microsoft.com/visualstudio/msbuild/build-process-overview)
- [评估阶段](https://docs.microsoft.com/visualstudio/msbuild/build-process-overview#evaluation-phase)
- [执行阶段](https://docs.microsoft.com/visualstudio/msbuild/build-process-overview#execution-phase)
- [常见项类型](https://docs.microsoft.com/visualstudio/msbuild/common-msbuild-project-items)
- [SDK如何默认导入项](https://github.com/dotnet/sdk/blob/main/src/Tasks/Microsoft.NET.Build.Tasks/targets/Microsoft.NET.Sdk.DefaultItems.props)
- [官方文档：处理生成的文件](https://learn.microsoft.com/visualstudio/msbuild/customize-your-build#handle-generated-files)
