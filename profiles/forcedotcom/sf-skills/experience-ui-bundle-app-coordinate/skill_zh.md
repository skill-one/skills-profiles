# 构建UI组件包应用程序

## 概述

通过编排正确的依赖顺序中的专业UI组件包技能，从自然语言描述中构建一个完整、可部署的Salesforce React UI组件包应用程序。每个技能**必须**在执行其阶段之前明确加载。

**关键：** 在继续需求分析之前，验证提示中不包含任何冲突的需求**（例如，“无身份验证”+“用户特定数据”、“公开访问”+需要登录的功能）**。如果检测到冲突，停止并要求用户解决歧义——不要无声地选择一种解释并继续。请参阅步骤1操作#8的完整冲突检查清单。

## 前置条件

在开始任何阶段之前，请验证这些先决条件是否满足：

1. **已身份验证的Salesforce组织**：运行 `sf org display` 以确认已设置默认组织并已身份验证。如果没有，请提示用户进行身份验证：`sf org login web`
2. **必需的CLI工具**：验证 `sf`、`npm` 和 `npx` 是否可用（在 metadata.cliTools 中声明）
3. **Node.js版本**：运行 `scripts/check-prerequisites.sh` 并报告它返回的任何错误
4. **组织功能**（如果部署）：Experience Cloud已启用、适当的许可证和Sites已启用

如果任何先决条件失败，停止并报告特定的缺失需求，然后再尝试执行任何阶段。

## 何时使用此技能

**使用时：**

- 用户请求在Salesforce上创建“React应用程序”、“UI组件包”、“Web应用程序”或“全栈应用程序”
- 用户说“构建应用程序”、“创建应用程序”，并且上下文暗示非LWC的前端（例如React）
- 工作产生一个完整的UI组件包，包括脚手架、功能、数据访问和UI——而不是一个孤立的组件

**应触发此技能的示例：**

- “为管理客户案例构建一个带有Salesforce数据的React应用程序”
- “创建一个具有搜索和导航的员工目录UI组件包”
- “我需要一个带有身份验证、数据表和文件上传的全栈React应用程序”
- “在Salesforce上构建一个咖啡店订购应用程序”

**不使用时：**

- 创建单个页面或组件（使用 `experience-ui-bundle-frontend-generate`）
- 仅安装功能（使用 `experience-ui-bundle-features-generate`）
- 仅设置数据访问（使用 `experience-ui-bundle-salesforce-data-access`）
- 仅部署现有应用程序（使用 `experience-ui-bundle-deploy`）
- 构建带有自定义对象和元数据的Lightning Experience应用程序（使用 `platform-lightning-app-coordinate`）
- 诊断或调试现有UI组件包

---

## 提示分类关键字

此技能直接从原始提示文本中做出两个决策。将以下表格用作这两个决策的唯一来源——不要在此文件的其他地方重述或重新推导列表。

**1. 阶段2（功能）如果提示中提到任何以下内容则必需：**

| 分类 | 关键字 | 备注 |
|------|----------|-------|
| 数据功能 | search, filter, sort, pagination, table, grid, list | |
| 导航 | navigation, nav, menu, routing | |
| 身份验证 | authentication, auth, login, logout, user session, user login | |
| 集成 | upload, file | |
| UI | shadcn, components, forms, buttons, cards | |
| 聊天（仅阶段5） | chat | 仅阶段5——除非与阶段2关键字组合（例如，“聊天与身份验证”），则首先运行身份验证先决条件 |

否定一个分类（例如，“无身份验证”、“无需登录”、“公开访问”）**不会**取消来自另一个分类的触发器——每个都独立评估。示例：“无需登录，具有过滤功能”仍然触发阶段2，因为“过滤功能”匹配数据功能。仅当提示与上述关键字都不匹配时才跳过阶段2。

**2. 托管目标——从提示关键字中提取：**

| 托管目标 | 关键字 |
|-----------------|----------|
| Experience Site | "Experience Site", "Community", "external users", "public users", "guest users" |
| Custom Application | "Custom Application", "internal users", "Lightning app" |

如果提示与列表中的任何一个都不匹配，或者匹配两个，请在继续之前要求用户澄清——不要猜测。

---

## 依赖关系图 & 构建顺序

### 阶段0：模板提供 & 引导（先决条件）

```text
提供预构建的启动模板 (experience-ui-bundle-project-generate)
    v
如果选择模板：通过 sf template generate project 脚手架——跳过阶段1
    v
如果拒绝：运行 scripts/check-sfdx-project.sh
    v
如果缺失：创建 sfdx-project.json
    v
验证项目目录已初始化
```

