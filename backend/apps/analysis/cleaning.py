import pandas as pd
import numpy as np


def detect_missing(df):
    """检测每列的缺失值数量"""
    missing = {}
    for col in df.columns:
        count = int(df[col].isna().sum())
        if count > 0:
            missing[col] = count
    return missing


def detect_outliers_iqr(df, column):
    """使用 IQR 方法检测异常值"""
    col_data = df[column].dropna()
    if len(col_data) == 0:
        return 0
    Q1 = col_data.quantile(0.25)
    Q3 = col_data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = col_data[(col_data < lower) | (col_data > upper)]
    return int(len(outliers))


def detect_outliers_zscore(df, column):
    """使用 Z-score 方法检测异常值 (|z| > 3)"""
    col_data = df[column].dropna()
    if len(col_data) == 0:
        return 0
    mean = col_data.mean()
    std = col_data.std()
    if std == 0 or pd.isna(std):
        return 0
    z_scores = np.abs((col_data - mean) / std)
    return int((z_scores > 3).sum())


def handle_missing(df, column, method='mean'):
    """处理指定列的缺失值"""
    if method == 'drop':
        return df.dropna(subset=[column])
    elif method == 'mean':
        fill_val = df[column].mean()
        if pd.isna(fill_val):
            fill_val = 0
        df[column] = df[column].fillna(fill_val)
    elif method == 'median':
        fill_val = df[column].median()
        if pd.isna(fill_val):
            fill_val = 0
        df[column] = df[column].fillna(fill_val)
    elif method == 'mode':
        mode_vals = df[column].mode()
        if len(mode_vals) > 0:
            df[column] = df[column].fillna(mode_vals[0])
        else:
            df[column] = df[column].fillna(0)
    return df


def get_column_stats(df, col):
    """获取单列的基本统计信息"""
    col_data = df[col].dropna()
    stats = {
        'count': int(len(col_data)),
        'missing': int(df[col].isna().sum()),
    }
    if len(col_data) > 0 and pd.api.types.is_numeric_dtype(col_data):
        stats.update({
            'mean': float(round(col_data.mean(), 4)),
            'std': float(round(col_data.std(), 4)),
            'min': float(round(col_data.min(), 4)),
            'max': float(round(col_data.max(), 4)),
            'median': float(round(col_data.median(), 4)),
        })
        stats['outliers_iqr'] = detect_outliers_iqr(df, col)
        stats['outliers_zscore'] = detect_outliers_zscore(df, col)
    return stats


def clean_dataset(file_path, cleaning_config):
    """执行数据清洗，返回清洗后的 DataFrame 和清洗报告"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    original_rows = len(df)
    report = {
        'before': {
            'rows': original_rows,
            'columns': len(df.columns),
            'missing': detect_missing(df),
        },
        'actions': [],
    }

    columns_config = cleaning_config.get('columns', [])

    for col_config in columns_config:
        col = col_config.get('column')
        action = col_config.get('missing_action', 'none')

        if col not in df.columns:
            continue

        if action in ('mean', 'median', 'mode'):
            before_missing = int(df[col].isna().sum())
            df = handle_missing(df, col, action)
            after_missing = int(df[col].isna().sum())
            report['actions'].append({
                'column': col,
                'action': f'fill_missing_{action}',
                'description': f'用{action}填充 {col} 列的缺失值',
                'before': before_missing,
                'after': after_missing,
            })
        elif action == 'drop':
            before_missing = int(df[col].isna().sum())
            rows_before = len(df)
            df = handle_missing(df, col, 'drop')
            rows_removed = rows_before - len(df)
            report['actions'].append({
                'column': col,
                'action': 'drop_missing_rows',
                'description': f'删除 {col} 列含缺失值的行',
                'rows_removed': rows_removed,
                'missing_before': before_missing,
            })

    report['after'] = {
        'rows': len(df),
        'columns': len(df.columns),
        'missing': detect_missing(df),
    }

    return df, report
