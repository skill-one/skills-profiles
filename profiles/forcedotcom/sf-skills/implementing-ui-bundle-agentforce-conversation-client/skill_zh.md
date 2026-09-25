# 管理Agentforce对话客户端

**硬性约束：** 绝对不要创建自定义的代理、聊天机器人或聊天小部件组件。所有此类请求都必须按照下方说明导入并渲染 `@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client` 中的现有 `<AgentforceConversationClient />`。如果某个需求不受此组件的属性支持，请说明限制，不要自行设计替代方案。

## 前置条件

在组件能够正常工作之前，用户必须配置以下Salesforce设置。在成功嵌入代理后，务必列出前置条件。

**受信任的域（仅本地开发时需要）：**

- 设置 → 会话设置 → 内联框架的受信任域 → 添加您的域
  - 本地开发：`localhost:5173`（默认Vite开发服务器端口）
  - **警告：** 部署到生产环境前，请移除此受信任域条目。

## 说明

### 第1步：检查组件是否已存在

在所有应用文件（不包括实现文件）中搜索现有使用情况：

```bash
grep -r "AgentforceConversationClient" --include="*.tsx" --include="*.jsx" --exclude-dir=node_modules
```

**重要：** 查找导入并使用该组件的React文件（例如，共享外壳、路由组件或功能页面）。不要打开名为 `AgentforceConversationClient.tsx` 或 `AgentforceConversationClient.jsx` 的文件——这些是组件的实现文件。

**如果找到多个文件：** 询问用户他们指的是哪个组件文件。在澄清之前不要继续。

**如果找到：** 阅读该文件并检查当前的 `agentId` 值。

**Agent ID验证规则（确定性）：**

- 仅当它匹配：`^0Xx[a-zA-Z0-9]{15}$`
- 含义：以 `0Xx` 开头，总长度为18个字符

**决策：**

- 如果 `agentId` 匹配 `^0Xx[a-zA-Z0-9]{15}$` 且用户想更新其他属性 → 转到第4步（更新属性）
- 如果 `agentId` 匹配 `^0Xx[a-zA-Z0x9]{15}$` 且用户要求“嵌入”或“添加”聊天客户端 → 通知：“Agentforce对话客户端已经嵌入在 `<文件>` 中，使用代理ID `<agentId>`。您想更改代理还是更新其他属性？”
  - 更改代理 → 第2步
  - 更新属性 → 第4b步
- 如果 `agentId` 为空、不存在或不符合 `^0Xx[a-zA-Z0x9]{15}$` → 继续到第2步（需要真实ID）
- 如果未找到 → 继续到第2步（添加新）

**如果用户报告错误：**

如果用户说组件“无法工作”、“显示错误”或类似情况——请要求他们提供具体的错误信息。然后继续到第2步以核对配置的 `agentId` 与组织。

### 第2步：解决和验证代理ID

#### 前置条件

1. **验证sf CLI是否可用：**
   ```bash
   sf --version
   ```
   如果失败：
   - 通知：“Salesforce CLI (`sf`) 未安装。需要它来查询您组织中的可用代理。”
   - 询问：“您想让我安装它吗？”
     - 是 → 通过 `npm install -g @salesforce/cli` 安装，然后继续。
     - 否 → “您可以在设置 → Agentforce代理 → 点击代理名称 → 从URL中复制ID。您现在想提供它，还是跳过此步骤？”
       - 用户提供ID → 验证格式 (`^0Xx[a-zA-Z0x9]{15}$`)，存储它，转到第3步。
       - 跳过 → 转到第4步，使用占位符 `<YOUR_AGENT_ID>`。

2. **验证组织连接性：**
   ```bash
   sf org display --json
   ```
   如果失败：
   - 通知：“未找到已认证的组织。”
   - 询问：“您想现在连接到您的组织吗？运行 `sf org login web` 进行身份验证。”
     - 用户进行身份验证 → 重试查询，继续。
     - 用户拒绝 → “您可以在设置 → Agentforce代理 → 点击代理名称 → 从URL中复制ID。您现在想提供它，还是跳过此步骤？”
       - 用户提供ID → 验证格式，存储它，转到第3步。
       - 跳过 → 转到第4步，使用占位符 `<YOUR_AGENT_ID>`。

