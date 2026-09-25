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
- 电视或娱乐系统控制
- 温控器或暖通空调
- 智能插座（除非是Hue智能插座）

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
openhue set light "卧室灯" --on
openhue set light "卧室灯" --off

# 亮度（0-100）
openhue set light "卧室灯" --on --brightness 50

# 色温（暖到冷：153-500 mirek）
openhue set light "卧室灯" --on --temperature 300

# 颜色（通过名称或十六进制）
openhue set light "卧室灯" --on --color red
openhue set light "卧室灯" --on --rgb "#FF5500"
```

### 控制房间

```bash
# 关闭整个房间
openhue set room "卧室" --off

# 设置房间亮度
openhue set room "卧室" --on --brightness 30
```

### 场景

```bash
# 激活场景
openhue set scene "放松" --room "卧室"
openhue set scene "集中" --room "办公室"
```

## 快速预设

```bash
# 睡前（调暗暖色）
openhue set room "卧室" --on --brightness 20 --temperature 450

# 工作模式（明亮冷色）
openhue set room "办公室" --on --brightness 100 --temperature 250

# 电影模式（调暗）
openhue set room "客厅" --on --brightness 10
```

## 注意事项

- Bridge 必须在本地网络中
- 首次运行需要按下 Hue Bridge 上的按钮进行配对
- 颜色仅在彩色灯泡上有效（白光灯泡无效）
