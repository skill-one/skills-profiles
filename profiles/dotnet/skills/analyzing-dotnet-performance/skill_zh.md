# .NET 性能模式

扫描 C#/.NET 代码中的性能反模式，并生成具有具体修复措施的优先级结果。模式来源于官方 .NET 性能博客系列，提炼为可操作的客户指导。

## 使用场景

- 审查 C#/.NET 代码以寻找性能优化机会
- 审计热点路径以查找资源密集型或效率低下的模式
- 在发布前对代码库进行系统性扫描以查找已知反模式
- 在手动性能审查后进行第二意见分析

## 不适用场景

- **算法复杂度分析** — 此技能针对 API 使用模式，而非算法设计
- **热点路径之外的代码** 没有性能要求 — 避免过早优化

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 源代码 | 是 | C# 文件、代码块或扫描的代码库路径 |
| 热点路径上下文 | 推荐使用 | 哪些代码路径对性能至关重要 |
| 目标框架 | 推荐使用 | .NET 版本（某些模式需要 .NET 8+） |
| 扫描深度 | 可选 | `critical-only`、`standard`（默认）或 `comprehensive` |

## 工作流程

### 第 1 步：加载关键参考

从包含此 `SKILL.md` 的目录中解析捆绑路径，而不是从用户的工位空间。首先加载此参考文件：

- `references/critical-patterns.md`

如果直接读取失败，请列出此技能的 `references/` 目录一次，并在列出显示预期文件时重试。不要使用工位文件或文本搜索来定位技能安装。

### 第 2 步：检测代码信号并选择主题配方

扫描代码以查找指示需要检查哪些模式类别的信号。在可用时使用来自关键参考的 `## Detection` 部分进行初始信号检测，并在第 3 步中使用内联配方。

检测到信号后，仅加载扫描深度选择的特定主题参考：

- `critical-only`：无附加参考（仅使用 `critical-patterns.md`）
- `standard`（默认）：加载与检测到的信号匹配的参考列表：
  - `references/async-patterns.md` — async/Task/ValueTask 信号
  - `references/memory-and-strings.md` — Span/Memory/string 分配信号
  - `references/regex-patterns.md` — Regex 信号
  - `references/collections-and-linq.md` — Dictionary/List/LINQ 信号
  - `references/io-and-serialization.md` — JsonSerializer/HttpClient/Stream 信号
  - `references/structural-patterns.md` — 总是加载（无论是否为未密封类进行检查）
- `comprehensive`：加载上述六个特定主题参考

对于覆盖报告，选择的参考是 `references/critical-patterns.md` 加上上述选择的特定主题参考。如果任何选择的参考在重试后仍然不可用，请使用第 3 步中的内联配方来补充缺失的覆盖。在最终报告中包含 `Reference coverage: reduced; unavailable: <paths>; used inline recipes for missing references.`，其中 `<paths>` 替换为所选参考的缺失相对路径。

使用加载的参考文件的 `## Detection` 部分和第 3 步中的内联配方来处理参考文件不可用的类别。

| 代码中的信号 | 主题 |
|-------------|------|
| `async`、`await`、`Task`、`ValueTask` | 异步模式 |
| `Span<`、`Memory<`、`stackalloc`、`ArrayPool`、`string.Substring`、`.Replace(`、`.ToLower()`、`+=` 在循环中、`params` | 内存和字符串 |
| `Regex`、`[GeneratedRegex]`、`Regex.Match`、`RegexOptions.Compiled` | Regex 模式 |
| `Dictionary<`、`List<`、`.ToList()`、`.Where(`、`.Select(`、LINQ 方法、`static readonly Dictionary<` | 集合和 LINQ |
| `JsonSerializer`、`HttpClient`、`Stream`、`FileStream` | I/O 和序列化 |

始终检查结构模式（未密封类），无论信号如何。

**扫描深度控制范围：**
- `critical-only`：仅关键模式（死锁、>10x 回归）
- `standard`（默认）：关键 + 检测到的主题模式
- `comprehensive`：所有模式类别

### 第 3 步：扫描和报告

**对于行数少于 500 行的文件，首先读取整个文件** — 你比运行单个 grep 配方更快地发现大多数模式。使用 grep 确认计数并捕获你可能遗漏的模式。

