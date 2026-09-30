---
name: gsd-2-agent-framework
description: 元提示、上下文工程和基于规范的自主长时运行编码代理开发系统
---

# GSD 2 — 自主规格驱动代理框架

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集

GSD 2 是一个独立的命令行工具，能够将结构化的规格自动转换为可运行的软件。它直接控制代理框架，管理每个任务的上下文窗口、git 工作树隔离、崩溃恢复、成本跟踪和卡顿检测，而不是依赖 LLM 自循环。一条命令，走开，回来时即可获得一个干净的 git 历史记录的项目。

---

## 安装

```bash
npm install -g gsd-pi
```

需要 Node.js 18+ 版本。通过 Pi SDK 与 Claude (Anthropic) 作为底层模型协同工作。

---

## 核心概念

### 工作层级

```
里程碑  →  一个可发布版本（4–10 个切片）
  切片    →  一个可演示的垂直功能（1–7 个任务）
    任务   →  一个上下文窗口大小的单元工作
```

**铁律：** 一个任务必须适合一个上下文窗口。如果不行，就将其拆分为两个任务。

### 目录布局

```
project/
├── .gsd/
│   ├── STATE.md          # 当前自动模式位置
│   ├── DECISIONS.md      # 架构决策注册表
│   ├── LOCK              # 崩溃恢复锁文件
│   ├── milestones/
│   │   └── M1/
│   │       ├── slices/
│   │       │   └── S1/
│   │       │       ├── PLAN.md        # 任务分解，包含必须项
│   │       │       ├── RESEARCH.md    # 代码库/文档侦察输出
│   │       │       ├── SUMMARY.md     # 完成摘要
│   │       │       └── tasks/
│   │       │           └── T1/
│   │       │               ├── PLAN.md
│   │       │               └── SUMMARY.md
│   └── costs/
│       └── ledger.json   # 每个单元的 token/成本跟踪
├── ROADMAP.md            # 里程碑/切片结构
└── PROJECT.md            # 项目描述和目标
```

---

## 命令

### `/gsd auto` — 主要自主模式

运行完整的自动化循环。读取 `.gsd/STATE.md`，在新鲜会话中分派每个单元，处理恢复，并在不干预的情况下通过整个里程碑。

```bash
/gsd auto
# 或带选项：
/gsd auto --budget 5.00        # 如果成本超过 $5 则暂停
/gsd auto --milestone M1       # 仅运行里程碑 1
/gsd auto --dry-run            # 显示分派计划但不执行
```

### `/gsd init` — 初始化项目

从 `ROADMAP.md` 和可选的 `PROJECT.md` 构建 `.gsd/` 目录。

```bash
/gsd init
```

创建初始 `STATE.md`，从您的路线图中注册里程碑和切片，设置成本账本。

### `/gsd status` — 仪表板

显示当前位置、每个切片的成本、token 使用情况以及下一个排队的内容。

```bash
/gsd status
```

输出示例：
```
里程碑 1：认证系统  [3/5 个切片完成]
  ✓ S1：用户模型 + 迁移
  ✓ S2：密码认证端点
  ✓ S3：JWT 会话管理
  → S4：OAuth 集成  [规划中]
    S5：基于角色的访问控制

成本：$1.84 / $5.00 预算
Tokens：142k 输入，38k 输出
```

### `/gsd run` — 单元分派

手动执行特定单元，而不是运行完整循环。

```bash
/gsd run --slice M1/S4            # 运行切片的研究 + 规划 + 执行
/gsd run --task M1/S4/T2          # 运行单个任务
/gsd run --phase research M1/S4   # 仅运行研究阶段
/gsd run --phase plan M1/S4       # 仅运行规划阶段
```

### `/gsd migrate` — 从 v1 迁移

导入原始 Get Shit Done 的旧 `.planning/` 目录。

```bash
/gsd migrate                        # 迁移当前目录
/gsd migrate ~/projects/old-project # 迁移特定路径
```

### `/gsd costs` — 成本报告

详细的成本分解和预测。

```bash
/gsd costs
/gsd costs --by-phase
/gsd costs --by-slice
/gsd costs --export costs.csv
```

---

## 项目设置

### 1. 编写 `ROADMAP.md`

```markdown
# 我的 项目路线图

## 里程碑 1：核心 API

### S1：数据库模式和迁移
为用户、帖子评论设置 Postgres 模式。

### S2：REST 端点
所有资源的 CRUD 端点，带验证。

### S3：认证
基于 JWT 的认证，带刷新令牌。

## 里程碑 2：前端

### S1：React 应用框架
...
```

### 2. 编写 `PROJECT.md`

