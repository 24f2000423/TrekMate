<template>
  <div class="container py-4">
    <!-- Welcome Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">Hello, {{ user?.name }} 👋</h2>
        <p class="text-muted mb-0">Welcome to your Trekker Dashboard</p>
      </div>
      <div class="d-flex gap-2">
        <router-link to="/" class="btn btn-outline-success">
          <i class="bi bi-compass me-1"></i> Explore Treks
        </router-link>
        <router-link to="/user/history" class="btn btn-success">
          <i class="bi bi-file-earmark-arrow-down me-1"></i> Export History
        </router-link>
      </div>
    </div>

    <!-- Metrics Row -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <StatCard
          title="Active Bookings"
          :value="activeBookings.length"
          subtitle="Upcoming expeditions"
          icon="bi-calendar-check"
          variant="success"
        />
      </div>
      <div class="col-md-4">
        <StatCard
          title="Completed Treks"
          :value="completedBookings.length"
          subtitle="Past summit journeys"
          icon="bi-flag-fill"
          variant="primary"
        />
      </div>
      <div class="col-md-4">
        <StatCard
          title="Total Spent"
          :value="`₹${totalSpent.toLocaleString('en-IN')}`"
          subtitle="Total trekking investments"
          icon="bi-cash-stack"
          variant="warning"
        />
      </div>
    </div>

    <!-- Active Expeditions -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-person-walking text-success me-2"></i>My Active Expeditions
        </h5>
        <router-link to="/user/bookings" class="small text-success text-decoration-none fw-bold">
          View All Bookings &rarr;
        </router-link>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border spinner-border-sm text-success"></div>
        </div>

        <div v-else-if="activeBookings.length === 0" class="text-center py-5">
          <p class="text-muted mb-2">You don't have any active bookings right now.</p>
          <router-link to="/" class="btn btn-outline-success btn-sm">Find a Trek to Join</router-link>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Start Date</th>
                <th>Assigned Leader</th>
                <th>Seats</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in activeBookings" :key="b.id">
                <td class="fw-bold">{{ b.trek_name }}</td>
                <td><i class="bi bi-geo-alt text-danger me-1"></i>{{ b.trek_location }}</td>
                <td>
                  <span class="badge" :class="getDifficultyBadge(b.trek_difficulty)">
                    {{ b.trek_difficulty }}
                  </span>
                </td>
                <td>{{ b.trek_start_date }}</td>
                <td>{{ b.assigned_staff_name || 'Guide Team' }}</td>
                <td><span class="badge bg-secondary">{{ b.seats }} seat(s)</span></td>
                <td><span class="badge bg-success">{{ b.status }}</span></td>
                <td>
                  <router-link :to="`/trek/${b.trek_id}`" class="btn btn-sm btn-outline-secondary">
                    View
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../api';
import { useAuth } from '../../store/auth';
import StatCard from '../../components/StatCard.vue';

const { user } = useAuth();
const bookings = ref([]);
const loading = ref(true);

const activeBookings = computed(() => bookings.value.filter(b => b.status === 'Booked'));
const completedBookings = computed(() => bookings.value.filter(b => b.status === 'Completed'));
const totalSpent = computed(() => bookings.value
  .filter(b => b.status !== 'Cancelled')
  .reduce((acc, b) => acc + (b.total_amount || 0), 0)
);

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success';
    case 'Moderate': return 'bg-warning text-dark';
    case 'Hard': return 'bg-danger';
    default: return 'bg-secondary';
  }
};

const fetchUserBookings = async () => {
  loading.value = true;
  try {
    const res = await api.get('/bookings/my-bookings');
    bookings.value = res.data.bookings || [];
  } catch (err) {
    console.error('Failed to load bookings', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchUserBookings();
});
</script>
