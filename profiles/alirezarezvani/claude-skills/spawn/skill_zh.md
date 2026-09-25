# /hub:spawn — 启动并行代理

启动 N 个子代理并行处理同一任务，每个代理在一个隔离的 git 工作树中运行。

## 使用方法

```
/hub:spawn                                    # 为最新会话启动代理
/hub:spawn 20260317-143022                    # 为特定会话启动代理
/hub:spawn --template optimizer               # 使用 optimizer 模板进行调度提示
/hub:spawn --template refactorer              # 使用 refactorer 模板
```

## 模板

当提供 `--template <name>` 时，将使用 `../agenthub/references/agent-templates.md` 中的调度提示，而不是默认提示。可用模板：

| 模板     | 模式     | 用例             |
|----------|---------|------------------|
| `optimizer` | 编辑 → 评估 → 保留/丢弃 → 重复 10 次 | 性能、延迟、大小优化 |
| `refactorer` | 重构 → 测试 → 直至绿色迭代 | 代码质量、技术债务 |
| `test-writer` | 编写测试 → 测量覆盖率 → 重复 | 测试覆盖率差距 |
| `bug-fixer` | 复现 → 诊断 → 修复 → 验证 | 具有竞争方法的错误修复 |

使用模板时，将所有 `{variables}` 替换为会话配置中的值。为每个代理分配一个适合模板和任务的**不同策略**，多样化的策略最大化并行探索的价值。

## 功能说明

1. 从 `.agenthub/sessions/{session-id}/config.yaml` 加载会话配置
2. 对每个代理 1..N：
   - 将任务分配写入 `.agenthub/board/dispatch/`
   - 使用任务、约束和板写入指令构建代理提示
3. 使用**单个消息**启动所有代理，包含多个 Agent 工具调用：

```
Agent(
  prompt: "你是 hub 会话 {session-id} 中的代理-{i}。

你的任务：{task}

在 .agenthub/board/dispatch/{seq}-agent-{i}.md 中阅读你的完整分配

指令：
1. 在你的工作树中工作 — 进行更改、运行测试、迭代
2. 提交所有更改并附带描述性信息
3. 将你的结果摘要写入 .agenthub/board/results/agent-{i}-result.md
   包括：采取的方法、更改的文件、指标（如果可用）、置信度
4. 完成时退出

约束：
- 不要读取或修改其他代理的工作
- 不要访问 .agenthub/board/results/ 中的其他代理
- 提交时附带描述性信息
- 如果你遇到死胡同，提交你已有的内容并在结果中解释",
  isolation: "worktree"
)
```

4. 通过以下命令更新会话状态为 `running`：

```bash
python {skill_path}/scripts/session_manager.py --update {session-id} --state running
```

## 关键规则

- **所有代理在一条消息中** — 同时启动所有 Agent 工具调用以实现真正的并行
- **isolation: "worktree"** 是强制性的 — 每个代理需要自己的文件系统
- **启动后不要修改会话配置** — 代理依赖稳定的配置
- **每个代理获得一个唯一的板发布** — 分配帖子按顺序编号

## 启动后

告知用户：
- 并行启动了 {N} 个代理
- 每个代理在一个隔离的工作树中运行
- 使用 `/hub:hub-status` 监控
- 完成时使用 `/hub:eval` 评估
