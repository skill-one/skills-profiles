## 何时使用此技能

使用此技能时，您需要：
- 创建闪电应用程序
- 将标签和功能组织成专注的应用程序
- 配置应用程序导航和品牌
- 为对象设置自定义页面布局
- 排查与自定义应用程序相关的部署错误

# CustomApplication (闪电 App) 元数据规范

## 概述

将标签和功能分组，为特定业务流程提供专注用户体验的自定义应用程序（闪电 App）。始终针对闪电体验进行配置。

## 目的
- 将相关功能组织成专注的应用程序
- 为特定用户角色分组标签和组件
- 提供定制的用户体验
- 控制对特定功能和数据的访问
- 使用标准导航进行一般业务应用程序，或使用控制台导航进行需要多标签工作区的专用服务/支持工作流
- 创建专业、带品牌的应用程序标识，具有自定义颜色和品牌
- 使用自定义闪电页面覆盖标准操作以增强用户体验
- 通过配置文件操作覆盖启用特定配置文件的用户体验

## 必须属性

### 核心应用程序属性
- **fullName**：应用程序的 API 名称
- **label**：应用程序的显示名称
- **uiType**：对于现代应用程序始终为 "Lightning"
- **navType**：CRITICAL - 根据用户需求和流程模式选择
    - "Standard"：DEFAULT，用于一般业务应用程序（例如，销售、营销、运营）
    - "Console"：仅当工作流需要同时管理多个记录，并使用分视图或多标签工作区时（例如，客户服务、呼叫中心、支持运营）
- **formFactors**：表单因素数组（["LARGE"] 用于桌面，["SMALL"] 用于移动，或两者）

### 可选属性
- **description**：应用程序目的的简要描述
- **tabs**：要包含的标签数组
- **utilityBar**：Utility Bar 配置的 API 名称
- **brand**：HIGHLY RECOMMENDED - 品牌配置对象（headerColor、shouldOverrideOrgTheme、footerColor）
- **actionOverrides**：当存在自定义记录页面时必须 - 操作覆盖配置（actionName、content、formFactor、type、pageOrSobjectType）
- **profileActionOverrides**：特定配置文件的操作覆盖（actionName、content、formFactor、pageOrSobjectType、type、profile）
- **isNavAutoTempTabsDisabled**：导航行为设置（默认：false）
- **isNavPersonalizationDisabled**：个性化设置（默认：false）
- **isNavTabPersistenceDisabled**：标签持久性设置（默认：false）

## 应用程序配置

### 导航类型选择（CRITICAL）
**navType 的决策标准：**

**选择 "Standard"（DEFAULT）的情况：**
- 一般业务应用程序和大多数工作流
- 单记录焦点或线性导航模式
- 标准基于标签的导航就足够了

**仅当工作流需要时选择 "Console"：**
- 在分视图中同时管理多个相关记录
- 用于处理复杂、相互关联数据的标签工作区
- 同时从多个来源显示上下文信息
- 示例：客户服务运营、支持台、呼叫中心

**不确定时：** 对于大多数一般业务用例，默认选择 "Standard"

### 导航设置
- **isNavAutoTempTabsDisabled**：控制自动临时标签创建
- **isNavPersonalizationDisabled**：控制用户个性化功能
- **isNavTabPersistenceDisabled**：控制跨会话的标签持久性

### 标签管理
- **tabs**：应用程序中包含的标签数组
- **formFactors**：设备特定配置（Large 用于桌面，Small 用于移动）

### Utility Bar
- **utilityBar**：引用闪电 Utility Bar（出现在闪电体验的底部）

### 品牌化（HIGHLY RECOMMENDED - DO NOT SKIP）
**重要提示**：提供品牌配置以创建专业、视觉上独特的应用程序标识。

- **brand.headerColor**：标题栏颜色，十六进制格式（例如，"#0070D2"）- RECOMMENDED
- **brand.shouldOverrideOrgTheme**：覆盖组织主题（true/false）- 默认：false
- **brand.footerColor**：页脚颜色，十六进制格式

