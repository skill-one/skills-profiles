# CodeQL 分析

支持的编程语言：Python、JavaScript/TypeScript、Go、Java/Kotlin、C/C++、C#、Ruby、Swift。

**技能资源**：参考文件和模板位于 `{baseDir}/references/` 和 `{baseDir}/workflows/`。

## 基本原则

1. **数据库质量不可妥协。** 能够构建的数据库并不一定就是好的——一个缓存的构建什么也提取不了，却报告成功。

2. **数据扩展可以捕捉 CodeQL 遗漏的内容。** Django、Spring 和 Express 项目仍然将数据库调用、请求解析和 shell 执行封装在项目特定的 API 中，而这些 API 没有被发布的模型所覆盖。

3. **显式套件引用防止静默查询丢弃。** 不要将包名传递给 `codeql database analyze`——每个包的 `defaultSuiteFile` 都会应用隐藏的过滤器，可能导致零结果。始终生成 `.qls`。

4. **零发现需要调查，而不是庆祝。** 这可能意味着提取质量差、缺少模型、包不正确或套件过滤。构建后运行 `{baseDir}/scripts/check_db_quality.py`，确认 `{baseDir}/scripts/verify_query_suite.py` 对正在使用的套件退出零（生成脚本会运行它，因此仅对重用或手动编辑的套件手动调用它），并在报告中说明两者都通过了。

5. **macOS Apple Silicon 需要对编译语言进行工作绕过。** 退出码 137 是 `arm64e`/`arm64` 不匹配，而不是构建失败。在回退到 `build-mode=none` 之前，尝试 Homebrew arm64 工具或罗塞塔。

6. **按步骤遵循工作流。** 每个阶段都会锁定下一个阶段；跳过质量评估或数据扩展会在结果中留下可见的差距。

## 每个 Bash 调用都是一个新的 Shell

Bash 调用之间没有任何内容传递：不是变量，不是数组，不是从 `build_log.sh` 源化的函数。以下每个使用值的块都必须在同一个块中重新建立它。工作流会回退到这里而不是重复它；它们所说明的是该地点的特定损坏，因为每个都不同且静默地失败：

- 失去的**函数**使 `run_logged` 退出 127，构建阶梯将其读取为失败的 方法并下移到 `--build-mode=none`，从未调用 CodeQL
- 失去的**数组**扩展为空，因此用户选择的所有 `--threat-model` 和 `--model-packs` 都会被丢弃，而最终报告仍然将它们列为已使用
- 在 `set -u` 下失去的**标量**会中止块，显示 `unbound variable`

## 输出目录

所有生成的文件（数据库、构建日志、诊断、扩展、结果）都存储在一个输出目录中。

- **如果用户在提示中指定了输出目录**，将其用作 `OUTPUT_DIR`。
- **如果没有指定**，默认为 `./static_analysis_codeql_1`。如果已存在，则增加到 `_2`、`_3` 等。

在这两种情况下，**始终使用 `mkdir -p` 创建目录**，然后再写入任何文件。

在运行此脚本之前，将 `USER_SPECIFIED_DIR` 设置为用户提示中的字面路径，或者将其留空以自动递增。否则不会分配它。

```bash
# 解析输出目录
USER_SPECIFIED_DIR="${USER_SPECIFIED_DIR:-}"   # 在这里替换用户的路径（如果有）
if [ -n "$USER_SPECIFIED_DIR" ]; then
  OUTPUT_DIR="$USER_SPECIFIED_DIR"
else
  BASE="static_analysis_codeql"
  N=1
  while [ -e "${BASE}_${N}" ]; do
    N=$((N + 1))
  done
  OUTPUT_DIR="${BASE}_${N}"
fi
mkdir -p "$OUTPUT_DIR"
```

输出目录在开始时解析一次，在工作流执行之前。所有工作流都会接收 `$OUTPUT_DIR` 并将其工件存储在那里：

```
$OUTPUT_DIR/
├── rulesets.txt                 # 选择的查询包（在步骤 3 后记录）
├── codeql.db/                   # CodeQL 数据库（包含 codeql-database.yml 的目录）
├── build.log                    # 构建日志
├── codeql-config.yml            # 排除配置（解释性语言）
├── diagnostics/                 # 诊断查询和 CSV 文件
├── extensions/                  # 数据扩展 YAML 文件
├── raw/                         # 未过滤的分析输出
│   ├── results.sarif
│   └── run-all.qls | important-only.qls
└── results/                     # 最终结果（过滤重要部分，为 run-all 复制）
    └── results.sarif
```

