# 管理Agentforce对话客户端

这项技能是**框架无关的**：它支持React和Angular UI Bundle应用程序。Agentforce客户端作为两个功能包提供，它们都包装了相同的Lightning Out粘合剂——选择与应用程序框架匹配的包（在步骤0中检测）：

| 框架 | 功能包 | 元素 | 组件符号 |
|-------|-----------------|---------|------------------|
| React | `@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client` | `<AgentforceConversationClient />` | `AgentforceConversationClient` |
| Angular | `@salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client` | `<app-agentforce-conversation-client>` | `AgentforceConversationClientComponent` |

**硬性约束**：永远不要创建自定义代理、聊天机器人或聊天小部件组件。所有此类请求都必须通过导入并渲染现有框架相应的组件（React `<AgentforceConversationClient />` 或 Angular `<app-agentforce-conversation-client>`）来满足，如下文所述。如果要求不受组件的属性/输入支持，请声明限制——不要自行改进替代方案。

## 前置条件

在组件正常工作之前，用户必须配置以下Salesforce设置。在成功嵌入代理后，始终调用前置条件。

**受信任的域（仅限本地开发所需）：**

- 设置 → 会话设置 → 内联框架的受信任域 → 添加您的域
  - 本地开发：`localhost:<dev-server-port>` — React (Vite) 默认为 `localhost:5173`；Angular模板可能使用不同的端口（检查应用程序的dev-server配置，例如 `localhost:5174`）。添加应用程序实际运行的端口。
  - **警告**：在生产环境中部署之前删除此受信任域条目。

## 说明

### 步骤0：检测应用程序框架

在执行任何操作之前，确定目标UI Bundle应用程序是 **React** 还是 **Angular**——它决定了以下每个步骤中的发现、导入、元素语法和属性绑定。

对应用程序（或uiBundle）根运行捆绑检测器。它确定性地执行检测并打印一个确切令牌——`react`、`angular`、`ambiguous` 或 `unknown`：

```bash
bash "<skill_dir>/scripts/detect-framework.sh" "<app-or-uiBundle-root>"
```

检测器组合：根目录处的 `angular.json`；任何非 `node_modules` `package.json` 中的 `@angular/core` / `react`；源文件签名（`*.component.ts`、`app.routes.ts` 或 Angular的 `@Component` 装饰类；React的 `*.tsx`/`*.jsx`）。

根据结果采取行动：

- `react` 或 `angular` → 使用该框架。**不要询问用户**——检测是确定性的。
- `ambiguous`（检测到两个框架）或 `unknown`（未检测到）→ 在继续之前询问用户应用程序使用哪个框架。

在剩余步骤中携带解析的框架。

### 步骤1：检查组件是否已存在

跨所有应用程序文件（不包括实现文件）搜索现有使用情况。使用检测到的框架的grep：

**React:**
```bash
grep -r "AgentforceConversationClient" --include="*.tsx" --include="*.jsx" --exclude-dir=node_modules
```

**Angular:**
```bash
grep -rn "app-agentforce-conversation-client" --include="*.html" --exclude-dir=node_modules
grep -rn "AgentforceConversationClientComponent" --include="*.ts" --exclude-dir=node_modules
```

**重要**：查找使用元素（例如共享外壳/布局、路由组件或功能页面）的文件——对于Angular，`<app-agentforce-conversation-client>` 标签位于 `*.html` 模板中，组件在主机的 `imports: [...]` 中注册。**不要打开组件的实现文件**：
- React: `AgentforceConversationClient.tsx` / `AgentforceConversationClient.jsx`
- Angular: `conversation.ts`，`conversation.html`，`__inherit__conversation.ts`，`agentforce-embed.service.ts`

**如果找到多个文件**：询问用户他们指的是哪个组件文件。直到澄清后才能继续。

**如果找到**：读取文件并检查当前的 `agentId` 值。

**Agent ID 验证规则（确定性地）：**

- 仅当它匹配时才有效：`^0Xx[a-zA-Z0x9]{15}$`
- 含义：以 `0Xx` 开头，总长度为18个字符

**决策：**

