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
  DataZoomComponent,
  TitleComponent,
  ToolboxComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { enhanceChartOption } from '../utils/chartInteraction'

use([
  BarChart,
  BoxplotChart,
  HeatmapChart,
  LineChart,
  PieChart,
  ScatterChart,
  DataZoomComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
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

const interactiveOption = computed(() => enhanceChartOption(props.option))

const isEmpty = computed(() => {
  const series = interactiveOption.value?.series
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
  chart.setOption(interactiveOption.value, true)
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
  () => [interactiveOption.value, props.height],
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
    #fbfcfd,
    #fbfcfd 12px,
    #f2f7f8 12px,
    #f2f7f8 24px
  );
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}
</style>
