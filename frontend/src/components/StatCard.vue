<template>
  <div class="card border-0 shadow-sm rounded-3 h-100" :class="`border-start border-${variant || 'primary'} border-4`">
    <div class="card-body d-flex align-items-center justify-content-between">
      <div>
        <h6 class="text-uppercase text-muted fw-bold mb-1" style="font-size: 12px; letter-spacing: 0.5px;">
          {{ title }}
        </h6>
        <h3 class="fw-bold mb-0 text-dark">{{ value }}</h3>
        <small v-if="subtitle" class="text-muted">{{ subtitle }}</small>
      </div>
      <div
        class="rounded-circle d-flex align-items-center justify-content-center p-3"
        :class="`bg-${variant || 'primary'}-subtle text-${variant || 'primary'}`"
        style="width: 52px; height: 52px;"
      >
        <i :class="`bi ${icon || 'bi-bar-chart'} fs-4`"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  subtitle: String,
  icon: String,
  variant: {
    type: String,
    default: 'primary'
  }
});
</script>
