# platform-docs-get

使用此技能从**公开网络上的 Salesforce 官方文档**中检索并获取答案。

此技能为难以获取的 Salesforce 文档提供了一个**可靠的在线检索方案**，特别是 `help.salesforce.com`、JS 重的 `developer.salesforce.com`、`lightningdesignsystem.com` 上的 Lightning Design System 文档，以及其他官方 Salesforce 拥有的文档页面，如 `architect.salesforce.com` 和 `admin.salesforce.com`。

可选的提取脚本位于 `scripts/` 目录下 — 请参阅下方的参考文件索引。

## 范围

| | |
|---|---|
| **范围内** | 官方 Salesforce 文档检索：Apex、API、LWC、元数据、Agentforce、设置文章、SLDS、架构师/管理员指南 |
| **超出范围** | 第三方博客、PDF 降级、本地语料库索引、基准工作流、生成代码或元数据 |

## 必须输入

在检索之前，请识别：
- 正在请求的确切概念、标识符、类、方法或功能名称
- 可能的文档系列（开发者文档、帮助文章、设计系统、架构师/管理员）

使用此技能中的检索方案无需额外设置。可选的提取脚本需要 `playwright` — 请参阅 `scripts/requirements.txt`。

## 仅限官方来源

优先使用 Salesforce 拥有的文档来源：
- `developer.salesforce.com`
- `help.salesforce.com`
- `architect.salesforce.com`
- `admin.salesforce.com`
- `lightningdesignsystem.com`
- 当 Salesforce 将其用作事实来源时，其他官方 Salesforce 文档页面

除非用户明确要求，否则避免使用第三方博客、视频或摘要文章。

**不要**降级到 PDF。

## 检索工作流程

### 1. 首先对请求进行分类

在检索任何内容之前，识别可能的文档系列。

| 系列 | 典型来源 | 用于 |
|---|---|---|
| 开发者文档 | `developer.salesforce.com/docs/...` | Apex、API、LWC、元数据、Agentforce 开发者文档 |
| 帮助文档 | `help.salesforce.com/...` | 设置、管理员、产品配置 |
| 架构师/管理员文档 | `architect.salesforce.com/...`, `admin.salesforce.com/...` | 最佳实践、模式、架构良好指南、管理员启用 |
| 设计系统文档 | `lightningdesignsystem.com/...` | SLDS、Cosmos、设计令牌、组件和样式指南 |
| 旧版图谱文档 | `developer.salesforce.com/docs/atlas.en-us.*` | 更旧的官方指南和参考文档 |

### 2. 识别确切概念

在搜索之前提取真实目标：
- 确切的 API/类/方法名称
- 确切的功能名称
- 确切的产品短语
- 确切的设置概念

示例：
- `Lightning Message Service`
- `Wire Service`
- `System.StubProvider`
- `Agentforce Actions`
- `Messaging for In-App and Web allowed domains`

### 3. 优先使用目标官方检索

**不要**广泛爬取 Salesforce 文档。

相反：
1. 识别最可能的官方指南根或文章
2. 如果需要搜索，仅限制在官方 Salesforce 域名内
3. 获取该官方页面
4. 检查 **确切概念是否实际出现在该页面上**
5. 如果没有，检查并遵循最相关的 **1-3 个官方子链接**
6. 一旦获得证实证据，停止

### 4. 不要在广泛入口页停止

指南入口页**不足以**，除非它明确包含请求的确切概念。

这对于以下情况尤其重要：
- LWC 文档
- Agentforce 文档
- 广泛的平台指南主页
- 指向真实文章的帮助入口页

### 5. 对于 `developer.salesforce.com`

使用此方案：
- 从最可能的官方指南根开始
- 如果页面 JS 重量大，优先使用浏览器渲染提取
- 检查页面是否出现确切概念
- 如果概念缺失，检查官方子链接并遵循最佳匹配的 1-3 个链接
- 优先选择确切概念页面而不是广泛指南根
- 如果旧版图谱页面是概念的真实官方参考，则它们是有效的

### 6. 对于 `help.salesforce.com`

帮助页面在简单检索时经常失败。