对于每个相关模式类别，运行以下检测配方。报告确切计数，而不是估计值。

**核心扫描配方**（当参考文件不可用时运行这些配方）：
```
# 字符串和内存
grep -n '\.IndexOf(\"' FILE                    # 缺失 StringComparison
grep -n '\.Substring(' FILE                    # Substring 分配
grep -En '\.(StartsWith|EndsWith|Contains)\s*\(' FILE  # 缺失 StringComparison
grep -n '\.ToLower()\|\.ToUpper()' FILE        # Culture-sensitive + 分配
grep -n '\.Replace(' FILE                      # Chained Replace 分配
grep -n 'params ' FILE                         # params 数组分配

# 集合和 LINQ
grep -n '\.Select\|\.Where\|\.OrderBy\|\.GroupBy' FILE  # 热点路径上的 LINQ
grep -n '\.All\|\.Any' FILE                    # 字符串/char 上的 LINQ
grep -n 'new Dictionary<\|new List<' FILE      # 每次调用分配
grep -n 'static readonly Dictionary<' FILE     # FrozenDictionary 候选

# Regex
grep -n 'RegexOptions.Compiled' FILE           # 编译 Regex 预算
grep -n 'new Regex(' FILE                      # 每次调用 Regex
grep -n 'GeneratedRegex' FILE                  # 积极：源码生成 Regex

# 结构
grep -n 'public class \|internal class ' FILE  # 未密封类
grep -n 'sealed class' FILE                    # 已经密封
grep -n ': IEquatable' FILE                    # 积极：结构体相等
```

**规则：**
- 运行检测到的模式类别的每个相关配方
- **在分类发现之前发出扫描执行清单** — 列出每个配方和命中计数
- **0 命中** 是有效的且有价值的（确认良好实践）
- 如果加载了参考文件，也运行它们的 `## Detection` 配方

**反向规则验证：** 对于缺失模式，始终计数两边并报告比率（例如，“N 个 M 个类是密封的”）。比率决定严重性 — 0/185 是系统性的，12/15 是一致性修复。

### 第 3b 步：跨文件一致性检查

如果在某个文件中找到一个优化模式，请检查同一目录、同一接口、同一基类的兄弟文件是否使用未优化的等效模式。标记为 🟡 中等，并附上优化文件作为证据。

### 第 3c 步：复合分配检查

运行扫描配方后，查找以下单行配方遗漏的多分配模式：

1. **分支 `.Replace()` 链：** 调用 `.Replace()` 跨多个 `if/else` 分支的方法 — 报告所有分支的总分配计数，而不仅仅是每行。
2. **跨方法链：** 当公共方法委托到另一个自身分配中间值的方法时（例如，A 调用 B 执行 3 个 Regex 替换，然后 A 调用 C），将整个链成本报告为一个发现。
3. **复合 `+=` 与嵌入分配调用：** 类似 `result += $"...{Foo().ToLower()}"` 的行是 2+ 分配（插值 + ToLower + 连接）— 标记复合成本，而不是 `.ToLower()`。
4. **`string.Format` 特定性：** 区分加载的资源格式字符串（不可修复）和编译时字面量格式字符串（可通过插值修复）。枚举可操作的站点。

### 第 4 步：分类和优先级排序发现

为每个发现分配严重性：

| 严重性 | 标准 | 行动 |
|-------|------|------|
| 🔴 **关键** | 死锁、崩溃、安全漏洞、>10x 回归 | 必须修复 |
| 🟡 **中等** | 2-10x 改进机会、热点路径的最佳实践 | 应在热点路径上修复 |
| ℹ️ **信息** | 模式适用但代码可能不在热点路径上 | 如果分析显示影响，请考虑 |

**优先级规则：**
1. 如果用户标识了热点路径代码，将其中所有发现的严重性提升到其最大严重性
2. 如果热点路径上下文未知，无条件报告 🔴 关键发现；报告 🟡 中等发现并附带注释：_“如果此代码在热点路径上，则影响重大”_
3. 永远不要在明显不敏感的代码上建议微优化

