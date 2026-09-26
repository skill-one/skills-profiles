# CMake

## 目的

指导代理使用现代（目标优先）的 CMake 进行 C/C++ 项目：离源构建、依赖管理、生成器选择以及与 CI 和 IDE 的集成。

## 触发条件

- "如何为我的项目编写 CMakeLists.txt？"
- "如何使用 CMake 添加外部库？"
- "CMake 找不到我的包 / 库"
- "如何在 CMake 中启用调试器？"
- "如何使用 CMake 进行交叉编译？"
- "如何使用 CMake 预设？"

## 工作流程

### 1. 现代 CMake 原则

- 定义目标，而不是变量。使用 `target_*` 命令。
- 使用 `PUBLIC`/`PRIVATE`/`INTERFACE` 控制属性传播。
- 不要使用 `include_directories()` 或 `link_libraries()`（旧版）。
- 最小 CMake 版本：`cmake_minimum_required(VERSION 3.20)` 以支持大多数功能。

### 2. 最小化项目

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyApp VERSION 1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(myapp
    src/main.c
    src/utils.c
)

target_include_directories(myapp PRIVATE include)
target_compile_options(myapp PRIVATE -Wall -Wextra)
```

### 3. 静态 / 动态库

```cmake
# 静态库
add_library(mylib STATIC lib/foo.c lib/bar.c)
target_include_directories(mylib
    PUBLIC  include      # 消费者获取此包含路径
    PRIVATE src          # 只有 mylib 本身可见
)

# 动态库
add_library(myshared SHARED lib/foo.c)
set_target_properties(myshared PROPERTIES
    VERSION   1.0.0
    SOVERSION 1
)

# 将库链接到可执行文件
add_executable(myapp src/main.c)
target_link_libraries(myapp PRIVATE mylib)
```

### 4. 配置和构建

```bash
# 离源构建（始终这样做）
cmake -S . -B build
cmake --build build

# 使用生成器
cmake -S . -B build -G Ninja
cmake --build build -- -j$(nproc)

# 调试构建
cmake -S . -B build-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build-debug

# 发布
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release

# 安装
cmake --install build --prefix /usr/local
```

构建类型：`Debug`、`Release`、`RelWithDebInfo`、`MinSizeRel`。

### 5. 外部依赖

#### find_package（系统安装的库）

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)

find_package(Threads REQUIRED)
target_link_libraries(myapp PRIVATE Threads::Threads)

find_package(ZLIB REQUIRED)
target_link_libraries(myapp PRIVATE ZLIB::ZLIB)
```

#### FetchContent（下载并构建依赖）

```cmake
include(FetchContent)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)
FetchContent_MakeAvailable(googletest)

add_executable(mytest test/test_foo.cpp)
target_link_libraries(mytest PRIVATE GTest::gtest_main mylib)
```

#### pkg-config 回退

```cmake
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBFOO REQUIRED libfoo>=1.2)
target_link_libraries(myapp PRIVATE ${LIBFOO_LIBRARIES})
target_include_directories(myapp PRIVATE ${LIBFOO_INCLUDE_DIRS})
```

### 6. 按配置编译选项

```cmake
target_compile_options(myapp PRIVATE
    $<$<CONFIG:Debug>:-g -Og -fsanitize=address>
    $<$<CONFIG:Release>:-O2 -DNDEBUG>
    $<$<CXX_COMPILER_ID:GNU>:-fanalyzer>
    $<$<CXX_COMPILER_ID:Clang>:-Weverything>
)

target_link_options(myapp PRIVATE
    $<$<CONFIG:Debug>:-fsanitize=address>
)
```

生成器表达式：`$<condition:value>` 在构建时评估。

### 7. 启用调试器

```cmake
option(ENABLE_ASAN "启用 AddressSanitizer" OFF)

if(ENABLE_ASAN)
    target_compile_options(myapp PRIVATE -fsanitize=address -fno-omit-frame-pointer -g -O1)
    target_link_options(myapp PRIVATE -fsanitize=address)
endif()
```

构建：`cmake -DENABLE_ASAN=ON -S . -B build-asan && cmake --build build-asan`

### 8. 交叉编译工具链文件

```cmake
# toolchain-aarch64.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_SYSROOT /opt/aarch64-sysroot)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

```bash
cmake -S . -B build-arm -DCMAKE_TOOLCHAIN_FILE=toolchain-aarch64.cmake
```

### 9. CMake 预设（CMake 3.20+）

```json
{
  "version": 6,
  "configurePresets": [
    {
      "name": "release",
      "displayName": "Release",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/release",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "debug",
      "displayName": "Debug",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/debug",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "ENABLE_ASAN": "ON"
      }
    }
  ],
  "buildPresets": [
    { "name": "release", "configurePreset": "release" },
    { "name": "debug",   "configurePreset": "debug" }
  ]
}
```

```bash
cmake --preset release
cmake --build --preset release
```

### 10. 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|---------|
| `Could not find package Foo` | 包未安装或前缀错误 | 安装开发包；设置 `CMAKE_PREFIX_PATH` |
| `No CMAKE_CXX_COMPILER` | 未找到 C++ 编译器 | 安装 g++/clang++；检查 PATH |
| `target_link_libraries called with wrong number of arguments` | 缺少 `PUBLIC/PRIVATE/INTERFACE` | 添加关键词 |
| `Cannot find source file` | 拼写错误或相对路径错误 | 检查相对于 `CMakeLists.txt` 的路径 |
| `generator expression` error | `$<>` 语法错误 | 检查 CMake 文档中的表达式名称 |

完整的 CMakeLists.txt 模板，请参阅 [references/templates.md](references/templates.md)。

## 相关技能

- 使用 `skills/build-systems/ninja` 查看 Ninja 生成器详细信息
- 使用 `skills/build-systems/make` 查看 Make 生成器
- 使用 `skills/compilers/cross-gcc` 查看交叉编译工具链设置
- 使用 `skills/runtimes/sanitizers` 查看调试器集成详细信息
