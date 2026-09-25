# blucli (blu)

使用 `blu` 来控制 Bluesound/NAD 播放器。

快速入门

- `blu devices` (选择目标)
- `blu --device <id> status`
- `blu play|pause|stop`
- `blu volume set 15`

目标选择（按优先级排序）

- `--device <id|name|alias>`
- `BLU_DEVICE`
- 配置默认值（如果设置）

常见任务

- 分组：`blu group status|add|remove`
- TuneIn 搜索/播放：`blu tunein search "query"`，`blu tunein play "query"`

脚本推荐使用 `--json`。更改播放前请确认目标设备。