使用此方案：
- 当可用时，优先使用确切的 `articleView?id=...` URL
- 当纯获取返回空内容时，使用浏览器渲染提取
- 将 `Loading`、`Sorry to interrupt`、`CSS Error` 或主要 Chrome/导航文本视为 **失败的提取**，而不是证据
- 寻找 **真实文章正文**，而不仅仅是标题、导航或页脚文本
- 拒绝空壳页面和软 404 页面，例如：
  - "我们到处找都找不到那个页面"
  - 通用空帮助空壳
- 如果从附近的指南或中心页面开始，请跟随链接的帮助文章，直到到达真实文章正文
- 如果在目标重试后提取仍然失败，请返回找到的最佳官方帮助 URL，并明确说明文章正文提取失败

## 接受规则

只有当满足以下至少一项时，页面才足够用于回答：
- 页面上出现确切标识符
- 页面上出现确切概念短语
- 多个查询特定短语以正确的官方上下文出现

当页面**不足以**时：
- 它只是一个广泛入口页
- 它是一个空壳页面，几乎没有真实文章文本
- 它来自错误的产品区域
- 它不包含请求的标识符或概念
- 它是第三方解释，而应该存在官方页面

## 拒绝规则

将这些作为最终证据拒绝：
- 没有确切概念的广泛指南主页
- 当期望概念/参考页面时，发布说明
- 请求开发者文档时，管理员博客文章
- 官方文档可用时，第三方博客
- 没有真实文章正文的空壳渲染页面
- 标题听起来正确但正文不包含请求概念的页面

## 确认要求

回答时包括：
1. 指南/文章标题
2. 确切官方 URL
3. 来源类型：
   - 开发者文档页面
   - 图谱参考页面
   - 帮助文章页面
4. 如果提取部分或浏览器渲染，则任何注意事项

如果证据薄弱，请明确说明。

## 示例

### 示例：Lightning Message Service
**不要**在一般 LWC 指南根停止。
找到 Lightning Message Service 的确切 LWC 页面，或从 LWC 文档中跟随最相关的子链接，直到出现确切概念。

### 示例：Wire Service
除非 `Wire Service` 实际上存在于那里，否则**不要**从 LWC 主页回答。
跟随与 wire service 或 wire adapters 相关的子文档页面。

### 示例：Agentforce Actions
**不要**从广泛的 Agentforce 入口页或博客文章回答。
找到官方 Agentforce 开发者页面，或从官方 Agentforce 文档中跟随最佳匹配的子页面。

### 示例：Messaging for In-App and Web allowed domains
优先使用官方帮助文章和浏览器渲染提取。
拒绝通用帮助空壳。如果需要，从附近的官方消息文档中跟随链接的帮助文章。

### 示例：System.StubProvider
优先选择确切标识符出现在官方 Salesforce 参考/开发者页面的页面。
如果标识符缺失，**不要**用更广泛的 Apex 入口页替代。

## 非目标

此技能**不应**：
- 维护本地文档语料库
- 依赖本地索引
- 使用 PDF 降级
- 运行基准工作流
- 依赖特定存储库脚本才能有用

## 输出预期

对于每次检索，包括：
1. 指南或文章标题
2. 确切官方 URL
3. 来源类型（开发者文档页面 / 图谱参考页面 / 帮助文章页面）
4. 如果提取部分或浏览器渲染，则任何注意事项

如果证据薄弱，请明确说明，而不是强行回答。

---

## 参考文件索引

| 文件 | 何时读取 |
|------|-------------|
| `scripts/extract_salesforce_doc.py` | 用于获取任何官方 Salesforce 文档 URL；自动将 `help.salesforce.com` 路由到专用的帮助提取器，并支持所有 Salesforce 拥有的文档主机的浏览器渲染提取 |
| `scripts/extract_help_salesforce.py` | 直接用于目标 `help.salesforce.com` `articleView` URL；当包装器不适用时使用 |
| `scripts/runtime_bootstrap.py` | 由提取脚本导入，用于解析隔离的 platform-docs-get Python 运行时和 Playwright 浏览器路径；不直接调用 |
| `scripts/requirements.txt` | 列出运行提取脚本所需的 Python 依赖项（`playwright`、`playwright-stealth`） |