**基于规模的严重性升级：**
当相同的反模式出现在许多实例中时，升级严重性：
- 1-10 个相同反模式的实例 → 按模式的基本严重性报告
- 11-50 个实例 → 将 ℹ️ 信息模式升级为 🟡 中等
- 50+ 个实例 → 升级为 🟡 中等并提高优先级；标记为代码库范围的系统性问题

始终报告确切计数（来自扫描配方），而不是估计值或代理摘要。

### 第 5 步：生成发现

**保持发现简洁。** 每个发现是一个简短块 — 不是一篇论文。按严重性（🔴 → 🟡 → ℹ️）分组，而不是按文件。

按发现格式：

```
#### ID. 标题 (N 个实例)
**影响：** 一行影响声明
**文件：** file1.cs:L1, file2.cs:L2, ... (列出位置，不要构建表格)
**修复：** 一行描述更改（例如，“添加 `StringComparison.Ordinal` 参数”）
**注意事项：** 仅当不明显时（版本要求、正确性风险）
```

**简洁输出的规则：**
- **无 ❌/✅ 代码块** 用于简单的修复（添加关键字、参数或类型更改）。一行修复描述就足够了。
- **仅包含代码块** 用于非明显的转换（例如，用 foreach 循环替换 LINQ 链，或提升闭包）。
- **文件位置作为内联逗号分隔列表**，而不是表格。使用 `File.cs:L42` 格式。
- **无解释性散文** 超出影响行 — 严重性图标已经传达了紧急性。
- **合并相关发现** 共享相同修复（例如，所有 `.ToLower()` 调用在一个发现中，而不是按文件拆分）。
- **积极发现** 在项目符号列表中，而不是表格。每行一个模式：`✅ 模式 — 证据`。

以总结表格和免责声明结束：

```markdown
| 严重性 | 计数 | 主要问题 |
|-------|------|---------|
| 🔴 关键 | N | ... |
| 🟡 中等 | N | ... |
| ℹ️ 信息 | N | ... |

> ⚠️ **免责声明：** 这些结果由 AI 助手生成，且非确定性。发现可能包括误报、遗漏真实问题或建议针对您特定上下文不正确的更改。在将更改应用到生产代码之前，始终通过基准测试和人工审查来验证建议。
```

## 验证

在交付结果之前，验证：

- [ ] 所有关键模式都进行了检查（来自参考文件或内联配方）
- [ ] 仅在匹配信号检测时运行特定主题配方
- [ ] 每个发现都包含具体的代码修复
- [ ] 扫描执行清单完整（所有配方运行）
- [ ] 结尾包含总结表格

## 常见陷阱

| 陷阱 | 正确方法 |
|------|---------|
| 将每个 `Dictionary` 标记为需要 `FrozenDictionary` | 仅当字典构建后从未修改时才标记 |
| 在异步方法中建议 `Span<T>` | 在异步代码中使用 `Memory<T>`；`Span<T>` 仅在同步热点路径中使用 |
| 报告热点路径之外的 LINQ | 仅在识别的热点路径或紧循环中标记 LINQ；LINQ 在运行频率低的代码中可以接受。自 .NET 7 起，LINQ Min/Max/Sum/Average 已向量化 — 一刀切的 LINQ 禁令是错误的 |
| 在应用代码中建议 `ConfigureAwait(false)` | 仅适用于库代码；不是主要性能问题 |
| 在所有地方建议 `ValueTask` | 仅适用于热点路径且频繁同步完成的 |
| 在 DI 服务中标记 `new HttpClient()` | 检查是否已使用 `IHttpClientFactory` |
| 建议使用 `[GeneratedRegex]` 动态模式 | 仅在模式字符串是编译时字面量时标记 |
| 广泛建议使用 `CollectionsMarshal.AsSpan` | 仅适用于经过基准测试证据的超热点路径；增加复杂性和脆弱性 |
| 建议使用 `unsafe` 代码进行微优化 | 除了绝对必要外，避免 `unsafe` — 不要为不重要的微优化推荐它。安全的替代方案如 `Span<T>`、在安全上下文中使用 `stackalloc` 和 `ArrayPool` 覆盖了绝大多数性能需求 |
