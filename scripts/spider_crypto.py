import requests
import pandas as pd
import numpy as np


def scrape_crypto():
    print("🪙 开始抓取加密货币实时行情数据 (REST API JSON 解析)...")
    # 使用著名的 CoinGecko 公共开放 API
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 50,  # 抓取市值前50的币种
        'page': 1,
        'sparkline': False
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # 直接将响应体解析为 Python 字典/列表 (JSON 格式)
        data = response.json()

        crypto_list = []
        for item in data:
            crypto_list.append({
                'Name': item.get('name'),
                'Symbol': item.get('symbol').upper(),
                'Current_Price': item.get('current_price'),
                'Market_Cap': item.get('market_cap'),
                'Total_Volume': item.get('total_volume')
            })

        df = pd.DataFrame(crypto_list)

        # 🚀 制造少许数据缺失，模拟网络延迟导致的字段丢失
        df.loc[1, 'Total_Volume'] = np.nan
        df.loc[4, 'Current_Price'] = np.nan
        df.loc[10, 'Market_Cap'] = np.nan

        output_file = 'crypto_markets.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 加密货币数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"❌ 抓取失败: {e}")


if __name__ == "__main__":
    scrape_crypto()