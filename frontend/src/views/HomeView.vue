<template>
  <div>
    <!-- Hero Banner -->
    <div class="bg-dark text-white position-relative py-5 mb-5 overflow-hidden" style="background: linear-gradient(135deg, #134e2c 0%, #1e3c72 100%);">
      <div class="container py-4 text-center">
        <span class="badge bg-warning text-dark px-3 py-2 rounded-pill fw-bold mb-3">
          <i class="bi bi-compass-fill me-1"></i> Explore The Great Outdoors
        </span>
        <h1 class="display-4 fw-bold mb-3">Trekking Management Application</h1>
        <p class="lead mx-auto mb-4 text-light-50" style="max-width: 680px;">
          Discover epic Himalayan peaks, lush rainforest trails, and hidden alpine lakes. Verified expedition staff, real-time slot bookings, and comprehensive management.
        </p>
        <div class="d-flex justify-content-center gap-2 flex-wrap">
          <a href="#trek-catalog" class="btn btn-warning btn-lg px-4 fw-bold text-dark rounded-pill">
            <i class="bi bi-search me-1"></i> Browse Open Treks
          </a>
          <router-link v-if="!isLoggedIn" to="/register" class="btn btn-outline-light btn-lg px-4 rounded-pill">
            Join as a Trekker
          </router-link>
        </div>
      </div>
    </div>

    <!-- Main Container -->
    <div class="container pb-5" id="trek-catalog">
      <!-- Search & Filter Controls -->
      <div class="card border-0 shadow-sm rounded-4 p-4 mb-4">
        <div class="row g-3 align-items-center">
          <!-- Search Input -->
          <div class="col-lg-4 col-md-6">
            <label class="form-label small fw-bold text-muted">Search Trek or Location</label>
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
              <input
                type="text"
                v-model="filters.search"
                class="form-control border-start-0 ps-0"
                placeholder="e.g. Kedarkantha, Himalayas..."
                @input="debounceFetch"
              />
            </div>
          </div>

          <!-- Difficulty Filter -->
          <div class="col-lg-2 col-md-3 col-6">
            <label class="form-label small fw-bold text-muted">Difficulty</label>
            <select v-model="filters.difficulty" class="form-select" @change="fetchTreks">
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="col-lg-2 col-md-3 col-6">
            <label class="form-label small fw-bold text-muted">Status</label>
            <select v-model="filters.status" class="form-select" @change="fetchTreks">
              <option value="">All Statuses</option>
              <option value="Open">Open for Booking</option>
              <option value="Closed">Closed / Full</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <!-- Max Duration Filter -->
          <div class="col-lg-2 col-md-6 col-6">
            <label class="form-label small fw-bold text-muted">Max Duration (Days)</label>
            <input
              type="number"
              v-model="filters.max_duration"
              class="form-control"
              placeholder="e.g. 7"
              min="1"
              @input="debounceFetch"
            />
          </div>

          <!-- Reset Filter Button -->
          <div class="col-lg-2 col-md-6 col-6 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
          </div>
        </div>

        <!-- Caching indicator badge -->
        <div class="mt-3 pt-2 border-top d-flex justify-content-between align-items-center small text-muted">
          <span>Found <strong>{{ treks.length }}</strong> trek(s) matching your criteria</span>
          <span v-if="isCached" class="badge bg-info-subtle text-info-emphasis border">
            <i class="bi bi-lightning-charge-fill me-1"></i> Cached via Redis
          </span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mt-3">Fetching available treks...</p>
      </div>

      <!-- Treks Grid -->
      <div v-else-if="treks.length > 0" class="row g-4">
        <div v-for="trek in treks" :key="trek.id" class="col-lg-4 col-md-6">
          <TrekCard :trek="trek" />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="card border-0 shadow-sm rounded-4 text-center py-5">
        <div class="card-body">
          <div class="display-1 text-muted mb-3">🏕️</div>
          <h4 class="fw-bold">No treks found</h4>
          <p class="text-muted">Try adjusting your search criteria or resetting filters.</p>
          <button class="btn btn-success px-4" @click="resetFilters">Show All Treks</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { useAuth } from '../store/auth';
import TrekCard from '../components/TrekCard.vue';

const { isLoggedIn } = useAuth();

const treks = ref([]);
const loading = ref(false);
const isCached = ref(false);

const filters = reactive({
  search: '',
  difficulty: '',
  status: 'Open',
  max_duration: '',
});

let debounceTimer = null;
const debounceFetch = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    fetchTreks();
  }, 350);
};

const fetchTreks = async () => {
  loading.value = true;
  try {
    const params = {};
    if (filters.search) params.search = filters.search;
    if (filters.difficulty) params.difficulty = filters.difficulty;
    if (filters.status) params.status = filters.status;
    if (filters.max_duration) params.max_duration = filters.max_duration;

    const res = await api.get('/treks', { params });
    treks.value = res.data.treks || [];
    isCached.value = !!res.data.cached;
  } catch (err) {
    console.error('Error loading treks:', err);
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  filters.search = '';
  filters.difficulty = '';
  filters.status = '';
  filters.max_duration = '';
  fetchTreks();
};

onMounted(() => {
  fetchTreks();
});
</script>
