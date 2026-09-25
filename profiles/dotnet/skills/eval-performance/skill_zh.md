# 诊断 MSBuild 评估性能

评估是 MSBuild 在任何目标运行*之前*所执行的工作——读取项目文件、处理导入、展开通配符。这项技能有助于您**发现和确认**评估瓶颈。先进行测量；只有当测量证明改变是合理时，才建议进行变更。

## 在更改任何内容之前确认问题

仅在评估*可量化*为瓶颈时才介入。以下情况不要采取行动：

- **缓慢发生在编译或目标执行期间，而不是评估期间。**
  这不是评估问题——请使用 `build-perf-diagnostics`。
- **抱怨“重建过多”/增量构建。** 请使用 `incremental-build`。
- **没有测量数据。** 如果没有 binlog 或时间摘要显示评估缓慢，请先收集数据（见下文）。不要根据阅读项目文件进行猜测。
- **以下模式出现，但评估已经很快。** 广泛的通配符、深层的导入或 `EnableDefaultItems` 只有在数据显示它们消耗实际时间时才值得标记。评估快速的项目无需更改。

当模式存在但未测量时，**将其作为观察结果报告并让用户决定**——不要为了匹配“最佳实践”而重写正常的工作配置，除非有证据表明它消耗了可衡量的评估时间。优先选择最小化、最精确的变更；首次不要禁用 SDK 默认值。

## MSBuild 评估阶段

有关 MSBuild 评估和执行模型的全面概述，请参阅 [构建过程概述](https://learn.microsoft.com/en-us/visualstudio/msbuild/build-process-overview)。

1. **初始属性**：环境变量、全局属性、保留属性
2. **导入和属性评估**：处理 `<Import>`，自上而下评估 `<PropertyGroup>`
3. **项定义评估**：`<ItemDefinitionGroup>` 元数据默认值
4. **项评估**：`<ItemGroup>` 与 `Include`、`Remove`、`Update`、通配符展开
5. **UsingTask 评估**：注册自定义任务

关键洞察：评估发生在任何目标运行*之前*。评估缓慢 = 即使不需要编译，构建启动也会变慢。

## 诊断评估性能

### 主要：binlog MCP（推荐）

使用**binlog MCP 服务器**（`Microsoft.AITools.BinlogMcp`，在 `binlog` MCP 命名空间下暴露）来分析评估性能：

1. 使用评估工具列出所有评估及其持续时间
2. 使用 `evaluation_global_properties` 检查具有不同全局属性的多次评估
3. 使用 `evaluation_properties` 检查特定项目+TFM 的已评估属性
4. 使用导入工具分析导入链的深度和结构
5. 使用属性工具检查昂贵的属性函数评估

### 备用：文本日志重放和预处理（当 MCP 不可用时）

### 使用 binlog

1. 重放 binlog：`dotnet msbuild build.binlog -noconlog -fl -flp:v=diag;logfile=full.log`
2. 搜索评估事件：`grep -i 'Evaluation started\|Evaluation finished' full.log`
3. 同一项目多次评估 = 过度构建
4. 查找“项目评估开始/结束”消息及其时间戳

### 使用 /pp（预处理）

- `dotnet msbuild -pp:full.xml MyProject.csproj`
- 显示完全展开的项目，所有导入都内联
- 用于理解：导入了什么、导入深度、总内容量
- 预处理输出很大（>10K 行）= 评估沉重

### 使用 /clp:PerformanceSummary

- 添加到构建命令以进行时间分解
- 将评估时间与目标/任务执行时间分开显示

## 昂贵的通配符模式

只有在测量显示项评估缓慢且通配符是原因时，才考虑这些补救措施；未遍历大型树的定制通配符是没问题的。

- 类似 `**/*.cs` 的通配符会遍历整个目录树
- 默认 SDK 通配符经过优化，但自定义通配符可能没有
- 问题：遍历 `node_modules/`、`.git/`、`bin/`、`obj/`——数百万个文件
- 补救：使用 `<DefaultItemExcludes>` 排除大型目录
- 补救：对通配符路径指定更具体：`src/**/*.cs` 而不是 `**/*.cs`
- 补救：仅作为最后手段使用 `<EnableDefaultItems>false</EnableDefaultItems>`（会丢失 SDK 默认值）——优先考虑上述两个选项
- 检查：在诊断日志中 grep 编译项 → 如果编译项包含意外文件，则通配符过于广泛

## 导入链分析

- 导入链过深（>20 层）会减慢评估
- 每个导入：文件 I/O + 解析 + 评估
- 常见原因：NuGet 包添加 .props/.targets、框架 SDK 导入、Directory.Build 链
- 诊断：`/pp` 输出 → 搜索 `<!-- Importing` 注释以查看导入树
- 补救（仅当链可量化为昂贵时）：尽可能减少传递式包导入，合并导入

## 多次评估

- 项目多次评估 = 浪费工作
- 常见原因：由具有不同全局属性的多个项目引用
- 每个独特的全局属性集 = 独立评估
- 诊断：`grep 'Evaluation started.*ProjectName' full.log` → 如果计数 > 1，请检查全局属性是否不同
- 修复：规范化全局属性，使用图构建（`/graph`）

## TreatAsLocalProperty

- 防止属性值通过 MSBuild 任务流向子项目
- 过度使用：声明许多 TreatAsLocalProperty 条目会增加评估开销
- 正确使用：仅在您确实需要覆盖继承属性时使用

## 属性函数成本

- 属性函数在评估期间执行
- 大多数函数很便宜（字符串操作）
- 昂贵：`$([System.IO.File]::ReadAllText(...))` 在评估期间——每次评估都会读取文件
- 昂贵：网络调用、重型计算
- 规则：属性函数应快速且无副作用

## 优化检查清单

- [ ] 检查预处理输出大小：`dotnet msbuild -pp:full.xml`
- [ ] 验证评估次数：每个项目每个 TFM 应为 1 次
- [ ] 从通配符中排除大型目录
- [ ] 在评估期间避免属性函数中的文件 I/O
- [ ] 最小化导入深度
- [ ] 使用图构建以减少冗余评估
- [ ] 检查不必要的 UsingTask 声明
