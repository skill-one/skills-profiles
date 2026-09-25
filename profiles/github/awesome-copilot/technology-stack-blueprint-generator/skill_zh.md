# 综合技术栈蓝图生成器

## 配置变量
${PROJECT_TYPE="自动检测|.NET|Java|JavaScript|React.js|React Native|Angular|Python|其他"} <!-- 主要技术 -->
${DEPTH_LEVEL="基础|标准|综合|即实施就绪"} <!-- 分析深度 -->
${INCLUDE_VERSIONS=true|false} <!-- 包含版本信息 -->
${INCLUDE_LICENSES=true|false} <!-- 包含许可证信息 -->
${INCLUDE_DIAGRAMS=true|false} <!-- 生成架构图 -->
${INCLUDE_USAGE_PATTERNS=true|false} <!-- 包含代码使用模式 -->
${INCLUDE_CONVENTIONS=true|false} <!-- 文档编码规范 -->
${OUTPUT_FORMAT="Markdown|JSON|YAML|HTML"} <!-- 选择输出格式 -->
${CATEGORIZATION="技术类型|层级|用途"} <!-- 组织方法 -->

## 生成的提示

"分析代码库并生成 ${DEPTH_LEVEL} 级别的技术栈蓝图，全面记录技术和实施模式，以促进一致的代码生成。使用以下方法：

### 1. 技术识别阶段
- ${PROJECT_TYPE == "自动检测" ? "扫描代码库中的项目文件、配置文件和依赖项，以确定所有使用的技术栈" : "专注于 ${PROJECT_TYPE} 技术"}
- 通过检查文件扩展名和内容识别所有编程语言
- 分析配置文件（package.json、.csproj、pom.xml 等）以提取依赖项
- 检查构建脚本和管道定义以获取工具信息
- ${INCLUDE_VERSIONS ? "从包文件和配置中提取精确的版本信息" : "跳过版本细节"}
- ${INCLUDE_LICENSES ? "记录所有依赖项的许可证信息" : ""}

### 2. 核心技术分析

