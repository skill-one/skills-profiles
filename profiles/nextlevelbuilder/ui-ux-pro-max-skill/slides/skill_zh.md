# 幻灯片

具有数据可视化的战略HTML演示文稿设计。

## 使用场景

- 市场营销演示文稿和提案演示文稿
- 使用Chart.js的数据驱动型幻灯片
- 具有布局模式的战略幻灯片设计
- 优化了文案的演示文稿内容

## 子命令

| 子命令 | 描述 | 参考 |
|------------|-------------|-----------|
| `create` | 创建战略演示文稿幻灯片 | `references/create.md` |

## 脚本路径

此技能及其`references/`中的脚本路径相对于包含此`SKILL.md`的目录，而不是项目目录：`scripts/<文件>`是此技能自己的`scripts/`文件夹，而`../<技能>/scripts/<文件>`是与它一同安装的兄弟子技能。从该目录（Claude Code在技能加载时报告为技能的基本目录）构建完整路径，并将工作目录保持在项目根目录——脚本相对于它读取和写入项目文件，例如`docs/品牌指南.md`、`assets/设计令牌.json`或`src/`。

## 参考（知识库）

| 主题 | 文件 |
|-------|------|
| 布局模式 | `references/layout-patterns.md` |
| HTML模板 | `references/html-template.md` |
| 文案公式 | `references/copywriting-formulas.md` |
| 幻灯片策略 | `references/slide-strategies.md` |

## 路由

1. 从`$ARGUMENTS`（第一个单词）解析子命令
2. 加载相应的`references/{子命令}.md`
3. 使用剩余参数执行
