---
name: legacy-circuit-mockups
description: 使用HTML5 Canvas绘图技术生成面包板电路示意图和视觉图表。当被要求创建电路布局、可视化电子元件位置、绘制面包板图、模拟6502构建、生成复古计算机原理图或设计复古电子项目时使用。支持555定时器、W65C02S微处理器、28C256 EEPROM、W65C22 VIA芯片、7400系列逻辑门、LED灯、电阻、电容、开关、按钮、晶振和导线。
---

# 遗留电路模拟

一项用于创建面包板电路模拟和可视化图表的技能，适用于复古计算和电子项目。该技能利用 HTML5 Canvas 绘图机制来渲染具有复古元件（如 6502 微处理器、555 定时器 IC、EEPROM 和 7400 系列逻辑门）的交互式电路布局。

## 使用此技能的场景

- 用户要求“创建面包板布局”或“模拟电路”
- 用户希望可视化元件在面包板上的位置
- 用户需要一个构建 6502 计算机的视觉参考
- 用户要求“绘制电路”或“绘制电子元件”
- 用户希望创建教育电子可视化图表
- 用户提到 Ben Eater 教程或复古计算项目
- 用户要求模拟 555 定时器电路或 LED 项目
- 用户需要可视化元件之间的导线连接

## 前置条件

- 理解捆绑参考文件中的元件引脚配置
- 了解面包板布局规范（行、列、电源轨）

## 支持的元件

### 微处理器和存储器

| 元件 | 引脚数 | 描述 |
|-------|------|------|
| W65C02S | 40 引脚 DIP | 8 位微处理器，16 位地址总线 |
| 28C256 | 28 引脚 DIP | 32KB 并行 EEPROM |
| W65C22 | 40 引脚 DIP | 通用接口适配器 (VIA) |
| 62256 | 28 引脚 DIP | 32KB 静态 RAM |

### 逻辑和定时器 IC

| 元件 | 引脚数 | 描述 |
|-------|------|------|
| NE555 | 8 引脚 DIP | 用于定时和振荡的定时器 IC |
| 7400 | 14 引脚 DIP | 四路 2 输入与非门 |
| 7402 | 14 引脚 DIP | 四路 2 输入或非门 |
| 7404 | 14 引脚 DIP | 六反相器（非门） |
| 7408 | 14 引脚 DIP | 四路 2 输入与门 |
| 7432 | 14 引脚 DIP | 四路 2 输入或门 |

### 无源和有源元件

| 元件 | 描述 |
|------|------|
| LED | 发光二极管（各种颜色） |
| 电阻器 | 限流（可配置值） |
| 电容器 | 滤波和定时（陶瓷/电解） |
| 晶体 | 时钟振荡器 |
| 开关 | 簧片开关（自锁） |
| 按钮 | 瞬时按钮 |
| 电位器 | 可变电阻 |
| 光敏电阻 | 光敏电阻 |

### 网格系统

```javascript
// 标准面包板网格：20px 间距
const gridSize = 20;
const cellX = Math.floor(x / gridSize) * gridSize;
const cellY = Math.floor(y / gridSize) * gridSize;
```

### 元件渲染模式

```javascript
// 所有元件遵循此结构：
{
  type: 'component-type',
  x: gridX,
  y: gridY,
  width: componentWidth,
  height: componentHeight,
  rotation: 0,  // 0, 90, 180, 270
  properties: { /* 元件特定数据 */ }
}
```

### 导线连接

```javascript
// 导线连接格式：
{
  start: { x: startX, y: startY },
  end: { x: endX, y: endY },
  color: '#ff0000'  // 导线颜色编码
}
```

## 分步工作流程

### 创建基本的 LED 电路模拟

1. 定义面包板尺寸和网格
2. 放置电源轨连接 (+5V 和 GND)
3. 添加 LED 元件并确定阳极/阴极方向
4. 放置限流电阻器
5. 绘制元件之间的导线连接
6. 添加标签和注释

### 创建 555 定时器电路

1. 将 NE555 IC 放置在面包板上（引脚 1-4 在左侧，引脚 5-8 在右侧）
2. 将引脚 1（GND）连接到接地轨
3. 将引脚 8（Vcc）连接到电源轨
4. 添加定时电阻器和电容器
5. 连接触发和阈值连接
6. 将输出连接到 LED 或其他负载

### 创建 6502 微处理器布局

1. 将 W65C02S 居中放置在面包板上
2. 添加 28C256 EEPROM 用于程序存储
3. 放置 W65C22 VIA 用于 I/O
4. 添加 7400 系列逻辑用于地址解码
5. 连接地址总线 (A0-A15)
6. 连接数据总线 (D0-D7)
7. 连接控制信号 (R/W, PHI2, RESB)
8. 添加复位按钮和时钟晶体

## 元件引脚配置快速参考

### 555 定时器 (8 引脚 DIP)

| 引脚 | 名称 | 功能 |
|:---:|:-----|:-----|
| 1 | GND | 接地 (0V) |
| 2 | TRIG | 触发 (< 1/3 Vcc 开始定时) |
| 3 | OUT | 输出 (源/漏 200mA) |
| 4 | RESET | 低电平有效复位 |
| 5 | CTRL | 控制电压 (用 10nF 旁路) |
| 6 | THR | 阈值 (> 2/3 Vcc 复位) |
| 7 | DIS | 放电 (开漏) |
| 8 | Vcc | 电源 (+4.5V 至 +16V) |

### W65C02S (40 引脚 DIP) - 关键引脚

