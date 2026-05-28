<template>
  <div id="app">
    <NavBar v-if="isAuthenticated" />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { storeToRefs } from 'pinia'
import NavBar from './components/NavBar.vue'

const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

onMounted(() => {
  authStore.init()
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
</style>
