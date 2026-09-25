# 控制CLI

使用可重复的本地测试框架来操作交互式CLI，而不是手动操作。首先，如果仓库中存在自己的测试/演示框架，请重用它；否则，使用标准本地工具临时构建一个框架。

## 用途

- 使用确定性输入重现CLI/TUI错误。
- 验证键盘流程、提示、中断、调整大小行为和终端布局。
- 捕获错误修复前后的会话记录。
- 分析启动时间、慢速操作、挂起或内存增长。
- 当输出比解释更容易展示时，录制简短的终端演示。

## 框架循环

1. 确定要测试的命令以及最小的可重复工作区。
2. 查找现有的本地框架：包脚本、端到端测试、演示录制器、expect脚本或PTY辅助工具。
3. 如果不存在框架，请在隔离的终端会话中启动CLI，并设置确定性环境变量。
4. 在交互之前捕获当前屏幕。
5. 逐个发送操作：文本、回车、箭头、Esc、Ctrl-C、调整大小。
6. 在执行下一个操作之前，等待具体的屏幕模式或提示。
7. 保存会话记录和任何分析工件。
8. 清理地终止会话。

## 框架选项

- 仓库原生框架：优先使用已提交的脚本，因为它们了解应用的启动、环境和提示。
- `tmux`：管理会话、`capture-pane`、`send-keys`、附加/分离。
- PTY探测：当`tmux`不可用时，使用简短的Python、Node或Expect脚本。
- 运行时分析器：使用Node或Bun分析器进行CPU分析、堆快照和实时评估。
- 终端录制器：当用户要求演示时，使用仓库本地演示工具或asciinema兼容工具。

## 最小tmux框架

```bash
SESSION="cli-harness-$(date +%s)"
tmux new-session -d -s "$SESSION" -- <command-under-test>
tmux capture-pane -pt "$SESSION"
tmux send-keys -t "$SESSION" "help" Enter
tmux capture-pane -pt "$SESSION"
tmux kill-session -t "$SESSION"
```

对于Node CLI：

```bash
NODE_OPTIONS="--inspect=127.0.0.1:0" tmux new-session -d -s "$SESSION" -- <node-cli-command>
```

查看终端输出以找到分析器URL，如果需要分析，则使用Chrome DevTools兼容的工具。

## 最小PTY框架

当您需要在没有`tmux`或演示框架的仓库中实现确定性等待时，使用PTY脚本。除非用户要求添加可重用的测试，否则将其保留为临时状态。

```python
import os
import pty
import select
import subprocess
import time

master_fd, slave_fd = pty.openpty()
proc = subprocess.Popen(
    ["<command>", "<arg>"],
    stdin=slave_fd,
    stdout=slave_fd,
    stderr=slave_fd,
    close_fds=True,
)
os.close(slave_fd)

deadline = time.time() + 30
buffer = b""
while time.time() < deadline:
    ready, _, _ = select.select([master_fd], [], [], 0.25)
    if not ready:
        continue
    chunk = os.read(master_fd, 4096)
    buffer += chunk
    if b"<ready text>" in buffer:
        os.write(master_fd, b"help\n")
        break

print(buffer.decode(errors="replace"))
proc.terminate()
os.close(master_fd)
```

如果CLI需要更丰富的终端控制，请使用`pty.fork()`或现有的PTY库。

## 分析配方

- 启动回归：在相同的机器、环境和命令下捕获基线和处理启动时间。
- 慢速操作：启动CPU分析，执行操作，停止分析，并比较顶级自时间函数。
- 内存泄漏：如果可用，强制执行GC，拍摄堆快照，重复执行操作，再次强制GC，并拍摄另一个快照。
- 挂起：在中断之前捕获屏幕、活动句柄/资源以及堆栈/CPU样本。

## 安全措施

- 优先使用确定性等待而不是睡眠。如果您必须睡眠，请解释原因。
- 不要将凭证或破坏性命令发送到受控会话。
- 除非仓库已经具有测试/演示框架，否则将框架保留在`/tmp`中。
- 不要硬编码来自另一个仓库的路径。调整命令以适应当前仓库的脚本和运行时。
- 除非用户要求保留，否则清理`tmux`会话、临时目录、分析器进程和演示工件。
