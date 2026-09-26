# macOS SwiftPM 应用打包（无需 Xcode）

## 概述
使用 `assets/templates/bootstrap/` 作为启动布局，构建一个完整的 SwiftPM macOS 应用文件夹，然后无需 Xcode 即可构建、打包和运行。使用 `references/packaging.md` + `references/release.md` 了解打包和发布详情。

## 两步工作流程
1) 引导项目文件夹
   - 将 `assets/templates/bootstrap/` 复制到新仓库中。
   - 将 `Package.swift`、`Sources/MyApp/` 和 `version.env` 中的 `MyApp` 重命名为其他名称。
   - 自定义 `APP_NAME`、`BUNDLE_ID` 和版本号。

2) 构建、打包并运行引导的应用
   - 将 `assets/templates/` 中的脚本复制到你的仓库中（例如，`Scripts/`）。
   - 构建/测试：`swift build` 和 `swift test`。
   - 打包：`Scripts/package_app.sh`。
   - 运行：`Scripts/compile_and_run.sh`（推荐）或 `Scripts/launch.sh`。
   - 发布（可选）：`Scripts/sign-and-notarize.sh` 和 `Scripts/make_appcast.sh`。
   - 标签 + GitHub 发布（可选）：创建 git 标签，上传 zip/appcast 到 GitHub 发布，并发布。

## 最小端到端示例
从引导到运行应用的捷径：
```bash
# 1. 复制并重命名骨架
cp -R assets/templates/bootstrap/ ~/Projects/MyApp
cd ~/Projects/MyApp
sed -i '' 's/MyApp/HelloApp/g' Package.swift version.env

# 2. 复制脚本
cp assets/templates/package_app.sh Scripts/
cp assets/templates/compile_and_run.sh Scripts/
chmod +x Scripts/*.sh

# 3. 构建和启动
swift build
Scripts/compile_and_run.sh
```

## 验证检查点
在关键步骤后运行这些命令，以便在进入下一阶段前尽早捕获失败。

**打包后 (`Scripts/package_app.sh`)：**
```bash
# 确认 .app 包结构完整
ls -R build/HelloApp.app/Contents

# 检查二进制文件是否存在且可执行
file build/HelloApp.app/Contents/MacOS/HelloApp
```

**签名后 (`Scripts/sign-and-notarize.sh` 或临时开发签名)：**
```bash
# 检查签名和权限
codesign -dv --verbose=4 build/HelloApp.app

# 验证包通过 Gatekeeper 检查
spctl --assess --type execute --verbose build/HelloApp.app
```

**签名后并 Staple：**
```bash
# 确认 Staple 票据已附加
stapler validate build/HelloApp.app

# 重新运行 Gatekeeper 确认签名被识别
spctl --assess --type execute --verbose build/HelloApp.app
```

## 常见签名失败
| 症状 | 可能原因 | 恢复 |
|---|---|---|
| `The software asset has already been uploaded` | 同版本重复提交 | 在 `version.env` 中增加 `BUILD_NUMBER` 并重新打包。 |
| `Package Invalid: Invalid Code Signing Entitlements` | `.entitlements` 文件中的权限与配置文件不匹配 | 对照 Apple 允许的权限集审计权限；移除不支持的键。 |
| `The executable does not have the hardened runtime enabled` | `codesign` 调用中缺少 `--options runtime` 标志 | 编辑 `sign-and-notarize.sh` 将 `--options runtime` 添加到所有 `codesign` 调用中。 |
| 签名卡住/无状态邮件 | `xcrun notarytool` 网络或凭证问题 | 运行 `xcrun notarytool history` 检查状态；如果 App Store Connect API 密钥过期，重新导出。 |
| `stapler validate` 签名成功后失败 | 票据尚未传播 | 等待 ~60 秒，然后重新运行 `xcrun stapler staple`。 |

## 模板
- `assets/templates/package_app.sh`：构建二进制文件、创建 .app 包、复制资源、签名。
- `assets/templates/compile_and_run.sh`：开发循环，终止运行中的应用、打包、启动。
- `assets/templates/build_icon.sh`：从 Icon Composer 文件生成 .icns（需要安装 Xcode）。
- `assets/templates/sign-and-notarize.sh`：签名、Staple 并压缩发布构建。
- `assets/templates/make_appcast.sh`：生成 Sparkle 更新 appcast 条目。
- `assets/templates/setup_dev_signing.sh`：创建稳定的开发代码签名身份。
- `assets/templates/launch.sh`：简单的 .app 包启动器。
- `assets/templates/version.env`：示例版本文件，被打包脚本使用。
- `assets/templates/bootstrap/`：最小的 SwiftPM macOS 应用骨架（Package.swift、Sources/、version.env）。

## 注意事项
- 保持权限和签名配置显式；编辑模板脚本而不是重新实现。
- 如果不使用 Sparkle 进行更新，请移除 Sparkle 步骤。
- Sparkle 依赖于包构建号 (`CFBundleVersion`)，因此 `version.env` 中的 `BUILD_NUMBER` 必须每次更新时增加。
- 对于菜单栏应用，打包时设置 `MENU_BAR_APP=1` 以在 Info.plist 中输出 `LSUIElement`。
