import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def scrape_wuhan_lianjia():
    print("开始抓取武汉链家二手房核心数据...")
    # 定位武汉站域名
    url = 'https://wh.lianjia.com/ershoufang/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        houses = []

        # 提取当前页面的房源信息卡片
        for item in soup.find_all('div', class_='info clear')[:30]:
            title = item.find('div', class_='title').a.text.strip()

            # 提取总价
            total_price = float(item.find('div', class_='totalPrice').span.text)

            # 提取单价并清洗掉千分位逗号和文字
            unit_price_str = item.find('div', class_='unitPrice').span.text
            unit_price_clean = unit_price_str.replace('单价', '').replace('元/平米', '').replace('元/平', '').replace(
                ',', '').strip()
            unit_price = float(unit_price_clean)

            # 根据总价和单价，算出该套房源建筑面积
            area = round(total_price * 10000 / unit_price, 2)

            houses.append({
                '房源标题': title,
                '总价(万)': total_price,
                '单价(元/平米)': unit_price,
                '建筑面积(平米)': area
            })

        df = pd.DataFrame(houses)

        # 制造2处缺失值NaN
        df.loc[3, '建筑面积(平米)'] = np.nan
        df.loc[7, '单价(元/平米)'] = np.nan

        output_file = 'wuhan_houses.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"武汉房价数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"抓取失败: {e}")


if __name__ == "__main__":
    scrape_wuhan_lianjia()
