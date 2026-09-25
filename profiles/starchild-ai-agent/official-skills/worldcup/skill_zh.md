# ⚽ 世界杯2026技能

FIFA世界杯2026数据 + 基于积分的预测游戏。**脚本技能**——
从`core.skill_tools.worldcup`中调用函数，并在bash中读取JSON。
认证自动（容器JWT）；无需API密钥。

## 如何调用

```bash
python3 -c "from core.skill_tools import worldcup; import json; print(json.dumps(worldcup.get_today_matches()))"
```

每个函数返回一个类似于`{"success": true, "data": ...}`的字典（失败时返回
`{"success": false, "error": ...}`）。

## 使用场景

- **比赛** — 今天 / 即将进行 / 实时 / 已结束，或特定比赛。
- **预测** — 下注、取消或查看预测历史。
- **统计** — 积分余额、投注限额、胜率、总投注额。
- **排行榜** — 按积分或准确率排名的顶尖预测者。

## 函数 (`from core.skill_tools import worldcup`)

| 函数 | 返回值 |
|------|-------|
| `get_today_matches()` | 今天的比赛 + 你的预测状态 |
| `get_upcoming_matches(limit=10)` | 下一次安排的比赛 |
| `get_live_matches()` | 当前进行的比赛 |
| `get_finished_matches(limit=20)` | 最近结果 |
| `get_match_detail(match_id)` | 一个完整比赛 |
| `place_bet(match_id, predict_type, prediction, stake)` | 下注预测 |
| `cancel_prediction(prediction_id)` | 取消未结算的预测，退还投注额 |
| `get_betting_status()` | 积分余额、待处理投注额、最小/最大投注额 |
| `get_my_predictions(match_id=None, settled_only=False)` | 你的预测历史 |
| `get_prediction_detail(prediction_id)` | 一个完整预测 |
| `get_my_stats()` | 你的胜率、总投注额等 |
| `get_leaderboard(limit=50, sort_by="points")` | 顶尖预测者 (`sort_by`: points\|accuracy) |

## 下注 — `predict_type` 和 `prediction`

`prediction`是一个取决于`predict_type`的字典。仅填写该类型的键：

| predict_type | prediction | 含义 |
|---|---|---|
| `win_draw_loss` | `{"choice": "home"\|"draw"\|"away"}` | 比赛结果 |
| `exact_score` | `{"home": N, "away": N}` | 最终确切比分 |
| `total_goals` | `{"range": "0-1"\|"2-3"\|"4+"}` | 总进球区间 |
| `first_goal` | `{"team": "TEAM_CODE"}` | 哪支球队能先进球（例如 `BRA`） |

`stake` = 投注积分：10的倍数，最小10，最大10000。

### 推荐的 `place_bet` 流程
1. `get_betting_status()` — 确认有足够的可用积分。
2. `get_match_detail(match_id)` 或 `get_today_matches()` — 确认比赛开放并获取球队代码（`first_goal`需要）。
3. `place_bet(match_id, predict_type, prediction, stake)`。
4. 将返回的预测ID读回用户。

示例：
```bash
python3 -c "from core.skill_tools import worldcup; import json; print(json.dumps(worldcup.place_bet(42, 'win_draw_loss', {'choice':'home'}, 100)))"
```

## 注意事项
- 积分是预测游戏的货币，不是真实货币 — 以游戏形式呈现，绝不作为财务建议。
- `cancel_prediction` 仅在预测未结算时有效；会退还投注额。
- 比赛时间为UTC；在相关情况下转换为用户的时区。
