# uv (Python 包管理器)

`uv` 是一个快速 Python 包管理器，Science Skills 使用它来运行他们的 Python CLI 脚本。许多技能依赖于 `uv` 已安装并在 PATH 中。

在运行任何依赖它的技能之前，请确保 `uv` 可用。

## 安装

1.  检查 `uv` 是否已经可用：`uv --version`（或在 PowerShell 中输入 `& uv --version`）。如果成功，则 `uv` 已就绪——跳过其余步骤。
2.  检查 `uv` 是否已安装在默认位置但不在 PATH 中：

    -   **Unix/macOS**：`"$HOME/.local/bin/uv" --version`
    -   **Windows (PowerShell)**：`& "$HOME\.local\bin\uv.exe" --version`

    如果其中任何一个成功，则跳到步骤 4。

3.  如果 `uv` 未安装，请按顺序执行以下步骤：

    
    (a) 告知用户 `uv` 是一个用于创建一致且可靠的 Python 环境的工具，该环境用于运行 Science Skills，并且需要立即安装它。

    (b) 安装 `uv`：

        -   **Unix/macOS**：`curl -LsSf https://astral.sh/uv/install.sh | sh`
        -   **Windows (PowerShell)**：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

    

4.  将 `uv` 添加到 PATH 并验证（作为单个命令运行）：

    -   **Unix/macOS**：`export PATH="$HOME/.local/bin:$PATH" && uv --version`
    -   **Windows (PowerShell)**：`$env:PATH = "$HOME\.local\bin;" + $env:PATH; uv --version`

安装完成后，裸 `uv` 命令应能直接使用，无需重复导出。
