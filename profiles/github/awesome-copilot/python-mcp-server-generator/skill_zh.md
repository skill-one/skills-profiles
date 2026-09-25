# 生成 Python MCP 服务器

创建一个符合以下规范的完整模型上下文协议（MCP）服务器：

## 要求

1. **项目结构**：使用 uv 创建具有正确结构的 Python 项目
2. **依赖项**：使用 uv 添加 mcp[cli] 包
3. **传输类型**：选择 stdio（本地）或 streamable-http（远程）
4. **工具**：创建至少一个具有正确类型提示的有用工具
5. **错误处理**：包含全面的错误处理和验证

## 实现细节

### 项目设置
- 使用 `uv init project-name` 初始化
- 添加 MCP SDK：`uv add "mcp[cli]"`
- 创建主服务器文件（例如 `server.py`）
- 添加 Python 项目的 `.gitignore`
- 使用 `if __name__ == "__main__"` 配置直接执行

### 服务器配置
- 使用 `mcp.server.fastmcp` 中的 `FastMCP` 类
- 设置服务器名称和可选说明
- 选择传输方式：stdio（默认）或 streamable-http
- 对于 HTTP：可选配置主机、端口和无状态模式

### 工具实现
- 在函数上使用 `@mcp.tool()` 装饰器
- 始终包含类型提示——它们会自动生成模式
- 编写清晰的 docstrings——它们将成为工具描述
- 使用 Pydantic 模型或 TypedDicts 进行结构化输出
- 支持异步操作以处理 I/O 密集型任务
- 包含适当的错误处理

### 资源/提示设置（可选）
- 使用 `@mcp.resource()` 装饰器添加资源
- 使用 URI 模板进行动态资源：`"resource://{param}"`
- 使用 `@mcp.prompt()` 装饰器添加提示
- 从提示返回字符串或消息列表

### 代码质量
- 为所有函数参数和返回值使用类型提示
- 为工具、资源和提示编写 docstrings
- 遵循 PEP 8 风格指南
- 使用 async/await 进行异步操作
- 实现上下文管理器以进行资源清理
- 为复杂逻辑添加内联注释

## 值得考虑的工具类型
- 数据处理和转换
- 文件系统操作（读取、分析、搜索）
- 外部 API 集成
- 数据库查询
- 文本分析或生成（带采样）
- 系统信息检索
- 数学或科学计算

## 配置选项
- **对于 stdio 服务器**：
  - 简单直接执行
  - 使用 `uv run mcp dev server.py` 进行测试
  - 安装到 Claude：`uv run mcp install server.py`
  
- **对于 HTTP 服务器**：
  - 通过环境变量配置端口
  - 无状态模式以实现可扩展性：`stateless_http=True`
  - JSON 响应模式：`json_response=True`
  - 浏览器客户端的 CORS 配置
  - 挂载到现有 ASGI 服务器（Starlette/FastAPI）

## 测试指南
- 解释如何运行服务器：
  - stdio：`python server.py` 或 `uv run server.py`
  - HTTP：`python server.py` 然后连接到 `http://localhost:PORT/mcp`
- 使用 MCP 检查器测试：`uv run mcp dev server.py`
- 安装到 Claude 桌面端：`uv run mcp install server.py`
- 包含示例工具调用
- 添加故障排除提示

## 值得考虑的附加功能
- 使用上下文进行日志记录、进度和通知
- 使用 LLM 采样为工具添加 AI 功能
- 用户输入提示以实现交互式工作流
- 共享资源（数据库、连接）的生命周期管理
- 使用 Pydantic 模型的结构化输出
- 用于 UI 显示的图标
- 使用 Image 类处理图像
- 支持完成以改善用户体验

## 最佳实践
- 在所有地方使用类型提示——它们不是可选的
- 尽可能返回结构化数据
- 将日志记录到 stderr（或使用上下文日志记录）以避免 stdout 污染
- 正确清理资源
- 早期验证输入
- 提供清晰的错误消息
- 在 LLM 集成之前独立测试工具

生成一个完整的、生产就绪的 MCP 服务器，具有类型安全、适当的错误处理和全面的文档。
