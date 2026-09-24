# 设置预提交钩子

## 本设置包含的内容

- **Husky** 预提交钩子
- **lint-staged** 对所有暂存文件运行 Prettier
- **Prettier** 配置（如缺失）
- 预提交钩子中的 **typecheck** 和 **test** 脚本

## 步骤

### 1. 检测包管理器

检查是否存在 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）或 `bun.lockb`（bun）。使用其中存在的一种。如果不确定，默认使用 npm。

### 2. 安装依赖

作为 devDependencies 安装：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录，并在 `package.json` 中添加 `prepare: "husky"`。

### 4. 创建 `.husky/pre-commit`

写入此文件（Husky v9+ 无需 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**适配**：将 `npm` 替换为检测到的包管理器。如果仓库的 `package.json` 中没有 `typecheck` 或 `test` 脚本，请省略这些行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 创建 `.prettierrc`（如缺失）

仅在没有 Prettier 配置存在时创建。使用以下默认配置：

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
- [ ] `package.json` 中的 `prepare` 脚本为 `"husky"`
- [ ] 存在 Prettier 配置
- [ ] 运行 `npx lint-staged` 以验证其正常工作

### 8. 提交

暂存所有变更/创建的文件，并提交，提交消息为：`Add pre-commit hooks (husky + lint-staged + prettier)`

这将运行新的预提交钩子：这是一次良好的冒烟测试，确认一切正常运行。

## 注意事项

- Husky v9+ 不需要在钩子文件中使用 shebang
- `prettier --ignore-unknown` 会跳过 Prettier 无法解析的文件（如图片等）
- 预提交钩子会先运行 lint-staged（快速，仅处理暂存文件），然后运行完整的 typecheck 和测试
