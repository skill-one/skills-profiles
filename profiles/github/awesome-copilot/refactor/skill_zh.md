# 重构

## 概述

在不改变外部行为的前提下，改进代码结构和可读性。重构是渐进式的演变，而非革命。使用重构来改进现有代码，而不是从零开始重写。

## 何时使用

当你遇到以下情况时，可以使用这项技能：

- 代码难以理解或维护
- 函数/类过于庞大
- 需要解决代码异味
- 由于代码结构复杂，添加功能很困难
- 用户要求“清理这段代码”、“重构这段代码”、“改进这段代码”

---

## 重构原则

### 黄金法则

1. **行为保持不变** - 重构不会改变代码的功能，只会改变实现方式
2. **小步快跑** - 做微小的改动，每次改动后进行测试
3. **版本控制是你的朋友** - 在安全状态下提交代码
4. **测试至关重要** - 没有测试，你只是在编辑，而不是重构
5. **一次只做一件事** - 不要将重构与功能变更混为一谈

### 何时不应重构

```
- 工作正常且不会再变更的代码（如果没坏……）
- 没有测试的关键生产代码（先添加测试）
- 在紧迫的截止日期下
- “就因为” - 需要有明确的目的
```

---

## 常见代码异味及修复方法

### 1. 过长的方法/函数

```diff
# BAD: 200行的函数，做所有事情
- async function processOrder(orderId) {
-   // 50行：获取订单
-   // 30行：验证订单
-   // 40行：计算价格
-   // 30行：更新库存
-   // 20行：创建发货
-   // 30行：发送通知
- }

# GOOD: 分解为专注的函数
+ async function processOrder(orderId) {
+   const order = await fetchOrder(orderId);
+   validateOrder(order);
+   const pricing = calculatePricing(order);
+   await updateInventory(order);
+   const shipment = await createShipment(order);
+   await sendNotifications(order, pricing, shipment);
+   return { order, pricing, shipment };
+ }
```

### 2. 重复代码

```diff
# BAD: 多处存在相同逻辑
- function calculateUserDiscount(user) {
-   if (user.membership === 'gold') return user.total * 0.2;
-   if (user.membership === 'silver') return user.total * 0.1;
-   return 0;
- }
-
- function calculateOrderDiscount(order) {
-   if (order.user.membership === 'gold') return order.total * 0.2;
-   if (order.user.membership === 'silver') return order.total * 0.1;
-   return 0;
- }

# GOOD: 提取公共逻辑
+ function getMembershipDiscountRate(membership) {
+   const rates = { gold: 0.2, silver: 0.1 };
+   return rates[membership] || 0;
+ }
+
+ function calculateUserDiscount(user) {
+   return user.total * getMembershipDiscountRate(user.membership);
+ }
+
+ function calculateOrderDiscount(order) {
+   return order.total * getMembershipDiscountRate(order.user.membership);
+ }
```

### 3. 过大的类/模块

```diff
# BAD: 知识过多的“上帝对象”
- class UserManager {
-   createUser() { /* ... */ }
-   updateUser() { /* ... */ }
-   deleteUser() { /* ... */ }
-   sendEmail() { /* ... */ }
-   generateReport() { /* ... */ }
-   handlePayment() { /* ... */ }
-   validateAddress() { /* ... */ }
-   // 50个更多方法...
- }

# GOOD: 每个类只负责一件事情
+ class UserService {
+   create(data) { /* ... */ }
+   update(id, data) { /* ... */ }
+   delete(id) { /* ... */ }
+ }
+
+ class EmailService {
+   send(to, subject, body) { /* ... */ }
+ }
+
+ class ReportService {
+   generate(type, params) { /* ... */ }
+ }
+
+ class PaymentService {
+   process(amount, method) { /* ... */ }
+ }
```

### 4. 过长的参数列表

```diff
# BAD: 参数太多
- function createUser(email, password, name, age, address, city, country, phone) {
-   /* ... */
- }

# GOOD: 将相关参数分组
+ interface UserData {
+   email: string;
+   password: string;
+   name: string;
+   age?: number;
+   address?: Address;
+   phone?: string;
+ }
+
+ function createUser(data: UserData) {
+   /* ... */
+ }

# 更好的做法：使用构建者模式处理复杂构建
+ const user = UserBuilder
+   .email('test@example.com')
+   .password('secure123')
+   .name('Test User')
+   .address(address)
+   .build();
```

