# 技能：移动 SSL 锁定绕过 — 专家攻击手册

> **AI 加载指令**：针对移动平台的专家级 SSL 锁定绕过技术。涵盖 Android 和 iOS 绕过方法（Frida、Objection、Xposed、SSL 杀手开关），特定框架的绕过（Flutter、React Native、Xamarin），以及非标准锁定实现的故障排除。基础模型会遗漏特定框架的钩点以及多层锁定配置。

## 0. 相关路由

在深入之前，请考虑加载：

- [android-pentesting-tricks](../android-pentesting-tricks/SKILL.md) 用于更广泛的 Android 测试（超越 SSL 绕过）
- [ios-pentesting-tricks](../ios-pentesting-tricks/SKILL.md) 用于更广泛的 iOS 测试（超越 SSL 绕过）
- [api-sec](../api-sec/SKILL.md) 一旦拦截流量，用于 API 级别的测试

---

## 1. SSL 锁定类型

| 锁定类型 | 锁定内容 | 弹性 | 常见于 |
|---|---|---|---|
| 证书锁定 | 精确的叶证书（DER/PEM） | 低（证书轮换时会失效） | 传统应用 |
| 公钥锁定 | Subject Public Key Info | 中等（如果密钥不变，证书更新后仍有效） | 现代应用 |
| SPKI 哈希锁定 | SHA-256 的 SPKI | 中等（与公钥相同） | OkHttp、AFNetworking |
| CA 锁定 | 中间或根 CA 证书 | 高（该 CA 的任何证书都有效） | 企业应用 |
| 多重锁定（备用锁定） | 主要 + 备用锁定 | 高（备用锁定） | HPKP 兼容应用 |

### 锁定工作原理

```
TLS 握手
│
├── 服务器呈现证书链
│
├── 标准验证（系统信任存储）
│   └── 通过？继续 : 连接失败
│
└── 锁定验证（应用级检查）
    ├── 提取服务器证书/公钥/SPKI 哈希
    ├── 与嵌入的锁定比较
    └── 匹配找到？→ 允许 : → 拒绝连接
```

---

## 2. Android 绕过方法

### 2.1 Frida 通用 SSL 绕过

```javascript
// 钩点 TrustManager、OkHttp、Volley、Retrofit、Conscrypt
Java.perform(function() {

    // ── TrustManagerImpl (Android 系统) ──
    try {
        var TMI = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        TMI.verifyChain.implementation = function() {
            console.log('[绕过] TrustManagerImpl.verifyChain');
            return arguments[0]; // 返回未修改的链
        };
    } catch(e) {}

    // ── X509TrustManager (自定义实现) ──
    var TrustManager = Java.registerClass({
        name: 'com.bypass.TrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function() {},
            checkServerTrusted: function() {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;',
        '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom')
        .implementation = function(km, tm, sr) {
        console.log('[绕过] SSLContext.init');
        this.init(km, [TrustManager.$new()], sr);
    };

    // ── OkHttp3 CertificatePinner ──
    try {
        var CP = Java.use('okhttp3.CertificatePinner');
        CP.check.overload('java.lang.String', 'java.util.List').implementation = function() {
            console.log('[绕过] OkHttp3 CertificatePinner.check: ' + arguments[0]);
        };
        // check$okhttp 变体（OkHttp 4.x）
        try { CP['check$okhttp'].implementation = function() {}; } catch(e) {}
    } catch(e) {}

    // ── Retrofit / OkHttp 拦截器 ──
    try {
        var OkHttpClient = Java.use('okhttp3.OkHttpClient$Builder');
        OkHttpClient.certificatePinner.implementation = function(pinner) {
            console.log('[绕过] OkHttpClient.Builder.certificatePinner');
            return this; // 返回不包含 pinner 的构建器
        };
    } catch(e) {}

    // ── Volley (HurlStack) ──
    try {
        var HurlStack = Java.use('com.android.volley.toolbox.HurlStack');
        HurlStack.createConnection.implementation = function(url) {
            console.log('[绕过] Volley HurlStack: ' + url);
            var conn = this.createConnection(url);
            // 移除主机名验证器
            conn.setHostnameVerifier(Java.use(
                'javax.net.ssl.HttpsURLConnection').getDefaultHostnameVerifier());
            return conn;
        };
    } catch(e) {}

    // ── Conscrypt / BoringSSL (现代 Android) ──
    try {
        var Conscrypt = Java.use('org.conscrypt.ConscryptFileDescriptorSocket');
        Conscrypt.verifyCertificateChain.implementation = function() {
            console.log('[绕过] Conscrypt verifyCertificateChain');
        };
    } catch(e) {}

    // ── Apache HttpClient (传统) ──
    try {
        var AbstractVerifier = Java.use('org.apache.http.conn.ssl.AbstractVerifier');
        AbstractVerifier.verify.overload('java.lang.String', '[Ljava.lang.String;',
            '[Ljava.lang.String;', 'boolean').implementation = function() {
            console.log('[绕过] Apache AbstractVerifier');
        };
    } catch(e) {}

    // ── HostnameVerifier ──
    try {
        var HV = Java.use('javax.net.ssl.HttpsURLConnection');
        HV.setDefaultHostnameVerifier.implementation = function(v) {
            console.log('[绕过] 忽略自定义 HostnameVerifier');
        };
    } catch(e) {}

    console.log('[+] Android 通用 SSL 绕过加载');
});
```

