<template>
  <div class="page">
    <div class="page-header">
      <h2>数据清洗</h2>
      <button class="btn btn-secondary" @click="$router.push('/')">
        返回工作台
      </button>
    </div>

    <div v-if="loading" class="card loading-card">
      <div class="spinner"></div>
      <p>正在加载数据...</p>
    </div>

    <div v-else-if="error" class="card error-card">
      <div class="error-icon">!</div>
      <p class="error-text">{{ error }}</p>
      <button class="btn btn-primary" @click="$router.push('/')">返回工作台</button>
    </div>

    <template v-else-if="dataset">
      <div class="dataset-info-card">
        <div class="info-left">
          <h3>{{ dataset.name }}</h3>
          <div class="info-tags">
            <span class="tag tag-type">{{ dataset.file_type.toUpperCase() }}</span>
            <span class="tag tag-rows">{{ dataset.rows.toLocaleString() }} 行</span>
            <span class="tag tag-cols">{{ dataset.columns?.length }} 列</span>
            <span v-if="dataset.file_size" class="tag tag-size">{{ dataset.file_size }}</span>
            <span class="tag" :class="dataset.is_cleaned ? 'tag-cleaned' : 'tag-pending'">
              {{ dataset.is_cleaned ? '已清洗' : '待清洗' }}
            </span>
          </div>
        </div>
        <div class="info-actions">
          <button class="btn btn-outline" @click="togglePreview">
            {{ showPreview ? '关闭预览' : '查看预览' }}
          </button>
          <button
            v-if="dataset.is_cleaned"
            class="btn btn-warning"
            @click="resetToOriginal"
          >
            返回原文件重新清洗
          </button>
        </div>
      </div>

      <div v-if="showPreview && previewData" class="card preview-card">
        <div class="preview-header">
          <h3>
            数据预览
            <span v-if="previewLabel" class="preview-label">({{ previewLabel }})</span>
          </h3>
        </div>
        <DataTable
          :columns="previewData.columns"
          :rows="previewData.rows"
          :total="previewData.total"
          :page="previewData.page"
          :page-size="previewData.page_size"
          :total-pages="previewData.total_pages"
          @page-change="(p) => loadPreview(p)"
        />
      </div>

      <StatsCard v-if="stats" :stats="stats" />

      <div v-if="stats" class="card column-card">
        <h3 class="section-title">列统计信息</h3>
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
                <th>异常值</th>
                <th>清洗方式</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="col in stats.columns" :key="col.name">
                <td><strong>{{ col.name }}</strong></td>
                <td>
                  <span class="type-badge" :class="col.type === 'numeric' ? 'numeric' : 'text'">
                    {{ col.type === 'numeric' ? '数值' : '文本' }}
                  </span>
                </td>
                <td :class="{ 'text-danger': col.missing > 0 }">{{ col.missing }}</td>
                <td>{{ col.mean != null ? Number(col.mean).toFixed(2) : '-' }}</td>
                <td>{{ col.std != null ? Number(col.std).toFixed(2) : '-' }}</td>
                <td>{{ col.min != null ? Number(col.min).toFixed(2) : '-' }}</td>
                <td>{{ col.max != null ? Number(col.max).toFixed(2) : '-' }}</td>
                <td>{{ col.outliers_iqr ?? '-' }}</td>
                <td>
                  <select
                    v-model="cleanConfig[col.name]"
                    :disabled="cleaning"
                    class="clean-select"
                  >
                    <option value="none">不处理</option>
                    <option v-if="col.missing > 0" value="drop">删除缺失行</option>
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

      <div v-if="stats" class="action-buttons">
        <button
          class="btn btn-success btn-lg"
          :disabled="cleaning || !hasCleanActions"
          @click="executeClean"
        >
          <span v-if="cleaning" class="btn-spinner"></span>
          {{ cleaning ? '清洗中...' : '执行清洗' }}
        </button>
        <button
          v-if="report"
          class="btn btn-primary btn-lg"
          @click="$router.push(`/analysis/${dataset.id}`)"
        >
          前往分析 →
        </button>
      </div>

      <div v-if="report" class="card report-card">
        <h3 class="section-title">清洗报告</h3>
        <div class="report-summary">
          <div class="report-stat">
            <span class="report-label">清洗前</span>
            <span class="report-value">{{ report.before.rows }} 行</span>
          </div>
          <div class="report-arrow">→</div>
          <div class="report-stat">
            <span class="report-label">清洗后</span>
            <span class="report-value success">{{ report.after.rows }} 行</span>
          </div>
          <div class="report-stat" v-if="report.before.rows - report.after.rows > 0">
            <span class="report-label">删除</span>
            <span class="report-value danger">-{{ report.before.rows - report.after.rows }} 行</span>
          </div>
        </div>
        <div v-if="report.actions.length > 0" class="actions-list">
          <h4>执行操作：</h4>
          <ul>
            <li v-for="(act, i) in report.actions" :key="i">
              {{ act.description }}
              <span v-if="act.before !== undefined" class="action-detail">
                ({{ act.before }} → {{ act.after ?? 0 }})
              </span>
            </li>
          </ul>
        </div>
        <div v-else class="no-actions">
          <p>无需执行任何清洗操作</p>
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
import DataTable from '@/components/DataTable.vue'

