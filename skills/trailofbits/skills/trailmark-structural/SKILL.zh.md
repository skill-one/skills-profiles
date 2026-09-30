---
name: trailmark-structural
description: 执行完整的 Trailmark 结构分析，通过构建图、运行 `preanalysis()` 并报告热点、污染、爆炸半径、权限边界、攻击面以及版本控制的 Trailmark 0.4+/0.5+ 数据（如代理计数、子图边、类型/引用摘要和入口点属性）。当 vivisect 需要目标详细的结构数据时使用。触发条件：结构分析、爆炸半径、污染分析、复杂热点、代理节点、类型引用。
---

# Trailmark 结构分析

构建 Trailmark 图并运行 `engine.preanalysis()` 来计算所有四个预分析阶段。核心工作流是 v0.2 安全版；v0.4 仅有的细节仅在检查方法可用性后才包含，更新的构建版本丰富了相同的输出（0.5.0+ 为攻击面条目添加了 `attributes` 键，并从 `.trailmark/links.toml` 中添加了 `proxy.external:*` 节点），而无需任何工作流变更。

## 使用场景

- Vivisect 第一阶段需要完整结构数据（热点、污染、爆炸半径、权限边界）
- 针对特定目标范围的详细预分析阶段
- 为审计优先级生成复杂性和污染数据
- 当安装了 Trailmark 0.4.0+ 时，检查代理/未解析调用计数、子图边或类型引用摘要

## 不应使用场景

- 仅需快速概览（使用 `trailmark-summary` 代替）
- 临时代码图查询（直接使用主 `trailmark` 技能）
- 目标是一个小文件，而结构分析没有价值

## 拒绝理由

| 拒绝理由 | 为什么错误 | 必要操作 |
|-----------------|----------------|-----------------|
| "摘要分析足够" | 摘要跳过了污染、爆炸半径和权限边界数据 | 当需要详细数据时运行完整结构分析 |
| "一个阶段就足够" | 阶段相互交叉引用——没有爆炸半径的污染会遗漏关键节点 | 运行所有四个阶段 |
| "工具未安装，我将手动分析" | 手动分析遗漏了工具能捕捉的内容 | 报告 "trailmark 未安装" 并返回 |
| "空阶段输出意味着阶段失败" | 某些阶段对某些代码库不产生数据（例如，没有权限边界） | 无论如何都返回完整输出 |
| "v0.4 字段始终存在" | 用户可能仍然安装了 Trailmark 0.2.x 版本 | 在查询 v0.4 仅有的方法前使用 `hasattr()` 探测 |

## 使用方法

目标目录通过 `args` 参数传递。

## 执行步骤

**步骤 1：检查 trailmark 是否可用。**

```bash
trailmark analyze --help 2>/dev/null || \
  uv run trailmark analyze --help 2>/dev/null
```

如果这两个命令都不起作用，报告 "trailmark 未安装" 并返回。不要运行 `pip install`、`uv pip install`、`git clone` 或任何安装命令。用户必须自行安装 trailmark。

可选地记录版本：

```bash
trailmark --version 2>/dev/null || uv run trailmark --version 2>/dev/null || true
```

如果此命令缺失，不要失败；使用下面的 API 功能探测。

**步骤 2：使用 Trailmark 的解析 API 检测语言。**

```bash
python3 - "{args}" <<'PY'
import json
import sys

try:
    from trailmark.parse import detect_languages  # 自 0.3.x 版本起的标准位置
except ModuleNotFoundError:
    # 0.2.x 版本早于 trailmark.parse；相同的功能位于 query.api
    from trailmark.query.api import detect_languages

print(json.dumps(detect_languages(sys.argv[1])))
PY
```

如果导入失败，使用 `uv run --with trailmark python - "{args}"` 重新运行相同代码片段。如果结果是 `[]`，报告 "Trailmark 在目标下未发现支持的语言" 并返回。

**步骤 3：通过 `QueryEngine` 运行完整结构分析。**

使用 `python3` 运行此代码片段。如果导入失败，在 `uv run --with trailmark python - "{args}"` 下重新运行相同代码片段。

```bash
python3 - "{args}" <<'PY'
import json
import sys

try:
    from trailmark.parse import detect_languages  # 自 0.3.x 版本起的标准位置
except ModuleNotFoundError:
    # 0.2.x 版本早于 trailmark.parse；相同的功能位于 query.api
    from trailmark.query.api import detect_languages

from trailmark.query.api import QueryEngine

target = sys.argv[1]
languages = detect_languages(target)
engine = QueryEngine.from_directory(target, language="auto")
preanalysis = engine.preanalysis()

def summarize_subgraph(name: str, limit: int = 25) -> dict[str, object]:
    nodes = engine.subgraph(name)
    summary = {
        "count": len(nodes),
        "sample_ids": [node["id"] for node in nodes[:limit]],
    }
    if hasattr(engine, "subgraph_edges"):
        summary["edge_count"] = len(engine.subgraph_edges(name))
    return summary

graph = json.loads(engine.to_json())
nodes = graph.get("nodes", {})
proxy_nodes = [
    node_id for node_id, node in nodes.items()
    if node.get("kind") == "proxy" or node.get("origin") == "proxy"
]

payload = {
    "languages": languages,
    "summary": engine.summary(),
    "preanalysis": preanalysis,
    "attack_surface": engine.attack_surface()[:25],
    "hotspots": engine.complexity_hotspots(10)[:25],
    "proxy_nodes": proxy_nodes[:25],
    "subgraphs": {
        name: summarize_subgraph(name)
        for name in engine.subgraph_names()
    },
}

if hasattr(engine, "type_references"):
    payload["type_reference_samples"] = {
        node_id: engine.type_references(node_id)[:10]
        for node_id in list(nodes)[:25]
    }

print(json.dumps(payload, indent=2))
PY
```

**步骤 4：验证输出。**

输出应包括：
- `languages`
- `summary`
- `preanalysis`
- `hotspots`（可能为空）
- `proxy_nodes`（在 v0.2.x 或没有未解析调用时为空；在 0.5.0+ 版本中可能包含 `.trailmark/links.toml` 中声明的 `proxy.external:*` 条目）
- `subgraphs` 包含计数和样本 ID

在 Trailmark 0.5.0+ 版本中，`attack_surface` 条目可能包含 `attributes` 对象（例如 `solidity_visibility`、`solidity_overridden_by`）。将其原样传递——下游消费者使用它来对入口点进行排序。

某些子图可能对某些代码库没有节点（这是正常的）。无论怎样都返回完整的 JSON 负载。
