以下是创建新的 Remotion 项目和组成的说明。  
如果这不是下一个任务，请参阅 Remotion 最佳实践

## 创建项目框架

如果项目已存在，请跳过此步骤。  
确保已安装 Node.js 和 Git，并且当前文件夹适合开始新项目。

在选择在哪里创建项目之前，检查当前文件夹，包括隐藏文件。  

### 空文件夹

如果文件夹为空，或仅包含可丢弃的操作系统元数据（例如 `.DS_Store`），则直接在当前文件夹中创建项目。  
首先删除这些可丢弃的元数据文件，因为 `create-video` 会拒绝非空文件夹。  
不要将所有隐藏文件都视为可丢弃的：`.env` 等文件和 `.git` 等目录是有效内容。  

在现有文件夹中创建框架：

```bash
npx create-video@latest --yes --blank --no-tailwind .
npm i
```

### 非空文件夹

如果当前文件夹包含有效内容且没有已存在的项目，请将框架创建到新的子文件夹中。  
将 `my-video` 替换为合适的项目名称。

```bash
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npm i
```

## 设计视频

保留框架并添加 React 标记。  
遵循 Remotion React 标记最佳实践和 [视频布局规则](video-layout.md) 以获得视频优先布局和文本尺寸指导。

## 这是否是多场景视频？

如果这是一个包含多个子序列视频的视频，请遵循多场景视频的指导。

## 交互性最佳实践

通过遵循 Remotion 交互性最佳实践来构建 React 标记，您允许用户在 Studio 中进行编辑，并将更改写回代码。

## TailwindCSS

如果需要使用 Tailwind，请参阅 [tailwind.md](tailwind.md) 以在 Remotion 中使用 TailwindCSS。

## 打开预览

构建组成后启动预览服务器：

```bash
npx remotion studio --no-open
```

这将启动一个长时间运行的过程，并打印预览的服务器 URL。  
如果服务器已启动，它将打印 URL。  
如果可用，可以在集成浏览器中打开它。  
您可以通过导航到 `/[composition-id]` 访问特定的组成，例如 `http://localhost:3000/MapAnimation`。

## 渲染视频

只有当用户明确要求时才渲染。

```
npx remotion render
```

更多选项，请参阅渲染。

## 后续步骤

视频创建过程已完成。  
后续提示，请使用 Remotion 最佳实践
