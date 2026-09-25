# gstack 工作流助手

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合

将 Claude Code 从通用助手转变为您可按需召唤的专家团队。八种带有主观倾向的工作流技能，充当CEO、工程经理、发布经理和QA工程师的角色，并提供用于规划、评审、发布和测试的斜杠命令。

## 功能概述

gstack 提供专业的AI角色和工作流：
- **CEO评审**：重新思考问题，在请求中找到隐藏的10星产品
- **工程规划**：锁定架构、数据流和边缘情况
- **代码评审**：偏执的员工级评审，可捕获生产环境错误
- **发布管理**：一键发布，包含测试和PR创建
- **QA测试**：带截图和系统化覆盖的自动化浏览器测试
- **浏览器自动化**：为您的应用添加AI"眼睛"，点击并捕获错误
- **会话管理**：导入真实浏览器cookie进行认证测试
- **团队复盘**：工程经理风格的复盘，包含个人洞察

## 安装

### 依赖项
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Git](https://git-scm.com/)
- [Bun](https://bun.sh/) v1.0+
- macOS或Linux (x64/arm64) 用于浏览器自动化

### 全局安装
```bash
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack
./setup
```

### 项目安装
```bash
cp -Rf ~/.claude/skills/gstack .claude/skills/gstack
rm -rf .claude/skills/gstack/.git
cd .claude/skills/gstack
./setup
```

添加到您的 `CLAUDE.md`：
```markdown
## gstack
使用 gstack 的 /browse 技能进行所有网页浏览。永远不要使用 mcp__claude-in-chrome__* 工具。

可用技能：
- /plan-ceo-review - 产品策略评审
- /plan-eng-review - 技术架构规划  
- /review - 彻底代码评审
- /ship - 一键分支发布
- /browse - 浏览器自动化和测试
- /qa - 系统化QA测试
- /setup-browser-cookies - 会话管理
- /retro - 工程复盘
```

## 核心命令

### 规划工作流

#### CEO产品评审
```typescript
// 从功能描述开始，然后评审策略
You: 我想在列表应用中添加卖家照片上传功能

You: /plan-ceo-review
// AI以CEO身份回应：挑战假设，发现更大的机会
// "照片上传" → "基于照片的AI驱动的列表创建"
```

#### 工程架构评审
```typescript
You: /plan-eng-review
// AI以技术主管身份回应：
// - 架构图
// - 状态机
// - 异步任务边界  
// - 故障模式
// - 测试矩阵
```

### 代码质量工作流

#### 彻底代码评审
```typescript
You: /review
// 偏执的员工级评审：
// - 竞态条件
// - 信任边界
// - 缺失的错误处理
// - 生产环境故障模式
```

#### 一键发布
```typescript
You: /ship
// 自动化发布流程：
// 1. 同步主分支
// 2. 运行测试套件
// 3. 解决评审评论
// 4. 推送分支
// 5. 打开pull request
```

### QA和测试工作流

#### 浏览器自动化
```typescript
You: /browse https://myapp.com
// AI导航您的应用：
// - 拍摄截图
// - 点击工作流
// - 识别错误
// - 测试响应式设计
```

#### 系统化QA测试
```typescript
You: /qa
// 分支感知测试：
// - 分析git diff
// - 识别受影响的页面
// - 测试localhost:3000
// - 全探索模式
// - 回归测试

You: /qa https://staging.myapp.com --quick
// 快速冒烟测试：30秒内测试5个页面
```

#### 会话管理
```typescript
You: /setup-browser-cookies staging.myapp.com
// 从真实浏览器导入cookie（Chrome、Arc、Brave、Edge）
// 允许在不手动登录的情况下测试认证页面
```

### 团队工作流

#### 工程复盘
```typescript
You: /retro
// 工程经理风格的复盘：
// - 分析git历史
// - 每个人的贡献
// - 增长机会
// - 团队动态
// - 保存到 .context/retros/
```

## 配置

### 浏览器设置
gstack 在 `.gstack/` 目录中创建隔离的浏览器实例：
```typescript
// 自动浏览器配置
{
  userDataDir: '.gstack/browser-data',
  headless: false, // 用于调试
  viewport: { width: 1280, height: 720 },
  timeout: 30000
}
```

### 项目结构
```
your-project/
├── .claude/
│   └── skills/
│       └── gstack/
│           ├── skills/           # 工作流提示
│           ├── browse/           # 浏览器自动化
│           └── package.json
├── .gstack/                      # 浏览器数据（git忽略）
│   ├── browser-data/
│   └── screenshots/
└── .context/
    └── retros/                   # 复盘历史
```

## 集成模式

### 多会话工作流
使用 [Conductor](https://conductor.build) 进行并行会话：
```typescript
// 会话1：功能开发
You: /plan-ceo-review
You: /plan-eng-review
// [实现功能]

// 会话2：代码评审
You: /review
// [修复问题]

// 会话3：QA测试  
You: /qa --full

// 会话4：发布
You: /ship
```

### CI/CD集成
```yaml
# .github/workflows/gstack-qa.yml
name: gstack QA
on: [pull_request]
jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: cd .claude/skills/gstack && ./setup
      - run: echo "/qa --regression" | claude-code
```

### 团队入职
```markdown
# 添加到团队文档
## 开发工作流
1. `/plan-ceo-review` - 验证产品方向
2. `/plan-eng-review` - 锁定架构  
3. 实现功能
4. `/review` - 偏执的代码评审
5. `/qa` - 彻底测试分支
6. `/ship` - 一键发布
7. `/qa staging.app.com` - 预发布验证
```

## 高级用法

### 自定义QA场景
```typescript
// 特定功能测试
You: /qa --focus=checkout-flow
You: /qa --mobile-only
You: /qa --accessibility

// 性能测试
You: /browse https://app.com
// 然后： "在这个页面上运行lighthouse审计"
```

### 跨浏览器测试
```typescript
// 在多个浏览器中测试
You: /setup-browser-cookies app.com
You: /browse app.com --browser=chrome
// [切换会话]
You: /browse app.com --browser=firefox
```

### 回归测试
```typescript
// 在进行重大更改前
You: /qa --baseline
// [进行更改]  
You: /qa --compare-baseline
// AI识别视觉/功能回归
```

## 故障排除

### 二进制问题
```bash
# 重建浏览器自动化二进制文件
cd .claude/skills/gstack
rm -rf browse/dist
./setup
```

### 权限错误
```bash
# 修复可执行权限
cd .claude/skills/gstack
chmod +x setup browse/dist/browse
```

### 缺失依赖项
```bash
# 重新安装Node依赖项
cd .claude/skills/gstack
rm -rf node_modules
bun install
```

### 浏览器自动化失败
```typescript
// 调试浏览器问题
You: /browse --debug
// 以非无头模式运行浏览器进行检查

// 清除浏览器数据
rm -rf .gstack/browser-data
```

### 技能注册问题
```typescript
// 重新注册技能
cd .claude/skills/gstack
./setup

// 验证技能是否可用
You: /plan-ceo-review --help
```

这些技能通过提供专业的提示和浏览器自动化工具，将 Claude Code 转变为领域专家。每个工作流强制执行特定的认知模式 - CEO战略思维、工程严谨性、偏执评审或系统化测试 - 而不是通用协助。
