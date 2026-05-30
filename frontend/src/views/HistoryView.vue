<template>
  <div class="page">
    <div class="history-header">
      <h2>历史记录</h2>
      <button class="btn btn-primary" :disabled="loading" @click="loadTasks">
        {{ loading ? '刷新中...' : '刷新' }}
      </button>
    </div>

    <div v-if="loading" class="card empty">加载中...</div>
    <div v-else-if="error" class="card empty error">{{ error }}</div>
    <div v-else-if="tasks.length === 0" class="card empty">暂无分析历史</div>

    <div v-else class="card">
      <table>
        <thead>
          <tr>
            <th>任务类型</th>
            <th>数据集</th>
            <th>参数</th>
            <th>指标</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="task in tasks"
            :key="task.id"
            class="task-row"
            tabindex="0"
            @click="openVisualize(task)"
            @keydown.enter="openVisualize(task)"
          >
            <td class="type-cell">{{ taskTypeLabel(task.task_type) }}</td>
            <td>{{ task.dataset_name || `#${task.dataset}` }}</td>
            <td>
              <div class="chip-list">
                <span
                  v-for="[key, value] in objectEntries(task.parameters)"
                  :key="key"
                  class="data-chip"
                >
                  {{ key }}: {{ formatValue(value) }}
                </span>
                <span v-if="objectEntries(task.parameters).length === 0" class="muted">-</span>
              </div>
            </td>
            <td>
              <div class="chip-list">
                <span
                  v-for="[key, value] in objectEntries(task.metrics).slice(0, 3)"
                  :key="key"
                  class="metric-chip"
                >
                  {{ key }}: {{ formatValue(value) }}
                </span>
                <span v-if="objectEntries(task.metrics).length === 0" class="muted">-</span>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="task.status">
                {{ statusLabel(task.status) }}
              </span>
            </td>
            <td class="time-cell">{{ formatDate(task.created_at) }}</td>
            <td>
              <button class="btn-action" @click.stop="openVisualize(task)">可视化</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useChartStore } from '../stores/chart'

const router = useRouter()
const chartStore = useChartStore()
const { tasks, loading, error } = storeToRefs(chartStore)

onMounted(loadTasks)

async function loadTasks() {
  await chartStore.fetchTasks()
}

function openVisualize(task) {
  chartStore.setCurrentTask(task)
  router.push({ name: 'Visualize', params: { taskId: task.id } })
}

function taskTypeLabel(type) {
  const labels = {
    kmeans: 'K-Means 聚类',
    regression: '线性回归',
  }
  return labels[type] || type || '-'
}

function statusLabel(status) {
  const labels = {
    pending: '等待中',
    running: '运行中',
    done: '已完成',
    error: '失败',
  }
  return labels[status] || status || '-'
}

function objectEntries(value) {
  if (!value || typeof value !== 'object') return []
  return Object.entries(value)
}

function formatValue(value) {
  if (Array.isArray(value)) {
    if (value.every((item) => typeof item === 'object' && item !== null)) {
      return `${value.length} 项`
    }
    return value.join(', ')
  }
  if (typeof value === 'number') return Number.isInteger(value) ? value : value.toFixed(4)
  if (typeof value === 'object' && value !== null) return JSON.stringify(value)
  return value ?? '-'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.history-header h2 {
  margin-bottom: 0;
}

.history-header .btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.task-row {
  cursor: pointer;
}

.task-row:hover,
.task-row:focus {
  background: #f8f9fa;
  outline: none;
}

.type-cell {
  font-weight: 600;
  color: var(--accent-strong);
  white-space: nowrap;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  max-width: 280px;
}

.data-chip,
.metric-chip {
  display: inline-block;
  max-width: 100%;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.data-chip {
  border: 1px solid var(--border);
  background: #f8fafc;
  color: #4a5568;
}

.metric-chip {
  border: 1px solid rgba(15,159,143,0.17);
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.status-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #fff3e0;
  color: #e65100;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.done {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.error {
  background: #fdecea;
  color: var(--danger);
}

.status-badge.running {
  background: #e8f4fd;
  color: #1976d2;
}

.time-cell {
  color: var(--text-muted);
  font-size: 0.8rem;
  white-space: nowrap;
}

.btn-action {
  padding: 0.2rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card-bg);
  cursor: pointer;
  font-size: 0.75rem;
  color: var(--accent-strong);
  transition: transform var(--motion-fast), background var(--motion-fast), color var(--motion-fast), border-color var(--motion-fast);
}

.btn-action:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  transform: translateY(-1px);
}

.empty {
  text-align: center;
  padding: 2.5rem;
  color: var(--text-muted);
}

.empty.error {
  color: var(--danger);
}

.muted {
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .card {
    overflow-x: auto;
  }

  table {
    min-width: 860px;
  }
}
</style>
