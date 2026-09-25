> **⚠️ 警告**：此技能已被弃用，取而代之的是使用 Python 协调器脚本的新命令 `ralph-loop-v2`。 
> 旧的 `/specs:ralph-loop` 命令将很快被移除。请迁移到新命令。
# Ralph Loop — Python 协调器

⚠️ **重要**：此技能使用 Python 协调器脚本。请勿执行任意 bash 命令。仅使用 `Bash` 来运行 `ralph_loop.py`。所有任务命令（如 `/developer-kit-specs:specs.task-implementation`）都显示给用户以手动执行。

## 概述

Ralph Loop 将 Geoffrey Huntley 的 "Ralph Wiggum 作为软件工程师" 技术应用于规范驱动开发。它使用一个 **Python 协调器脚本**，该脚本管理一个状态机：一次调用 = 一步，状态保存在 `fix_plan.json` 中。

**关键洞察**：一次实现 + 审查 + 同步会爆炸上下文窗口。解决方案：每个循环迭代只做一步，保存状态到 `fix_plan.json`，然后停止。下一次迭代从保存的状态恢复。

**关键改进**：Python 脚本 `ralph_loop.py` 处理所有状态管理、任务选择和命令生成。它不直接执行任务命令 — 它在您的 CLI 中显示您应执行的正确命令。

## 何时使用

- 用户运行 `/loop` 命令进行周期性自动化
- 用户要求“自动化实现”或“循环运行任务”
- 用户希望“逐步迭代任务”或“运行工作流自动化”
- 用户需要在多个 SDD 命令之间进行“上下文窗口管理”
- 用户希望“处理从 TASK-N 到 TASK-M 的任务范围”
- 用户需要多代理支持（不同 CLI 用于不同任务）

## 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ralph_loop.py │────▶│   fix_plan.json │────▶│  User executes  │
│   (协调器)      │     │   (状态文件)  │     │  命令 in CLI   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         │                                               ▼
         │                                      ┌─────────────────┐
         └──────────────────────────────────────│   任务结果   │
                                                │   (成功/     │
                                                │   失败)      │
                                                └─────────────────┘
