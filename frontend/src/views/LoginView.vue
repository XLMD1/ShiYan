<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <label>用户名</label>
        <input v-model="username" type="text" required placeholder="请输入用户名" />
        <label>密码</label>
        <input v-model="password" type="password" required placeholder="请输入密码" />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="switch">
        没有账号？<router-link to="/register">立即注册</router-link>
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
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
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
