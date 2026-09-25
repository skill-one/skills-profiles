# Burp 项目解析器

使用 burpsuite-project-file-parser 扩展搜索和提取 Burp Suite 项目文件中的数据。

## 使用场景

- 使用正则表达式模式搜索响应头或正文
- 从 Burp 项目中提取安全审计结果
- 导出代理历史记录或站点地图数据
- 分析 Burp 项目文件中捕获的 HTTP 流量

## 前置条件

此技能将解析委托给 Burp Suite Professional——它不会直接解析 .burp 文件。

**必需：**
1. **Burp Suite Professional** - 必须已安装 ([portswigger.net](https://portswigger.net/burp/pro))
2. **burpsuite-project-file-parser 扩展** - 提供命令行功能

**安装扩展：**
1. 从 [github.com/BuffaloWill/burpsuite-project-file-parser](https://github.com/BuffaloWill/burpsuite-project-file-parser) 下载
2. 在 Burp Suite 中：扩展器 → 扩展 → 添加
3. 选择下载的 JAR 文件

## 快速参考

使用包装脚本：
```bash
{baseDir}/scripts/burp-search.sh /path/to/project.burp [FLAGS]
```

该脚本使用环境变量以实现平台兼容性：
- `BURP_JAVA`：Java 可执行文件的路径
- `BURP_JAR`：burpsuite_pro.jar 的路径

**检查退出代码。空输出不是干净的结果。** Burp 会忽略它不认识的标志，因此如果没有解析器扩展，它会正常启动并丢弃查询——这看起来就像一个没有匹配的搜索。

| 退出码 | 含义 | 应该怎么办 |
|------|---------|------------|
| 0 | 产生输出 | 继续 |
| 1 | 使用不当，或缺少文件、Java 或 JAR | 阅读消息；修复路径 |
| 3 | 完全没有输出 | **不要报告“未找到”。** 空结果集和未加载的扩展在这里是无法区分的。运行下面的控制查询以区分它们 |
| 4 | 输出不是 JSON | 扩展未加载，Burp 忽略了标志。在信任任何结果之前安装它 |

除 0 外的任何值都表示搜索结果未经验证，并且基于此说“没有匹配的流量”是一个假阴性，报告为干净的结果。

### 解决退出码 3：控制查询

退出码 3 是常见情况——大多数范围狭窄的正则表达式确实匹配不到任何内容——因此需要你自己执行的解决方案。你有 `Bash` 和 `Read`；Burp 在这里以无头方式运行，所以没有扩展器选项卡可以打开，也没有 GUI 可以检查。重新运行相同的查询只会再次返回 3。

运行**控制查询**：选择范围足够广，如果解析器在工作，它必须返回行，针对同一个项目文件。使用子组件过滤器，而不是裸选择器——控制仍然是一个查询，上述规则对其适用不变。

```bash
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.request.headers | head -c 2000
```

`proxyHistory.request.headers` 是正确的控制，因为它范围广但有限：它涵盖了项目中的每条记录，每个记录小于 1KB。裸 `proxyHistory` 会回答相同的问题，并且有原因禁止它——一条带有正文的记录可以是兆字节，而 `head -n 1` 不会阻止这一点，它会完整地交付其中之一。

| 控制结果 | 含义 | 应该怎么办 |
|---|---|---|
| 标准输出上有行 | 解析器工作正常 | 你的较窄查询确实匹配不到任何内容。报告该结果 |
| 再次退出码 3 | 完全没有返回 | 要么扩展未加载，要么此项目不包含代理历史记录。检查你是否命名了正确的项目文件，并且它不为空，然后要求用户在 Burp Suite → 扩展器下确认 `burpsuite-project-file-parser` |
| 退出码 4 | Burp 启动并丢弃了标志 | 扩展未加载。这样说；不要报告流量 |

**在得出任何关于项目流量的结论之前运行控制查询。** 假设扩展已加载，这 exactly 是一个未经验证的空结果如何变成一张干净的健康证明——如果控制结果不确定，要求用户检查 GUI 是一个合法的答案。猜测是不对的。

**通过管道退出码不是你该读的。** 管道报告其最后一个命令的状态，并且这里几乎每个例子都以 `| jq`、`| head` 或 `| wc -cl` 结尾——所以 `$?` 是 `head` 的 0，而不是脚本的 3。两个可靠的信号：

- **stderr**，无论管道如何都能到达你这里。`Error: 解析器未产生输出。` 或 `Error: Burp 产生了输出，但不是 JSON 对象` 是答案；没有这样的块意味着运行正常。
- **`set -o pipefail`** 当你想得到代码本身，或者读取 `${PIPESTATUS[0]}`：

```bash
set -o pipefail
{baseDir}/scripts/burp-search.sh project.burp auditItems | jq -c 'select(.severity == "High")'
echo "exit: $?"
```

非 JSON 输出永远不会到达标准输出，所以下游的 `grep` 或 `jq` 无法匹配 Burp 启动横幅并将其误认为是数据。

有关平台配置的设置说明，请参阅 [Platform Configuration](#platform-configuration)。

## 子组件过滤器（使用这些）

**始终使用子组件过滤器，而不是完整转储。** 完整的 `proxyHistory` 或 `siteMap` 可能返回数十 GB 的数据。子组件过滤器只返回你需要的内容。

### 可用过滤器

| 过滤器 | 返回 | 典型大小 |
|--------|---------|--------------|
| `proxyHistory.request.headers` | 请求行 + 头部仅 | 小 (< 1KB/记录) |
| `proxyHistory.request.body` | 请求正文仅 | 可变 |
| `proxyHistory.response.headers` | 状态 + 头部仅 | 小 (< 1KB/记录) |
| `proxyHistory.response.body` | 响应正文仅 | **大 - 避免** |
| `siteMap.request.headers` | 站点地图的上述内容 | 小 |
| `siteMap.request.body` | | 可变 |
| `siteMap.response.headers` | | 小 |
| `siteMap.response.body` | | **大 - 避免** |

### 默认方法

**从头部开始，而不是正文：**

```bash
# 好 - 仅头部，安全可检索
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.request.headers | head -c 50000
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.response.headers | head -c 50000

# 坏 - 完整记录包括正文，可能是数十 GB
{baseDir}/scripts/burp-search.sh project.burp proxyHistory  # 永远不要这样做
```

**在审查头部后，仅针对特定 URL 检索正文，并且始终截断：**

```bash
# 1. 首先，从头部找到感兴趣的 URL
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.response.headers | \
  jq -r 'select(.headers | test("text/html")) | .url' | head -n 20

# 2. 然后使用目标正则表达式搜索正文 - 必须截断正文到 1000 个字符
{baseDir}/scripts/burp-search.sh project.burp "responseBody='.*specific-pattern.*'" | \
  head -n 10 | jq -c '.body = (.body[:1000] + "...[TRUNCATED]")'
```

**硬规则：正文内容超过 1000 个字符绝不能进入上下文。** 如果用户需要完整的正文内容，他们必须在 Burp Suite 的 UI 中查看。

## 正则表达式搜索操作

### 搜索响应头部
```bash
responseHeader='.*regex.*'
```
搜索所有响应头部。输出：`{"url":"...", "header":"..."}`

示例 - 查找服务器签名：
```bash
responseHeader='.*(nginx|Apache|Servlet).*' | head -c 50000
```

### 搜索响应正文
```bash
responseBody='.*regex.*'
```
**强制：始终将正文内容截断到最大 1000 个字符。** 响应正文每个可以是兆字节。

```bash
# 必需格式 - 始终截断 .body 字段
{baseDir}/scripts/burp-search.sh project.burp "responseBody='.*<form.*action.*'" | \
  head -n 10 | jq -c '.body = (.body[:1000] + "...[TRUNCATED]")'
```

**永远不要检索完整正文内容。** 如果你需要查看特定响应的更多信息，请要求用户在 Burp Suite 的 UI 中打开它。

## 其他操作

### 提取审计项
```bash
auditItems
```
返回所有安全发现。输出包括：名称、严重性、置信度、主机、端口、协议、URL。

**注意：** 审计项很小（没有正文）- 安全检索，使用 `head -n 100`。

### 导出代理历史记录（避免）
```bash
proxyHistory
```
**永远不要直接使用。** 使用子组件过滤器：
- `proxyHistory.request.headers`
- `proxyHistory.response.headers`

### 导出站点地图（避免）
```bash
siteMap
```
**永远不要直接使用。** 使用子组件过滤器。

## 输出限制（必需）

**关键：检索数据之前始终检查结果大小。** 一个广泛的搜索可以返回数千条记录，每条记录可能兆字节。这将溢出上下文窗口。

### 第 1 步：始终先检查大小

在任何搜索之前，检查记录数和字节大小：

```bash
# 检查记录数和总字节数 - 永远不要跳过这一步
{baseDir}/scripts/burp-search.sh project.burp proxyHistory | wc -cl
{baseDir}/scripts/burp-search.sh project.burp "responseHeader='.*Server.*'" | wc -cl
{baseDir}/scripts/burp-search.sh project.burp auditItems | wc -cl
```

`wc -cl` 输出显示：`<字节数> <行数>`（例如，`524288 42` 表示 512KB 跨 42 条记录）。

**解释结果 - 两者都必须通过：**

| 指标 | 安全 | 窄搜索 | 太宽 | 停止 |
|------|------|--------|------|------|
| **行数** | < 50 | 50-200 | 200+ | 1000+ |
| **字节数** | < 50KB | 50-200KB | 200KB+ | 1MB+ |

**超过 10MB 的单个响应在一条线上会显示高字节数，但只有 1 行 - 字节数检查会捕获这一点。**

`0 0` 来自 `wc -cl` 不是要采取的大小——脚本退出码 3 并且没有验证任何内容。管道隐藏了这一点，所以单独运行查询并读取退出码，然后再得出项目没有匹配流量的结论。

### 第 2 步：细化广泛搜索

如果计数/大小太高：

1. **使用子组件过滤器**（见上表）：
   ```bash
   # 不是：proxyHistory（数十 GB）
   # 使用：proxyHistory.request.headers（千字节）
   ```

2. **细化正则表达式模式：**
   ```bash
   # 太宽（匹配所有）：
   responseHeader='.*'

   # 更好 - 针对特定头部：
   responseHeader='.*X-Frame-Options.*'
   responseHeader='.*Content-Security-Policy.*'
   ```

3. **在检索前使用 jq 过滤：**
   ```bash
   # 仅获取特定内容类型
   {baseDir}/scripts/burp-search.sh project.burp proxyHistory.response.headers | \
     jq -c 'select(.url | test("/api/"))' | head -n 50
   ```

### 第 3 步：始终截断输出

即使在细化后，也始终通过截断：

```bash
# 始终使用 head -c 限制总字节数（最大 50KB）
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.request.headers | head -c 50000

# 对于正文搜索，截断每个 JSON 对象的正文字段：
{baseDir}/scripts/burp-search.sh project.burp "responseBody='pattern'" | \
  head -n 20 | jq -c '.body = (.body | if length > 1000 then .[:1000] + "...[TRUNCATED]" else . end)'

# 限制记录数和字节大小：
{baseDir}/scripts/burp-search.sh project.burp auditItems | head -n 50 | head -c 50000
```

**强制执行的硬限制：**
- `head -c 50000`（最大 50KB）对所有输出
- **截断 `.body` 字段到 1000 个字符 - 强制，没有例外**
  ```bash
  jq -c '.body = (.body[:1000] + "...[TRUNCATED]")'
  ```

**永远不要在没有计数之前运行这些，并且截断：**
- `proxyHistory` / `siteMap`（完整转储 - 始终使用子组件过滤器）
- `responseBody='...'` 搜索（正文可以是兆字节每个）
- 任何像 `.*` 或 `.+` 这样广泛的正则表达式

## 调查工作流程

1. **确定范围** - 你在寻找什么？（特定漏洞类型、端点、头部模式）

2. **首先搜索审计项** - 从 Burp 的发现开始：
   ```bash
   {baseDir}/scripts/burp-search.sh project.burp auditItems | jq 'select(.severity == "High")'
   ```

3. **检查置信度分数** - 过滤可操作的发现：
   ```bash
   ... | jq 'select(.confidence == "Certain" or .confidence == "Firm")'
   ```

4. **提取受影响的 URL** - 获取攻击面：
   ```bash
   ... | jq -r '.url' | sort -u
   ```

5. **搜索原始流量以获取上下文** - 检查实际的请求/响应：
   ```bash
   {baseDir}/scripts/burp-search.sh project.burp "responseBody='pattern'"
   ```

6. **手动验证** - Burp 发现只是指示，不是证明。验证每一个。

## 理解结果

### 严重性 vs 置信度

Burp 报告**严重性**（高/中/低）和**置信度**（确定/稳固/暂定）。在分类时使用两者：

| 组合 | 含义 |
|------|------|
| 高 + 确定 | 可能是真实漏洞，优先调查 |
| 高 + 暂定 | 通常是误报，验证后再报告 |
| 中 + 稳固 | 值得调查，可能需要手动验证 |

一个“高严重性，暂定置信度”的发现通常是误报。不要仅基于严重性报告发现。

### 当代理历史记录不完整时

代理历史记录只包含 Burp 捕获的内容。它可能由于以下原因缺少流量：
- **范围过滤器** 排除了域
- **拦截设置** 丢弃了请求
- **浏览器流量** 未通过 Burp 代理路由

如果你找不到预期的流量，请检查原始项目中的 Burp 范围和代理设置。

### HTTP 正文编码

响应正文可能是 gzip 压缩、分块或使用非 UTF8 编码。在纯文本上工作的正则表达式可能对编码响应静默失败。如果搜索返回的少于预期结果：
- 检查响应是否压缩
- 尝试更广泛的模式或首先搜索头部
- 使用 Burp 的 UI 检查原始与渲染的响应

## 拒绝的合理化

导致遗漏漏洞或误报的常见捷径：

| 短路 | 为什么不对 |
|------|------------|
| "这个正则表达式看起来不错" | 首先在样本数据上验证——编码和转义会导致静默失败 |
| "高严重性 = 必须修复" | 检查置信度分数；Burp 有误报 |
| "所有审计项都相关" | 根据实际威胁模型过滤；并非每个发现对每个应用程序都重要 |
| "代理历史记录是完整的" | 可能被 Burp 范围/拦截设置过滤；你只看到 Burp 捕获的内容 |
| "Burp 找到了，所以它是漏洞" | Burp 发现需要手动验证——它们指示潜在问题，而不是证明 |
| "搜索返回了空，所以流量不存在" | 首先检查退出码。退出码 3 意味着脚本无法区分空结果和未加载的扩展，退出码 4 意味着查询从未运行。只有 0 才使“未找到”成为关于项目而不是工具的陈述 |

## 输出格式

所有输出都是 JSON，每行一个对象。管道到 `jq` 以进行格式化：
```bash
{baseDir}/scripts/burp-search.sh project.burp auditItems | jq .
```

使用 grep 过滤：
```bash
{baseDir}/scripts/burp-search.sh project.burp auditItems | grep -i "sql injection"
```

## 示例

搜索 CORS 头部（带字节限制）：
```bash
{baseDir}/scripts/burp-search.sh project.burp "responseHeader='.*Access-Control.*'" | head -c 50000
```

获取所有高严重性发现（审计项很小，但仍然限制）：
```bash
{baseDir}/scripts/burp-search.sh project.burp auditItems | jq -c 'select(.severity == "High")' | head -n 100
```

仅提取代理历史记录中的请求 URL：
```bash
{baseDir}/scripts/burp-search.sh project.burp proxyHistory.request.headers | jq -r '.request.url' | head -n 200
```

搜索响应正文（必须截断正文到 1000 个字符）：
```bash
{baseDir}/scripts/burp-search.sh project.burp "responseBody='.*password.*'" | \
  head -n 10 | jq -c '.body = (.body[:1000] + "...[TRUNCATED]")'
```

## 平台配置

包装脚本需要两个环境变量来定位 Burp Suite 的捆绑 Java 和 JAR 文件。

### macOS

```bash
export BURP_JAVA="/Applications/Burp Suite Professional.app/Contents/Resources/jre.bundle/Contents/Home/bin/java"
export BURP_JAR="/Applications/Burp Suite Professional.app/Contents/Resources/app/burpsuite_pro.jar"
```

### Windows

```powershell
$env:BURP_JAVA = "C:\Program Files\BurpSuiteProfessional\jre\bin\java.exe"
$env:BURP_JAR = "C:\Program Files\BurpSuiteProfessional\burpsuite_pro.jar"
```

### Linux

```bash
export BURP_JAVA="/opt/BurpSuiteProfessional/jre/bin/java"
export BURP_JAR="/opt/BurpSuiteProfessional/burpsuite_pro.jar"
```

将这些导出添加到你的 shell 配置文件（`.bashrc`、`.zshrc` 等）以实现持久性。

### 手动调用

如果不使用包装脚本，直接调用：
```bash
"$BURP_JAVA" -jar -Djava.awt.headless=true "$BURP_JAR" \
  --project-file=/path/to/project.burp [FLAGS]
```
