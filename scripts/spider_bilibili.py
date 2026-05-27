import requests
import pandas as pd
import numpy as np


def scrape_bilibili():
    print("始抓取 B站综合热门视频数据 (REST API JSON解析)...")
    # B站官方的综合热门公开 API，国内直连秒开，无需登录
    url = 'https://api.bilibili.com/x/web-interface/popular'
    params = {
        'ps': 50,  # 获取 50 条数据
        'pn': 1
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        video_list = []

        # 解析 B 站多层嵌套的 JSON 结构
        if data['code'] == 0:
            for item in data['data']['list']:
                video_list.append({
                    '视频标题': item['title'],
                    'UP主': item['owner']['name'],
                    '播放量': item['stat']['view'],
                    '弹幕数': item['stat']['danmaku'],
                    '点赞数': item['stat']['like']
                })

        df = pd.DataFrame(video_list)

        # 故意制造缺失值，为队友的清洗模块提供发挥空间
        df.loc[2, '播放量'] = np.nan
        df.loc[5, '点赞数'] = np.nan

        output_file = 'bilibili_hot.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"B站数据抓取成功！已保存至 {output_file}")

    except Exception as e:
        print(f"抓取失败: {e}")


if __name__ == "__main__":
    scrape_bilibili()