# 使用 GitNexus 进行影响分析

## 使用场景

- "修改这个函数安全吗？"
- "如果我修改 X 会出什么问题？"
- "显示影响范围"
- "谁在使用这段代码？"
- 在进行非平凡的代码修改前
- 在提交前——了解你的修改会影响什么

## 首先绑定仓库

影响分析是授权编辑的关卡，因此它必须针对你即将编辑的仓库进行回答。

在首次调用工具前调用 `list_repos {}`。对于单个索引仓库，直接使用以下示例。对于多个仓库，在每次调用时传递 `repo`：省略 `repo` 通常会报错，但在配置了默认值的 MCP 策略下会静默解析为默认值。如果你无法确定目标仓库，请停止并询问——对于模糊标识的结果，以下所有结果都会继承这种模糊性。`list_repos` 是分页的，所以在得出仓库不存在的结论前，使用 `offset: pagination.nextOffset` 分页，直到 `hasMore` 为假。

`detect_changes` 在你的修改位于 MCP 服务器未从其启动的链接工作树中时需要 `worktree`。服务器仅在从工作树内部启动时自动检测工作树；否则 `git diff` 在错误的检出中运行并报告零个变更符号——这是一个不携带以下描述的降级标志的虚假干净检查。在 CLI 降级方案中，`--repo .` 表示当前检出；当你不在其中时，请传递预期的仓库路径。

在风险报告中声明绑定的标识：

```
仓库: <名称> (<路径>)   工作树: <路径>   索引: <提交>, <n> 落后 HEAD
```

## 工作流程

```
0. list_repos {}                                           → 绑定仓库（和工作树）
1. impact({target: "X", direction: "upstream"}) 或 `node .gitnexus/run.cjs impact "X" --direction upstream --repo .`
2. READ gitnexus://repo/{name}/processes                   → 检查受影响的执行流程
3. detect_changes({scope: "all"}) 或 `node .gitnexus/run.cjs detect-changes --scope all --repo .`
4. 评估风险并向用户报告，同时回显仓库/工作树/索引标识
```

> 如果 "索引已过时" → 在终端中运行 `node .gitnexus/run.cjs analyze`。
> 热工具 `staleness` 指出哪个索引回答了（`branch`/`lastCommit`）以及它的新鲜程度（`status`）。仅对 `behind` 或 `diverged` 进行重新分析——`current` 是标识，`unknown` 是不可测量的。
> 如果 `.gitnexus/run.cjs` 缺失，在降级命令中将 `node .gitnexus/run.cjs` 替换为 `npx gitnexus`。

## 检查清单

```
- [ ] list_repos {} — 绑定仓库；当索引 >1 时显式指定仓库，如果模糊则询问
- [ ] impact({target, direction: "upstream"}) 或 CLI 降级方案以查找依赖项
- [ ] 首先审查 d=1 项（这些 WILL BREAK）
- [ ] 检查高置信度 (>0.8) 的依赖项
- [ ] READ processes 以检查受影响的执行流程
- [ ] detect_changes({scope: "all"}) 或 CLI 降级方案用于预提交检查
- [ ] 确认你编辑的检出是进行 diff 的检出
- [ ] 评估风险等级并报告，声明仓库/工作树/索引标识
```

## 理解输出

| 深度 | 风险等级       | 含义                  |
| ----- | ---------------- | ------------------------ |
| d=1   | **WILL BREAK**   | 直接调用者/导入者      |
| d=2   | LIKELY AFFECTED  | 间接依赖项            |
| d=3   | MAY NEED TESTING | 传递效应               |

## 风险评估

| 受影响                       | 风险     |
| ------------------------------ | -------- |
| <5 个符号，少量流程      | 低      |
| 5-15 个符号，2-5 个流程    | 中等   |
| >15 个符号或大量流程  | 高     |
| 关键路径（认证、支付） | 危险     |
| **未找到调用者**         | **未知** |

`未知` 在这个等级上不是低级别——它意味着无法回答。空的调用集与 "确实未使用" 和 "调用者无法通过索引解析"（普通对象属性访问、动态分发、跨语言调用）同样一致，因此少量调用 ⇒ 低不适用。结果会附带 `riskNote` 说明这一点。在文本搜索前确认，在将符号视为安全修改或删除前不要将其视为安全。

`risk` 是编辑关卡：对高/危险发出警告，对未知停止，直到不确定性解决。在单仓库模式下，比较文件和符号目标与本地 `riskSharedAxes`（直接/总计仅）。在组模式下，仅比较组结果：它们的 `riskSharedAxes` 在该本地值上叠加解析的跨仓库交叉。永远不要使用这些字段来豁免编辑关卡。在比较类型前检查 `riskScale.unusedAxes`：MCP 文件遍历省略流程/模块轴，而 Web Graph-RAG 在丰富前将文件目标扩展为文件内符号。

## 工具

**impact** — 符号影响范围的主要工具。如果 MCP 不可用，使用 `node .gitnexus/run.cjs impact <符号> --direction upstream --repo .` 代替：

```
impact({
  target: "validateUser",
  repo: "my-app",          // 一旦索引 >1 个仓库后必须
  direction: "upstream",
  minConfidence: 0.8,
  maxDepth: 3
})

→ d=1 (WILL BREAK):
  - loginHandler (src/auth/login.ts:42) [CALLS, 100%]
  - apiMiddleware (src/api/middleware.ts:15) [CALLS, 100%]

→ d=2 (LIKELY AFFECTED):
  - authRouter (src/routes/auth.ts:22) [CALLS, 95%]
```

**detect_changes** — 基于 git-diff 的影响分析。如果 MCP 不可用，使用 `node .gitnexus/run.cjs detect-changes --scope all --repo .` 代替：

```
detect_changes({scope: "all"})

→ 变更: 3 个文件中的 5 个符号
→ 受影响: LoginFlow, TokenRefresh, APIMiddlewarePipeline
→ 风险: 中等
```

一旦索引超过一个仓库，再添加一次 `repo`，当你的修改位于服务器未从其启动的链接工作树中时添加 `worktree: "<绝对路径>"`。

`partial: true`（图查询失败）或 `truncated: true`（变更符号列表被截断）意味着结果不完整，类似于上面的 `UNKNOWN`：零表示未看到，而不是未受影响。重新运行它而不是勾选预提交检查。

错误工作树的零不携带任何标志，与真实的干净结果形状相同，因此在进行空变更集检查前确认你编辑的检出是进行 diff 的检出。

## 示例："修改 validateUser 会出什么问题？"

```
0. list_repos {}
   → 总计: 2 (my-app, billing-api) — 两者都定义了 validateUser，因此显式绑定

1. impact({target: "validateUser", repo: "my-app", direction: "upstream"}) 或 `node .gitnexus/run.cjs impact "validateUser" --direction upstream --repo .`
   → d=1: loginHandler, apiMiddleware (WILL BREAK)
   → d=2: authRouter, sessionManager (LIKELY AFFECTED)

2. READ gitnexus://repo/my-app/processes
   → LoginFlow 和 TokenRefresh 触发 validateUser

3. 风险: 2 个直接调用者，2 个流程 = 中等
   仓库: my-app (/绝对路径/my-app)  工作树: 相同  索引: 当前
```

对于单个索引仓库，步骤 0 返回 `total: 1`，并且上述所有调用中的 `repo` 参数都会消失。
