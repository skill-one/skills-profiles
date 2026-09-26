# sf-docs

使用此技能从**公开网络上的 Salesforce 官方文档**中检索并获取答案。

此技能设计得非常简单：
- **没有本地语料库**
- **没有索引**
- **没有基准工作流**
- **没有辅助 CLI 依赖**
- **没有 PDF 降级方案**

它的任务是提供一套**可靠的在线检索方案**，用于获取难以检索的 Salesforce 文档，特别是 `help.salesforce.com`、JS 重的 `developer.salesforce.com`、`lightningdesignsystem.com` 上的 Lightning Design System 文档，以及其他官方 Salesforce 拥有的文档页面，如 `architect.salesforce.com` 和 `admin.salesforce.com`。

一个可选的包装脚本位于：
- `skills/sf-docs/scripts/extract_salesforce_doc.py`

它自动将 `help.salesforce.com` URL 路由到专门的 Help 提取器，并支持其他官方文档页面，如 `*.salesforce.com` 和 `lightningdesignsystem.com` 通过通用的浏览器渲染路径。对于对机器人敏感的页面，当安装了 `playwright-stealth` 时，它也支持通过 `--stealth` 进行最佳效果的隐身模式。

专门的 Help 提取器也直接可用：
- `skills/sf-docs/scripts/extract_help_salesforce.py`

## 核心目标

在线找到最佳的官方 Salesforce HTML 页面，并提取足够的真实内容以自信地回答。

如果证据不足，请明确说明，而不是强迫给出一个弱的答案。

## 使用场景

当用户询问以下内容时使用 `sf-docs`：
- 官方 Salesforce 文档
- Apex、API、LWC、元数据、Agentforce、设置或帮助文章
- 来自 `developer.salesforce.com` 的文档
- 来自 `help.salesforce.com` 的文档
- 看起来 JS 重的、shell 渲染的或用普通获取方式难以阅读的页面

## 仅限官方来源

优先选择 Salesforce 拥有的文档来源：
- `developer.salesforce.com`
- `help.salesforce.com`
- `architect.salesforce.com`
- `admin.salesforce.com`
- `lightningdesignsystem.com`
- 当 Salesforce 将其用作事实来源时，其他相关的官方 Salesforce 文档页面

避免第三方博客、视频或摘要文章，除非用户明确要求。

**不要**降级到 PDF。

## 检索工作流

### 1. 首先对请求进行分类

在获取任何内容之前，识别可能的文档系列。

| 系列 | 典型来源 | 用于 |
|---|---|---|
| 开发者文档 | `developer.salesforce.com/docs/...` | Apex、API、LWC、元数据、Agentforce 开发者文档 |
| 帮助文档 | `help.salesforce.com/...` | 设置、管理、产品配置 |
| 架构师/管理文档 | `architect.salesforce.com/...`, `admin.salesforce.com/...` | 最佳实践、模式、架构良好指导、管理启用 |
| 设计系统文档 | `lightningdesignsystem.com/...` | SLDS、Cosmos、设计令牌、组件和样式指导 |
| 遗留图谱文档 | `developer.salesforce.com/docs/atlas.en-us.*` | 较旧的官方指南和参考文档 |

### 2. 确定确切的概念

在搜索之前提取真实的目标：
- 确切的 API/类/方法名称
- 确切的功能名称
- 确切的产品短语
- 确切设置概念

示例：
- `Lightning Message Service`
- `Wire Service`
- `System.StubProvider`
- `Agentforce Actions`
- `Messaging for In-App and Web allowed domains`

### 3. 优先选择目标官方检索

**不要**广泛爬取 Salesforce 文档。

相反：
1. 确定最可能的官方指南根或文章
2. 如果需要搜索，仅将其限制在官方 Salesforce 域名内
3. 获取该官方页面
4. 检查 **确切的概念是否实际出现在该页面上**
5. 如果没有，检查并遵循最相关的 **1–3 个官方子链接**
6. 一旦获得可靠证据即停止

### 4. 不要在宽泛的着陆页停止

指南着陆页**不足以**，除非它明确包含所需的精确概念。

