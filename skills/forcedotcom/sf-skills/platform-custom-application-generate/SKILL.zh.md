---
name: platform-custom-application-generate
description: 当用户需要创建或配置具有导航、品牌和操作覆盖的基于标签的 Salesforce 自定义应用程序时，请使用此技能。当用户提及自定义应用程序、应用程序元数据、应用程序导航或组织标签到应用程序时，会触发此技能。当用户希望为标签和页面创建应用程序容器时，请使用此技能。当目标是在应用程序启动器中托管 React UI 包时，请勿使用此技能——在这种情况下，请使用 experience-ui-bundle-custom-app-generate。
---

## 何时使用此技能

当您需要执行以下操作时，请使用此技能：
- 创建闪电应用程序
- 将标签和功能组织成专注的应用程序
- 配置应用程序导航和品牌标识
- 为对象设置自定义页面布局
- 排查与自定义应用程序相关的部署错误

# CustomApplication (闪电应用程序) 元数据规范

## 概述

将标签和功能分组，为特定业务流程提供专注用户体验的自定义应用程序（闪电应用程序）。始终针对闪电体验进行配置。

## 目的
- 将相关功能组织成专注的应用程序
- 为特定用户角色分组标签和组件
- 提供定制的用户体验
- 控制对特定功能和数据的访问
- 使用标准导航进行一般业务应用程序，或使用控制台导航进行需要多标签工作区的专用服务/支持工作流
- 创建专业、带品牌标识的应用程序身份，具有自定义颜色和品牌标识
- 使用自定义闪电页面覆盖标准操作以增强用户体验
- 通过配置文件操作覆盖启用特定配置文件的用户体验

## 必要属性

### 核心应用程序属性
- **fullName**：应用程序的API名称
- **label**：应用程序的显示名称
- **uiType**：对于现代应用程序，始终为“Lightning”
- **navType**：CRITICAL - 根据用户需求和流程模式选择
    - "Standard"：DEFAULT，用于一般业务应用程序（例如，销售、营销、运营）
    - "Console"：仅在需要同时管理多个记录、分屏或多标签工作区时使用（例如，客户服务、呼叫中心、支持运营）
- **formFactors**：表单因素数组（["LARGE"]用于桌面，["SMALL"]用于移动，或两者）

### 可选属性
- **description**：应用程序目的的简要描述
- **tabs**：要包含的标签数组
- **utilityBar**：Utility Bar配置的API名称
- **brand**：高度推荐 - 品牌标识配置对象（headerColor、shouldOverrideOrgTheme、footerColor）
- **actionOverrides**：当存在自定义记录页面时 - 操作覆盖配置（actionName、content、formFactor、type、pageOrSobjectType）
- **profileActionOverrides**：特定配置文件的操作覆盖（actionName、content、formFactor、pageOrSobjectType、type、profile）
- **isNavAutoTempTabsDisabled**：导航行为设置（默认：false）
- **isNavPersonalizationDisabled**：个性化设置（默认：false）
- **isNavTabPersistenceDisabled**：标签持久性设置（默认：false）

## 应用程序配置

### 导航类型选择（CRITICAL）
**navType的决策标准：**

**选择“Standard”（DEFAULT）的情况：**
- 一般业务应用程序和大多数工作流
- 单记录焦点或线性导航模式
- 标准标签式导航足够

**仅在流程需要时选择“Console”：**
- 在分屏中同时管理多个相关记录
- 用于处理复杂、相互关联数据的标签式工作区
- 同时显示来自多个来源的上下文信息
- 示例：客户服务运营、支持台、呼叫中心

**不确定时：** 对于大多数一般业务用例，默认选择“Standard”

### 导航设置
- **isNavAutoTempTabsDisabled**：控制自动临时标签创建
- **isNavPersonalizationDisabled**：控制用户个性化功能
- **isNavTabPersistenceDisabled**：控制跨会话的标签持久性

### 标签管理
- **tabs**：应用程序中包含的标签数组
- **formFactors**：设备特定配置（桌面为Large，移动为Small）

### Utility Bar
- **utilityBar**：引用闪电Utility Bar（位于闪电体验的底部）

### 品牌标识（高度推荐 - 不要跳过）
**重要提示**：提供品牌标识配置，以创建专业、视觉上独特的应用程序身份。

- **brand.headerColor**：标题栏颜色，十六进制格式（例如，“#0070D2”） - 推荐
- **brand.shouldOverrideOrgTheme**：覆盖组织主题（true/false） - 默认：false
- **brand.footerColor**：页脚颜色，十六进制格式

### 操作覆盖（CRITICAL - 不要跳过）
**重要提示**：对于每个具有由flexipage专家生成的记录页面的自定义对象标签，都必须创建操作覆盖。

- **actionOverrides.actionName**：要覆盖的操作（“View”或“Tab”）
- **actionOverrides.content**：页面/组件名称（FlexiPage、Visualforce、闪电组件）
    - 对于“View”操作：引用由flexipage专家生成的记录页面
    - 对于“Tab”操作：引用由flexipage专家生成的主页/应用程序页面
- **actionOverrides.formFactor**：设备类型（“Large”或“Small”）
- **actionOverrides.type**：覆盖类型（“Default”、“Visualforce”、“Flexipage”、“LightningComponent”、“Scontrol”）
    - 推荐：使用“Flexipage”为flexipage专家生成的闪电记录/主页
- **actionOverrides.pageOrSobjectType**：覆盖适用的对象API名称
- **actionOverrides.comment**：可选描述（最多1000个字符）
    - 自动生成的评论：“由闪电应用程序构建器在激活期间创建的操作覆盖。”
- **actionOverrides.skipRecordTypeSelect**：跳过记录类型选择（默认：false）

