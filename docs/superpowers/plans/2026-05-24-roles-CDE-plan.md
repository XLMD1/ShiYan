# 角色 C / E / D 实现计划

> 角色 A、B 已完成。C/E/D 三人并行开发，文件零冲突，可独立 MR。

---

## 接口约定（C ← 调用方 → E）

C 先定义函数签名，E 照着写 Django 视图调用：

```python
# cleaning.py — C 提供
def detect_missing(df: pd.DataFrame) -> dict
def handle_missing(df: pd.DataFrame, method: str) -> pd.DataFrame
def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> list
def get_dataset_stats(df: pd.DataFrame) -> dict

# clustering.py — C 提供
def run_kmeans(df: pd.DataFrame, features: list, k: int) -> dict
def elbow_method(df: pd.DataFrame, features: list, k_range: range) -> dict

# regression.py — C 提供
def run_linear_regression(df: pd.DataFrame, x_cols: list, y_col: str) -> dict

# visualization.py — E 提供
def build_echarts_option(chart_type: str, data: dict, config: dict) -> dict
```

---

## 角色 C：Python 算法 + 清洗页面

**文件列表（只改这些，不碰 E/D 的文件）：**

| 创建 | 文件 |
|------|------|
| ✅ | `backend/apps/analysis/cleaning.py` |
| ✅ | `backend/apps/analysis/clustering.py` |
| ✅ | `backend/apps/analysis/regression.py` |
| ✅ | `frontend/src/views/CleanView.vue` |
| ✅ | `frontend/src/components/StatsCard.vue` |

---

### Task C1：cleaning.py — 数据清洗

创建 `backend/apps/analysis/cleaning.py`：

```python
import pandas as pd
import numpy as np


def detect_missing(df):
    """检测缺失值，返回每列缺失数量"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    result = {}
    for col in df.columns:
        if missing[col] > 0:
            result[col] = {'count': int(missing[col]), 'percent': float(missing_pct[col])}
    return {
        'total_rows': len(df),
        'total_missing': int(missing.sum()),
        'columns': result,
    }


def handle_missing(df, method='mean'):
    """
    处理缺失值
    method: 'mean' | 'median' | 'mode' | 'drop'
    """
    if method == 'drop':
        return df.dropna()
    df = df.copy()
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            if method == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif method == 'median':
                df[col].fillna(df[col].median(), inplace=True)
    return df


def detect_outliers(df, column, method='iqr'):
    """
    异常值检测
    method: 'iqr' | 'zscore'
    返回异常值索引列表
    """
    data = df[column].dropna()
    if method == 'zscore':
        from scipy import stats
        z = np.abs(stats.zscore(data))
        return data[z > 3].index.tolist()
    else:  # IQR
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return data[(data < lower) | (data > upper)].index.tolist()


def get_dataset_stats(df):
    """返回数据概览统计"""
    stats = {
        'rows': len(df),
        'columns': len(df.columns),
        'dtypes': {col: str(df[col].dtype) for col in df.columns},
    }
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        desc = df[numeric_cols].describe().to_dict()
        stats['numeric_summary'] = {
            col: {k: round(v, 2) if isinstance(v, float) else v for k, v in desc[col].items()}
            for col in numeric_cols
        }
    return stats
```

---

### Task C2：clustering.py — K-Means 聚类

创建 `backend/apps/analysis/clustering.py`：

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np


def run_kmeans(df, features, k=3):
    """
    执行 K-Means 聚类
    df: DataFrame
    features: 用于聚类的列名列表
    k: 聚类数
    """
    X = df[features].dropna().values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)

    silhouette = silhouette_score(X_scaled, labels)

    return {
        'labels': labels.tolist(),
        'centers': model.cluster_centers_.tolist(),
        'inertia': float(model.inertia_),
        'silhouette_score': round(float(silhouette), 4),
        'k': k,
        'features': features,
        'cluster_sizes': [int((labels == i).sum()) for i in range(k)],
    }


def elbow_method(df, features, k_range=range(2, 11)):
    """
    肘部法则：计算不同 K 值下的 inertia
    """
    X = df[features].dropna().values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    results = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(X_scaled)
        results.append({'k': k, 'inertia': float(model.inertia_)})

    return results
