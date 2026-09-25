# experience-lwc-generate：Lightning Web Components 开发

当用户需要 **Lightning Web Components**（LWC）时使用此技能：LWC 打包、线模式、Apex/GraphQL 集成、SLDS 2 样式、可访问性、性能优化或 Jest 单元测试。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `experience-lwc-generate`：
- `lwc/**/*.js`、`.html`、`.css`、`.js-meta.xml`
- 组件脚手架和打包设计
- 线服务、Apex 集成、GraphQL 集成
- SLDS 2、暗黑模式及可访问性工作
- LWC 的 Jest 单元测试

当用户处于以下情况时，应委派给其他技能：
- 首先编写 Apex 控制器或业务逻辑 → [platform-apex-generate](../platform-apex-generate/SKILL.md)
- 构建 Flow XML 而不是 LWC 屏幕组件 → [automation-flow-generate](../automation-flow-generate/SKILL.md)
- 部署元数据 → [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md)

---

## 首先收集必要的上下文

询问或推断：
- 组件用途和目标界面
- 数据源：LDS、Apex、GraphQL、LMS 或通过 Apex 的外部系统
- 用户是否需要测试
- 组件是否必须在 Flow、App Builder、Experience Cloud 或仪表板环境中运行
- 可访问性和样式预期

---

## 推荐的工作流程

### 1. 选择正确的架构
使用 **PICKLES** 思维方式：
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
| 单记录 UI | LDS / `getRecord` |
| 简单 CRUD 表单 | 基础记录表单组件 |
| 复杂服务器查询 | Apex `@AuraEnabled(cacheable=true)` |
| 相关图形数据 | GraphQL 线适配器 |
| 跨 DOM 通信 | Lightning 消息服务 |

### 3. 在需要时从资源开始

使用提供的资源：
- 基础组件打包
- 数据表格
- 模态模式
- Flow 屏幕组件
- GraphQL 组件
- LMS 消息通道
- Jest 测试
- TypeScript 支持的组件

### 4. 验证前端质量

检查：
- 可访问性
- SLDS 2 / 暗黑模式合规性
- 事件契约
- 性能 / 重绘安全性
- 当需要时 Jest 覆盖率

### 5. 委派支持的后端或部署工作

使用：
- [platform-apex-generate](../platform-apex-generate/SKILL.md) 用于控制器 / 服务
- [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) 用于部署
- [platform-apex-test-run](../platform-apex-test-run/SKILL.md) 仅用于 Apex 端测试循环，不包括 Jest

---

## 高信号规则

- 优先使用平台基础组件，而不是重新发明控件
- 使用 `@wire` 用于响应式只读用例；命令式调用用于显式操作和 DML 路径
- 不要引入不可访问的自定义 UI
- 避免硬编码颜色；使用 SLDS 2 兼容的样式钩 / 变量
- 避免 `renderedCallback()` 中的重绘循环
- 保持组件通信模式明确和最小化

---

## 输出格式

完成时按以下顺序报告：
1. **创建或更新的组件**
2. **选择的数据访问模式**
3. **更改的文件**
4. **可访问性 / 样式 / 测试说明**
5. **下一步实现或部署步骤**

建议格式：

```text
LWC 工作： <摘要>
模式： <wire / apex / graphql / lms / flow-screen>
文件： <路径>
质量： <a11y, SLDS2, 暗黑模式, Jest>
下一步： <部署, 添加控制器, 或运行测试>
```

---

## 本地开发服务器

使用热重载在本地预览 LWC 组件——无需部署。运行 `scripts/local-dev-preview.sh` 中的命令，以开始组件、应用或 Experience Cloud 站点的本地开发会话。

本地开发命令在首次运行时即时安装。它们是长时间运行的过程，会打开带有实时预览的浏览器。更改 `.js`、`.html` 和 `.css` 文件会即时自动重载。需要活跃的组织连接以进行数据和 Apex 调用。

---

## 跨技能集成

| 需求 | 委派给 | 原因 |
|---|---|---|
| Apex 控制器或服务 | [platform-apex-generate](../platform-apex-generate/SKILL.md) | 后端逻辑 |
| 嵌入 Flow 屏幕 | [automation-flow-generate](../automation-flow-generate/SKILL.md) | 声明式编排 |
| 部署组件打包 | [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) | 组织推广 |
| 创建支持性元数据（消息通道、对象） | [platform-metadata-deploy](../platform-metadata-deploy/SKILL.md) | 元数据部署 |