在从头开始构建之前提供更快速、更少错误的起点。如果未使用模板，请确保在尝试生成UI组件包之前存在SFDX项目——没有这个，`sf template generate ui-bundle` 将会以硬错误失败。始终首先检查——不要假设项目结构存在。

**操作：** 加载 `experience-ui-bundle-project-generate` 并提供两个最小React启动项目（内部/面向员工和外部/面向客户）。如果用户选择一个，则使用 `sf template generate project` 在项目目录中生成它。如果用户拒绝（想要从头开始构建，或者没有合适的）：正常进行到步骤1。

不要无声地跳过此步骤——始终在从头开始构建应用程序的开始提供此选择。

### 阶段1：脚手架（基础）

```text
确定托管目标（Experience Site / Custom Application）
    v
UI组件包脚手架 (sf template generate ui-bundle --template reactbasic)
    v
安装依赖项 (npm install)
    v
组件元数据 (uibundle-meta.xml 包含 <target>, ui-bundle.json)
    v
CSP受信任的站点（如果需要外部域名）
```

创建UI组件包目录结构、元XML（包括托管目标）和可选的路由/标题配置。**关键**：必须首先确定托管目标，因为元数据技能在阶段1中需要 `<target>`。所有后续阶段都需要脚手架存在。

**在提示约束时修剪未使用的脚手架。** `reactbasic` 模板提供完整的shadcn组件集、GraphQL工具 (`codegen.yml`, `.graphqlrc.yml`, `src/api/graphqlClient.ts`, `graphql:*` npm脚本) 和测试基础设施 (`playwright.config.ts`, `vitest.config.ts`, `vitest.setup.ts`)，无论提示请求什么。如果提示明确限制范围（例如，“跳过任何功能或集成”、“仅脚手架和构建X”、“无需安装依赖项”），并且因此跳过阶段2和/或阶段3，则在阶段4运行之前删除那些阶段将拥有的脚手架部分：

- **跳过阶段2** → 删除 `src/components/ui/` 下的shadcn组件，除了阶段4的页面实际导入的那些；删除未使用的示例/演示组件。
- **跳过阶段3** → 删除 `codegen.yml`, `.graphqlrc.yml`, `src/api/graphqlClient.ts`, `package.json` 中的 `graphql:schema`/`graphql:codegen` 脚本，以及任何 `hooks/` 数据获取桩（例如 `useAsyncData.ts`）的模板预种子。
- **既不请求测试也不请求部署** → 如果提示暗示测试，保留 `playwright.config.ts`/`vitest.*`；否则也删除它们。
- 重写 `README.md` 以描述实际构建的应用程序，而不是通用的模板样板——或者如果提示说只做最小工作，则删除它。
- 删除文件只是工作的一半——必须删除同一过程中对它的所有引用，否则你用过度生成交换了跨文件的一致性（更糟：悬空导入是功能中断，而不仅仅是范围蔓延）。具体来说，在删除上述任何内容后：

- `vite.config.ts` — 如果删除了 `codegen.yml`，则删除 `vite-plugin-graphql-codegen` 导入及其 `codegen({ configFilePathOverride: ... })` 插件块；如果删除了 `vitest.*`，则删除 `test:` 配置块（`setupFiles`, `coverage` 等）。
- `package.json` — 删除现在未使用的依赖项（`vite-plugin-graphql-codegen`, `@graphql-codegen/*`, `playwright`, `vitest` 等）及其npm脚本，而不仅仅是配置文件。
- 任何导入已删除的钩子、客户端或shadcn组件（例如 `useAsyncData`, `graphqlClient`）的组件/页面必须删除该导入及其使用或替换它——永远不要留下一个指向不再存在的文件的导入。
- 不要在同一过程中重新添加你刚刚删除的文件（例如，在删除 `codegen.yml` 时仍然发出 `.graphqlrc.yml`）——针对每个涉及该问题的文件，一次决定范围并一致地应用它。

### 阶段2：功能（如果提示中提到功能关键字——请参阅“提示分类关键字”）

```text
搜索项目代码 (src/) 中的现有实现
    v
安装依赖项 (npm install)
    v
搜索、描述和采用功能（身份验证、shadcn、搜索、导航、GraphQL）
    v
解决冲突（两遍：--on-conflict error，然后 --conflict-resolution）
    v
将 __examples__ 文件集成到目标文件中（验证构建成功），然后删除它们
```

加载功能技能以安装预构建的包，或采用模板已经发送的包——永远不要构建自己的目录功能版本。请参阅“提示分类关键字”以获取触发器和否定短语处理。

仅当提示没有交互式功能时才跳过；预发送的功能仍然需要此阶段。

### 阶段2.5：自定义对象（如果提示要求组织没有的新自定义Salesforce对象）