- 如果 `agentId` 匹配 `^0Xx[a-zA-Z0x9]{15}$` 且用户想更新其他属性 → 转到步骤4（更新属性）
- 如果 `agentId` 匹配 `^0Xx[a-zA-Z0x9]{15}$` 且用户要求“嵌入”或“添加”聊天客户端 → 通知：“Agentforce Conversation Client 已嵌入 `<file>` 中，代理 ID 为 `<agentId>`。您想更改代理还是更新其他属性？”
  - 更改代理 → 步骤2
  - 更新属性 → 步骤4b
- 如果 `agentId` 缺失、为空或**不**匹配 `^0Xx[a-zA-Z0x9]{15}$` → 继续到步骤2（需要真实ID）
- 如果未找到 → 继续到步骤2（添加新）

**如果用户报告错误：**

如果用户说组件“无法工作”、“显示错误”或类似情况——请他们提供具体的错误消息。然后继续到步骤2以检查配置的agentId是否与组织匹配。

### 步骤2：解析和验证 Agent ID

#### 前置条件

1. **验证 sf CLI 是否可用：**
   ```bash
   sf --version
   ```
   如果失败：
   - 通知：“Salesforce CLI (`sf`) 未安装。需要它来查询您组织中的可用代理。”
   - 询问：“您想让我安装它吗？”
     - 是 → 通过 `npm install -g @salesforce/cli` 安装，然后继续。
     - 否 → “您可以在设置 → Agentforce Agents → 点击代理名称 → 从URL复制ID。您现在想提供它，还是跳过此步骤？”
       - 用户提供ID → 验证格式 (`^0Xx[a-zA-Z0x9]{15}$`)，存储它，继续到步骤3。
       - 跳过 → 继续到步骤4，使用占位符 `<YOUR_AGENT_ID>`。

2. **验证组织连接性：**
   ```bash
   sf org display --json
   ```
   如果失败：
   - 通知：“未找到已认证的组织。”
   - 询问：“您想现在连接到您的组织吗？运行 `sf org login web` 进行身份验证。”
     - 用户进行身份验证 → 重试查询，继续。
     - 用户拒绝 → “您可以在设置 → Agentforce Agents → 点击代理名称 → 从URL复制ID。您现在想提供它，还是跳过此步骤？”
       - 用户提供ID → 验证格式，存储它，继续到步骤3。
       - 跳过 → 继续到步骤4，使用占位符 `<YOUR_AGENT_ID>`。

**注意**：即使用户提供自己的 agentId，组织必须连接，代理才能在运行时起作用。没有连接组织的 agentId 将无法工作。

#### 查询所有 Employee Agents

运行在 `references/agent-id-resolution.md` 中定义的 SOQL 查询。

#### 处理结果

**完全没有记录：**
> “在此组织中未找到 Employee Agents。在设置 → Agentforce Agents 中创建一个。”

询问用户是否想手动提供代理ID或跳过。如果跳过，继续到步骤4，使用占位符 `<YOUR_AGENT_ID>`。

**所有代理都处于非活动状态：**
> 查询到 Employee Agents，但没有一个是活动的：
>   - Agentforce 销售代理 (0Xxxx000000001dCAA)
>   - 人力资源助手 (0Xxxx0000000002BBB)
>
> 要激活：设置 → Agentforce Agents → 点击代理名称 → 在 Agent Builder 中打开 → 按下激活。
> 然后重新运行此步骤。

询问用户是否想手动提供代理ID或跳过。如果跳过，继续到步骤4，使用占位符 `<YOUR_AGENT_ID>`。

**有活动代理——路径A（全新安装/没有现有的 agentId）：**

仅显示活动代理供选择：
> 聊天小部件应使用哪个代理？
>   1. 房产管理代理 (0Xxxx0000000001CAA)
>   2. 人力资源助手 (0Xxxx0000000002BBB)

- 一个代理 → 仍然确认用户的选择，不要自动选择。
- 如果用户选择一个 → 存储选定的 `Id` 以用于步骤4。
- 如果用户拒绝选择（“跳过”、“不”、“我不想设置一个”）→ 接受它并继续下一步。不要重新询问。在步骤4中，对于全新安装使用占位符 `<YOUR_AGENT_ID>`。对于现有项目，保留组件原样。

