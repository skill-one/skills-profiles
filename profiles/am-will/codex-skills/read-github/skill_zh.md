# 阅读 GitHub 文档

通过 gitmcp.io MCP 服务访问 GitHub 仓库文档和代码。

## URL 转换

将 GitHub URL 转换为 gitmcp.io：
- `github.com/owner/repo` → `gitmcp.io/owner/repo`
- `https://github.com/karpathy/llm-council` → `https://gitmcp.io/karpathy/llm-council`

## 命令行使用

`scripts/gitmcp.py` 脚本提供对仓库文档的命令行访问。

### 列出可用工具

```bash
python3 scripts/gitmcp.py list-tools owner/repo
```

### 获取文档

获取完整的文档文件（README、文档等）：

```bash
python3 scripts/gitmcp.py fetch-docs owner/repo
```

### 搜索文档

在仓库文档中进行语义搜索：

```bash
python3 scripts/gitmcp.py search-docs owner/repo "query"
```

### 搜索代码

使用 GitHub 搜索 API 搜索代码（精确匹配）：

```bash
python3 scripts/gitmcp.py search-code owner/repo "function_name"
```

### 获取引用的 URL

获取文档中提到的 URL 内容：

```bash
python3 scripts/gitmcp.py fetch-url owner/repo "https://example.com/doc"
```

### 直接调用工具

直接调用任何 MCP 工具：

```bash
python3 scripts/gitmcp.py call owner/repo tool_name '{"arg": "value"}'
```

## 工具名称

工具名称会动态地加上仓库名称（下划线前缀）：
- `karpathy/llm-council` → `fetch_llm_council_documentation`
- `facebook/react` → `fetch_react_documentation`
- `my-org/my-repo` → `fetch_my_repo_documentation`

## 可用的 MCP 工具

对于任何仓库，这些工具可用：

1. **fetch_{repo}_documentation** - 获取整个文档。对于一般性问题，应首先调用。
2. **search_{repo}_documentation** - 在文档中语义搜索。用于特定查询。
3. **search_{repo}_code** - 通过 GitHub API 搜索代码（精确匹配）。返回匹配的文件。
4. **fetch_generic_url_content** - 获取文档中引用的任何 URL 内容，并遵守 robots.txt。

## 工作流程

1. 当给定 GitHub 仓库时，首先获取文档以了解项目
2. 使用 search-docs 搜索关于用法或特性的具体问题
3. 使用 search-code 查找实现或特定函数
4. 使用 fetch-url 获取文档中提到的外部引用
