<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">My Bookings</h2>
        <p class="text-muted mb-0">Track and manage your upcoming trek reservations</p>
      </div>
      <router-link to="/" class="btn btn-success">
        <i class="bi bi-plus-circle me-1"></i> Book Another Trek
      </router-link>
    </div>

    <!-- Alert message -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Bookings Table / Cards -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="bookings.length === 0" class="text-center py-5">
          <div class="display-3 text-muted mb-3">🎫</div>
          <h5>No bookings found</h5>
          <p class="text-muted">You haven't booked any treks yet.</p>
          <router-link to="/" class="btn btn-success">Explore Available Treks</router-link>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Booking ID</th>
                <th>Trek Details</th>
                <th>Dates</th>
                <th>Assigned Guide</th>
                <th>Seats</th>
                <th>Amount Paid</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td class="text-muted font-monospace">#{{ b.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ b.trek_name }}</div>
                  <small class="text-muted"><i class="bi bi-geo-alt me-1 text-danger"></i>{{ b.trek_location }}</small>
                </td>
                <td>
                  <div class="small fw-semibold">{{ b.trek_start_date }}</div>
                  <small class="text-muted">to {{ b.trek_end_date }}</small>
                </td>
                <td>
                  <div class="small fw-semibold">{{ b.assigned_staff_name || 'TMA Team' }}</div>
                </td>
                <td>
                  <span class="badge bg-secondary-subtle text-secondary-emphasis border">
                    {{ b.seats }} seat(s)
                  </span>
                </td>
                <td>
                  <div class="fw-bold text-success">₹{{ (b.total_amount || 0).toLocaleString('en-IN') }}</div>
                  <small class="badge bg-success-subtle text-success">{{ b.payment_status }}</small>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadge(b.status)">{{ b.status }}</span>
                </td>
                <td class="text-end">
                  <div class="btn-group">
                    <router-link :to="`/trek/${b.trek_id}`" class="btn btn-outline-secondary btn-sm" title="View Trek">
                      <i class="bi bi-eye"></i>
                    </router-link>
                    <button
                      v-if="b.status === 'Booked'"
                      class="btn btn-outline-danger btn-sm"
                      @click="confirmCancel(b)"
                      title="Cancel Booking"
                    >
                      <i class="bi bi-x-circle me-1"></i> Cancel
                    </button>
                  </div>
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
import { ref, onMounted } from 'vue';
import api from '../../api';

const bookings = ref([]);
const loading = ref(true);
const successMsg = ref('');
const errorMsg = ref('');

const getStatusBadge = (status) => {
  switch (status) {
    case 'Booked': return 'bg-success';
    case 'Completed': return 'bg-info text-dark';
    case 'Cancelled': return 'bg-danger';
    default: return 'bg-secondary';
  }
};

const fetchBookings = async () => {
  loading.value = true;
  try {
    const res = await api.get('/bookings/my-bookings');
    bookings.value = res.data.bookings || [];
  } catch (err) {
    console.error('Failed to load bookings:', err);
  } finally {
    loading.value = false;
  }
};

const confirmCancel = async (booking) => {
  if (!confirm(`Are you sure you want to cancel your booking for "${booking.trek_name}"? Slots will be released back to the trek.`)) {
    return;
  }

  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.post(`/bookings/${booking.id}/cancel`);
    successMsg.value = res.data.message || 'Booking cancelled successfully';
    await fetchBookings();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to cancel booking';
  }
};

onMounted(() => {
  fetchBookings();
});
</script>
