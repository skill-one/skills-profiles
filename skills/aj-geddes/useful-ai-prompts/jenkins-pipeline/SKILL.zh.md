---
name: jenkins-pipeline
description: 使用阶段、代理、参数和插件构建Jenkins声明式和脚本化流水线。实现多分支流水线和部署自动化。
---

# Jenkins 流水线

## 目录

- [概述](#overview)
- [适用场景](#when-to-use)
- [快速入门](#quick-start)
- [参考指南](#reference-guides)
- [最佳实践](#best-practices)

## 概述

使用声明式和脚本式方法创建企业级 Jenkins 流水线，以自动化构建、测试和部署，并实现高级控制流。

## 适用场景

- 企业级 CI/CD 基础设施
- 复杂的多阶段构建
- 本地部署自动化
- 参数化构建

## 快速入门

最小可行示例：

```groovy
pipeline {
    agent { label 'linux-docker' }
    environment {
        REGISTRY = 'docker.io'
        IMAGE_NAME = 'myapp'
    }
    parameters {
        string(name: 'DEPLOY_ENV', defaultValue: 'staging')
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install') { steps { sh 'npm ci' } }
        stage('Lint') { steps { sh 'npm run lint' } }
        stage('Test') {
            steps {
                sh 'npm run test:coverage'
                junit 'test-results.xml'
            }
        }
        stage('Build') {
            steps {
                sh 'npm run build'
                archiveArtifacts artifacts: 'dist/**/*'
            }
        }
// ...（完整实现请参见参考指南）
```

## 参考指南

详细实现位于 `references/` 目录中：

| 指南 | 内容 |
|---|---|
| [声明式流水线（Jenkinsfile）](references/declarative-pipeline-jenkinsfile.md) | 声明式流水线（Jenkinsfile） |
| [脚本式流水线](references/scripted-pipeline.md) | 脚本式流水线（Groovy）、多分支流水线、参数化流水线、带凭据的流水线 |

## 最佳实践

### ✅ 推荐做法

- 使用声明式流水线以提高清晰度
- 使用凭据插件管理机密信息
- 归档产物和报告
- 为生产环境实施审批门控
- 保持流水线模块化和可复用

### ❌ 不推荐做法

- 在流水线代码中存储凭据
- 忽略流水线错误
- 跳过测试覆盖率报告
- 使用已弃用的插件
