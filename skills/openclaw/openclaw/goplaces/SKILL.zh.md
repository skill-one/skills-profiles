---
name: goplaces
description: 使用goplaces查询Google Places，进行文本搜索、地点详情、解析、评论或可脚本化的JSON。
---

# goplaces

现代 Google Places API (新版本) 命令行工具。默认输出人类可读格式，使用 `--json` 参数用于脚本。

安装

- Homebrew: `brew install steipete/tap/goplaces`

配置

- 需要 `GOOGLE_PLACES_API_KEY`。
- 可选：`GOOGLE_PLACES_BASE_URL` 用于测试/代理。

常用命令

- 搜索：`goplaces search "咖啡" --open-now --min-rating 4 --limit 5`
- 偏好：`goplaces search "披萨" --lat 40.8 --lng -73.9 --radius-m 3000`
- 分页：`goplaces search "披萨" --page-token "NEXT_PAGE_TOKEN"`
- 解析：`goplaces resolve "Soho, 伦敦" --limit 5`
- 详情：`goplaces details <place_id> --reviews`
- JSON：`goplaces search "寿司" --json`

注意事项

- `--no-color` 或 `NO_COLOR` 禁用 ANSI 颜色。
- 价格等级：0..4 (免费 -> 非常昂贵)。
- 类型筛选仅发送第一个 `--type` 值 (API 接受一个)。
