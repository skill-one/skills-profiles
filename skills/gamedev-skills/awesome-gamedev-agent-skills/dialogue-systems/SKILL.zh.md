---
name: dialogue-systems
description: 构建分支对话和叙事——一个带有条件、变量和本地化钩子的节点/选择图——并选择使用Ink或Yarn Spinner等创作工具，或自定义数据驱动运行器。引擎无关。当用户提到对话系统、分支对话、对话树、选择、Ink (.ink)、Yarn Spinner (.yarn) 或NPC对话时使用。
---

# 对话系统

将模型对话视为一个**图**：节点包含台词，选择分支流程，条件控制选项，变量记录玩家的行为。第一个真正的决策是*构建还是购买*——采用成熟的创作工具（**Ink**或**Yarn Spinner**）或编写一个小型的数据驱动运行器。这项技能同时适用于Ink和Yarn；`视觉小说`和`角色扮演游戏`（RPG）类型使用它。

## 何时使用

- 用于设计分支对话、选择菜单或影响后续对话的叙事状态（标志、关系值）。
- 用于在Ink、Yarn Spinner和自定义JSON/资源格式之间进行选择。
- 用于将对话脚本连接到游戏循环（推进台词、展示选择、运行命令、解析变量）。

**不使用的情况**：对于引擎UI（文本框、肖像、选择按钮），使用`godot-ui-control`或引擎的UI技能。对于跨会话持久化叙事变量，使用`save-systems`。对于Godot/Unity中的数据作为资源，请参阅`godot-resources` / `unity-scriptableobjects`。

## 核心工作流程

1. **选择创作方法**。
   - **Ink** — 以文本优先、作家友好、编织/收集流程；非常适合台词密集型或选择式冒险（CYOA）叙事。通过ink运行时 / inkle插件集成。
   - **Yarn Spinner** — 基于节点、显式的`<<命令>>`，非常适合游戏驱动的对话，具有大量引擎钩子。
   - **自定义运行器** — 一个JSON/资源图 + 一个小型解释器，当你需要完全控制或最小依赖时使用。不要构建*语言*；构建一个图。
2. **定义节点契约**。节点产生以下之一：一条台词（说话者 + 文本）、一组选择、一个命令/副作用，或一个结束/跳转。运行器通过节点并把手台词/选择交给UI。
3. **将变量与流程分离**。保留一个变量存储（布尔值、数字、字符串），对话读取/写入；用条件控制选择。
4. **从一开始就本地化**。使用**台词ID**而不是原始字符串进行创作，以便显示的文本来自按区域键值对字符串表。
5. **从游戏循环驱动**。运行器是一个状态机：`当前`节点 → 发出内容 → 等待输入（继续或选择）→ 推进。
6. **通过遍历分支进行验证**。执行每个选择路径；确认条件、变量写入，并确保每个分支到达结束或有效跳转。

## 模式

### 1. 引擎无关的对话图（数据而非代码）

```json
{
  "start": "guard_intro",
  "nodes": {
    "guard_intro": {
      "speaker": "Guard", "line": "DLG_GUARD_001",
      "choices": [
        { "text": "DLG_OPT_BRIBE", "to": "bribe", "if": "gold >= 50" },
        { "text": "DLG_OPT_LEAVE", "to": "end" }
      ]
    },
    "bribe": {
      "speaker": "Guard", "line": "DLG_GUARD_BRIBED",
      "set": { "gate_open": true, "gold": "gold - 50" },
      "next": "end"
    },
    "end": { "end": true }
  }
}
```

`line`/`text`是**字符串表ID**（本地化），不是原始文本。`if`控制选择；`set`修改变量存储。遍历此图的完整解释器在`references/runner.md`中。

### 2. 运行器步骤（图上的状态机）

```gdscript
# 运行器包含当前节点和变量存储；UI调用advance()。
func present(node):
    if node.has("line"):
        ui.show_line(node.speaker, localize(node.line))
    if node.has("choices"):
        var shown = node.choices.filter(func(c): return eval_cond(c.get("if", "")))
        ui.show_choices(shown)            # 只有条件通过的选择

func choose(choice):                       # 玩家点击选择时调用
    apply_set(choice.get("set", {}))       # 写入变量
    goto(choice.to)

func goto(id):
    current = graph.nodes[id]
    apply_set(current.get("set", {}))
    if current.get("end", false): ui.close(); return
    present(current)
    if current.has("next") and not current.has("choices"):
        goto(current.next)                 # 自动推进线性节点
```

### 3. Ink — 使用节点、选择和变量（inkle）

```ink
// Ink: '*' = 一次性选择，'+' = 黏性。括号内文本仅在选项中显示，不在打印结果中。'->'转移；'-> END'停止流程。
VAR gold = 60

=== guard_intro ===
守卫挡住了门。
* {gold >= 50} [提供50金币]   "给你。"
    ~ gold = gold - 50
    守卫收下并让开。 -> END
* [离开]   你转身离开。 -> END
```

Ink跟踪每个节点的查看次数，因此`{visited_knot}`是一个内置条件。变量是全局（`VAR`）或临时（`~ temp`）。

### 4. Yarn Spinner — 节点、选项和命令（Yarn Spinner 3.x）

```yarn
title: GuardIntro
---
<<declare $gold = 60>>
<<declare $gate_open = false>>
Guard: 你不能通过。
-> 提供50金币 <<if $gold >= 50>>
    <<set $gold = $gold - 50>>
    Guard: ...好吧。通行。
    <<set $gate_open to true>>
-> 离开
    Guard: 好选择。
===
```

Yarn台词可能以`Speaker:`开头；选项使用`->`；`<<set>>`/`<<declare>>`管理`$变量`；`<<if>>`控制选项；`<<jump NodeName>>`在节点间移动。在文本中插入值使用`{$gold}`。在首次使用前声明每个变量：未声明的变量仍然编译（Yarn推断其类型和零/假/空初始值），但这会隐藏拼写错误。这些结构自Yarn Spinner 2.x以来未更改。

## 陷阱

- **硬编码显示字符串**而不是台词ID会使本地化成为重写。从一开始就针对字符串表创作。
- **为简单的分支树发明脚本语言**。如果你只需要台词+选择+标志，JSON/资源图加50行运行器比必须维护的解析器更优。在作家需要真实流程控制时使用Ink/Yarn。
- **变量与UI耦合**：将叙事状态单独存储，以便相同的对话在过场动画、菜单和测试中工作。通过`save-systems`持久化它。
- **无法到达或死路的节点**：没有`next`、选择或结束的节点会静默卡住。验证每个节点是否终止或分支。
- **在玩家可以重访的台词节点中修改状态**会导致重复应用（`gold`被消耗两次）。在过渡时应用`set`，或用已见标志控制。
- **意外混合Ink的`*`（一次性）和`+`（黏性）**：循环菜单需要黏性`+`选择，否则选项在第一次使用后消失。

## 参考

- `references/ink-and-yarn.md` — 并列语法速查表（选择、转移/跳转、变量、条件、包含）和集成说明。
- `references/runner.md` — 一个完整的自定义对话运行器：图模式、条件/表达式评估、变量存储和本地化查找。

## 相关技能

- `save-systems` — 持久化叙事变量和已见标志。
- `godot-resources`, `unity-scriptableobjects` — 将对话作为引擎数据存储。
- `godot-ui-control` — 渲染文本框、肖像和选择按钮。
- `visual-novel`, `rpg` — 组成此技能的类型。
