---
name: react-native-tv-best-practices
description: 对 React Native TV 应用进行评估，涵盖焦点/D-pad 导航、10 英尺 UI 布局、电视播放/DRM 集成、低内存电视性能和电视无障碍功能。在构建、调试或审查 react-native-tvos、Expo TV、Amazon Vega/Kepler 或 React Native web TV 目标时使用，其中问题取决于遥控输入、电视焦点、电视封装、电视硬件或电视播放限制。
---

# React Native TV 最佳实践

## 概述

针对在 Apple TV、Android TV、Fire TV、Amazon Vega/Kepler 以及基于 Web 的 TV 目标（如 Tizen 或 webOS）上运行的 React Native 支持的应用的 TV 特定审查指南。

仅使用此技能处理 TV 差异：遥控输入、焦点引擎、10 英尺布局、平台打包、播放/DRM、低内存 TV 硬件和 TV 可访问性。对于普通的 React Native 性能或架构问题，请使用 [react-native-best-practices](../react-native-best-practices/SKILL.md)。

## 技能格式

参考文件按主题前缀分组：

- `focus-*`：焦点引擎、焦点指南、焦点事件性能
- `nav-*`：方向键导航、返回/菜单行为、键盘/搜索输入
- `design-*`：10 英尺字体、布局、颜色、焦点可见性
- `perf-*`：启动、内存、列表、动画和 TV 硬件上的网络限制
- `video-*`：播放架构、DRM/协议选择、调试
- `a11y-*`：TV 可访问性实现和审计检查
- `setup-*`：堆栈检测、设置、架构、跨平台行为
- `test-*` 和 `release-*`：测试覆盖率、E2E 和 CI/发布工作流

## 何时应用

当应用目标为 TV 平台并且工作涉及以下内容时，请应用此技能：

- 焦点移动、可见焦点、焦点恢复或遥控器/方向键输入
- TV 布局可读性、过扫描/安全区域或 10 英尺 UI 密度
- TV 播放器控件、清单、DRM、解码器支持或播放错误
- 低内存 TV 硬件上的性能，尤其是在视频或大型轮播时
- 使用屏幕阅读器、字幕、焦点顺序或仅遥控器交互的 TV 可访问性
- `react-native-tvos`、Expo TV、Amazon Vega/Kepler、Tizen 或 webOS 的平台设置

## 开始前 — 确定TV堆栈

此技能涵盖多个 TV 堆栈。**在标记设置问题之前检测应用目标的是哪一个** — 在 Vega/Kepler 或基于 Web 的 TV 应用上要求 `react-native-tvos`、tvOS Podfile 或 Android TV 清单会产生误报。

| 堆栈                                                 | 如何检测                                                                                     | 设置预期                                                                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **react-native-tvos** (Apple TV, Android TV, Fire TV) | 在 `package.json` 中 `"react-native": "npm:react-native-tvos@…"`                                       | tvOS Podfile (`platform :tvos`)；Android TV `leanback`/`LEANBACK_LAUNCHER` 清单条目；TV 模拟器/模拟器             |
| **Expo + react-native-tvos**                          | 上述 **加上** `@react-native-tvos/config-tv` 在 `app.json` 中                                         | `EXPO_TV=1` 预构建；`react-native-tvos` 版本必须与 Expo SDK 匹配；TV 上并非所有 Expo 功能/库都可用             |
| **Amazon Vega / Kepler**                              | Vega/Kepler SDK & 工具 (`@amazon-devices/*` 依赖项、Kepler 清单)；**没有** `react-native-tvos` | Amazon 的 Vega/Kepler 工具链 — `react-native-tvos`、tvOS Podfile 和 Android TV 清单**不适用**                   |
| **基于 Web 的 TV** (Tizen, webOS)                       | Web 打包器 (Rsbuild/webpack) + 平台打包；空间导航库                                           | 平台 SDK 打包；`@noriginmedia/norigin-spatial-navigation` 用于焦点                                                   |

焦点、10 英尺设计、性能、可访问性和播放器指南适用于所有这些 — 只有**设置/构建**预期是堆栈特定的。

## 审查规则

- 在设置建议之前解决目标堆栈。
- 优先考虑自然焦点顺序和焦点指南，而不是强制焦点调用或广泛的 `nextFocus*` 映射。
- 将焦点丢失、不可见焦点和损坏的返回/菜单行为视为导航错误。
- 在调整视觉细节之前，在 TV 距离检查可读性、安全区域和焦点状态。
- 在报告性能修复为完成之前，在支持的最弱 TV 设备上进行分析。
- 按层分离播放失败：清单请求、DRM 许可证交换、解码器能力、播放器状态和 React UI 控件。

## 优先级排序指南

| 优先级 | 类别       | 影响     | 前缀   |
|--------|------------|----------|--------|
| 1      | 焦点和方向键导航 | 关键     | `focus-*`, `nav-*` |
| 2      | 列表、动画和输入性能 | 关键     | `perf-*` |
| 3      | 播放和 DRM 失败   | 高       | `video-*` |
| 4      | 10 英尺可读性和布局 | 高       | `design-*` |
| 5      | TV 可访问性     | 高       | `a11y-*` |
| 6      | 堆栈设置、测试和发布 | 中       | `setup-*`, `test-*`, `release-*` |

## 快速参考

