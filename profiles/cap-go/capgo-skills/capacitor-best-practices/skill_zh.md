# Capacitor 最佳实践

构建生产级 Capacitor 应用的全面指南。

## 何时使用此技能

- 设置新的 Capacitor 项目
- 审查 Capacitor 应用架构
- 优化应用性能
- 实施安全措施
- 准备应用商店提交

## 项目结构

### 推荐的目录布局

```text
my-app/
├── src/                      # Web 应用源代码
├── android/                  # Android 原生项目
├── ios/                      # iOS 原生项目
├── capacitor.config.ts       # Capacitor 配置
├── package.json
└── tsconfig.json
```

### 配置最佳实践

**capacitor.config.ts** (正确):
```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.company.app',
  appName: 'My App',
  webDir: 'dist',
  server: {
    // 仅开发环境启用
    ...(process.env.NODE_ENV === 'development' && {
      url: 'http://localhost:5173',
      cleartext: true,
    }),
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: false,
    },
  },
};

export default config;
```

**capacitor.config.json** (避免):
```json
{
  "server": {
    "url": "http://localhost:5173",
    "cleartext": true
  }
}
```
*永远不要将开发服务器 URL 提交到生产环境*

## 插件使用

### 关键：始终使用最新版 Capacitor

保持 Capacitor 核心包同步：

```bash
npm install @capacitor/core@latest @capacitor/cli@latest
npm install @capacitor/ios@latest @capacitor/android@latest
npx cap sync
```

### 插件安装模式

**正确**:
```bash
# 1. 安装包
npm install @capgo/capacitor-native-biometric

# 2. 同步原生项目
npx cap sync

# 3. 对于 iOS：安装 pod (或使用 SPM)
cd ios/App && pod install && cd ../..
```

**错误**:
```bash
# 缺少同步步骤
npm install @capgo/capacitor-native-biometric
# 应用崩溃，因为原生代码未链接
```

### 插件初始化

**正确** - 使用前检查可用性:
```typescript
import { NativeBiometric, BiometryType } from '@capgo/capacitor-native-biometric';

async function authenticate() {
  const { isAvailable, biometryType } = await NativeBiometric.isAvailable();

  if (!isAvailable) {
    // 回退到密码
    return authenticateWithPassword();
  }

  try {
    await NativeBiometric.verifyIdentity({
      reason: '验证以访问您的账户',
      title: '生物识别登录',
    });
    return true;
  } catch (error) {
    // 用户取消或生物识别失败
    return false;
  }
}
```

**错误** - 未进行可用性检查:
```typescript
// 如果生物识别不可用，将崩溃
await NativeBiometric.verifyIdentity({ reason: '登录' });
```

## 性能优化

### 关键：懒加载插件

**正确** - 动态导入:
```typescript
// 仅在需要时加载
async function scanDocument() {
  const { DocumentScanner } = await import('@capgo/capacitor-document-scanner');
  return DocumentScanner.scanDocument();
}
```

**错误** - 启动时导入所有内容:
```typescript
// 增加初始包体积
import { DocumentScanner } from '@capgo/capacitor-document-scanner';
import { NativeBiometric } from '@capgo/capacitor-native-biometric';
import { Camera } from '@capacitor/camera';
// ... 还有 20 个插件
```

### 高优先级：优化 WebView 性能

**正确** - 使用硬件加速:
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<application
    android:hardwareAccelerated="true"
    android:largeHeap="true">
```

```xml
<!-- ios/App/App/Info.plist -->
<key>UIViewGroupOpacity</key>
<false/>
```

### 高优先级：最小化桥接调用

**正确** - 批量操作:
```typescript
// 使用单个调用与批量数据
await Storage.set({
  key: 'userData',
  value: JSON.stringify({ name, email, preferences }),
});
```

**错误** - 多个桥接调用:
```typescript
// 每次调用都会跨越 JS-原生桥接
await Storage.set({ key: 'name', value: name });
await Storage.set({ key: 'email', value: email });
await Storage.set({ key: 'preferences', value: JSON.stringify(preferences) });
```

### 中优先级：图像优化

**正确**:
```typescript
import { Camera, CameraResultType } from '@capacitor/camera';

const photo = await Camera.getPhoto({
  quality: 80,           // 不是 100
  width: 1024,           // 合理的最大值
  resultType: CameraResultType.Uri,  // 不是 Base64 用于大图像
  correctOrientation: true,
});
```

**错误**:
```typescript
const photo = await Camera.getPhoto({
  quality: 100,
  resultType: CameraResultType.Base64,  // 内存密集型
  // 没有大小限制
});
```

## 安全最佳实践

### 关键：安全存储

**正确** - 使用安全存储敏感数据:
```typescript
import { NativeBiometric } from '@capgo/capacitor-native-biometric';

// 安全存储凭证
await NativeBiometric.setCredentials({
  username: 'user@example.com',
  password: 'secret',
  server: 'api.myapp.com',
});

