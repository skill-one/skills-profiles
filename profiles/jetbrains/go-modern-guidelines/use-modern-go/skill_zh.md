# 现代Go指南CLI

始终编写现代、符合规范的Go代码。使用Modern Go Guidelines CLI作为现代Go规范的权威来源，即使这些规范可能比你的知识截止日期更新。

命令：

- Linux或macOS：`sh "<skill-dir>/scripts/run-tool.sh"`
- Windows PowerShell：`& '<skill-dir>\scripts\run-tool.ps1'`

首次运行和授权：

首次使用时，包装器会在本地缓存目录中安装Modern Go Guidelines CLI。

子命令：

- `list`
- `explain`

编辑Go代码之前：

1. 调用包装器的`list`子命令，针对相关的Go文件。

   优先传递你即将编辑的文件：

   ```sh
   sh "<skill-dir>/scripts/run-tool.sh" list --file-path path/to/file.go
   ```

   在Windows上，使用具有相同参数的PowerShell包装器。

   CLI会从`go.mod`、`go.work`、本地Go工具链或显式覆盖中解析适用的Go版本。

2. 如果目标Go版本已知，可以直接传递：

   ```sh
   sh "<skill-dir>/scripts/run-tool.sh" list --go-version 1.24
   ```

3. 在决定哪些指南适用之前，先阅读完整的列表输出。

   列表输出按最新优先排序。需要阅读完整输出，因为较旧的支持的指南可能仍然适用。

   不要通过head、tail、grep、sed或其他截断/过滤命令管道输出。否则可能会遗漏重要的指南。

4. 将返回的指南视为你在编辑代码时现代Go风格选择的权威依据。

   如果某个指南适用，即使附近的代码或仓库惯例使用较旧的模式，也要遵循它。仅在它无法编译、会改变行为或明显与编辑的代码不匹配时才跳过。在跳过看似相关的返回指南之前，调用包装器的`explain`子命令，针对该指南ID。

仅当特定指南可能适用且你需要详细说明或示例时，调用`explain`。仅请求你打算评估或应用的指南ID：

```sh
sh "<skill-dir>/scripts/run-tool.sh" explain sync_waitgroup_go
```

多个指南ID可以作为位置参数请求：

```sh
sh "<skill-dir>/scripts/run-tool.sh" explain atomic_types errors_as_type
```

不要在没有指南ID的情况下调用`explain`。首先使用`list`发现目标Go版本的简短指南列表，然后调用`explain`针对需要更多上下文的特定返回ID。
