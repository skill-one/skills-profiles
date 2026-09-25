## 1. 项目场景评估

在开始开发之前，评估当前项目状态：

| 场景 | 特征 | 方法 |
|------|------|------|
| **空目录** | 不存在文件 | 需要完全初始化，包括 Gradle Wrapper |
| **存在 Gradle Wrapper** | 存在 `gradlew` 和 `gradle/wrapper/` | 直接使用 `./gradlew` 进行构建 |
| **Android Studio 项目** | 完整的项目结构，可能缺少 Wrapper | 检查 Wrapper，如有需要运行 `gradle wrapper` |
| **不完整项目** | 存在部分文件 | 检查缺失文件，完成配置 |

**关键原则**：
- 在编写业务逻辑之前，确保 `./gradlew assembleDebug` 成功
- 如果缺少 `gradle.properties`，请先创建它并配置 AndroidX

### 1.1 必要文件检查清单

```
MyApp/
├── gradle.properties          # 配置 AndroidX 和其他设置
├── settings.gradle.kts
├── build.gradle.kts           # 根级别
├── gradle/wrapper/
│   └── gradle-wrapper.properties
├── app/
│   ├── build.gradle.kts       # 模块级别
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/example/myapp/
│       │   └── MainActivity.kt
│       └── res/
│           ├── values/
│           │   ├── strings.xml
│           │   ├── colors.xml
│           │   └── themes.xml
│           └── mipmap-*/       # 应用图标
```

---

## 2. 项目配置

### 2.1 gradle.properties

```properties
# 必要配置
android.useAndroidX=true
android.enableJetifier=true

# 构建优化
org.gradle.parallel=true
kotlin.code.style=official

# JVM 内存设置（根据项目大小调整）
# 小型项目：2048m，中型：4096m，大型：8192m+
# org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
```

> **注意**：如果在构建过程中遇到 `OutOfMemoryError`，请增加 `-Xmx` 值。具有大量依赖的大型项目可能需要 8GB 或更多。

### 2.2 依赖声明标准

```kotlin
dependencies {
    // 使用 BOM 管理 Compose 版本
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    
    // Activity & ViewModel
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
}
```

### 2.3 构建变体与产品风味

产品风味允许您创建应用的不同版本（例如，免费/付费，开发/测试/生产）。

**在 app/build.gradle.kts 中的配置**：

```kotlin
android {
    // 定义风味维度
    flavorDimensions += "environment"
    
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            
            // 每个风味不同的配置值
            buildConfigField("String", "API_BASE_URL", "\"https://dev-api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
            
            // 不同的资源
            resValue("string", "app_name", "MyApp Dev")
        }
        
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"
            
            buildConfigField("String", "API_BASE_URL", "\"https://staging-api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
            resValue("string", "app_name", "MyApp Staging")
        }
        
        create("prod") {
            dimension = "environment"
            // 生产版本无后缀
            
            buildConfigField("String", "API_BASE_URL", "\"https://api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "false")
            resValue("string", "app_name", "MyApp")
        }
    }
    
    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
        }
        release {
            isDebuggable = false
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

**构建变体命名**：`{flavor}{BuildType}` → 例如，`devDebug`，`prodRelease`

**Gradle 构建命令**：

```bash
# 列出所有可用的构建变体
./gradlew tasks --group="build"

# 构建特定变体（风味 + 构建类型）
./gradlew assembleDevDebug        # 开发风味，Debug 构建
./gradlew assembleStagingDebug    # 测试风味，Debug 构建
./gradlew assembleProdRelease     # 生产风味，Release 构建

# 构建特定风味的所有变体
./gradlew assembleDev             # 所有开发变体（debug + release）
./gradlew assembleProd            # 所有生产变体

# 构建特定构建类型的所有变体
./gradlew assembleDebug           # 所有风味的 Debug 构建
./gradlew assembleRelease         # 所有风味的 Release 构建

# 将特定变体安装到设备
./gradlew installDevDebug
./gradlew installProdRelease