```

---

### Task C3：regression.py — 线性回归

创建 `backend/apps/analysis/regression.py`：

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np


def run_linear_regression(df, x_cols, y_col, test_size=0.2):
    """
    执行线性回归
    df: DataFrame
    x_cols: 自变量列名列表
    y_col: 因变量列名
    test_size: 测试集比例
    """
    data = df[x_cols + [y_col]].dropna()
    X = data[x_cols].values
    y = data[y_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = float(mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))
    coefficients = {col: float(coef) for col, coef in zip(x_cols, model.coef_)}
    intercept = float(model.intercept_)

    return {
        'coefficients': coefficients,
        'intercept': intercept,
        'mse': round(mse, 4),
        'rmse': round(np.sqrt(mse), 4),
        'r2_score': round(r2, 4),
        'formula': f"y = {intercept:.4f}" + ''.join(
            f" + ({coef:.4f})*{col}" for col, coef in coefficients.items()
        ),
        'x_cols': x_cols,
        'y_col': y_col,
        'test_size': test_size,
        'actual_vs_predicted': [
            {'actual': round(float(a), 4), 'predicted': round(float(p), 4)}
            for a, p in zip(y_test[:100], y_pred[:100])
        ],
    }
```

---

### Task C4：StatsCard 组件 + CleanView 页面

创建 `frontend/src/components/StatsCard.vue` 和 `frontend/src/views/CleanView.vue`，调用 `/api/analysis/stats/` 和 `/api/analysis/clean/` 展示清洗选项和统计信息。

（具体 Vue 代码与 B 的页面风格一致，使用现有 CSS 变量，`page` / `card` 类名）

---

## 角色 E：分析 API + 图表数据

**文件列表（只改这些，不碰 C/D 的文件）：**

| 创建/改写 | 文件 |
|-----------|------|
| ✅ | `backend/apps/analysis/models.py` |
| ✅ | `backend/apps/analysis/serializers.py` |
| ✅ | `backend/apps/analysis/views.py` |
| ✅ | `backend/apps/analysis/urls.py` |
| ✅ | `backend/apps/analysis/visualization.py` |
| ✅ | `frontend/src/views/AnalysisView.vue` |
| ✅ | `frontend/src/components/AnalysisParams.vue` |
| ✅ | `frontend/src/stores/analysis.js` |

---

### Task E1：数据模型

改写 `backend/apps/analysis/models.py`：

```python
from django.db import models
from django.contrib.auth.models import User


class AnalysisTask(models.Model):
    TASK_TYPES = [
        ('kmeans', 'K-Means 聚类'),
        ('regression', '线性回归'),
    ]
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('done', '已完成'),
        ('error', '失败'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey('datafile.Dataset', on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    parameters = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict, null=True, blank=True)
    metrics = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ChartConfig(models.Model):
    CHART_TYPES = [
        ('scatter', '散点图'),
        ('line', '折线图'),
        ('bar', '柱状图'),
        ('heatmap', '热力图'),
        ('boxplot', '箱线图'),
        ('pie', '饼图'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis_task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, null=True, blank=True)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    x_column = models.CharField(max_length=100, blank=True)
    y_column = models.CharField(max_length=100, blank=True)
    color_column = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, blank=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Task E2：序列化器

改写 `backend/apps/analysis/serializers.py`：

```python
from rest_framework import serializers
from .models import AnalysisTask, ChartConfig


class AnalysisTaskSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AnalysisTask
        fields = '__all__'


class ChartConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartConfig
        fields = '__all__'
```

### Task E3：API 视图

改写 `backend/apps/analysis/views.py`：

```python
import pandas as pd
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from apps.datafile.models import Dataset
from .models import AnalysisTask, ChartConfig
from .serializers import AnalysisTaskSerializer, ChartConfigSerializer
from .cleaning import detect_missing, handle_missing, detect_outliers, get_dataset_stats
from .clustering import run_kmeans, elbow_method
from .regression import run_linear_regression
from .visualization import build_echarts_option


class DatasetCleanView(APIView):
    """POST /api/analysis/clean/{dataset_id}/"""
    def post(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=404)

        df = pd.read_csv(dataset.file.path) if dataset.file_type == 'csv' else pd.read_excel(dataset.file.path)
        method = request.data.get('method', 'mean')

        before = detect_missing(df)
        cleaned_df = handle_missing(df, method)
        after = detect_missing(cleaned_df)

        return Response({
            'missing_before': before,
            'missing_after': after,
            'method': method,
        })


