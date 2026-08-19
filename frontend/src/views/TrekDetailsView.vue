<template>
  <div class="container py-5">
    <!-- Back button -->
    <router-link to="/" class="btn btn-outline-secondary btn-sm mb-4 rounded-pill">
      <i class="bi bi-arrow-left me-1"></i> Back to All Treks
    </router-link>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Loading trek details...</span>
      </div>
    </div>

    <!-- Main Detail View -->
    <div v-else-if="trek" class="row g-4">
      <!-- Left Column: Image and Description -->
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
          <div class="position-relative" style="height: 380px;">
            <img
              :src="trek.image_url || defaultImage"
              :alt="trek.name"
              class="w-100 h-100 object-fit-cover"
              @error="onImageError"
            />
            <span
              class="position-absolute top-0 start-0 m-3 badge px-3 py-2 rounded-pill shadow"
              :class="getDifficultyBadge(trek.difficulty)"
              style="font-size: 14px;"
            >
              {{ trek.difficulty }}
            </span>
            <span
              class="position-absolute top-0 end-0 m-3 badge px-3 py-2 rounded-pill shadow"
              :class="getStatusBadge(trek.status)"
              style="font-size: 14px;"
            >
              {{ trek.status }}
            </span>
          </div>

          <div class="card-body p-4">
            <h2 class="fw-bold text-dark mb-2">{{ trek.name }}</h2>
            <p class="text-muted d-flex align-items-center mb-4">
              <i class="bi bi-geo-alt-fill text-danger me-2"></i> {{ trek.location }}
            </p>

            <h5 class="fw-bold border-bottom pb-2 mb-3">Trek Overview</h5>
            <p class="text-secondary leading-relaxed" style="white-space: pre-line; line-height: 1.7;">
              {{ trek.description || 'Join us for this picturesque trekking expedition with certified mountaineers and comprehensive logistics support.' }}
            </p>

            <hr class="my-4" />

            <!-- Staff Guide Information -->
            <h5 class="fw-bold mb-3">Expedition Leader / Assigned Staff</h5>
            <div class="d-flex align-items-center bg-light p-3 rounded-3">
              <div class="rounded-circle bg-success text-white fw-bold d-flex align-items-center justify-content-center me-3" style="width: 48px; height: 48px;">
                <i class="bi bi-person-badge fs-4"></i>
              </div>
              <div>
                <h6 class="fw-bold mb-0">{{ trek.assigned_staff_name || 'TMA Expedition Guide' }}</h6>
                <small class="text-muted d-block">Contact: {{ trek.assigned_staff_contact || 'N/A' }} | Email: {{ trek.assigned_staff_email || 'staff@trekma.com' }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Booking Card & Key Facts -->
      <div class="col-lg-4">
        <div class="card border-0 shadow-sm rounded-4 p-4 sticky-top" style="top: 90px;">
          <div class="d-flex justify-content-between align-items-baseline mb-3">
            <span class="text-muted small">Trek Package</span>
            <span class="display-6 fw-bold text-success">₹{{ formatPrice(trek.price) }}</span>
          </div>

          <div class="list-group list-group-flush mb-4">
            <div class="list-group-item d-flex justify-content-between px-0 py-2">
              <span class="text-muted"><i class="bi bi-clock me-2"></i>Duration</span>
              <strong class="text-dark">{{ trek.duration_days }} Days</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between px-0 py-2">
              <span class="text-muted"><i class="bi bi-calendar-event me-2"></i>Start Date</span>
              <strong class="text-dark">{{ trek.start_date }}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between px-0 py-2">
              <span class="text-muted"><i class="bi bi-calendar-check me-2"></i>End Date</span>
              <strong class="text-dark">{{ trek.end_date }}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between px-0 py-2">
              <span class="text-muted"><i class="bi bi-people me-2"></i>Available Slots</span>
              <span class="badge px-2 py-1" :class="trek.available_slots > 0 ? 'bg-success' : 'bg-danger'">
                {{ trek.available_slots }} / {{ trek.total_slots }} Slots
              </span>
            </div>
          </div>

          <!-- Alert message -->
          <div v-if="bookingError" class="alert alert-danger alert-dismissible fade show small" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-1"></i> {{ bookingError }}
            <button type="button" class="btn-close" @click="bookingError = ''"></button>
          </div>

          <div v-if="bookingSuccess" class="alert alert-success alert-dismissible fade show small" role="alert">
            <i class="bi bi-check-circle-fill me-1"></i> {{ bookingSuccess }}
            <button type="button" class="btn-close" @click="bookingSuccess = ''"></button>
          </div>

          <!-- Action Box -->
          <template v-if="!isLoggedIn">
            <div class="alert alert-warning small mb-3">
              <i class="bi bi-info-circle me-1"></i> You must be logged in as a Trekker to book this trek.
            </div>
            <router-link to="/login" class="btn btn-success w-100 py-2 fw-bold rounded-pill">
              Log In to Book
            </router-link>
          </template>

          <template v-else-if="isTrekker">
            <div v-if="trek.status !== 'Open'" class="alert alert-secondary small text-center mb-0">
              <i class="bi bi-lock-fill me-1"></i> Bookings are currently {{ trek.status }}.
            </div>
            <div v-else-if="trek.available_slots <= 0" class="alert alert-danger small text-center mb-0">
              <i class="bi bi-x-circle-fill me-1"></i> All slots for this trek are fully booked!
            </div>
            <div v-else>
              <form @submit.prevent="submitBooking">
                <div class="mb-3">
                  <label class="form-label small fw-bold">Number of Seats</label>
                  <input
                    type="number"
                    v-model="bookingForm.seats"
                    class="form-control"
                    min="1"
                    :max="trek.available_slots"
                    required
                  />
                  <small class="text-muted" style="font-size: 11px;">Max {{ trek.available_slots }} slots available</small>
                </div>

                <div class="mb-3">
                  <label class="form-label small fw-bold">Special Dietary / Medical Notes (Optional)</label>
                  <textarea
                    v-model="bookingForm.special_notes"
                    class="form-control"
                    rows="2"
                    placeholder="e.g. Vegetarian meal preference, trek poles needed..."
                  ></textarea>
                </div>

                <div class="bg-light p-3 rounded-3 mb-3 text-center">
                  <span class="text-muted small d-block">Estimated Total</span>
                  <span class="fs-4 fw-bold text-success">₹{{ formatPrice(trek.price * bookingForm.seats) }}</span>
                </div>

                <button type="submit" class="btn btn-success w-100 py-2 fw-bold rounded-pill shadow-sm" :disabled="bookingLoading">
                  <span v-if="bookingLoading" class="spinner-border spinner-border-sm me-2"></span>
                  Confirm & Book Now
                </button>
              </form>
            </div>
          </template>

          <template v-else>
            <div class="alert alert-info small mb-0">
              Logged in as <strong>{{ user?.role }}</strong>. Trekkers can book slots from their user portal.
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import { useAuth } from '../store/auth';

const route = useRoute();
const router = useRouter();
const { isLoggedIn, isTrekker, user } = useAuth();

const trek = ref(null);
const loading = ref(true);
const bookingLoading = ref(false);
const bookingError = ref('');
const bookingSuccess = ref('');

const bookingForm = reactive({
  seats: 1,
  special_notes: ''
});

const defaultImage = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80';

const onImageError = (e) => {
  e.target.src = defaultImage;
};

const getDifficultyBadge = (diff) => {
  switch (diff) {
    case 'Easy': return 'bg-success text-white';
    case 'Moderate': return 'bg-warning text-dark';
    case 'Hard': return 'bg-danger text-white';
    default: return 'bg-secondary text-white';
  }
};

const getStatusBadge = (status) => {
  switch (status) {
    case 'Open': return 'bg-primary text-white';
    case 'Closed': return 'bg-dark text-white';
    case 'Completed': return 'bg-info text-dark';
    default: return 'bg-secondary text-white';
  }
};

const formatPrice = (p) => Number(p || 0).toLocaleString('en-IN');

const fetchTrekDetails = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/treks/${route.params.id}`);
    trek.value = res.data.trek;
  } catch (err) {
    console.error('Failed to load trek details:', err);
  } finally {
    loading.value = false;
  }
};

const submitBooking = async () => {
  bookingError.value = '';
  bookingSuccess.value = '';
  bookingLoading.value = true;

  try {
    const res = await api.post('/bookings', {
      trek_id: trek.value.id,
      seats: bookingForm.seats,
      special_notes: bookingForm.special_notes
    });

    bookingSuccess.value = res.data.message || 'Booking successful!';
    await fetchTrekDetails(); // refresh slot counts
    setTimeout(() => {
      router.push('/user/bookings');
    }, 1500);
  } catch (err) {
    bookingError.value = err.response?.data?.error || 'Booking could not be processed.';
  } finally {
    bookingLoading.value = false;
  }
};

onMounted(() => {
  fetchTrekDetails();
});
</script>
