# eightctl

使用 `eightctl` 控制Eight Sleep pod。需要认证。

认证

- 配置文件：`~/.config/eightctl/config.yaml`
- 环境变量：`EIGHTCTL_EMAIL`, `EIGHTCTL_PASSWORD`

快速入门

- `eightctl status`
- `eightctl on|off`
- `eightctl temp 20`

常见任务

- 闹钟：`eightctl alarm list|create|dismiss`
- 计划：`eightctl schedule list|create|update`
- 音频：`eightctl audio state|play|pause`
- 底座：`eightctl base info|angle`

注意事项

- API非官方且有限速；避免重复登录。
- 修改温度或闹钟前请确认。
