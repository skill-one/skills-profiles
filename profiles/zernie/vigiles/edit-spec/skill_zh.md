编辑 `.spec.ts` 文件以更新项目的指令文件。规范是事实来源——CLAUDE.md 和 AGENTS.md 是必须直接编辑的编译构建产物。

## 参数

$ARGUMENTS — 用户想要更改的内容。示例：

- "添加一条始终使用自定义日志记录器的规则"
- "更新架构部分"
- "将 src/services/auth.ts 添加到关键文件"
- "将 npm run lint 添加到命令"
- "更改测试指南"

## 指令

### 第 1 步：找到规范

在仓库根目录中查找规范文件：

- `CLAUDE.md.spec.ts` — CLAUDE.md 的来源
- `AGENTS.md.spec.ts` — AGENTS.md 的来源
- 任何匹配指令文件的 `*.spec.ts`

如果不存在规范：如果存在手写的 `CLAUDE.md`，建议 `adopt-spec` 技能；否则建议使用 `npx vigiles init` 来生成一个。

### 第 2 步：阅读和理解规范

阅读规范文件。它是一个导出 `claude()` 调用的 TypeScript 文件，包含以下字段：

```typescript
import { claude, enforce, guidance, check, every } from "vigiles/spec";

export default claude({
  // 可选：输出目标（默认为 "CLAUDE.md"）
  target: "CLAUDE.md",
  // 或多目标：
  // target: ["CLAUDE.md", "AGENTS.md"],

  // 文本部分 — 在编译输出中成为 ## 标题
  sections: {
    positioning: "这个项目做什么...",
    architecture: "代码库如何结构化...",
  },

  // 在编译时验证存在的文件路径
  keyFiles: {
    "src/index.ts": "主入口",
  },

  // 与 package.json 验证的命令
  commands: {
    "npm run build": "编译项目",
    "npm test": "运行所有测试",
  },

  // 规则 — 三种类型
  rules: {
    // enforce() — 由 linter 规则支持，验证存在且已启用
    "no-any": enforce(
      "@typescript-eslint/no-explicit-any",
      "使用 unknown 和类型守卫来缩小类型。",
    ),

    // check() — 由 vigiles 运行的文件系统断言
    "test-pairing": check(
      every("src/**/*.service.ts").has("{name}.test.ts"),
      "每个服务都必须有测试。",
    ),

    // guidance() — 仅文本，无强制执行
    "research-first": guidance("在实现不熟悉的 API 之前使用 Google。"),
  },
});
```

### 第 3 步：进行更改

根据用户的要求：

**添加规则**（这会吸收旧的 `generate-rule` 技能）：

- **从请求中分类规则**：
  - `enforce()` — 可以由 linter 规则支持。检查项目的 linter 配置（ESLint、Ruff、Clippy、Pylint、RuboCop、Stylelint）以查找匹配的规则；还考虑架构工具（ast-grep、Dependency Cruiser、Steiger）。如果不确定是否存在规则，**询问用户**而不是猜测。
  - `check()` — 文件系统结构约定（"每个 X 需要一个 Y"）。仅用于文件配对；从不用于代码内容。
  - `guidance()` — 无法机械执行（主观约定、流程规则、迁移上下文）。
- 对于 `enforce()`：使用真实的 linter 规则名称（例如 `eslint/no-console`、`@typescript-eslint/no-explicit-any`、`ruff/T201`）。
- 添加到 `rules` 对象，使用从意图派生的 kebab-case 键，并保持现有规则的字母顺序。导入任何需要的构建器（例如，第一个 `check()` 需要 `check` 和 `every`）。

**更新部分**：

- 编辑 `sections` 中的字符串。部分是普通字符串或带有 `file()`、`cmd()`、`ref()` 的标记模板字面量以验证引用
- 不要在部分中添加 `#` 或 `##` 标题——它们会破坏文档结构

**添加关键文件或命令**：

- 添加到 `keyFiles` 或 `commands`。编译器在编译时验证这些是否存在
- 对于命令：必须匹配 `package.json` 中的脚本
- 对于关键文件：必须在磁盘上存在
- 🔴 **保持描述为单行——目标 120 个字符，不超过 ~200。** `keyFiles` 条目是一个指针：文件的作用是什么，以便读者知道是否要打开它。其工作原理的解释属于该文件自己的头注释，当有人实际在文件中时才会读取。指令文件在每次请求时都会加载，因此在这里添加段落会永远支付给每个读者——包括那些从未接触过该文件的读者。
- **这个列表只会增长除非你缩减它。** 每次会话都会添加条目而不会删除它们，因此在添加之前，检查是否有附近的条目现在已过时（文件已移动、角色已更改、描述重述其头），并在同一编辑中修复它。在不修剪的情况下添加会导致指令文件达到其 harness 预算的四倍——`vigiles audit` 报告该数字为 `Always-loaded instructions`，因此当您触摸此列表时请检查它。

### 第 4 步：编译

编辑规范后，运行：

```bash
npx vigiles compile
```

这将重新生成编译后的指令文件。检查输出中的任何错误：

- `stale-file` — 关键文件路径不存在
- `stale-command` — 命令不在 package.json 中
- `invalid-rule` — linter 规则不存在或已禁用
- `section-has-header` — 部分包含 `#` 标题（拆分为单独命名的部分）

### 第 5 步：验证

```bash
npx vigiles lint
```

如果安装了 vigiles 插件（`/plugin marketplace add zernie/vigiles` 然后是 `/plugin install vigiles@vigiles`，或 `npx vigiles init`），PostToolUse 钩子在您保存规范后会自动重新编译。

## 重要

- **做用户要求的；不要无声地升级强制执行。** 添加用户要求的规则。如果将其设为 `enforce()` 需要编辑 linter 配置或安装插件（成本），或者它可能会使干净的 CI 失败，**说出并让用户选择**——不要自己更改 linter 配置或切换严格/`workflow` 门控。纯赢（已启用的规则）你可以直接应用。`strengthen` 技能拥有 `guidance()` → `enforce()` 升级。
- **永远不要直接编辑 CLAUDE.md 或 AGENTS.md** — 它们有 vigiles 哈希注释，是构建产物
- **规范是 TypeScript** — 你会获得类型检查、自动完成和验证引用
- **`enforce()` 规则是验证的** — 编译器检查规则是否存在且在 linter 配置中已启用
- **部分不能包含 `#` 或 `##` 标题** — 使用单独命名的部分代替