### 操作覆盖（CRITICAL - DO NOT SKIP）
**重要提示**：对于每个具有由 flexipage 专家生成的记录页面的自定义对象标签，都必须创建操作覆盖。

- **actionOverrides.actionName**：要覆盖的操作（"View" 或 "Tab"）
- **actionOverrides.content**：页面/组件名称（FlexiPage、Visualforce、闪电组件）
    - 对于 "View" 操作：引用由 flexipage 专家生成的记录页面
    - 对于 "Tab" 操作：引用由 flexipage 专家生成的主页/应用程序页面
- **actionOverrides.formFactor**：设备类型（"Large" 或 "Small"）
- **actionOverrides.type**：覆盖类型（"Default"、"Visualforce"、"Flexipage"、"LightningComponent"、"Scontrol"）
    - 推荐：使用 "Flexipage" 用于由 flexipage 专家生成的闪电记录/主页
- **actionOverrides.pageOrSobjectType**：覆盖适用的对象 API 名称
- **actionOverrides.comment**：可选描述（最多 1000 个字符）
    - 自动生成的评论："Action override created by Lightning App Builder during activation."
- **actionOverrides.skipRecordTypeSelect**：跳过记录类型选择（默认：false）

### 配置文件操作覆盖
- **profileActionOverrides.actionName**：要覆盖的操作（"View" 或 "Tab"）
- **profileActionOverrides.content**：页面/组件名称
    - 对于 "View" 操作：引用由 flexipage 专家生成的特定配置文件的记录页面
    - 对于 "Tab" 操作：引用由 flexipage 专家生成的特定配置文件的主页
    - 可以引用与 actionOverrides 相同或不同的 FlexiPages，以提供特定配置文件的用户体验
- **profileActionOverrides.formFactor**：设备类型（"Large" 或 "Small"）
- **profileActionOverrides.pageOrSobjectType**：对象 API 名称
- **profileActionOverrides.type**：覆盖类型
    - 推荐：使用 "Flexipage" 用于由 flexipage 专家生成的闪电页面
- **profileActionOverrides.profile**：配置文件 API 名称（例如，"Admin"、"Standard User"）
    - 为不同用户配置文件启用不同的页面布局

## 设备支持

### 桌面配置
- **formFactor**："Large"
- **tabs**：应用程序的完整标签列表

### 手机配置
- **formFactor**："Small"
- **tabs**：移动优化的标签选择

### 平板配置
- **formFactor**："Medium"
- **tabs**：适合平板电脑的标签选择

## 用户体验功能

### 导航行为
- **Auto Temporary Tabs**：可以启用/禁用
- **Personalization**：用户自定义选项
- **Tab Persistence**：记住用户的标签选择

### 无障碍性
- **Keyboard Navigation**：完整的键盘支持
- **Screen Reader**：兼容辅助技术
- **High Contrast**：支持高对比度模式

## 集成点
- **Custom Tabs**：包含自定义对象和网页标签
- **Standard Tabs**：包含标准的 Salesforce 标签
- **Lightning Pages**：与闪电页面布局集成
- **Components**：包含自定义闪电组件

## 最佳实践
- **始终使用闪电 UI**：将 `uiType` 设置为 "Lightning" 以创建现代应用程序
- **选择适当的导航**：CRITICAL - 仔细分析需求以选择 `navType`
    - 使用 "Standard"（DEFAULT）用于一般业务应用程序
    - 仅当工作流需要多标签工作区、分视图或同时管理多个相关记录时使用 "Console"
    - Console 示例：客户服务、呼叫中心、支持运营
    - 对于大多数一般业务用例，默认选择 "Standard"
