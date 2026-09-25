# Expo 示例

[expo/examples](https://github.com/expo/examples) 是 Expo 的官方库，包含约 70 个 **集成示例** — 这些示例是名为 `with-<library>`（例如 `with-stripe`，`with-maps`）的目录，每个示例都围绕 **一个** 库或服务构建。这些不是完整的应用程序：它们是 **受管理的项目**（没有 `ios/`/`android/` 目录 — 原生设置通过配置插件完成），典型的示例是一个 **约 100–200 行的单屏**。从中挖掘标准的集成 *模式* — 依赖集、`app.json` 配置插件以及 Expo 维护的最小化接线（针对当前 SDK），并将该模式应用到用户的应用程序中。不要期望从它们中直接复制应用程序架构。

在手动构建集成之前，先查找一个示例。（类型 — 全栈、展示、启动器 — 在 `./references/catalog.md` 中注明。）

## 两种模式

1. **灵感 / 适配**（最常见）— 用户已经有一个项目。找到匹配的示例，阅读其关键文件，并将 *模式* 应用到他们的代码中。
2. **脚手架** — 绿地开发。直接从示例启动一个全新的项目。

## 工作流程

### 1. 找到合适的示例

将用户的需求映射到示例名称（例如支付 → `with-stripe`，认证 → `with-clerk`）。`./references/catalog.md` 是一个分类的快照，用于快速筛选 — 但它会漂移，因此请与实时列表确认：

```bash
# 实时示例名称：
gh api repos/expo/examples/contents --jq '.[] | select(.type=="dir" and (.name|startswith(".")|not)) | .name'
# 别名（重命名）+ 已弃用（已删除/移动）的示例 — 在推荐前检查：
gh api repos/expo/examples/contents/meta.json --jq '.content' | base64 -d
```

`meta.json` 是重命名或已删除（已弃用示例从存储库树中移除但仍在此列出，每个都有 `message`）的来源。如果一个示例在其 `deprecated` 映射中，不要推荐它 — 按照 `message` 路径找到现代路径。如果它在 `aliases` 中，请使用 `destination`。

### 2a. 灵感模式 — 无需修改用户的项目进行研究

常见情况：用户已经有一个应用程序，并希望看到 Expo 如何做某事。将示例作为 **参考** 阅读并手动应用模式 — 永远不要在他们的项目上构建示例。

**首先，一次性列出整个示例。** 集成代码通常是嵌套的（例如 Stripe 的服务器路由位于 `app/api/` 中），因此一级列表会遗漏重要文件：

```bash
gh api 'repos/expo/examples/git/trees/master?recursive=1' \
  --jq '.tree[].path | select(startswith("with-stripe/"))'
```

**然后首先阅读高信号文件：** `README.md`（设置）→ `package.json`（依赖项）→ `app.json`（配置插件 / 权限）→ 宣告的集成代码 → `.env`（必需的密钥）。按文件：

```bash
gh api repos/expo/examples/contents/with-stripe/utils/stripe-server.ts --jq '.content' | base64 -d
# 没有 gh？原始 URL（分支是 master）：
curl -s https://raw.githubusercontent.com/expo/examples/master/with-stripe/utils/stripe-server.ts
```

**阅读超过几个文件？** 许多集成分布在服务器路由、客户端提供程序和配置中（Stripe 就是）。跳过逐文件调用 — 将整个示例拉入一个 **丢弃/忽略的目录（不是用户的项目）** 并用 Grep/Read 自由阅读，然后手动应用：

```bash
npx degit expo/examples/with-stripe /tmp/expo-ref/with-stripe   # 纯净副本，无 git 历史记录
# 没有 degit（稀疏检查，无完整 ~64 MB 克隆）：
git clone --depth 1 --filter=blob:none --sparse https://github.com/expo/examples.git /tmp/expo-ref/examples \
  && (cd /tmp/expo-ref/examples && git sparse-checkout set with-stripe)
```

从那里用 Grep/Read 阅读；完成后删除临时目录。

### 2b. 脚手架模式 — 从示例创建新项目

```bash
npx create-expo --example with-stripe   # 简短形式：  npx create-expo -e with-stripe
bun create expo --example with-stripe    # 使用 bun
```

### 3. 适配到用户的应用程序 — 非破坏性（关键）

当用户已经有一个应用程序时，**仅添加示例引入的内容；永远不要覆盖他们的设置。**

- **版本对齐 — 不要复制固定版本。** 示例跟踪 **最新** SDK，因此它们的 `package.json` 固定的版本不会与旧项目匹配。使用 `npx expo install <pkg>` 添加 *缺失* 的依赖项（它会解析 SDK 正确的版本），而不是复制确切版本。
- **合并配置，不要替换它。** 仅添加示例引入且用户缺少的 `app.json`/`app.config.*` 插件和权限 — 保留他们现有的配置块。
- **移植集成代码。**
- **重新创建环境变量** 从示例的 `.env` 结构 — 它包含占位符，不包含工作密钥。

**完成时** 集成代码已移植，并且它需要的每个依赖项、配置插件、权限和环境变量都在用户的应用程序中有所体现 — 而不是当它仅仅 *看起来* 连接好时。

## 注意事项

- **默认分支是 `master`，** 不是 `main`（对原始 URL 和稀疏检查很重要）。
- **单次点击部署。** 每个示例都有一个启动 URL：`https://launch.expo.dev/?github=https://github.com/expo/examples/tree/master/<example>`。

## 相关技能

- 原生 UI 组件 (@expo/ui 包) → `expo-ui`
- 样式和原生感觉的屏幕 → `expo-native-ui`
- 导航和路由 → `expo-router`
- 编写原生模块 → `expo-module`
- 在采用最新 SDK 示例之前升级 SDK → `expo-upgrade`

## 参考

- `./references/catalog.md` — 示例库的分类快照，用于快速筛选。

## 提交反馈
如果您遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-examples" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时提交。尽可能包含所有相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 `eval-candidate` 流程，而不是重复使用上面的命令。
