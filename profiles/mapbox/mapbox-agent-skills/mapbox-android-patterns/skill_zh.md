# Mapbox Android 集成模式

官方集成模式，用于在 Android 上使用 Kotlin、Jetpack Compose 和 View 系统集成 Mapbox Maps SDK v11。

**在以下情况下使用此技能：**

- 安装和配置 Android Mapbox Maps SDK
- 向地图添加标记和注释
- 显示用户位置并使用相机跟踪
- 向地图添加自定义数据（GeoJSON）
- 使用地图样式、相机或用户交互
- 处理功能交互和点击

**官方资源：**

- [Android 地图指南](https://docs.mapbox.com/android/maps/guides/)
- [API 参考](https://docs.mapbox.com/android/maps/api-reference/)
- [示例应用](https://github.com/mapbox/mapbox-maps-android/tree/main/Examples)

---

## 安装与设置

### 要求

- Android SDK 21+
- Kotlin 或 Java
- Android Studio
- 免费的 Mapbox 账户

### 第 1 步：配置访问令牌

创建 `app/res/values/mapbox_access_token.xml`：

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <string name="mapbox_access_token" translatable="false"
        tools:ignore="UnusedResources">YOUR_MAPBOX_ACCESS_TOKEN</string>
</resources>
```

**获取您的令牌：** 登录 [mapbox.com](https://account.mapbox.com/access-tokens/)

### 第 1 步 b：互联网权限（必需）

地图需要网络访问。在 `AndroidManifest.xml` 中包含此内容 — 代理经常忽略它，并且只在稍后列出位置权限：

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 第 2 步：添加 Maven 仓库

在 `settings.gradle.kts` 中：

```kotlin
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://api.mapbox.com/downloads/v2/releases/maven")
        }
    }
}
```

### 第 3 步：添加依赖项

在模块 `build.gradle.kts` 中：

```kotlin
android {
    defaultConfig {
        minSdk = 21
    }
}

dependencies {
    implementation("com.mapbox.maps:android:11.18.1")
}
```

**对于 Jetpack Compose：**

```kotlin
dependencies {
    implementation("com.mapbox.maps:android:11.18.1")
    implementation("com.mapbox.extension:maps-compose:11.18.1")
}
```

---

## 地图初始化

### Jetpack Compose 模式

**基本地图：**

```kotlin
import androidx.compose.runtime.*
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.Modifier
import com.mapbox.maps.extension.compose.*
import com.mapbox.maps.Style
import com.mapbox.geojson.Point

@Composable
fun MapScreen() {
    MapboxMap(
        modifier = Modifier.fillMaxSize()
    ) {
        // 通过 MapEffect 初始化相机（默认加载 Style.STANDARD）
        MapEffect(Unit) { mapView ->
            // 设置初始相机位置
            mapView.mapboxMap.setCamera(
                CameraOptions.Builder()
                    .center(Point.fromLngLat(-122.4194, 37.7749))
                    .zoom(12.0)
                    .build()
            )
        }
    }
}
```

**带装饰：**

```kotlin
MapboxMap(
    modifier = Modifier.fillMaxSize(),
    scaleBar = {
        ScaleBar(
            enabled = true,
            position = Alignment.BottomStart
        )
    },
    compass = {
        Compass(enabled = true)
    }
) {
    // 默认加载 Style.STANDARD
}
```

### View 系统模式

**布局 XML (activity_map.xml)：**

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <com.mapbox.maps.MapView
        android:id="@+id/mapView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

**Activity：**

```kotlin
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.mapbox.maps.MapView
import com.mapbox.maps.Style
import com.mapbox.geojson.Point

class MapActivity : AppCompatActivity() {
    private lateinit var mapView: MapView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_map)

        mapView = findViewById(R.id.mapView)

        mapView.mapboxMap.setCamera(
            CameraOptions.Builder()
                .center(Point.fromLngLat(-122.4194, 37.7749))
                .zoom(12.0)
                .build()
        )

        mapView.mapboxMap.loadStyle(Style.STANDARD)
    }

    override fun onStart() {
        super.onStart()
        mapView.onStart()
    }

    override fun onStop() {
        super.onStop()
        mapView.onStop()
    }

    override fun onDestroy() {
        super.onDestroy()
        mapView.onDestroy()
    }
}
```

---

## 添加标记（点注释）

点注释是最常见的在地图上标记位置的方式。

**Jetpack Compose：**

```kotlin
MapboxMap(modifier = Modifier.fillMaxSize()) {
    MapEffect(Unit) { mapView ->
        // 首先加载样式
        mapView.mapboxMap.loadStyle(Style.STANDARD)

        // 创建注释管理器并添加标记
        val annotationManager = mapView.annotations.createPointAnnotationManager()
        val pointAnnotation = PointAnnotationOptions()
            .withPoint(Point.fromLngLat(-122.4194, 37.7749))
            .withIconImage("custom-marker")
        annotationManager.create(pointAnnotation)
    }
}

