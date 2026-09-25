# Android Kotlin 技能

---

## 项目结构

```
project/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/com/example/app/
│   │   │   │   ├── data/               # 数据层
│   │   │   │   │   ├── local/          # Room 数据库
│   │   │   │   │   ├── remote/         # Retrofit/Ktor 服务
│   │   │   │   │   └── repository/     # 仓库实现
│   │   │   │   ├── di/                 # Hilt 模块
│   │   │   │   ├── domain/             # 业务逻辑
│   │   │   │   │   ├── model/          # 领域模型
│   │   │   │   │   ├── repository/     # 仓库接口
│   │   │   │   │   └── usecase/        # 用例
│   │   │   │   ├── ui/                 # 表示层
│   │   │   │   │   ├── feature/        # 功能界面
│   │   │   │   │   │   ├── FeatureScreen.kt      # Compose UI
│   │   │   │   │   │   └── FeatureViewModel.kt
│   │   │   │   │   ├── components/     # 可重用的 Compose 组件
│   │   │   │   │   └── theme/          # Material 主题
│   │   │   │   └── App.kt              # 应用类
│   │   │   ├── res/
│   │   │   └── AndroidManifest.xml
│   │   ├── test/                       # 单元测试
│   │   └── androidTest/                # 仪器测试
│   └── build.gradle.kts
├── build.gradle.kts                    # 项目级构建文件
├── gradle.properties
├── settings.gradle.kts
└── CLAUDE.md
```

---

## Gradle 配置 (Kotlin DSL)

### 应用级 build.gradle.kts
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.example.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.app"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }
}

dependencies {
    // Compose BOM
    val composeBom = platform("androidx.compose:compose-bom:2024.01.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-compiler:2.50")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.9")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("app.cash.turbine:turbine:1.0.0")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

---

## Kotlin 协程 & Flow

### 带有 StateFlow 的 ViewModel
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    private val userId: String = checkNotNull(savedStateHandle["userId"])

    init {
        loadUser()
    }

    fun loadUser() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            getUserUseCase(userId)
                .catch { e ->
                    _uiState.update {
                        it.copy(isLoading = false, error = e.message)
                    }
                }
                .collect { user ->
                    _uiState.update {
                        it.copy(isLoading = false, user = user, error = null)
                    }
                }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### 带有 Flow 的仓库
```kotlin
interface UserRepository {
    fun getUser(userId: String): Flow<User>
    fun observeUsers(): Flow<List<User>>
    suspend fun saveUser(user: User)
}

class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {

    override fun getUser(userId: String): Flow<User> = flow {
        // 首先发射缓存数据
        dao.getUserById(userId)?.let { emit(it) }

        // 从网络获取并更新缓存
        val remoteUser = api.getUser(userId)
        dao.insert(remoteUser)
        emit(remoteUser)
    }.flowOn(dispatcher)

    override fun observeUsers(): Flow<List<User>> =
        dao.observeAllUsers().flowOn(dispatcher)

    override suspend fun saveUser(user: User) = withContext(dispatcher) {
        api.saveUser(user)
        dao.insert(user)
    }
}
```

---

## Jetpack Compose

### 带有 ViewModel 的界面
```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    UserScreenContent(
        uiState = uiState,
        onRefresh = viewModel::loadUser,
        onErrorDismiss = viewModel::clearError,
        onNavigateBack = onNavigateBack
    )
}

@Composable
private fun UserScreenContent(
    uiState: UserUiState,
    onRefresh: () -> Unit,
    onErrorDismiss: () -> Unit,
    onNavigateBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("用户资料") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                uiState.user != null -> {
                    UserContent(user = uiState.user)
                }
            }

            uiState.error?.let { error ->
                Snackbar(
                    modifier = Modifier.align(Alignment.BottomCenter),
                    action = {
                        TextButton(onClick = onErrorDismiss) {
                            Text("关闭")
                        }
                    }
                ) {
                    Text(error)
                }
            }
        }
    }
}
```

---

## 用于状态的密封类

### 结果包装器
```kotlin
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val exception: Throwable) : Result<Nothing>
    data object Loading : Result<Nothing>
}

fun <T> Result<T>.getOrNull(): T? = (this as? Result.Success)?.data

inline fun <T, R> Result<T>.map(transform: (T) -> R): Result<R> = when (this) {
    is Result.Success -> Result.Success(transform(data))
    is Result.Error -> this
    is Result.Loading -> this
}
```

---

## 使用 MockK & Turbine 进行测试

### ViewModel 测试
```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase: GetUserUseCase = mockk()
    private val savedStateHandle = SavedStateHandle(mapOf("userId" to "123"))

    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel(getUserUseCase, savedStateHandle)
    }

    @Test
    fun `loadUser success updates state with user`() = runTest {
        val user = User("123", "John Doe", "john@example.com")
        coEvery { getUserUseCase("123") } returns flowOf(user)

        viewModel.uiState.test {
            val initial = awaitItem()
            assertFalse(initial.isLoading)

            viewModel.loadUser()

            val loading = awaitItem()
            assertTrue(loading.isLoading)

            val success = awaitItem()
            assertFalse(success.isLoading)
            assertEquals(user, success.user)
        }
    }
}

class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

---

## GitHub Actions

```yaml
name: Android Kotlin CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: 设置 JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: 设置 Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: 运行 Detekt
        run: ./gradlew detekt

      - name: 运行 Ktlint
        run: ./gradlew ktlintCheck

      - name: 运行单元测试
        run: ./gradlew testDebugUnitTest

      - name: 构建调试 APK
        run: ./gradlew assembleDebug
```

---

## Lint 配置

### detekt.yml
```yaml
build:
  maxIssues: 0

complexity:
  LongMethod:
    threshold: 20
  LongParameterList:
    functionThreshold: 4
  TooManyFunctions:
    thresholdInFiles: 10

style:
  MaxLineLength:
    maxLineLength: 120
  WildcardImport:
    active: true

coroutines:
  GlobalCoroutineUsage:
    active: true
```

---

## Kotlin 反模式

- ❌ **在主线程上阻塞协程** - 不要在主线程上使用 `runBlocking`
- ❌ **使用 GlobalScope** - 使用结构化并发，使用 viewModelScope/lifecycleScope
- ❌ **在 init 中收集 flows** - 使用 `repeatOnLifecycle` 或 `collectAsStateWithLifecycle`
- ❌ **暴露可变状态** - 暴露 `StateFlow` 而不是 `MutableStateFlow`
- ❌ **在 flows 中不处理异常** - 总是使用 `catch` 操作符
- ❌ **用于可空的 lateinit** - 使用 `lazy` 或可空与 `?`
- ❌ **硬编码的调度器** - 注入调度器以提高可测试性
- ❌ **不使用密封类** - 对于有限状态集，优先使用密封类
- ❌ **Composables 中的副作用** - 使用 `LaunchedEffect`/`SideEffect`
- ❌ **不稳定的 Compose 参数** - 使用稳定/不可变类型或 `@Stable`
