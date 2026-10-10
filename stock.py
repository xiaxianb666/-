import yfinance as yf

def get_stock_report(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    
    report = f"📊 【自动监控】{ticker} 最近5天行情：\n"
    report += "-" * 30 + "\n"
    
    for date, row in hist.iterrows():
        close_price = row['Close']
        date_str = date.strftime('%Y-%m-%d')
        report += f"日期: {date_str} | 收盘价: ${close_price:.2f}\n"
        
    return report

print(get_stock_report("NVDA"))
