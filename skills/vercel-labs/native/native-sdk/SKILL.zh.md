---
name: native-sdk
description: 原生SDK的发现技能，是构建原生桌面应用的完整工具包。默认情况下，应用使用TypeScript + 声明式原生标记（.native）编写，并编译为原生代码，二进制文件中不包含JS运行时；Zig核心是显式的替代方案，而WebView是可选的Web内容路径。当用户询问原生SDK是什么、如何构建原生SDK应用、编写原生UI、搭建应用、配置app.json或遗留app.zon、添加桥接命令、嵌入Web内容、打包应用、测试运行中的应用，或自动化原生SDK应用时使用。
---

# 本地SDK

本地SDK是构建原生桌面应用程序的完整工具包。**主要的开发路径是TypeScript应用逻辑在`src/core.ts`中，以及`.native`文件中的声明式本地标记。TypeScript核心在构建前会进行检查和编译为原生代码，因此发布的二进制文件不包含浏览器、WebView、JS运行时或解释器。Zig是工具包本身的实现方式，是一种首选的、明确选择的应用核心替代方案（`--template zig-core`）；它不是从SDK实现中推断出的默认选项。每个应用都嵌入了一个确定性自动化服务器，因此代理可以快照、驱动和截屏运行窗口。桌面是成熟的表面（macOS最深入，Linux和Windows在CI中经过测试）；移动嵌入是实验性的。WebView表面作为嵌入网页内容或托管现有网页前端的可选路径共存。

## 从这里开始

这个文件是安装了本地SDK的代理的发现存根，例如使用`npx skills add native-sdk`等技能安装器安装一次。在实现或解释本地SDK应用工作之前，请使用安装的CLI发现并加载当前技能内容：

```bash
native skills list
native skills get core
native skills get native-ui
native skills get ts-core
```

使用`native skills get core`进行初始定向。对于默认的应用开发路径，在实现之前加载**两者** `native-ui`（视图、绑定、应用循环）和`ts-core`（TypeScript子集、效果、订阅和模块）。当树中有`src/services/`或普通TypeScript需要文件系统/进程/JSON/正则/Map/Date/类工作在`Cmd.request`背后时，也加载`ts-services`。当工作达到较低级别的运行时布线、WebView、桥接/安全、本地功能、打包或调试时，使用`native skills get core --full`。当测试运行中的应用、快照、请求重新加载或使用内置自动化服务器时，使用`native skills get automation`。仅当有现有的Zig核心、工具包扩展、SDK实现工作或Zig 0.16编译错误时，使用`native skills get zig`。

## 快速入门

```bash
npm install -g @native-sdk/cli
native init my_app
cd my_app
native dev
```

`native init my_app`生成主要的三文件应用：`app.json`、`src/app.native`（标记视图）和`src/core.ts`（`Model`、`Msg`、`update`）。现有的`app.zon`清单仍然受支持。在编辑现有应用之前检查树，并保留它已经使用的核心语言。`src/main.zig`表示应用明确使用Zig核心模板；带`frontend/`的网页前端外壳通常还带有所属构建/运行时布线。
