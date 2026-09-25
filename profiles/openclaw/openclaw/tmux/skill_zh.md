# tmux

用于现有交互式 tmux 会话。一次性命令请使用普通 shell。对于新的非交互式后台任务，请使用后台执行。

## 基础操作

```bash
tmux ls
tmux list-windows -t shared
tmux list-panes -t shared:0
tmux capture-pane -t shared:0.0 -p
tmux capture-pane -t shared:0.0 -p -S -
```

目标格式：`会话:窗口.窗格`，例如 `shared:0.0`。

## 发送输入

直接输入文本，然后按 Enter：

```bash
tmux send-keys -t shared:0.0 -l -- "请继续"
tmux send-keys -t shared:0.0 Enter
```

特殊按键：

```bash
tmux send-keys -t shared:0.0 C-c
tmux send-keys -t shared:0.0 C-d
tmux send-keys -t shared:0.0 Escape
```

使用 `-l --` 输入任意文本。分开发送文本和 Enter 以避免粘贴/换行意外。

## 会话管理

```bash
tmux new-session -d -s worker
tmux rename-session -t old new
tmux kill-session -t worker
```

## 提示检查

```bash
tmux capture-pane -t worker-3 -p | tail -20
tmux capture-pane -t worker-3 -p | rg "proceed|permission|Yes|No|❯"
```

仅当理解提示时才进行确认/选择：

```bash
tmux send-keys -t worker-3 -l -- "y"
tmux send-keys -t worker-3 Enter
```

## 辅助工具

- `scripts/find-sessions.sh`：发现会话。
- `scripts/wait-for-text.sh`：等待窗格输出包含文本。

## 注意事项

- `capture-pane -p` 将内容打印到标准输出以供脚本使用。
- `-S -` 捕获完整的滚动历史。
- tmux 会话在 SSH 断开连接时仍然保持。
