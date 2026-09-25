# Home Assistant 自动化

自动化智能家居设备并创建智能自动化工作流。

## 核心功能

### 设备控制
```yaml
device_commands:
  lights:
    - turn_on:
        entity_id: light.living_room
        brightness_pct: 80
        color_temp: 350
    - turn_off:
        entity_id: light.all_lights
        
  climate:
    - set_temperature:
        entity_id: climate.main_thermostat
        temperature: 72
        hvac_mode: heat
        
  media:
    - media_play_pause:
        entity_id: media_player.living_room_tv
    - volume_set:
        entity_id: media_player.sonos
        volume_level: 0.5
```

### 自动化模板
```yaml
automations:
  morning_routine:
    trigger:
      - platform: time
        at: "06:30:00"
      - platform: state
        entity_id: binary_sensor.alarm
        to: "off"
    condition:
      - condition: state
        entity_id: person.owner
        state: "home"
    action:
      - service: light.turn_on
        target:
          entity_id: light.bedroom
        data:
          brightness_pct: 30
          transition: 300
      - service: climate.set_temperature
        data:
          temperature: 72
      - delay: "00:05:00"
      - service: media_player.play_media
        data:
          media_content_type: music
          media_content_id: "news_briefing"

  away_mode:
    trigger:
      platform: state
      entity_id: group.family
      to: "not_home"
      for: "00:10:00"
    action:
      - service: climate.set_preset_mode
        data:
          preset_mode: away
      - service: light.turn_off
        target:
          entity_id: all
      - service: lock.lock
        target:
          entity_id: lock.front_door
```

### 场景
```yaml
scenes:
  movie_night:
    entities:
      light.living_room:
        state: on
        brightness: 20
        color_temp: 500
      light.tv_backlight:
        state: on
        rgb_color: [0, 0, 255]
      media_player.soundbar:
        state: on
        source: "TV"
      cover.blinds:
        state: closed
        
  good_night:
    entities:
      light.all_lights:
        state: off
      lock.all_locks:
        state: locked
      alarm_control_panel.home:
        state: armed_night
      climate.thermostat:
        temperature: 68
```

### 语音指令
```yaml
voice_intents:
  - intent: "打开灯光"
    action: light.turn_on
    entity: light.all_lights
    
  - intent: "设置温度为 {temp}"
    action: climate.set_temperature
    entity: climate.thermostat
    data:
      temperature: "{{ temp }}"
      
  - intent: "我出门了"
    action: script.away_mode
```

## 集成示例

### 能量监测
```yaml
energy_dashboard:
  sensors:
    - sensor.electricity_usage
    - sensor.solar_production
    - sensor.battery_level
  automations:
    - name: "低谷充电"
      trigger:
        platform: time
        at: "00:00:00"
      action:
        service: switch.turn_on
        entity_id: switch.ev_charger
```

### 安全系统
```yaml
security:
  motion_detection:
    trigger:
      platform: state
      entity_id: binary_sensor.motion_front
      to: "on"
    condition:
      - condition: state
        entity_id: alarm_control_panel.home
        state: armed_away
    action:
      - service: camera.snapshot
        entity_id: camera.front_door
      - service: notify.mobile_app
        data:
          message: "前门检测到移动"
          data:
            image: "/local/snapshots/front_door.jpg"
```

## 最佳实践

1. **实体命名**：使用一致的命名规范
2. **分组**：逻辑组织设备
3. **条件**：始终添加适当的条件
4. **通知**：不要过度通知
5. **测试**：彻底测试自动化
6. **备份**：定期备份配置