const route = useRoute()
const datasetStore = useDatasetStore()

const dataset = ref(null)
const stats = ref(null)
const cleanConfig = ref({})
const cleaning = ref(false)
const report = ref(null)
const loading = ref(true)
const error = ref(null)
const showPreview = ref(false)
const previewData = ref(null)
const previewLabel = ref('')

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
    for (const col of res.data.columns) {
      cleanConfig.value[col.name] = 'none'
    }
  } catch (e) {
    error.value = e.response?.data?.error || '加载统计信息失败'
  } finally {
    loading.value = false
  }
})

async function togglePreview() {
  showPreview.value = !showPreview.value
  if (showPreview.value) {
    await loadPreview(1)
  }
}

async function loadPreview(page = 1) {
  if (!dataset.value) return
  try {
    const res = await api.get(`/datasets/${dataset.value.id}/preview/`, {
      params: { page, page_size: 100 },
    })
    previewData.value = res.data
    previewLabel.value = dataset.value.is_cleaned ? '清洗后数据' : '原始数据'
  } catch (e) {
    console.error('预览加载失败:', e)
  }
}

async function resetToOriginal() {
  if (!confirm('确定要返回原文件并重新清洗吗？清洗后的数据将被覆盖。')) return
  try {
    const res = await api.post(`/analysis/reset/${dataset.value.id}/`)
    if (res.data.dataset) {
      dataset.value = res.data.dataset
      report.value = null
      showPreview.value = false
      previewData.value = null
      const statsRes = await api.get(`/analysis/stats/${dataset.value.id}/`)
      stats.value = statsRes.data
      for (const col of statsRes.data.columns) {
        cleanConfig.value[col.name] = 'none'
      }
    }
  } catch (e) {
    alert(e.response?.data?.error || '重置失败')
  }
}

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
    if (showPreview.value) {
      await loadPreview(previewData.value?.page || 1)
    }
  } catch (e) {
    error.value = e.response?.data?.error || '清洗失败'
  } finally {
    cleaning.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin: 0;
}

.loading-card, .error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--danger);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.error-text {
  color: var(--danger);
  margin-bottom: 1rem;
}

.dataset-info-card {
  background: var(--card-bg);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.info-left h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.15rem;
}

.info-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag-type {
  background: #e8f4fd;
  color: #1976d2;
}

.tag-rows, .tag-cols {
  background: #f3e5f5;
  color: #7b1fa2;
}

.tag-size {
  background: #fff3e0;
  color: #e65100;
}

.tag-pending {
  background: #fff3e0;
  color: #e65100;
}

.tag-cleaned {
  background: #e8f5e9;
  color: #2e7d32;
}

.info-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.preview-card {
  margin-bottom: 1.25rem;
}

.preview-header {
  margin-bottom: 1rem;
}

.preview-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: normal;
}

.column-card {
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 1.05rem;
  margin-bottom: 1rem;
  color: var(--text);
}

.table-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

th, td {
  padding: 0.65rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-size: 0.82rem;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: var(--text);
}

tr:hover td {
  background: #f8f9ff;
}

.type-badge {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
  font-size: 0.72rem;
  font-weight: 500;
}

.type-badge.numeric {
  background: #e3f2fd;
  color: #1565c0;
}

.type-badge.text {
  background: #fce4ec;
  color: #c2185b;
}

.text-danger {
  color: var(--danger);
  font-weight: 600;
}

.clean-select {
  padding: 0.3rem 0.5rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--card-bg);
  font-size: 0.78rem;
  min-width: 110px;
  cursor: pointer;
}

.clean-select:focus {
  outline: none;
  border-color: var(--primary);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.btn-lg {
  padding: 0.7rem 1.5rem;
  font-size: 0.95rem;
}

.btn-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.report-card {
  margin-bottom: 1.25rem;
}

.report-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.report-stat {
  text-align: center;
}

.report-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.2rem;
}

.report-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
}

.report-value.success {
  color: var(--success);
}

.report-value.danger {
  color: var(--danger);
}

.report-arrow {
  font-size: 1.2rem;
  color: var(--text-muted);
}

.actions-list h4 {
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: var(--text);
}

.actions-list ul {
  padding-left: 1.2rem;
  line-height: 1.8;
}

.actions-list li {
  font-size: 0.85rem;
}

.action-detail {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.no-actions p {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
}

.btn-outline:hover {
  background: var(--border);
}

.btn-warning {
  background: #ff9800;
  color: white;
  border-color: #ff9800;
}

.btn-warning:hover {
  background: #f57c00;
  border-color: #f57c00;
}

@media (max-width: 768px) {
  .dataset-info-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .info-actions {
    width: 100%;
  }

  .info-actions .btn {
    flex: 1;
  }
}
</style>
