# 升级 React Native

## 概述

涵盖完整的 React Native 升级工作流程：通过升级助手获取模板差异、依赖更新、Expo SDK 步骤以及常见陷阱。

## 典型升级顺序

1. **路线**：通过 `[upgrading-react-native.md][upgrading-react-native]` 选择正确的升级路径
2. **差异**：使用升级助手获取规范模板差异，通过 `[upgrade-helper-core.md][upgrade-helper-core]`
3. **依赖**：评估并更新第三方包，通过 `[upgrading-dependencies.md][upgrading-dependencies]`
4. **React**：如果升级，对齐 React 版本，通过 `[react.md][react]`
5. **Expo**（如果适用）：应用 Expo SDK 层，通过 `[expo-sdk-upgrade.md][expo-sdk-upgrade]`
6. **验证**：运行升级后检查，通过 `[upgrade-verification.md][upgrade-verification]`

```bash
# 快速启动：检测当前版本并获取差异
npm pkg get dependencies.react-native --prefix "$APP_DIR"
npm view react-native dist-tags.latest

# 示例：从 0.76.9 升级到 0.78.2
# 1. 获取模板差异
curl -L -f -o /tmp/rn-diff.diff \
  "https://raw.githubusercontent.com/react-native-community/rn-diff-purge/diffs/diffs/0.76.9..0.78.2.diff" \
  && echo "Diff 下载成功" || echo "ERROR: 差异未找到，检查版本"
# 2. 查看已更改文件
grep -n "^diff --git" /tmp/rn-diff.diff
# 3. 更新 package.json，应用原生更改，然后安装 + 重建
npm install --prefix "$APP_DIR"
cd "$APP_DIR/ios" && pod install
# 4. 验证：两个平台都必须成功构建
npx react-native build-android --mode debug --no-packager
xcodebuild -workspace "$APP_DIR/ios/App.xcworkspace" -scheme App -sdk iphonesimulator build
```

## 何时应用

参考这些指南的情况：
- 将 React Native 应用迁移到更高版本
- 调整升级助手生成的原生配置更改
- 验证破坏性变更的发布说明

## 快速参考

| 文件 | 描述 |
|------|-------------|
| [upgrading-react-native.md][upgrading-react-native] | 路由器：选择正确的升级路径 |
| [upgrade-helper-core.md][upgrade-helper-core] | 核心升级助手工作流程和可靠性门禁 |
| [upgrading-dependencies.md][upgrading-dependencies] | 依赖兼容性检查和迁移规划 |
| [react.md][react] | React 和 React 19 升级对齐规则 |
| [expo-sdk-upgrade.md][expo-sdk-upgrade] | Expo SDK 特定的升级层（条件性） |
| [upgrade-verification.md][upgrade-verification] | 升级后验证清单，包括代理-设备辅助检查 |
| [monorepo-singlerepo-targeting.md][monorepo-singlerepo-targeting] | 单一仓库和多仓库应用的目标定位和命令作用域 |

## 问题 → 技能映射

| 问题 | 从此开始 |
|---------|------------|
| 需要升级 React Native | [upgrade-helper-core.md][upgrade-helper-core] |
| 需要依赖风险评估和迁移选项 | [upgrading-dependencies.md][upgrading-dependencies] |
| 需要React/React 19包对齐 | [react.md][react] |
| 需要先进行工作流程路由 | [upgrading-react-native.md][upgrading-react-native] |
| 需要Expo SDK特定步骤 | [expo-sdk-upgrade.md][expo-sdk-upgrade] |
| 需要手动或代理辅助回归验证 | [upgrade-verification.md][upgrade-verification] |
| 需要仓库/应用命令作用域 | [monorepo-singlerepo-targeting.md][monorepo-singlerepo-targeting] |

[upgrading-react-native]: references/upgrading-react-native.md
[upgrade-helper-core]: references/upgrade-helper-core.md
[upgrading-dependencies]: references/upgrading-dependencies.md
[react]: references/react.md
[expo-sdk-upgrade]: references/expo-sdk-upgrade.md
[upgrade-verification]: references/upgrade-verification.md
[monorepo-singlerepo-targeting]: references/monorepo-singlerepo-targeting.md
