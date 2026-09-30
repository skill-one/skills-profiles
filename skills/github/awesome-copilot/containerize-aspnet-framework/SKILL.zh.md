---
name: containerize-aspnet-framework
description: 将 ASP.NET .NET Framework 项目容器化，通过创建针对项目的 Dockerfile 和 .dockerfile 文件来实现。
---

# ASP.NET .NET Framework 容器化提示

容器化下方容器化设置中指定的 ASP.NET (.NET Framework) 项目，重点关注**仅**应用程序在 Windows Docker 容器中运行所需的更改。容器化应考虑此处指定的所有设置。

**记住：** 这是一个 .NET Framework 应用程序，而不是 .NET Core。容器化过程将与 .NET Core 应用程序的容器化过程不同。

## 容器化设置

本提示的这一部分包含容器化 ASP.NET (.NET Framework) 应用程序所需的特定设置和配置。在运行此提示之前，请确保已使用必要信息填写设置。请注意，在许多情况下，只需要填写前几个设置。如果它们不适用于要容器化的项目，则可以保留后续设置为默认值。

未指定的任何设置都将设置为默认值。默认值提供在 `[方括号]` 中。

### 基本项目信息
1. 要容器化的项目：
   - `[项目名称（提供 .csproj 文件的路径）]`

2. 要使用的 Windows Server SKU：
   - `[Windows Server Core（默认）或 Windows Server Full]`

3. 要使用的 Windows Server 版本：
   - `[2022、2019 或 2016（默认 2022）]`

4. Docker 图像构建阶段的自定义基础镜像（“None”以使用标准 Microsoft 基础镜像）：
   - `[指定用于构建阶段的基础镜像（默认 None）]`

5. Docker 图像运行阶段的自定义基础镜像（“None”以使用标准 Microsoft 基础镜像）：
   - `[指定用于运行阶段的基础镜像（默认 None）]`   

### 容器配置
1. 容器镜像中必须暴露的端口：
   - 主要 HTTP 端口：`[例如，80]`
   - 其他端口：`[列出任何其他端口，或 "None"]`

2. 容器应作为其运行的用户帐户：
   - `[用户帐户，或默认为 "ContainerUser"]`

3. 容器镜像中必须配置的 IIS 设置：
   - `[列出任何特定 IIS 设置，或 "None"]`

### 构建配置
1. 构建容器镜像之前必须执行的的自定义构建步骤：
   - `[列出任何特定构建步骤，或 "None"]`

2. 构建容器镜像之后必须执行的自定义构建步骤：
   - `[列出任何特定构建步骤，或 "None"]`

### 依赖项
1. 容器镜像中应在 GAC 中注册的 .NET 程序集：
   - `[程序集名称和版本，或 "None"]`

2. 必须复制到容器镜像并安装的 MSIs：
   - `[MSI 名称和版本，或 "None"]`

3. 必须在容器镜像中注册的 COM 组件：
   - `[COM 组件名称，或 "None"]`

### 系统配置
1. 必须添加到容器镜像中的注册表键和值：
   - `[注册表路径和值，或 "None"]`

2. 必须在容器镜像中设置的 môi trường 变量：
   - `[变量名称和值，或 "使用默认值"]`

3. 必须在容器镜像中安装的 Windows Server 角色和功能：
   - `[角色/功能名称，或 "None"]`

### 文件系统
1. 需要复制到容器镜像的文件/目录：
   - `[相对于项目根目录的路径，或 "None"]`
   - 容器中的目标位置：`[容器路径，或 "不适用"]`

2. 要从容器化中排除的文件/目录：
   - `[要排除的路径，或 "None"]`

### .dockerignore 配置
1. 要包含在 `.dockerignore` 文件中的模式（.dockerignore 将已经具有常见默认值；这些是附加模式）：
   - 附加模式：`[列出任何附加模式，或 "None"]`

### 健康检查配置
1. 健康检查端点：
   - `[健康检查 URL 路径，或 "None"]`

2. 健康检查间隔和超时：
   - `[间隔和超时值，或 "使用默认值"]`

### 其他说明
1. 容器化项目必须遵循的其他说明：
   - `[特定要求，或 "None"]`

2. 已知的要解决的问题：
   - `[描述任何已知问题，或 "None"]`

