import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random


def scrape_douban():
    print("🎬 开始抓取 豆瓣电影 Top250 数据 (防反爬加强版)...")
    url = 'https://movie.douban.com/top250'

    # 生成随机的访客 bid，完美伪装真实用户
    bid = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 11))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://movie.douban.com/',  # 伪装是从豆瓣首页跳转过来的
        'Cookie': f'bid={bid};'  # 携带随机访客身份
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 使用 Python 内置的 html.parser，兼容性最强
        soup = BeautifulSoup(response.text, 'html.parser')
        movies_data = []

        items = soup.find_all('div', class_='item')
        if not items:
            print("警告：虽然连上豆瓣，但被认出是爬虫，返回了验证页面。请稍后再试。")
            return

        for item in items:
            try:
                title = item.find('span', class_='title').text
                rating = float(item.find('span', class_='rating_num').text)

                # 防御性编程：如果抓不到星级评分，就给默认值，绝不让程序崩溃
                star_div = item.find('div', class_='star')
                if star_div:
                    spans = star_div.find_all('span')
                    # 确保提取的内容真的是数字
                    votes_str = spans[3].text if len(spans) > 3 else "0人评价"
                    votes = int(votes_str.replace('人评价', '').strip())
                else:
                    votes = 0

                movies_data.append({
                    '电影名称': title,
                    '豆瓣评分': rating,
                    '评价人数': votes
                })
            except Exception as inner_e:
                # 遇到个别排版乱掉的电影直接跳过
                continue

        df = pd.DataFrame(movies_data)

        if not df.empty:
            # 故意制造缺失值
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