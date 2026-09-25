# 卫生检查

VS Code 会作为 git 预提交钩子运行卫生检查。如果卫生检查失败，提交将被拒绝。

## 运行卫生检查

**在宣布工作完成之前，请始终运行预提交卫生检查。** 这可以捕获会阻止提交的问题。

要对暂存文件运行卫生检查：

```bash
npm run precommit
```

这会执行 `node --experimental-strip-types build/hygiene.ts`，该命令只会扫描**暂存文件**（来自 `git diff --cached`）。

要直接检查特定文件（无需先暂存）：

```bash
node --experimental-strip-types build/hygiene.ts 路径/到/文件.ts
```

## 检查内容

卫生检查器会扫描暂存文件，查找包括但不限于以下问题：

- **Unicode 字符**：拒绝非 ASCII 字符（破折号、曲柄引号、表情符号等）。在注释和代码中使用 ASCII 等价物。使用 `// allow-any-unicode-next-line` 或 `// allow-any-unicode-comment-file` 来抑制。
- **双引号字符串**：仅使用 `"双引号"` 用于外部化（本地化）字符串。其他地方使用 `'单引号'`。
- **版权声明**：所有文件都必须包含 Microsoft 版权声明。
- **缩进**：仅使用制表符缩进，不允许使用空格。
- **格式**：TypeScript 文件必须与格式化器输出匹配（运行 `Format Document` 来修复）。
- **ESLint**：使用 ESLint 对 TypeScript 文件进行代码检查。
- **Stylelint**：使用 stylelint 对 CSS 文件进行代码检查。
