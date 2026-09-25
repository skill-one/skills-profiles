# 图演化

在两个源快照构建 Trailmark 代码图，并计算结构差异。揭示文本级差异遗漏的安全相关变化：新的攻击路径、复杂度变化、影响范围扩大、污染传播变化和权限边界修改。

## 使用场景

- 比较两个 git 引用以了解结构上的变化
- 审计一系列提交以进行安全相关演化
- 检测代码变化创建的新攻击路径
- 查找影响范围或复杂度无声增长的功能
- 识别重构中的污染传播变化
- 发布前的结构比较（标签对标签或分支对分支）

## 不适用场景

- 行级代码审查（使用 `differential-review` 进行文本差异分析）
- 单快照分析（直接使用 `trailmark` 技能）
- 从单个快照生成图表（使用 `diagramming-code` 技能）
- 变异测试筛选（使用 `genotoxic` 技能）

## 拒绝理由

| 拒绝理由 | 为什么错误 | 必要操作 |
|---------|----------|---------|
| "我们只需要结构差异，跳过预分析" | 没有预分析会遗漏污染变化、影响范围增长和权限边界变化 | 在两个快照上运行 `engine.preanalysis()` |
| "文本差异涵盖了所有变化" | 文本差异遗漏新的攻击路径、传递式复杂度变化和子图成员变化 | 使用结构差异补充文本差异 |
| "只有添加的节点重要" | 删除的安全函数和权限边界变化同样危险 | 审查删除项和修改项，而不仅仅是添加项 |
| "低严重性的结构变化可以忽略" | INFO 级别变化（死代码删除）可能掩盖删除的安全检查 | 对每个变化进行分类，审查删除项以检查替换功能 |
| "一个快照的图就足够比较" | 单快照分析无法检测演化——你需要前后两个快照 | 总是构建和导出两个图 |
| "工具未安装，我将手动比较" | 手动比较遗漏图分析捕获的内容 | 首先安装 trailmark |
| "差异返回为空，所以结构上没有变化" | `trailmark diff` 默认 `--language` 为 `python`，在其他目标上返回 0 并以空数组退出，所以空差异无论代码是否未变都读作相同 | 明确传递 `--language` 并在得出未变化结论前重新运行 |

---

## 前置条件

**trailmark** 必须已安装。如果 `uv run trailmark` 失败，运行：

```bash
uv tool install trailmark
# Python 代码片段：uv run --with trailmark python - （工具环境不可导入）
```

**不要** 落回到“手动比较”或读取源文件作为运行 trailmark 的替代。必须安装并程序化使用该工具。如果安装失败，请报告错误。

---

## 快速入门

```bash
# 比较两个 git 引用（例如，标签、分支、提交）
# 1. 在每个快照构建图
# 2. 在两个快照上运行预分析
# 3. 计算结构差异
# 4. 生成报告

# 分步操作：见工作流下方
```

---

## 决策树

```
├─ 需要了解每个指标的含义？
│  └─ 阅读：references/evolution-metrics.md
│
├─ 需要报告输出格式？
│  └─ 阅读：references/report-format.md
│
├─ 已有两个图 JSON 导出？
│  └─ 跳到阶段 3（运行原生差异 + graph_diff.py）
│
└─ 从两个 git 引用开始？
   └─ 从阶段 1 开始
```

---

## 工作流

```
图演化进度：
- [ ] 阶段 1：创建快照（git worktrees）
- [ ] 阶段 2：构建图 + 在两个快照上运行预分析
- [ ] 阶段 3：计算结构差异
- [ ] 阶段 4：解释差异并生成报告
- [ ] 阶段 5：清理工作树
```

### 阶段 1：创建快照

使用 git worktrees 获取每个引用的干净副本，而不会扰乱工作树。

```bash
# 创建用于工作树的临时目录
BEFORE_DIR=$(mktemp -d)
AFTER_DIR=$(mktemp -d)

# 创建工作树（从仓库根目录运行）
git worktree add "$BEFORE_DIR" {before_ref}
git worktree add "$AFTER_DIR" {after_ref}
```

如果比较两个目录而不是 git 引用，跳过此阶段，并在阶段 2 中直接使用目录路径。

### 阶段 2：构建图并运行预分析

