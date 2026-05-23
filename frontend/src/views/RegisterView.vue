<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <label>用户名</label>
        <input v-model="username" type="text" required placeholder="请输入用户名" />
        <label>邮箱</label>
        <input v-model="email" type="email" placeholder="请输入邮箱（可选）" />
        <label>密码</label>
        <input v-model="password" type="password" required placeholder="至少6位密码" />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="switch">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(username.value, password.value, email.value)
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'object' ? Object.values(data).flat().join(', ') : '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.auth-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  width: 400px;
}
.auth-card h2 { margin-bottom: 1.5rem; text-align: center; }
.auth-card label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #333; }
.auth-card input {
  width: 100%; padding: 0.6rem; margin-bottom: 1rem;
  border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem;
}
.auth-card button {
  width: 100%; padding: 0.7rem;
  background: #1a1a2e; color: #fff; border: none;
  border-radius: 4px; font-size: 1rem; cursor: pointer;
  margin-top: 0.5rem;
}
.auth-card button:hover { background: #16213e; }
.auth-card button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 0.85rem; margin-bottom: 0.5rem; }
.switch { margin-top: 1rem; text-align: center; font-size: 0.9rem; color: #666; }
.switch a { color: #1a1a2e; }
</style>
