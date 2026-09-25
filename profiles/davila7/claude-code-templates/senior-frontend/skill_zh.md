# 高级前端

为高级前端开发者提供的现代工具和最佳实践完整工具包。

## 快速入门

### 主要功能

该技能通过自动化脚本提供三种核心功能：

```bash
# 脚本 1：组件生成器
python scripts/component_generator.py [选项]

# 脚本 2：包分析器
python scripts/bundle_analyzer.py [选项]

# 脚本 3：前端脚手架生成器
python scripts/frontend_scaffolder.py [选项]
```

## 核心功能

### 1. 组件生成器

用于组件生成任务的自动化工具。

**功能：**
- 自动化脚手架
- 内置最佳实践
- 可配置模板
- 质量检查

**使用方法：**
```bash
python scripts/component_generator.py <项目路径> [选项]
```

### 2. 包分析器

全面的分析和优化工具。

**功能：**
- 深度分析
- 性能指标
- 建议
- 自动修复

**使用方法：**
```bash
python scripts/bundle_analyzer.py <目标路径> [--verbose]
```

### 3. 前端脚手架生成器

用于专业任务的先进工具。

**功能：**
- 专家级自动化
- 自定义配置
- 集成准备就绪
- 生产级输出

**使用方法：**
```bash
python scripts/frontend_scaffolder.py [参数] [选项]
```

## 参考文档

### React 模式

在 `references/react_patterns.md` 中提供的全面指南：

- 详细模式和最佳实践
- 代码示例
- 最佳实践
- 需避免的反模式
- 真实场景

### Next.js 优化指南

在 `references/nextjs_optimization_guide.md` 中提供的完整工作流文档：

- 步骤详解
- 优化策略
- 工具集成
- 性能调优
- 故障排除指南

### 前端最佳实践

在 `references/frontend_best_practices.md` 中的技术参考指南：

- 技术栈细节
- 配置示例
- 集成模式
- 安全考虑
- 可扩展性指南

## 技术栈

**语言：** TypeScript, JavaScript, Python, Go, Swift, Kotlin
**前端：** React, Next.js, React Native, Flutter
**后端：** Node.js, Express, GraphQL, REST API
**数据库：** PostgreSQL, Prisma, NeonDB, Supabase
**DevOps：** Docker, Kubernetes, Terraform, GitHub Actions, CircleCI
**云：** AWS, GCP, Azure

## 开发工作流

### 1. 设置和配置

```bash
# 安装依赖
npm install
# 或
pip install -r requirements.txt

# 配置环境
cp .env.example .env
```

### 2. 运行质量检查

```bash
# 使用分析器脚本
python scripts/bundle_analyzer.py .

# 查看建议
# 应用修复
```

### 3. 实施最佳实践

遵循在以下文档中记录的模式和最佳实践：
- `references/react_patterns.md`
- `references/nextjs_optimization_guide.md`
- `references/frontend_best_practices.md`

## 最佳实践总结

### 代码质量
- 遵循既定模式
- 编写全面的测试
- 记录决策
- 定期审查

### 性能
- 优化前进行测量
- 使用适当的缓存
- 优化关键路径
- 生产环境中监控

### 安全
- 验证所有输入
- 使用参数化查询
- 实施适当的认证
- 保持依赖项更新

### 可维护性
- 编写清晰的代码
- 使用一致的命名
- 添加有帮助的注释
- 保持简洁

## 常用命令

```bash
# 开发
npm run dev
npm run build
npm run test
npm run lint

# 分析
python scripts/bundle_analyzer.py .
python scripts/frontend_scaffolder.py --analyze

# 部署
docker build -t app:latest .
docker-compose up -d
kubectl apply -f k8s/
```

## 故障排除

### 常见问题

检查 `references/frontend_best_practices.md` 中的全面故障排除部分。

### 获取帮助

- 查看参考文档
- 检查脚本输出消息
- 咨询技术栈文档
- 查看错误日志

## 资源

- 模式参考：`references/react_patterns.md`
- 工作流指南：`references/nextjs_optimization_guide.md`
- 技术指南：`references/frontend_best_practices.md`
- 工具脚本：`scripts/` 目录