// 注意：Compose 没有声明式的 PointAnnotation 组件
// 标记必须通过 MapEffect 逐条添加
```

**View 系统：**

```kotlin
// 创建注释管理器（一次性，用于更新）
val pointAnnotationManager = mapView.annotations.createPointAnnotationManager()

// 创建标记
val pointAnnotation = PointAnnotationOptions()
    .withPoint(Point.fromLngLat(-122.4194, 37.7749))
    .withIconImage("custom-marker")

pointAnnotationManager.create(pointAnnotation)
```

**多个标记：**

```kotlin
val locations = listOf(
    Point.fromLngLat(-122.4194, 37.7749),
    Point.fromLngLat(-122.4094, 37.7849),
    Point.fromLngLat(-122.4294, 37.7649)
)

val annotations = locations.map { point ->
    PointAnnotationOptions()
        .withPoint(point)
        .withIconImage("marker")
}

pointAnnotationManager.create(annotations)
```

---

## 显示用户位置（显示）

**第 1 步：在 AndroidManifest.xml 中添加权限：**

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

**第 2 步：请求权限并显示位置：**

```kotlin
// 首先请求权限（使用 ActivityResultContracts）

// 显示位置指示器
mapView.location.updateSettings {
    enabled = true
    puckBearingEnabled = true
}
```

---

## 性能最佳实践

### 重用注释管理器

```kotlin
// 不要重复创建新的管理器
// val manager = mapView.annotations.createPointAnnotationManager() // 每次调用

// 一次性创建，重用
val pointAnnotationManager = mapView.annotations.createPointAnnotationManager()

fun updateMarkers() {
    pointAnnotationManager.deleteAll()
    pointAnnotationManager.create(markers)
}
```

### 批量注释更新

```kotlin
// 一次性创建所有
pointAnnotationManager.create(allAnnotations)

// 不要在循环中逐个创建
```

### 生命周期管理

```kotlin
// 始终调用生命周期方法
override fun onStart() {
    super.onStart()
    mapView.onStart()
}

override fun onStop() {
    super.onStop()
    mapView.onStop()
}

override fun onDestroy() {
    super.onDestroy()
    mapView.onDestroy()
}
```

### 使用标准样式

```kotlin
// 标准样式经过优化并推荐使用
Style.STANDARD

// 仅在特定用例需要时使用其他样式
Style.STANDARD_SATELLITE // 卫星影像
```

---

## 故障排除

### 地图未显示

**检查：**

1. `mapbox_access_token.xml` 中的令牌
2. 令牌有效（在 mapbox.com 上测试）
3. Maven 仓库配置正确
4. 依赖项添加正确
5. manifest 中的互联网权限

### 样式未加载

```kotlin
mapView.mapboxMap.subscribeStyleLoaded { _ ->
    Log.d("Map", "Style loaded successfully")
    // 在此处添加图层和源
}
```

### 性能问题

- 使用 `Style.STANDARD`（推荐且优化）
- 限制视口内的可见注释
- 重用注释管理器
- 避免频繁重新加载样式
- 调用生命周期方法（onStart, onStop, onDestroy）
- 批量更新注释

---

## 参考文件

在需要特定主题的详细模式时加载这些参考：

- **`references/compose.md`** -- Jetpack Compose：依赖项、令牌设置、MapboxMap、带点击的注释、GeoJSON、MapEffect
- **`references/annotations.md`** -- 圆形、折线和多边形注释模式
- **`references/location-tracking.md`** -- 相机跟随用户位置 + 获取当前位置一次
- **`references/custom-data.md`** -- GeoJSON 源和图层：线、多边形、点、更新/删除
- **`references/camera-styles.md`** -- 相机控制（设置、动画、适应）+ 地图样式（内置和自定义）
- **`references/interactions.md`** -- 功能集交互、自定义图层点击、长按、手势

---

## 其他资源

- [Android 地图指南](https://docs.mapbox.com/android/maps/guides/)
- [API 参考](https://docs.mapbox.com/android/maps/api/11.18.1/)
- [交互指南](https://docs.mapbox.com/android/maps/guides/user-interaction/interactions/)
- [Jetpack Compose 指南](https://docs.mapbox.com/android/maps/guides/using-jetpack-compose/)
- [示例应用](https://github.com/mapbox/mapbox-maps-android/tree/main/Examples)
- [迁移指南 (v10 -> v11)](https://docs.mapbox.com/android/maps/guides/migrate-to-v11/)