# 一次性构建并安装
./gradlew installDevDebug && adb shell am start -n com.example.myapp.dev/.MainActivity
```

**在代码中访问 BuildConfig**：

> **注意**：从 AGP 8.0 开始，`BuildConfig` 默认不再生成。您必须在 `build.gradle.kts` 中显式启用它：
> ```kotlin
> android {
>     buildFeatures {
>         buildConfig = true
>     }
> }
> ```

```kotlin
// 在代码中使用 build config 值
val apiUrl = BuildConfig.API_BASE_URL
val isLoggingEnabled = BuildConfig.ENABLE_LOGGING

if (BuildConfig.DEBUG) {
    // 仅 Debug 的代码
}
```

**风味特定源集**：

```
app/src/
├── main/           # 所有风味共享的代码
├── dev/            # 仅开发使用的代码和资源
│   ├── java/
│   └── res/
├── staging/        # 仅测试使用的代码和资源
├── prod/           # 仅生产使用的代码和资源
├── debug/          # Debug 构建类型的代码
└── release/        # Release 构建类型的代码
```

**多个风味维度**（例如，环境 + 层级）：

```kotlin
android {
    flavorDimensions += listOf("environment", "tier")
    
    productFlavors {
        create("dev") { dimension = "environment" }
        create("prod") { dimension = "environment" }
        
        create("free") { dimension = "tier" }
        create("paid") { dimension = "tier" }
    }
}
// 结果为：devFreeDebug, devPaidDebug, prodFreeRelease, 等
```

---

## 3. Kotlin 开发标准

### 3.1 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 类/接口 | PascalCase | `UserRepository`，`MainActivity` |
| 函数/变量 | camelCase | `getUserName()`，`isLoading` |
| 常量 | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| 包 | 小写 | `com.example.myapp` |
| Composable | PascalCase | `@Composable fun UserCard()` |

### 3.2 代码标准（重要）

**空安全**：
```kotlin
// ❌ 避免：非空断言 !!（可能崩溃）
val name = user!!.name

// ✅ 推荐：安全调用 + 默认值
val name = user?.name ?: "Unknown"

// ✅ 推荐：使用 let 处理
user?.let { processUser(it) }
```

**异常处理**：
```kotlin
// ❌ 避免：业务层中随机使用 try-catch 吞噬异常
fun loadData() {
    try {
        val data = api.fetch()
    } catch (e: Exception) {
        // 吞噬异常，难以调试
    }
}

// ✅ 推荐：异常向上传递，在适当层处理
suspend fun loadData(): Result<Data> {
    return try {
        Result.success(api.fetch())
    } catch (e: Exception) {
        Result.failure(e)  // 包装并返回，让调用者决定处理
    }
}

// ✅ 推荐：在 ViewModel 中统一处理
viewModelScope.launch {
    runCatching { repository.loadData() }
        .onSuccess { _uiState.value = UiState.Success(it) }
        .onFailure { _uiState.value = UiState.Error(it.message) }
}
```

### 3.3 线程 & 协程（关键）

**线程选择原则**：

| 操作类型 | 线程 | 描述 |
|----------|------|------|
| UI 更新 | `Dispatchers.Main` | 更新视图、状态、LiveData |
| 网络请求 | `Dispatchers.IO` | HTTP 调用、API 请求 |
| 文件 I/O | `Dispatchers.IO` | 本地存储、数据库操作 |
| 计算密集型 | `Dispatchers.Default` | JSON 解析、排序、加密 |

**正确用法**：
```kotlin
// 在 ViewModel 中
viewModelScope.launch {
    // 默认在主线程，可以更新 UI State
    _uiState.value = UiState.Loading
    
    // 切换到 IO 线程进行网络请求
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    
    // 自动返回主线程，更新 UI
    _uiState.value = UiState.Success(result)
}

// 在 Repository 中（挂起函数应该是主线程安全的）
suspend fun fetchData(): Data = withContext(Dispatchers.IO) {
    api.getData()
}
```

**常见错误**：
```kotlin
// ❌ 错误：在 IO 线程更新 UI
viewModelScope.launch(Dispatchers.IO) {
    val data = api.fetch()
    _uiState.value = data  // 可能崩溃或警告!
}

