<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">🏔️ Trek Management</h2>
        <p class="text-muted mb-0">Create, update, monitor, and remove trekking routes</p>
      </div>
      <button class="btn btn-success" @click="openCreateModal">
        <i class="bi bi-plus-circle me-1"></i> Add New Trek
      </button>
    </div>

    <!-- Alert -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
      <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Filter & Search Bar -->
    <div class="card border-0 shadow-sm rounded-4 p-3 mb-4">
      <div class="row g-2 align-items-center">
        <div class="col-md-5">
          <input
            type="text"
            v-model="searchTerm"
            class="form-control"
            placeholder="Search by trek name or location..."
          />
        </div>
        <div class="col-md-3">
          <select v-model="filterDifficulty" class="form-select">
            <option value="">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
        <div class="col-md-3">
          <select v-model="filterStatus" class="form-select">
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
        <div class="col-md-1">
          <button class="btn btn-outline-secondary w-100" @click="resetFilters">
            <i class="bi bi-arrow-counterclockwise"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Treks Table -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
        </div>

        <div v-else-if="filteredTreks.length === 0" class="text-center py-5 text-muted">
          <p>No treks found matching your criteria.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Trek Details</th>
                <th>Difficulty</th>
                <th>Duration</th>
                <th>Slots (Avail/Total)</th>
                <th>Assigned Staff</th>
                <th>Dates</th>
                <th>Price</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in filteredTreks" :key="t.id">
                <td class="text-muted font-monospace">#{{ t.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ t.name }}</div>
                  <small class="text-muted"><i class="bi bi-geo-alt text-danger me-1"></i>{{ t.location }}</small>
                </td>
                <td>
                  <span class="badge" :class="getDifficultyBadge(t.difficulty)">{{ t.difficulty }}</span>
                </td>
                <td>{{ t.duration_days }}d</td>
                <td>
                  <span class="badge" :class="t.available_slots > 0 ? 'bg-success' : 'bg-danger'">
                    {{ t.available_slots }} / {{ t.total_slots }}
                  </span>
                </td>
                <td>
                  <span v-if="t.assigned_staff_name" class="badge bg-primary-subtle text-primary border">
                    {{ t.assigned_staff_name }}
                  </span>
                  <span v-else class="badge bg-light text-muted border">Unassigned</span>
                </td>
                <td class="small">
                  <div>{{ t.start_date }}</div>
                  <div class="text-muted">to {{ t.end_date }}</div>
                </td>
                <td class="fw-bold text-success">₹{{ Number(t.price).toLocaleString('en-IN') }}</td>
                <td>
                  <span class="badge" :class="getStatusBadge(t.status)">{{ t.status }}</span>
                </td>
                <td class="text-end">
                  <div class="btn-group">
                    <button class="btn btn-outline-primary btn-sm" @click="openEditModal(t)" title="Edit Trek">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" @click="deleteTrek(t)" title="Delete Trek">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <div v-if="showModal" class="modal-backdrop fade show"></div>
    <div v-if="showModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content rounded-4 border-0 shadow">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title fw-bold">
              {{ isEditing ? 'Edit Trek Route' : 'Create New Trek Route' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
          </div>

          <form @submit.prevent="saveTrek">
            <div class="modal-body p-4">
              <div class="row g-3">
                <div class="col-md-8">
                  <label class="form-label small fw-bold">Trek Name *</label>
                  <input type="text" v-model="formData.name" class="form-control" placeholder="e.g. Kedarkantha Winter Summit" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-bold">Difficulty *</label>
                  <select v-model="formData.difficulty" class="form-select" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Location *</label>
                  <input type="text" v-model="formData.location" class="form-control" placeholder="e.g. Uttarakhand, Himalayas" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold">Price per Trekker (INR) *</label>
                  <input type="number" v-model="formData.price" class="form-control" min="0" step="100" required />
                </div>

                <div class="col-md-4">
                  <label class="form-label small fw-bold">Duration (in Days) *</label>
                  <input type="number" v-model="formData.duration_days" class="form-control" min="1" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-bold">Total Slots *</label>
                  <input type="number" v-model="formData.total_slots" class="form-control" min="1" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-bold">Status *</label>
                  <select v-model="formData.status" class="form-select" required>
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Start Date *</label>
                  <input type="date" v-model="formData.start_date" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold">End Date *</label>
                  <input type="date" v-model="formData.end_date" class="form-control" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Assign Staff Leader</label>
                  <select v-model="formData.assigned_staff_id" class="form-select">
                    <option :value="null">-- Unassigned --</option>
                    <option v-for="s in staffList" :key="s.id" :value="s.id">
                      {{ s.name }} ({{ s.email }})
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold">Cover Image URL</label>
                  <input type="url" v-model="formData.image_url" class="form-control" placeholder="https://..." />
                </div>

                <div class="col-12">
                  <label class="form-label small fw-bold">Trek Description</label>
                  <textarea v-model="formData.description" class="form-control" rows="3" placeholder="Trek route overview, highlights, difficulty level notes..."></textarea>
                </div>
              </div>
            </div>

            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-success px-4" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                {{ isEditing ? 'Update Trek' : 'Create Trek' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../../api';

const treks = ref([]);
const staffList = ref([]);
const loading = ref(true);
const saving = ref(false);
const showModal = ref(false);
const isEditing = ref(false);
const currentTrekId = ref(null);

const searchTerm = ref('');
const filterDifficulty = ref('');
const filterStatus = ref('');

const successMsg = ref('');
const errorMsg = ref('');

const formData = reactive({
  name: '',
  location: '',
  difficulty: 'Moderate',
  duration_days: 3,
  total_slots: 20,
  price: 5000,
  status: 'Open',
  start_date: '',
  end_date: '',
  assigned_staff_id: null,
  image_url: '',
  description: ''
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
    case 'Completed': return 'bg-info text-dark';
    default: return 'bg-secondary';
  }
};

const filteredTreks = computed(() => {
  return treks.value.filter(t => {
    const matchesSearch = !searchTerm.value ||
      t.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      t.location.toLowerCase().includes(searchTerm.value.toLowerCase());
    const matchesDiff = !filterDifficulty.value || t.difficulty === filterDifficulty.value;
    const matchesStatus = !filterStatus.value || t.status === filterStatus.value;
    return matchesSearch && matchesDiff && matchesStatus;
  });
});

const resetFilters = () => {
  searchTerm.value = '';
  filterDifficulty.value = '';
  filterStatus.value = '';
};

const fetchTreks = async () => {
  loading.value = true;
  try {
    const [tRes, sRes] = await Promise.all([
      api.get('/treks'),
      api.get('/admin/staff')
    ]);
    treks.value = tRes.data.treks || [];
    staffList.value = sRes.data.staff || [];
  } catch (err) {
    console.error('Failed to load treks:', err);
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  isEditing.value = false;
  currentTrekId.value = null;
  Object.assign(formData, {
    name: '',
    location: '',
    difficulty: 'Moderate',
    duration_days: 3,
    total_slots: 20,
    price: 5000,
    status: 'Open',
    start_date: '',
    end_date: '',
    assigned_staff_id: null,
    image_url: '',
    description: ''
  });
  showModal.value = true;
};

const openEditModal = (trek) => {
  isEditing.value = true;
  currentTrekId.value = trek.id;
  Object.assign(formData, {
    name: trek.name,
    location: trek.location,
    difficulty: trek.difficulty,
    duration_days: trek.duration_days,
    total_slots: trek.total_slots,
    price: trek.price,
    status: trek.status,
    start_date: trek.start_date,
    end_date: trek.end_date,
    assigned_staff_id: trek.assigned_staff_id,
    image_url: trek.image_url || '',
    description: trek.description || ''
  });
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveTrek = async () => {
  saving.value = true;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    if (isEditing.value) {
      const res = await api.put(`/treks/${currentTrekId.value}`, formData);
      successMsg.value = res.data.message || 'Trek updated successfully';
    } else {
      const res = await api.post('/treks', formData);
      successMsg.value = res.data.message || 'Trek created successfully';
    }
    closeModal();
    await fetchTreks();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to save trek';
  } finally {
    saving.value = false;
  }
};

const deleteTrek = async (trek) => {
  if (!confirm(`Are you sure you want to delete trek "${trek.name}"? This action cannot be undone.`)) {
    return;
  }

  try {
    const res = await api.delete(`/treks/${trek.id}`);
    successMsg.value = res.data.message || 'Trek deleted';
    await fetchTreks();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to delete trek';
  }
};

onMounted(() => {
  fetchTreks();
});
</script>
