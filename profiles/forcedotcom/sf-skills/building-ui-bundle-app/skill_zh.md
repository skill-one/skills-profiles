# 构建一个 UI Bundle 应用

## 概述

通过编排专门的 UI Bundle 技能，并按照正确的依赖顺序执行，从自然语言描述中构建一个完整的、可部署的 Salesforce React UI Bundle 应用。每个技能**必须**在执行其阶段之前显式加载。

## 使用此技能的场景

**使用场景：**

- 用户在 Salesforce 上请求 "React 应用"、"UI Bundle"、"Web 应用" 或 "全栈应用"
- 用户说 "构建一个应用"、"创建一个应用程序"，并且上下文暗示非 LWC 基的前端（例如 React）
- 工作成果是一个包含脚手架、功能、数据访问和 UI 的完整 UI Bundle，而不是一个孤立的单一组件

**应触发此技能的示例：**

- "为管理 Salesforce 数据构建一个 React 应用"
- "创建一个具有搜索和导航功能的员工目录 UI Bundle"
- "我需要一个带有身份验证、数据表格和文件上传的全栈 React 应用"
- "在 Salesforce 上构建一个咖啡店订购应用"

**不使用场景：**

- 创建单个页面或组件（使用 `building-ui-bundle-frontend`）
- 仅安装功能（使用 `generating-ui-bundle-features`）
- 仅设置数据访问（使用 `using-ui-bundle-salesforce-data`）
- 仅部署现有应用（使用 `deploying-ui-bundle`）
- 构建带有自定义对象和元数据的 Lightning Experience 应用（使用 `generating-lightning-app`）
- 排错或调试现有 UI Bundle

---

## 依赖关系图与构建顺序

### 第一阶段：脚手架（基础）

```
UI Bundle 脚手架 (sf template generate ui-bundle)
    v
安装依赖项 (npm install)
    v
Bundle 元数据 (uibundle-meta.xml, ui-bundle.json)
    v
CSP 受信任站点 (如果需要外部域名)
```

创建 UI Bundle 目录结构、meta XML 和可选的路由/标题配置。所有后续阶段都需要脚手架存在。

### 第二阶段：功能（可选）

```
搜索项目代码 (src/) 中的现有实现
    v
安装依赖项 (npm install)
    v
搜索、描述和安装功能 (身份验证、shadcn、搜索、导航、GraphQL)
    v
解决冲突 (两阶段：--on-conflict error，然后 --conflict-resolution)
    v
将 __example__ 文件集成到目标文件中，然后删除它们
```

安装预构建的、经过测试的功能包。如果应用不需要预构建的功能，则跳过。始终在从头构建之前检查现有功能。功能提供了 UI 组件构建的基础。

### 第三阶段：数据访问（后端连接）

```
获取模式 (npm run graphql:schema)
    v
查找实体模式 (graphql-search.sh，最多 2 次运行)
    v
生成查询/变异 (使用验证的字段名，所有记录字段上的 @optional)
    v
验证和测试 (npx eslint，在测试变异之前询问用户)
```

使用 `@salesforce/sdk-data` 设置数据层。推荐使用 GraphQL 进行记录操作；使用 REST 进行 Connect、Apex 或 UI API 端点。

### 第四阶段：UI（前端）

```
布局、导航、标题和页脚 (appLayout.tsx)
    v
页面 (路由视图)
    v
组件 (小部件、表单、表格)
```

构建 React UI。从第三阶段引用数据层，从第二阶段引用功能。必须替换所有样板和占位符内容。

### 第五阶段：集成（可选）

```
Agentforce 聊天小部件（如果请求）
文件上传 API（如果请求）
```

这些是独立的，如果两者都需要，可以并行执行。

### 第六阶段：部署

```
组织身份验证
    v
预部署 UI Bundle 构建 (npm install + npm run build)
    v
部署元数据
    v
部署后配置 (权限、配置文件、命名凭证、连接应用、自定义设置、流程激活)
    v
导入数据（如果存在数据计划）
    v
获取 GraphQL 模式并运行 codegen
*(重新获取已部署组织的模式 -- 必须执行，因为远程模式可能与第三阶段使用的本地模式不同)*
    v
最终 UI Bundle 构建 (使用已部署的模式重新构建)
```

遵循标准的 7 步部署序列。必须先部署元数据再获取模式。必须先分配权限再获取模式。

### 第七阶段：托管目标

根据应用的受众选择**一个**以下选项：

#### 第七阶段 a：体验站点（外部）

```
解析站点属性 (siteName, appDevName, 等.)
    v
生成站点元数据 (Network, CustomSite, DigitalExperience)
    v
部署站点基础设施
```

