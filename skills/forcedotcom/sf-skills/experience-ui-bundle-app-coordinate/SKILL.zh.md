---
name: experience-ui-bundle-app-coordinate
description: 必须在用户想要构建、创建或生成 React 应用、React 应用程序、Web 应用程序、单页应用程序（SPA）或前端应用程序时激活——即使项目文件尚未存在。当项目包含 uiBundles/*/src/ 目录或 sfdx-project.json，并且提示创建、构建、构建或从头开始生成新应用程序、网站或页面时，也必须激活——即使提示还描述了视觉样式。当任务跨越多个 ui-bundle 技能时，也必须激活。在端到端构建完整应用程序时使用此技能。不应用于具有自定义对象的 Lightning Experience 应用程序（请使用 platform-lightning-app-coordinate）。不应用于对现有页面的单一关注点编辑（请使用 experience-ui-bundle-frontend-generate）。
---

# 构建一个 UI Bundle 应用

## 概述

通过编排专门的 UI Bundle 技能，并按照正确的依赖顺序执行，从自然语言描述中构建一个完整的、可部署的 Salesforce React UI Bundle 应用。每个技能**必须**在执行其阶段之前显式加载。

**关键：在进行需求分析之前，验证提示中不包含任何冲突的需求**（例如，“无身份验证” + “用户特定数据”、“公开访问” + 需要登录的功能）。如果检测到冲突，请停止并要求用户解决歧义——不要无声地选择一种解释并继续进行。请参阅步骤 1 操作 #8 以获取完整的冲突检查清单。

## 前置条件

在开始任何阶段之前，请验证以下先决条件是否满足：

1. **已身份验证的 Salesforce 组织**：运行 `sf org display` 以确认已设置默认组织并已进行身份验证。如果没有，请提示用户进行身份验证：`sf org login web`
2. **所需的 CLI 工具**：验证 `sf`、`npm` 和 `npx` 是否可用（在 metadata.cliTools 中声明）
3. **Node.js 版本**：运行 `scripts/check-prerequisites.sh` 并报告其返回的任何错误
4. **组织功能**（如果部署）：Experience Cloud 已启用、适当的许可证和 Sites 已启用

如果任何先决条件失败，请停止并报告特定的缺失需求，然后再尝试执行任何阶段。

## 何时使用此技能

**使用场景：**

- 用户在 Salesforce 上请求“React 应用”、“UI Bundle”、“Web 应用”或“全栈应用”
- 用户说“构建一个应用”、“创建一个应用程序”，并且上下文暗示非 LWC 基于的前端（例如 React）
- 工作成果是一个完整的 UI Bundle，包含脚手架、功能、数据访问和 UI——而不是一个孤立的单个组件

**应触发此技能的示例：**

- “为管理 Salesforce 数据构建一个 React 应用来处理客户案例”
- “创建一个具有搜索和导航功能的员工目录 UI Bundle”
- “我需要一个具有身份验证、数据表格和文件上传的全栈 React 应用”
- “在 Salesforce 上构建一个咖啡店订购应用”

**不使用场景：**

- 创建单个页面或组件（使用 `experience-ui-bundle-frontend-generate`）
- 仅安装功能（使用 `experience-ui-bundle-features-generate`）
- 仅设置数据访问（使用 `experience-ui-bundle-salesforce-data-access`）
- 仅部署现有应用（使用 `experience-ui-bundle-deploy`）
- 构建具有自定义对象和元数据的 Lightning Experience 应用（使用 `platform-lightning-app-coordinate`）
- 故障排除或调试现有的 UI Bundle

---

## 提示分类关键词

此技能直接从原始提示文本中做出两个决策。将以下表格用作这两个决策的唯一来源——不要在此文件的其他地方重述或重新推导列表。

**1. 如果提示中提到任何以下关键词，则必须执行阶段 2（功能）：**

| 类别 | 关键词 | 备注 |
|------|--------|------|
| 数据功能 | search、filter、sort、pagination、table、grid、list | |
| 导航 | navigation、nav、menu、routing | |
| 身份验证 | authentication、auth、login、logout、user session、user login | |
| 集成 | upload、file | |
| UI | shadcn、components、forms、buttons、cards | |
| 聊天（仅阶段 5） | chat | 仅阶段 5——除非与阶段 2 的关键词组合（例如，“具有身份验证的聊天”），否则首先运行身份验证先决条件 |

否定一个类别（例如，“无身份验证”、“无需登录”、“公开访问”）**不会**取消来自另一个类别的触发器——每个触发器都是独立评估的。示例：“无需登录，具有过滤功能”仍然会触发阶段 2，因为“过滤功能”与数据功能匹配。仅当提示与上述关键词列表中的任何一个都不匹配时，才跳过阶段 2。

**2. 托管目标——从提示关键词中提取：**

| 托管目标 | 关键词 |
|----------|--------|
| Experience Site | "Experience Site"、"Community"、"外部用户"、"公共用户"、"访客用户" |
| Custom Application | "Custom Application"、"内部用户"、"Lightning app" |

如果提示与列表中的任何一个都不匹配，或者匹配两个，请在继续之前要求用户澄清——不要猜测。

---

## 依赖关系图和构建顺序

### 阶段 0：模板提供和引导（先决条件）

```text
提供预构建的启动模板（experience-ui-bundle-project-generate）
    v
如果选择模板：通过 sf template generate project 进行脚手架搭建——跳过阶段 1
    v
如果拒绝：运行 scripts/check-sfdx-project.sh
    v
如果缺失：创建 sfdx-project.json
    v
验证项目目录已初始化
```

在从头开始构建之前提供更快速、更少错误的起点。如果未使用模板，请确保在尝试生成 UI Bundle 之前存在 SFDX 项目——如果没有，`sf template generate ui-bundle` 将会以硬错误失败。始终首先检查——不要假设项目结构存在。

**操作：** 加载 `experience-ui-bundle-project-generate` 并提供两个启动模板。如果拒绝，运行 `scripts/check-sfdx-project.sh` 并报告其返回的任何错误。如果脚本报告错误，请在继续之前创建缺失的 `sfdx-project.json`。

### 阶段 1：脚手架（基础）

```text
确定托管目标（Experience Site / Custom Application）
    v
UI Bundle 脚手架（sf template generate ui-bundle --template reactbasic）
    v
安装依赖项（npm install）
    v
Bundle 元数据（uibundle-meta.xml 包含 <target>、ui-bundle.json）
    v
CSP 受信任的站点（如果需要外部域名）
```

创建 UI Bundle 目录结构、元 XML（包括托管目标）和可选的路由/标题配置。**关键**：必须首先确定托管目标，因为元数据技能在阶段 1 需要在 `<target>` 中包含托管目标。所有后续阶段都需要脚手架存在。

**当提示具有约束性时，修剪未使用的脚手架。** `reactbasic` 模板提供完整的 shadcn 组件集、GraphQL 工具（`codegen.yml`、`.graphqlrc.yml`、`src/api/graphqlClient.ts`、`graphql:*` npm 脚本）和测试基础设施（`playwright.config.ts`、`vitest.config.ts`、`vitest.setup.ts`），无论提示请求了什么。如果提示明确限制范围（例如，“跳过任何功能或集成”、“仅脚手架和构建 X”、“无需安装依赖项”），并且因此跳过阶段 2 和/或阶段 3，请在阶段 4 运行之前删除那些阶段将拥有的脚手架部分：

- **跳过阶段 2** → 删除 `src/components/ui/` 下除阶段 4 的页面实际导入的 shadcn 组件之外的组件；删除未使用的示例/演示组件。
- **跳过阶段 3** → 删除 `codegen.yml`、`.graphqlrc.yml`、`src/api/graphqlClient.ts`、`package.json` 中的 `graphql:schema`/`graphql:codegen` 脚本，以及任何 `hooks/` 数据获取占位符（例如 `useAsyncData.ts`）的模板预置。
- **既不请求测试也不部署** → 如果提示暗示测试，保留 `playwright.config.ts`/`vitest.*`；否则也删除它们。
- 重写 `README.md` 以描述实际构建的应用，而不是通用的模板样板——或者如果提示仅进行最小工作量，则删除它。
- 删除文件只是工作的一半——必须删除同一过程中对它的所有引用，否则你用过度生成换取了跨文件的一致性问题（更糟：悬空导入是功能错误，而不仅仅是范围蔓延）。具体来说，在删除上述任何内容后：

  - `vite.config.ts` — 如果删除了 `codegen.yml`，则删除 `vite-plugin-graphql-codegen` 导入及其 `codegen({ configFilePathOverride: ... })` 插件块；如果删除了 `vitest.*`，则删除 `test:` 配置块（`setupFiles`、`coverage` 等）。
  - `package.json` — 删除现在未使用的依赖项（`vite-plugin-graphql-codegen`、`@graphql-codegen/*`、`playwright`、`vitest` 等）及其 npm 脚本，而不仅仅是配置文件。
  - 任何导入已删除的钩子、客户端或 shadcn 组件（例如 `useAsyncData`、`graphqlClient`）的组件/页面必须删除或替换该导入及其使用——永远不要留下指向不再存在的文件的导入。
  - 不要在同一过程中重新添加你刚刚删除的文件（例如，在删除 `codegen.yml` 时仍然发出 `.graphqlrc.yml`）——针对每个问题一次确定范围并一致地应用于所有涉及该问题的文件。
  - 在完成阶段 4 之前，对每个已删除的文件运行 `scripts/check-dangling-refs.sh <deleted-basename>` 并报告其返回的任何错误。

### 阶段 2：功能（如果提示提到功能关键词——请参阅“提示分类关键词”）

```text
搜索项目代码（src/）以查找现有实现
    v
安装依赖项（npm install）
    v
搜索、描述并安装功能（身份验证、shadcn、搜索、导航、GraphQL）
    v
解决冲突（两阶段：--on-conflict 错误，然后 --conflict-resolution）
    v
将 __examples__ 文件集成到目标文件中（验证构建成功），然后删除它们
```

安装预构建的、经过测试的功能包。请参阅“提示分类关键词”中的完整触发关键词列表和否定短语处理——这些功能为 UI 组件构建提供基础。

仅当应用是一个真正的“你好世界”且没有交互功能（没有任何触发关键词）时，才跳过此阶段。

### 阶段 2.5：自定义对象（如果提示要求组织没有的新自定义 Salesforce 对象）

请参阅 `references/phase-custom-objects.md` 以获取阶段 2.5（自定义对象）的详细信息。

### 阶段 3：数据访问（后端连接）

```text
将每个实体/字段与组织进行关联（每个 experience-ui-bundle-salesforce-data-access）
    v
根据验证的名称生成查询/变异（从不猜测字段名称）
    v
生成类型（npm run graphql:codegen）并将其连接到组件
    v
验证和测试（npx eslint，在测试变异之前询问用户）
```

使用 `@salesforce/platform-sdk` 数据 SDK（`createDataSDK().graphql`）设置数据层。
对于记录操作，首选 GraphQL；对于 Connect、Apex 或 UI API 端点，首选 REST。**`experience-ui-bundle-salesforce-data-access` 技能负责关联+编写工作流程——加载它并遵循它；不要用本地模式的 grep 或猜测字段名称来替代。** 关联针对**实时组织**进行，因此不需要本地 `schema.graphql` 存在。如果阶段 2.5 创建了新对象，则必须在此阶段的关联步骤之前部署它，以便关联步骤可以发现它。

### 阶段 4：UI（前端）

```text
布局、导航、标题和页脚（appLayout.tsx）
    v
页面（路由视图）
    v
组件（小部件、表单、表格）
```

构建 React UI。从阶段 3 引用数据层，从阶段 2 引用功能。必须替换所有样板和占位符内容。

### 阶段 5：集成（可选）

```text
Agentforce 聊天小部件（如果请求）
文件上传 API（如果请求）
```

这些是独立的，如果两者都需要，可以并行执行。

### 阶段 6：部署

```text
组织身份验证
    v
预部署 UI Bundle 构建（npm install + npm run build）
    v
部署元数据
    v
部署后配置（权限、配置文件、命名凭证、连接应用、自定义设置、流程激活）
    v
导入数据（如果存在数据计划）
    v
获取 GraphQL 模式并运行 codegen
*(重新获取已部署组织的模式——这是必需的，因为远程模式可能与阶段 3 中使用的本地模式不同。防止空或过时的结果——Salesforce Edge 缓存可能会短暂提供预部署模式；在信任它为空并运行 codegen 之前重新获取/重试)*
    v
最终 UI Bundle 构建（使用部署的模式重新构建）
```

遵循标准的 7 步骤部署序列。必须先部署元数据，然后才能获取模式。必须先分配权限，然后才能获取模式。

### 阶段 7：托管目标基础设施

部署阶段 1 中确定的托管目标基础设施。根据应用的受众选择**一个**以下选项：

#### 阶段 7a：Experience Site（外部）

```text
解析站点属性（siteName、appDevName、等）
    v
生成站点元数据（Network、CustomSite、DigitalExperience）
    v
部署站点基础设施
```

创建托管 UI Bundle 的 Digital Experience 站点。用于用户想要为外部用户提供公共面或经过身份验证的站点 URL。**注意**：`<target>ExperienceSite</target>` 已经在阶段 1 的元 XML 中设置。

#### 阶段 7b：Custom Application（内部）

```text
解析应用属性（appName、appNamespace、appLabel）
    v
生成 CustomApplication 元数据（applications/*.app-meta.xml）
    v
部署自定义应用
```

在 Lightning App Launcher 中创建一个 Custom Application 条目。用于应用是供内部用户在 Lightning Experience 中访问的。**注意**：`<target>CustomApplication</target>` 已经在阶段 1 的元 XML 中设置。

---

## 执行工作流

### 步骤 0：提供预构建模板（在从头开始脚手架之前）

**在**分析需求或脚手架之前，检查是否适合预构建的启动模板——它比从头开始构建更快、更不容易出错。

- **加载技能：调用 `experience-ui-bundle-project-generate`。** 它提供两个最小的 React 启动项目（内部/面向员工和外部/面向客户），如果用户选择其中一个，则使用 `sf template generate project` 将其生成到项目目录中。
- **如果用户选择模板：** 脚手架阶段（阶段 1）实际上已完成。直接跳转到填充/自定义项目——通常继续在匹配他们想要更改的阶段（通常是阶段 4 UI，或阶段 3 数据访问），然后是阶段 6 部署。
- **如果用户拒绝**（想要从头开始构建，或者没有合适的）：正常进行到步骤 1。

不要无声地跳过此步骤——始终在从头开始构建应用的开头提供此选择。

- [ ] **未检测到冲突需求** — 如果存在冲突（见上文操作 #8），请停止并报告：
  ```text
  ERROR: 检测到冲突需求：
  - [描述具体冲突，例如，"提示要求'无需身份验证'，同时要求'我的案例'视图仅限于当前用户的身份"]
  
  需要解决：请澄清：
  - [具体问题，例如，"应用是否需要登录（移除'无需身份验证'要求），还是所有数据都应公开（移除用户范围视图）？"]
  ```
  **在解决此冲突之前，请勿继续进行构建计划生成或任何阶段执行。**

**输出：构建计划**

```text
UI Bundle 应用构建计划：[应用名称]

框架搭建：
- 应用名称：[PascalCase 名称]
- 托管目标：[体验站点 / 定制应用] **必需**
- 路由：[SPA 重写、尾随斜杠配置]
- 外部域名：[需要 CSP 注册的域名]

功能：
- [要安装的功能列表：认证、shadcn、搜索、导航等]

自定义对象（如适用）：
- 新对象/字段：[列出组织尚未拥有的任何对象及其字段 -- 委托给 platform-custom-object-generate，此处不编写]

数据访问：
- 对象：[要查询/修改的 Salesforce 对象]
- 基础验证：[通过 experience-ui-bundle-salesforce-data-access 在编写前验证每个对象及其字段与组织 — 确认对象/字段列表，而非假设正确的名称]
- 查询：[基于验证的名称编写 GraphQL 查询]
- REST 端点：[仅在 GraphQL/uiapi 真正无法覆盖的情况下使用 — 不仅仅是字段难以验证的回退]

UI：
- 布局：[应用外壳/导航的描述]
- 页面：[带路由的页面列表]
- 组件：[每个页面的关键组件]
- 设计方向：[美学/风格意图]

集成（如适用）：
- Agentforce 聊天：[是/否，如已知则提供代理 ID]
- 文件上传：[是/否，记录链接模式]

部署：
- 目标组织：[如已知则提供组织别名]

技能加载顺序：
0. experience-ui-bundle-project-generate (首先提供预构建模板；如果选择，则跳过阶段 1 的框架搭建；如果拒绝，则运行 Bootstrap 检查以查找现有的 SFDX 项目 — 无需技能加载)
1. experience-ui-bundle-metadata-generate (首先确定托管目标)
2. experience-ui-bundle-features-generate (如果需要功能)
2.5. platform-custom-object-generate (如果提示要求组织没有的自定义 Salesforce 对象 — 必须完成并部署才能进入步骤 3)
3. experience-ui-bundle-salesforce-data-access (如果需要数据访问)
4. experience-ui-bundle-frontend-generate
5a. experience-ui-bundle-agentforce-client-generate (如果请求聊天)
5b. experience-ui-bundle-file-upload-generate (如果请求文件上传)
6. experience-ui-bundle-deploy
7a. experience-ui-bundle-site-generate (如果请求体验站点 — 外部用户)
7b. experience-ui-bundle-custom-app-generate (如果请求定制应用 — 内部用户)
```

### 步骤 2：按阶段执行

按 `references/phase-execution-pattern.md` 中的标准模式顺序执行每个阶段。**关键：加载技能后再执行。** 跳过或重新排序阶段会导致应用损坏。

---

**阶段 0 -- 模板提供 & Bootstrap**
- 加载 `experience-ui-bundle-project-generate`，提供模板。如果选择：跳过阶段 1，继续阶段 4。如果拒绝：运行 `scripts/check-sfdx-project.sh`，如果缺少项目则创建。

**阶段 1 -- 框架搭建**（如果使用阶段 0 的模板则跳过）
- **前提条件**：`scripts/check-sfdx-project.sh` 通过
- 加载 `experience-ui-bundle-metadata-generate`。首先确定托管目标。运行 `sf template generate ui-bundle --template reactbasic`，配置 meta XML 使用 `<target>`。
- **验证后**：`scripts/check-phase-1-complete.sh` 通过

**阶段 2 -- 功能**（如果没有功能关键词则跳过 — 见“提示分类关键词”）
- 加载 `experience-ui-bundle-features-generate`。安装功能，集成示例。使用 `npm run build` 进行验证。

**阶段 2.5 -- 自定义对象**（如果组织已有所有所需对象则跳过）
- 阅读 `references/phase-custom-objects.md` 并遵循执行步骤。

**阶段 3 -- 数据访问**（如果没有 Salesforce 数据则跳过）
- 加载 `experience-ui-bundle-salesforce-data-access`。获取架构，验证实体，生成查询/变异。使用 `npx eslint` 进行验证。

**阶段 4 -- UI**（始终必需）
- **前提条件**：`scripts/check-phase-1-complete.sh` 通过
- 加载 `experience-ui-bundle-frontend-generate`。构建布局、页面、组件。替换所有样板内容。
- **验证后**：`scripts/check-phase-4-complete.sh` 通过
- **关键**：阶段 4 生成实际的 React UI。切勿跳过。

**阶段 5 -- 集成**（如果未请求则跳过）
- 根据需要加载 `experience-ui-bundle-agentforce-client-generate` (5a) 和/或 `experience-ui-bundle-file-upload-generate` (5b)。

**阶段 6 -- 部署**
- **前提条件**：`scripts/check-phase-6-ready.sh` 通过
- 加载 `experience-ui-bundle-deploy`。遵循 7 步序列。如果可用，优先使用 `scripts/org-setup.mjs`。
- **关键**：防止空架构 — 在代码生成前重试获取 3 次。

**阶段 7a -- 体验站点**（外部用户）
- **触发条件**：`scripts/check-hosting-target.sh` 输出 "ExperienceSite"
- 加载 `experience-ui-bundle-site-generate`。部署站点基础设施。

**阶段 7b -- 定制应用**（内部用户）
- **触发条件**：`scripts/check-hosting-target.sh` 输出 "CustomApplication"
- 加载 `experience-ui-bundle-custom-app-generate`。部署应用元数据。

### 步骤 2.5：阶段完成验证

在继续步骤 3（最终摘要）之前，验证所有必需阶段是否已执行。有关完整的临界/警告检查清单和报告的确切错误/警告文本，请参阅 `references/phase-completion-validation.md`。

### 步骤 3：最终摘要

所有阶段完成后，提供构建摘要：

```text
UI Bundle 应用构建完成：[应用名称]

已完成的阶段：
[x] 阶段 0：模板提供 & Bootstrap -- [使用模板：<名称> / 拒绝；SFDX 项目验证/创建]
[x] 阶段 1：框架搭建 -- [应用名称] UI bundle 已创建，托管目标为 [体验站点 / 定制应用]
[x] 阶段 2：功能 -- [已安装的功能列表，或“跳过”]
[x] 阶段 2.5：自定义对象 -- [已创建和部署的对象/字段列表，或“跳过 — 无需新架构”]
[x] 阶段 3：数据访问 -- [已连接的实体列表]
[x] 阶段 4：UI -- [页面数量] 页面，[组件数量] 组件
[x] 阶段 5：集成 -- [列表或“无”]
[x] 阶段 6：部署 -- 部署到 [组织]
[x] 阶段 7：托管目标 -- [体验站点 URL / 定制应用名称] **（永远不能“跳过” — 阶段 1 需要目标，因此 7a/7b 中恰好有一个始终执行）**

生成的文件：
[列出关键文件及其路径]

下一步：
[用户应采取的任何手动步骤]
```

---

## 验证

在将构建呈现为完成之前，验证：

- [ ] **框架存在**：UI bundle 目录包含有效的 meta XML 和 ui-bundle.json
- [ ] **托管目标已解析并部署**：meta XML 包含 `<target>ExperienceSite</target>` 或 `<target>CustomApplication</target>`（永远不能未设置），并且已生成并部署匹配的阶段 7a 或 7b 基础设施 — 未跳过
- [ ] **依赖项已安装**：`node_modules/` 存在，`package.json` 包含预期包
- [ ] **构建通过**：`npm run build` 生成 `dist/` 且无错误
- [ ] **dist 内容存在**：`dist/` 包含 index.html、JS/CSS 打包文件和资源（而不仅仅是空目录）
- [ ] **Lint 通过**：`npx eslint src/` 报告 0 个错误
- [ ] **无样板内容**：所有占位符文本、默认标题和模板内容均已替换
- [ ] **导航正常**：`appLayout.tsx` 包含与创建的页面匹配的真实导航项
- [ ] **数据层已连接**：组件使用 `@salesforce/platform-sdk` 数据 SDK (`createDataSDK().graphql`)，所有实体/字段均已针对组织进行验证 — 未猜测（如果执行了数据访问阶段）
- [ ] **CSP 注册**：所有外部域名均有 CSP 受信任站点元数据（如适用）

---

## 错误处理

### 类别 1：停止并询问用户

- 应用目的过于模糊，无法确定页面或数据需求
- 用户希望的功能冲突（例如，“无需身份验证” + “显示用户特定数据”）
- 无法确定托管目标（询问：“这是为内部用户（定制应用）还是外部用户（体验站点）？”）
- 目标组织未知且请求部署

### 类别 2：记录警告，继续

- 功能安装存在轻微冲突（解决并继续）
- 可选集成设置遇到非阻塞问题
- 构建有非错误警告

---

## 最佳实践

### 1. 始终遵循阶段顺序

构建 UI 前切勿安装功能。部署前切勿构建。依赖项严格。

### 2. 替换所有样板内容

每个生成的应用都必须感觉是专门构建的。替换“React 应用”标题、“Vite + React”占位符和所有默认内容，使用实际应用特定文本和品牌。

### 3. 带意图设计

遵循 `experience-ui-bundle-frontend-generate` 的设计思维和前端美学指南。每个应用都应有明确的视觉方向 — 而非通用默认值。
