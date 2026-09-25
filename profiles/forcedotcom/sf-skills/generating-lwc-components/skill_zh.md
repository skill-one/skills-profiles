# 生成lwc组件：Lightning Web Components开发

当用户需要**Lightning Web Components**时使用此技能：LWC包、线模式、Apex/GraphQL集成、SLDS 2样式、可访问性、性能工作或Jest单元测试。

## 此技能何时负责任务

当工作涉及以下内容时，使用`generating-lwc-components`：
- `lwc/**/*.js`、`.html`、`.css`、`.js-meta.xml`
- 组件脚手架和包设计
- 线服务、Apex集成、GraphQL集成
- SLDS 2、暗黑模式、可访问性工作
- LWC的Jest单元测试

当用户是以下情况时，将任务委托给其他技能：
- 首先编写Apex控制器或业务逻辑 → [generating-apex](../generating-apex/SKILL.md)
- 构建Flow XML而不是LWC屏幕组件 → [generating-flow](../generating-flow/SKILL.md)
- 部署元数据 → [deploying-metadata](../deploying-metadata/SKILL.md)

---

## 首先收集的必要上下文

询问或推断：
- 组件用途和目标表面
- 数据源：LDS、Apex、GraphQL、LMS或通过Apex的外部系统
- 用户是否需要测试
- 组件是否必须在Flow、App Builder、Experience Cloud或仪表板上下文中运行
- 可访问性和样式预期

---

## 推荐的工作流程

### 1. 选择正确的架构
使用**PICKLES**思维模式：
- 原型设计
- 集成正确的数据源
- 组成组件边界
- 定义交互模型
- 使用平台库
- 优化执行
- 强制执行安全

### 2. 选择正确的数据访问模式
| 需求 | 默认模式 |
|---|---|
| 单记录UI | LDS / `getRecord` |
| 简单CRUD表单 | 基础记录表单组件 |
| 复杂服务器查询 | Apex `@AuraEnabled(cacheable=true)` |
| 相关图形数据 | GraphQL线适配器 |
| 跨DOM通信 | Lightning消息服务 |

### 3. 在需要时从资源开始
使用提供的资源：
- 基本组件包
- 数据表格
- 模态模式
- Flow屏幕组件
- GraphQL组件
- LMS消息通道
- Jest测试
- TypeScript启用组件

### 4. 验证前端质量
检查：
- 可访问性
- SLDS 2 / 暗黑模式合规性
- 事件契约
- 性能 / 重绘安全性
- 当需要时Jest覆盖率

### 5. 移交支持的后端或部署工作
使用：
- [generating-apex](../generating-apex/SKILL.md) 用于控制器 / 服务
- [deploying-metadata](../deploying-metadata/SKILL.md) 用于部署
- [running-apex-tests](../running-apex-tests/SKILL.md) 仅用于Apex侧测试循环，不是Jest

---

## 高信号规则

- 优先使用平台基础组件而不是重新发明控件
- 使用`@wire`用于响应式只读用例；命令式调用用于显式操作和DML路径
- 不要引入不可访问的自定义UI
- 避免硬编码颜色；使用SLDS 2兼容的样式钩 / 变量
- 避免在`renderedCallback()`中重绘循环
- 保持组件通信模式明确和最小化

---

## 输出格式

完成时，按以下顺序报告：
1. **创建或更新的组件**
2. **选择的数据访问模式**
3. **更改的文件**
4. **可访问性 / 样式 / 测试说明**
5. **下一步实现或部署步骤**

建议的格式：

```text
LWC工作：<摘要>
模式：<wire / apex / graphql / lms / flow-screen>
文件：<路径>
质量：<a11y, SLDS2, 暗黑模式, Jest>
下一步：<部署, 添加控制器或运行测试>
```

---

## 本地开发服务器

使用热重载在本地预览LWC组件——无需部署。运行`scripts/local-dev-preview.sh`中的命令以启动组件、应用程序或Experience Cloud站点的本地开发会话。

本地开发命令在首次运行时即时安装。它们是长时间运行的过程，打开浏览器进行实时预览。更改`.js`、`.html`和`.css`文件会立即自动重载。需要活动的org连接以进行数据和Apex调用。

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| Apex控制器或服务 | [generating-apex](../generating-apex/SKILL.md) | 后端逻辑 |
| 嵌入Flow屏幕 | [generating-flow](../generating-flow/SKILL.md) | 声明性编排 |
| 部署组件包 | [deploying-metadata](../deploying-metadata/SKILL.md) | org推广 |
| 创建支持元数据（消息通道、对象） | [deploying-metadata](../deploying-metadata/SKILL.md) | 元数据部署 |

