import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import requests
import numpy as np


def scrape_weather():
    print("🌤️ 开始抓取全球城市平均气温数据...")
    url = 'https://en.wikipedia.org/wiki/List_of_cities_by_average_temperature'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 使用 io 包装破解警告（和电影爬虫一样稳）
        html_stream = io.StringIO(response.text)
        tables = pd.read_html(html_stream)

        # 获取第一个大表（非洲各大城市的气温记录），数据非常规整
        df = tables[0]

        # 截取最核心的列：国家、城市、1月气温、2月气温、3月气温、全年平均气温
        # 维基百科该表共有15列，我们按索引提取 [0, 1, 2, 3, 4, 14]
        df = df.iloc[:, [0, 1, 2, 3, 4, 14]]
        df.columns = ['Country', 'City', 'Jan_Temp', 'Feb_Temp', 'Mar_Temp', 'Year_Avg']

        # 🚀 制造“小麻烦”：给第3行和第6行故意挖两个空缺值 (NaN)
        df.loc[2, 'Feb_Temp'] = np.nan
        df.loc[5, 'Year_Avg'] = np.nan

        output_file = 'global_temperature.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 气象数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"❌ 抓取失败: {e}")


if __name__ == "__main__":
    scrape_weather()