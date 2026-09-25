# Holoscan SDK — 从源代码构建

## 目的

使用 `nvidia-holoscan/holoscan-sdk` 源代码树中的 `./run` 脚本（该脚本在 Docker 容器内构建）从源代码构建 Holoscan SDK，生成一个本地安装树，可作为 CMake 依赖项使用。

## 前置条件

- Linux 主机带有 NVIDIA GPU 及驱动程序 (`nvidia-smi`)。
- `git`、带有 NVIDIA 容器工具包的 Docker (`docker run --gpus all` 可用)，以及 `docker-buildx-plugin`。
- 构建容器 + 构建安装树需要约 20 GB 的可用磁盘空间。
- 第一次干净构建需要 10–30 分钟。

## 限制

- 仅在已发布的软件包（Conda / 容器 / apt / wheel）不符合要求时推荐使用——调试符号、自定义 CMake 选项或不受支持的配置。
- 仍然需要 Docker——`./run` 脚本在容器内构建；这不是一个真正的无头构建。
- 向 aarch64 跨编译需要在主机上安装 `qemu-user-static`。

## 第 0 步：查阅官方安装说明

在构建之前，始终获取 `https://docs.nvidia.com/holoscan/sdk-user-guide/sdk_installation.html` 的“从源代码构建”部分（以及所选标签的链接 GitHub `README.md` / `DEVELOP.md`），提取：目标架构和 CUDA 主版本的所需 `./run` 标志、支持的分支/标签、为发布指定的任何 Dockerfile 补丁，以及建议用于验证的测试名称。如果文档与以下内容不一致，则以文档为准。

## 第 1 步：前置条件

检查 git 和 Docker（带 GPU 转发）是否可用：

```bash
git --version
docker --version
docker run --rm --gpus all ubuntu:22.04 nvidia-smi
```

- 如果 Docker 缺失 → 从 https://docs.docker.com/engine/install/ 帮助安装。
- 如果 GPU 转发失败 → 安装 NVIDIA 容器工具包：
  ```bash
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
  sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
  sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
  ```
- 如果 Docker buildx 缺失：`sudo apt-get install docker-buildx-plugin`

## 第 2 步：克隆仓库

如果需要，将仓库克隆到 ~/holoscan/holoscan-sdk

```bash
mkdir -p ~/holoscan/
git clone https://github.com/nvidia-holoscan/holoscan-sdk.git
cd ~/holoscan/holoscan-sdk
```

要构建特定的发布标签（推荐用于稳定性）：

```bash
git tag | grep -E '^v[0-9]' | sort -V | tail -5   # 列出最近标签
git checkout v<VERSION>                             # 例如 v4.1.0
```

## 第 3 步：构建

`./run build` 脚本处理容器创建、CMake 配置、编译和安装，一步完成。首次运行时提醒用户这可能需要 **10–30 分钟**（下载基础镜像 + 编译）。

```bash
./run build
```

常见选项：

| 标志 | 目的 |
|------|---------|
| `--type debug` | 调试构建（符号，无优化） |
| `--type RelWithDebInfo` | 发布 + 调试符号 |
| `--arch aarch64` | 为 ARM64 跨编译（需要 `sudo apt install qemu-user-static`） |
| `--gpu igpu` | Jetson/IGX 的 iGPU 构建 |
| `--dryrun` | 预览命令而不执行 |

如果更改选项后出现 CMake 缓存错误：

```bash
./run clear_cache && ./run build
```

输出将位于以下文件夹中，并可以使用 `./run get_build_dir` 和 `./run get_install_dir` 获取
* 构建目录：`build-cu<N>-<arch>/`
* 安装目录：`install-cu<N>-<arch>/`.

## 第 4 步：运行测试

运行以下测试
* EXAMPLE_CPP_HELLO_WORLD_TEST
* EXAMPLE_PYTHON_HELLO_WORLD_TEST
* EXAMPLE_CPP_TENSOR_INTEROP_TEST
* EXAMPLE_PYTHON_TENSOR_INTEROP_TEST
* EXAMPLE_CPP_VIDEO_REPLAYER_TEST
* EXAMPLE_PYTHON_VIDEO_REPLAYER_TEST

```bash
./run test
```

要一次性运行所有六个必需的测试，使用单引号正则表达式（`|` 必须加引号以防止 bash 将其视为管道）：

```bash
./run test --options "-R 'EXAMPLE_CPP_HELLO_WORLD_TEST|EXAMPLE_PYTHON_HELLO_WORLD_TEST|EXAMPLE_CPP_TENSOR_INTEROP_TEST|EXAMPLE_PYTHON_TENSOR_INTEROP_TEST|EXAMPLE_CPP_VIDEO_REPLAYER_TEST|EXAMPLE_PYTHON_VIDEO_REPLAYER_TEST' --output-on-failure"
```

通过名称或正则表达式运行特定测试：

```bash
./run test --name <test_name>
./run test --options "-R '<regex>' --output-on-failure"
./run test --verbose
```

**重要提示：** 当正则表达式字符串包含 `|` 时，始终使用单引号——不加引号，bash 将 `|` 解释为管道，命令会因 `command not found` 而失败。

预期：所有测试通过。注意任何失败情况，并在继续之前向用户报告。

## 第 5 步：将应用程序指向安装树

构建完成后，应用程序可以将安装树作为 CMake 依赖项使用。给用户这个路径：

```
/path/to/holoscan-sdk/install-cu<N>-<arch>/
```

他们可以在构建自己的应用程序时将 `Holoscan_ROOT` 或 `CMAKE_PREFIX_PATH` 设置为此目录。

## 故障排除

| 症状 | 解决方法 |
|------|-----|
| 运行测试时出现 `bash: <TEST_NAME>: command not found` | 正则表达式包含 `\|`——用单引号括起来：`--options "-R '<regex>'"` |
| 更改选项后出现 CMake 缓存错误 | `./run clear_cache && ./run build` |
| Docker buildx 未找到 | `sudo apt-get install docker-buildx-plugin` |
| 构建容器内看不到 GPU | 验证 NVIDIA 容器工具包并重新运行 `sudo nvidia-ctk runtime configure --runtime=docker` |
| 跨编译失败（aarch64） | 安装 qemu：`sudo apt-get install qemu-user-static` |