创建托管 UI Bundle 的 Digital Experience 站点。当用户需要为外部用户提供一个公共面或经过身份验证的站点 URL 时使用。

#### 第七阶段 b：自定义应用（内部）

```
解析应用属性 (appName, appNamespace, appLabel)
    v
生成 CustomApplication 元数据 (applications/*.app-meta.xml)
    v
将 <target>CustomApplication</target> 添加到 .uibundle-meta.xml
    v
部署自定义应用
```

在 Lightning App Launcher 中创建一个 Custom Application 条目。当应用是供内部用户在 Lightning Experience 中访问时使用。

---

## 执行工作流

### 第一步：需求分析与规划

**操作：**

1. 解析用户的自然语言请求
2. 确定应用名称和目的
3. 提取页面和导航结构
4. 确定需要的数据实体和 Salesforce 对象
5. 检测功能需求（身份验证、搜索、文件上传、聊天）
6. 确定是否需要体验站点
7. 确定用于 CSP 注册的外部域名

**输出：构建计划**

```
UI Bundle 应用构建计划：[应用名称]

脚手架：
- 应用名称：[PascalCase 名称]
- 路由：[SPA 重写、尾随斜杠配置]
- 外部域名：[需要 CSP 注册的域名]

功能：
- [要安装的功能列表：身份验证、shadcn、搜索、导航等]

数据访问：
- 对象：[要查询/变异的 Salesforce 对象]
- 查询：[需要的 GraphQL 查询列表]
- REST 端点：[Apex REST 或 Connect API 调用，如果有]

UI：
- 布局：[应用外壳/导航的描述]
- 页面：[带路由的页面列表]
- 组件：[每个页面的关键组件]
- 设计方向：[美学/风格意图]

集成（如果适用）：
- Agentforce 聊天：[是/否，如果知道代理 ID]
- 文件上传：[是/否，记录链接模式]

部署：
- 目标组织：[如果知道，组织别名]
- 托管目标：[体验站点 / 自定义应用 / 无]

技能加载顺序：
1. generating-ui-bundle-metadata
2. generating-ui-bundle-features (如果需要功能)
3. using-ui-bundle-salesforce-data (如果需要数据访问)
4. building-ui-bundle-frontend
5a. implementing-ui-bundle-agentforce-conversation-client (如果请求聊天)
5b. implementing-ui-bundle-file-upload (如果请求文件上传)
6. deploying-ui-bundle
7a. generating-ui-bundle-site (如果请求体验站点 -- 外部用户)
7b. generating-ui-bundle-custom-app (如果请求自定义应用 -- 内部用户)
```

### 第二步：按阶段执行

按顺序执行每个阶段。在进入下一个阶段之前完成阶段内的所有步骤。对于每个阶段：

| 步骤 | 要做什么 | 为什么 |
|------|-----------|-----|
| **1. 加载技能** | 调用此阶段的技能（例如，通过 Skill 工具） | 提供当前规则、模式、约束和实施指南 |
| **2. 执行** | 按加载的技能的工作流程生成代码/配置 | 技能定义了如何正确地做工作 |
| **3. 验证** | 从 UI Bundle 目录运行Lint和构建 | 在进入下一个阶段之前捕获错误 |
| **4. 检查点** | 在继续之前确认阶段完成 | 确保满足下一个阶段的依赖关系 |

**不要跳过步骤 1（加载技能）。** 即使你记得技能的内容，技能也在不断发展。始终加载当前版本。

---

**第一阶段 -- 脚手架**
- 1. 加载技能：调用 `generating-ui-bundle-metadata`
- 2. 执行：运行 `sf template generate ui-bundle`，安装依赖项 (`npm install`)，配置 meta XML、ui-bundle.json 和 CSP 受信任站点
- 3. 验证：确认目录结构和元数据文件存在
- 4. 检查点：UI Bundle 脚手架准备就绪 -- 进入第二阶段

**第二阶段 -- 功能**（如果不需要预构建功能，则跳过）
- 1. 加载技能：调用 `generating-ui-bundle-features`
- 2. 执行：安装依赖项，搜索和安装功能，集成示例文件
- 3. 验证：运行 `npm run build` 以确认功能干净地集成
- 4. 检查点：功能安装完毕 -- 进入第三阶段

**第三阶段 -- 数据访问**（如果不需要 Salesforce 数据，则跳过）
- 1. 加载技能：调用 `using-ui-bundle-salesforce-data`
- 2. 执行：获取模式，查找实体，生成查询/变异，连接到组件
- 3. 验证：在包含 GraphQL 查询的文件上运行 `npx eslint`
- 4. 检查点：数据层准备就绪 -- 进入第四阶段

