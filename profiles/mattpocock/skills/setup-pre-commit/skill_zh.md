# 设置预提交钩子

## 这会设置的内容

- **Husky** 预提交钩子
- **lint-staged** 在所有已暂存文件上运行 Prettier
- **Prettier** 配置（如果缺失）
- 预提交钩子中的 **typecheck** 和 **test** 脚本

## 步骤

### 1. 检测包管理器

检查是否存在 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun）。使用存在的那个。如果不确定，默认为 npm。

### 2. 安装依赖

作为开发依赖安装：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录并在 `package.json` 中添加 `prepare: "husky"`。

### 4. 创建 `.husky/pre-commit`

编写这个文件（Husky v9+ 不需要 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**调整**：将 `npm` 替换为检测到的包管理器。如果仓库的 `package.json` 中没有 `typecheck` 或 `test` 脚本，则省略这些行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 创建 `.prettierrc`（如果缺失）

只有在不存在 Prettier 配置时才创建。使用这些默认值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] `package.json` 中的 `prepare` 脚本是 `"husky"`
- [ ] `prettier` 配置存在
- [ ] 运行 `npx lint-staged` 验证其是否正常工作

### 8. 提交

暂存所有已更改/创建的文件，并使用消息提交：`Add pre-commit hooks (husky + lint-staged + prettier)`

这将运行新的预提交钩子：一个良好的烟雾测试，确保一切正常工作。

## 注意事项

- Husky v9+ 的钩子文件不需要 shebang
- `prettier --ignore-unknown` 会跳过 Prettier 无法解析的文件（如图片等）
- 预提交会先运行 lint-staged（快速，仅暂存），然后运行完整的 typecheck 和测试
