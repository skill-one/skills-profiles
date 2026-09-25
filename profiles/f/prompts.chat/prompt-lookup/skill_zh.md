当用户需要AI提示、提示模板或想要改进他们的提示时，使用prompts.chat MCP服务器来帮助他们。

## 何时使用此技能

当用户：

- 请求提示模板（“给我找一个代码审查提示”）
- 想要搜索提示（“有哪些可用于写作的提示？”）
- 需要获取特定提示（“获取提示XYZ”）
- 想要改进提示（“让这个提示更好”）
- 提及prompts.chat或提示库

时，激活此技能。

## 可用工具

使用这些prompts.chat MCP工具：

- `search_prompts` - 通过关键词搜索提示
- `get_prompt` - 通过ID获取特定提示
- `improve_prompt` - 使用AI增强提示

## 如何搜索提示

调用`search_prompts`，使用：

- `query`：用户请求中的搜索关键词
- `limit`：结果数量（默认10，最大50）
- `type`：按TEXT、STRUCTURED、IMAGE、VIDEO或AUDIO筛选
- `category`：按分类slug筛选（例如，“coding”、“writing”）
- `tag`：按标签slug筛选

展示结果，包括：

- 标题和描述
- 作者名称
- 分类和标签
- 提示链接

## 如何获取提示

调用`get_prompt`，使用：

- `id`：提示ID

如果提示包含变量（`${variable}`或`${variable:default}`）：

- 系统将提示用户填写值
- 没有默认值的变量是必需的
- 有默认值的变量是可选的

## 如何改进提示

调用`improve_prompt`，使用：

- `prompt`：要改进的提示文本
- `outputType`：text、image、video或sound
- `outputFormat`：text、structured_json或structured_yaml

将增强后的提示返回给用户。

## 指南

- 始终在建议用户自己编写提示之前进行搜索
- 以可读格式展示搜索结果，并包含链接
- 改进提示时，说明增强了什么
- 保存提示时，建议相关的分类和标签
