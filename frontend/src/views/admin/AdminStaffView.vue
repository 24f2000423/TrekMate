<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">👥 Staff Management & Roster</h2>
        <p class="text-muted mb-0">Onboard expedition guides, view workloads, and manage trek assignments</p>
      </div>
      <button class="btn btn-primary" @click="showOnboardModal = true">
        <i class="bi bi-person-plus-fill me-1"></i> Onboard New Staff
      </button>
    </div>

    <!-- Alerts -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Staff Cards Grid -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else class="row g-4">
      <div v-for="staff in staffList" :key="staff.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm rounded-4 h-100 p-3">
          <div class="card-body d-flex flex-column">
            <!-- Staff Info Header -->
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-primary-subtle text-primary fw-bold fs-4 d-flex align-items-center justify-content-center me-3" style="width: 54px; height: 54px;">
                {{ staff.name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h5 class="fw-bold text-dark mb-0">{{ staff.name }}</h5>
                <small class="text-muted d-block">{{ staff.email }}</small>
                <span class="badge" :class="staff.is_active ? 'bg-success' : 'bg-danger'">
                  {{ staff.is_active ? 'Active Guide' : 'Deactivated' }}
                </span>
              </div>
            </div>

            <!-- Skills & Experience -->
            <div class="bg-light p-2 rounded-3 small mb-3">
              <div class="mb-1">
                <strong class="text-muted">Specialization:</strong>
                <div>{{ staff.specialization || 'Wilderness Trekking & First Aid' }}</div>
              </div>
              <div>
                <strong class="text-muted">Experience:</strong> {{ staff.experience_years || 0 }} years |
                <strong class="text-muted">Phone:</strong> {{ staff.contact_no || 'N/A' }}
              </div>
            </div>

            <!-- Assigned Treks List -->
            <div class="flex-grow-1 mb-3">
              <h6 class="fw-bold small text-muted text-uppercase mb-2">
                Assigned Treks ({{ staff.treks_count || 0 }})
              </h6>
              <ul v-if="staff.assigned_treks_list && staff.assigned_treks_list.length > 0" class="list-group list-group-flush small">
                <li v-for="t in staff.assigned_treks_list" :key="t.id" class="list-group-item px-0 py-1 d-flex justify-content-between align-items-center">
                  <span class="text-truncate" style="max-width: 180px;">{{ t.name }}</span>
                  <span class="badge bg-secondary-subtle text-secondary border">{{ t.status }}</span>
                </li>
              </ul>
              <div v-else class="text-muted small fst-italic">
                No active routes currently assigned.
              </div>
            </div>

            <!-- Quick Action -->
            <div class="border-top pt-2 d-flex justify-content-between align-items-center">
              <span class="small text-muted">Staff ID: #{{ staff.id }}</span>
              <button class="btn btn-outline-primary btn-sm" @click="openAssignModal(staff)">
                <i class="bi bi-pin-map me-1"></i> Assign Trek
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Onboard New Staff -->
    <div v-if="showOnboardModal" class="modal-backdrop fade show"></div>
    <div v-if="showOnboardModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content rounded-4 border-0 shadow">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold">Onboard Trek Staff Member</h5>
            <button type="button" class="btn-close btn-close-white" @click="showOnboardModal = false"></button>
          </div>

          <form @submit.prevent="createStaff">
            <div class="modal-body p-4">
              <div class="mb-3">
                <label class="form-label small fw-bold">Full Name *</label>
                <input type="text" v-model="onboardForm.name" class="form-control" required />
              </div>
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label small fw-bold">Username *</label>
                  <input type="text" v-model="onboardForm.username" class="form-control" required />
                </div>
                <div class="col-6">
                  <label class="form-label small fw-bold">Password *</label>
                  <input type="password" v-model="onboardForm.password" class="form-control" minlength="6" required />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Email Address *</label>
                <input type="email" v-model="onboardForm.email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Contact Number</label>
                <input type="tel" v-model="onboardForm.contact_no" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Specialization</label>
                <input type="text" v-model="onboardForm.specialization" class="form-control" placeholder="e.g. High Altitude, Navigation, River Crossing" />
              </div>
              <div class="mb-3">
                <label class="form-label small fw-bold">Years of Experience</label>
                <input type="number" v-model="onboardForm.experience_years" class="form-control" min="0" />
              </div>
            </div>

            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" @click="showOnboardModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary px-4" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                Create Staff Account
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal: Assign Trek -->
    <div v-if="showAssignModal" class="modal-backdrop fade show"></div>
    <div v-if="showAssignModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-md modal-dialog-centered">
        <div class="modal-content rounded-4 border-0 shadow">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold">Assign Trek to {{ selectedStaff?.name }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="showAssignModal = false"></button>
          </div>

          <form @submit.prevent="assignTrek">
            <div class="modal-body p-4">
              <label class="form-label small fw-bold">Select Trek Route *</label>
              <select v-model="selectedTrekId" class="form-select" required>
                <option value="" disabled>-- Choose a Trek --</option>
                <option v-for="t in allTreks" :key="t.id" :value="t.id">
                  {{ t.name }} ({{ t.location }}) - Currently: {{ t.assigned_staff_name || 'Unassigned' }}
                </option>
              </select>
              <small class="text-muted mt-2 d-block">
                Assigning this trek will authorize {{ selectedStaff?.name }} to manage participant rosters and operational slot updates.
              </small>
            </div>

            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" @click="showAssignModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary px-4" :disabled="saving">
                Confirm Assignment
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../../api';

const staffList = ref([]);
const allTreks = ref([]);
const loading = ref(true);
const saving = ref(false);
const showOnboardModal = ref(false);
const showAssignModal = ref(false);
const selectedStaff = ref(null);
const selectedTrekId = ref('');

const successMsg = ref('');
const errorMsg = ref('');

const onboardForm = reactive({
  name: '',
  username: '',
  email: '',
  password: '',
  contact_no: '',
  specialization: '',
  experience_years: 2
});

const fetchStaffAndTreks = async () => {
  loading.value = true;
  try {
    const [staffRes, treksRes] = await Promise.all([
      api.get('/admin/staff'),
      api.get('/treks')
    ]);
    staffList.value = staffRes.data.staff || [];
    allTreks.value = treksRes.data.treks || [];
  } catch (err) {
    console.error('Failed to load staff roster', err);
  } finally {
    loading.value = false;
  }
};

const createStaff = async () => {
  saving.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.post('/admin/staff', onboardForm);
    successMsg.value = res.data.message || 'Staff member onboarded successfully!';
    showOnboardModal.value = false;
    Object.assign(onboardForm, {
      name: '',
      username: '',
      email: '',
      password: '',
      contact_no: '',
      specialization: '',
      experience_years: 2
    });
    await fetchStaffAndTreks();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to onboard staff';
  } finally {
    saving.value = false;
  }
};

const openAssignModal = (staff) => {
  selectedStaff.value = staff;
  selectedTrekId.value = '';
  showAssignModal.value = true;
};

const assignTrek = async () => {
  if (!selectedTrekId.value || !selectedStaff.value) return;

  saving.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.post('/admin/assign-staff', {
      trek_id: selectedTrekId.value,
      staff_id: selectedStaff.value.id
    });
    successMsg.value = res.data.message || 'Trek assigned successfully!';
    showAssignModal.value = false;
    await fetchStaffAndTreks();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to assign trek';
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchStaffAndTreks();
});
</script>
