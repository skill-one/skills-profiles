# 使用 GitNexus 进行重构

## 何时使用

- 安全地重命名此函数
- 将此内容提取为模块
- 分割此服务
- 将此内容移动到新文件
- 任何涉及重命名、提取、分割或重构代码的任务

## 先绑定仓库

重构会写入磁盘。使用 `rename` 并设置 `dry_run: false` 时，会编辑已解析的仓库中的文件，因此在此处绑定身份是一种安全措施，而非账本记录。

在首次调用工具前调用 `list_repos {}`。对于单个索引仓库，直接使用以下示例。对于多个仓库，每个调用都需要传递 `repo` 参数：省略 `repo` 通常会报错，但在配置了默认值的 MCP 策略下，它会静默地解析为默认值。如果你无法确定目标仓库，请停止并询问。在绑定仓库中预览后，切勿使用 `rename` 并设置 `dry_run: false` — 返回的 `file_path` 值显示即将写入的检出，因此将其视为身份确认。

`list_repos` 是分页的，因此在得出仓库不存在之前，使用 `offset: pagination.nextOffset` 分页，直到 `hasMore` 为 `false`。

`detect_changes` 在你编辑 MCP 服务器未从其启动的链接工作树时需要 `worktree`；否则 `git diff` 会运行在错误的检出中并报告未发生变化，这会被解读为已验证的重构。

## 工作流程

```
0. list_repos {}                                  → 绑定仓库（和工作树）
1. impact({target: "X", direction: "upstream"})  → 映射所有依赖项
2. query({search_query: "X"})                            → 查找涉及 X 的执行流程
3. context({name: "X"})                           → 查看所有传入/传出引用
4. 规划更新顺序：接口 → 实现 → 调用者 → 测试
```

> 如果显示 "索引已过期" → 在终端中运行 `node .gitnexus/run.cjs analyze`。
> 热工具 `staleness` 指出哪个索引已回答（`branch`/`lastCommit`）及其新鲜度（`status`）。仅对 `behind` 或 `diverged` 进行重新分析 — `current` 是身份，`unknown` 是不可测量的。

## 检查清单

### 重命名符号

```
- [ ] list_repos {} — 绑定仓库；多个索引时显式指定仓库，若模糊则询问
- [ ] rename({symbol_name: "oldName", new_name: "newName", dry_run: true}) — 预览所有修改
- [ ] 确认预览的文件路径位于绑定的仓库/工作树中
- [ ] 审查图编辑（高置信度）和文本搜索编辑（仔细审查）
- [ ] 若满意：rename({..., dry_run: false}) — 应用修改
- [ ] detect_changes() — 验证仅预期文件发生变化
- [ ] 运行受影响流程的测试
```

### 提取模块

```
- [ ] list_repos {} — 绑定仓库；多个索引时显式指定仓库，若模糊则询问
- [ ] context({name: target}) — 查看所有传入/传出引用
- [ ] impact({target, direction: "upstream"}) — 查找所有外部调用者
- [ ] 定义新模块接口
- [ ] 提取代码，更新导入
- [ ] detect_changes() — 验证受影响范围
- [ ] 运行受影响流程的测试
```

### 分割函数/服务

```
- [ ] list_repos {} — 绑定仓库；多个索引时显式指定仓库，若模糊则询问
- [ ] context({name: target}) — 理解所有被调用者
- [ ] 按职责分组被调用者
- [ ] impact({target, direction: "upstream"}) — 映射调用者以更新
- [ ] 创建新函数/服务
- [ ] 更新调用者
- [ ] detect_changes() — 验证受影响范围
- [ ] 运行受影响流程的测试
```

## 工具

**rename** — 自动多文件重命名：

```
rename({symbol_name: "validateUser", new_name: "authenticateUser", repo: "my-app", dry_run: true})
→ 12 次修改跨越 8 个文件
→ 10 次图编辑（高置信度），2 次文本搜索编辑（审查）
→ 修改：[{file_path, edits: [{line, old_text, new_text, confidence}]}]
```

**impact** — 首先映射所有依赖项：

```
impact({target: "validateUser", repo: "my-app", direction: "upstream"})
→ d=1: loginHandler, apiMiddleware, testUtils
→ 受影响流程：LoginFlow, TokenRefresh
```

**detect_changes** — 重构后验证你的修改：

```
detect_changes({scope: "all"})
→ 变更：8 个文件，12 个符号
→ 受影响流程：LoginFlow, TokenRefresh
→ 风险：中等
```

`partial: true`（图查询失败）或 `truncated: true`（变更符号列表被截断）表示结果不完整：短或空列表并非证明仅预期文件发生变化。重新运行它，而不是将重构视为已验证。

错误的零工作树不带任何标志，且与干净的验证无法区分，因此请确认差异的检出是你编辑的那个。

**cypher** — 自定义引用查询：

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "validateUser"})
RETURN caller.name, caller.filePath ORDER BY caller.filePath
```

## 风险规则

| 风险因素         | 缓解措施                                |
| ------------------- | ----------------------------------------- |
| 调用者过多 (>5)   | 使用 rename 进行自动更新 |
| 跨领域引用     | 使用 detect_changes 后验证范围  |
| 字符串/动态引用 | query 查找它们               |
| 外部/公共 API | 正确版本和弃用            |
| 另一个索引仓库中的同名符号 | 绑定 `repo`；应用前验证预览路径 |

## 示例：将 `validateUser` 重命名为 `authenticateUser`

```
0. list_repos {}
   → 总计：2 (my-app, billing-api) — 两者都定义了 validateUser，因此显式绑定

1. rename({symbol_name: "validateUser", new_name: "authenticateUser", repo: "my-app", dry_run: true})
   → 12 次修改：10 次图（安全），2 次文本搜索（审查）
   → 文件：validator.ts, login.ts, middleware.ts, config.json...

2. 审查文本搜索修改（config.json：动态引用！）

3. rename({symbol_name: "validateUser", new_name: "authenticateUser", repo: "my-app", dry_run: false})
   → 应用 12 次修改跨越 8 个文件

4. detect_changes({scope: "all", repo: "my-app"})
   → 受影响：LoginFlow, TokenRefresh
   → 风险：中等 — 运行这些流程的测试
   仓库：my-app (/abs/path/my-app)  工作树：相同  索引：当前
```

对于单个索引仓库，步骤 0 返回 `total: 1`，并且上述每个调用中的 `repo` 参数都会被省略。
