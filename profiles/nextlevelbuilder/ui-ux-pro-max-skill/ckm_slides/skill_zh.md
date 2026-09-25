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

## 参考文献（知识库）

| 主题 | 文件 |
|-------|------|
| 布局模式 | `references/layout-patterns.md` |
| HTML模板 | `references/html-template.md` |
| 文案公式 | `references/copywriting-formulas.md` |
| 幻灯片策略 | `references/slide-strategies.md` |

## 路由

1. 从`$ARGUMENTS`（第一个单词）解析子命令
2. 加载相应的`references/{subcommand}.md`
3. 使用剩余参数执行