- **包含标准标签**：添加常见的 Salesforce 标签（主页、账户、联系人等）
- **使用清晰、描述性的应用程序名称**
- **逻辑地分组相关功能**
- **考虑不同的用户角色和需求**
- **跨不同设备类型进行测试**
- **确保适当的权限和访问控制**
- **为用户提供有意义的描述**
- **遵循一致的命名约定**
- **始终配置品牌**：设置 headerColor 以创建专业的应用程序标识
- **使用可访问的品牌颜色**：确保十六进制颜色具有足够的对比度（WCAG AA 合规）
- **配置 utility bars**：为用户提供有用的快速访问工具
- **利用操作覆盖**：使用 flexipage 专家生成的 FlexiPages 自定义特定对象的页面布局
- **使用配置文件覆盖**：通过引用每个配置文件不同的 flexipage 专家生成的页面来提供基于角色的体验

## 增强规则
- **uiType**：始终设置为 "Lightning" 以获得现代应用程序体验
- **navType**：CRITICAL DECISION - 仔细分析用户需求
    - 设置为 "Standard"（DEFAULT）用于一般业务应用程序
    - 仅当工作流需要时设置为 "Console"：
        - 在分视图中同时管理多个相关记录
        - 用于处理复杂、相互关联数据的标签工作区
        - 同时从多个来源显示上下文信息
    - Console 示例：客户服务运营、呼叫中心、支持台
    - 在 Standard 和 Console 之间不确定时，选择 "Standard" 用于大多数业务用例
- **formFactors**：始终设置为 ["LARGE"] 用于桌面闪电体验
- **Standard Tabs**：自动添加主页、账户、联系人、机会、潜在客户、案例
- **导航设置**：将所有导航标志设置为 false 以获得最佳用户体验
- **品牌化**：ALWAYS 包含品牌配置以创建专业的应用程序标识
    - MANDATORY：将 brand.headerColor 设置为适当的颜色（例如，"#0070D2" 用于 Salesforce Blue）
    - 根据需求设置 brand.shouldOverrideOrgTheme
- **操作覆盖**：ALWAYS 在存在自定义记录页面时创建操作覆盖
    - MANDATORY：为 "View" 操作添加指向 flexipage 专家生成的记录页面的操作覆盖
    - 使用 "Flexipage" 类型并引用确切的 FlexiPage 名称
    - 将 formFactor 设置为 "Large" 用于桌面
    - 包括 pageOrSobjectType 并带有对象 API 名称
- **配置文件操作覆盖**：引用 flexipage 专家生成的页面以进行基于角色的自定义
- **表单因素**：在覆盖中使用 "Large" 用于桌面，"Small" 用于移动

## CRITICAL 验证清单（MUST VERIFY）
- [ ] 所有标签都包含在应用程序中
- [ ] **navType 是否正确设置** - 验证 Console 与 Standard 的选择
- [ ] 对于大多数一般业务应用程序，默认选择 "Standard"
- [ ] 仅当工作流需要同时管理多个记录、分视图或多标签工作区时，才选择 "Console"
- [ ] 如果需求是一般/模糊的 → navType 应该是 "Standard"
- [ ] **品牌化已配置** - 这是 HIGHLY RECOMMENDED 以创建专业应用程序
- [ ] brand.headerColor 已设置有效的十六进制颜色（例如，"#0070D2"）
- [ ] brand.shouldOverrideOrgTheme 已设置（默认：false）
- [ ] **操作覆盖已创建** - 这是 MANDATORY 的，对于每个具有记录页面的自定义对象
- [ ] 为每个自定义对象标签定义操作覆盖，指向正确的记录页面
- [ ] actionOverrides.content 匹配 flexipage 专家生成的确切的 FlexiPage 名称
- [ ] actionOverrides.pageOrSobjectType 设置为正确的对象 API 名称
- [ ] actionOverrides.type 设置为 "Flexipage"
- [ ] actionOverrides.actionName 设置为 "View"
- [ ] actionOverrides.formFactor 设置为 "Large"
- [ ] 所有必需字段都已填写（fullName、label、uiType、navType、formFactors）
