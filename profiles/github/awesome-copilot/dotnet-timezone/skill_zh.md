# .NET 时区

使用生产安全指南和可直接复制粘贴的代码片段解决 .NET 和 C# 代码中的时区问题。

## 选择正确的路径

首先确定请求类型：

- 地址或位置查询
- 时区 ID 查询
- UTC/本地转换
- 跨平台时区兼容性
- 调度或夏令时处理
- API 或持久化设计

如果库不明确，跨平台工作默认使用 `TimeZoneConverter`。如果场景涉及周期性调度或严格的夏令时规则，优先选择 `NodaTime`。

## 解析地址和位置

如果用户提供地址、城市、地区、国家或包含地名文档：

1. 从输入中提取每个位置。
2. 查看 `references/timezone-index.md` 获取常见的 Windows 和 IANA 映射。
3. 如果精确位置未列出，根据地理信息推断正确的 IANA 时区，然后将其映射到 Windows ID。
4. 返回两个 ID 和一个可直接使用的 C# 示例。

针对每个解析的位置，提供：

```text
位置: <解析出的地点>
Windows ID: <windows id>
IANA ID: <iana id>
UTC 偏移: <标准偏移和夏令时偏移（适用时）>
夏令时: <是/否>
```

然后包含跨平台代码片段，例如：

```csharp
using TimeZoneConverter;

TimeZoneInfo tz = TZConvert.GetTimeZoneInfo("Asia/Colombo");
DateTime local = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, tz);
```

如果存在多个位置，为每个位置包含一个代码块，然后提供一个多时区组合代码片段。

如果位置不明确，列出可能的时区匹配项，并要求用户选择正确的一项。

## 查询时区 ID

使用 `references/timezone-index.md` 进行 Windows 到 IANA 的映射。

始终提供两种格式：

- Windows ID 用于 `TimeZoneInfo.FindSystemTimeZoneById()` 在 Windows 上
- IANA ID 用于 Linux、容器、`NodaTime` 和 `TimeZoneConverter`

## 生成代码

使用 `references/code-patterns.md` 并选择最符合的简单模式：

- 模式 1: `TimeZoneInfo` 仅用于 Windows 代码
- 模式 2: `TimeZoneConverter` 用于跨平台转换
- 模式 3: `NodaTime` 用于严格的时区计算和夏令时敏感的调度
- 模式 4: `DateTimeOffset` 用于 API 和数据传输
- 模式 5: ASP.NET Core 持久化和展示
- 模式 6: 周期性任务和调度器
- 模式 7: 模糊和无效的夏令时时间戳

推荐第三方库时，始终包含包指导。

## 警惕常见陷阱

适用时提及相关警告：

- `TimeZoneInfo.FindSystemTimeZoneById()` 对时区 ID 是平台特定的。
- 避免将 `DateTime.Now` 存储在数据库中，应存储 UTC 时间。
- 将 `DateTimeKind.Unspecified` 视为潜在错误，除非是故意输入。
- 夏令时转换可能跳过或重复本地时间。
- Azure Windows 和 Azure Linux 环境可能期望不同的时区 ID 格式。

## 响应结构

针对地址和位置请求：

1. 为每个位置返回解析的时区代码块。
2. 用一句话说明推荐实现。
3. 包含可直接复制粘贴的 C# 代码片段。

针对代码和架构请求：

1. 用一句话说明推荐方法。
2. 如相关，提供时区 ID。
3. 包含最小可运行代码片段。
4. 如有必要，提及包要求。
5. 如有重要，添加一个陷阱警告。

保持响应简洁，代码优先。

## 参考文献

- `references/timezone-index.md`: 常见 Windows 和 IANA 时区映射
- `references/code-patterns.md`: 可直接使用的 .NET 时区模式
