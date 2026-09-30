---
name: code-simplification
description: 简化代码以提高清晰度。在重构代码以提高清晰度但不改变行为时使用。在代码可以更易于阅读、维护或扩展但实际更困难时使用。在审查积累了不必要复杂性的代码时使用。
---

# 代码简化

> 受到 [Claude 代码简化插件](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) 的启发。在此将其改编为一个与模型无关、以流程驱动的技能，适用于任何 AI 编码代理。

## 概述

通过减少复杂性来简化代码，同时保持精确的行为。目标不是减少行数——而是编写更容易阅读、理解、修改和调试的代码。每个简化都必须通过一个简单的测试：“一个新团队成员是否比原始代码更快地理解这段代码？”

## 何时使用

- 功能工作正常且测试通过，但实现感觉比实际需要的更重
- 在代码审查期间，当发现可读性或复杂性问题时
- 当你遇到深层嵌套逻辑、长函数或不清晰的命名时
- 在时间压力下编写的代码进行重构时
- 合并分散在多个文件中的相关逻辑时
- 合并引入了重复或不一致更改的更改后

**不使用时：**

- 代码已经干净且可读——不要为了简化而简化
- 你还不理解代码的作用——理解后再简化
- 代码是性能关键的，而“更简单”的版本会明显变慢
- 你即将完全重写模块——简化一次性代码浪费精力

## 五项原则

### 1. 精确保留行为

不要改变代码的行为——只改变它的表达方式。所有输入、输出、副作用、错误行为和边缘情况必须保持不变。如果你不确定简化是否保留了行为，就不要进行简化。

```
每次更改前都要询问：
→ 这是否为每个输入都产生相同的输出？
→ 这是否保持了相同的错误行为？
→ 这是否保留了相同的副作用和顺序？
→ 所有现有测试是否仍然通过而无需修改？
```

### 2. 遵循项目规范

简化意味着使代码与代码库更一致，而不是强加外部偏好。在简化之前：

```
1. 阅读 CLAUDE.md / 项目规范
2. 研究相邻代码如何处理类似的模式
3. 匹配项目的风格：
   - 导入顺序和模块系统
   - 函数声明风格
   - 命名规范
   - 错误处理模式
   - 类型注解深度
```

破坏项目一致性的简化不是简化——它是重复劳动。

### 3. 优先清晰胜于巧妙

当紧凑版本需要暂停思考才能解析时，显式代码比紧凑代码更好。

```typescript
// 不清晰：密集的三元运算符链
const label = isNew ? 'New' : isUpdated ? 'Updated' : isArchived ? 'Archived' : 'Active';

// 清晰：可读的映射
function getStatusLabel(item: Item): string {
  if (item.isNew) return 'New';
  if (item.isUpdated) return 'Updated';
  if (item.isArchived) return 'Archived';
  return 'Active';
}
```

```typescript
// 不清晰：带内联逻辑的链式 reduce
const result = items.reduce((acc, item) => ({
  ...acc,
  [item.id]: { ...acc[item.id], count: (acc[item.id]?.count ?? 0) + 1 }
}), {});

// 清晰：命名中间步骤
const countById = new Map<string, number>();
for (const item of items) {
  countById.set(item.id, (countById.get(item.id) ?? 0) + 1);
}
```

### 4. 保持平衡

简化有一个失效模式：过度简化。注意以下陷阱：

- **过度内联**——移除提供了概念名称的辅助函数使调用位置更难阅读
- **合并不相关的逻辑**——两个简单函数合并成一个复杂函数并不是更简单
- **移除“不必要”的抽象**——某些抽象是为了可扩展性或可测试性而存在的，而不是为了复杂性
- **优化行数**——行数少不是目标；更容易理解才是

### 5. 范围限制在已更改的内容

默认情况下，简化最近修改的代码。除非明确要求扩大范围，否则避免对不相关的代码进行一次性重构。无范围的简化会在差异中产生噪音，并导致意外的回归风险。

## 简化流程

### 第 1 步：在触摸之前理解（切斯特顿栅栏）

