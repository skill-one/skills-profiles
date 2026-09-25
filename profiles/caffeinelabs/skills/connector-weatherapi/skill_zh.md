# 使用 `weatherapi-client` 获取天气数据

这是 [WeatherAPI.com](https://www.weatherapi.com/) 的 Motoko 绑定，根据其 OpenAPI 规范生成。所有九个操作都位于一个模块中，**`Apis/APIsApi`**，并且所有九个操作都是只读的 `GET` 请求。

# 后端

一个可以读取当前温度和未来三天最高温度序列的 canister。默认情况下是非复制的，因此你只需要提供密钥：

```motoko filepath=src/backend/main.mo
import { realtimeWeather; forecastWeather } "mo:weatherapi-client/Apis/APIsApi";
import { type Config; defaultConfig } "mo:weatherapi-client/Config";
import Array "mo:core/Array"; // 在作用域内，以便 `days.map(…)` 点表示法解析

persistent actor {
  // 密钥是一个查询字符串凭证。通过管理员调用设置的稳定变量来持有它；切勿在源代码中硬编码它。
  func config(apiKey : Text) : Config = { defaultConfig with auth = ?#apiKey apiKey };

  // `q` 是任何 WeatherAPI 位置查询："Zurich"、"47.37,8.55"、邮政编码、IATA 代码或 "auto:ip"。
  public func currentTempC(apiKey : Text, q : Text) : async ?Float {
    let res = await* realtimeWeather(config apiKey, q, "");
    do ? { res.current!.temp_c! };
  };

  // 未来三天的每日最高温度。
  public func maxTempsC(apiKey : Text, q : Text) : async [?Float] {
    let res = await* forecastWeather(config apiKey, q, #_3_, "", 0, 0, "", "no", "no", 0);
    let ?forecast = res.forecast else return [];
    let ?days = forecast.forecastday else return [];
    days.map(func(d) = do ? { d.day!.maxtemp_c! });
  };
}
```

## 九个操作

| 函数 | 端点 | 返回值 |
|---|---|---|
| `realtimeWeather(cfg, q, lang)` | `/current.json` | `RealtimeWeather200Response` |
| `forecastWeather(cfg, q, days, dt, unixdt, hour, lang, alerts, aqi, tp)` | `/forecast.json` | `ForecastWeather200Response` |
| `historyWeather(cfg, q, dt, unixdt, endDt, unixendDt, hour, lang)` | `/history.json` | `FutureWeather200Response` |
| `futureWeather(cfg, q, dt, lang)` | `/future.json` | `FutureWeather200Response` |
| `marineWeather(cfg, q, days, dt, unixdt, hour, lang)` | `/marine.json` | `MarineWeather200Response` |
| `astronomy(cfg, q, dt)` | `/astronomy.json` | `Astronomy200Response` |
| `timeZone(cfg, q)` | `/timezone.json` | `Location` |
| `ipLookup(cfg, q)` | `/ip.json` | `Ip` |
| `searchAutocompleteWeather(cfg, q)` | `/search.json` | `[Search]` |

`days` 是一个枚举，而不是数字：`ForecastWeatherDaysParameter` 是 `#_1_` … `#_14_`，而 `MarineWeatherDaysParameter` 是 `#_1_` … `#_7_`（下划线是生成器如何转义数字枚举值的——`#_3_`，而不是 `#_3` 或 `3`）。

## API 密钥设置

1. 在 [weatherapi.com](https://www.weatherapi.com/signup.aspx) 注册——免费套餐涵盖当前天气、3 天预报、天文、时区、搜索和 IP 查找。历史记录、未来、海洋和 14 天预报需要付费计划，并且免费密钥会返回 **403**。
2. 从控制面板复制密钥，并将其作为 `auth = ?#apiKey key` 传递。
3. 客户端将其追加为 `?key=…`（WeatherAPI 不接受 `Authorization` 头），因此 **它出现在请求 URL 中**。将其保存在由管理员调用设置的稳定变量中，并且永远不要记录构建的 URL。

## 默认情况下调用是非复制的

该软件包在 `defaultConfig` 中提供 `is_replicated = ?false`，并且在这里这是一个 *正确性* 要求，而不仅仅是节省成本。每个响应都携带请求时钟——`Location.localtime` / `localtime_epoch`、`Current.last_updated` / `last_updated_epoch`——这些每秒都在变化。*复制的* 外调用会导致每个子网节点发出自己的请求并要求位相同的正文，因此这些字段会在大多数调用中破坏共识，同时消耗 ~13× 的周期。你不需要自己设置它；默认值是正确的。

仅在与 `transform` 一起使用 `is_replicated = ?true` 时覆盖，该 `transform` 会删除易变字段。

## 所有内容都是可选的

WeatherAPI 没有将任何响应字段标记为必需的，因此生成的模型都是可选的：`RealtimeWeather200Response.current : ?Current`、`Current.temp_c : ?Float`，等等。使用 `do ?` 块（`do ? { res.current!.temp_c! }`）而不是嵌套的 `switch`，并决定对于你的调用者缺失字段意味着什么——API 会省略你的计划不涵盖的字段（例如，没有 `aqi=yes` 参数的 `air_quality`）。

## 空字符串和零表示“省略”

可选的查询参数在为 `""` 或 `0` 时会被丢弃，因为 WeatherAPI 拒绝空的 `lang=` 和零值的数字。因此，传递 `""` 作为 `lang`、`dt`、`alerts`、`aqi` 和 `0` 作为 `unixdt`、`tp` 是如何表示“未提供”——没有 `?Text` 参数可以留空。

值得知道的一个后果：**`hour = 0` 不会选择午夜**，它会完全省略 `hour` 过滤器，并且你会得到整个小时的数组。如果你需要 00:00，请自己过滤返回的 `hour : ?[ForecastForecastdayInnerHourInner]`。

## 错误

非 2xx 响应和解码失败 `throw Error.reject(…)`。客户端使用 `diagnostics` 生成，因此消息是 `HTTP <status> body[<n>B]=<first 100 chars>: <reason>`——足够区分 401（坏密钥）、403（你的计划不包括此端点）和 400（`q` 无法解析）而无需额外日志记录。使用 `try`/`catch` 捕获并显示 `Error.message(err)`。