### 2.2 Objection（单命令）

```bash
objection -g com.target.app explore --startup-command "android sslpinning disable"
```

### 2.3 网络安全配置（调试覆盖）

```xml
<!-- AndroidManifest.xml: android:networkSecurityConfig="@xml/network_security_config" -->

<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <base-config>
    <trust-anchors>
      <certificates src="system" />
      <certificates src="user" />     <!-- 信任用户安装的 CA -->
    </trust-anchors>
  </base-config>
</network-security-config>
```

工作流程：反编译 APK → 添加/修改配置 → 重新打包 → 重新签名 → 安装。

```bash
apktool d target.apk -o target_dir
# 编辑 res/xml/network_security_config.xml
# 如果缺少引用，在 AndroidManifest.xml 中添加
apktool b target_dir -o target_patched.apk
zipalign -v 4 target_patched.apk target_aligned.apk
apksigner sign --ks my-key.keystore target_aligned.apk
adb install target_aligned.apk
```

### 2.4 Xposed / LSPosed 模块

| 模块 | 方法 | 范围 | 是否需要 Root |
|---|---|---|---|
| JustTrustMe | 钩点 TrustManager + OkHttp | 每个应用 | 是（Xposed） |
| SSLUnpinning | 钩点证书验证 | 每个应用 | 是（LSPosed） |
| TrustMeAlready | 全局 TrustManager 绕过 | 系统范围 | 是（LSPosed） |

### 2.5 Magisk + 系统CA 安装

```bash
# 将代理 CA 作为系统证书安装（Android 7+ 需要此操作以实现系统级信任）
# 方法 1：MagiskTrustUserCerts 模块
# 通过 Magisk overlay 将用户 CA 移动到 /system/etc/security/cacerts/

# 方法 2：手动（需要 Root）
adb push burp_ca.pem /sdcard/
adb shell
su
mount -o remount,rw /system
cp /sdcard/burp_ca.pem /system/etc/security/cacerts/9a5ba575.0  # 哈希命名的
chmod 644 /system/etc/security/cacerts/9a5ba575.0
mount -o remount,ro /system

# 获取正确的哈希文件名：
openssl x509 -inform PEM -subject_hash_old -in burp_ca.pem | head -1
# 输出：9a5ba575 → 文件名是 9a5ba575.0
```

### 2.6 手动反编译 → 修补 → 重新打包

```bash
# 步骤 1：反编译
jadx -d decompiled/ target.apk

# 步骤 2：查找锁定代码
grep -r "CertificatePinner\|X509TrustManager\|checkServerTrusted\|ssl" decompiled/

# 步骤 3：识别锁定实现并修补
# 使用 smali 编辑进行精确控制：
apktool d target.apk
# 编辑 smali 文件以 NOP 锁定检查
# 查找 invoke-virtual {checkServerTrusted} 并替换为 return-void

# 步骤 4：重新打包并签名
apktool b target_dir -o patched.apk
apksigner sign --ks debug.keystore patched.apk
```

