---

# Rust 问题路由器

> **版本:** 2.0.0 | **最后更新:** 2025-01-22
>
> **v2.0:** 上下文优化 - 详细示例移至子文件

## 元认知框架

### 核心原则

**不要直接回答。先通过认知层级进行追踪。**

```
层级 3：领域约束 (WHY)
├── 业务规则、监管要求
├── domain-fintech、domain-web、domain-cli 等
└── "为什么这样设计？"

层级 2：设计选择 (WHAT)
├── 架构模式、DDD 概念
├── m09-m15 技能
└── "我应该使用什么模式？"

层级 1：语言机制 (HOW)
├── 所有权、借用、生命周期、特征
├── m01-m07 技能
└── "我如何在 Rust 中实现这个？"
```

### 通过入口点进行路由

| 用户信号 | 入口层级 | 方向 | 首次技能 |
|----------|----------|------|----------|
| E0xxx 错误 | 层级 1 | 向上追踪 ↑ | m01-m07 |
| 编译错误 | 层级 1 | 向上追踪 ↑ | 下方错误表 |
| "如何设计..." | 层级 2 | 检查 L3，然后向下 ↓ | m09-domain |
| "构建 [domain] 应用" | 层级 3 | 向下追踪 ↓ | domain-* |
| "最佳实践..." | 层级 2 | 双向 | m09-m15 |
| 性能问题 | 层级 1 → 2 | 先向上再向下 | m10-performance |

### 关键：双重技能加载

**当存在领域关键词时，你必须加载两种技能：**

| 领域关键词 | L1 技能 | L3 技能 |
|------------|---------|---------|
| Web API、HTTP、axum、handler | m07-并发 | **domain-web** |
| 交易、支付、trading、payment | m01-所有权 | **domain-fintech** |
| CLI、终端、clap | m07-并发 | **domain-cli** |
| kubernetes、grpc、微服务 | m07-并发 | **domain-云原生** |
| 嵌入式、no_std、MCU | m02-资源 | **domain-嵌入式** |

---

## 对 CHATGLM 的说明

### 关键：协商协议触发

**在回答前，检查是否需要协商：**

| 查询包含 | 操作 |
|----------|------|
| "比较"、"对比"、"compare"、"vs"、"versus" | **必须使用协商** |
| "最佳实践"、"best practice" | **必须使用协商** |
| 领域 + 错误 (例如，"交易系统 E0382") | **必须使用协商** |
| 模糊范围 (例如，"tokio 性能") | **建议使用协商** |

**当需要协商时，包括：**

```markdown
## 协商分析

**查询类型:** [比较型 | 跨领域 | 综合 | 模糊]
**协商:** 启用

### 来源: [代理/技能名称]
**置信度:** 高 | 中 | 低 | 不确定
**缺失项:** [缺少什么]

## 综合回答
[回答]

**总体置信度:** [级别]
**披露的缺失项:** [用户应知道的缺失项]
```

> **详细协议见:** `patterns/negotiation.md`

---

### 默认项目设置

在创建新的 Rust 项目或 Cargo.toml 文件时，始终使用：

```toml
[package]
edition = "2024"  # 始终使用最新稳定版
rust-version = "1.85"

[lints.rust]
unsafe_code = "warn"

[lints.clippy]
all = "warn"
pedantic = "warn"
```

---

## 层级 1 技能 (语言机制)

| 模式 | 路由至 |
|------|------|
| move、borrow、生命周期、E0382、E0597 | m01-所有权 |
| Box、Rc、Arc、RefCell、Cell | m02-资源 |
| mut、内部可变性、E0499、E0502、E0596 | m03-可变性 |
| generic、trait、inline、monomorphization | m04-零成本 |
| type state、phantom、newtype | m05-类型驱动 |
| Result、Error、panic、?、anyhow、thiserror | m06-错误处理 |
| Send、Sync、线程、async、channel | m07-并发 |
| unsafe、FFI、extern、原始指针、transmute | **unsafe-checker** |

