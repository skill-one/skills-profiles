# /printing-press-score

对 Steinberger 标杆生成的 CLI 进行评分。支持重新评分、按名称/路径评分以及比较两个 CLI。

## 快速入门

```
/printing-press-score                              # 重新评分当前 CLI
/printing-press-score notion-pp-cli-4              # 按名称评分
/printing-press-score ~/my-cli                     # 按路径评分
/printing-press-score notion-pp-cli-4 vs notion-pp-cli-2  # 比较两个
```

## 前置条件

- 安装 Go 1.26.6 或更高版本
- `cli-printing-press` 二进制文件在 PATH 上（使用 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 安装）

## 第 0 步：设置

在任何其他命令之前，运行设置合约以验证 `cli-printing-press` 二进制文件是否在 PATH 上并初始化作用域变量：

<!-- PRESS_SETUP_CONTRACT_START -->
```bash
# min-binary-version: 4.0.0

# 首先推导作用域 — 需要用于本地构建检测
_scope_dir="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
_scope_dir="$(cd "$_scope_dir" && pwd -P)"

# 从 printing-press 仓库内部运行时优先使用本地构建。
_press_repo=false
if [ -x "$_scope_dir/cli-printing-press" ] && [ -d "$_scope_dir/cmd/cli-printing-press" ]; then
  _press_repo=true
  export PATH="$_scope_dir:$PATH"
  echo "使用本地构建: $_scope_dir/cli-printing-press"
elif ! command -v cli-printing-press >/dev/null 2>&1; then
  if [ -x "$HOME/go/bin/cli-printing-press" ]; then
    echo "cli-printing-press 位于 ~/go/bin/cli-printing-press 但不在 PATH 上。"
    echo "将 GOPATH/bin 添加到你的 PATH:  export PATH=\"\$HOME/go/bin:\$PATH\""
  else
    echo "cli-printing-press 二进制文件未找到。"
    echo "使用以下命令安装:  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  fi
  return 1 2>/dev/null || exit 1
fi

# 解析并输出代理必须用于每个后续 `cli-printing-press` 调用的绝对路径。上面 `export PATH` 仅影响该单个 Bash 工具调用；后续调用会打开一个新的 shell 并根据用户的默认 PATH 解析 `cli-printing-press`，其中可能存在陈旧的全球变量会静默地遮蔽本地构建。代理会捕获这个标记并将绝对路径替换到每个后续调用中。
if [ "$_press_repo" = "true" ]; then
  PRINTING_PRESS_BIN="$_scope_dir/cli-printing-press"
else
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi
echo "PRINTING_PRESS_BIN=$PRINTING_PRESS_BIN"

PRESS_BASE="$(basename "$_scope_dir" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]/-/g; s/^-+//; s/-+$//')"
if [ -z "$PRESS_BASE" ]; then
  PRESS_BASE="workspace"
fi

PRESS_SCOPE="$PRESS_BASE-$(printf '%s' "$_scope_dir" | shasum -a 256 | cut -c1-8)"
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_RUNSTATE="$PRESS_HOME/.runstate/$PRESS_SCOPE"
PRESS_LIBRARY="$PRESS_HOME/library"
PRESS_MANUSCRIPTS="$PRESS_HOME/manuscripts"
PRESS_CURRENT="$PRESS_RUNSTATE/current"

mkdir -p "$PRESS_RUNSTATE" "$PRESS_LIBRARY" "$PRESS_MANUSCRIPTS" "$PRESS_CURRENT"
```
<!-- PRESS_SETUP_CONTRACT_END -->

运行设置合约后，从标准输出捕获 `PRINTING_PRESS_BIN=<abs-path>` 行。**在此技能中的每个后续 `cli-printing-press ...` 调用都必须使用该绝对路径**（替换值，而不是 `$PRINTING_PRESS_BIN` 字符串）— 上面 `export PATH` 仅影响它运行的单个 Bash 工具调用，因此后续调用会在一个新的 shell 中解析 `cli-printing-press` 对应于用户的默认 `PATH`，陈旧的全球变量可能会遮蔽本地构建。

捕获二进制路径后，检查二进制版本兼容性。从此技能的 YAML 前置字段中读取 `min-binary-version` 字段。运行 `<PRINTING_PRESS_BIN> version --json` 并从输出中解析版本。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制文件比最小版本旧，立即停止并告知用户： "cli-printing-press 二进制文件 vX.Y.Z 比最小要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 更新。"

