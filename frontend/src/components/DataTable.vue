<template>
  <div class="data-table-wrapper">
    <div v-if="loading" class="table-loading">加载中...</div>
    <div v-else-if="!columns.length" class="table-empty">暂无数据</div>
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th class="row-num">#</th>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
            <td class="row-num">{{ (page - 1) * pageSize + rowIndex + 1 }}</td>
            <td v-for="(col, colIndex) in columns" :key="colIndex">
              {{ formatCell(row[colIndex]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="totalPages > 1" class="pagination">
      <button class="btn-page" :disabled="page <= 1" @click="$emit('page-change', page - 1)">上一页</button>
      <span class="page-info">第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
      <button class="btn-page" :disabled="page >= totalPages" @click="$emit('page-change', page + 1)">下一页</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 100 },
  totalPages: { type: Number, default: 1 },
  loading: { type: Boolean, default: false },
})

defineEmits(['page-change'])

function formatCell(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    if (Number.isInteger(value)) return value
    return Number(value.toFixed(4))
  }
  return String(value)
}
</script>

<style scoped>
.data-table-wrapper {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

th, td {
  padding: 0.64rem 0.78rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-size: 0.82rem;
  white-space: nowrap;
}

th {
  background: linear-gradient(180deg, #f9fbfc, #f3f7f9);
  color: #3a4758;
  font-weight: 750;
  position: sticky;
  top: 0;
  z-index: 1;
}

tr {
  transition: background var(--motion-fast);
}

tr:hover td { background: #f6fbfa; }

.row-num {
  width: 50px;
  color: var(--text-muted);
  text-align: center;
  font-size: 0.78rem;
}

.table-loading, .table-empty {
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.9), rgba(248,251,252,0.9)),
    repeating-linear-gradient(-45deg, transparent 0 18px, rgba(15,159,143,0.035) 18px 19px);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border);
}

.btn-page {
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card-bg);
  cursor: pointer;
  font-size: 0.8rem;
  color: var(--text);
  transition: background var(--motion-fast), color var(--motion-fast), border-color var(--motion-fast), transform var(--motion-fast);
}

.btn-page:hover:not(:disabled) {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  transform: translateY(-1px);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