1. 从包文件、清单、原生文件夹和平台工具中检测 TV 堆栈。
2. 使用遥控器或方向键路径重现已知导航，而不是鼠标/触摸假设。
3. 确认焦点元素始终可见、可到达并在模态/路由后恢复。
4. 在更改 React 控件之前，从网络/DRM 层向上检查播放失败。
5. 在支持的最弱 TV 目标上测量列表、动画、内存和启动工作。

## 参考

### 焦点和导航

| 文件               | 影响     | 描述             |
|--------------------|----------|------------------|
| [focus-management.md](references/focus-management.md) | 关键     | 焦点引擎、焦点指南、`nextFocus*` 和焦点恢复 |
| [focus-performance.md](references/focus-performance.md) | 关键     | 避免因焦点事件处理导致的帧丢失 |
| [nav-directional.md](references/nav-directional.md) | 关键     | 跨 TV 平台的方向导航规则 |
| [nav-patterns.md](references/nav-patterns.md) | 关键     | 全局/局部导航、模态、标签和返回行为 |
| [nav-keyboard.md](references/nav-keyboard.md) | 中       | 使用遥控器的搜索和文本输入 |

### 设计

| 文件               | 影响     | 描述             |
|--------------------|----------|------------------|
| [design-10foot.md](references/design-10foot.md) | 高       | 10 英尺审查启发式 |
| [design-typography.md](references/design-typography.md) | 高       | TV 字体大小和可读性 |
| [design-layout.md](references/design-layout.md) | 高       | 安全区域、间距、轮播和焦点空间 |
| [design-color.md](references/design-color.md) | 中       | 对比度和 TV 显示颜色限制 |

### 性能

| 文件               | 影响     | 描述             |
|--------------------|----------|------------------|
| [perf-overview.md](references/perf-overview.md) | 高       | TV 性能目标和分析顺序 |
| [perf-lists.md](references/perf-lists.md) | 关键     | 虚拟化行和海报密集型列表 |
| [perf-animations.md](references/perf-animations.md) | 关键     | 焦点和过渡动画性能 |
| [perf-memory.md](references/perf-memory.md) | 高       | 低内存 TV崩溃和图像/视频压力 |
| [perf-network.md](references/perf-network.md) | 高       | 遥控器输入、请求停滞和网络弹性 |

### 视频、可访问性、设置、测试

| 文件               | 影响     | 描述             |
|--------------------|----------|------------------|
| [video-streaming.md](references/video-streaming.md) | 高       | TV 平台协议/DRM 选择 |
| [video-players.md](references/video-players.md) | 高       | 播放器选择和自定义控件 |
| [video-debugging.md](references/video-debugging.md) | 高       | 清单、DRM、编解码器和播放调试 |
| [a11y-overview.md](references/a11y-overview.md) | 中       | TV 特定可访问性差异 |
| [a11y-implementation.md](references/a11y-implementation.md) | 高       | 可访问标签、角色、实时区域和焦点 |
| [a11y-checklist.md](references/a11y-checklist.md) | 中       | 启动可访问性审计清单 |
| [setup-getting-started.md](references/setup-getting-started.md) | 中       | `react-native-tvos` 和 Expo TV 设置 |
| [setup-cross-platform.md](references/setup-cross-platform.md) | 中       | 平台检测和跨平台注意事项 |
| [setup-architecture.md](references/setup-architecture.md) | 中       | 代码共享和项目结构 |
| [test-strategy.md](references/test-strategy.md) | 中       | TV 测试范围和覆盖分割 |
| [test-javascript.md](references/test-javascript.md) | 中       | JS 级别遥控器/焦点测试辅助工具 |
| [test-e2e.md](references/test-e2e.md) | 中       | Appium 和 TV E2E 覆盖 |
| [release-cicd.md](references/release-cicd.md) | 中       | CI、构建指纹和发布检查 |

## 问题 → 技能映射

| 症状               | 从这里开始                                                                   |
|--------------------| ---------------------------------------------------------------------------- |
| "焦点跳转到错误的元素" | [focus-management.md](references/focus-management.md) → 调试部分    |
| "滚动列表时应用冻结"   | [perf-lists.md](references/perf-lists.md) → 虚拟化                   |
| "Fire TV 上动画卡顿"      | [perf-animations.md](references/perf-animations.md) → 本地驱动          |
| "TV 上文字太小"               | [design-typography.md](references/design-typography.md) → 最小尺寸      |
| "视频无法播放 / DRM 错误"      | [video-streaming.md](references/video-streaming.md) → DRM 部分            |
| "屏幕阅读器跳过元素"       | [a11y-implementation.md](references/a11y-implementation.md) → 角色 & 标签 |
| "返回按钮无法正常工作"     | [nav-patterns.md](references/nav-patterns.md) → 返回导航              |
| "键盘遮挡内容"            | [nav-keyboard.md](references/nav-keyboard.md) → 内置 vs 自定义           |
| "应用启动时间过长"         | [perf-overview.md](references/perf-overview.md) → 启动时间               |
| "图像导致内存崩溃"      | [perf-memory.md](references/perf-memory.md) → 图像优化             |
| "CI 管道耗时过长"            | [release-cicd.md](references/release-cicd.md) → 指纹                |
| "如何跨平台共享代码" | [setup-architecture.md](references/setup-architecture.md) → 代码共享     |

## 安全 (TV 特定)

任何 RN 应用中都适用的通用依赖项/输入卫生；值得强调的 TV 特定差异：

- 永远不要在客户端代码中嵌入 FairPlay/Widevine/PlayReady 密钥 — 将许可证服务器视为信任边界，并保持 DRM 令牌服务器颁发。
