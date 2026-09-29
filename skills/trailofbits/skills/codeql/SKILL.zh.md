---
name: codeql
description: 使用 CodeQL 的跨过程数据流和污点跟踪分析扫描代码库中的安全漏洞。在 "run codeql"、"codeql scan"、"build codeql database"、"SAST 扫描"、"污点分析"、"数据流分析" 或 "在此仓库中查找漏洞" 时触发。支持 Python、JavaScript/TypeScript、Go、Java/Kotlin、C/C++、C#、Ruby 和 Swift。支持 "run all"（安全与质量 + 安全实验）和 "重要仅"（高精度）扫描模式，并为项目特定的源和汇创建数据扩展模型。对于快速单文件模式匹配，或编译型语言无构建可用时，使用 semgrep 技能；若要解析已存在的 SARIF 而非生成，使用 sarif-parsing 技能。
---

# CodeQL 分析

支持的语言：Python、JavaScript/TypeScript、Go、Java/Kotlin、C/C++、C#、Ruby、Swift。

**技能资源**：参考文件和模板位于 `{baseDir}/references/` 和 `{baseDir}/workflows/`。

## 基本原则

1. **数据库质量不可妥协。** 能够构建的数据库不一定是好的——一个缓存的构建什么也提取不了，却报告成功。

2. **数据扩展能捕捉 CodeQL 遗漏的内容。** Django、Spring 和 Express 项目仍然在项目特定的 API 中封装数据库调用、请求解析和 Shell 执行，而这些 API 没有被发布的模型覆盖。

3. **显式套件引用防止静默查询丢弃。** 不要将包名传递给 `codeql database analyze` —— 每个包的 `defaultSuiteFile` 应用隐藏的过滤器，可能导致零结果。始终生成 `.qls`。

4. **零发现需要调查，而不是庆祝。** 这可能意味着提取不良、缺少模型、错误的包或套件过滤。构建后运行 `{baseDir}/scripts/check_db_quality.py`，确认 `{baseDir}/scripts/verify_query_suite.py` 对使用的套件退出为零——生成脚本会运行它，因此仅对重用或手动编辑的套件手动调用它——并在报告中说明两者都通过了。

5. **macOS Apple Silicon 需要对编译语言进行工作绕过。** 退出码 137 是 `arm64e`/`arm64` 不匹配，而不是构建失败。在回退到 `build-mode=none` 之前，尝试 Homebrew arm64 工具或罗塞塔。

6. **按步骤遵循工作流。** 每个阶段都控制下一个阶段；跳过质量评估或数据扩展会在结果中留下可见的差距。

## 每个 Bash 调用都是一个新的 Shell

Bash 调用之间不会传递任何内容：不是变量，不是数组，不是从 `build_log.sh` 源码的函数。以下每个使用值的块都必须在同一个块中重新建立它。
工作流会回退到这里而不是重复它；它们所说明的是该地点的具体损坏，因为每个都不同且静默地失败：

- 失去的**函数**使 `run_logged` 退出 127，构建阶梯将其读取为失败的方法并下移到 `--build-mode=none`，从未调用 CodeQL
- 失去的**数组**扩展为空，因此用户选择的每个 `--threat-model` 和 `--model-packs` 都会被丢弃，而最终报告仍然将它们列为使用
- 在 `set -u` 下失去的**标量**会中止块，显示 `unbound variable`

## 输出目录

所有生成的文件（数据库、构建日志、诊断、扩展、结果）都存储在一个输出目录中。

- **如果用户在提示中指定了输出目录**，将其用作 `OUTPUT_DIR`。
- **如果没有指定**，默认为 `./static_analysis_codeql_1`。如果已存在，则递增为 `_2`、`_3` 等。

在这两种情况下，**始终使用 `mkdir -p` 创建目录**，然后再写入任何文件。

在运行此命令之前，将 `USER_SPECIFIED_DIR` 设置为用户提示中的字面路径，或者将其留空以自动递增。否则不会分配它。

```bash
# 解析输出目录
USER_SPECIFIED_DIR="${USER_SPECIFIED_DIR:-}"   # 在这里替换用户路径，如果有的话
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

输出目录在**工作流执行之前**解析一次。所有工作流接收 `$OUTPUT_DIR` 并将其工件存储在那里：

```
$OUTPUT_DIR/
├── rulesets.txt                 # 选择的查询包（在步骤 3 后记录）
├── codeql.db/                   # CodeQL 数据库（包含 codeql-database.yml 的目录）
├── build.log                    # 构建日志
├── codeql-config.yml            # 排除配置（解释性语言）
├── diagnostics/                 # 诊断查询和 CSV
├── extensions/                  # 数据扩展 YAML
├── raw/                         # 未过滤的分析输出
│   ├── results.sarif
│   └── run-all.qls | important-only.qls
└── results/                     # 最终结果（过滤为 important-only，复制为 run-all）
    └── results.sarif
