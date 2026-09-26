# 交易策略开发技能

## 策略基础类

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class Signal:
    type: SignalType
    token_id: str
    price: float
    size: float
    confidence: float  # 0-1
    timestamp: datetime
    metadata: dict = None

@dataclass
class MarketState:
    token_id: str
    yes_price: float
    no_price: float
    volume_24h: float
    open_interest: float
    orderbook: dict
    recent_trades: list
    timestamp: datetime

class BaseStrategy(ABC):
    """所有交易策略的基础类。"""
    
    def __init__(self, config: dict):
        self.config = config
        self.positions = {}
        self.signals_history = []
    
    @abstractmethod
    async def analyze(self, market: MarketState) -> Optional[Signal]:
        """分析市场并生成信号。"""
        pass
    
    @abstractmethod
    def calculate_position_size(
        self,
        signal: Signal,
        portfolio_value: float
    ) -> float:
        """计算适当的仓位大小。"""
        pass
    
    def should_execute(self, signal: Signal) -> bool:
        """确定是否应该执行信号。"""
        return signal.confidence >= self.config.get("min_confidence", 0.6)
```

## 策略类型

### 1. 套利策略
```python
class ArbitrageStrategy(BaseStrategy):
    """检测并利用价格不匹配。"""
    
    async def find_opportunities(
        self,
        markets: list[MarketState]
    ) -> list[Signal]:
        opportunities = []
        
        # 检查 YES + NO > 1（价格过高）
        for market in markets:
            total = market.yes_price + market.no_price
            if total > 1.02:  # 2% 阈值
                opportunities.append(
                    self._create_arb_signal(market, "overpriced", total)
                )
        
        # 检查相关市场
        opportunities.extend(
            await self._find_related_arbs(markets)
        )
        
        return opportunities
    
    async def analyze(self, market: MarketState) -> Optional[Signal]:
        total = market.yes_price + market.no_price
        
        # 价格过高市场（YES + NO > 1）
        if total > 1.0 + self.config.get("arb_threshold", 0.02):
            profit_pct = (total - 1.0) * 100
            return Signal(
                type=SignalType.SELL,
                token_id=market.token_id,
                price=total,
                size=self.config.get("default_size", 100),
                confidence=min(profit_pct / 10, 1.0),
                timestamp=datetime.utcnow(),
                metadata={"arb_type": "overpriced", "profit_pct": profit_pct}
            )
        
        return None
```

### 2. 动量策略
```python
class MomentumStrategy(BaseStrategy):
    """基于价格动量和成交量进行交易。"""
    
    async def analyze(self, market: MarketState) -> Optional[Signal]:
        # 计算动量指标
        price_change = self._calculate_price_change(market, hours=4)
        volume_ratio = self._calculate_volume_ratio(market)
        orderbook_imbalance = self._calculate_imbalance(market.orderbook)
        
        score = (
            price_change * 0.4 +
            volume_ratio * 0.3 +
            orderbook_imbalance * 0.3
        )
        
        if score > self.config.get("buy_threshold", 0.3):
            return Signal(
                type=SignalType.BUY,
                token_id=market.token_id,
                price=market.yes_price,
                size=self.calculate_position_size(score, 10000),
                confidence=min(abs(score), 1.0),
                timestamp=datetime.utcnow(),
                metadata={
                    "price_change": price_change,
                    "volume_ratio": volume_ratio,
                    "imbalance": orderbook_imbalance
                }
            )
        elif score < self.config.get("sell_threshold", -0.3):
            return Signal(
                type=SignalType.SELL,
                token_id=market.token_id,
                price=market.yes_price,
                size=self.calculate_position_size(score, 10000),
                confidence=min(abs(score), 1.0),
                timestamp=datetime.utcnow()
            )
        
        return None
    
    def _calculate_imbalance(self, orderbook: dict) -> float:
        """计算买卖不平衡。"""
        total_bids = sum(b["size"] for b in orderbook.get("bids", [])[:5])
        total_asks = sum(a["size"] for a in orderbook.get("asks", [])[:5])
        
        if total_bids + total_asks == 0:
            return 0
        
        return (total_bids - total_asks) / (total_bids + total_asks)
