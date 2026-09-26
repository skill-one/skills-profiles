# 持续改进：Kaizen

应用持续改进的思维模式 - 提出小型的迭代改进，设计防错，遵循既定模式，避免过度设计；自动应用于指导质量和简洁性

## 概述

小改进，持续进行。设计上防错。遵循有效的方法。仅构建所需之物。

**核心原则：** 许多小改进胜过一次重大变革。在设计时预防错误，而不是事后修复。

## 使用场景

**始终应用于：**

- 代码实现和重构
- 架构和设计决策
- 流程和工作流改进
- 错误处理和验证

**哲学：** 通过渐进式进步和预防来保证质量，而不是通过巨大努力来追求完美。

## 四大支柱

### 1. 持续改进（Kaizen）

小而频繁的改进会累积成重大收益。

#### 原则

**渐进优于革命：**

- 做最小的可行改进来提高质量
- 一次只做一项改进
- 在进行下一项改进前验证当前变更
- 通过小胜利建立势头

**始终让代码变得更好：**

- 遇到小问题时立即修复
- 在工作过程中重构（在范围内）
- 更新过时的注释
- 看到死代码时立即移除

**迭代优化：**

- 第一版：使其能工作
- 第二版：使其清晰
- 第三版：使其高效
- 不要一次尝试所有三件事

<Good>
```typescript
// 迭代 1：使其能工作
const calculateTotal = (items: Item[]) => {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i].price * items[i].quantity;
  }
  return total;
};

// 迭代 2：使其清晰（重构）
const calculateTotal = (items: Item[]): number => {
  return items.reduce((total, item) => {
    return total + (item.price * item.quantity);
  }, 0);
};

// 迭代 3：使其健壮（添加验证）
const calculateTotal = (items: Item[]): number => {
  if (!items?.length) return 0;
  
  return items.reduce((total, item) => {
    if (item.price < 0 || item.quantity < 0) {
      throw new Error('Price and quantity must be non-negative');
    }
    return total + (item.price * item.quantity);
  }, 0);
};

```
每一步都是完整的、经过测试且可工作的
</Good>

<Bad>
```typescript
// 试图一次性做所有事情
const calculateTotal = (items: Item[]): number => {
  // 同时验证、优化、添加功能、处理边界情况
  if (!items?.length) return 0;
  const validItems = items.filter(item => {
    if (item.price < 0) throw new Error('Negative price');
    if (item.quantity < 0) throw new Error('Negative quantity');
    return item.quantity > 0; // 也过滤零数量的项
  });
  // 加上缓存、加上日志、加上货币转换...
  return validItems.reduce(...); // 一次处理太多关注点
};
```

令人不知所措、易出错、难以验证
</Bad>

#### 实践中

**在实现功能时：**

1. 从能工作的最简单版本开始
2. 添加一项改进（错误处理、验证等）
3. 测试和验证
4. 如果有时间，重复进行
5. 不要试图立即使其完美

**在重构时：**

- 一次修复一个异味
- 每次改进后提交
- 在整个过程中保持测试通过
- 当达到“足够好”（边际效益递减）时停止

**在审查代码时：**

- 建议渐进式改进（而不是重写）
- 优先级：关键 → 重要 → 可选
- 首先关注影响最大的变更
- 即使不完美也接受“比之前更好”

### 2. Poka-Yoke（防错设计）

设计系统在编译/设计时防止错误，而不是在运行时。

#### 原则

**使错误不可能发生：**

- 类型系统捕获错误
- 编译器强制执行契约
- 无效状态不可表示
- 错误在早期捕获（生产之前）

**设计时考虑安全：**

- 快速失败并大声报告
- 提供有帮助的错误消息
- 使正确路径显而易见
- 使错误路径难以选择

**分层防御：**

1. 类型系统（编译时）
2. 验证（运行时，早期）
3. 守卫（前置条件）
4. 错误边界（优雅降级）

#### 类型系统防错

<Good>
```typescript
// 错误：string 状态可以是任何值
type OrderBad = {
  status: string; // 可以是 "pending"、"PENDING"、"pnding"，任何值！
  total: number;
};

// 良好：只有有效的状态可能
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered';
type Order = {
  status: OrderStatus;
  total: number;
};

// 更好：带有相关数据的状体
type Order =
  | { status: 'pending'; createdAt: Date }
  | { status: 'processing'; startedAt: Date; estimatedCompletion: Date }
  | { status: 'shipped'; trackingNumber: string; shippedAt: Date }
  | { status: 'delivered'; deliveredAt: Date; signature: string };

// 现在不可能没有 trackingNumber 而已发货

```
类型系统防止整类错误
</Good>

