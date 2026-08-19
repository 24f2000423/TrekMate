<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">🏔️ Trek Staff Operations Portal</h2>
        <p class="text-muted mb-0">Welcome back, <strong>{{ user?.name }}</strong>. Manage your assigned treks and participant rosters.</p>
      </div>
      <div class="badge bg-primary px-3 py-2 fs-6">
        <i class="bi bi-person-badge me-1"></i> Expedition Leader
      </div>
    </div>

    <!-- Metrics Row -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <StatCard
          title="Assigned Treks"
          :value="assignedTreks.length"
          subtitle="Routes assigned by Admin"
          icon="bi-map"
          variant="primary"
        />
      </div>
      <div class="col-md-4">
        <StatCard
          title="Total Trekkers Registered"
          :value="totalParticipants"
          subtitle="Active booked participants"
          icon="bi-people-fill"
          variant="success"
        />
      </div>
      <div class="col-md-4">
        <StatCard
          title="Open for Booking"
          :value="openTreksCount"
          subtitle="Active booking status"
          icon="bi-door-open-fill"
          variant="warning"
        />
      </div>
    </div>

    <!-- Assigned Treks List -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
        <h5 class="fw-bold mb-0 text-dark">
          <i class="bi bi-compass text-primary me-2"></i>My Assigned Expeditions
        </h5>
      </div>

      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else-if="assignedTreks.length === 0" class="text-center py-5 text-muted">
          <i class="bi bi-inbox display-4 d-block mb-2"></i>
          <h5>No treks assigned</h5>
          <p>The Admin has not assigned any active treks to your profile yet.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Dates</th>
                <th>Available Slots</th>
                <th>Registered Trekkers</th>
                <th>Current Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in assignedTreks" :key="t.id">
                <td>
                  <div class="fw-bold text-dark">{{ t.name }}</div>
                  <small class="text-muted">{{ t.duration_days }} Days</small>
                </td>
                <td><i class="bi bi-geo-alt text-danger me-1"></i>{{ t.location }}</td>
                <td>
                  <span class="badge" :class="getDifficultyBadge(t.difficulty)">{{ t.difficulty }}</span>
                </td>
                <td class="small">
                  <div>{{ t.start_date }}</div>
                  <div class="text-muted">to {{ t.end_date }}</div>
                </td>
                <td>
                  <span class="badge px-2 py-1" :class="t.available_slots > 0 ? 'bg-success' : 'bg-danger'">
                    {{ t.available_slots }} / {{ t.total_slots }} Left
                  </span>
                </td>
                <td>
                  <span class="badge bg-primary-subtle text-primary border fw-bold px-2 py-1">
                    {{ t.registered_users_count || 0 }} Trekkers
                  </span>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadge(t.status)">{{ t.status }}</span>
                </td>
                <td class="text-end">
                  <router-link :to="`/staff/trek/${t.id}`" class="btn btn-sm btn-primary">
                    <i class="bi bi-people me-1"></i> Manage & Roster
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
const assignedTreks = ref([]);
const loading = ref(true);

const totalParticipants = computed(() => {
  return assignedTreks.value.reduce((acc, t) => acc + (t.registered_users_count || 0), 0);
});

const openTreksCount = computed(() => {
  return assignedTreks.value.filter(t => t.status === 'Open').length;
});

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success';
    case 'Moderate': return 'bg-warning text-dark';
    case 'Hard': return 'bg-danger';
    default: return 'bg-secondary';
  }
};

const getStatusBadge = (status) => {
  switch (status) {
    case 'Open': return 'bg-success';
    case 'Closed': return 'bg-dark';
    case 'Started': return 'bg-warning text-dark';
    case 'Completed': return 'bg-info text-dark';
    default: return 'bg-secondary';
  }
};

const fetchAssignedTreks = async () => {
  loading.value = true;
  try {
    const res = await api.get('/staff/treks');
    assignedTreks.value = res.data.treks || [];
  } catch (err) {
    console.error('Failed to load assigned treks', err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchAssignedTreks();
});
</script>