${PROJECT_TYPE == ".NET" || PROJECT_TYPE == "自动检测" ? "#### .NET 技术栈分析（如果检测到）
- 目标框架和语言版本（从项目文件检测）
- 所有 NuGet 包引用及其版本和目的注释
- 项目结构和组织模式
- 配置方法（appsettings.json、IOptions 等）
- 身份验证机制（Identity、JWT 等）
- API 设计模式（REST、GraphQL、最小 API 等）
- 数据访问方法（EF Core、Dapper 等）
- 依赖注入模式
- 中间件管道组件" : ""}

${PROJECT_TYPE == "Java" || PROJECT_TYPE == "自动检测" ? "#### Java 技术栈分析（如果检测到）
- JDK 版本和核心框架
- 所有 Maven/Gradle 依赖项及其版本和目的
- 包结构组织
- Spring Boot 使用和配置
- 注解模式
- 依赖注入方法
- 数据访问技术（JPA、JDBC 等）
- API 设计（Spring MVC、JAX-RS 等）" : ""}

${PROJECT_TYPE == "JavaScript" || PROJECT_TYPE == "自动检测" ? "#### JavaScript 技术栈分析（如果检测到）
- ECMAScript 版本和转译器设置
- 所有 npm 依赖项按目的分类
- 模块系统（ESM、CommonJS）
- 构建工具（webpack、Vite 等）及其配置
- TypeScript 使用和配置
- 测试框架和模式" : ""}

${PROJECT_TYPE == "React.js" || PROJECT_TYPE == "自动检测" ? "#### React 分析（如果检测到）
- React 版本和关键模式（钩子 vs 类组件）
- 状态管理方法（Context、Redux、Zustand 等）
- 组件库使用（Material-UI、Chakra 等）
- 路由实现
- 表单处理策略
- API 集成模式
- 组件测试方法" : ""}

${PROJECT_TYPE == "Python" || PROJECT_TYPE == "自动检测" ? "#### Python 分析（如果检测到）
- Python 版本和使用的关键语言特性
- 包依赖项和虚拟环境设置
- Web 框架细节（Django、Flask、FastAPI）
- ORM 使用模式
- 项目结构组织
- API 设计模式" : ""}

### 3. 实施模式与规范
${INCLUDE_CONVENTIONS ? 
"记录每个技术领域的编码规范和模式：

#### 命名规范
- 类/类型命名模式
- 方法/函数命名模式
- 变量命名规范
- 文件命名和组织规范
- 接口/抽象类模式

#### 代码组织
- 文件结构和组织
- 文件夹层次模式
- 组件/模块边界
- 代码分离和责任模式

#### 常见模式
- 错误处理方法
- 日志模式
- 配置访问
- 身份验证/授权实现
- 验证策略
- 测试模式" : ""}

### 4. 使用示例
${INCLUDE_USAGE_PATTERNS ? 
"提取展示标准实施模式的代表性代码示例：

#### API 实施示例
- 标准控制器/端点实现
- 请求 DTO 模式
- 响应格式化
- 验证方法
- 错误处理

#### 数据访问示例
- 仓库模式实现
- 实体/模型定义
- 查询模式
- 事务处理

#### 服务层示例
- 服务类实现
- 业务逻辑组织
- 跨领域关注点集成
- 依赖注入使用

#### UI 组件示例（如果适用）
- 组件结构
- 状态管理模式
- 事件处理
- API 集成模式" : ""}

### 5. 技术栈映射
${DEPTH_LEVEL == "综合" || DEPTH_LEVEL == "即实施就绪" ? 
"创建全面的技术映射，包括：

#### 核心框架使用
- 主要框架及其在项目中的具体使用
- 框架特定配置和自定义
- 扩展点和自定义

#### 集成点
- 不同技术组件如何集成
- 组件之间的身份验证流程
- 前端和后端之间的数据流
- 第三方服务集成模式

#### 开发工具
- IDE 设置和规范
- 代码分析工具
- 代码检查器和格式化工具及其配置
- 构建和部署管道
- 测试框架和方法

#### 基础设施
- 部署环境细节
- 容器技术
- 使用的云服务
- 监控和日志基础设施" : ""}

### 6. 技术特定实施细节

${PROJECT_TYPE == ".NET" || PROJECT_TYPE == "自动检测" ? 
"#### .NET 实施细节（如果检测到）
- **依赖注入模式**:
  - 服务注册方法（Scoped/Singleton/Transient 模式）
  - 配置绑定模式
  
- **控制器模式**:
  - 基类控制器使用
  - 动作结果类型和模式
  - 路由属性规范
  - 过滤器使用（授权、验证等）
  
- **数据访问模式**:
  - ORM 配置和使用
  - 实体配置方法
  - 关系定义
  - 查询模式和优化方法
  
- **API 设计模式**（如果使用）:
  - 端点组织
  - 参数绑定方法
  - 响应类型处理
  
- **语言特性使用**:
  - 从代码检测特定语言特性
  - 识别常见模式和习语
  - 注记任何特定于版本的特性" : ""}

${PROJECT_TYPE == "React.js" || PROJECT_TYPE == "自动检测" ? 
"#### React 实施细节（如果检测到）
- **组件结构**:
  - 函数 vs 类组件
  - Props 接口定义
  - 组件组合模式
  
- **钩子使用模式**:
  - 自定义钩子实现风格
  - useState 模式
  - useEffect 清理方法
  - Context 使用模式
  
- **状态管理**:
  - 本地 vs 全局状态决策
  - 状态管理库模式
  - 存储配置
  - 选择器模式
  
- **样式方法**:
  - CSS 方法（CSS 模块、styled-components 等）
  - 主题实现
  - 响应式设计模式" : ""}

### 7. 新代码实施蓝图
${DEPTH_LEVEL == "即实施就绪" ? 
"基于分析，提供实施新功能的详细蓝图：

- **文件/类模板**: 常见组件类型的标准结构
- **代码片段**: 常见操作的即用型代码模式
- **实施检查清单**: 实施端到端功能的标准步骤
- **集成点**: 如何将新代码与现有系统集成
- **测试要求**: 不同组件类型的标准测试模式
- **文档要求**: 新功能的标凈文档模式" : ""}

${INCLUDE_DIAGRAMS ? 
"### 8. 技术关系图
- **栈图**: 完整技术栈的视觉表示
- **依赖流**: 不同技术如何交互
- **组件关系**: 主要组件如何依赖彼此
- **数据流**: 数据如何流经技术栈" : ""}

### ${INCLUDE_DIAGRAMS ? "9" : "8"}. 技术决策背景
- 记录技术选择明显的原因
- 注记标记为替换的遗留或过时技术
- 识别技术约束和边界
- 记录技术升级路径和兼容性考虑

以 ${OUTPUT_FORMAT} 格式化输出，并按 ${CATEGORIZATION} 对技术进行分类。

将输出保存为 'Technology_Stack_Blueprint.${OUTPUT_FORMAT == "Markdown" ? "md" : OUTPUT_FORMAT.toLowerCase()}'
"
