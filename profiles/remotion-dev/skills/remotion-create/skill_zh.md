这是用于创建新的 Remotion 项目与合成的说明。
如果这不是接下来的任务，请参阅 Remotion Best Practices

## 搭建项目

如果已存在项目，请跳过此步骤。
确保已安装 Node.js 和 Git，且当前文件夹适合用于启动新项目。

在确定搭建位置之前，请检查当前文件夹（包括隐藏文件）。

### 空文件夹

如果该文件夹为空，或仅包含诸如 `.DS_Store` 等可丢弃的操作系统元数据，则直接在当前文件夹中创建项目。
首先仅移除这些可丢弃的元数据文件，因为 `create-video` 会拒绝非空文件夹。
不要将所有隐藏文件视为可丢弃内容：诸如 `.env` 文件和 `.git` 目录是有意义的内容。

在现有文件夹中搭建项目：

```bash
npx create-video@latest --yes --blank --no-tailwind .
npm i
```

### 非空文件夹

如果当前文件夹包含有意义的内容且尚未存在项目，则在新子文件夹中搭建项目。
请将 `my-video` 替换为一个合适的项目名称。

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npm i
```

## 设计视频

保留脚手架，并添加 React Markup。
遵循 Remotion React Markup 最佳实践及 [Video Layout Rules](video-layout.md)，以获取视频优先布局与文本尺寸的相关指导。

## 这是多场景视频吗？

如果是包含多个子序列视频的视频，请遵循 Multi-scene videos 部分的指导。

## 交互性最佳实践

通过遵循 Remotion 交互性最佳实践来构建 React Markup，您可以允许用户在 Studio 中进行编辑，并将这些修改写回代码。

## TailwindCSS

如果需要 Tailwind，请参阅 [tailwind.md](tailwind.md) 了解如何在 Remotion 中使用 TailwindCSS。

## 打开预览

在构建完合成后，启动预览服务器：

```bash
npx remotion studio --no-open
```

这将启动一个长时间运行的进程，并打印预览服务器的 URL。
如果服务器已启动，它将打印 URL。
如果可用内置浏览器，请在其中打开。
您可以通过导航至 `/[composition-id]`（例如 `http://localhost:3000/MapAnimation`）来访问特定的合成。

## 渲染视频

仅在用户明确要求时进行渲染。

```
npx remotion render
```

有关更多选项，请参阅 Rendering。

## 后续步骤

视频创建过程已完成。
如需后续提示，请使用 Remotion Best Practices。
