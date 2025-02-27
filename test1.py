import yfinance as yf
import mplfinance as mpf
import pandas as pd
import numpy as np  # 用來處理 NaN 值

# 下載台積電 (2330.TW) 的股票數據
ticker = yf.Ticker("2330.TW")
df = ticker.history(period="1y")

# 檢查數據是否成功下載
if df.empty:
    print("股票數據下載失敗或沒有數據。")
else:
    # 計算 x 日均線
    x=10
    df['x_day_avg'] = df['Close'].rolling(window=x).mean()
    # 計算 x 日均線
    y=20
    df['twenty_day_avg'] = df['Close'].rolling(window=y).mean()

    # 交易變數初始化
    cash = 50000  # 初始現金
    stock_owned = 0  # 持有股數
    total_investment = cash  # 初始投資總額
    buy_price_threshold = 0.01  # 買入閾值
    buy_price_threshold1 = 0.06  # 買入閾值
    buy_price_threshold2 = 0.09  # 買入閾值
    sell_price_threshold = 0.02  # 賣出閾值
    sell_price_threshold1 = 0.03  # 賣出閾值
    sell_price_threshold2 = 0.04  # 賣出閾值
    buy_signals = []
    sell_signals = []
    copy_buy_signals = []

    # 交易策略
    for i in range(25, len(df)):
        yesterday_close = df.iloc[i - 1]['Close']
        today_close = df.iloc[i]['Close']
        ten_day_avg = df.iloc[i]['x_day_avg']

        if ten_day_avg * (1 - buy_price_threshold1) < today_close < ten_day_avg * (1 - buy_price_threshold) and cash > today_close and today_close < yesterday_close:
            stock_owned += 1
            cash -= today_close * (100.0855/100)
            buy_signals.append((df.index[i], today_close))  # 記錄日期與價格
            copy_buy_signals.append((df.index[i], today_close))
            
        if ten_day_avg * (1 - buy_price_threshold2) < today_close <= ten_day_avg * (1 - buy_price_threshold1) and cash > 2 * today_close and today_close < yesterday_close:
            stock_owned += 2
            cash -= 2*today_close * (100.0855/100)
            buy_signals.append((df.index[i], today_close))  # 記錄日期與價格
            copy_buy_signals.append((df.index[i], today_close))
            
        if today_close < ten_day_avg * (1 - buy_price_threshold2) and cash > 3 * today_close and today_close < yesterday_close:
            stock_owned += 3
            cash -= 3 * today_close * (100.0855/100)
            buy_signals.append((df.index[i], today_close))  # 記錄日期與價格
            copy_buy_signals.append((df.index[i], today_close))
            
        for n in range(len(copy_buy_signals)):
            if ten_day_avg * (1 + sell_price_threshold1) > today_close >= ten_day_avg * (1 + sell_price_threshold) and today_close > copy_buy_signals[n][1] and stock_owned >=1 and today_close < yesterday_close :
                stock_owned -= 1
                cash += 1 * today_close * (99.6145/100)
                copy_buy_signals.pop(n)#刪除第n個
                sell_signals.append((df.index[i], today_close))  # 更新成第i日期與價格
                print(f"賣一張{df.index[i], today_close}")
                break
            if ten_day_avg * (1 + sell_price_threshold2) > today_close >= ten_day_avg * (1 + sell_price_threshold1) and today_close > copy_buy_signals[n][1] and stock_owned >=2 and today_close < yesterday_close :
                stock_owned -= 2
                cash += 2 * today_close * (99.6145/100)
                copy_buy_signals.pop(n)#刪除第n個
                sell_signals.append((df.index[i], today_close))  # 更新成第i日期與價格
                print(f"賣兩張{df.index[i], today_close}")
                break
            if today_close >= ten_day_avg * (1 + sell_price_threshold2) and today_close > copy_buy_signals[n][1] and stock_owned >= 3 and today_close < yesterday_close :
                stock_owned -= 3
                cash += 3 * today_close * (99.6145/100)
                copy_buy_signals.pop(n)#刪除第n個
                sell_signals.append((df.index[i], today_close))  # 更新成第i日期與價格
                print(f"賣三張{df.index[i], today_close}")
                break                       

    print(stock_owned)
    # 計算最終投資價值
    final_value = cash + stock_owned * df.iloc[-1]['Close']
    investment_return = (final_value - total_investment) / total_investment * 100

    print(f"初始投資金額: {total_investment:.2f} 新台幣")
    print(f"最終價值: {final_value:.2f} 新台幣")
    print(f"投資報酬率: {investment_return:.2f}%")

    # 建立新的欄位來存放買賣信號
    df['Buy_Signal'] = np.nan  # 用 NaN 代替 None
    df['Sell_Signal'] = np.nan

    for date, price in buy_signals:
        df.at[date, 'Buy_Signal'] = price

    for date, price in sell_signals:
        df.at[date, 'Sell_Signal'] = price

    # 添加買賣點標記
    ap_buy = mpf.make_addplot(df['Buy_Signal'], type='scatter', markersize=100, marker='^', color='g') if not df['Buy_Signal'].isna().all() else None
    ap_sell = mpf.make_addplot(df['Sell_Signal'], type='scatter', markersize=100, marker='v', color='r') if not df['Sell_Signal'].isna().all() else None    
    # Create an addplot for the x-day moving average
    ap_ma = mpf.make_addplot(df['x_day_avg'], color='r')
    # Create an addplot for the twenty-day moving average
    ap_ma1 = mpf.make_addplot(df['twenty_day_avg'], color='purple')
    
    # 組合 addplot
    addplots = [ap for ap in [ap_buy, ap_sell, ap_ma, ap_ma1] if ap is not None]

    # 繪製 K 線圖
    mpf.plot(df, type='line', style='charles', title='2330', volume=True, addplot=addplots)