### 5. 功能依赖

```diff
# BAD: 方法使用其他对象的数据多于自己的数据
- class Order {
-   calculateDiscount(user) {
-     if (user.membershipLevel === 'gold') {
+       return this.total * 0.2;
+     }
+     if (user.accountAge > 365) {
+       return this.total * 0.1;
+     }
+     return 0;
+   }
+ }

# GOOD: 将逻辑移动到拥有数据的对象
+ class User {
+   getDiscountRate(orderTotal) {
+     if (this.membershipLevel === 'gold') return 0.2;
+     if (this.accountAge > 365) return 0.1;
+     return 0;
+   }
+ }
+
+ class Order {
+   calculateDiscount(user) {
+     return this.total * user.getDiscountRate(this.total);
+   }
+ }
```

### 6. 原始类型痴迷

```diff
# BAD: 使用原始类型表示领域概念
- function sendEmail(to, subject, body) { /* ... */ }
- sendEmail('user@example.com', 'Hello', '...');

- function createPhone(country, number) {
-   return `${country}-${number}`;
- }

# GOOD: 使用领域类型
+ class Email {
+   private constructor(public readonly value: string) {
+     if (!Email.isValid(value)) throw new Error('Invalid email');
+   }
+   static create(value: string) { return new Email(value); }
+   static isValid(email: string) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
+ }
+
+ class PhoneNumber {
+   constructor(
+     public readonly country: string,
+     public readonly number: string
+   ) {
+     if (!PhoneNumber.isValid(country, number)) throw new Error('Invalid phone');
+   }
+   toString() { return `${this.country}-${this.number}`; }
+   static isValid(country: string, number: string) { /* ... */ }
+ }
+
+ // 使用示例
+ const email = Email.create('user@example.com');
+ const phone = new PhoneNumber('1', '555-1234');
```

### 7. 魔术数字/字符串

```diff
# BAD: 未解释的值
- if (user.status === 2) { /* ... */ }
- const discount = total * 0.15;
- setTimeout(callback, 86400000);

# GOOD: 使用命名常量
+ const UserStatus = {
+   ACTIVE: 1,
+   INACTIVE: 2,
+   SUSPENDED: 3
+ } as const;
+
+ const DISCOUNT_RATES = {
+   STANDARD: 0.1,
+   PREMIUM: 0.15,
+   VIP: 0.2
+ } as const;
+
+ const ONE_DAY_MS = 24 * 60 * 60 * 1000;
+
+ if (user.status === UserStatus.INACTIVE) { /* ... */ }
+ const discount = total * DISCOUNT_RATES.PREMIUM;
+ setTimeout(callback, ONE_DAY_MS);
```

### 8. 嵌套条件

```diff
# BAD: 箭头代码
- function process(order) {
-   if (order) {
-     if (order.user) {
-       if (order.user.isActive) {
-         if (order.total > 0) {
-           return processOrder(order);
+         } else {
+           return { error: 'Invalid total' };
+         }
+       } else {
+         return { error: 'User inactive' };
+       }
+     } else {
+       return { error: 'No user' };
+     }
+   } else {
+     return { error: 'No order' };
+   }
+ }

# GOOD: 守卫语句/提前返回
+ function process(order) {
+   if (!order) return { error: 'No order' };
+   if (!order.user) return { error: 'No user' };
+   if (!order.user.isActive) return { error: 'User inactive' };
+   if (order.total <= 0) return { error: 'Invalid total' };
+   return processOrder(order);
+ }

# 更好的做法：使用结果类型
+ function process(order): Result<ProcessedOrder, Error> {
+   return Result.combine([
+     validateOrderExists(order),
+     validateUserExists(order),
+     validateUserActive(order.user),
+     validateOrderTotal(order)
+   ]).flatMap(() => processOrder(order));
+ }
```

### 9. 闲置代码

