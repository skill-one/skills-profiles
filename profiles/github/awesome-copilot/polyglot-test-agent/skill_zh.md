# 多语言测试生成技能

一种使用协调的多智能体管道为任何编程语言生成全面、可工作的单元测试的人工智能技能。

## 使用此技能的场景

当你需要时使用此技能：
- 为整个项目或特定文件生成单元测试
- 提高现有代码库的测试覆盖率
- 创建遵循项目约定的测试文件
- 编写实际可以编译和通过的测试
- 为新功能或未测试的代码添加测试

## 工作原理

此技能协调多个专业智能体，按照**研究 → 规划 → 实现**的管道流程工作：

### 管道概述

```
┌─────────────────────────────────────────────────────────────┐
│                     测试生成器                          │
│ 协调整个管道并管理状态                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────────┐
│ 研究者   │  │  规划者   │  │  实现者   │
│           │  │           │  │               │
│ 分析代码库 │  │ 创建分阶段的 │  │ 按阶段编写测试 │
│           │  │ 计划      │→ │               │
└───────────┘  └───────────┘  └───────┬───────┘
                                      │
                    ┌─────────┬───────┼───────────┐
                    ▼         ▼       ▼           ▼
              ┌─────────┐ ┌───────┐ ┌───────┐ ┌───────┐
              │ 构建者   │ │ 测试者 │ │ 修复者 │ │ 格式化工具 │
              │         │ │       │ │       │ │       │
              │ 编译代码 │ │ 运行测试 │ │ 修复错误 │ │ 格式化代码 │
              └─────────┘ └───────┘ └───────┘ └───────┘
```

## 分步说明

### 第 1 步：确定用户请求

确保你理解用户请求的内容和范围。
当用户对测试风格、覆盖率目标或约定没有明确要求时，从 [unit-test-generation.prompt.md](unit-test-generation.prompt.md) 中获取指南。此提示提供了发现约定、参数化策略、覆盖率目标（目标为 80%）和特定语言模式的最佳实践。

### 第 2 步：调用测试生成器

首先使用你的测试生成请求调用 `polyglot-test-generator` 智能体：

```
为 [要测试的路径或描述] 生成单元测试，遵循 [unit-test-generation.prompt.md](unit-test-generation.prompt.md) 指南
```

测试生成器将自动管理整个管道。

### 第 3 步：研究阶段（自动）

`polyglot-test-researcher` 智能体分析你的代码库以理解：
- **语言 & 框架**：检测 C#、TypeScript、Python、Go、Rust、Java 等
- **测试框架**：识别 MSTest、xUnit、Jest、pytest、go test 等
- **项目结构**：映射源文件、现有测试和依赖项
- **构建命令**：发现如何构建和测试项目

输出：`.testagent/research.md`

### 第 4 步：规划阶段（自动）

`polyglot-test-planner` 智能体创建结构化的实现计划：
- 将文件分组为逻辑阶段（典型为 2-5 个阶段）
- 按复杂性和依赖项进行优先级排序
- 为每个文件指定测试用例
- 定义每个阶段的成功标准

输出：`.testagent/plan.md`

### 第 5 步：实现阶段（自动）

`polyglot-test-implementer` 智能体按顺序执行每个阶段：

1. **读取** 源文件以理解 API
2. **编写** 遵循项目模式的测试文件
3. 使用 `polyglot-test-builder` 子智能体**构建**以验证编译
4. 使用 `polyglot-test-tester` 子智能体**运行**测试以验证测试通过
5. 如果出现错误，使用 `polyglot-test-fixer` 子智能体**修复**错误
6. 使用 `polyglot-test-linter` 子智能体**格式化**代码

每个阶段完成后再开始下一个阶段，确保渐进式进展。

### 覆盖类型
- **常规路径**：有效输入产生预期输出
- **边界情况**：空值、边界、特殊字符
- **错误情况**：无效输入、空值处理、异常

## 状态管理

所有管道状态存储在 `.testagent/` 文件夹中：

| 文件 | 目的 |
|------|------|
| `.testagent/research.md` | 代码库分析结果 |
| `.testagent/plan.md` | 分阶段实现计划 |
| `.testagent/status.md` | 进度跟踪（可选） |

## 示例

### 示例 1：完整项目测试
```
为 C:\src\Calculator 中的 Calculator 项目生成单元测试
```

### 示例 2：特定文件测试
```
为 src/services/UserService.ts 生成单元测试
```

### 示例 3：目标覆盖
```
为认证模块添加测试，重点关注边界情况
```

## 智能体参考

| 智能体 | 目的 | 工具 |
|-------|------|------|
| `polyglot-test-generator` | 协调管道 | runCommands, codebase, editFiles, search, runSubagent |
| `polyglot-test-researcher` | 分析代码库 | runCommands, codebase, editFiles, search, fetch, runSubagent |
| `polyglot-test-planner` | 创建测试计划 | codebase, editFiles, search, runSubagent |
| `polyglot-test-implementer` | 编写测试文件 | runCommands, codebase, editFiles, search, runSubagent |
| `polyglot-test-builder` | 编译代码 | runCommands, codebase, search |
| `polyglot-test-tester` | 运行测试 | runCommands, codebase, search |
| `polyglot-test-fixer` | 修复错误 | runCommands, codebase, editFiles, search |
| `polyglot-test-linter` | 格式化代码 | runCommands, codebase, search |

## 要求

- 项目必须配置构建/测试系统
- 测试框架应已安装（或可安装）
- 配备 GitHub Copilot 扩展的 VS Code

## 故障排除

### 测试无法编译
`polyglot-test-fixer` 智能体会尝试解决编译错误。检查 `.testagent/plan.md` 以获取预期的测试结构。

### 测试失败
查看测试输出并调整测试预期。某些测试可能需要模拟依赖项。

### 检测到错误的测试框架
在初始请求中指定你首选的框架："为...生成 Jest 测试"
