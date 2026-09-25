# Vega 多平台迁移

## 概述

将 Vega OS（Fire TV）应用迁移到跨平台的 React Native 单一仓库，实现 Android TV、Apple TV 和 Vega OS 之间 70-85% 的代码复用。

## 适用场景

当用户提到以下情况时使用此技能：
- 将 Vega/Fire TV 应用迁移到其他平台
- 开发跨平台电视应用
- 将单平台电视应用转换为单一仓库
- 添加 Android TV 或 Apple TV 支持
- 在电视平台之间共享代码
- 为电视应用设置 Yarn 工作区

## 阶段优先级指南

| 优先级 | 阶段 | 影响 | 使用场景 |
|--------|------|------|----------|
| 1 | 分析 | 关键 | 开始迁移，没有现有分析 |
| 2 | 实施 | 关键 | 已有分析，需要单一仓库结构 |
| 3 | 平台支持 | 高 | 已有可工作的 Vega 单一仓库，添加平台 |
| 4 | 配置 | 中 | 解决构建/解析问题 |

## 快速决策树

```
用户是否有现有的 Vega 应用？
├─ 是 → 他们是否有迁移分析？
│  ├─ 否 → 开始阶段 1（分析）
│  └─ 是 → 单一仓库是否设置？
│     ├─ 否 → 开始阶段 2（实施）
│     └─ 是 → 开始阶段 3（平台支持）
└─ 否 → 从零开始？
   └─ 是 → 跳过阶段 1，使用新项目开始阶段 2
```

## 快速参考

### 关键：项目结构
```bash
# 验证单一仓库结构是否存在
ls -la packages/shared packages/vega packages/expotv

# 检查 Yarn 工作区是否配置
grep -A5 "workspaces:" package.json
```

### 关键：依赖分类
分析时的常见模式：
- **共享**：业务逻辑、UI 组件、工具、状态管理
- **平台特定**：导航、视频播放器、DRM、原生模块
- **VMRP 兼容**：标准 RN 库，映射到 Vega 对应组件

### 高：VMRP 配置
快速检查 VMRP 是否工作：
```bash
# 应该看到 @vega-tv/react-native-module-resolver-preset
grep "vmrp" packages/vega/babel.config.js
```

## 参考文献

### 阶段 1：分析（analysis-*）

| 文件 | 影响 | 描述 |
|------|------|------|
| [PHASE1_ANALYSIS.md](references/PHASE1_ANALYSIS.md) | 关键 | 代码库分析、依赖分类、迁移规划 |

**使用场景**：开始迁移，没有现有分析文档

### 阶段 2：实施（impl-*）

| 文件 | 影响 | 描述 |
|------|------|------|
| [PHASE2_IMPLEMENTATION.md](references/PHASE2_IMPLEMENTATION.md) | 关键 | 单一仓库脚手架、代码迁移、使用模板引用的 VMRP 设置 |

**使用场景**：已有分析，准备构建单一仓库结构

### 阶段 3：平台支持（platform-*）

| 文件 | 影响 | 描述 |
|------|------|------|
| [PHASE3_PLATFORM_SUPPORT.md](references/PHASE3_PLATFORM_SUPPORT.md) | 高 | Android TV 和 Apple TV 实现 |

**使用场景**：已有可工作的 Vega 单一仓库，添加新平台

### 模板
所有配置模板位于 [assets/templates/](assets/templates/)，并配有 `.md` 文档：
- `root-package.json` - Yarn 工作区设置
- `root-tsconfig.json` - TypeScript 项目引用
- `yarnrc.yml` - 依赖去重（关键）
- `shared-package.json` + `.md` - 共享包配置及规则
- `vega-metro.config.js` - Vega Metro 单一仓库解析
- `expotv-package.json` + `.md` - Expo TV 包配置
- `expotv-app.json` + `.md` - 带插件的 Expo TV 配置
- `expotv-metro.config.js` - 带电视扩展的 Expo Metro

## 问题 → 技能映射

| 问题 | 从此开始 |
|------|---------|
| 需要分析现有 Vega 应用 | PHASE1_ANALYSIS.md |
| 已有分析，需要单一仓库设置 | PHASE2_IMPLEMENTATION.md → 模板 |
| 单一仓库存在，添加 Android TV | PHASE3_PLATFORM_SUPPORT.md |
| Metro 解析错误 | PHASE2_IMPLEMENTATION.md → Metro 配置 |
| 重复的 React 版本 | PHASE2_IMPLEMENTATION.md → .yarnrc.yml |
| VMRP 未映射导入 | PHASE2_IMPLEMENTATION.md → VMRP 部分 |
| TypeScript 路径错误 | PHASE2_IMPLEMENTATION.md → TypeScript 配置 |
| 原生模块集成 | PHASE3_PLATFORM_SUPPORT.md → 原生模块 |
| 构建配置问题 | PHASE2_IMPLEMENTATION.md → 配置文件 |
| 从零开始 | PHASE2_IMPLEMENTATION.md（跳过阶段 1） |

## 工作流程

1. 使用上述决策树确定起始阶段
2. 加载该阶段的适当参考文件
3. 在每个参考文件中遵循快速启动 → 深入探索的模式
4. 在进入下一阶段前验证每个阶段的检查点
5. 使用 [VALIDATION_CHECKLIST.md](assets/templates/VALIDATION_CHECKLIST.md) 进行全面验证

## 归因

基于 Vega OS 多平台迁移模式和 React Native 单一仓库最佳实践。
