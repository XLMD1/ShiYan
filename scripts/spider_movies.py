import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import requests


def scrape_movies():
    print("🎬 开始抓取全球票房最高电影数据...")
    url = 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'

    # 伪装成正常的 Windows 电脑 Chrome 浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 使用 io.StringIO 包装 HTML 文本，专治最新版 pandas 的长篇警告！
        html_stream = io.StringIO(response.text)
        tables = pd.read_html(html_stream)

        df = tables[0]  # 获取第一个大表

        # 保留前几列核心数据
        df = df.iloc[:, [0, 1, 2, 3]]
        df.columns = ['Rank', 'Title', 'Worldwide_Gross', 'Year']

        output_file = 'movies_box_office.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 电影数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"❌ 抓取失败: {e}")


if __name__ == "__main__":
    scrape_movies()