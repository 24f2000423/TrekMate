<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">🛡️ User & Staff Moderation</h2>
        <p class="text-muted mb-0">Manage accounts, search users, activate/deactivate access, and blacklist</p>
      </div>
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

    <!-- Search & Filter Card -->
    <div class="card border-0 shadow-sm rounded-4 p-3 mb-4">
      <div class="row g-2 align-items-center">
        <div class="col-md-7">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
            <input
              type="text"
              v-model="searchTerm"
              class="form-control border-start-0"
              placeholder="Search user by name, email, or username..."
              @input="debounceSearch"
            />
          </div>
        </div>
        <div class="col-md-4">
          <select v-model="filterRole" class="form-select" @change="fetchUsers">
            <option value="">All Roles (Trekkers, Staff, Admin)</option>
            <option value="user">Trekkers (Users)</option>
            <option value="staff">Staff Members</option>
            <option value="admin">Admins</option>
          </select>
        </div>
        <div class="col-md-1">
          <button class="btn btn-outline-secondary w-100" @click="resetFilters">
            <i class="bi bi-arrow-counterclockwise"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
        </div>

        <div v-else-if="users.length === 0" class="text-center py-5 text-muted">
          <p>No accounts found matching search criteria.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>User ID</th>
                <th>Name & Username</th>
                <th>Email & Phone</th>
                <th>Role</th>
                <th>Account Status</th>
                <th>Joined Date</th>
                <th class="text-end">Moderation Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" :class="{'table-danger-subtle': u.is_blacklisted, 'opacity-75': !u.is_active}">
                <td class="font-monospace text-muted">#{{ u.id }}</td>
                <td>
                  <div class="fw-bold text-dark">{{ u.name }}</div>
                  <small class="text-muted">@{{ u.username }}</small>
                </td>
                <td>
                  <div>{{ u.email }}</div>
                  <small class="text-muted">{{ u.contact_no || 'N/A' }}</small>
                </td>
                <td>
                  <span class="badge" :class="getRoleBadge(u.role)">{{ u.role }}</span>
                </td>
                <td>
                  <div class="d-flex flex-column gap-1">
                    <span class="badge" :class="u.is_active ? 'bg-success' : 'bg-secondary'">
                      {{ u.is_active ? 'Active' : 'Deactivated' }}
                    </span>
                    <span v-if="u.is_blacklisted" class="badge bg-danger">
                      <i class="bi bi-shield-x me-1"></i> Blacklisted
                    </span>
                  </div>
                </td>
                <td class="small text-muted">{{ u.created_at }}</td>
                <td class="text-end">
                  <template v-if="u.role !== 'admin'">
                    <div class="btn-group">
                      <!-- Toggle Active -->
                      <button
                        class="btn btn-sm"
                        :class="u.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                        @click="toggleUserActive(u)"
                        :title="u.is_active ? 'Deactivate Account' : 'Activate Account'"
                      >
                        <i :class="u.is_active ? 'bi bi-pause-circle' : 'bi bi-play-circle'"></i>
                        {{ u.is_active ? 'Deactivate' : 'Activate' }}
                      </button>

                      <!-- Toggle Blacklist -->
                      <button
                        class="btn btn-sm"
                        :class="u.is_blacklisted ? 'btn-outline-secondary' : 'btn-outline-danger'"
                        @click="toggleUserBlacklist(u)"
                        :title="u.is_blacklisted ? 'Remove from Blacklist' : 'Blacklist User'"
                      >
                        <i class="bi bi-slash-circle me-1"></i>
                        {{ u.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                      </button>
                    </div>
                  </template>
                  <span v-else class="badge bg-light text-muted border">Protected Superuser</span>
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

const users = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const filterRole = ref('');
const successMsg = ref('');
const errorMsg = ref('');

let searchTimer = null;
const debounceSearch = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    fetchUsers();
  }, 350);
};

const getRoleBadge = (role) => {
  switch (role) {
    case 'admin': return 'bg-danger text-white';
    case 'staff': return 'bg-primary text-white';
    case 'user': return 'bg-success text-white';
    default: return 'bg-secondary text-white';
  }
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = {};
    if (searchTerm.value) params.search = searchTerm.value;
    if (filterRole.value) params.role = filterRole.value;

    const res = await api.get('/admin/users', { params });
    users.value = res.data.users || [];
  } catch (err) {
    console.error('Failed to load users:', err);
  } finally {
    loading.value = false;
  }
};

const resetFilters = () => {
  searchTerm.value = '';
  filterRole.value = '';
  fetchUsers();
};

const toggleUserActive = async (user) => {
  const newActive = !user.is_active;
  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.put(`/admin/users/${user.id}/status`, {
      is_active: newActive
    });
    user.is_active = newActive;
    successMsg.value = res.data.message || 'Status updated';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update user status';
  }
};

const toggleUserBlacklist = async (user) => {
  const newBlacklist = !user.is_blacklisted;
  const action = newBlacklist ? 'blacklist' : 'remove from blacklist';
  if (!confirm(`Are you sure you want to ${action} ${user.name}?`)) return;

  successMsg.value = '';
  errorMsg.value = '';

  try {
    const res = await api.put(`/admin/users/${user.id}/status`, {
      is_blacklisted: newBlacklist
    });
    user.is_blacklisted = newBlacklist;
    successMsg.value = res.data.message || 'Blacklist updated';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update blacklist';
  }
};

onMounted(() => {
  fetchUsers();
});
</script>
