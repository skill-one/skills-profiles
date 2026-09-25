# 在Limrun RBE上构建Bazel iOS项目

在Limrun的远程Mac工作器上构建Apple Bazel项目——无论您身处何种环境（Linux、Windows、macOS、虚拟机、容器），无需本地Xcode。`lim xcode rbe`将远程RBE堆栈启动起来，将其隧道传输到本地端口，并写入`.limrun/`配置文件，以便`bazelisk build --config=limrun`远程执行Apple操作。永远不会回退到本地Xcode或构建工具。

## 认证和CLI

如有需要，请安装：`npm install --global lim`。认证方式为`lim login`或`LIM_API_KEY`（可能设置在项目外部——不要因为缺失就索要它）。CLI是权威来源：本技巧中的命令已验证，但如果标志出错或您需要此处未显示的标志，请检查`lim xcode rbe --help`而不是猜测。

## 构建

1. 从**Bazel工作区根目录**（包含`MODULE.bazel` / `WORKSPACE`），运行`lim xcode rbe`。它会设置实例并写入`.limrun/`配置文件，并**打印确切的构建命令**。隧道在后台运行（打印PID）；`--no-daemon`将其保持在前台。
2. 运行打印的命令，例如：
   `bazelisk --digest_function=sha256 build --config=limrun //App`。

不要手动编写`.limrun/`或标志——CLI会为沙盒的Xcode和您的操作系统生成它们。`lim xcode version set 27`（或一次性`lim xcode rbe --xcode-version 27`）使用另一个安装的Xcode构建：一个主版本绑定该主版本的GA版本，一个主次版本（如`27.1`）固定该确切版本（预发布版）。在`--stop`后重新运行`lim xcode rbe`以刷新，以便在舰队Xcode升级或Xcode切换后刷新。

要在limrun路径中添加您自己的Bazel标志，而无需编辑生成的配置，请将它们放在工作区根目录下的**`user.limrun.bazelrc`**中。生成的配置最后尝试导入它，因此您的`build:limrun --…`行会生效，并且它会在`lim xcode rbe`重新生成时保留（`.limrun/`不会）。

## 在模拟器上运行

`lim xcode rbe`仅用于构建；当用户想要查看或运行应用时，请附加模拟器。检查或附加（它会立即安装最后一次构建，因此无需重新构建）：

```bash
lim xcode get             # 模拟器是否已附加？
lim ios create --attach   # 附加一个
```

当您没有浏览器向用户展示时，请添加`--no-open`；它会跳过在本地打开流URL，但仍会打印出来以供分享。

如果附加输出包含一个已签名的流URL，请将其作为Markdown链接与用户分享，例如`[Live simulator](<signed-stream-url>)`。

附加模拟器后，每个成功的`--config=limrun`构建会自动重新安装并重新启动应用，无需单独的安装步骤：

```bash
bazelisk --digest_function=sha256 build --config=limrun //App
```

注意：
- 如果您已经知道需要模拟器：`lim xcode rbe --ios`（在启动时附加，`--stop`时移除）。
- 自动安装在服务器端从构建事件发生；没有`lim xcode rbe install`子命令或`--target`标志。要强制重新安装，请重新构建（缓存命中的重新构建只需几秒钟）。
- 它在成功调用生成单个应用时触发；在多应用工作区构建中，每个调用一个应用目标（`//App`，而不是`//...`）；多应用构建会成功但不会安装任何内容。

要点击、输入、读取元素树、截图或录制运行中的应用，请切换到**`limrun-ios-simulator`**技巧。

## 将构建作为资源上传

要发布构建为Limrun资源（预览链接、在其他模拟器上安装、CI工件），在隧道启动时或事后上传一次：

```bash
lim xcode rbe --auto-upload preview/my-app --upload-ttl 24h  # 每次成功的构建都会刷新资源
lim xcode rbe upload preview/my-app --ttl 24h                # 一次性：最新成功的构建
```

- `--auto-upload`适用于隧道的整个生命周期：每个成功的`--config=limrun`构建都会在资源名称下重新上传应用，无需后构建步骤。上传结果会出现在`.limrun/rbe.log`中。
- `rbe upload`从工作区根目录运行，需要一个后台隧道以及至少一次成功的构建；否则会出错。
- TTL是Go持续时间（`24h`，`30m`；`1d`无效）且可选；每个没有TTL的上传会将资源的过期时间推至该上传后的14天。
- 要更改运行隧道中的`--auto-upload`配置，请使用`--stop`并重新运行；CLI会拒绝不匹配的重新武装，而不是静默忽略它。
- 在浏览器中预览上传的应用：
  `https://console.limrun.com/preview?asset=<name>&platform=ios`。

## 拆卸

使用**`lim xcode rbe --stop`**停止（~20秒拆除远程堆栈）并使用**`lim xcode delete <id>`**删除实例

## 注意事项

- **在`build`之前始终传递`--digest_function=sha256`**（使用CLI打印的命令字面量）。Limrun缓存仅支持SHA256；Bazel 9默认为BLAKE3。这是一个启动标志，因此它不能存在于`--config=limrun`中。症状：
  构建 → `无法使用BLAKE3哈希函数与远程缓存`；安装 → `非SHA256摘要 … 使用 --digest_function=sha256 重新构建`。
- **从工作区根目录运行`lim xcode rbe`**，而不是子目录——它会将`.limrun/`写入其中，否则会快速失败。
- **绿色的构建并不能证明远程执行**——缓存命中（`action cache hit` / `remote cache hit`）即使隧道消失也会使构建通过。要强制并验证真实的远程执行，请参阅`references/verify-remote.md`。
- **打印的`.ipa`路径在您的机器上不存在**——构建命令包含`--remote_download_outputs=minimal`，这会保留工件在实例的缓存中，并且不会下载任何内容。Bazel仍然会打印其通常的`Target //App:App up-to-date: …/App.ipa`行，但该文件**不在**磁盘上。这是预期的，不是失败的构建。附加模拟器时，构建会从工件的缓存摘要自动安装（从构建事件日志读取，而不是本地文件）。只有当您确实需要在本地需要`.ipa`时，从构建命令中删除`--remote_download_outputs=minimal`，Bazel会下载顶层输出；无论哪种方式，自动安装都有效。
- **新实例可能会在第一次构建时因`Lost inputs no longer available remotely`（例如`… Assets.car`）而失败**。这是实例之间的临时缓存驱逐，不是代码错误；Bazel会打印`Found transient remote cache error, retrying the build...`，并且重试会成功。为了避免在演示中途遇到它，在`lim xcode rbe`后立即进行完整构建进行预热。
- **`You don't have permission to save … in "CoreSimulator"`（actool/ibtool）是舰队端的设备差距，而不是您的配置。重试；如果仍然存在，请向Limrun报告。
- **项目的自己的Bazel设置可能会与RBE冲突**（通过Starlark转换固定Xcode、自定义`remote_default_exec_properties`、对沙盒不利的genrules）。这些是按项目划分的，而不是Limrun的错误——在得出RBE已损坏的结论之前，请参阅`references/project-compatibility.md`。
