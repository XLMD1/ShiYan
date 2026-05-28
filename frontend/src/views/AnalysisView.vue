<template>
  <div class="page">
    <h2>数据分析</h2>

    <!-- 加载中 -->
    <div v-if="loading" class="card">
      <p class="text-muted">正在加载数据...</p>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="card">
      <p class="text-danger">{{ error }}</p>
      <button class="btn btn-primary" @click="$router.push('/')">返回工作台</button>
    </div>

    <template v-else-if="dataset">
      <!-- 数据集信息 -->
      <div class="card">
        <h3>{{ dataset.name }}</h3>
        <p class="text-muted">{{ dataset.file_type }} · {{ dataset.rows }} 行 · {{ dataset.columns?.length }} 列</p>
        <p v-if="!dataset.is_cleaned" class="text-warning" style="margin-top: 0.5rem">
          提示：该数据集尚未清洗，分析时将自动跳过含缺失值的行
        </p>
      </div>

      <!-- 算法选择 -->
      <div class="card">
        <div class="tab-bar">
          <button
            :class="['tab', { active: algorithm === 'kmeans' }]"
            @click="algorithm = 'kmeans'"
          >
            K-Means 聚类
          </button>
          <button
            :class="['tab', { active: algorithm === 'regression' }]"
            @click="algorithm = 'regression'"
          >
            线性回归
          </button>
        </div>

        <!-- K-Means 参数配置 -->
        <div v-if="algorithm === 'kmeans'" class="params-section">
          <div class="form-group">
            <label>选择特征列（多选）</label>
            <div class="checkbox-group">
              <label
                v-for="col in numericColumns"
                :key="col"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="col"
                  v-model="kmeansParams.features"
                  :disabled="running"
                />
                {{ col }}
              </label>
            </div>
            <p v-if="numericColumns.length === 0" class="text-muted">
              没有可用的数值列
            </p>
          </div>
          <div class="form-group">
            <label>K 值：{{ kmeansParams.k }}</label>
            <input
              type="range"
              min="2"
              max="10"
              v-model.number="kmeansParams.k"
              :disabled="running"
              style="max-width: 300px"
            />
            <span class="text-muted">（聚类数，2~10）</span>
          </div>
          <button
            class="btn btn-primary"
            :disabled="running || kmeansParams.features.length < 1"
            @click="runKMeans"
          >
            {{ running ? '运行中...' : '执行 K-Means 聚类' }}
          </button>
        </div>

        <!-- 回归参数配置 -->
        <div v-if="algorithm === 'regression'" class="params-section">
          <div class="form-group">
            <label>自变量 X（多选）</label>
            <div class="checkbox-group">
              <label
                v-for="col in numericColumns"
                :key="col"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="col"
                  v-model="regressionParams.x_columns"
                  :disabled="running"
                />
                {{ col }}
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>因变量 Y（单选）</label>
            <div class="checkbox-group">
              <label
                v-for="col in numericColumns"
                :key="col"
                class="checkbox-label"
              >
                <input
                  type="radio"
                  :value="col"
                  v-model="regressionParams.y_column"
                  :disabled="running"
                />
                {{ col }}
              </label>
            </div>
          </div>
          <button
            class="btn btn-primary"
            :disabled="running || regressionParams.x_columns.length < 1 || !regressionParams.y_column"
            @click="runRegression"
          >
            {{ running ? '运行中...' : '执行线性回归' }}
          </button>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="result" class="card">
        <h3 style="margin-bottom: 0.8rem">分析结果</h3>

        <!-- K-Means 结果 -->
        <template v-if="result.type === 'kmeans'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-value">{{ result.metrics?.inertia }}</span>
              <span class="metric-label">Inertia（簇内平方和）</span>
            </div>
            <div class="metric-card">
              <span class="metric-value">{{ result.metrics?.silhouette_score }}</span>
              <span class="metric-label">轮廓系数（Silhouette）</span>
            </div>
          </div>

          <h4 style="margin: 1rem 0 0.5rem">聚类中心</h4>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>簇</th>
                  <th v-for="f in kmeansParams.features" :key="f">{{ f }}</th>
                  <th>样本数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(center, cname) in result.cluster_centers" :key="cname">
                  <td><strong>{{ cname }}</strong></td>
                  <td v-for="f in kmeansParams.features" :key="f">
                    {{ center[f] }}
                  </td>
                  <td>{{ result.cluster_sizes?.[cname] ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="result.metrics?.elbow_data" style="margin-top: 1rem">
            <h4 style="margin-bottom: 0.5rem">肘部法则数据</h4>
            <div class="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>K 值</th>
                    <th>Inertia</th>
                    <th>轮廓系数</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(kv, i) in result.metrics.elbow_data.k_values" :key="kv">
                    <td>{{ kv }}</td>
                    <td>{{ result.metrics.elbow_data.inertias[i] }}</td>
                    <td>{{ result.metrics.elbow_data.silhouette_scores[i] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

        <!-- 回归结果 -->
        <template v-if="result.type === 'regression'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-value">{{ result.metrics?.r2_score }}</span>
              <span class="metric-label">R² 决定系数</span>
            </div>
            <div class="metric-card">
              <span class="metric-value">{{ result.metrics?.mse }}</span>
              <span class="metric-label">MSE 均方误差</span>
            </div>
            <div class="metric-card">
              <span class="metric-value">{{ result.metrics?.rmse }}</span>
              <span class="metric-label">RMSE 均方根误差</span>
            </div>
          </div>

          <div style="margin-top: 1rem">
            <h4 style="margin-bottom: 0.5rem">回归方程</h4>
            <p class="equation">{{ result.metrics?.equation }}</p>
          </div>

          <h4 style="margin: 1rem 0 0.5rem">回归系数</h4>
          <div class="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>变量</th>
                  <th>系数</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>截距（Intercept）</td>
                  <td>{{ result.metrics?.intercept }}</td>
                </tr>
                <tr v-for="(coef, col) in result.metrics?.coefficients" :key="col">
                  <td>{{ col }}</td>
                  <td>{{ coef }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- 操作按钮 -->
        <div v-if="result.taskId" style="margin-top: 1.2rem">
          <button
            class="btn btn-primary"
            @click="$router.push(`/visualize/${result.taskId}`)"
          >
            前往可视化 →
          </button>
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

const route = useRoute()
const datasetStore = useDatasetStore()

const dataset = ref(null)
const stats = ref(null)
const algorithm = ref('kmeans')
const running = ref(false)
const loading = ref(true)
const error = ref(null)
const result = ref(null)

const kmeansParams = ref({ features: [], k: 3 })
const regressionParams = ref({ x_columns: [], y_column: null })

const numericColumns = computed(() => {
  if (!stats.value?.columns) return []
  return stats.value.columns
    .filter(c => c.type === 'numeric')
    .map(c => c.name)
})

onMounted(async () => {
  const id = route.params.id
  try {
    dataset.value = await datasetStore.fetchDataset(id)
    const res = await api.get(`/analysis/stats/${id}/`)
    stats.value = res.data
  } catch {
    error.value = '加载数据集失败'
  } finally {
    loading.value = false
  }
})

async function runKMeans() {
  running.value = true
  result.value = null
  try {
    const res = await api.post('/analysis/kmeans/', {
      dataset_id: dataset.value.id,
      features: kmeansParams.value.features,
      k: kmeansParams.value.k,
    })
    result.value = {
      type: 'kmeans',
      taskId: res.data.task?.id,
      ...res.data,
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'K-Means 聚类失败'
  } finally {
    running.value = false
  }
}

async function runRegression() {
  running.value = true
  result.value = null
  try {
    const res = await api.post('/analysis/regression/', {
      dataset_id: dataset.value.id,
      x_columns: regressionParams.value.x_columns,
      y_column: regressionParams.value.y_column,
    })
    result.value = {
      type: 'regression',
      taskId: res.data.task?.id,
      ...res.data,
    }
  } catch (e) {
    error.value = e.response?.data?.error || '线性回归失败'
  } finally {
    running.value = false
  }
}
</script>

<style scoped>
.text-muted { color: var(--text-muted) }
.text-danger { color: var(--danger); font-weight: 600 }
.text-warning { color: #e67e22; font-size: 0.85rem }
.table-scroll { overflow-x: auto }

.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--border);
  margin-bottom: 1.2rem;
}
.tab {
  padding: 0.5rem 1.2rem;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-muted);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.2s, border-color 0.2s;
}
.tab.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
  font-weight: 600;
}
.tab:hover:not(.active) { color: var(--text) }

.params-section { padding: 0.5rem 0 }
.form-group { margin-bottom: 1rem }
.form-group label { display: block; margin-bottom: 0.4rem; font-weight: 600 }
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.checkbox-label input { width: auto }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
}
.metric-card {
  text-align: center;
  padding: 0.8rem;
  background: #f8f9fa;
  border-radius: 6px;
}
.metric-value {
  display: block;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--primary);
}
.metric-label {
  display: block;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.2rem;
}

.equation {
  font-family: 'Courier New', monospace;
  background: #f0f0f0;
  padding: 0.6rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  word-break: break-all;
}
</style>
