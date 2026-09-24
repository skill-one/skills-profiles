# Obsidian Vault

## Vault location

`/mnt/d/Obsidian Vault/AI Research/`

主要位于根目录层级，结构扁平。

## Naming conventions

- **索引笔记**：汇总相关主题（例如，`Ralph Wiggum Index.md`、`Skills Index.md`、`RAG Index.md`）
- 所有笔记名称均使用**标题大写**（Title Case）
- 不使用文件夹进行组织 - 改用链接和索引笔记

## Linking

- 使用 Obsidian `[[wikilinks]]` 语法：`[[笔记标题]]`
- 笔记在底部链接到依赖项/相关笔记
- 索引笔记仅为 `[[wikilinks]]` 列表

## Workflows

### 搜索笔记

```bash
# 按文件名搜索
find "/mnt/d/Obsidian Vault/AI Research/" -name "*.md" | grep -i "keyword"

# 按内容搜索
grep -rl "keyword" "/mnt/d/Obsidian Vault/AI Research/" --include="*.md"
```

或直接在仓库路径上使用 Grep/Glob 工具。

### 创建新笔记

1. 文件名使用**标题大写**（Title Case）
2. 以学习单元（按照仓库规则）编写内容
3. 在底部的相关笔记中添加 `[[wikilinks]]`
4. 若属于编号序列，则使用层级编号方案

### 查找相关笔记

在仓库中搜索 `[[笔记标题]]` 以查找反向链接：

```bash
grep -rl "\\[\\[Note Title\\]\\]" "/mnt/d/Obsidian Vault/AI Research/"
```

### 查找索引笔记

```bash
find "/mnt/d/Obsidian Vault/AI Research/" -name "*Index*"
```