为两个快照构建 Trailmark 图，并在每个上运行预分析。预分析计算影响范围、污染传播、权限边界和入口点枚举。

```python
from trailmark.query.api import QueryEngine

def build_and_export(target_dir, output_path, language="auto"):
    """构建图，运行预分析，导出 JSON."""
    engine = QueryEngine.from_directory(target_dir, language=language)
    engine.preanalysis()
    json_str = engine.to_json()
    with open(output_path, "w") as f:
        f.write(json_str)
    return engine.summary()

import tempfile, os
work_dir = tempfile.mkdtemp(prefix="trailmark_evolution_")
before_json = os.path.join(work_dir, "before_graph.json")
after_json = os.path.join(work_dir, "after_graph.json")

before_summary = build_and_export(
    "{before_dir}", before_json
)
after_summary = build_and_export(
    "{after_dir}", after_json
)
```

通过检查摘要输出来验证两个图是否构建成功。如果任一失败，使用显式语言或逗号分隔列表重新运行，而不是 `auto`。

### 阶段 3：计算结构差异

运行 **两者**：

1. Trailmark 的原生结构差异（节点、边和入口点）
2. 插件的 `graph_diff.py` 辅助工具（用于子图成员变化）

使用阶段 2 的相同 `work_dir`，并传递与阶段 2 构建的相同 `--language` 值。`trailmark diff` 默认该标志为 `python`，在任意其他目标上默认退出 0 并写入空数组，而不是报告不匹配。

```bash
trailmark diff --json --language auto "{before_dir}" "{after_dir}" > "{work_dir}/trailmark_diff.json" || \
  uv run trailmark diff --json --language auto "{before_dir}" "{after_dir}" > "{work_dir}/trailmark_diff.json"

uv run {baseDir}/scripts/graph_diff.py \
    --before "{before_json}" \
    --after "{after_json}" > "{work_dir}/subgraph_diff.json"
```

如果阶段 2 需要显式语言或逗号分隔列表而不是 `auto`，在此处使用相同值。

如果任一差异命令失败或写入空 JSON 文件，停止并报告错误，而不是继续到阶段 4。

一个 `trailmark_diff.json`，其 `nodes`、`edges` 和 `entrypoints` 数组全部为空，意味着结构上未发生变化或两个快照解析为（近）空图。使用阶段 2 的图摘要决定：如果任一快照的节点数为零或对目标来说不切实际地小，则解析遗漏了代码——明确指定语言集（`rust`、`solidity`、`python,rust`）并重新运行。两个快照上健康的节点数加上空差异表示真正的结构稳定性。

原生 Trailmark 差异包含：

| 键 | 内容 |
|----|------|
| `summary_delta` | 节点/边/入口点计数的变更 |
| `nodes.added` | 新功能、类、方法 |
| `nodes.removed` | 删除的功能、类、方法 |
| `nodes.modified` | 复杂度、参数、行跨度发生变化的功能 |
| `edges.added` | 新的调用/继承/导入关系 |
| `edges.removed` | 删除的关系 |
| `entrypoints` | 添加、删除和修改的入口点 |

子图差异包含：

| 键 | 内容 |
|----|------|
| `subgraphs` | 每个子图的成员变化（污染、高影响范围等） |

### 阶段 4：解释差异并生成报告

读取 **两者** 差异 JSON 文件并生成安全聚焦的 markdown 报告。
参见 [references/report-format.md](references/report-format.md) 获取完整模板。

**解释优先级（从高到低）：**

1. **新的污染路径** — 进入 `tainted` 子图的节点，特别是如果它们也出现在指向敏感函数的添加边中
2. **权限边界变化** — 原生入口点/边差异中新增或删除的信任转换，加上子图差异
3. **攻击面增长** — 来自 `trailmark_diff.json` 的新入口点，特别是 `untrusted_external`
4. **影响范围增加** — 进入 `high_blast_radius` 的节点
5. **复杂度峰值** — 污染或入口点可达节点的 CC 增加超过 3
6. **结构添加** — 新节点和边（需要审查）
7. **结构删除** — 验证删除的安全函数是否被替换

将结构变化与 `git diff {before_ref}..{after_ref}` 跨参考，为发现添加源级上下文。

**严重性分类：**

