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
        <div class="upload-icon">+</div>
        <p class="upload-text">点击或拖拽 CSV / Excel 文件到此处</p>
        <p class="upload-hint">支持 .csv .xlsx .xls 格式，文件大小不超过 20MB</p>
      </div>
      <div v-else class="upload-progress">
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
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  background: var(--card-bg);
}

.drop-zone.hovering {
  border-color: var(--primary);
  background: #f0f1ff;
}

.drop-zone.uploading {
  cursor: default;
  border-color: var(--primary);
}

.hidden-input { display: none; }

.upload-icon {
  font-size: 2.5rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.upload-text {
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 0.3rem;
}

.upload-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.upload-progress { width: 100%; }

.progress-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s;
  border-radius: 3px;
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
</style>