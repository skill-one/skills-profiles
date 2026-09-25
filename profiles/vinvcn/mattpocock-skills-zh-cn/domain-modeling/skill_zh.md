# 领域建模

在设计过程中主动构建并打磨项目的领域模型。这是 *主动* 的学科：挑战术语、发明 edge-case 场景，并在概念形成时立即写入术语表和决策记录。

## 文件结构

多数仓库只有一个 context：

```text
/
|- CONTEXT.md
|- docs/
|  `- adr/
|     |- 0001-event-sourced-orders.md
|     `- 0002-postgres-for-write-model.md
`- src/
```

如果 root 目录有 `CONTEXT-MAP.md`，说明仓库有多个 context。map 指向每个 context 的位置：

```text
/
|- CONTEXT-MAP.md
|- docs/
|  `- adr/                          -> 全局决策
`- src/
   |- ordering/
   |  |- CONTEXT.md
   |  `- docs/adr/                  -> 特定 context 决策
   `- billing/
      |- CONTEXT.md
      `- docs/adr/
```

按需懒创建文件：只有在有内容要写时才创建。如果没有 `CONTEXT.md`，当第一个术语被解决时创建它。如果没有 `docs/adr/`，当第一个 ADR 需要出现时创建它。

## 会话期间

### 与术语表进行挑战

当用户使用的术语与 `CONTEXT.md` 中既有语言冲突时，立即指出。"您的术语表将 'cancellation' 定义为 X，但您似乎想表达 Y - 到底是哪个意思？"

### 锤炼模糊语言

当用户使用模糊或过载术语时，提出一个精确的规范术语。"您提到 'account' - 您是指 Customer 还是 User？这两者不同。"

### 讨论具体场景

讨论领域关系时，用具体场景做压力测试。发明能探测 edge cases 的场景，迫使用户精确定义概念之间的边界。

### 与代码交叉引用

当用户描述某事如何工作时，检查代码是否同意。如果发现矛盾，要指出："您的代码取消整个 Orders，但您刚才说部分取消是可能的 - 到底哪个正确？"

### 内联更新 CONTEXT.md

当一个术语被解决时，立即更新 `CONTEXT.md`。不要批量攒到最后；随着概念出现就捕获。使用 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) 中的格式。

`CONTEXT.md` 必须完全不包含实现细节。不要把 `CONTEXT.md` 当作 spec、草稿板或实现决策的仓库。它只是一份术语表。

### 勤俭地提供 ADR

只有以下三项都成立时，才提出创建 ADR：

1. **难以逆转** - 改变主意的成本有意义
2. **缺乏背景会令人惊讶** - 未来读者会疑惑 "为什么他们要这样做？"
3. **是真实权衡的结果** - 确实存在替代方案，而您基于具体理由选择了其中一个

缺少任一项就跳过 ADR。使用 [ADR-FORMAT.md](./ADR-FORMAT.md) 中的格式。
