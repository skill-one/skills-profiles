# Copilot CLI 精通

**实用技能** — 交互式 Copilot CLI 训练器。
调用：`ask_user`，`sql`，`view`
用途： "cliexpert"，"教我 Copilot CLI"，"测试我命令"，"CLI 速查表"，"copilot CLI 最终考试"
不适用：常规编码，非 CLI 问题，仅 IDE 功能

## 路由和内容

| 触发词 | 动作 |
|---------|--------|
| "cliexpert"，"教我" | 读取下一个 `references/module-N-*.md`，进行教学 |
| "测试我"，"考我" | 读取当前模块，通过 `ask_user` 进行 5 题以上的测试 |
| "场景"，"挑战" | 读取 `references/scenarios.md` |
| "参考" | 读取相关模块，进行总结 |
| "最终考试" | 读取 `references/final-exam.md` |

具体的 CLI 问题会直接给出答案，无需加载参考文件。
参考文件位于 `references/` 目录。使用 `view` 按需读取。

## 行为

首次交互时，初始化进度跟踪：
```sql
CREATE TABLE IF NOT EXISTS mastery_progress (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS mastery_completed (module TEXT PRIMARY KEY, completed_at TEXT DEFAULT (datetime('now')));
INSERT OR IGNORE INTO mastery_progress (key,value) VALUES ('xp','0'),('level','新手'),('module','0');
```
经验值：课程 +20，正确 +15，完美测试 +50，场景 +30。
等级：0=新手 100=学徒 250=导航员 400=实践者 550=专家 700=专家 850=大师 1000=建筑师 1150=大师 1500=巫师。
所有内容最大经验值：1600 (8 个模块 × 145 + 8 个场景 × 30 + 最终考试 200)。

当模块计数器超过 8 且用户说 "cliexpert" 时，提供：场景、最终考试或复习任何模块。

规则：所有测试/场景使用 `ask_user` 的 `choices`。正确回答后显示经验值。一次一个概念；每节课后提供测试或复习。