在更改或删除任何东西之前，理解它为什么存在。这是切斯特顿栅栏：如果你看到一条横跨道路的栅栏，而且不明白为什么它在那里，就不要拆掉它。首先理解原因，然后决定原因是否仍然适用。

```
简化之前回答：
- 这段代码的职责是什么？
- 谁调用它？它调用什么？
- 边缘情况和错误路径是什么？
- 有哪些测试定义了预期行为？
- 它可能以这种方式编写的原因是什么？（性能？平台限制？历史原因？）
- 检查 git blame：这段代码的原始上下文是什么？
```

如果你不能回答这些问题，你还没有准备好简化。先阅读更多上下文。

### 第 2 步：识别简化机会

扫描这些模式——每个模式都是一个具体的信号，而不是模糊的气味：

**结构复杂性：**

| 模式 | 信号 | 简化 |
|------|------|------|
| 深层嵌套（3 层以上） | 难以跟踪控制流 | 将条件提取到保护子句或辅助函数中 |
| 长函数（50 行以上） | 多个职责 | 分割为具有描述性名称的专注函数 |
| 嵌套三元运算符 | 需要暂停思考才能解析 | 替换为 if/else 链、switch 或查找对象 |
| 布尔参数标志 | `doThing(true, false, true)` | 替换为选项对象或分离函数 |
| 重复的条件 | 在多个地方相同的 `if` 检查 | 提取为命名良好的谓词函数 |

**命名和可读性：**

| 模式 | 信号 | 简化 |
|------|------|------|
| 通用名称 | `data`、`result`、`temp`、`val`、`item` | 重命名为描述内容：`userProfile`、`validationErrors` |
| 缩写名称 | `usr`、`cfg`、`btn`、`evt` | 使用全字，除非缩写是通用的（`id`、`url`、`api`） |
| 指导性名称 | 名为 `get` 的函数也修改状态 | 重命名为反映实际行为 |
| 解释“什么”的注释 | `// 增加计数器` 在 `count++` 上面 | 删除注释——代码足够清晰 |
| 解释“为什么”的注释 | `// 因为 API 在负载下不稳定而重试` | 保留这些——它们携带代码无法表达的意图 |

**冗余：**

| 模式 | 信号 | 简化 |
|------|------|------|
| 重复的逻辑 | 相同的 5 行以上在多个地方 | 提取为共享函数 |
| 死代码 | 无法到达的分支、未使用的变量、已注释的块 | 删除（确认它确实已死亡后） |
| 不必要的抽象 | 没有价值的包装器 | 内联包装器，直接调用底层函数 |
| 过度设计的模式 | 工厂工厂、策略策略 | 替换为简单的直接方法 |
| 重复的类型断言 | 强制转换为已经推断的类型 | 删除断言 |

### 第 3 步：增量应用更改

一次做一个简化。每次更改后运行测试。**将重构更改与功能或错误修复更改分开提交。** 一个重构并添加功能的 PR 是两个 PR——分开它们。

```
对于每个简化：
1. 进行更改
2. 运行测试套件
3. 如果测试通过 → 提交（或继续下一个简化）
4. 如果测试失败 → 撤销并重新考虑
```

避免将多个简化批量到一个未经测试的更改中。如果某件事出错了，你需要知道是哪个简化导致的。

**500 规则：** 如果重构将触及超过 500 行，投资于自动化（codemods、sed 脚本、AST 转换）而不是手动进行更改。手动编辑在该规模下容易出错且令人筋疲力尽。

### 第 4 步：验证结果

所有简化完成后，退后并评估整体：

```
比较之前和之后：
- 简化版本是否确实更容易理解？
- 你是否引入了与代码库不一致的新模式？
- 差异是否干净且可审查？
- 你的队友会批准这个更改吗？
```

如果“简化”版本更难理解或审查，请撤销。不是每个简化尝试都会成功。

## 语言特定指南

### TypeScript / JavaScript