```markdown
# 我的 项目

一个使用 Express + TypeScript + Postgres 构建的博客平台 REST API。

## 技术栈
- Node.js 20, TypeScript 5
- Express 4
- PostgreSQL 15 通过 pg + kysely
- Jest 用于测试

## 规范
- 所有端点返回 `{ data, error }` 封装
- 数据库迁移在 `db/migrations/`
- 功能模块在 `src/features/<name>/`
```

### 3. 初始化

```bash
/gsd init
```

### 4. 运行

```bash
/gsd auto
```

---

## 自主模式状态机

```
研究 → 规划 → 执行（每个任务）→ 完成 → 重新评估 → 下一个切片
```

每个阶段都在一个**新鲜会话**中运行，上下文预内联到分派提示中：

| 阶段 | LLM 接收的内容 | LLM 生成的内容 |
|---|---|---|
| 研究 | PROJECT.md, ROADMAP.md, 切片描述, 代码库索引 | RESEARCH.md 带有发现、注意事项、相关文件 |
| 规划 | 研究输出, 切片描述, 必须项 | PLAN.md 带有任务分解、验证步骤 |
| 执行（任务 N） | 任务计划, 先前任务摘要, 依赖摘要, DECISIONS.md | 提交到 git 的工作代码 |
| 完成 | 所有任务摘要, 切片计划 | SUMMARY.md, UAT 脚本, 更新的 ROADMAP.md |
| 重新评估 | 已完成的切片摘要, 完整的 ROADMAP.md | 更新路线图，如有任何更正 |

---

## 必须项：机械可验证的成果

每个任务计划都包括必须项 — LLM 用于确认完成的明确、可检查标准。将它们写为 shell 命令或文件存在性检查：

```markdown
## 必须项

- [ ] `npm test -- --testPathPattern=auth` 通过，0 个失败
- [ ] 文件 `src/features/auth/jwt.ts` 存在并导出 `signToken`, `verifyToken`
- [ ] `curl -X POST http://localhost:3000/auth/login` 返回 200 并带有 `{ data: { token } }`
- [ ] 没有 TypeScript 错误：`npx tsc --noEmit` 退出码为 0
```

执行阶段仅在 LLM 可以勾选所有必须项时结束。

---

## Git 策略

在自主模式下，GSD 自动管理 git：

```
main
 └── milestone/M1          ← 启动时创建的工作树分支
      ├── 提交：[M1/S1/T1] 实现用户模型
      ├── 提交：[M1/S1/T2] 添加迁移
      ├── 提交：[M1/S1] 切片完成
      ├── 提交：[M1/S2/T1] POST /users 端点
      └── ...
 
 里程碑完成后：
main ← 将里程碑/M1 压缩合并为 "[M1] 认证系统"
```

每个任务都使用结构化消息提交。每个切片都提交一个摘要提交。里程碑压缩合并到 main 作为一条干净的条目。

---

## 崩溃恢复

GSD 在单元启动时在 `.gsd/LOCK` 写入锁文件，并在干净完成时删除它。如果进程死亡：

```bash
# 下一次运行检测到锁并自动恢复：
/gsd auto

# 输出：
# ⚠ 发现锁文件：M1/S3/T2 被中断
# 从会话工件中合成恢复摘要...
# 带完整上下文恢复
```

恢复摘要是从每个到达磁盘的工具调用合成的 — 文件写入、shell 输出、部分完成 — 因此恢复的会话具有上下文连续性。

---

## 成本控制

设置预算上限以在超支前暂停自主模式：

```bash
/gsd auto --budget 10.00
```

`.gsd/costs/ledger.json` 中的成本账本：

```json
{
  "units": [
    {
      "id": "M1/S1/research",
      "model": "claude-opus-4",
      "inputTokens": 12400,
      "outputTokens": 3200,
      "costUsd": 0.21,
      "completedAt": "2025-01-15T10:23:44Z"
    }
  ],
  "totalCostUsd": 1.84,
  "budgetUsd": 10.00
}
```

---

## 决策注册表

`.gsd/DECISIONS.md` 会自动注入到每个任务分派中。在此记录架构决策，LLM 将在所有未来会话中尊重它们：

```markdown
# 决策注册表

## D1：使用 kysely 而不是 prisma
**日期：** 2025-01-14
**原因：** 更好的 TypeScript 推断，不需要代码生成步骤。
**影响：** 所有数据库查询使用 kysely QueryBuilder 语法。

## D2：JWT 存储在 httpOnly cookie 中，而不是 Authorization 头
**日期：** 2025-01-14  
**原因：** 对 Web 客户端更好的 XSS 保护。
**影响：** 认证中间件读取 `req.cookies.token`。
```

---

## 卡顿检测

如果同一个单元分派两次而没有生成其预期工件，GSD：

1. 使用包含预期内容与磁盘上实际内容的深度诊断提示重试一次
2. 如果第二次尝试失败，**停止自主模式**并报告：

```
✗ 在 M1/S3/T1 卡顿，尝试 2 次后
预期：src/features/auth/jwt.ts（未找到）
最后会话：.gsd/sessions/M1-S3-T1-attempt2.log
手动重试：/gsd run --task M1/S3/T1
```

---

## 技能集成

GSD 支持在研究阶段自动检测和安装相关技能。在您的项目中创建 `SKILLS.md`：

```markdown
# 项目技能

