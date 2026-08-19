<template>
  <div class="container py-4">
    <!-- Back Button -->
    <router-link to="/staff/dashboard" class="btn btn-outline-secondary btn-sm mb-4 rounded-pill">
      <i class="bi bi-arrow-left me-1"></i> Back to Assigned Treks
    </router-link>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="trek" class="row g-4">
      <!-- Top Row: Operational Controls -->
      <div class="col-12">
        <div class="card border-0 shadow-sm rounded-4 p-4 bg-light">
          <div class="row align-items-center g-3">
            <div class="col-lg-6">
              <h3 class="fw-bold mb-1">{{ trek.name }}</h3>
              <p class="text-muted mb-0">
                <i class="bi bi-geo-alt text-danger me-1"></i> {{ trek.location }} | 
                <span class="badge bg-secondary ms-1">{{ trek.difficulty }}</span> |
                <span class="ms-1">{{ trek.start_date }} to {{ trek.end_date }}</span>
              </p>
            </div>

            <!-- Status & Slots Control Panel -->
            <div class="col-lg-6">
              <div class="d-flex gap-2 justify-content-lg-end flex-wrap align-items-center">
                <!-- Status Dropdown -->
                <div>
                  <label class="form-label small fw-bold text-muted mb-1 d-block">Trek Status</label>
                  <select v-model="operationalStatus" class="form-select form-select-sm">
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Started">Started</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>

                <!-- Available Slots Input -->
                <div style="max-width: 120px;">
                  <label class="form-label small fw-bold text-muted mb-1 d-block">Available Slots</label>
                  <input
                    type="number"
                    v-model="availableSlots"
                    class="form-control form-control-sm"
                    min="0"
                    :max="trek.total_slots"
                  />
                </div>

                <div class="align-self-end">
                  <button
                    class="btn btn-primary btn-sm px-3 fw-bold"
                    :disabled="saving"
                    @click="updateTrekOperations"
                  >
                    <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                    Update Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alert -->
      <div class="col-12" v-if="successMsg || errorMsg">
        <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
          <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
          <button type="button" class="btn-close" @click="successMsg = ''"></button>
        </div>
        <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
          <button type="button" class="btn-close" @click="errorMsg = ''"></button>
        </div>
      </div>

      <!-- Participant Roster Table -->
      <div class="col-12">
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
          <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
            <h5 class="fw-bold mb-0">
              <i class="bi bi-people-fill text-primary me-2"></i>Registered Participant Roster ({{ participants.length }})
            </h5>
            <span class="badge bg-success-subtle text-success fs-6">
              Total Confirmed: {{ totalRegisteredSeats }} Seats
            </span>
          </div>

          <div class="card-body p-0">
            <div v-if="participants.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-person-x display-4 d-block mb-2"></i>
              <h5>No participants registered yet</h5>
              <p>When trekkers book slots for this trek, they will appear here in your roster.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Booking #</th>
                    <th>Participant Name</th>
                    <th>Email</th>
                    <th>Contact Phone</th>
                    <th>Seats Booked</th>
                    <th>Payment</th>
                    <th>Special Notes</th>
                    <th>Booking Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in participants" :key="p.booking_id">
                    <td class="font-monospace text-muted">#{{ p.booking_id }}</td>
                    <td class="fw-bold">{{ p.name }}</td>
                    <td>{{ p.email }}</td>
                    <td>{{ p.contact_no || 'N/A' }}</td>
                    <td>
                      <span class="badge bg-secondary">{{ p.seats }}</span>
                    </td>
                    <td>
                      <span class="badge bg-success-subtle text-success">{{ p.payment_status }}</span>
                    </td>
                    <td>
                      <span class="small text-muted fst-italic">{{ p.special_notes || 'None' }}</span>
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="p.status === 'Booked' ? 'bg-success' : 'bg-danger'"
                      >
                        {{ p.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../../api';

const route = useRoute();
const trek = ref(null);
const participants = ref([]);
const loading = ref(true);
const saving = ref(false);
const operationalStatus = ref('Open');
const availableSlots = ref(0);
const successMsg = ref('');
const errorMsg = ref('');

const totalRegisteredSeats = computed(() => {
  return participants.value
    .filter(p => p.status === 'Booked')
    .reduce((acc, p) => acc + (p.seats || 0), 0);
});

const fetchTrekParticipants = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/staff/treks/${route.params.id}/participants`);
    trek.value = res.data.trek;
    participants.value = res.data.participants || [];
    operationalStatus.value = trek.value.status;
    availableSlots.value = trek.value.available_slots;
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to load trek participants';
  } finally {
    loading.value = false;
  }
};

const updateTrekOperations = async () => {
  saving.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.put(`/staff/treks/${route.params.id}/status`, {
      status: operationalStatus.value,
      available_slots: availableSlots.value
    });

    trek.value = res.data.trek;
    successMsg.value = res.data.message || 'Operational details updated successfully';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update details';
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchTrekParticipants();
});
</script>
