# Swarm

并行处理多个独立项。`create` 构建一个表格句柄；`run` 将工作分配到各行并合并结果。一行 = 一个工作单元 — swarm 自动处理批处理。

## 流程

1. **创建。** 从源构建表格 — 文件、通配符模式或预解析的记录。每项一个行。返回一个句柄。
2. **运行。** 将`指令`模板分配到各行。结果合并回表格。返回`{ completed, failed, skipped, failures }`。
3. **聚合。** 使用`rows()`和普通JS进行计数、过滤或汇总。不要为聚合创建额外的子代理。
4. **重试。** 使用`filter: { column: "<col>", exists: false }`重新运行，仅重新处理失败的行。

## 选择数据源

**`glob` / `filePaths`** — 一个文件 = 一个行。使用每个文件是一个独立工作单元时。每行获得`{ id, file }`；子代理通过`{file}`占位符读取文件。

**`tasks`** — 直接传递预构建的记录。使用数据保存在文件中（JSONL、CSV、JSON数组）。在`eval`中首先读取和解析文件，然后传递记录。一条记录 = 一个行 — 不要将多个项组合成一个行。

对于小文件（少于~500行），在一个块中解析和创建：

```javascript
const { create } = await import("@/skills/swarm");
const raw = await tools.readFile({ file_path: "/data.jsonl" });
const records = raw.trim().split("\n").map(l => JSON.parse(l));
const table = await create({ tasks: records });
console.log(table);
```

对于大文件，分块读取500行以避免截断：

```javascript
const { create } = await import("@/skills/swarm");
let records = [];
let offset = 0;
while (true) {
  const chunk = await tools.readFile({ file_path: "/data.txt", offset, limit: 500 });
  const lines = chunk.split("\n").filter(l => l.trim());
  for (const l of lines) { records.push({ id: `r${records.length}`, text: l }); }
  if (lines.length < 500) break;
  offset += 500;
}
const table = await create({ tasks: records });
console.log(table);
```

当文件太大无法在一个`eval`调用中解析和分配时，分成两个块。只有调用swarm函数的块需要导入：

```javascript
// eval 1: 仅解析 — 无需导入swarm
const raw = await tools.readFile({ file_path: "/data.jsonl" });
globalThis.records = raw.trim().split("\n").map(l => JSON.parse(l));
console.log(`解析了 ${globalThis.records.length} 条记录`);
```

```javascript
// eval 2: 创建和分配
const { create, run } = await import("@/skills/swarm");
const table = await create({ tasks: globalThis.records });
const result = await run(table.id, {
  instruction: "分类 {text}",
  responseSchema: {
    type: "object",
    properties: { label: { type: "string" } },
    required: ["label"],
  },
});
console.log(result);
```

传递`filePaths: ["/data.jsonl"]`将生成一个**一行**指向文件的表格 — 不是一行每条记录。

## 何时使用`subagentType`

省略`subagentType`用于分类、提取、标记和任何单个模型调用即可完成结构化输出的任务。这是默认值，显著更便宜更快 — 每次分配都是直接模型调用，无需工具，无需迭代。

设置`subagentType`当任务需要工具、文件访问或多步推理时。每次分配运行一个完整的代理循环，使用命名的子代理。

```javascript
// 直接模型调用 — 分类，无需工具
await run(table.id, {
  instruction: "分类 {text}",
  responseSchema: { type: "object", properties: { label: { type: "string" } }, required: ["label"] },
});

// 子代理 — 需要读取文件和多步推理
await run(table.id, {
  subagentType: "reviewer",
  instruction: "检查 {file} 的安全问题。",
  responseSchema: { type: "object", properties: { finding: { type: "string" } }, required: ["finding"] },
});
```

## 指令 + 上下文

`instruction` 是一个每项模板，包含`{column}`占位符。占位符由框架解析 — 你的列名在提示中作为值列表的引用出现，而不是原始模板语法。子代理执行工作 — 不要在JS中自行处理项并写入行。

`context` 是附加到每个子代理提示的自由文本。用于共享背景：领域术语、分类规则、示例等。

```javascript
const { create, run } = await import("@/skills/swarm");

const table = await create({ glob: "src/**/*.ts" });
const r = await run(table.id, {
  subagentType: "reviewer",
  instruction: "检查 {file} 的安全问题。列出发现或写入'无问题'。",
  context: "TypeScript Express后端使用Prisma ORM。重点关注注入、认证绕过、路径遍历。",
  responseSchema: {
    type: "object",
    properties: { review: { type: "string" } },
    required: ["review"],
  },
});
console.log(r);
// → { completed: 45, failed: 2, skipped: 0, failures: [...] }
```

## 结构化输出

`responseSchema` 是必需的。模式属性成为每行的顶级列，并限制子代理可以返回的内容。

```javascript
const { run } = await import("@/skills/swarm");
await run(table.id, {
  instruction: "分类：{text}",
  responseSchema: {
    type: "object",
    properties: {
      sentiment: { type: "string", enum: ["positive", "negative", "neutral"] },
    },
    required: ["sentiment"],
  },
});
// 行后：{ id: "r1", text: "...", sentiment: "positive" }
```

## 批处理

默认情况下，swarm自动批处理以保持总分配次数少于10。对于小表格（≤10行）每行都有自己的子代理调用。对于较大的表格，行会自动分组。

设置`batchSize`以控制分组：

- **数字** — 所有行的统一批处理大小。`batchSize: 1`强制逐行分配；`batchSize: 20`二十个一组。
- **函数** — `(row, rowCount) => number`。返回每行所需的批处理大小。具有相同批处理大小的行会分组，然后分块。允许混合分配，其中一些行单独分配，其他行分组。