- name: postgres-kysely
- name: express-typescript  
- name: jest-testing
```

技能注入到研究和规划分派提示中，为 LLM 提供关于您确切堆栈的精选知识，而不会在无关文档上消耗上下文。

---

## 超时监督

三个超时层级防止失控会话：

| 超时 | 默认 | 行为 |
|---|---|---|
| 软 | 8 分钟 | 发送 "请结束" 引导消息 |
| 空闲 | 3 分钟无工具调用 | 发送 "是否卡顿？" 恢复提示 |
| 硬 | 15 分钟 | 暂停自主模式，保留所有磁盘状态 |

在 `.gsd/config.json` 中配置：

```json
{
  "timeouts": {
    "softMinutes": 8,
    "idleMinutes": 3,
    "hardMinutes": 15
  },
  "defaultModel": "claude-opus-4",
  "researchModel": "claude-sonnet-4"
}
```

---

## TypeScript 集成（Pi SDK）

GSD 基于 [Pi SDK](https://github.com/badlogic/pi-mono) 构建。您可以编程扩展它：

```typescript
import { GSDProject, AutoRunner } from 'gsd-pi';

const project = await GSDProject.load('/path/to/project');

// 检查当前状态
const state = await project.getState();
console.log(state.currentMilestone, state.currentSlice);

// 程序化运行单个切片
const runner = new AutoRunner(project, {
  budget: 5.00,
  onUnitComplete: (unit, cost) => {
    console.log(`Completed ${unit.id}, cost: $${cost.toFixed(3)}`);
  },
  onStuck: (unit, attempts) => {
    console.error(`Stuck on ${unit.id} after ${attempts} attempts`);
    process.exit(1);
  }
});

await runner.runSlice('M1/S4');
```

---

## 自定义分派钩子

向任何分派提示注入自定义上下文：

```typescript
// .gsd/hooks.ts
import type { DispatchHook } from 'gsd-pi';

export const beforeTaskDispatch: DispatchHook = async (ctx) => {
  // 将自定义上下文附加到每个任务分派
  return {
    ...ctx,
    extraContext: `
## 实时 API 文档
${await fetchInternalAPIDocs()}
    `
  };
};
```

在 `.gsd/config.json` 中注册：

```json
{
  "hooks": "./hooks.ts"
}
```

---

## 路线图重新评估

每个切片完成后，GSD 运行重新评估，可能会：

- 根据发现的依赖重新排序即将到来的切片
- 将一个超出预期的切片拆分
- 标记不再需要的切片
- 添加一个新切片以进行发现的工作

LLM 直接编辑 `ROADMAP.md`。您可以使用以下命令查看差异：

```bash
git diff ROADMAP.md
```

要禁用重新评估：

```json
{
  "reassessment": false
}
```

---

## 故障排除

### 自主模式立即停止，显示 "没有待处理的切片"
`ROADMAP.md` 中的所有切片都标记为 `[x]`。重置切片：从其条目中删除 `[x]` 并删除 `.gsd/milestones/M1/slices/S3/SUMMARY.md`。

### LLM 不断失败必须项
检查 `.gsd/sessions/` 中的最后会话日志。常见原因：必须项引用了错误的文件路径，或测试命令需要环境变量。调整任务 `PLAN.md` 中的必须项，并使用 `/gsd run --task M1/S3/T2` 重新运行。

### 意外达到成本上限
大型代码库的研究阶段可能很昂贵。在配置中将 `researchModel` 设置为更便宜的模型，或减少代码库索引深度。

### 干净退出后留下锁文件
```bash
rm .gsd/LOCK
/gsd auto
```

### Git 工作树冲突
```bash
git worktree list          # 查看活动工作树
git worktree remove .gsd/worktrees/M1 --force
/gsd auto                  # 干净地重建
```

### 会话文件太大无法恢复
如果 `.gsd/sessions/` 变得很大，GSD 会自动压缩 24 小时以上的会话。手动清理：
```bash
/gsd cleanup --sessions --older-than 7d
```

---

## 链接

- [GitHub: gsd-build/GSD-2](https://github.com/gsd-build/GSD-2)
- [npm: gsd-pi](https://www.npmjs.com/package/gsd-pi)
- [Pi SDK](https://github.com/badlogic/pi-mono)
- [原始 GSD v1](https://github.com/gsd-build/get-shit-done)
