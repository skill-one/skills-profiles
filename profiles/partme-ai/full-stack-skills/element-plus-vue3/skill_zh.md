## 何时使用此技能

当用户希望执行以下操作时，请使用此技能：
- 在 Vue 3 项目中安装和设置 Element Plus
- 在 Vue 3 应用程序中使用 Element Plus 组件
- 配置 Element Plus（全局配置、i18n、主题等）
- 使用表单组件（按钮、输入、表单等）
- 使用数据展示组件（表格、卡片等）
- 使用反馈组件（消息、通知、对话框等）
- 使用导航组件（菜单、标签页等）
- 自定义组件样式和主题
- 处理组件事件
- 了解 Element Plus API 和方法
- 排错 Element Plus 问题

## 如何使用此技能

此技能的结构与 Element Plus 官方文档结构相匹配（https://element-plus.org/zh-CN/，https://element-plus.org/en-US/guide/design，https://element-plus.org/en-US/component/overview）。在使用 Element Plus 时：

1. **从用户请求中识别主题**：
   - 安装/安装 → `examples/guide/installation.md`
   - 快速开始/快速开始 → `examples/guide/quick-start.md`
   - 设计/设计 → `examples/guide/design.md`
   - 组件/组件 → `examples/components/`
   - API/API 文档 → `api/`

2. **从 `examples/` 目录加载相应的示例文件**：

   **指南（使用指南）**：
   - `examples/guide/installation.md` - 安装指南
   - `examples/guide/quick-start.md` - 快速开始指南
   - `examples/guide/design.md` - 设计指南
   - `examples/guide/i18n.md` - 国际化
   - `examples/guide/theme.md` - 主题定制
   - `examples/guide/global-config.md` - 全局配置

   **组件（组件）**：
   - `examples/components/overview.md` - 组件概览
   - `examples/components/button.md` - 按钮组件
   - `examples/components/input.md` - 输入组件
   - `examples/components/form.md` - 表单组件
   - `examples/components/table.md` - 表格组件
   - `examples/components/card.md` - 卡片组件
   - `examples/components/dialog.md` - 对话框组件
   - `examples/components/message.md` - 消息组件
   - `examples/components/notification.md` - 通知组件
   - `examples/components/menu.md` - 菜单组件
   - `examples/components/tabs.md` - 标签页组件
   - `examples/components/date-picker.md` - 日期选择器组件
   - `examples/components/select.md` - 选择器组件
   - `examples/components/switch.md` - 开关组件
   - `examples/components/checkbox.md` - 复选框组件
   - `examples/components/radio.md` - 单选框组件
   - `examples/components/upload.md` - 上传组件
   - `examples/components/pagination.md` - 分页组件
   - `examples/components/tree.md` - 树形控件组件
   - `examples/components/tree-select.md` - 树形选择器组件
   - `examples/components/transfer.md` - 穿梭框组件
   - `examples/components/descriptions.md` - 描述列表组件
   - `examples/components/avatar.md` - 头像组件
   - `examples/components/badge.md` - 徽标组件
   - `examples/components/tag.md` - 标签组件
   - `examples/components/empty.md` - 空状态组件
   - `examples/components/loading.md` - 加载组件
   - `examples/components/popover.md` - 弹出框组件
   - `examples/components/tooltip.md` - 提示组件
   - `examples/components/dropdown.md` - 下拉菜单组件
   - `examples/components/drawer.md` - 抽屉组件
   - `examples/components/popconfirm.md` - 确认框组件

3. **遵循该示例文件中的特定说明**，包括语法、结构和最佳实践

   **重要提示**：
   - Element Plus 仅适用于 Vue 3
   - 组件使用 Vue 3 Composition API
   - 示例包含 Options API 和 Composition API
   - 每个示例文件包含关键概念、代码示例和要点

4. **在需要时参考 `api/` 目录中的 API 文档**：
   - `api/component-api.md` - 组件 API 参考
   - `api/props-and-events.md` - 属性和事件参考
   - `api/global-config.md` - 全局配置 API

