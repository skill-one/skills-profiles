此技能提供使用 `android` 命令行工具的说明。该工具包含用于创建项目、运行应用程序、与设备交互以及管理命令行环境的各种命令。

## 安装

如果 `android` 工具不在路径中，请安装它。要安装，请运行以下命令：

- Linux: curl -fsSL https://dl.google.com/android/cli/latest/linux_x86_64/install.sh \| bash
- Mac Arm: curl -fsSL https://dl.google.com/android/cli/latest/darwin_arm64/install.sh \| bash
- Mac Intel: curl -fsSL https://dl.google.com/android/cli/latest/darwin_x86_64/install.sh \| bash
- Windows: curl -fsSL https://dl.google.com/android/cli/latest/windows_x86_64/install.cmd -o "%TEMP%\\i.cmd" \&\& "%TEMP%\\i.cmd"

## SDK 管理

要管理 Android SDK 和工具的安装，请使用 `sdk` 命令。例如：

- `android sdk install <package>[@<version>]...`: 安装特定包。可以指定多个包，用空格分隔。`<version>` 默认为最新版本。例如：`android sdk install platforms/android-30@2 platforms/android-34`
- `android sdk update [<pkg-name>]`: 更新特定包或所有包到最新版本。
- `android sdk remove <pkg-name>`: 从本地 SDK 中删除包。
- `android sdk list --all`: 列出已安装和可用的 SDK 包。

## 项目创建

使用 `create` 命令从模板创建项目。

例如：`android create empty-activity --name="My App" --output=./my-app`

## 与 Android 设备交互

使用 `android layout` 命令以 JSON 格式检查 Android 应用程序的 UI 布局。使用 `android screen` 命令以可视化方式检查 UI 并获取视觉区域的边界坐标。

**重要提示**：在使用 `android layout` 或 `android screen` 之前，你必须阅读此参考：[interact.md](references/interact.md) 参考文件 [interact.md](references/interact.md) 包含与 Android 设备正确交互的说明。请严格按照其说明操作。

### 运行 journey 测试

Journey 测试涉及设备交互；使用 `android layout` 和 `android screen` 命令评估 Journeys。此处同样适用设备交互说明。

**重要提示**：在评估 journey 之前，你必须阅读此参考：[journeys.md](references/journeys.md) 参考文件 [journeys.md](references/journeys.md) 包含正确评估 Android journey 的说明。请严格按照其说明操作。

## 文档搜索

`docs` 命令搜索 Android 开发者知识库中的权威、高质量的 Android 开发文档。通过提供几个关键词，该工具将返回包含示例或使用 Android API 或库的指导的高质量文章。使用此工具获取有关如何实现特定于 Android 的任务或了解更多关于 Android API、表面、库或设备的信息。

始终使用此工具获取有关 Android 概念的最新信息。典型的良好用例包括：

- 查找 API 的迁移指南。
- 查找 API 的示例。
- 查找有关 Android API 的最新信息。
- 查找 Android 概念的最佳实践。

## 运行 APK

使用 `run` 命令运行 Android 应用程序。

## 管理 模拟器

使用 `android emulator` 命令管理 Android 虚拟设备 (AVD)。

## 截屏

使用 `android screen` 命令捕获连接的 Android 设备当前屏幕的图像并将其输出到文件。

## 管理 技能

使用 `android skills` 命令管理 Android 代理技能。

## 更新 CLI

使用 `android update` 命令更新 Android CLI。

