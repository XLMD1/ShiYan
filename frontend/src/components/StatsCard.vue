<template>
  <div class="card">
    <div class="stats-grid">
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_rows ?? '-' }}</span>
        <span class="stat-label">总行数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_columns ?? '-' }}</span>
        <span class="stat-label">总列数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_missing ?? '-' }}</span>
        <span class="stat-label">缺失值总数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_outliers ?? '-' }}</span>
        <span class="stat-label">异常值总数</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    default: () => ({}),
  },
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
}
.stat-item {
  text-align: center;
  padding: 0.6rem;
}
.stat-value {
  display: block;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--primary);
}
.stat-label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}
</style>
