# 媒体搜索

通用路由技能，用于搜索和检索现有的图像和媒体。

## 范围

**此技能用于搜索现有媒体，而非创建新媒体。**

**当用户需要时使用此技能：**
- 在 Salesforce CMS、Data Cloud 中搜索图像
- 查找可用于其应用程序的现有视觉资产
- 从连接的来源检索媒体
- 浏览可用于其项目的图像
- 定位特定的照片或图形

**当用户不需要使用此技能时：**
- 使用 AI 生成新图像（使用图像生成工具）
- 从零开始创建图形或设计
- 编辑或修改现有图像
- 构建自定义视觉或图表

## 搜索前准备

**关键：这是一个路由技能，而非直接搜索技能。**

当用户请求查找图像时：

**你的第一个操作必须使用 ask_followup_question 工具来展示搜索来源。**

1. **使用 ask_followup_question** 来展示可用的搜索来源作为选项
2. **从工具响应中接收用户的选定内容**
3. **然后** 根据其选择调用相应的搜索工具


**不正确的示例：**
- ❌ 在用户选择来源之前调用任何工具（MCP 工具、文件读取、描述符检查等）
- ❌ "检查哪些 MCP 工具可用" — 不要通过工具调用进行探测或发现工具
- ❌ 立即调用 `search_electronic_media` 或 `search_media_cms_channels`
- ❌ 读取 MCP 工具描述符或模式以查看可用内容
- ❌ 在询问之前决定使用哪个搜索来源

**正确的示例：**
- ✅ 仅响应纯文本 — 一个编号的搜索来源列表
- ✅ 询问："您想使用哪个选项？"
- ✅ 等待用户回复其选择
- ✅ 然后（并且仅然后）调用其选择的工具

**当此技能触发时，你的第一个响应必须是纯文本消息来展示搜索来源。没有工具调用。没有例外。**


## 工作流程概述

**用户必须选择搜索来源。你不能跳过这一步。**

复制此清单并跟踪你的进度：

```
媒体搜索进度：
- [ ] 第 1 步：检查你自己的工具列表以查找可用的搜索工具（不进行工具调用 — 仅检查你的上下文中包含的内容）
- [ ] 第 2 步：将可用的选项作为编号列表仅向用户展示（纯文本，不进行工具调用）
- [ ] 第 3 步：等待用户回复其选择
- [ ] 第 4 步：执行选定的搜索方法（这是第一个工具调用）
- [ ] 第 5 步：向用户展示所有结果以供选择
- [ ] 第 6 步：将选定的图像应用于代码
```

如果你在步骤 4 之前调用了任何工具，你就没有正确地遵循此技能。

## 展示搜索来源（第一个响应）

**不要调用任何工具、读取任何 MCP 描述符或进行任何外部请求以确定可用工具。**

你的工具已经加载到你的上下文中。查看你已经可以访问的工具名称 — 这是内省，而不是工具调用。

**第 1 步：检查你自己的工具列表（不进行工具调用）**

查看上下文中已有的工具并检查这些名称：
- `search_media_cms_channels` → 如果存在，包括 **"使用关键词搜索"**
- `search_electronic_media` → 如果存在，包括 **"使用 Data 360 混合搜索"**
- 始终包括 **"其他"** 作为最后一个选项

**第 2 步：构建你的响应**

仅包括你实际拥有的工具的来源。按顺序编号。

```
我可以帮你找到那张图像。你想在哪里搜索？

[编号]. [搜索来源名称] — [简要描述]
...
[编号]. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**第 3 步：停止并等待**

展示列表后，停止。不要调用任何工具。不要继续。等待用户回复其选择。

### 示例

**两个工具都可用：**
```
我可以帮你找到那张图像。你想在哪里搜索？