class DatasetStatsView(APIView):
    """GET /api/analysis/stats/{dataset_id}/"""
    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=404)

        df = pd.read_csv(dataset.file.path) if dataset.file_type == 'csv' else pd.read_excel(dataset.file.path)
        stats = get_dataset_stats(df)
        missing = detect_missing(df)
        return Response({**stats, 'missing': missing})


class KMeansView(APIView):
    """POST /api/analysis/kmeans/"""
    def post(self, request):
        dataset_id = request.data.get('dataset_id')
        features = request.data.get('features', [])
        k = int(request.data.get('k', 3))

        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=404)

        df = pd.read_csv(dataset.file.path) if dataset.file_type == 'csv' else pd.read_excel(dataset.file.path)

        task = AnalysisTask.objects.create(
            user=request.user, dataset=dataset, task_type='kmeans',
            parameters={'features': features, 'k': k}, status='running'
        )

        result = run_kmeans(df, features, k)
        elbow = elbow_method(df, features)

        task.result_data = result
        task.metrics = {'silhouette_score': result['silhouette_score'], 'elbow': elbow}
        task.status = 'done'
        task.save()

        return Response(AnalysisTaskSerializer(task).data)


class RegressionView(APIView):
    """POST /api/analysis/regression/"""
    def post(self, request):
        dataset_id = request.data.get('dataset_id')
        x_cols = request.data.get('x_cols', [])
        y_col = request.data.get('y_col', '')

        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=404)

        df = pd.read_csv(dataset.file.path) if dataset.file_type == 'csv' else pd.read_excel(dataset.file.path)

        task = AnalysisTask.objects.create(
            user=request.user, dataset=dataset, task_type='regression',
            parameters={'x_cols': x_cols, 'y_col': y_col}, status='running'
        )

        result = run_linear_regression(df, x_cols, y_col)

        task.result_data = result
        task.metrics = {'r2_score': result['r2_score'], 'rmse': result['rmse']}
        task.status = 'done'
        task.save()

        return Response(AnalysisTaskSerializer(task).data)


class AnalysisTaskListView(ListAPIView):
    """GET /api/analysis/tasks/"""
    serializer_class = AnalysisTaskSerializer

    def get_queryset(self):
        return AnalysisTask.objects.filter(user=self.request.user)


class AnalysisTaskDetailView(APIView):
    """GET /api/analysis/tasks/{id}/"""
    def get(self, request, pk):
        try:
            task = AnalysisTask.objects.get(id=pk, user=request.user)
        except AnalysisTask.DoesNotExist:
            return Response({'error': '任务不存在'}, status=404)
        return Response(AnalysisTaskSerializer(task).data)


class ChartGenerateView(APIView):
    """POST /api/charts/generate/"""
    def post(self, request):
        chart_type = request.data.get('chart_type', 'scatter')
        data = request.data.get('data', {})
        config = request.data.get('config', {})

        option = build_echarts_option(chart_type, data, config)

        chart = ChartConfig.objects.create(
            user=request.user,
            chart_type=chart_type,
            x_column=config.get('x_column', ''),
            y_column=config.get('y_column', ''),
            title=config.get('title', ''),
            config=config,
        )

        return Response({'option': option, 'chart_id': chart.id})


class ChartConfigListView(ListAPIView):
    """GET /api/charts/configs/"""
    serializer_class = ChartConfigSerializer

    def get_queryset(self):
        return ChartConfig.objects.filter(user=self.request.user)
```

### Task E4：URL 路由

改写 `backend/apps/analysis/urls.py`：

```python
from django.urls import path
from . import views