<Good>
```typescript
// 使无效状态不可表示
type NonEmptyArray<T> = [T, ...T[]];

const firstItem = <T>(items: NonEmptyArray<T>): T => {
  return items[0]; // 总是安全的，永远不会是 undefined！
};

// 调用者必须证明数组非空
const items: number[] = [1, 2, 3];
if (items.length > 0) {
  firstItem(items as NonEmptyArray<number>); // 安全
}
```

函数签名保证安全
</Good>

#### 验证防错

<Good>
```typescript
// 错误：使用后验证
const processPayment = (amount: number) => {
  const fee = amount * 0.03; // 使用前就计算了！
  if (amount <= 0) throw new Error('Invalid amount');
  // ...
};

// 良好：立即验证
const processPayment = (amount: number) => {
  if (amount <= 0) {
    throw new Error('Payment amount must be positive');
  }
  if (amount > 10000) {
    throw new Error('Payment exceeds maximum allowed');
  }
  
  const fee = amount * 0.03;
  // ... 现在安全使用
};

// 更好：边界验证与标记类型
type PositiveNumber = number & { readonly __brand: 'PositiveNumber' };

const validatePositive = (n: number): PositiveNumber => {
  if (n <= 0) throw new Error('Must be positive');
  return n as PositiveNumber;
};

const processPayment = (amount: PositiveNumber) => {
  // amount 保证为正，无需检查
  const fee = amount * 0.03;
};

// 在系统边界验证
const handlePaymentRequest = (req: Request) => {
  const amount = validatePositive(req.body.amount); // 一次验证
  processPayment(amount); // 安全使用
};

```
在边界处验证一次，其他地方安全
</Good>

#### 守卫和前置条件

<Good>
```typescript
// 早返回防止深层嵌套代码
const processUser = (user: User | null) => {
  if (!user) {
    logger.error('User not found');
    return;
  }
  
  if (!user.email) {
    logger.error('User email missing');
    return;
  }
  
  if (!user.isActive) {
    logger.info('User inactive, skipping');
    return;
  }
  
  // 主要逻辑在这里，保证 user 有效且活跃
  sendEmail(user.email, 'Welcome!');
};
```

守卫使假设显式且强制执行
</Good>

#### 配置防错

<Good>
```typescript
// 错误：可选配置与不安全的默认值
type ConfigBad = {
  apiKey?: string;
  timeout?: number;
};

const client = new APIClient({ timeout: 5000 }); // apiKey 缺失！

// 良好：必需配置，早期失败
type Config = {
  apiKey: string;
  timeout: number;
};

const loadConfig = (): Config => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    throw new Error('API_KEY 环境变量必需');
  }
  
  return {
    apiKey,
    timeout: 5000,
  };
};

// 如果配置无效，应用在启动时失败，而不是在生产中
const config = loadConfig();
const client = new APIClient(config);

```
在启动时失败，而不是在生产中
</Good>

#### 实践中

**在设计 API 时：**
- 使用类型来约束输入
- 使无效状态不可表示
- 返回 Result<T, E> 而不是抛出
- 在类型中记录前置条件

**在处理错误时：**
- 在系统边界验证
- 使用守卫进行前置条件
- 快速失败并带有清晰消息
- 记录上下文以便调试

**在配置时：**
- 必需而非可选，带默认值
- 在启动时验证所有配置
- 如果配置无效则失败部署
- 不要允许部分配置

### 3. 标准化工作

遵循既定模式。记录有效的方法。使良好实践易于遵循。

#### 原则

**一致性优于巧思：**
- 遵循现有代码库模式
- 不要重新发明已解决的问题
- 只有在显著更好时才引入新模式
- 团队对新模式达成一致

**文档与代码共存：**
- README 用于设置和架构
- CLAUDE.md 用于 AI 编码规范
- 注释用于解释“为什么”，而非“什么”
- 示例用于复杂模式