1. 使用 Data 360 混合搜索 — 跨 Salesforce CMS 和连接的 DAM 进行语义搜索
2. 使用关键词 — 通过关键词和分类体系搜索 Salesforce CMS
3. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**仅 `search_media_cms_channels` 可用：**
```
我可以帮你找到那张图像。你想在哪里搜索？

1. 使用关键词 — 通过关键词和分类体系搜索 Salesforce CMS
2. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**仅 `search_electronic_media` 可用：**
```
我可以帮你找到那张图像。你想在哪里搜索？

1. 使用 Data 360 混合搜索 — 跨 Salesforce CMS 和连接的 DAM 进行语义搜索
2. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**两者都不可用：**
```
当前没有配置自动媒体搜索来源。请提供直接 URL 或资产库路径。
```

**等待用户选择** 再继续。

## 执行选定的搜索方法

**⚠️ 只有在用户明确从你的编号列表中选择了一个选项后，才到达此步骤。**

如果你还没有展示选项，请先回到 "展示搜索来源" 部分。

用户选择选项后，执行下面的相应搜索方法。

### 使用关键词搜索

**工具：** `search_media_cms_channels`

**流程：**

1. **分析查询** — 理解用户在搜索什么（主题、属性、领域）

2. **提取关键词** — 会出现在图像元数据中的具体名词
   - 使用领域特定同义词
   - 最大 10 个术语
   - 示例：
     - "豪华公寓" → 公寓、别墅、顶层公寓、住宅、公寓楼
     - "公司标志" → 标志、徽章、企业标志
     - "明亮的房间" → _(如果没有具体名词则为空)_

3. **提取分类体系** — 描述性质量、风格、情绪、类别
   - 仅形容词和属性
   - 示例：
     - "带河景的豪华公寓" → 豪华、高端、河景、滨河、全景
     - "明亮的宽敞房间" → 明亮、宽敞、开放、通风、光线充足
     - "汽车" → _(如果没有描述性术语则为空)_

4. **确定区域设置** — 使用格式 `en_US`、`es_MX`、`fr_FR`（默认：`en_US`）

5. **构建 JSON 负载** — 构建此确切结构：