## `android help` 输出

    使用方法：android [-Vhv] [--sdk=PARAM] [COMMAND]
      -h, --help       显示此命令的帮助信息
          --sdk=PARAM  Android SDK 的路径
      -v, --verbose    启用调试信息的详细输出
      -V, --version    打印版本信息并退出
    命令：
      completion  为 Android CLI 在当前用户配置文件中安装 shell 自动完成配置
      create      从可用模板创建新的 Android 项目。允许指定项目名称、输出目录、minSdk 和干运行执行
      describe    分析 Android 项目以生成描述性元数据。此命令识别并输出详细说明项目结构的 JSON 文件路径，包括构建目标和它们对应的输出工件位置（例如，APK）。这些信息使其他工具和命令能够高效地定位构建工件
      docs        Android 文档命令，用于搜索和获取来自官方知识库的开发者文档
      emulator    管理 Android 虚拟设备 (AVDs)。包括启动、停止、列出和查看模拟器详细信息的命令
      help        显示所有命令的帮助信息
      info        打印环境信息，包括 SDK 位置、连接的设备和配置变量。使用特定字段来缩小输出
      init        初始化 Android CLI 的环境。设置所需的配置、目录和默认技能
      install     将 Android 应用程序（一个或多个 APK）安装到连接的设备或模拟器，而不会激活任何组件，使用增量优化比 adb 更快的部署
      layout      返回应用程序的布局树
      run         在连接的设备或模拟器上构建、部署和启动 Android 应用程序
      screen      查看设备的命令
      sdk         管理 Android SDK 安装。包括安装、更新、删除和列出可用和已安装 SDK 包的命令
      skills      管理 Android CLI 技能。包括安装、删除、列出和按关键字搜索技能的命令
      studio      Android Studio 命令
      update      将 Android CLI 更新到最新版本

    completion
              使用方法：android completion [-h] [<shell>]
              为 Android CLI 在当前用户配置文件中安装 shell 自动完成配置
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              
              位置参数：
                <shell>  如果提供，则打印给定的 shell 自动完成，而不会安装。支持：bash, zsh

    create
              使用方法：android create [-h] [--applicationId=PARAM] [--list] [--minSdk=PARAM]
                                    [--name=PARAM] [--namespace=PARAM] [--output=PARAM]
                                    [<template-name>]
              从可用模板创建新的 Android 项目。允许指定项目名称、输出目录、minSdk 和干运行执行
              
              选项：
                    --applicationId=PARAM  应用程序的应用 ID（例如 'com.example.myapp'）
                -h, --help                 显示此命令的帮助信息
                    --list                 列出所有可用模板
                    --minSdk=PARAM         应用程序支持的 'minSdk'（默认在模板中定义）
                    --name=PARAM           应用程序的名称（例如 'My Application'）
                    --namespace=PARAM      资源和 Kotlin 源文件的包名命名空间
                -o, --output=PARAM         目标项目目录路径（默认为 '.'）
              
              android 选项：
                    --sdk=PARAM            Android SDK 的路径
                -v, --verbose              启用调试信息的详细输出
                -V, --version              打印版本信息并退出
              
              位置参数：
                <template-name>  模板名称

    describe
              使用方法：android describe [-h] [--project_dir=PARAM]
              分析 Android 项目以生成描述性元数据。此命令识别并输出详细说明项目结构的 JSON 文件路径，包括构建目标和它们对应的输出工件位置（例如，APK）。这些信息使其他工具和命令能够高效地定位构建工件
              
              选项：
                -h, --help               显示此命令的帮助信息
                    --project_dir=PARAM  要描述的项目目录
              
              android 选项：
                    --sdk=PARAM          Android SDK 的路径
                -v, --verbose            启用调试信息的详细输出
                -V, --version            打印版本信息并退出

    docs
              使用方法：android docs [-h] [COMMAND]
              Android 文档命令，用于搜索和获取来自官方知识库的开发者文档
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              命令：
                search  搜索 Android 文档。将关键词括在引号中
                fetch   从 URL（kb://...）获取 Android 文档文章

    emulator
              使用方法：android emulator [-h] [COMMAND]
              管理 Android 虚拟设备 (AVDs)。包括启动、停止、列出和查看模拟器详细信息的命令
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              命令：
                create  创建虚拟设备
                start   启动指定的虚拟设备。此命令将在模拟器完全启动并准备好使用时返回
                stop    停止指定的虚拟设备
                list    列出可用的虚拟设备
                remove  删除虚拟设备

    help
              使用方法：android help [-h] [COMMAND]
              显示所有命令的帮助信息
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              
              位置参数：
                COMMAND  要显示帮助信息的命令

    info
              使用方法：android info [-h] [<field>]
              打印环境信息，包括 SDK 位置、连接的设备和配置变量。使用特定字段来缩小输出
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              
              位置参数：
                <field>  要打印值的特定字段。如果省略，则打印所有内容

    init
              使用方法：android init [-h]
              初始化 Android CLI 的环境。设置所需的配置、目录和默认技能
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出

    install
              使用方法：android install [-h] [--apks=PARAM] [--device=PARAM] [--install-options=PARAM]
                                     [--use-delta-install]
              将 Android 应用程序（一个或多个 APK）安装到连接的设备或模拟器，而不会激活任何组件，使用增量优化比 adb 更快的部署
              
              选项：
                    --apks=PARAM             APK 的路径，用逗号分隔
                    --device=PARAM           设备序列号
                -h, --help                   显示此命令的帮助信息
                    --install-options=PARAM  传递给包管理器安装的附加选项/标志（例如 -g,-d）
                    --use-delta-install      使用快速增量安装（通过仅传输修改的代码和资源来加快增量更新；默认为 true)
              
              android 选项：
                    --sdk=PARAM              Android SDK 的路径
                -v, --verbose                启用调试信息的详细输出
                -V, --version                打印版本信息并退出

    layout
              使用方法：android layout [-dhp] [--device=PARAM] [--flat] [--full] [--no-idle]
                                    [--output=PARAM]
              返回应用程序的布局树
              
              选项：
                    --device=PARAM  设备序列号
                -d, --diff          已弃用；无操作标志。将在未来的版本中删除
                    --flat          返回扁平列表而不是树
                    --full          返回完整树，包括非交互式和隐藏元素
                -h, --help          显示此命令的帮助信息
                    --no-idle       在获取布局时不等待布局空闲状态
                -o, --output=PARAM  将布局写入指定的文件或目录。如果省略，则打印到标准输出
                -p, --pretty        美化返回的 JSON
              
              android 选项：
                    --sdk=PARAM     Android SDK 的路径
                -v, --verbose       启用调试信息的详细输出
                -V, --version       打印版本信息并退出

    run
              使用方法：android run [-h] [--activity=PARAM] [--apks=PARAM] [--debug] [--device=PARAM]
                                 [--install-options=PARAM] [--type=PARAM] [--use-delta-install]
              在连接的设备或模拟器上构建、部署和启动 Android 应用程序
              
              选项：
                    --activity=PARAM         活动名称
                    --apks=PARAM             APK 的路径，用逗号分隔
                    --debug                  以调试模式运行
                    --device=PARAM           设备序列号
                -h, --help                   显示此命令的帮助信息
                    --install-options=PARAM  传递给包管理器安装的附加选项/标志（例如 -g,-d）
                    --type=PARAM             组件类型（ACTIVITY, WATCH_FACE, TILE, COMPLICATION,
                                             DECLARATIVE_WATCH_FACE, WEAR_WIDGET）
                    --use-delta-install      使用快速增量安装（通过仅传输修改的代码和资源来加快增量更新；默认为 true)
              
              android 选项：
                    --sdk=PARAM              Android SDK 的路径
                -v, --verbose                启用调试信息的详细输出
                -V, --version                打印版本信息并退出

    screen
              使用方法：android screen [-h] [COMMAND]
              查看设备的命令
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              命令：
                capture  将设备屏幕输出为 PNG
                resolve  以可视化方式目标 UI 元素。将注释屏幕中的边界框坐标替换为字符串。将所有 '#N' 实例替换为标记为 'N' 的边界框的中心坐标

    sdk
              使用方法：android sdk [-h] [--platform=PARAM] [COMMAND]
              管理 Android SDK 安装。包括安装、更新、删除和列出可用和已安装 SDK 包的命令
              
              选项：
                -h, --help            显示此命令的帮助信息
                    --platform=PARAM  目标平台 <os>_<arch>（例如 linux_x86_64, mac_arm64, windows_x86），默认为当前主机
              
              android 选项：
                    --sdk=PARAM       Android SDK 的路径
                -v, --verbose         启用调试信息的详细输出
                -V, --version         打印版本信息并退出
              命令：
                install  安装 SDK 包
                update   将一个或所有包更新到最新版本
                remove   从 SDK 中删除包
                list     列出已安装和可用的 SDK 包

    skills
              使用方法：android skills [-h] [COMMAND]
              管理 Android CLI 技能。包括安装、删除、列出和按关键字搜索技能的命令
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              命令：
                add     通过其 ID 在环境中安装特定技能
                remove  通过其 ID 删除已安装的技能
                list    列出已安装和可用的技能
                find    在存储库中搜索与关键字匹配的可用技能
                update  更新已安装的技能

    studio
              使用方法：android studio [-h] [COMMAND]
              Android Studio 命令
              
              选项：
                -h, --help       显示此命令的帮助信息
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
              命令：
                find-declaration        查找符号的声明
                find-usages             查找符号的使用情况
                open-file               在 Android Studio 中打开文件
                check                   检查正在运行的 Studio 实例的状态
                analyze-file            在 Android Studio 中分析文件
                render-compose-preview  在 Android Studio 中渲染 Compose 预览
                version-lookup          在互联网上查找 maven 工件、Android 版本等最新可用版本

    update
              使用方法：android update [-h] [--url=PARAM]
              将 Android CLI 更新到最新版本
              
              选项：
                -h, --help       显示此命令的帮助信息
                    --url=PARAM  下载更新的 URL
              
              android 选项：
                    --sdk=PARAM  Android SDK 的路径
                -v, --verbose    启用调试信息的详细输出
                -V, --version    打印版本信息并退出
