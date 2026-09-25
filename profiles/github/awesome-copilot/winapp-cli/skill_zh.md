# Windows 应用开发 CLI

`winapp` 管理 Windows SDKs、MSIX 打包、应用标识、清单、证书、签名、商店发布以及面向 Windows 的任何框架（.NET/csproj、C++、Electron、Rust、Tauri、Flutter 等）的 UI 自动化。公共预览版 — 可随时更改。

## 前置条件

- Windows 10 或更高版本
- 通过以下任一方式安装：
  - WinGet: `winget install Microsoft.WinAppCli --source winget`
  - npm (Electron/Node): `npm install @microsoft/winappcli --save-dev`
  - CI: [`setup-WinAppCli`](https://github.com/microsoft/setup-WinAppCli) GitHub Action
  - 手动: [GitHub 发布](https://github.com/microsoft/WinAppCli/releases/latest)

## 命令

| 命令 | 目的 |
| ------- | ------- |
| `init` | 初始化项目：SDKs (`stable`/`preview`/`experimental`/`none`)、清单、`winapp.yaml`。**`.csproj` 项目会跳过 `winapp.yaml`** 并直接使用 NuGet。**不会自动生成证书** (v0.2.0+)。 |
| `restore` / `update` | 恢复或更新 SDK 包版本 (`--setup-sdks preview` 用于预览 SDKs)。 |
| `pack <dir>` | 构建MSIX。标志：`--generate-cert`、`--cert <pfx> --cert-password`、`--self-contained` (捆绑 WinAppSDK 运行时)、`--output`。自动发现第三方 WinRT 组件（v0.2.1+）。 |
| `run <dir> [-- <app args>]` | 作为松散布局打包并作为打包应用启动 — 适用于无需生成 MSIX 的 IDE F5 调试。支持 `--` 参数透传（v0.3.1+）。(v0.3.0+) |
| `create-debug-identity <exe>` | 为可执行文件添加稀疏包标识，以便它可以调用需要标识的应用程序 API（通知、Windows AI、外壳集成）而无需完整打包。 |
| `unregister` | 移除由 `run` / `create-debug-identity` 注册的 sideloaded 开发包。 |
| `manifest` | 生成 `AppxManifest.xml`；支持占位符和限定名称。`manifest update-assets <image>` 从一个源生成所有必需的图标尺寸（PNG **或 SVG**，v0.2.1+）。 |
| `cert generate` / `install` / `info` | 管理开发证书。`cert info <pfx> --password <pwd>` 显示主题/颁发者/有效期。`--export-cer` 导出公钥。`--json` 在 `generate` 和 `info` 上可用（v0.2.1+）。 |
| `sign <target> --cert <pfx>` | 签名 MSIX 或可执行文件；可选的时间戳服务器。 |
| `tool` | 使用配置的路径运行 Windows SDK 构建工具。 |
| `store` | 运行 Microsoft Store 开发者 CLI 进行商店提交/验证/发布。 |
| `create-external-catalog` | 为 TrustedLaunch 稀疏包生成 `CodeIntegrityExternal.cat`。 |
| `ui list-windows` / `inspect` / `click` / `search` / `wait-for` / `get-focused` | 通过 Microsoft UI Automation 进行 UI 自动化。所有支持 `--json`。**`inspect`、`get-focused`、`search` 和 `wait-for` 的 JSON 封装在 v0.3.1 中更改** — 查看 [`references/ui-json-envelope.md`](./references/ui-json-envelope.md)（其他 `ui` 子命令保留其 0.3.1 之前的输出）。(v0.3.0+) |
| `node create-addon` / `add-electron-debug-identity` / `clear-electron-debug-identity` | Electron/Node 辅助工具。所有命令也作为 `@microsoft/winappcli` 的类型化 JS/TS 函数公开（v0.2.1+）。 |

CI 小贴士：传递 `--no-prompt` 以跳过交互式提示。

## 工作流

标准的初始化 → 打包流程：

1. **初始化项目** 在你的应用文件夹中。设置 SDK 引用、清单和 `winapp.yaml`（`.csproj` 项目会跳过 YAML 并直接配置 NuGet）。

   ```bash
   winapp init        # 在 CI 中添加 --no-prompt
   ```

2. **生成开发签名证书** — 用于 sideloading 所需。`init` 不再为非 `.csproj` 项目创建证书（v0.2.0+）。固定输出路径，以便后续步骤可以引用它。

   ```bash
   winapp cert generate --publisher "CN=My Company" --output ./mycert.pfx --install
   ```

3. **使用框架自己的工具链构建你的应用** (`dotnet build`、`npm run build`、`cargo build` 等）。
4. **作为 MSIX 打包**，使用步骤 2 中的证书签名。

   ```bash
   winapp pack ./build-output --cert ./mycert.pfx --cert-password password --output MyApp.msix
   ```

5. **（可选）在分发前使用生产证书重新签名**。

   ```bash
   winapp sign MyApp.msix --cert ./prod.pfx --cert-password $env:CERT_PWD
   ```

6. **（可选）使用 `winapp store …` 提交给 Microsoft Store**（封装了 Store 开发者 CLI）。

### 替代流程

- **无需打包调试需要标识的 API**（通知、Windows AI、外壳）：

  ```bash
  winapp create-debug-identity ./bin/MyApp.exe
  ./bin/MyApp.exe
  ```

- **作为打包应用运行以进行 IDE F5**（松散布局；应用参数在 `--` 后）：

  ```bash
  winapp run ./bin/Debug/net10.0-windows10.0.26100.0/win-x64 \
    --manifest ./appxmanifest.xml -- --my-flag value
  ```

- **Electron**:

  ```bash
  npx winapp init
  npx winapp node add-electron-debug-identity
  npx winapp pack ./out --output MyElectronApp.msix
  ```

## 注意事项

- **`winapp ui --json` 封装在 v0.3.1 中重塑** — `ui inspect`、`ui get-focused`、`ui search` 和 `ui wait-for` 使用新的形状；移除了每个元素的 `id` / `parentSelector` / `windowHandle`（使用 `selector`）。完整模式在 [`references/ui-json-envelope.md`](./references/ui-json-envelope.md) 中。
- **`winapp init` 不再自动生成证书** (v0.2.0+) — 明确运行 `winapp cert generate`。旧的 `--no-cert` 标志已移除。
- **`.csproj` 项目会跳过 `winapp.yaml`** — SDK 包位于项目文件中。混合设置需要调整。
- **NuGet 全局缓存，不是 `%userprofile%/.winapp/packages`** (v0.2.0+) — 依赖于旧文件夹的脚本将中断。
- **在任何清单更改后重新运行 `create-debug-identity`** — 标识在注册时绑定。

## 故障排除

| 问题 | 解决方法 |
| ----- | --- |
| 证书不受信任 | `winapp cert install <pfx>` 添加到本地计算机存储 |
| 需要标识的 API 失败 | 在清单更改后重新运行 `create-debug-identity` |
| SDK 未找到 | `winapp restore` 或 `winapp update` |
| `run` / `create-debug-identity` 注册错误 `0x800704EC` | 开发者模式关闭 — 在 **设置 → 隐私和安全 → 开发者** 中启用它（或 `Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock' -Name AllowDevelopmentWithoutDevLicense -Value 1`），然后重试 |
| `run` / `create-debug-identity` 注册错误 `0x80073CFB` | 包已使用冲突的标识注册 — 运行 `winapp unregister`（如果从不同的项目树注册，则 `winapp unregister --force`），然后重试 |

## 参考

- [winapp CLI 仓库](https://github.com/microsoft/WinAppCli) · [完整使用文档](https://github.com/microsoft/WinAppCli/blob/main/docs/usage.md) · [.NET 指南](https://github.com/microsoft/WinAppCli/blob/main/docs/guides/dotnet.md) · [示例](https://github.com/microsoft/WinAppCli/tree/main/samples)
- [Windows 应用 SDK](https://learn.microsoft.com/windows/apps/windows-app-sdk/) · [MSIX 概述](https://learn.microsoft.com/windows/msix/overview) · [包标识概述](https://learn.microsoft.com/windows/apps/desktop/modernize/package-identity-overview)
