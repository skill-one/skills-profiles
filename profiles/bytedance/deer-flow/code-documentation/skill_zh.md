# 代码文档技能

## 概述

该技能可生成专业、全面的软件项目、代码库、库和 API 文档。它遵循 React、Django、Stripe 和 Kubernetes 等项目中的行业最佳实践，以生成准确、结构良好且对新手贡献者和经验丰富的开发者都有用的文档。

输出范围从单文件 README 到多文档开发者指南，始终与项目的复杂性和用户需求相匹配。

## 核心功能

- 生成包含徽章、安装说明、使用方法和 API 参考的综合 README.md 文件
- 从源代码分析创建 API 参考文档
- 生成包含图表的架构和设计文档
- 编写开发者入职和贡献指南
- 从提交历史记录或发布说明中生成变更日志
- 创建遵循特定语言约定的内联代码文档
- 支持 JSDoc、docstrings、GoDoc、Javadoc 和 Rustdoc 格式
- 根据项目的语言和生态系统调整文档风格

## 使用此技能的场景

**始终加载此技能当：**

- 用户要求为任何代码“编写文档”、“创建文档”或“生成文档”
- 用户请求 README、API 参考或开发者指南
- 用户分享代码库或存储库并希望生成文档
- 用户要求改进或更新现有文档
- 用户需要架构文档，包括图表
- 用户请求变更日志或迁移指南

## 文档工作流程

### 第一阶段：代码库分析

在编写任何文档之前，彻底理解代码库。

#### 第 1.1 步：项目发现

识别项目基础信息：

| 字段 | 确定方法 |
|------|----------|
| **语言** | 检查文件扩展名、`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml` 等 |
| **框架** | 查看依赖项以识别已知框架（React、Django、Express、Spring 等） |
| **构建系统** | 检查 `Makefile`、`CMakeLists.txt`、`webpack.config.js`、`build.gradle` 等 |
| **包管理器** | npm/yarn/pnpm、pip/uv/poetry、cargo、go 模块等 |
| **项目结构** | 绘制目录树以了解架构 |
| **入口点** | 找到主文件、CLI 入口点、导出的模块 |
| **现有文档** | 检查现有的 README、docs/、wiki 或内联文档 |

#### 第 1.2 步：代码结构分析

使用沙盒工具探索代码库：

```bash
# 获取目录结构
ls /mnt/user-data/uploads/project-dir/

# 读取关键文件
read_file /mnt/user-data/uploads/project-dir/package.json
read_file /mnt/user-data/uploads/project-dir/pyproject.toml

# 搜索公共 API 表面
grep -r "export " /mnt/user-data/uploads/project-dir/src/
grep -r "def " /mnt/user-data/uploads/project-dir/src/ --include="*.py"
grep -r "func " /mnt/user-data/uploads/project-dir/ --include="*.go"
```

#### 第 1.3 步：确定文档范围

根据分析结果，确定要生成的文档类型：

| 项目规模 | 推荐文档 |
|---------|----------|
| **单文件/脚本** | 内联注释 + 使用说明 |
| **小型库** | README + API 参考 |
| **中型项目** | README + API 文档 + 示例 |
| **大型项目** | README + 架构 + API + 贡献 + 变更日志 |

### 第二阶段：文档生成

#### 第 2.1 步：README 生成

每个项目都需要 README。遵循以下结构：

```markdown
# 项目名称

[一句话项目描述——它是什么、为什么重要]

[![徽章](链接)](#) [![徽章](链接)](#)

## 功能

- [关键功能 1——简短描述]
- [关键功能 2——简短描述]
- [关键功能 3——简短描述]

## 快速入门

### 前置条件

- [前置条件 1 + 版本要求]
- [前置条件 2 + 版本要求]

### 安装

[可复制粘贴的安装命令代码块]

### 基本使用

[展示核心功能的极简工作示例]

## 文档

- [链接到完整的 API 参考（如果单独）]
- [链接到架构文档（如果单独）]
- [链接到示例目录（如果适用）]

## API 参考

[小型项目的内联 API 参考，或链接到生成的文档]

## 配置

[环境变量、配置文件或运行时选项]

## 示例

[2-3 个覆盖常见用例的实用示例]

## 开发

### 设置

[如何设置开发环境]

### 测试

[如何运行测试]

### 构建

[如何构建项目]

## 贡献

[贡献指南或链接到 CONTRIBUTING.md]

## 许可证

[许可证信息]
```

