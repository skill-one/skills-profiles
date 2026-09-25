# 任何事物都能理解——Codebase 知识图谱

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

任何事物都能理解是一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 插件，它会在你的项目上运行一个多代理管道，为每个文件、函数、类和依赖项构建知识图谱，并打开一个交互式 React 仪表板进行可视化探索。它为每个节点生成简体中文摘要，因此任何人——开发者、产品经理或设计师——都能理解代码库。

---

## 安装

### 通过 Claude Code 插件市场

```bash
/plugin marketplace add Lum1104/Understand-Anything
/plugin install understand-anything
```

### 从源代码（开发）

```bash
git clone https://github.com/Lum1104/Understand-Anything
cd Understand-Anything
pnpm install
pnpm --filter @understand-anything/core build
pnpm --filter @understand-anything/skill build
pnpm --filter @understand-anything/dashboard build
```

---

## 核心技能/命令

| 命令 | 它的作用 |
|---|---|
| `/understand` | 在当前项目上运行完整的多代理分析管道 |
| `/understand-dashboard` | 打开交互式知识图谱仪表板 |
| `/understand-chat <问题>` | 用自然语言询问代码库的任何问题 |
| `/understand-diff` | 分析当前未提交更改的影响 |
| `/understand-explain <路径>` | 深入解释特定文件或函数 |
| `/understand-onboard` | 为新团队成员生成入职指南 |

---

## 典型工作流程

### 1. 分析项目

```bash
# 在任何项目目录中，在 Claude Code 中：
/understand
```

这会依次协调 5 个代理（文件分析器最多可同时运行 3 个）：

1. **project-scanner** — 发现文件，检测语言/框架
2. **file-analyzer** — 提取函数、类、导入；构建图节点和边
3. **architecture-analyzer** — 将节点分组到架构层（API、服务、数据、UI、工具）
4. **tour-builder** — 生成有序的学习路线
5. **graph-reviewer** — 验证引用完整性

输出保存到项目根目录下的 `.understand-anything/knowledge-graph.json`。

### 2. 打开仪表板

```bash
/understand-dashboard
```

React + Vite 仪表板将在你的浏览器中打开。功能：
- **图视图** — React Flow 画布，按层着色，缩放/平移
- **节点检查器** — 点击任何节点查看代码、关系、LLM 摘要
- **搜索** — 在所有节点中进行模糊+语义搜索
- **路线** — 按依赖顺序的引导式巡游
- **角色模式** — 切换详细程度（初级开发者 / 产品经理 / 高级用户）

### 3. 提问

```bash
/understand-chat 这个项目中的认证是如何工作的？
/understand-chat 哪些调用支付服务？
/understand-chat 哪些文件依赖最多？
```

### 4. 提交前审查 diff 影响

```bash
# 在做出更改后：
/understand-diff
```

返回知识图谱中受影响的节点列表——在你推送之前显示级联效应。

### 5. 解释特定文件

```bash
/understand-explain src/auth/login.ts
/understand-explain src/services/PaymentService.ts
```

---

## 知识图谱模式

图存储在 `.understand-anything/knowledge-graph.json` 中。关键类型（来自 `packages/core`）：

```typescript
// packages/core/src/types.ts

interface GraphNode {
  id: string;                    // 唯一标识："file:src/auth/login.ts"
  type: "file" | "function" | "class" | "module";
  name: string;
  filePath: string;
  layer: ArchitectureLayer;      // "api" | "service" | "data" | "ui" | "utility"
  summary: string;               // LLM 生成的简体中文描述
  code?: string;                 // 原始源代码片段
  language?: string;
  concepts?: LanguageConcept[];  // 例如："generics"、"closures"、"decorators"
  metadata?: Record<string, unknown>;
}

interface GraphEdge {
  id: string;
  source: string;                // 节点 ID
  target: string;                // 节点 ID
  type: "imports" | "calls" | "extends" | "implements" | "uses";
  label?: string;
}

interface KnowledgeGraph {
  version: string;
  generatedAt: string;
  projectRoot: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  tours: GuidedTour[];
}

type ArchitectureLayer = "api" | "service" | "data" | "ui" | "utility" | "unknown";

type LanguageConcept =
  | "generics"
  | "closures"
  | "decorators"
  | "async-await"
  | "interfaces"
  | "higher-order-functions"
  | "dependency-injection"
  | "observers"
  | "iterators"
  | "pattern-matching"
  | "monads"
  | "currying";
```

---

## 以编程方式使用核心包