```typescript
// 简化：不必要的异步包装器
// 之前
async function getUser(id: string): Promise<User> {
  return await userService.findById(id);
}
// 之后
function getUser(id: string): Promise<User> {
  return userService.findById(id);
}

// 简化：冗长的条件赋值
// 之前
let displayName: string;
if (user.nickname) {
  displayName = user.nickname;
} else {
  displayName = user.fullName;
}
// 之后
const displayName = user.nickname || user.fullName;

// 简化：手动数组构建
// 之前
const activeUsers: User[] = [];
for (const user of users) {
  if (user.isActive) {
    activeUsers.push(user);
  }
}
// 之后
const activeUsers = users.filter((user) => user.isActive);

// 简化：冗余布尔返回
// 之前
function isValid(input: string): boolean {
  if (input.length > 0 && input.length < 100) {
    return true;
  }
  return false;
}
// 之后
function isValid(input: string): boolean {
  return input.length > 0 && input.length < 100;
}
```

### Python

```python
# 简化：冗长的字典构建
# 之前
result = {}
for item in items:
    result[item.id] = item.name
# 之后
result = {item.id: item.name for item in items}

# 简化：带早期返回的嵌套条件
# 之前
def process(data):
    if data is not None:
        if data.is_valid():
            if data.has_permission():
                return do_work(data)
            else:
                raise PermissionError("No permission")
        else:
            raise ValueError("Invalid data")
    else:
        raise TypeError("Data is None")
# 之后
def process(data):
    if data is None:
        raise TypeError("Data is None")
    if not data.is_valid():
        raise ValueError("Invalid data")
    if not data.has_permission():
        raise PermissionError("No permission")
    return do_work(data)
```

### React / JSX

```tsx
// 简化：冗长的条件渲染
// 之前
function UserBadge({ user }: Props) {
  if (user.isAdmin) {
    return <Badge variant="admin">Admin</Badge>;
  } else {
    return <Badge variant="default">User</Badge>;
  }
}
// 之后
function UserBadge({ user }: Props) {
  const variant = user.isAdmin ? 'admin' : 'default';
  const label = user.isAdmin ? 'Admin' : 'User';
  return <Badge variant={variant}>{label}</Badge>;
}

// 简化：通过中间组件的属性钻取
// 之前——考虑是否使用上下文或组合更好。
// 这是一个判断——标记它，不要自动重构。
```

## 常见理由

| 理由 | 现实 |
|------|------|
| “它已经可以工作了，不需要碰它” | 可以工作的代码如果难以阅读，在它出问题时将难以修复。现在简化将节省未来每次更改的时间。 |
| “行数少总是更简单” | 1 行嵌套三元运算符不比 5 行 if/else 更简单。简单性是关于理解速度，而不是行数。 |
| “我会快速简化这个不相关的代码” | 无范围的简化会产生噪音的差异，并导致你没有打算更改的代码发生回归。保持专注。 |
| “类型使代码自说明” | 类型说明结构，而不是意图。一个命名良好的函数比类型签名更好地说明意图。 |
| “这个抽象以后可能有用” | 不要保留推测性的抽象。如果现在没有使用，它就是没有价值的复杂性。删除它，在需要时再添加。 |
| “原始作者一定有原因” | 也许。检查 git blame——应用切斯特顿栅栏。但累积的复杂性往往没有原因；它是压力下迭代的残留物。 |
| “我会在添加功能时重构” | 将重构与功能工作分开。混合更改更难审查、撤销和理解历史记录。 |

## 信号旗

- 简化需要修改测试才能通过（你可能改变了行为）
- “简化”的代码比原始代码更长且更难理解
- 重命名以匹配你的偏好而不是项目规范
- 因为“使代码更干净”而移除错误处理
- 简化你不太理解的代码
- 将许多简化批量到一个大而难以审查的提交中
- 在未经要求的情况下重构当前任务范围之外的代码

## 验证

完成一次简化后：

- [ ] 所有现有测试在不修改的情况下通过
- [ ] 构建成功，没有新的警告
- [ ] 静态分析器/格式化器通过（没有风格回归）
- [ ] 每个简化都是一个可审查的增量更改
- [ ] 差异干净——没有无关的更改混合在一起
- [ ] 简化代码遵循项目规范（与 CLAUDE.md 或等效文件检查）
- [ ] 没有移除或削弱错误处理
- [ ] 没有留下死代码（未使用的导入、无法到达的分支）
- [ ] 一个队友或审查代理会批准这个更改作为净改进