### 数据库发现

CodeQL 数据库由其目录中存在的 `codeql-database.yml` 标记文件标识。在搜索现有数据库时，**始终收集所有匹配项**——可能有多个来自先前运行或不同语言的数据库。

**发现命令。** `find_databases.sh` 每行打印一个数据库路径，过滤掉构建失败留下的标记文件。在构建数组**与选择它的同一块中**——每个 Bash 调用都是一个新 Shell，因此在此处构建的数组在下一个调用时为空，并且运行结束，因为没有数据库：

```bash
# 命令替换，不是 `done < <(...)`：进程替换会忽略脚本退出状态，因此“codeql 不在此 Shell 的 PATH 上”（退出 2）会作为空列表到达，并路由到“构建新数据库”，磁盘上还有三个好的数据库。
if ! DB_LIST=$("{baseDir}/scripts/find_databases.sh" "${OUTPUT_DIR:-.}" .); then
  echo "ERROR: 数据库发现失败——请查看上面的消息" >&2
  exit 1
fi

FOUND_DBS=()
while IFS= read -r db; do
  [ -n "$db" ] || continue
  FOUND_DBS+=("$db")
done <<<"$DB_LIST"

echo "发现 ${#FOUND_DBS[@]} 个现有数据库"

# 选择提示需要的元数据，在此处收集，而不是单独的块中：FOUND_DBS 在下一个 Bash 调用中消失，并且对不再存在的数组进行循环打印为空并报告成功。
for db in "${FOUND_DBS[@]}"; do
  CODEQL_LANG=$(codeql resolve database --format=json -- "$db" 2>/dev/null | jq -r '.languages[0]')
  CREATED=$(grep '^creationMetadata:' -A5 "$db/codeql-database.yml" 2>/dev/null | grep 'creationTime' | awk '{print $2}')
  echo "$db — 语言：$CODEQL_LANG，创建时间：$CREATED"
done
```

永远不要假设数据库命名为 `codeql.db`——通过其标记文件发现它。

**当发现多个数据库时**：使用 `AskUserQuestion` 让用户选择要使用的数据库，或从上面打印的语言和创建时间构建一个新数据库。`AskUserQuestion` 最多接受四个选项，因此如果有更多数据库，请提供三个最新的加上“构建新数据库”，并在提示文本中列出其余的。**如果用户明确说明要使用哪个数据库或构建一个新数据库，则跳过 `AskUserQuestion`。**

## 快速入门

对于常见情况（“扫描此代码库以查找漏洞”）：

```bash
# 验证 CodeQL 是否已安装。如果未安装，请停止——每个后续命令都会出现不太明确的错误，并且运行会浪费一个构建周期才说明原因。
if ! command -v codeql >/dev/null 2>&1; then
  echo "ERROR: codeql 未在 PATH 上找到。使用以下方式之一安装它：" >&2
  echo "  gh extension install github/gh-codeql   # 然后：gh codeql install-stub" >&2
  echo "  brew install --cask codeql" >&2
  echo "  https://github.com/github/codeql-action/releases  (codeql-bundle)" >&2
  exit 1
fi

# jq 解析 `codeql resolve database --format=json` 在下一步中。如果没有它，CODEQL_LANG 会为空，并且运行会继续针对错误的语言。
if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq 未在 PATH 上找到（brew install jq / apt install jq）" >&2
  exit 1
fi

# uv 运行两个保护脚本和两个套件生成器。在此处检查它，而不是在套件生成后检查，因为套件生成是在构建之后——否则没有 uv 的机器会花费整个构建时间才失败。
if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv 未在 PATH 上找到（https://docs.astral.sh/uv/getting-started/）" >&2
  exit 1
fi

codeql --version
```

