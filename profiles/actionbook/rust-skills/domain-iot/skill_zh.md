# 物联网领域

> **第 3 层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 不可靠网络 | 离线优先 | 本地缓存 |
| 功耗约束 | 高效代码 | 睡眠模式、最小化分配 |
| 资源限制 | 小型占用 | 在需要的地方使用 no_std |
| 安全性 | 加密通信 | TLS、签名固件 |
| 可靠性 | 自我恢复 | 看门狗、错误处理 |
| OTA 更新 | 安全升级 | 撤销能力 |

---

## 关键约束

### 网络不可靠

```
规则：网络随时可能失效
原因：无线、偏远地区
Rust：本地队列、带退避的重试
```

### 功耗管理

```
规则：最小化功耗
原因：电池寿命、能源成本
Rust：睡眠模式、高效算法
```

### 设备安全

```
规则：所有通信加密
原因：可能存在物理访问
Rust：TLS、签名消息
```

---

## 向下追踪 ↓

从约束到设计（第 2 层）：

```
"需要离线优先设计"
    ↓ m12-lifecycle：带持久化的本地缓存
    ↓ m13-domain-error：带退避的重试

"需要功耗效率"
    ↓ domain-embedded：no_std 模式
    ↓ m10-performance：最小化分配

"需要可靠消息传递"
    ↓ m07-concurrency：带超时的异步
    ↓ MQTT：QoS 级别
```

---

## 环境比较

| 环境 | 堆栈 | Crate |
|-------------|-------|--------|
| Linux 网关 | tokio + std | rumqttc, reqwest |
| MCU 设备 | embassy + no_std | embedded-hal |
| 混合 | 分离工作负载 | 两者 |

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| MQTT (std) | rumqttc, paho-mqtt |
| 嵌入式 | embedded-hal, embassy |
| 异步 (std) | tokio |
| 异步 (no_std) | embassy |
| 日志 (no_std) | defmt |
| 日志 (std) | tracing |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| 发布/订阅 | 设备通信 | MQTT 主题 |
| 边缘计算 | 本地处理 | 上传前过滤 |
| OTA 更新 | 固件升级 | 签名 + 撤销 |
| 功耗管理 | 电池寿命 | 睡眠 + 唤醒事件 |
| 存储 & 转发 | 网络可靠性 | 本地队列 |

## 代码模式：MQTT 客户端

```rust
use rumqttc::{AsyncClient, MqttOptions, QoS};

async fn run_mqtt() -> anyhow::Result<()> {
    let mut options = MqttOptions::new("device-1", "broker.example.com", 1883);
    options.set_keep_alive(Duration::from_secs(30));

    let (client, mut eventloop) = AsyncClient::new(options, 10);

    // 订阅命令
    client.subscribe("devices/device-1/commands", QoS::AtLeastOnce).await?;

    // 发布遥测数据
    tokio::spawn(async move {
        loop {
            let data = read_sensor().await;
            client.publish("devices/device-1/telemetry", QoS::AtLeastOnce, false, data).await.ok();
            tokio::time::sleep(Duration::from_secs(60)).await;
        }
    });

    // 处理事件
    loop {
        match eventloop.poll().await {
            Ok(event) => handle_event(event).await,
            Err(e) => {
                tracing::error!("MQTT 错误: {}", e);
                tokio::time::sleep(Duration::from_secs(5)).await;
            }
        }
    }
}
```

---

## 常见错误

| 错误 | 领域违规 | 修复 |
|---------|-----------------|-----|
| 无重试逻辑 | 丢失数据 | 指数退避 |
| 始终开启无线电 | 电池耗尽 | 发送间隔睡眠 |
| 未加密 MQTT | 安全风险 | TLS |
| 无本地缓存 | 网络中断 = 数据丢失 | 本地持久化 |

---

## 向第 1 层追踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 离线优先 | 存储 & 转发 | 本地队列 + 冲刷 |
| 功耗效率 | 睡眠模式 | 定时唤醒 |
| 网络可靠性 | 重试 | tokio-retry, 退避 |
| 安全性 | TLS | rustls, native-tls |

---

## 相关技能

| 当... | 查看 |
|------|-----|
| 嵌入式模式 | domain-embedded |
| 异步模式 | m07-concurrency |
| 错误恢复 | m13-domain-error |
| 性能 | m10-performance |
