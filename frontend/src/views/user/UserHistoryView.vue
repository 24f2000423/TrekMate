<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
      <div>
        <h2 class="fw-bold mb-1">Trekking History & CSV Export</h2>
        <p class="text-muted mb-0">Review all your historical trekking expeditions and trigger asynchronous CSV exports</p>
      </div>
      <div>
        <button
          class="btn btn-success shadow-sm d-flex align-items-center"
          :disabled="exportLoading"
          @click="triggerAsyncCsvExport"
        >
          <span v-if="exportLoading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-spreadsheet-fill me-2"></i>
          Export History as CSV (Celery Job)
        </button>
      </div>
    </div>

    <!-- Export Alert Notification -->
    <div v-if="exportAlert" class="alert alert-info alert-dismissible fade show shadow-sm" role="alert">
      <div class="d-flex align-items-center">
        <div class="spinner-border spinner-border-sm text-info me-3" v-if="exportStatus === 'PENDING'"></div>
        <i v-else class="bi bi-check-circle-fill text-success fs-5 me-3"></i>
        <div class="flex-grow-1">
          <div class="fw-bold">{{ exportAlert.title }}</div>
          <div class="small">{{ exportAlert.message }}</div>
          <a
            v-if="exportAlert.downloadUrl"
            :href="exportAlert.downloadUrl"
            class="btn btn-sm btn-primary mt-2"
            download
          >
            <i class="bi bi-download me-1"></i> Download Exported CSV Now
          </a>
        </div>
      </div>
      <button type="button" class="btn-close" @click="exportAlert = null"></button>
    </div>

    <!-- Tabs: History vs Export Jobs -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="card-header bg-white border-bottom p-3">
        <ul class="nav nav-pills card-header-pills">
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'history' }"
              @click="activeTab = 'history'"
            >
              <i class="bi bi-clock-history me-1"></i> Full Trek History ({{ history.length }})
            </button>
          </li>
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'exports' }"
              @click="activeTab = 'exports'"
            >
              <i class="bi bi-folder-check me-1"></i> My Generated Exports ({{ pastExports.length }})
            </button>
          </li>
        </ul>
      </div>

      <div class="card-body p-0">
        <!-- Tab 1: Full History -->
        <div v-if="activeTab === 'history'">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-success"></div>
          </div>
          <div v-else-if="history.length === 0" class="text-center py-5 text-muted">
            <p>No historical treks recorded yet.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>#ID</th>
                  <th>Trek Name</th>
                  <th>Location</th>
                  <th>Difficulty</th>
                  <th>Expedition Dates</th>
                  <th>Seats</th>
                  <th>Total Cost</th>
                  <th>Status</th>
                  <th>Booking Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in history" :key="item.id">
                  <td class="font-monospace text-muted">#{{ item.id }}</td>
                  <td class="fw-bold">{{ item.trek_name }}</td>
                  <td>{{ item.trek_location }}</td>
                  <td>
                    <span class="badge" :class="getDifficultyBadge(item.trek_difficulty)">
                      {{ item.trek_difficulty }}
                    </span>
                  </td>
                  <td>{{ item.trek_start_date }} &rarr; {{ item.trek_end_date }}</td>
                  <td>{{ item.seats }}</td>
                  <td class="fw-bold">₹{{ (item.total_amount || 0).toLocaleString('en-IN') }}</td>
                  <td>
                    <span class="badge" :class="getStatusBadge(item.status)">{{ item.status }}</span>
                  </td>
                  <td class="small text-muted">{{ item.booking_date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab 2: Past Exports -->
        <div v-if="activeTab === 'exports'">
          <div v-if="pastExports.length === 0" class="text-center py-5 text-muted">
            <i class="bi bi-file-earmark-arrow-down display-4 d-block mb-2"></i>
            <p>No CSV exports generated yet. Click "Export History as CSV" above to trigger a batch job.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Job / Task ID</th>
                  <th>File Name</th>
                  <th>Status</th>
                  <th>Generated At</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in pastExports" :key="job.id">
                  <td class="font-monospace small text-muted">{{ job.task_id }}</td>
                  <td class="fw-bold">{{ job.file_name || 'Generating...' }}</td>
                  <td>
                    <span class="badge" :class="job.status === 'SUCCESS' ? 'bg-success' : 'bg-warning text-dark'">
                      {{ job.status }}
                    </span>
                  </td>
                  <td class="small text-muted">{{ job.created_at }}</td>
                  <td class="text-end">
                    <a
                      v-if="job.download_url"
                      :href="job.download_url"
                      class="btn btn-sm btn-outline-success"
                      download
                    >
                      <i class="bi bi-download me-1"></i> Download
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../../api';
import { useAuth } from '../../store/auth';

const { user, fetchNotifications } = useAuth();

const history = ref([]);
const pastExports = ref([]);
const loading = ref(true);
const exportLoading = ref(false);
const activeTab = ref('history');

const exportAlert = ref(null);
const exportStatus = ref('');

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
    case 'Booked': return 'bg-success';
    case 'Completed': return 'bg-info text-dark';
    case 'Cancelled': return 'bg-danger';
    default: return 'bg-secondary';
  }
};

const fetchHistoryData = async () => {
  loading.value = true;
  try {
    const [histRes, expRes] = await Promise.all([
      api.get('/bookings/history'),
      api.get('/reports/my-exports')
    ]);
    history.value = histRes.data.history || [];
    pastExports.value = expRes.data.exports || [];
  } catch (err) {
    console.error('Failed to load history', err);
  } finally {
    loading.value = false;
  }
};

const triggerAsyncCsvExport = async () => {
  exportLoading.value = true;
  exportAlert.value = null;

  try {
    const res = await api.post('/reports/trigger-export');
    const { task_id, download_url, file_name, message, status } = res.data;

    exportStatus.value = status;
    exportAlert.value = {
      title: 'Batch Job Dispatched (Celery)',
      message: message || 'Your CSV export is being processed in the background.',
      downloadUrl: download_url || (file_name ? `/api/reports/download-export/${file_name}` : null)
    };

    // If already synchronous result
    if (download_url) {
      exportStatus.value = 'SUCCESS';
    } else {
      // Poll for completion
      pollExportStatus(task_id);
    }

    await fetchHistoryData();
    await fetchNotifications();
  } catch (err) {
    exportAlert.value = {
      title: 'Export Failed',
      message: err.response?.data?.error || 'Failed to trigger batch job.'
    };
  } finally {
    exportLoading.value = false;
  }
};

const pollExportStatus = (taskId) => {
  let attempts = 0;
  const interval = setInterval(async () => {
    attempts++;
    try {
      const res = await api.get(`/reports/export-status/${taskId}`);
      const job = res.data.job;
      if (job.status === 'SUCCESS') {
        clearInterval(interval);
        exportStatus.value = 'SUCCESS';
        exportAlert.value = {
          title: 'Export Complete!',
          message: `CSV generated with file name "${job.file_name}". Click below to download.`,
          downloadUrl: job.download_url
        };
        fetchHistoryData();
        fetchNotifications();
      } else if (job.status === 'FAILURE' || attempts > 10) {
        clearInterval(interval);
      }
    } catch (e) {
      if (attempts > 8) clearInterval(interval);
    }
  }, 2000);
};

onMounted(() => {
  fetchHistoryData();
});
</script>
