# .NET 工作流精通

## 核心原则

1. **并行优于顺序** — 使用 git worktrees 同时运行 3-5 个 Claude 会话。在一个会话中构建功能，在另一个会话中修复 Bug，在第三个会话中运行测试。这是最大的生产力解锁方式。
2. **先计划再执行** — 对于任何非平凡的任务，先进入计划模式，迭代直到计划无懈可击，然后切换到自动接受。一个好的计划意味着 Claude 可以单次就完成实现。
3. **验证形成闭环** — 给 Claude 提供证明其工作的方式：`dotnet build`，`dotnet test`，通过 MCP 的 `get_diagnostics`。这一单一实践可以将输出质量提升 2-3 倍。
4. **上下文是一种预算，而不是倾倒场** — 上下文窗口很快就会填满：一个典型的 .cs 文件是 500-2000 个 token，50 次文件读取会消耗大量预算。像冲刺容量一样有意识地使用 token。
5. **自动化重复性工作** — 如果你每天做多次，就把它做成钩子、斜杠命令或子代理。预先允许安全权限。消除摩擦。
6. **积累知识** — 每次更正都成为 `MEMORY.md` 中的规则（参见 `instinct-system` 技能）。每次 PR 审查都增加学习。随着时间的推移，Claude 的错误率会下降，因为你的项目知识库在增长。

## 模式

### 使用 Git Worktrees 的并行会话

最大的生产力倍增器。每个 worktree 都有自己的 Claude 会话，自己的文件，零冲突。

```bash
# 创建用于并行工作的 worktrees
git worktree add ../my-project-feature origin/main
git worktree add ../my-project-bugfix origin/main
git worktree add ../my-project-tests origin/main

# 在每个（单独的终端标签页）中启动 Claude
cd ../my-project-feature && claude
cd ../my-project-bugfix && claude
cd ../my-project-tests && claude
```

**实用的 .NET 工作流：**

| Worktree | 任务 | Claude 会话 |
|----------|------|---------------|
| `feature` | 构建新的端点 + 处理器 | 主要开发 |
| `bugfix` | 修复失败的 CI 测试 | 自动化 Bug 修复 |
| `tests` | 为现有功能编写集成测试 | 测试生成 |
| `analysis` | 查询 Roslyn MCP，读取日志，审查架构 | 只读研究 |

**技巧：**
- 通过任务命名终端标签页，以免丢失
- 使用 shell 别名（`alias zf='cd ../my-project-feature'`）实现一键切换
- 启用终端通知，以便知道何时需要输入

### .NET 自动格式化钩子

在每次文件写入时捕获格式化问题——消除“CI 因格式化失败”的循环。

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "dotnet format --include \"$CLAUDE_FILE_PATH\" --no-restore 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

为什么 `|| true`：钩子不应阻塞 Claude 的工作流程。如果格式化失败（例如，在非 C# 文件上），则静默继续。

### 预允许安全的 .NET 权限

停止为每个 `dotnet` 命令点击“允许”。将这些添加到 `.claude/settings.json`：

```json
{
  "permissions": {
    "allow": [
      "Bash(dotnet build *)",
      "Bash(dotnet test *)",
      "Bash(dotnet run *)",
      "Bash(dotnet ef *)",
      "Bash(dotnet format *)",
      "Bash(dotnet restore *)",
      "Bash(dotnet pack *)",
      "Bash(dotnet tool *)"
    ]
  }
}
```

将其提交到 git，以便整个团队都能获得无摩擦的工作流程。

### 计划模式策略

对于涉及 3 个或更多文件或涉及架构决策的任何任务：

```
步骤 1：进入计划模式（Shift+Tab 两次）
步骤 2：用完整上下文描述任务
步骤 3：迭代计划——挑战假设，询问“边缘情况会怎样？”
步骤 4：一旦计划牢固，切换到正常模式
步骤 5：Claude 自动接受执行——通常单次就完成实现
```

**高级模式：** 让一个 Claude 编写计划，然后启动第二个 Claude 会话作为资深工程师进行审查：

```
"以资深 .NET 工程师的身份审查此计划。挑战每个假设。
可能出什么问题？遗漏了什么？你会怎么做不同？"
```

**当事情出错时：** 一旦实现偏离计划，立即停止。不要强行推进。切换回计划模式，理解发生了什么变化，重新计划，然后继续。

### .NET 验证循环

> 关于完整的 7 阶段验证管道（构建、诊断、反模式、测试、安全、格式化、差异审查）以及结构化 PASS/FAIL 报告，请参阅 **verify** 技能。

