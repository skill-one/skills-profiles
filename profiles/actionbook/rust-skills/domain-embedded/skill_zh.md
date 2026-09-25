## 项目背景（自动注入）

**目标配置：**
!`cat .cargo/config.toml 2>/dev/null || echo "未找到 .cargo/config.toml"`

---

# 嵌入式域

> **第 3 层：域约束**

## 域约束 → 设计影响

| 域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 无堆 | 栈分配 | heapless, 无 Box/Vec |
| 无 std | 核心仅用 | #![no_std] |
| 实时性 | 可预测时序 | 无动态分配 |
| 资源受限 | 最小内存 | 静态缓冲区 |
| 硬件安全 | 安全外设访问 | HAL + 所有权 |
| 中断安全 | ISR 中无阻塞 | 原子操作, 临界区 |

---

## 关键约束

### 无动态分配

```
规则: 不能使用堆（无分配器）
原因: 确定性内存, 无 OOM
Rust: heapless::Vec<T, N>, 数组
```

### 中断安全

```
规则: 共享状态必须中断安全
原因: ISR 可随时抢占
Rust: Mutex<RefCell<T>> + 临界区
```

### 硬件所有权

```
规则: 外设必须有明确所有权
原因: 防止冲突访问
Rust: HAL 获取所有权, 单例
```

---

## 向下追踪 ↓

从约束到设计（第 2 层）:

```
"需要 no_std 兼容的数据结构"
    ↓ m02-resource: heapless 集合
    ↓ 静态尺寸: heapless::Vec<T, N>

"需要中断安全状态"
    ↓ m03-mutability: Mutex<RefCell<Option<T>>>
    ↓ m07-并发: 临界区

"需要外设所有权"
    ↓ m01-所有权: 单例模式
    ↓ m12-生命周期: RAII 用于硬件
```

---

## 层级栈

| 层级 | 示例 | 目的 |
|-------|----------|---------|
| PAC | stm32f4, esp32c3 | 寄存器访问 |
| HAL | stm32f4xx-hal | 硬件抽象 |
| 框架 | RTIC, Embassy | 并发 |
| 特性 | embedded-hal | 可移植驱动 |

## 框架对比

| 框架 | 风格 | 适合 |
|-----------|-------|----------|
| RTIC | 优先级驱动 | 中断驱动应用 |
| Embassy | 异步 | 复杂状态机 |
| 硬件裸机 | 手动 | 简单应用 |

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| 运行时 (ARM) | cortex-m-rt |
| 恐慌处理 | panic-halt, panic-probe |
| 集合 | heapless |
| HAL 特性 | embedded-hal |
| 日志 | defmt |
| Flash/调试 | probe-run |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| no_std 设置 | 硬件裸机 | `#![no_std]` + `#![no_main]` |
| 入口点 | 启动 | `#[entry]` 或 embassy |
| 静态状态 | ISR 访问 | `Mutex<RefCell<Option<T>>>` |
| 固定缓冲区 | 无堆 | `heapless::Vec<T, N>` |

## 代码模式：静态外设

```rust
#![no_std]
#![no_main]

use cortex_m::interrupt::{self, Mutex};
use core::cell::RefCell;

static LED: Mutex<RefCell<Option<Led>>> = Mutex::new(RefCell::new(None));

#[entry]
fn main() -> ! {
    let dp = pac::Peripherals::take().unwrap();
    let led = Led::new(dp.GPIOA);

    interrupt::free(|cs| {
        LED.borrow(cs).replace(Some(led));
    });

    loop {
        interrupt::free(|cs| {
            if let Some(led) = LED.borrow(cs).borrow_mut().as_mut() {
                led.toggle();
            }
        });
    }
}
```

---

## 常见错误

| 错误 | 域违规 | 修复 |
|---------|-----------------|-----|
| 使用 Vec | 堆分配 | heapless::Vec |
| 无临界区 | 与 ISR 竞态 | Mutex + interrupt::free |
| ISR 中阻塞 | 丢失中断 | 延迟至主循环 |
| 不安全外设 | 硬件冲突 | HAL 所有权 |

---

## 向第 1 层追踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 无堆 | 静态集合 | heapless::Vec<T, N> |
| ISR 安全 | 临界区 | Mutex<RefCell<T>> |
| 硬件所有权 | 单例 | take().unwrap() |
| no_std | 核心仅用 | #![no_std], #![no_main] |

---

## 相关技能

| 当... | 看到... |
|------|-----|
| 静态内存 | m02-resource |
| 内部可变性 | m03-mutability |
| 中断模式 | m07-concurrency |
| 硬件用 unsafe | unsafe-checker |
