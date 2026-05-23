<template>
  <div class="page">
    <div class="dashboard-header">
      <h2>工作台</h2>
      <router-link to="/upload" class="btn btn-primary">上传新数据</router-link>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-num">{{ datasets.length }}</span>
        <span class="stat-label">数据集总数</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{{ totalRows }}</span>
        <span class="stat-label">累计数据行数</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{{ cleanedCount }}</span>
        <span class="stat-label">已清洗数据集</span>
      </div>
    </div>

    <div class="card">
      <h3 class="section-title">我的数据集</h3>
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="datasets.length === 0" class="empty">
        <p>暂无数据集，点击上方按钮上传您的第一个文件</p>
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>名称</th>
            <th>类型</th>
            <th>行数</th>
            <th>列数</th>
            <th>状态</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ds in datasets" :key="ds.id">
            <td class="name-cell">{{ ds.name }}</td>
            <td>
              <span class="type-badge" :class="ds.file_type">{{ ds.file_type.toUpperCase() }}</span>
            </td>
            <td>{{ ds.rows.toLocaleString() }}</td>
            <td>{{ (ds.columns || []).length }}</td>
            <td>
              <span class="status-badge" :class="{ cleaned: ds.is_cleaned }">
                {{ ds.is_cleaned ? '已清洗' : '待清洗' }}
              </span>
            </td>
            <td class="time-cell">{{ formatDate(ds.uploaded_at) }}</td>
            <td class="action-cell">
              <button class="btn-action" @click="openPreview(ds.id)">预览</button>
              <router-link :to="`/clean/${ds.id}`" class="btn-action">清洗</router-link>
              <router-link :to="`/analysis/${ds.id}`" class="btn-action">分析</router-link>
              <button class="btn-action" @click="handleExport(ds.id, ds.file_type)">导出</button>
              <button class="btn-action danger" @click="handleDelete(ds)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showPreview && previewData" class="card">
      <div class="preview-header">
        <h3 class="section-title">数据预览 - {{ previewDatasetName }}</h3>
        <button class="btn-close" @click="showPreview = false">关闭预览</button>
      </div>
      <DataTable
        :columns="previewData.columns"
        :rows="previewData.rows"
        :total="previewData.total"
        :page="previewData.page"
        :page-size="previewData.page_size"
        :total-pages="previewData.total_pages"
        @page-change="(p) => openPreview(currentPreviewId, p)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDatasetStore } from '../stores/dataset'
import { storeToRefs } from 'pinia'
import DataTable from '../components/DataTable.vue'

const store = useDatasetStore()
const { datasets, loading, previewData } = storeToRefs(store)

const showPreview = ref(false)
const currentPreviewId = ref(null)
const previewDatasetName = ref('')

const totalRows = computed(() => datasets.value.reduce((sum, d) => sum + d.rows, 0))
const cleanedCount = computed(() => datasets.value.filter((d) => d.is_cleaned).length)

onMounted(() => {
  store.fetchDatasets()
})

async function openPreview(id, page = 1) {
  currentPreviewId.value = id
  showPreview.value = true
  await store.previewDataset(id, page)
  const ds = datasets.value.find((d) => d.id === id)
  if (ds) previewDatasetName.value = ds.name
}

function handleExport(id, fileType) {
  const url = store.getExportUrl(id, fileType === 'csv' ? 'csv' : 'xlsx')
  window.open(url, '_blank')
}

async function handleDelete(ds) {
  if (!confirm(`确定要删除数据集 "${ds.name}" 吗？此操作不可撤销。`)) return
  await store.deleteDataset(ds.id)
  if (currentPreviewId.value === ds.id) {
    showPreview.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.dashboard-header h2 { margin-bottom: 0; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--card-bg);
  padding: 1.25rem;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 0.3rem;
}

.section-title {
  font-size: 1.05rem;
  margin-bottom: 0.75rem;
}

.empty {
  text-align: center;
  padding: 2.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.name-cell {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #e8f4fd;
  color: #1976d2;
}

.type-badge.xlsx { background: #e8f5e9; color: #2e7d32; }

.status-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  background: #fff3e0;
  color: #e65100;
}

.status-badge.cleaned { background: #e8f5e9; color: #2e7d32; }

.time-cell {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.action-cell {
  white-space: nowrap;
}

.btn-action {
  padding: 0.2rem 0.5rem;
  margin-right: 0.25rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: var(--card-bg);
  cursor: pointer;
  font-size: 0.75rem;
  color: var(--primary);
  text-decoration: none;
  display: inline-block;
}

.btn-action:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

.btn-action.danger { color: var(--danger); border-color: var(--danger); }

.btn-action.danger:hover { background: var(--danger); color: #fff; }

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  padding: 0.3rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--card-bg);
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-close:hover { background: #f0f0f0; }
</style>