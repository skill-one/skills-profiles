# GitHub Actions 模板

用于测试、构建和部署应用程序的生产就绪 GitHub Actions 工作流模式。

## 目的

为各种技术栈创建高效、安全的 GitHub Actions 工作流，以实现持续集成和部署。

## 使用场景

- 自动化测试和部署
- 构建 Docker 镜像并推送到注册中心
- 部署到 Kubernetes 集群
- 运行安全扫描
- 为多个环境实现矩阵构建

## 常见工作流模式

### 模式 1：测试工作流

```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: 使用 Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: 安装依赖项
        run: npm ci

      - name: 运行代码检查器
        run: npm run lint

      - name: 运行测试
        run: npm test

      - name: 上传覆盖率
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
```

**参考：** 查看 `assets/test-workflow.yml`

### 模式 2：构建和推送 Docker 镜像

```yaml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: 登录到容器注册中心
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 提取元数据
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: 构建和推送
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**参考：** 查看 `assets/deploy-workflow.yml`

### 模式 3：部署到 Kubernetes

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 配置 AWS 凭证
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: 更新 kubeconfig
        run: |
          aws eks update-kubeconfig --name production-cluster --region us-west-2

      - name: 部署到 Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/my-app -n production
          kubectl get services -n production

      - name: 验证部署
        run: |
          kubectl get pods -n production
          kubectl describe deployment my-app -n production
```

### 模式 4：矩阵构建

```yaml
name: Matrix Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: 设置 Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: 安装依赖项
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 运行测试
        run: pytest
```

**参考：** 查看 `assets/matrix-build.yml`

## 工作流最佳实践

1. **使用特定版本的动作** (@v4，而不是 @latest)
2. **缓存依赖项** 以加快构建速度
3. **使用密钥** 存储敏感数据
4. **在 PR 上实现状态检查**
5. **使用矩阵构建** 进行多版本测试
6. **设置适当的权限**
7. **使用可重用工作流** 进行常见模式
8. **为生产环境实现审批门禁**
9. **添加通知步骤** 用于失败情况
10. **使用自托管运行器** 进行敏感工作负载

## 可重用工作流

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm test
```

**使用可重用工作流：**

```yaml
jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: "20.x"
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 安全扫描

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 运行 Trivy 漏洞扫描器
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"

      - name: 将 Trivy 结果上传到 GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"

      - name: 运行 Snyk 安全扫描
        uses: snyk/actions/node@0.4.0
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## 带审批的部署

```yaml
name: Deploy to Production

on:
  push:
    tags: ["v*"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com

    steps:
      - uses: actions/checkout@v4

      - name: 部署应用程序
        run: |
          echo "Deploying to production..."
          # 部署命令在此处

      - name: 通知 Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Deployment to production completed successfully!"
            }
```

## 相关技能

- `gitlab-ci-patterns` - 用于 GitLab CI 工作流
- `deployment-pipeline-design` - 用于管道架构
- `secrets-management` - 用于密钥管理