---

## 参考文件索引

### 从这里开始
- [references/component-patterns.md](references/component-patterns.md) — 组件架构模式和包设计
- [references/slds-design-guide.md](references/slds-design-guide.md) — SLDS 2样式、暗黑模式、CSS钩
- [references/lwc-best-practices.md](references/lwc-best-practices.md) — 高信号规则和反模式
- [references/scoring-and-testing.md](references/scoring-and-testing.md) — 165分评分标准在8个类别中
- [references/jest-testing.md](references/jest-testing.md) — Jest单元测试模式和异步渲染辅助
- [references/slds-blueprints.json](references/slds-blueprints.json) — 机器可读的SLDS组件蓝图
- [references/cli-commands.md](references/cli-commands.md) — SF CLI命令用于LWC开发

### 可访问性 / 性能 / 状态
- [references/accessibility-guide.md](references/accessibility-guide.md) — WCAG、ARIA、键盘导航模式
- [references/performance-guide.md](references/performance-guide.md) — 懒加载、防抖、重绘安全性
- [references/state-management.md](references/state-management.md) — 反应性状态模式和LMS
- [references/template-anti-patterns.md](references/template-anti-patterns.md) — 避免常见的HTML模板错误

### 集成 / 高级功能
- [references/lms-guide.md](references/lms-guide.md) — Lightning消息服务模式
- [references/flow-integration-guide.md](references/flow-integration-guide.md) — Flow屏幕组件设计
- [references/advanced-features.md](references/advanced-features.md) — Spring '26功能：TypeScript、lwc:on、GraphQL变异
- [references/async-notification-patterns.md](references/async-notification-patterns.md) — toast、通知、异步流程
- [references/triangle-pattern.md](references/triangle-pattern.md) — 父子兄弟通信三角形

### 资产模板
- [assets/basic-component/basicComponent.js](assets/basic-component/basicComponent.js) — 线服务、错误/加载状态、事件调度
- [assets/datatable-component/datatableComponent.js](assets/datatable-component/datatableComponent.js) — 带内联编辑的数据表格
- [assets/flow-screen-component/flowScreenComponent.js](assets/flow-screen-component/flowScreenComponent.js) — 带输入/输出属性的Flow屏幕
- [assets/form-component/formComponent.js](assets/form-component/formComponent.js) — 表单验证和DML模式
- [assets/graphql-component/graphqlComponent.js](assets/graphql-component/graphqlComponent.js) — 带基于光标的分页的GraphQL线适配器
- [assets/jest-test/componentName.test.js.example](assets/jest-test/componentName.test.js.example) — Jest测试模板（复制并重命名，删除`.example`后缀）
- [assets/message-channel/lmsPublisher.js](assets/message-channel/lmsPublisher.js) — LMS发布者模式
- [assets/message-channel/lmsSubscriber.js](assets/message-channel/lmsSubscriber.js) — LMS订阅者模式
- [assets/modal-component/modalComponent.js](assets/modal-component/modalComponent.js) — 带焦点陷阱和ESC处理的模态
- [assets/record-picker/recordPicker.js](assets/record-picker/recordPicker.js) — 带搜索的记录选择器
- [assets/state-store/store.js](assets/state-store/store.js) — 用于跨组件状态的反应性状态存储
- [assets/typescript-component/typescriptComponent.ts](assets/typescript-component/typescriptComponent.ts) — TypeScript启用组件（Spring '26）
- [assets/workspace-api/workspaceComponent.js](assets/workspace-api/workspaceComponent.js) — 用于标签和焦点管理的Workspace API
- [assets/apex-controller/LwcController.cls](assets/apex-controller/LwcController.cls) — 带有`@AuraEnabled(cacheable=true)`模式的Apex控制器

### 脚本
- [scripts/local-dev-preview.sh](scripts/local-dev-preview.sh) — 组件、应用程序和站点预览的本地开发服务器命令

---

## 评分指南

| 分数 | 含义 |
|---|---|
| 150+ | 生产就绪的LWC包 |
| 125–149 | 强大的组件，但仍有少量润色空间 |
| 100–124 | 功能性，但建议审查 |
| < 100 | 需要显著改进 |
