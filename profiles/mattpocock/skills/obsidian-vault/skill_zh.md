# Obsidian Vault

## Vault 位置

`/mnt/d/Obsidian Vault/AI Research/`

根目录层级较为扁平。

## 命名规范

- **索引笔记**：聚合相关主题（例如，`Ralph Wiggum Index.md`，`Skills Index.md`，`RAG Index.md`）
- 笔记名称使用**标题大小写**
- 不使用文件夹进行组织 - 而是使用链接和索引笔记

## 链接

- 使用 Obsidian `[[wikilinks]]` 语法：`[[笔记标题]]`
- 笔记在底部链接到依赖项/相关笔记
- 索引笔记只是 `[[wikilinks]]` 的列表

## 工作流

### 搜索笔记

```bash
# 按文件名搜索
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "关键词"

# 按内容搜索
grep -rl "关键词" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```

或者直接在 Vault 路径上使用 Grep/Glob 工具。

### 创建新笔记

1. 文件名使用**标题大小写**
2. 按照 Vault 规则将内容作为学习单元编写
3. 在底部为相关笔记添加 `[[wikilinks]]`
4. 如果是编号序列的一部分，使用层级编号方案

### 查找相关笔记

跨 Vault 搜索 `[[笔记标题]]` 以查找反向链接：

```bash
grep -rl "\\[\\[笔记标题\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```

### 查找索引笔记

```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```