```diff
# BAD: 留存未使用的代码
- function oldImplementation() { /* ... */ }
- const DEPRECATED_VALUE = 5;
- import { unusedThing } from './somewhere';
- // 注释掉的代码
- // function oldCode() { /* ... */ }

# GOOD: 删除它
+ // 删除未使用的函数、导入和注释掉的代码
+ // 如果需要再次使用，git历史记录中有它
```

### 10. 不适当的亲密关系

```diff
# BAD: 一个类深入另一个类内部
- class OrderProcessor {
-   process(order) {
-     order.user.profile.address.street;  // 过于亲密
-     order.repository.connection.config;  // 破坏封装
+   }
+ }

# GOOD: 请求而非告知
+ class OrderProcessor {
+   process(order) {
+     order.getShippingAddress();  // Order知道如何获取它
+     order.save();  // Order知道如何保存自己
+   }
+ }
```

---

## 提取方法重构

### 前后对比

```diff
# Before: 一个长函数
- function printReport(users) {
-   console.log('USER REPORT');
-   console.log('============');
-   console.log('');
-   console.log(`Total users: ${users.length}`);
-   console.log('');
-   console.log('ACTIVE USERS');
-   console.log('------------');
-   const active = users.filter(u => u.isActive);
-   active.forEach(u => {
-     console.log(`- ${u.name} (${u.email})`);
-   });
-   console.log('');
-   console.log(`Active: ${active.length}`);
-   console.log('');
-   console.log('INACTIVE USERS');
-   console.log('--------------');
-   const inactive = users.filter(u => !u.isActive);
-   inactive.forEach(u => {
-     console.log(`- ${u.name} (${u.email})`);
-   });
-   console.log('');
-   console.log(`Inactive: ${inactive.length}`);
- }

# After: 提取了方法
+ function printReport(users) {
+   printHeader('USER REPORT');
+   console.log(`Total users: ${users.length}\n`);
+   printUserSection('ACTIVE USERS', users.filter(u => u.isActive));
+   printUserSection('INACTIVE USERS', users.filter(u => !u.isActive));
+ }
+
+ function printHeader(title) {
+   const line = '='.repeat(title.length);
+   console.log(title);
+   console.log(line);
+   console.log('');
+ }
+
+ function printUserSection(title, users) {
+   console.log(title);
+   console.log('-'.repeat(title.length));
+   users.forEach(u => console.log(`- ${u.name} (${u.email})`));
+   console.log('');
+   console.log(`${title.split(' ')[0]}: ${users.length}`);
+   console.log('');
+ }
```

---

## 引入类型安全

### 从无类型到有类型

```diff
# Before: 没有类型
- function calculateDiscount(user, total, membership, date) {
-   if (membership === 'gold' && date.getDay() === 5) {
-     return total * 0.25;
-   }
-   if (membership === 'gold') return total * 0.2;
-   return total * 0.1;
- }

# After: 完全类型安全
+ type Membership = 'bronze' | 'silver' | 'gold';
+
+ interface User {
+   id: string;
+   name: string;
+   membership: Membership;
+ }
+
+ interface DiscountResult {
+   original: number;
+   discount: number;
+   final: number;
+   rate: number;
+ }
+
+ function calculateDiscount(
+   user: User,
+   total: number,
+   date: Date = new Date()
+ ): DiscountResult {
+   if (total < 0) throw new Error('Total cannot be negative');
+
+   let rate = 0.1; // 默认青铜
+
+   if (user.membership === 'gold' && date.getDay() === 5) {
+     rate = 0.25; // 周五对黄金会员的奖励
+   } else if (user.membership === 'gold') {
+     rate = 0.2;
+   } else if (user.membership === 'silver') {
+     rate = 0.15;
+   }
+
+   const discount = total * rate;
+
+   return {
+     original: total,
+     discount,
+     final: total - discount,
+     rate
+   };
+ }
```

---

## 用于重构的设计模式

### 策略模式

