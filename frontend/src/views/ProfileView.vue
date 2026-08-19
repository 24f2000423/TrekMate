<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Header -->
        <div class="card border-0 shadow-sm rounded-4 mb-4 bg-success text-white p-4">
          <div class="d-flex align-items-center">
            <div class="rounded-circle bg-white text-success fw-bold display-6 d-flex align-items-center justify-content-center me-3" style="width: 70px; height: 70px;">
              {{ user?.name ? user.name.charAt(0).toUpperCase() : 'U' }}
            </div>
            <div>
              <h3 class="fw-bold mb-1">{{ user?.name }}</h3>
              <p class="mb-0 text-white-50">
                <span class="badge bg-light text-success text-uppercase me-2">{{ user?.role }}</span>
                {{ user?.email }}
              </p>
            </div>
          </div>
        </div>

        <!-- Alert messages -->
        <div v-if="successMsg" class="alert alert-success alert-dismissible fade show" role="alert">
          <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
          <button type="button" class="btn-close" @click="successMsg = ''"></button>
        </div>
        <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMsg }}
          <button type="button" class="btn-close" @click="errorMsg = ''"></button>
        </div>

        <div class="row g-4">
          <!-- Edit Profile Form -->
          <div class="col-md-7">
            <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
              <h5 class="fw-bold mb-3 border-bottom pb-2">
                <i class="bi bi-person-lines-fill text-success me-2"></i>Personal Details
              </h5>
              <form @submit.prevent="updateProfile">
                <div class="mb-3">
                  <label class="form-label small fw-bold">Full Name</label>
                  <input type="text" v-model="profileForm.name" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Username</label>
                  <input type="text" :value="user?.username" class="form-control bg-light" disabled />
                  <small class="text-muted" style="font-size: 11px;">Username cannot be changed</small>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Email Address</label>
                  <input type="email" :value="user?.email" class="form-control bg-light" disabled />
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Contact Number</label>
                  <input type="tel" v-model="profileForm.contact_no" class="form-control" />
                </div>

                <!-- Staff specific fields -->
                <template v-if="user?.role === 'staff'">
                  <div class="mb-3">
                    <label class="form-label small fw-bold">Specialization</label>
                    <input type="text" v-model="profileForm.specialization" class="form-control" placeholder="e.g. Alpine, First Aid" />
                  </div>
                  <div class="mb-3">
                    <label class="form-label small fw-bold">Years of Experience</label>
                    <input type="number" v-model="profileForm.experience_years" class="form-control" min="0" />
                  </div>
                </template>

                <button type="submit" class="btn btn-success px-4" :disabled="savingProfile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-1"></span>
                  Save Changes
                </button>
              </form>
            </div>
          </div>

          <!-- Change Password Form -->
          <div class="col-md-5">
            <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
              <h5 class="fw-bold mb-3 border-bottom pb-2">
                <i class="bi bi-shield-lock text-success me-2"></i>Security
              </h5>
              <form @submit.prevent="changePassword">
                <div class="mb-3">
                  <label class="form-label small fw-bold">Current Password</label>
                  <input type="password" v-model="passForm.old_password" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">New Password</label>
                  <input type="password" v-model="passForm.new_password" class="form-control" minlength="6" required />
                </div>
                <button type="submit" class="btn btn-outline-dark w-100" :disabled="savingPass">
                  <span v-if="savingPass" class="spinner-border spinner-border-sm me-1"></span>
                  Update Password
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { useAuth } from '../store/auth';

const { user, fetchProfile } = useAuth();

const profileForm = reactive({
  name: '',
  contact_no: '',
  specialization: '',
  experience_years: 0,
});

const passForm = reactive({
  old_password: '',
  new_password: '',
});

const savingProfile = ref(false);
const savingPass = ref(false);
const successMsg = ref('');
const errorMsg = ref('');

const loadUserData = () => {
  if (user.value) {
    profileForm.name = user.value.name || '';
    profileForm.contact_no = user.value.contact_no || '';
    profileForm.specialization = user.value.specialization || '';
    profileForm.experience_years = user.value.experience_years || 0;
  }
};

const updateProfile = async () => {
  savingProfile.value = true;
  successMsg.value = '';
  errorMsg.value = '';
  try {
    const res = await api.put('/auth/me', profileForm);
    successMsg.value = res.data.message || 'Profile updated!';
    await fetchProfile();
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update profile';
  } finally {
    savingProfile.value = false;
  }
};

const changePassword = async () => {
  savingPass.value = true;
  successMsg.value = '';
  errorMsg.value = '';
  try {
    const res = await api.post('/auth/change-password', passForm);
    successMsg.value = res.data.message || 'Password changed!';
    passForm.old_password = '';
    passForm.new_password = '';
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to change password';
  } finally {
    savingPass.value = false;
  }
};

onMounted(() => {
  loadUserData();
});
</script>
