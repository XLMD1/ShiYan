import pandas as pd
import numpy as np


def generate_synthetic_aqi():
    print("启用 NumPy/Pandas 随机模拟器，生成大规模气象与空气质量监测数据...")

    try:
        # 设定生成数据的规模
        num_samples = 500

        # 模拟全国500个监测站点的编号
        station_ids = [f"ST_{str(i).zfill(3)}" for i in range(1, num_samples + 1)]

        # 使用NumPy生成具有统计学意义的随机特征数据
        aqi_values = np.random.lognormal(mean=4.0, sigma=0.8, size=num_samples)
        aqi_values = np.clip(aqi_values, 10, 500).astype(int)

        # 基于AQI添加一些随机噪声
        pm25_values = (aqi_values * 0.7 + np.random.normal(loc=0, scale=10, size=num_samples))
        pm25_values = np.clip(pm25_values, 5, 400).astype(int)

        # 模拟正态分布
        temp_values = np.random.normal(loc=15.0, scale=10.0, size=num_samples).round(1)

        # 模拟均匀分布
        humidity_values = np.random.uniform(low=20.0, high=95.0, size=num_samples).round(1)

        # 使用Pandas构建DataFrame
        df = pd.DataFrame({
            '监测站编号': station_ids,
            '空气质量指数(AQI)': aqi_values,
            'PM2.5(微克/立方米)': pm25_values,
            '气温(摄氏度)': temp_values,
            '相对湿度(%)': humidity_values
        })

        # 人工注入脏数据NaN
        # 我们随机选择 5% 的数据，将其设置为 NaN
        num_missing = int(num_samples * 0.05)

        # 为PM2.5注入缺失值
        missing_indices_pm = np.random.choice(df.index, size=num_missing, replace=False)
        df.loc[missing_indices_pm, 'PM2.5(微克/立方米)'] = np.nan

        # 为气温注入缺失值
        missing_indices_temp = np.random.choice(df.index, size=num_missing, replace=False)
        df.loc[missing_indices_temp, '气温(摄氏度)'] = np.nan

        # 保存为CSV文件
        output_file = 'simulated_aqi_weather.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"成功利用 NumPy/Pandas 生成 {num_samples} 条模拟数据！")
        print(f"数据包含 4 个数值特征，并已随机注入 {num_missing} 个 NaN 缺失值。")
        print(f"已保存至 {output_file}")

    except Exception as e:
        print(f"数据生成失败: {e}")


if __name__ == "__main__":
    generate_synthetic_aqi()