```diff
# Before: 条件逻辑
- function calculateShipping(order, method) {
-   if (method === 'standard') {
-     return order.total > 50 ? 0 : 5.99;
-   } else if (method === 'express') {
-     return order.total > 100 ? 9.99 : 14.99;
+   } else if (method === 'overnight') {
+     return 29.99;
+   }
+ }

# After: 策略模式
+ interface ShippingStrategy {
+   calculate(order: Order): number;
+ }
+
+ class StandardShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return order.total > 50 ? 0 : 5.99;
+   }
+ }
+
+ class ExpressShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return order.total > 100 ? 9.99 : 14.99;
+   }
+ }
+
+ class OvernightShipping implements ShippingStrategy {
+   calculate(order: Order) {
+     return 29.99;
+   }
+ }
+
+ function calculateShipping(order: Order, strategy: ShippingStrategy) {
+   return strategy.calculate(order);
+ }
```

### 责任链

```diff
# Before: 嵌套验证
- function validate(user) {
-   const errors = [];
-   if (!user.email) errors.push('Email required');
+   else if (!isValidEmail(user.email)) errors.push('Invalid email');
+   if (!user.name) errors.push('Name required');
+   if (user.age < 18) errors.push('Must be 18+');
+   if (user.country === 'blocked') errors.push('Country not supported');
+   return errors;
+ }

# After: 责任链
+ abstract class Validator {
+   abstract validate(user: User): string | null;
+   setNext(validator: Validator): Validator {
+     this.next = validator;
+     return validator;
+   }
+   validate(user: User): string | null {
+     const error = this.doValidate(user);
+     if (error) return error;
+     return this.next?.validate(user) ?? null;
+   }
+ }
+
+ class EmailRequiredValidator extends Validator {
+   doValidate(user: User) {
+     return !user.email ? 'Email required' : null;
+   }
+ }
+
+ class EmailFormatValidator extends Validator {
+   doValidate(user: User) {
+     return user.email && !isValidEmail(user.email) ? 'Invalid email' : null;
+   }
+ }
+
+ // 构建链
+ const validator = new EmailRequiredValidator()
+   .setNext(new EmailFormatValidator())
+   .setNext(new NameRequiredValidator())
+   .setNext(new AgeValidator())
+   .setNext(new CountryValidator());
```

---

## 重构步骤

### 安全重构流程

```
1. 准备
   - 确保有测试（如果缺失，则编写）
   - 提交当前状态
   - 创建特性分支

2. 识别
   - 找到要解决的代码异味
   - 理解代码的作用
   - 规划重构

3. 重构（小步）
   - 做一个小的改动
   - 运行测试
   - 如果测试通过，提交
   - 重复

4. 验证
   - 所有测试通过
   - 如有需要，进行手动测试
   - 性能保持不变或提升

5. 清理
   - 更新注释
   - 更新文档
   - 最终提交
```

---

## 重构检查清单

### 代码质量

- [ ] 函数简短（<50行）
- [ ] 函数只做一件事
- [ ] 无重复代码
- [ ] 变量、函数、类名描述清晰
- [ ] 无魔术数字/字符串
- [ ] 删除闲置代码

### 结构

- [ ] 相关代码放在一起
- [ ] 清晰的模块边界
- [ ] 依赖单向流动
- [ ] 无循环依赖

### 类型安全

- [ ] 所有公共API都有类型定义
- [ ] 无无理由的`any`类型
- [ ] 显式标记可空类型

### 测试

- [ ] 重构代码已测试
- [ ] 测试覆盖边缘情况
- [ ] 所有测试通过

---

## 常见重构操作

| 操作                         | 描述                           |
| ---------------------------- | ------------------------------ |
| 提取方法                     | 将代码片段转换为方法            |
| 提取类                       | 将行为移动到新类                |
| 提取接口                     | 从实现创建接口                  |
| 内联方法                     | 将方法体移回调用者              |
| 内联类                       | 将类行为移至调用者              |
| 上移方法                     | 将方法移到超类                  |
| 下移方法                     | 将方法移到子类                  |
| 重命名方法/变量             | 提高清晰度                      |
| 引入参数对象                 | 组合相关参数                    |
| 用多态替换条件               | 使用多态代替switch/if          |
| 用常量替换魔术数字           | 命名常量                       |
| 分解条件                     | 拆分复杂条件                    |
| 合并条件                     | 合并重复条件                    |
| 用守卫语句替换嵌套条件       | 提前返回                         |
| 引入空对象                   | 消除空值检查                   |
| 用类/枚举替换类型代码       | 强类型                         |
| 用委托替换继承               | 组合优于继承                    |
