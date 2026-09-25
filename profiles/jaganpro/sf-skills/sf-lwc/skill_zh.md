# sf-lwc：Lightning Web Components 开发

当用户需要 **Lightning Web Components** 时使用此技能：LWC 打包、线模式、Apex/GraphQL 集成、SLDS 2 样式、可访问性、性能优化工作或 Jest 单元测试。

## 此技能负责任务的情况

当工作涉及以下内容时使用 `sf-lwc`：
- `lwc/**/*.js`、`.html`、`.css`、`.js-meta.xml`
- 组件脚手架和打包设计
- 线服务、Apex 集成、GraphQL 集成
- SLDS 2、暗黑模式及可访问性工作
- LWC 的 Jest 单元测试

当用户处于以下情况时将任务委托给其他技能：
- 首先编写 Apex 控制器或业务逻辑 → [sf-apex](../sf-apex/SKILL.md)
- 构建 Flow XML 而不是 LWC 屏幕组件 → [sf-flow](../sf-flow/SKILL.md)
- 部署元数据 → [sf-deploy](../sf-deploy/SKILL.md)

---

## 首先收集的必要上下文

询问或推断：
- 组件用途和目标表面
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
- 强制执行安全策略

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
- 支持 TypeScript 的组件

### 4. 验证前端质量
检查：
- 可访问性
- SLDS 2 / 暗黑模式合规性
- 事件契约
- 性能 / 重绘安全性
- 当需要时 Jest 覆盖率

### 5. 移交支持的后端或部署工作
使用：
- [sf-apex](../sf-apex/SKILL.md) 用于控制器 / 服务
- [sf-deploy](../sf-deploy/SKILL.md) 用于部署
- [sf-testing](../sf-testing/SKILL.md) 仅用于 Apex 端测试循环，不包括 Jest

---

## 高信号规则

- 优先使用平台基础组件而不是重新发明控件
- 使用 `@wire` 用于响应式只读用例；使用命令式调用用于显式操作和 DML 路径
- 不要引入不可访问的自定义 UI
- 避免硬编码颜色；使用 SLDS 2 兼容的样式钩 / 变量
- 避免 `renderedCallback()` 中的重绘循环
- 保持组件通信模式明确且最小化

---

## 输出格式

完成时按以下顺序报告：
1. **创建或更新的组件**
2. **选择的数据访问模式**
3. **更改的文件**
4. **可访问性 / 样式 / 测试备注**
5. **下一步实现或部署步骤**

建议格式：

```text
LWC 工作： <摘要>
模式： <wire / apex / graphql / lms / flow-screen>
文件： <路径>
质量： <a11y, SLDS2, 暗黑模式, Jest>
下一步： <部署, 添加控制器或运行测试>
```

---

## 本地开发服务器

使用热重载在本地预览 LWC 组件——无需部署：

```bash
# 独立预览 LWC 组件
sf lightning dev component --target-org <别名>

# 本地预览 Lightning Experience 应用
sf lightning dev app --target-org <别名>

# 本地预览 Experience Cloud 网站
sf lightning dev site --target-org <别名>
```

在当前的 SF CLI 版本中，这些本地开发命令在第一次运行时即时安装。它们是长时间运行的过程，打开浏览器进行实时预览。更改 `.js`、`.html` 和 `.css` 文件会立即自动重载。需要活跃的 org 连接以获取数据和 Apex 调用。

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| Apex 控制器或服务 | [sf-apex](../sf-apex/SKILL.md) | 后端逻辑 |
| 嵌入 Flow 屏幕 | [sf-flow](../sf-flow/SKILL.md) | 声明式编排 |
| 部署组件打包 | [sf-deploy](../sf-deploy/SKILL.md) | org 推广 |
| 创建消息通道等元数据 | [sf-metadata](../sf-metadata/SKILL.md) | 支持元数据 |

---

## 参考地图

### 从这里开始
- [references/component-patterns.md](references/component-patterns.md)
- [references/slds-design-guide.md](references/slds-design-guide.md)
- [references/lwc-best-practices.md](references/lwc-best-practices.md)
- [references/scoring-and-testing.md](references/scoring-and-testing.md)
- [references/jest-testing.md](references/jest-testing.md)

### 可访问性 / 性能 / 状态
- [references/accessibility-guide.md](references/accessibility-guide.md)
- [references/performance-guide.md](references/performance-guide.md)
- [references/state-management.md](references/state-management.md)
- [references/template-anti-patterns.md](references/template-anti-patterns.md)

### 集成 / 高级功能
- [references/lms-guide.md](references/lms-guide.md)
- [references/flow-integration-guide.md](references/flow-integration-guide.md)
- [references/advanced-features.md](references/advanced-features.md)
- [references/async-notification-patterns.md](references/async-notification-patterns.md)
- [references/triangle-pattern.md](references/triangle-pattern.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 150+ | 生产就绪的 LWC 打包 |
| 125–149 | 强大的组件，但仍有少量润色空间 |
| 100–124 | 功能性但建议审查 |
| < 100 | 需要显著改进 |
