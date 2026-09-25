# mem — 代理记忆存储

一个用于存储和检索记忆的命令行工具，支持全文搜索。数据存储在本地 `~/.mem/mem.db` 中。

## 使用场景

- **记录** 用户偏好、项目决策、重要事实
- **存储** 代码片段、命令、配置以便日后调用
- **搜索** 知识库，在向用户询问信息前检查是否已存储相关内容
- **附加** 图片（截图、图表）到记忆中

## 命令

三个操作符：无操作符 = 检索，`+` = 记录，`-` = 忘记。

### 检索（搜索、列出、获取）

```bash
mem                             # 列出最近的记忆
mem "deploy"                    # 全文搜索
mem "database" --tag db         # 按标签搜索
mem 7sjtNVyZrNIa                # 通过 ID 获取完整内容
mem --tag prefs                 # 按标签列出
mem "api" --limit 5 --json     # 限制结果数量，JSON 输出
mem --full                      # 显示所有记忆的完整内容
```

### 记录

```bash
mem + "用户偏好深色模式" --tag prefs
mem + "部署： bun build --compile" --tag deploy
mem + "选择 SQLite 以简化" --tag architecture
mem + --image ./screenshot.png --title "当前 UI" --tag ui
echo "长内容" | mem + --tag notes
```

### 忘记

```bash
mem - <id>                      # 删除一条记忆
mem - id1 id2 id3               # 删除多条
```

## 管道操作

```bash
mem "旧记忆" --json | jq -r '.[].id' | xargs -I{} mem - {}
echo "长内容" | mem + --tag notes
```

## 最佳实践

1. **统一使用标签** — 使用小写、描述性的标签，如 `prefs`、`api`、`deploy`、`db`
2. **搜索后再提问** — 在向用户提问前检查是否已存储相关信息
3. **记录决策** — 在进行架构或设计决策时，记录决策的依据
4. **保持记忆原子性** — 每条记忆只包含一个概念，以提高可搜索性

## 输出格式

- 默认：每条结果一行摘要
- `--full`：完整内容内联显示
- `--json`：结构化 JSON 格式，便于解析