Boris 的 #1 技巧：“给 Claude 提供验证其工作的方式。” 简短版本：始终告诉 Claude 在声明完成之前运行 `dotnet build`，`dotnet test`，`get_diagnostics` 和 `dotnet format --verify-no-changes`。验证技能包含完整的管道，包括短路规则和报告模板。

### 通过更正积累知识

关于完整的更正捕获系统——检测、泛化、分类存储和定期审计——请参阅 **`instinct-system`** 技能。简短版本：每次更正后，在 `MEMORY.md` 中捕获一个泛化规则，以便相同的错误不再发生。

### .NET 提示技巧

**挑战 Claude 的工作：**
```
"让我 grilled 这些更改。这会通过资深 .NET 工程师的代码审查吗？
检查：N+1 查询、缺少 CancellationToken、暴露的领域实体、缺失的验证、不正确的服务生命周期。"
```

**要求证明：**
```
"证明它有效。运行测试，显示输出。
然后比较 main 和此分支之间的 API 响应。"
```

**在平庸的修复后：**
```
"知道你现在所知道的一切，放弃这个并实现优雅的解决方案。
不要使用技巧，不要使用变通方法。"
```

**对于 EF Core 迁移：**
```
"生成迁移，然后显示它产生的原始 SQL。
我想在应用它之前验证迁移。"
```

### .NET 子代理模式

套件提供 10 个专家代理——在编写自己的之前先路由到它们：
`dotnet-architect`，`code-reviewer`，`refactor-cleaner`，`test-engineer`，
`security-auditor`，`build-error-resolver`，`ef-core-specialist`，
`api-designer`，`performance-analyst`，`devops-engineer`。每个代理都携带预加载的技能和领域上下文，普通会话缺乏这些。

**使用它们：**
```
"在我创建 PR 之前，在更改上运行 code-reviewer 代理。"
"让 refactor-cleaner 简化我刚刚修改的文件。"
"将失败的 CI 日志发送到 build-error-resolver。"
```

对于套件未涵盖的工作流程，在 `.claude/agents/` 中创建特定于项目的子代理——一个包含角色、编号任务列表和所需报告格式（PASS 带摘要 / FAIL 带具体细节）的 markdown 文件。每个代理保持一个关注点，以便其输出保持可审查。

**何时卸载 vs. 保持主上下文：** 参见上下文纪律部分——子代理也是您的上下文隔离室，而不仅仅是任务运行器。

## 上下文纪律

`.claude/rules/agents.md` 中的规则已经要求 MCP 首先导航（`find_symbol` 优先于文件读取，`get_diagnostics` 优先于构建）。本节是顶层策略：如何预算、何时卸载以及如何恢复。

### Token 经济学

一个 Roslyn MCP 查询成本 30-150 个 token；一个文件读取成本 500-2000+。要理解 `OrderService`，四个 MCP 调用（`find_symbol` → `get_public_api` → `find_references` → `get_type_hierarchy`）成本约 310 个 token；读取四个相关文件成本约 2900。然后只读取您将要修改的方法。保留完整的文件读取用于您即将编辑的文件。

### 子代理卸载决策矩阵

```
卸载到子代理当：
- 探索不熟悉的代码（> 3 个文件要读取）
- 需要文档或多个文件的研究
- 详细的输出（测试运行、诊断、比较）
- 任何任务，其过程详细但答案简洁

保持主上下文当：
- 修改您已经读取的文件
- 快速查找（1-2 个 MCP 查询）
- 构建在用户正在进行的对话上的工作
```

要求子代理提供压缩答案：`"跟踪从登录到令牌验证的认证流程。返回带文件:行引用的编号步骤。"` 您会获得约 300 个 token 的发现，而不是 15k 个 token 的原始文件。

### 文件读取优先级

```
优先级 1 — 您将要修改的文件：完全读取（编辑需要精确内容）
优先级 2 — 您必须满足的契约：读取接口，跳过实现
优先级 3 — 参考模式：首先 get_public_api，如果不足则读取
优先级 4 — 一般上下文：子代理总结；主上下文中永不读取

永不读取：整个目录（get_project_graph），用于上下文的测试文件（get_test_coverage_map），生成的文件/迁移，除非需要配置
```

### 预算规划和恢复

在复杂任务之前，勾勒出支出：理解 ~5k（MCP + 子代理），计划 ~2k，实现 ~15k（读取目标 + 写入 + 迭代），验证 ~3k——将大部分窗口留给对话。

