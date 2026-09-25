# 完成（GSD）- 项目管理系统

一个为独立开发者与Claude AI代理设计的全面项目管理系统。GSD提供结构化的工作流程，用于项目初始化、规划、执行、验证和调试。

## 概述

GSD是一个模块化的基于代理的系统，通过以下方式将项目想法转化为已发布的软件：

1. **深度提问** - 提取用户愿景和需求
2. **领域研究** - 发现标准堆栈和模式
3. **路线图创建** - 将需求分解为阶段
4. **阶段规划** - 创建带验证的可执行计划
5. **执行** - 使用原子提交实施计划
6. **验证** - 确保目标达成，而不仅仅是完成任务
7. **调试** - 系统性问题调查

## 核心理念

- **独立开发者 + Claude工作流程** - 无团队、无利益相关者、无仪式
- **计划即提示** - PLAN.md文件是执行提示，而非文档
- **目标导向规划** - 从必须为真的事实出发，推导出要构建的内容
- **原子提交** - 每个任务独立提交，保持清晰的版本历史
- **质量优先于速度** - 在上下文退化（约50%使用率）前停止
- **快速发布** - 计划 → 执行 → 发布 → 学习 → 重复

## 何时使用GSD

当你需要时使用GSD：

- 初始化新软件项目
- 规划和执行开发阶段
- 映射现有代码库
- 系统性调试问题
- 验证阶段完成情况
- 跟踪项目进度和状态

## 快速启动命令

### 新建项目
```bash
/gsd:new-project
```
使用提问 → 研究 → 需求 → 路线图流程初始化新项目。

### 规划阶段
```bash
/gsd:plan-phase [阶段编号]
```
创建带研究和验证的详细执行计划。

### 执行阶段
```bash
/gsd:execute-phase [阶段编号]
```
执行阶段内的所有计划，支持并行执行。

### 映射代码库
```bash
/gsd:map-codebase [可选聚焦区域]
```
使用并行映射代理分析现有代码库。

### 调试问题
```bash
/gsd:debug [问题描述]
```
使用科学方法和假设测试进行系统性调试。

### 验证阶段
```bash
/gsd:verify-work [阶段编号]
```
阶段完成情况的目标反向验证。

### 检查进度
```bash
/gsd:progress
```
显示当前项目位置、已完成阶段和下一步操作。

## 代理技能

GSD包含用于不同任务的专用代理：

- **gsd-codebase-mapper** - 探索和记录代码库结构
- **gsd-planner** - 创建可执行的阶段计划
- **gsd-executor** - 使用原子提交执行计划
- **gsd-debugger** - 系统性调查错误
- **gsd-verifier** - 验证目标达成
- **gsd-research-synthesizer** - 汇总研究输出
- **gsd-roadmapper** - 创建项目路线图
- **gsd-phase-researcher** - 研究阶段实施
- **gsd-project-researcher** - 研究领域生态系统
- **gsd-integration-checker** - 验证集成工作
- **gsd-plan-checker** - 验证计划质量

## 命令技能

GSD提供用于协调整个项目生命周期的命令：

- **gsd:new-project** - 初始化新项目
- **gsd:map-codebase** - 映射现有代码库
- **gsd:plan-phase** - 规划阶段
- **gsd:execute-phase** - 执行阶段
- **gsd:verify-work** - 验证阶段完成
- **gsd:debug** - 调试问题
- **gsd:discuss-phase** - 收集阶段上下文
- **gsd:research-phase** - 研究阶段实施
- **gsd:complete-milestone** - 完成里程碑
- **gsd:audit-milestone** - 审计里程碑
- **gsd:add-phase** - 添加新阶段
- **gsd:insert-phase** - 插入阶段
- **gsd:remove-phase** - 删除阶段
- **gsd:add-todo** - 添加待办事项
- **gsd:check-todos** - 检查待办事项
- **gsd:plan-milestone-gaps** - 规划里程碑差距
- **gsd:pause-work** - 暂停工作
- **gsd:resume-work** - 恢复工作
- **gsd:update** - 更新项目状态
- **gsd:whats-new** - 显示最新内容

## 工作流技能

用于复杂操作的详细工作流定义：

- **discovery-phase** - 阶段发现工作流
- **execute-phase** - 阶段执行工作流
- **diagnose-issues** - 并行UAT诊断
- **map-codebase** - 代码库映射工作流
- **discuss-phase** - 阶段讨论工作流
- **verify-phase** - 阶段验证工作流
- **verify-work** - 工作验证工作流
- **transition** - 阶段转换工作流
- **resume-project** - 项目恢复工作流

## 参考技能

最佳实践和指南的参考文档：

- **questioning** - 深度提问技巧
- **tdd** - 测试驱动开发模式
- **ui-brand** - UI/UX指南
- **verification-patterns** - 验证方法
- **git-integration** - Git工作流模式
- **checkpoints** - 检查点处理
- **continuation-format** - 连续格式规范

## 项目结构

GSD创建一个`.planning/`目录，包含：

```
.planning/
├── PROJECT.md           # 项目上下文和愿景
├── config.json          # 工作流偏好设置
├── REQUIREMENTS.md      # 范围需求
├── ROADMAP.md          # 阶段结构
├── STATE.md            # 项目记忆和状态
├── research/            # 领域研究输出
├── phases/              # 阶段特定工件
│   ├── XX-name/
│   │   ├── XX-PLAN.md
│   │   ├── XX-SUMMARY.md
│   │   ├── XX-CONTEXT.md
│   │   ├── XX-RESEARCH.md
│   │   ├── XX-VERIFICATION.md
│   │   └── XX-UAT.md
└── codebase/            # 代码库分析
    ├── STACK.md
    ├── ARCHITECTURE.md
    ├── STRUCTURE.md
    ├── CONVENTIONS.md
    ├── TESTING.md
    ├── INTEGRATIONS.md
    └── CONCERNS.md
```

## 关键概念

### 目标反向规划

与其问"我们应该构建什么"，不如问"什么必须为真才能实现目标？"

**正向:** "构建认证系统" → 任务列表
**目标反向:** "用户可以安全访问账户" → 推导出必须存在的内容

### 原子提交

每个任务独立提交，带有描述性消息：

```bash
feat(01-01): 实现用户登录
fix(01-02): 修复密码验证
test(01-03): 添加登录测试
```

### 上下文预算

计划在~50%上下文使用率内完成以保持质量：
- 0-30%：峰值质量
- 30-50%：良好质量
- 50-70%：退化质量
- 70%+: 差质量（避免）

### 波次执行

计划分组为波次进行并行执行：
- **波次1:** 无依赖的独立计划
- **波次2:** 仅依赖波次1的计划
- **波次3:** 依赖波次2的计划，以此类推

## 应避免的反模式

- **企业级PM戏剧** - 无RACI矩阵、冲刺仪式、利益相关者管理
- **水平分层** - 不要按"所有模型，然后所有API"分组 - 按功能分组
- **模糊的成功标准** - "认证工作正常" → "用户可以用邮箱/密码登录"
- **时间估算** - 从不按小时/天/周估算
- **任务完成≠目标达成** - 验证结果，而非仅任务完成

## 获取帮助

每个代理、命令和工作流都有自己的SKILL.md文件，包含详细说明。使用：

- `@skills/gsd/agents/` 用于代理特定帮助
- `@skills/gsd/commands/` 用于命令特定帮助
- `@skills/gsd/workflows/` 用于工作流特定帮助
- `@skills/gsd/references/` 用于参考文档

## 版本

GSD版本：1.0.0
最后更新：2026-01-19
