从现有的手写 CLAUDE.md（或 AGENTS.md）开始创建一个类型的 `CLAUDE.md.spec.ts`。这是非破坏性的采用路径——你可以将现有的指令文件作为起点，并从现在开始获得类型安全。

## 采用规则

采用是**安全、忠实的入口——绝不是伪装的升级**。这些是不可协商的：

- **忠实。** 保留每个规则、命令、键文件和散文部分原样不变。不要凭空创造——规范必须能编译回用户现有的文件。
- **非破坏性。** 不要编辑原始的 `CLAUDE.md` / `AGENTS.md`。只编写新的 `.spec.ts`。不要自动`编译`覆盖文件——切换到规范管理是一个单独的显式步骤，用户需要运行带差异的步骤来审查。
- **不要升级强制执行。** 保持 `guidance()` 为 `guidance()`。升级到 `enforce()` 有成本（配置/插件、可能的误报），这是一个单独的选入步骤——`strengthen` 技能。采用**不是**打开严格 / `workflow` 门控。
- **可逆。** `vigiles eject <file>` 随时将文件以普通手写 markdown 的形式交还——它绝不是单程门。告诉用户这一点。
- **写之前先询问。** 先展示生成的规范和转换摘要；只在用户同意后编写。
- **存在更轻触的方式。** 对于完全没有规范的情况，内联 `<!-- vigiles:enforce ... -->` 评论会被 `vigiles lint` 用相同引擎验证。

## 指令

### 第 1 步：读取现有文件

读取目标指令文件（默认：存储库根目录中的 `CLAUDE.md`）。如果用户指定了路径，则使用该路径。

还要检查 vigiles 是否已安装：在 `package.json` 的 devDependencies 中查找 `vigiles`。如果没有，建议：

```bash
npm install -D vigiles
```

### 第 2 步：解析结构

在 markdown 中识别以下部分：

- **命令** — 类似 `` `npm run build` — 描述 `` 或 ``- `command` — 描述`` 的行
- **键文件** — 类似 `` `src/foo.ts` — 描述 `` 列出重要文件的行
- **规则** — 带有 `**Enforced by:**` 或 `**Guidance only**` 注释的 `###` 标题
- **散文部分** — 其他所有内容（定位、架构、原则等）

对于每个规则，进行分类：

- 有 `**Enforced by:** \`linter/rule`` → `enforce("linter/rule", "为什么")`
- 有 `**Enforced by:** \`code-review`` 或类似的非 linter → `guidance("...")`
- 有 `**Guidance only**` → `guidance("...")`
- 没有注释 → 标记为 TODO，让用户进行分类

### 第 3 步：生成规范文件

创建 `CLAUDE.md.spec.ts`（或根据源文件适当命名）的结构：

```typescript
import {
  claude,
  enforce,
  guidance,
  file,
  cmd,
  ref,
  instructions,
} from "vigiles/spec";

export default claude({
  sections: {
    // 散文部分在这里
  },

  keyFiles: {
    // 键文件在这里。一个路径映射到一个说明文件用途的行——目标为 120 个字符，不超过 ~200。条目是一个指针，不是摘要：文件的工作原理属于它自己的头注释，当有人打开它时会被读取。这个文件在每次请求时都会加载，所以这里的段落每轮都会付出代价。添加一个时，修剪一个陈旧的邻居；`vigiles audit` 打印运行总数作为 `Always-loaded instructions`。
  },

  commands: {
    // 命令在这里
  },

  rules: {
    // 规则在这里
  },
});
```

**重要指南：**

- 在出现文件路径的 `sections` 中使用 `file()` 引用——这启用了陈旧引用检测
- 对于 `sections` 中提到的任何 `npm run` 命令，使用 `cmd()` 引用
- 将 `**Enforced by:** \`code-review`` 规则转换为 `guidance()` —— 代码审查不是机械执行
- 对于没有注释的规则，添加 `// TODO: 将其分类为 enforce() 或 guidance()` 注释
- 保持规则 ID 为标题文本的 kebab-case 版本
- 保留 `**Why:**` 文本作为 `enforce()` 或 `guidance()` 的第二个参数
- 如果 `sections` 引用其他文件或技能，使用 `ref()` 进行交叉引用

### 第 4 步：验证规范编译

运行：

```bash
npm run build
npx vigiles compile CLAUDE.md.spec.ts
```

将编译输出与原始文件进行比较。预期的关键差异是（格式化、部分顺序），但所有规则、命令、键文件和散文内容都应保留。

### 第 5 步：展示结果

向用户展示：

1. 生成的规范文件
2. 转换了多少规则（enforce vs guidance vs TODO）
3. 添加了多少文件/命令引用以进行陈旧引用检测
4. 编译命令：`npx vigiles compile`
5. 验证命令：`npx vigiles lint`

询问他们是否希望您编写文件。如果同意，还建议添加到 `.gitignore` 或更新 CI 以运行 `vigiles compile` 和 `vigiles lint`。

### 第 6 步：可选——设置 CI

如果用户希望集成 CI，建议将以下内容添加到他们的 GitHub Actions 工作流：

```yaml
- name: Compile specs
  run: npx vigiles compile
- name: Verify references + integrity
  run: npx vigiles lint
```

或使用 vigiles GitHub Action：

```yaml
- uses: zernie/vigiles@v1
  with:
    command: lint
```
