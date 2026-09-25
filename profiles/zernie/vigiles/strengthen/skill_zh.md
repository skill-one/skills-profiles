扫描规范文件中的 `guidance()` 规则，并建议使用基于真实代码检查规则的 `enforce()` 替换。

## 原则：免费胜出，成本助推

分界线在于**成本而非严格性**。当 `guidance()` → `enforce()` 的转换中代码检查规则**已存在且已启用**时，这是一个纯粹的胜利——免费、可逆、无误报风险——因此应用它（Tier 1 以下）。任何**需要成本**的操作——编辑代码检查配置、安装插件，或可能导致干净 CI 失败的变更——都由用户决定：**明确说明权衡利弊并让他们选择**（Tier 2–4）。永远不要在无声中编辑配置、安装依赖项或将仓库升级为严格门禁。这是 `init` 强制模型（结构 = 默认开启，工作流/严格 = 选择加入）应用于编辑时。

## 指令

### 第 0 步：选择模式

询问用户：

> **自动还是交互式？**
>
> - **自动** — 我将应用所有安全的变更（直接替换且规则已启用），提交并显示差异。有风险的变更（需要配置编辑或插件安装）将汇总供您审查。
> - **交互式** — 我将逐个展示建议，您选择要应用的项。

如果用户未指定，则默认为交互式。

### 第 1 步：发现已安装项

运行 `npx vigiles generate types` 获取项目中所有启用的代码检查规则。阅读 `.vigiles/generated.d.ts` 查看所有检测到的代码检查器中可用的规则。

注意生成的类型中出现的代码检查器前缀（例如，`EslintRule`、`RuffRule`）。您只需要检测到代码检查器的参考文档。

### 第 2 步：查找所有 `guidance()` 规则

在项目中查找所有 `.spec.ts` 文件（`**/*.md.spec.ts`）。对于每个文件，识别所有 `guidance()` 规则。

### 第 3 步：与生成类型匹配（快速路径）

对于每个 `guidance()` 规则，检查 `.vigiles/generated.d.ts` 中是否有启用的规则直接匹配。这是快速、确定性的路径——无需阅读文档。

查找：

- **文本中的确切规则名** — `guidance()` 说“禁止使用 console.log”，而 `no-console` 在 EslintRule 中
- **语义匹配** — `guidance()` 说“不要使用 console.log”，而 `no-console` 可用
- **规则描述匹配** — `guidance()` 说“未使用的变量”，而 `no-unused-vars` 或 `@typescript-eslint/no-unused-vars` 可用

如果找到匹配且规则在生成类型中（这意味着它已启用），这是一个**直接替换**——无需配置变更。

### 第 4 步：阅读代码检查器文档（慢速路径）

对于第 3 步中未匹配的 `guidance()` 规则，阅读项目检测到的代码检查器的参考文档：

- ESLint → `../linter-docs/eslint.md`
- Stylelint → `../linter-docs/stylelint.md`
- Ruff → `../linter-docs/ruff.md`
- Pylint → `../linter-docs/pylint.md`
- RuboCop → `../linter-docs/rubocop.md`
- Clippy → `../linter-docs/clippy.md`

**仅阅读项目实际使用的代码检查器的文档。** 跳过没有规则在生成类型中的代码检查器的文档。

检查插件表格和决策矩阵。`guidance()` 文本可能描述了由以下项覆盖的模式：

- 已安装但未启用的插件规则
- 尚未安装的插件
- `no-restricted-*` 配置模式（见第 4b 步）

### 第 4b 步：`no-restricted-*` 模式

许多 `guidance()` 规则可以通过内置代码检查器配置强制执行，而无需自定义规则。这是最常见的加强模式——“不要做 X”映射到限制配置。

**ESLint:**

```js
// "不要从内部模块导入"
"no-restricted-imports": ["error", {
  patterns: [{ group: ["src/internal/*"], message: "使用公共 API。" }]
}],

// "不要调用 console.log"
"no-restricted-syntax": ["error", {
  selector: 'CallExpression[callee.object.name="console"]',
  message: "使用项目日志器。"
}],

// "不要使用 moment.js"
"no-restricted-imports": ["error", {
  paths: [{ name: "moment", message: "使用 dayjs 代替。" }]
}],
```

**Ruff:**

```toml
# "不要使用 os.system"
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"os.system".msg = "使用 subprocess.run 代替。"
```

**RuboCop:**

```yaml
# "生产环境中不要使用 puts" — 如果 Rails/Output 不适用
Custom/NoPuts:
  Enabled: true
```

当建议 `no-restricted-*` 变更时：

1. 显示所需的精确配置编辑（哪个文件，哪个部分）
2. 显示引用它的 `enforce()` 规则
3. 注意这会更改代码检查器配置，而不仅仅是规范

### 第 5 步：展示建议

将输出分组为等级：

**Tier 1：直接替换**（规则已启用——零风险）

```typescript
// 之前
"no-console": guidance("使用结构化日志器代替 console.log"),
// 之后
"no-console": enforce("eslint/no-console", "使用结构化日志器代替 console.log"),
```

**Tier 2：配置支持**（规则存在但需要配置选项）

```typescript
// 规范变更：
"no-moment": enforce("eslint/no-restricted-imports", "使用 dayjs 代替 moment。"),

// 配置变更需要（eslint.config.mjs）：
"no-restricted-imports": ["error", {
  paths: [{ name: "moment", message: "使用 dayjs 代替。" }]
}],
```

**Tier 3：需要安装插件**

```
"cognitive-complexity": guidance("保持函数简单")
→ 安装 eslint-plugin-sonarjs，启用 sonarjs/cognitive-complexity
→ enforce("eslint/sonarjs/cognitive-complexity", "保持函数简单")
```

**Tier 4：无匹配**（保持为 guidance——是未来规则合成技能的候选项）

```
"research-first": guidance("先搜索不熟悉的 API。")
→ 没有代码检查器规则可以强制执行。暂时保持为 guidance。
→ (自定义规则合成计划中但尚未发布。)
```

### 第 6 步：应用变更

**在自动模式下：**

1. 应用所有 Tier 1 变更（编辑规范文件，将 `guidance()` 替换为 `enforce()`）
2. 运行 `npm run build && npx vigiles compile` 验证每个变更是否编译
3. 如果任何编译失败，回滚该特定变更并报告错误
4. 提交所有成功的变更
5. 将 Tier 2-4 作为摘要供用户审查

**在交互式模式下：**

1. 展示所有等级
2. 询问用户要应用哪些建议
3. 对于批准的 Tier 2 变更：编辑代码检查器配置，然后编辑规范
4. 运行 `npm run build && npx vigiles compile` 验证
5. 如果编译失败，报告错误并回滚

**对于 Tier 4（无匹配）：** 告知用户这些规则保持为 guidance——自定义规则合成是计划中的技能，尚未可用。