| 引脚 | 名称 | 功能 |
|:---:|:-----|:-----|
| 8 | VDD | 电源 |
| 21 | VSS | 接地 |
| 37 | PHI2 | 系统时钟输入 |
| 40 | RESB | 低电平有效复位 |
| 34 | RWB | 读/写信号 |
| 9-25 | A0-A15 | 地址总线 |
| 26-33 | D0-D7 | 数据总线 |

### 28C256 EEPROM (28 引脚 DIP) - 关键引脚

| 引脚 | 名称 | 功能 |
|:---:|:-----|:-----|
| 14 | GND | 接地 |
| 28 | VCC | 电源 |
| 20 | CE | 片选 (低电平有效) |
| 22 | OE | 输出使能 (低电平有效) |
| 27 | WE | 写使能 (低电平有效) |
| 1-10, 21-26 | A0-A14 | 地址输入 |
| 11-19 | I/O0-I/O7 | 数据总线 |

## 公式参考

### 电阻器计算

- **欧姆定律**：V = I × R
- **LED 电流**：R = (Vcc - Vled) / Iled
- **功率**：P = V × I = I² × R

### 555 定时器公式

**非稳态模式：**

- 频率：f = 1.44 / ((R1 + 2×R2) × C)
- 高电平时间：t₁ = 0.693 × (R1 + R2) × C
- 低电平时间：t₂ = 0.693 × R2 × C
- 占空比：D = (R1 + R2) / (R1 + 2×R2) × 100%

**单稳态模式：**

- 脉冲宽度：T = 1.1 × R × C

### 电容器计算

- 容抗：Xc = 1 / (2πfC)
- 储能：E = ½ × C × V²

## 颜色编码规范

### 导线颜色

| 颜色 | 用途 |
|------|------|
| 红色 | +5V / 电源 |
| 黑色 | 接地 |
| 黄色 | 时钟 / 定时 |
| 蓝色 | 地址总线 |
| 绿色 | 数据总线 |
| 橙色 | 控制信号 |
| 白色 | 通用 |

### LED 颜色

| 颜色 | 正向电压 |
|------|----------|
| 红色 | 1.8V - 2.2V |
| 绿色 | 2.0V - 2.2V |
| 黄色 | 2.0V - 2.2V |
| 蓝色 | 3.0V - 3.5V |
| 白色 | 3.0V - 3.5V |

## 构建示例

### 构建 1 — 单个 LED

**元件**：红色 LED、220Ω 电阻器、跳线、电源

**步骤：**

1. 从电源 GND 到 A5 行插入黑色跳线
2. 从电源 +5V 到 J5 行插入红色跳线
3. 将 LED 的阴极（短腿）放置在与 GND 对齐的行
4. 在电源和 LED 阳极之间放置 220Ω 电阻器

### 构建 2 — 555 非稳态闪烁器

**元件**：NE555、LED、电阻器 (10kΩ, 100kΩ)、电容器 (10µF)

**步骤：**

1. 将 555 IC 横跨中心通道放置
2. 将引脚 1 连接到 GND，引脚 8 连接到 +5V
3. 将引脚 4 连接到引脚 8（禁用复位）
4. 在引脚 7 和 +5V 之间连接 10kΩ 电阻器
5. 在引脚 6 和 7 之间连接 100kΩ 电阻器
6. 在引脚 6 和 GND 之间连接 10µF 电容器
7. 将引脚 3（输出）连接到 LED 电路

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| LED 不亮 | 检查极性（阳极到 +，阴极到 -） |
| 电路无法供电 | 验证电源轨连接 |
| IC 无法工作 | 检查 VCC 和 GND 引脚连接 |
| 555 不振荡 | 验证阈值/触发电容器连接 |
| 微处理器卡住 | 检查 RESB 在复位脉冲后是否为高电平 |

## 参考文献

详细的元件规格在捆绑的参考文件中提供：

- [555.md](references/555.md) - 完整的 555 定时器 IC 规格
- [6502.md](references/6502.md) - MOS 6502 微处理器详细信息
- [6522.md](references/6522.md) - W65C22 VIA 接口适配器
- [28256-eeprom.md](references/28256-eeprom.md) - AT28C256 EEPROM 规格
- [6C62256.md](references/6C62256.md) - 62256 SRAM 详细信息
- [7400-series.md](references/7400-series.md) - TTL 逻辑门引脚配置
- [assembly-compiler.md](references/assembly-compiler.md) - 汇编编译器规格
- [assembly-language.md](references/assembly-language.md) - 汇编语言规格
- [basic-electronic-components.md](references/basic-electronic-components.md) - 电阻器、电容器、开关
- [breadboard.md](references/breadboard.md) - 面包板规格
- [common-breadboard-components.md](references/common-breadboard-components.md) - 综合元件参考
- [connecting-electronic-components.md](references/connecting-electronic-components.md) - 分步构建指南
- [emulator-28256-eeprom.md](references/emulator-28256-eeprom.md) - 模拟 28256-eeprom 规格
- [emulator-6502.md](references/emulator-6502.md) - 模拟 6502 规格
- [emulator-6522.md](references/emulator-6522.md) - 模拟 6522 规格
- [emulator-6C62256.md](references/emulator-6C62256.md) - 模拟 6C62256 规格
- [emulator-lcd.md](references/emulator-lcd.md) - 模拟 LCD 规格
- [lcd.md](references/lcd.md) - LCD 显示接口
- [minipro.md](references/minipro.md) - EEPROM 编程器使用
- [t48eeprom-programmer.md](references/t48eeprom-programmer.md) - T48 编程器参考
