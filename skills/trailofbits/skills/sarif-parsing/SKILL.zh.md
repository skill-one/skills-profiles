---
name: sarif-parsing
description: 解析并处理 CodeQL、Semgrep 等静态分析工具生成的 SARIF 文件。在执行 "解析 SARIF"、"读取扫描结果"、"聚合发现"、"去重警报" 或 "处理 SARIF 输出" 等操作时触发。支持 SARIF 数据的过滤、去重、格式转换以及 CI/CD 集成。不执行扫描操作——请使用 Semgrep 或 CodeQL 技能进行扫描。
---

# SARIF 解析最佳实践

您是一位 SARIF 解析专家。您的角色是帮助用户有效地读取、分析和处理静态分析工具生成的 SARIF 文件。

## 使用场景

在以下情况下使用此技能：
- 读取或解释 SARIF 格式的静态分析扫描结果
- 聚合来自多个安全工具的发现
- 去重或过滤安全警报
- 从 SARIF 文件中提取特定漏洞
- 将 SARIF 数据集成到 CI/CD 管道中
- 将 SARIF 输出转换为其他格式

## 不适用场景

不要在以下情况下使用此技能：
- 运行静态分析扫描（请使用 CodeQL 或 Semgrep 技能）
- 编写 CodeQL 或 Semgrep 规则（请使用相应的技能）
- 直接分析源代码（SARIF 用于处理现有的扫描结果）
- 在没有 SARIF 输入的情况下进行问题分类（请使用 variant-analysis 或 audit 技能）

## SARIF 结构概述

SARIF 2.1.0 是当前的 OASIS 标准。每个 SARIF 文件都有以下分层结构：

```
sarifLog
├── version: "2.1.0"
├── $schema: (可选，启用 IDE 验证)
└── runs[] (分析运行数组)
    ├── tool
    │   ├── driver
    │   │   ├── name (必需)
    │   │   ├── version
    │   │   └── rules[] (规则定义)
    │   └── extensions[] (插件)
    ├── results[] (发现结果)
    │   ├── ruleId
    │   ├── ruleIndex (指向 tool.driver.rules[] 的索引)
    │   ├── level (可选，当缺失时继承自规则)
    │   ├── message.text
    │   ├── locations[]
    │   │   └── physicalLocation
    │   │       ├── artifactLocation.uri
    │   │       └── region (startLine, startColumn 等)
    │   ├── fingerprints{}
    │   └── partialFingerprints{}
    └── artifacts[] (扫描文件元数据)
```

### 严重性不总是出现在结果中

`result.level` 是可选的。CodeQL 在每个结果中都省略它，并将严重性记录为 `defaultConfiguration.level`，结果会继承它。直接读取 `result.level`，即使 CodeQL 运行发现了很多错误，也会将其评分干净，这就是为什么严重性门禁在失败的仓库中退出状态为 0。

按照以下顺序解析严重性（SARIF 2.1.0 第 3.27.10 节）：

1.  `kind` 不是 `"fail"`（通过记录），所以是 `"none"`
2.  `result.level`，当存在时
3.  匹配的规则的 `defaultConfiguration.level`，将 `ruleIndex` 映射到 `runs[].tool.driver.rules[]`，或者当工具省略 `ruleIndex` 时，通过 `ruleId` 匹配 `rules[].id`
4.  `"warning"`，SARIF 默认值

此技能中的每个严重性查询都从此解析开始。在 jq 中，它是 [{baseDir}/resources/jq-queries.md]({baseDir}/resources/jq-queries.md) 中的 `LEVEL_FN` 定义；在 Python 中，它是 [{baseDir}/resources/sarif_helpers.py]({baseDir}/resources/sarif_helpers.py) 中的 `resolve_level(result, run)`。

### 为什么指纹很重要

没有稳定的指纹，您无法跨运行跟踪发现：

- **基线比较**："这是一个新发现还是我们之前见过？"
- **回归检测**："这个 PR 是否引入了新的漏洞？"
- **抑制**："在未来的运行中忽略这个已知的误报"

工具报告不同的路径（`/path/to/project/` 与 `/github/workspace/`），因此基于路径的匹配会失败。指纹对内容（代码片段、规则 ID、相对位置）进行哈希处理，以创建与环境无关的稳定标识符。

## 工具选择指南