// ❌ 错误：在主线程执行耗时操作
viewModelScope.launch {
    val data = api.fetch()  // 阻塞主线程！ANR
}

// ✅ 正确：IO 线程获取数据，主线程更新
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) { api.fetch() }
    _uiState.value = data
}
```

### 3.4 可见性规则

```kotlin
// 默认是 public，需要时显式声明
class UserRepository {           // public
    private val cache = mutableMapOf<String, User>()  // 仅在类内部可见
    internal fun clearCache() {} // 仅在模块内部可见
}

// data class 属性默认是 public，跨模块使用时需小心
data class User(
    val id: String,       // public
    val name: String
)
```

### 3.5 常见语法陷阱

```kotlin
// ❌ 错误：访问未初始化的 lateinit
class MyViewModel : ViewModel() {
    lateinit var data: String
    fun process() = data.length  // 可能崩溃
}

// ✅ 正确：使用可空或默认值
class MyViewModel : ViewModel() {
    var data: String? = null
    fun process() = data?.length ?: 0
}

// ❌ 错误：在 lambda 中使用 return
list.forEach { item ->
    if (item.isEmpty()) return  // 返回外部函数！
}

// ✅ 正确：使用 return@forEach
list.forEach { item ->
    if (item.isEmpty()) return@forEach
}
```

### 3.6 服务器响应数据类字段必须为可空

```kotlin
// ❌ 错误：字段声明为非可空（服务器可能不返回它们）
data class UserResponse(
    val id: String = "",
    val name: String = "",
    val avatar: String = ""
)

// ✅ 正确：所有字段声明为可空
data class UserResponse(
    @SerializedName("id")
    val id: String? = null,
    @SerializedName("name")
    val name: String? = null,
    @SerializedName("avatar")
    val avatar: String? = null
)
```

### 3.7 生命周期资源管理

```kotlin
// ❌ 错误：仅添加 Observer，未移除
class MyView : View {
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        activity?.lifecycle?.addObserver(this)
    }
    // 内存泄漏!
}

// ✅ 正确：配对添加和移除
class MyView : View {
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        activity?.lifecycle?.addObserver(this)
    }

    override fun onDetachedFromWindow() {
        activity?.lifecycle?.removeObserver(this)
        super.onDetachedFromWindow()
    }
}
```

### 3.8 日志级别使用

```kotlin
import android.util.Log

// Info：正常流程中的关键检查点
Log.i(TAG, "loadData: started, userId = $userId")

// Warning：异常但可恢复的情况
Log.w(TAG, "loadData: cache miss, fallback to network")

// Error：失败/错误情况
Log.e(TAG, "loadData failed: ${error.message}")
```

| 级别 | 使用场景 |
|------|----------|
| `i` (Info) | 正常流程、方法入口、关键参数 |
| `w` (Warning) | 可恢复异常、回退处理、可空返回 |
| `e` (Error) | 请求失败、捕获的异常、不可恢复错误 |

---

## 4. Jetpack Compose 标准

### 4.1 @Composable 上下文规则

```kotlin
// ❌ 错误：从非 @Composable 函数调用 Composable
fun showError(message: String) {
    Text(message)  // 编译错误!
}

// ✅ 正确：标记为 @Composable
@Composable
fun ErrorMessage(message: String) {
    Text(message)
}

// ❌ 错误：在 LaunchedEffect 外部使用 suspend
@Composable
fun MyScreen() {
    val data = fetchData()  // 错误!
}

// ✅ 正确：使用 LaunchedEffect
@Composable
fun MyScreen() {
    var data by remember { mutableStateOf<Data?>(null) }
    LaunchedEffect(Unit) {
        data = fetchData()
    }
}
```

### 4.2 状态管理

```kotlin
// 基本状态
var count by remember { mutableStateOf(0) }

// 派生状态（避免冗余计算）
val isEven by remember { derivedStateOf { count % 2 == 0 } }

// 跨重组合状态（例如，滚动位置）
val scrollState = rememberScrollState()

