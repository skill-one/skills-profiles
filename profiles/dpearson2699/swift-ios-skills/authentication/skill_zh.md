# 身份验证

使用 AuthenticationServices 框架在 iOS 上实现身份验证流程，包括使用 Apple 登录、密钥凭证、OAuth/第三方网页认证、密码自动填充和生物识别重新验证。

## 内容

- [使用 Apple 登录](#使用-apple-登录)
- [凭证处理](#凭证处理)
- [凭证状态检查](#凭证状态检查)
- [令牌验证](#令牌验证)
- [现有账户设置流程](#现有账户设置流程)
- [密钥凭证](#密钥凭证)
- [ASWebAuthenticationSession (OAuth)](#aswebauthenticationsession-oauth)
- [密码自动填充凭证](#密码自动填充凭证)
- [生物识别认证](#生物识别认证)
- [安全边界](#安全边界)
- [SwiftUI SignInWithAppleButton](#swiftui-signinwithapplebutton)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 使用 Apple 登录

在使用这些 API 之前，需要在 Xcode 中添加“使用 Apple 登录”功能。

### UIKit: ASAuthorizationController 设置

```swift
import AuthenticationServices

final class LoginViewController: UIViewController {
    func startSignInWithApple() {
        let provider = ASAuthorizationAppleIDProvider()
        let request = provider.createRequest()
        request.requestedScopes = [.fullName, .email]

        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.delegate = self
        controller.presentationContextProvider = self
        controller.performRequests()
    }
}

extension LoginViewController: ASAuthorizationControllerPresentationContextProviding {
    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        view.window!
    }
}
```

### Delegate: 处理成功和失败

```swift
extension LoginViewController: ASAuthorizationControllerDelegate {
    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        guard let credential = authorization.credential
            as? ASAuthorizationAppleIDCredential else { return }

        let userID = credential.user  // 稳定、唯一、按团队标识符
        let email = credential.email  // 第一次授权后为 nil
        let fullName = credential.fullName  // 第一次授权后为 nil
        let identityToken = credential.identityToken  // 用于服务器验证的 JWT
        let authCode = credential.authorizationCode  // 用于服务器交换的短期代码

        // 将 userID 保存到 Keychain 以进行凭证状态检查
        // 参考参考资料/keychain-biometric.md 了解 Keychain 模式
        saveUserID(userID)

        // 将 identityToken 和 authCode 发送到您的服务器
        authenticateWithServer(identityToken: identityToken, authCode: authCode)
    }

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithError error: any Error
    ) {
        switch (error as? ASAuthorizationError)?.code {
        case .canceled, .notInteractive:
            break
        case .failed:
            showError("认证失败")
        default:
            showError("认证失败: \(error.localizedDescription)")
        }
    }
}
```

## 凭证处理

| 凭证数据 | 需要的处理 |
|---|---|
| `user` | 为凭证状态检查持久化此稳定、按团队标识符。 |
| `email`, `fullName` | 这些可选值仅在第一次授权时出现；立即缓存它们。 |
| `identityToken`, `authorizationCode` | 将它们发送到服务器进行验证或交换；不要将它们作为客户端证明信任。 |

仅将 `realUserStatus` 视为欺诈预防信号，而不是认证证明。

## 凭证状态检查

在每次应用启动时检查凭证状态。用户可以随时通过设置 > Apple 账户 > 登录和安全撤销访问权限。

```swift
func checkCredentialState() {
    let provider = ASAuthorizationAppleIDProvider()
    guard let userID = loadSavedUserID() else {
        showLoginScreen()
        return
    }

    provider.getCredentialState(forUserID: userID) { state, _ in
        DispatchQueue.main.async {
            switch state {
            case .authorized:
                proceedToMainApp()
            case .revoked:
                // 用户撤销 -- 注销并清除本地数据
                signOut()
                showLoginScreen()
            case .notFound:
                showLoginScreen()
            case .transferred:
                // 应用转移到新团队 -- 迁移用户标识符
                migrateUser()
            @unknown default:
                showLoginScreen()
            }
        }
    }
}
```

### 凭证撤销通知

```swift
NotificationCenter.default.addObserver(
    forName: ASAuthorizationAppleIDProvider.credentialRevokedNotification,
    object: nil,
    queue: .main
) { _ in
    // 立即注销
    AuthManager.shared.signOut()
}
```

## 令牌验证

`identityToken` 是一个 JWT。将其发送到您的服务器进行验证 -- 不要单独在客户端信任它。

在服务器端，使用 Apple 的公钥在 `https://appleid.apple.com/auth/keys`（JWKS）验证 JWT。验证：`iss` 是 `https://appleid.apple.com`，`aud` 与您的 Bundle ID 匹配，`exp` 尚未过期。在服务器上交换短期授权代码，并将生成的应用会话令牌存储在 Keychain 中。

## 现有账户设置流程

在显示登录屏幕之前，启动时静默检查现有的使用 Apple 登录和密码凭证：

```swift
func performExistingAccountSetupFlows() {
    let appleIDRequest = ASAuthorizationAppleIDProvider().createRequest()
    let passwordRequest = ASAuthorizationPasswordProvider().createRequest()

    let controller = ASAuthorizationController(
        authorizationRequests: [appleIDRequest, passwordRequest]
    )
    controller.delegate = self
    controller.presentationContextProvider = self
    controller.performRequests(
        options: .preferImmediatelyAvailableCredentials
    )
}
```

在 `viewDidAppear` 或应用启动时调用此方法。如果未找到现有凭证，委托将收到 `.notInteractive` 错误 -- 沉默处理并显示您的正常登录 UI。

## 密钥凭证

仅当依赖方域配置了 `webcredentials:` 关联域和 AASA 条目时使用密钥凭证。注册和断言都需要一个新鲜的服务器挑战、一个 `ASAuthorizationPlatformPublicKeyCredentialProvider`、一个具有活动呈现锚点的授权控制器，以及在发出会话之前进行服务器端验证。

加载 [参考资料/passkeys.md](references/passkeys.md) 了解规范注册、断言、结果处理、自动填充辅助和物理安全密钥流程。

## ASWebAuthenticationSession (OAuth)

使用 `ASWebAuthenticationSession` 进行 OAuth 和第三方认证（Google、GitHub 等）。永远不要使用 `WKWebView` 进行认证流程。

```swift
import AuthenticationServices

final class OAuthController: NSObject, ASWebAuthenticationPresentationContextProviding {
    private weak var presentationAnchor: ASPresentationAnchor?

    init(presentationAnchor: ASPresentationAnchor) {
        self.presentationAnchor = presentationAnchor
    }

    func startOAuthFlow() {
        let authURL = URL(string:
            "https://provider.com/oauth/authorize?client_id=YOUR_ID&redirect_uri=myapp://callback&response_type=code"
        )!
        let session = ASWebAuthenticationSession(
            url: authURL, callback: .customScheme("myapp")
        ) { callbackURL, error in
            guard let callbackURL, error == nil,
                  let code = URLComponents(url: callbackURL, resolvingAgainstBaseURL: false)?
                      .queryItems?.first(where: { $0.name == "code" })?.value else { return }
            Task { await self.exchangeCodeForTokens(code) }
        }
        session.presentationContextProvider = self
        session.prefersEphemeralWebBrowserSession = true  // 无共享 cookie
        session.start()
    }

    func presentationAnchor(for session: ASWebAuthenticationSession) -> ASPresentationAnchor {
        guard let presentationAnchor else {
            fatalError("ASWebAuthenticationSession 需要活动窗口")
        }
        return presentationAnchor
    }
}
```

在 SwiftUI 中，使用 `@Environment(\.webAuthenticationSession)` 并调用
`authenticate(using:callback:preferredBrowserSession:additionalHeaderFields:)`
使用 `.customScheme("myapp")` 或 `.https(host:path:)`；仅在提供方流程应避免共享浏览器 cookie 时才使用 `.ephemeral`。

## 密码自动填充凭证

使用 `ASAuthorizationPasswordProvider` 与使用 Apple 登录一起提供，使用 [现有账户设置流程](#现有账户设置流程) 中的单个控制器。在该控制器委托中处理 `ASPasswordCredential`。

为自动填充设置文本字段的 `textContentType`：

```swift
usernameField.textContentType = .username
passwordField.textContentType = .password
```

## 生物识别认证

使用 LocalAuthentication 的 `LAContext` 在显示账户设置或启动敏感操作之前进行本地重新验证。不要将返回的 `Bool` 视为解锁存储密钥的证明；使用 Keychain 访问控制来保护密钥。参见 [参考资料/keychain-biometric.md](references/keychain-biometric.md) 了解规范 `LAContext`、回退、`SecAccessControl` 和 `.biometryCurrentSet` 模式。

**必须**：在 Info.plist 中添加 `NSFaceIDUsageDescription`。缺少此键会在 Face ID 设备上导致崩溃。

## 安全边界

此技能拥有面向用户的账户认证：使用 Apple 登录、密钥凭证、密码自动填充、ASAuthorizationController、OAuth 会话呈现、凭证状态和本地生物识别重新验证。将深层安全工作路由到 `swift-security`：Keychain 架构/迁移、CryptoKit、Secure Enclave、证书锁定/信任、Keychain 共享、存储硬化以及 OWASP MASVS/MASTG。在此处仅保留存储最小值：令牌和密钥属于 Keychain；`LAContext.evaluatePolicy` 单独不能释放受保护的密钥。

## SwiftUI SignInWithAppleButton

在登录界面是 SwiftUI 时，在 SwiftUI 视图中使用 `SignInWithAppleButton`。请求 `.fullName` 和 `.email`，将成功结果转换为 `ASAuthorizationAppleIDCredential`，并将其传递给共享的 [令牌验证](#令牌验证) 流程。使用 `.signInWithAppleButtonStyle(...)` 进行样式设置。

## 常见错误

- 假设保存的本地会话意味着 Apple ID 凭证仍然有效。在启动时检查凭证状态并处理撤销通知。
- 在尝试现有账户设置流程之前显示完整的登录屏幕。将 `.notInteractive` 视为“本地无凭证”的正常路径。
- 强制解包 `email` 或 `fullName`。在第一次授权时缓存它们，并稍后处理 `nil`。
- 创建没有呈现上下文提供者的 `ASAuthorizationController`。认证 UI 需要活动的呈现锚点。
- 将 identity tokens、授权代码、访问令牌、密码或密钥凭证服务器状态存储在 `UserDefaults`、文件或 Core Data 中。将密钥存储在 Keychain 中，并将依赖方密钥凭证验证保留在服务器端。
- 为依赖方域添加密钥凭证请求而没有 `webcredentials:` 关联域，或尝试使用原生密钥凭证用于无关的网站。
- 将认证工作扩展到 CryptoKit、Secure Enclave、证书锁定或 OWASP MASVS。将这些路由到 `swift-security`。

## 审查清单

- [ ] Xcode 项目中添加了“使用 Apple 登录”功能
- [ ] 实现了 `ASAuthorizationControllerPresentationContextProviding`
- [ ] 每次应用启动时检查凭证状态 (`getCredentialState(forUserID:completion:)`)
- [ ] 注册了 `credentialRevokedNotification`；处理了注销
- [ ] 在第一次授权时缓存 `email` 和 `fullName`（不假设之后可用）
- [ ] 将 `identityToken` 发送到服务器进行验证，不仅信任客户端
- [ ] 令牌存储在 Keychain 中，不在 UserDefaults 或文件中
- [ ] 调用了 `performExistingAccountSetupFlows` 在显示登录界面之前
- [ ] 处理了错误情况：`.canceled`、`.failed`、`.notInteractive`
- [ ] Info.plist 中有 `NSFaceIDUsageDescription` 用于生物识别认证
- [ ] 使用 `ASWebAuthenticationSession` 进行 OAuth（不使用 `WKWebView`)
- [ ] 适当设置 `prefersEphemeralWebBrowserSession` 进行 OAuth
- [ ] 用户名/密码字段设置了 `textContentType` 以进行自动填充
- [ ] 依赖方密钥凭证配置了 `webcredentials:` 关联域
- [ ] 密钥凭证注册/断言挑战来自服务器并在服务器端验证
- [ ] 深层 Keychain、CryptoKit、Secure Enclave、证书锁定/信任和 MASVS 工作路由到 `swift-security`

## 参考资料

- Keychain & 生物识别模式：[参考资料/keychain-biometric.md](references/keychain-biometric.md)
- 密钥凭证模式：[参考资料/passkeys.md](references/passkeys.md)
- [AuthenticationServices](https://sosumi.ai/documentation/authenticationservices)
- [ASAuthorizationAppleIDProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationappleidprovider)
- [ASAuthorizationAppleIDCredential](https://sosumi.ai/documentation/authenticationservices/asauthorizationappleidcredential)
- [ASAuthorizationController](https://sosumi.ai/documentation/authenticationservices/asauthorizationcontroller)
- [ASWebAuthenticationSession](https://sosumi.ai/documentation/authenticationservices/aswebauthenticationsession)
- [支持密钥凭证](https://sosumi.ai/documentation/authenticationservices/supporting-passkeys)
- [ASAuthorizationPlatformPublicKeyCredentialProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationplatformpublickeycredentialprovider)
- [ASAuthorizationPasswordProvider](https://sosumi.ai/documentation/authenticationservices/asauthorizationpasswordprovider)
- [SignInWithAppleButton](https://sosumi.ai/documentation/authenticationservices/signinwithapplebutton)
- [使用 Apple 登录实现用户认证](https://sosumi.ai/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
