# 图形化 DOT 图表生成器

> **重要提示：** 使用 ` ```dot ` 作为代码分隔符，不要使用 ` ```graphviz `。

**快速入门：** 选择 `digraph`（有向）或 `graph`（无向）→ 定义带属性的节点（形状、颜色、标签）→ 使用 `->` 或 `--` 连接 → 设置布局（rankdir、间距）→ 用 ` ```dot ` 分隔符包裹。默认：自上而下（`rankdir=TB`），簇名必须以 `cluster_` 开头，使用分号。

---

## 关键语法规则

### 规则 1：簇命名
```
❌ subgraph backend { }      → 不会渲染为框
✅ subgraph cluster_backend { }  → 必须以 cluster_ 开头
```

### 规则 2：带空格的节点 ID
```
❌ API Gateway [label="API"];    → 无效 ID
✅ "API Gateway" [label="API"];  → 引号包裹 ID
✅ api_gateway [label="API Gateway"];  → 使用下划线 ID
```

### 规则 3：边语法差异
```
digraph: A -> B;   → 有向箭头
graph:   A -- B;   → 无向线
```

### 规则 4：属性语法
```
❌ node [shape=box color=red]    → 缺少逗号
✅ node [shape=box, color=red];  → 逗号分隔
```

### 规则 5：HTML 标签
```
✅ shape=plaintext 用于 HTML 标签
✅ 使用 < > 而不是 " " 包裹 HTML 内容
```

---

## 常见陷阱

| 问题 | 解决方案 |
|-------|----------|
| 节点重叠 | 增加 `nodesep` 和 `ranksep` |
| 布局不佳 | 更改 `rankdir` 或添加 `{rank=same}` |
| 边交叉 | 使用 `splines=ortho` 或调整节点顺序 |
| 簇未显示 | 名字必须以 `cluster_` 开头 |
| 标签不显示 | 检查引号转义 |

---

## 输出格式

````markdown
```dot
digraph G {
    [图表代码]
}
```
````

---

## 相关文件

> 对于高级布局控制和复杂样式，请参考以下参考：

- [syntax.md](references/syntax.md) — 布局控制（rankdir、splines、rank）、HTML 标签、边样式、簇子图和基于记录的节点
