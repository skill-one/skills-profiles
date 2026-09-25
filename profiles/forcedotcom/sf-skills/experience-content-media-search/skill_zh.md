# 媒体搜索

通用路由技能，用于搜索和检索现有的图像和媒体。

## 范围

**此技能用于搜索现有媒体，而非创建新媒体。**

**当用户需要时使用此技能：**
- 在 Salesforce CMS、Data Cloud 中搜索图像
- 查找可用于其应用的现有视觉资产
- 从连接的源中检索媒体
- 浏览可用于其项目的图像
- 定位特定照片或图形

**当用户不需要使用此技能时：**
- 使用 AI 生成新图像（使用图像生成工具）
- 从零开始创建图形或设计
- 编辑或修改现有图像
- 构建自定义视觉或图表
- 搜索版权免费图像（使用 `experience-content-media-stock-image-search`）

## 搜索前准备

**关键：这是一个路由技能，而非直接搜索技能。**

当用户请求查找图像时：

**你的第一个操作必须使用 `ask_followup_question` 工具来展示搜索源。**

1. **使用 `ask_followup_question`** 来展示可用的搜索源作为选项
2. **接收用户的选择** 来自工具响应
3. **然后** 根据其选择调用相应的搜索工具


**不正确的示例：**
- 在用户选择源之前调用任何工具（MCP 工具、文件读取、描述符检查等）
- "检查哪些 MCP 工具可用" — 不要通过工具调用进行探测或发现工具
- 立即调用 `search_electronic_media` 或 `search_media_cms_channels`
- 读取 MCP 工具描述符或模式以查看可用内容
- 在询问之前决定使用哪个搜索源

**正确的示例：**
- 仅响应纯文本 — 一个搜索源的编号列表
- 询问："您想使用哪个选项？"
- 等待用户回复其选择
- 然后调用（并且仅调用）他们选择的工具

**当此技能触发时，你的第一个响应必须是纯文本消息来展示搜索源。没有工具调用。没有例外。**


## 工作流程概述

**用户必须选择搜索源。你不能跳过这一步。**

复制此清单并跟踪你的进度：

```text
媒体搜索进度：
- [ ] 第 1 步：检查你自己的工具列表以查找可用的搜索工具（不进行工具调用 — 仅检查你的上下文中包含的内容）
- [ ] 第 2 步：将可用的选项作为编号列表仅展示给用户（纯文本，不进行工具调用）
- [ ] 第 3 步：等待用户回复其选择
- [ ] 第 4 步：执行选定的搜索方法（这是第一个工具调用）
- [ ] 第 5 步：向用户展示所有结果以供选择
- [ ] 第 6 步：将选定的图像应用于代码
```

如果你在步骤 4 之前调用任何工具，你没有正确遵循此技能。

## 展示搜索源（第一个响应）

**不要调用任何工具、读取任何 MCP 描述符或进行任何外部请求以确定可用工具。**

你的工具已经加载到你的上下文中。查看你已经可以访问的工具名称 — 这是内省，而不是工具调用。

**第 1 步：检查你自己的工具列表（不进行工具调用）**

查看上下文中已有的工具并检查这些名称：
- `search_media_cms_channels` → 如果存在，包括 **"使用关键词搜索"**
- `search_electronic_media` → 如果存在，包括 **"使用 Data 360 混合搜索"**
- 总是包括 **"其他"** 作为最后一个选项

**第 2 步：构建你的响应**

仅包括你实际拥有的工具的来源。按顺序编号。

```text
我可以帮你找到这张图像。你想在哪里搜索？

[编号]. [搜索源名称] — 简要描述
...
[编号]. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**第 3 步：停止并等待**

展示列表后，停止。不要调用任何工具。不要继续。等待用户回复其选择。

### 示例

**两个工具都可用：**
```text
我可以帮你找到这张图像。你想在哪里搜索？

1. 使用 Data 360 混合搜索 — 跨 Salesforce CMS 和连接的 DAM 进行语义搜索
2. 使用关键词搜索 — 通过关键词和分类体系搜索 Salesforce CMS
3. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**仅 `search_media_cms_channels` 可用：**
```text
我可以帮你找到这张图像。你想在哪里搜索？

1. 使用关键词搜索 — 通过关键词和分类体系搜索 Salesforce CMS
2. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**仅 `search_electronic_media` 可用：**
```text
我可以帮你找到这张图像。你想在哪里搜索？

1. 使用 Data 360 混合搜索 — 跨 Salesforce CMS 和连接的 DAM 进行语义搜索
2. 其他 — 提供你自己的 URL 或路径

你想使用哪个选项？
```

**两个工具都不可用：**
```text
当前没有配置自动媒体搜索源。请提供直接 URL 或资产库路径。
```

**等待用户选择** 再继续。

## 执行选定的搜索方法

**只有在用户明确从你的编号列表中选择了一个选项后，你才到达这一步。**

如果你还没有展示选项，请先回到 "展示搜索源" 部分。

用户选择选项后，执行下方的相应搜索方法。

### 使用关键词搜索

**工具：** `search_media_cms_channels`

**流程：**

1. **分析查询** — 理解用户在搜索什么（主题、属性、领域）

2. **提取关键词** — 会出现在图像元数据中的具体名词
   - 使用领域特定同义词
   - 最大 10 个术语
   - 示例：
     - "豪华公寓" → 公寓、别墅、顶层公寓、住宅、联排别墅
     - "公司标志" → 标志、徽章、企业标志
     - "明亮的房间" → _(如果没有具体名词则为空)_

3. **提取分类体系** — 描述性质量、风格、情绪、类别
   - 仅使用形容词和属性
   - 示例：
     - "带河景的豪华公寓" → 豪华、高端、河景、滨河、全景
     - "明亮的宽敞房间" → 明亮、宽敞、开放、通风、光线充足
     - "汽车" → _(如果没有描述性术语则为空)_

4. **确定区域设置** — 使用格式 `en_US`、`es_MX`、`fr_FR`（默认：`en_US`）

5. **构建 JSON 负载** — 构建此精确结构：

```json
{
  "inputs": [{
    "searchKeyword": "keyword1 OR keyword2 OR keyword3",
    "taxonomyExpression": "{\"OR\": [\"Taxonomy1\", \"Taxonomy2\"]}",
    "searchLanguage": "en_US",
    "contentAccessScope": "Public",
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
- `contentAccessScope`：始终为 `"Public"`（涵盖公共-未认证和公共 Experience Cloud 站点通道）
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
    "contentAccessScope": "Public",
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
    "contentAccessScope": "Public",
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
    "contentAccessScope": "Public",
    "contentTypeFqn": "sfdc_cms__image",
    "pageOffset": 0,
    "searchLimit": 5
  }]
}
```

6. **调用工具** 并使用精确的 JSON 负载 — 在调用工具前在你的响应中展示负载

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
- 检查的特定系统/位置

## 展示搜索结果

**你的操作必须使用 `ask_followup_question` 工具将搜索结果作为选项展示。**
1. **解析工具响应** — 提取所有图像结果（标题和来源）
2. **使用 `ask_followup_question`** 将所有结果作为可选选项展示。仅显示图像标题 — 不要显示 URL。
3. **接收用户的选
