---
name: openhue
description: 通过 OpenHue CLI 控制飞利浦 Hue 灯光和场景。
---

# OpenHue CLI

使用 `openhue` 通过 Hue Bridge 控制飞利浦 Hue 灯具和场景。

## 何时使用

在以下情况下使用：

- 打开/关闭灯具
- 调暗客厅灯光
- 设置场景或电影模式
- 控制特定的 Hue 房间或区域
- 调整亮度、颜色或色温

## 何时不应使用

在以下情况下不应使用：

- 非Hue智能设备（其他品牌）-> 不受支持
- HomeKit 场景或快捷指令 -> 使用苹果的生态系统
- 控制电视或娱乐系统
- 温控器或暖通空调
- 智能插座（除非是 Hue 智能插座）

## 常用命令

### 列出资源

```bash
openhue get light       # 列出所有灯具
openhue get room        # 列出所有房间
openhue get scene       # 列出所有场景
```

### 控制灯具

```bash
# 打开/关闭
openhue set light "Bedroom Lamp" --on
openhue set light "Bedroom Lamp" --off

# 亮度（0-100）
openhue set light "Bedroom Lamp" --on --brightness 50

# 色温（暖到冷：153-500 mirek）
openhue set light "Bedroom Lamp" --on --temperature 300

# 颜色（通过名称或十六进制）
openhue set light "Bedroom Lamp" --on --color red
openhue set light "Bedroom Lamp" --on --rgb "#FF5500"
```

### 控制房间

```bash
# 关闭整个房间
openhue set room "Bedroom" --off

# 设置房间亮度
openhue set room "Bedroom" --on --brightness 30
```

### 场景

```bash
# 激活场景
openhue set scene "Relax" --room "Bedroom"
openhue set scene "Concentrate" --room "Office"
```

## 快速预设

```bash
# 睡前（调暗暖色）
openhue set room "Bedroom" --on --brightness 20 --temperature 450

# 工作模式（明亮冷色）
openhue set room "Office" --on --brightness 100 --temperature 250

# 电影模式（调暗）
openhue set room "Living Room" --on --brightness 10
```

## 注意事项

- Bridge 必须在本地网络中
- 首次运行需要按下 Hue bridge 上的按钮进行配对
- 颜色仅在彩色灯泡上有效（不支持仅白光灯泡）