当前运行状态来自 `$PRESS_RUNSTATE`。已发布的 CLI 来自 `$PRESS_LIBRARY`。存档的手稿来自 `$PRESS_MANUSCRIPTS`。

## 第 1 步：解析参数

读取用户在 `/printing-press-score` 后面的输入。输入是 **自由形式的** — 解释意图，不要强制语法。

**要删除的噪声词：** `compare`, `vs`, `versus`, `and`, `against`, `with`, `to`

删除噪声词后，计算剩余标记的数量：

- **0 标记** → 重新评分当前模式
- **1 标记** → 评分单个模式
- **2 标记** → 比较模式

## 第 2 步：解析 CLI 目录

对于每个 CLI 标识符，将其解析为目录路径：

### 如果标记包含 `/` 或 `.`
将其视为路径（绝对或相对）。验证目录是否存在。

### 如果标记是纯名称
按以下顺序尝试：

1. `$PRESS_LIBRARY/<name>/` — 精确匹配
2. `$PRESS_LIBRARY/<name>-pp-cli/` — 带有 -pp-cli 后缀
3. 如果都不存在，使用 `$PRESS_LIBRARY/<name>-pp-cli*` 进行 Glob 匹配
4. 如果恰好有一个 Glob 匹配且是目录，使用它
5. 如果有多个 Glob 匹配，使用 AskUserQuestion 显示编号菜单

如果都不存在，扫描当前运行和存档状态：

6. 使用 Glob 查找 `$PRESS_RUNSTATE/runs/*/state.json` 文件
7. 读取每个文件，查找 `output_dir` 或 `working_dir` 值的 basename 包含名称
8. 如果找到且目录存在，使用它

如果无法解析，报告错误： "找不到 CLI '<name>'。提供路径或检查名称。"

### 重新评分当前（0 标记）
1. 使用 Glob 查找所有 `$PRESS_CURRENT/*.json` 文件
2. 读取每个文件以获取 `api_name`, `state_path`, 和 `working_dir`
3. 过滤到 `working_dir` 实际存在于磁盘上的那些
4. 如果没有找到，使用 `$PRESS_LIBRARY/*-pp-cli*` 中的目录
5. 如果恰好一个 → 自动使用它
6. 如果多个 → 使用 AskUserQuestion 显示编号菜单：
   ```
   找到多个 CLI。选择要评分的 CLI？
   1. stripe-pp-cli ($PRESS_LIBRARY/stripe-pp-cli)
   2. notion-pp-cli ($PRESS_LIBRARY/notion-pp-cli)
   3. linear-pp-cli ($PRESS_LIBRARY/linear-pp-cli)
   ```
7. 如果没有找到 → 报告： "未找到生成的 CLI。提供名称或路径。"

## 第 3 步：查找 Tier 2 评分的规范

对于每个解析的 CLI 目录，查找 OpenAPI 规范：

1. 检查 `<cli-dir>/spec.json` — 管道在生成过程中将 YAML 规范转换为 JSON
2. 如果未找到，扫描 `$PRESS_RUNSTATE/runs/*/state.json` 文件查找与该 CLI 目录匹配的规范。读取其 `spec_path` 字段。如果该文件存在于磁盘上，使用它。
3. 如果未找到规范，**不使用 `--spec`**。告知用户： "未找到规范 — 规范派生的维度将被标记为 N/A 并从分母中省略。提供规范路径以进行完整评分。"

## 第 4 步：运行 Scorecard

### 单个评分模式

运行 scorecard 命令：

```bash
cli-printing-press scorecard --dir <resolved-path> --json
```

如果找到规范，添加 `--spec <spec-path>`。

解析 JSON 输出。结构如下：

```json
{
  "api_name": "...",
  "steinberger": {
    "output_modes": 8,
    "auth": 7,
    "error_handling": 6,
    "terminal_ux": 9,
    "readme": 5,
    "doctor": 10,
    "agent_native": 7,
    "local_cache": 4,
    "breadth": 7,
    "vision": 6,
    "workflows": 3,
    "insight": 5,
    "path_validity": 0,
    "auth_protocol": 0,
    "data_pipeline_integrity": 7,
    "sync_correctness": 6,
    "type_fidelity": 4,
    "dead_code": 3,
    "total": 72,
    "percentage": 72
  },
  "overall_grade": "B",
  "gap_report": ["..."],
  "unscored_dimensions": ["path_validity", "auth_protocol"]
}
```