---

## 参考文件索引

### 从这里开始
- [references/component-patterns.md](references/component-patterns.md) — 组件架构模式和打包设计
- [references/slds-design-guide.md](references/slds-design-guide.md) — SLDS 2 样式、暗黑模式、CSS 钩
- [references/lwc-best-practices.md](references/lwc-best-practices.md) — 高信号规则和反模式
- [references/scoring-and-testing.md](references/scoring-and-testing.md) — 165 分评分标准，涵盖 8 个类别
- [references/jest-testing.md](references/jest-testing.md) — Jest 单元测试模式和异步渲染辅助
- [references/slds-blueprints.json](references/slds-blueprints.json) — 机器可读的 SLDS 组件蓝图
- [references/cli-commands.md](references/cli-commands.md) — SF CLI 命令用于 LWC 开发

### 可访问性 / 性能 / 状态
- [references/accessibility-guide.md](references/accessibility-guide.md) — WCAG、ARIA、键盘导航模式
- [references/performance-guide.md](references/performance-guide.md) — 懒加载、防抖、重绘安全性
- [references/state-management.md](references/state-management.md) — 反应式状态模式和 LMS
- [references/template-anti-patterns.md](references/template-anti-patterns.md) — 避免的常见 HTML 模板错误

### 集成 / 高级功能
- [references/lms-guide.md](references/lms-guide.md) — Lightning 消息服务模式
- [references/flow-integration-guide.md](references/flow-integration-guide.md) — Flow 屏幕组件设计
- [references/advanced-features.md](references/advanced-features.md) — Spring '26 功能：TypeScript、lwc:on、GraphQL 变更
- [references/async-notification-patterns.md](references/async-notification-patterns.md) — toast、通知、异步流程
- [references/triangle-pattern.md](references/triangle-pattern.md) — 父子兄弟通信三角形

### 资源模板
- [assets/basic-component/basicComponent.js](assets/basic-component/basicComponent.js) — 线服务、错误/加载状态、事件调度
- [assets/datatable-component/datatableComponent.js](assets/datatable-component/datatableComponent.js) — 带内联编辑的数据表格
- [assets/flow-screen-component/flowScreenComponent.js](assets/flow-screen-component/flowScreenComponent.js) — 带输入/输出属性的 Flow 屏幕
- [assets/form-component/formComponent.js](assets/form-component/formComponent.js) — 表单验证和 DML 模式
- [assets/graphql-component/graphqlComponent.js](assets/graphql-component/graphqlComponent.js) — 带基于游标的分页的 GraphQL 线适配器
- [assets/jest-test/componentName.test.js.example](assets/jest-test/componentName.test.js.example) — Jest 测试模板（复制并重命名，删除 `.example` 后缀）
- [assets/message-channel/lmsPublisher.js](assets/message-channel/lmsPublisher.js) — LMS 发布者模式
- [assets/message-channel/lmsSubscriber.js](assets/message-channel/lmsSubscriber.js) — LMS 订阅者模式
- [assets/modal-component/modalComponent.js](assets/modal-component/modalComponent.js) — 带焦点捕获和 ESC 处理的模态组件
- [assets/record-picker/recordPicker.js](assets/record-picker/recordPicker.js) — 带搜索的记录选择器
- [assets/state-store/store.js](assets/state-store/store.js) — 跨组件状态的反应式状态存储
- [assets/typescript-component/typescriptComponent.ts](assets/typescript-component/typescriptComponent.ts) — TypeScript 支持的组件（Spring '26）
- [assets/workspace-api/workspaceComponent.js](assets/workspace-api/workspaceComponent.js) — 用于标签和焦点管理的 workspace API
- [assets/apex-controller/LwcController.cls](assets/apex-controller/LwcController.cls) — 带有 `@AuraEnabled(cacheable=true)` 模式的 Apex 控制器

### 脚本
- [scripts/local-dev-preview.sh](scripts/local-dev-preview.sh) — 组件、应用和站点的本地开发服务器命令

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 150+ | 生产就绪的 LWC 打包 |
| 125–149 | 强大的组件，但仍有少量完善空间 |
| 100–124 | 功能性，但建议审查 |
| < 100 | 需要显著改进 |