---

## 3. iOS 绕过方法

### 3.1 Frida（SecTrust 钩点）

```javascript
// 钩点核心 iOS SSL 验证函数
var SecTrustEvaluateWithError = Module.findExportByName('Security', 'SecTrustEvaluateWithError');
Interceptor.attach(SecTrustEvaluateWithError, {
    onLeave: function(retval) {
        retval.replace(ptr(1));
    }
});

var SecTrustEvaluate = Module.findExportByName('Security', 'SecTrustEvaluate');
Interceptor.attach(SecTrustEvaluate, {
    onLeave: function(retval) {
        retval.replace(ptr(0));
    }
});

// 钩点 SSLHandshake（较低级别）
var SSLHandshake = Module.findExportByName('Security', 'SSLHandshake');
if (SSLHandshake) {
    Interceptor.attach(SSLHandshake, {
        onLeave: function(retval) {
            if (retval.toInt32() === -9807) { // errSSLXCertChainInvalid
                retval.replace(ptr(0));
            }
        }
    });
}

// 钩点 NSURLSession 委托方法
try {
    var cls = ObjC.classes.NSURLSession;
    // 钩点 URLSession:didReceiveChallenge:completionHandler: 在委托上
    ObjC.enumerateLoadedClasses({
        onMatch: function(name) {
            try {
                var methods = ObjC.classes[name].$ownMethods;
                for (var i = 0; i < methods.length; i++) {
                    if (methods[i].indexOf('didReceiveChallenge') !== -1 &&
                        methods[i].indexOf('completionHandler') !== -1) {
                        console.log('[SSL] 找到委托: ' + name + ' ' + methods[i]);
                    }
                }
            } catch(e) {}
        },
        onComplete: function() {}
    });
} catch(e) {}
```

### 3.2 Objection（单命令）

```bash
objection -g com.target.app explore --startup-command "ios sslpinning disable"
```

### 3.3 SSL 杀手开关 2（越狱调整）

```bash
# 通过 Cydia/Sileo 安装
# 包名：com.nablac0d3.sslkillswitch2
# 通过设置开关在系统范围或每个应用中禁用 SSL 锁定

# 钩点：
# - SecTrustEvaluate
# - SSLHandshake
# - SSLSetSessionOption
# - tls_helper_create_peer_trust
```

### 3.4 库特定钩点

| 库 | iOS 钩点 | Frida 方法 |
|---|---|---|
| AFNetworking | `AFSecurityPolicy.evaluateServerTrust:forDomain:` | 返回 YES |
| Alamofire | `ServerTrustManager.evaluate(_:forHost:)` | 跳过评估 |
| TrustKit | `TSKPinningValidator verifyPublicKeyPin:` | 返回成功 |
| NSURLSession | `URLSession:didReceiveChallenge:completionHandler:` | 调用 completionHandler 并使用 .useCredential |

### 3.5 手动二进制修补

```bash
# 在二进制中查找锁定函数
strings decrypted_binary | grep -i "pin\|cert\|trust"
# 反汇编并找到验证函数
# 将比较/分支指令替换为 NOP 或无条件通过

# LLDB 运行时修改
lldb -n TargetApp
(lldb) breakpoint set -n "SecTrustEvaluateWithError"
(lldb) breakpoint command add 1
> thread return 1
> continue
> DONE
```

---

## 4. 框架特定绕过

### 4.1 Flutter

Flutter 使用 Dart 的 `dart:io` 库，底层使用 BoringSSL。标准的 Java/ObjC 层钩点不起作用。