**第四阶段 -- UI**
- 1. 加载技能：调用 `building-ui-bundle-frontend`
- 2. 执行：构建布局、页面、组件、导航。替换所有样板。
- 3. 验证：运行Lint和构建 -- 需要 0 个错误
- 4. 检查点：UI 完成 -- 进入第五阶段

**第五阶段 -- 集成**（如果未请求，则跳过）
- 1. 加载技能：调用 `implementing-ui-bundle-agentforce-conversation-client` (5a) 和/或 `implementing-ui-bundle-file-upload` (5b)。如果两者都需要，它们是独立的，可以并行执行。
- 2. 执行：按照每个技能的工作流程添加集成
- 3. 验证：运行Lint和构建
- 4. 检查点：集成完成 -- 进入第六阶段

**第六阶段 -- 部署**
- 1. 加载技能：调用 `deploying-ui-bundle`
- 2. 执行：遵循 7 步部署序列（身份验证、构建、部署、权限、数据、模式、最终构建）
- 3. 验证：确认部署成功且应用可访问
- 4. 检查点：应用已部署 -- 如果需要，进入第七阶段

**第七阶段 a -- 体验站点**（如果未请求或选择自定义应用，则跳过）
- 1. 加载技能：调用 `generating-ui-bundle-site`
- 2. 执行：解析属性，生成站点元数据，部署
- 3. 验证：确认站点 URL 可访问
- 4. 检查点：站点上线 -- 构建完成

**第七阶段 b -- 自定义应用**（如果未请求或选择体验站点，则跳过）
- 1. 加载技能：调用 `generating-ui-bundle-custom-app`
- 2. 执行：解析应用属性，生成 CustomApplication 元数据，将 CustomApplication 目标添加到 meta XML
- 3. 验证：确认应用出现在 App Launcher 中
- 4. 检查点：应用注册完毕 -- 构建完成

### 第三步：最终总结

所有阶段完成后，提供构建摘要：

```
UI Bundle 应用构建完成：[应用名称]

已完成的阶段：
[x] 第一阶段：脚手架 -- [应用名称] UI Bundle 创建
[x] 第二阶段：功能 -- [已安装的功能列表，或 "跳过"]
[x] 第三阶段：数据访问 -- [连接的实体列表]
[x] 第四阶段：UI -- [页面数] 页面，[组件数] 组件
[x] 第五阶段：集成 -- [列表或 "无"]
[x] 第六阶段：部署 -- 部署到 [组织]
[x] 第七阶段：托管目标 -- [体验站点 URL / 自定义应用名称 / "跳过"]

生成的文件：
[列出关键文件及其路径]

下一步：
[用户应采取的任何手动步骤]
```

---

## 验证

在将构建呈现为完成之前，验证：

- [ ] **脚手架存在**：UI Bundle 目录，包含有效的 meta XML 和 ui-bundle.json
- [ ] **依赖项已安装**：`node_modules/` 存在，`package.json` 包含预期包
- [ ] **构建通过**：`npm run build` 生成 `dist/` 且无错误
- [ ] **Lint 通过**：`npx eslint src/` 报告 0 个错误
- [ ] **无样板**：所有占位符文本、默认标题和模板内容已替换
- [ ] **导航正常**：`appLayout.tsx` 包含与创建的页面匹配的真实导航项
- [ ] **数据层连接**：组件使用 `@salesforce/sdk-data`（如果执行了数据访问阶段）
- [ ] **CSP 注册**：所有外部域名都有 CSP 受信任站点元数据（如果适用）

---

## 错误处理

### 类别 1：停止并询问用户

- 应用目的过于模糊，无法确定页面或数据需求
- 用户想要冲突的功能（例如，“无身份验证” + “显示用户特定数据”）
- 目标组织未知且请求部署

### 类别 2：记录警告，继续

- 功能安装存在轻微冲突（解决并继续）
- 可选集成设置遇到非阻塞问题
- 构建有非错误警告

---

## 最佳实践

### 1. 始终遵循阶段顺序

不要在安装功能之前构建 UI。不要在构建之前部署。依赖关系是严格的。

### 2. 替换所有样板

每个生成的应用都必须感觉是专门构建的。用真实的应用特定文本和品牌替换 "React 应用" 标题、"Vite + React" 占位符和所有默认内容。

### 3. 带意图设计

遵循 `building-ui-bundle-frontend` 提供的设计思维和前端美学指导。每个应用都应该有一个清晰的可视方向 -- 不是通用的默认值。
