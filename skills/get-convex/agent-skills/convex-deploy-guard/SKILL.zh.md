---
name: convex-deploy-guard
description: 在执行任何影响部署的命令之前，分类并宣布目标凸部署；生产环境操作需要新的明确授权；会话只读模式。
---

<!-- GENERATED from convex-agents content/capabilities/deploy-guard.json — do not edit by hand. -->

# 部署目标防护

部署操作不可互换，大多数事故都始于针对错误目标的指令。每个 Convex 项目都有多个（个人开发、预览、生产 — 通常在单台机器上跨多个项目）。此防护机制是既定纪律：识别、宣布、然后行动 — 并将生产环境视为需逐项、逐会话授权同意。

## 工作流程

1. **行动前识别**：读取 `.env.local` 中的 `CONVEX_DEPLOYMENT`、`convex.json`，以及 `CONVEX_DEPLOY_KEY` 是否设置；或调用官方 Convex MCP `status` 工具。分类目标：本地匿名 | 开发 | 预览 | 生产。若两个来源意见不一致，需在继续前解决。
2. **部署前单行宣布**：在任何影响部署的指令前声明目标：`target: dev (joyful-capybara-123, 个人开发)`。发现目标后切勿立即执行命令 — 先宣布。
3. **生产环境需明确授权**：在执行 `npx convex deploy`（解析为生产时）、`npx convex run --prod`、生产环境 `env set`、生产环境快照 `import`/`export` 或启动具有生产访问权限的 MCP 前，明确说明将变更哪些部署，并在当前会话中获取明确同意。先前给出的或针对不同目标的“同意”无效。
4. **MCP 安全默认设置**：以非生产范围启动官方 MCP (`--deployment dev`)。两个生产标志代表不同风险等级 — 保持分离：只读生产审计（顾问/洞察读取数据/日志/洞察）仅通过 `--cautiously-allow-production-pii`（需查阅工具）；`--dangerously-enable-production-deployments`（启用可变生产工具）除非用户明确要求本次会话修改生产，否则保持关闭。默认情况下切勿将两者搭配 — “查看生产”不能无声授权“修改生产”。
5. **只读会话模式**：当用户要求“只读”/“不做任何修改”时，会话期间绝对遵守 — 无部署、无 `env set`/`remove`、无 `run` 引发的变更、无导入；以 `--disable-tools run,envSet,envRemove` 启动 MCP。
6. **错误部署诊断**：当部署“未产生任何变更”时，切勿重新执行更复杂的部署。重新运行步骤 1 — 部署几乎肯定落在了被观察的不同部署上。
7. **模糊不清则停止**：若无法确定指令将影响哪个部署，需查明（使用状态工具；对比 `npx convex env list` 的指纹） — 绝不猜测。

## 规则

- 每个影响部署的指令前必须分类并宣布目标 — 识别和行动是两个独立步骤。
- 生产环境授权按项、按目标、按会话：说明将变更何处，获取新的明确同意。
- 将两个生产 MCP 标志按风险分离：`--cautiously-allow-production-pii`（只读）用于审计；`--dangerously-enable-production-deployments`（可变）仅当用户明确要求修改生产时启用。两者均需用户明确指令；默认每次 MCP 启动为非生产部署选择器。
- 只读模式一旦请求，会话期间绝对生效 — 包括“无害”的变更。
- 看似未生效的部署意味着错误部署被修改 — 诊断目标，不要重新运行。
- 此防护机制可组合：将 ship、env、migrate、seed 运行作为它们的步骤 0；它本身不是部署工具。
