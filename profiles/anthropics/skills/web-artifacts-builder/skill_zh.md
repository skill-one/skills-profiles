# Web 产物构建器

要构建强大的前端 claude.ai 产物，请遵循以下步骤：
1. 使用 `scripts/init-artifact.sh` 初始化前端仓库
2. 通过编辑生成的代码来开发你的产物
3. 使用 `scripts/bundle-artifact.sh` 将所有代码打包为单个 HTML 文件
4. 向用户展示产物
5. （可选）测试产物

**技术栈**：React 18 + TypeScript + Vite + Parcel（打包）+ Tailwind CSS + shadcn/ui

## 设计与样式指南

非常重要：为避免通常所说的“AI 垃圾”，避免使用过多的居中布局、紫色渐变、统一圆角以及 Inter 字体。

## 快速开始

### 步骤 1：初始化项目

运行初始化脚本以创建新的 React 项目：
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

这将创建一个完全配置的project，包含：
- ✅ React + TypeScript（通过 Vite）
- ✅ Tailwind CSS 3.4.1 及 shadcn/ui 主题系统
- ✅ 已配置的路径别名（`@/`）
- ✅ 预安装了 40+ 个 shadcn/ui 组件
- ✅ 包含所有 Radix UI 依赖
- ✅ 通过 `.parcelrc` 配置了 Parcel 打包
- ✅ 兼容 Node 18+（自动检测并固定 Vite 版本）

### 步骤 2：开发你的产物

要构建产物，请编辑生成的文件。请参阅下方 **常见开发任务** 获取指导。

### 步骤 3：打包为单个 HTML 文件

要将 React 应用打包为单个 HTML 产物：
```bash
bash scripts/bundle-artifact.sh
```

这将生成 `bundle.html` - 一个自包含的产物，所有 JavaScript、CSS 和依赖项均已内联。该文件可直接在 Claude 对话中作为产物共享。

**要求**：你的项目必须在根目录下包含 `index.html`。

**脚本功能**：
- 安装打包依赖（parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline）
- 创建包含路径别名支持的 `.parcelrc` 配置
- 使用 Parcel 构建（不包含源码映射）
- 使用 html-inline 将所有资源内联为单个 HTML 文件

### 步骤 4：与用户分享产物

最后，在与用户的对话中分享打包后的 HTML 文件，以便用户将其作为产物查看。

### 步骤 5：测试/可视化产物（可选）

注意：此步骤完全可选。仅在必要时或经请求时执行。

要测试/可视化产物，可使用可用工具（包括其他 Skills 或 Playwright、Puppeteer 等内置工具）。通常，避免在展示产物前提前测试，因为这样会增加请求与最终产物可见之间的延迟。如经请求或出现问题时，请在展示产物后进行测试。

## 参考资料

- **shadcn/ui 组件**：https://ui.shadcn.com/docs/components
