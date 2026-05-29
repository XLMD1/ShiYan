<template>
  <div class="page">
    <h2>上传数据</h2>

    <div class="card">
      <h3 class="section-title">一键抓取在线数据</h3>
      <div class="fetch-buttons">
        <button class="btn btn-primary" @click="doFetch('douban')" :disabled="!!fetching">
          {{ fetching === 'douban' ? '抓取中...' : '豆瓣电影 Top250' }}
        </button>
        <button class="btn btn-primary" @click="doFetch('bilibili')" :disabled="!!fetching">
          {{ fetching === 'bilibili' ? '抓取中...' : 'B站热门视频' }}
        </button>
        <button class="btn btn-primary" @click="doFetch('aqi')" :disabled="!!fetching">
          {{ fetching === 'aqi' ? '生成中...' : '空气质量模拟数据' }}
        </button>
        <button class="btn btn-primary" @click="doFetch('house')" :disabled="!!fetching">
          {{ fetching === 'house' ? '抓取中...' : '武汉二手房' }}
        </button>
      </div>
      <p class="fetch-hint">{{ fetchMsg }}</p>
    </div>

    <div class="card">
      <FileUploader
        :uploading="uploading"
        :progress="uploadProgress"
        :error="uploadError"
        @upload="handleUpload"
      />
    </div>

    <div v-if="uploadedDataset" ref="resultCard" class="card upload-result">
      <h3 class="section-title">上传成功</h3>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">文件名</span>
          <span class="info-value">{{ uploadedDataset.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">文件类型</span>
          <span class="info-value">{{ uploadedDataset.file_type.toUpperCase() }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">数据行数</span>
          <span class="info-value">{{ uploadedDataset.rows.toLocaleString() }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">列数</span>
          <span class="info-value">{{ (uploadedDataset.columns || []).length }}</span>
        </div>
        <div class="info-item" v-if="uploadedDataset.file_size">
          <span class="info-label">文件大小</span>
          <span class="info-value">{{ uploadedDataset.file_size }}</span>
        </div>
      </div>

      <div class="column-list" v-if="uploadedDataset.columns && uploadedDataset.columns.length">
        <span class="info-label">字段列表：</span>
        <span v-for="col in uploadedDataset.columns" :key="col" class="col-tag">{{ col }}</span>
      </div>

      <div class="result-actions">
        <button class="btn btn-primary" @click="openPreview(uploadedDataset.id)">查看数据预览</button>
        <router-link to="/" class="btn btn-success">返回工作台</router-link>
        <router-link :to="`/clean/${uploadedDataset.id}`" class="btn btn-primary">去清洗数据</router-link>
      </div>
    </div>

    <div v-if="showPreview && previewData" class="card preview-card">
      <div class="preview-header">
        <h3 class="section-title">数据预览</h3>
        <button class="btn-close" @click="showPreview = false">关闭预览</button>
      </div>
      <DataTable
        :columns="previewData.columns"
        :rows="previewData.rows"
        :total="previewData.total"
        :page="previewData.page"
        :page-size="previewData.page_size"
        :total-pages="previewData.total_pages"
        @page-change="(p) => openPreview(uploadedDataset.id, p)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useDatasetStore } from '../stores/dataset'
import { storeToRefs } from 'pinia'
import FileUploader from '../components/FileUploader.vue'
import DataTable from '../components/DataTable.vue'

const store = useDatasetStore()
const { uploading, previewData } = storeToRefs(store)

const resultCard = ref(null)
const uploadProgress = ref(0)
const uploadError = ref('')
const uploadedDataset = ref(null)
const showPreview = ref(false)

async function handleUpload(file) {
  uploadError.value = ''
  showPreview.value = false
  uploadProgress.value = 0
  try {
    const data = await store.uploadFile(file, (progress) => {
      uploadProgress.value = progress
    })
    uploadedDataset.value = data
    await nextTick()
    resultCard.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    const msg = e.response?.data?.error || '上传失败，请重试'
    uploadError.value = msg
  }
}

async function openPreview(id, page = 1) {
  showPreview.value = true
  await store.previewDataset(id, page)
}

const fetching = ref('')
const fetchMsg = ref('')

async function doFetch(source) {
  fetching.value = source
  fetchMsg.value = '正在抓取数据...'
  try {
    const data = await store.fetchData(source)
    uploadedDataset.value = data
    fetchMsg.value = '数据抓取成功！'
    await nextTick()
    resultCard.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    fetchMsg.value = e.response?.data?.error || e.message || '抓取失败'
  } finally {
    fetching.value = ''
  }
}
</script>

<style scoped>
.upload-result { margin-top: 1.5rem; }

.section-title {
  font-size: 1.05rem;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
}

.info-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text);
  word-break: break-all;
}

.column-list {
  margin-bottom: 1.25rem;
}

.col-tag {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  margin: 0.15rem 0.25rem;
  border-radius: 4px;
  background: #e8f4fd;
  color: #1976d2;
  font-size: 0.78rem;
}

.result-actions {
  display: flex;
  gap: 0.75rem;
}

.result-actions .btn {
  text-decoration: none;
  display: inline-block;
}

.fetch-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.fetch-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.preview-card {
  margin-top: 1rem;
}

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
