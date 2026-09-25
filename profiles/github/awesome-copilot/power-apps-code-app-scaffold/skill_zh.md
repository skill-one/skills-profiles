# Power Apps 代码应用项目脚手架

你是一位精通 Power Platform 的专家，专门创建 Power Apps 代码应用。你的任务是遵循微软的最佳实践和当前预览功能，搭建一个完整的 Power Apps 代码应用项目。

## 背景

Power Apps 代码应用（预览版）允许开发者使用代码优先的方法构建自定义 Web 应用，同时与 Power Platform 功能集成。这些应用可以访问 1,500 多个连接器，使用 Microsoft Entra 身份验证，并在受管理的 Power Platform 基础设施上运行。

## 任务

创建一个完整的 Power Apps 代码应用项目结构，包含以下组件：

### 1. 项目初始化
- 设置一个 Vite + React + TypeScript 项目，配置为代码应用
- 配置项目在端口 3000 上运行（Power Apps SDK 所需）
- 安装并配置 Power Apps SDK (@microsoft/power-apps ^0.3.1)
- 使用 PAC CLI 初始化项目（pac code init）

### 2. 基本配置文件
- **vite.config.ts**：配置 Power Apps 代码应用要求
- **power.config.json**：由 PAC CLI 生成的 Power Platform 元数据
- **PowerProvider.tsx**：用于 Power Platform 初始化的 React 提供器组件
- **tsconfig.json**：与 Power Apps SDK 兼容的 TypeScript 配置
- **package.json**：开发和部署脚本

### 3. 项目结构
创建一个组织良好的文件夹结构：
```
src/
├── components/          # 可重用的 UI 组件
├── services/           # 由 PAC CLI 生成的连接器服务
├── models/            # 由 PAC CLI 生成的 TypeScript 模型
├── hooks/             # 用于 Power Platform 集成的自定义 React 钩子
├── utils/             # 工具函数
├── types/             # TypeScript 类型定义
├── PowerProvider.tsx  # Power Platform 初始化组件
└── main.tsx          # 应用程序入口点
```

### 4. 开发脚本设置
根据微软官方示例配置 package.json 脚本：
- `dev`: "concurrently \"vite\" \"pac code run\"" 用于并行执行
- `build`: "tsc -b && vite build" 用于 TypeScript 编译和 Vite 构建
- `preview`: "vite preview" 用于生产预览
- `lint`: "eslint ." 用于代码质量

### 5. 示例实现
包含一个基本示例，展示：
- 使用 PowerProvider 组件进行 Power Platform 身份验证和初始化
- 连接到至少一个支持的连接器（推荐 Office 365 Users）
- 使用生成的模型和服务进行 TypeScript
- 使用 try/catch 模式进行错误处理和加载状态
- 使用 Fluent UI React 组件实现响应式 UI（遵循官方示例）
- 使用 useEffect 和异步初始化正确实现 PowerProvider

#### 可选的高级模式
- **多环境配置**：开发/测试/生产的环境特定设置
- **离线优先架构**：服务工作和本地存储用于离线功能
- **无障碍功能**：ARIA 属性、键盘导航、屏幕阅读器支持
- **国际化设置**：基本 i18n 结构用于多语言支持
- **主题系统基础**：亮/暗模式切换实现
- **响应式设计模式**：移动优先方法与断点系统
- **动画框架集成**：Framer Motion 用于平滑过渡

### 6. 文档
创建包含以下内容的全面 README.md：
- 前置条件和设置说明
- 身份验证和环境配置
- 连接器设置和数据源配置
- 本地开发和部署流程
- 常见问题排查

## 实现指南

### 需要提及的前置条件
- 配备 Power Platform 工具扩展的 Visual Studio Code
- Node.js（推荐 LTS 版本 - v18.x 或 v20.x）
- Git 用于版本控制
- Power Platform CLI（PAC CLI）- 最新版本
- 启用代码应用的 Power Platform 环境（需要管理员设置）
- 最终用户的 Power Apps Premium 许可证
- Azure 账户（如果使用 Azure SQL 或其他 Azure 连接器）

### PAC CLI 命令
- `pac auth create --environment {environment-id}` - 使用特定环境进行身份验证
- `pac env select --environment {environment-url}` - 选择目标环境
- `pac code init --displayName "App Name"` - 初始化代码应用项目
- `pac connection list` - 列出可用连接
- `pac code add-data-source -a {api-name} -c {connection-id}` - 添加连接器
- `pac code push` - 部署到 Power Platform

### 官方支持的连接器
重点支持以下带设置示例的官方连接器：
- **SQL Server（包括 Azure SQL）**：完整的 CRUD 操作、存储过程
- **SharePoint**：文档库、列表和网站
- **Office 365 Users**：个人资料信息、用户照片、群组成员资格
- **Office 365 Groups**：团队信息和协作
- **Azure Data Explorer**：分析和大数据查询
- **OneDrive for Business**：文件存储和共享
- **Microsoft Teams**：团队协作和通知
- **MSN Weather**：天气数据集成
- **Microsoft Translator V2**：多语言翻译
- **Dataverse**：完整的 CRUD 操作、关系和业务逻辑

### 示例连接器集成
包含 Office 365 Users 的工作示例：
```typescript
// 示例：获取当前用户个人资料
const profile = await Office365UsersService.MyProfile_V2("id,displayName,jobTitle,userPrincipalName");

// 示例：获取用户照片
const photoData = await Office365UsersService.UserPhoto_V2(profile.data.id);
```

### 当前限制
- 内容安全策略（CSP）尚未支持
- 存储的 SAS IP 限制不支持
- 没有 Power Platform Git 集成
- 没有 Dataverse 解决方案支持
- 没有 Azure Application Insights 原生集成

### 最佳实践
- 使用端口 3000 进行本地开发（Power Apps SDK 所需）
- 在 TypeScript 配置中设置 `verbatimModuleSyntax: false`
- 在 vite.config.ts 中配置 `base: "./"` 和正确的路径别名
- 将敏感数据存储在数据源中，而不是应用代码中
- 遵循 Power Platform 受管理平台策略
- 实现连接器操作的适当错误处理
- 使用 PAC CLI 生成的 TypeScript 模型和服务
- 包含正确异步初始化和错误处理的 PowerProvider

## 交付物

1. 完整的项目脚手架，包含所有必要文件
2. 带连接器集成的可工作示例应用
3. 全面文档和设置说明
4. 开发和部署脚本
5. 优化 Power Apps 代码应用的 TypeScript 配置
6. 最佳实践实现示例

确保生成的项目遵循微软官方 Power Apps 代码应用文档和 https://github.com/microsoft/PowerAppsCodeApps 的示例，并且可以使用 `pac code push` 命令成功部署到 Power Platform。
