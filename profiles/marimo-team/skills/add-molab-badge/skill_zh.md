# 添加 molab 徽章

添加指向 marimo 笔记本的 "在 molab 中打开" 徽章。该徽章可以添加到任何目标：GitHub README、文档网站、博客文章、网页或任何其他 Markdown/HTML 文件。

## 说明

### 0. 为 molab 导出会话

如果 GitHub 仓库包含会话信息，molab 预览会显示得更好。这可以通过以下方式添加：

```bash
uvx marimo export session notebook.py
uvx marimo export session folder/
```

这会执行笔记本并导出它们的会话快照，molab 使用这些快照来提供预渲染的笔记本。

关键标志：

- `--sandbox` — 使用 PEP 723 依赖项在每个笔记本中运行隔离的环境
- `--continue-on-error` — 如果一个笔记本失败，继续处理其他笔记本
- `--force-overwrite` — 覆盖所有现有快照，即使它们是最新版本

### 1. 确定笔记本链接

用户可以通过以下两种方式提供笔记本链接：

- **用户直接提供链接。** 用户粘贴笔记本的 URL。直接使用这些链接——无需发现。
- **笔记本发现（仅限 README 目标）。** 如果用户要求将徽章添加到仓库的 README，但没有指定哪些笔记本，则发现它们：
  1. 在仓库中查找所有 marimo 笔记本文件（`.py` 文件）。使用 `Glob` 并使用模式如 `**/*.py`，然后检查 marimo 头 (`import marimo` 或 `app = marimo.App`) 以确认它们是 marimo 笔记本。
  2. 如果 README 已经有指向笔记本的链接（例如，通过 `marimo.app` 链接或现有徽章），则替换这些链接。
  3. 否则，询问用户哪些笔记本应该被链接。

### 2. 构建 molab URL

对于每个笔记本，使用以下格式构建 molab URL：

```
https://molab.marimo.io/github/{owner}/{repo}/blob/{branch}/{path_to_notebook}
```

- `{owner}/{repo}`：GitHub 的所有者和仓库名称。从 git 远程 (`git remote get-url origin`)、用户提供的 URL 或询问用户来确定。
- `{branch}`：通常是 `main`。从仓库的默认分支确认。
- `{path_to_notebook}`：相对于仓库根目录的 `.py` 笔记本文件路径。

### 3. 应用 `/wasm` 后缀规则

- 如果**替换**现有的 `marimo.app` 链接，则将 `/wasm` 添加到 molab URL。这是因为 `marimo.app` 在客户端运行笔记本（WASM），因此 molab 的等效项需要 `/wasm` 后缀来保留该行为。
- 如果添加**新的**徽章（不替换 `marimo.app` 链接），则**不要**添加 `/wasm`，除非用户明确要求。

### 4. 格式化徽章

使用以下 Markdown 徽章格式：

```markdown
[![在 molab 中打开](https://marimo.io/molab-shield.svg)](URL)
```

其中 `URL` 是构建的 molab URL（根据上述规则带有或没有 `/wasm`）。

对于 HTML 目标，使用：

```html
<a href="URL"><img src="https://marimo.io/molab-shield.svg" alt="在 molab 中打开" /></a>
```

### 5. 在目标中插入或替换徽章

- 当替换现有徽章或链接时：
  - 将 `marimo.app` URL 替换为等效的 `molab.marimo.io` URL。
  - 将旧的盾牌图像 URL（例如，`https://marimo.io/shield.svg` 或 camo 代理版本）替换为 `https://marimo.io/molab-shield.svg`。
  - 将 alt 文本设置为 `在 molab 中打开`。
  - 保留周围的文本和结构。
- 直接编辑目标文件。不要重写无关部分。
- 如果用户只想徽章的 Markdown/HTML（而不是编辑文件），直接输出它。

## 示例

**在 README 中替换 marimo.app 徽章：**

之前：
```markdown
[![](https://marimo.io/shield.svg)](https://marimo.app/github.com/owner/repo/blob/main/notebook.py)
```

之后：
```markdown
[![在 molab 中打开](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/owner/repo/blob/main/notebook.py/wasm)
```

注意：`/wasm` 被添加，因为这是替换了一个 `marimo.app` 链接。

**从用户提供的链接添加新的徽章：**

用户说："为这些笔记本添加 molab 徽章：`https://github.com/owner/repo/blob/main/demo.py`，`https://github.com/owner/repo/blob/main/tutorial.py`"

输出：
```markdown
[![在 molab 中打开](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/owner/repo/blob/main/demo.py)
[![在 molab 中打开](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/owner/repo/blob/main/tutorial.py)
```

注意：新徽章默认不带 `/wasm` 后缀。
