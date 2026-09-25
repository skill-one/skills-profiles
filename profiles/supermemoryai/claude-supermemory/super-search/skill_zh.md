# 超级搜索

搜索 Supermemory 中的过往编码会话、决策和保存的信息。

## 如何搜索

使用用户的查询和可选的范围标志运行搜索脚本：

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/search-memory.cjs" [--user|--repo|--both] "USER_QUERY_HERE"
```

### 范围标志

- `--both`（默认）：并行搜索个人会话和项目记忆，涵盖团队成员
- `--user`：跨会话搜索个人/用户记忆
- `--repo`：跨团队成员搜索项目/仓库记忆

## 示例

- 用户询问"我昨天做了什么"：

  ```bash
  node "${CLAUDE_PLUGIN_ROOT}/scripts/search-memory.cjs" "work yesterday recent activity"
  ```

- 用户询问"我们如何实现认证"（项目特定）：

  ```bash
  node "${CLAUDE_PLUGIN_ROOT}/scripts/search-memory.cjs" --repo "authentication implementation"
  ```

- 用户询问"我的编码偏好是什么"：
  ```bash
  node "${CLAUDE_PLUGIN_ROOT}/scripts/search-memory.cjs" --user "coding preferences style"
  ```

## 展示结果

脚本输出带时间戳和相关性分数的格式化记忆结果。向用户清晰展示结果，并在需要时提供使用不同术语再次搜索的选项。