### 配置文件操作覆盖
- **profileActionOverrides.actionName**：要覆盖的操作（“View”或“Tab”）
- **profileActionOverrides.content**：页面/组件名称
    - 对于“View”操作：引用由flexipage专家生成的特定配置文件的记录页面
    - 对于“Tab”操作：引用由flexipage专家生成的特定配置文件的主页
    - 可以引用与actionOverrides相同的或不同的FlexiPages，以提供特定配置文件的用户体验
- **profileActionOverrides.formFactor**：设备类型（“Large”或“Small”）
- **profileActionOverrides.pageOrSobjectType**：对象API名称
- **profileActionOverrides.type**：覆盖类型
    - 推荐：使用“Flexipage”为flexipage专家生成的闪电页面
- **profileActionOverrides.profile**：配置文件API名称（例如，“Admin”、“Standard User”）
    - 为不同用户配置文件启用不同的页面布局

## 设备支持

### 桌面配置
- **formFactor**：“Large”
- **tabs**：应用程序的完整标签列表

### 手机配置
- **formFactor**：“Small”
- **tabs**：移动优化的标签选择

### 平板配置
- **formFactor**：“Medium”
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
- **Standard Tabs**：包含标准Salesforce标签
- **Lightning Pages**：与闪电页面布局集成
- **Components**：包含自定义闪电组件

## 最佳实践
- **始终使用闪电UI**：将`uiType`设置为“Lightning”，以创建现代应用程序
- **选择适当的导航**：CRITICAL - 仔细分析需求，选择`navType`
    - 使用“Standard”（DEFAULT）进行一般业务应用程序
    - 仅当工作流需要多标签工作区、分屏或同时管理多个相关记录时使用“Console”
    - 示例：客户服务、呼叫中心、支持运营
    - 对于大多数一般业务用例，默认选择“Standard”
- **包含标准标签**：添加常见的Salesforce标签（主页、账户、联系人等）
- **使用清晰、描述性的应用程序名称**
- **逻辑分组相关功能**
- **考虑不同的用户角色和需求**
- **跨不同设备类型进行测试**
- **确保适当的权限和访问控制**
- **为用户提供有意义的描述**
- **遵循一致的命名约定**
- **始终配置品牌标识**：设置headerColor以创建专业的应用程序身份
- **使用无障碍品牌颜色**：确保十六进制颜色具有足够的对比度（符合WCAG AA标准）
- **配置utility bars**：为用户提供有用的快速访问工具
- **利用操作覆盖**：使用flexipage专家生成的FlexiPages自定义特定对象的页面布局
- **使用配置文件覆盖**：通过引用每个配置文件不同的flexipage专家生成的页面，提供基于角色的用户体验

## 增强规则
- **uiType**：始终设置为“Lightning”，以获得现代应用程序体验
- **navType**：CRITICAL DECISION - 仔细分析用户需求
    - 设置为“Standard”（DEFAULT）进行一般业务应用程序
    - 仅当工作流需要：
        - 使用分屏同时管理多个相关记录
        - 用于处理复杂、相互关联数据的标签式工作区
        - 同时显示来自多个来源的上下文信息
    - 示例：客户服务运营、呼叫中心、支持台
    - 在Standard和Console之间不确定时，对于大多数业务用例选择“Standard”
- **formFactors**：始终设置为`["LARGE"]`，用于桌面闪电体验
- **Standard Tabs**：自动添加主页、账户、联系人、机会、潜在客户、案例
- **导航设置**：将所有导航标志设置为false，以获得最佳用户体验
- **品牌标识**：始终包含品牌配置，以创建专业的应用程序身份
    - 必须设置brand.headerColor为适当的颜色（例如，“#0070D2”为Salesforce蓝色）
    - 根据需求设置brand.shouldOverrideOrgTheme
- **操作覆盖**：当存在自定义记录页面时，始终创建操作覆盖
    - 必须为“View”操作添加指向flexipage专家生成的记录页面的操作覆盖
    - 使用“Flexipage”类型并引用确切的FlexiPage名称
    - 将formFactor设置为“Large”，用于桌面
    - 包括pageOrSobjectType与对象API名称
- **配置文件操作覆盖**：引用flexipage专家生成的页面，以进行基于角色的自定义
- **表单因素**：在覆盖中使用“Large”用于桌面，“Small”用于移动

## CRITICAL验证清单（必须验证）
- [ ] 所有标签都已包含在应用程序中
- [ ] **navType已正确设置** - 验证Console与Standard的选择
- [ ] 对于大多数一般业务应用程序，默认选择“Standard”
- [ ] 仅当工作流需要同时管理多个记录、分屏或多标签工作区时，才选择“Console”
- [ ] 如果需求是通用/模糊的 → navType应为“Standard”
- [ ] **已配置品牌标识** - 这对于专业应用程序是高度推荐的
- [ ] brand.headerColor已设置有效的十六进制颜色（例如，“#0070D2”）
- [ ] brand.shouldOverrideOrgTheme已设置（默认：false）
- [ ] **已创建操作覆盖** - 这对于每个具有记录页面的自定义对象是必须的
- [ ] 为每个自定义对象标签定义了操作覆盖，指向正确的记录页面
- [ ] actionOverrides.content与flexipage专家生成的确切的FlexiPage名称匹配
- [ ] actionOverrides.pageOrSobjectType设置为正确的对象API名称
- [ ] actionOverrides.type设置为“Flexipage”
- [ ] actionOverrides.actionName设置为“View”
- [ ] actionOverrides.formFactor设置为“Large”
- [ ] 所有必需字段都已填写（fullName、label、uiType、navType、formFactors）