```javascript
// Flutter SSL 绕过 — 必须直接钩点 BoringSSL
// 查找 ssl_crypto_x509_session_verify_cert_chain 在 libflutter.so 中
var libflutter = Process.findModuleByName('libflutter.so');  // Android
// var libflutter = Process.findModuleByName('Flutter');       // iOS

// 钩点 ssl_verify_peer_cert（BoringSSL 函数）
// 签名因 Flutter 版本而异 — 使用模式扫描
var pattern = 'FF C3 ..';  // 示例模式，因版本而异
var matches = Memory.scan(libflutter.base, libflutter.size, pattern, {
    onMatch: function(address, size) {
        console.log('[Flutter] 潜在验证函数在: ' + address);
        Interceptor.attach(address, {
            onLeave: function(retval) {
                retval.replace(ptr(0));  // SSL_VERIFY_OK
            }
        });
    },
    onComplete: function() {}
});

// 替代方案：使用 reflutter 工具进行自动修补
// reflutter target.apk
// 这会直接修补 Flutter 引擎中的 BoringSSL
```

**reflutter 工具**（推荐用于 Flutter 应用）：

```bash
pip install reflutter
reflutter target.apk
# 输出修补的 APK，将流量重定向到您的代理
# 还禁用了 BoringSSL 引擎中的 SSL 验证
```

### 4.2 React Native

React Native 使用平台网络：Android 上使用 OkHttp，iOS 上使用 NSURLSession。

| 平台 | 网络栈 | 绕过方法 |
|---|---|---|
| Android | OkHttp3 | 标准 OkHttp CertificatePinner 钩点 |
| iOS | NSURLSession | 标准 SecTrust 钩点 |
| Android (Hermes) | 相同 OkHttp | 相同钩点，但 Hermes JIT 可能需要额外处理 |

```javascript
// React Native Android — 与 OkHttp 绕过相同
Java.perform(function() {
    try {
        var CP = Java.use('okhttp3.CertificatePinner');
        CP.check.overload('java.lang.String', 'java.util.List').implementation = function() {};
    } catch(e) { console.log('OkHttp3 未找到，尝试 okhttp2...'); }

    try {
        var CP2 = Java.use('com.squareup.okhttp.CertificatePinner');
        CP2.check.overload('java.lang.String', 'java.util.List').implementation = function() {};
    } catch(e) {}
});
```

### 4.3 Xamarin

```csharp
// Xamarin 锁定通常通过：
// ServicePointManager.ServerCertificateValidationCallback
// 或自定义 HttpClientHandler
```

```javascript
// Frida 绕过 Xamarin（Mono 运行时）
// 钩点 Mono 方法: System.Net.ServicePointManager.set_ServerCertificateValidationCallback
var mono_method = Module.findExportByName('libmonosgen-2.0.so',
    'mono_runtime_invoke');
// 更实用的方法：在 CIL 层钩点管理的回调
// 使用 Frida 的 Mono 桥或 objection 的内置 Xamarin 支持

// Objection 具有内置的 Xamarin 绕过：
// objection -g com.target.app explore
// > android sslpinning disable   (覆盖 Android 上的 Xamarin)
```

---

## 5. 证书透明度 & HPKP

| 技术 | 状态 | 对测试的影响 |
|---|---|---|
| 证书透明度 (CT) | 活跃，由浏览器强制执行 | 移动应用很少执行 CT；不是绕过障碍 |
| HPKP（HTTP 公钥锁定） | 已弃用（2018） | 传统应用可能仍会检查；从代理响应中移除标头 |
| Expect-CT 标头 | 已弃用（2024） | 对移动测试影响最小 |
| 移动应用中的 CT | 罕见 | 只有 Google 应用通过自定义 CT 检查执行 |

---

## 6. 故障排除

### 6.1 常见失败

| 症状 | 原因 | 解决方法 |
|---|---|---|
| 绕过脚本加载但流量仍失败 | 多重锁定层 | 钩点所有层：TrustManager + OkHttp + 自定义检查 |
| "客户端证书要求" | 互操作 TLS (mTLS) | 从应用包/密钥链中提取客户端证书，导入到代理 |
| 连接成功但无 HTTP 流量 | 非HTTP协议（MQTT、gRPC、WebSocket） | 使用 Wireshark 或协议特定代理 |
| 应用绕过后崩溃 | 检测到钩点的反篡改 | 首先绕过完整性检查，然后绕过 SSL |
| 代理 CA 未被信任 | Android 7+ 用户 CA 限制 | 将 CA 作为系统证书安装（Magisk模块） |
| Flutter 应用忽略钩点 | 未在原生层钩点 BoringSSL | 使用 reflutter 或原生 BoringSSL 钩点 |
| 证书链验证超时 | OCSP 拉取不匹配 | 禁用 OCSP 检查或模拟 OCSP 响应器 |