urlpatterns = [
    path('clean/<int:dataset_id>/', views.DatasetCleanView.as_view(), name='dataset_clean'),
    path('stats/<int:dataset_id>/', views.DatasetStatsView.as_view(), name='dataset_stats'),
    path('kmeans/', views.KMeansView.as_view(), name='kmeans'),
    path('regression/', views.RegressionView.as_view(), name='regression'),
    path('tasks/', views.AnalysisTaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.AnalysisTaskDetailView.as_view(), name='task_detail'),
    path('charts/generate/', views.ChartGenerateView.as_view(), name='chart_generate'),
    path('charts/configs/', views.ChartConfigListView.as_view(), name='chart_configs'),
]
```

### Task E5：图表数据生成

创建 `backend/apps/analysis/visualization.py`：

```python
def build_echarts_option(chart_type, data, config):
    """根据图表类型和数据生成 ECharts option"""
    title = config.get('title', '')
    x_field = config.get('x_column', 'x')
    y_field = config.get('y_column', 'y')

    base = {
        'title': {'text': title},
        'tooltip': {},
        'xAxis': {},
        'yAxis': {},
        'series': [],
    }

    if chart_type == 'scatter':
        base['xAxis'] = {'name': x_field}
        base['yAxis'] = {'name': y_field}
        base['series'] = [{'type': 'scatter', 'data': data.get('points', [])}]

    elif chart_type == 'line':
        base['series'] = [{'type': 'line', 'data': data.get('values', [])}]

    elif chart_type == 'bar':
        base['xAxis'] = {'data': data.get('labels', []), 'axisLabel': {'rotate': 45}}
        base['series'] = [{'type': 'bar', 'data': data.get('values', [])}]

    elif chart_type == 'heatmap':
        base['series'] = [{'type': 'heatmap', 'data': data.get('matrix', [])}]

    elif chart_type == 'boxplot':
        base['series'] = [{
            'type': 'boxplot',
            'data': data.get('box_data', []),
        }]

    elif chart_type == 'pie':
        base.pop('xAxis', None)
        base.pop('yAxis', None)
        base['series'] = [{
            'type': 'pie',
            'data': data.get('items', []),
        }]

    return base
```

### Task E6：前端页面

创建 `frontend/src/stores/analysis.js`、`frontend/src/views/AnalysisView.vue`、`frontend/src/components/AnalysisParams.vue`，调用 `/api/analysis/kmeans/` 和 `/api/analysis/regression/` 展示分析结果。

---

## 角色 D：可视化 + 历史 + 部署

**文件列表（只改这些，不碰 C/E 的文件）：**

| 创建 | 文件 |
|------|------|
| ✅ | `frontend/src/views/VisualizeView.vue` |
| ✅ | `frontend/src/views/HistoryView.vue` |
| ✅ | `frontend/src/components/ChartPanel.vue` |
| ✅ | `frontend/src/components/ChartConfig.vue` |
| ✅ | `frontend/src/stores/chart.js` |

---

### Task D1：ChartPanel.vue — ECharts 渲染容器

创建 `frontend/src/components/ChartPanel.vue`：

```vue
<template>
  <div ref="chartRef" class="chart-container" :style="{ height: height + 'px' }"></div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: Number, default: 400 },
})

const chartRef = ref(null)
let chart = null

function initChart() {
  if (!chartRef.value) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  chart.setOption(props.option)
}

onMounted(initChart)
watch(() => props.option, initChart, { deep: true })
onBeforeUnmount(() => { if (chart) chart.dispose() })
</script>

<style scoped>
.chart-container { width: 100%; }
</style>
```

### Task D2：ChartConfig.vue — 图表配置面板

创建 `frontend/src/components/ChartConfig.vue`，提供：
- 图表类型下拉选择（散点/折线/柱状/热力/箱线/饼图）
- X 轴 / Y 轴字段选择
- 标题输入
- 颜色选择
- "生成图表" 按钮，调用 `/api/charts/generate/`

### Task D3：VisualizeView + HistoryView

创建 `frontend/src/views/VisualizeView.vue`：
- 引入 ChartPanel + ChartConfig
- 从 `analysisStore` 读取分析结果
- 用户配置图表参数 → 调用 API → 渲染

创建 `frontend/src/views/HistoryView.vue`：
- 调用 `/api/analysis/tasks/` 展示分析历史
- 每条记录显示任务类型、参数、指标、时间
- 点击可跳转到 Visualize 页

### Task D4：Pinia chart store

创建 `frontend/src/stores/chart.js`：
- `currentOption` — 当前 ECharts option
- `chartConfigs` — 用户保存的配置列表
- `generateChart(chartType, data, config)` — 调用 API 生成图表

### Task D5：部署 + 报告

```bash
cd frontend && npm run build
cp -r dist/* ../backend/static/
cd ../backend && python manage.py collectstatic --noinput
```

撰写实验报告。

---

## Git 分支策略

```
main (A+B 完成)
├── feature/cleaning-analysis (C) → MR#2
├── feature/analysis-api (E)      → MR#3
└── feature/visualize (D)         → MR#4
```

三个分支零文件冲突，各自开发完后分别提 PR 合入 main。
