# CUDA-Q 指南

## 目的

指导用户完成 CUDA-Q 的安装、基本内核、GPU 模拟目标、QPU 访问、内置应用程序、多 GPU 执行以及 Python `@cudaq.kernel` 编写。对于 Qiskit 到 CUDA-Q 的移植，请使用 `cudaq-importing` 技能。

## 前置条件

- Python 3.10+ 用于 Python CUDA-Q 工作流。
- Linux 系统上的 CUDA Toolkit 和 NVIDIA GPU 用于 GPU 加速目标。
- 通过 `qpp-cpu` 可用 CPU 模拟；macOS 仅支持 CPU 模拟。
- C++ 工作流需要 Linux 或 WSL 以及 C++20。
- QPU 工作流需要特定提供者的凭证和账户。

## 说明

- 使用 `/cudaq-guide [参数]` 调用。
- 如果未提供参数，将显示入门菜单并询问用户想了解哪个主题。
- 使用下方的路由表选择相关的参考文件。
- 当答案取决于特定 CUDA-Q 版本或后端行为时，请阅读本地 CUDA-Q 文档文件。
- 不要从本技能回答 Qiskit 移植问题；请使用 `cudaq-importing`。

## 参数路由

| 参数 | 操作 | 参考 |
|---|---|---|
| `install` | 指导 Python 或 C++ 的安装和验证。 | [references/onboarding.md](references/onboarding.md) |
| `test-program` | 构建并运行一个 Bell 态内核。 | [references/onboarding.md](references/onboarding.md) |
| `gpu-sim` | 选择 GPU、多 GPU、张量网络或 CPU 目标。 | [references/onboarding.md](references/onboarding.md) |
| `qpu` | 指导提供者选择和安全设置 QPU。 | [references/onboarding.md](references/onboarding.md) |
| `applications` | 总结 CUDA-Q 应用领域和笔记本。 | [references/onboarding.md](references/onboarding.md) |
| `parallelize` | 选择 `mgpu`、`mqpu`、异步调度或分布式观察。 | [references/onboarding.md](references/onboarding.md) |
| `author` | 编写 CUDA-Q Python 内核，选择执行 API，并调试编译器问题。 | [references/authoring.md](references/authoring.md) |
| _(无)_ | 打印下方菜单并询问要探索的主题。 | 本文件 |

## 菜单

```text
CUDA-Q 入门

CUDA-Q 是 NVIDIA 的统一量子-经典编程模型，支持 CPU、GPU 和 QPU。
支持 Python 和 C++。文档：https://nvidia.github.io/cuda-quantum/latest/

选择一个主题：
  /cudaq-guide install         安装 CUDA-Q
  /cudaq-guide test-program    编写和运行 Bell 态内核
  /cudaq-guide gpu-sim         在 NVIDIA GPU 上加速模拟
  /cudaq-guide qpu             连接到真实的 QPU 硬件
  /cudaq-guide applications    探索可以构建的内容
  /cudaq-guide parallelize     在 GPU 或 QPU 上运行
  /cudaq-guide author          编写 @cudaq.kernel Python 代码
```

## 参考文件

- [references/onboarding.md](references/onboarding.md)：安装、测试程序、GPU 目标、QPU 提供者、应用领域、并行化模式、示例和平台故障排除。
- [references/authoring.md](references/authoring.md)：执行 API、内核语言约束、静默失败陷阱、常见编码模式、资源指标、调试和验证。

## 限制

- 指南针对 CUDA-Q Python/C++ 工作流，编写细节侧重于 CUDA-Q 0.14 和 0.15 中使用的装饰器模式 Python API。
- GPU 和多 GPU 支持取决于本地 CUDA-Q、CUDA Toolkit、驱动程序、MPI 和硬件可用性。
- QPU 访问和目标选项是提供者特定的，可能会更改；在提供操作步骤之前，请与本地文档进行验证。

## 故障排除

- **安装 `pip install cudaq` 后出现导入错误**：检查 Python 3.10+ 和支持的操作系统。
- **未检测到 GPU**：验证 CUDA Toolkit 和 `nvidia-smi`；回退到 `qpp-cpu`。
- **内核编译错误**：阅读 [references/authoring.md](references/authoring.md) 并检查受限的内核语言子集。
- **特定版本的行行为不同**：比较 `cudaq.__version__` 与最新文档，然后调试已安装版本时，查看相关文档或源代码更改。
- **QPU 提交失败**：验证提供者凭证是否设置为环境变量或通过密钥管理器，切勿硬编码。
- **文档查找失败**：尝试一次暂时的 MCP 或存储库查找，然后回退到本地文档或官方 CUDA-Q 文档。
