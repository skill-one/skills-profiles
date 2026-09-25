# Trailmark 摘要

在目标目录上运行 `trailmark analyze --language auto --summary`。
这是一个 v0.2 安全的工作流程；仅为了生成摘要而无需 Trailmark 0.4.0。

## 使用场景

- Vivisect 阶段 0 在分解前需要快速的结构性概览
- Galvanize 阶段 1 需要检测到的语言和入口点计数
- 在进行深入分析前对不熟悉的代码库进行快速了解

## 不适用场景

- 需要进行完整结构性分析且所有步骤都需要的场景（使用 `trailmark-structural`）
- 需要进行详细的代码图查询（直接使用主 `trailmark` 技能）
- 你需要热点分数或污染数据（使用 `trailmark-structural`）

## 拒绝的理由及原因

| 拒绝的理由 | 为什么不正确 | 必要操作 |
|-----------|-------------|---------|
| "我可以手动阅读代码" | 手动阅读会遗漏基于解析器的语言检测、依赖数据以及入口点枚举 | 安装并运行 trailmark |
| "语言检测不重要" | 错误的语言选择会导致空分析或部分分析 | 使用 Trailmark 的基于解析器的检测或 `--language auto` |
| "部分输出足够了" | 任何三个必需输出（检测到的语言、入口点、依赖）的缺失都意味着分析不完整 | 验证所有三个都存在 |
| "工具未安装，我将跳过" | 这个技能的存在就是为了运行 trailmark | 报告安装缺口而不是跳过 |

## 使用方法

目标目录通过 `args` 参数传递。

## 执行步骤

**步骤 1：检查 trailmark 是否可用。**

```bash
trailmark analyze --help 2>/dev/null || \
  uv run trailmark analyze --help 2>/dev/null
```

如果两个命令都不起作用，报告 "trailmark 未安装" 并返回。不要运行 `pip install`、`uv pip install`、`git clone` 或任何安装命令。用户必须自行安装 trailmark。

可选地，如果安装的构建支持，记录版本号：

```bash
trailmark --version 2>/dev/null || uv run trailmark --version 2>/dev/null || true
```

如果版本命令缺失，不要失败；较旧的 v0.2.x 构建可能仍然支持摘要工作流程。

**步骤 2：使用 Trailmark 的解析 API 检测语言。**

```bash
python3 - "{args}" <<'PY'
import json
import sys

try:
    from trailmark.parse import detect_languages  # 自 0.3.x 起的标准位置
except ModuleNotFoundError:
    # v0.2.x 之前的版本；相同的功能位于 query.api
    from trailmark.query.api import detect_languages

print(json.dumps(detect_languages(sys.argv[1])))
PY
```

如果导入失败，使用 `uv run --with trailmark python - "{args}"` 重新运行相同的片段。如果结果是 `[]`，报告 "Trailmark 在目标下未发现支持的语言" 并返回。

**步骤 3：使用自动检测运行摘要。**

```bash
trailmark analyze --language auto --summary {args} 2>&1 || \
  uv run trailmark analyze --language auto --summary {args} 2>&1
```

**步骤 4：验证输出。**

输出必须包含以下全部三项：
1. 步骤 2 中检测到的语言
2. 摘要输出中的 `Entrypoints:` 行
3. 摘要输出中的 `Dependencies:` 行

如果有任何缺失，报告缺口。不要编造输出。

返回检测到的语言列表以及完整的 Trailmark 摘要输出。如果提供了版本字符串，请在返回的元数据中包含它。
