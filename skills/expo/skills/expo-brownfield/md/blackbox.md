# expo-brownfield (`expo/skills/expo-brownfield`)

## blackbox

**function**: 把 React Native 页面塞进你现有的原生 iOS / Android App 里, 让原生工程和 RN 代码共存且能正常构建运行。

- input: 一个现有的原生 iOS 或 Android 工程目录 + 一句需求, 如「在这个 SwiftUI App 里加一个 React Native 页面」, output: 改好的工程代码与配置; 原生 App 构建后在原有导航中能打开该 RN 页面, 可传入参数、拿到返回结果、正常关闭再重开
- input: 约束条件, 如「原生团队不装 Node/RN 工具链」或「RN 代码和原生代码分两个仓库、各自发版」, output: 可直接引用的 AAR (Android 库包) / XCFramework (iOS 库包) 产物, 原生 App 像引一个普通库一样接入, 无需 RN 开发环境
- input: 一段报错信息或现象描述, 如「RN 页面在原生 App 里白屏」「Release 包跑不起来」「依赖解析失败」, output: 问题原因说明 + 修复后的代码/配置改动, 并附上「在 Release 构建、关闭 Metro 下验证通过」的验收结果