5. **使用 `templates/` 目录中的模板**：
   - `templates/installation.md` - 安装模板
   - `templates/component-usage.md` - 组件使用模板
   - `templates/project-setup.md` - 项目设置模板

### 1. 了解 Element Plus

Element Plus 是一个基于 Vue 3 的组件库，提供丰富的 UI 组件，遵循 Element Design 设计原则。

**关键概念**：
- **Vue 3 支持**：专为 Vue 3 和 Composition API 构建
- **设计系统**：遵循 Element Design 设计语言
- **丰富组件**：60+ 组件，适用于各种场景
- **主题定制**：支持主题定制
- **i18n**：国际化支持
- **TypeScript**：完全支持 TypeScript

### 2. 安装

**使用 npm**：

```bash
npm install element-plus
```

**使用 yarn**：

```bash
yarn add element-plus
```

**使用 pnpm**：

```bash
pnpm add element-plus
```

### 3. 基本设置

**完全导入**：

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
```

**按需导入**：

```javascript
import { ElButton, ElInput } from 'element-plus'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/input/style/css'
```

### 文档映射（与官方文档一一对应）

**指南（指南）**：
- 查看 `examples/guide/` 或 `examples/getting-started/` 中的指南文件 → https://element-plus.org/en-US/guide/design

**组件（组件）**：
- 查看 `examples/components/` 中的组件文件 → https://element-plus.org/en-US/component/overview

## 示例和模板

此技能包含按官方文档结构组织的详细示例。所有示例都在 `examples/` 目录中（见映射说明）。

**使用示例**：
- 从用户请求中识别主题
- 从上述映射中加载相应的示例文件
- 遵循该文件中的说明、语法和最佳实践
- 将代码示例调整到您的具体使用场景

**使用模板**：
- 参考 `templates/` 目录中的模板进行常见脚手架
- 将模板调整到您的具体需求和编码风格

## API 参考

详细的 API 文档在 `api/` 目录中提供，结构与官方 Element Plus API 文档结构相匹配：

### 组件 API (`api/component-api.md`)
- 组件属性和事件
- 组件方法
- 组件插槽

### 属性和事件 (`api/props-and-events.md`)
- 常用属性
- 常用事件
- 事件处理

### 全局配置 (`api/global-config.md`)
- 全局配置选项
- ConfigProvider 使用
- 主题配置

**使用 API 参考**：
1. 识别您需要帮助的 API
2. 从 `api/` 目录加载相应的 API 文件
3. 查找 API 签名、参数、返回类型和示例
4. 参考 linked 示例文件以获取详细的使用模式
5. 所有 API 文件都包含指向 `examples/` 目录中相关示例文件的链接

## 最佳实践

1. **按需导入**：仅导入您需要的组件以减少包体积
2. **使用 Composition API**：优先使用 Composition API 以更好地组织代码
3. **正确处理事件**：使用正确的事件处理组件交互
4. **定制主题**：使用主题变量进行定制
5. **遵循设计规范**：遵循 Element Design 规范
6. **使用 TypeScript**：利用 TypeScript 提高类型安全性

## 资源

- **官方文档**：https://element-plus.org/zh-CN/
- **英文文档**：https://element-plus.org/en-US/
- **设计指南**：https://element-plus.org/en-US/guide/design
- **组件概览**：https://element-plus.org/en-US/component/overview
- **GitHub 仓库**：https://github.com/element-plus/element-plus

## 关键词

Element Plus, element-plus, Vue 3, Vue3, UI 组件, 组件库, 按钮, 表单, 表格, 弹窗, 消息, 通知, 菜单, 标签页, 日期选择器, 选择器, 开关, 复选框, 单选框, 上传, 分页, 树形控件, 穿梭框, 描述列表, 头像, 徽标, 标签, 空状态, 加载, 弹出框, 提示, 下拉菜单, 抽屉, 气泡确认框, Button, Form, Table, Dialog, Message, Notification, Menu, Tabs, DatePicker, Select, Switch, Checkbox, Radio, Upload, Pagination, Tree, Transfer, Descriptions, Avatar, Badge, Tag, Empty, Loading, Popover, Tooltip, Dropdown, Drawer, Popconfirm
