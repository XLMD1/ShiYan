<template>
  <div class="page">
    <h2>上传数据</h2>

    <div class="card">
      <FileUploader
        :uploading="uploading"
        :progress="uploadProgress"
        :error="uploadError"
        @upload="handleUpload"
      />
    </div>

    <div v-if="currentDataset" class="card upload-result">
      <h3 class="section-title">上传成功</h3>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">文件名</span>
          <span class="info-value">{{ currentDataset.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">文件类型</span>
          <span class="info-value">{{ currentDataset.file_type.toUpperCase() }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">数据行数</span>
          <span class="info-value">{{ currentDataset.rows.toLocaleString() }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">列数</span>
          <span class="info-value">{{ (currentDataset.columns || []).length }}</span>
        </div>
      </div>

      <div class="column-list" v-if="currentDataset.columns && currentDataset.columns.length">
        <span class="info-label">字段列表：</span>
        <span v-for="col in currentDataset.columns" :key="col" class="col-tag">{{ col }}</span>
      </div>

      <div class="result-actions">
        <button class="btn btn-primary" @click="loadPreview">查看数据预览</button>
        <router-link to="/" class="btn btn-success">返回工作台</router-link>
        <router-link :to="`/clean/${currentDataset.id}`" class="btn btn-primary">去清洗数据</router-link>
      </div>
    </div>

    <div v-if="previewData" class="card">
      <h3 class="section-title">数据预览</h3>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDatasetStore } from '../stores/dataset'
import { storeToRefs } from 'pinia'
import FileUploader from '../components/FileUploader.vue'
import DataTable from '../components/DataTable.vue'

const store = useDatasetStore()
const { uploading, currentDataset, previewData } = storeToRefs(store)

const uploadProgress = ref(0)
const uploadError = ref('')

async function handleUpload(file) {
  uploadError.value = ''
  uploadProgress.value = 0
  try {
    await store.uploadFile(file, (progress) => {
      uploadProgress.value = progress
    })
  } catch (e) {
    const msg = e.response?.data?.error || '上传失败，请重试'
    uploadError.value = msg
  }
}

async function loadPreview(pageOrEvent = 1) {
  console.log('=== loadPreview 被调用了！===')
  console.log('pageOrEvent:', pageOrEvent)
  
  // 如果是事件对象，用默认值 1
  let page = 1
  if (typeof pageOrEvent === 'number') {
    page = pageOrEvent
  }
  
  console.log('最终使用的 page:', page)
  console.log('currentDataset.value:', currentDataset.value)
  
  if (!currentDataset.value) {
    console.log('没有 currentDataset！')
    return
  }
  
  console.log('开始请求 previewDataset，id:', currentDataset.value.id)
  try {
    const result = await store.previewDataset(currentDataset.value.id, page)
    console.log('previewDataset 完成，结果:', result)
    console.log('previewData.value 现在是:', previewData.value)
  } catch (e) {
    console.error('previewDataset 出错了:', e)
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
  grid-template-columns: repeat(4, 1fr);
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
</style>