然后使用上面 [输出目录](#output-directory) 中的块解析 `OUTPUT_DIR`——它会尊重用户指定的目录，而裸自动递增不会。

然后执行完整管道：**构建数据库 → 创建数据扩展 → 运行分析**，使用以下工作流。

## 拒绝的理由

这些捷径会导致遗漏发现。不要接受它们：

- **“security-extended 足够了”** —— 它是基准。始终检查 Trail of Bits 包和社区包是否适用于该语言。它们捕获了 `security-extended` 完全遗漏的类别。
- **“security-and-quality 是最广泛的套件”** —— `security-and-quality` 排除了所有 `experimental/` 查询路径。对于 run-all 模式，导入 `security-and-quality` 和 `security-experimental`。差异取决于语言，为 1–52 个查询。
- **“数据库构建了，所以它是好的”** —— 构建成功的数据库并不意味着它提取得很好。始终运行质量评估并检查文件计数与预期源文件是否一致。
- **“标准框架不需要数据扩展”** —— 即使 Django/Spring 应用也有 CodeQL 未建模的自定义包装器。跳过扩展意味着遗漏漏洞。
- **“build-mode=none 对编译语言可以”** —— 它会产生严重不完整分析。仅作为绝对最后的手段使用。在 macOS 上，先尝试 arm64 工具链工作绕过或罗塞塔。
- **“构建在 macOS 上失败，只需使用 build-mode=none”** —— 退出码 137 是由 `arm64e`/`arm64` 不匹配引起的，而不是根本性的构建失败。参见 [macos-arm64e-workaround.md](references/macos-arm64e-workaround.md)。
- **“没有发现意味着代码是安全的”** —— 运行 `check_db_quality.py` 和 `verify_query_suite.py` 并报告它们通过了。如果没有它们，零发现和提取了 nothing 的数据库是相同的输出。
- **“我将只运行默认套件”** / **“我将直接传递包名”** —— 每个包的 `defaultSuiteFile` 都会应用隐藏的过滤器，并且可以产生零结果。始终使用显式套件引用。
- **“我将把文件放在当前目录”** —— 所有生成的文件都必须放在 `$OUTPUT_DIR` 中。在工作目录中分散文件使清理变得不可能，并可能导致覆盖以前的运行。
- **“只需使用我找到的第一个数据库”** —— 可能有多个数据库存在于不同的语言或以前的运行中。当发现多个时，向用户展示所有选项。仅当用户已经指定要使用哪个数据库时才跳过提示。
- **“用户说‘扫描’，这意味着他们希望我选择一个数据库”** —— “扫描”不是数据库选择。如果存在多个数据库并且用户没有指定一个，请询问。

---

## 工作流选择

此技能有三个工作流。**一旦选择了工作流，就按步骤执行，不要跳过阶段。**

这些运行很漫长。数据库构建有四个回退方法，因此使用任务工具跟踪进度。根据运行决定哪些步骤值得跟踪。

| 工作流 | 目的 |
|----------|---------|
| [build-database](workflows/build-database.md) | 使用按顺序的构建方法创建 CodeQL 数据库 |
| [create-data-extensions](workflows/create-data-extensions.md) | 检测或生成项目 API 的数据扩展模型 |
| [run-analysis](workflows/run-analysis.md) | 选择规则集，执行查询，处理结果 |

### 无需人工干预的构建

此插件提供 `/static-analysis:codeql-build`，它端到端运行构建数据库步骤：检测语言和工具链，在 rungs 之间应用 [build-fixes.md](references/build-fixes.md) 中的修复，并执行质量门禁。

```
/static-analysis:codeql-build {"target": "/abs/path", "lang": "cpp"}
```

它什么也不问。每个方法失败，以及构建成功但低于质量阈值的数据库，都会作为状态返回——`no-method-succeeded` 和 `built-below-threshold`——供您在此处处理，因为剩余的提取器错误是否仅限于不需要分析的代码是一个判断，运行无法做出。

当构建是漫长且不确定的部分，并且您希望它被驱动到结论时使用它。当您想参与选择要尝试的方法，或当构建失败需要解释时手动执行 [build-database.md](workflows/build-database.md)。

### 自动检测逻辑

**如果用户明确指定了要做什么**（例如，“构建数据库”，“在 ./my-db 上运行分析”），则直接执行该工作流。**如果用户的提示已经清楚地表明了意图**（例如，“构建一个新数据库”，“分析 static_analysis_codeql_2 中的 codeql 数据库”，“从头开始运行完整扫描”），则不要调用 `AskUserQuestion` 进行数据库选择。

**“test”、“scan”、“analyze”或类似默认管道：** 使用上面 [数据库发现](#database-discovery) 中的命令发现现有数据库，然后决定。

| 条件 | 操作 |
|-----------|--------|
| 未发现数据库 | 解析新的 `$OUTPUT_DIR`，执行构建 → 扩展 → 分析（完整管道） |
| 发现一个数据库 | 使用 `AskUserQuestion`：重用它还是构建新数据库？ |
| 发现多个数据库 | 使用 `AskUserQuestion`，最多四个选项——参见 [数据库发现](#database-discovery) |
| 用户明确说明意图 | 跳过 `AskUserQuestion`，直接根据其指示操作 |

### 数据库选择提示

当发现现有数据库**并且用户没有明确指定要使用哪个数据库**时，通过 `AskUserQuestion` 在“现有 CodeQL 数据库”标题下展示它们。用上面收集的路径、语言和创建时间标记每个选项——`./static_analysis_codeql_1/codeql.db (语言：python，创建时间：2026-02-24)`——并将最后一个选项设置为“构建新数据库”。

选择后：
- **如果用户选择现有数据库**：将 `$OUTPUT_DIR` 设置为其父目录（或包含它的目录），将 `$DB_NAME` 设置为选定路径，然后继续扩展 → 分析。
- **如果用户选择“构建新”**：解析新的 `$OUTPUT_DIR`，执行构建 → 扩展 → 分析。

### 一般决策提示

如果数据库和工作流都不清楚，提供四个工作流通过 `AskUserQuestion`——完整扫描（推荐）、构建数据库、创建数据扩展、运行分析——命名发现的任何数据库和解析的 `$OUTPUT_DIR`。

---

## 参考索引

| 文件 | 内容 |
|------|---------|
| **脚本** | |
| [scripts/verify_query_suite.py](scripts/verify_query_suite.py) | 如果套件解析为零查询则失败的套件。生成脚本会运行它；仅对重用或手动编辑的套件手动调用它 |
| [scripts/check_db_quality.py](scripts/check_db_quality.py) | 如果数据库没有可分析的源则失败的数据库。每次构建后运行 |
| [scripts/build_log.sh](scripts/build_log.sh) | `log_step`/`run_logged` 辅助程序；在构建任何步骤之前源化 |
| [scripts/find_databases.sh](scripts/find_databases.sh) | 打印 `codeql resolve database` 接受的每个数据库，每行一个。在读取它的块中构建你的数组 |
| [scripts/generate_suite.sh](scripts/generate_suite.sh) | 写入 run-all 或 important-only `.qls` 并验证它解析为非零查询计数 |
| [references/macos-arm64e-workaround.md](references/macos-arm64e-workaround.md) | Apple Silicon 构建跟踪工作绕过 |
| [references/build-fixes.md](references/build-fixes.md) | 构建失败修复目录 |
| [references/quality-assessment.md](references/quality-assessment.md) | 数据库质量指标和改进 |
| [references/extension-yaml-format.md](references/extension-yaml-format.md) | 数据扩展 YAML 列定义和示例 |
| [references/sarif-processing.md](references/sarif-processing.md) | 用于 SARIF 输出处理的 jq 命令 |
| [references/diagnostic-query-templates.md](references/diagnostic-query-templates.md) | 用于源/汇枚举的 QL 查询 |
| [references/important-only-suite.md](references/important-only-suite.md) | 重要套件模板和生成 |
| [references/run-all-suite.md](references/run-all-suite.md) | run-all 套件模板 |
| [references/ruleset-catalog.md](references/ruleset-catalog.md) | 按语言划分的可用查询包 |
| [references/threat-models.md](references/threat-models.md) | 威胁模型配置 |
| [references/language-details.md](references/language-details.md) | 语言特定的构建和提取详细信息 |
| [references/performance-tuning.md](references/performance-tuning.md) | 内存、线程和超时配置 |

---

## 成功标准

完整的 CodeQL 分析运行应满足：

- [ ] 解析输出目录（用户指定或自动递增的默认值）
- [ ] 所有生成的文件存储在 `$OUTPUT_DIR` 内
- [ ] 构建了数据库（通过 `codeql-database.yml` 标记发现）并且 `{baseDir}/scripts/check_db_quality.py` 退出零
- [ ] 评估了数据扩展——要么在 `$OUTPUT_DIR/extensions/` 中创建，要么使用理由显式跳过
- [ ] 使用显式套件引用运行分析（不是默认包套件），并且 `{baseDir}/scripts/verify_query_suite.py` 对它退出零
- [ ] 使用了所有安装的查询包（官方 + Trail of Bits + 社区），或显式排除了它们
- [ ] 选择的查询包记录到 `$OUTPUT_DIR/rulesets.txt`
- [ ] 保留未过滤的结果在 `$OUTPUT_DIR/raw/results.sarif`
- [ ] 最终结果在 `$OUTPUT_DIR/results/results.sarif`（过滤重要部分，为 run-all 复制）
- [ ] 零发现结果进行了调查（数据库质量、模型覆盖范围、套件选择）
- [ ] 构建日志保存在 `$OUTPUT_DIR/build.log`，包含所有命令、修复和质量评估
