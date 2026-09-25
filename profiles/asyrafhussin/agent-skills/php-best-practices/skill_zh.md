# PHP 最佳实践

现代 PHP 8.x 模式、PSR 标准、类型系统最佳实践和 SOLID 原则。包含 51 条规则，用于编写干净、可维护的 PHP 代码。

## 第 1 步：检测 PHP 版本

**在给出任何建议之前，始终检查项目的 PHP 版本。** 功能在 8.0 到 8.5 之间存在显著差异。切勿建议项目中不存在的语法。

检查 `composer.json` 中所需的 PHP 版本：
```json
{ "require": { "php": "^8.1" } }   // -> 8.1 规则及以下
{ "require": { "php": "^8.3" } }   // -> 8.3 规则及以下
{ "require": { "php": ">=8.4" } }  // -> 8.4 规则及以下
```

也检查运行时版本：
```bash
php -v   # 例如：PHP 8.3.12
```

### 按版本的功能可用性

| 功能 | 版本 | 规则前缀 |
|------|------|----------|
| 联合类型、match、nullsafe、命名参数、构造器提升、属性 | 8.0+ | `type-`、`modern-` |
| 枚举、只读属性、交集类型、第一类可调用、never、协程 | 8.1+ | `modern-` |
| 只读类、DNF 类型、true/false/null 独立类型 | 8.2+ | `modern-` |
| 类型化的类常量、`#[\Override]`、`json_validate()` | 8.3+ | `modern-` |
| 属性钩子、非对称可见性、`#[\Deprecated]`、无括号的 `new` | 8.4+ | `modern-` |
| 管道运算符 `|>` | 8.5+ | `modern-` |

**仅建议检测到的版本中可用的功能。** 如果用户询问升级或新功能，请说明每个版本中可用的内容。

## 何时应用

参考这些指南的情况：
- 编写或审查 PHP 代码
- 实现类和接口
- 使用 PHP 8.x 现代功能
- 确保类型安全
- 遵循 PSR 标准
- 应用设计模式

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 | 规则 |
|--------|------|------|------|------|
| 1 | 类型系统 | 关键 | `type-` | 9 |
| 2 | 现代 PHP 功能 | 关键 | `modern-` | 16 |
| 3 | PSR 标准 | 高 | `psr-` | 6 |
| 4 | SOLID 原则 | 高 | `solid-` | 5 |
| 5 | 错误处理 | 高 | `error-` | 5 |
| 6 | 性能 | 中 | `perf-` | 5 |
| 7 | 安全 | 关键 | `sec-` | 5 |

## 快速参考

### 1. 类型系统 (关键) — 9 条规则

- `type-strict-mode` - 在每个文件中声明严格类型
- `type-return-types` - 始终声明返回类型
- `type-parameter-types` - 类型化所有参数
- `type-property-types` - 类型化类属性
- `type-union-types` - 有效使用联合类型
- `type-intersection-types` - 使用交集类型
- `type-nullable-types` - 正确处理可空类型
- `type-void-never` - 使用 void/never 适用于适当的返回类型
- `type-mixed-avoid` - 尽可能避免混合类型

### 2. 现代 PHP 功能 (关键) — 16 条规则

**8.0+:**
- `modern-constructor-promotion` - 构造器属性提升
- `modern-match-expression` - 用 match 代替 switch
- `modern-named-arguments` - 命名参数以提高清晰度
- `modern-nullsafe-operator` - Nullsafe 运算符 (?->)
- `modern-attributes` - 用于元数据的属性

**8.1+:**
- `modern-enums` - 用枚举代替常量
- `modern-enums-methods` - 带方法和接口的枚举
- `modern-readonly-properties` - 只读属性用于不可变数据
- `modern-first-class-callables` - 第一类可调用语法
- `modern-arrow-functions` - 箭头函数（7.4+，与 8.1 功能配合良好）

**8.2+:**
- `modern-readonly-classes` - 只读类

**8.3+:**
- `modern-typed-constants` - 类型化的类常量（`const string NAME = 'foo'`）
- `modern-override-attribute` - `#[\Override]` 捕获父方法拼写错误

**8.4+:**
- `modern-property-hooks` - 属性钩子代替获取器/设置器
- `modern-asymmetric-visibility` - `public private(set)` 用于受控访问

**8.5+:**
- `modern-pipe-operator` - 管道运算符（`|>`）用于函数式链式操作