## 范围

- ✅ 应用程序配置修改，以确保使用配置构建器从环境变量中读取应用程序设置和连接字符串
- ✅ 创建和配置 ASP.NET 应用程序的 Dockerfile
- ✅ 在 Dockerfile 中指定多个阶段以构建/发布应用程序并将输出复制到最终镜像
- ✅ 配置 Windows 容器平台兼容性（Windows Server Core 或 Full）
- ✅ 正确处理依赖项（GAC 程序集、MSIs、COM 组件）
- ❌ 无基础设施设置（假定将分别处理）
- ❌ 无超出容器化所需代码更改的代码更改

## 执行过程

1. 审查上述容器化设置以了解容器化要求
2. 创建一个 `progress.md` 文件以跟踪更改并使用复选标记
3. 通过检查 `.csproj` 文件中的 `TargetFrameworkVersion` 元素来确定 .NET Framework 版本
4. 根据以下内容选择适当的 Windows Server 容器镜像：
   - 从项目中检测到的 .NET Framework 版本
   - 容器化设置中指定的 Windows Server SKU（Core 或 Full）
   - 容器化设置中指定的 Windows Server 版本（2016、2019 或 2022）
   - Windows Server Core 标签可以在以下位置找到：https://github.com/microsoft/dotnet-framework-docker/blob/main/README.aspnet.md#full-tag-listing
5. 确保安装了所需的 NuGet 包。**不要**如果它们缺失则安装它们。如果它们未安装，用户必须手动安装它们。如果它们未安装，请暂停执行此提示并要求用户使用 Visual Studio NuGet 包管理器或 Visual Studio 包管理器控制台安装它们。所需的包如下：
   - `Microsoft.Configuration.ConfigurationBuilders.Environment`
6. 修改 `web.config` 文件以添加配置构建器部分和设置，从环境变量中读取应用程序设置和连接字符串：
   - 在 `configSections` 中添加 ConfigBuilders 部分
   - 在根目录中添加 configBuilders 部分
   - 配置 EnvironmentConfigBuilder 以用于 appSettings 和 connectionStrings
   - 示例模式：
     ```xml
     <configSections>
       <section name="configBuilders" type="System.Configuration.ConfigurationBuildersSection, System.Configuration, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" restartOnExternalChanges="false" requirePermission="false" />
     </configSections>
     <configBuilders>
       <builders>
         <add name="Environment" type="Microsoft.Configuration.ConfigurationBuilders.EnvironmentConfigBuilder, Microsoft.Configuration.ConfigurationBuilders.Environment" />
       </builders>
     </configBuilders>
     <appSettings configBuilders="Environment">
       <!-- 现有的 app settings -->
     </appSettings>
     <connectionStrings configBuilders="Environment">
       <!-- 现有的连接字符串 -->
     </connectionStrings>
     ```
7. 在将创建 Dockerfile 的文件夹中创建一个 `LogMonitorConfig.json` 文件，通过复制本提示末尾的参考 `LogMonitorConfig.json` 文件。文件的内容**必须**不修改，并且应与参考内容完全匹配，除非容器化设置中的说明指定否则如此。
   - 特别是，确保要记录的问题级别不变，因为使用 `Information` 级别对于 EventLog 源会导致不必要的噪音。
