# 代理设置

设置工具栏，并在需要时将其连接到用户的编码代理。
可见的工具栏和健康的MCP服务器并不能证明浏览器反馈已到达代理。在调用设置完成之前，请验证最后一步。

## 步骤

1. **检查项目**
   - 阅读项目的说明并检测其包管理器。
   - 在安装前，查找`agentation`和现有的`<Agentation>`挂载。
   - 如果已经挂载，检查其`endpoint`和当前的MCP设置。不要因为组件存在就退出，也不要添加重复的挂载。
   - 如果缺少`agentation`，使用现有锁文件的包管理器进行安装。

2. **从请求中选择连接模式**
   - 对于MCP或实时代理反馈，使用与代理相同的HTTP服务器URL。默认的本地服务器是`http://localhost:4747`；保留现有的自定义端口或代理URL。当项目是远程时，不要假设浏览器和代理使用同一台机器。
   - 仅用于手动复制粘贴时，省略`endpoint`并说明反馈将保留在此浏览器中。不要在无声的情况下启用服务器连接。
   - 如果预期的模式不明确，在检查现有项目时问一个简短的问题。继续进行独立的设置检查。

3. **添加或更新组件**

   对于Next.js App Router项目，在子组件之后在根布局的body中渲染。对于Pages Router，在`pages/_app`中的`Component`之后渲染。保留任何现有的回调和选项。

   ```tsx
   import { Agentation } from "agentation";

   // 使用上面选择的实际服务器URL进行MCP同步：
   {process.env.NODE_ENV === "development" && (
     <Agentation endpoint="http://localhost:4747" />
   )}
   ```

   该包提供自己的客户端边界。除非项目有其他原因需要更改，否则应保留应用程序的根布局服务器渲染。

4. **在请求MCP时配置代理**
   - 使用项目的现有MCP客户端和配置约定。
   - 启动命令必须包含`server`子命令：
     `npx -y agentation-mcp server`。
   - 对于支持的代理，`npx add-mcp "npx -y agentation-mcp server"`是其中一个设置选项。对于Claude Code，使用
     `claude mcp add agentation -- npx -y agentation-mcp server`或初始化向导。
   - 将相同的自定义端口应用于服务器命令和组件endpoint。
   - 当代理配置需要时，重新启动或重新连接代理。不要在已经由工作服务器拥有的端口上创建第二个HTTP服务器。

5. **验证完整的连接**
   - 运行`npx agentation-mcp doctor`进行服务诊断。对于自定义URL，在安装版本支持时使用`doctor --http-url <url>`。
   - 打开应用程序并通过工具栏创建一个明确标识的测试注释。使用`agentation_get_all_pending`或会话范围工具读取它。
   - 检查确切的测试评论和页面，而不仅仅是非零计数或健康响应。不要理会无关的注释。
   - 如果注释为空，检查组件endpoint、浏览器网络故障/CORS，以及代理和浏览器是否指向同一服务器。
   - 如果浏览器或MCP工具不可用，说明哪些部分仍然未验证，并给用户这个最后的检查。不要声称实时同步工作。

## 注意事项

- 开发守卫防止工具栏在生产环境中出现。
- Agentation需要React 18或更新版本。
- 安装工具栏不会安装、配置或连接MCP服务器。
- 支持手动复制模式，不需要运行的服务器。