| 使用场景 | 工具 | 安装/运行 |
|----------|------|--------------|
| 快速 CLI 查询 | jq | `brew install jq` / `apt install jq` |
| 简单 Python 脚本 | pysarif | `uv run --with pysarif python script.py` |
| 高级 Python 脚本 | sarif-tools | `uv run --with sarif-tools python script.py` |
| .NET 应用 | SARIF SDK | NuGet 包 |
| JavaScript/Node.js | sarif-js | npm 包 |
| Go 应用 | garif | `go get github.com/chavacava/garif` |
| 验证 | SARIF Validator | sarifweb.azurewebsites.net |

## 策略 1：使用 jq 快速分析

用于快速探索和一次性查询：

```bash
# 美化打印文件
jq '.' results.sarif

# 计算总发现数量
jq '[.runs[].results[]] | length' results.sarif

# 列出所有触发的规则 ID
jq '[.runs[].results[].ruleId] | unique' results.sarif

# 严重性解析，以下查询需要过滤级别，因此需要此解析。
# 参考资源/jq-queries.md 获取注释版本。
LEVEL_FN='
  def rule($run):
    . as $r
    | ($run.tool.driver.rules // []) as $rules
    | (if ($r.ruleIndex | type) == "number" and $r.ruleIndex >= 0
       then $rules[$r.ruleIndex] else null end)
      // first($rules[] | select(.id == $r.ruleId))
      // null;
  def level($run):
    . as $r
    | if ($r.kind // "fail") != "fail" then "none"
      else ($r.level // rule($run).defaultConfiguration.level // "warning") end;
'

# 提取错误
jq "$LEVEL_FN"'.runs[] as $run | $run.results[] | select(level($run) == "error")' results.sarif

# 获取带文件位置的发现结果
jq '.runs[].results[] | {
  rule: .ruleId,
  message: .message.text,
  file: .locations[0].physicalLocation.artifactLocation.uri,
  line: .locations[0].physicalLocation.region.startLine
}' results.sarif

# 按严重性过滤并获取每个规则的计数
jq "$LEVEL_FN"'[.runs[] as $run | $run.results[] | select(level($run) == "error")] | group_by(.ruleId) | map({rule: .[0].ruleId, count: length})' results.sarif

# 提取特定文件的发现结果
jq --arg file "src/auth.py" '.runs[].results[] | select(.locations[].physicalLocation.artifactLocation.uri | contains($file))' results.sarif
```

## 策略 2：使用 pysarif 的 Python

使用完整的对象模型进行程序化访问：

```python
from pysarif import load_from_file, save_to_file

# 加载 SARIF 文件
sarif = load_from_file("results.sarif")

# 遍历运行和结果
for run in sarif.runs:
    tool_name = run.tool.driver.name
    print(f"工具: {tool_name}")

    for result in run.results:
        # pysarif 会用 "warning" 填充缺失的 result.level，因此这里的 .level 不是规则继承的严重性：CodeQL 错误（结果没有 level，规则有严重性）会读取为 "warning"。使用策略 1 的 level() 或 resources/sarif_helpers.py 中的 resolve_level() 来门禁严重性，后者从规则中解析它。
        print(f"  {result.rule_id}: {result.message.text}")

        if result.locations:
            loc = result.locations[0].physical_location
            if loc and loc.artifact_location:
                print(f"    文件: {loc.artifact_location.uri}")
                if loc.region:
                    print(f"    行: {loc.region.start_line}")

# 保存修改后的 SARIF
save_to_file(sarif, "modified.sarif")
```

## 策略 3：使用 sarif-tools 的 Python

用于聚合、报告和 CI/CD 集成：

```python
from sarif import loader

# 加载单个文件
sarif_data = loader.load_sarif_file("results.sarif")

# 或加载多个文件
sarif_set = loader.load_sarif_files(["tool1.sarif", "tool2.sarif"])

# 获取摘要报告
report = sarif_data.get_report()

# 按严重性获取直方图
errors = report.get_issue_type_histogram_for_severity("error")
warnings = report.get_issue_type_histogram_for_severity("warning")

# 按严重性过滤。sarif-tools 返回原始结果字典，且结果的 level 可能存在于其规则中，因此应针对运行而不是读取 r["level"] 进行解析。
from sarif_helpers import extract_findings, filter_by_level, load_sarif

high_severity = filter_by_level(extract_findings(load_sarif("results.sarif")), "error")
```

**sarif-tools CLI 命令:**

```bash
# 发现摘要
sarif summary results.sarif

# 列出所有结果及详情
sarif ls results.sarif

# 按严重性获取结果
sarif ls --level error results.sarif

# 两个 SARIF 文件的差异（查找新发现/已修复问题）
sarif diff baseline.sarif current.sarif

# 转换为其他格式
sarif csv results.sarif > results.csv
sarif html results.sarif > report.html
```

## 策略 4：聚合多个 SARIF 文件

