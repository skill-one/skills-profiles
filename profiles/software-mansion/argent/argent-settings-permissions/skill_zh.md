## 这个工具的用途

`settings-permissions` 直接编辑平台的权限存储 - iOS 模拟器的 TCC 数据库或 Android 的包管理器权限标志。它取代了测试设置过程中的手动 **设置 → 隐私** 操作：预先授权一个服务，以便应用程序永远不需要询问；提前拒绝它以测试拒绝路径，或重置它以便在下次启动时再次显示首次运行对话框。

它是一个 **测试设置 / 旁路** 工具，而不是一个通用的权限切换工具。更改权限的默认方式仍然是通过应用程序 - 这个工具只是应用程序无法触达的情况下的例外。

## 何时使用它 - 以及何时不要使用

按此顺序决定。第一个匹配的行将胜出。

| 情况                                                                                                        | 执行此操作                                                                                       | 原因                                                                                                                                                                     |
| ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 应用程序具有 **应用程序内控制** 权限（其自己的设置屏幕中的切换开关）                       | **在应用程序中点击它** (`describe` → `gesture-tap`) - 不要使用这个工具                     | 这是真实用户行为，并执行了您正在测试的流程。参见 `argent-device-interact`。                                                                            |
| 应用程序 **即将请求**（或刚刚请求）并且系统 **权限对话框显示在屏幕上**                    | **点击对话框** (`允许` / `不允许` / `仅在使用应用程序时允许`) - 不要使用这个工具 | 应用程序触发的提示是自然路径；回答它是用户会做的事情。`describe` 暴露了对话框按钮；如果它不存在，则回退到 `screenshot`。    |
| 您需要权限 **在应用程序运行之前已经授权/拒绝**，以便流程不会被对话框中断                 | **使用这个工具** (`grant` / `deny`) 在 `launch-app` 之前使用                                      | 应用程序无法预先设置自己的权限；真实用户会在设置中这样做。这是核心用例。 (`deny` 仅在 **iOS** 上抑制提示 - 见 Gotchas。 |
| 用户 **已经拒绝** 它并且您需要它 **再次启用**                                                      | **使用这个工具** (`grant`)                                                                   | iOS 永远不会在拒绝后重新显示对话框 - 唯一设备路径是设置应用程序。这个工具是快捷方式。                                                       |
| 您需要 **首次运行对话框再次出现**（测试提示本身，或重置脏状态）                 | **使用这个工具** (`reset`)                                                                   | 将权限恢复到“尚未询问”状态，以便应用程序在下次使用时提示。                                                                                               |
| 权限是 **目标平台此工具不支持** 的（参见支持表）                  | **不要使用这个工具**                                                                      | 它将返回一个“不支持”的错误。如果应用程序触发对话框，请使用应用程序对话框，或者导航到真实的设置应用程序。                                                   |
| 该设置不是 **以下 11 个运行时权限** 之一（例如 Wi-Fi、蜂窝数据、深色模式、VPN、专注模式） | **不要使用这个工具**                                                                      | 范围之外 - 驱动设置应用程序或应用程序自己的 UI。                                                                                                      |

**经验法则：** 如果人类测试人员可以在应用程序内部切换它，那就这样做。只有在人类原本会在 **系统设置应用程序** 中更改的情况下才使用 `settings-permissions`。

## 支持的权限和平台覆盖范围

| `permission`      | iOS 模拟器 (TCC 服务)                                                                                                                            | Android (`android.permission.*`)                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `camera`          | `camera` - 只有在目标模拟器的 **运行时** 模型它的情况下（由模拟器运行时而不是安装的 Xcode 决定；模拟器没有摄像头硬件） | `CAMERA`                                                                                                  |
| `microphone`      | `microphone`                                                                                                                                           | `RECORD_AUDIO`                                                                                            |
| `photos`          | `photos` + `photos-add`（仅添加访问是一个单独的 TCC 服务；`photos-add` 是尽力而为 - 检查 `applied` 以查看是否都更改了）         | `READ_MEDIA_IMAGES` + `READ_MEDIA_VIDEO` + `READ_MEDIA_VISUAL_USER_SELECTED` + `READ_EXTERNAL_STORAGE`    |
| `contacts`        | `contacts`                                                                                                                                             | `READ_CONTACTS` + `WRITE_CONTACTS`                                                                        |
| `notifications`   | **不支持** - 没有iOS等效项；改用应用程序的对话框                                                                                   | `POST_NOTIFICATIONS`                                                                                      |
| `calendar`        | `calendar`                                                                                                                                             | `READ_CALENDAR` + `WRITE_CALENDAR`                                                                        |
| `location`        | `location`                                                                                                                                             | `ACCESS_FINE_LOCATION` + `ACCESS_COARSE_LOCATION`                                                         |
| `location-always` | `location-always`                                                                                                                                      | `ACCESS_BACKGROUND_LOCATION`（一个 **授权** 也添加了精细 + 粗略 - 仅背景无法读取位置） |
| `media-library`   | `media-library`                                                                                                                                        | `READ_MEDIA_AUDIO` + `READ_EXTERNAL_STORAGE`                                                              |
| `motion`          | `motion`                                                                                                                                               | `ACTIVITY_RECOGNITION`                                                                                    |
| `reminders`       | `reminders`                                                                                                                                            | **不支持** - 没有Android运行时权限                                                           |

一个抽象权限可以映射到多个具体的 Android 权限；实际存在的权限取决于应用程序的清单和设备的 API 级别（例如 API 33+ 上的 `READ_MEDIA_*` 与其下的 `READ_EXTERNAL_STORAGE`）。

## 操作

- **`grant`** - 预先授权权限。需要 `bundleId`。
- **`deny`** - 拒绝它。需要 `bundleId`。用于测试应用程序的“权限被拒绝”路径。
- **`reset`** - 恢复到“尚未询问”状态，以便下次使用时对话框再次出现。始终按应用程序 (`bundleId` 需要)：
  - iOS：删除该应用程序的 TCC 行。没有全局重置（不需要 `bundleId`） - 在最近的 iOS 运行时中，它报告成功但保留现有的按应用程序授权不变，因此它会报告一个从未发生过的更改。
  - Android：撤销授权，然后尽力清除用户设置/用户固定标志（标志清除首先出现在 Android 13 / API 33；撤销决定成功）。低于 API 33（即 API 23-32，任何用户固定状态可以存在的位置）标志清除不可用，因此那里的 `reset` 撤销授权但无法清除“不再询问”（用户固定）状态 - 在那些较旧的设备上对话框可能会被抑制。
  
## 参数

```json
{
  "udid": "<UDID-or-serial>",
  "action": "grant",
  "permission": "camera",
  "bundleId": "com.example.app"
}
```

- `udid` - 从 `list-devices` 获取的目标（iOS 模拟器 UDID，或 Android 序列号）。参见 `argent-ios-simulator-setup` / `argent-android-emulator-setup` 获取一个。
- `action` - `grant` | `deny` | `reset`。
- `permission` - 上面 11 个名称之一。
- `bundleId` - iOS 包 ID 或 Android 包名。**每个操作都需要**。

## 平台行为

**仅限 iOS 模拟器。** 编辑模拟器的 TCC 存储始终按应用程序 (`bundleId` 需要)。在物理 iPhone 上没有主机侧 TCC 开关，因此此工具不适用于真实 iOS 设备。模拟器必须 **启动** 首先 (`boot-device`) - 否则该工具将因“当前状态：关机”错误而失败，并显示启动提示。

**Android 模拟器和物理设备。** 通过 adb 更改应用程序的 `android.permission.*` 运行时权限（对于 `reset`，尽力清除用户设置/用户固定标志 - 撤销决定成功；标志清除需要 Android 13 / API 33+）。要求：

- 应用程序必须 **安装** - 该工具首先探测包并如果缺失会明确报错（传输/超时失败会显示 adb 的真实原因，而不是虚假的“未安装”）。
- 应用程序必须在其清单中 **声明** 权限。包管理器会拒绝任何映射的权限，如果清单没有请求它们；这些会出现在结果的 `skipped` 列表中。如果 **至少一个** 映射的权限粘住，操作就会成功，并且只有在 **所有** 都被拒绝时才会出错。

## Gotchas

- **更改权限可能会导致正在运行的应用程序终止**（两个平台的系统行为）。最好在 `launch-app` 之前设置权限；如果您在应用程序运行时更改权限，请在之后使用 `restart-app`。
- **重置在两个平台上都是按应用程序** - 传递 `bundleId`；没有可靠的设备级重置。
- **Android 结果可能不完整。** `applied` 列出实际更改的内容；`skipped` 列出包管理器拒绝的映射权限（通常不在清单中，或受 API 级别限制）。两者结合起来告诉您发生了什么。
- **预启动 `deny` 仅在 iOS 上抑制提示。** 在 iOS 上，TCC 拒绝回答应用程序的请求，因此不会显示对话框。在 Android 上，`deny` 清除授权但设置没有“用户固定”标志，因此应用程序的下一个请求仍然显示系统对话框 - 在那里预启动 `deny` 测试的是撤销的状态，而不是被抑制的提示。
- **iOS 上的 `camera`** 可能被不模拟该服务的模拟器 **运行时** 拒绝（它由模拟器运行时决定，而不是安装的 Xcode；运行时可以接受 `camera`，即使平台的自己的服务列表中不包含它）。拒绝会显示为通用 CoreSimulator 错误，因此 `camera` 失败（除非是关闭模拟器的案例，该案例会显示启动提示）会以关于运行时支持服务的提示报告。
- **`grant location` 需要先安装应用程序（iOS）。** 位置授权不存储在 TCC 中，并且不会应用于包 ID，直到应用程序存在，因此预安装 `grant location` / `grant location-always` 记录为空。在 **本地** 模拟器上，该工具检查安装状态并明确报错而不是报告虚假成功；在 **远程** 模拟器上，它无法探测安装状态，因此那里的预安装授权会报告成功而记录为空 - 请确保在远程授权位置之前安装应用程序。（TCC 支持的服务如 `camera`/`photos` 可以在安装前授权；它们会持续存在并在安装时应用。）

## 结果

返回 `{ action, permission, bundleId, applied, skipped? }`：

- `applied` - 实际更改的平台级服务/权限（iOS 上的 TCC 服务；Android 上的 `android.permission.*` 名称）。
- `skipped` - Android 仅限，当某些映射的权限被拒绝但其他权限成功时存在。

该调用 **失败** 当没有任何内容可以应用时 - 阅读错误；它命名了原因：平台不支持的不受支持的权限（iOS 上的 `notifications`，Android 上的 `reminders`），应用程序未安装（包括 iOS 上的预安装 `grant location`），关闭模拟器（iOS），或所有映射的权限都被拒绝（通常是缺少清单条目）。非关闭 `camera` 失败会额外提示关于模拟器运行时支持的服务（关闭模拟器失败会显示启动提示）。

## 示例

在启动之前预先授权相机，以便应用程序永远不会提示：

```json
{ "udid": "<UDID>", "action": "grant", "permission": "camera", "bundleId": "com.example.app" }
```

测试拒绝路径 - 拒绝位置，然后启动并观察回退：

```json
{ "udid": "<serial>", "action": "deny", "permission": "location", "bundleId": "com.example.app" }
```

重置 Android 上的通知，以便下次启动时首次运行提示再次出现：

```json
{
  "udid": "<serial>",
  "action": "reset",
  "permission": "notifications",
  "bundleId": "com.example.app"
}
```

在 Android 上授权始终开启位置（会自动扩展到后台 + 前台）：

```json
{
  "udid": "<serial>",
  "action": "grant",
  "permission": "location-always",
  "bundleId": "com.example.app"
}
```
