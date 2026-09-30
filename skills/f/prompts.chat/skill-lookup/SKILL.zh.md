---
name: skill-lookup
description: 使用MCP工具从prompts.chat注册中心搜索、检索和安装代理技能。当用户要求查找技能、浏览技能目录、为Claude安装技能或使用可重用的AI代理组件扩展Claude的功能时使用。
---

## 工作流程

1. 使用 `search_skills` 根据用户请求搜索匹配的技能
2. 以标题、描述、作者和文件列表的形式呈现结果
3. 如果用户选择了一个技能，使用 `get_skill` 获取所有文件
4. 通过将文件保存到 `.claude/skills/{slug}/` 并验证是否存在 SKILL.md 来安装
5. 确认安装并解释该技能的作用以及何时激活

## 示例

```
search_skills({"query": "代码审查", "limit": 5, "category": "编程"})
get_skill({"id": "abc123"})
```

## 可用工具

使用这些 prompts.chat MCP 工具：

- `search_skills` - 通过关键词搜索技能
- `get_skill` - 通过 ID 获取特定技能及其所有文件

## 如何搜索技能

调用 `search_skills` 时，使用：

- `query`：用户请求中的搜索关键词
- `limit`：结果数量（默认 10，最大 50）
- `category`：按分类 slug 过滤（例如，"coding"、"automation"）
- `tag`：按标签 slug 过滤

呈现结果时显示：

- 标题和描述
- 作者名称
- 文件列表（SKILL.md、参考文档、脚本）
- 分类和标签
- 技能链接

## 如何获取技能

调用 `get_skill` 时，使用：

- `id`：技能 ID

返回技能元数据和所有文件内容：

- SKILL.md（主要说明）
- 参考文档
- 辅助脚本
- 配置文件

## 如何安装技能

当用户要求安装技能时：

1. 调用 `get_skill` 获取所有文件
2. 创建目录 `.claude/skills/{slug}/`
3. 将每个文件保存到适当的位置：
   - `SKILL.md` → `.claude/skills/{slug}/SKILL.md`
   - 其他文件 → `.claude/skills/{slug}/{filename}`
4. 重新读取 `SKILL.md` 以验证 frontmatter 是否完整

## 指南

- 始终在建议用户创建自己的技能之前进行搜索
- 以可读的格式呈现搜索结果，并显示文件数量
- 安装时，确认技能已成功保存
- 解释技能的作用以及何时激活