```

### 3. 均值回归策略
```python
class MeanReversionStrategy(BaseStrategy):
    """从价格极端进行反转交易。"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.lookback_hours = config.get("lookback_hours", 24)
        self.std_threshold = config.get("std_threshold", 2.0)
    
    async def analyze(self, market: MarketState) -> Optional[Signal]:
        historical_prices = await self._get_historical_prices(
            market.token_id,
            hours=self.lookback_hours
        )
        
        mean_price = sum(historical_prices) / len(historical_prices)
        std_dev = self._calculate_std(historical_prices, mean_price)
        
        current_price = market.yes_price
        z_score = (current_price - mean_price) / std_dev if std_dev > 0 else 0
        
        # 价格显著低于均值 - 买入
        if z_score < -self.std_threshold:
            return Signal(
                type=SignalType.BUY,
                token_id=market.token_id,
                price=current_price,
                size=self.config.get("default_size", 100),
                confidence=min(abs(z_score) / 3, 1.0),
                timestamp=datetime.utcnow(),
                metadata={"z_score": z_score, "mean": mean_price}
            )
        
        # 价格显著高于均值 - 卖出
        elif z_score > self.std_threshold:
            return Signal(
                type=SignalType.SELL,
                token_id=market.token_id,
                price=current_price,
                size=self.config.get("default_size", 100),
                confidence=min(abs(z_score) / 3, 1.0),
                timestamp=datetime.utcnow(),
                metadata={"z_score": z_score, "mean": mean_price}
            )
        
        return None
```

## 回测框架

```python
@dataclass
class BacktestResult:
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_value: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    trades: list[dict]
    equity_curve: list[float]

class Backtester:
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000,
        fee_rate: float = 0.01
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
    
    async def run(
        self,
        historical_data: list[MarketState],
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """在历史数据上运行回测。"""
        portfolio_value = self.initial_capital
        cash = self.initial_capital
        positions = {}
        equity_curve = [portfolio_value]
        trades = []
        
        for market_state in historical_data:
            if market_state.timestamp < start_date:
                continue
            if market_state.timestamp > end_date:
                break
            
            signal = await self.strategy.analyze(market_state)
            
            if signal and self.strategy.should_execute(signal):
                trade_result = self._simulate_trade(
                    signal, cash, positions, market_state
                )
                if trade_result:
                    trades.append(trade_result)
                    cash = trade_result["remaining_cash"]
                    positions = trade_result["positions"]
            
            # 更新投资组合价值
            portfolio_value = cash + self._calculate_positions_value(
                positions, market_state
            )
            equity_curve.append(portfolio_value)
        
        return self._calculate_metrics(
            trades, equity_curve, start_date, end_date
        )
    
    def _calculate_metrics(
        self,
        trades: list,
        equity_curve: list,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """计算性能指标。"""
        returns = [
            (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            for i in range(1, len(equity_curve))
            if equity_curve[i-1] > 0
        ]
        
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = self._calculate_std(returns, avg_return) if returns else 0
        sharpe = (avg_return * 252**0.5) / std_return if std_return > 0 else 0
        
        # 最大回撤
        peak = equity_curve[0]
        max_dd = 0
        for value in equity_curve:
            peak = max(peak, value)
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
        
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        
        return BacktestResult(
            strategy_name=self.strategy.__class__.__name__,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_value=equity_curve[-1],
            total_return=(equity_curve[-1] - self.initial_capital) / self.initial_capital,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=len(winning_trades) / len(trades) if trades else 0,
            total_trades=len(trades),
            trades=trades,
            equity_curve=equity_curve
        )
```

## 风险管理

```python
class RiskManager:
    def __init__(self, config: dict):
        self.max_position_pct = config.get("max_position_pct", 0.1)
        self.max_drawdown_pct = config.get("max_drawdown_pct", 0.2)
        self.daily_loss_limit = config.get("daily_loss_limit", 0.05)
        self.max_correlation = config.get("max_correlation", 0.7)
    
    def validate_signal(
        self,
        signal: Signal,
        portfolio: dict
    ) -> tuple[bool, str]:
        """根据风险参数验证信号。"""
        # 检查仓位集中度
        position_value = signal.price * signal.size
        if position_value > portfolio["value"] * self.max_position_pct:
            return False, f"仓位过大: {position_value:.2f}"
        
        # 检查回撤
        current_drawdown = (
            portfolio["peak_value"] - portfolio["value"]
        ) / portfolio["peak_value"]
        if current_drawdown > self.max_drawdown_pct:
            return False, f"最大回撤超过: {current_drawdown:.2%}"
        
        # 检查每日亏损限额
        daily_pnl = portfolio.get("daily_pnl", 0)
        if daily_pnl < -portfolio["value"] * self.daily_loss_limit:
            return False, f"每日亏损限额超过: {daily_pnl:.2f}"
        
        return True, "OK"
    
    def calculate_kelly_size(
        self,
        win_prob: float,
        win_amount: float,
        loss_amount: float
    ) -> float:
        """计算凯利准则仓位大小。"""
        if loss_amount == 0:
            return 0
        
        b = win_amount / loss_amount
        p = win_prob
        q = 1 - p
        
        kelly = (b * p - q) / b
        
        # 使用半凯利以安全起见
        return max(0, kelly * 0.5)
```