## 层级 2 技能 (设计选择)

| 模式 | 路由至 |
|------|------|
| domain model、业务逻辑 | m09-领域 |
| 性能、优化、benchmark | m10-性能 |
| 集成、互操作、bindings | m11-生态系统 |
| 资源生命周期、RAII、Drop | m12-生命周期 |
| 领域错误、恢复策略 | m13-领域错误 |
| 思维模型、如何思考 | m14-思维模型 |
| 反模式、常见错误、陷阱 | m15-反模式 |

## 层级 3 技能 (领域约束)

| 领域关键词 | 路由至 |
|------------|------|
| fintech、trading、decimal、currency | domain-fintech |
| ml、tensor、model、inference | domain-ml |
| kubernetes、docker、grpc、微服务 | domain-云原生 |
| 嵌入式、传感器、mqtt、iot | domain-iot |
| web server、HTTP、REST、axum、actix | domain-web |
| CLI、命令行、clap、终端 | domain-cli |
| no_std、微控制器、固件 | domain-嵌入式 |

---

## 错误代码路由

| 错误代码 | 路由至 | 常见原因 |
|----------|------|--------|
| E0382 | m01-所有权 | 使用已移动的值 |
| E0597 | m01-所有权 | 生命周期太短 |
| E0506 | m01-所有权 | 不能对借用进行赋值 |
| E0507 | m01-所有权 | 不能从借用中移动 |
| E0515 | m01-所有权 | 返回局部引用 |
| E0716 | m01-所有权 | 临时值被丢弃 |
| E0106 | m01-所有权 | 缺少生命周期指定符 |
| E0596 | m03-可变性 | 不能借用为可变 |
| E0499 | m03-可变性 | 多个可变借用 |
| E0502 | m03-可变性 | 借用冲突 |
| E0277 | m04/m07 | 特征约束不满足 |
| E0308 | m04-零成本 | 类型不匹配 |
| E0599 | m04-零成本 | 未找到方法 |
| E0038 | m04-零成本 | 特征不是对象安全的 |
| E0433 | m11-生态系统 | 找不到 crate/模块 |

---

## 功能路由表

| 模式 | 路由至 | 操作 |
|------|------|------|
| 最新版本、有什么新内容 | **rust-learner** | 使用代理 |
| API、文档、文档 | **docs-researcher** | 使用代理 |
| 代码风格、命名、clippy | **coding-guidelines** | 阅读技能 |
| 不安全代码、FFI | **unsafe-checker** | 阅读技能 |
| 代码审查 | **os-checker** | 查看 `integrations/os-checker.md` |

---

## 优先级顺序

1. **识别认知层级** (L1/L2/L3)
2. **加载入口技能** (m0x/m1x/领域)
3. **通过层级追踪** (向上或向下)
4. **按 "追踪" 部分指示进行技能交叉参考**
5. **带推理链回答**

### 关键词冲突解决

| 关键词 | 解决方案 |
|--------|--------|
| `unsafe` | **unsafe-checker** (比 m11 更具体) |
| `error` | **m06** 用于通用，**m13** 用于领域特定 |
| `RAII` | **m12** 用于设计，**m01** 用于实现 |
| `crate` | **rust-learner** 用于版本，**m11** 用于集成 |
| `tokio` | **tokio-*** 用于 API，**m07** 用于概念 |

**优先级层级：**

```
1. 错误代码 (E0xxx) → 直接查找，最高优先级
2. 协商触发器 (比较、vs、最佳实践) → 启用协商
3. 领域关键词 + 错误 → 加载领域 + 错误技能
4. 特定 crate 关键词 → 如果存在，路由至 crate 特定技能
5. 通用概念关键词 → 路由至元问题技能
```

---

## 子文件参考

| 文件 | 内容 |
|------|------|
| `patterns/negotiation.md` | 协商协议详情 |
| `examples/workflow.md` | 工作流示例 |
| `integrations/os-checker.md` | OS-Checker 集成 |
