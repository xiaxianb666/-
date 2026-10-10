#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import requests
import os

# 🌟 配置区：可以随意增加或减少你想监控的股票代码
# NVDA=英伟达, AAPL=苹果, TSLA=特斯拉, MSFT=微软, BTC-USD=比特币
SYMBOLS = ["NVDA", "AAPL", "TSLA", "MSFT", "BTC-USD"]

def analyze_stock_data(symbol):
    """获取单只股票的数据，并计算复杂的量化指标"""
    try:
        ticker = yf.Ticker(symbol)
        # 取近3个月数据，保证有足够的数据计算20日均线
        hist = ticker.history(period="3mo", interval="1d")
        if hist.empty:
            return None
        
        hist = hist[["Close", "Volume"]].dropna().sort_index()
        
        # 1. 基础涨跌数据
        hist["涨跌幅%"] = (hist["Close"] / hist["Close"].shift(1) - 1) * 100
        # 2. 计算5日和20日均线（智能趋势指标）
        hist["MA5"] = hist["Close"].rolling(window=5).mean()
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        
        # 只取最近5天来做汇报
        recent = hist.tail(5)
        current_price = recent["Close"].iloc[-1]
        
        # 生成文本数据给AI
        data_text = f"标的：{symbol}\n最近5天收盘价及涨跌幅：\n"
        for date, row in recent.iterrows():
            data_text += f"  {date.strftime('%Y-%m-%d')}: {row['Close']:.2f} ({row['涨跌幅%']:+.2f}%)\n"
        
        # 附加趋势判断
        ma5_last = recent["MA5"].iloc[-1]
        ma20_last = recent["MA20"].iloc[-1]
        trend = "多头排列（强势）" if ma5_last > ma20_last else "空头排列（弱势）"
        
        # 连跌判断
        last_three = recent["涨跌幅%"].tail(3)
        is_falling = "是" if len(last_three) == 3 and (last_three < 0).all() else "否"
        
        data_text += f"当前价格：{current_price:.2f}\nMA5：{ma5_last:.2f} | MA20：{ma20_last:.2f} | 趋势：{trend}\n最近3天是否连跌：{is_falling}\n"
        return data_text, trend, is_falling
    except Exception as e:
        print(f"获取 {symbol} 数据失败：{e}")
        return None, None, None

def ask_ai_portfolio_manager(all_data_text):
    """把多只股票的数据一次性发给AI，让它做综合分析"""
    api_key = os.environ.get("AI_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 🌟 极其复杂的“超级提示词”，迫使AI展现出专业性
    prompt = f"""你现在是全球顶尖对冲基金的量化投资总监。请你阅读以下多只股票的近期数据（包括价格、涨跌幅、均线趋势和连跌情况），为我的模拟投资组合写一份专业的每日复盘报告。

【数据如下】：
{all_data_text}

【你的任务】：
1. 逐一简要点评这5只标的的近期表现。
2. 重点表扬表现最好的，提示风险最大的标的。
3. 根据这些数据，给出一个【模拟资金分配建议】（例如：50%买NVDA，30%买BTC，20%现金）。
4. 用Markdown表格在最后做一个汇总。语气要专业、冷静、客观。
5. 结尾必须加上免责声明：本报告由AI自动生成，仅供数据学习研究，不构成任何真实投资建议。
"""
    payload = {
        "model": "llama-3.3-70b-versatile", # 这里已经换成了 Groq 目前最强模型
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用AI失败：{e}"

def main():
    print(f"🚀 正在启动多股票智能量化雷达...")
    all_data = ""
    for symbol in SYMBOLS:
        print(f"正在扫描 {symbol}...")
        data_text, trend, is_falling = analyze_stock_data(symbol)
        if data_text:
            all_data += data_text + "\n" + "-"*30 + "\n"
    
    if not all_data:
        print("所有数据获取失败，退出。")
        return
        
    print("正在将数据发送给AI投资总监进行分析...")
    ai_report = ask_ai_portfolio_manager(all_data)
    
    print("\n" + "="*50)
    print("🧠 AI 量化投资总监 - 多股票每日复盘报告")
    print("="*50)
    print(ai_report)

if __name__ == "__main__":
    main()
