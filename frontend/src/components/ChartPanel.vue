<template>
  <div class="chart-shell" :style="{ minHeight: `${height}px` }">
    <div
      ref="chartRef"
      class="chart-container"
      :style="{ height: `${height}px` }"
      aria-label="图表预览"
    ></div>
    <div v-if="isEmpty" class="chart-empty">暂无图表数据</div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { init, use } from 'echarts/core'
import {
  BarChart,
  BoxplotChart,
  HeatmapChart,
  LineChart,
  PieChart,
  ScatterChart,
} from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([
  BarChart,
  BoxplotChart,
  HeatmapChart,
  LineChart,
  PieChart,
  ScatterChart,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  CanvasRenderer,
])

const props = defineProps({
  option: { type: Object, default: () => ({}) },
  height: { type: Number, default: 400 },
})

const chartRef = ref(null)
let chart = null

const isEmpty = computed(() => {
  const series = props.option?.series
  return !Array.isArray(series) || series.length === 0
})

function renderChart() {
  if (!chartRef.value) return

  if (isEmpty.value) {
    if (chart) chart.clear()
    return
  }

  if (!chart) {
    chart = init(chartRef.value)
  }
  chart.clear()
  chart.setOption(props.option, true)
  chart.resize()
}

function resizeChart() {
  if (chart) chart.resize()
}

onMounted(() => {
  nextTick(renderChart)
  window.addEventListener('resize', resizeChart)
})

watch(
  () => [props.option, props.height],
  () => nextTick(renderChart),
  { deep: true }
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.chart-shell {
  position: relative;
  width: 100%;
}

.chart-container {
  width: 100%;
}

.chart-empty {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  background: repeating-linear-gradient(
    -45deg,
    #fafafa,
    #fafafa 12px,
    #f5f6fa 12px,
    #f5f6fa 24px
  );
  border: 1px dashed var(--border);
  border-radius: 6px;
}
</style>
