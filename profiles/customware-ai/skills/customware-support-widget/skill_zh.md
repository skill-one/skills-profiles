# 自定义支持小部件

当 Customware React Router 客户端专用 SPA 模板需要 Customware 支持聊天入口时，使用此技能。

该小部件是一个第三方浏览器自定义元素。在此模板中，在 `root.tsx` 或定义 HTML 文档结构的等效 React Router 根文件/组件中加载小部件脚本，并在需要显示支持的路由或布局中仅渲染 `<customware-chat>`。小部件拥有其 Shadow DOM UI、聊天运行时、服务调用、工具徽章、语音输入和页面操作行为。

有关所有 React 代码示例、脚本加载模式、JSX 类型定义、气泡/全屏模式示例、元数据和样式选项，请参阅 [references/component-usage.md](references/component-usage.md)。

## 提供的功能

- 支持 `<customware-chat>` 聊天 UI。
- `chat-bubble` 模式用于浮动启动器/对话框。
- `full` 模式用于侧边栏、轨道、抽屉或分栏聊天区域。
- 通过 `meta` DOM 属性提供可选访客元数据。
- 通过 `styleOptions` 或 `style-options` 提供可选的尺寸/自定义选项。
- 工具支持行为：读取域/上下文、列出任务、创建任务和操作可见页面。
- 用户请求的页面操作，如填写表单、选择选项、点击按钮、替换值或提交可见 UI。

## 使用场景

- 将支持聊天添加到 Customware React Router 客户端专用 SPA 模板。
- 在应用外壳中放置浮动支持启动器。
- 在布局区域中放置支持聊天作为全屏嵌入面板。
- 允许支持代理帮助用户处理可见应用 UI，例如代表用户填写表单。
- 更新现有的支持小部件位置或样式。

有关确切的 React 实现模式，请参阅 [references/component-usage.md](references/component-usage.md)。

## 不应使用场景

- 不要使用此技能进行服务器端渲染工作。目标模板是客户端专用的 React Router SPA 模式。
- 不要使用此技能构建自定义聊天 UI。
- 不要使用此技能将小部件嵌入 iframe。
- 不要使用此技能直接调用支持聊天端点。
- 不要使用此技能用于非模板 React 应用或非 React 应用，除非明确要求。
- 如果无法确定 `orgId` 或 `projectId`，则应明确说明缺少所需的 Customware 组织/项目 ID 并失败任务。

## 必须遵守的规则

- 始终渲染真实自定义元素：`<customware-chat>`。
- 始终传递 `org-id` 和 `project-id`。
- 如果任一 ID 不可用，则以明确的缺失 ID 原因失败任务，而不是渲染占位符或询问后续问题。
- 从 `root.tsx` 或模板的等效 React Router 根文档外壳中加载 `https://app.customware.ai/support-widget/customware-chat.js` 一次，除非现有的应用级加载器已经这样做。
- 不要将任务 ID、域 ID、用户 ID、API 令牌、会话令牌、认证 Cookie 或密钥传递到组件中。
- 仅将 `meta` 用于可选的访客身份：`email` 和/或 `name`。
- 使用包装 CSS、`styleOptions` 或 `style-options` 进行尺寸调整。不要使用原生 DOM `style` 属性作为小部件配置。
- 工具调用是紧凑状态徽章，而不是按钮。
- 页面操作在内部处理。不要在小部件周围添加自定义点击/填写/页面控制处理程序。
- 不要将页面操作提示或值硬编码到主机应用中。用户必须在小部件中输入请求。

## 实现工作流程

1. 阅读 [references/component-usage.md](references/component-usage.md)。
2. 确认 React 应用具有 `orgId` 和 `projectId`。
3. 选择模式：
   - `chat-bubble` 用于浮动支持启动器/对话框。
   - `full` 用于嵌入轨道、抽屉、分栏或固定聊天区域。
4. 在 `root.tsx` 或定义 HTML 文档 `<head>` 的 React Router 根文件/组件中添加脚本标签，除非它已存在。
5. 在 `.d.ts` 文件中添加 JSX 自定义元素类型定义，当模板不知道 `<customware-chat>` 时。
6. 在需要支持的具体路由或布局中渲染 `<customware-chat>` 并传递 `org-id` 和 `project-id`。
7. 通过类型化的 React 引用在需要时设置可选的 `meta` 和 `styleOptions`。
8. 对于全屏模式，确保包装/组件具有具体的高度，并且内部滚动属于小部件。
9. 对于气泡模式，确保包装没有被裁剪并且具有适当的 `z-index`。
10. 当可用时，通过代码检查和 `npm run check` 验证生成的 React 代码的语法。

有关每种模式的完整代码示例，请参阅 [references/component-usage.md](references/component-usage.md)。

## MITB 代理限制

- 不要假设可以访问 Playwright、截图、浏览器开发者工具或视觉测试。
- 不要声称小部件经过了视觉测试。
- 不要在生成的应用中编写面向用户的状态报告。
- 通过代码检查、TypeScript/编译检查，并确保生成的 React Router/Vite 代码遵循 [references/component-usage.md](references/component-usage.md) 中的示例来验证。
- 如果生成期间无法获取运行时 ID，则以明确的缺失 ID 原因失败任务。如果 ID 预期在运行时异步加载，则通过 `orgId && projectId` 隔离组件，确保它永远不会渲染占位符。

## 不应做的事情

- 不要创建 iframe 集成。
- 不要在 React 中重建或重新样式小部件内部。
- 不要深入 Shadow DOM 或依赖内部类名。
- 不要将工具调用作为可点击的 UI 控件公开。
- 不要从主机应用直接调用支持聊天 API 或页面操作 API。
- 不要添加回退嵌入模式。
- 不要在组件属性中存储密钥、访问令牌、私有负载或认证/会话数据。
- 不要将任意的用户/配置对象传递到 `meta`；仅传递可选的 `email` 和 `name`。
- 不要仅在想象的内部消息列表上设置固定高度。调整全屏模式主机区域的尺寸。
- 除非该行为是故意的，否则不要将气泡模式放置在裁剪或变换的容器内。
