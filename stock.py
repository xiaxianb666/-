#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import requests
import os

# 🌟 A股热门标的：中际旭创、宁德时代、新易盛、药明康德、寒武纪、工业富联
SYMBOLS = ["300308.SZ", "300750.SZ", "300502.SZ", "603259.SS", "688256.SS", "601138.SS"]

def analyze_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # A股数据在yfinance里可能稍微短一点，我们取6个月的数据保证均线准确
        hist = ticker.history(period="6mo", interval="1d")
        if hist.empty:
            return None
        
        hist = hist[["Close", "Volume"]].dropna().sort_index()
        hist["涨跌幅%"] = (hist["Close"] / hist["Close"].shift(1) - 1) * 100
        hist["MA5"] = hist["Close"].rolling(window=5).mean()
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        
        recent = hist.tail(5)
        current_price = recent["Close"].iloc[-1]
        
        data_text = f"标的：{symbol}\n最近5天收盘价及涨跌幅：\n"
        for date, row in recent.iterrows():
            data_text += f"  {date.strftime('%Y-%m-%d')}: {row['Close']:.2f} ({row['涨跌幅%']:+.2f}%)\n"
        
        ma5_last = recent["MA5"].iloc[-1]
        ma20_last = recent["MA20"].iloc[-1]
        trend = "多头排列（强势）" if ma5_last > ma20_last else "空头排列（弱势）"
        
        last_three = recent["涨跌幅%"].tail(3)
        is_falling = "是" if len(last_three) == 3 and (last_three < 0).all() else "否"
        
        data_text += f"当前价格：{current_price:.2f}\nMA5：{ma5_last:.2f} | MA20：{ma20_last:.2f} | 趋势：{trend}\n最近3天是否连跌：{is_falling}\n"
        return data_text, trend, is_falling
    except Exception as e:
        print(f"获取 {symbol} 数据失败：{e}")
        return None, None, None

def ask_ai_portfolio_manager(all_data_text):
    api_key = os.environ.get("AI_API_KEY")
    # 🌟 这里使用了 Groq 目前最稳定的 OpenAI 兼容接口
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""你现在是全球顶尖对冲基金的量化投资总监。请你阅读以下多只A股的近期数据，为我的模拟投资组合写一份专业的每日复盘报告。

【数据如下】：
{all_data_text}

【你的任务】：
1. 逐一简要点评这6只A股的近期表现。
2. 重点表扬表现最好的，提示风险最大的标的。
3. 根据这些数据，给出一个【模拟资金分配建议】。
4. 用Markdown表格在最后做一个汇总。语气要专业、冷静、客观。
5. 结尾必须加上免责声明：本报告由AI自动生成，仅供数据学习研究，不构成任何真实投资建议。
"""
    payload = {
        # 🌟 换成 Groq 目前最强大的免费模型 Llama 3.3 70B
        "model": "llama-3.3-70b-versatile", 
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
    print(f"🚀 正在启动A股智能量化雷达...")
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
    print("🧠 AI 量化投资总监 - A股每日复盘报告")
    print("="*50)
    print(ai_report)

if __name__ == "__main__":
    main()
