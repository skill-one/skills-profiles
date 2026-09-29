---
name: experience-ui-bundle-agentforce-client-generate
description: 在用户要求在 UI Bundle 项目（React 或 Angular）中添加、嵌入、集成、配置、样式化或删除代理、聊天机器人、聊天小部件、对话客户端或 AI 助手时使用此技能。触发条件为：项目包含 uiBundles/*/src/ 目录，且任务涉及添加或修改聊天小部件、聊天机器人或对话 AI；在 React 的 `.tsx`/`.jsx` 文件中导入 AgentforceConversationClient，或在 Angular 的 `.html` 模板中使用 app-agentforce-conversation-client 元素，并在 `.component.ts` 文件中使用 AgentforceConversationClientComponent；用户要求向页面添加任何聊天或代理功能。不触发条件为：用户希望从头开始创建自定义代理、聊天机器人或聊天小部件组件；项目没有 uiBundles 目录。
---

# 管理Agentforce对话客户端

这项技能是**框架无关的**：它支持React和Angular UI Bundle应用程序。Agentforce客户端作为两个功能包提供，它们封装了相同的Lightning Out粘合剂——选择与应用程序框架匹配的那个（在步骤0中检测）：

| 框架 | 功能包 | 元素 | 组件符号 |
|-------|--------|------|----------|
| React | `@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client` | `<AgentforceConversationClient />` | `AgentforceConversationClient` |
| Angular | `@salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client` | `<app-agentforce-conversation-client>` | `AgentforceConversationClientComponent` |

**硬性约束**：**永远不要**创建自定义代理、聊天机器人或聊天小部件组件。**所有此类请求都必须通过导入并渲染文档中记录的现有框架适用组件（React `<AgentforceConversationClient />` 或 Angular `<app-agentforce-conversation-client>`）来满足**。如果要求不受组件的属性/输入支持，请声明限制——不要自行设计替代方案。

## 前置条件

在组件正常工作之前，用户必须配置以下Salesforce设置。**在成功嵌入代理后，始终调用前置条件**。

**受信任的域（仅限本地开发所需）**：

- 设置 → 会话设置 → 内联框架的受信任域 → 添加您的域
  - 本地开发：`localhost:<dev-server-port>` — React（Vite）默认为`localhost:5173`；Angular模板可能使用不同的端口（检查应用程序的dev-server配置，例如`localhost:5174`）。添加应用程序实际运行的端口。
  - **警告**：在生产环境中部署之前，请删除此受信任域条目。

## 说明

### 步骤0：检测应用程序框架

在执行任何操作之前，确定目标UI Bundle应用程序是**React**还是**Angular**——它决定了以下每个步骤中的发现、导入、元素语法和属性绑定。

对应用程序（或uiBundle）根运行捆绑检测器。它确定性地执行检测并打印一个确切标记——`react`、`angular`、`ambiguous`或`unknown`：

```bash
bash "<skill_dir>/scripts/detect-framework.sh" "<app-or-uiBundle-root>"
```

检测器组合：根目录处的`angular.json`；任何非`node_modules`中的`package.json`中的`@angular/core` / `react`；以及源文件签名（`*.component.ts`、`app.routes.ts`，或Angular的`*.component.ts`/`@Component`装饰的类；React的`*.tsx`/`*.jsx`）。

根据结果采取行动：

- `react`或`angular` → 使用该框架。**不要**询问用户——检测是确定性的。
- `ambiguous`（检测到两个框架）或`unknown`（一个都没有）→ 在继续之前询问用户应用程序使用哪个框架。

将解析的框架传递到剩余步骤。

### 步骤1：检查组件是否已存在

在所有应用程序文件（不包括实现文件）中搜索现有使用情况。使用检测到的框架的grep：

**React:**
```bash
grep -r "AgentforceConversationClient" --include="*.tsx" --include="*.jsx" --exclude-dir=node_modules
```

**Angular:**
```bash
grep -rn "app-agentforce-conversation-client" --include="*.html" --exclude-dir=node_modules
grep -rn "AgentforceConversationClientComponent" --include="*.ts" --exclude-dir=node_modules
```

**重要**：查找使用元素（例如共享外壳/布局、路由组件或功能页面）的文件——对于Angular，`<app-agentforce-conversation-client>`标签位于`*.html`模板中，组件在主机的`imports: [...]`中注册。**不要**打开组件*实现*文件：
- React: `AgentforceConversationClient.tsx` / `AgentforceConversationClient.jsx`
- Angular: `conversation.ts`，`conversation.html`，`__inherit__conversation.ts`，`agentforce-embed.service.ts`

**如果找到多个文件**：询问用户他们指的是哪个组件文件。直到澄清后才能继续。

**如果找到**：读取文件并检查当前的`agentId`值。

**Agent ID验证规则（确定性）**：

- 仅当它与`^0Xx[a-zA-Z0x9]{15}$`匹配时才有效
- 含义：以`0Xx`开头，总长度为18个字符

**决策**：

- 如果`agentId`匹配`^0Xx[a-zA-Z0x9]{15}$`且用户想更新其他属性→转到步骤4（更新属性）
- 如果`agentId`匹配`^0Xx[a-zA-Z0x9]{15}$`且用户要求“嵌入”或“添加”聊天客户端→通知：“Agentforce Conversation Client已经嵌入在`<file>`中，agent ID为`<agentId>`。您想更改代理还是更新其他属性？”
  - 更改代理→步骤2
  - 更新属性→步骤4b
- 如果`agentId`缺失、为空或**不**匹配`^0Xx[a-zA-Z0x9]{15}$`→继续到步骤2（需要真实ID）
- 如果未找到→继续到步骤2（添加新）

**如果用户报告错误**：

如果用户说组件“无法工作”、“显示错误”或类似情况——请他们提供具体的错误消息。然后继续到步骤2以交叉检查配置的agentId与组织。

### 步骤2：解析和验证Agent ID

#### 前置条件

1. **验证sf CLI可用性:**
   ```bash
   sf --version
   ```
   如果失败：
   - 通知：“Salesforce CLI (`sf`)未安装。需要它来查询您组织中的可用代理。”
   - 询问：“您想让我安装它吗？”
     - 是→通过`npm install -g @salesforce/cli`安装，然后继续。
     - 否→“您可以在设置→Agentforce代理→点击代理名称→从URL复制ID。您现在想提供它，还是跳过这个步骤？”
       - 用户提供ID→验证格式（`^0Xx[a-zA-Z0x9]{15}$`），存储它，转到步骤3。
       - 跳过→转到步骤4，使用占位符`<YOUR_AGENT_ID>`。

2. **验证组织连接性:**
   ```bash
   sf org display --json
   ```
   如果失败：
   - 通知：“未找到经过身份验证的组织。”
   - 询问：“您想现在连接到您的组织吗？运行`sf org login web`进行身份验证。”
     - 用户进行身份验证→重试查询，继续。
     - 用户拒绝→“您可以在设置→Agentforce代理→点击代理名称→从URL复制ID。您现在想提供它，还是跳过这个步骤？”
       - 用户提供ID→验证格式，存储它，转到步骤3。
       - 跳过→转到步骤4，使用占位符`<YOUR_AGENT_ID>`。

**注意**：即使用户提供自己的agentId，组织必须连接，代理才能在运行时起作用。没有连接组织的agentId将无法工作。

#### 查询所有员工代理

运行在`references/agent-id-resolution.md`中定义的SOQL查询。

#### 处理结果

**完全没有记录**：
> “在此组织中未找到员工代理。在设置→Agentforce代理中创建一个。”

询问用户是否想手动提供代理ID或跳过。如果跳过，转到步骤4，使用占位符`<YOUR_AGENT_ID>`。

**所有代理都处于非活动状态**：
> 查询到员工代理，但没有一个是活动的：
>   - Agentforce销售代理 (0Xxxx000000001dCAA)
>   - 人力资源助手 (0Xxxx0000000002BBB)
>
> 要激活：设置→Agentforce代理→点击代理名称→在Agent Builder中打开→按激活。
> 然后重新运行此步骤。

询问用户是否想手动提供代理ID或跳过。如果跳过，转到步骤4，使用占位符`<YOUR_AGENT_ID>`。

**有活动代理——路径A（全新安装/没有现有的agentId）**：

仅显示活动代理供选择：
> 聊天小部件应使用哪个代理？
>   1. 房产管理代理 (0Xxxx0000000001CAA)
>   2. 人力资源助手 (0Xxxx0000000002BBB)

- 一个代理→仍然确认用户的选择，不要自动选择。
- 如果用户选择一个→存储选定的`Id`以用于步骤4。
- 如果用户拒绝选择（“跳过”、“不”、“我不想设置一个”）→接受它并继续下一步。不要重新询问。在步骤4中，对于全新安装，使用占位符`<YOUR_AGENT_ID>`。对于现有项目，保留组件原样。

**有活动代理——路径B（来自步骤1的现有agentId，通过格式检查）**：

将现有agentId与查询结果交叉检查：

- **ID找到，代理处于活动状态**→“Agent ID映射到'Property Manager Agent'——在组织中处于活动状态。”继续。
- **ID找到，代理处于非活动状态**→“配置的代理'Sales Agent'存在但处于非活动状态。要激活：设置→Agentforce代理→点击代理名称→在Agent Builder中打开→按激活。或选择一个不同的活动代理：”→显示活动列表。
- **ID完全找不到**→“配置的代理（0Xxxx...）在此组织中不存在——它可能已被删除或属于不同的组织。选择一个替代方案：”→显示活动列表。如果没有活动代理可用，显示非活动列表并附带激活说明。

如果用户报告了错误→即使代理处于活动状态，也要显示代理名称，以便用户确认它是预期的那个。

#### 查询错误处理

如果SOQL查询失败，直接向用户显示来自响应的错误消息。不要猜测解决方案——只需报告收到的内容。例如：
> “查询失败：`[来自响应的错误消息]`。检查您的组织权限或API版本是否支持此对象。”

#### 此步骤不做什么

- 没有回退到GraphQL或Tooling API——仅SOQL
- 没有自动选择（始终与用户确认）
- 没有程序化激活（仅通过设置UI激活）
- 没有文件写入（那是步骤4）

### 步骤3：规范导入策略

使用检测到的框架的导入。

**React**——默认在应用程序代码中导入组件：

```tsx
import { AgentforceConversationClient } from "@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client";
```

如果包未安装，请安装它：

```bash
npm install @salesforce/ui-bundle-template-feature-react-agentforce-conversation-client
```

**Angular**——导入独立的组件**并在主机组件的`imports`数组中注册它**（Angular如果没有此注册将渲染什么都没有——没有React的对应物）：

```ts
import { AgentforceConversationClientComponent } from "@salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client";

@Component({
  selector: "app-layout",
  imports: [/* 现有导入 */ AgentforceConversationClientComponent],
  templateUrl: "./app-layout.html",
})
export class AppLayoutComponent {}
```

如果包未安装，请安装它：

```bash
npm install @salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client
```

**本地/组合导入**：仅在用户明确要求使用修补/本地组件，或应用程序是已经本地继承功能文件的组合UI Bundle时才使用本地相对导入——React组合应用程序从`./components/AgentforceConversationClient`导入，Angular组合应用程序从继承的功能文件（例如`../../../features/agentforce/__inherit__conversation`）导入`AgentforceConversationClientComponent`。如果主机以这种方式导入它，请匹配现有的导入，而不是切换到包。

不要仅凭文件发现来推断导入路径。在代码库中优先使用一致的导入。

### 步骤4：添加或更新组件

确定适用哪个子步骤：

- 组件在步骤1中未找到→转到**4a（新安装）**
- 组件在步骤1中找到→转到**4b（更新现有）**

#### 4a — 新安装

1. 如果用户已经指定了目标文件，请使用该文件。否则，询问用户：“我应该将Agentforce Conversation Client添加到哪个文件？”不要继续，直到确认了目标文件。（React：一个`*.tsx`/`*.jsx`组件。Angular：主机组件的`*.html`模板——加上其`*.ts`用于导入+`imports: []`注册。）
2. 读取目标文件以了解现有的导入和模板结构。
3. 添加来自步骤3的导入。**Angular额外要求在主机`@Component({ imports: [...] })`数组中注册组件**——没有这个元素将不会渲染任何内容。
4. 将元素作为现有内容的兄弟插入——不要包装或重新结构现有标记。使用来自步骤2的真实`agentId`，或如果用户跳过步骤2，则使用占位符`<YOUR_AGENT_ID>`。

**React (JSX):**
```tsx
<AgentforceConversationClient agentId="0Xx8X00000001AbCDE" />
```

**Angular (模板):**
```html
<app-agentforce-conversation-client agentId="0Xx8X00000001AbCDE" />
```

5. 除非用户明确要求，否则**不要**添加任何其他代码（包装器、布局组件、新函数）。

> **Angular属性绑定规则（关键）**：输入*名称*在两个框架中相同，但绑定语法不同。一个裸属性是一个**字符串**，因此布尔值/数字/对象**必须**使用`[prop]`绑定：
> - 字符串 → `agentId="0Xx..."`，`width="420px"`（普通属性可以）
> - 布尔值 → `[inline]="true"`，`[headerEnabled]="false"`（**不是**裸`inline`，它产生字符串`""`）
> - 数字 → `[width]="420"`
> - 对象 → `[styleTokens]="{ headerBlockBackground: '#0176d3' }"`

**完成前验证（Angular）**：

- [ ] 每个非字符串输入（布尔值/数字/对象）都使用`[prop]`绑定——没有裸`inline`/`headerEnabled`属性。
- [ ] `AgentforceConversationClientComponent`在主机组件的`@Component({ imports: [...] })`数组中注册（没有它元素将不会渲染）。

#### 4b — 更新现有

1. 读取步骤1中标识的文件。
2. 定位现有元素（`<AgentforceConversationClient ... />`对于React，`<app-agentforce-conversation-client ...>`对于Angular）。
3. 应用**仅**用户请求的更改。规则：
   - **添加**用户请求的新属性。
   - **更改**用户请求更新的属性值。
   - **保留**用户未提及的每个属性和值——不要删除、重新排序或重新格式化它们。
   - **永远**不要删除组件并重新创建它。
4. 如果步骤2被触发（交叉检查或全新选择）并解析了新的agent ID，请用新的值替换现有的agentId值。
5. 如果当前`agentId`已经有效，用户没有请求更改它，并且步骤2确认它是活动的，则保持原样。

#### 步骤4后的错误处理

如果用户在组件设置后报告错误（例如，“它不起作用”，“我看到错误”），转到步骤2以验证配置的agentId与组织。交叉检查代理是否处于活动状态、是否存在并属于连接的组织。

### 步骤5：配置属性

**可用属性/输入（两个框架中的名称相同；只有绑定语法不同——参见步骤4a中的Angular规则）**：

- `agentId`（字符串，必需）- Salesforce代理ID
- `inline`（布尔值）- `true`为内联模式，省略为浮动
- `width`（数字 | 字符串）- 例如，`420`或`"100%"`
- `height`（数字 | 字符串）- 例如，`600`或`"80vh"`
- `headerEnabled`（布尔值）- 显示/隐藏标题
- `styleTokens`（对象）- 用于所有样式（颜色、字体、间距）
- `salesforceOrigin`（字符串）- 自动解析
- `frontdoorUrl`（字符串）- 自动解析
- `agentLabel`（字符串）- 代理的标题

**示例**：

浮动模式（默认）：

```tsx
// React
<AgentforceConversationClient agentId="0Xx..." />
```
```html
<!-- Angular -->
<app-agentforce-conversation-client agentId="0Xx..." />
```

内联模式带尺寸：

```tsx
// React
<AgentforceConversationClient agentId="0Xx..." inline width="420px" height="600px" />
```
```html
<!-- Angular — 布尔值输入需要`[ ]`绑定 -->
<app-agentforce-conversation-client agentId="0Xx..." [inline]="true" width="420px" height="600px" />
```

添加或更新代理标签：

```tsx
// React
<AgentforceConversationClient agentId="0Xx..." agentLabel="<dummy-agent-label>" />
```
```html
<!-- Angular -->
<app-agentforce-conversation-client agentId="0Xx..." agentLabel="<dummy-agent-label>" />
```

**样式规则（强制）**：

- 所有视觉定制（颜色、字体、间距、边框、圆角、阴影）必须通过 `styleTokens` prop/输入传递。没有例外。
- 仅使用下方表格中列出的 token 名称。不要编造自定义的 token 名称。
- 绝对不要通过 CSS 文件、`style` 属性、`className`/`class` 或包装元素应用样式。这些方法将不起作用，组件将忽略它们。
- Angular：使用 `[styleTokens]="{ ... }"` 绑定（对象）传递 token，而不是裸属性。
- 如果用户请求的视觉变更不映射到下方的 token，请告知他们此变更当前不被 token 集支持。

有关可用样式 token 的完整列表，请参阅 `references/style-tokens.md`。

**对于复杂模式**，请参阅 `references/examples.md` 以获取：

- 侧边栏容器和响应式尺寸
- 暗主题和高级主题组合
- 无标题的行内样式，计算尺寸
- 完整的主组件示例

**常见错误避免**：请参阅 `references/constraints.md` 以获取：

- 无效的 props（containerStyle、style、className）
- 无效的样式方法（CSS 文件、style 标签）
- 不应编辑的文件（实现文件）

## 常见问题

如果组件未显示或身份验证失败，请参阅 `references/troubleshooting.md` 以获取：

- 代理激活和部署
- 本地主机信任域
- Cookie 限制设置

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/agent-id-resolution.md` | 第 2 步 — SOQL 查询结构、响应格式、激活路径、手动查找 |
| `references/style-tokens.md` | 第 5 步 — 所有 UI 区域的完整样式 token 参考 |
| `references/examples.md` | 第 5 步 — 布局模式、尺寸、主题组合、主组件示例 |
| `references/constraints.md` | 第 4 步 — 无效的 props、无效的样式方法、不应编辑的文件 |
| `references/troubleshooting.md` | 安装后 — 代理激活、信任域、Cookie 设置 |