### 3. PSR 标准 (高) — 6 条规则

- `psr-4-autoloading` - 遵循 PSR-4 自动加载
- `psr-12-coding-style` - 遵循 PSR-12 编码风格
- `psr-naming-classes` - 类命名约定
- `psr-naming-methods` - 方法命名约定
- `psr-file-structure` - 每个文件一个类
- `psr-namespace-usage` - 正确使用命名空间

### 4. SOLID 原则 (高) — 5 条规则

- `solid-srp` - 单一职责：一个变更的原因
- `solid-ocp` - 开放/封闭：扩展，不要修改
- `solid-lsp` - 里氏替换：子类型必须是可替换的
- `solid-isp` - 接口隔离：小而专注的接口
- `solid-dip` - 依赖倒置：依赖抽象

### 5. 错误处理 (高) — 5 条规则

- `error-custom-exceptions` - 为不同错误创建特定异常
- `error-exception-hierarchy` - 将异常组织成有意义的层次结构
- `error-try-catch-specific` - 捕获特定异常，而不是通用的 `\Exception`
- `error-finally-cleanup` - 使用 finally 进行保证的资源清理
- `error-never-suppress` - 不要使用 @ 错误抑制运算符

### 6. 性能 (中) — 5 条规则

- `perf-avoid-globals` - 避免全局变量，使用依赖注入
- `perf-lazy-loading` - 延迟昂贵的操作直到需要时
- `perf-array-functions` - 使用原生数组函数而不是手动循环
- `perf-string-functions` - 使用原生字符串函数而不是正则表达式
- `perf-generators` - 使用生成器处理大型数据集

### 7. 安全 (关键) — 5 条规则

- `sec-input-validation` - 验证和清理所有外部输入
- `sec-output-escaping` - 根据上下文（HTML、JS、URL）转义输出
- `sec-password-hashing` - 使用 password_hash/verify，永远不要使用 MD5/SHA1
- `sec-sql-prepared` - 对所有 SQL 查询使用预处理语句
- `sec-file-uploads` - 验证文件类型、大小、名称；存储在 Web 根目录之外

## 基本指南

有关详细示例和解释，请参阅规则文件：

- [type-strict-mode.md](rules/type-strict-mode.md) - 严格类型声明
- [modern-constructor-promotion.md](rules/modern-constructor-promotion.md) - 构造器属性提升
- [modern-enums.md](rules/modern-enums.md) - PHP 8.1+ 带方法的枚举
- [solid-srp.md](rules/solid-srp.md) - 单一职责原则

### 关键模式（快速参考）

```php
<?php
declare(strict_types=1);

// 8.0+ 构造器提升 + 只读（8.1+）
class User
{
    public function __construct(
        public readonly string $id,
        private string $email,
    ) {}
}

// 8.1+ 带方法的枚举
enum Status: string
{
    case Active = 'active';
    case Inactive = 'inactive';

    public function label(): string
    {
        return match($this) {
            self::Active => 'Active',
            self::Inactive => 'Inactive',
        };
    }
}

// 8.0+ match 表达式
$result = match($status) {
    'pending' => 'Waiting',
    'active' => 'Running',
    default => 'Unknown',
};

// 8.0+ nullsafe 运算符
$country = $user?->getAddress()?->getCountry();

// 8.3+ 类型化的类常量 + #[\Override]
class PaymentService extends BaseService
{
    public const string GATEWAY = 'stripe';

    #[\Override]
    public function process(): void { /* ... */ }
}

// 8.4+ 属性钩子 + 非对称可见性
class Product
{
    public string $name { set => trim($value); }
    public private(set) float $price;
}

// 8.5+ 管道运算符
$result = $input
    |> trim(...)
    |> strtolower(...)
    |> htmlspecialchars(...);
```

## 输出格式

在审计代码时，以以下格式输出发现的问题：

```
文件:行 - [类别] 问题的描述
```

示例：
```
src/Services/UserService.php:15 - [type] 缺少返回类型声明
src/Models/Order.php:42 - [modern] 使用 match 表达式代替 switch
src/Controllers/ApiController.php:28 - [solid] 类有多个职责
```

## 如何使用

阅读单个规则文件以获取详细解释：

```
rules/modern-constructor-promotion.md
rules/type-strict-mode.md
rules/solid-srp.md
```