#### 第 2.2 步：API 参考生成

为每个公共 API 表面文档化：

**函数/方法文档**：

```markdown
### `functionName(param1, param2, options?)`

该函数的简短描述。

**参数**：

| 参数 | 类型 | 必填 | 默认 | 描述 |
|------|------|------|------|------|
| `param1` | `string` | 是 | — | `param1` 的描述 |
| `param2` | `number` | 是 | — | `param2` 的描述 |
| `options` | `Object` | 否 | `{}` | 配置选项 |
| `options.timeout` | `number` | 否 | `5000` | 毫秒级超时 |

**返回**： `Promise<Result>` — 返回值的描述

**抛出**：
- `ValidationError` — 当 `param1` 为空时
- `TimeoutError` — 当操作超时时

**示例**：

\`\`\`javascript
const result = await functionName("hello", 42, { timeout: 10000 });
console.log(result.data);
\`\`\`
```

**类文档**：

```markdown
### `ClassName`

类的简短描述及其用途。

**构造函数**：

\`\`\`javascript
new ClassName(config)
\`\`\`

| 参数 | 类型 | 描述 |
|------|------|------|
| `config.option1` | `string` | 描述 |
| `config.option2` | `boolean` | 描述 |

**方法**：

- [`method1()`](#method1) — 简短描述
- [`method2(param)`](#method2) — 简短描述

**属性**：

| 属性 | 类型 | 描述 |
|------|------|------|
| `property1` | `string` | 描述 |
| `property2` | `number` | 只读。描述 |
```

#### 第 2.3 步：架构文档

对于中型到大型项目，包括架构文档：

```markdown
# 架构概述

## 系统图表

[包含一个 Mermaid 图表，展示高级架构]

\`\`\`mermaid
graph TD
    A[客户端] --> B[API 网关]
    B --> C[服务 A]
    B --> D[服务 B]
    C --> E[(数据库)]
    D --> E
\`\`\`

## 组件概述

### 组件名称
- **目的**：该组件的作用
- **位置**：`src/components/name/`
- **依赖项**：它依赖的内容
- **公共 API**：关键导出或接口

## 数据流

[描述关键操作中数据如何通过系统流动]

## 设计决策

### 决策标题
- **背景**：导致此决策的情况
- **决策**：做出的决定
- **理由**：选择此方法的原因
- **权衡**：牺牲了什么
```

#### 第 2.4 步：内联代码文档

生成语言特定的内联文档：

**Python（Google 风格的 docstrings）**：
```python
def process_data(input_path: str, options: dict | None = None) -> ProcessResult:
    """从给定文件路径处理数据。

    读取输入文件，根据提供的选项应用转换，并返回结构化结果对象。

    Args:
        input_path: 输入数据文件的绝对路径。
            支持的格式：CSV、JSON 和 Parquet。
        options: 可选配置字典。
            - "validate" (bool): 启用输入验证。默认为 True。
            - "format" (str): 输出格式 ("json" 或 "csv")。默认为 "json"。

    Returns:
        包含转换数据元数据的 ProcessResult。

    Raises:
        FileNotFoundError: 如果 input_path 不存在。
        ValidationError: 如果启用验证且数据格式不正确。

    示例：
        >>> result = process_data("/data/input.csv", {"validate": True})
        >>> print(result.row_count)
        1500
    """
```

**TypeScript（JSDoc / TSDoc）**：
```typescript
/**
 * 从 API 获取用户数据并转换为显示格式。
 *
 * @param userId - 用户的唯一标识符
 * @param options - 配置获取操作的选项
 * @param options.includeProfile - 是否包含完整配置。默认为 `false`。
 * @param options.cache - 缓存持续时间（秒）。设为 `0` 则禁用。
 * @returns 准备好渲染的转换后用户数据
 * @throws {NotFoundError} 当用户 ID 不存在时
 * @throws {NetworkError} 当 API 不可达时
 *
 * @example
 * ```ts
 * const user = await fetchUser("usr_123", { includeProfile: true });
 * console.log(user.displayName);
 * ```
 */
```

