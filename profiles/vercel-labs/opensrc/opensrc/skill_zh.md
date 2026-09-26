# 使用 opensrc 获取源代码

获取依赖项的源代码，以便代理可以读取实现，而不仅仅是类型。它会在正确的版本标签下克隆存储库，并将它们全局缓存到 `~/.opensrc/`。

## 核心模式

```bash
rg "parse" $(opensrc path zod)
cat $(opensrc path zod)/src/types.ts
find $(opensrc path zod) -name "*.test.ts"
```

`opensrc path <pkg>` 会打印缓存的源代码的绝对路径。如果未缓存，它会自动获取。进度输出到 stderr，路径输出到 stdout，因此 `$(opensrc path ...)` 可以在子 shell 中工作。

## 获取源代码

```bash
opensrc path zod
opensrc path pypi:requests
opensrc path crates:serde
opensrc path facebook/react

# 同时获取多个包
opensrc path zod react next
opensrc path pypi:requests pypi:flask
opensrc path crates:serde crates:tokio

# 指定版本
opensrc path zod@3.22.0
opensrc path pypi:flask@3.0.0
opensrc path owner/repo@v1.0.0
opensrc path owner/repo#main
```

### 版本解析

对于 npm 包，opensrc 会从锁文件中自动检测已安装的版本（`package-lock.json`、`pnpm-lock.yaml`、`yarn.lock`）。使用 `--cwd` 从不同的项目解析：

```bash
opensrc path zod --cwd /path/to/project
```

对于 PyPI 和 crates.io，使用显式版本或最新版本。对于存储库，使用 `@ref` 或 `#ref` 来固定分支、标签或提交。

## 管理缓存

源代码全局缓存到 `~/.opensrc/`（可以使用 `OPENSRC_HOME` 覆盖）。

```bash
opensrc list                     # 显示所有缓存的源代码
opensrc list --json              # JSON 输出

opensrc remove zod               # 删除一个包
opensrc remove facebook/react    # 删除一个存储库

opensrc clean                    # 删除所有内容
opensrc clean --npm              # 仅 npm 包
opensrc clean --pypi             # 仅 PyPI 包
opensrc clean --crates           # 仅 crates.io 包
opensrc clean --packages         # 所有包，保留存储库
opensrc clean --repos            # 所有存储库，保留包
```

## 何时获取源代码

当你需要时获取源代码：
- 理解类型无法揭示的内部行为
- 调试意外的库行为
- 从知名实现中学习模式
- 验证函数如何处理边界情况

对于文档或类型可以回答的简单 API 使用问题，不要获取源代码。
