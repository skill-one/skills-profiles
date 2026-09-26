# 升级 React Native

通过获取并应用来自
[React Native 升级辅助工具](https://react-native-community.github.io/upgrade-helper/)的 diff，将 React Native Community CLI 项目升级到目标版本。

<!-- LLM_EXCLUDE: 以下仅限人类上下文 -->
> [!注意]
> **Expo 用户：** 对于 Expo 项目或更复杂的升级场景，请尝试：
> - [expo/skills/upgrading-expo](https://skills.sh/expo/skills/upgrading-expo)
> - [callstackincubator/agent-skills/upgrading-react-native](https://skills.sh/callstackincubator/agent-skills/upgrading-react-native)
<!-- /LLM_EXCLUDE -->

## 调用方式

```
/upgrade-react-native <目标版本>
```

- `<目标版本>` — 要升级到的 React Native 版本（例如 `0.79.0`）。

## 分步操作

按以下步骤**按顺序**执行。不要跳过步骤。

### 1. 检测当前 React Native 版本

读取项目的根 `package.json`，并从 `dependencies`（或 `devDependencies`）中提取 `react-native` 版本。去除任何 semver 范围前缀（`^`、`~`、`>=` 等）以获取确切的当前版本字符串。

如果无法确定当前版本，请停止并询问用户。

### 2. 验证目标版本

- 目标版本必须是一个有效的 semver 字符串（例如 `0.79.0`）。
- 它必须**大于**当前版本。
- 通过检查以下链接验证目标版本是否存在：
  ```
  https://raw.githubusercontent.com/react-native-community/rn-diff-purge/master/RELEASES
  ```
  获取此文件并确认目标版本是否列出。如果没有，请报告最接近的可用版本并询问用户选择。

### 3. 获取升级 diff

获取两个版本之间的统一 diff：

```
https://raw.githubusercontent.com/react-native-community/rn-diff-purge/diffs/diffs/<当前版本>..<目标版本>.diff
```

例如，要从 `0.73.0` 升级到 `0.74.0`：

```
https://raw.githubusercontent.com/react-native-community/rn-diff-purge/diffs/diffs/0.73.0..0.74.0.diff
```

如果无法获取 diff（404），可能是因为确切的补丁版本不可用。尝试最近的次要版本（例如 `0.73.0` 而不是 `0.73.2`）。报告您尝试的内容，并在需要时询问用户。

### 4. 解析 diff 并映射文件路径

diff 使用模板项目名称 `RnDiffApp`。将 diff 中的每个路径映射到实际项目：

| Diff 路径前缀 | 实际项目路径 |
|------------------|---------------------|
| `RnDiffApp/` | 项目根 (`./`) |

此外，将模板标识符的出现替换为项目的实际名称：

| 模板值 | 替换为 |
|----------------|--------------|
| `RnDiffApp` | 项目的应用名称（从 `app.json` → `name`，或 `package.json` 中的 `name` 字段） |
| `rndiffapp` | 项目应用名称的小写版本 |
| `com.rndiffapp` | 项目的 Android 包名（从 `android/app/build.gradle` 或 `android/app/src/main/AndroidManifest.xml`） |

### 5. 审查 diff 并规划变更

在进行任何编辑之前，审查整个 diff 并对变更进行分类：

1. **直接应用** — 项目中存在的文件，其原始内容与 diff 的 `-` 行匹配。这些可以直接应用。
2. **冲突** — 项目内容与模板已分叉的文件（自定义修改）。这些需要手动合并。
3. **新文件** — diff 中存在而项目尚未存在的文件。创建它们。
4. **已删除文件** — diff 删除的文件。仅当项目未向其添加自定义内容时才删除它们。

在继续之前向用户展示此计划。按区域分组变更：

- **根配置文件** (`package.json`、`metro.config.js`、`.eslintrc.js` 等）
- **iOS 本地文件** (`ios/` 目录）
- **Android 本地文件** (`android/` 目录）
- **JavaScript/TypeScript 源代码**（如果任何模板源文件已更改）
- **第三方本地依赖项**（来自步骤 7 — 包括任何在那里识别的版本提升）

### 6. 应用变更

按照步骤 5 的计划应用变更：

- 对于 **直接应用**：编辑文件以匹配 diff 的 `+` 行。
- 对于 **冲突**：应用升级变更，同时保留项目的自定义内容。使用您的判断进行合并。如有不确定，请显示两个版本并询问用户。
- 对于 **新文件**：在映射路径处创建它们。
- 对于 **已删除文件**：删除它们。

**重要注意事项：**

- 更新 `package.json` 时，更新 `react-native` 版本以及 diff 中提到的任何相关依赖项（例如 `react`、`@react-native/*` 包、Gradle 版本、CocoaPods 版本）。
- 不要自动运行 `npm install` / `yarn install` / `pod install`。告知用户升级后需要执行这些步骤。
- 参考 [参考资料](#references) 部分了解特定版本的 breaking changes 和迁移说明。

### 7. 更新第三方本地依赖项

扫描 `package.json` 中的 `dependencies` 和 `devDependencies`，查找包含 **本地代码** 的第三方 React Native 库（即它们有 `ios/` 或 `android/` 目录，或已知为本地模块）。常见示例包括 `react-native-screens`、`react-native-reanimated`、`react-native-gesture-handler`、`@react-native-async-storage/async-storage`、`react-native-svg`、`react-native-safe-area-context` 等。

对于每个候选依赖项：

1. **从其 GitHub 仓库或 npm 页面获取库的 README**。
2. **查找 React Native 版本兼容性表或部分** — 许多本地库记录其包支持哪些 React Native 版本（例如“兼容性”或“版本支持”表）。
3. **如果 README 包含兼容性表**，将目标 React Native 版本映射到特定库版本，请将此库版本提升包含在升级计划中。
4. **如果 README 未提及与 React Native 版本的版本兼容性**，请跳过库 — 不要猜测或假设需要升级。

在步骤 5 中将 diff 基于变更和这些依赖项提升一起呈现（分组在 **第三方本地依赖项** 部分）。对于每个：

- 说明当前版本、建议版本，并链接到您找到的兼容性信息。
- 如果多个主版本兼容，请优先选择支持目标 React Native 版本的最新的稳定版本。

作为步骤 6 的一部分，将这些版本提升应用到 `package.json`。

### 8. 迁移到严格的 TypeScript API（目标 >= 0.87）

React Native 0.87 将 [严格的 TypeScript API](https://reactnative.dev/docs/strict-typescript-api) 设为默认值。当升级跨越此边界（当前版本 < 0.87，目标 >= 0.87）并且项目使用 TypeScript（存在 `tsconfig.json`）时，项目类型检查将受到影响，此步骤是 **必需的** — 不要静默跳过。

询问用户他们更喜欢：

1. **立即迁移（推荐）** — 运行 [`migrate-to-strict-api`](https://skills.sh/react-native-community/skills/migrate-to-strict-api) 技能（`/migrate-to-strict-api`），它处理依赖项兼容性、深度导入重写和已知的 breaking 类型变更。
2. **使用临时 opt-out 推迟** — 在 `tsconfig.json` 中的 `compilerOptions` 中添加 `"customConditions": ["react-native", "react-native-legacy-deep-imports"]`，保留两个条目。告诉用户这是一个临时 opt-out，将在未来版本中删除。

对于目标版本低于 0.87，或没有 TypeScript 的项目，跳过此步骤，不要未经提示建议迁移。

### 9. 升级后检查清单

应用所有变更后，向用户展示检查清单：

- [ ] 运行 `npm install` 或 `yarn install` 更新 JS 依赖项
- [ ] 运行 `cd ios && bundle exec pod install`（或 `npx pod-install`）更新本地 iOS 依赖项
- [ ] 运行 Android 的干净构建：`cd android && ./gradlew clean`
- [ ] 运行 iOS 的干净构建：`cd ios && xcodebuild clean`
- [ ] 在两个平台上运行应用以验证其启动
- [ ] 运行项目的测试套件
- [ ] （TypeScript，目标 >= 0.87）运行 `npx tsc --noEmit` 以确认严格的 TypeScript API 迁移或从步骤 8 opt-out
- [ ] 检查任何冲突解决的正确性
- [ ] 查看 [React Native 变更日志](https://github.com/facebook/react-native/blob/main/CHANGELOG.md) 以获取额外的 breaking changes
- [ ] 查看 [升级辅助工具 Web UI](https://react-native-community.github.io/upgrade-helper/?from=<当前版本>&to=<目标版本>) 以获取任何补充说明

## 参考资料

查阅这些以获取特定版本的迁移指南：

- [references/upgrade-helper-api.md](./references/upgrade-helper-api.md) — 如何以编程方式获取 diffs 和版本列表
- [migrate-to-strict-api](https://skills.sh/react-native-community/skills/migrate-to-strict-api) — 严格的 TypeScript API 迁移的配套技能（从 0.87 开始默认）
