import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def run_kmeans(file_path, features, k):
    """执行 K-Means 聚类分析"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # 检查特征列是否存在
    missing_cols = [f for f in features if f not in df.columns]
    if missing_cols:
        raise ValueError(f'特征列不存在: {", ".join(missing_cols)}')

    # 选择特征列并移除缺失值行
    df_features = df[features].dropna()
    original_indices = df_features.index

    if len(df_features) < k:
        raise ValueError(f'有效数据行数 ({len(df_features)}) 少于 K 值 ({k})')

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_features)

    # K-Means 聚类
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # 肘部法则和轮廓系数（K=2 到 min(10, 样本数)）
    max_k = min(10, len(df_features) - 1)
    inertias = []
    silhouette_scores = []
    k_range = list(range(2, max_k + 1))

    for i in k_range:
        km = KMeans(n_clusters=i, random_state=42, n_init=10)
        km_labels = km.fit_predict(X_scaled)
        inertias.append(float(km.inertia_))
        if len(set(km_labels)) > 1:
            silhouette_scores.append(round(float(silhouette_score(X_scaled, km_labels)), 4))
        else:
            silhouette_scores.append(0.0)

    # 当前模型评估
    current_silhouette = round(float(silhouette_score(X_scaled, labels)), 4) if k > 1 else 0.0

    # 聚类中心（反标准化）
    centers_unscaled = scaler.inverse_transform(kmeans.cluster_centers_)

    # 构建结果数据（前 500 条）
    result_df = df.loc[original_indices].copy()
    result_df['cluster'] = labels.astype(int)
    result_records = result_df.head(500).to_dict('records')
    for rec in result_records:
        for key, val in rec.items():
            if isinstance(val, (np.integer,)):
                rec[key] = int(val)
            elif isinstance(val, (np.floating,)):
                rec[key] = float(val)
            elif isinstance(val, np.ndarray):
                rec[key] = val.tolist()

    # 每个簇的大小
    cluster_sizes = {}
    for i in range(k):
        cluster_sizes[f'cluster_{i}'] = int((labels == i).sum())

    # 将聚类中心转为前端友好的数组格式（每个簇一个坐标数组）
    centers_array = [
        [round(float(centers_unscaled[i][j]), 4) for j in range(len(features))]
        for i in range(k)
    ]
    sizes_array = [cluster_sizes[f'cluster_{i}'] for i in range(k)]

    return {
        'cluster_labels': labels.astype(int).tolist(),
        'cluster_centers': {
            f'cluster_{i}': {
                features[j]: round(float(centers_unscaled[i][j]), 4)
                for j in range(len(features))
            }
            for i in range(k)
        },
        'cluster_sizes': cluster_sizes,
        'result_data': {
            'records': result_records,
            'centers': centers_array,
            'sizes': sizes_array,
        },
        'metrics': {
            'inertia': round(float(kmeans.inertia_), 4),
            'silhouette_score': current_silhouette,
            'elbow_data': {
                'k_values': k_range,
                'inertias': inertias,
                'silhouette_scores': silhouette_scores,
            },
        },
    }
