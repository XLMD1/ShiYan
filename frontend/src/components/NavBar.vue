<template>
  <nav class="navbar">
    <div class="nav-left">
      <router-link to="/" class="logo">
        <span class="logo-mark">DA</span>
        <span>数据分析系统</span>
      </router-link>
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
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  height: 58px;
  background: linear-gradient(180deg, #151a2f 0%, #101527 100%);
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 22px rgba(9, 12, 24, 0.18);
}

.nav-left { display: flex; gap: 0.65rem; align-items: center; min-width: 0; }

.nav-left a {
  position: relative;
  color: #c8d2df;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 650;
  padding: 0.38rem 0.62rem;
  border-radius: 6px;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.nav-left a:hover,
.nav-left a.router-link-active:not(.logo) {
  color: #fff;
  background: rgba(255,255,255,0.08);
  transform: translateY(-1px);
}

.nav-left .logo {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  color: #fff;
  font-weight: 800;
  font-size: 1.05rem;
  padding-left: 0;
  white-space: nowrap;
}

.logo-mark {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: linear-gradient(135deg, #13a796, #f0a536);
  color: #fff;
  font-size: 0.72rem;
  letter-spacing: 0;
  box-shadow: 0 8px 18px rgba(15, 159, 143, 0.28);
}

.nav-right { display: flex; gap: 1rem; align-items: center; }

.username {
  max-width: 180px;
  padding: 0.25rem 0.55rem;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 999px;
  color: #d9e4ec;
  font-size: 0.82rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  padding: 0.3rem 0.8rem;
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 6px;
  background: rgba(255,255,255,0.04);
  color: #d7dee8;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.12);
  color: #fff;
  transform: translateY(-1px);
}

@media (max-width: 720px) {
  .navbar {
    height: auto;
    min-height: 58px;
    align-items: flex-start;
    flex-direction: column;
    gap: 0.65rem;
    padding: 0.7rem 0.9rem;
  }

  .nav-left,
  .nav-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .nav-right {
    justify-content: space-between;
  }
}
</style>
