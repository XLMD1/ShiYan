import pandas as pd
import numpy as np


def generate_synthetic_aqi():
    print("启用 NumPy/Pandas 随机模拟器，生成大规模气象与空气质量监测数据...")

    try:
        # 1. 设定生成数据的规模
        num_samples = 500

        # 2. 生成基础结构：模拟全国 500 个监测站点的编号
        station_ids = [f"ST_{str(i).zfill(3)}" for i in range(1, num_samples + 1)]

        # 3. 使用 NumPy 生成具有统计学意义的随机特征数据

        # AQI (空气质量指数): 模拟偏态分布 (大部分在 30-100，少数会很高)
        # 使用 numpy.random.lognormal 生成偏态数据，然后限制范围并取整
        aqi_values = np.random.lognormal(mean=4.0, sigma=0.8, size=num_samples)
        aqi_values = np.clip(aqi_values, 10, 500).astype(int)

        # PM2.5: 通常与 AQI 高度正相关，我们基于 AQI 添加一些随机噪声
        pm25_values = (aqi_values * 0.7 + np.random.normal(loc=0, scale=10, size=num_samples))
        pm25_values = np.clip(pm25_values, 5, 400).astype(int)

        # 气温 (Temp): 模拟正态分布，全国均温大概在 15度 左右，标准差 10度
        temp_values = np.random.normal(loc=15.0, scale=10.0, size=num_samples).round(1)

        # 相对湿度 (Humidity): 模拟均匀分布，在 20% 到 95% 之间
        humidity_values = np.random.uniform(low=20.0, high=95.0, size=num_samples).round(1)

        # 4. 使用 Pandas 构建 DataFrame
        df = pd.DataFrame({
            '监测站编号': station_ids,
            '空气质量指数(AQI)': aqi_values,
            'PM2.5(微克/立方米)': pm25_values,
            '气温(摄氏度)': temp_values,
            '相对湿度(%)': humidity_values
        })

        # 5. 关键步骤：人工注入“脏数据 (NaN)”，完美适配下游清洗模块
        # 我们随机选择 5% 的数据，将其设置为 NaN
        num_missing = int(num_samples * 0.05)

        # 为 PM2.5 注入缺失值
        missing_indices_pm = np.random.choice(df.index, size=num_missing, replace=False)
        df.loc[missing_indices_pm, 'PM2.5(微克/立方米)'] = np.nan

        # 为 气温 注入缺失值
        missing_indices_temp = np.random.choice(df.index, size=num_missing, replace=False)
        df.loc[missing_indices_temp, '气温(摄氏度)'] = np.nan

        # 6. 保存为 CSV 文件
        output_file = 'simulated_aqi_weather.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"成功利用 NumPy/Pandas 生成 {num_samples} 条模拟数据！")
        print(f"数据包含 4 个数值特征，并已随机注入 {num_missing} 个 NaN 缺失值。")
        print(f"已保存至 {output_file}")

    except Exception as e:
        print(f"数据生成失败: {e}")


if __name__ == "__main__":
    generate_synthetic_aqi()