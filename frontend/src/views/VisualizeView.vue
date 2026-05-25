<template>
  <div class="page">
    <div class="view-header">
      <div>
        <h2>图表可视化</h2>
        <p v-if="currentTask" class="subtitle">{{ taskLabel }} · {{ datasetName }}</p>
      </div>
      <router-link to="/history" class="btn btn-primary">历史记录</router-link>
    </div>

    <div v-if="loading" class="card empty">加载中...</div>
    <div v-else-if="error" class="card empty error">{{ error }}</div>
    <div v-else-if="!currentTask" class="card empty">暂无分析任务</div>

    <template v-else>
      <div class="workspace-grid">
        <ChartConfig
          :columns="chartColumns"
          :loading="generating"
          :initial-config="initialChartConfig"
          @generate="handleGenerate"
        />

        <section class="card task-card">
          <div class="card-header">
            <h3>任务概览</h3>
            <span class="status-badge" :class="currentTask.status">
              {{ statusLabel(currentTask.status) }}
            </span>
          </div>
          <dl class="summary-list">
            <div>
              <dt>任务类型</dt>
              <dd>{{ taskLabel }}</dd>
            </div>
            <div>
              <dt>创建时间</dt>
              <dd>{{ formatDate(currentTask.created_at) }}</dd>
            </div>
            <div>
              <dt>参数</dt>
              <dd>{{ formatObject(currentTask.parameters) }}</dd>
            </div>
          </dl>
          <div v-if="metricEntries.length" class="metric-grid">
            <div v-for="[key, value] in metricEntries" :key="key" class="metric-item">
              <span>{{ key }}</span>
              <strong>{{ formatValue(value) }}</strong>
            </div>
          </div>
        </section>
      </div>

      <section class="card chart-card">
        <div class="chart-header">
          <h3>{{ chartTitle }}</h3>
          <span v-if="generating" class="loading-text">生成中...</span>
        </div>
        <div v-if="chartError" class="inline-error">{{ chartError }}</div>
        <ChartPanel :option="currentOption || {}" :height="430" />
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import ChartConfig from '../components/ChartConfig.vue'
import ChartPanel from '../components/ChartPanel.vue'
import { useChartStore } from '../stores/chart'

const route = useRoute()
const chartStore = useChartStore()
const { currentOption, currentTask, loading, generating, error } = storeToRefs(chartStore)
const chartError = ref('')

const taskLabel = computed(() => {
  const labels = {
    kmeans: 'K-Means 聚类',
    regression: '线性回归',
  }
  return labels[currentTask.value?.task_type] || currentTask.value?.task_type || '分析任务'
})

const datasetName = computed(() => currentTask.value?.dataset_name || `数据集 #${currentTask.value?.dataset || '-'}`)

const chartColumns = computed(() => {
  const params = currentTask.value?.parameters || {}
  const values = [
    ...(Array.isArray(params.features) ? params.features : []),
    ...(Array.isArray(params.x_cols) ? params.x_cols : []),
    params.y_col,
  ]
  return [...new Set(values.filter(Boolean))]
})

const initialChartConfig = computed(() => ({
  title: `${taskLabel.value}结果`,
  x_column: chartColumns.value[0] || '',
  y_column: chartColumns.value[1] || '',
}))

const metricEntries = computed(() => Object.entries(currentTask.value?.metrics || {}).slice(0, 6))

const chartTitle = computed(() => currentOption.value?.title?.text || initialChartConfig.value.title)

onMounted(async () => {
  const taskId = route.params.taskId
  chartStore.clearChart()
  if (taskId) {
    await chartStore.fetchTask(taskId)
  }
})

async function handleGenerate({ chartType, config }) {
  chartError.value = ''
  try {
    const chartData = buildChartData(currentTask.value, chartType)
    await chartStore.generateChart(chartType, chartData, config)
  } catch (err) {
    chartError.value = err.response?.data?.error || '图表生成失败，请稍后重试'
  }
}

function buildChartData(task, chartType) {
  const result = task?.result_data || {}
  const metrics = task?.metrics || {}

  if (task?.task_type === 'regression') {
    return buildRegressionData(result, metrics, chartType)
  }

  if (task?.task_type === 'kmeans') {
    return buildKMeansData(result, metrics, chartType)
  }

  return buildGenericData(result, metrics, chartType)
}

function buildRegressionData(result, metrics, chartType) {
  const rows = result.actual_vs_predicted || []
  const predicted = rows.map((row) => Number(row.predicted || 0))
  const actual = rows.map((row) => Number(row.actual || 0))

  if (chartType === 'scatter') {
    return { points: rows.map((row) => [row.actual, row.predicted]) }
  }
  if (chartType === 'pie') {
    return {
      items: [
        { name: 'R2', value: Math.max(0, Number(result.r2_score ?? metrics.r2_score ?? 0)) },
        { name: 'RMSE', value: Math.max(0, Number(result.rmse ?? metrics.rmse ?? 0)) },
      ],
    }
  }
  if (chartType === 'boxplot') {
    return { box_data: [boxStats(actual), boxStats(predicted)] }
  }
  if (chartType === 'heatmap') {
    return { matrix: rows.slice(0, 80).map((row, index) => [index, 0, Math.abs(row.actual - row.predicted)]) }
  }
  if (chartType === 'bar') {
    return { labels: rows.map((_, index) => `#${index + 1}`), values: predicted }
  }
  return { values: predicted }
}