```typescript
import { loadKnowledgeGraph, searchGraph, buildTour } from "@understand-anything/core";

// 加载持久化的图
const graph = await loadKnowledgeGraph(".understand-anything/knowledge-graph.json");

// 在所有节点中进行模糊搜索
const results = searchGraph(graph, "payment processing");
console.log(results.map(r => `${r.type}:${r.name} (${r.filePath})`));

// 查找所有调用某个函数的地方
const paymentNode = graph.nodes.find(n => n.name === "processPayment");
const callers = graph.edges
  .filter(e => e.target === paymentNode?.id && e.type === "calls")
  .map(e => graph.nodes.find(n => n.id === e.source));

// 获取服务层中的所有节点
const serviceNodes = graph.nodes.filter(n => n.layer === "service");

// 从特定节点开始构建引导路线
const tour = buildTour(graph, { startNodeId: "file:src/index.ts" });
tour.steps.forEach((step, i) => {
  console.log(`步骤 ${i + 1}: ${step.node.name} — ${step.node.summary}`);
});
```

---

## 仪表板开发

```bash
# 启动仪表板开发服务器（热重载）
pnpm dev:dashboard

# 生产环境构建
pnpm --filter @understand-anything/dashboard build
```

仪表板是一个 Vite + React 18 应用，使用：
- **React Flow** — 图形画布渲染
- **Zustand** — 图形状态管理
- **TailwindCSS v4** — 样式
- **Fuse.js** — 模糊搜索
- **web-tree-sitter** — 浏览器内 AST 解析
- **Dagre** — 自动图形布局

---

## 项目结构

```
understand-anything-plugin/
├── .claude-plugin/          # 插件清单（由 Claude Code 读取）
├── agents/                  # 代理定义（project-scanner、file-analyzer 等）
├── skills/                  # 技能定义（/understand、/understand-chat 等）
├── src/                     # 插件 TypeScript 源代码
│   ├── context-builder.ts   # 从图中构建 LLM 上下文
│   └── diff-analyzer.ts     # Git diff → 受影响的节点
├── packages/
│   ├── core/                # 分析引擎
│   │   ├── src/
│   │   │   ├── types.ts     # GraphNode、GraphEdge、KnowledgeGraph
│   │   │   ├── persistence.ts
│   │   │   ├── search.ts    # 模糊+语义搜索
│   │   │   ├── tours.ts     # 路线生成
│   │   │   ├── schema.ts    # Zod 验证模式
│   │   │   └── tree-sitter.ts
│   │   └── tests/
│   └── dashboard/           # React 仪表板应用
│       └── src/
```

---

## 增量更新

重新运行 `/understand` 仅重新分析自上次运行以来更改的文件（基于 mtime 和存储在图元数据中的内容哈希）。对于大型单体仓库，这使得后续运行非常快。

要强制完整重新分析：

```bash
rm -rf .understand-anything/
/understand
```

---

## 开发命令

```bash
pnpm install                                        # 安装所有依赖
pnpm --filter @understand-anything/core build       # 构建核心包
pnpm --filter @understand-anything/core test        # 运行核心测试
pnpm --filter @understand-anything/skill build      # 构建插件包
pnpm --filter @understand-anything/skill test       # 运行插件测试
pnpm --filter @understand-anything/dashboard build  # 构建仪表板
pnpm dev:dashboard                                  # 带热重载的仪表板开发服务器
```

---

## 常见模式

### 代码审查前

```bash
# 查看你的 diff 实际上影响了架构中的哪些部分
/understand-diff
```

### 新工程师入职

```bash
# 生成基于真实代码的结构化入职文档
/understand-onboard
```

### 研究功能区域

```bash
/understand-chat GraphQL API 的所有入口点是什么？
/understand-explain src/graphql/resolvers/
```

### 理解不熟悉的模块

```bash
/understand-explain src/workers/queue-processor.ts
# 返回：摘要、关键函数、调用它的内容、它调用的内容、使用的概念
```

---

## 故障排除

**`/understand` 在大型仓库中超时**
- 文件分析器最多可同时运行 3 个工作进程。非常大的仓库（>50k 文件）可能需要耐心。如果之前的运行中断，请删除 `.understand-anything/` 并重新运行。

**仪表板无法打开**
- 如果从源代码工作，请先运行 `pnpm --filter @understand-anything/dashboard build`，然后重试 `/understand-dashboard`。

**主要重构后图谱过时**
- 删除 `.understand-anything/knowledge-graph.json` 以强制完整重新分析：`rm .understand-anything/knowledge-graph.json && /understand`

**`pnpm install` 因工作区错误失败**
- 确保你使用的是 pnpm v8+：`pnpm --version`。该项目使用在 `pnpm-workspace.yaml` 中定义的 pnpm 工作区。

**搜索无结果**
- 确认图已生成：`cat .understand-anything/knowledge-graph.json | head -5`。如果为空或缺失，请先运行 `/understand`。

---

## 贡献

```bash
# Fork 后：
git checkout -b feature/my-feature
pnpm --filter @understand-anything/core test   # 必须通过
# 打开 PR — 对于重大更改先提交问题
```

许可证：MIT © [Lum1104](https://github.com/Lum1104)
