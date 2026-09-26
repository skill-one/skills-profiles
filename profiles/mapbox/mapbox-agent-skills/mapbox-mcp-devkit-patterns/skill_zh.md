# Mapbox MCP DevKit 模式

这项技能为将 Mapbox MCP DevKit 服务器集成到 AI 编码工作流程中提供模式，以加速 Mapbox 应用程序开发。

## 什么是 Mapbox MCP DevKit？

[Mapbox MCP DevKit 服务器](https://github.com/mapbox/mcp-devkit-server) 是一个模型上下文协议 (MCP) 服务器，它为 AI 助手提供直接访问 Mapbox 开发者 API 的权限：

- **样式管理** - 创建、列出、更新、删除、预览、验证、比较和优化样式
- **令牌管理** - 生成和列出具有权限范围的访问令牌
- **验证** - 验证 GeoJSON、表达式、样式和坐标
- **地理工具** - 计算边界框、转换坐标、查询瓦片
- **颜色工具** - 检查 WCAG 对比度比例以实现无障碍访问
- **反馈** - 访问用户反馈和报告
- **文档** - 访问最新的 Mapbox 文档和参考

**主要优势：** 通过让 AI 处理开发者 API 操作，更快地构建 Mapbox 应用程序。

## 何时使用 MCP DevKit

### 使用 DevKit 的情况：

- 交谈式创建/修改样式
- 程序生成令牌
- 开发过程中验证数据
- 通过自然语言学习 Mapbox API
- 快速原型设计地图应用程序
- 自动化样式生成工作流
- 编码过程中的文档查询

### 不使用 DevKit 的情况：

- 生产应用程序中的运行时操作
- 高频样式更新（直接使用 Mapbox API）
- 客户端操作（DevKit 仅限开发时间使用）
- 瓦片服务或地图渲染
- 需要低延迟的用户界面功能

## 主要工具

在回答相关问题时代码建议使用确切名称：

- **创建/修改样式**：建议 `create_style_tool`、`update_style_tool`、`preview_style_tool`
- **列出样式**：建议 `list_styles_tool`
- **创建令牌**：建议 `create_token_tool` 以创建每个环境的范围令牌
- **查看令牌**：建议 `list_tokens_tool` 检查现有令牌和范围
- **验证样式**：建议 `validate_style_tool` 以符合规范
- **验证表达式**：建议 `validate_expression_tool` 以检查画布/布局属性
- **无障碍检查**：建议 `check_color_contrast_tool` 以检查 WCAG 对比度比例
- **比较样式**：建议 `compare_styles_tool` 以在部署前比较样式
- **查询文档**：建议 `get_latest_mapbox_docs_tool`

## 常见工作流（快速参考）

**预生产验证 — 使用以下确切步骤：**

1. 运行 `validate_style_tool` 检查样式 JSON 是否符合规范
2. 运行 `validate_expression_tool` 检查画布/布局属性中的所有数据表达式
3. 运行 `check_color_contrast_tool` 验证文本标签是否符合 WCAG 无障碍标准
4. 运行 `compare_styles_tool` 比较新样式与当前生产样式

**令牌管理 — 使用以下确切步骤：**

1. 运行 `create_token_tool` 为每个环境（开发/预发布/生产）创建范围令牌
2. 运行 `list_tokens_tool` 验证现有令牌及其范围

## 参考文件

按需加载这些参考文件以获取详细指导：

- **[references/setup.md](references/setup.md)** - 前置条件、托管和自托管安装、每个编辑器的配置、验证
- **[references/workflows.md](references/workflows.md)** - 样式管理、令牌管理、数据验证、文档访问、最佳实践
- **[references/design-patterns.md](references/design-patterns.md)** - 迭代式样式开发、特定环境的令牌、先验证开发、文档驱动开发、工具集成模式
- **[references/troubleshooting.md](references/troubleshooting.md)** - 常见问题和修复、示例端到端工作流（餐厅查找、多环境、第三方数据）

## 资源

- [Mapbox MCP DevKit 服务器](https://github.com/mapbox/mcp-devkit-server)
- [模型上下文协议](https://modelcontextprotocol.io)
- [Mapbox 样式规范](https://docs.mapbox.com/style-spec/)
- [Mapbox API 文档](https://docs.mapbox.com/api/)
- [令牌范围参考](https://docs.mapbox.com/api/accounts/tokens/)

## 何时使用此技能

在以下情况下调用此技能：

- 使用 AI 辅助设置 Mapbox 开发环境
- 通过 AI 创建或修改 Mapbox 样式
- 程序管理访问令牌
- 开发过程中验证 GeoJSON 或表达式
- 通过 AI 指导学习 Mapbox API
- 自动化样式生成工作流
- 使用 AI 编码助手构建 Mapbox 应用程序