8. 在项目目录的根目录中创建一个 Dockerfile 以容器化应用程序
   - Dockerfile 应使用多个阶段：
     - 构建阶段：使用 Windows Server Core 镜像构建应用程序
       - 构建阶段必须使用 `mcr.microsoft.com/dotnet/framework/sdk` 基础镜像，除非设置文件中指定了自定义基础镜像
       - 首先复制 sln、csproj 和 packages.config 文件
       - 如果存在，则复制 NuGet.config 并配置任何私有源
       - 恢复 NuGet 包       
       - 然后，复制其余的源代码并使用 MSBuild 构建和发布到 C:\publish
     - 最终阶段：使用选定的 Windows Server 镜像运行应用程序
       - 最终阶段必须使用 `mcr.microsoft.com/dotnet/framework/aspnet` 基础镜像，除非设置文件中指定了自定义基础镜像
       - 将 `LogMonitorConfig.json` 文件复制到容器中的目录（例如，C:\LogMonitor）
       - 从 Microsoft 存储库下载 LogMonitor.exe 到同一目录
           - 正确的 LogMonitor.exe URL 是：https://github.com/microsoft/windows-container-tools/releases/download/v2.1.1/LogMonitor.exe
       - 将工作目录设置为 C:\inetpub\wwwroot
       - 将构建阶段的发布输出（在 C:\publish）复制到最终镜像
       - 将容器的入口点设置为使用 LogMonitor.exe 和 ServiceMonitor.exe 监控 IIS 服务
           - `ENTRYPOINT [ "C:\\LogMonitor\\LogMonitor.exe", "C:\\ServiceMonitor.exe", "w3svc" ]`
   - 确保考虑容器化设置中的所有要求：
     - Windows Server SKU 和版本
     - 暴露的端口
     - 容器的用户帐户
     - IIS 设置
     - GAC 程序集注册
     - MSI 安装
     - COM 组件注册
     - 注册表键
     - 环境变量
     - Windows 角色和功能
     - 文件/目录复制
   - 参照本提示末尾提供的示例 Dockerfile 进行建模，但请确保根据特定项目要求和设置进行自定义
   - **重要：** 除非用户在设置文件中**明确请求**了完整的 Windows Server 镜像，否则必须使用 Windows Server Core 基础镜像
9. 在项目目录的根目录中创建一个 `.dockerignore` 文件以排除 Docker 镜像中的不必要文件。`.dockerignore` 文件**必须**至少包含以下元素以及容器化设置中指定的附加模式：
   - packages/
   - bin/
   - obj/
   - .dockerignore
   - Dockerfile
   - .git/
   - .github/
   - .vs/
   - .vscode/
   - **/node_modules/
   - *.user
   - *.suo
   - **/.DS_Store
   - **/Thumbs.db
   - 容器化设置中指定的任何附加模式
10. 如果设置中指定了健康检查，请配置：
    - 如果提供了健康检查端点，则向 Dockerfile 添加 HEALTHCHECK 指令
11. 通过向项目文件添加以下项将 dockerfile 添加到项目中：`<None Include="Dockerfile" />`
12. 将任务标记为完成：[ ] → [✓]
13. 继续直到所有任务完成并且 Docker 构建成功

## 构建和运行时验证

完成 Dockerfile 后，确认 Docker 构建成功。使用以下命令构建 Docker 镜像：

```bash
docker build -t aspnet-app:latest .
```

如果构建失败，请查看错误消息并对 Dockerfile 或项目配置进行必要的调整。报告成功/失败。

## 进度跟踪

维护一个 `progress.md` 文件，具有以下结构：
```markdown
# 容器化进度

## 环境检测
- [ ] .NET Framework 版本检测（版本：___）
- [ ] Windows Server SKU 选择（SKU：___）
- [ ] Windows Server 版本选择（版本：___）

## 配置更改
- [ ] Web.config 修改以用于配置构建器
- [ ] NuGet 包源配置（如果适用）
- [ ] 复制 LogMonitorConfig.json 并根据设置要求进行调整

## 容器化
- [ ] Dockerfile 创建
- [ ] .dockerignore 文件创建
- [ ] 使用 SDK 镜像创建构建阶段
- [ ] 复制 sln、csproj、packages.config 以及（如果适用）NuGet.config 以进行包还原
- [ ] 使用运行时镜像创建运行时阶段
- [ ] 非根用户配置
- [ ] 依赖项处理（GAC、MSI、COM、注册表、附加文件等）
- [ ] 健康检查配置（如果适用）
- [ ] 特殊要求实现

## 验证
- [ ] 审查容器化设置并确保所有要求都得到满足
- [ ] Docker 构建成功
```

在步骤之间不要暂停确认。按部就班地进行，直到应用程序已容器化并且 Docker 构建成功。

**直到所有复选框都被标记，您才算完成！** 这包括成功构建 Docker 镜像并解决构建过程中出现的任何问题。

## 参考材料

### 示例 Dockerfile

用于 ASP.NET (.NET Framework) 应用程序的示例 Dockerfile，使用 Windows Server Core 基础镜像。

```dockerfile
# escape=`
# 脱逸指令将脱逸字符从 \ 改为 `
# 这在 Windows Dockerfile 中特别有用，因为 \ 是路径分隔符

