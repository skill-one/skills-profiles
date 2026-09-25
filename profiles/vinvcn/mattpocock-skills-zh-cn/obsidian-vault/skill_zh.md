# Obsidian Vault

## Vault 位置

`/mnt/d/Obsidian Vault/AI Research/`

根目录基本保持扁平。

## 命名规范

- **索引笔记**：聚合相关 topics（例如 `Ralph Wiggum Index.md`、`Skills Index.md`、`RAG Index.md`）
- 所有笔记名称使用 **Title case**
- 不使用文件夹进行组织；改用链接和索引笔记

## 链接

- 使用 Obsidian `[[wikilinks]]` 语法：`[[笔记标题]]`
- 笔记在底部链接依赖项/相关笔记
- 索引笔记只是 `[[wikilinks]]` 列表

## 工作流

### 搜索笔记

```bash
# 按文件名搜索
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "关键词"

# 按内容搜索
grep -rl "关键词" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```

或直接在 vault 路径上使用 Grep/Glob 工具。

### 创建新笔记

1. 文件名使用 **Title Case**
2. 按 vault 规则，把内容写成一个 learning unit
3. 在底部添加指向相关笔记的 `[[wikilinks]]`
4. 如果属于编号序列，使用层级编号方案

### 查找相关笔记

在 vault 中搜索 `[[笔记标题]]` 来找反向链接：

```bash
grep -rl "\\[\\[笔记标题\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```

### 查找索引笔记

```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```