```json
{
  "inputs": [{
    "searchKeyword": "keyword1 OR keyword2 OR keyword3",
    "taxonomyExpression": "{\"OR\": [\"Taxonomy1\", \"Taxonomy2\"]}",
    "searchLanguage": "en_US",
    "channelIds": "",
    "channelType": "PublicUnauthenticated",
    "contentTypeFqn": "sfdc_cms__image",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

**字段规则：**
- `searchKeyword`：使用 ` OR `（空格-OR-空格）连接关键词。如果没有关键词，使用空字符串。
- `taxonomyExpression`：将 JSON 对象 `{"OR": ["term1", "term2"]}` 字符串化。如果没有分类体系，使用 `"{}"`。
- `searchLanguage`：带下划线的区域设置（例如，`en_US`）
- `channelIds`：始终为空字符串
- `channelType`：始终为 `"PublicUnauthenticated"`
- `contentTypeFqn`：始终为 `"sfdc_cms__image"`
- `pageOffset`：从 `0` 开始，以 `searchLimit` 为步长进行分页
- `searchLimit`：默认 `5`，如果用户请求更多，则调整

**示例：**

查询："带河景的豪华公寓"
```json
{
  "inputs": [{
    "searchKeyword": "apartment OR villa OR penthouse OR residence",
    "taxonomyExpression": "{\"OR\": [\"Luxury\", \"Premium\", \"Waterfront\", \"Riverside\"]}",
    "searchLanguage": "en_US",
    "channelIds": "",
    "channelType": "PublicUnauthenticated",
    "contentTypeFqn": "sfdc_cms__image",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

查询："明亮的宽敞房间"（没有具体名词）
```json
{
  "inputs": [{
    "searchKeyword": "",
    "taxonomyExpression": "{\"OR\": [\"Bright\", \"Spacious\", \"Open\", \"Airy\"]}",
    "searchLanguage": "en_US",
    "channelIds": "",
    "channelType": "PublicUnauthenticated",
    "contentTypeFqn": "sfdc_cms__image",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

查询："汽车图像"（没有描述性术语）
```json
{
  "inputs": [{
    "searchKeyword": "car OR automobile OR vehicle OR auto",
    "taxonomyExpression": "{}",
    "searchLanguage": "en_US",
    "channelIds": "",
    "channelType": "PublicUnauthenticated",
    "contentTypeFqn": "sfdc_cms__image",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

6. **使用工具** 并传递确切的 JSON 负载

### 使用 Data 360 混合搜索

**工具：** `search_electronic_media`

**流程：**

1. 使用用户的查询 **原样** — 无需关键词提取或转换
2. 调用 `search_electronic_media`
3. 将查询传递给工具的 `searchQuery` 参数

**示例：**
- 用户查询："现代豪华公寓带自然光照"
- 工具调用：`search_electronic_media(searchQuery="modern luxury apartment with natural lighting")`

### 其他（用户提供的 URL）

询问用户提供：
- 图像的直接 URL
- 资产库路径
- 特定的系统/位置进行检查

## 展示搜索结果

**你的操作必须使用 `ask_followup_question` 工具将搜索结果作为选项展示。**
1. **解析工具响应** — 提取所有图像结果（标题和来源）
2. **使用 `ask_followup_question`** 将所有结果作为可选选项展示。仅显示图像标题 — 不要显示 URL。
3. **从工具响应中接收用户的选定内容**
4. **然后** 应用选定的图像

```
我找到了 4 张图像。你想使用哪一张？

1. 豪华公寓外观
   来源：Salesforce CMS

2. 现代高层建筑
   来源：Salesforce CMS

3. 滨河住宅
   来源：Salesforce CMS

4. 高端公寓楼
   来源：Salesforce CMS
```

**永远不要自动选择图像。** 始终等待用户选择。

## 应用选定的图像


用户选择后：

1. 确认选择，包括图像名称和 URL
2. 使用工具返回的完整 URL，包括所有查询参数。CMS 和 DAM URL 依赖于查询参数进行身份验证、调整大小和 CDN 路由 — 删除它们会破坏图像。例如，一个 URL 像这样 `https://cms.example.com/media/img.jpg?oid=00D&refid=0EM&v=2` 必须完整使用。
3. 将 URL 应用于用户的代码/组件
4. 显示更改的内容（文件路径和行号）

## 错误处理

| 错误 | 响应 |
|---|---|
| 工具不可用 | "The [source name] tool is unavailable. Would you like to try a different source?" |
| 工具返回错误 | 显示错误消息，提供使用不同术语重试或替代来源的选项 |
| 未找到结果 | "No results found. Try broader keywords, removing descriptive terms, or a different source." |
| 无效用户选择 | 重新显示选项并再次询问 |

**永远不要无声失败。** 始终通知用户并提供替代方案。

## 搜索行为注意事项

**使用关键词搜索：**
- 关键词和分类体系都存在 → 结果匹配关键词 OR（关键词 + 分类体系）
- 空关键词 → 仅通过分类体系搜索
- 空分类体系 → 仅通过关键词搜索
- 使用 `pageOffset` 进行分页（以 `searchLimit` 为步长）

**使用 Data 360 混合搜索：**
- 处理自然语言查询
- 语义相似度匹配
- 跨多个连接系统进行搜索

## 关键原则

1. **第一个响应始终是纯文本** — 无需调用任何工具即可展示搜索来源
2. **仅显示配置的来源** — 检查你自己的工具列表（内省，不是工具调用）并仅展示你拥有的工具的来源
3. **等待用户选择** — 始终不要自动选择来源或图像
4. **展示所有结果** — 让用户选择最佳匹配
5. **应用前确认** — 在修改代码前验证选择
6. **优雅处理错误** — 提供清晰的反馈和替代方案
