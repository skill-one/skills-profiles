**首先**：使用父级 `neon` 技能进行 Neon 概览，了解 Neon 入门、Neon 开发最佳实践等内容。

如果 `neon` 技能未安装，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
neon skills -s neon -y
```

# Lakebase Postgres 分支

**结果**：创建 Neon 分支，或如果创建无法进行，则提供清晰的下一步操作指南。选择正确的分支类型，然后使用 CLI（或无法使用 CLI 时使用 MCP）执行分支创建。

- **普通分支**：用于使用真实数据进行实际迁移和查询测试。
- **仅限架构分支（Beta）**：用于敏感数据工作流，需要架构而不需要复制行。

## 分支类型决策

首先使用此决策规则：

1. 如果用户想要测试复杂的迁移、性能或行为，并使用类似生产的数据，请选择**普通分支**。
2. 如果用户需要避免复制敏感数据，请选择**仅限架构分支**。

如果请求不明确，请提出一个澄清问题：
"您需要使用真实数据进行测试，还是只需要架构结构，因为数据是敏感的？"

## 工具选择：CLI 或 MCP

支持 Neon CLI 和 Neon MCP 服务器，但**默认使用 CLI**。仅在 CLI 不可用或您的环境中被阻止、无法进行身份验证，或用户明确要求使用 MCP 时才使用 MCP。

- CLI 链接：https://neon.com/docs/cli/quickstart.md
- MCP 链接：https://neon.com/docs/ai/neon-mcp-server.md

### 选择顺序

1. 首先检查 CLI：
   - 运行 `neon --version` 确认已安装 CLI。
   - 运行 `neon projects list` 确认身份验证/上下文。
2. 如果缺少 CLI，请通过快速入门进行安装。
3. 如果已安装 CLI 但未进行身份验证，请指导用户完成 `neon auth`（或 API 密钥身份验证），然后继续。
4. 当无法使用 CLI 时切换到 MCP——环境中没有 CLI 访问权限、执行被阻止，或无法进行身份验证——或用户明确要求使用 MCP。确认 Neon MCP 工具可用并已进行身份验证（例如，列出项目可以工作），然后按照以下 MCP 分支流程操作。
5. 如果两种路径都不成功，请使用 Neon REST API：
   - https://neon.com/docs/guides/branching-neon-api.md

### MCP 分支流程

1. 根据数据敏感性和迁移测试目标选择普通分支或仅限架构分支。
2. 使用分支工具（例如，`create_branch`）创建分支。
3. 使用读取工具（例如，`describe_branch`）进行验证。
4. 对于迁移工作流，在应用到主分支之前，优先使用基于分支的迁移流程。

## 创建普通分支（推荐用于真实数据迁移测试）

当用户需要真实测试条件时使用此方法。
真实的生产类数据可以暴露种子或数据迁移脚本遗漏的边缘情况，这有助于在上线前捕获迁移问题。

链接：https://neon.com/docs/introduction/branching.md

### 步骤

1. 首先确定工具路径（见 [选择顺序](#selection-order)）：使用 `neon --version` 验证 CLI，如果 CLI 不可用则回退到 MCP。
2. 确保项目上下文已设置（`neon set-context --project-id <your-project-id>`）或在命令中包含 `--project-id`。
3. 创建分支：

   ```bash
   neon branches create \
     --name <branch-name> \
     --parent <parent-branch-id-or-name> \
     --expires-at 2026-12-15T18:02:16Z
   ```

4. 可选地获取新分支的连接字符串：

   ```bash
   neon connection-string <branch-name>
   ```

## 创建仅限架构分支（Beta，敏感数据）

当用户必须不将生产行复制到测试分支时使用此方法。

链接：https://neon.com/docs/guides/branching-schema-only.md

### 步骤

1. 首先确定工具路径（见 [选择顺序](#selection-order)）：使用 `neon --version` 验证 CLI，如果 CLI 不可用则回退到 MCP。
2. 创建仅限架构分支：

   ```bash
   neon branches create \
     --name <schema-only-branch-name> \
     --parent <parent-branch-id-or-name> \
     --schema-only \
     --expires-at 2026-12-15T18:02:16Z
   ```

   如果存在多个项目，请包含 `--project-id`：

   ```bash
   neon branches create \
     --name <schema-only-branch-name> \
     --parent <parent-branch-id-or-name> \
     --schema-only \
     --project-id <your-project-id> \
     --expires-at 2026-12-15T18:02:16Z
   ```

### Beta 支持指南（强制要求）

仅限架构分支处于 Beta 版本。如果用户报告意外行为、错误或缺失功能：

1. 请他们分享反馈到 Neon 控制台：
   - https://console.neon.tech/app/projects?modal=feedback
2. 建议在 Neon Discord 中打开支持对话：
   - https://neon.com/discord

## 从父分支重置

当子分支已偏离且用户希望从父分支的最新架构和数据进行刷新时使用此方法。

链接：https://neon.com/docs/guides/reset-from-parent.md

### 它的作用

- 完全用父分支的最新状态替换子分支的架构和数据。
- 不合并；子分支上的本地更改将丢失。
- 保持相同的连接详情，但在重置期间活动连接会短暂中断。

### 推荐使用时机

- 开发或 staging 分支与生产版本差距太大。
- 用户希望从干净的父对齐状态开始新功能。
- 团队希望从生产版本刷新 staging 以获得一致的测试基线。

### 硬性约束和障碍

- 只有子分支可以重置（根分支和仅限架构根分支不能从父分支重置）。
- 如果目标分支有子分支，则直到删除这些子分支后才能重置。
- 从快照恢复父分支后，重置-from-parent 可能最多 24 小时不可用。
- 重置-from-parent 总是使用当前父状态；对于时间点恢复需求，请使用 Instant restore。

### CLI 使用

```bash
neon branches reset <id|name> --parent --preserve-under-name <backup-branch-name>
```

如果项目上下文尚未设置，请包含项目 ID：

```bash
neon branches reset <id|name> --parent --preserve-under-name <backup-branch-name> --project-id <project-id>
```

`--preserve-under-name` 将重置前的状态作为回滚备份分支，但会多一个额外的分支需要清理。

可选的上下文设置以避免重复 `--project-id`：

```bash
neon set-context --project-id <project-id>
```

### 控制台和 API 使用

- **控制台**：打开目标子分支，然后从 **操作** 中选择 **从父分支重置**。
- **API**：使用分支的恢复端点并将 `source_branch_id` 设置为父分支 ID。

## 注意事项和注意事项

- 仅限架构分支用于结构克隆和敏感/合规数据控制。
- 仅限架构分支是独立的根分支（没有父分支和没有共享历史），因此不适用重置-from-parent。
- 对于依赖于真实世界行形状、容量和边缘情况的迁移测试，请优先使用普通分支。
- 根分支权限和每个分支的存储限制可能会限制用户可以创建的仅限架构分支数量。
- 如果用户不确定，默认建议是：
  - **普通分支**：用于迁移验证。
  - **仅限架构分支**：用于合规和隐私约束。

## 有用的工作流模式

如果用户要求过程建议（而不仅仅是单个命令），请建议以下内容：

- **每个 PR 一个分支**：PR 打开时创建分支，合并/关闭时删除，将迁移测试隔离。
- **每个测试运行一个分支**：在管道启动时创建分支，运行迁移/测试，在结束时删除，以实现确定的 CI。
- **每个开发者一个分支**：隔离的开发环境具有类似生产的形状；避免团队在共享测试数据上发生冲突。
- **PII 感知分支**：如果生产中有敏感数据，请从匿名分支派生开发/PR 分支或使用仅限架构分支。
- **瞬态生命周期卫生**：设置分支过期并自动清理，以避免旧分支累积不必要的存储/历史成本。

### 创建分支后的环境更新提示

创建分支后，询问用户是否希望更新本地环境凭证以指向新分支。

- 询问："您希望我更新 `.env` `DATABASE_URL` 以指向此新分支的连接字符串吗？"
- 如果是，将新分支的连接字符串写入请求的环境文件/键。
- 如果不是，保持凭证不变，并共享连接字符串以供手动使用。
- 永不覆盖现有的环境键，除非明确确认。

## Neon 基础设施即代码 (`neon.ts`)

除了使用 CLI / MCP / API 上述命令强制创建分支外，您还可以在 `neon.ts` 中**声明式地编程新分支接收的配置**——Neon 的基础设施即代码文件（有关完整参考，请查看 `neon` 技能）。`branch` 属性是正在评估的分支的函数，它返回其设置，因此您的项目生成的每个分支都获得了一致的生命周期和计算配置，而无需每个分支的标志。

```bash
npm i @neon/config
```

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  branch: (branch) => {
    if (branch.exists) return {}; // 不要重新协调现有分支
    if (branch.isDefault) return { protected: true };
    if (branch.name.startsWith("preview/") || branch.name.startsWith("dev")) {
      return {
        parent: "main",
        ttl: "7d", // 瞬态：创建后 7 天自动过期（最大 30 天）
        postgres: {
          computeSettings: {
            autoscalingLimitMinCu: 0.25, // 缩放到零
            autoscalingLimitMaxCu: 1, // 保持临时分支廉价
            suspendTimeout: "5m",
          },
        },
      };
    }
    return {};
  },
});
```

