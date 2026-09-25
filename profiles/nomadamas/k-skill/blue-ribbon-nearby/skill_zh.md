# 蓝缎带附近

## 此技能的作用

根据用户提供的当前位置，查找蓝缎带调查的官方区域，并通过 k-skill-proxy 显示 **附近的蓝缎带美食店**。

- 不会自动估计位置。
- **必须先询问当前位置**。
- 位置字符串与官方 `zone` 列表匹配，并通过周边 JSON 端点缩小范围进行查找。
- 如果直接接收坐标，可以进行更精确的附近搜索。
- 附近搜索默认通过 k-skill-proxy (`/v1/blue-ribbon/nearby`) 进行。必须设置代理中的 `BLUE_RIBBON_SESSION_ID`。

## 使用场景

- "帮我找附近的美食店"
- "这里附近的蓝缎带美食店有什么？"
- "光化门附近的推荐餐厅"
- "只显示我附近的蓝缎带餐厅"

## 路由规则

- 当用户询问 **美食店** / **附近餐厅** / **附近餐馆** 时，默认优先考虑此技能。
- 但如果用户指定了蓝缎带以外的其他标准（例如：芒果街、百度地图评论、特定餐厅预订），则优先考虑该表面。

## 前置条件

- 互联网连接
- `node` 18+
- 此存储库的 `blue-ribbon-nearby` 包或相同逻辑

## 必须首先询问的问题

不要在没有位置信息的情况下直接搜索，必须首先询问。

- 推荐问题：`请告诉我您的当前位置。您可以使用社区/地铁站/地标/经纬度中方便的格式发送，我将帮您查找附近的蓝缎带美食店。`
- 如果位置不明确：`请再告诉我一次附近的地铁站或社区名称。`
- 如果收到坐标，则直接用于附近搜索。

## 接受的位置输入

- 社区/商圈：`成寿洞`, `光化门`, `板교`
- 地铁站/地标：`江南站`, `首尔站`, `COEX`
- 经纬度：`37.573713, 126.978338`

地标通过内部别名与最近的官方 Blue Ribbon zone 名称匹配。例如：`COEX` → `三成洞/大峙洞`

## 官方蓝缎带表面

- zone 目录：`https://www.bluer.co.kr/search/zone`
- 附近搜索 JSON：`https://www.bluer.co.kr/restaurants/map`
- 搜索页面：`https://www.bluer.co.kr/search`

关键的附近参数：

- `zone1`
- `zone2`
- `zone2Lat`
- `zone2Lng`
- `isAround=true`
- `ribbon=true`
- `ribbonType=RIBBON_THREE,RIBBON_TWO,RIBBON_ONE`
- `distance=500|1000|2000|5000`

直接搜索坐标时，使用 `latitude1`, `latitude2`, `longitude1`, `longitude2` bounding box。

## 工作流程

### 1. 首先询问当前位置

在没有询问位置的情况下不要开始搜索。

### 2. 解析位置

- 如果收到社区/地铁站/地标，则首先与官方 `https://www.bluer.co.kr/search/zone` 目录匹配。
- 对于像 COEX 这样不是官方 zone 名称的代表性地标，首先扩展为最接近的官方 zone 别名。
- 如果收到经纬度，则直接进入基于坐标的附近搜索。
- 如果最有可能的 zone 候选有多个，则只显示 2-3 个并再次确认。

### 3. 查询附近蓝缎带端点

默认通过 k-skill-proxy 获取附近结果。

```js
const { searchNearbyByLocationQuery } = require("blue-ribbon-nearby");

const result = await searchNearbyByLocationQuery("光化门", {
  distanceMeters: 1000,
  limit: 5
});

console.log(result.anchor);
console.log(result.items);
```

内部首先匹配 zone，然后将坐标和距离发送到代理的 `/v1/blue-ribbon/nearby`。代理使用 Premium 会话调用 Blue Ribbon upstream。

如果需要直接调用，可以使用 `useDirectApi: true` 选项，但没有 Premium 会话会返回 `premium_required` 错误。

### 4. 用简短的餐厅摘要回复

通常只整理 3-5 个。

- 餐厅名称
- 蓝缎带数量
- 代表性食物类别
- 地址
- 距离

## 完成条件

- 首先确认了用户的当前位置。
- 找到至少 1 个官方 Blue Ribbon 附近结果，或因代理未设置等原因无法获取结果并给出下一个问题。
- 结果按距离顺序简短整理。

## 浏览器回退（机器人绕过封锁）

如果 bluer.co.kr 阻止自动化访问（403），如果已安装 `rebrowser-playwright`，则会自动通过实际 Chrome 浏览器回退。

### 条件

- 必须安装 `rebrowser-playwright`：`npm install rebrowser-playwright`
- 系统中必须安装 Google Chrome
- 需要以 headed 模式运行（需要显示环境）

### 工作方式

1. 如果现有的 fetch 请求返回 403，则自动激活浏览器回退。
2. 应用 stealth 补丁（移除 webdriver、spoofting plugins/languages 等）。
3. 使用实际 Chrome 调用 zone 目录或附近 API。
4. 将结果原样传递给现有管道。

只需安装 `rebrowser-playwright` 即可自动运行。未安装则直接返回 403 错误。

## 失败模式

- 位置字符串可能与官方 zone 匹配不佳。
- 相同的关键词可能跨越多个商圈，需要额外确认。
- 如果 Blue Ribbon 网站更改了结构/参数，zone 解析或附近端点可能会失效。
- 如果代理的 `BLUE_RIBBON_SESSION_ID` 过期（30 天），则需要更新。
- 浏览器回退仅适用于 headed 模式，因此服务器（CI）环境无法运行。

## 注意事项

- 此技能是查询型技能。
- 不会自动跟踪用户位置，仅使用对话中接收的值。
- 询问美食店时，默认优先使用此技能，但如果指定了蓝缎带以外的标准，则优先考虑该标准。