**注意：** 即使用户提供自己的 `agentId`，组织必须连接，代理才能在运行时起作用。没有连接组织的 `agentId` 将无法工作。

#### 查询所有员工代理

运行在 `references/agent-id-resolution.md` 中定义的SOQL查询。

#### 处理结果

**完全没有记录：**
> “此组织中未找到员工代理。请在设置 → Agentforce代理中创建一个。”

询问用户是否想手动提供代理ID或跳过。如果跳过，转到第4步，使用占位符 `<YOUR_AGENT_ID>`。

**所有代理都处于非活动状态：**
> 查询到员工代理，但没有一个是活动的：
>   - Agentforce销售代理 (0Xxxx000000001dCAA)
>   - 人力资源助手 (0Xxxx0000000002BBB)
>
> 要激活：设置 → Agentforce代理 → 点击代理名称 → 在代理构建器中打开 → 点击激活。
> 然后重新运行此步骤。

询问用户是否想手动提供代理ID或跳过。如果跳过，转到第4步，使用占位符 `<YOUR_AGENT_ID>`。

**有活动代理 — 路径A（全新安装/不存在现有 `agentId`）：**

仅显示活动代理供选择：
> 聊天小部件应使用哪个代理？
>   1. 房产管理代理 (0Xxxx0000000001CAA)
>   2. 人力资源助手 (0Xxxx0000000002BBB)

- 一个代理 → 仍需确认用户选择，不要自动选择。
- 如果用户选择一个 → 存储选中的 `Id` 以用于第4步。
- 如果用户拒绝选择（“跳过”、“不”、“我不想设置”）→ 接受它并继续下一步。不要重新询问。在第4步中，对于全新安装使用占位符 `<YOUR_AGENT_ID>`。对于现有项目，保留组件原样。

**有活动代理 — 路径B（来自第1步的现有 `agentId`，格式检查通过）：**

将现有 `agentId` 与查询结果进行核对：

- **ID找到，代理处于活动状态** → “Agent ID映射到‘房产管理代理’——在组织中处于活动状态。” 继续。
- **ID找到，代理处于非活动状态** → “配置的代理‘销售代理’存在但处于非活动状态。要激活：设置 → Agentforce代理 → 点击代理名称 → 在代理构建器中打开 → 点击激活。或选择一个不同的活动代理：” → 显示活动列表。
- **ID完全找不到** → “配置的代理 (0Xxxx...) 在此组织中不存在——它可能已被删除或属于不同的组织。选择一个替代代理：” → 显示活动列表。如果没有活动代理可用，显示非活动列表并附带激活说明。

如果用户报告错误 → 即使代理处于活动状态，也显示代理名称，以便用户确认它是预期的代理。

#### SOQL查询错误处理

如果SOQL查询失败，直接向用户显示来自响应的错误消息。不要猜测解决方案——只需报告返回的内容。例如：
> “查询失败：`[来自响应的错误消息]`。检查您的组织权限或API版本是否支持此对象。”

#### 此步骤不做什么

- 不回退到GraphQL或Tooling API——仅使用SOQL
- 不自动选择（始终与用户确认）
- 不程序化激活（仅通过设置UI）
- 不进行文件写入（那是第4步）

### 第3步：规范导入策略

在应用代码中默认使用此导入路径：

```tsx
import { AgentforceConversationClient } from "@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client";
```

如果包未安装，则安装它：

```bash
npm install @salesforce/ui-bundle-template-feature-react-agentforce-conversation-client
```

仅在用户明确要求在此应用中使用修补/本地组件时，才使用本地相对导入（例如，`./components/AgentforceConversationClient`）。不要仅凭文件发现推断导入路径。在代码库中优先使用一致的包导入。

### 第4步：添加或更新组件

确定适用哪个子步骤：

- 第1步中未找到组件 → 转到 **4a（全新安装）**
- 第1步中找到组件 → 转到 **4b（更新现有）**

#### 4a — 全新安装

1. 如果用户已经指定了目标文件，则使用该文件。否则，询问用户：“我应该将 AgentforceConversationClient 添加到哪个文件？” 直到确认目标文件。
2. 读取目标文件以了解其现有的导入和TSX结构。
3. 在文件顶部添加导入，与现有导入一起使用。使用第3步中的规范包导入：

```tsx
import { AgentforceConversationClient } from "@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client";
```

