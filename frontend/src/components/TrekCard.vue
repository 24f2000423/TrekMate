<template>
  <div class="card h-100 border-0 shadow-sm rounded-3 overflow-hidden trek-card transition-all">
    <!-- Image Header -->
    <div class="position-relative" style="height: 190px; overflow: hidden; background-color: #e9ecef;">
      <img
        :src="trek.image_url || defaultImage"
        :alt="trek.name"
        class="w-100 h-100 object-fit-cover trek-img"
        @error="onImageError"
      />
      <span
        class="position-absolute top-0 start-0 m-3 badge px-3 py-2 rounded-pill shadow-sm"
        :class="getDifficultyBadge(trek.difficulty)"
      >
        {{ trek.difficulty }}
      </span>
      <span
        class="position-absolute top-0 end-0 m-3 badge px-3 py-2 rounded-pill shadow-sm"
        :class="getStatusBadge(trek.status)"
      >
        {{ trek.status }}
      </span>
    </div>

    <!-- Body -->
    <div class="card-body d-flex flex-column p-3">
      <div class="d-flex align-items-center text-muted small mb-1">
        <i class="bi bi-geo-alt-fill text-danger me-1"></i>
        <span class="text-truncate">{{ trek.location }}</span>
      </div>

      <h5 class="card-title fw-bold text-dark mb-2 text-truncate" :title="trek.name">
        {{ trek.name }}
      </h5>

      <p class="card-text text-muted small flex-grow-1 line-clamp-2 mb-3">
        {{ trek.description || 'Experience an unforgettable adventure with panoramic views and thrilling trails.' }}
      </p>

      <!-- Key Details -->
      <div class="bg-light rounded-3 p-2 mb-3 small">
        <div class="row g-1 text-center">
          <div class="col-4 border-end">
            <span class="text-muted d-block" style="font-size: 11px;">Duration</span>
            <span class="fw-bold">{{ trek.duration_days }} Days</span>
          </div>
          <div class="col-4 border-end">
            <span class="text-muted d-block" style="font-size: 11px;">Slots Left</span>
            <span class="fw-bold" :class="trek.available_slots > 0 ? 'text-success' : 'text-danger'">
              {{ trek.available_slots }} / {{ trek.total_slots }}
            </span>
          </div>
          <div class="col-4">
            <span class="text-muted d-block" style="font-size: 11px;">Start Date</span>
            <span class="fw-bold">{{ formatDate(trek.start_date) }}</span>
          </div>
        </div>
      </div>

      <!-- Footer & Action -->
      <div class="d-flex align-items-center justify-content-between pt-2 border-top">
        <div>
          <span class="text-muted small d-block" style="font-size: 11px;">Price per trekker</span>
          <span class="fs-5 fw-bold text-success">₹{{ formatPrice(trek.price) }}</span>
        </div>
        <router-link :to="`/trek/${trek.id}`" class="btn btn-outline-success btn-sm px-3 rounded-pill fw-semibold">
          Details & Book <i class="bi bi-arrow-right ms-1"></i>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  trek: {
    type: Object,
    required: true
  }
});

const defaultImage = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80';

const onImageError = (e) => {
  e.target.src = defaultImage;
};

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success text-white';
    case 'Moderate': return 'bg-warning text-dark';
    case 'Hard': return 'bg-danger text-white';
    default: return 'bg-secondary text-white';
  }
};

const getStatusBadge = (status) => {
  switch (status) {
    case 'Open': return 'bg-primary text-white';
    case 'Closed': return 'bg-dark text-white';
    case 'Completed': return 'bg-info text-dark';
    case 'Pending': return 'bg-secondary text-white';
    case 'Approved': return 'bg-success text-white';
    default: return 'bg-secondary text-white';
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'TBA';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
};

const formatPrice = (price) => {
  return Number(price || 0).toLocaleString('en-IN');
};
</script>

<style scoped>
.trek-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.trek-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08) !important;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
