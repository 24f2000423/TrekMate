<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="card-header bg-success text-white text-center py-4 border-0">
            <h3 class="fw-bold mb-1">🏔️ Welcome to TMA</h3>
            <p class="small text-white-50 mb-0">Sign in to your role-based account</p>
          </div>

          <div class="card-body p-4 p-md-5">
            <!-- Alert message -->
            <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ errorMessage }}
              <button type="button" class="btn-close" @click="errorMessage = ''"></button>
            </div>

            <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
              <i class="bi bi-check-circle-fill me-2"></i>{{ successMessage }}
              <button type="button" class="btn-close" @click="successMessage = ''"></button>
            </div>

            <!-- Form -->
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label small fw-bold">Email or Username</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-person"></i></span>
                  <input
                    type="text"
                    v-model="form.identifier"
                    class="form-control"
                    placeholder="e.g. admin@trekma.com or trekker_john"
                    required
                  />
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label small fw-bold">Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-lock"></i></span>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    v-model="form.password"
                    class="form-control"
                    placeholder="Enter your password"
                    required
                  />
                  <button class="btn btn-outline-secondary" type="button" @click="showPassword = !showPassword">
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <button type="submit" class="btn btn-success w-100 py-2 fw-bold mb-3 shadow-sm" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Sign In
              </button>
            </form>

            <!-- Quick Demo Auto-Fill Buttons for Evaluation -->
            <div class="mt-4 pt-3 border-top">
              <label class="form-label small fw-bold text-muted d-block text-center mb-2">
                ⚡ Quick Demo Login (One-Click)
              </label>
              <div class="d-grid gap-2">
                <button class="btn btn-outline-danger btn-sm text-start" @click="fillCredentials('admin@trekma.com', 'Admin@123')">
                  <i class="bi bi-shield-lock me-1"></i> <strong>Admin:</strong> admin@trekma.com (Admin@123)
                </button>
                <button class="btn btn-outline-primary btn-sm text-start" @click="fillCredentials('alex@trekma.com', 'Staff@123')">
                  <i class="bi bi-person-badge me-1"></i> <strong>Staff:</strong> alex@trekma.com (Staff@123)
                </button>
                <button class="btn btn-outline-success btn-sm text-start" @click="fillCredentials('john@example.com', 'User@123')">
                  <i class="bi bi-person-walking me-1"></i> <strong>Trekker:</strong> john@example.com (User@123)
                </button>
              </div>
            </div>

            <!-- Footer links -->
            <div class="text-center mt-4 pt-2 small text-muted">
              Don't have a Trekker account?
              <router-link to="/register" class="text-success fw-bold text-decoration-none">
                Register here
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
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import { useAuth } from '../store/auth';

const router = useRouter();
const route = useRoute();
const { setAuth } = useAuth();

const form = reactive({
  identifier: '',
  password: '',
});

const showPassword = ref(false);
const loading = ref(false);
const errorMessage = ref(route.query.expired ? 'Your session expired. Please sign in again.' : '');
const successMessage = ref('');

const fillCredentials = (id, pass) => {
  form.identifier = id;
  form.password = pass;
};

const handleLogin = async () => {
  errorMessage.value = '';
  successMessage.value = '';
  loading.value = true;

  try {
    const res = await api.post('/auth/login', form);
    const { access_token, user } = res.data;
    setAuth(access_token, user);

    // Role-based redirection
    if (user.role === 'admin') {
      router.push('/admin/dashboard');
    } else if (user.role === 'staff') {
      router.push('/staff/dashboard');
    } else {
      router.push('/user/dashboard');
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Login failed. Please check your credentials.';
  } finally {
    loading.value = false;
  }
};
</script>
