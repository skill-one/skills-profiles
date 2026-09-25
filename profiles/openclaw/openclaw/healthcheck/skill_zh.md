# OpenClaw 主机健康检查

目标：评估主机风险，运行只读检查，然后提出分阶段的加固方案，同时不破坏访问权限。

## 规则

- 执行状态改变操作前需询问。
- 在确认访问路径之前，不要更改 SSH/防火墙/远程访问。
- 优先选择可逆步骤和回滚说明。
- 永远不要声称 OpenClaw 管理 OS 防火墙、SSH 或更新。
- 如果身份/角色未知，仅建议。
- 用户选择：编号列表。
- 永远不要打印秘密信息。

## 需要推断的上下文

- 操作系统/版本，容器与主机。
- 权限级别。
- 访问路径：本地、SSH、RDP、尾网。
- 网络暴露：公网 IP、反向代理、隧道、仅局域网。
- OpenClaw 网关状态，绑定、认证。
- 备份状态。
- 磁盘加密。
- 自动安全更新。
- 使用模式：个人工作站、本地助手盒、远程服务器、其他。

仅询问缺失的事实。偏好简洁的表述。

## 只读检查

询问一次运行只读检查的权限。然后运行相关命令。

常见：

```bash
openclaw security audit --deep
openclaw gateway status --deep
openclaw doctor --lint
```

`doctor --lint` 可能因发现问题而退出 `1`：阅读报告并继续剩余检查。普通的 `doctor` 和 `doctor --non-interactive` 可以复制遗留配置并迁移状态，无需 `--fix`；将修复工作保留为明确批准。只读检查排除配置/服务修复和状态迁移，但可能产生附带日志或缓存账本。

macOS:

```bash
sw_vers
lsof -nP -iTCP -sTCP:LISTEN
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
pfctl -s info
tmutil status
fdesetup status
softwareupdate --schedule
```

Linux:

```bash
cat /etc/os-release
ss -ltnup || ss -ltnp
ufw status || firewall-cmd --state || nft list ruleset
systemctl status ssh sshd
lsblk -f
```

Windows:

```powershell
systeminfo
Get-NetFirewallProfile
Get-BitLockerVolume
```

## 风险配置

在了解上下文后，询问期望的配置：

1. 便利性：本地/私有，最小提示。
2. 平衡性：安全默认值，低摩擦。
3. 严格性：远程/公网/敏感数据，更多锁定。

## 报告格式

- 当前配置：一段话。
- 发现问题：严重性 + 证据 + 为什么重要。
- 建议计划：分阶段、可逆。
- 命令：先执行只读操作；批准后才执行写操作。
- 缺失项：无法检查的内容。

## 加固菜单

仅提供相关项：

- 故意将网关绑定到回环/LAN/尾网。
- 对远程访问要求认证。
- 关闭公网端口或通过防火墙限制。
- 启用 OS 安全更新。
- 启用磁盘加密。
- 验证备份和恢复路径。
- 在适当位置禁用密码 SSH 或要求密钥/MFA。
- 添加定期 `openclaw security audit --deep`。

应用前确认确切操作。