如果 `unscored_dimensions` 存在，这些维度应显示为 `N/A`，而不是 `0/x`，并应描述为从分母中省略，而不是作为可修复的 CLI 缺陷。为了向后兼容，JSON 仍然将数值字段编码为 `0`；消费者必须使用 `unscored_dimensions` 来区分 `N/A` 和真实的零。

学习循环信用是静态行为性的，永远不会基于存在性：scorecard 信用 `teach`/`recall`/`learnings` 注册在根命令上和非空的实体查找种子（或规范记录的 no-entities 逃避）。学习循环默认开启，因此 `internal/learn/` 存在的会一无所获；解释学习差距时，指向缺失的种子或未注册的命令，而不是缺失的文件。执行证明（验证矩阵，`learnings stats`）属于验证和 dogfood；scorecard 不会运行任何二进制文件。

### 比较模式

使用两个同时进行的 Bash 工具调用并行运行 **两个** scorecard 命令：

```bash
# 调用 1:
cli-printing-press scorecard --dir <path1> --spec <spec1> --json

# 调用 2:
cli-printing-press scorecard --dir <path2> --spec <spec2> --json
```

解析两个 JSON 输出。

## 第 5 步：渲染输出

### 单个评分表格

渲染一个丰富的 markdown 表格。注意：Tier 1 维度都是 /10。Tier 2 维度都是 /10，除了 TypeFidelity 和 DeadCode 是 /5。

```
Scorecard: <api_name>

基础设施 (Tier 1)
| 维度        | 评分 |
|-------------|------|
| Output Modes | 8/10 |
| Auth        | 7/10 |
| Error Handling | 6/10 |
| Terminal UX | 9/10 |
| README      | 5/10 |
| Doctor      | 10/10|
| Agent Native | 7/10 |
| Local Cache | 4/10 |
| Breadth     | 7/10 |
| Vision      | 6/10 |
| Workflows   | 3/10 |
| Insight     | 5/10 |

领域正确性 (Tier 2)
| 维度               | 评分 |
|--------------------|------|
| Path Validity      | 9/10 |
| Auth Protocol      | 8/10 |
| Data Pipeline Integrity | 7/10 |
| Sync Correctness  | 6/10 |
| Type Fidelity      | 4/5  |
| Dead Code          | 3/5  |

**总计: 72/100 — 等级 B**
```

如果 `gap_report` 非空，列出差距：

```
差距:
- <gap 1>
- <gap 2>
```

如果 `unscored_dimensions` 非空，在表格后添加一条注释：

```
注意: path_validity, auth_protocol 未评分并从分母中省略。提供规范路径以进行完整评分。
```

### 比较表格

渲染一个并排的表格，包含一个差值列。将第一个 CLI 名称和第二个 CLI 名称作为列标题。计算差值为 (CLI 1 评分 - CLI 2 评分)。显示 `+N` 表示正数，`-N` 表示负数，`—` 表示零。

```
Scorecard Comparison: <name1> vs <name2>

基础设施 (Tier 1)
| 维度        | <name1> | <name2> | 差值 |
|-------------|---------|---------|------|
| Output Modes | 8/10    | 5/10    | +3   |
| Auth        | 7/10    | 7/10    | —    |
| ...         |         |         |      |

领域正确性 (Tier 2)
| 维度               | <name1> | <name2> | 差值 |
|--------------------|---------|---------|------|
| Path Validity      | 9/10    | 6/10    | +3   |
| ...                |         |         |      |

| **总计**  | **72/100 (B)** | **56/100 (C)** | **+16** |
```

## 错误处理

- 如果 `cli-printing-press` 二进制文件不在 PATH 上 → 显示安装说明：`go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest`
- 如果 scorecard 命令失败 → 报告错误并显示完整的 stderr 输出
- 如果 CLI 目录不存在 → 报告哪个名称无法解析
- 如果 JSON 解析失败 → 显示原始输出并报告解析错误
