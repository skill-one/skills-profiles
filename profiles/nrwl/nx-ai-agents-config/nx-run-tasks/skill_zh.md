你可以按以下方式使用 Nx 运行任务。

请注意，如果用户没有全局安装 Nx，可能需要用 npx/pnpx/yarn 前缀。查看 package.json 或 lockfile 以确定使用的包管理器。

要了解任何命令的更多详细信息，请使用 `--help` 运行它（例如 `nx run-many --help`，`nx affected --help`）。

## 了解哪些任务可以运行

你可以通过 `nx show project <projectname> --json` 查看这些信息，例如 `nx show project myapp --json`。它包含一个 `targets` 部分，其中包含有关可运行目标的详细信息。你也可以直接查看 `package.json` 脚本或 `project.json` 目标，但你可能会错过 Nx 插件推断的任务。

## 运行单个任务

```
nx run <project>:<task>
```

其中 `project` 是在 `package.json` 或 `project.json`（如果存在）中定义的项目名称。

## 运行多个任务

```
nx run-many -t build test lint typecheck
```

你可以使用 `-p` 标志过滤到特定项目，否则它在所有项目上运行。你也可以使用 `--exclude` 排除项目，以及 `--parallel` 控制并行进程的数量（默认为 3）。

示例：

- `nx run-many -t test -p proj1 proj2` — 测试特定项目
- `nx run-many -t test --projects=*-app --exclude=excluded-app` — 测试匹配模式的项目
- `nx run-many -t test --projects=tag:api-*` — 按标签测试项目

## 运行受影响项目的任务

使用 `nx affected` 仅在已更改的项目和依赖已更改项目的项目上运行任务。这在 CI 和大型工作区中特别有用。

```
nx affected -t build test lint
```

默认情况下，它将基于基础分支进行比较。你可以自定义此设置：

- `nx affected -t test --base=main --head=HEAD` — 与特定基础和头进行比较
- `nx affected -t test --files=libs/mylib/src/index.ts` — 直接指定已更改的文件

## 有用的标志

这些标志与 `run`、`run-many` 和 `affected` 一起使用：

- `--skipNxCache` — 即使结果已缓存，也要重新运行任务
- `--verbose` — 打印附加信息，例如堆栈跟踪
- `--nxBail` — 在第一个失败的任务后停止执行
- `--configuration=<name>` — 使用特定配置（例如 `production`）
