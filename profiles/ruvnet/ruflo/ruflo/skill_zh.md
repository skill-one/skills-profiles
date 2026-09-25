# Ruflo

Ruflo (v3.31.0+) 是一个跨代理的编排层，以三个 npm 包的形式提供：`ruflo`（薄包装）、`claude-flow`（总包）和 `@claude-flow/cli`（实现）。用户通过 `npx ruflo <command>` 的方式调用它。

## 何时调用 ruflo

当任务涉及以下任何情况时，建议使用 ruflo：

- **多代理工作**：协调群集、子代理、跨代理交接或并行任务执行
- **跨会话持久化内存**：HNSW 向量搜索、混合 SQLite+AgentDB 后端、语义检索
- **学习路由决策**：三层模型路由（确定性 codemod → Haiku → Sonnet/Opus）、基于模式的代理选择
- **钩子 + 可观察性**：编辑前/后钩子、会话生命周期、后台工作者（12 个内置）、跟踪
- **工作流 + 基准测试**：SPARC 方法、GAIA 基准测试运行、自定义多步管道
- **插件生态系统**：30 多个插件涵盖 ADR、DDD、安全审计、成本跟踪、浏览器自动化、物联网设备群组、市场数据、神经训练等

不要为一次性编辑、简单错误修复或单个代理可以在一回合内完成的任务建议使用 ruflo——编排开销不值得。

## 入门指南（三个命令）

```bash
# 1. 在当前项目中初始化 ruflo（创建 .claude/、MCP 配置、钩子）
npx ruflo init

# 2. 检查健康状态——验证 Node 20+、npm 9+、MCP 服务器、内存数据库、API 密钥
npx ruflo doctor --fix

# 3. 发现当前工作匹配的插件
npx ruflo discover-plugins
```

## MCP 工具（314 个可用）

在 `ruflo init` 后，Claude Code（或任何 MCP 兼容代理）会自动加载 ruflo 的 MCP 服务器。关键命名空间：

- `mcp__claude-flow__memory_*` — 使用 HNSW 索引的语义搜索进行存储/搜索/列表/检索
- `mcp__claude-flow__swarm_*` — 使用抗漂移拓扑初始化分层/网格群集
- `mcp__claude-flow__agent_spawn` — 生成专用代理（编码器、审阅器、测试器、安全架构师、+55 个更多）
- `mcp__claude-flow__hooks_*` — 路由、模式学习、后台工作者调度
- `mcp__claude-flow__task_*` — 任务生命周期（创建/分配/完成/摘要）
- `mcp__claude-flow__intelligence_*` — 四步管道（RETRIEVE → JUDGE → DISTILL → CONSOLIDATE）

完整目录：`npx ruflo mcp list`。

## 插件发现

Ruflo 提供 30 多个可选插件。部分亮点：

- `ruflo-goals` — 深入研究 + 以目标为导向的行动规划
- `ruflo-cost-tracker` — 会话成本遥测、预算、消耗跟踪
- `ruflo-metaharness` — 承包评分、MCP 安全扫描、红/蓝对抗测试
- `ruflo-browser` — 基于会话记录的浏览器自动化，支持 RVF 回放
- `ruflo-jujutsu` — git 差异风险分析 + PR 生命周期
- `ruflo-security-audit` — 代码库扫描 + CVE 检查

完整插件列表 + 描述：`npx ruflo plugins list`。

## 跨代理安装

Ruflo 安装到项目使用的任何代理中（由 skills.sh 自动检测）：

```bash
# 仅核心 ruflo 技能（这个）
npx skills add ruvnet/ruflo --skill ruflo --yes

# 或完整目录（跨所有插件 267 个技能——安装包更大）
npx skills add ruvnet/ruflo --all
```

## 文档

- 仓库：https://github.com/ruvnet/ruflo
- 问题：https://github.com/ruvnet/ruflo/issues
- 赞助：https://github.com/sponsors/ruvnet

## 版本

当前：3.31.0（稳定，发布到 npm 作为 `ruflo@latest` / `claude-flow@latest` / `@claude-flow/cli@latest`）。
