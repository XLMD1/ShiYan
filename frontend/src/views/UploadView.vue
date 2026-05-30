<template>
  <div class="page">
    <div class="upload-hero">
      <div>
        <p class="eyebrow">数据接入</p>
        <h2>上传数据</h2>
        <p class="page-subtitle">从在线数据源或本地文件创建数据集，进入清洗、分析和可视化流程。</p>
      </div>
      <div class="hero-meter">
        <span>CSV</span>
        <span>Excel</span>
        <strong>≤ 20MB</strong>
      </div>
    </div>

    <div class="card fetch-card">
      <div class="card-heading">
        <div>
          <h3 class="section-title">一键抓取在线数据</h3>
          <p class="section-desc">快速生成演示数据集，用于后续清洗和分析。</p>
        </div>
        <span v-if="fetching" class="fetch-status">任务运行中</span>
      </div>
      <div class="fetch-buttons">
        <button class="btn btn-primary fetch-btn" :class="{ active: fetching === 'douban' }" @click="doFetch('douban')" :disabled="!!fetching">
          <span class="fetch-icon">DB</span>
          <span>{{ fetching === 'douban' ? '抓取中...' : '豆瓣电影 Top250' }}</span>
        </button>
        <button class="btn btn-primary fetch-btn" :class="{ active: fetching === 'bilibili' }" @click="doFetch('bilibili')" :disabled="!!fetching">
          <span class="fetch-icon">BV</span>
          <span>{{ fetching === 'bilibili' ? '抓取中...' : 'B站热门视频' }}</span>
        </button>
        <button class="btn btn-primary fetch-btn" :class="{ active: fetching === 'aqi' }" @click="doFetch('aqi')" :disabled="!!fetching">
          <span class="fetch-icon">AQ</span>
          <span>{{ fetching === 'aqi' ? '生成中...' : '空气质量模拟数据' }}</span>
        </button>
        <button class="btn btn-primary fetch-btn" :class="{ active: fetching === 'house' }" @click="doFetch('house')" :disabled="!!fetching">
          <span class="fetch-icon">WH</span>
          <span>{{ fetching === 'house' ? '抓取中...' : '武汉二手房' }}</span>
        </button>
      </div>
      <p v-if="fetchMsg" class="fetch-hint">{{ fetchMsg }}</p>
    </div>

    <div class="card uploader-card">
      <FileUploader
        :uploading="uploading"
        :progress="uploadProgress"
        :error="uploadError"
        @upload="handleUpload"
      />
    </div>

    <div v-if="uploadedDataset" ref="resultCard" class="card upload-result">
      <div class="result-header">
        <div>
          <p class="eyebrow">数据集已创建</p>
          <h3 class="section-title">上传成功</h3>
        </div>
        <span class="success-badge">可继续处理</span>
      </div>
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
        <span class="info-label column-title">字段列表</span>
        <div class="column-tags">
          <span v-for="col in uploadedDataset.columns" :key="col" class="col-tag">{{ col }}</span>
        </div>
      </div>

      <div class="result-actions">
        <button class="btn btn-primary" @click="openPreview(uploadedDataset.id)">查看数据预览</button>
        <router-link to="/" class="btn btn-success">返回工作台</router-link>
        <router-link :to="`/clean/${uploadedDataset.id}`" class="btn btn-primary">去清洗数据</router-link>
      </div>
    </div>

    <div v-if="showPreview && previewData" class="card preview-card">
      <div class="preview-header">
        <div>
          <p class="eyebrow">Preview</p>
          <h3 class="section-title">数据预览</h3>
        </div>
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
.upload-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.upload-hero h2 {
  margin-bottom: 0.25rem;
}

.eyebrow {
  color: var(--accent-strong);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
  margin-bottom: 0.2rem;
}

.page-subtitle,
.section-desc {
  color: var(--text-muted);
  font-size: 0.88rem;
}

.hero-meter {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  justify-content: flex-end;
  min-width: 220px;
}

.hero-meter span,
.hero-meter strong {
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
  color: #415268;
  font-size: 0.75rem;
}

.hero-meter strong {
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.fetch-card,
.uploader-card,
.upload-result,
.preview-card {
  animation: card-in 420ms ease both;
}

.uploader-card { animation-delay: 50ms; }
.upload-result { margin-top: 1.5rem; animation-delay: 80ms; }
.preview-card { animation-delay: 90ms; }

.card-heading,
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.05rem;
  line-height: 1.25;
  margin-bottom: 0.2rem;
}

.fetch-status,
.success-badge {
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  white-space: nowrap;
  font-size: 0.74rem;
  font-weight: 800;
}

.fetch-status {
  background: var(--warning-soft);
  color: var(--warning);
}

.success-badge {
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, #f9fbfc, #f5f8fa);
  padding: 0.85rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: transform var(--motion-fast), border-color var(--motion-fast), background var(--motion-fast);
}

.info-item:hover {
  transform: translateY(-1px);
  border-color: var(--border-strong);
  background: #fff;
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

.column-title {
  margin-bottom: 0.45rem;
}

.column-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.col-tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border: 1px solid rgba(15,159,143,0.17);
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 0.78rem;
  transition: transform var(--motion-fast), background var(--motion-fast);
}

.col-tag:hover {
  background: #d8f2ef;
  transform: translateY(-1px);
}

.result-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.result-actions .btn {
  text-decoration: none;
  display: inline-block;
}

.fetch-buttons {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
}

.fetch-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 42px;
  padding-inline: 0.75rem;
}

.fetch-btn.active {
  background: var(--warning);
  border-color: var(--warning);
}

.fetch-icon {
  display: inline-grid;
  place-items: center;
  width: 26px;
  height: 24px;
  border-radius: 5px;
  background: rgba(255,255,255,0.13);
  font-size: 0.68rem;
  font-weight: 850;
}

.fetch-hint {
  margin-top: 0.75rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: #f8fafc;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.preview-card {
  margin-top: 1rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.btn-close {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card-bg);
  cursor: pointer;
  font-size: 0.8rem;
  color: var(--text);
  transition: background var(--motion-fast), transform var(--motion-fast), border-color var(--motion-fast);
}

.btn-close:hover {
  background: #f8fafc;
  border-color: var(--border-strong);
  transform: translateY(-1px);
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 920px) {
  .fetch-buttons {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 680px) {
  .upload-hero,
  .card-heading,
  .result-header,
  .preview-header {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-meter {
    justify-content: flex-start;
    min-width: 0;
  }

  .fetch-buttons {
    grid-template-columns: 1fr;
  }

  .result-actions .btn {
    width: 100%;
  }
}
</style>
