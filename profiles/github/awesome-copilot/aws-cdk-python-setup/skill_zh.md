# AWS CDK Python 安装指南

本指南提供使用 **Python** 开发 **AWS CDK (Cloud Development Kit)** 项目的设置指导。

---

## 前置条件

开始之前，请确保已安装以下工具：

- **Node.js** ≥ 14.15.0 — AWS CDK CLI 所需
- **Python** ≥ 3.7 — 用于编写 CDK 代码
- **AWS CLI** — 管理凭证和资源
- **Git** — 版本控制和项目管理

---

## 安装步骤

### 1. 安装 AWS CDK CLI
```bash
npm install -g aws-cdk
cdk --version
```

### 2. 配置 AWS 凭证
```bash
# 如果未安装，请安装 AWS CLI
brew install awscli

# 配置凭证
aws configure
```
在提示时输入您的 AWS Access Key、Secret Access Key、默认区域和输出格式。

### 3. 创建新的 CDK 项目
```bash
mkdir my-cdk-project
cd my-cdk-project
cdk init app --language python
```

您的项目将包含：
- `app.py` — 主应用程序入口
- `my_cdk_project/` — CDK 堆栈定义
- `requirements.txt` — Python 依赖
- `cdk.json` — 配置文件

### 4. 设置 Python 虚拟环境
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 5. 安装 Python 依赖
```bash
pip install -r requirements.txt
```
主要依赖：
- `aws-cdk-lib` — 核心CDK结构
- `constructs` — 基础构造库

---

## 开发工作流

### 合成 CloudFormation 模板
```bash
cdk synth
```
生成 `cdk.out/` 包含 CloudFormation 模板。

### 部署堆栈到 AWS
```bash
cdk deploy
```
审查并确认部署到配置的 AWS 账户。

### 首次部署前的引导
```bash
cdk bootstrap
```
准备环境资源（如 S3 桶）用于存储资源。

---

## 最佳实践

- 工作前始终激活虚拟环境。
- 部署前运行 `cdk diff` 预览变更。
- 使用开发账户进行测试。
- 遵循 Pythonic 命名和目录规范。
- 固定 `requirements.txt` 以确保构建一致性。

---

## 故障排除提示

如果出现问题，请检查：

- AWS 凭证是否正确配置。
- 默认区域是否设置正确。
- Node.js 和 Python 版本是否满足最低要求。
- 运行 `cdk doctor` 诊断环境问题。
