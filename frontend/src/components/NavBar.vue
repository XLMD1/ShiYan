<template>
  <nav class="navbar">
    <div class="nav-left">
      <router-link to="/" class="logo">数据分析系统</router-link>
      <router-link to="/upload">上传数据</router-link>
      <router-link to="/history">历史记录</router-link>
    </div>
    <div class="nav-right">
      <span class="username">{{ user?.username }}</span>
      <button @click="handleLogout" class="btn-logout">退出</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  height: 56px;
  background: #1a1a2e;
  color: #fff;
}
.nav-left { display: flex; gap: 1.5rem; align-items: center; }
.nav-left a { color: #ccc; text-decoration: none; font-size: 0.9rem; }
.nav-left a:hover { color: #fff; }
.nav-left .logo { color: #fff; font-weight: 700; font-size: 1.1rem; }
.nav-right { display: flex; gap: 1rem; align-items: center; }
.username { font-size: 0.85rem; color: #aaa; }
.btn-logout {
  padding: 0.3rem 0.8rem;
  border: 1px solid #555;
  border-radius: 4px;
  background: transparent;
  color: #ccc;
  cursor: pointer;
  font-size: 0.8rem;
}
.btn-logout:hover { background: #333; }
</style>