**有活动代理——路径B（来自步骤1的现有 agentId，通过格式检查）：**

将现有 agentId 与查询结果进行交叉检查：

- **ID找到，代理处于活动状态** → “Agent ID 映射到 'Property Manager Agent' — 在组织中处于活动状态。” 继续。
- **ID找到，代理处于非活动状态** → “配置的代理 'Sales Agent' 存在，但处于非活动状态。要激活：设置 → Agentforce Agents → 点击代理名称 → 在 Agent Builder 中打开 → 按下激活。或选择一个不同的活动代理：” → 显示活动列表。
- **ID完全找不到** → “配置的代理 (0Xxxx...) 在此组织中不存在——它可能已被删除或属于不同的组织。选择一个替代方案：” → 显示活动列表。如果没有活动代理可用，显示带有激活说明的非活动列表。

如果用户报告错误 → 即使代理处于活动状态，也显示代理名称，以便用户确认它是预期的代理。

#### 查询错误处理

如果 SOQL 查询失败，直接向用户显示来自响应的错误消息。不要猜测解决方案——只需报告返回的内容。例如：
> “查询失败，错误信息为：`[来自响应的错误消息]`。检查您的组织权限或API版本是否支持此对象。”

#### 此步骤不做什么

- 不回退到 GraphQL 或 Tooling API——仅 SOQL
- 不自动选择（始终与用户确认）
- 不程序化激活（仅通过设置UI激活）
- 不文件写入（那是步骤4）

### 步骤3：规范导入策略

使用检测到的框架的导入。

**React** — 默认在应用程序代码中导入组件：

```tsx
import { AgentforceConversationClient } from "@salesforce/ui-bundle-template-feature-react-agentforce-conversation-client";
```

如果包未安装，安装它：

```bash
npm install @salesforce/ui-bundle-template-feature-react-agentforce-conversation-client
```

**Angular** — 导入独立的组件**并在主机组件的 `imports` 数组中注册它**（Angular不注册它将渲染什么——没有React类似物）：

```ts
import { AgentforceConversationClientComponent } from "@salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client";

@Component({
  selector: "app-layout",
  imports: [/* 现有导入 */, AgentforceConversationClientComponent],
  templateUrl: "./app-layout.html",
})
export class AppLayoutComponent {}
```

如果包未安装，安装它：

```bash
npm install @salesforce/ui-bundle-template-feature-angular-agentforce-conversation-client
```

**本地/组合导入**：仅在用户明确要求使用修补/本地组件，或应用程序是本地UI Bundle且已本地继承功能文件时使用本地相对导入——React组合应用程序从 `./components/AgentforceConversationClient` 导入，Angular组合应用程序从继承的功能文件（例如 `../../../features/agentforce/__inherit__conversation`）导入 `AgentforceConversationClientComponent`。如果主机以这种方式导入它，请与现有导入匹配，而不是切换到包。

不要仅凭文件发现推断导入路径。在代码库中始终使用一致的导入。

### 步骤4：添加或更新组件

确定适用哪个子步骤：

- 组件在步骤1中未找到 → 前往 **4a（新安装）**
- 组件在步骤1中找到 → 前往 **4b（更新现有）**

#### 4a — 新安装

1. 如果用户已指定目标文件，则使用该文件。否则，询问用户：_“我应该将 Agentforce Conversation Client 添加到哪个文件？”_ 直到确认目标文件后才能继续。（React：一个 `*.tsx`/`*.jsx` 组件。Angular：主机组件的 `*.html` 模板——以及其 `*.ts` 用于导入 + `imports: []` 注册。）
2. 读取目标文件以了解现有的导入和模板结构。
3. 添加来自步骤3的导入。**Angular 需要额外在主机 `@Component({ imports: [...] })` 数组中注册组件**——没有它，元素将不会渲染。
4. 将元素作为现有内容的兄弟插入——不要包装或重新结构现有标记。使用来自步骤2的真实 `agentId`，或如果用户跳过步骤2，则使用占位符 `<YOUR_AGENT_ID>`。

**React (JSX):**
```tsx
<AgentforceConversationClient agentId="0Xx8X00000001AbCDE" />
```

**Angular (模板):**
```html
<app-agentforce-conversation-client agentId="0Xx8X00000001AbCDE" />
```

