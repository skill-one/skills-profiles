# 清晰代码原则

基础软件设计原则、SOLID、设计模式和清晰代码实践。语言无关的指南，用于编写可维护、可扩展的软件。

## 何时应用

在以下情况下参考这些指南：
- 设计新功能或系统
- 审查代码架构
- 重构现有代码
- 讨论设计决策
- 提高代码质量

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | SOLID原则 | 关键 | `solid-` |
| 2 | 核心原则 | 关键 | `core-` |
| 3 | 设计模式 | 高 | `pattern-` |
| 4 | 代码组织 | 高 | `org-` |
| 5 | 命名与可读性 | 中 | `name-` |
| 6 | 函数与方法 | 中 | `func-` |
| 7 | 注释与文档 | 低 | `doc-` |

## 快速参考

### 1. SOLID原则 (关键)

- `solid-srp` - 单一职责原则
- `solid-ocp` - 开放/封闭原则
- `solid-lsp` - 里氏替换原则
- `solid-isp` - 接口隔离原则
- `solid-dip` - 依赖倒置原则

### 2. 核心原则 (关键)

- `core-dry` - 不要重复自己
- `core-kiss` - 保持简单，愚蠢
- `core-yagni` - 你不需要它
- `core-separation-of-concerns` - 分离不同职责
- `core-composition-over-inheritance` - 偏好组合
- `core-law-of-demeter` - 最少知识原则
- `core-fail-fast` - 早期检测和报告错误
- `core-encapsulation` - 隐藏实现细节

### 3. 设计模式 (高)

- `pattern-factory` - 用于对象创建的工厂模式
- `pattern-strategy` - 用于算法的策略模式
- `pattern-repository` - 用于数据访问的仓库模式
- `pattern-decorator` - 用于行为扩展的装饰器模式
- `pattern-observer` - 用于事件处理的观察者模式
- `pattern-adapter` - 用于接口转换的适配器模式
- `pattern-facade` - 用于简化接口的 фасад模式
- `pattern-dependency-injection` - 用于松散耦合的依赖注入

### 4. 代码组织 (高) — 计划中

- `org-feature-folders` - 按功能组织，而非层次
- `org-module-boundaries` - 清晰的模块边界
- `org-layered-architecture` - 正确的层次分离
- `org-package-cohesion` - 相关代码放在一起
- `org-circular-dependencies` - 避免循环依赖

### 5. 命名与可读性 (中) — 计划中

- `name-meaningful` - 使用意图揭示的名称
- `name-consistent` - 一致的命名规范
- `name-searchable` - 避免魔法数字/字符串
- `name-avoid-encodings` - 无匈牙利记法
- `name-domain-language` - 使用领域术语

### 6. 函数与方法 (中) — 计划中

- `func-small` - 保持函数小
- `func-single-purpose` - 做一件事情
- `func-few-arguments` - 限制参数
- `func-no-side-effects` - 最小化副作用
- `func-command-query` - 分离命令和查询

### 7. 注释与文档 (低) — 计划中

- `doc-self-documenting` - 代码应自解释
- `doc-why-not-what` - 解释原因，而非结果
- `doc-avoid-noise` - 无冗余注释
- `doc-api-docs` - 文档公共API

## 基本指南

有关详细示例和解释，请参阅规则文件：

- [core-dry.md](rules/core-dry.md) - 不要重复自己原则
- [pattern-repository.md](rules/pattern-repository.md) - 用于数据访问的仓库模式

### SOLID原则 (摘要)

| 原则 | 定义 |
|------|------|
| **S**ingle Responsibility | 一个类应该只有一个改变的原因 |
| **O**pen/Closed | 对扩展开放，对修改封闭 |
| **L**iskov Substitution | 子类型必须可替换为基类型 |
| **I**nterface Segregation | 不要强迫客户端依赖未使用的接口 |
| **D**ependency Inversion | 依赖抽象，而非具体 |

### 核心原则 (摘要)

| 原则 | 定义 |
|------|------|
| **DRY** | 不要重复自己 - 单一事实来源 |
| **KISS** | 保持简单 - 避免过度设计 |
| **YAGNI** | 你不需要它 - 只构建需要的 |

### 快速示例

```typescript
// 单一职责 - 一个类，一个工作
class UserService {
  constructor(
    private validator: UserValidator,
    private repository: UserRepository,
  ) {}

  createUser(data) {
    this.validator.validate(data);
    return this.repository.create(data);
  }
}

// 依赖倒置 - 依赖抽象
interface Repository<T> {
  find(id: string): Promise<T | null>;
  save(entity: T): Promise<T>;
}

class OrderService {
  constructor(private repository: Repository<Order>) {}
}

// DRY - 单一事实来源
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const isValidEmail = (email: string) => EMAIL_REGEX.test(email);

// 有意义的名称胜过魔法数字
const MINIMUM_AGE = 18;
if (user.age >= MINIMUM_AGE) { }
```

## 输出格式

在审计代码时，以以下格式输出发现：

```
文件:行 - [原则] 问题描述
```

示例：
```
src/services/UserService.ts:15 - [solid-srp] 类处理验证、持久化和通知
src/utils/helpers.ts:42 - [core-dry] 电子邮件验证重复自 validators/email.ts
src/models/Order.ts:28 - [name-meaningful] 变量 'x' 应描述其用途
```

## 如何使用

阅读单个规则文件以获取详细解释：

```
rules/solid-srp-class.md
rules/core-dry.md
rules/pattern-repository.md
```

## 参考文献

这项技能基于成熟的软件工程原则：

### 核心书籍
- **清晰代码** by Robert C. Martin - 清晰代码实践的基础
- **设计模式** by 四人帮 - 经典设计模式目录
- **重构** by Martin Fowler - 改善代码结构
- **实用主义程序员** by Hunt & Thomas - 实用智慧

### 在线资源
- [重构大师](https://refactoring.guru/) - 设计模式和代码异味
- [Martin Fowler的重构目录](https://refactoring.com/catalog/) - 综合重构技术
- [Uncle Bob的清晰程序员博客](https://blog.cleancoder.com/) - 软件工艺文章

### 模式目录
- [重构大师 - 设计模式](https://refactoring.guru/design-patterns)
- [Martin Fowler - 企业模式](https://martinfowler.com/eaaCatalog/)

## 元数据

**版本:** 1.0.2
**状态:** 活跃
**覆盖范围:** 23条规则跨越3个实施类别（SOLID、核心原则、设计模式）；4个计划中
**最后更新:** 2026-03-07

### 规则统计
- SOLID原则: 10条规则
- 核心原则: 12条规则
- 设计模式: 1条规则