这对于以下内容尤其重要：
- LWC 文档
- Agentforce 文档
- 广泛的平台指南主页
- 指南着陆页，这些页面链接到实际文章

### 5. 对于 `developer.salesforce.com`

使用此方案：
- 从最可能的官方指南根开始
- 如果页面 JS 重，优先使用浏览器渲染提取
- 检查页面是否出现确切概念
- 如果概念缺失，检查官方子链接并跟随最佳匹配的 1–3 个链接
- 优先选择确切概念页面而不是宽泛的指南根
- 遗留图谱页面是有效的，如果它们是概念的真实官方参考

### 6. 对于 `help.salesforce.com`

帮助页面通常在简单获取时失败。

使用此方案：
- 当可用时，优先选择确切的 `articleView?id=...` URL
- 当纯获取返回 shell 内容时，使用浏览器渲染提取
- 将类似 `Loading`、`Sorry to interrupt`、`CSS Error` 或大部分 Chrome/导航文本的输出视为 **获取失败**，而不是证据
- 寻找 **真实文章正文**，而不仅仅是页眉、导航或页脚文本
- 拒绝 shell 页面和软 404 页面，例如：
  - "我们到处找过，但找不到那个页面"
  - 通用空帮助 shell
- 如果从附近的指南或中心页面开始，跟随链接的帮助文章，直到到达真实文章正文
- 如果在目标重试后提取仍然失败，返回您找到的最佳官方帮助 URL，并明确说明文章正文提取失败

## 接受规则

只有当满足以下至少一项时，页面才足够用于回答：
- 页面上出现确切的标识符
- 页面上出现确切的概念短语
- 多个特定于查询的短语以正确的官方上下文出现

当页面**不足以**时：
- 它只是一个宽泛的着陆页
- 它是一个 shell 页面，几乎没有真实文章文本
- 它来自错误的产品区域
- 它不包含请求的标识符或概念
- 它是第三方解释，而应该存在官方页面

## 拒绝规则

拒绝以下作为最终证据：
- 没有确切概念的宽泛指南主页
- 当期望概念/参考页面时，发布说明
- 当请求开发者文档时，管理博客文章
- 当有官方文档可用时，第三方博客
- 没有真实文章正文的 shell 渲染页面
- 标题听起来正确但正文不包含请求概念的页面

## 定位要求

回答时包括：
1. 指南/文章标题
2. 确切官方 URL
3. 来源类型：
   - 开发者文档页面
   - 图谱参考页面
   - 帮助文章页面
4. 如果提取部分或浏览器渲染，则任何注意事项

如果证据不足，请明确说明。

## 示例

### 示例：Lightning Message Service
**不要**在一般 LWC 指南根停止。
找到 Lightning Message Service 的确切 LWC 页面，或从 LWC 文档跟随最相关的子链接，直到出现确切概念。

### 示例：Wire Service
**不要**从 LWC 主页回答，除非 `Wire Service` 实际上在那里。
跟随与 wire service 或 wire adapters 相关的子文档页面。

### 示例：Agentforce Actions
**不要**从宽泛的 Agentforce 着陆页或博客文章回答。
找到官方 Agentforce 开发者页面，用于 actions，或从官方 Agentforce 文档跟随最佳匹配的 1–3 个子页面。

### 示例：Messaging for In-App and Web allowed domains
优先选择官方帮助文章和浏览器渲染提取。
拒绝通用帮助 shell。如果需要，从附近的官方消息文档跟随链接的帮助文章。

### 示例：System.StubProvider
优先选择确切的标识符出现在官方 Salesforce 参考/开发者页面的情况。
如果标识符缺失，**不要**用更广泛的 Apex 着陆页替代。

## 非目标

此技能**不应**：
- 维护本地文档语料库
- 依赖本地索引
- 使用 PDF 降级方案
- 运行基准工作流
- 依赖特定于存储库的脚本才能使用

## 跨技能角色

其他 `sf-*` 技能在使用时需要权威的 Salesforce 文档，而不是仅依赖通用搜索，应使用 `sf-docs`。
