# 将 Grafana 插件迁移到 React 19

Grafana 13（2026年4月）将从 React 18 迁移到 React 19。不兼容的插件将会失效。
**不要将 React 升级到 19** — 仅进行向前兼容的更改。

所有更改都在 **一个 PR** 中进行。按顺序执行步骤。切勿手动编辑 `yarn.lock`。

---

## 第 1 步：检测插件上下文

```bash
PLUGIN_JSON=$([ -f src/plugin.json ] && echo "src/plugin.json" \
  || ([ -f plugin/src/plugin.json ] && echo "plugin/src/plugin.json" || echo ""))
PKG_JSON=$([ -f package.json ] && echo "package.json" \
  || ([ -f plugin/package.json ] && echo "plugin/package.json" || echo ""))
PLUGIN_ID=$(jq -r '.id' $PLUGIN_JSON 2>/dev/null)
[ -f yarn.lock ] && PM="yarn" || ([ -f pnpm-lock.yaml ] && PM="pnpm" || PM="npm")
CP_VERSION=$(jq -r '.version' .config/.cprc.json 2>/dev/null)
echo "PLUGIN_ID=$PLUGIN_ID  PM=$PM  CP=$CP_VERSION"
```

如果 `PLUGIN_ID` 为空，请让用户输入插件根路径。

---

## 第 2 步：扫描兼容性问题

构建插件并运行 React 19 兼容性扫描器：

```bash
npm run build 2>&1 | tail -5
npx -y @grafana/react-detect@latest 2>&1
```

保存输出。它标记：

- `jsxRuntimeImport` / `__SECRET_INTERNALS` → 第 4 步修复此问题
- `defaultProps` / `propTypes` / `ReactDOM.render` → 第 8 步（源代码修复）
- `findDOMNode` → 第 6 步（依赖版本升级）或第 8 步（源代码修复）

如果构建失败（插件之前未构建过），请跳过此步骤，并在第 9 步后运行 react-detect。如果输出显示“未检测到破坏性更改”，仍然继续——jsx-runtime 外部化和 grafanaDependency 升级始终是必需的。

在第 9 步后重新运行 react-detect 以确认所有问题已解决。

---

## 第 3 步：更新 `@grafana/create-plugin`

脚手架更新引入了外部提取、jest 模拟、Docker 修复和 webpack 改进，这些对于 React 19 是必需的。**始终在 `add externalize-jsx-runtime` 之前执行此操作。**

需要干净的 git 工作树。如果尚未在特性分支上，请先创建一个。

### 运行更新

```bash
npx @grafana/create-plugin@latest update 2>&1
```

### 如果 `yarn install` 失败并显示“引擎不兼容”

更新会运行一个不带 `--ignore-engines` 的中间 `yarn install`。手动完成它：

```bash
yarn install --ignore-scripts --ignore-engines 2>&1 | tail -10
```

提交中间状态并重新运行：

```bash
git add -A && git commit -m "chore: 中间 create-plugin 更新" --no-verify
npx @grafana/create-plugin@latest update 2>&1
```

### 如果 ESLint 9 迁移（004）因解析错误失败

自动迁移可能会在具有复杂 ESLint 配置的插件上生成无效的 JS。
**不要跳过** — 提交已成功的内容，然后手动完成 ESLint 9 迁移：

```bash
git add -A && git commit -m "chore: 更新 create-plugin (ESLint 9 迁移手动)" --no-verify
```

然后按照下面的“完成 ESLint 9 迁移”部分来完成。

### 更新后

始终运行安装和验证：

```bash
yarn install --ignore-scripts --ignore-engines 2>&1 | tail -10
cat .config/.cprc.json
```

如果有更改，请提交：

```bash
git add -A && git diff --cached --quiet || git commit -m "chore: 更新 create-plugin 脚手架" --no-verify
```

---

## 第 3b 步：完成 ESLint 9 迁移

`create-plugin update` 将 ESLint 升级到 v9，这需要扁平配置（`eslint.config.js`）而不是 `.eslintrc`。无论自动迁移（004）成功、部分成功还是失败，**你必须确保 ESLint 在继续之前可以正常工作。**

### 检查当前状态

```bash
ls eslint.config.js .eslintrc* .config/.eslintrc* 2>/dev/null
npx eslint --version 2>&1
```

三种情况：

**A) `eslint.config.js` 存在且 `yarn lint` 通过** — 自动迁移成功。继续。

**B) `eslint.config.js` 存在但 `yarn lint` 失败** — 部分迁移。修复问题：

```bash
yarn lint 2>&1 | head -30
```

