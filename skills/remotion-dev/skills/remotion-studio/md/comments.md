# remotion-studio (`remotion-dev/skills/remotion-studio`)

## comments

- user: 第一次用的新手, category: 坑, comment: 它是个常驻进程, 命令会一直挂着. 我以为跑完就退出, 顺手关了终端, 预览页立刻打不开了. 要长期预览就让它挂着或丢进 tmux.
- user: 前端兼职做视频, category: 妙用, comment: 我固定 --port=3000 再存成浏览器书签, 每天一键进工作台. 不固定的话端口随机分配, 书签天天失效.
- user: 远程开发党, category: 注意, comment: 打印的 URL 是 localhost, 我在远程服务器上跑, 本地浏览器打不开. 先做 SSH 端口转发 (ssh -L) 再访问就正常.
- user: 同时赶两个视频的独立开发者, category: 妙用, comment: 默认同项目已运行就只打印 URL 退出, 我想同时开两个预览, 加 --force-new 就强制再起一个新实例, 互不打架.
- user: 排查渲染问题的人, category: 注意, comment: 预览页报错看不懂别硬猜, 重启时加 --log=verbose, 日志会细到能定位是哪个 composition 出的问题, 默认 info 级别常不够用.
- user: 写脚本的运维老哥, category: 妙用, comment: 我拿它当探活: 没开时命令常驻, 已开时打印 URL 立即退出. 脚本里靠这个行为判断要不要重复拉起, 不会开出第二个重复实例.