5. 除非用户明确要求，否则**不要添加任何其他代码**（包装器、布局组件、新函数）。

> **Angular 属性绑定规则（关键）**：输入*名称*与React相同，但绑定语法不同。裸属性是**字符串**，因此布尔值/数字/对象**必须**使用 `[prop]` 绑定：
> - 字符串 → `agentId="0Xx..."`，`width="420px"`（普通属性可以）
> - 布尔值 → `[inline]="true"`，`[headerEnabled]="false"`（**不是**裸 `inline`，它会产生字符串 `""`）
> - 数字 → `[width]="420"`
> - 对象 → `[styleTokens]="{ headerBlockBackground: '#0176d3' }"`

**完成前验证（Angular）：**

- [ ] 每个非字符串输入（布尔值/数字/对象）都使用 `[prop]` 绑定——没有裸 `inline`/`headerEnabled` 属性。
- [ ] `AgentforceConversationClientComponent` 在主机组件的 `@Component({ imports: [...] })` 数组中注册（没有它，元素将不会渲染）。

#### 4b — 更新现有

1. 读取步骤1中标识的文件。
2. 定位现有元素 (`<AgentforceConversationClient ... />` 对于React，`<app-agentforce-conversation-client ...>` 对于Angular)。
3. 应用**仅**用户请求的更改。规则：
   - **添加**用户请求的新属性。
   - **更改**用户请求更新的属性值。
   - **保留**用户未提及的每个属性和值——不要删除、重新排序或重新格式化它们。
   - **永远**不要删除组件并重新创建它。
4. 如果步骤2被触发（交叉检查或新选择）并解析了新的 agent ID，请用新的值替换现有的 agentId。
5. 如果当前 `agentId` 已有效且用户没有要求更改它，并且步骤2确认它是活动的，则保持原样。

#### 步骤4后的错误处理

如果用户在组件设置后报告错误（例如，“它不起作用”、“我看到错误”），转到步骤2以验证配置的 agentId 是否与组织匹配。交叉检查代理是否处于活动状态、存在并属于连接的组织。

### 步骤5：配置属性

**可用属性/输入（两个框架名称相同；仅绑定语法不同——参见步骤4a中的Angular规则）：**

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
<!-- Angular — 布尔值输入需要 [ ] 绑定 -->
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

**样式规则（强制）：**

- 所有视觉定制（颜色、字体、间距、边框、半径、阴影）**必须**通过 `styleTokens` 属性/输入进行。没有例外。
- **仅**使用下面表格中列出的标记名称。**不要**编造自定义标记名称。
- **永远**不要通过CSS文件、`style`属性、`className`/`class`或包装元素应用样式。这些方法将不起作用，组件将忽略它们。
- Angular：使用 `[styleTokens]="{ ... }"` 绑定（一个对象），而不是裸属性。
- 如果用户请求的视觉更改未映射到下面的标记，请通知他们此更改当前不受当前标记集支持。

有关完整可用样式标记列表，请参阅 `references/style-tokens.md`。

对于复杂模式，请参阅 `references/examples.md` 以获取：

- 侧边栏容器和响应式尺寸
- 暗主题和高级主题组合
- 无标题的内联，计算尺寸
- 完整主机组件示例


**常见错误避免**：请参阅 `references/constraints.md` 以获取：

- 无效属性（containerStyle、style、className）
- 无效样式方法（CSS文件、style标签）
- 不要编辑的文件（实现文件）

## 常见问题

如果组件不显示或身份验证失败，请参阅 `references/troubleshooting.md` 以获取：

- 代理激活和部署
- 本地主机受信任域
- Cookie限制设置

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/agent-id-resolution.md` | 步骤2 — SOQL查询结构、响应格式、激活路径、手动查找 |
| `references/style-tokens.md` | 步骤5 — 完整样式标记参考，适用于所有UI区域 |
| `references/examples.md` | 步骤5 — 布局模式、尺寸、主题组合、主机组件示例 |
| `references/constraints.md` | 步骤4 — 无效属性、无效样式方法、不要编辑的文件 |
| `references/troubleshooting.md` | 设置后 — 代理激活、受信任域、Cookie设置 |