**Go（GoDoc）**：
```go
// ProcessData 读取给定路径的输入文件，应用指定的转换，并返回处理结果。
//
// 输入路径必须是 CSV 或 JSON 文件的绝对路径。
// 如果 options 为 nil，则使用默认选项。
//
// ProcessData 如果文件不存在或无法解析，将返回错误。
func ProcessData(inputPath string, options *ProcessOptions) (*Result, error) {
```

### 第三阶段：质量保证

#### 第 3.1 步：文档完整性检查

验证文档是否涵盖：

- [ ] **它是什么** — 新手能理解的清晰项目描述
- [ ] **它为什么存在** — 解决的问题和价值主张
- [ ] **如何安装** — 可复制粘贴的安装命令
- [ ] **如何使用** — 至少一个展示核心功能的最小工作示例
- [ ] **API 表面** — 所有公共函数、类和类型都已文档化
- [ ] **配置** — 所有环境变量、配置文件和选项
- [ ] **错误处理** — 常见错误及解决方法
- [ ] **贡献** — 如何设置开发环境和提交更改

#### 第 3.2 步：质量标准

| 标准 | 检查 |
|------|------|
| **准确性** | 每个代码示例必须与描述的 API 完全兼容 |
| **完整性** | 没有公共 API 表面未被文档化 |
| **一致性** | 全部使用相同的格式和结构 |
| **时效性** | 文档与当前代码一致，而非旧版本 |
| **可访问性** | 无专业术语，首次使用时解释缩写 |
| **示例** | 每个复杂概念至少有一个实用示例 |

#### 第 3.3 步：交叉引用验证

确保：

- 所有提及的文件路径在项目中存在
- 所有引用的函数和类在代码中存在
- 所有代码示例使用正确的函数签名
- 版本号与项目的实际版本一致
- 所有链接（内部和外部）都有效

## 文档风格指南

### 写作原则

1. **先说“为什么”** — 在解释如何工作之前，先解释它为什么存在
2. **渐进式披露** — 从简单开始，逐步增加复杂性
3. **展示而非说明** — 优先使用代码示例而非冗长解释
4. **使用主动语态** — “函数返回 X”而非“X 由函数返回”
5. **现在时态** — “服务器在 8080 端口启动”而非“服务器将启动在 8080 端口”
6. **第二人称** — “你可以配置…”而非“用户可以配置…”

### 格式规则

- 使用 ATX 风格标题（`#`、`##`、`###`）
- 使用带语言指定的代码块（` ```python `、` ```bash `）
- 使用表格表示结构化信息（参数、选项、配置）
- 使用提示框表示重要注释、警告和技巧
- 保持行长度可读（源代码中约 80-100 字符）
- 使用 `code formatting` 格式化函数名、文件路径、变量名和 CLI 命令

### 语言特定约定

| 语言 | 文档格式 | 风格指南 |
|------|----------|----------|
| Python | Google-style docstrings | PEP 257 |
| TypeScript/JavaScript | TSDoc / JSDoc | TypeDoc 约定 |
| Go | GoDoc 评论 | Effective Go |
| Rust | Rustdoc (`///`) | Rust API 指南 |
| Java | Javadoc | Oracle Javadoc 指南 |
| C/C++ | Doxygen | Doxygen 手册 |

## 输出处理

生成后：

- 将文档文件保存到 `/mnt/user-data/outputs/`
- 对于多文件文档，保持项目目录结构
- 使用 `present_files` 工具向用户展示生成的文件
- 提供迭代特定部分或调整详细程度的选项
- 建议可能具有价值的额外文档

## 注意事项

- 始终在编写文档前分析实际代码——不要猜测 API 签名或行为
- 现有文档存在时，除非用户明确要求重写，否则保留其结构
- 对于大型代码库，优先文档化公共 API 表面和关键抽象
- 文档应使用与项目现有文档相同的语言；若无，默认为英文
- 生成变更日志时，使用 [Keep a Changelog](https://keepachangelog.com/) 格式
- 此技能与 `deep-research` 技能结合使用，可更好地文档化第三方集成或依赖项
