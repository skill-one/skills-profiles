# Jenkins Pipeline

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

使用声明式和脚本式方法创建企业级 Jenkins 管道，以自动化构建、测试和部署，并具有高级控制流程。

## 使用场景

- 企业 CI/CD 基础设施
- 复杂的多阶段构建
- 本地部署自动化
- 参数化构建

## 快速入门

最小工作示例：

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
        stage('检出') { steps { checkout scm } }
        stage('安装') { steps { sh 'npm ci' } }
        stage('校验') { steps { sh 'npm run lint' } }
        stage('测试') {
            steps {
                sh 'npm run test:coverage'
                junit 'test-results.xml'
            }
        }
        stage('构建') {
            steps {
                sh 'npm run build'
                archiveArtifacts artifacts: 'dist/**/*'
            }
        }
// ... (参考指南查看完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [声明式管道 (Jenkinsfile)](references/declarative-pipeline-jenkinsfile.md) | 声明式管道 (Jenkinsfile) |
| [脚本式管道](references/scripted-pipeline.md) | 脚本式管道 (Groovy), 多分支管道, 参数化管道, 带凭证的管道 |

## 最佳实践

### ✅ 应该

- 使用声明式管道以提高清晰度
- 使用凭证插件管理密钥
- 归档工件和报告
- 为生产环境实现审批门禁
- 保持管道模块化和可复用

### ❌ 不应该

- 在管道代码中存储凭证
- 忽略管道错误
- 忽略测试覆盖率报告
- 使用已弃用的插件
