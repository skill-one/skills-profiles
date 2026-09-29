---
name: mcp-hass
description: 用于通过MCP协议控制Home Assistant智能家居设备并查询状态的技能。
---

# Home Assistant
使用MCP协议控制Home Assistant智能家居并查询状态。

## 前置条件
在Home Assistant中启用MCP服务器：
- 访问您的Home Assistant实例。
- 转到设置 > 设备与服务。
- 在右下角，选择[+ 添加集成](https://my.home-assistant.io/redirect/config_flow_start?domain=mcp)按钮。
- 从列表中选择模型上下文协议。
- 按照屏幕上的说明完成设置。

## 配置
当提示MCP服务器不存在时，提醒用户通过执行以下命令来配置`HASS_BASE_URL`和`HASS_ACCESS_TOKEN`环境变量以添加配置：
```shell
npx -y mcporter config add home-assistant \
  --transport http \
  --url "${HASS_BASE_URL:-http://homeassistant.local:8123}/api/mcp" \
  --header "Authorization=Bearer \${HASS_ACCESS_TOKEN}"
```

## 使用
```shell
# 获取状态
npx -y mcporter call home-assistant.GetLiveContext

# 打开设备
npx -y mcporter call home-assistant.HassTurnOn(name: "Bedroom Light")
npx -y mcporter call home-assistant.HassTurnOn(name: "Light", area: "Bedroom")

# 关闭设备
npx -y mcporter call home-assistant.HassTurnOff(name: "Bedroom Light")
npx -y mcporter call home-assistant.HassTurnOff(area: "Bedroom", domain: ["light"])

# 控制灯光
# brightness: 灯光百分比，0表示关闭，100表示全亮。
# color: 颜色名称
npx -y mcporter call home-assistant.HassLightSet(name: "Bedroom Light", brightness: 50)

# 控制风扇
# percentage: 风扇百分比，0表示关闭，100表示全速。
npx -y mcporter call home-assistant.HassFanSetSpeed(name: "Fan", area: "Bedroom", percentage: 80)
```

执行以下命令以了解具体的使用方法：
- `npx -y mcporter list home-assistant --schema --all-parameters`

## 关于`mcporter`
- 为提高兼容性，执行命令时使用`npx -y mcporter`而不是`mcporter`。
- https://github.com/steipete/mcporter/raw/refs/heads/main/docs/call-syntax.md
- https://github.com/steipete/mcporter/raw/refs/heads/main/docs/cli-reference.md
