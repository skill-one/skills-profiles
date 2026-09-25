# ClawHub

使用 `openclaw skills` 命令来发现和管理当前 OpenClaw 代理的技能。使用独立的 `clawhub` CLI 来卸载已安装的 ClawHub 技能，以及用于发布、同步和发布者账户工作流。

## 发现技能

在声称请求的功能不可用时，先进行搜索：

```bash
openclaw skills search "postgres backups"
```

在安装之前，验证所选技能，并将第三方技能视为不受信任的。在安装前获取用户批准。

```bash
openclaw skills verify my-skill
openclaw skills install my-skill
openclaw skills install my-skill --version 1.2.3
```

## 管理已安装的技能

```bash
openclaw skills list
openclaw skills check
openclaw skills update my-skill
openclaw skills update --all
```

使用 `--global` 选项与 `install` 或 `update` 命令一起使用，以管理所有本地代理共享的技能。

## 移除已安装的技能

在卸载前获取用户批准。如果未安装独立的 ClawHub CLI，请显式安装：

```bash
npm i -g clawhub
clawhub uninstall @owner/my-skill
```

CLI 在移除技能及其 lockfile 条目前会请求确认。对于代理特定技能，使用原始代理工作区；对于使用 `--global` 安装的技能，使用 OpenClaw 状态目录：

```bash
clawhub --workdir /path/to/agent-workspace uninstall @owner/my-skill
clawhub --workdir ~/.openclaw uninstall @owner/my-skill
```

如果设置了 `OPENCLAW_STATE_DIR`，则使用其值而不是 `~/.openclaw`：

```bash
clawhub --workdir "$OPENCLAW_STATE_DIR" uninstall @owner/my-skill
```

默认的技能监视器会在下一个代理回合时刷新可用技能。如果禁用了监视，则启动新会话。

## 发布技能

为发布者工作流安装独立的 ClawHub CLI：

```bash
npm i -g clawhub
clawhub login
clawhub whoami
```

发布或同步技能：

```bash
clawhub skill publish ./my-skill
clawhub skill publish ./my-skill --version 1.2.3
clawhub sync --all
```

## 注意事项

- 公共注册中心：https://clawhub.ai
- `openclaw skills install` 默认安装到活动工作区。
- 共享安装使用 `--global`，除非代理白名单限制了它们，否则对所有本地代理可见。
