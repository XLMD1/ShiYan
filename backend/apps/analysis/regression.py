import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error


def run_regression(file_path, x_columns, y_column):
    """执行线性回归分析"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    all_cols = x_columns + [y_column]

    # 检查列是否存在
    missing_cols = [c for c in all_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f'列不存在: {", ".join(missing_cols)}')

    # 移除含缺失值的行
    df_clean = df[all_cols].dropna()

    if len(df_clean) < 2:
        raise ValueError('有效数据行数不足（至少需要 2 行）')

    X = df_clean[x_columns].values
    y = df_clean[y_column].values

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 线性回归
    model = LinearRegression()
    model.fit(X_scaled, y)

    # 预测
    y_pred = model.predict(X_scaled)

    # 评估指标
    r2 = round(float(r2_score(y, y_pred)), 4)
    mse = round(float(mean_squared_error(y, y_pred)), 4)
    rmse = round(float(np.sqrt(mse)), 4)

    # 系数
    coefficients = {col: round(float(model.coef_[i]), 4) for i, col in enumerate(x_columns)}
    intercept = round(float(model.intercept_), 4)

    # 回归方程
    terms = [f'({coefficients[col]} * {col})' for col in x_columns]
    equation = f'{y_column} = {intercept} + ' + ' + '.join(terms)

    # 构建结果数据（前 500 条）
    result_data = []
    for i in range(min(len(y), 500)):
        row = {col: float(df_clean[col].iloc[i]) if pd.api.types.is_numeric_dtype(df_clean[col]) else str(df_clean[col].iloc[i]) for col in x_columns}
        row[y_column] = float(y[i])
        row['predicted'] = round(float(y_pred[i]), 4)
        row['residual'] = round(float(y[i] - y_pred[i]), 4)
        result_data.append(row)

    return {
        'result_data': result_data,
        'metrics': {
            'r2_score': r2,
            'mse': mse,
            'rmse': rmse,
            'coefficients': coefficients,
            'intercept': intercept,
            'equation': equation,
        },
    }
