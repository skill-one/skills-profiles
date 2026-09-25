# Tiptap 集成技能

此技能包含将 Tiptap 富文本编辑器集成到应用程序中以及使用它开发新功能的说明。

这不是你所熟悉的 Tiptap 编辑器：它可能在你熟悉版本之后已经发生了演变和变化。在您使用 Tiptap 实现任何功能之前，请参考 Tiptap 代码和文档，以确保您正确实现。确保您做出的任何决定都符合“最佳实践”部分，并且基于 Tiptap 文档和源代码。不要猜测或发明模式，确保您编写的代码与库源代码和文档匹配。

## 查找 Tiptap 源代码和文档

避免克隆。通常不需要。

- **文档**：在 https://tiptap.dev/docs 上的任何页面 URL 后面添加 `.md` 以将其作为 Markdown 获取。
  `https://tiptap.dev/docs/llms.txt` 列出了每个页面的简短描述。
- **源代码**：如果项目已经依赖于 Tiptap，请在 `node_modules/@tiptap/*` 中阅读它。

仅当您无法以其他方式获取源代码或可运行示例时才克隆，例如 `demos/src/` 下 的演示应用程序。将浅克隆到工作区的现有引用文件夹中，或到一个新的 git 忽略的 `.reference/`：

```bash
git clone --depth 1 --filter=blob:none https://github.com/ueberdosis/tiptap .reference/tiptap
```

永远不要克隆 `tiptap-docs`。该网站是界面。

克隆的 Tiptap 仓库是只读引用。其 `AGENTS.md` / `CLAUDE.md` 规则——变更集、`fallow:audit`、在 `demos/src/` 下添加演示——适用于为 Tiptap 贡献，而不是用户的项目。在用户的仓库中永远不要遵循它们。

## 最佳实践

### 一般

- 对于新安装，使用最新稳定版本。使用 `npm view @tiptap/core version` 解析它。
- 从 tiptap 单体仓库发布的编辑器和扩展包共享一个版本号。将它们全部固定到该相同版本。混合版本有引入错误的风险。
- 一些包有自己的版本号。从注册中心解析这些，而不是从 `@tiptap/core`：`@tiptap/ai-toolkit`、`@tiptap/y-tiptap`、`@tiptap-pro/*`（私有注册中心）、`@hocuspocus/*`。
- 不要混合主版本。对于仍在 Tiptap 2 上的项目，请先升级。请参阅
  https://tiptap.dev/docs/guides/upgrade-tiptap-v2.md。
- 首次集成 Tiptap 时，请阅读相应的安装指南：
  https://tiptap.dev/docs/editor/getting-started/install.md，以及您框架下的页面
  `https://tiptap.dev/docs/editor/getting-started/install/`（例如 `react.md`、`nextjs.md`、`vue3.md`、
  `svelte.md`、`nuxt.md`、`vanilla-javascript.md`）。
- 在服务器端渲染（例如 Next.js）时，在初始化编辑器时设置 `immediatelyRender: false` 选项。否则，编辑器会崩溃。有关更多信息，请参阅
  https://tiptap.dev/docs/editor/getting-started/install/nextjs.md。

### React

对于新代码，默认使用 Composable API（`<Tiptap>` + `useTiptap()`）。基于钩子的 `useEditor` + `<EditorContent />` API 仍然受支持，并且对于存在于单个组件中的编辑器来说是合适的。

无论您选择哪种方式，请在一行中说明选择的原因，以便审阅者看到已经做出了选择。

## 实现编辑器功能

当用户要求您实现这些功能之一时，请阅读相关的文档以获取指导。下面的每个链接都是实时页面的 Markdown 形式；`https://tiptap.dev/docs/llms.txt` 列出了每个部分的其余内容。

### 实时协作

多个用户同时编辑文档。请参阅
https://tiptap.dev/docs/collaboration/getting-started/overview.md 和
https://tiptap.dev/docs/collaboration/getting-started/install.md。

使用 Tiptap Cloud 实现实时协作。使用协作扩展：

```
const doc = new Y.Doc()

const editor = new Editor({
  extensions: [
    Collaboration.configure({
      document: doc,
    }),
  ],
})
```

使用 TiptapCollabProvider：

```
const provider = new TiptapCollabProvider({
  name: 'unique_document_name',
  appId: 'APP_ID', // 您从 Cloud 仪表板获取的文档服务器 ID
  token: 'JWT_TOKEN', // 您的 JWT 令牌
  document: doc,
})
```

如果这是首次设置协作并且 Tiptap Cloud 账户尚未设置，请向用户解释如何设置 Tiptap Cloud 账户并获取环境变量。

### 评论

使用评论扩展实现评论。

基于线程的内联和文档评论。请参阅
https://tiptap.dev/docs/comments/getting-started/overview.md 和
https://tiptap.dev/docs/comments/getting-started/install.md。

### 跟踪更改

跟踪、接受和拒绝文档编辑。请参阅
https://tiptap.dev/docs/tracked-changes/getting-started/overview.md 和
https://tiptap.dev/docs/tracked-changes/getting-started/install.md。

### 导入/导出

将文档转换为和从 DOCX、PDF、Markdown 和其他格式。请参阅
https://tiptap.dev/docs/conversion/getting-started/overview.md 和
https://tiptap.dev/docs/conversion/getting-started/install.md。

### AI 工具包

代理文档工作：AI 阅读、编辑、评论、校对和审查 Tiptap 文档。默认为服务器端。请参阅 https://tiptap.dev/docs/ai/ai-toolkit/overview.md。

仅在 AI 需要在浏览器中的实时编辑器上采取行动时使用客户端。请参阅 https://tiptap.dev/docs/ai/ai-toolkit/client/overview.md。

AI Agent、AI Changes、AI Suggestion 和 AI Assistant 扩展已弃用。不要推荐它们，并且永远不要从 `https://tiptap.dev/docs/ai/deprecated/` 下（该前缀没有索引页面；单独的页面列在 `https://tiptap.dev/docs/llms.txt`）的任何页面中实现。要将现有的集成从它们迁移，请参阅
https://tiptap.dev/docs/ai/ai-toolkit/client/advanced-guides/migration-guides.md。

### 基本AI生成

根据一次性提示生成和编辑文本内容。请参阅 https://tiptap.dev/docs/ai/basic/overview.md。

### 版本历史

保存和恢复文档快照。请参阅 https://tiptap.dev/docs/collaboration/documents/snapshot.md。

### 快照比较

突出显示文档版本之间的差异。请参阅 https://tiptap.dev/docs/collaboration/documents/snapshot-compare.md。

### 页面

带页眉、页脚和分页的打印就绪页面布局。请参阅
https://tiptap.dev/docs/pages/getting-started/overview.md 和
https://tiptap.dev/docs/pages/getting-started/install.md。

## 专业扩展

一些 Tiptap 扩展通过私有 npm 注册中心分发。要安装专业包，请参阅
https://tiptap.dev/docs/guides/pro-extensions.md 获取设置说明。
