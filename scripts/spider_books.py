import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def scrape_books():
    print("📚 开始抓取图书价格与评分数据 (BeautifulSoup DOM结构解析)...")
    # 这是一个专门供新手练习爬虫的合法沙盒网站
    url = 'http://books.toscrape.com/catalogue/page-1.html'

    try:
        response = requests.get(url)
        response.raise_for_status()

        # 使用 BeautifulSoup 解析 HTML 树
        soup = BeautifulSoup(response.text, 'lxml')

        books_data = []
        # 找到所有包含图书信息的 <article> 标签
        articles = soup.find_all('article', class_='product_pod')

        for article in articles:
            # 提取书名 (在 a 标签的 title 属性里)
            title = article.h3.a['title']

            # 提取价格并转为浮点数
            price_str = article.find('p', class_='price_color').text
            price = float(price_str.replace('£', '').replace('Â', ''))

            # 提取星级评分 (把英文类名转为数字)
            rating_class = article.p['class'][1]
            rating_dict = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_dict.get(rating_class, 0)

            books_data.append({
                'Title': title,
                'Price': price,
                'Rating': rating
            })

        df = pd.DataFrame(books_data)

        # 🚀 故意制造缺失值，为清洗模块提供发挥空间
        df.loc[2, 'Price'] = np.nan
        df.loc[5, 'Rating'] = np.nan

        output_file = 'books_data.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ 图书数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"❌ 抓取失败: {e}")


if __name__ == "__main__":
    scrape_books()