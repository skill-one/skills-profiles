# 遗留电路模拟

一项用于创建面包板电路模拟和可视化图表的技能，适用于复古计算和电子项目。该技能利用HTML5 Canvas绘图机制来渲染具有复古元件（如6502微处理器、555定时器IC、EEPROM和7400系列逻辑门）的交互式电路布局。

## 使用此技能的场景

- 用户要求“创建面包板布局”或“模拟电路”
- 用户希望可视化元件在面包板上的位置
- 用户需要一个构建6502计算机的可视参考
- 用户要求“绘制电路”或“绘制电子元件”
- 用户希望创建教育电子可视化图表
- 用户提到Ben Eater教程或复古计算项目
- 用户要求模拟555定时器电路或LED项目
- 用户需要可视化元件之间的导线连接

## 前置条件

- 理解捆绑参考文件中的元件引脚配置
- 了解面包板布局规范（行、列、电源轨）

## 支持的元件

### 微处理器和存储器

| 元件 | 引脚数 | 描述 |
|-------|------|------|
| W65C02S | 40引脚DIP | 8位微处理器，16位地址总线 |
| 28C256 | 28引脚DIP | 32KB并行EEPROM |
| W65C22 | 40引脚DIP | 通用接口适配器（VIA） |
| 62256 | 28引脚DIP | 32KB静态RAM |

### 逻辑和定时器IC

| 元件 | 引脚数 | 描述 |
|-------|------|------|
| NE555 | 8引脚DIP | 用于定时和振荡的定时器IC |
| 7400 | 14引脚DIP | 四路2输入NAND门 |
| 7402 | 14引脚DIP | 四路2输入NOR门 |
| 7404 | 14引脚DIP | 六反相器（非门） |
| 7408 | 14引脚DIP | 四路2输入AND门 |
| 7432 | 14引脚DIP | 四路2输入OR门 |

### 无源和有源元件

| 元件 | 描述 |
|------|------|
| LED | 发光二极管（各种颜色） |
| 电阻器 | 限流（可配置值） |
| 电容器 | 滤波和定时（陶瓷/电解） |
| 晶体 | 时钟振荡器 |
| 开关 | 簧片开关（自锁） |
| 按钮开关 | 瞬时按压按钮 |
| 电位器 | 可变电阻 |
| 光敏电阻 | 光敏电阻 |

### 网格系统

