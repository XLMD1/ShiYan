<template>
  <div class="file-uploader">
    <div
      class="drop-zone"
      :class="{ hovering: isHovering, uploading: uploading }"
      @dragover.prevent="isHovering = true"
      @dragleave.prevent="isHovering = false"
      @drop.prevent="handleDrop"
      @click="triggerInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".csv,.xlsx,.xls"
        class="hidden-input"
        @change="handleFileChange"
      />
      <div v-if="!uploading" class="upload-content">
        <div class="upload-icon">CSV</div>
        <p class="upload-text">点击或拖拽 CSV / Excel 文件到此处</p>
        <p class="upload-hint">
          <span>.csv</span>
          <span>.xlsx</span>
          <span>.xls</span>
          <span>≤ 20MB</span>
        </p>
      </div>
      <div v-else class="upload-progress">
        <p class="progress-title">正在上传并解析数据</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">上传中 {{ progress }}%</p>
      </div>
    </div>
    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  uploading: { type: Boolean, default: false },
  progress: { type: Number, default: 0 },
  error: { type: String, default: '' },
})

const emit = defineEmits(['upload'])

const fileInput = ref(null)
const isHovering = ref(false)

function triggerInput() {
  if (!props.uploading) {
    fileInput.value.click()
  }
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    if (file.size > 20 * 1024 * 1024) {
      emit('error', '文件大小超过 20MB 限制')
      return
    }
    emit('upload', file)
  }
}

function handleDrop(e) {
  isHovering.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    if (file.size > 20 * 1024 * 1024) {
      emit('error', '文件大小超过 20MB 限制')
      return
    }
    emit('upload', file)
  }
}
</script>

<style scoped>
.file-uploader { width: 100%; }

.drop-zone {
  position: relative;
  overflow: hidden;
  border: 1.5px dashed var(--border-strong);
  border-radius: var(--radius);
  padding: 3.3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--motion-base), background var(--motion-base), box-shadow var(--motion-base), transform var(--motion-base);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.95), rgba(248,251,252,0.95)),
    repeating-linear-gradient(90deg, transparent 0 28px, rgba(15,159,143,0.04) 28px 29px);
}

.drop-zone::before {
  content: "";
  position: absolute;
  inset: 12px;
  border-radius: 7px;
  border: 1px solid rgba(15,159,143,0.08);
  pointer-events: none;
}

.drop-zone.hovering {
  border-color: var(--accent);
  background:
    linear-gradient(180deg, #ffffff, #f0fbf9),
    repeating-linear-gradient(90deg, transparent 0 28px, rgba(15,159,143,0.07) 28px 29px);
  box-shadow: inset 0 0 0 1px rgba(15,159,143,0.13), 0 18px 36px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.drop-zone.uploading {
  cursor: default;
  border-color: var(--accent);
  background: #f8fcfb;
}

.hidden-input { display: none; }

.upload-content,
.upload-progress {
  position: relative;
  z-index: 1;
}

.upload-icon {
  display: inline-grid;
  place-items: center;
  width: 58px;
  height: 58px;
  margin-bottom: 0.8rem;
  border: 1px solid rgba(15,159,143,0.2);
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 0.82rem;
  font-weight: 800;
  box-shadow: 0 12px 24px rgba(15,159,143,0.12);
}

.upload-text {
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.upload-hint {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}

.upload-hint span {
  padding: 0.12rem 0.42rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #fff;
}

.upload-progress { width: 100%; }

.progress-title {
  margin-bottom: 0.7rem;
  color: var(--text);
  font-weight: 700;
}

.progress-bar {
  height: 8px;
  background: #e7edf2;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 0.6rem;
}

.progress-fill {
  position: relative;
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #f0a536);
  transition: width 0.3s;
  border-radius: 999px;
}

.progress-fill::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.38), transparent);
  animation: shimmer 1.2s linear infinite;
}

.progress-text {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.error-msg {
  color: var(--danger);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

@keyframes shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}
</style>
