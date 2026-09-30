---
name: prisma-next-upgrade
description: 升级您的应用程序中的 Prisma Next。将 lockfile 中固定版本的每个 `@prisma-next/*` 依赖项升级到请求的目标版本（或 npm `latest`），应用每个过渡升级说明中所需的任何代码转换步骤，使用项目自身的类型检查和测试进行验证，并为每个次要步骤单独提交。当用户要求“升级 Prisma Next”、“提升 Prisma Next”、“迁移到 Prisma Next X.Y”，或请求代理处理应用程序中的 `@prisma-next/*` 次要版本升级时使用。
---

# 升级 Prisma Next (用户应用)

此技能用于升级一个通过公共包 API (`@prisma-next/postgres`, `@prisma-next/mongo`, `prisma/` 中的合约文件等) **使用** Prisma Next 的项目。如果该项目本身是一个 Prisma Next *扩展*，请使用 `prisma-next-extension-upgrade` 技能——如果存储库同时包含一个应用和一个扩展包，则两者都可以使用。

## 第 0 步 — 确保技能是最新的

在其他任何操作之前，请确保此技能已安装为 `@latest` 并重新加载。旧版本过渡升级说明中的错误修复包含在最新技能发布中作为其累积集的一部分；使用过时的技能可能会导致应用已知的损坏转换。

如果代理运行时支持会话内刷新，请立即执行。否则，退出并要求用户重新安装 (`pnpm dlx skills add prisma/prisma-next/skills/upgrade --all`)，然后重新调用。升级技能的子路径有意未固定（始终为 `main`）——累积指令集是权威来源，最新版本修复适用于所有先前的过渡。

## 过渡前检查 — 扩展兼容性

在更改任何代码之前，拒绝升级超过任何已安装扩展的固定 Prisma Next 版本。Prisma Next 中的扩展会将每个 `@prisma-next/*` 依赖项固定为单个确切版本（不带波浪号，不带范围）；该固定版本是扩展经过验证的最高版本。升级用户应用超过该固定版本将导致扩展的类型身份与应用的同步中断。

步骤：

1. **读取 `prisma-next.config.ts`**（或其在项目根目录的 TS 可发现等效文件）并枚举它导入的扩展包列表。每个 `extensions: [...]` 条目对应一个已安装的 npm 包。
2. **对于每个扩展**，从 `node_modules/<扩展包名称>/package.json` 读取其已安装的 `package.json`，并在 `dependencies`、`peerDependencies` 或 `optionalDependencies` 下查找任何 `@prisma-next/*` 条目。根据设计，这些条目是确切版本的固定（例如 `"0.7.0"`），这是扩展作者上次运行其升级时设置的。
3. **计算所有扩展中最低的固定版本。** 这就是此应用在其当前扩展集上可达到的最高 Prisma Next 版本。
4. **与用户的目标进行比较。** 如果目标超过最低固定版本，则停止，并使用结构化消息命名每个落后的扩展及其固定版本，并提供两条路径：
   - (a) 等待落后的扩展发布兼容版本，然后重新运行。
   - (b) 使用 `--to=<最高可达到>`（或用户使用的设置目标的任何标志/选项）重新运行。

不要自动降级目标；不要跳过落后的扩展；不要超过它。如果用户明确覆盖了停止，请首先清晰地展示风险。

如果 `prisma-next.config.ts` 不存在或未命名任何扩展，则跳过过渡前检查。

## 角色检测

当项目 **使用** Prisma Next 时应用此技能：

- `package.json` 在 `dependencies` / `devDependencies` 下声明一个或多个 `@prisma-next/*` 包，并且
- 该包本身不是扩展（在 `dependencies`/`peerDependencies` 下没有 `@prisma-next/contract`（或其他 SPI）；名称不匹配 `^@.*/extension-`；未从兄弟应用的 `prisma-next.config.ts` 中引用）。

如果项目也匹配扩展作者的角色，请安装 `prisma-next-extension-upgrade` 技能 (`pnpm dlx skills add prisma/prisma-next/skills/extension-author --all`) 并首先运行 **此** 流程，然后在同一会话中运行那个流程。如果检测模糊，请询问用户。