// 使用生物识别验证检索
const credentials = await NativeBiometric.getCredentials({
  server: 'api.myapp.com',
});
```

**错误** - 普通存储:
```typescript
import { Preferences } from '@capacitor/preferences';

// 永远不要在普通偏好设置中存储敏感数据
await Preferences.set({
  key: 'password',
  value: 'secret',  // 存储为明文!
});
```

### 关键：证书绑定

对于处理敏感数据的生产品应用:

```typescript
// capacitor.config.ts
const config: CapacitorConfig = {
  plugins: {
    CapacitorHttp: {
      enabled: true,
    },
  },
  server: {
    // 生产环境中禁用明文
    cleartext: false,
  },
};
```

### 高优先级：Root/Jailbreak 检测

```typescript
import { IsRoot } from '@capgo/capacitor-is-root';

async function checkDeviceSecurity() {
  const { isRooted } = await IsRoot.isRooted();

  if (isRooted) {
    // 显示警告或限制功能
    showSecurityWarning('设备似乎被 Root/Jailbreak');
  }
}
```

### 高优先级：iOS 应用跟踪透明度

```typescript
import { AppTrackingTransparency } from '@capgo/capacitor-app-tracking-transparency';

async function requestTracking() {
  const { status } = await AppTrackingTransparency.requestPermission();

  if (status === 'authorized') {
    // 启用分析
  }
}
```

## 错误处理

### 关键：始终处理插件错误

**正确**:
```typescript
import { Camera, CameraResultType } from '@capacitor/camera';

async function takePhoto() {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      resultType: CameraResultType.Uri,
    });
    return image;
  } catch (error) {
    if (error.message === 'User cancelled photos app') {
      // 用户取消，不是错误
      return null;
    }
    if (error.message.includes('permission')) {
      // 权限被拒绝
      showPermissionDialog();
      return null;
    }
    // 预期之外的错误
    console.error('Camera error:', error);
    throw error;
  }
}
```

**错误**:
```typescript
// 没有错误处理
const image = await Camera.getPhoto({ quality: 90 });
```

## 实时更新

### 使用 Capacitor Updater

```typescript
import { CapacitorUpdater } from '@capgo/capacitor-updater';

// 应用就绪时通知
CapacitorUpdater.notifyAppReady();

// 监听更新
CapacitorUpdater.addListener('updateAvailable', async (update) => {
  // 在后台下载
  const bundle = await CapacitorUpdater.download({
    url: update.url,
    version: update.version,
  });

  // 在下次应用启动时应用
  await CapacitorUpdater.set(bundle);
});
```

### 更新策略

**正确** - 后台下载，重启时应用:
```typescript
// 静默下载
const bundle = await CapacitorUpdater.download({ url, version });

// 用户继续使用应用...

// 在他们关闭/重新打开时应用
await CapacitorUpdater.set(bundle);
```

**错误** - 打断用户:
```typescript
// 不要在用户活跃时强制重新加载
const bundle = await CapacitorUpdater.download({ url, version });
await CapacitorUpdater.reload();  // 打断用户
```

## 原生项目管理

### iOS：使用 Swift Package Manager (SPM)

现代方法 - 优先使用 SPM 而不是 CocoaPods:

```ruby
# Podfile - 移除插件 pod，使用 SPM 代替
target 'App' do
  capacitor_pods
  # 通过 SPM 在 Xcode 中添加插件依赖
end
```

### Android：Gradle 配置

```groovy
// android/app/build.gradle
android {
    defaultConfig {
        minSdkVersion 22
        targetSdkVersion 34
    }

    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

## 测试

### 插件模拟

```typescript
// Web 测试模拟
jest.mock('@capgo/capacitor-native-biometric', () => ({
  NativeBiometric: {
    isAvailable: jest.fn().mockResolvedValue({
      isAvailable: true,
      biometryType: 'touchId',
    }),
    verifyIdentity: jest.fn().mockResolvedValue({}),
  },
}));
```

### 平台检测

```typescript
import { Capacitor } from '@capacitor/core';

if (Capacitor.isNativePlatform()) {
  // 原生特定代码
} else {
  // Web 回退
}

// 或检查特定平台
if (Capacitor.getPlatform() === 'ios') {
  // iOS 特定代码
}
```

## 部署检查清单

- [ ] 从配置中移除开发服务器 URL
- [ ] 为 Android 发布构建启用 ProGuard
- [ ] 设置适当的 iOS 部署目标
- [ ] 在真实设备上测试，而不仅仅是模拟器
- [ ] 验证所有权限都已声明
- [ ] 在差网络条件下测试
- [ ] 验证深度链接工作正常
- [ ] 测试应用后台/前台
- [ ] 验证推送通知工作正常
- [ ] 测试生物识别认证边缘情况

## 资源

- Capacitor 文档: https://capacitorjs.com/docs
- Capgo 文档: https://capgo.app/docs
- Ionic 框架: https://ionicframework.com/docs