常见修复：
- `Invalid option '--ignore-path'` 或 `Invalid option '--ext'` → 从 `package.json` 中的 `lint` 脚本中删除这些标志。在 ESLint v9 扁平配置中，忽略和文件匹配在 `eslint.config.js` 内部配置，而不是通过 CLI 标志配置。更新为：`eslint --cache .`
- `Cannot find module 'eslint-plugin-deprecation'` → 从 `eslint.config.js` 中删除导入/引用（由 `@typescript-eslint/no-deprecated` 替代）
- 其他已弃用的插件导入 → 如果已删除包，则从配置中删除它们

**C) 不存在 `eslint.config.js`** — 自动迁移失败。手动创建一个：

```bash
ls node_modules/@grafana/eslint-config/flat.js 2>/dev/null
```

如果 `flat.js` 存在，使用它作为基础创建 `eslint.config.js`：

```js
import grafanaConfig from '@grafana/eslint-config/flat';

export default [
  ...grafanaConfig,
  {
    ignores: ['**/dist/', '**/node_modules/', '**/.config/', '**/coverage/'],
  },
];
```

然后从旧的 `.eslintrc` 中将任何自定义规则迁移到数组中的附加配置对象中。
创建扁平配置后：
1. 更新 `lint` 脚本：`"lint": "eslint --cache ."`
2. 删除根 `.eslintrc`（保留 `.config/.eslintrc` — 它是脚手架的，无害）

### 验证 lint 是否正常工作

```bash
yarn lint 2>&1 | tail -20
```

使用 `yarn lint --fix` 修复可自动修复的问题。提交：

```bash
git add -A && git diff --cached --quiet || git commit -m "chore: 完成 ESLint 9 扁平配置迁移" --no-verify
```

---

## 第 4 步：外部化 jsx-runtime

**始终使用 `create-plugin add` 命令。** 需要干净的 git 工作树。

```bash
npx @grafana/create-plugin@latest add externalize-jsx-runtime 2>&1
```

验证：

```bash
grep "jsx-runtime" .config/bundler/externals.ts 2>/dev/null
```

- 找到 → 提交并继续。
- 未找到 → 命令失败。**仅在此之后** 才能手动将外部添加到根 `webpack.config.ts`：

```ts
externals: ['react/jsx-runtime', 'react/jsx-dev-runtime'],
```

提交：

```bash
git add -A && git diff --cached --quiet || git commit -m "feat: 外部化 jsx-runtime" --no-verify
```

---

## 第 5 步：升级 `grafanaDependency`

```bash
jq -r '.dependencies.grafanaDependency' $PLUGIN_JSON
```

如果还不是 `>=12.3.0`，请更新它。第 3 步中的 `create-plugin add` 可能已经完成了此操作。

---

## 第 6 步：升级依赖项

### Faro（如果存在）

```bash
grep '"@grafana/faro' $PKG_JSON
```

| 包 | 目标 |
|---------|--------|
| `@grafana/faro-react` | `^2.2.3` |
| `@grafana/faro-web-sdk` | `^2.2.3` |
| `@grafana/faro-web-tracing` | `^2.0.0` |

### Grafana 包

```bash
grep '"@grafana/' $PKG_JSON | grep -v faro | grep -v create-plugin
```

将 `@grafana/data`、`@grafana/runtime`、`@grafana/schema`、`@grafana/ui` 升级到 `^12.2.0` 或更高版本。
如果插件使用翻译或 `@grafana/scenes` 需要，添加 `@grafana/i18n@^12.2.0`。

### React 类型

将 `react` 和 `react-dom` 升级到 `^18.3.0`（提前暴露 React 19 问题）。
如果缺少，请将 `@types/react@^18.3.0` 和 `@types/react-dom@^18.3.0` 添加到 devDependencies。

### 删除已弃用的包

如果存在，从 devDependencies 中删除：
- `eslint-plugin-deprecation`（由 `@typescript-eslint/no-deprecated` 替代）
- `@types/testing-library__jest-dom`（由 `setupTests.d.ts` 替代）

### 破坏的传递依赖项

如果 `yarn install` 因陈旧的 git 引用而失败，**不要编辑 yarn.lock**。添加一个 `resolutions` 条目：

```json
"resolutions": {
  "<package-name>": "<working-version-or-git-ref>"
}
```

然后删除 `yarn.lock` 和 `node_modules` 并重新安装：

```bash
rm -rf node_modules yarn.lock
yarn install --ignore-engines 2>&1 | tail -10
```

---

## 第 7 步：修复未满足的 `@openfeature/web-sdk` 依赖项

`@grafana/runtime` 依赖于 `@openfeature/react-sdk`，它将 `@openfeature/web-sdk` 作为**依赖项**。Yarn v1（经典）不会自动安装依赖项。

