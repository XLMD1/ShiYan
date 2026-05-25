<template>
  <form class="card chart-config" @submit.prevent="submit">
    <div class="config-header">
      <h3>图表配置</h3>
      <span class="chart-type">{{ selectedChartLabel }}</span>
    </div>

    <div class="form-grid">
      <label class="form-field">
        <span>图表类型</span>
        <select v-model="form.chartType">
          <option v-for="item in chartTypes" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </label>

      <label class="form-field">
        <span>X 轴字段</span>
        <select v-model="form.xColumn">
          <option value="">自动</option>
          <option v-for="column in normalizedColumns" :key="column" :value="column">
            {{ column }}
          </option>
        </select>
      </label>

      <label class="form-field">
        <span>Y 轴字段</span>
        <select v-model="form.yColumn">
          <option value="">自动</option>
          <option v-for="column in normalizedColumns" :key="column" :value="column">
            {{ column }}
          </option>
        </select>
      </label>

      <label class="form-field title-field">
        <span>标题</span>
        <input v-model.trim="form.title" type="text" placeholder="分析图表" />
      </label>

      <label class="form-field color-field">
        <span>颜色</span>
        <input v-model="form.color" type="color" aria-label="图表颜色" />
      </label>
    </div>

    <button class="btn btn-primary generate-btn" type="submit" :disabled="loading">
      {{ loading ? '生成中...' : '生成图表' }}
    </button>
  </form>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['generate'])

const chartTypes = [
  { value: 'scatter', label: '散点图' },
  { value: 'line', label: '折线图' },
  { value: 'bar', label: '柱状图' },
  { value: 'heatmap', label: '热力图' },
  { value: 'boxplot', label: '箱线图' },
  { value: 'pie', label: '饼图' },
]

const form = reactive({
  chartType: props.initialConfig.chart_type || 'scatter',
  xColumn: props.initialConfig.x_column || '',
  yColumn: props.initialConfig.y_column || '',
  title: props.initialConfig.title || '分析图表',
  color: props.initialConfig.color || '#1976d2',
})

const normalizedColumns = computed(() => (
  [...new Set(props.columns.filter(Boolean).map((column) => String(column)))]
))

const selectedChartLabel = computed(() => {
  return chartTypes.find((item) => item.value === form.chartType)?.label || '图表'
})

watch(
  () => normalizedColumns.value,
  (columns) => {
    if (!form.xColumn && columns[0]) form.xColumn = columns[0]
    if (!form.yColumn && columns[1]) form.yColumn = columns[1]
  },
  { immediate: true }
)

function submit() {
  emit('generate', {
    chartType: form.chartType,
    config: {
      chart_type: form.chartType,
      x_column: form.xColumn,
      y_column: form.yColumn,
      title: form.title || selectedChartLabel.value,
      color: form.color,
      itemStyle: { color: form.color },
    },
  })
}
</script>

<style scoped>
.chart-config {
  margin-bottom: 0;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.config-header h3 {
  font-size: 1.05rem;
  margin: 0;
}

.chart-type {
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #e8f4fd;
  color: #1976d2;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.form-field span {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.title-field {
  grid-column: span 2;
}

.color-field input {
  min-height: 38px;
  padding: 0.2rem;
}

.generate-btn {
  width: 100%;
  margin-top: 1rem;
}

.generate-btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .title-field {
    grid-column: auto;
  }
}
</style>