| 严重性 | 结构信号 |
|-------|----------|
| CRITICAL | 新污染路径到敏感函数，删除认证边界 |
| HIGH | 新入口点 + 高影响范围，污染节点的 CC 大幅增加 |
| MEDIUM | 新信任边界跨越边，中等 CC 增加 |
| LOW | 没有入口点可达性的添加节点 |
| INFO | 死代码删除，复杂度减少 |

有关详细指标定义，请参阅
[references/evolution-metrics.md](references/evolution-metrics.md)。

### 阶段 5：清理

报告写入后删除 git 工作树：

```bash
git worktree remove "{before_dir}"
git worktree remove "{after_dir}"
```

---

## 差异参考

```
trailmark diff --json --language auto BEFORE AFTER
uv run {baseDir}/scripts/graph_diff.py [OPTIONS]
```

`trailmark diff --language` 默认为 `python`。在任何其他语言的目标上，默认仍然退出 0，发出格式良好的 JSON，其中 `nodes`、`edges` 和 `entrypoints` 数组为空，因此始终传递该标志：`auto` 检测并合并目标下找到的每个支持的语言，并使用单个名称（`rust`、`solidity`）或逗号分隔列表（`python,rust`）固定显式集。`auto` 在快照包含它无法解析的内容时响亮失败，`<path>` 下未检测到支持的语言，这是你想要的结果。首先确认语言；只有到那时，空差异才能作为未变化的证据。

使用 `trailmark diff` 进行：

- 节点/边变化
- 添加/删除/修改的入口点
- 人类可读的结构差异报告

使用 `graph_diff.py` 进行：

- 从 `engine.preanalysis()` 派生的子图成员变化
- `tainted`、`high_blast_radius`、`privilege_boundary` 和相关集

| 参数 | 默认 | 描述 |
|------|------|------|
| `--before` | 必需 | "之前" 图 JSON 的路径 |
| `--after` | 必需 | "之后" 图 JSON 的路径 |
| `--indent` | `2` | JSON 输出缩进 |

`graph_diff.py` 输入格式：来自 `engine.to_json()` 的 Trailmark JSON 导出。
`graph_diff.py` 输出：节点、边和子图的结构差异 JSON。

---

## 质量检查清单

交付报告前：

- [ ] 两个图构建成功（检查摘要）
- [ ] 在两个快照上运行了预分析
- [ ] 计算了原生 Trailmark 差异（`trailmark_diff.json`）；如果为空，则两个快照的阶段 2 节点数非零，所以空意味着稳定
- [ ] 计算了子图差异且非空（`subgraph_diff.json`）
- [ ] 解释了所有子图变化（污染、影响范围等）
- [ ] 关键发现包括证据（节点 ID、边差异）
- [ ] 所有发现都分配了严重性级别
- [ ] 通过 git diff 跨参考添加了源级上下文
- [ ] 清理了工作树（或删除了临时目录）
- [ ] 报告写入到 `GRAPH_EVOLUTION_*.md`

---

## 集成

**trailmark 技能：**
阶段 2 使用 trailmark API 进行图构建和预分析。
所有 trailmark 查询模式都适用于快照的任一引擎。

**differential-review 技能：**
使用 graph-evolution 进行结构分析，differential-review 进行行级代码审查。两者互补——graph-evolution 发现文本差异遗漏的攻击路径，而 differential-review 提供 git blame 上下文和微观对抗性分析。

**trailmark-review-gate 技能：**
graph-evolution 后使用 trailmark-review-gate，当分支、拉取请求、修复提交或发布差异需要结构审查包（PASS/WARN/FAIL/UNKNOWN）时。该网关对 graph-evolution 输出应用确定性审查规则；它不取代人工审查。

**genotoxic 技能：**
如果 graph-evolution 揭示新的高 CC 污染节点，将其输入 genotoxic 进行变异测试筛选。

**diagramming-code 技能：**
生成前后图表以可视化结构变化。
使用 `call-graph` 或 `data-flow` 图表，聚焦于已更改节点。

---

## 支持文档

- **[references/evolution-metrics.md](references/evolution-metrics.md)** —
  每个结构指标的含义及其为何对安全重要
- **[references/report-format.md](references/report-format.md)** —
  报告模板、严重性分类和示例发现
