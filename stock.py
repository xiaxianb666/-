#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd


def main():
    symbol = "NVDA"

    try:
        ticker = yf.Ticker(symbol)
        # 多取一段时间的日线数据，保证最近5天里的第一天也能算出涨跌幅
        hist = ticker.history(period="1mo", interval="1d")
    except Exception as e:
        print(f"获取 {symbol} 数据失败：{e}")
        return

    if hist.empty:
        print(f"未获取到 {symbol} 的历史数据。")
        return

    # 只保留收盘价，删除缺失值，并按日期升序排列
    hist = hist[["Close"]].dropna().sort_index()

    if len(hist) < 2:
        print(f"{symbol} 数据不足，无法计算涨跌幅。")
        return

    # 计算每日涨跌幅：相对前一交易日收盘价
    hist["涨跌幅%"] = (hist["Close"] / hist["Close"].shift(1) - 1) * 100

    # 只报告最近5个交易日
    report_df = hist.tail(5).copy()

    print(f"{symbol} 最近5个交易日收盘价报告：")
    print("-" * 60)

    for date, row in report_df.iterrows():
        date_str = date.strftime("%Y-%m-%d")
        close = row["Close"]
        pct = row["涨跌幅%"]

        if pd.isna(pct):
            pct_str = "N/A"
            warning = ""
        else:
            pct_str = f"{pct:+.2f}%"
            # 跌幅超过 2% 时追加暴跌预警
            warning = " ⚠️ 暴跌预警" if pct < -2 else ""

        print(f"{date_str}  收盘价: {close:.2f}  涨跌幅: {pct_str}{warning}")

    # 判断最近3个交易日是否连续下跌：最近3天涨跌幅都为负
    last_three_pct = report_df["涨跌幅%"].tail(3)
    if len(last_three_pct) == 3 and (last_three_pct < 0).all():
        print("\n📉 注意：该股票已连续3天下跌，建议谨慎观察。")


if __name__ == "__main__":
    main()
