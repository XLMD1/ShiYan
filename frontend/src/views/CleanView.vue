<template>
  <div class="page">
    <h2>数据清洗</h2>

    <!-- 加载中 -->
    <div v-if="loading" class="card">
      <p class="text-muted">正在加载数据...</p>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="card">
      <p class="text-danger">{{ error }}</p>
      <button class="btn btn-primary" @click="$router.push('/')">返回工作台</button>
    </div>

    <!-- 主内容 -->
    <template v-else-if="dataset">
      <!-- 数据集信息 -->
      <div class="card">
        <h3>{{ dataset.name }}</h3>
        <p class="text-muted">{{ dataset.file_type }} · {{ dataset.rows }} 行 · {{ dataset.columns?.length }} 列</p>
      </div>

      <!-- 统计概览 -->
      <StatsCard v-if="stats" :stats="stats" />

      <!-- 列详情 -->
      <div v-if="stats" class="card">
        <h3 style="margin-bottom: 0.8rem">列统计信息</h3>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>列名</th>
                <th>类型</th>
                <th>缺失数</th>
                <th>均值</th>
                <th>标准差</th>
                <th>最小值</th>
                <th>最大值</th>
                <th>异常值(IQR)</th>
                <th>清洗方式</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="col in stats.columns" :key="col.name">
                <td><strong>{{ col.name }}</strong></td>
                <td>{{ col.type === 'numeric' ? '数值' : '文本' }}</td>
                <td :class="{ 'text-danger': col.missing > 0 }">{{ col.missing }}</td>
                <td>{{ col.mean ?? '-' }}</td>
                <td>{{ col.std ?? '-' }}</td>
                <td>{{ col.min ?? '-' }}</td>
                <td>{{ col.max ?? '-' }}</td>
                <td>{{ col.outliers_iqr ?? '-' }}</td>
                <td>
                  <select
                    v-model="cleanConfig[col.name]"
                    :disabled="cleaning"
                    style="min-width: 130px"
                  >
                    <option value="none">不处理</option>
                    <option v-if="col.missing > 0" value="drop">删除含缺失行</option>
                    <option v-if="col.missing > 0 && col.type === 'numeric'" value="mean">均值填充</option>
                    <option v-if="col.missing > 0 && col.type === 'numeric'" value="median">中位数填充</option>
                    <option v-if="col.missing > 0" value="mode">众数填充</option>
                  </select>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div v-if="stats" style="margin-top: 1rem; display: flex; gap: 0.8rem; flex-wrap: wrap">
        <button
          class="btn btn-success"
          :disabled="cleaning || !hasCleanActions"
          @click="executeClean"
        >
          {{ cleaning ? '清洗中...' : '执行清洗' }}
        </button>
        <button
          v-if="report"
          class="btn btn-primary"
          @click="$router.push(`/analysis/${dataset.id}`)"
        >
          前往分析 →
        </button>
        <button class="btn" @click="$router.push('/')" style="background:#eee">
          返回工作台
        </button>
      </div>

      <!-- 清洗报告 -->
      <div v-if="report" class="card" style="margin-top: 1rem">
        <h3 style="margin-bottom: 0.8rem">清洗报告</h3>
        <div class="report-summary">
          <p><strong>清洗前：</strong>{{ report.before.rows }} 行</p>
          <p><strong>清洗后：</strong>{{ report.after.rows }} 行</p>
        </div>
        <div v-if="report.actions.length > 0" style="margin-top: 0.8rem">
          <h4 style="margin-bottom: 0.4rem">执行操作：</h4>
          <ul class="action-list">
            <li v-for="(act, i) in report.actions" :key="i">
              {{ act.description }}
              <span v-if="act.before !== undefined" class="text-muted">
                （{{ act.before }} → {{ act.after ?? 0 }}）
              </span>
            </li>
          </ul>
        </div>
        <div v-else style="margin-top: 0.5rem">
          <p class="text-muted">无需执行任何清洗操作</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useDatasetStore } from '@/stores/dataset'
import api from '@/api'
import StatsCard from '@/components/StatsCard.vue'

const route = useRoute()
const datasetStore = useDatasetStore()

const dataset = ref(null)
const stats = ref(null)
const cleanConfig = ref({})
const cleaning = ref(false)
const report = ref(null)
const loading = ref(true)
const error = ref(null)

const hasCleanActions = computed(() => {
  return Object.values(cleanConfig.value).some(v => v !== 'none')
})

onMounted(async () => {
  const id = route.params.id
  try {
    dataset.value = await datasetStore.fetchDataset(id)
  } catch {
    error.value = '加载数据集失败'
    loading.value = false
    return
  }

  try {
    const res = await api.get(`/analysis/stats/${id}/`)
    stats.value = res.data
    // 初始化清洗配置
    for (const col of res.data.columns) {
      cleanConfig.value[col.name] = 'none'
    }
  } catch (e) {
    error.value = e.response?.data?.error || '加载统计信息失败'
  } finally {
    loading.value = false
  }
})

async function executeClean() {
  cleaning.value = true
  const columns = Object.entries(cleanConfig.value)
    .filter(([, action]) => action !== 'none')
    .map(([column, action]) => ({ column, missing_action: action }))

  try {
    const res = await api.post(`/analysis/clean/${dataset.value.id}/`, { columns })
    report.value = res.data.report
    if (res.data.rows) {
      dataset.value.rows = res.data.rows
      dataset.value.columns = res.data.columns
      dataset.value.is_cleaned = true
    }
  } catch (e) {
    error.value = e.response?.data?.error || '清洗失败'
  } finally {
    cleaning.value = false
  }
}
</script>

<style scoped>
.text-muted { color: var(--text-muted) }
.text-danger { color: var(--danger); font-weight: 600 }
.table-scroll { overflow-x: auto }
.report-summary {
  display: flex;
  gap: 2rem;
}
.action-list {
  padding-left: 1.2rem;
  line-height: 1.8;
}
</style>
