---
name: ci-cd
description: .NET应用程序的CI/CD流水线。涵盖GitHub Actions和Azure DevOps YAML流水线，包含构建、测试、发布和部署阶段。在设置持续集成、自动化测试、部署工作流时加载此技能，或当用户提及“CI/CD”、“流水线”、“GitHub Actions”、“Azure DevOps”、“工作流”、“部署”、“构建流水线”、“发布”、“NuGet推送”、“发布”或“持续集成”时。
---

# CI/CD

## 核心原则

1. **将流水线作为代码** — 将 YAML 流水线提交到代码库。UI 中不使用点击式操作。
2. **快速反馈** — 每次推送时构建和测试。缓存 NuGet 包。快速失败。
3. **一次构建，多次部署** — 一次构建工件，通过环境（开发 → 测试预发布 → 生产）进行分发。
4. **永不跳过测试** — 测试控制流水线。没有通过测试的部署不允许进行。

## 模式

### GitHub Actions — 构建 + 测试

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  DOTNET_VERSION: '10.0.x'
  DOTNET_NOLOGO: true
  DOTNET_CLI_TELEMETRY_OPTOUT: true

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v5

      - name: 设置 .NET
        uses: actions/setup-dotnet@v5
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: 还原
        run: dotnet restore

      - name: 构建
        run: dotnet build --no-restore --configuration Release

      - name: 格式检查
        run: dotnet format --verify-no-changes --no-restore

      - name: 测试
        run: dotnet test --no-build --configuration Release --logger trx --results-directory TestResults
        env:
          ConnectionStrings__Default: "Host=localhost;Database=testdb;Username=postgres;Password=postgres"

      - name: 发布测试结果
        uses: actions/upload-artifact@v5
        if: always()
        with:
          name: test-results
          path: TestResults/*.trx
```

### GitHub Actions — 构建 + 发布 Docker 镜像

```yaml
# .github/workflows/publish.yml
name: Publish

on:
  push:
    tags: ['v*']

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v5

      - name: 登录 GitHub 容器注册中心
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 从标签提取版本号
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: 构建并推送
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.version.outputs.VERSION }}
            ghcr.io/${{ github.repository }}:latest
```

### Azure DevOps — 构建 + 测试

与 GitHub Actions 相同的还原 → 构建 → 格式 → 测试流程。主要区别：

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main]
  paths:
    exclude: ['*.md', docs/]

pool:
  vmImage: 'ubuntu-latest'          # vs runs-on: ubuntu-latest

variables:
  dotnetVersion: '10.0.x'

# 与 GitHub Actions 的主要任务区别：
#   设置 .NET:  task: UseDotNet@2  (inputs: version: $(dotnetVersion))
#   测试结果: task: PublishTestResults@2  (testResultsFormat: VSTest)
#   步骤使用 `script:` + `displayName:` 而不是 `- name:` + `run:`
#   服务（例如 Postgres）需要单独的 Docker 任务或流水线服务连接
```

### NuGet 包发布

```yaml
# GitHub Actions 工作流的一部分
- name: 打包
  run: dotnet pack src/MyLibrary -c Release -o ./nupkg --no-build

- name: 推送到 NuGet
  run: dotnet nuget push ./nupkg/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
```

## 反模式

### 每个环境构建不同的工件

```yaml
# BAD — 为每个环境单独构建
- script: dotnet publish -c Debug   # 用于开发
- script: dotnet publish -c Release # 用于生产

# GOOD — 一次构建，到处部署
- script: dotnet publish -c Release -o ./publish
# 然后将相同的 ./publish 工件部署到开发、测试预发布、生产
```

### CI 中跳过格式检查

```yaml
# BAD — 无格式强制执行
steps:
  - run: dotnet build
  - run: dotnet test

# GOOD — 格式检查可早期捕获风格问题
steps:
  - run: dotnet build
  - run: dotnet format --verify-no-changes
  - run: dotnet test
```

### 在流水线中硬编码密钥

```yaml
# BAD — 流水线 YAML 中的密钥
env:
  DB_PASSWORD: "my-secret-password"

# GOOD — 使用流水线密钥
env:
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 开源项目 | GitHub Actions |
| 企业使用 Azure | Azure DevOps 流水线 |
| Docker 部署 | CI 中的多阶段构建，推送到容器注册中心 |
| NuGet 库 | 构建 → 测试 → 打包 → 标签时推送 |
| 数据库迁移 | 在 CI 测试阶段运行，生产环境使用脚本 |
| 环境提升 | 相同工件，不同配置 |
