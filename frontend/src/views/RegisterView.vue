<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-7 col-lg-6">
        <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="card-header bg-warning text-dark text-center py-4 border-0">
            <h3 class="fw-bold mb-1">🏕️ Trekker Registration</h3>
            <p class="small text-muted mb-0">Create your account to start booking trekking adventures</p>
          </div>

          <div class="card-body p-4 p-md-5">
            <!-- Alert message -->
            <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMessage }}
              <button type="button" class="btn-close" @click="errorMessage = ''"></button>
            </div>

            <!-- Form -->
            <form @submit.prevent="handleRegister">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label small fw-bold">Full Name *</label>
                  <input
                    type="text"
                    v-model="form.name"
                    class="form-control"
                    placeholder="e.g. Rahul Sharma"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Username *</label>
                  <input
                    type="text"
                    v-model="form.username"
                    class="form-control"
                    placeholder="e.g. trekker_rahul"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Email Address *</label>
                  <input
                    type="email"
                    v-model="form.email"
                    class="form-control"
                    placeholder="rahul@example.com"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Contact Number</label>
                  <input
                    type="tel"
                    v-model="form.contact_no"
                    class="form-control"
                    placeholder="+91 98765 43210"
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Password *</label>
                  <input
                    type="password"
                    v-model="form.password"
                    class="form-control"
                    placeholder="At least 6 characters"
                    minlength="6"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label small fw-bold">Confirm Password *</label>
                  <input
                    type="password"
                    v-model="form.confirm_password"
                    class="form-control"
                    placeholder="Re-enter password"
                    minlength="6"
                    required
                  />
                </div>
              </div>

              <div class="form-check mt-3 mb-4">
                <input class="form-check-input" type="checkbox" id="termsCheck" required />
                <label class="form-check-label small text-muted" for="termsCheck">
                  I agree to the trekking safety guidelines and terms of service.
                </label>
              </div>

              <button type="submit" class="btn btn-warning w-100 py-2 fw-bold text-dark mb-3 shadow-sm" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Create Trekker Account
              </button>
            </form>

            <div class="text-center mt-3 small text-muted">
              Already registered?
              <router-link to="/login" class="text-success fw-bold text-decoration-none">
                Sign in here
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import { useAuth } from '../store/auth';

const router = useRouter();
const { setAuth } = useAuth();

const form = reactive({
  name: '',
  username: '',
  email: '',
  contact_no: '',
  password: '',
  confirm_password: '',
});

const loading = ref(false);
const errorMessage = ref('');

const handleRegister = async () => {
  errorMessage.value = '';

  if (form.password !== form.confirm_password) {
    errorMessage.value = 'Passwords do not match.';
    return;
  }

  loading.value = true;
  try {
    const res = await api.post('/auth/register', {
      name: form.name,
      username: form.username,
      email: form.email,
      contact_no: form.contact_no,
      password: form.password,
    });

    const { access_token, user } = res.data;
    setAuth(access_token, user);
    router.push('/user/dashboard');
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Registration failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