# ============================================================
# 阶段 1：构建并发布应用程序
# ============================================================

# 基础镜像 - 选择合适的 .NET Framework 版本和 Windows Server Core 版本
# 可能的标签包括：
# - 4.8.1-windowsservercore-ltsc2025 (Windows Server 2025)
# - 4.8-windowsservercore-ltsc2022 (Windows Server 2022)
# - 4.8-windowsservercore-ltsc2019 (Windows Server 2019)
# - 4.8-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7.2-windowsservercore-ltsc2019 (Windows Server 2019)
# - 4.7.2-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7.1-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.6.2-windowsservercore-ltsc2016 (Windows Server 2016)
# - 3.5-windowsservercore-ltsc2025 (Windows Server 2025)
# - 3.5-windowsservercore-ltsc2022 (Windows Server 2022)
# - 3.5-windowsservercore-ltsc2019 (Windows Server 2019)
# - 3.5-windowsservercore-ltsc2019 (Windows Server 2016)
# 使用 .NET Framework SDK 镜像来构建应用程序
FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2022 AS build
ARG BUILD_CONFIGURATION=Release

# 将默认 shell 设置为 PowerShell
SHELL ["powershell", "-command"]

WORKDIR /app

# 复制解决方案和项目文件
COPY YourSolution.sln .
COPY YourProject/*.csproj ./YourProject/
COPY YourOtherProject/*.csproj ./YourOtherProject/

# 复制 packages.config 文件
COPY YourProject/packages.config ./YourProject/
COPY YourOtherProject/packages.config ./YourOtherProject/

# 恢复 NuGet 包
RUN nuget restore YourSolution.sln

# 复制源代码
COPY . .

# 在这里执行自定义的预构建步骤，如果需要的话

# 构建并发布应用程序到 C:\publish
RUN msbuild /p:Configuration=$BUILD_CONFIGURATION `
            /p:WebPublishMethod=FileSystem `
            /p:PublishUrl=C:\publish `
            /p:DeployDefaultTarget=WebPublish

# 在这里执行自定义的构建后步骤，如果需要的话

# ============================================================
# 阶段 2：最终的运行时镜像
# ============================================================

# 基础镜像 - 选择合适的 .NET Framework 版本和 Windows Server Core 版本
# 可能的标签包括：
# - 4.8.1-windowsservercore-ltsc2025 (Windows Server 2025)
# - 4.8-windowsservercore-ltsc2022 (Windows Server 2022)
# - 4.8-windowsservercore-ltsc2019 (Windows Server 2019)
# - 4.8-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7.2-windowsservercore-ltsc2019 (Windows Server 2019)
# - 4.7.2-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7.1-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.7-windowsservercore-ltsc2016 (Windows Server 2016)
# - 4.6.2-windowsservercore-ltsc2016 (Windows Server 2016)
# - 3.5-windowsservercore-ltsc2025 (Windows Server 2025)
# - 3.5-windowsservercore-ltsc2022 (Windows Server 2022)
# - 3.5-windowsservercore-ltsc2019 (Windows Server 2019)
# - 3.5-windowsservercore-ltsc2019 (Windows Server 2016)
# 使用 .NET Framework ASP.NET 镜像来运行应用程序
FROM mcr.microsoft.com/dotnet/framework/aspnet:4.8-windowsservercore-ltsc2022

# 将默认 shell 设置为 PowerShell
SHELL ["powershell", "-command"]

WORKDIR /inetpub/wwwroot

# 从构建阶段复制
COPY --from=build /publish .

# 添加任何应用程序需要的额外环境变量（根据需要取消注释并修改）
# ENV KEY=VALUE

# 安装 MSI 包（根据需要取消注释并修改）
# COPY ./msi-installers C:/Installers
# RUN Start-Process -Wait -FilePath 'msiexec.exe' -ArgumentList '/i', 'C:\Installers\your-package.msi', '/quiet', '/norestart'

# 安装自定义的 Windows Server 角色和功能（根据需要取消注释并修改）
# RUN dism /Online /Enable-Feature /FeatureName:YOUR-FEATURE-NAME

# 添加额外的 Windows 功能（根据需要取消注释并修改）
# RUN Add-WindowsFeature Some-Windows-Feature; `
#    Add-WindowsFeature Another-Windows-Feature

# 如果需要，安装 MSI 包（根据需要取消注释并修改）
# COPY ./msi-installers C:/Installers
# RUN Start-Process -Wait -FilePath 'msiexec.exe' -ArgumentList '/i', 'C:\Installers\your-package.msi', '/quiet', '/norestart'

# 如果需要，在 GAC 中注册程序集（根据需要取消注释并修改）
# COPY ./assemblies C:/Assemblies
# RUN C:\Windows\Microsoft.NET\Framework64\v4.0.30319\gacutil -i C:/Assemblies/YourAssembly.dll

# 如果需要，注册 COM 组件（根据需要取消注释并修改）
# COPY ./com-components C:/Components
# RUN regsvr32 /s C:/Components/YourComponent.dll

# 如果需要，添加注册表键（根据需要取消注释并修改）
# RUN New-Item -Path 'HKLM:\Software\YourApp' -Force; `
#     Set-ItemProperty -Path 'HKLM:\Software\YourApp' -Name 'Setting' -Value 'Value'

# 如果需要，配置 IIS 设置（根据需要取消注释并修改）
# RUN Import-Module WebAdministration; `
#     Set-ItemProperty 'IIS:\AppPools\DefaultAppPool' -Name somePropertyName -Value 'SomePropertyValue'; `
#     Set-ItemProperty 'IIS:\Sites\Default Web Site' -Name anotherPropertyName -Value 'AnotherPropertyValue'

# 暴露必要的端口 - 默认情况下，IIS 使用端口 80
EXPOSE 80
# EXPOSE 443  # 如果使用 HTTPS，请取消注释

# 从 microsoft/windows-container-tools 仓库复制 LogMonitor
WORKDIR /LogMonitor
RUN curl -fSLo LogMonitor.exe https://github.com/microsoft/windows-container-tools/releases/download/v2.1.1/LogMonitor.exe

# 从本地文件复制 LogMonitorConfig.json
COPY LogMonitorConfig.json .

# 设置非管理员用户
USER ContainerUser

# 覆盖容器的默认入口点，以利用 LogMonitor
ENTRYPOINT [ "C:\\LogMonitor\\LogMonitor.exe", "C:\\ServiceMonitor.exe", "w3svc" ]
```

## 适应此示例

**注意：** 根据容器化设置中的具体要求自定义此模板。

在适应此示例 Dockerfile 时：

1. 将 `YourSolution.sln`、`YourProject.csproj` 等替换为您的实际文件名
2. 根据需要调整 Windows Server 和 .NET Framework 版本
3. 根据您的需求修改依赖项安装步骤，并删除任何不必要的步骤
4. 根据您的特定工作流程添加或删除阶段

## 阶段命名的注意事项

- `AS stage-name` 语法为每个阶段命名
- 使用 `--from=stage-name` 从先前的阶段复制文件
- 您可以有多个中间阶段，这些阶段在最终镜像中未使用

### LogMonitorConfig.json

LogMonitorConfig.json 文件应在项目目录的根目录中创建。它用于配置 LogMonitor 工具，该工具监控容器中的日志。此文件的内容应与以下内容完全一致，以确保正确的日志记录功能：
```json
{
  "LogConfig": {
    "sources": [
      {
        "type": "EventLog",
        "startAtOldestRecord": true,
        "eventFormatMultiLine": false,
        "channels": [
          {
            "name": "system",
            "level": "Warning"
          },
          {
            "name": "application",
            "level": "Error"
          }
        ]
      },
      {
        "type": "File",
        "directory": "c:\\inetpub\\logs",
        "filter": "*.log",
        "includeSubdirectories": true,
        "includeFileNames": false
      },
      {
        "type": "ETW",
        "eventFormatMultiLine": false,
        "providers": [
          {
            "providerName": "IIS: WWW Server",
            "providerGuid": "3A2A4E84-4C21-4981-AE10-3FDA0D9B0F83",
            "level": "Information"
          },
          {
            "providerName": "Microsoft-Windows-IIS-Logging",
            "providerGuid": "7E8AD27F-B271-4EA2-A783-A47BDE29143B",
            "level": "Information"
          }
        ]
      }
    ]
  }
}
```