function buildKMeansData(result, metrics, chartType) {
  const sizes = result.cluster_sizes || []
  const centers = result.centers || []

  if (chartType === 'scatter') {
    return {
      points: centers.map((center, index) => [
        Number(center[0] ?? index),
        Number(center[1] ?? center[0] ?? 0),
      ]),
    }
  }
  if (chartType === 'pie') {
    return { items: sizes.map((value, index) => ({ name: `Cluster ${index + 1}`, value })) }
  }
  if (chartType === 'line' && Array.isArray(metrics.elbow)) {
    return { values: metrics.elbow.map((item) => item.inertia) }
  }
  if (chartType === 'heatmap') {
    return {
      matrix: centers.flatMap((center, rowIndex) => (
        center.map((value, colIndex) => [colIndex, rowIndex, value])
      )),
    }
  }
  if (chartType === 'boxplot') {
    return { box_data: [boxStats(sizes)] }
  }
  return { labels: sizes.map((_, index) => `Cluster ${index + 1}`), values: sizes }
}

function buildGenericData(result, metrics, chartType) {
  const entries = Object.entries({ ...metrics, ...result })
    .filter(([, value]) => typeof value === 'number')

  if (chartType === 'pie') {
    return { items: entries.map(([name, value]) => ({ name, value })) }
  }

  return {
    labels: entries.map(([name]) => name),
    values: entries.map(([, value]) => value),
    points: entries.map(([, value], index) => [index, value]),
  }
}

function boxStats(values) {
  const sorted = values.map(Number).filter((value) => Number.isFinite(value)).sort((a, b) => a - b)
  if (!sorted.length) return [0, 0, 0, 0, 0]
  return [
    sorted[0],
    percentile(sorted, 0.25),
    percentile(sorted, 0.5),
    percentile(sorted, 0.75),
    sorted[sorted.length - 1],
  ]
}

function percentile(sorted, ratio) {
  const index = (sorted.length - 1) * ratio
  const lower = Math.floor(index)
  const upper = Math.ceil(index)
  if (lower === upper) return sorted[lower]
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (index - lower)
}

function statusLabel(status) {
  const labels = {
    pending: '等待中',
    running: '运行中',
    done: '已完成',
    error: '失败',
  }
  return labels[status] || status || '-'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatObject(value) {
  if (!value || Object.keys(value).length === 0) return '-'
  return Object.entries(value).map(([key, item]) => `${key}: ${formatValue(item)}`).join('，')
}

function formatValue(value) {
  if (Array.isArray(value)) {
    if (value.every((item) => typeof item === 'object' && item !== null)) {
      return `${value.length} 项`
    }
    return value.join(', ')
  }
  if (typeof value === 'number') return Number.isInteger(value) ? value : value.toFixed(4)
  if (typeof value === 'object' && value !== null) return JSON.stringify(value)
  return value ?? '-'
}
</script>

<style scoped>
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.view-header h2 {
  margin-bottom: 0.2rem;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.88rem;
}

.view-header .btn {
  text-decoration: none;
  white-space: nowrap;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.task-card {
  margin-bottom: 0;
}

.card-header,
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.card-header h3,
.chart-header h3 {
  font-size: 1.05rem;
  margin: 0;
}

.summary-list {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.summary-list div {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 0.75rem;
}

.summary-list dt {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.summary-list dd {
  min-width: 0;
  overflow-wrap: anywhere;
  font-size: 0.9rem;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.metric-item {
  padding: 0.75rem;
  border-radius: 6px;
  background: #f8f9fa;
}

.metric-item span {
  display: block;
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-bottom: 0.2rem;
}

.metric-item strong {
  display: block;
  color: var(--primary);
  font-size: 1rem;
  overflow-wrap: anywhere;
}

.status-badge {
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #fff3e0;
  color: #e65100;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.done {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.error {
  background: #fdecea;
  color: var(--danger);
}

.status-badge.running {
  background: #e8f4fd;
  color: #1976d2;
}

.loading-text {
  color: var(--text-muted);
  font-size: 0.82rem;
}

.inline-error {
  padding: 0.65rem 0.8rem;
  margin-bottom: 0.75rem;
  border-radius: 6px;
  background: #fdecea;
  color: var(--danger);
  font-size: 0.85rem;
}

.empty {
  text-align: center;
  padding: 2.5rem;
  color: var(--text-muted);
}

.empty.error {
  color: var(--danger);
}

@media (max-width: 900px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .view-header,
  .card-header,
  .chart-header {
    flex-direction: column;
    align-items: stretch;
  }

  .summary-list div {
    grid-template-columns: 1fr;
    gap: 0.15rem;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
