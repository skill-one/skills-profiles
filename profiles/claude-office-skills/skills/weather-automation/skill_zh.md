# 天气自动化

自动化基于天气的工作流程和通知。

## 核心功能

### 当前天气
```yaml
current_weather:
  location: "旧金山，CA"
  # 或者坐标
  lat: 37.7749
  lon: -122.4194
  
  response:
    temperature: 65°F
    feels_like: 63°F
    humidity: 72%
    wind_speed: 12 mph
    conditions: "局部多云"
    uv_index: 5
```

### 预报
```yaml
forecast:
  location: "纽约，NY"
  days: 7
  
  daily:
    - date: "2024-01-20"
      high: 45°F
      low: 32°F
      conditions: "雪"
      precipitation_chance: 80%
      
  hourly:
    interval: 3  # 小时
    periods: 24
```

### 天气警报
```yaml
alert_rules:
  - name: "降雨警报"
    condition:
      precipitation_chance: "> 70%"
      within_hours: 6
    action:
      notify: slack
      message: "☔ 未来6小时将有降雨"
      
  - name: "冰冻预警"
    condition:
      temperature: "< 32°F"
    action:
      - notify: sms
      - trigger: home_assistant
        action: protect_pipes
```

## 工作流程示例

### 早晨简报
```yaml
morning_weather:
  trigger: 每日 6:30 AM
  actions:
    - get_forecast:
        location: home
        days: 1
    - send_notification:
        channel: slack_dm
        message: |
          🌤️ 早上好！今天的天气：
          最高气温：{{high}}°F | 最低气温：{{low}}°F
          {{conditions}}
          {{#if rain}}☔ 带伞！{{/if}}
```

### 活动策划
```yaml
event_weather:
  trigger: 明日日历事件
  condition:
    event_type: outdoor
  actions:
    - get_forecast:
        location: "{{event.location}}"
        date: "{{event.date}}"
    - if:
        precipitation_chance: "> 50%"
      then:
        - notify: organizer
          message: "考虑备用场地 - 可能下雨"
```

## 最佳实践

1. **缓存**：缓存频繁请求
2. **单位**：支持公制/英制
3. **准确性**：使用可靠的数据源
4. **警报**：设置合理的阈值
5. **位置**：支持多种格式
