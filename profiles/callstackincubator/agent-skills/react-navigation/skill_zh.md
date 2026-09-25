# React Navigation

## 概述

React Navigation 的导航 UI 构建指南。

此技能仅适用于 React Navigation 7 版本。API 和模式可能不适用于不同版本。

## API 选择

React Navigation 提供两种 API：基于对象的 `静态 API` 和基于组件的 `动态 API`。

- **现有应用**：检查当前的导航设置，并在使用参考时遵循相同的 API 风格
- **新应用**：如果应用还没有现有的导航设置，优先选择 `静态 API`

## 适用场景

在以下情况下参考此技能：

- 构建 stack、tabs、drawers、sheets 等导航 UI 模式
- 配置标题栏和其他内置导航器 UI
- 处理导航 UI 中的安全区域和 insets

## 参考

| 文件                                        | 描述                    |
| ------------------------------------------- | ------------------------------ |
| [stacks.md][stacks]                         | 基于 stack 的导航         |
| [form-sheet.md][form-sheet]                 | 底部 sheet 和表单 sheets   |
| [bottom-tabs.md][bottom-tabs]               | 跨平台底部 tabs           |
| [native-bottom-tabs.md][native-bottom-tabs] | 原生底部 tabs             |
| [material-top-tabs.md][material-top-tabs]   | 可滑动的顶部 tabs         |
| [drawers.md][drawers]                       | Drawer 导航和侧边栏      |
| [header.md][header]                         | 配置标题栏               |
| [safe-areas.md][safe-areas]                 | 安全区域处理             |

## 问题 -> 技能映射

| 问题                                                                   | 从此开始                                  |
| ------------------------------------------------------------------------- | ------------------------------------------- |
| 在 stack 中显示屏幕和模态框                                           | [stacks.md][stacks]                         |
| 显示底部 sheet 或表单 sheets                                          | [form-sheet.md][form-sheet]                 |
| 在支持 web 的底部 tabs 或响应式侧边栏中显示屏幕                        | [bottom-tabs.md][bottom-tabs]               |
| 在 iOS & Android 的原生 tabs 中显示屏幕                              | [native-bottom-tabs.md][native-bottom-tabs] |
| 在可滑动的顶部 tabs 中显示内容                                        | [material-top-tabs.md][material-top-tabs]   |
| 使用 Drawer 或侧边栏                                                 | [drawers.md][drawers]                       |
| 配置底部 tabs 或 Drawer 导航器中的标题栏                              | [header.md][header]                         |
| 处理安全区域，如状态栏、标题栏 insets、tab 栏 insets 等                | [safe-areas.md][safe-areas]                 |

[stacks]: references/stacks.md
[form-sheet]: references/form-sheet.md
[safe-areas]: references/safe-areas.md
[bottom-tabs]: references/bottom-tabs.md
[native-bottom-tabs]: references/native-bottom-tabs.md
[material-top-tabs]: references/material-top-tabs.md
[drawers]: references/drawers.md
[header]: references/header.md