### 6.2 诊断步骤

```bash
# 验证代理 CA 是否正确安装
# Android:
adb shell "ls /system/etc/security/cacerts/ | grep $(openssl x509 -subject_hash_old -in ca.pem | head -1)"

# iOS: 设置 → 通用 → 关于 → 证书信任设置

# 检查目标应用是否实际使用 SSL（而不是纯 HTTP）
# Wireshark 过滤器: tcp.port == 443 and ip.addr == <device_ip>

# 检查 Frida 是否钩点正确的进程
frida-ps -U | grep target

# 调试钩点的详细 Frida 输出
frida -U -f com.target.app -l bypass.js --debug
```

---

## 7. SSL 锁定绕过决策树

```
需要拦截移动应用 HTTPS 流量
│
├── 平台?
│   ├── Android ↓
│   │   ├── Rooted 设备可用?
│   │   │   ├── 是 → Frida 通用绕过 (§2.1) [首选]
│   │   │   │   ├── 工作? → 完成
│   │   │   │   └── 失败? → 添加 Conscrypt + Volley 钩点
│   │   │   ├── 仍然失败? → LSPosed + TrustMeAlready (§2.4)
│   │   │   └── 仍然失败? → 安装 CA 作为系统证书 (§2.5)
│   │   └── 无 Root?
│   │       ├── 调试构建? → Network Security Config (§2.3)
│   │       └── 发布构建? → 反编译 + 修补 + 重新打包 (§2.6)
│   │
│   └── iOS ↓
│       ├── 越狱设备可用?
│       │   ├── 是 → Objection ios sslpinning disable (§3.2) [首选]
│       │   │   ├── 工作? → 完成
│       │   │   └── 失败? → Frida SecTrust 钩点 (§3.1)
│       │   ├── 仍然失败? → SSL 杀手开关 2 (§3.3)
│       │   └── 仍然失败? → 库特定钩点 (§3.4)
│       └── 无越狱?
│           ├── 使用 Frida 模块重新签名 → 运行 Frida 钩点
│           └── 二进制修补 → 侧载 (§3.5)
│
├── 框架特定应用?
│   ├── Flutter → reflutter 工具或原生 BoringSSL 钩点 (§4.1)
│   ├── React Native → 标准平台钩点 (§4.2)
│   └── Xamarin → Objection 或 Mono 运行时钩点 (§4.3)
│
├── 绕过工作但仍有问题?
│   ├── 需要客户端证书? → 提取 + 导入到代理 (§6.1)
│   ├── 非HTTP协议? → 协议特定工具 (§6.1)
│   └── 应用崩溃? → 首先修复反篡改 (§6.1)
│
└── 所有方法都失败?
    ├── 在网络级别分析流量（Wireshark/tcpdump）
    ├── 检查是否存在自定义专有协议
    └── 考虑 iptables + 透明代理方法
```

---

## 8. 代理设置快速参考

| 代理工具 | 最佳用途 | SSL 绕过集成 |
|---|---|---|
| Burp Suite | 完整 HTTP 分析 | 将 CA 导入设备 |
| mitmproxy | 脚本化拦截 | `mitmproxy --set confdir=~/.mitmproxy` |
| Charles Proxy | macOS 本地，易于设置 | 内置 CA 安装 |
| Proxyman | macOS/iOS 本地 | 直接支持 iOS 设备 |
| HTTP Toolkit | 快速 Android 设置 | 自动化 CA + Frida 绕过 |

```bash
# Android 代理设置
adb shell settings put global http_proxy <host_ip>:8080

# 移除代理
adb shell settings put global http_proxy :0

# iOS 代理: 设置 → Wi-Fi → 配置代理 → 手动
```