闭包接收目标分支的可读描述——`name`、`exists`、`isDefault`、`parentId` 等——并返回要应用的调整：`parent`、`ttl`（自动过期）、`protected` 和 `postgres.computeSettings`。这是上述**瞬态生命周期卫生**和每个 PR / 每个测试模式的声明式补充：不再需要记住每个 `neon branches create` 上的 `--expires-at`，TTL 和计算配置存储在版本控制中，并应用于每个匹配的分支。

因为 `neon checkout` 在创建分支时应用此策略，所以新的 `preview/*` 或 `dev-*` 分支会立即过期并缩放到零。检出**现有**分支不会重新协调它——运行 `neon deploy`（`neon config apply` 的别名）以将更改应用于已存在的分支。

## CI/CD 中的分支

Neon 分支的常见 CI/CD 用例：

- **每个 PR 预览部署**：PR 打开时创建分支，预览部署，关闭时删除。每个 PR 都会获得一个隔离的数据库分支。将分支的 `DATABASE_URL` 注入部署的应用程序取决于托管提供商——请参阅 [使用 Cloudflare 的预览分支](https://github.com/neondatabase/preview-branches-with-cloudflare)、[使用 Vercel 的预览分支](https://github.com/neondatabase/preview-branches-with-vercel) 或 [使用 Fly 的预览分支](https://github.com/neondatabase/preview-branches-with-fly) 以获取经过测试的模式。
- **CI 中的迁移测试**：在合并前对具有生产类数据的分支运行有风险的架构更改。
- **架构差异可见性**：使用 [schema-diff GitHub Action](https://github.com/marketplace/actions/neon-schema-diff-github-action) 自动在 PR 上注释数据库层差异。

## 示例

### 示例 1：使用真实数据进行迁移测试

**用户输入**："我需要使用生产类数据进行测试一个有风险的迁移。"

**代理输出形状**：

1. 推荐普通分支并解释原因。
2. 分享文档链接：https://neon.com/docs/introduction/branching
3. 首先检查工具路径（使用 `neon --version` 的 CLI；如果 CLI 不可用则仅使用 MCP）。
4. 提供命令：
   - `neon branches create --name migration-test --parent main --expires-at 2026-12-15T18:02:16Z`
   - `neon connection-string migration-test`

### 示例 2：敏感数据开发工作流

**用户输入**："由于合规性，我们不能复制生产数据。"

**代理输出形状**：

1. 推荐仅限架构分支并解释原因。
2. 分享文档链接：https://neon.com/docs/guides/branching-schema-only
3. 首先检查工具路径（使用 `neon --version` 的 CLI；如果 CLI 不可用则仅使用 MCP）。
4. 提供命令：
   - `neon branches create --name compliance-dev --parent main --schema-only --project-id <your-project-id> --expires-at 2026-12-15T18:02:16Z`
5. 提及 Beta 支持路径：
   - https://console.neon.tech/app/projects?modal=feedback
   - https://neon.com/discord

## 进一步阅读

- https://neon.com/docs/guides/branch-expiration.md
- https://neon.com/docs/guides/neon-github-integration.md
- https://neon.com/docs/ai/neon-mcp-server.md
- https://neon.com/branching