检查插件是否使用 yarn 经典：

```bash
yarn --version 2>&1 | head -1
```

如果版本以 `1.` 开头，请检查警告：

```bash
yarn install --ignore-engines 2>&1 | grep "unmet peer dependency.*openfeature/web-sdk"
```

如果发现警告：

```bash
yarn add -D @openfeature/web-sdk @openfeature/core --ignore-engines
```

**跳过条件**：Yarn v2+ 或 npm v7+（依赖项会自动安装）。

---

## 第 8 步：修复源代码问题

```bash
grep -rn "ReactDOM\.render\|ReactDOM\.unmountComponentAtNode\|ReactDOM\.findDOMNode" src/ --include="*.tsx" --include="*.ts"
grep -rn "\.defaultProps\s*=" src/ --include="*.tsx" --include="*.ts"
grep -rn "\.propTypes\s*=" src/ --include="*.tsx" --include="*.ts"
grep -rn "contextTypes\|getChildContext" src/ --include="*.tsx" --include="*.ts"
grep -rn "createFactory" src/ --include="*.tsx" --include="*.ts"
grep -rn "ChangeEvent<HTMLInputElement>" src/ --include="*.tsx" --include="*.ts"
```

| 模式 | 修复 |
|---------|-----|
| `ReactDOM.render()` | `createRoot(container).render(element)` |
| **函数** 组件上的 `defaultProps` | 移动到解构参数默认值 |
| **类** 组件上的 `defaultProps` | 保留 — 仍然有效 |
| `propTypes` | 删除 |
| `contextTypes` / `getChildContext` | 使用 `React.createContext()` + `useContext()` |
| `createFactory` | 使用 JSX 或 `createElement()` |
| 复选框上的 `ChangeEvent<HTMLInputElement>` | 更改为 `FormEvent<HTMLInputElement>` |

---

## 第 9 步：构建、类型检查、测试

```bash
rm -rf node_modules dist
yarn install --ignore-engines 2>&1 | tail -10
yarn build 2>&1 | tail -10
yarn typecheck 2>&1 | tail -10
yarn test --watchAll=false 2>&1 | tail -10
```

| 错误 | 修复 |
|-------|-----|
| `Cannot find module 'react/jsx-runtime'` | 第 4 步未应用 — 重新运行 `create-plugin add` |
| `Cannot find module '@openfeature/web-sdk'` | 第 7 步 — `yarn add -D @openfeature/web-sdk @openfeature/core` |
| `Can't resolve '@grafana/i18n'` | `yarn add @grafana/i18n@^12.2.0` |
| `Cannot read properties of undefined (reading 'ReactCurrentOwner')` | 升级 `@grafana-cloud/*` 包 — 见第 6 步 |
| 图标按钮上的 `aria-label` 缺失 | 添加 `aria-label` 属性（较新的 `@grafana/ui` 需要） |
| `yarn.lock` 中的陈旧 git 哈希 | 在 `package.json` 中添加 `resolutions`，删除锁文件，重新安装 |

对于已知问题（i18n 崩溃、`@grafana/schema` 类型破坏、publicPath 不匹配），请参阅
[references/known-issues.md](references/known-issues.md)。

---

## 第 10 步：更新 CI（如果适用）

```bash
grep -rn "plugin-ci-workflows\|e2e-version" .github/workflows/ 2>/dev/null
```

- `plugin-ci-workflows@main` 或 >= 6.0.0 → 已经测试 React 19。无需更改。
- `plugin-actions/e2e-version` → 添加 `skip-grafana-react-19-preview-image: false`。
- 均未找到 → 使用 `GRAFANA_VERSION=dev-preview-react19 docker compose up --build` 手动测试。

---

## 第 11 步：合并并推送

```bash
git reset --soft origin/main
git add -A
git commit -m "fix: 为 React 19 兼容性准备插件"
```

提交信息正文应列出：create-plugin 版本更改、ESLint 9 迁移、关键依赖项升级和任何源代码修复。

---

## 参考

- [迁移指南](https://grafana.com/developers/plugin-tools/migration-guides/update-from-grafana-versions/migrate-12_x-to-13_x)
- [React 19 博客文章（插件开发者）](https://grafana.com/blog/react-19-is-coming-to-grafana-what-plugin-developers-need-to-know/)
- [React 19 更新日志](https://react.dev/blog/2024/12/05/react-19)
- [grafana-collector-app #1337](https://github.com/grafana/grafana-collector-app/pull/1337) — 使用 create-plugin 更新 + 源代码修复的完整迁移
- [grafana/scenes 问题](https://github.com/grafana/scenes/issues) — 上游 i18n 跟踪
