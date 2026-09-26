# Context7 文档获取器

通过 Context7 API 获取当前库文档。

**重要提示**：`CONTEXT7_API_KEY` 存储在 Context7 技能安装所在的技能文件夹的 .env 文件中。请在那里查找。.env 文件是隐藏文件。

示例：
~/.agents/skills/context7/.env
~/.claude/skills/context7/.env

## 工作流程

### 1. 搜索库

```bash
python3 ~/.codex/skills/context7/scripts/context7.py search "<库名>"
```

示例：
```bash
python3 ~/.codex/skills/context7/scripts/context7.py search "next.js"
```

返回库元数据，包括步骤 2 所需的 `id` 字段。

### 2. 获取文档上下文

```bash
python3 ~/.codex/skills/context7/scripts/context7.py context "<库id>" "<查询>"
```

示例：
```bash
python3 ~/.codex/skills/context7/scripts/context7.py context "/vercel/next.js" "app router middleware"
```

选项：
- `--type txt|md` - 输出格式（默认：txt）
- `--tokens N` - 限制响应 token 数量

## 快速参考

| 任务 | 命令 |
|------|---------|
| 查找 React 文档 | `search "react"` |
| 获取 React hooks 信息 | `context "/facebook/react" "useEffect cleanup"` |
| 查找 Supabase | `search "supabase"` |
| 获取 Supabase 认证 | `context "/supabase/supabase" "authentication row level security"` |

## 使用场景

- 在实现任何库依赖功能之前
- 当不确定当前 API 签名时
- 用于库版本特定的行为
- 验证最佳实践和模式
