执行以下命令：

```bash
npx remotion studio --no-open
```

如果 Studio 已经打开，将打印 URL 并命令退出。
否则，将启动一个长时间运行的过程，并打印 URL。

在浏览器中打开 URL。

## 有用参数

| 参数 | 用途 |
| --- | --- |
| `--log=<level>` | 设置 `error`、`warn`、`info`（默认）或 `verbose` 日志。 |
| `--port=<number>` | 请求 Studio 服务器端口；否则 Remotion 会找到空闲端口。 |
| `--force-new` | 即使已为同一项目和端口运行 Studio，也启动另一个 Studio 实例。 |