当组合来自多个工具的结果时：

```python
import json

from sarif_helpers import deduplicate, extract_findings

def aggregate_sarif_files(sarif_paths: list[str]) -> dict:
    """将多个 SARIF 文件合并为一个。"""
    aggregated = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": []
    }

    for path in sarif_paths:
        with open(path) as f:
            sarif = json.load(f)
            aggregated["runs"].extend(sarif.get("runs", []))

    return aggregated

unique = deduplicate(extract_findings(aggregate_sarif_files(["tool1.sarif", "tool2.sarif"])))
```

`deduplicate()` 优先使用工具提供的 `fingerprints` 或 `partialFingerprints`，如果它们不存在，则回退到哈希规则 ID、整个规范化路径、行和消息。保留目录在键中：同一行在 `auth/login.py` 和 `admin/login.py` 中的相同规则是两个发现，而仅使用基本名作为键会丢失其中一个。

## 策略 5：提取可操作数据

`resources/sarif_helpers.py` 使用标准库即可完成此操作。
`extract_findings()` 返回严重性已解析的 `Finding` 对象，`filter_by_level()`、`sort_by_severity()`、`deduplicate()` 和 `diff_findings()` 消费这些对象：

```python
from sarif_helpers import extract_findings, filter_by_level, load_sarif, sort_by_severity

findings = sort_by_severity(extract_findings(load_sarif("results.sarif")))
for f in filter_by_level(findings, "error"):
    print(f"{f.file_path}:{f.start_line} [{f.level}] {f.rule_id}: {f.message}")
```

编写自己的提取器时，严重性部分可能会无声地出错：

```python
def resolve_level(result: dict, run: dict) -> str:
    """结果的严重性：其 own level，否则其规则的 defaultConfiguration.level，否则 "warning"."""
    if result.get("kind", "fail") != "fail":
        return "none"
    if result.get("level"):
        return result["level"]

    rules = run.get("tool", {}).get("driver", {}).get("rules", [])
    index = result.get("ruleIndex")
    rule = rules[index] if isinstance(index, int) and 0 <= index < len(rules) else next(
        (r for r in rules if r.get("id") == result.get("ruleId")), {}
    )
    return rule.get("defaultConfiguration", {}).get("level") or "warning"
```

一些工具在结果中携带 `ruleIndex`，而另一些工具只携带 `ruleId`，因此解析器只采用一种方式会无声地返回默认值，适用于该种工具生成的所有结果。

## 常见陷阱和解决方案

### 1. 路径规范化问题

不同工具报告的路径不同（绝对路径、相对路径、URI 编码），因此 `file:///src/a%20b.py` 和 `src/a b.py` 可能是同一个文件。在比较或哈希任何内容之前，删除 `file://` 方案、百分比解码、相对于基本路径解析并规范化分隔符：`resources/sarif_helpers.py` 中的 `normalize_path()` 执行所有四项操作。

### 2. 跨运行指纹不匹配

如果：
- 文件路径在不同环境中不同
- 工具版本更改了指纹算法
- 代码被重新格式化（改变行号）

**解决方案：** 使用多种指纹策略：

```python
def compute_stable_fingerprint(result: dict, file_content: str = None) -> str:
    """计算环境无关的指纹。"""
    import hashlib

    components = [
        result.get("ruleId", ""),
        result.get("message", {}).get("text", "")[:100],  # 前 100 个字符
    ]

    # 如果可用，添加代码片段
    if file_content and result.get("locations"):
        region = result["locations"][0].get("physicalLocation", {}).get("region", {})
        if region.get("startLine"):
            lines = file_content.split("\n")
            line_idx = region["startLine"] - 1
            if 0 <= line_idx < len(lines):
                # 规范化空白
                components.append(lines[line_idx].strip())

    return hashlib.sha256("".join(components).encode()).hexdigest()[:16]
```

### 3. 缺失或不完整数据

SARIF 允许多个可选字段。始终使用防御性访问：

```python
def safe_get_location(result: dict) -> tuple[str, int]:
    """安全地从结果中提取文件和行号。"""
    try:
        loc = result.get("locations", [{}])[0]
        phys = loc.get("physicalLocation", {})
        file_path = phys.get("artifactLocation", {}).get("uri", "unknown")
        line = phys.get("region", {}).get("startLine", 0)
        return file_path, line
    except (IndexError, KeyError, TypeError):
        return "unknown", 0
```

### 4. 大文件性能

对于非常大的 SARIF 文件（100MB+）：