```

**一步流程**：
1. 运行 `ralph_loop.py --action=loop`
2. 脚本读取 `fix_plan.json` 并确定当前步骤
3. 脚本显示要执行的命令（例如，`/developer-kit-specs:specs.task-implementation`）
4. 用户在他们的 CLI 中执行命令
5. 用户再次运行 `ralph_loop.py --action=loop`
6. 脚本根据结果更新状态并显示下一个命令

## 状态机

```
fix_plan.json 状态机：
┌─────────────────────────────────────────────────────────────┐
│  state: "init"                                            │
│    → --action=start: 初始化 fix_plan.json                  │
│    → 从 spec 文件夹中的 tasks/TASK-*.md 文件加载任务        │
│    → 应用 task_range 过滤器                              │
│                                                             │
│  state: "choose_task"                                      │
│    → 选择下一个待处理任务（在范围内，依赖满足）              │
│    → 范围内无任务 → state: "complete"                     │
│    → 找到任务 → state: "implementation"                  │
│                                                             │
│  state: "implementation"                                  │
│    → 显示 /developer-kit-specs:specs.task-implementation 命令             │
│    → 用户执行，然后再次运行 loop                          │
│    → 下一个状态: "review"                                │
│                                                             │
│  state: "review"                                          ││    → 显示 /developer-kit-specs:specs.task-implementation --action=cleanup 命令│},{find:                    │
│    → 用户审查结果，然后再次运行 loop                      │
│    → 发现问题 → state: "fix" (重试 ≤ 3)                 │
│    → 清洁 → state: "cleanup"                            │
│                                                             │
│  state: "fix"                                             │
│    → 显示修复问题的命令                         │
│    → 用户应用修复，然后再次运行 loop            │
│    → 下一个状态: "review"                                │
│                                                             │
│  state: "cleanup"                                         │
│    → 显示 /developer-kit-specs:specs.task-implementation --action=cleanup 命令│
│    → 下一个状态: "sync"                                  │
│                                                             │
│  state: "sync"                                            │
│    → 显示 /developer-kit-specs:specs.sync 命令             │
│    → 下一个状态: "update_done"                           │
│                                                             │
│  state: "update_done"                                     │
│    → 标记任务完成，提交 git 变更                  │
│    → 重新评估依赖关系                            │
│    → state: "choose_task"                                │
│                                                             │
│  state: "complete" | "failed"                            │
│    → 打印结果，停止                                   │
└─────────────────────────────────────────────────────────────┘
```

## 文件位置要求

**⚠️ 关键**：`fix_plan.json` 文件必须始终位于：

```
docs/specs/[ID-feature]/_ralph_loop/fix_plan.json
```

这是由脚本强制执行的，以防止 LLM 在错误位置创建文件。

**迁移**：如果您在 spec 文件夹的根目录下有一个旧的 `fix_plan.json`，脚本将在第一次运行时自动将其迁移到 `_ralph_loop/`。

## 说明

### 第一阶段：初始化

使用 `--action=start` 运行 Python 脚本扫描任务文件并在正确位置创建 `fix_plan.json`：

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 \
  --to-task=TASK-041
```

### 第二阶段：执行循环步骤

使用 `--action=loop` 运行脚本以获取当前状态和要执行的命令：

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-feature/
```

脚本将显示当前步骤的精确命令。在您的 CLI 中执行它，然后再次运行循环命令。

### 第三阶段：手动推进状态

执行显示的命令后，手动推进到下一步：

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=next \
  --spec=docs/specs/001-feature/
```

这将更新 `fix_plan.json` 到下一个状态（例如，`implementation` → `review`）。

### 第四阶段：监控进度

随时使用 `--action=status` 检查状态：

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=status \
  --spec=docs/specs/001-feature/
```

## 快速入门

### 1. 初始化

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-036 \
  --to-task=TASK-041 \
  --agent=claude
```

### 2. 运行循环

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-feature/
```

脚本将显示您要执行的命令。执行它，然后再次运行循环。

### 3. 检查状态

```bash
python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=status \
  --spec=docs/specs/001-feature/
```

## 参数

| 参数 | 描述 |
|----------|-------------|
| `--action` | `start` (初始化), `loop` (运行一步), `status`, `resume`, `next` (推进步骤) |
| `--spec` | Spec 文件夹路径 (例如 `docs/specs/001-feature/`) |
| `--from-task` | 任务范围的开始 (例如 `TASK-036`) |
| `--to-task` | 任务范围的结束 (例如 `TASK-041`) |
| `--agent` | 默认代理: `claude`, `codex`, `copilot`, `kimi`, `gemini`, `glm4`, `minimax` |
| `--no-commit` | 跳过 git 提交 (用于测试) |

## 步骤详情

### 第一步：初始化 (`--action=start`)

脚本：
1. 扫描 spec 文件夹中的 `tasks/TASK-*.md` 文件
2. 从 YAML 前置部分提取元数据（id、标题、状态、语言、依赖关系、代理）
3. 应用 `--from-task` 和 `--to-task` 过滤器
4. 创建 `fix_plan.json` 并保存完整状态

### 第二步：选择任务 (`choose_task`)

脚本：
1. 查找范围内的待处理任务
2. 检查依赖关系是否满足
3. 选择下一个任务
4. 更新 `fix_plan.json` 中的 `current_task`
5. 显示要执行的命令

### 第三步：实现 (`implementation`)

脚本显示：
```
→ 实现: TASK-037

执行:
  /developer-kit-specs:specs.task-implementation --task=TASK-037

执行后，更新状态:
  python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

### 第四步：审查 (`review`)

脚本显示：
```
→ 审查: TASK-037 | 重试: 0/3

执行:
  /developer-kit-specs:specs.task-review --task=TASK-037

审查生成的审查报告，然后更新状态:
  python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
```

### 第五步：修复 (`fix`) - 如果审查失败

如果发现问题，脚本将显示修复说明。修复后，用户再次运行 loop。

### 第六步：清理 (`cleanup`)

脚本显示：
```
→ 清理: TASK-037

执行:
  /developer-kit-specs:specs.task-implementation --task=TASK-037 --action=cleanup
```

### 第七步：同步 (`sync`)

脚本显示：
```
→ 同步: TASK-037

执行:
  /developer-kit-specs:specs.sync docs/specs/001-feature/ --after-task=TASK-037
```

### 第八步：更新完成 (`update_done`)

脚本：
1. 在 `fix_plan.json` 中将任务标记为完成
2. 提交 git 变更（除非 `--no-commit`）
3. 更新迭代计数
4. 返回 `choose_task`

## 多代理支持

### 所有任务的默认代理

```bash
python3 ralph_loop.py --action=start --spec=... --agent=codex
```

### 每个任务的代理

在任务文件的 YAML 前置部分指定代理：

```yaml
---
id: TASK-036
title: 重构用户服务
status: pending
lang: java
agent: codex
---
```

支持的代理: `claude`, `codex`, `copilot`, `kimi`, `gemini`, `glm4`, `minimax`

## 与 /loop (Claude 代码) 一起使用

对于每 5 分钟自动调度：

```bash
/loop 5m python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/001-feature/
```

这将反复运行循环，每次显示下一个命令。

**注意**：Ralph Loop 现在直接通过 Python 脚本管理。已弃用的 `/developer-kit-specs:specs.ralph-loop` 命令已被移除。

## 任务文件格式

每个任务应为单独文件：`tasks/TASK-XXX.md`

```markdown
---
id: TASK-036
title: 实现用户认证
status: pending
lang: java
dependencies: []
complexity: medium
agent: claude
---

## 描述

为 API 实现基于 JWT 的认证。

## 接受标准

- [ ] 登录端点返回 JWT 令牌
- [ ] 令牌验证中间件
- [ ] 刷新令牌机制
```

## 示例

### 示例 1：基本用法

```bash
# 初始化
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --from-task=TASK-001 \
  --to-task=TASK-005

# 循环直到完成
while true; do
  python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
  # 手动执行显示的命令
  # 然后继续循环
done
```

### 示例 2：与 Claude 代码 /loop 一起使用

```bash
# 使用特定范围启动
/loop 5m python3 plugins/developer-kit-specs/skills/ralph-loop/scripts/ralph_loop.py \
  --action=loop \
  --spec=docs/specs/002-tdd-command \
  --from-task=TASK-001 \
  --to-task=TASK-010
```

### 示例 3：多代理设置

```bash
# 使用 Claude 作为默认代理初始化
python3 ralph_loop.py --action=start \
  --spec=docs/specs/001-feature/ \
  --agent=claude

# 某些任务在其前置部分有 "agent: codex"
# 那些将显示 Codex 格式的命令
```

## 最佳实践

- **每次调用一步**：执行精确一步，保存状态，停止
- **信任状态**：从 `fix_plan.json` 读取，写入 `fix_plan.json`
- **无上下文累积**：状态保存在文件中，不在上下文中
- **手动命令执行**：脚本显示命令；您在 CLI 中执行它们
- **审查失败时重试**：最多重试 3 次，然后失败
- **范围过滤**：始终按 `task_range` 过滤
- **依赖优先**：仅选择所有依赖都完成的任务
- **git 提交**：脚本在每次完成的任务后自动提交

## 限制和警告

- **上下文爆炸**：不要在一次调用中实现 + 审查 + 同步 — 上下文将溢出
- **最大重试次数**：审查失败最多重试 3 次，然后失败
- **git 状态**：启动前确保干净的 git 状态
- **测试基础设施**：循环需要测试通过 — 没有测试，背压无效
- **严格状态验证**：有效的 `state.step` 值仅限：`init`, `choose_task`, `implementation`, `review`, `fix`, `cleanup`, `sync`, `update_done`, `complete`, `failed`
- **不自动执行命令**：脚本显示命令但不会执行它们 — 您必须在 CLI 中运行它们

## 故障排除

### "fix_plan.json 未找到"

首先运行 `--action=start`：
```bash
python3 ralph_loop.py --action=start --spec=docs/specs/001-feature/
```

脚本将在正确位置创建 `fix_plan.json`：
```
docs/specs/001-feature/_ralph_loop/fix_plan.json
```

### "fix_plan.json 在错误位置"

如果您看到关于文件位于错误位置的警告，脚本将引导您完成迁移：

```bash
# 如果需要手动迁移
mkdir -p docs/specs/001-feature/_ralph_loop
mv docs/specs/001-feature/fix_plan.json docs/specs/001-feature/_ralph_loop/fix_plan.json
```

脚本将在第一次运行时自动迁移旧文件。

### "无效的 spec 文件夹"

首先运行 `--action=start`：
```bash
python3 ralph_loop.py --action=start --spec=docs/specs/001-feature/
```

### 任务文件未找到

确保任务位于 `tasks/TASK-XXX.md` 格式，带有 YAML 前置部分。

### 错误的代理命令

检查 `--agent` 参数或任务 `agent:` 前置部分字段。

## 参考

- `references/state-machine.md` - 完整状态机文档
- `references/multi-cli-integration.md` - 多 CLI 设置指南
- `references/loop-prompt-template.md` - shell 循环的提示模板
