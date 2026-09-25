# 搜索 AEM 文档

## 概述

此技能可帮助您高效地搜索完整的 aem.live 文档（包括文档和博客文章），避免在无关页面上浪费时间。使用提供的搜索脚本查找相关的文档页面，然后获取并阅读最相关结果的完整内容。

## 何时使用此技能

在以下情况下使用此技能：
- 您需要有关 aem.live 功能或概念的信息
- 您已经查看了项目代码库以获取上下文
- 您尝试了基本的网络搜索，但没有找到相关的 aem.live 文档
- 您需要有关实现 aem.live 功能的技术指导
- 您正在寻找官方文档中的最佳实践或示例

**不使用此技能的情况：**
- 您需要可重用的代码片段或块示例（请使用 `block-collection-and-party`）
- 您已经知道特定的文档 URL
- 您正在寻找一般性的网络开发信息（非 aem.live 特定）

## 如何使用此技能

### 第 1 步：确定关键词

确定 1-3 个与您要搜索内容相关的具体关键词。具体优于笼统。

**好的关键词：**
- "块装饰"
- "元数据"
- "通用编辑器"
- "侧边栏插件"

**差的关键词：**
- "aem"（过于笼统，被过滤为停用词）
- "如何构建网站"（过于宽泛）
- "the"（停用词）

### 第 2 步：运行搜索脚本

从项目根目录执行搜索脚本：

```bash
node .claude/skills/docs-search/scripts/search.js [--all] <keyword1> [keyword2] [...]
```

**选项：**
- `--all`：返回所有匹配结果（默认：限制为 10 个最相关的结果）
- 不带 `--all`：返回前 10 个结果

**示例：**
```bash
# 搜索块装饰信息
node .claude/skills/docs-search/scripts/search.js block decoration

# 搜索元数据并返回所有结果
node .claude/skills/docs-search/scripts/search.js --all metadata

# 多词搜索
node .claude/skills/docs-search/scripts/search.js universal editor blocks
```

### 第 3 步：查看搜索结果

脚本返回具有以下结构的 JSON：

```json
[
  {
    "path": "/developer/markup-sections-blocks",
    "title": "Markup, Sections, Blocks, and Auto Blocking",
    "description": "To design websites and create functionality, developers use the markup and DOM...",
    "snippet": "Markup, Sections, Blocks, and Auto Blocking\n\nTo design websites...",
    "type": "doc",
    "deprecation": null,
    "relevanceScore": 141
  }
]
```

**字段说明：**
- `path`：文档页面的 URL 路径
- `title`：页面标题
- `description`：简要摘要（通常约 150 个字符）- **用于快速获取上下文**
- `snippet`：页面内容中的相关摘录，显示关键词上下文
- `type`："doc" 或 "blog"
- `deprecation`：如果功能已弃用，则显示警告消息（或为 null）
- `relevanceScore`：相关性分数（越高 = 越相关）

**重要说明：**
- 结果按相关性排序（从高到低）
- 已弃用的页面相关性分数降低但仍会出现在结果中
- `description` 字段提供了页面的最佳快速摘要
- `snippet` 显示关键词上下文，但可能不完整

### 第 4 步：获取并阅读完整文档

搜索结果为您提供概览。要获取详细信息，您必须获取并阅读完整页面的内容。

**目标 URL 格式：**
```
https://www.aem.live{path}
```

**获取方法：** 使用您可用的任何方法获取完整的 HTML/文本内容：
- 专用网络抓取工具
- 终端命令（curl、wget 等）
- 网页浏览/抓取功能

**最佳实践：** 先阅读前 2-3 个最相关的结果，完整阅读它们，然后决定是否需要更多。您还可以遵循文档中引用的链接或根据您学到的知识进行额外搜索。

### 第 5 步：提醒用户有关弃用情况

如果任何结果具有包含内容的 `deprecation` 字段，**请告知用户**该功能已弃用，并包含弃用消息。建议他们查看排名更高（非弃用）的替代方案。

## 搜索内容

搜索脚本首先搜索文档（150+ 页）。如果文档结果少于 5 个，则仅搜索博客文章。如果您需要包括博客的全面覆盖，请使用 `--all` 标志。

## 示例

### 示例 1：查找块文档

**用户请求：** "如何在 aem.live 中装饰块？"

**良好方法：**
1. 搜索：`node .claude/skills/docs-search/scripts/search.js block decoration`
2. 查看前 3 个结果
3. 获取最相关页面：`https://www.aem.live/developer/markup-sections-blocks`
4. 阅读完整内容并提供答案

**不良方法：**
- 使用通用网络搜索（浪费时间在无关结果上）
- 不使用搜索脚本（可能错过最佳文档页面）

### 示例 2：学习元数据

**用户请求：** "我需要给我的页面添加元数据"

**良好方法：**
1. 搜索：`node .claude/skills/docs-search/scripts/search.js metadata`
2. 注意前一个结果是 "/docs/bulk-metadata"（分数：63）
3. 还看到 "/docs/metadata"（分数：30）
4. 获取并阅读两者以了解页面级与批量元数据
5. 提供包含两种方法的全面答案

**不良方法：**
- 仅阅读第一个结果并错过批量元数据选项
- 使用 `--all` 时需要全面覆盖但没有使用

### 示例 3：弃用功能警告

**用户请求：** "如何使用文件夹映射？"

**搜索结果：**
```json
[
  {
    "path": "/developer/authoring-path-mapping",
    "title": "Path mapping for AEM authoring",
    "relevanceScore": 51,
    "deprecation": null
  },
  {
    "path": "/developer/folder-mapping",
    "title": "Folder Mapping",
    "relevanceScore": 34.5,
    "deprecation": "Please contact us if you have a use case for folder mapping..."
  }
]
```

**良好响应：**
"我找到了有关文件夹映射的信息，但**此功能已弃用**。弃用消息说：'如果您有文件夹映射的用例，请联系我们...'。当前推荐的方法是**Path mapping for AEM authoring**（前一个结果）。让我为您阅读该文档内容。"

**不良响应：**
- 忽略弃用警告并实现已弃用的功能
- 不提及更好的替代方案

## 相关技能

- **block-collection-and-party**：当您需要可重用的代码示例或块实现时使用
- **building-blocks**：当您从零开始创建块时使用
- **content-modeling**：当您设计块的内容模型时使用

## 重要提醒

1. **始终检查弃用警告**并提醒用户
2. **获取并阅读完整页面** - 搜索结果仅用于找到正确的页面
3. **先从前 2-3 个结果开始**再扩展搜索
4. **description 字段是您的朋友** - 它通常写得很好且简洁
5. **不要仅依赖 snippets** - 它们用于上下文，不是全面信息
