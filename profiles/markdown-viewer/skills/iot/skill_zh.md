# 物联网架构图生成器

**快速入门：** 选择设备/传感器图标 → 放置边缘网关 → 连接到云服务 → 分组到区域 → 用 ` ```plantuml ` 分隔符包裹。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码分隔符。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `left to right direction` 用于典型的物联网数据流（设备 → 边缘 → 云）
- 使用 `mxgraph.aws4.*` 样式板语法用于物联网服务和设备图标
- 默认颜色会自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "区域"  { ... }` 或 `package "站点" { ... }` 进行分组
- 有向流使用 `-->`，异步/事件驱动流使用 `..>`（虚线）

**完整样式板参考：** 参考 [stencils/README.md](../uml/stencils/README.md) 获取 9500+ 可用图标。

## Mxgraph 样式板语法

```
mxgraph.aws4.<icon> "标签" as <别名>
```

### 核心物联网样式板

| 类别 | 样式板 | 用途 |
|------|--------|------|
| 物联网平台 | `iot_core`, `internet_of_things`, `iot_1click` | 中央物联网中心/消息代理 |
| 边缘/网关 | `greengrass`, `iot_device_gateway`, `freertos`, `iot_expresslink` | 边缘计算 & 设备网关 |
| Greengrass | `iot_greengrass_component`, `iot_greengrass_nucleus`, `iot_greengrass_stream_manager` | 边缘运行时组件 |
| 设备管理 | `iot_device_management`, `iot_device_defender`, `iot_device_tester`, `iot_over_the_air_update` | 队列配置、安全、OTA |
| 分析 | `iot_analytics`, `iot_analytics_channel`, `iot_analytics_pipeline`, `iot_analytics_dataset`, `iot_analytics_data_store` | 物联网数据处理管道 |
| 事件/规则 | `iot_events`, `iot_device_defender_iot_device_jobs` | 事件检测 & 任务执行 |
| 数字孪生 | `iot_twinmaker`, `iot_sitewise`, `iot_sitewise_asset`, `iot_sitewise_asset_model` | 资产建模 & 可视化 |
| 队列 | `iot_fleetwise`, `iot_device_management_fleet` | 车辆 & 设备队列遥测 |

### 设备 & 传感器样式板

| 类别 | 样式板 |
|------|--------|
| 传感器 | `sensor`, `iot_thing_temperature_sensor`, `iot_thing_humidity_sensor`, `iot_thing_vibration_sensor`, `iot_thing_temperature_humidity_sensor`, `iot_thing_temperature_vibration_sensor` |
| 执行器 | `actuator`, `iot_thing_relay`, `iot_thing_stacklight` |
| 工业 | `factory`, `iot_thing_industrial_pc`, `iot_thing_plc` |
| 智能家居 | `thermostat`, `alexa_enabled_device`, `alexa_smart_home_skill`, `camera`, `camera2` |
| 协议 | `mqtt_protocol`, `iot_lorawan_protocol`, `iot_greengrass_protocol` |
| 船舶/车辆 | `iot_sailboat`, `iot_fleetwise` |
| 机器人 | `robomaker`, `iot_roborunner` |

### 连接类型

| 语法 | 含义 | 用例 |
|------|------|------|
| `A --> B` | 实线箭头 | 同步API / 数据流 |
| `A ..> B` | 虚线箭头 | 异步遥测 / MQTT发布 |
| `A -- B` | 实线 | 物理双向连接 |
| `A --> B : "标签"` | 带标签的连接 | 描述协议或数据 |

### 快速示例

```plantuml
@startuml
left to right direction
rectangle "工厂车间" {
  mxgraph.aws4.sensor "温度\n传感器" as s1
  mxgraph.aws4.iot_thing_plc "PLC" as plc
}
mxgraph.aws4.greengrass "Greengrass\n边缘" as gg
mxgraph.aws4.iot_core "物联网核心" as core
mxgraph.aws4.iot_analytics "物联网\n分析" as analytics

s1 --> gg : MQTT
plc --> gg
gg --> core
core --> analytics
@enduml
```

## 物联网架构类型

| 类型 | 用途 | 关键样式板 | 示例 |
|------|------|------------|------|
| 智能工厂 | 工业物联网监控 | `sensor`, `iot_thing_plc`, `greengrass`, `iot_sitewise` | [smart-factory.md](examples/smart-factory.md) |
| 智能家居 | 家庭自动化 | `thermostat`, `alexa_enabled_device`, `camera`, `iot_core` | [smart-home.md](examples/smart-home.md) |
| 队列遥测 | 车辆队列跟踪 | `iot_fleetwise`, `iot_core`, `iot_analytics` | [fleet-telemetry.md](examples/fleet-telemetry.md) |
| 边缘计算 | 边缘本地处理 | `greengrass`, `freertos`, `iot_greengrass_component` | [edge-computing.md](examples/edge-computing.md) |
| 数字孪生 | 资产建模 & 模拟 | `iot_twinmaker`, `iot_sitewise_asset_model`, `iot_sitewise` | [digital-twin.md](examples/digital-twin.md) |
| 传感器网络 | 分布式传感器网格 | `sensor`, `iot_lorawan_protocol`, `iot_device_gateway` | [sensor-network.md](examples/sensor-network.md) |
| 设备管理 | 队列配置 & OTA | `iot_device_management`, `iot_device_defender`, `iot_over_the_air_update` | [device-management.md](examples/device-management.md) |
| 机器人 | 机器人队列编排 | `robomaker`, `iot_roborunner`, `greengrass` | [robotics.md](examples/robotics.md) |
