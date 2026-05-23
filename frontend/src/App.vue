<template>
  <div id="app">
    <NavBar v-if="isLoggedIn" />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavBar from './components/NavBar.vue'

const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
.container { max-width: 1200px; margin: 0 auto; padding: 1.5rem; }
</style>