```python
import ijson  # 通过: uv run --with ijson 运行

def stream_results(sarif_path: str):
    """无需加载整个文件即可流式传输结果。"""
    with open(sarif_path, "rb") as f:
        # 流式传输结果数组
        for result in ijson.items(f, "runs.item.results.item"):
            yield result
```

### 5. 模式验证

在处理之前验证以捕获格式错误的文件：

```bash
# 使用 ajv-cli
npm install -g ajv-cli
ajv validate -s sarif-schema-2.1.0.json -d results.sarif

# 使用 Python jsonschema
uv run --with jsonschema python your_script.py   # 例如下面的函数
```

```python
from jsonschema import validate, ValidationError
import json

def validate_sarif(sarif_path: str, schema_path: str) -> bool:
    """根据模式验证 SARIF 文件。"""
    with open(sarif_path) as f:
        sarif = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)

    try:
        validate(sarif, schema)
        return True
    except ValidationError as e:
        print(f"验证错误: {e.message}")
        return False
```

## CI/CD 集成模式

### GitHub Actions

```yaml
- name: 上传 SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif

- name: 检查高严重性
  run: |
    # select(.level == "error") 在 CodeQL 输出中计数为零，CodeQL 在规则中记录严重性。解析 level 或在包含大量错误的仓库中通过门禁通过。
    HIGH_COUNT=$(jq '
      def rule($run):
        . as $r
        | ($run.tool.driver.rules // []) as $rules
        | (if ($r.ruleIndex | type) == "number" and $r.ruleIndex >= 0
           then $rules[$r.ruleIndex] else null end)
          // first($rules[] | select(.id == $r.ruleId))
          // null;
      def level($run):
        . as $r
        | if ($r.kind // "fail") != "fail" then "none"
          else ($r.level // rule($run).defaultConfiguration.level // "warning") end;
      [.runs[] as $run | $run.results[] | select(level($run) == "error")] | length
    ' results.sarif)
    if [ "$HIGH_COUNT" -gt 0 ]; then
      echo "发现 $HIGH_COUNT 个高严重性问题"
      exit 1
    fi
```

### 新问题失败

```python
from sarif import loader

def check_for_regressions(baseline: str, current: str) -> int:
    """返回不在基线中的新问题数量。"""
    baseline_data = loader.load_sarif_file(baseline)
    current_data = loader.load_sarif_file(current)

    baseline_fps = {get_fingerprint(r) for r in baseline_data.get_results()}
    new_issues = [r for r in current_data.get_results()
                  if get_fingerprint(r) not in baseline_fps]

    return len(new_issues)
```

## 关键原则

1. **先验证**：在处理之前检查 SARIF 结构
2. **解析严重性，永不读取 `result.level`**：它是可选的，CodeQL 总是省略它
3. **处理可选字段**：许多字段是可选的；使用防御性访问
4. **规范化路径**：工具报告的路径不同；尽早规范化
5. **明智地使用指纹**：结合多种策略以实现稳定的去重
6. **流式传输大文件**：使用 ijson 或类似工具处理 100MB+ 文件
7. **谨慎聚合**：合并文件时保留工具元数据

## 技能资源

对于现成的查询模板，请参阅 [{baseDir}/resources/jq-queries.md]({baseDir}/resources/jq-queries.md)：
- 40+ 用于常见 SARIF 操作的 jq 查询
- `LEVEL_FN` - 每个过滤查询都从其继承的严重性级别开始
- 严重性过滤、规则提取、聚合模式

对于 Python 工具，请参阅 [{baseDir}/resources/sarif_helpers.py]({baseDir}/resources/sarif_helpers.py)：
- `resolve_level()` - 从结果或规则继承的严重性
- `normalize_path()` - 处理工具特定的路径格式
- `compute_fingerprint()` - 规则、规范化路径、行和消息
- `deduplicate()` - 删除跨运行时的重复项

两个 SARIF 测试用例位于 [{baseDir}/resources/fixtures]({baseDir}/resources/fixtures) 中，一个仅规则具有严重性，另一个仅结果具有严重性。每个测试用例都包含恰好一个错误，因此可以在信任之前将其与已知答案进行比对。

## 参考链接

- [OASIS SARIF 2.1.0 规范](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Microsoft SARIF 教程](https://github.com/microsoft/sarif-tutorials)
- [SARIF SDK (.NET)](https://github.com/microsoft/sarif-sdk)
- [sarif-tools (Python)](https://github.com/microsoft/sarif-tools)
- [pysarif (Python)](https://github.com/Kjeld-P/pysarif)
- [GitHub SARIF 支持](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [SARIF 验证器](https://sarifweb.azurewebsites.net/)
