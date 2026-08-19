<template>
  <div class="d-flex flex-column min-vh-100">
    <Navbar />

    <main class="flex-grow-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-auto border-top border-secondary">
      <div class="container text-center">
        <div class="mb-2 d-flex justify-content-center align-items-center gap-2">
          <span class="fs-4">🏔️</span>
          <span class="fw-bold fs-5 text-success">Trekking Management Application (TMA) - V2</span>
        </div>
        <p class="small text-muted mb-2">
          Role-Based Portals for Superuser Admin, Trek Staff, and Trekkers &bull; Powered by Flask, Vue 3, Bootstrap 5, Redis & Celery
        </p>
        <div class="small text-secondary">
          &copy; {{ new Date().getFullYear() }} TMA Platform. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
</script>

<style>
/* Global styling adjustments */
body {
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
  background-color: #f8faf9;
  color: #2b3035;
}

.transition-all {
  transition: all 0.2s ease-in-out;
}
</style>
