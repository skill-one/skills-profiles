# GameKit

使用 GameKit 进行 Game Center 身份验证、竞赛、匹配、社交界面和存档游戏；保留渲染、棋盘逻辑和完整的 SharePlay 组活动设计在其所属框架技能中。

## 目录

- [身份验证](#身份验证)
- [接入点](#接入点)
- [控制面板](#控制面板)
- [排行榜](#排行榜)
- [成就](#成就)
- [实时多人游戏](#实时多人游戏)
- [回合制多人游戏](#回合制多人游戏)
- [常见错误](#常见错误)
- [审核清单](#审核清单)
- [参考资料](#参考资料)

## 身份验证

所有 GameKit 功能都需要本地玩家先进行身份验证。在应用程序生命周期早期设置 `authenticateHandler` 在 `GKLocalPlayer.local` 上。GameKit 在初始化期间会多次调用该处理程序。

```swift
import GameKit

func authenticatePlayer() {
    GKLocalPlayer.local.authenticateHandler = { viewController, error in
        if let viewController {
            // 显示视图，让玩家可以登录或创建账户。
            present(viewController, animated: true)
            return
        }
        if let error {
            // 玩家无法登录。禁用 Game Center 功能。
            disableGameCenter()
            return
        }

        // 玩家已通过身份验证。在开始前检查限制。
        let player = GKLocalPlayer.local

        if player.isUnderage {
            hideExplicitContent()
        }
        if player.isMultiplayerGamingRestricted {
            disableMultiplayer()
        }
        if player.isPersonalizedCommunicationRestricted {
            disableInGameChat()
        }

        configureAccessPoint()
    }
}
```

在调用任何 GameKit API 之前，先检查 `GKLocalPlayer.local.isAuthenticated`。有关服务器端身份验证，请参阅 [参考资料/gamekit-patterns.md](references/gamekit-patterns.md)。

## 接入点

`GKAccessPoint` 在屏幕角落显示 Game Center 控件。点击时会打开 Game Center 控制面板。在身份验证后进行配置。

```swift
func configureAccessPoint() {
    GKAccessPoint.shared.location = .topLeading
    GKAccessPoint.shared.showHighlights = true
    GKAccessPoint.shared.isActive = true
}
```

在游戏过程中隐藏接入点，并在菜单屏幕上显示它：

```swift
GKAccessPoint.shared.isActive = false  // 游戏过程中隐藏
GKAccessPoint.shared.isActive = true   // 暂停或菜单时显示
```

通过编程方式打开控制面板到特定状态。特定排行榜接入点触发器需要 iOS 18+。

```swift
// 直接打开排行榜
GKAccessPoint.shared.trigger(
    leaderboardID: "com.mygame.highscores",
    playerScope: .global,
    timeScope: .allTime
) { }

// 直接打开成就
GKAccessPoint.shared.trigger(state: .achievements) { }
```

## 控制面板

使用 `GKGameCenterViewController` 显示 Game Center 控制面板。呈现对象必须遵守 `GKGameCenterControllerDelegate`。

```swift
final class GameViewController: UIViewController, GKGameCenterControllerDelegate {

    func showDashboard() {
        let vc = GKGameCenterViewController(state: .dashboard)
        vc.gameCenterDelegate = self
        present(vc, animated: true)
    }

    func showLeaderboard(_ leaderboardID: String) {
        let vc = GKGameCenterViewController(
            leaderboardID: leaderboardID,
            playerScope: .global,
            timeScope: .allTime
        )
        vc.gameCenterDelegate = self
        present(vc, animated: true)
    }

    func gameCenterViewControllerDidFinish(
        _ gameCenterViewController: GKGameCenterViewController
    ) {
        gameCenterViewController.dismiss(animated: true)
    }
}
```

控制面板状态包括 `.dashboard`、`.leaderboards`、`.achievements`、`.challenges`、`.localPlayerProfile` 和 `.localPlayerFriendsList`。

## 排行榜

在提交分数之前，在 App Store Connect 中配置排行榜。支持经典（持久）和周期性（有时间限制、自动重置）类型。

### 提交分数

使用类方法提交到一个或多个排行榜：

```swift
func submitScore(_ score: Int, leaderboardIDs: [String]) async throws {
    try await GKLeaderboard.submitScore(
        score,
        context: 0,
        player: GKLocalPlayer.local,
        leaderboardIDs: leaderboardIDs
    )
}
```

### 加载条目

```swift
func loadTopScores(
    leaderboardID: String,
    count: Int = 10
) async throws -> (GKLeaderboard.Entry?, [GKLeaderboard.Entry]) {
    let leaderboards = try await GKLeaderboard.loadLeaderboards(
        IDs: [leaderboardID]
    )
    guard let leaderboard = leaderboards.first else { return (nil, []) }

    let (localEntry, entries, _) = try await leaderboard.loadEntries(
        for: .global,
        timeScope: .allTime,
        range: 1...count
    )
    return (localEntry, entries)
}
```

`GKLeaderboard.Entry` 提供 `player`、`rank`、`score`、`formattedScore`、`context` 和 `date`。有关周期性排行榜的定时、排行榜图像和排行榜集，请参阅 [参考资料/gamekit-patterns.md](references/gamekit-patterns.md)。

## 成就

在 App Store Connect 中配置成就。每个成就都有一个唯一的标识符、积分值和本地化标题/描述。

### 报告进度

设置 `percentComplete` 从 `0...100`。属性类型是 `Double`，但 Apple 需要一个整数值。GameKit 只接受增加。

```swift
func reportAchievement(identifier: String, percentComplete: Int) async throws {
    let achievement = GKAchievement(identifier: identifier)
    achievement.percentComplete = Double(min(max(percentComplete, 0), 100))
    achievement.showsCompletionBanner = true
    try await GKAchievement.report([achievement])
}

// 完全解锁成就
func unlockAchievement(_ identifier: String) async throws {
    try await reportAchievement(identifier: identifier, percentComplete: 100)
}
```

### 加载玩家成就

```swift
func loadPlayerAchievements() async throws -> [GKAchievement] {
    try await GKAchievement.loadAchievements()
}
```

如果某个成就没有被返回，玩家还没有在该成就上的进度。创建一个新的 `GKAchievement(identifier:)` 开始报告。使用 `GKAchievement.resetAchievements()` 在测试期间重置所有进度。

## 实时多人游戏

实时多人游戏将玩家连接到对等网络进行同步游戏。玩家通过 `GKMatch` 直接交换数据。

### 使用 GameKit UI 进行匹配

使用 `GKMatchmakerViewController` 进行标准的匹配界面：

```swift
func presentMatchmaker() {
    let request = GKMatchRequest()
    request.minPlayers = 2
    request.maxPlayers = 4
    request.inviteMessage = "加入我的游戏！"

    guard let matchmakerVC = GKMatchmakerViewController(matchRequest: request) else {
        return
    }
    matchmakerVC.matchmakerDelegate = self
    present(matchmakerVC, animated: true)
}
```

实现 `GKMatchmakerViewControllerDelegate`：

```swift
extension GameViewController: GKMatchmakerViewControllerDelegate {
    func matchmakerViewController(
        _ viewController: GKMatchmakerViewController,
        didFind match: GKMatch
    ) {
        match.delegate = self
        viewController.dismiss(animated: true)
        startGame(with: match)
    }

    func matchmakerViewControllerWasCancelled(
        _ viewController: GKMatchmakerViewController
    ) {
        viewController.dismiss(animated: true)
    }

    func matchmakerViewController(
        _ viewController: GKMatchmakerViewController,
        didFailWithError error: Error
    ) {
        viewController.dismiss(animated: true)
    }
}
```

### 交换数据

通过 `GKMatch` 和 `GKMatchDelegate` 发送和接收游戏状态：

```swift
extension GameViewController: GKMatchDelegate {
    func sendAction(_ action: GameAction, to match: GKMatch) throws {
        let data = try JSONEncoder().encode(action)
        try match.sendData(toAllPlayers: data, with: .reliable)
    }

    func match(_ match: GKMatch, didReceive data: Data, fromRemotePlayer player: GKPlayer) {
        guard let action = try? JSONDecoder().decode(GameAction.self, from: data) else {
            return
        }
        handleRemoteAction(action, from: player)
    }

    func match(_ match: GKMatch, player: GKPlayer, didChange state: GKPlayerConnectionState) {
        switch state {
        case .connected:
            checkIfReadyToStart(match)
        case .disconnected:
            handlePlayerDisconnected(player)
        default:
            break
        }
    }
}
```

数据模式：`.reliable` 发送直到成功交付或连接超时；`.unreliable` 发送一次，可能乱序到达。使用 `.reliable` 发送关键状态，使用 `.unreliable` 发送频繁的小更新。将接收到的匹配数据视为不受信任的输入。注册本地玩家为监听器 (`GKLocalPlayer.local.register(self)`) 接收邀请。有关程序化匹配和自定义匹配 UI，请参阅 [参考资料/gamekit-patterns.md](references/gamekit-patterns.md)。

## 回合制多人游戏

回合制游戏将匹配状态存储在 Game Center 服务器上。玩家异步轮流进行，不需要同时在线。

### 开始匹配

```swift
let request = GKMatchRequest()
request.minPlayers = 2
request.maxPlayers = 4

let matchmakerVC = GKTurnBasedMatchmakerViewController(matchRequest: request)
matchmakerVC.turnBasedMatchmakerDelegate = self
present(matchmakerVC, animated: true)
```

### 轮流

将游戏状态编码为 `Data`，结束回合，并指定下一个参与者：

```swift
func endTurn(match: GKTurnBasedMatch, gameState: GameState) async throws {
    let data = try JSONEncoder().encode(gameState)

    // 构建下一个参与者列表：剩余的活跃玩家
    let nextParticipants = match.participants.filter {
        $0.status != .done && $0 != match.currentParticipant
    }

    try await match.endTurn(
        withNextParticipants: nextParticipants,
        turnTimeout: GKTurnTimeoutDefault,
        match: data
    )
}
```

### 结束匹配

为所有参与者设置结果，然后结束匹配：

```swift
func endMatch(_ match: GKTurnBasedMatch, winnerIndex: Int, data: Data) async throws {
    for (index, participant) in match.participants.enumerated() {
        participant.matchOutcome = (index == winnerIndex) ? .won : .lost
    }
    try await match.endMatchInTurn(withMatch: data)
}
```

### 监听回合事件

注册为监听器。当单个对象处理多个 Game Center 事件类别时，优先使用 `GKLocalPlayerListener`。

```swift
GKLocalPlayer.local.register(self)

extension GameViewController: GKLocalPlayerListener {
    func player(_ player: GKPlayer, receivedTurnEventFor match: GKTurnBasedMatch,
                didBecomeActive: Bool) {
        // 加载匹配数据并更新 UI
        loadAndDisplayMatch(match)
    }

    func player(_ player: GKPlayer, matchEnded match: GKTurnBasedMatch) {
        showMatchResults(match)
    }
}
```

### 匹配数据大小

在结束回合之前检查匹配对象的 `matchDataMaximumSize`。将较大的状态存储在外部，仅在匹配数据中保留紧凑的引用。

## 常见错误

### 在使用 GameKit API 之前未进行身份验证

```swift
// 不要
func submitScore() {
    GKLeaderboard.submitScore(100, context: 0, player: GKLocalPlayer.local,
                              leaderboardIDs: ["scores"]) { _ in }
}

// 要
func submitScore() async throws {
    guard GKLocalPlayer.local.isAuthenticated else { return }
    try await GKLeaderboard.submitScore(
        100, context: 0, player: GKLocalPlayer.local, leaderboardIDs: ["scores"]
    )
}
```

### 多次设置 authenticateHandler

```swift
// 不要：在每个场景转换时设置处理程序
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    GKLocalPlayer.local.authenticateHandler = { vc, error in /* ... */ }
}

// 要：在应用程序生命周期早期设置一次处理程序
```

### 忽略多人游戏限制

```swift
// 不要
func showMultiplayerMenu() { presentMatchmaker() }

// 要
func showMultiplayerMenu() {
    guard !GKLocalPlayer.local.isMultiplayerGamingRestricted else { return }
    presentMatchmaker()
}
```

### 未立即设置匹配代理

```swift
// 不要：在关闭完成时设置代理——会错过早期的消息
func matchmakerViewController(_ vc: GKMatchmakerViewController, didFind match: GKMatch) {
    vc.dismiss(animated: true) { match.delegate = self }
}

// 要：在关闭之前设置代理
func matchmakerViewController(_ vc: GKMatchmakerViewController, didFind match: GKMatch) {
    match.delegate = self
    vc.dismiss(animated: true)
}
```

### 未调用 finishMatchmaking for 程序化匹配

```swift
// 不要
let match = try await GKMatchmaker.shared().findMatch(for: request)
startGame(with: match)

// 要
let match = try await GKMatchmaker.shared().findMatch(for: request)
GKMatchmaker.shared().finishMatchmaking(for: match)
startGame(with: match)
```

### 未从匹配中断开连接

```swift
// 不要
func returnToMenu() { showMainMenu() }

// 要
func returnToMenu() {
    currentMatch?.disconnect()
    currentMatch?.delegate = nil
    currentMatch = nil
    showMainMenu()
}
```

## 审核清单

- [ ] `GKLocalPlayer.local.authenticateHandler` 在应用启动时设置一次
- [ ] 在任何 GameKit API 调用之前检查 `isAuthenticated`
- [ ] 检查玩家限制 (`isUnderage`、`isMultiplayerGamingRestricted`、`isPersonalizedCommunicationRestricted`)
- [ ] 在 Xcode 签名设置中添加 Game Center 功能
- [ ] 在 App Store Connect 中配置排行榜和成就
- [ ] 在游戏过程中配置和适当切换接入点
- [ ] `GKGameCenterControllerDelegate` 在 `gameCenterViewControllerDidFinish` 中关闭控制面板
- [ ] 匹配找到时立即设置匹配代理
- [ ] 程序化匹配调用 `finishMatchmaking(for:)`；退出时调用 `disconnect()` 和 nil 代理
- [ ] 回合制匹配数据保持在 `match.matchDataMaximumSize` 以下
- [ ] 回合制参与者在进行 `endMatchInTurn` 之前设置结果
- [ ] 使用 `GKLocalPlayer.local.register(_:)` 注册邀请或回合监听器
- [ ] 适当选择数据模式：`.reliable` 用于状态，`.unreliable` 用于频繁更新
- [ ] 所有异步 GameKit 调用进行错误处理

## 参考资料

- 有关身份验证、遗留语音聊天、存档游戏、自定义匹配 UI、排行榜图像、挑战处理和基于规则的匹配，请参阅 [参考资料/gamekit-patterns.md](references/gamekit-patterns.md)。
- [GameKit 文档](https://sosumi.ai/documentation/gamekit)
- [GKLocalPlayer](https://sosumi.ai/documentation/gamekit/gklocalplayer)
- [GKAccessPoint](https://sosumi.ai/documentation/gamekit/gkaccesspoint)
- [GKLeaderboard](https://sosumi.ai/documentation/gamekit/gkleaderboard)
- [GKAchievement](https://sosumi.ai/documentation/gamekit/gkachievement)
- [GKMatch](https://sosumi.ai/documentation/gamekit/gkmatch)
- [GKTurnBasedMatch](https://sosumi.ai/documentation/gamekit/gkturnbasedmatch)