**自动化标准：**
- Linters 强制风格
- 类型检查强制契约
- 测试验证行为
- CI/CD 强制质量门

#### 遵循模式

<Good>
```typescript
// 现有代码库的 API 客户端模式
class UserAPIClient {
  async getUser(id: string): Promise<User> {
    return this.fetch(`/users/${id}`);
  }
}

// 新代码遵循相同模式
class OrderAPIClient {
  async getOrder(id: string): Promise<Order> {
    return this.fetch(`/orders/${id}`);
  }
}
```

一致性使代码库可预测
</Good>

<Bad>
```typescript
// 现有模式使用类
class UserAPIClient { /* ... */ }

// 新代码引入不同模式而不讨论
const getOrder = async (id: string): Promise<Order> => {
  // 打破一致性“因为我更喜欢函数”
};

```
不一致性造成困惑
</Bad>

#### 错误处理模式

<Good>
```typescript
// 项目标准：用于可恢复错误的 Result 类型
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

// 所有服务都遵循此模式
const fetchUser = async (id: string): Promise<Result<User, Error>> => {
  try {
    const user = await db.users.findById(id);
    if (!user) {
      return { ok: false, error: new Error('User not found') };
    }
    return { ok: true, value: user };
  } catch (err) {
    return { ok: false, error: err as Error };
  }
};

// 调用者使用一致模式
const result = await fetchUser('123');
if (!result.ok) {
  logger.error('Failed to fetch user', result.error);
  return;
}
const user = result.value; // 类型安全！
```

代码库中标准模式
</Good>

#### 文档标准

<Good>
```typescript
/**
 * 带指数退避重试异步操作。
 *
 * 为什么：网络请求可能暂时失败；重试提高可靠性
 * 何时使用：外部 API 调用，数据库操作
 * 何时不用：用户输入验证，内部函数调用
 *
 * @example
 * const result = await retry(
 *   () => fetch('https://api.example.com/data'),
 *   { maxAttempts: 3, baseDelay: 1000 }
 * );
 */
const retry = async <T>(
  operation: () => Promise<T>,
  options: RetryOptions
): Promise<T> => {
  // 实现...
};
```
记录为什么、何时、如何
</Good>

#### 实践中

**在添加新模式前：**

- 在代码库中搜索类似问题解决方案
- 检查 CLAUDE.md 中的项目规范
- 如果打破模式，与团队讨论
- 引入新模式时更新文档

**在编写代码时：**

- 匹配现有文件结构
- 使用相同的命名规范
- 遵循相同的错误处理方法
- 从相同位置导入

**在审查时：**

- 检查与现有代码的一致性
- 指向代码库中的示例
- 建议与标准对齐
- 如果出现新标准，更新 CLAUDE.md

### 4. Just-In-Time（JIT）

现在需要什么就构建什么。不多不少。避免过早优化和过度设计。

#### 原则

**YAGNI（你不会需要它）：**

- 只实现当前需求
- 没有“以防万一”的功能
- 没有“以后可能需要”的代码
- 删除猜测

**最简单能工作的东西：**

- 从简单的解决方案开始
- 只有在需要时才添加复杂性
- 需求变化时重构
- 不要预测未来需求

**测量后再优化：**

- 没有过早优化
- 优化前进行性能分析
- 测量变更的影响
- 接受“足够好”的性能

#### YAGNI 实践

<Good>
```typescript
// 当前需求：将错误记录到控制台
const logError = (error: Error) => {
  console.error(error.message);
};
```
简单，满足当前需求
</Good>

<Bad>
```typescript
// 过度设计以“满足未来需求”
interface LogTransport {
  write(level: LogLevel, message: string, meta?: LogMetadata): Promise<void>;
}

class ConsoleTransport implements LogTransport { /*... */ }
class FileTransport implements LogTransport { /* ... */ }
class RemoteTransport implements LogTransport { /* ...*/ }

class Logger {
  private transports: LogTransport[] = [];
  private queue: LogEntry[] = [];
  private rateLimiter: RateLimiter;
  private formatter: LogFormatter;
  
  // 200 行代码用于“可能需要它”
}

const logError = (error: Error) => {
  Logger.getInstance().log('error', error.message);
};

```
为想象中的未来需求构建
</Bad>

**何时添加复杂性：**
- 当前需求需要
- 通过使用发现痛点
- 测量到的性能问题
- 多个用例出现