```

### 数据库发现

CodeQL 数据库由其目录中存在的 `codeql-database.yml` 标记文件标识。在搜索现有数据库时，**始终收集所有匹配项**——可能有来自先前运行或不同语言的多个数据库。

**发现命令。** `find_databases.sh` 每行打印一个数据库路径，过滤掉构建失败留下的标记文件。在构建数组**在同一个选择它的块中**——每个 Bash 调用都是一个新 Shell，因此在此构建的数组在下一个调用时为空，并且运行结束没有数据库：

```bash
# 命令替换，不是 `done < <(...)`：进程替换会丢弃脚本
# 的退出状态，因此“codeql 不在这个 Shell 的 PATH 上”（退出 2）会作为空列表到达，并路由到“构建新数据库”，磁盘上有三个好的数据库。
if ! DB_LIST=$("{baseDir}/scripts/find_databases.sh" "${OUTPUT_DIR:-.}" .); then
  echo "ERROR: 数据库发现失败——请查看上面的消息" >&2
  exit 1
fi

FOUND_DBS=()
while IFS= read -r db; do
  [ -n "$db" ] || continue
  FOUND_DBS+=("$db")
done <<<"$DB_LIST"

echo "找到 ${#FOUND_DBS[@]} 个现有数据库"

# 选择提示需要的元数据，收集在这里而不是它自己的块中：FOUND_DBS 在下一个 Bash 调用中消失，并且一个循环遍历不再存在的数组会打印 nothing 并报告成功。
for db in "${FOUND_DBS[@]}"; do
  CODEQL_LANG=$(codeql resolve database --format=json -- "$db" 2>/dev/null | jq -r '.languages[0]')
  CREATED=$(grep '^creationMetadata:' -A5 "$db/codeql-database.yml" 2>/dev/null | grep 'creationTime' | awk '{print $2}')
  echo "$db — 语言：$CODEQL_LANG，创建时间：$CREATED"
done
```

永远不要假设数据库命名为 `codeql.db`——通过它的标记文件发现它。

**当发现多个数据库时：** 使用 `AskUserQuestion` 让用户选择要使用的数据库，或者根据上面打印的语言和创建时间构建一个新的，从 `AskUserQuestion` 最多四个选项，因此如果有更多数据库，提供三个最新的加上“构建新数据库”，并在提示文本中列出其余的。**如果用户在提示中明确说明了要使用哪个数据库或构建一个新数据库，则跳过 `AskUserQuestion`。**

## 快速入门

对于常见情况（“扫描此代码库以查找漏洞”）：

```bash
# 验证 CodeQL 是否已安装。如果未安装，停止——每个后续命令都会出现不太明确的错误，并且运行会浪费构建周期才说明原因。
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

# uv 运行两个保护脚本和两个套件生成器。在套件生成之前检查它，而不是在构建之后——否则没有 uv 的机器会花费整个构建时间才失败。
if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv 未在 PATH 上找到（https://docs.astral.sh/uv/getting-started/）" >&2
  exit 1
fi