```
警告信号：10+ 个文件读取，50+ 次交换，忘记早期细节，重新读取您已经看到的文件

恢复：用 5-10 行总结您所知的内容 → 子代理进行剩余探索 → MCP 仅查找 → 如果仍然退化，建议重新会话

大型代码库（50+ 项目）：get_project_graph → 窄化为 2-3 个相关项目 → find_symbol 查找关键类型 → get_public_api 查找接口 →
只读取您将要修改的文件 → 子代理处理跨领域问题
```

### 懒加载技能

不要“以防万一”预加载技能——15 个技能，每个约 300 个 token，在开始任何工作之前就会花费 ~4500 个 token。如果相关，在会话开始时加载 `modern-csharp`；一旦主题实际出现，就拉取 `ef-core`，`testing` 等。

## 反模式

### 不要为复杂任务跳过计划模式

```
// BAD — 直接进入多文件重构
"重构 Orders 模块以使用 DDD，包含聚合和价值对象"
*Claude 修改了 15 个文件，遗漏了半个不变式，打乱了迁移*

// GOOD — 先计划，后执行
"进入计划模式。我想重构 Orders 模块以使用 DDD。
让我们计划哪些文件会更改，聚合边界是什么，
价值对象如何映射到 EF Core，以及迁移策略是什么。"
```

### 不要在可以并行化时单线程工作

```
// BAD — 单个会话中的顺序工作
1. 构建功能       (20 分钟)
2. 编写测试         (15 分钟)
3. 修复格式化      (5 分钟)
4. 更新文档         (10 分钟)
总计：50 分钟

// GOOD — 并行 worktrees
Worktree 1：构建功能     (20 分钟)
Worktree 2：编写测试       (15 分钟，同时开始)
Worktree 3：更新文档       (10 分钟，同时开始)
总计：约 20 分钟（墙上时间）
```

### 不要接受第一个解决方案

```
// BAD — 接受平庸的代码
Claude："这是实现" *通用，可以工作但不是很好*
您："看起来不错，发布它"

// GOOD — 追求质量
Claude："这是实现"
您："资深 .NET 工程师会批准这个吗？
服务生命周期是什么？这是安全的 N+1 吗？
使用 C# 14 特性是否有更优雅的方法？"
```

### 不要因为窗口很大而加载所有内容

```
// BAD — "上下文窗口很大，让我们加载所有内容"
读取 Orders 模块的 30 个文件，15 个测试文件，
docker-compose.yml，每个迁移
*在编写一行代码之前消耗了 80k 个 token*

// GOOD — 最小可行上下文
MCP：get_project_graph（解决方案形状）+ find_symbol（定位目标）
读取：您实际要修改的 2-3 个文件
子代理：总结任何其他内容
*消耗 ~3k 个 token，其余用于实际工作*
```

## 决策指南

| 情景 | 建议 |
|----------|---------------|
| 任务涉及 3 个或更多文件 | 先使用计划模式 |
| 任务是一个简单的 Bug 修复 | 直接修复，用 `dotnet test` 验证 |
| 需要构建 + 测试 + 审查 | 3 个并行 worktrees |
| CI 不断因格式化失败 | 添加 PostToolUse 格式化钩子 |
| 对权限提示感到厌倦 | 预允许 `dotnet *` 命令 |
| Claude 出错 | "更新 CLAUDE.md 以免再次犯这个错误" |
| 代码感觉是技巧 | "知道你现在所知道的一切，实现优雅的解决方案" |
| 想验证架构 | 启动第二个会话作为资深审查者 |
| 重复的 PR 工作流程 | 路由到套件代理（code-reviewer，refactor-cleaner）或创建项目子代理 |
| 学习新代码库 | 通过 `/config` 使用 "Explanatory" 输出样式 |
| 需要类型的 API 或位置 | `get_public_api` / `find_symbol`——不要读取文件 |
| 需要修改文件 | 完全读取它——需要精确内容 |
| 探索不熟悉的代码 | 创建子代理——保持主上下文干净 |
| 会话中读取了 10 个以上文件 | 暂停——切换到 MCP + 子代理 |
| 上下文感觉沉重或缓慢 | 总结您所知的内容，后续使用子代理 |
| 大型代码库（50+ 项目） | MCP 首先导航，子代理密集，只读取您修改的文件 |
| 会话中途出现新主题 | 按需加载相关技能，而不是预先加载 |
