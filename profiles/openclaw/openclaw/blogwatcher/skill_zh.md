# blogwatcher

使用 `blogwatcher` 命令行工具跟踪博客和 RSS/Atom 提要的更新。

安装

- Go: `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`

快速入门

- `blogwatcher --help`

常用命令

- 添加博客: `blogwatcher add "我的博客" https://example.com`
- 列出博客: `blogwatcher blogs`
- 扫描更新: `blogwatcher scan`
- 列出文章: `blogwatcher articles`
- 标记文章为已读: `blogwatcher read 1`
- 标记所有文章为已读: `blogwatcher read-all`
- 删除博客: `blogwatcher remove "我的博客"`

示例输出

```
$ blogwatcher blogs
已跟踪博客 (1):

  xkcd
    URL: https://xkcd.com
```

```
$ blogwatcher scan
正在扫描 1 个博客...

  xkcd
    源: RSS | 发现: 4 | 新增: 4

总共发现 4 篇新文章！
```

注意

- 使用 `blogwatcher <命令> --help` 来发现标志和选项。