// ViewModel 中的状态
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}
```

### 4.3 常见 Compose 错误

```kotlin
// ❌ 错误：在 Composable 中创建对象（每次重组时都会创建）
@Composable
fun MyScreen() {
    val viewModel = MyViewModel()  // 错误!
}

// ✅ 正确：使用 viewModel() 或 remember
@Composable
fun MyScreen(viewModel: MyViewModel = viewModel()) {
    // ...
}
```

---

## 5. 资源和图标

### 5.1 应用图标要求

必须提供多分辨率图标：

| 目录 | 尺寸 | 用途 |
|------|------|------|
| mipmap-mdpi | 48x48 | 基线 |
| mipmap-hdpi | 72x72 | 1.5x |
| mipmap-xhdpi | 96x96 | 2x |
| mipmap-xxhdpi | 144x144 | 3x |
| mipmap-xxxhdpi | 192x192 | 4x |

推荐：使用自适应图标（Android 8+）：

```xml
<!-- res/mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon>
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
```

### 5.2 资源命名约定

| 类型 | 前缀 | 示例 |
|------|------|------|
| 布局 | layout_ | `layout_main.xml` |
| 图片 | ic_, img_, bg_ | `ic_user.png` |
| 颜色 | color_ | `color_primary` |
| 字符串 | - | `app_name`, `btn_submit` |

### 5.3 避免使用 Android 保留名称（重要）

变量名、资源 ID、颜色、图标和 XML 元素**必须**不使用 Android 保留词或系统资源名称。使用保留名称会导致构建错误或资源冲突。

**常见的保留名称要避免**：

| 类别 | 保留名称（不要使用） |
|------|----------------------|
| 颜色 | `background`, `foreground`, `transparent`, `white`, `black` |
| 图标/可绘制资源 | `icon`, `logo`, `image`, `drawable` |
| 视图 | `view`, `text`, `button`, `layout`, `container` |
| 属性 | `id`, `name`, `type`, `style`, `theme`, `color` |
| 系统 | `app`, `android`, `content`, `data`, `action` |

**示例**：

```xml
<!-- ❌ 错误：使用保留名称 -->
<color name="background">#FFFFFF</color>
<color name="icon">#000000</color>

<!-- ✅ 正确：添加前缀或特定命名 -->
<color name="app_background">#FFFFFF</color>
<color name="icon_primary">#000000</color>
```

```kotlin
// ❌ 错误：变量名与系统冲突
val icon = R.drawable.my_icon
val background = Color.White

// ✅ 正确：使用描述性名称
val appIcon = R.drawable.my_icon
val screenBackground = Color.White
```

```xml
<!-- ❌ 错误：可绘制资源名称冲突 -->
<ImageView android:src="@drawable/icon" />

<!-- ✅ 正确：添加前缀 -->
<ImageView android:src="@drawable/ic_home" />
```

---

## 6. 构建错误诊断和修复

### 6.1 常见错误快速参考

| 错误关键词 | 原因 | 修复 |
|-------------|------|------|
| `Unresolved reference` | 缺少导入或未定义 | 检查导入，验证依赖 |
| `Type mismatch` | 类型不兼容 | 检查参数类型，添加转换 |
| `Cannot access` | 可见性问题 | 检查 public/private/internal |
| `@Composable invocations` | Composable 上下文错误 | 确保 caller 也是 @Composable |
| `Duplicate class` | 依赖冲突 | 使用 `./gradlew dependencies` 调查 |
| `AAPT: error` | 资源文件错误 | 检查 XML 语法和资源引用 |

### 6.2 修复最佳实践

1. **首先阅读完整的错误信息**：定位文件和行号
2. **检查最近的更改**：问题通常在最新修改中
3. **清理构建**：`./gradlew clean assembleDebug`
4. **检查依赖版本**：版本冲突是常见原因
5. **如有需要，刷新依赖**：清除缓存并重建

### 6.3 调试命令

```bash
# 清理和构建
./gradlew clean assembleDebug

# 查看依赖树（调查冲突）
./gradlew :app:dependencies

# 查看详细错误
./gradlew assembleDebug --stacktrace

# 刷新依赖
./gradlew --refresh-dependencies
```
