# expo-brownfield (`expo/skills/expo-brownfield`)

## whitebox

- 检查宿主: 确认原生入口、导航归属、构建系统、部署目标、是否已链接 RN 运行时, 并从 lockfile 记录版本; 与 RN 无关的任务 (如纯 EAS 提交) 转交 eas-app-stores
- 选方案: 按快速规则在 isolated (产出 AAR/XCFramework) 和 integrated (RN 源码进现有 Gradle/CocoaPods) 之间二选一
- 对齐版本: 现有 Expo/RN 项目保持原 SDK 用 npx expo install 对齐依赖; 新建生产端选当前稳定 SDK 并先查 version-compatibility.md
- 集成: 按所选方案的参考文档改造构建, 保留宿主原生外壳和导航; 手动维护的原生工程全程禁跑 prebuild
- 验收: 在宿主内打开 RN 页面→传入参数→回传结果→关闭→带新参数重开, 检查监听清理和原生导航; 以 Release 构建 + 停掉 Metro 为准

- 方案决策机制: 基于『原生团队是否要装 Node/RN 工具链、RN 与原生代码是否分仓、团队归属』的快速规则, 再落到 comparison.md 决策矩阵
- 版本兼容机制: version-compatibility.md 匹配各 SDK 的原生模板、工具链/OS 要求与构建默认值; 依赖对齐靠 npx expo install
- 外部依赖: Node.js (LTS) + Expo CLI + 项目自有包管理器 (不换); iOS 构建需 Xcode + CocoaPods; isolated 消费端只需 Xcode 即可使用产物, Debug 阶段两种方案都靠 Metro 做热刷新
