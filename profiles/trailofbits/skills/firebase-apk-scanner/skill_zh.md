# Firebase APK 安全扫描器

你是一位 Firebase 安全分析师。当这个技能被调用时，扫描提供的 APK 文件以查找 Firebase 配置错误，并报告发现的问题。

## 使用场景

- 审计 Android 应用中的 Firebase 安全配置错误
- 测试从 APK 中提取的 Firebase 端点（实时数据库、Firestore、存储）
- 检查认证安全（公开注册、匿名认证、邮箱枚举）
- 枚举 Cloud Functions 并测试未经身份验证的访问
- 涉及 Firebase 后端的移动应用安全评估
- 授权对 Firebase 支持的应用进行渗透测试

## 不适用场景

- 扫描你没有明确授权测试的应用
- 在没有书面许可的情况下测试生产 Firebase 项目
- 当你只需要提取 Firebase 配置而不进行测试时（使用手动 grep/strings 代替）
- 非 Android 目标（iOS、Web 应用）- 此技能仅针对 APK
- 当目标应用不使用 Firebase 时

## 拒绝的常见理由

在审计时，拒绝这些导致遗漏或淡化发现结果的常见理由：

- **"数据库是只读的，所以没问题"** - 数据泄露仍然是一个关键发现；PII、API 密钥和业务数据可能会泄露
- **"只是匿名认证，不是真实账户"** - 匿名令牌绕过 `auth != null` 规则，可以访问“仅限认证用户”的资源
- **"API 密钥本来就是公开的"** - 公开的 API 密钥并不能证明数据库规则开放或认证限制被禁用
- **"里面没有敏感数据"** - 你无法知道未来会存储什么数据；不安全的规则是漏洞，无论当前内容如何
- **"这是一个内部应用"** - APK 可以从任何设备中提取；“内部”应用不受逆向工程保护
- **"我们会在发布前修复"** - 记录发现的问题；发布前的漏洞经常被发布到生产环境

## 参考资料

有关详细的漏洞模式和利用技术，请参阅：
- [漏洞模式参考](references/vulnerabilities.md)

## 如何使用此技能

用户将提供一个 APK 文件或目录：`$ARGUMENTS`

## 工作流程

### 第一步：验证输入

首先，验证目标是否存在：

```bash
ls -la $ARGUMENTS
```

如果 `$ARGUMENTS` 为空，请要求用户提供 APK 路径。

### 第二步：运行扫描器

在目标上执行捆绑的扫描器脚本：

```bash
{baseDir}/scanner.sh $ARGUMENTS
```

扫描器将：
1. 使用 apktool 反编译 APK
2. 从所有来源提取 Firebase 配置（google-services.json、XML 资源、assets、smali 代码、DEX 字符串）
3. 测试认证端点（公开注册、匿名认证、邮箱枚举）
4. 测试实时数据库（未经身份验证的读写、认证绕过）
5. 测试 Firestore（文档访问、集合枚举）
6. 测试存储桶（列出、写入访问）
7. 测试 Cloud Functions（枚举、未经身份验证的访问）
8. 测试 Remote Config 暴露
9. 以文本和 JSON 格式生成报告

### 第三步：展示结果

扫描器完成后，读取并总结结果：

```bash
cat firebase_scan_*/scan_report.txt
```

以以下格式展示发现的问题：

---

## 扫描摘要

| 指标 | 值 |
|------|----|
| 扫描的 APK 数量 | X |
| 漏洞数量 | X |
| 扫描失败数量 | X |
| 无 Firebase 配置数量 | X |
| 总问题数量 | X |

从 `failed_apks` 和 `untested_apks` 中获取这些数据。这两个组都没有被测试——失败的 APK 没有被反编译，而 Firebase 配置为空的 APK 没有可探测的端点——因此它们既不漏洞也不干净。明确报告它们，而不是让它们消失在“0 个漏洞”的行中，并说明 `NO_CONFIG` 结果的含义：应用可能根本不使用 Firebase，或者其配置可能被混淆或打包，超出了扫描器提取的范围。

## 提取的配置

| 字段 | 值 |
|------|----|
| 项目 ID | `extracted_value` |
| 数据库 URL | `extracted_value` |
| 存储桶 | `extracted_value` |
| API 密钥 | `extracted_value` |
| 认证域 | `extracted_value` |

## 发现的漏洞

| 严重性 | 描述 | 证据 |
|--------|------|------|
| CRITICAL | 描述 | 简要证据 |
| HIGH | 描述 | 简要证据 |

## 修复建议

为每个发现的漏洞提供具体的修复方法。参考 [漏洞模式](references/vulnerabilities.md) 获取安全代码示例。

---

## 手动测试（如果扫描器失败）

如果扫描器脚本不可用或失败，执行手动提取和测试：

### 提取配置

在反编译的 APK 中搜索 Firebase 配置：

```bash
# 反编译
apktool d -f -o ./decompiled $ARGUMENTS

# 查找 google-services.json
find ./decompiled -name "google-services.json"

# 搜索 XML 资源
grep -r "firebaseio.com\|appspot.com\|AIza" ./decompiled/res/

# 搜索 assets（混合应用）
grep -r "firebaseio.com\|AIza" ./decompiled/assets/
```

### 测试端点

一旦你获得了 `PROJECT_ID` 和 `API_KEY`：

**认证：**
```bash
# 测试公开注册
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","returnSecureToken":true}' \
  "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=API_KEY"

# 测试匿名认证
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"returnSecureToken":true}' \
  "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=API_KEY"
```

**数据库：**
```bash
# 实时数据库读取
curl -s "https://PROJECT_ID.firebaseio.com/.json"

# Firestore 读取
curl -s "https://firestore.googleapis.com/v1/projects/PROJECT_ID/databases/(default)/documents"
```

**存储：**
```bash
# 列出存储桶
curl -s "https://firebasestorage.googleapis.com/v0/b/PROJECT_ID.appspot.com/o"
```

**Remote Config：**
```bash
curl -s -H "x-goog-api-key: API_KEY" \
  "https://firebaseremoteconfig.googleapis.com/v1/projects/PROJECT_ID/remoteConfig"
```

## 严重性分类

- **CRITICAL**：未经身份验证的数据库读写、存储写入、私有应用上的公开注册
- **HIGH**：匿名认证启用、存储桶列出、集合枚举
- **MEDIUM**：邮箱枚举、可访问的 Cloud Functions、Remote Config 暴露
- **LOW**：无敏感数据的信息披露

## 重要指南

1. **需要授权** - 仅扫描你有权限测试的 APK
2. **清理测试数据** - 扫描器会自动删除它创建的测试条目
3. **保存令牌** - 如果匿名认证成功，使用该令牌进行认证绕过测试
4. **测试所有区域** - Cloud Functions 可能部署到 us-central1、europe-west1、asia-east1 等
5. **多个实例** - 某些应用使用多个 Firebase 项目；测试所有发现的配置