<Good>
```typescript
// 开始简单
const formatCurrency = (amount: number): string => {
  return `$${amount.toFixed(2)}`;
};

// 需求演变：支持多种货币
const formatCurrency = (amount: number, currency: string): string => {
  const symbols = { USD: '$', EUR: '€', GBP: '£' };
  return `${symbols[currency]}${amount.toFixed(2)}`;
};

// 需求演变：支持本地化
const formatCurrency = (amount: number, locale: string): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: locale === 'en-US' ? 'USD' : 'EUR',
  }).format(amount);
};
```

只有在需要时才添加复杂性
</Good>

#### 过早抽象

<Bad>
```typescript
// 一个用例，但构建通用框架
abstract class BaseCRUDService<T> {
  abstract getAll(): Promise<T[]>;
  abstract getById(id: string): Promise<T>;
  abstract create(data: Partial<T>): Promise<T>;
  abstract update(id: string, data: Partial<T>): Promise<T>;
  abstract delete(id: string): Promise<void>;
}

class GenericRepository<T> { /*300 行 */ }
class QueryBuilder<T> { /* 200 行*/ }
// ... 构建整个 ORM 用于单个表

```
为不确定的未来构建巨大抽象
</Bad>

<Good>
```typescript
// 简单函数用于当前需求
const getUsers = async (): Promise<User[]> => {
  return db.query('SELECT * FROM users');
};

const getUserById = async (id: string): Promise<User | null> => {
  return db.query('SELECT * FROM users WHERE id = $1', [id]);
};

// 当模式在多个实体中显现时，再抽象
```

只有在 3 个或更多用例中证明模式时才抽象
</Good>

#### 性能优化

<Good>
```typescript
// 当前：简单方法
const filterActiveUsers = (users: User[]): User[] => {
  return users.filter(user => user.isActive);
};

// 性能分析显示：1000 个用户 50ms（可接受）
// ✓ 直接发布，无需优化

// 后来：在性能分析显示这是瓶颈后
// 然后使用索引查找或缓存进行优化

```
根据测量优化，而不是假设
</Good>

<Bad>
```typescript
// 过早优化
const filterActiveUsers = (users: User[]): User[] => {
  // “这可能很慢，所以让我们缓存和索引”
  const cache = new WeakMap();
  const indexed = buildBTreeIndex(users, 'isActive');
  // 100 行优化代码
  // 增加复杂性，更难维护
  // 没有证据表明需要它
};
```

为未测量的问题使用复杂解决方案
</Bad>

#### 实践中

**在实现时：**

- 解决当前问题
- 使用简单方法
- 抵制“什么如果”思维
- 删除猜测代码

**在优化时：**

- 先分析后优化
- 优化前后的测量
- 记录为何需要优化
- 保留简单版本在测试中

**在抽象时：**

- 等待 3 个或更多相似情况（三条规则）
- 使抽象尽可能简单
- 优先复制而非错误的抽象
- 当模式清晰时重构

## 与命令集成

Kaizen 技能指导你如何工作。命令提供结构化分析：

- **`/why`**：根本原因分析（五问法）
- **`/cause-and-effect`**：多因素分析（鱼骨图）
- **`/plan-do-check-act`**：迭代改进周期
- **`/analyse-problem`**：综合文档（A3）
- **`/analyse`**：智能方法选择（Gemba/VSM/Muda）

使用命令进行结构化问题解决。应用技能进行日常开发。

## 警示信号

**违反持续改进：**

- “我以后会重构”（永远不会发生）
- 留下比发现时更差的代码
- 一次性大改而不是渐进式

**违反 Poka-Yoke：**

- “用户应该小心”
- 使用后验证而不是使用前
- 可选配置没有验证

**违反标准化工作：**

- “我更喜欢用自己的方式”
- 不检查现有模式
- 忽略项目规范

**违反 Just-In-Time：**

- “我们以后可能需要”
- 在使用前构建框架
- 没有测量就优化

## 记住

**Kaizen 是关于：**

- 持续的小改进
- 通过设计预防错误
- 遵循已证明的模式
- 仅构建所需之物

**不是关于：**

- 第一次尝试就完美
- 大型重构项目
- 巧妙的抽象
- 过早优化

**心态：** 今天足够好，明天更好。重复。