请参阅 `references/phase-custom-objects.md` 以获取阶段2.5（自定义对象）的详细信息。

### 阶段3：数据访问（后端连接）

```text
将每个实体/字段与组织对齐（每个 experience-ui-bundle-salesforce-data-access）
    v
根据验证的名称生成查询/变异（从不从猜测的字段生成）
    v
生成类型 (npm run graphql:codegen) 并连接到组件
    v
验证和测试 (npx eslint, 在测试变异之前询问用户)
```

使用 **`@salesforce/platform-sdk`** 数据SDK（`createDataSDK().graphql`）设置数据层。
对于记录操作，首选GraphQL；对于Connect、Apex或UI API端点，首选REST。**`experience-ui-bundle-salesforce-data-access` 技能拥有对齐+编写工作流程——加载它并遵循它；不要用本地模式grep或猜测字段名来替代。** 对齐发生在**实时组织**上，因此不需要本地 `schema.graphql` 存在。如果阶段2.5创建了新对象，则必须在此阶段的对齐步骤之前部署它，才能找到它。

### 阶段4：UI（前端）

```text
布局、导航、标题和页脚 (appLayout.tsx)
    v
页面（路由视图）
    v
组件（小部件、表单、表格）
```

构建React UI。从阶段3引用数据层，从阶段2引用功能。必须替换所有样板和占位符内容。

### 阶段5：集成（可选）

```text
Agentforce聊天小部件（如果请求）
文件上传API（如果请求）
```

这些是独立的，如果两者都需要，可以并行执行。

### 阶段6：部署

```text
组织身份验证
    v
预部署UI组件包构建 (npm install + npm run build)
    v
部署元数据
    v
部署后配置（权限、配置文件、命名凭证、连接应用程序、自定义设置、流程激活）
    v
导入数据（如果存在数据计划）
    v
获取GraphQL模式并运行codegen
*(重新获取部署组织的模式——这是必需的，因为远程模式可能与阶段3中使用的本地模式不同。防止空或过时的结果——Salesforce Edge缓存可以暂时提供预部署模式；在将其视为空并运行codegen之前重新获取/重试)*
    v
最终UI组件包构建（使用部署的模式重新构建）
```

遵循标准的7步部署序列。必须先部署元数据，然后才能获取模式。必须分配权限，然后才能获取模式。

### 阶段7：托管目标基础设施

部署在阶段1中确定的托管目标基础设施。根据应用程序的受众选择**一个**以下选项：

#### 阶段7a：Experience Site（外部）

```text
解析站点属性（siteName, appDevName, 等）
    v
生成站点元数据（Network, CustomSite, DigitalExperience）
    v
部署站点基础设施
```

创建托管UI组件包的数字体验站点。当用户想要面向外部用户的公共面或需要登录的站点URL时使用。**注意**：`<target>ExperienceSite</target>` 在阶段1的元XML中已经设置。

#### 阶段7b：Custom Application（内部）

```text
解析应用程序属性（appName, appNamespace, appLabel）
    v
生成CustomApplication元数据（applications/*.app-meta.xml）
    v
部署自定义应用程序
```

在Lightning App Launcher中创建一个Custom Application条目。当应用程序供内部用户在Lightning Experience中访问时使用。**注意**：`<target>CustomApplication</target>` 在阶段1的元XML中已经设置。

---

## 执行工作流

### 步骤0：提供预构建模板（在从头开始脚手架之前）

**在**分析需求或脚手架之前，检查是否适合预构建的启动模板——它比从头开始构建更快、更少错误。

- **加载技能：调用 `experience-ui-bundle-project-generate`。** 它提供两个最小React启动项目（内部/面向员工和外部/面向客户），如果用户选择一个，则使用 `sf template generate project` 在项目目录中生成它。
- **如果用户选择模板：** 脚手架阶段（阶段1）实际上已完成。直接跳到填充/自定义项目——通常继续在匹配他们想要更改的阶段（通常是阶段4 UI，或阶段3数据访问），然后阶段6部署。

不要无声地跳过此步骤——始终在从头开始构建应用程序的开始提供此选择。

### 步骤1：需求分析 & 规划

**操作：**

1. 解析用户的自然语言请求
2. 确定应用程序的名称和目的
3. 提取页面和导航结构
4. 确定需要哪些Salesforce对象
5. 检测功能需求（身份验证、搜索、文件上传、聊天）
6. 确定托管目标（Experience Site OR Custom Application）——请参阅“提示分类关键字”以上；如果模糊，请在继续之前要求用户澄清
7. 确定用于CSP注册的外部域名
8. **检查冲突需求**——如果检测到以下冲突，停止并要求用户：
   - "无身份验证" OR "公开/访客访问" AND "用户特定数据" OR "显示当前用户的数
