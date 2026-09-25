# 创建 React Native 库

## 概述

使用此技能来搭建一个独立的 React Native 库，或在一个现有应用中搭建一个本地库，然后继续使用正确的实现文档。

示例：

- 仅使用 JavaScript 的库，可能使用其他 React Native 库
- 本地模块，将原生功能暴露给 JavaScript
- 原生 UI 组件，在 React Native 中渲染原生视图

首先选择一个流程：

- 使用 [scaffold-library.md][scaffold-library] 创建一个可能发布到 npm 的新库
- 使用 [local-library.md][local-library] 在 React Native 应用中暴露原生功能

## 何时应用

在以下情况下使用此技能：

- 使用 `create-react-native-library` 创建或处理 React Native 库
- 在现有应用中创建原生模块或视图
- 包装原生 SDK 并将其暴露给 React Native

## 快速参考

```bash
# 在搭建前检查当前选项
npx create-react-native-library@latest --help

# 使用 turbo modules 和 Expo 示例应用搭建库
npx create-react-native-library@latest awesome-library \
  --no-interactive \
  --yes \
  --description "库的简要描述" \
  --type turbo-module \
  --languages kotlin-objc \
  --example expo

# 在现有应用中搭建本地 Turbo Module
cd MyApp
npx create-react-native-library@latest awesome-library \
  --local \
  --no-interactive \
  --yes \
  --description "库的简要描述" \
  --type turbo-module \
  --languages kotlin-objc
```

## 参考

| 文件                                    | 描述                                             |
| --------------------------------------- | ------------------------------------------------------- |
| [scaffold-library.md][scaffold-library] | 搭建新库并默认使用 Expo 示例  |
| [local-library.md][local-library]       | 在现有应用中添加本地库并自动链接 |

## 问题 -> 技能映射

| 问题                                      | 从此开始                           |
| -------------------------------------------- | ------------------------------------ |
| 需要新库的骨架                          | [scaffold-library][scaffold-library] |
| 需要在应用中添加本地原生库              | [local-library][local-library]       |

[scaffold-library]: references/scaffold-library.md
[local-library]: references/local-library.md
