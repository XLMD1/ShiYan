import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random
import re


def scrape_douban():
    print("开始抓取 豆瓣电影 Top250 数据 (最终暴力破解版)...")
    url = 'https://movie.douban.com/top250'

    bid = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 11))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://movie.douban.com/',
        'Cookie': f'bid={bid};'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        movies_data = []

        items = soup.find_all('div', class_='item')
        if not items:
            print("警告：被豆瓣认出是爬虫，返回了验证页面。请稍后再试。")
            return

        for item in items:
            try:
                title = item.find('span', class_='title').text
                rating = float(item.find('span', class_='rating_num').text)

                # 降维打击：提取整块HTML里的所有纯文本，无视任何标签层级
                item_text = item.get_text()

                # 暴力扫描：寻找连续的数字(\d+)，后面跟着任意数量的空格(\s*)，再跟着"人评价"
                match = re.search(r'(\d+)\s*人评价', item_text)

                # 如果找到了，就提取数字部分；没找到再用 0 兜底
                votes = int(match.group(1)) if match else 0

                movies_data.append({
                    '电影名称': title,
                    '豆瓣评分': rating,
                    '评价人数': votes
                })
            except Exception as inner_e:
                continue

        df = pd.DataFrame(movies_data)

        if not df.empty:
            # 故意制造缺失值 (NaN) 供下游清洗
            df.loc[1, '豆瓣评分'] = np.nan
            df.loc[4, '评价人数'] = np.nan

            output_file = 'douban_movies.csv'
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"豆瓣数据抓取成功！共抓取 {len(df)} 条，已保存至 {output_file}")
        else:
            print("解析完成，但数据为空。")

    except Exception as e:
        print(f"抓取失败: {e}")


if __name__ == "__main__":
    scrape_douban()