```javascript
const { create, run } = await import("@/skills/swarm");
const table = await create({ tasks: items });

// 复杂项获得单独关注；简单项一起批处理
await run(table.id, {
  instruction: "分析 {text}",
  responseSchema: {
    type: "object",
    properties: { analysis: { type: "string" } },
    required: ["analysis"],
  },
  batchSize: (row) => (row.token_count > 1000 ? 1 : 10),
});
```

批处理大小在评估后限制在[1, 50]。

## 聚合

在`run()`后，使用`rows()`和普通JS — 无需额外的子代理。

```javascript
const { rows } = await import("@/skills/swarm");
const data = await rows(table.id, { columns: ["sentiment"] });
const counts = {};
data.forEach(r => { counts[r.sentiment] = (counts[r.sentiment] || 0) + 1 });
console.log(counts);
// → { positive: 120, negative: 45, neutral: 35 }
```

## 链式传递

`run`原地更新表格 — 链式调用以累积列。

```javascript
const { create, run } = await import("@/skills/swarm");
const table = await create({ tasks: interviews });
await run(table.id, {
  instruction: "分类 {text} 的情感",
  responseSchema: {
    type: "object",
    properties: { sentiment: { type: "string", enum: ["positive", "negative", "neutral"] } },
    required: ["sentiment"],
  },
});
await run(table.id, {
  filter: { column: "sentiment", equals: "negative" },
  instruction: "总结为什么 {text} 有负面情感。",
  responseSchema: {
    type: "object",
    properties: { summary: { type: "string" } },
    required: ["summary"],
  },
});
```

## 仅动作任务

当子代理执行动作（写入文件、应用修复）而不是返回数据时，使用简单的模式，包含状态或标记字段。`exists: false`过滤器仍然适用于重试。

```javascript
const { create, run } = await import("@/skills/swarm");
const fixedSchema = {
  type: "object",
  properties: { fixed: { type: "string" } },
  required: ["fixed"],
};
const table = await create({ glob: "src/**/*.ts" });
await run(table.id, {
  subagentType: "fixer",
  instruction: "为 {file} 中所有导出的函数添加缺失的JSDoc。",
  responseSchema: fixedSchema,
});
// 重试任何失败的
await run(table.id, {
  subagentType: "fixer",
  instruction: "为 {file} 中所有导出的函数添加缺失的JSDoc。",
  responseSchema: fixedSchema,
  filter: { column: "fixed", exists: false },
});
```

## 过滤

```javascript
{ column: "status", equals: "done" }
{ column: "status", notEquals: "done" }
{ column: "category", in: ["A", "B"] }
{ column: "result", exists: false }      // 尚未处理
{ and: [filter1, filter2] }
{ or: [filter1, filter2] }
```

## 技术说明

- **仅在调用swarm函数的块中导入`@/skills/swarm`。**
  数据准备（读取文件、解析、存储在`globalThis`）不需要导入。解构你使用的部分：`{ create }`，`{ run }`，`{ create, run }`等。
- **控制台输出限制在~5 KB。** 从不记录原始文件内容 — 仅记录计数和短样本。
- **`eval`中的`readFile`返回原始内容 — 无行号前缀。** 每次调用最多请求500行。对于超过500行的文件，使用递增的`offset`循环。
- **从文件构建表格时，在`eval`中读取。** 在沙盒中读取的数据保留在那里；它永远不会进入代理的上下文窗口。
- **不要直接写入`.swarm/`。** 始终使用`create()`。
- **子代理需要的所有内容必须在`instruction` + `context`中。**
  子代理看不到代理的上下文。
- **行ID必须唯一。** `create()`拒绝产生重复ID的源。对于`tasks`，这是调用者的责任；对于`glob` / `filePaths`，ID由父目录自动消除歧义。
- **未知列快速失败。** 如果`instruction`引用`{foo}`且没有匹配的行提供`foo`，`run()`在分配任何子代理之前抛出异常。

## API参考

### `create(source)`

创建表格。返回一个句柄`{ id, count, columns }`。

| 源 | 描述 |
|----|------|
| `{ glob: "src/**/*.ts" }` 或 `{ glob: ["src/**/*.ts", "lib/**/*.ts"] }` | 通过一个或多个模式匹配文件。列：`id`，`file` |
| `{ filePaths: ["a.ts", "b.ts"] }` | 显式文件列表。列：`id`，`file` |
| `{ tasks: [{ id: "t1", text: "..." }] }` | 自定义行。每个必须具有`id` |

### `run(tableId, options)`

跨行分配工作。返回`{ completed, failed, skipped, failures }`。

| 选项 | 默认 | 描述 |
|------|------|------|
| `instruction` | (必需) | 包含`{column}`占位符的模板 |
| `responseSchema` | (必需) | JSON模式(`type: "object"`) — 属性成为行列 |
| `context` | — | 附加到每个子代理提示的自由文本 |
| `filter` | — | 仅分配匹配的行 |
| `subagentType` | — | 要分配的子代理的名称。设置时，运行完整的代理循环。省略时，运行直接模型调用 |
| `batchSize` | auto | 数字或`(row, rowCount) => number`。自动限制分配次数为10；`1` = 逐行；函数 = 逐行大小 |
| `concurrency` | `10` | 最大并发子代理分配（限制为1–10） |

### `rows(tableId, options?)`

检索行。用于检查和基于JS的聚合。

| 选项 | 描述 |
|------|------|
| `filter` | 仅返回匹配的行 |
| `columns` | 投影到特定列 |
| `limit` | 返回的最大行数 |
