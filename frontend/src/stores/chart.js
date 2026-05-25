import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

function normalizeList(payload) {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  return []
}

async function requestWithFallback(method, endpoints, payload) {
  let lastError = null

  for (const endpoint of endpoints) {
    try {
      if (method === 'post') {
        return await api.post(endpoint, payload)
      }
      return await api.get(endpoint)
    } catch (error) {
      lastError = error
      if (error.response?.status !== 404) break
    }
  }

  throw lastError
}

export const useChartStore = defineStore('chart', () => {
  const currentOption = ref(null)
  const chartConfigs = ref([])
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const generating = ref(false)
  const error = ref('')

  async function generateChart(chartType, data, config) {
    generating.value = true
    error.value = ''

    try {
      const payload = {
        chart_type: chartType,
        data,
        config: {
          ...config,
          chart_type: chartType,
        },
      }
      const { data: response } = await requestWithFallback(
        'post',
        ['/charts/generate/', '/analysis/charts/generate/'],
        payload
      )

      currentOption.value = response.option
      if (response.chart_id) {
        chartConfigs.value.unshift({
          id: response.chart_id,
          chart_type: chartType,
          config: payload.config,
        })
      }
      return response
    } catch (err) {
      error.value = err.response?.data?.error || '图表生成失败'
      throw err
    } finally {
      generating.value = false
    }
  }

  async function fetchChartConfigs() {
    const { data } = await requestWithFallback(
      'get',
      ['/charts/configs/', '/analysis/charts/configs/']
    )
    chartConfigs.value = normalizeList(data)
    return chartConfigs.value
  }

  async function fetchTasks() {
    loading.value = true
    error.value = ''

    try {
      const { data } = await api.get('/analysis/tasks/')
      tasks.value = normalizeList(data)
      return tasks.value
    } catch (err) {
      error.value = err.response?.data?.error || '历史记录加载失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(id) {
    loading.value = true
    error.value = ''

    try {
      const { data } = await api.get(`/analysis/tasks/${id}/`)
      currentTask.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.error || '分析任务加载失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentTask(task) {
    currentTask.value = task
  }

  function clearChart() {
    currentOption.value = null
  }

  return {
    currentOption,
    chartConfigs,
    tasks,
    currentTask,
    loading,
    generating,
    error,
    generateChart,
    fetchChartConfigs,
    fetchTasks,
    fetchTask,
    setCurrentTask,
    clearChart,
  }
})