codeql --version
```

然后使用上面 [输出目录](#output-directory) 中的块解析 `OUTPUT_DIR`——它尊重用户指定的目录，而裸自动递增不会。

然后执行完整管道：**构建数据库 → 创建数据扩展 → 运行分析** 使用以下工作流。

## 拒绝的理由

这些捷径会导致遗漏发现。不要接受它们：

- **“security-extended 足够”** - 它是基准。始终检查是否有适用于该语言的 Trail of Bits 包和社区包。它们完全捕获了 `security-extended` 完全遗漏的类别。
- **“security-and-quality 是最广泛的套件”** - `security-and-quality` 排除了所有 `experimental/` 查询路径。对于 run-all 模式，导入 `security-and-quality` 和 `security-experimental`。差异取决于语言，为 1–52 个查询。
- **“数据库构建了，所以它是好的”** - 构建成功的数据库不意味着它提取得很好。始终运行质量评估并检查文件计数与预期源文件是否一致。
- **“标准框架不需要数据扩展”** - 即使 Django/Spring 应用也有 CodeQL 未建模的自定义包装器。跳过扩展意味着遗漏漏洞。
- **“build-mode=none 对编译语言可以”** - 它会产生严重不完整分析。仅作为绝对最后的手段使用。在 macOS 上，先尝试 arm64 工具链工作绕过或罗塞塔。
- **“macOS 构建失败，只需使用 build-mode=none”** - 退出码 137 是由 `arm64e`/`arm64` 不匹配引起的，而不是根本性的构建失败。参见 [macos-arm64e-workaround.md](references/macos-arm64e-workaround.md)。
- **“没有发现意味着代码是安全的”** - 运行 `check_db_quality.py` 和 `verify_query_suite.py` 并报告它们通过了。如果没有它们，零发现和提取了 nothing 的数据库是相同的输出。
- **“我将只运行默认套件”** / **“我将直接传递包名”** - 每个包的 `defaultSuiteFile` 应用隐藏的过滤器，并且可以产生零结果。始终使用显式套件引用。
- **“我将把文件放在当前目录”** - 所有生成的文件都必须放在 `$OUTPUT_DIR`。在工作目录中分散文件使清理不可能，并且有风险覆盖以前的运行。
- **“只需使用我找到的第一个数据库”** - 可能有多个数据库存在于不同的语言或以前的运行中。当发现多个时，向用户展示所有选项。仅当用户已经指定要使用哪个数据库时才跳过提示。
- **“用户说‘扫描’，这意味着他们希望我选择一个数据库”** - “扫描”不是数据库选择。如果存在多个数据库并且用户没有指定，请询问。

| 文件 | 内容 |
|------|---------|
| **脚本** | |
| [scripts/verify_query_suite.py](scripts/verify_query_suite.py) | 生成一个解析为零查询的套件。生成脚本会运行它；仅手动为重用或手动编辑的套件调用 |
| [scripts/check_db_quality.py](scripts/check_db_quality.py) | 生成一个没有可分析源的数据库。每次构建后运行 |
| [scripts/build_log.sh](scripts/build_log.sh) | `log_step`/`run_logged` 辅助函数；任何构建步骤之前都要源代码 |
| [scripts/find_databases.sh](scripts/find_databases.sh) | 打印 `codeql resolve database` 接受的每个数据库，每行一个。从它构建你的数组，在读取它的代码块中 |
| [scripts/generate_suite.sh](scripts/generate_suite.sh) | 写入 run-all 或 important-only 的 `.qls`，并验证它解析为非零查询数 |
| **参考资料** — 三个工作流在 [工作流选择](#workflow-selection) 下列出 | |
| [references/macos-arm64e-workaround.md](references/macos-arm64e-workaround.md) | Apple Silicon 构建跟踪解决方案 |
| [references/build-fixes.md](references/build-fixes.md) | 构建失败修复目录 |
| [references/quality-assessment.md](references/quality-assessment.md) | 数据库质量指标和改进 |
| [references/extension-yaml-format.md](references/extension-yaml-format.md) | 数据扩展 YAML 列定义和示例 |
| [references/sarif-processing.md](references/sarif-processing.md) | 用于 SARIF 输出处理的 jq 命令 |
| [references/diagnostic-query-templates.md](references/diagnostic-query-templates.md) | 用于源/汇枚举的 QL 查询 |
| [references/important-only-suite.md](references/important-only-suite.md) | important-only 套件模板和生成 |
| [references/run-all-suite.md](references/run-all-suite.md) | run-all 套件模板 |
| [references/ruleset-catalog.md](references/ruleset-catalog.md) | 按语言划分的可用查询包 |
| [references/threat-models.md](references/threat-models.md) | 威胁模型配置 |
| [references/language-details.md](references/language-details.md) | 语言特定的构建和提取细节 |
| [references/performance-tuning.md](references/performance-tuning.md) | 内存、线程和超时配置 |

---

## 成功标准

一个完整的 CodeQL 分析运行应满足：

- [ ] 输出目录解析（用户指定或自动递增默认值）
- [ ] 所有生成的文件存储在 `$OUTPUT_DIR` 内
- [ ] 数据库构建（通过 `codeql-database.yml` 标记发现）且 `{baseDir}/scripts/check_db_quality.py` 退出状态为零
- [ ] 数据扩展评估 — 要么创建在 `$OUTPUT_DIR/extensions/` 内，要么明确跳过并说明理由
- [ ] 使用显式套件引用进行分析（非默认包套件），且 `{baseDir}/scripts/verify_query_suite.py` 对其退出状态为零
- [ ] 所有已安装的查询包（官方 + Trail of Bits + 社区）使用或明确排除
- [ ] 选定的查询包记录到 `$OUTPUT_DIR/rulesets.txt`
- [ ] 未过滤结果保留在 `$OUTPUT_DIR/raw/results.sarif`
- [ ] 最终结果在 `$OUTPUT_DIR/results/results.sarif`（重要-only 过滤，run-all 复制）
- [ ] 零发现结果调查（数据库质量、模型覆盖率、套件选择）
- [ ] 构建日志保留在 `$OUTPUT_DIR/build.log`，包含所有命令、修复和质量评估