4. 将 `<AgentforceConversationClient />` TSX插入组件的返回块中。将其作为现有内容的同级元素插入——不要包装或重构现有TSX。使用在第2步中获得的真实 `agentId`。如果未解析出代理ID（用户跳过第2步），则使用占位符：

**使用解析出的代理ID：**
```tsx
<AgentforceConversationClient agentId="0Xx8X00000001AbCDE" />
```

**未解析出代理ID（用户跳过）：**
```tsx
<AgentforceConversationClient agentId="<YOUR_AGENT_ID>" />
```

5. 除非用户明确要求，否则不要添加任何其他代码（包装器、布局组件、新函数）。

#### 4b — 更新现有

1. 读取第1步中标识的文件。
2. 定位现有的 `<AgentforceConversationClient ... />` TSX元素。
3. 仅应用用户请求的更改。规则：
   - **添加** 用户请求的新属性。
   - **更改** 用户请求更新的属性值。
   - **保留** 用户未提及的每个属性和值——不要删除、重新排序或重新格式化它们。
   - **永远** 不要删除组件并重新创建它。
4. 如果第2步被触发（交叉核对或全新选择）并解析出新的代理ID，则用新值替换现有 `agentId`。
5. 如果当前 `agentId` 已经有效，用户没有要求更改它，且第2步确认它是活动的，则保持不变。

#### 第4步后的错误处理

如果用户在组件设置后报告错误（例如，“它不工作”、“我看到错误”），转到第2步以验证配置的 `agentId` 与组织。交叉核对代理是否处于活动状态、是否存在，且属于连接的组织。

### 第5步：配置属性

**可用属性（直接应用于组件）：**

- `agentId`（字符串，必需）- Salesforce代理ID
- `inline`（布尔值）- `true` 用于内联模式，省略用于浮动
- `width`（数字 | 字符串）- 例如，`420` 或 `"100%"`
- `height`（数字 | 字符串）- 例如，`600` 或 `"80vh"`
- `headerEnabled`（布尔值）- 显示/隐藏标题
- `styleTokens`（对象）- 用于所有样式（颜色、字体、间距）
- `salesforceOrigin`（字符串）- 自动解析
- `frontdoorUrl`（字符串）- 自动解析
- `agentLabel`（字符串）- 代理的标题

**示例：**

浮动模式（默认）：

```tsx
<AgentforceConversationClient agentId="0Xx..." />
```

内联模式带尺寸：

```tsx
<AgentforceConversationClient agentId="0Xx..." inline width="420px" height="600px" />
```

添加或更新代理标签：

```tsx
<AgentforceConversationClient agentId="0Xx..." agentLabel="<dummy-agent-label>" />
```

**样式规则（强制）：**

- 所有视觉定制（颜色、字体、间距、边框、半径、阴影）都必须通过 `styleTokens` 属性进行。没有例外。
- 仅使用下方表格中列出的标记名称。不要发明自定义标记名称。
- 绝对不要通过CSS文件、`style`属性、`className`或包装元素应用样式。这些方法将不起作用，组件将忽略它们。
- 如果用户请求的视觉更改未映射到下方标记，请通知他们此更改当前不受支持的标记集支持。

有关完整可用样式标记列表，请参阅 `references/style-tokens.md`。

对于复杂模式，请参阅 `references/examples.md`，了解：

- 侧边栏容器和响应式尺寸
- 暗色主题和高级主题组合
- 无标题的内联，计算尺寸
- 完整主机组件示例


**常见错误：** 请参阅 `references/constraints.md`，了解：

- 无效属性（containerStyle、style、className）
- 无效样式方法（CSS文件、style标签）
- 不要编辑的文件（实现文件）

## 常见问题

如果组件未显示或身份验证失败，请参阅 `references/troubleshooting.md`，了解：

- 代理激活和部署
- 本地主机受信任域
- Cookie限制设置

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/agent-id-resolution.md` | 第2步 — SOQL查询结构、响应格式、激活路径、手动查找 |
| `references/style-tokens.md` | 第5步 — 完整样式标记参考，适用于所有UI区域 |
| `references/examples.md` | 第5步 — 布局模式、尺寸、主题组合、主机组件示例 |
| `references/constraints.md` | 第4步 — 无效属性、无效样式方法、不要编辑的文件 |
| `references/troubleshooting.md` | 设置后 — 代理激活、受信任域、Cookie设置 |
