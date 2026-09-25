# ordercli

使用 `ordercli` 检查过去的订单并跟踪活跃订单状态（目前仅支持 Foodora）。

快速入门（Foodora）

- `ordercli foodora countries`
- `ordercli foodora config set --country AT`
- `ordercli foodora login --email you@example.com --password-stdin`
- `ordercli foodora orders`
- `ordercli foodora history --limit 20`
- `ordercli foodora history show <orderCode>`

订单

- 活跃列表（到达/状态）：`ordercli foodora orders`
- 监控：`ordercli foodora orders --watch`
- 活跃订单详情：`ordercli foodora order <orderCode>`
- 历史详情 JSON：`ordercli foodora history show <orderCode> --json`

重新订购（添加到购物车）

- 预览：`ordercli foodora reorder <orderCode>`
- 确认：`ordercli foodora reorder <orderCode> --confirm`
- 地址：`ordercli foodora reorder <orderCode> --confirm --address-id <id>`

Cloudflare / 机器人保护

- 浏览器登录：`ordercli foodora login --email you@example.com --password-stdin --browser`
- 重用配置文件：`--browser-profile "$HOME/Library/Application Support/ordercli/browser-profile"`
- 导入 Chrome Cookie：`ordercli foodora cookies chrome --profile "Default"`

会话导入（无需密码）

- `ordercli foodora session chrome --url https://www.foodora.at/ --profile "Default"`
- `ordercli foodora session refresh --client-id android`

Deliveroo（WIP，目前无法使用）

- 需要 `DELIVEROO_BEARER_TOKEN`（可选 `DELIVEROO_COOKIE`）。
- `ordercli deliveroo config set --market uk`
- `ordercli deliveroo history`

注意事项

- 使用 `--config /tmp/ordercli.json` 进行测试。
- 在任何重新订购或更改购物车的操作前进行确认。
