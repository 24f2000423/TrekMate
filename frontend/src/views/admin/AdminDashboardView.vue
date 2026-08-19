<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">👑 Admin Analytics & Oversight Portal</h2>
        <p class="text-muted mb-0">System-wide metrics, live statistics, and trekking activity oversight</p>
      </div>
      <div class="d-flex gap-2 flex-wrap">
        <button class="btn btn-outline-primary" @click="triggerDailyReminders">
          <i class="bi bi-bell me-1"></i> Run Daily Reminders (Celery)
        </button>
        <router-link to="/admin/reports" class="btn btn-success">
          <i class="bi bi-file-earmark-pdf me-1"></i> Monthly Activity Reports
        </router-link>
      </div>
    </div>

    <!-- Alert -->
    <div v-if="alertMsg" class="alert alert-info alert-dismissible fade show shadow-sm" role="alert">
      <i class="bi bi-info-circle-fill me-2"></i>{{ alertMsg }}
      <button type="button" class="btn-close" @click="alertMsg = ''"></button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
    </div>

    <template v-else>
      <!-- Top Metrics Grid -->
      <div class="row g-3 mb-4">
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Total Treks" :value="metrics.total_treks" subtitle="All routes" icon="bi-map" variant="success" />
        </div>
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Open Treks" :value="metrics.open_treks" subtitle="Accepting bookings" icon="bi-door-open" variant="primary" />
        </div>
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Total Trekkers" :value="metrics.total_users" subtitle="Registered users" icon="bi-people" variant="info" />
        </div>
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Staff Guides" :value="metrics.total_staff" subtitle="Field experts" icon="bi-person-badge" variant="secondary" />
        </div>
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Total Bookings" :value="metrics.total_bookings" subtitle="All-time reservations" icon="bi-ticket-detailed" variant="warning" />
        </div>
        <div class="col-xl-2 col-md-4 col-6">
          <StatCard title="Total Revenue" :value="`₹${(metrics.total_revenue || 0).toLocaleString('en-IN')}`" subtitle="Gross bookings" icon="bi-cash-coin" variant="success" />
        </div>
      </div>

      <!-- Charts Section (ChartJS) -->
      <div class="row g-4 mb-4">
        <!-- Popular Treks Chart -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
            <h5 class="fw-bold mb-3 d-flex align-items-center">
              <i class="bi bi-bar-chart-fill text-success me-2"></i>Most Popular Treks (by Bookings)
            </h5>
            <div style="min-height: 280px;">
              <TrekChart type="bar" :data="popularTreksChartData" :options="barOptions" />
            </div>
          </div>
        </div>

        <!-- Difficulty Distribution Chart -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
            <h5 class="fw-bold mb-3 d-flex align-items-center">
              <i class="bi bi-pie-chart-fill text-primary me-2"></i>Trek Difficulty Ratio
            </h5>
            <div style="min-height: 280px;">
              <TrekChart type="doughnut" :data="difficultyChartData" />
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Action Panels -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <router-link to="/admin/treks" class="card border-0 shadow-sm rounded-4 text-decoration-none text-dark p-3 text-center h-100 hover-lift">
            <div class="fs-2 text-success mb-2"><i class="bi bi-plus-circle"></i></div>
            <h6 class="fw-bold mb-1">Create & Manage Treks</h6>
            <small class="text-muted">Add new routes, set dates & pricing</small>
          </router-link>
        </div>
        <div class="col-md-3">
          <router-link to="/admin/staff" class="card border-0 shadow-sm rounded-4 text-decoration-none text-dark p-3 text-center h-100 hover-lift">
            <div class="fs-2 text-primary mb-2"><i class="bi bi-person-plus"></i></div>
            <h6 class="fw-bold mb-1">Onboard Staff Members</h6>
            <small class="text-muted">Create credentials & assign treks</small>
          </router-link>
        </div>
        <div class="col-md-3">
          <router-link to="/admin/users" class="card border-0 shadow-sm rounded-4 text-decoration-none text-dark p-3 text-center h-100 hover-lift">
            <div class="fs-2 text-warning mb-2"><i class="bi bi-shield-lock"></i></div>
            <h6 class="fw-bold mb-1">User Moderation</h6>
            <small class="text-muted">Search, deactivate, or blacklist</small>
          </router-link>
        </div>
        <div class="col-md-3">
          <router-link to="/admin/reports" class="card border-0 shadow-sm rounded-4 text-decoration-none text-dark p-3 text-center h-100 hover-lift">
            <div class="fs-2 text-info mb-2"><i class="bi bi-file-earmark-ruled"></i></div>
            <h6 class="fw-bold mb-1">Monthly Activity Reports</h6>
            <small class="text-muted">View HTML / PDF batch reports</small>
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../../api';
import StatCard from '../../components/StatCard.vue';
import TrekChart from '../../components/TrekChart.vue';

const metrics = ref({});
const charts = ref({});
const loading = ref(true);
const alertMsg = ref('');

const popularTreksChartData = computed(() => {
  const treks = charts.value?.popular_treks || [];
  return {
    labels: treks.map(t => t.name.length > 20 ? t.name.substring(0, 18) + '...' : t.name),
    datasets: [{
      label: 'Active Bookings',
      data: treks.map(t => t.bookings_count),
      backgroundColor: 'rgba(25, 135, 84, 0.75)',
      borderColor: 'rgb(25, 135, 84)',
      borderWidth: 1,
      borderRadius: 6,
    }]
  };
});

const difficultyChartData = computed(() => {
  const diff = charts.value?.difficulty_distribution || {};
  return {
    labels: ['Easy', 'Moderate', 'Hard'],
    datasets: [{
      data: [diff['Easy'] || 0, diff['Moderate'] || 0, diff['Hard'] || 0],
      backgroundColor: ['#198754', '#ffc107', '#dc3545'],
    }]
  };
});

const barOptions = {
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 }
    }
  }
};

const fetchAdminStats = async () => {
  loading.value = true;
  try {
    const res = await api.get('/admin/stats');
    metrics.value = res.data.metrics || {};
    charts.value = res.data.charts || {};
  } catch (err) {
    console.error('Failed to load admin stats', err);
  } finally {
    loading.value = false;
  }
};

const triggerDailyReminders = async () => {
  alertMsg.value = '';
  try {
    const res = await api.post('/reports/trigger-daily-reminders');
    alertMsg.value = res.data.message || 'Daily reminders executed successfully!';
  } catch (err) {
    alertMsg.value = 'Failed to trigger reminders: ' + (err.response?.data?.error || err.message);
  }
};

onMounted(() => {
  fetchAdminStats();
});
</script>

<style scoped>
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08) !important;
}
</style>
