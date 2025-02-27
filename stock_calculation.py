import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.download(ticker, start=start_date, end=end_date)
    return stock['Close']

def simulate_strategy(prices, drop_rate=0.02, rise_rate=0.25, fixed_shares=10, lookback=25):
    total_shares = 0
    total_cash = 40000  # 初始現金
    initial_investment = total_cash  # 記錄初始投入資金
    num_trades = 0
    
    # 創建 DataFrame 來儲存交易紀錄
    trades = pd.DataFrame(columns=["buy_date", "buy_price", "sell_date", "sell_price", "shares"])
    
    for i in range(lookback, len(prices)):  
        last_buy_price = prices.iloc[i-lookback-1:i-1].mean()

        #  記錄買入交易
        if  i > 1 and prices.iloc[i] <= last_buy_price * (1 - drop_rate) and total_cash >= prices.iloc[i] * fixed_shares and prices.iloc[i] < prices.iloc[i-1]:
            new_trade = pd.DataFrame({
                "buy_date": [prices.index[i]],   # 買入日期
                "buy_price": [prices[i]],        # 買入價格
                "sell_date": [None],             # 賣出日期
                "sell_price": [None],            # 賣出價格
                "shares": [fixed_shares]         # 買入數量
            })
            trades = pd.concat([trades, new_trade], ignore_index=True)
            total_shares += fixed_shares
            total_cash -= prices.iloc[i] * fixed_shares
            print(f"買入: {prices.iloc[i]:.2f}, 日期: {prices.index[i]}")
            print(trades.tail(10))  
        
        else:
            print(f"資金不足，無法買入 {fixed_shares} 股，當前現金: {total_cash:.2f}, 需要: {prices.iloc[i] * fixed_shares:.2f}")
        
        last_sell_date = None  # 記錄上一次賣出的日期
        
        #  檢查哪些交易達到 rise_rate 增長，可以賣出
        for index, row in trades.iterrows():
            current_date = prices.index[i]  # 當前價格對應的日期
            
            # 如果當天已經賣出過，就不再賣出
            if last_sell_date == current_date:
                continue  
            if pd.isna(row["sell_price"]) and prices.iloc[i] >= row["buy_price"] * (1 + rise_rate) and prices.iloc[i] >= last_buy_price and prices.iloc[i] < prices.iloc[i-1]:
                trades.at[index, "sell_price"] = prices.iloc[i]  # 用 at[] 確保 sell_price 更新
                trades.at[index, "sell_date"] = current_date  # 記錄賣出日期
                total_cash += prices.iloc[i] * row["shares"]
                total_shares -= row["shares"]
                num_trades += 1
                last_sell_date = current_date  # 更新最後一次賣出的日期
                print(f"賣出: {prices.iloc[i]:.2f}, 日期: {prices.index[i]}")
                print(trades.tail(10))

    total_value = total_cash + (total_shares * prices.iloc[-1])
    roi = (total_value / initial_investment - 1) * 100
    
    return roi, num_trades, trades

ticker = "AAPL"
start_date = "2024-01-01"
end_date = "2025-02-15"

prices = fetch_stock_data(ticker, start_date, end_date)
roi, num_trades, trades = simulate_strategy(prices)

print(f"股票代號: {ticker}")
print(f"投資報酬率 (ROI): {roi:.2f}%")
print(f"交易次數: {num_trades}")

# 確保 sell_price 是 float，防止 NaN 影響繪圖
trades["sell_price"] = pd.to_numeric(trades["sell_price"], errors="coerce")

#  繪製價格走勢圖
plt.figure(figsize=(12, 5))
plt.plot(prices.index, prices.iloc, label="Stock Price", color='b')

#  提取買入與賣出交易資訊
buy_trades = trades.dropna(subset=["buy_price"])
sell_trades = trades.dropna(subset=["sell_price"])

#  修正買入與賣出點的繪圖方式
plt.scatter(buy_trades["buy_date"], buy_trades["buy_price"], marker='^', color='g', label="Buy", zorder=3)
plt.scatter(sell_trades["sell_date"], sell_trades["sell_price"], marker='v', color='r', label="Sell", zorder=3)

#  顯示 ROI 文字
plt.text(0.5, 0.9, f"ROI: {roi:.2f}%", horizontalalignment='center', verticalalignment='center', 
         transform=plt.gca().transAxes, fontsize=12, color='black', backgroundcolor='white')

#  加入標籤與網格
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title(f"{ticker} Price Trend with Buy/Sell Points")
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.show()