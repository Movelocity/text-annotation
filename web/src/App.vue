<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'

// Scroll behavior
const lastScrollPosition = ref(0)
const isHeaderVisible = ref(true)
const isScrollingUp = ref(true)

const handleScroll = () => {
  const currentScrollPosition = window.scrollY

  // Determine scroll direction
  isScrollingUp.value = currentScrollPosition < lastScrollPosition.value

  // Show/hide header based on scroll direction
  // Always show header at the top of the page
  if (currentScrollPosition <= 0) {
    isHeaderVisible.value = true
  } else {
    isHeaderVisible.value = isScrollingUp.value
  }

  lastScrollPosition.value = currentScrollPosition
}

// Setup scroll event listener
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="app-container">
    <!-- Header component -->
    <AppHeader :is-header-visible="isHeaderVisible" />

    <!-- Main content -->
    <main class="app-main">
      <!-- Router view for dynamic content -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
/* Base styles */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: var(--font-family);
}

.app-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.app-main {
  flex: 1;
  background-color: var(--background-dark);
  overflow-y: auto;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