```javascript
// 标准面包板网格：20px间距
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

### 创建基本LED电路模拟

1. 定义面包板尺寸和网格
2. 放置电源轨连接（+5V和GND）
3. 添加LED元件并确定阳极/阴极方向
4. 放置限流电阻器
5. 绘制元件之间的导线连接
6. 添加标签和注释

### 创建555定时器电路

1. 将NE555 IC放置在面包板上（引脚1-4在左侧，引脚5-8在右侧）
2. 将引脚1（GND）连接到接地轨
3. 将引脚8（Vcc）连接到电源轨
4. 添加定时电阻器和电容器
5. 连接触发和阈值连接
6. 将输出连接到LED或其他负载

### 创建6502微处理器布局

1. 将W65C02S居中放置在面包板上
2. 添加28C256 EEPROM用于程序存储
3. 放置W65C22 VIA用于I/O
4. 添加7400系列逻辑用于地址解码
5. 连接地址总线（A0-A15）
6. 连接数据总线（D0-D7）
7. 连接控制信号（R/W, PHI2, RESB）
8. 添加复位按钮和时钟晶体

## 元件引脚配置快速参考

### 555定时器（8引脚DIP）

| 引脚 | 名称 | 功能 |
|:----:|:-----|:-----|
| 1 | GND | 接地（0V） |
| 2 | TRIG | 触发（< 1/3 Vcc开始定时） |
| 3 | OUT | 输出（源/漏200mA） |
| 4 | RESET | 低电平有效复位 |
| 5 | CTRL | 控制电压（用10nF旁路） |
| 6 | THR | 阈值（> 2/3 Vcc复位） |
| 7 | DIS | 放电（开漏） |
| 8 | Vcc | 电源（+4.5V至+16V） |

### W65C02S（40引脚DIP）- 关键引脚

| 引脚 | 名称 | 功能 |
|:----:|:-----|:-----|
| 8 | VDD | 电源 |
| 21 | VSS | 接地 |
| 37 | PHI2 | 系统时钟输入 |
| 40 | RESB | 低电平有效复位 |
| 34 | RWB | 读/写信号 |
| 9-25 | A0-A15 | 地址总线 |
| 26-33 | D0-D7 | 数据总线 |

### 28C256 EEPROM（28引脚DIP）- 关键引脚

| 引脚 | 名称 | 功能 |
|:----:|:-----|:-----|
| 14 | GND | 接地 |
| 28 | VCC | 电源 |
| 20 | CE | 片选（低电平有效） |
| 22 | OE | 输出使能（低电平有效） |
| 27 | WE | 写使能（低电平有效） |
| 1-10, 21-26 | A0-A14 | 地址输入 |
| 11-19 | I/O0-I/O7 | 数据总线 |

## 公式参考

### 电阻器计算

- **欧姆定律**：V = I × R
- **LED电流**：R = (Vcc - Vled) / Iled
- **功率**：P = V × I = I² × R

### 555定时器公式

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

### LED颜色

| 颜色 | 正向电压 |
|------|----------|
| 红色 | 1.8V - 2.2V |
| 绿色 | 2.0V - 2.2V |
| 黄色 | 2.0V - 2.2V |
| 蓝色 | 3.0V - 3.5V |
| 白色 | 3.0V - 3.5V |

## 构建示例

### 构建示例1 — 单个LED

**元件**：红色LED、220Ω电阻器、跳线、电源

**步骤：**

1. 从电源GND到行A5插入黑色跳线
2. 从电源+5V到行J5插入红色跳线
3. 将LED的阴极（短腿）放置在与GND对齐的行中
4. 在电源和LED阳极之间放置220Ω电阻器

### 构建示例2 — 555非稳态振荡器

**元件**：NE555、LED、电阻器（10kΩ、100kΩ）、电容器（10µF）

**步骤：**

1. 将555 IC跨在中心通道上
2. 将引脚1连接到GND，引脚8连接到+5V
3. 将引脚4连接到引脚8（禁用复位）
4. 在引脚7和+5V之间连接10kΩ电阻器
5. 在引脚6和7之间连接100kΩ电阻器
6. 在引脚6和GND之间连接10µF电容器
7. 将引脚3（输出）连接到LED电路

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| LED不亮 | 检查极性（阳极接+，阴极接-） |
| 电路无法供电 | 验证电源轨连接 |
| IC不工作 | 检查VCC和GND引脚连接 |
| 555不振荡 | 验证阈值/触发电容器接线 |
| 微处理器卡住 | 检查复位脉冲后RESB是否为高电平 |

## 参考文献

详细的元件规格在捆绑的参考文件中提供：

- [555.md](references/555.md) - 完整的555定时器IC规格
- [6502.md](references/6502.md) - MOS 6502微处理器详情
- [6522.md](references/6522.md) - W65C22 VIA接口适配器
- [28256-eeprom.md](references/28256-eeprom.md) - AT28C256 EEPROM规格
- [6C62256.md](references/6C62256.md) - 62256 SRAM详情
- [7400-series.md](references/7400-series.md) - TTL逻辑门引脚配置
- [assembly-compiler.md](references/assembly-compiler.md) - 汇编编译器规格
- [assembly-language.md](references/assembly-language.md) - 汇编语言规格
- [basic-electronic-components.md](references/basic-electronic-components.md) - 电阻器、电容器、开关
- [breadboard.md](references/breadboard.md) - 面包板规格
- [common-breadboard-components.md](references/common-breadboard-components.md) - 综合元件参考
- [connecting-electronic-components.md](references/connecting-electronic-components.md) - 分步构建指南
- [emulator-28256-eeprom.md](references/emulator-28256-eeprom.md) - 模拟28256-eeprom规格
- [emulator-6502.md](references/emulator-6502.md) - 模拟6502规格
- [emulator-6522.md](references/emulator-6522.md) - 模拟6522规格
- [emulator-6C62256.md](references/emulator-6C62256.md) - 模拟6C62256规格
- [emulator-lcd.md](references/emulator-lcd.md) - 模拟LCD规格
- [lcd.md](references/lcd.md) - LCD显示接口
- [minipro.md](references/minipro.md) - EEPROM编程器使用
- [t48eeprom-programmer.md](references/t48eeprom-programmer.md) - T48编程器参考
