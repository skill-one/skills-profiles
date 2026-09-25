# 资产构建器

要构建强大的前端 claude.ai 资产，请按照以下步骤操作：
1. 使用 `scripts/init-artifact.sh` 初始化前端仓库
2. 通过编辑生成的代码来开发您的资产
3. 使用 `scripts/bundle-artifact.sh` 将所有代码打包成一个 HTML 文件
4. 向用户展示资产
5. （可选）测试资产

**技术栈**：React 18 + TypeScript + Vite + Parcel（打包）+ Tailwind CSS + shadcn/ui

## 设计与样式指南

非常重要：为了避免通常所说的“AI 拉圾”，请避免使用过多的居中布局、紫色渐变、统一的圆角和 Inter 字体。

## 快速入门

### 第 1 步：初始化项目

运行初始化脚本来创建一个新的 React 项目：
```bash
bash scripts/init-artifact.sh <项目名称>
cd <项目名称>
```

这会创建一个完全配置好的项目，包含：
- ✅ React + TypeScript（通过 Vite）
- ✅ Tailwind CSS 3.4.1 与 shadcn/ui 主题系统
- ✅ 路径别名（`@/`）已配置
- ✅ 预装了 40 多个 shadcn/ui 组件
- ✅ 包含所有 Radix UI 依赖项
- ✅ 通过 .parcelrc 配置了 Parcel 进行打包
- ✅ 兼容 Node 18+（自动检测并固定 Vite 版本）

### 第 2 步：开发您的资产

要构建资产，请编辑生成的文件。有关指导，请参阅下方的 **常见开发任务**。

### 第 3 步：打包为单个 HTML 文件

要将 React 应用打包为单个 HTML 资产：
```bash
bash scripts/bundle-artifact.sh
```

这会创建 `bundle.html` - 一个自包含的资产，其中包含所有 JavaScript、CSS 和依赖项。该文件可以直接在 Claude 对话中作为资产共享。

**要求**：您的项目必须在根目录中有一个 `index.html`。

**脚本的作用**：
- 安装打包依赖项（parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline）
- 创建支持路径别名的 `.parcelrc` 配置
- 使用 Parcel 构建（不生成源映射）
- 使用 html-inline 将所有资源内联到单个 HTML 中

### 第 4 步：向用户分享资产

最后，在对话中与用户分享打包的 HTML 文件，以便他们将其视为资产查看。

### 第 5 步：测试/可视化资产（可选）

注意：这是一个完全可选的步骤。仅在必要时或被要求时执行。

要测试/可视化资产，请使用可用工具（包括其他技能或内置工具如 Playwright 或 Puppeteer）。通常，避免在前期测试资产，因为这会增加请求和最终资产可见之间的延迟。如果被要求或出现问题时，在展示资产后进行测试。

## 参考

- **shadcn/ui 组件**：https://ui.shadcn.com/docs/components