## 版本检测

- **起始版本。** 从 `pnpm-lock.yaml`（或 `package-lock.json` / `yarn.lock`）中读取当前安装的 Prisma Next 版本，通过检查任何 `@prisma-next/*` 包的解析版本。如果锁文件显示多个 `@prisma-next/*` 包在不同次版本（已经损坏），则 **最低** 次版本是起始版本。
- **目标版本。** 要么用户指定的版本，要么来自 `npm view @prisma-next/postgres dist-tags.latest` 的最新稳定版本。

在继续之前向用户报告这两个版本。

## 过渡链

如果从版本到版本的差异跨越多个次版本（例如 `0.6 → 0.8`），构建一个一版本步骤的链：

```text
0.6 → 0.7 → 0.8
```

按顺序依次应用每个步骤，完全：增加、安装、运行说明、验证、提交——然后才能移动到下一个。在第一个失败步骤处停止链；不要跳过。

链的顺序不依赖于安装了哪些扩展；过渡前检查已经确定了目标是可达的。

## 每步流程

对于链中的每个 `(起始, 目标)` 步骤：

1. **增加 `@prisma-next/*` 依赖项。** 将项目 `package.json` 中的每个 `@prisma-next/*` 条目重写为确切的 `<目标>` 版本（不带波浪号，不带 tilde）。所有条目都提升到同一版本。覆盖 `dependencies` 和 `devDependencies`。升级技能通过 `pnpm dlx skills add` 提供，并位于 `.agents/skills/prisma-next-upgrade/`（或等效的 CLI 管理目录）下——没有 `@prisma-next/upgrade-skill` npm 条目需要增加。

2. **安装。** 运行 `pnpm install`（或项目的锁文件管理命令）。现在项目的代码与新的类型不兼容——升级说明 `<起始> → <目标>` 存在以修复它。

3. **读取升级说明。** 从此技能包中加载 `upgrades/<起始>-to-<目标>/instructions.md`。解析 YAML 前置符并特别注意其 `changes[]` 数组。

4. **应用每个更改。** 对于 `changes[]` 中的每个条目：
   - 如果条目有一个 `detection` 块（glob + 内容谓词），请运行它；如果没有文件匹配，则跳过更改。没有 `detection` → 无条件应用。
   - 如果条目命名一个 `script:`（`instructions.md` 旁边的相对路径），从项目根目录调用它：`*.ts` 通过 `pnpm exec tsx <路径>`，`*.sh` 通过 `bash <路径>`，根据脚本自己的文字进行 codemods。没有 `script` → 直接跟随文字正文。

   空的 `changes[]`（用于没有用户端破坏性更改的过渡的占位符形状）是 no-op——继续验证。

5. **验证。** 运行 `pnpm typecheck && pnpm test`（或项目的等效操作——项目的 `package.json` 的 `scripts` 字段是发现表面）。如果任何内容为红色，则停止链。不 **自动回滚**；向用户展示失败的更改的 `id`（来自前置符）、更改操作的文件路径以及推断的修复方案。

6. **提交。** 每个步骤一个提交，包含 `package.json` 增加和锁文件变更以及任何源重写：

   ```text
   chore: upgrade @prisma-next/* to <目标版本>
   ```

   （或项目的自己的提交消息约定。）永远不要合并步骤。用户可以在合并时合并；飞行中的历史记录必须按步骤进行，以便失败的步骤可以进行二分法。

然后继续到下一步。

## 链完成时

向用户报告：应用的步骤数、您所做的提交的 SHAs 以及任何开放的后续事项（例如，升级前已经为红色的测试仍然为红色）。

## 失败表面

当步骤失败时：展示一个结构化错误，代码为 `PN-UPGRADE-NNNN`，失败更改的 `id`，触及的文件路径（或锁文件，或验证命令），以及推断的修复方案。不要自动重试；不自动回滚。用户可以回滚以获得干净的起点。

如果过渡前检查触发停止，则不要增加任何内容；项目保持不变。
